"""Shot/scene selection using dynamic programming"""

import logging
from typing import List, Tuple, Dict, Set
import numpy as np

logger = logging.getLogger(__name__)


class ShotSelector:
    """Selects optimal shots/scenes based on directives and metadata"""
    
    @staticmethod
    def calculate_aesthetic_score(
        scene: Dict,
        has_target_objects: bool = True,
        has_excluded_objects: bool = False
    ) -> float:
        """
        Calculate aesthetic score for a scene
        
        Args:
            scene: Scene metadata
            has_target_objects: Whether scene contains desired objects
            has_excluded_objects: Whether scene contains unwanted objects
            
        Returns:
            Score between 0 and 1
        """
        score = 0.5  # Base score
        
        # Bonus for having target objects
        if has_target_objects:
            score += 0.3
        
        # Penalty for having excluded objects
        if has_excluded_objects:
            score -= 0.2
        
        # Normalize
        score = max(0.0, min(1.0, score))
        return score
    
    @staticmethod
    def knapsack_selection(
        scenes: List[Dict],
        target_duration: float
    ) -> List[Dict]:
        """
        Select subset of scenes to match target duration using dynamic programming
        
        Args:
            scenes: List of scene dictionaries with 'start', 'end', 'score'
            target_duration: Target duration in seconds
            
        Returns:
            List of selected scenes
        """
        if not scenes or target_duration <= 0:
            return []
        
        n = len(scenes)
        
        # Create DP table
        # dp[i][d] = max score using first i scenes with duration d
        dp = {}
        selected = {}
        
        for i in range(n + 1):
            for d in range(int(target_duration * 10) + 1):
                if i == 0 or d == 0:
                    dp[(i, d)] = 0
                    selected[(i, d)] = []
                else:
                    scene = scenes[i - 1]
                    duration = int((scene['end'] - scene['start']) * 10)
                    score = scene.get('score', 0.5)
                    
                    # Don't include this scene
                    dp[(i, d)] = dp[(i - 1, d)]
                    selected[(i, d)] = selected[(i - 1, d)].copy()
                    
                    # Include this scene
                    if d >= duration:
                        current_score = dp[(i - 1, d - duration)] + score
                        if current_score > dp[(i, d)]:
                            dp[(i, d)] = current_score
                            selected[(i, d)] = selected[(i - 1, d - duration)].copy()
                            selected[(i, d)].append(i - 1)
        
        # Find closest to target duration
        best_duration = 0
        best_selected = []
        for d in range(int(target_duration * 10), -1, -1):
            if (n, d) in selected and len(selected[(n, d)]) > 0:
                best_duration = d / 10
                best_selected = selected[(n, d)]
                break
        
        result = [scenes[i] for i in best_selected]
        logger.debug(f"Selected {len(result)} scenes with total duration {best_duration}s")
        return result
    
    @staticmethod
    def select_shots(
        scenes_with_tags: List[Dict],
        target_duration: float,
        include_tags: Set[str],
        exclude_tags: Set[str]
    ) -> List[Dict]:
        """
        Select optimal shots based on tags and duration
        
        Args:
            scenes_with_tags: List of scene dicts with 'start', 'end', 'tags' keys
            target_duration: Target duration in seconds
            include_tags: Set of tags to prioritize
            exclude_tags: Set of tags to avoid
            
        Returns:
            List of selected scenes
        """
        logger.info(f"Selecting shots for {target_duration}s (include: {include_tags}, exclude: {exclude_tags})")
        
        # Score each scene
        scored_scenes = []
        for scene in scenes_with_tags:
            scene_tags = set(scene.get('tags', []))
            
            # Check inclusion
            has_target = any(tag in scene_tags for tag in include_tags) if include_tags else True
            
            # Check exclusion
            has_excluded = any(tag in scene_tags for tag in exclude_tags) if exclude_tags else False
            
            score = ShotSelector.calculate_aesthetic_score(
                scene,
                has_target_objects=has_target,
                has_excluded_objects=has_excluded
            )
            
            scene_copy = scene.copy()
            scene_copy['score'] = score
            scored_scenes.append(scene_copy)
        
        # Select using knapsack
        selected = ShotSelector.knapsack_selection(scored_scenes, target_duration)
        
        logger.info(f"Selected {len(selected)} shots")
        return selected


# Global shot selector
shot_selector = ShotSelector()
