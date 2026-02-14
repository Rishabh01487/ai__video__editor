"""Video rendering using MoviePy"""

import logging
from typing import List, Dict, Optional
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class VideoRenderer:
    """Renders final video from selected shots"""
    
    def __init__(self):
        """Initialize renderer"""
        try:
            from moviepy.editor import (
                VideoFileClip, ImageClip, concatenate_videoclips,
                CompositeVideoClip, TextClip
            )
            self.VideoFileClip = VideoFileClip
            self.ImageClip = ImageClip
            self.concatenate_videoclips = concatenate_videoclips
            self.CompositeVideoClip = CompositeVideoClip
            self.TextClip = TextClip
            logger.info("VideoRenderer initialized")
        except ImportError as e:
            logger.error(f"MoviePy not available: {e}")
            raise
    
    def _apply_filter(self, clip, filter_name: str):
        """Apply visual filter to clip"""
        if filter_name == "none":
            return clip
        
        try:
            if filter_name == "grayscale":
                logger.debug("Applying grayscale filter")
                return clip.fx(lambda f: self._grayscale_frame(f))
            elif filter_name == "sepia":
                logger.debug("Applying sepia filter")
                return clip.fx(lambda f: self._sepia_frame(f))
            elif filter_name == "vintage":
                logger.debug("Applying vintage filter")
                # Vintage = sepia + slight desaturation
                return clip.fx(lambda f: self._vintage_frame(f))
            elif filter_name == "cool":
                logger.debug("Applying cool filter")
                return clip.fx(lambda f: self._cool_frame(f))
            elif filter_name == "warm":
                logger.debug("Applying warm filter")
                return clip.fx(lambda f: self._warm_frame(f))
        except Exception as e:
            logger.warning(f"Error applying filter {filter_name}: {e}")
        
        return clip
    
    @staticmethod
    def _grayscale_frame(frame):
        """Convert frame to grayscale"""
        import numpy as np
        if len(frame.shape) == 3:
            # RGB to grayscale
            gray = np.dot(frame[..., :3], [0.299, 0.587, 0.114])
            return np.dstack([gray, gray, gray]).astype(np.uint8)
        return frame
    
    @staticmethod
    def _sepia_frame(frame):
        """Apply sepia tone"""
        import numpy as np
        sepia_filter = np.array([[0.272, 0.534, 0.131],
                                [0.349, 0.686, 0.168],
                                [0.393, 0.769, 0.189]])
        if len(frame.shape) == 3:
            return np.dot(frame[..., :3], sepia_filter.T).astype(np.uint8)
        return frame
    
    @staticmethod
    def _vintage_frame(frame):
        """Apply vintage effect"""
        import numpy as np
        # Sepia with slight desaturation
        frame = VideoRenderer._sepia_frame(frame)
        # Reduce brightness slightly
        frame = np.clip(frame * 0.95, 0, 255).astype(np.uint8)
        return frame
    
    @staticmethod
    def _cool_frame(frame):
        """Apply cool color tone"""
        import numpy as np
        if len(frame.shape) == 3:
            # Reduce red, enhance blue
            frame = frame.astype(float)
            frame[..., 0] *= 0.9  # Red down
            frame[..., 2] *= 1.1  # Blue up
            return np.clip(frame, 0, 255).astype(np.uint8)
        return frame
    
    @staticmethod
    def _warm_frame(frame):
        """Apply warm color tone"""
        import numpy as np
        if len(frame.shape) == 3:
            # Enhance red, reduce blue
            frame = frame.astype(float)
            frame[..., 0] *= 1.1  # Red up
            frame[..., 2] *= 0.9  # Blue down
            return np.clip(frame, 0, 255).astype(np.uint8)
        return frame
    
    def _apply_speed(self, clip, speed: str):
        """Apply speed modification"""
        if speed == "slow":
            logger.debug("Applying slow motion (0.5x)")
            return clip.speedx(0.5)
        elif speed == "fast":
            logger.debug("Applying fast forward (2x)")
            return clip.speedx(2.0)
        return clip
    
    def render(
        self,
        shots: List[Dict],
        output_path: str,
        filter_name: str = "none",
        speed: str = "normal",
        music_path: Optional[str] = None
    ) -> bool:
        """
        Render final video from shots
        
        Args:
            shots: List of shot dicts with 'video_path', 'start', 'end' keys
            output_path: Output video file path
            filter_name: Filter to apply
            speed: Speed modification
            music_path: Optional path to background music file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Rendering video to {output_path}")
            
            if not shots:
                logger.error("No shots to render")
                return False
            
            # Load and trim shots
            clips = []
            for shot in shots:
                try:
                    video_path = shot['video_path']
                    start = shot.get('start', 0)
                    end = shot.get('end')
                    
                    logger.debug(f"Loading clip: {video_path} ({start}-{end})")
                    
                    clip = self.VideoFileClip(video_path)
                    if end is None:
                        end = clip.duration
                    
                    # Trim clip
                    clip = clip.subclipped(start, end)
                    
                    # Apply filter
                    clip = self._apply_filter(clip, filter_name)
                    
                    # Apply speed
                    clip = self._apply_speed(clip, speed)
                    
                    clips.append(clip)
                except Exception as e:
                    logger.error(f"Error loading clip {shot.get('video_path')}: {e}")
                    continue
            
            if not clips:
                logger.error("No valid clips loaded")
                return False
            
            # Concatenate clips
            logger.debug(f"Concatenating {len(clips)} clips")
            final_clip = self.concatenate_videoclips(clips)
            
            # Add music if provided and exists
            if music_path and os.path.exists(music_path):
                try:
                    logger.info(f"Adding music from {music_path}")
                    from moviepy.editor import AudioFileClip
                    music = AudioFileClip(music_path)
                    # Loop music to match video duration
                    if music.duration < final_clip.duration:
                        from moviepy.audio.io.AudioFileClip import AudioFileClip as AFC
                        from moviepy.editor import concatenate_audioclips
                        # Create list of music clips
                        music_clips = []
                        current_time = 0
                        while current_time < final_clip.duration:
                            music_clips.append(music.subclipped(0, min(music.duration, final_clip.duration - current_time)))
                            current_time += music.duration
                        music = concatenate_audioclips(music_clips)
                    else:
                        music = music.subclipped(0, final_clip.duration)
                    
                    final_clip = final_clip.set_audio(music)
                except Exception as e:
                    logger.warning(f"Error adding music: {e}")
            
            # Create output directory if needed
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Write video with codec optimization
            logger.info(f"Writing video to {output_path}")
            final_clip.write_videofile(
                output_path,
                verbose=False,
                logger=None,
                codec='libx264',
                preset='medium',
                fps=24
            )
            
            logger.info(f"Video rendered successfully: {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error rendering video: {str(e)}")
            return False


# Global renderer
video_renderer = VideoRenderer()
