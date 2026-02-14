"""Prompt parser - rule-based interpretation of user prompts"""

import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)


class PromptParser:
    """Parse user prompts into editing directives using rule-based parsing"""
    
    # Keywords for different directives
    DURATION_KEYWORDS = {
        'second', 'seconds', 's', 'minute', 'minutes', 'm'
    }
    
    FILTER_KEYWORDS = {
        'vintage': 'vintage',
        'black and white': 'grayscale',
        'b&w': 'grayscale',
        'bw': 'grayscale',
        'sepia': 'sepia',
        'cool': 'cool',
        'warm': 'warm'
    }
    
    SPEED_KEYWORDS = {
        'slow motion': 'slow',
        'slow-motion': 'slow',
        'slowmotion': 'slow',
        'slo-mo': 'slow',
        'fast': 'fast',
        'speed up': 'fast',
        'speedup': 'fast'
    }
    
    MUSIC_KEYWORDS = {
        'music': 'upbeat',
        'song': 'upbeat',
        'beat': 'upbeat',
        'upbeat': 'upbeat',
        'calm': 'calm',
        'relaxing': 'calm',
        'energetic': 'upbeat',
        'epic': 'epic'
    }
    
    INCLUDE_EXCLUDE_KEYWORDS = {
        'include', 'only', 'show', 'feature',
        'exclude', 'remove', 'hide', 'skip'
    }
    
    def parse(self, prompt: str) -> Dict:
        """
        Parse prompt into structured directives
        
        Args:
            prompt: User's text prompt
            
        Returns:
            Dictionary with directives
        """
        prompt_lower = prompt.lower()
        
        directives = {
            'duration_target': self._extract_duration(prompt_lower),
            'filter': self._extract_filter(prompt_lower),
            'speed': self._extract_speed(prompt_lower),
            'music': self._extract_music(prompt_lower),
            'include_tags': self._extract_include_tags(prompt_lower),
            'exclude_tags': self._extract_exclude_tags(prompt_lower),
            'style': self._extract_style(prompt_lower)
        }
        
        logger.debug(f"Parsed prompt directives: {directives}")
        return directives
    
    def _extract_duration(self, prompt: str) -> int:
        """Extract target duration in seconds"""
        try:
            # Look for patterns like "30 seconds", "2 minutes", etc.
            patterns = [
                r'(\d+)\s*(?:second|sec|s)(?:\s|$)',  # seconds
                r'(\d+)\s*(?:minute|min|m)(?:\s|$)',   # minutes
            ]
            
            for pattern in patterns:
                match = re.search(pattern, prompt)
                if match:
                    value = int(match.group(1))
                    if 'minute' in pattern or 'min' in pattern or ' m' in pattern:
                        value *= 60  # Convert to seconds
                    logger.debug(f"Extracted duration: {value} seconds")
                    return value
        except Exception as e:
            logger.debug(f"Error extracting duration: {e}")
        
        # Default to 60 seconds
        return 60
    
    def _extract_filter(self, prompt: str) -> str:
        """Extract visual filter/effect"""
        for keyword, filter_name in self.FILTER_KEYWORDS.items():
            if keyword in prompt:
                logger.debug(f"Extracted filter: {filter_name}")
                return filter_name
        return "none"
    
    def _extract_speed(self, prompt: str) -> str:
        """Extract speed modification"""
        for keyword, speed in self.SPEED_KEYWORDS.items():
            if keyword in prompt:
                logger.debug(f"Extracted speed: {speed}")
                return speed
        return "normal"
    
    def _extract_music(self, prompt: str) -> str:
        """Extract music/audio mood"""
        for keyword, mood in self.MUSIC_KEYWORDS.items():
            if keyword in prompt:
                logger.debug(f"Extracted music mood: {mood}")
                return mood
        return None
    
    def _extract_include_tags(self, prompt: str) -> List[str]:
        """Extract objects/people to include"""
        tags = []
        try:
            # Look for patterns like "include person", "only people", "show cars"
            patterns = [
                r'(?:include|only|show|feature)\s+([a-z\s]+?)(?:\s+(?:and|,|or|in the|$))',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, prompt)
                for match in matches:
                    # Clean up match
                    items = [item.strip() for item in match.split()]
                    tags.extend(items)
        except Exception as e:
            logger.debug(f"Error extracting include tags: {e}")
        
        logger.debug(f"Extracted include tags: {tags}")
        return list(set(tags))  # Remove duplicates
    
    def _extract_exclude_tags(self, prompt: str) -> List[str]:
        """Extract objects/people to exclude"""
        tags = []
        try:
            # Look for patterns like "exclude person", "remove people", "hide cars"
            patterns = [
                r'(?:exclude|remove|hide|skip)\s+([a-z\s]+?)(?:\s+(?:and|,|or|in the|$))',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, prompt)
                for match in matches:
                    # Clean up match
                    items = [item.strip() for item in match.split()]
                    tags.extend(items)
        except Exception as e:
            logger.debug(f"Error extracting exclude tags: {e}")
        
        logger.debug(f"Extracted exclude tags: {tags}")
        return list(set(tags))  # Remove duplicates
    
    def _extract_style(self, prompt: str) -> str:
        """Extract editing style"""
        style_keywords = {
            'cinematic': 'cinematic',
            'montage': 'montage',
            'highlights': 'highlights',
            'vlog': 'vlog'
        }
        
        for keyword, style in style_keywords.items():
            if keyword in prompt:
                logger.debug(f"Extracted style: {style}")
                return style
        return "default"


# Global prompt parser
prompt_parser = PromptParser()
