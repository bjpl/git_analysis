"""
Vocabulary User Preferences and Personalization System
=====================================================

This module manages user preferences for vocabulary learning, including:
- Study preferences and habits
- Difficulty adjustment algorithms
- Personalized recommendation engine
- Learning style adaptation
- Goal setting and tracking
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import math
from collections import defaultdict


class LearningStyle(Enum):
    """Different learning style preferences."""
    VISUAL = "visual"           # Prefer images and visual aids
    AUDITORY = "auditory"       # Prefer audio and pronunciation
    KINESTHETIC = "kinesthetic" # Prefer hands-on interaction
    READING = "reading"         # Prefer text-based learning
    MIXED = "mixed"             # No strong preference


class StudyMode(Enum):
    """Preferred study modes."""
    FLASHCARDS = "flashcards"
    MULTIPLE_CHOICE = "multiple_choice"
    TYPING_PRACTICE = "typing_practice"
    LISTENING_COMPREHENSION = "listening_comprehension"
    CONTEXT_LEARNING = "context_learning"
    SPACED_REPETITION = "spaced_repetition"


class DifficultyPreference(Enum):
    """How user prefers difficulty progression."""
    CONSERVATIVE = "conservative"   # Stick to easier words longer
    BALANCED = "balanced"          # Standard progression
    AGGRESSIVE = "aggressive"      # Challenge with harder words quickly
    ADAPTIVE = "adaptive"          # AI-driven difficulty adjustment


@dataclass
class StudyGoal:
    """Individual study goal tracking."""
    id: str
    name: str
    description: str
    target_value: int
    current_value: int = 0
    target_date: str = ""
    created_date: str = ""
    completed: bool = False
    goal_type: str = "daily"  # daily, weekly, monthly, custom
    
    def get_progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.target_value <= 0:
            return 0.0
        return min((self.current_value / self.target_value) * 100, 100.0)
    
    def is_overdue(self) -> bool:
        """Check if goal is overdue."""
        if not self.target_date or self.completed:
            return False
        target = datetime.fromisoformat(self.target_date)
        return datetime.now() > target


@dataclass
class LearningPreferences:
    """User's learning preferences and settings."""
    # Study preferences
    daily_study_goal: int = 20  # words per day
    session_length_minutes: int = 15
    max_new_words_per_session: int = 5
    review_ratio: float = 0.7  # ratio of review vs new words
    
    # Difficulty settings
    difficulty_preference: DifficultyPreference = DifficultyPreference.BALANCED
    auto_difficulty_adjustment: bool = True
    difficulty_adjustment_threshold: float = 0.75  # accuracy threshold for difficulty increase
    
    # Learning style
    preferred_learning_style: LearningStyle = LearningStyle.MIXED
    preferred_study_modes: List[StudyMode] = field(default_factory=lambda: [StudyMode.FLASHCARDS])
    
    # Timing preferences
    preferred_study_times: List[str] = field(default_factory=list)  # "09:00", "18:00", etc.
    reminder_enabled: bool = True
    reminder_frequency_hours: int = 24
    
    # Content preferences
    preferred_themes: List[str] = field(default_factory=list)
    avoid_themes: List[str] = field(default_factory=list)
    prioritize_high_frequency_words: bool = True
    include_pronunciation: bool = True
    include_example_sentences: bool = True
    
    # UI preferences
    show_learning_statistics: bool = True
    show_progress_animations: bool = True
    dark_mode: bool = False
    font_size: str = "medium"  # small, medium, large
    
    # Advanced settings
    spaced_repetition_enabled: bool = True
    adaptive_scheduling: bool = True
    forgetting_curve_factor: float = 0.8
    minimum_interval_days: int = 1
    maximum_interval_days: int = 365


@dataclass
class PersonalizationData:
    """Data used for personalizing the learning experience."""
    # Performance patterns
    best_study_times: List[str] = field(default_factory=list)
    worst_study_times: List[str] = field(default_factory=list)
    average_session_accuracy: float = 0.0
    average_response_time_ms: float = 0.0
    
    # Difficulty patterns
    strengths_by_theme: Dict[str, float] = field(default_factory=dict)
    weaknesses_by_theme: Dict[str, float] = field(default_factory=dict)
    optimal_difficulty_level: int = 3
    
    # Learning patterns
    most_effective_study_mode: StudyMode = StudyMode.FLASHCARDS
    learning_velocity: float = 1.0  # words mastered per hour of study
    retention_rate: float = 0.8  # percentage of words retained
    
    # Behavioral patterns
    study_frequency_pattern: Dict[str, int] = field(default_factory=dict)  # day_of_week -> session_count
    peak_performance_hours: List[int] = field(default_factory=list)
    concentration_span_minutes: int = 15


