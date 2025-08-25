"""
Review Scheduler for Spaced Repetition System
Manages review queues and scheduling logic
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import heapq
import json

from .sm2_algorithm import SM2Algorithm, CardMetrics, ResponseQuality


class ReviewType(Enum):
    """Types of reviews in the system"""
    NEW = "new"
    LEARNING = "learning"
    REVIEW = "review"
    OVERDUE = "overdue"


@dataclass
class ReviewItem:
    """Item in the review queue"""
    card_id: str
    review_type: ReviewType
    priority: float
    scheduled_time: datetime
    card_metrics: CardMetrics
    content_type: str = "vocab"  # vocab, grammar, etc.
    
    def __lt__(self, other):
        # For heapq - higher priority items are "less than"
        return self.priority > other.priority


class ReviewScheduler:
    """Manages review scheduling and queue management"""
    
    def __init__(self, sm2_algorithm: SM2Algorithm = None, max_daily_reviews: int = 50):
        """
        Initialize review scheduler
        
        Args:
            sm2_algorithm: SM2 algorithm instance
            max_daily_reviews: Maximum reviews per day
        """
        self.sm2 = sm2_algorithm or SM2Algorithm()
        self.max_daily_reviews = max_daily_reviews
        self.review_queue: List[ReviewItem] = []
        self.daily_reviews_completed = 0
        self.last_queue_update = datetime.now()
        self.user_performance_factor = 1.0
        
    def add_new_card(self, card_id: str, content_type: str = "vocab") -> None:
        """Add a new card to the review system"""
        card_metrics = CardMetrics()
        review_item = ReviewItem(
            card_id=card_id,
            review_type=ReviewType.NEW,
            priority=1.0,
            scheduled_time=datetime.now(),
            card_metrics=card_metrics,
            content_type=content_type
        )
        heapq.heappush(self.review_queue, review_item)
    
    def process_review_response(self, 
                              card_id: str, 
                              response_quality: ResponseQuality,
                              review_duration_seconds: int = 0) -> Dict:
        """
        Process a review response and update scheduling
        
        Args:
            card_id: Card identifier
            response_quality: Quality of user response
            review_duration_seconds: Time taken for review
            
        Returns:
            Dictionary with scheduling information
        """
        # Find the card in the queue or create new metrics
        card_metrics = self._find_card_metrics(card_id)
        if card_metrics is None:
            card_metrics = CardMetrics()
        
        # Calculate next review using SM2 algorithm
        updated_metrics, next_review = self.sm2.calculate_next_review(
            card_id, response_quality, card_metrics, self.user_performance_factor
        )
        
        # Update performance factor based on recent performance
        self._update_user_performance_factor(response_quality, review_duration_seconds)
        
        # Determine review type for next scheduling
        next_review_type = self._determine_review_type(updated_metrics)
        
        # Schedule next review
        next_priority = self.sm2.get_review_priority(updated_metrics)
        next_review_item = ReviewItem(
            card_id=card_id,
            review_type=next_review_type,
            priority=next_priority,
            scheduled_time=next_review,
            card_metrics=updated_metrics,
            content_type=self._get_content_type(card_id)
        )
        
        # Remove old review item and add new one
        self._remove_card_from_queue(card_id)
        if next_review_type != ReviewType.NEW:  # Don't reschedule completed items immediately
            heapq.heappush(self.review_queue, next_review_item)
        
        self.daily_reviews_completed += 1
        
        return {
            'card_id': card_id,
            'next_review': next_review,
            'interval_days': updated_metrics.interval,
            'easiness_factor': updated_metrics.easiness_factor,
            'review_type': next_review_type.value,
            'retention_prediction': self.sm2.get_retention_prediction(updated_metrics),
            'graduated': self.sm2.should_graduate(updated_metrics)
        }
    
    def get_next_reviews(self, limit: int = 10, include_future: bool = False) -> List[ReviewItem]:
        """
        Get next reviews to present to user
        
        Args:
            limit: Maximum number of reviews to return
            include_future: Whether to include future reviews
            
        Returns:
            List of review items sorted by priority
        """
        self._update_queue_priorities()
        
        current_time = datetime.now()
        available_reviews = []
        
        # Create a copy of queue to examine without modifying original
        queue_copy = self.review_queue.copy()
        heapq.heapify(queue_copy)
        
        while queue_copy and len(available_reviews) < limit:
            item = heapq.heappop(queue_copy)
            
            if include_future or item.scheduled_time <= current_time:
                available_reviews.append(item)
            elif not include_future and len(available_reviews) == 0:
                # If no current reviews, include one future review
                available_reviews.append(item)
                break
        
        return available_reviews
    
    def get_daily_review_stats(self) -> Dict:
        """Get statistics for daily reviews"""
        current_time = datetime.now()
        
        # Count reviews by type
        stats = {
            'total_due': 0,
            'new_cards': 0,
            'learning_cards': 0,
            'review_cards': 0,
            'overdue_cards': 0,
            'completed_today': self.daily_reviews_completed,
            'remaining_capacity': max(0, self.max_daily_reviews - self.daily_reviews_completed)
        }
        
        for item in self.review_queue:
            if item.scheduled_time <= current_time:
                stats['total_due'] += 1
                if item.review_type == ReviewType.NEW:
                    stats['new_cards'] += 1
                elif item.review_type == ReviewType.LEARNING:
                    stats['learning_cards'] += 1
                elif item.review_type == ReviewType.REVIEW:
                    stats['review_cards'] += 1
                elif item.review_type == ReviewType.OVERDUE:
                    stats['overdue_cards'] += 1
        
        return stats
    
    def get_upcoming_schedule(self, days_ahead: int = 7) -> Dict[str, int]:
        """Get upcoming review schedule for next N days"""
        schedule = {}
        current_date = datetime.now().date()
        
        for i in range(days_ahead):
            date_key = (current_date + timedelta(days=i)).strftime('%Y-%m-%d')
            schedule[date_key] = 0
        
        for item in self.review_queue:
            review_date = item.scheduled_time.date()
            date_key = review_date.strftime('%Y-%m-%d')
            if date_key in schedule:
                schedule[date_key] += 1
        
        return schedule
    
    def adjust_daily_limit(self, new_limit: int) -> None:
        """Adjust maximum daily reviews"""
        self.max_daily_reviews = max(1, new_limit)
    
    def reset_daily_counter(self) -> None:
        """Reset daily review counter (typically called at start of new day)"""
        self.daily_reviews_completed = 0
        self.last_queue_update = datetime.now()
    
    def _find_card_metrics(self, card_id: str) -> Optional[CardMetrics]:
        """Find card metrics in the review queue"""
        for item in self.review_queue:
            if item.card_id == card_id:
                return item.card_metrics
        return None
    
    def _remove_card_from_queue(self, card_id: str) -> None:
        """Remove a card from the review queue"""
        self.review_queue = [item for item in self.review_queue if item.card_id != card_id]
        heapq.heapify(self.review_queue)
    
    def _update_queue_priorities(self) -> None:
        """Update priorities for all items in queue"""
        current_time = datetime.now()
        updated_queue = []
        
        for item in self.review_queue:
            updated_priority = self.sm2.get_review_priority(item.card_metrics, current_time)
            updated_item = ReviewItem(
                card_id=item.card_id,
                review_type=item.review_type,
                priority=updated_priority,
                scheduled_time=item.scheduled_time,
                card_metrics=item.card_metrics,
                content_type=item.content_type
            )
            updated_queue.append(updated_item)
        
        self.review_queue = updated_queue
        heapq.heapify(self.review_queue)
    
    def _determine_review_type(self, card_metrics: CardMetrics) -> ReviewType:
        """Determine the review type for next scheduling"""
        if card_metrics.total_reviews == 1:
            return ReviewType.LEARNING
        elif self.sm2.should_graduate(card_metrics):
            return ReviewType.REVIEW
        elif card_metrics.consecutive_correct == 0:
            return ReviewType.LEARNING
        else:
            current_time = datetime.now()
            if card_metrics.next_review and card_metrics.next_review < current_time - timedelta(days=1):
                return ReviewType.OVERDUE
            return ReviewType.REVIEW
    
    def _update_user_performance_factor(self, response_quality: ResponseQuality, duration_seconds: int) -> None:
        """Update global user performance factor based on recent performance"""
        # Simple exponential moving average
        alpha = 0.1
        
        # Convert response quality to performance score
        quality_score = response_quality.value / 5.0
        
        # Adjust for response time (faster responses within reason are better)
        time_factor = 1.0
        if 5 <= duration_seconds <= 15:  # Optimal response time
            time_factor = 1.1
        elif duration_seconds > 30:  # Too slow
            time_factor = 0.9
        elif duration_seconds < 2:  # Too fast, might be guessing
            time_factor = 0.95
        
        current_performance = quality_score * time_factor
        self.user_performance_factor = (1 - alpha) * self.user_performance_factor + alpha * current_performance
        
        # Bound the performance factor
        self.user_performance_factor = max(0.5, min(2.0, self.user_performance_factor))
    
    def _get_content_type(self, card_id: str) -> str:
        """Get content type for a card (to be implemented based on card ID structure)"""
        # This would typically query the database or parse card_id
        # For now, return default
        return "vocab"
    
    def export_queue_state(self) -> str:
        """Export current queue state as JSON"""
        queue_data = []
        for item in self.review_queue:
            queue_data.append({
                'card_id': item.card_id,
                'review_type': item.review_type.value,
                'priority': item.priority,
                'scheduled_time': item.scheduled_time.isoformat(),
                'content_type': item.content_type,
                'card_metrics': {
                    'easiness_factor': item.card_metrics.easiness_factor,
                    'repetitions': item.card_metrics.repetitions,
                    'interval': item.card_metrics.interval,
                    'last_review': item.card_metrics.last_review.isoformat() if item.card_metrics.last_review else None,
                    'consecutive_correct': item.card_metrics.consecutive_correct,
                    'total_reviews': item.card_metrics.total_reviews,
                    'total_correct': item.card_metrics.total_correct
                }
            })
        
        return json.dumps({
            'queue': queue_data,
            'daily_reviews_completed': self.daily_reviews_completed,
            'user_performance_factor': self.user_performance_factor,
            'last_update': self.last_queue_update.isoformat()
        }, indent=2)