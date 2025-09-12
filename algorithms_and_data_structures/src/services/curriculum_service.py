"""
Curriculum Service - Business logic for curriculum operations
Manages learning paths, topics, and educational content structure.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import asdict
from datetime import datetime, timedelta

from models.content_models import Topic, Problem, Concept, LearningPath
from models.user_profile import UserProfile, UserProgress
from data.database_manager import DatabaseManager
from utils.logging_config import get_logger


class CurriculumService:
    """
    Service for managing curriculum structure, learning paths,
    and educational content organization.
    """
    
    def __init__(self, db_manager: DatabaseManager, config: Dict[str, Any]):
        """
        Initialize the curriculum service.
        
        Args:
            db_manager: Database manager instance
            config: Application configuration
        """
        self.db_manager = db_manager
        self.config = config
        self.logger = get_logger(__name__)
        
        # Cache for frequently accessed data
        self._topics_cache: Optional[List[Topic]] = None
        self._learning_paths_cache: Optional[List[LearningPath]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=30)  # Cache for 30 minutes
        
        self.logger.info("Curriculum service initialized")
    
    def get_all_topics(self, force_refresh: bool = False) -> List[Topic]:
        """
        Get all available topics with caching.
        
        Args:
            force_refresh: Force refresh of cache
            
        Returns:
            List of all topics
        """
        try:
            # Check cache validity
            if (not force_refresh and 
                self._topics_cache and 
                self._cache_timestamp and 
                datetime.now() - self._cache_timestamp < self._cache_ttl):
                return self._topics_cache
            
            # Fetch from database
            topics = self.db_manager.get_all_topics()
            
            # Update cache
            self._topics_cache = topics
            self._cache_timestamp = datetime.now()
            
            self.logger.info(f"Loaded {len(topics)} topics")
            return topics
            
        except Exception as e:
            self.logger.error(f"Failed to get topics: {str(e)}")
            raise
    
    def get_topic_by_name(self, name: str) -> Optional[Topic]:
        """
        Get a specific topic by name.
        
        Args:
            name: Topic name
            
        Returns:
            Topic if found, None otherwise
        """
        try:
            topics = self.get_all_topics()
            for topic in topics:
                if topic.name.lower() == name.lower():
                    return topic
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get topic '{name}': {str(e)}")
            return None
    
    def get_topics_by_difficulty(self, difficulty: str) -> List[Topic]:
        """
        Get topics filtered by difficulty level.
        
        Args:
            difficulty: Difficulty level (beginner, intermediate, advanced)
            
        Returns:
            List of topics matching difficulty
        """
        try:
            topics = self.get_all_topics()
            filtered_topics = [
                topic for topic in topics 
                if topic.difficulty.lower() == difficulty.lower()
            ]
            
            self.logger.info(f"Found {len(filtered_topics)} topics with difficulty '{difficulty}'")
            return filtered_topics
            
        except Exception as e:
            self.logger.error(f"Failed to get topics by difficulty '{difficulty}': {str(e)}")
            return []
    
    def get_topic_prerequisites(self, topic_name: str) -> List[str]:
        """
        Get prerequisite topics for a given topic.
        
        Args:
            topic_name: Name of the topic
            
        Returns:
            List of prerequisite topic names
        """
        try:
            topic = self.get_topic_by_name(topic_name)
            if topic:
                return topic.prerequisites
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to get prerequisites for '{topic_name}': {str(e)}")
            return []
    
    def get_topic_dependents(self, topic_name: str) -> List[str]:
        """
        Get topics that depend on the given topic.
        
        Args:
            topic_name: Name of the topic
            
        Returns:
            List of dependent topic names
        """
        try:
            all_topics = self.get_all_topics()
            dependents = []
            
            for topic in all_topics:
                if topic_name in topic.prerequisites:
                    dependents.append(topic.name)
            
            self.logger.info(f"Found {len(dependents)} dependents for '{topic_name}'")
            return dependents
            
        except Exception as e:
            self.logger.error(f"Failed to get dependents for '{topic_name}': {str(e)}")
            return []
    
    def get_learning_paths(self, force_refresh: bool = False) -> List[LearningPath]:
        """
        Get all learning paths with caching.
        
        Args:
            force_refresh: Force refresh of cache
            
        Returns:
            List of learning paths
        """
        try:
            # Check cache validity
            if (not force_refresh and 
                self._learning_paths_cache and 
                self._cache_timestamp and 
                datetime.now() - self._cache_timestamp < self._cache_ttl):
                return self._learning_paths_cache
            
            # Fetch from database
            learning_paths = self.db_manager.get_all_learning_paths()
            
            # Update cache
            self._learning_paths_cache = learning_paths
            self._cache_timestamp = datetime.now()
            
            self.logger.info(f"Loaded {len(learning_paths)} learning paths")
            return learning_paths
            
        except Exception as e:
            self.logger.error(f"Failed to get learning paths: {str(e)}")
            raise
    
    def get_recommended_learning_path(self, user_profile: UserProfile) -> Optional[LearningPath]:
        """
        Get recommended learning path based on user profile.
        
        Args:
            user_profile: User profile
            
        Returns:
            Recommended learning path or None
        """
        try:
            learning_paths = self.get_learning_paths()
            user_level = self._determine_user_level(user_profile)
            user_goals = user_profile.learning_goals
            
            # Score learning paths based on user profile
            path_scores = []
            for path in learning_paths:
                score = self._score_learning_path(path, user_level, user_goals)
                path_scores.append((path, score))
            
            # Return highest scoring path
            if path_scores:
                best_path = max(path_scores, key=lambda x: x[1])[0]
                self.logger.info(f"Recommended learning path: {best_path.name}")
                return best_path
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get recommended learning path: {str(e)}")
            return None
    
    def get_next_topics_in_path(self, learning_path: LearningPath, 
                               user_progress: UserProgress) -> List[str]:
        """
        Get next topics to study in a learning path based on user progress.
        
        Args:
            learning_path: Learning path
            user_progress: User's progress data
            
        Returns:
            List of next topic names to study
        """
        try:
            completed_topics = set(user_progress.completed_topics)
            path_topics = learning_path.topics
            
            # Find topics that can be started (prerequisites met)
            available_topics = []
            for topic_name in path_topics:
                if topic_name not in completed_topics:
                    prerequisites = self.get_topic_prerequisites(topic_name)
                    if all(prereq in completed_topics for prereq in prerequisites):
                        available_topics.append(topic_name)
            
            # Limit to recommended number of concurrent topics
            max_concurrent = self.config.get('max_concurrent_topics', 3)
            next_topics = available_topics[:max_concurrent]
            
            self.logger.info(f"Next topics in path '{learning_path.name}': {next_topics}")
            return next_topics
            
        except Exception as e:
            self.logger.error(f"Failed to get next topics in path: {str(e)}")
            return []
    
    def validate_topic_sequence(self, topic_names: List[str]) -> Dict[str, Any]:
        """
        Validate if a sequence of topics respects prerequisites.
        
        Args:
            topic_names: List of topic names in sequence
            
        Returns:
            Validation result with details
        """
        try:
            validation_result = {
                'is_valid': True,
                'issues': [],
                'missing_prerequisites': [],
                'suggested_order': []
            }
            
            completed_topics = set()
            
            for i, topic_name in enumerate(topic_names):
                prerequisites = self.get_topic_prerequisites(topic_name)
                missing_prereqs = [prereq for prereq in prerequisites 
                                 if prereq not in completed_topics]
                
                if missing_prereqs:
                    validation_result['is_valid'] = False
                    validation_result['issues'].append(
                        f"Topic '{topic_name}' at position {i} is missing prerequisites: {missing_prereqs}"
                    )
                    validation_result['missing_prerequisites'].extend(missing_prereqs)
                
                completed_topics.add(topic_name)
            
            # Generate suggested order if there are issues
            if not validation_result['is_valid']:
                validation_result['suggested_order'] = self._generate_valid_sequence(topic_names)
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Failed to validate topic sequence: {str(e)}")
            return {'is_valid': False, 'error': str(e)}
    
    def create_custom_learning_path(self, name: str, description: str, 
                                  topic_names: List[str], 
                                  user_profile: UserProfile) -> LearningPath:
        """
        Create a custom learning path for a user.
        
        Args:
            name: Path name
            description: Path description
            topic_names: List of topic names
            user_profile: User profile
            
        Returns:
            Created learning path
        """
        try:
            # Validate topic sequence
            validation = self.validate_topic_sequence(topic_names)
            if not validation['is_valid']:
                # Use suggested order
                topic_names = validation['suggested_order']
                self.logger.warning(f"Used suggested topic order: {topic_names}")
            
            # Create learning path
            learning_path = LearningPath(
                name=name,
                description=description,
                topics=topic_names,
                difficulty=self._determine_path_difficulty(topic_names),
                estimated_duration=self._estimate_path_duration(topic_names),
                created_by=user_profile.name,
                is_custom=True
            )
            
            # Save to database
            self.db_manager.save_learning_path(learning_path)
            
            # Clear cache to include new path
            self._learning_paths_cache = None
            
            self.logger.info(f"Created custom learning path: {name}")
            return learning_path
            
        except Exception as e:
            self.logger.error(f"Failed to create custom learning path: {str(e)}")
            raise
    
    def get_topic_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about topics and curriculum.
        
        Returns:
            Dictionary with statistics
        """
        try:
            topics = self.get_all_topics()
            
            stats = {
                'total_topics': len(topics),
                'difficulty_distribution': {},
                'topics_with_prerequisites': 0,
                'average_concepts_per_topic': 0,
                'average_problems_per_topic': 0,
                'topics_by_category': {}
            }
            
            # Calculate statistics
            difficulty_counts = {}
            total_concepts = 0
            total_problems = 0
            category_counts = {}
            
            for topic in topics:
                # Difficulty distribution
                difficulty = topic.difficulty
                difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
                
                # Prerequisites
                if topic.prerequisites:
                    stats['topics_with_prerequisites'] += 1
                
                # Concepts and problems
                total_concepts += len(topic.concepts)
                total_problems += len(topic.problems)
                
                # Categories
                for category in topic.categories:
                    category_counts[category] = category_counts.get(category, 0) + 1
            
            stats['difficulty_distribution'] = difficulty_counts
            stats['average_concepts_per_topic'] = total_concepts / len(topics) if topics else 0
            stats['average_problems_per_topic'] = total_problems / len(topics) if topics else 0
            stats['topics_by_category'] = category_counts
            
            self.logger.info("Generated topic statistics")
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get topic statistics: {str(e)}")
            return {}
    
    def _determine_user_level(self, user_profile: UserProfile) -> str:
        """Determine user's current level based on profile."""
        # Simple heuristic - can be made more sophisticated
        if hasattr(user_profile, 'progress') and user_profile.progress:
            completed_topics = len(user_profile.progress.completed_topics)
            if completed_topics < 5:
                return 'beginner'
            elif completed_topics < 15:
                return 'intermediate'
            else:
                return 'advanced'
        return 'beginner'
    
    def _score_learning_path(self, path: LearningPath, user_level: str, 
                           user_goals: List[str]) -> float:
        """Score a learning path for a user."""
        score = 0.0
        
        # Difficulty match
        if path.difficulty == user_level:
            score += 0.4
        elif abs(['beginner', 'intermediate', 'advanced'].index(path.difficulty) - 
                ['beginner', 'intermediate', 'advanced'].index(user_level)) == 1:
            score += 0.2
        
        # Goal alignment
        if user_goals:
            path_topics = set(path.topics)
            goal_matches = sum(1 for goal in user_goals if goal.lower() in 
                             ' '.join(path_topics).lower())
            score += 0.6 * (goal_matches / len(user_goals))
        
        return score
    
    def _generate_valid_sequence(self, topic_names: List[str]) -> List[str]:
        """Generate a valid topic sequence respecting prerequisites."""
        # Topological sort of topics
        topics_set = set(topic_names)
        in_degree = {}
        graph = {}
        
        # Initialize
        for topic in topic_names:
            in_degree[topic] = 0
            graph[topic] = []
        
        # Build graph
        for topic in topic_names:
            prerequisites = self.get_topic_prerequisites(topic)
            for prereq in prerequisites:
                if prereq in topics_set:
                    graph[prereq].append(topic)
                    in_degree[topic] += 1
        
        # Topological sort
        queue = [topic for topic in topic_names if in_degree[topic] == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def _determine_path_difficulty(self, topic_names: List[str]) -> str:
        """Determine overall difficulty of a learning path."""
        topics = [self.get_topic_by_name(name) for name in topic_names]
        topics = [topic for topic in topics if topic is not None]
        
        if not topics:
            return 'beginner'
        
        difficulty_weights = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
        avg_difficulty = sum(difficulty_weights[topic.difficulty] for topic in topics) / len(topics)
        
        if avg_difficulty <= 1.5:
            return 'beginner'
        elif avg_difficulty <= 2.5:
            return 'intermediate'
        else:
            return 'advanced'
    
    def _estimate_path_duration(self, topic_names: List[str]) -> int:
        """Estimate duration for completing a learning path (in hours)."""
        # Simple estimation - can be improved with actual data
        base_hours_per_topic = self.config.get('base_hours_per_topic', 8)
        return len(topic_names) * base_hours_per_topic
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._topics_cache = None
        self._learning_paths_cache = None
        self._cache_timestamp = None
        self.logger.info("Curriculum service cache cleared")