class VocabularyPreferencesManager:
    """Manages user preferences and personalization for vocabulary learning."""
    
    def __init__(self, data_dir: Path, user_id: str = "default"):
        self.data_dir = data_dir
        self.user_id = user_id
        self.db_path = data_dir / f"preferences_{user_id}.db"
        
        # Current preferences
        self.preferences = LearningPreferences()
        self.personalization = PersonalizationData()
        self.goals: Dict[str, StudyGoal] = {}
        
        # Analytics data
        self.performance_history: List[Dict[str, Any]] = []
        self.adaptation_history: List[Dict[str, Any]] = []
        
        self._initialize_database()
        self._load_preferences()
    
    def _initialize_database(self):
        """Initialize preferences database."""
        with sqlite3.connect(self.db_path) as conn:
            # User preferences table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    last_updated TEXT NOT NULL
                )
            """)
            
            # Study goals table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS study_goals (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    target_value INTEGER NOT NULL,
                    current_value INTEGER DEFAULT 0,
                    target_date TEXT,
                    created_date TEXT NOT NULL,
                    completed BOOLEAN DEFAULT FALSE,
                    goal_type TEXT NOT NULL
                )
            """)
            
            # Performance tracking table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    session_id TEXT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    context_data TEXT
                )
            """)
            
            # Adaptation history table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS adaptation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    adaptation_type TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    reason TEXT,
                    effectiveness_score REAL
                )
            """)
            
            conn.commit()
    
    def _load_preferences(self):
        """Load user preferences from database."""
        with sqlite3.connect(self.db_path) as conn:
            # Load preferences
            rows = conn.execute(
                "SELECT key, value, data_type FROM user_preferences"
            ).fetchall()
            
            prefs_dict = {}
            for key, value, data_type in rows:
                if data_type == 'int':
                    prefs_dict[key] = int(value)
                elif data_type == 'float':
                    prefs_dict[key] = float(value)
                elif data_type == 'bool':
                    prefs_dict[key] = value.lower() == 'true'
                elif data_type == 'json':
                    prefs_dict[key] = json.loads(value)
                elif data_type == 'enum':
                    # Handle enum values
                    if 'difficulty_preference' in key:
                        prefs_dict[key] = DifficultyPreference(value)
                    elif 'learning_style' in key:
                        prefs_dict[key] = LearningStyle(value)
                    elif 'study_modes' in key:
                        prefs_dict[key] = [StudyMode(mode) for mode in json.loads(value)]
                else:
                    prefs_dict[key] = value
            
            # Update preferences object
            if prefs_dict:
                for key, value in prefs_dict.items():
                    if hasattr(self.preferences, key):
                        setattr(self.preferences, key, value)
            
            # Load goals
            goal_rows = conn.execute("SELECT * FROM study_goals").fetchall()
            for row in goal_rows:
                goal = StudyGoal(
                    id=row[0],
                    name=row[1],
                    description=row[2] or "",
                    target_value=row[3],
                    current_value=row[4],
                    target_date=row[5] or "",
                    created_date=row[6],
                    completed=bool(row[7]),
                    goal_type=row[8]
                )
                self.goals[goal.id] = goal
    
    def save_preferences(self):
        """Save current preferences to database."""
        with sqlite3.connect(self.db_path) as conn:
            # Save preferences
            prefs_dict = asdict(self.preferences)
            
            for key, value in prefs_dict.items():
                if isinstance(value, Enum):
                    value_str = value.value
                    data_type = 'enum'
                elif isinstance(value, list) and value and isinstance(value[0], Enum):
                    value_str = json.dumps([item.value for item in value])
                    data_type = 'enum'
                elif isinstance(value, (list, dict)):
                    value_str = json.dumps(value)
                    data_type = 'json'
                elif isinstance(value, bool):
                    value_str = str(value).lower()
                    data_type = 'bool'
                elif isinstance(value, int):
                    value_str = str(value)
                    data_type = 'int'
                elif isinstance(value, float):
                    value_str = str(value)
                    data_type = 'float'
                else:
                    value_str = str(value)
                    data_type = 'str'
                
                conn.execute("""
                    INSERT OR REPLACE INTO user_preferences 
                    (key, value, data_type, last_updated)
                    VALUES (?, ?, ?, ?)
                """, (key, value_str, data_type, datetime.now().isoformat()))
            
            conn.commit()
    
    def update_preference(self, key: str, value: Any):
        """Update a single preference."""
        if hasattr(self.preferences, key):
            setattr(self.preferences, key, value)
            self.save_preferences()
            
            # Log adaptation if this is an AI-driven change
            self._log_adaptation('preference_update', key, str(value), 
                               f"User updated {key}")
    
    def create_goal(self, name: str, description: str, target_value: int,
                   target_date: str = "", goal_type: str = "daily") -> str:
        """Create a new study goal."""
        import uuid
        goal_id = str(uuid.uuid4())[:8]
        
        goal = StudyGoal(
            id=goal_id,
            name=name,
            description=description,
            target_value=target_value,
            target_date=target_date,
            created_date=datetime.now().isoformat(),
            goal_type=goal_type
        )
        
        self.goals[goal_id] = goal
        
        # Save to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO study_goals 
                (id, name, description, target_value, target_date, created_date, goal_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                goal.id, goal.name, goal.description, goal.target_value,
                goal.target_date, goal.created_date, goal.goal_type
            ))
            conn.commit()
        
        return goal_id
    
    def update_goal_progress(self, goal_id: str, progress: int):
        """Update progress on a goal."""
        if goal_id in self.goals:
            goal = self.goals[goal_id]
            goal.current_value = progress
            
            # Check if goal is completed
            if progress >= goal.target_value:
                goal.completed = True
            
            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE study_goals SET 
                        current_value = ?, completed = ?
                    WHERE id = ?
                """, (goal.current_value, goal.completed, goal_id))
                conn.commit()
    
    def get_active_goals(self) -> List[StudyGoal]:
        """Get all active (non-completed) goals."""
        return [goal for goal in self.goals.values() if not goal.completed]
    
    def get_overdue_goals(self) -> List[StudyGoal]:
        """Get goals that are overdue."""
        return [goal for goal in self.goals.values() if goal.is_overdue()]
    
    def record_performance(self, session_id: str, metrics: Dict[str, float],
                          context: Dict[str, Any] = None):
        """Record performance metrics for personalization."""
        timestamp = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            for metric_name, value in metrics.items():
                conn.execute("""
                    INSERT INTO performance_logs 
                    (timestamp, session_id, metric_name, metric_value, context_data)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    timestamp, session_id, metric_name, float(value),
                    json.dumps(context or {})
                ))
            conn.commit()
        
        # Update personalization data
        self._update_personalization_data(metrics, context or {})
    
    def _update_personalization_data(self, metrics: Dict[str, float], 
                                   context: Dict[str, Any]):
        """Update personalization data based on performance."""
        # Update averages
        if 'accuracy' in metrics:
            current_avg = self.personalization.average_session_accuracy
            new_accuracy = metrics['accuracy']
            # Exponential moving average
            self.personalization.average_session_accuracy = (
                current_avg * 0.9 + new_accuracy * 0.1
            )
        
        if 'response_time_ms' in metrics:
            current_avg = self.personalization.average_response_time_ms
            new_time = metrics['response_time_ms']
            self.personalization.average_response_time_ms = (
                current_avg * 0.9 + new_time * 0.1
            )
        
        # Track study time patterns
        if 'study_time' in context:
            study_hour = datetime.now().hour
            if study_hour not in self.personalization.peak_performance_hours:
                # Add hour if performance is above average
                if metrics.get('accuracy', 0) > self.personalization.average_session_accuracy:
                    self.personalization.peak_performance_hours.append(study_hour)
        
        # Update theme strengths/weaknesses
        if 'themes' in context and 'accuracy' in metrics:
            themes = context['themes']
            accuracy = metrics['accuracy']
            
            for theme in themes:
                current_strength = self.personalization.strengths_by_theme.get(theme, 50.0)
                # Update based on performance
                if accuracy > 80:
                    self.personalization.strengths_by_theme[theme] = (
                        current_strength * 0.9 + accuracy * 0.1
                    )
                elif accuracy < 60:
                    self.personalization.weaknesses_by_theme[theme] = (
                        self.personalization.weaknesses_by_theme.get(theme, 50.0) * 0.9 + 
                        (100 - accuracy) * 0.1
                    )
    
    def get_study_recommendations(self, available_words: List[Any]) -> Dict[str, Any]:
        """Generate personalized study recommendations."""
        recommendations = {
            'recommended_words': [],
            'suggested_session_length': self.preferences.session_length_minutes,
            'recommended_study_mode': self.personalization.most_effective_study_mode.value,
            'optimal_difficulty_mix': {},
            'personalization_notes': []
        }
        
        # Recommend words based on preferences and performance
        preferred_themes = set(self.preferences.preferred_themes)
        weak_themes = set(self.personalization.weaknesses_by_theme.keys())
        
        word_scores = []
        for word in available_words:
            score = 0
            
            # Theme preference bonus
            word_themes = getattr(word, 'themes', set())
            if preferred_themes.intersection(word_themes):
                score += 20
            
            # Weakness improvement bonus
            if weak_themes.intersection(word_themes):
                score += 30
                recommendations['personalization_notes'].append(
                    f"Focusing on weak theme: {list(weak_themes.intersection(word_themes))[0]}"
                )
            
            # Difficulty appropriateness
            word_difficulty = getattr(word, 'difficulty', 3)
            optimal_difficulty = self.personalization.optimal_difficulty_level
            
            difficulty_diff = abs(word_difficulty - optimal_difficulty)
            if difficulty_diff <= 1:
                score += 15
            elif difficulty_diff == 2:
                score += 5
            
            # Priority bonus
            word_priority = getattr(word, 'priority', 3)
            score += word_priority * 5
            
            # Due date urgency
            if hasattr(word, 'is_due_for_review') and word.is_due_for_review():
                score += 40
            
            word_scores.append((word, score))
        
        # Sort by score and take top recommendations
        word_scores.sort(key=lambda x: x[1], reverse=True)
        max_words = min(self.preferences.max_new_words_per_session, len(word_scores))
        recommendations['recommended_words'] = [
            word for word, score in word_scores[:max_words]
        ]
        
        # Suggest session adjustments based on performance
        if self.personalization.average_session_accuracy < 60:
            recommendations['suggested_session_length'] = max(
                self.preferences.session_length_minutes - 5, 10
            )
            recommendations['personalization_notes'].append(
                "Shortened session due to low accuracy - focus on quality over quantity"
            )
        elif self.personalization.average_session_accuracy > 90:
            recommendations['suggested_session_length'] = min(
                self.preferences.session_length_minutes + 5, 30
            )
            recommendations['personalization_notes'].append(
                "Extended session - you're performing excellently!"
            )
        
        return recommendations
    
    def adapt_difficulty(self, word_performance: Dict[str, float]) -> Dict[str, Any]:
        """Adapt difficulty settings based on performance."""
        if not self.preferences.auto_difficulty_adjustment:
            return {'adapted': False, 'reason': 'Auto-adjustment disabled'}
        
        adaptations = {}
        threshold = self.preferences.difficulty_adjustment_threshold
        
        # Analyze recent performance
        recent_accuracy = word_performance.get('accuracy', 0)
        response_time = word_performance.get('avg_response_time_ms', 0)
        
        # Adjust optimal difficulty level
        current_optimal = self.personalization.optimal_difficulty_level
        
        if recent_accuracy > threshold + 0.15 and response_time < 3000:
            # Performance is excellent, increase difficulty
            new_optimal = min(current_optimal + 1, 5)
            if new_optimal != current_optimal:
                adaptations['optimal_difficulty_level'] = new_optimal
                self.personalization.optimal_difficulty_level = new_optimal
                
        elif recent_accuracy < threshold - 0.15 or response_time > 8000:
            # Performance is struggling, decrease difficulty
            new_optimal = max(current_optimal - 1, 1)
            if new_optimal != current_optimal:
                adaptations['optimal_difficulty_level'] = new_optimal
                self.personalization.optimal_difficulty_level = new_optimal
        
        # Adjust session length based on concentration patterns
        if response_time > 5000:  # Slow responses indicate fatigue
            new_length = max(self.preferences.session_length_minutes - 2, 10)
            if new_length != self.preferences.session_length_minutes:
                adaptations['session_length_minutes'] = new_length
                self.preferences.session_length_minutes = new_length
        
        # Log adaptations
        if adaptations:
            for key, value in adaptations.items():
                self._log_adaptation('auto_adaptation', key, str(value), 
                                   f"Performance-based adjustment: accuracy={recent_accuracy:.2f}")
        
        return {
            'adapted': bool(adaptations),
            'adaptations': adaptations,
            'reason': f"Based on accuracy: {recent_accuracy:.2f}, response time: {response_time:.0f}ms"
        }
    
    def _log_adaptation(self, adaptation_type: str, parameter: str, 
                       new_value: str, reason: str, effectiveness: float = 0.0):
        """Log an adaptation for tracking effectiveness."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO adaptation_history 
                (timestamp, adaptation_type, old_value, new_value, reason, effectiveness_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                adaptation_type,
                parameter,  # Using parameter as old_value for simplicity
                new_value,
                reason,
                effectiveness
            ))
            conn.commit()
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Generate insights about learning patterns and progress."""
        insights = {
            'learning_velocity': self.personalization.learning_velocity,
            'retention_rate': self.personalization.retention_rate,
            'strongest_themes': [],
            'areas_for_improvement': [],
            'study_pattern_analysis': {},
            'goal_progress_summary': {},
            'recommendations': []
        }
        
        # Analyze theme performance
        if self.personalization.strengths_by_theme:
            strongest = max(self.personalization.strengths_by_theme.items(), 
                          key=lambda x: x[1])
            insights['strongest_themes'] = [strongest[0]]
        
        if self.personalization.weaknesses_by_theme:
            weakest = max(self.personalization.weaknesses_by_theme.items(), 
                        key=lambda x: x[1])
            insights['areas_for_improvement'] = [weakest[0]]
        
        # Goal progress summary
        active_goals = self.get_active_goals()
        if active_goals:
            total_progress = sum(goal.get_progress_percentage() for goal in active_goals)
            avg_progress = total_progress / len(active_goals)
            insights['goal_progress_summary'] = {
                'active_goals': len(active_goals),
                'average_progress': avg_progress,
                'overdue_goals': len(self.get_overdue_goals())
            }
        
        # Generate recommendations
        if self.personalization.average_session_accuracy < 70:
            insights['recommendations'].append(
                "Consider reducing difficulty or session length to improve accuracy"
            )
        
        if not self.personalization.peak_performance_hours:
            insights['recommendations'].append(
                "Try studying at different times to find your optimal study hours"
            )
        
        return insights
    
    def export_preferences(self) -> str:
        """Export user preferences and data."""
        export_data = {
            'preferences': asdict(self.preferences),
            'personalization': asdict(self.personalization),
            'goals': {goal_id: asdict(goal) for goal_id, goal in self.goals.items()},
            'export_timestamp': datetime.now().isoformat(),
            'user_id': self.user_id
        }
        
        # Handle enum serialization
        def enum_serializer(obj):
            if isinstance(obj, Enum):
                return obj.value
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        return json.dumps(export_data, indent=2, default=enum_serializer)
    
    def import_preferences(self, data: str) -> bool:
        """Import user preferences from JSON data."""
        try:
            import_data = json.loads(data)
            
            # Import preferences
            if 'preferences' in import_data:
                prefs_dict = import_data['preferences']
                
                # Handle enum conversion
                if 'difficulty_preference' in prefs_dict:
                    prefs_dict['difficulty_preference'] = DifficultyPreference(
                        prefs_dict['difficulty_preference']
                    )
                if 'preferred_learning_style' in prefs_dict:
                    prefs_dict['preferred_learning_style'] = LearningStyle(
                        prefs_dict['preferred_learning_style']
                    )
                if 'preferred_study_modes' in prefs_dict:
                    prefs_dict['preferred_study_modes'] = [
                        StudyMode(mode) for mode in prefs_dict['preferred_study_modes']
                    ]
                
                # Update preferences
                for key, value in prefs_dict.items():
                    if hasattr(self.preferences, key):
                        setattr(self.preferences, key, value)
            
            # Import goals
            if 'goals' in import_data:
                for goal_id, goal_data in import_data['goals'].items():
                    goal = StudyGoal(**goal_data)
                    self.goals[goal_id] = goal
            
            # Save imported data
            self.save_preferences()
            return True
            
        except Exception as e:
            print(f"Error importing preferences: {e}")
            return False