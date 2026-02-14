"""Jobs routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Project, Job, JobStatus
from app.schemas import StartEditRequest, StartEditResponse, JobResponse
from app.auth.dependencies import get_current_user
from app.workers.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/start-edit", response_model=StartEditResponse)
async def start_edit_job(
    request: StartEditRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start an edit job for a project"""
    try:
        # Verify project belongs to user and has assets
        project = db.query(Project).filter(
            (Project.id == request.project_id) & (Project.user_id == current_user.id)
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if not project.assets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project must have at least one asset"
            )
        
        if not project.prompt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project must have a prompt"
            )
        
        # Create job record
        new_job = Job(
            project_id=project.id,
            status=JobStatus.PENDING
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        
        # Dispatch Celery task
        try:
            celery_task = celery_app.send_task(
                "app.workers.tasks.process_edit_job",
                args=[project.id, project.prompt],
                task_id=f"job-{new_job.id}"
            )
            
            new_job.celery_task_id = celery_task.id
            new_job.status = JobStatus.PROCESSING
            db.commit()
            db.refresh(new_job)
            
            logger.info(f"Edit job started: {new_job.id} for project {project.id}")
        except Exception as e:
            logger.error(f"Error dispatching Celery task: {str(e)}")
            new_job.status = JobStatus.FAILED
            new_job.error_message = "Failed to dispatch task"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error starting edit job"
            )
        
        return StartEditResponse(
            job_id=new_job.id,
            celery_task_id=celery_task.id,
            status=new_job.status
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error starting edit job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error starting edit job"
        )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get job status"""
    try:
        # Get job and verify ownership
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        project = db.query(Project).filter(
            (Project.id == job.project_id) & (Project.user_id == current_user.id)
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this job"
            )
        
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting job status"
        )


@router.get("/project/{project_id}/latest", response_model=JobResponse)
async def get_latest_job(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get latest job for a project"""
    try:
        # Verify project belongs to user
        project = db.query(Project).filter(
            (Project.id == project_id) & (Project.user_id == current_user.id)
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        job = db.query(Job).filter(
            Job.project_id == project_id
        ).order_by(Job.created_at.desc()).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No jobs found for this project"
            )
        
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting latest job"
        )
