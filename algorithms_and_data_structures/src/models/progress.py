"""
Progress tracking model for user progress and analytics.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import statistics

from .base import BaseModel, ValidationError


class CompletionStatus(Enum):
    """Completion status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class ActivityType(Enum):
    """Learning activity types."""
    LESSON_VIEW = "lesson_view"
    CONTENT_INTERACTION = "content_interaction"
    QUIZ_ATTEMPT = "quiz_attempt"
    ASSIGNMENT_SUBMISSION = "assignment_submission"
    DISCUSSION_POST = "discussion_post"
    RESOURCE_DOWNLOAD = "resource_download"
    VIDEO_WATCH = "video_watch"
    READING_PROGRESS = "reading_progress"
    PRACTICE_EXERCISE = "practice_exercise"
    PEER_REVIEW = "peer_review"


@dataclass
class LearningActivity:
    """
    Individual learning activity record.
    """
    
    activity_type: ActivityType = ActivityType.LESSON_VIEW
    content_id: str = ""
    content_title: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_minutes: int = 0
    score: Optional[float] = None  # Score achieved if applicable
    max_score: Optional[float] = None  # Maximum possible score
    attempt_number: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'activity_type': self.activity_type.value,
            'content_id': self.content_id,
            'content_title': self.content_title,
            'timestamp': self.timestamp.isoformat(),
            'duration_minutes': self.duration_minutes,
            'score': self.score,
            'max_score': self.max_score,
            'attempt_number': self.attempt_number,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningActivity':
        """Create from dictionary."""
        return cls(
            activity_type=ActivityType(data.get('activity_type', 'lesson_view')),
            content_id=data.get('content_id', ''),
            content_title=data.get('content_title', ''),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat())),
            duration_minutes=data.get('duration_minutes', 0),
            score=data.get('score'),
            max_score=data.get('max_score'),
            attempt_number=data.get('attempt_number', 1),
            metadata=data.get('metadata', {})
        )
    
    def get_score_percentage(self) -> Optional[float]:
        """Get score as percentage."""
        if self.score is not None and self.max_score is not None and self.max_score > 0:
            return (self.score / self.max_score) * 100
        return None


@dataclass
class ProgressMetrics:
    """
    Detailed progress metrics and analytics.
    """
    
    # Time metrics
    total_time_minutes: int = 0
    active_time_minutes: int = 0  # Time actually engaged
    average_session_minutes: int = 0
    longest_session_minutes: int = 0
    
    # Completion metrics
    items_completed: int = 0
    items_total: int = 0
    completion_percentage: float = 0.0
    
    # Performance metrics
    average_score: float = 0.0
    highest_score: float = 0.0
    lowest_score: float = 0.0
    passing_items: int = 0
    failing_items: int = 0
    
    # Engagement metrics
    login_count: int = 0
    streak_days: int = 0
    longest_streak_days: int = 0
    last_activity: Optional[datetime] = None
    
    # Learning velocity
    items_per_day: float = 0.0
    hours_per_week: float = 0.0
    projected_completion_date: Optional[datetime] = None
    
    # Quality metrics
    quiz_attempts: int = 0
    assignment_submissions: int = 0
    peer_reviews_given: int = 0
    peer_reviews_received: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_time_minutes': self.total_time_minutes,
            'active_time_minutes': self.active_time_minutes,
            'average_session_minutes': self.average_session_minutes,
            'longest_session_minutes': self.longest_session_minutes,
            'items_completed': self.items_completed,
            'items_total': self.items_total,
            'completion_percentage': self.completion_percentage,
            'average_score': self.average_score,
            'highest_score': self.highest_score,
            'lowest_score': self.lowest_score,
            'passing_items': self.passing_items,
            'failing_items': self.failing_items,
            'login_count': self.login_count,
            'streak_days': self.streak_days,
            'longest_streak_days': self.longest_streak_days,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'items_per_day': self.items_per_day,
            'hours_per_week': self.hours_per_week,
            'projected_completion_date': self.projected_completion_date.isoformat() if self.projected_completion_date else None,
            'quiz_attempts': self.quiz_attempts,
            'assignment_submissions': self.assignment_submissions,
            'peer_reviews_given': self.peer_reviews_given,
            'peer_reviews_received': self.peer_reviews_received
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProgressMetrics':
        """Create from dictionary."""
        return cls(
            total_time_minutes=data.get('total_time_minutes', 0),
            active_time_minutes=data.get('active_time_minutes', 0),
            average_session_minutes=data.get('average_session_minutes', 0),
            longest_session_minutes=data.get('longest_session_minutes', 0),
            items_completed=data.get('items_completed', 0),
            items_total=data.get('items_total', 0),
            completion_percentage=data.get('completion_percentage', 0.0),
            average_score=data.get('average_score', 0.0),
            highest_score=data.get('highest_score', 0.0),
            lowest_score=data.get('lowest_score', 0.0),
            passing_items=data.get('passing_items', 0),
            failing_items=data.get('failing_items', 0),
            login_count=data.get('login_count', 0),
            streak_days=data.get('streak_days', 0),
            longest_streak_days=data.get('longest_streak_days', 0),
            last_activity=datetime.fromisoformat(data['last_activity']) if data.get('last_activity') else None,
            items_per_day=data.get('items_per_day', 0.0),
            hours_per_week=data.get('hours_per_week', 0.0),
            projected_completion_date=datetime.fromisoformat(data['projected_completion_date']) if data.get('projected_completion_date') else None,
            quiz_attempts=data.get('quiz_attempts', 0),
            assignment_submissions=data.get('assignment_submissions', 0),
            peer_reviews_given=data.get('peer_reviews_given', 0),
            peer_reviews_received=data.get('peer_reviews_received', 0)
        )


