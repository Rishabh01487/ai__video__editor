"""Scene detection using PySceneDetect"""

import logging
from typing import List, Tuple
import os

logger = logging.getLogger(__name__)


class SceneDetector:
    """Detects scene cuts in videos"""
    
    def __init__(self):
        """Initialize scene detector"""
        try:
            from scenedetect import detect, ContentDetector
            self.detect = detect
            self.ContentDetector = ContentDetector
            logger.info("SceneDetector initialized")
        except ImportError:
            logger.warning("scenedetect not available - scenes will not be detected")
            self.detect = None
            self.ContentDetector = None
    
    def detect_scenes(self, video_path: str) -> List[Tuple[float, float]]:
        """
        Detect scene cuts in video and return list of (start_time, end_time) tuples
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of (start_seconds, end_seconds) tuples
        """
        if not self.detect or not self.ContentDetector:
            logger.warning(f"Scene detection not available for {video_path}")
            # Return full video as single scene
            try:
                from moviepy.editor import VideoFileClip
                with VideoFileClip(video_path) as video:
                    duration = video.duration
                return [(0.0, duration)]
            except Exception as e:
                logger.error(f"Error getting video duration: {str(e)}")
                return [(0.0, 60.0)]  # Default fallback
        
        try:
            logger.info(f"Detecting scenes in {video_path}")
            
            # Detect scenes with ContentDetector
            scenes = self.detect(video_path, ContentDetector(threshold=27.0))
            
            # Convert to (start, end) tuples
            scene_list = []
            for i, scene in enumerate(scenes):
                start_time = scene[0].get_seconds()
                if i + 1 < len(scenes):
                    end_time = scenes[i + 1][0].get_seconds()
                else:
                    # Get video duration for last scene
                    try:
                        from moviepy.editor import VideoFileClip
                        with VideoFileClip(video_path) as video:
                            end_time = video.duration
                    except:
                        end_time = start_time + 30
                
                scene_list.append((start_time, end_time))
            
            logger.info(f"Detected {len(scene_list)} scenes")
            return scene_list
        
        except Exception as e:
            logger.error(f"Error detecting scenes: {str(e)}")
            # Fallback: return full video as single scene
            try:
                from moviepy.editor import VideoFileClip
                with VideoFileClip(video_path) as video:
                    duration = video.duration
                return [(0.0, duration)]
            except:
                return [(0.0, 60.0)]


# Global scene detector
scene_detector = SceneDetector()
