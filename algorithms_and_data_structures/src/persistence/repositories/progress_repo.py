"""
Progress Repository

Repository for managing user progress, achievements, and learning analytics.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from .base import BaseRepository
from ..exceptions import ValidationError, RepositoryError


class ProgressStatus(Enum):
    """Progress status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"


class AssessmentResult(Enum):
    """Assessment result enumeration."""
    PASS = "pass"
    FAIL = "fail"
    PARTIAL = "partial"
    PENDING = "pending"


@dataclass
class UserProgress:
    """User progress entity tracking learning progress."""
    
    id: Optional[str] = None
    user_id: str = ""
    curriculum_id: Optional[str] = None
    module_id: Optional[str] = None
    lesson_id: Optional[str] = None
    content_id: Optional[str] = None
    progress_type: str = "lesson"  # lesson, module, curriculum, content
    status: str = ProgressStatus.NOT_STARTED.value
    completion_percentage: float = 0.0
    time_spent_minutes: int = 0
    attempts: int = 0
    best_score: Optional[float] = None
    current_score: Optional[float] = None
    metadata: Dict[str, Any] = None
    notes: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    last_accessed_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Achievement:
    """Achievement entity for tracking user accomplishments."""
    
    id: Optional[str] = None
    user_id: str = ""
    achievement_type: str = "completion"  # completion, streak, score, time, special
    title: str = ""
    description: str = ""
    icon: str = ""
    points: int = 0
    difficulty_level: str = "beginner"
    criteria: Dict[str, Any] = None
    earned_at: Optional[str] = None
    curriculum_id: Optional[str] = None
    module_id: Optional[str] = None
    lesson_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    is_earned: bool = False
    
    def __post_init__(self):
        """Initialize default values."""
        if self.criteria is None:
            self.criteria = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass
class LearningSession:
    """Learning session entity tracking study sessions."""
    
    id: Optional[str] = None
    user_id: str = ""
    session_type: str = "study"  # study, practice, assessment, review
    curriculum_id: Optional[str] = None
    module_id: Optional[str] = None
    lesson_id: Optional[str] = None
    content_ids: List[str] = None
    duration_minutes: int = 0
    activities: List[Dict[str, Any]] = None
    progress_made: Dict[str, Any] = None
    performance_metrics: Dict[str, Any] = None
    notes: str = ""
    started_at: str = ""
    ended_at: Optional[str] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.content_ids is None:
            self.content_ids = []
        if self.activities is None:
            self.activities = []
        if self.progress_made is None:
            self.progress_made = {}
        if self.performance_metrics is None:
            self.performance_metrics = {}


@dataclass
class Assessment:
    """Assessment entity for tracking quiz/test results."""
    
    id: Optional[str] = None
    user_id: str = ""
    assessment_type: str = "quiz"  # quiz, test, assignment, project
    curriculum_id: Optional[str] = None
    module_id: Optional[str] = None
    lesson_id: Optional[str] = None
    content_id: Optional[str] = None
    title: str = ""
    total_questions: int = 0
    correct_answers: int = 0
    score_percentage: float = 0.0
    time_taken_minutes: int = 0
    result: str = AssessmentResult.PENDING.value
    answers: List[Dict[str, Any]] = None
    feedback: Dict[str, Any] = None
    attempts: int = 1
    max_attempts: int = 3
    started_at: str = ""
    submitted_at: Optional[str] = None
    graded_at: Optional[str] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.answers is None:
            self.answers = []
        if self.feedback is None:
            self.feedback = {}


