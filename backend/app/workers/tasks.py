"""Celery tasks for video processing"""

import logging
import os
import tempfile
from pathlib import Path
from datetime import datetime, timezone
import uuid

from app.workers.celery_app import celery_app
from app.database import SessionLocal, init_db
from app.models import Job, Project, JobStatus, Asset
from app.storage import s3_client
from app.ai_engine.scene_detector import scene_detector
from app.ai_engine.object_tagger import object_tagger
from app.ai_engine.prompt_parser import prompt_parser
from app.ai_engine.shot_selector import shot_selector
from app.ai_engine.renderer import video_renderer

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.workers.tasks.process_edit_job")
def process_edit_job(self, project_id: str, prompt: str):
    """
    Main task to process video editing job
    
    Args:
        project_id: Project ID
        prompt: User's editing prompt
    """
    job_id = self.request.id
    db = SessionLocal()
    temp_dir = None
    
    try:
        logger.info(f"Starting edit job {job_id} for project {project_id}")
        
        # Update job status
        job = db.query(Job).filter(Job.id == job_id.replace('job-', '')).first()
        if not job:
            logger.error(f"Job not found: {job_id}")
            return {"status": "error", "message": "Job not found"}
        
        job.status = JobStatus.PROCESSING
        job.progress_percent = 10
        db.commit()
        
        # Get project and assets
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project or not project.assets:
            raise Exception("Project or assets not found")
        
        logger.info(f"Processing {len(project.assets)} assets")
        job.progress_percent = 20
        db.commit()
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        logger.info(f"Using temp directory: {temp_dir}")
        
        # Download assets from S3
        asset_paths = []
        for i, asset in enumerate(project.assets):
            try:
                local_path = os.path.join(temp_dir, asset.filename)
                logger.debug(f"Downloading asset {i+1}/{len(project.assets)}: {asset.s3_key}")
                
                s3_client.download_file(asset.s3_key, local_path)
                asset_paths.append({
                    'path': local_path,
                    'type': asset.asset_type,
                    'asset_id': asset.id
                })
            except Exception as e:
                logger.error(f"Error downloading asset {asset.s3_key}: {e}")
                continue
        
        if not asset_paths:
            raise Exception("No assets downloaded successfully")
        
        job.progress_percent = 40
        db.commit()
        logger.info(f"Downloaded {len(asset_paths)} assets")
        
        # Analyze assets - detect scenes and tag objects
        scenes_with_tags = []
        for asset_path_info in asset_paths:
            asset_path = asset_path_info['path']
            asset_type = asset_path_info['type']
            
            try:
                if asset_type == 'video':
                    logger.debug(f"Analyzing video: {asset_path}")
                    # Detect scenes
                    scenes = scene_detector.detect_scenes(asset_path)
                    
                    # Tag objects in video
                    tags = object_tagger.tag_video(asset_path, sample_frames=5)
                    
                    # Create scene dictionaries with tags
                    for start, end in scenes:
                        scenes_with_tags.append({
                            'video_path': asset_path,
                            'start': start,
                            'end': end,
                            'tags': list(tags),
                            'duration': end - start
                        })
                
                elif asset_type == 'image':
                    logger.debug(f"Analyzing image: {asset_path}")
                    # Tag objects in image
                    tags = object_tagger.tag_image(asset_path)
                    
                    # Create image as a scene (3 second duration)
                    scenes_with_tags.append({
                        'image_path': asset_path,
                        'video_path': asset_path,  # Will be converted to video clip
                        'start': 0,
                        'end': 3,  # 3 second default for images
                        'tags': list(tags),
                        'duration': 3,
                        'is_image': True
                    })
            except Exception as e:
                logger.error(f"Error analyzing asset {asset_path}: {e}")
                continue
        
        if not scenes_with_tags:
            raise Exception("No scenes extracted from assets")
        
        job.progress_percent = 60
        db.commit()
        logger.info(f"Extracted {len(scenes_with_tags)} scenes/images")
        
        # Parse prompt
        directives = prompt_parser.parse(prompt)
        job.progress_percent = 70
        db.commit()
        logger.info(f"Parsed directives: {directives}")
        
        # Select shots
        include_tags = set(directives.get('include_tags', []))
        exclude_tags = set(directives.get('exclude_tags', []))
        target_duration = directives.get('duration_target', 60)
        
        selected_shots = shot_selector.select_shots(
            scenes_with_tags,
            target_duration,
            include_tags,
            exclude_tags
        )
        
        if not selected_shots:
            logger.warning("No shots selected, using all scenes")
            selected_shots = scenes_with_tags[:min(5, len(scenes_with_tags))]
        
        job.progress_percent = 75
        db.commit()
        logger.info(f"Selected {len(selected_shots)} shots")
        
        # Render video
        output_filename = f"output_{uuid.uuid4()}.mp4"
        output_path = os.path.join(temp_dir, output_filename)
        
        music_path = None
        if directives.get('music'):
            # Try to use default background music if available
            default_music = "/app/ai_engine/assets/upbeat.mp3"
            if os.path.exists(default_music):
                music_path = default_music
        
        success = video_renderer.render(
            selected_shots,
            output_path,
            filter_name=directives.get('filter', 'none'),
            speed=directives.get('speed', 'normal'),
            music_path=music_path
        )
        
        if not success:
            raise Exception("Video rendering failed")
        
        job.progress_percent = 85
        db.commit()
        logger.info(f"Video rendered: {output_path}")
        
        # Upload output to S3
        s3_output_key = f"projects/{project_id}/output/{output_filename}"
        logger.debug(f"Uploading output to S3: {s3_output_key}")
        
        s3_client.upload_file(output_path, s3_output_key)
        
        # Update project and job
        project.output_video_key = s3_output_key
        project.status = JobStatus.COMPLETED
        
        job.status = JobStatus.COMPLETED
        job.progress_percent = 100
        job.completed_at = datetime.now(timezone.utc)
        
        db.commit()
        logger.info(f"Job completed successfully: {job_id}")
        
        return {
            "status": "completed",
            "output_key": s3_output_key,
            "job_id": job_id
        }
    
    except Exception as e:
        logger.error(f"Error processing edit job: {str(e)}")
        
        try:
            job = db.query(Job).filter(Job.celery_task_id == job_id).first()
            if job:
                job.status = JobStatus.FAILED
                job.error_message = str(e)
                job.progress_percent = 0
                job.completed_at = datetime.now(timezone.utc)
                db.commit()
                
                # Update project status
                project = db.query(Project).filter(Project.id == project_id).first()
                if project:
                    project.status = JobStatus.FAILED
                    db.commit()
        except Exception as db_error:
            logger.error(f"Error updating job status: {str(db_error)}")
        
        return {
            "status": "error",
            "message": str(e),
            "job_id": job_id
        }
    
    finally:
        # Cleanup
        db.close()
        if temp_dir and os.path.exists(temp_dir):
            try:
                import shutil
                shutil.rmtree(temp_dir)
                logger.debug(f"Cleaned up temp directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Error cleaning up temp directory: {e}")


# Health check task
@celery_app.task(name="app.workers.tasks.health_check")
def health_check():
    """Simple health check task"""
    logger.info("Health check task executed")
    return {"status": "ok"}
