"""
Zone of Proximal Development (ZPD) System
Implements adaptive difficulty based on Vygotsky's educational theory
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import statistics
import math


class DifficultyLevel(Enum):
    """Difficulty levels for content"""
    VERY_EASY = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    VERY_HARD = 5


class LearningState(Enum):
    """Current learning state of the user"""
    FRUSTRATION = "frustration"      # Too difficult, needs easier content
    ZPD_LOWER = "zpd_lower"         # Lower end of ZPD, slight challenge
    ZPD_OPTIMAL = "zpd_optimal"     # Optimal challenge level
    ZPD_UPPER = "zpd_upper"         # Upper end of ZPD, higher challenge
    MASTERY = "mastery"             # Too easy, needs harder content


@dataclass
class SkillAssessment:
    """Assessment of a specific skill"""
    skill_name: str
    current_level: float  # 0.0 to 1.0
    confidence: float     # 0.0 to 1.0
    last_assessment: datetime
    trend: float         # Positive = improving, Negative = declining
    stability: float     # How consistent the performance is
    practice_time: int   # Minutes spent practicing this skill
    
    @property
    def mastery_level(self) -> str:
        """Determine mastery level"""
        if self.current_level >= 0.9 and self.confidence >= 0.8:
            return "expert"
        elif self.current_level >= 0.75:
            return "proficient"
        elif self.current_level >= 0.6:
            return "intermediate"
        elif self.current_level >= 0.4:
            return "developing"
        else:
            return "novice"


@dataclass
class ZPDProfile:
    """User's Zone of Proximal Development profile"""
    user_id: str
    skill_assessments: Dict[str, SkillAssessment]
    current_zpd_range: Tuple[float, float]  # (lower_bound, upper_bound)
    optimal_difficulty: float  # 0.0 to 1.0
    frustration_threshold: float
    mastery_threshold: float
    learning_velocity: float  # How quickly user learns
    preferred_challenge_level: float
    last_updated: datetime