@dataclass
class Progress(BaseModel):
    """
    Progress tracking model for user progress and analytics.
    
    Tracks comprehensive learning progress including completion status,
    scores, time spent, and detailed analytics for any curriculum item.
    """
    
    # Core identifiers
    user_id: str = ""
    curriculum_id: str = ""
    course_id: str = ""
    module_id: str = ""
    lesson_id: str = ""
    content_id: str = ""
    
    # Progress status
    status: CompletionStatus = CompletionStatus.NOT_STARTED
    
    # Completion tracking
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    
    # Performance tracking
    current_score: float = 0.0
    best_score: float = 0.0
    attempts: int = 0
    max_attempts: int = 3
    passing_score: float = 70.0
    
    # Time tracking
    time_spent_minutes: int = 0
    estimated_time_minutes: int = 0
    
    # Detailed tracking
    activities: List[LearningActivity] = field(default_factory=list)
    bookmarks: List[str] = field(default_factory=list)  # Bookmarked positions/pages
    notes: List[Dict[str, Any]] = field(default_factory=list)  # User notes
    
    # Computed metrics
    metrics: ProgressMetrics = field(default_factory=ProgressMetrics)
    
    # Flags
    is_required: bool = True
    is_locked: bool = False  # Locked by prerequisites
    is_overdue: bool = False
    
    # Adaptive learning
    difficulty_adjustment: float = 0.0  # -1.0 to 1.0
    recommended_review: bool = False
    mastery_level: float = 0.0  # 0.0 to 1.0
    
    def validate(self) -> None:
        """
        Validate the progress model.
        
        Raises:
            ValidationError: If validation fails
        """
        # Required fields
        if not self.user_id:
            raise ValidationError("User ID is required")
        
        # At least one content identifier required
        if not any([self.curriculum_id, self.course_id, self.module_id, 
                   self.lesson_id, self.content_id]):
            raise ValidationError("At least one content identifier is required")
        
        # Status validation
        if not isinstance(self.status, CompletionStatus):
            raise ValidationError("Invalid completion status")
        
        # Score validation
        if not 0.0 <= self.current_score <= 100.0:
            raise ValidationError("Current score must be between 0 and 100")
        
        if not 0.0 <= self.best_score <= 100.0:
            raise ValidationError("Best score must be between 0 and 100")
        
        if not 0.0 <= self.passing_score <= 100.0:
            raise ValidationError("Passing score must be between 0 and 100")
        
        # Attempts validation
        if self.attempts < 0:
            raise ValidationError("Attempts cannot be negative")
        
        if self.max_attempts < 1:
            raise ValidationError("Max attempts must be at least 1")
        
        # Time validation
        if self.time_spent_minutes < 0:
            raise ValidationError("Time spent cannot be negative")
        
        if self.estimated_time_minutes < 0:
            raise ValidationError("Estimated time cannot be negative")
        
        # Date validation
        if (self.started_at and self.completed_at and 
            self.started_at > self.completed_at):
            raise ValidationError("Start date cannot be after completion date")
        
        # Adaptive learning validation
        if not -1.0 <= self.difficulty_adjustment <= 1.0:
            raise ValidationError("Difficulty adjustment must be between -1.0 and 1.0")
        
        if not 0.0 <= self.mastery_level <= 1.0:
            raise ValidationError("Mastery level must be between 0.0 and 1.0")
    
    def start_progress(self) -> None:
        """Start tracking progress."""
        if self.status == CompletionStatus.NOT_STARTED:
            self.status = CompletionStatus.IN_PROGRESS
            self.started_at = datetime.utcnow()
            self.last_accessed = datetime.utcnow()
            self.update_timestamp()
    
    def complete_progress(self, score: float = 0.0) -> None:
        """
        Mark progress as completed.
        
        Args:
            score: Final score achieved
        """
        self.current_score = score
        self.best_score = max(self.best_score, score)
        self.completed_at = datetime.utcnow()
        self.last_accessed = datetime.utcnow()
        
        # Determine status based on score
        if score >= self.passing_score:
            self.status = CompletionStatus.PASSED
        else:
            self.status = CompletionStatus.FAILED
        
        self.update_timestamp()
        self.calculate_metrics()
    
    def record_attempt(self, score: float) -> bool:
        """
        Record an attempt.
        
        Args:
            score: Score achieved in this attempt
            
        Returns:
            True if attempt was recorded, False if max attempts exceeded
        """
        if self.attempts >= self.max_attempts:
            return False
        
        self.attempts += 1
        self.current_score = score
        self.best_score = max(self.best_score, score)
        self.last_accessed = datetime.utcnow()
        
        # Create activity record
        activity = LearningActivity(
            activity_type=ActivityType.QUIZ_ATTEMPT,
            content_id=self.content_id,
            timestamp=datetime.utcnow(),
            score=score,
            max_score=100.0,
            attempt_number=self.attempts
        )
        self.activities.append(activity)
        
        self.update_timestamp()
        return True
    
    def add_activity(self, activity: LearningActivity) -> None:
        """Add a learning activity."""
        self.activities.append(activity)
        self.time_spent_minutes += activity.duration_minutes
        self.last_accessed = activity.timestamp
        
        # Update status if not started
        if self.status == CompletionStatus.NOT_STARTED:
            self.start_progress()
        
        self.update_timestamp()
    
    def add_study_time(self, minutes: int) -> None:
        """
        Add study time to progress.
        
        Args:
            minutes: Number of minutes to add
        """
        if minutes > 0:
            self.time_spent_minutes += minutes
            self.last_accessed = datetime.utcnow()
            self.update_timestamp()
    
    def add_bookmark(self, position: str) -> None:
        """
        Add a bookmark.
        
        Args:
            position: Position identifier (page, timestamp, etc.)
        """
        if position not in self.bookmarks:
            self.bookmarks.append(position)
            self.update_timestamp()
    
    def add_note(self, content: str, position: str = "") -> None:
        """
        Add a note.
        
        Args:
            content: Note content
            position: Position where note was made
        """
        note = {
            'content': content,
            'position': position,
            'timestamp': datetime.utcnow().isoformat(),
            'id': len(self.notes) + 1
        }
        self.notes.append(note)
        self.update_timestamp()
    
    def calculate_metrics(self) -> None:
        """Calculate and update progress metrics."""
        # Time metrics
        if self.activities:
            session_times = []
            current_session = []
            
            for activity in sorted(self.activities, key=lambda x: x.timestamp):
                # Group activities into sessions (activities within 30 minutes)
                if (current_session and 
                    activity.timestamp - current_session[-1].timestamp > timedelta(minutes=30)):
                    # End current session
                    session_time = sum(a.duration_minutes for a in current_session)
                    if session_time > 0:
                        session_times.append(session_time)
                    current_session = []
                
                current_session.append(activity)
            
            # Add final session
            if current_session:
                session_time = sum(a.duration_minutes for a in current_session)
                if session_time > 0:
                    session_times.append(session_time)
            
            # Calculate time metrics
            self.metrics.total_time_minutes = self.time_spent_minutes
            self.metrics.active_time_minutes = sum(
                a.duration_minutes for a in self.activities
            )
            
            if session_times:
                self.metrics.average_session_minutes = int(statistics.mean(session_times))
                self.metrics.longest_session_minutes = max(session_times)
        
        # Performance metrics
        scores = [a.get_score_percentage() for a in self.activities 
                 if a.get_score_percentage() is not None]
        
        if scores:
            self.metrics.average_score = statistics.mean(scores)
            self.metrics.highest_score = max(scores)
            self.metrics.lowest_score = min(scores)
            self.metrics.passing_items = len([s for s in scores if s >= self.passing_score])
            self.metrics.failing_items = len([s for s in scores if s < self.passing_score])
        
        # Activity counts
        self.metrics.quiz_attempts = len([
            a for a in self.activities 
            if a.activity_type == ActivityType.QUIZ_ATTEMPT
        ])
        
        self.metrics.assignment_submissions = len([
            a for a in self.activities 
            if a.activity_type == ActivityType.ASSIGNMENT_SUBMISSION
        ])
        
        # Last activity
        if self.activities:
            self.metrics.last_activity = max(a.timestamp for a in self.activities)
        
        # Calculate learning velocity
        if self.started_at:
            days_elapsed = (datetime.utcnow() - self.started_at).days
            if days_elapsed > 0:
                self.metrics.items_per_day = self.metrics.items_completed / days_elapsed
                self.metrics.hours_per_week = (self.time_spent_minutes / 60) / (days_elapsed / 7)
        
        # Project completion date
        if (self.estimated_time_minutes > 0 and 
            self.time_spent_minutes < self.estimated_time_minutes and 
            self.metrics.average_session_minutes > 0):
            
            remaining_minutes = self.estimated_time_minutes - self.time_spent_minutes
            sessions_needed = remaining_minutes / self.metrics.average_session_minutes
            
            # Assume 3 sessions per week
            weeks_needed = sessions_needed / 3
            self.metrics.projected_completion_date = (
                datetime.utcnow() + timedelta(weeks=weeks_needed)
            )
    
    def get_completion_percentage(self) -> float:
        """Get completion percentage."""
        if self.status == CompletionStatus.COMPLETED or self.status == CompletionStatus.PASSED:
            return 100.0
        elif self.status == CompletionStatus.NOT_STARTED:
            return 0.0
        else:
            # Calculate based on time spent vs estimated time
            if self.estimated_time_minutes > 0:
                return min(100.0, (self.time_spent_minutes / self.estimated_time_minutes) * 100)
            return 0.0
    
    def is_passing(self) -> bool:
        """Check if current progress is passing."""
        return self.best_score >= self.passing_score
    
    def is_complete(self) -> bool:
        """Check if progress is complete."""
        return self.status in [CompletionStatus.COMPLETED, CompletionStatus.PASSED]
    
    def is_overdue_now(self) -> bool:
        """Check if progress is currently overdue."""
        if self.due_date and not self.is_complete():
            return datetime.utcnow() > self.due_date
        return False
    
    def days_until_due(self) -> Optional[int]:
        """Get days until due date."""
        if self.due_date:
            delta = self.due_date - datetime.utcnow()
            return delta.days
        return None
    
    def get_streak_days(self) -> int:
        """Calculate current learning streak."""
        if not self.activities:
            return 0
        
        # Group activities by date
        activity_dates = set()
        for activity in self.activities:
            activity_dates.add(activity.timestamp.date())
        
        # Calculate streak
        current_date = datetime.utcnow().date()
        streak = 0
        
        while current_date in activity_dates:
            streak += 1
            current_date -= timedelta(days=1)
        
        self.metrics.streak_days = streak
        return streak
    
    def get_performance_trend(self, days: int = 7) -> List[float]:
        """
        Get performance trend over the last N days.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of average scores by day
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_activities = [
            a for a in self.activities 
            if a.timestamp >= cutoff_date and a.get_score_percentage() is not None
        ]
        
        # Group by day
        daily_scores = {}
        for activity in recent_activities:
            day = activity.timestamp.date()
            if day not in daily_scores:
                daily_scores[day] = []
            daily_scores[day].append(activity.get_score_percentage())
        
        # Calculate daily averages
        trend = []
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=i)).date()
            if date in daily_scores:
                trend.append(statistics.mean(daily_scores[date]))
            else:
                trend.append(0.0)
        
        return list(reversed(trend))  # Return chronologically
    
    def recommend_review(self) -> bool:
        """
        Determine if review is recommended based on performance.
        
        Returns:
            True if review is recommended
        """
        # Recommend review if:
        # - Current score is below passing
        # - Performance trend is declining
        # - Long time since last access
        
        if self.current_score < self.passing_score:
            self.recommended_review = True
            return True
        
        if self.last_accessed:
            days_since_access = (datetime.utcnow() - self.last_accessed).days
            if days_since_access > 14:  # 2 weeks
                self.recommended_review = True
                return True
        
        # Check performance trend
        trend = self.get_performance_trend(7)
        if len(trend) >= 3:
            recent_avg = statistics.mean(trend[-3:])
            earlier_avg = statistics.mean(trend[:3])
            if recent_avg < earlier_avg - 10:  # 10 point decline
                self.recommended_review = True
                return True
        
        self.recommended_review = False
        return False
    
    def adjust_difficulty(self, performance_score: float) -> None:
        """
        Adjust difficulty based on performance.
        
        Args:
            performance_score: Recent performance score (0-100)
        """
        if performance_score >= 90:
            # Increase difficulty
            self.difficulty_adjustment = min(1.0, self.difficulty_adjustment + 0.1)
        elif performance_score < 60:
            # Decrease difficulty
            self.difficulty_adjustment = max(-1.0, self.difficulty_adjustment - 0.1)
        
        # Update mastery level
        self.mastery_level = min(1.0, performance_score / 100.0)
        self.update_timestamp()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get progress summary."""
        return {
            'status': self.status.value,
            'completion_percentage': self.get_completion_percentage(),
            'current_score': self.current_score,
            'best_score': self.best_score,
            'attempts': self.attempts,
            'time_spent_hours': round(self.time_spent_minutes / 60, 1),
            'is_passing': self.is_passing(),
            'is_overdue': self.is_overdue_now(),
            'streak_days': self.get_streak_days(),
            'recommended_review': self.recommend_review(),
            'mastery_level': self.mastery_level
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = super().to_dict()
        data['status'] = self.status.value
        data['activities'] = [a.to_dict() for a in self.activities]
        data['metrics'] = self.metrics.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Progress':
        """Create from dictionary."""
        # Extract nested objects
        activities_data = data.pop('activities', [])
        metrics_data = data.pop('metrics', {})
        
        # Handle enum
        if 'status' in data:
            data['status'] = CompletionStatus(data['status'])
        
        # Create progress
        progress = super().from_dict(data)
        
        # Set nested objects
        progress.activities = [LearningActivity.from_dict(a) for a in activities_data]
        progress.metrics = ProgressMetrics.from_dict(metrics_data)
        
        return progress
    
    def __str__(self) -> str:
        """String representation."""
        return f"Progress(user='{self.user_id}', status='{self.status.value}', score={self.current_score})"