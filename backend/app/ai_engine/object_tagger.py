"""Object detection using YOLOv8-nano"""

import logging
from typing import List, Set
import os
import urllib.request

logger = logging.getLogger(__name__)


class ObjectTagger:
    """Tags objects in video frames and images using YOLOv8-nano"""
    
    def __init__(self):
        """Initialize object tagger with YOLOv8-nano model"""
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load YOLOv8-nano model"""
        try:
            from ultralytics import YOLO
            
            # Model name (nano variant is ~6MB)
            model_name = "yolov8n.pt"
            
            # Try to load - ultralytics auto-downloads if not present
            logger.info(f"Loading YOLO model: {model_name}")
            self.model = YOLO(model_name)
            logger.info("YOLOv8-nano model loaded successfully")
        except ImportError:
            logger.warning("ultralytics not available - object detection disabled")
            self.model = None
        except Exception as e:
            logger.error(f"Error loading YOLO model: {str(e)}")
            self.model = None
    
    def tag_image(self, image_path: str) -> Set[str]:
        """
        Detect and tag objects in an image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Set of detected object names (e.g., {'person', 'car', 'dog'})
        """
        if not self.model:
            logger.debug(f"YOLO model not available, returning empty tags for {image_path}")
            return set()
        
        try:
            logger.debug(f"Running inference on image: {image_path}")
            results = self.model(image_path, verbose=False)
            
            objects = set()
            if results and len(results) > 0:
                result = results[0]
                if hasattr(result, 'names') and hasattr(result, 'boxes'):
                    for box in result.boxes:
                        class_id = int(box.cls)
                        object_name = result.names[class_id]
                        objects.add(object_name.lower())
            
            logger.debug(f"Detected objects in image: {objects}")
            return objects
        except Exception as e:
            logger.error(f"Error tagging image: {str(e)}")
            return set()
    
    def tag_video(self, video_path: str, sample_frames: int = 5) -> Set[str]:
        """
        Detect and tag objects in video by sampling frames
        
        Args:
            video_path: Path to video file
            sample_frames: Number of frames to sample
            
        Returns:
            Set of detected object names
        """
        if not self.model:
            logger.debug(f"YOLO model not available, returning empty tags for {video_path}")
            return set()
        
        try:
            from moviepy.editor import VideoFileClip
            import numpy as np
            
            logger.info(f"Tagging video: {video_path} (sampling {sample_frames} frames)")
            
            all_objects = set()
            
            with VideoFileClip(video_path) as video:
                duration = video.duration
                fps = video.fps if hasattr(video, 'fps') else 24
                total_frames = int(duration * fps)
                
                if total_frames < sample_frames:
                    sample_frames = max(1, total_frames)
                
                # Sample frames evenly throughout video
                frame_indices = np.linspace(0, total_frames - 1, sample_frames, dtype=int)
                
                for frame_idx in frame_indices:
                    try:
                        timestamp = frame_idx / fps
                        frame = video.get_frame(timestamp)
                        
                        # Run inference on frame
                        results = self.model(frame, verbose=False)
                        
                        if results and len(results) > 0:
                            result = results[0]
                            if hasattr(result, 'names') and hasattr(result, 'boxes'):
                                for box in result.boxes:
                                    class_id = int(box.cls)
                                    object_name = result.names[class_id]
                                    all_objects.add(object_name.lower())
                    except Exception as e:
                        logger.warning(f"Error processing frame {frame_idx}: {str(e)}")
                        continue
            
            logger.debug(f"Detected objects in video: {all_objects}")
            return all_objects
        except Exception as e:
            logger.error(f"Error tagging video: {str(e)}")
            return set()


# Global object tagger
object_tagger = ObjectTagger()
