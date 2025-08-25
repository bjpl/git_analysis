"""
Enhanced SM2 Algorithm for Spaced Repetition
Based on SuperMemo 2 algorithm with improvements for language learning
"""

import math
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ResponseQuality(Enum):
    """Response quality levels for spaced repetition"""
    BLACKOUT = 0        # Complete blackout
    INCORRECT = 1       # Incorrect response with familiar feeling
    DIFFICULT = 2       # Correct response with serious difficulty
    HESITANT = 3        # Correct response with hesitation
    EASY = 4           # Correct response with some effort
    PERFECT = 5        # Perfect response


@dataclass
class CardMetrics:
    """Metrics for a single flashcard or learning item"""
    easiness_factor: float = 2.5
    repetitions: int = 0
    interval: int = 1
    last_review: Optional[datetime] = None
    next_review: Optional[datetime] = None
    consecutive_correct: int = 0
    total_reviews: int = 0
    total_correct: int = 0
    streak_bonus: float = 1.0
    difficulty_penalty: float = 1.0
    learning_velocity: float = 1.0


class SM2Algorithm:
    """Enhanced SM2 Algorithm with user performance factors"""
    
    def __init__(self, 
                 min_easiness: float = 1.3,
                 max_easiness: float = 4.0,
                 initial_interval: int = 1,
                 graduation_interval: int = 4,
                 streak_bonus_factor: float = 0.1,
                 difficulty_penalty_factor: float = 0.15):
        """
        Initialize SM2 algorithm with enhanced parameters
        
        Args:
            min_easiness: Minimum easiness factor
            max_easiness: Maximum easiness factor
            initial_interval: Starting interval in days
            graduation_interval: Interval for graduating from learning phase
            streak_bonus_factor: Bonus multiplier for streak performance
            difficulty_penalty_factor: Penalty for difficult responses
        """
        self.min_easiness = min_easiness
        self.max_easiness = max_easiness
        self.initial_interval = initial_interval
        self.graduation_interval = graduation_interval
        self.streak_bonus_factor = streak_bonus_factor
        self.difficulty_penalty_factor = difficulty_penalty_factor
    
    def calculate_next_review(self, 
                            card_id: str,
                            response_quality: ResponseQuality,
                            card_metrics: CardMetrics,
                            user_performance_factor: float = 1.0) -> Tuple[CardMetrics, datetime]:
        """
        Calculate next review date based on response quality and card history
        
        Args:
            card_id: Unique identifier for the card
            response_quality: Quality of the user's response
            card_metrics: Current metrics for the card
            user_performance_factor: Global user performance multiplier
            
        Returns:
            Tuple of updated card metrics and next review date
        """
        now = datetime.now()
        updated_metrics = CardMetrics(
            easiness_factor=card_metrics.easiness_factor,
            repetitions=card_metrics.repetitions,
            interval=card_metrics.interval,
            last_review=now,
            consecutive_correct=card_metrics.consecutive_correct,
            total_reviews=card_metrics.total_reviews + 1,
            total_correct=card_metrics.total_correct,
            streak_bonus=card_metrics.streak_bonus,
            difficulty_penalty=card_metrics.difficulty_penalty,
            learning_velocity=card_metrics.learning_velocity
        )
        
        # Update success rate
        if response_quality.value >= 3:  # Correct responses
            updated_metrics.total_correct += 1
            updated_metrics.consecutive_correct += 1
        else:
            updated_metrics.consecutive_correct = 0
        
        # Calculate new easiness factor
        updated_metrics.easiness_factor = self._calculate_easiness_factor(
            card_metrics.easiness_factor,
            response_quality.value
        )
        
        # Apply user performance factors
        updated_metrics = self._apply_performance_factors(updated_metrics, user_performance_factor)
        
        # Calculate new interval
        if response_quality.value < 3:
            # Reset for incorrect responses
            updated_metrics.repetitions = 0
            updated_metrics.interval = self.initial_interval
        else:
            updated_metrics.repetitions += 1
            updated_metrics.interval = self._calculate_interval(
                updated_metrics.repetitions,
                updated_metrics.interval,
                updated_metrics.easiness_factor,
                updated_metrics.streak_bonus,
                updated_metrics.difficulty_penalty,
                user_performance_factor
            )
        
        # Calculate next review date
        next_review = now + timedelta(days=updated_metrics.interval)
        updated_metrics.next_review = next_review
        
        return updated_metrics, next_review
    
    def _calculate_easiness_factor(self, current_ef: float, quality: int) -> float:
        """Calculate new easiness factor based on response quality"""
        new_ef = current_ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        return max(self.min_easiness, min(self.max_easiness, new_ef))
    
    def _apply_performance_factors(self, metrics: CardMetrics, user_factor: float) -> CardMetrics:
        """Apply streak bonuses and difficulty penalties"""
        # Streak bonus calculation
        if metrics.consecutive_correct >= 5:
            metrics.streak_bonus = min(2.0, 1.0 + (metrics.consecutive_correct - 4) * self.streak_bonus_factor)
        else:
            metrics.streak_bonus = 1.0
        
        # Difficulty penalty for cards with low success rate
        success_rate = metrics.total_correct / max(1, metrics.total_reviews)
        if success_rate < 0.6:
            metrics.difficulty_penalty = max(0.5, 1.0 - (0.6 - success_rate) * self.difficulty_penalty_factor)
        else:
            metrics.difficulty_penalty = 1.0
        
        # Learning velocity based on recent performance
        metrics.learning_velocity = min(2.0, max(0.5, user_factor))
        
        return metrics
    
    def _calculate_interval(self, 
                          repetitions: int,
                          previous_interval: int,
                          easiness_factor: float,
                          streak_bonus: float,
                          difficulty_penalty: float,
                          user_performance_factor: float) -> int:
        """Calculate the next interval with all modifying factors"""
        if repetitions == 1:
            base_interval = self.initial_interval
        elif repetitions == 2:
            base_interval = self.graduation_interval
        else:
            base_interval = math.ceil(previous_interval * easiness_factor)
        
        # Apply all modifying factors
        modified_interval = base_interval * streak_bonus * difficulty_penalty * user_performance_factor
        
        # Ensure reasonable bounds
        return max(1, min(365, int(modified_interval)))
    
    def get_review_priority(self, card_metrics: CardMetrics, current_time: datetime = None) -> float:
        """
        Calculate review priority for scheduling
        Higher values indicate higher priority
        
        Args:
            card_metrics: Card metrics
            current_time: Current time (defaults to now)
            
        Returns:
            Priority score (0.0 to 1.0+)
        """
        if current_time is None:
            current_time = datetime.now()
        
        if card_metrics.next_review is None:
            return 1.0  # New cards get high priority
        
        # Calculate how overdue the card is
        time_diff = (current_time - card_metrics.next_review).total_seconds()
        overdue_hours = time_diff / 3600
        
        if overdue_hours <= 0:
            # Not yet due
            return max(0.0, 1.0 + overdue_hours / 24)  # Slightly negative priority
        
        # Overdue - higher priority
        base_priority = min(2.0, 1.0 + overdue_hours / 24)
        
        # Adjust for difficulty
        difficulty_multiplier = 2.0 - card_metrics.difficulty_penalty
        
        # Adjust for learning velocity
        velocity_multiplier = 2.0 - card_metrics.learning_velocity
        
        return base_priority * difficulty_multiplier * velocity_multiplier
    
    def should_graduate(self, card_metrics: CardMetrics) -> bool:
        """Determine if a card should graduate from learning phase"""
        return (card_metrics.consecutive_correct >= 2 and 
                card_metrics.repetitions >= 2 and
                card_metrics.total_correct / max(1, card_metrics.total_reviews) >= 0.7)
    
    def get_retention_prediction(self, card_metrics: CardMetrics, days_ahead: int = 7) -> float:
        """
        Predict retention probability for a card after specified days
        
        Args:
            card_metrics: Card metrics
            days_ahead: Days in the future to predict
            
        Returns:
            Predicted retention probability (0.0 to 1.0)
        """
        # Simplified retention model based on forgetting curve
        if card_metrics.total_reviews == 0:
            return 0.5  # Unknown retention for new cards
        
        # Calculate time since last review
        if card_metrics.last_review:
            days_since_review = (datetime.now() - card_metrics.last_review).days
        else:
            days_since_review = 0
        
        total_days = days_since_review + days_ahead
        
        # Forgetting curve with easiness factor influence
        decay_rate = 0.1 / card_metrics.easiness_factor
        base_retention = math.exp(-decay_rate * total_days)
        
        # Adjust for historical performance
        success_rate = card_metrics.total_correct / max(1, card_metrics.total_reviews)
        adjusted_retention = base_retention * (0.5 + 0.5 * success_rate)
        
        return max(0.0, min(1.0, adjusted_retention))