class UserProgressRepository(BaseRepository[UserProgress]):
    """Repository for user progress management."""
    
    def __init__(self, storage):
        super().__init__(storage, "user_progress")
        
    def _validate_entity_fields(self, entity_data: Dict[str, Any]) -> None:
        """Validate user progress-specific fields."""
        required_fields = ['user_id', 'progress_type']
        for field in required_fields:
            if not entity_data.get(field):
                raise ValidationError(f"User progress {field} is required")
        
        # Validate progress type
        valid_types = ['lesson', 'module', 'curriculum', 'content', 'exercise']
        if entity_data.get('progress_type') not in valid_types:
            raise ValidationError(f"Progress type must be one of: {valid_types}")
        
        # Validate status
        valid_statuses = [s.value for s in ProgressStatus]
        if entity_data.get('status') not in valid_statuses:
            raise ValidationError(f"Progress status must be one of: {valid_statuses}")
        
        # Validate completion percentage
        percentage = entity_data.get('completion_percentage', 0.0)
        if not isinstance(percentage, (int, float)) or percentage < 0 or percentage > 100:
            raise ValidationError("Completion percentage must be between 0 and 100")
        
        # Validate time spent
        time_spent = entity_data.get('time_spent_minutes', 0)
        if not isinstance(time_spent, int) or time_spent < 0:
            raise ValidationError("Time spent must be a non-negative integer")
    
    def _serialize_entity(self, entity: UserProgress) -> Dict[str, Any]:
        """Serialize user progress to dictionary."""
        return {
            'id': entity.id,
            'user_id': entity.user_id,
            'curriculum_id': entity.curriculum_id,
            'module_id': entity.module_id,
            'lesson_id': entity.lesson_id,
            'content_id': entity.content_id,
            'progress_type': entity.progress_type,
            'status': entity.status,
            'completion_percentage': entity.completion_percentage,
            'time_spent_minutes': entity.time_spent_minutes,
            'attempts': entity.attempts,
            'best_score': entity.best_score,
            'current_score': entity.current_score,
            'metadata': entity.metadata,
            'notes': entity.notes,
            'started_at': entity.started_at,
            'completed_at': entity.completed_at,
            'last_accessed_at': entity.last_accessed_at,
            'created_at': entity.created_at,
            'updated_at': entity.updated_at
        }
    
    def _deserialize_entity(self, data: Dict[str, Any]) -> UserProgress:
        """Deserialize dictionary to user progress."""
        return UserProgress(
            id=data.get('id'),
            user_id=data.get('user_id', ''),
            curriculum_id=data.get('curriculum_id'),
            module_id=data.get('module_id'),
            lesson_id=data.get('lesson_id'),
            content_id=data.get('content_id'),
            progress_type=data.get('progress_type', 'lesson'),
            status=data.get('status', ProgressStatus.NOT_STARTED.value),
            completion_percentage=data.get('completion_percentage', 0.0),
            time_spent_minutes=data.get('time_spent_minutes', 0),
            attempts=data.get('attempts', 0),
            best_score=data.get('best_score'),
            current_score=data.get('current_score'),
            metadata=data.get('metadata', {}),
            notes=data.get('notes', ''),
            started_at=data.get('started_at'),
            completed_at=data.get('completed_at'),
            last_accessed_at=data.get('last_accessed_at'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def find_by_user(self, user_id: str) -> List[UserProgress]:
        """Find all progress for a user."""
        return self.find_by_field('user_id', user_id)
    
    def find_user_curriculum_progress(self, user_id: str, curriculum_id: str) -> List[UserProgress]:
        """Find user progress for a specific curriculum."""
        try:
            user_progress = self.find_by_user(user_id)
            return [p for p in user_progress if p.curriculum_id == curriculum_id]
        except Exception as e:
            raise RepositoryError(f"Failed to find user curriculum progress: {str(e)}")
    
    def find_user_lesson_progress(self, user_id: str, lesson_id: str) -> Optional[UserProgress]:
        """Find user progress for a specific lesson."""
        try:
            user_progress = self.find_by_user(user_id)
            for progress in user_progress:
                if progress.lesson_id == lesson_id:
                    return progress
            return None
        except Exception as e:
            raise RepositoryError(f"Failed to find user lesson progress: {str(e)}")
    
    def get_completion_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user completion statistics."""
        try:
            user_progress = self.find_by_user(user_id)
            
            stats = {
                'total_items': len(user_progress),
                'completed': 0,
                'in_progress': 0,
                'not_started': 0,
                'total_time_minutes': 0,
                'completion_rate': 0.0,
                'by_type': {}
            }
            
            for progress in user_progress:
                # Count by status
                if progress.status == ProgressStatus.COMPLETED.value:
                    stats['completed'] += 1
                elif progress.status == ProgressStatus.IN_PROGRESS.value:
                    stats['in_progress'] += 1
                else:
                    stats['not_started'] += 1
                
                # Sum time spent
                stats['total_time_minutes'] += progress.time_spent_minutes
                
                # Count by type
                progress_type = progress.progress_type
                if progress_type not in stats['by_type']:
                    stats['by_type'][progress_type] = {
                        'total': 0, 'completed': 0, 'in_progress': 0
                    }
                
                stats['by_type'][progress_type]['total'] += 1
                if progress.status == ProgressStatus.COMPLETED.value:
                    stats['by_type'][progress_type]['completed'] += 1
                elif progress.status == ProgressStatus.IN_PROGRESS.value:
                    stats['by_type'][progress_type]['in_progress'] += 1
            
            # Calculate completion rate
            if stats['total_items'] > 0:
                stats['completion_rate'] = (stats['completed'] / stats['total_items']) * 100
            
            return stats
            
        except Exception as e:
            raise RepositoryError(f"Failed to get completion stats: {str(e)}")
    
    def update_progress(self, user_id: str, progress_type: str, item_id: str, 
                       completion_percentage: float, time_spent_minutes: int = 0) -> str:
        """Update or create progress record."""
        try:
            # Find existing progress
            existing_progress = None
            user_progress_list = self.find_by_user(user_id)
            
            for progress in user_progress_list:
                if (progress.progress_type == progress_type and
                    ((progress_type == 'lesson' and progress.lesson_id == item_id) or
                     (progress_type == 'module' and progress.module_id == item_id) or
                     (progress_type == 'curriculum' and progress.curriculum_id == item_id) or
                     (progress_type == 'content' and progress.content_id == item_id))):
                    existing_progress = progress
                    break
            
            now = datetime.now().isoformat()
            
            if existing_progress:
                # Update existing progress
                existing_progress.completion_percentage = completion_percentage
                existing_progress.time_spent_minutes += time_spent_minutes
                existing_progress.last_accessed_at = now
                
                # Update status based on completion
                if completion_percentage >= 100:
                    existing_progress.status = ProgressStatus.COMPLETED.value
                    if not existing_progress.completed_at:
                        existing_progress.completed_at = now
                elif completion_percentage > 0:
                    existing_progress.status = ProgressStatus.IN_PROGRESS.value
                    if not existing_progress.started_at:
                        existing_progress.started_at = now
                
                self.update(existing_progress.id, existing_progress)
                return existing_progress.id
            else:
                # Create new progress
                new_progress = UserProgress(
                    user_id=user_id,
                    progress_type=progress_type,
                    completion_percentage=completion_percentage,
                    time_spent_minutes=time_spent_minutes,
                    started_at=now if completion_percentage > 0 else None,
                    completed_at=now if completion_percentage >= 100 else None,
                    last_accessed_at=now
                )
                
                # Set appropriate ID field
                if progress_type == 'lesson':
                    new_progress.lesson_id = item_id
                elif progress_type == 'module':
                    new_progress.module_id = item_id
                elif progress_type == 'curriculum':
                    new_progress.curriculum_id = item_id
                elif progress_type == 'content':
                    new_progress.content_id = item_id
                
                # Set status
                if completion_percentage >= 100:
                    new_progress.status = ProgressStatus.COMPLETED.value
                elif completion_percentage > 0:
                    new_progress.status = ProgressStatus.IN_PROGRESS.value
                
                return self.create(new_progress)
                
        except Exception as e:
            raise RepositoryError(f"Failed to update progress: {str(e)}")


class AchievementRepository(BaseRepository[Achievement]):
    """Repository for achievement management."""
    
    def __init__(self, storage):
        super().__init__(storage, "achievement")
        
    def _validate_entity_fields(self, entity_data: Dict[str, Any]) -> None:
        """Validate achievement-specific fields."""
        required_fields = ['user_id', 'achievement_type', 'title']
        for field in required_fields:
            if not entity_data.get(field):
                raise ValidationError(f"Achievement {field} is required")
        
        # Validate achievement type
        valid_types = ['completion', 'streak', 'score', 'time', 'special', 'milestone']
        if entity_data.get('achievement_type') not in valid_types:
            raise ValidationError(f"Achievement type must be one of: {valid_types}")
        
        # Validate points
        points = entity_data.get('points', 0)
        if not isinstance(points, int) or points < 0:
            raise ValidationError("Points must be a non-negative integer")
    
    def _serialize_entity(self, entity: Achievement) -> Dict[str, Any]:
        """Serialize achievement to dictionary."""
        return {
            'id': entity.id,
            'user_id': entity.user_id,
            'achievement_type': entity.achievement_type,
            'title': entity.title,
            'description': entity.description,
            'icon': entity.icon,
            'points': entity.points,
            'difficulty_level': entity.difficulty_level,
            'criteria': entity.criteria,
            'earned_at': entity.earned_at,
            'curriculum_id': entity.curriculum_id,
            'module_id': entity.module_id,
            'lesson_id': entity.lesson_id,
            'metadata': entity.metadata,
            'is_earned': entity.is_earned
        }
    
    def _deserialize_entity(self, data: Dict[str, Any]) -> Achievement:
        """Deserialize dictionary to achievement."""
        return Achievement(
            id=data.get('id'),
            user_id=data.get('user_id', ''),
            achievement_type=data.get('achievement_type', 'completion'),
            title=data.get('title', ''),
            description=data.get('description', ''),
            icon=data.get('icon', ''),
            points=data.get('points', 0),
            difficulty_level=data.get('difficulty_level', 'beginner'),
            criteria=data.get('criteria', {}),
            earned_at=data.get('earned_at'),
            curriculum_id=data.get('curriculum_id'),
            module_id=data.get('module_id'),
            lesson_id=data.get('lesson_id'),
            metadata=data.get('metadata', {}),
            is_earned=data.get('is_earned', False)
        )
    
    def find_by_user(self, user_id: str) -> List[Achievement]:
        """Find all achievements for a user."""
        return self.find_by_field('user_id', user_id)
    
    def find_earned_achievements(self, user_id: str) -> List[Achievement]:
        """Find earned achievements for a user."""
        user_achievements = self.find_by_user(user_id)
        return [a for a in user_achievements if a.is_earned]
    
    def get_user_points(self, user_id: str) -> int:
        """Get total points for a user."""
        earned_achievements = self.find_earned_achievements(user_id)
        return sum(a.points for a in earned_achievements)


class LearningSessionRepository(BaseRepository[LearningSession]):
    """Repository for learning session management."""
    
    def __init__(self, storage):
        super().__init__(storage, "learning_session")
        
    def _validate_entity_fields(self, entity_data: Dict[str, Any]) -> None:
        """Validate learning session-specific fields."""
        required_fields = ['user_id', 'session_type', 'started_at']
        for field in required_fields:
            if not entity_data.get(field):
                raise ValidationError(f"Learning session {field} is required")
        
        # Validate session type
        valid_types = ['study', 'practice', 'assessment', 'review', 'project']
        if entity_data.get('session_type') not in valid_types:
            raise ValidationError(f"Session type must be one of: {valid_types}")
        
        # Validate duration
        duration = entity_data.get('duration_minutes', 0)
        if not isinstance(duration, int) or duration < 0:
            raise ValidationError("Duration must be a non-negative integer")
    
    def _serialize_entity(self, entity: LearningSession) -> Dict[str, Any]:
        """Serialize learning session to dictionary."""
        return {
            'id': entity.id,
            'user_id': entity.user_id,
            'session_type': entity.session_type,
            'curriculum_id': entity.curriculum_id,
            'module_id': entity.module_id,
            'lesson_id': entity.lesson_id,
            'content_ids': entity.content_ids,
            'duration_minutes': entity.duration_minutes,
            'activities': entity.activities,
            'progress_made': entity.progress_made,
            'performance_metrics': entity.performance_metrics,
            'notes': entity.notes,
            'started_at': entity.started_at,
            'ended_at': entity.ended_at,
            'created_at': entity.created_at
        }
    
    def _deserialize_entity(self, data: Dict[str, Any]) -> LearningSession:
        """Deserialize dictionary to learning session."""
        return LearningSession(
            id=data.get('id'),
            user_id=data.get('user_id', ''),
            session_type=data.get('session_type', 'study'),
            curriculum_id=data.get('curriculum_id'),
            module_id=data.get('module_id'),
            lesson_id=data.get('lesson_id'),
            content_ids=data.get('content_ids', []),
            duration_minutes=data.get('duration_minutes', 0),
            activities=data.get('activities', []),
            progress_made=data.get('progress_made', {}),
            performance_metrics=data.get('performance_metrics', {}),
            notes=data.get('notes', ''),
            started_at=data.get('started_at', ''),
            ended_at=data.get('ended_at'),
            created_at=data.get('created_at')
        )
    
    def find_by_user(self, user_id: str) -> List[LearningSession]:
        """Find all sessions for a user."""
        return self.find_by_field('user_id', user_id)
    
    def find_recent_sessions(self, user_id: str, days: int = 7) -> List[LearningSession]:
        """Find recent sessions for a user."""
        try:
            all_sessions = self.find_by_user(user_id)
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_iso = cutoff_date.isoformat()
            
            recent_sessions = []
            for session in all_sessions:
                if session.started_at >= cutoff_iso:
                    recent_sessions.append(session)
            
            return sorted(recent_sessions, key=lambda s: s.started_at, reverse=True)
            
        except Exception as e:
            raise RepositoryError(f"Failed to find recent sessions: {str(e)}")


class AssessmentRepository(BaseRepository[Assessment]):
    """Repository for assessment management."""
    
    def __init__(self, storage):
        super().__init__(storage, "assessment")
        
    def _validate_entity_fields(self, entity_data: Dict[str, Any]) -> None:
        """Validate assessment-specific fields."""
        required_fields = ['user_id', 'assessment_type', 'started_at']
        for field in required_fields:
            if not entity_data.get(field):
                raise ValidationError(f"Assessment {field} is required")
        
        # Validate assessment type
        valid_types = ['quiz', 'test', 'assignment', 'project', 'exam']
        if entity_data.get('assessment_type') not in valid_types:
            raise ValidationError(f"Assessment type must be one of: {valid_types}")
        
        # Validate result
        valid_results = [r.value for r in AssessmentResult]
        if entity_data.get('result') not in valid_results:
            raise ValidationError(f"Assessment result must be one of: {valid_results}")
        
        # Validate score
        score = entity_data.get('score_percentage', 0.0)
        if not isinstance(score, (int, float)) or score < 0 or score > 100:
            raise ValidationError("Score percentage must be between 0 and 100")
    
    def _serialize_entity(self, entity: Assessment) -> Dict[str, Any]:
        """Serialize assessment to dictionary."""
        return {
            'id': entity.id,
            'user_id': entity.user_id,
            'assessment_type': entity.assessment_type,
            'curriculum_id': entity.curriculum_id,
            'module_id': entity.module_id,
            'lesson_id': entity.lesson_id,
            'content_id': entity.content_id,
            'title': entity.title,
            'total_questions': entity.total_questions,
            'correct_answers': entity.correct_answers,
            'score_percentage': entity.score_percentage,
            'time_taken_minutes': entity.time_taken_minutes,
            'result': entity.result,
            'answers': entity.answers,
            'feedback': entity.feedback,
            'attempts': entity.attempts,
            'max_attempts': entity.max_attempts,
            'started_at': entity.started_at,
            'submitted_at': entity.submitted_at,
            'graded_at': entity.graded_at,
            'created_at': entity.created_at
        }
    
    def _deserialize_entity(self, data: Dict[str, Any]) -> Assessment:
        """Deserialize dictionary to assessment."""
        return Assessment(
            id=data.get('id'),
            user_id=data.get('user_id', ''),
            assessment_type=data.get('assessment_type', 'quiz'),
            curriculum_id=data.get('curriculum_id'),
            module_id=data.get('module_id'),
            lesson_id=data.get('lesson_id'),
            content_id=data.get('content_id'),
            title=data.get('title', ''),
            total_questions=data.get('total_questions', 0),
            correct_answers=data.get('correct_answers', 0),
            score_percentage=data.get('score_percentage', 0.0),
            time_taken_minutes=data.get('time_taken_minutes', 0),
            result=data.get('result', AssessmentResult.PENDING.value),
            answers=data.get('answers', []),
            feedback=data.get('feedback', {}),
            attempts=data.get('attempts', 1),
            max_attempts=data.get('max_attempts', 3),
            started_at=data.get('started_at', ''),
            submitted_at=data.get('submitted_at'),
            graded_at=data.get('graded_at'),
            created_at=data.get('created_at')
        )
    
    def find_by_user(self, user_id: str) -> List[Assessment]:
        """Find all assessments for a user."""
        return self.find_by_field('user_id', user_id)
    
    def find_by_result(self, user_id: str, result: str) -> List[Assessment]:
        """Find assessments by result for a user."""
        user_assessments = self.find_by_user(user_id)
        return [a for a in user_assessments if a.result == result]
    
    def get_assessment_stats(self, user_id: str) -> Dict[str, Any]:
        """Get assessment statistics for a user."""
        try:
            assessments = self.find_by_user(user_id)
            
            stats = {
                'total_assessments': len(assessments),
                'passed': 0,
                'failed': 0,
                'pending': 0,
                'average_score': 0.0,
                'total_time_minutes': 0,
                'by_type': {}
            }
            
            total_score = 0
            scored_assessments = 0
            
            for assessment in assessments:
                # Count by result
                if assessment.result == AssessmentResult.PASS.value:
                    stats['passed'] += 1
                elif assessment.result == AssessmentResult.FAIL.value:
                    stats['failed'] += 1
                else:
                    stats['pending'] += 1
                
                # Sum scores and time
                if assessment.score_percentage > 0:
                    total_score += assessment.score_percentage
                    scored_assessments += 1
                
                stats['total_time_minutes'] += assessment.time_taken_minutes
                
                # Count by type
                assessment_type = assessment.assessment_type
                if assessment_type not in stats['by_type']:
                    stats['by_type'][assessment_type] = {
                        'count': 0, 'passed': 0, 'average_score': 0.0
                    }
                
                stats['by_type'][assessment_type]['count'] += 1
                if assessment.result == AssessmentResult.PASS.value:
                    stats['by_type'][assessment_type]['passed'] += 1
            
            # Calculate averages
            if scored_assessments > 0:
                stats['average_score'] = total_score / scored_assessments
            
            return stats
            
        except Exception as e:
            raise RepositoryError(f"Failed to get assessment stats: {str(e)}")