class ZPDSystem:
    """Zone of Proximal Development system for adaptive difficulty"""
    
    def __init__(self, 
                 initial_zpd_width: float = 0.3,
                 min_zpd_width: float = 0.15,
                 max_zpd_width: float = 0.5,
                 adaptation_rate: float = 0.1):
        """
        Initialize ZPD system
        
        Args:
            initial_zpd_width: Initial width of ZPD range
            min_zpd_width: Minimum ZPD width
            max_zpd_width: Maximum ZPD width
            adaptation_rate: Rate at which ZPD adapts to performance
        """
        self.initial_zpd_width = initial_zpd_width
        self.min_zpd_width = min_zpd_width
        self.max_zpd_width = max_zpd_width
        self.adaptation_rate = adaptation_rate
        
        # User profiles
        self.user_profiles: Dict[str, ZPDProfile] = {}
        
        # Skill categories for Spanish learning
        self.skill_categories = {
            'vocabulary': ['basic_words', 'advanced_words', 'idiomatic_expressions', 'collocations'],
            'grammar': ['present_tense', 'past_tenses', 'future_tense', 'subjunctive', 'conditionals', 'imperatives'],
            'listening': ['slow_speech', 'normal_speed', 'fast_speech', 'accents', 'background_noise'],
            'reading': ['simple_texts', 'complex_texts', 'literary_texts', 'technical_texts'],
            'speaking': ['pronunciation', 'fluency', 'accuracy', 'spontaneity'],
            'writing': ['basic_sentences', 'paragraphs', 'essays', 'formal_writing'],
            'culture': ['customs', 'history', 'current_events', 'regional_differences']
        }
    
    def initialize_user_profile(self, 
                               user_id: str, 
                               initial_assessment: Dict[str, float] = None) -> ZPDProfile:
        """
        Initialize a new user profile
        
        Args:
            user_id: User identifier
            initial_assessment: Initial skill assessments (skill_name: level)
            
        Returns:
            Created ZPD profile
        """
        skill_assessments = {}
        
        # Create skill assessments
        for category, skills in self.skill_categories.items():
            for skill in skills:
                initial_level = 0.3  # Default beginner level
                if initial_assessment and skill in initial_assessment:
                    initial_level = initial_assessment[skill]
                
                skill_assessments[skill] = SkillAssessment(
                    skill_name=skill,
                    current_level=initial_level,
                    confidence=0.5,
                    last_assessment=datetime.now(),
                    trend=0.0,
                    stability=0.5,
                    practice_time=0
                )
        
        # Calculate initial ZPD range
        avg_skill_level = statistics.mean(skill.current_level for skill in skill_assessments.values())
        zpd_lower = max(0.0, avg_skill_level - self.initial_zpd_width / 2)
        zpd_upper = min(1.0, avg_skill_level + self.initial_zpd_width / 2)
        
        profile = ZPDProfile(
            user_id=user_id,
            skill_assessments=skill_assessments,
            current_zpd_range=(zpd_lower, zpd_upper),
            optimal_difficulty=avg_skill_level + self.initial_zpd_width / 4,  # Slightly above current level
            frustration_threshold=0.3,  # Success rate below this causes frustration
            mastery_threshold=0.85,     # Success rate above this indicates mastery
            learning_velocity=1.0,
            preferred_challenge_level=0.65,  # Moderate challenge preference
            last_updated=datetime.now()
        )
        
        self.user_profiles[user_id] = profile
        return profile
    
    def update_skill_assessment(self, 
                               user_id: str, 
                               skill_name: str,
                               performance_score: float,
                               confidence_score: float,
                               response_time: float,
                               difficulty_attempted: float) -> None:
        """
        Update skill assessment based on performance
        
        Args:
            user_id: User identifier
            skill_name: Name of the skill
            performance_score: Performance score (0.0 to 1.0)
            confidence_score: User's confidence in their response
            response_time: Time taken for response
            difficulty_attempted: Difficulty level of the content attempted
        """
        if user_id not in self.user_profiles:
            self.initialize_user_profile(user_id)
        
        profile = self.user_profiles[user_id]
        
        if skill_name not in profile.skill_assessments:
            # Create new skill assessment
            profile.skill_assessments[skill_name] = SkillAssessment(
                skill_name=skill_name,
                current_level=0.3,
                confidence=0.5,
                last_assessment=datetime.now(),
                trend=0.0,
                stability=0.5,
                practice_time=0
            )
        
        skill = profile.skill_assessments[skill_name]
        
        # Update skill level using weighted average with performance
        previous_level = skill.current_level
        
        # Weight the performance score by difficulty attempted
        adjusted_performance = performance_score * (0.5 + 0.5 * difficulty_attempted)
        
        # Use exponential moving average for smooth updates
        alpha = 0.2  # Learning rate
        skill.current_level = (1 - alpha) * skill.current_level + alpha * adjusted_performance
        skill.current_level = max(0.0, min(1.0, skill.current_level))
        
        # Update confidence
        skill.confidence = (1 - alpha) * skill.confidence + alpha * confidence_score
        
        # Calculate trend
        skill.trend = skill.current_level - previous_level
        
        # Update stability (inverse of recent variance)
        recent_changes = getattr(skill, 'recent_changes', [])
        recent_changes.append(skill.trend)
        recent_changes = recent_changes[-10:]  # Keep last 10 changes
        
        if len(recent_changes) > 1:
            variance = statistics.variance(recent_changes)
            skill.stability = max(0.1, 1.0 - variance)
        
        skill.recent_changes = recent_changes
        skill.last_assessment = datetime.now()
        
        # Update practice time (estimate based on response time)
        skill.practice_time += int(response_time / 60)  # Convert to minutes
        
        # Recalculate ZPD range
        self._recalculate_zpd(profile)
    
    def get_recommended_difficulty(self, 
                                 user_id: str, 
                                 skill_name: str,
                                 content_type: str = "mixed") -> Tuple[float, str]:
        """
        Get recommended difficulty for a skill
        
        Args:
            user_id: User identifier
            skill_name: Name of the skill
            content_type: Type of content being presented
            
        Returns:
            Tuple of (difficulty_level, learning_state)
        """
        if user_id not in self.user_profiles:
            return 0.3, LearningState.ZPD_LOWER.value
        
        profile = self.user_profiles[user_id]
        
        if skill_name not in profile.skill_assessments:
            return 0.3, LearningState.ZPD_LOWER.value
        
        skill = profile.skill_assessments[skill_name]
        
        # Calculate target difficulty based on ZPD
        zpd_lower, zpd_upper = profile.current_zpd_range
        
        # Adjust based on skill-specific performance
        skill_adjustment = (skill.current_level - 0.5) * 0.2
        
        # Adjust based on confidence
        confidence_adjustment = (skill.confidence - 0.5) * 0.1
        
        # Adjust based on learning trend
        trend_adjustment = skill.trend * 2.0  # Recent improvement suggests readiness for harder content
        
        # Calculate recommended difficulty
        base_difficulty = profile.optimal_difficulty
        adjusted_difficulty = base_difficulty + skill_adjustment + confidence_adjustment + trend_adjustment
        
        # Ensure difficulty is within reasonable bounds
        adjusted_difficulty = max(0.1, min(0.9, adjusted_difficulty))
        
        # Determine learning state
        learning_state = self._determine_learning_state(skill, adjusted_difficulty, zpd_lower, zpd_upper)
        
        return adjusted_difficulty, learning_state.value
    
    def analyze_learning_progress(self, user_id: str, days_back: int = 7) -> Dict[str, Any]:
        """
        Analyze learning progress over time
        
        Args:
            user_id: User identifier
            days_back: Number of days to analyze
            
        Returns:
            Analysis results
        """
        if user_id not in self.user_profiles:
            return {}
        
        profile = self.user_profiles[user_id]
        
        # Calculate overall progress
        skill_levels = [skill.current_level for skill in profile.skill_assessments.values()]
        avg_skill_level = statistics.mean(skill_levels)
        skill_variance = statistics.variance(skill_levels) if len(skill_levels) > 1 else 0
        
        # Identify strengths and weaknesses
        strengths = [
            skill.skill_name for skill in profile.skill_assessments.values()
            if skill.current_level >= avg_skill_level + 0.1
        ]
        
        weaknesses = [
            skill.skill_name for skill in profile.skill_assessments.values()
            if skill.current_level <= avg_skill_level - 0.1
        ]
        
        # Calculate learning velocity
        improving_skills = [
            skill.skill_name for skill in profile.skill_assessments.values()
            if skill.trend > 0.05
        ]
        
        declining_skills = [
            skill.skill_name for skill in profile.skill_assessments.values()
            if skill.trend < -0.05
        ]
        
        # ZPD analysis
        zpd_width = profile.current_zpd_range[1] - profile.current_zpd_range[0]
        zpd_position = (profile.optimal_difficulty - profile.current_zpd_range[0]) / max(0.01, zpd_width)
        
        return {
            'overall_level': avg_skill_level,
            'skill_consistency': 1.0 - skill_variance,
            'zpd_range': profile.current_zpd_range,
            'zpd_width': zpd_width,
            'optimal_difficulty': profile.optimal_difficulty,
            'learning_velocity': profile.learning_velocity,
            'strengths': strengths[:5],  # Top 5 strengths
            'weaknesses': weaknesses[:5],  # Top 5 weaknesses
            'improving_skills': improving_skills,
            'declining_skills': declining_skills,
            'zpd_utilization': zpd_position,  # How well positioned within ZPD
            'skill_assessments': {
                name: {
                    'level': skill.current_level,
                    'confidence': skill.confidence,
                    'trend': skill.trend,
                    'mastery': skill.mastery_level
                }
                for name, skill in profile.skill_assessments.items()
            }
        }
    
    def get_challenge_adjustment(self, 
                               user_id: str,
                               recent_performance: List[Tuple[float, float]]) -> float:
        """
        Calculate challenge adjustment based on recent performance
        
        Args:
            user_id: User identifier
            recent_performance: List of (performance_score, difficulty_level) tuples
            
        Returns:
            Adjustment factor for difficulty (-0.3 to +0.3)
        """
        if not recent_performance or user_id not in self.user_profiles:
            return 0.0
        
        profile = self.user_profiles[user_id]
        
        # Calculate performance trend
        if len(recent_performance) < 3:
            return 0.0
        
        # Check if user is consistently succeeding or failing
        recent_scores = [score for score, _ in recent_performance[-5:]]
        recent_difficulties = [diff for _, diff in recent_performance[-5:]]
        
        avg_score = statistics.mean(recent_scores)
        avg_difficulty = statistics.mean(recent_difficulties)
        
        # Calculate adjustment based on performance zone
        if avg_score > profile.mastery_threshold:
            # User is finding content too easy - increase difficulty
            adjustment = min(0.3, (avg_score - profile.mastery_threshold) * 2.0)
        elif avg_score < profile.frustration_threshold:
            # User is struggling - decrease difficulty
            adjustment = max(-0.3, (avg_score - profile.frustration_threshold) * 2.0)
        else:
            # User is in good learning zone - minor adjustments
            target_score = 0.7  # Target success rate
            adjustment = (avg_score - target_score) * 0.1
        
        # Consider difficulty context
        difficulty_factor = avg_difficulty - 0.5  # Center around 0.5
        adjustment += difficulty_factor * 0.1
        
        return max(-0.3, min(0.3, adjustment))
    
    def _recalculate_zpd(self, profile: ZPDProfile) -> None:
        """Recalculate ZPD range based on current skill levels"""
        skill_levels = [skill.current_level for skill in profile.skill_assessments.values()]
        confidences = [skill.confidence for skill in profile.skill_assessments.values()]
        
        if not skill_levels:
            return
        
        # Calculate weighted average skill level
        weights = [conf * (1 + skill.stability) for skill, conf in 
                  zip(profile.skill_assessments.values(), confidences)]
        
        if sum(weights) > 0:
            weighted_avg = sum(level * weight for level, weight in zip(skill_levels, weights)) / sum(weights)
        else:
            weighted_avg = statistics.mean(skill_levels)
        
        # Calculate skill variance to determine ZPD width
        skill_variance = statistics.variance(skill_levels) if len(skill_levels) > 1 else 0.1
        
        # Adaptive ZPD width based on skill consistency
        zpd_width = max(self.min_zpd_width, 
                       min(self.max_zpd_width, 
                           self.initial_zpd_width + skill_variance * 0.5))
        
        # Update ZPD range
        zpd_lower = max(0.0, weighted_avg - zpd_width / 2)
        zpd_upper = min(1.0, weighted_avg + zpd_width / 2)
        
        profile.current_zpd_range = (zpd_lower, zpd_upper)
        profile.optimal_difficulty = weighted_avg + zpd_width / 4
        profile.last_updated = datetime.now()
        
        # Update learning velocity based on recent trends
        recent_trends = [skill.trend for skill in profile.skill_assessments.values() 
                        if abs(skill.trend) > 0.01]  # Only significant trends
        
        if recent_trends:
            avg_trend = statistics.mean(recent_trends)
            profile.learning_velocity = max(0.3, min(2.0, 1.0 + avg_trend * 10))
    
    def _determine_learning_state(self, 
                                skill: SkillAssessment, 
                                difficulty: float,
                                zpd_lower: float, 
                                zpd_upper: float) -> LearningState:
        """Determine current learning state"""
        skill_level = skill.current_level
        
        # Consider both skill level and attempted difficulty
        performance_gap = difficulty - skill_level
        
        if performance_gap > 0.4:  # Much too difficult
            return LearningState.FRUSTRATION
        elif performance_gap > 0.2:  # Quite challenging
            return LearningState.ZPD_UPPER
        elif performance_gap > 0.05:  # Moderately challenging
            return LearningState.ZPD_OPTIMAL
        elif performance_gap > -0.1:  # Slight challenge
            return LearningState.ZPD_LOWER
        else:  # Too easy
            return LearningState.MASTERY
    
    def export_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Export user profile for persistence"""
        if user_id not in self.user_profiles:
            return None
        
        profile = self.user_profiles[user_id]
        
        return {
            'user_id': profile.user_id,
            'skill_assessments': {
                name: {
                    'skill_name': skill.skill_name,
                    'current_level': skill.current_level,
                    'confidence': skill.confidence,
                    'last_assessment': skill.last_assessment.isoformat(),
                    'trend': skill.trend,
                    'stability': skill.stability,
                    'practice_time': skill.practice_time,
                    'mastery_level': skill.mastery_level
                }
                for name, skill in profile.skill_assessments.items()
            },
            'zpd_range': profile.current_zpd_range,
            'optimal_difficulty': profile.optimal_difficulty,
            'thresholds': {
                'frustration': profile.frustration_threshold,
                'mastery': profile.mastery_threshold
            },
            'learning_velocity': profile.learning_velocity,
            'preferred_challenge_level': profile.preferred_challenge_level,
            'last_updated': profile.last_updated.isoformat()
        }