"""
Comprehensive Vocabulary Analytics and Insights System
=====================================================

Advanced analytics engine for vocabulary learning with features including:
- Learning progress tracking and visualization
- Performance pattern analysis
- Predictive learning models
- Personalized insights and recommendations  
- Comparative analysis and benchmarking
- Study habit optimization
- Memory retention modeling
"""

import json
import sqlite3
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import math
import statistics
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
import pandas as pd


class AnalyticsTimeframe(Enum):
    """Time frames for analytics analysis."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ALL_TIME = "all_time"


class MetricType(Enum):
    """Types of metrics tracked."""
    ACCURACY = "accuracy"
    SPEED = "speed"
    RETENTION = "retention"
    CONSISTENCY = "consistency"
    DIFFICULTY_PROGRESSION = "difficulty_progression"
    THEME_MASTERY = "theme_mastery"
    STUDY_FREQUENCY = "study_frequency"
    SESSION_LENGTH = "session_length"


@dataclass
class LearningMetric:
    """Individual learning metric data point."""
    timestamp: str
    metric_type: MetricType
    value: float
    context: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    word_id: Optional[str] = None


@dataclass
class PerformanceTrend:
    """Performance trend analysis results."""
    metric: MetricType
    timeframe: AnalyticsTimeframe
    trend_direction: str  # "improving", "declining", "stable"
    trend_strength: float  # -1.0 to 1.0
    current_value: float
    change_from_previous: float
    data_points: List[Tuple[str, float]]
    statistical_confidence: float


@dataclass
class LearningInsight:
    """Individual learning insight or recommendation."""
    insight_id: str
    category: str  # "strength", "weakness", "opportunity", "warning"
    title: str
    description: str
    confidence: float
    actionable_steps: List[str]
    supporting_data: Dict[str, Any]
    priority: int  # 1-5, with 1 being highest priority


@dataclass
class ComprehensiveAnalysis:
    """Complete analytics analysis results."""
    user_id: str
    analysis_date: str
    timeframe: AnalyticsTimeframe
    
    # Core metrics
    overall_progress_score: float
    learning_velocity: float  # words mastered per hour
    retention_rate: float
    consistency_score: float
    
    # Trends
    performance_trends: List[PerformanceTrend]
    
    # Detailed breakdowns
    theme_performance: Dict[str, Dict[str, float]]
    difficulty_progression: Dict[str, float]
    temporal_patterns: Dict[str, Any]
    
    # Insights and recommendations
    insights: List[LearningInsight]
    next_study_recommendations: List[Dict[str, Any]]
    
    # Predictions
    predicted_mastery_dates: Dict[str, str]  # word_id -> predicted_date
    estimated_study_time_needed: Dict[str, int]  # theme -> minutes
    
    # Comparative data
    percentile_rankings: Dict[str, float]
    benchmark_comparisons: Dict[str, Dict[str, float]]


class VocabularyAnalyticsEngine:
    """Advanced analytics engine for vocabulary learning data."""
    
    def __init__(self, vocabulary_manager, session_manager, preferences_manager):
        self.vocabulary_manager = vocabulary_manager
        self.session_manager = session_manager
        self.preferences_manager = preferences_manager
        
        # Analytics database
        self.analytics_db_path = vocabulary_manager.data_dir / "vocabulary_analytics.db"
        self._initialize_analytics_db()
        
        # Cached data for performance
        self.metrics_cache: Dict[str, List[LearningMetric]] = {}
        self.analysis_cache: Dict[str, ComprehensiveAnalysis] = {}
        
        # Machine learning models
        self.retention_model = None
        self.difficulty_model = None
        self.performance_model = None
    
    def _initialize_analytics_db(self):
        """Initialize analytics database schema."""
        with sqlite3.connect(self.analytics_db_path) as conn:
            # Learning metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    context TEXT,
                    session_id TEXT,
                    word_id TEXT,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Analysis results cache
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analysis_cache (
                    cache_key TEXT PRIMARY KEY,
                    analysis_data TEXT NOT NULL,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    expiry_date TEXT
                )
            """)
            
            # Performance benchmarks
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_benchmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_type TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    percentile_50 REAL,
                    percentile_75 REAL,
                    percentile_90 REAL,
                    percentile_95 REAL,
                    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User achievements
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_achievements (
                    achievement_id TEXT PRIMARY KEY,
                    achievement_name TEXT NOT NULL,
                    description TEXT,
                    earned_date TEXT NOT NULL,
                    metric_value REAL,
                    category TEXT
                )
            """)
            
            # Create indices
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON learning_metrics(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_type ON learning_metrics(metric_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_session ON learning_metrics(session_id)")
            
            conn.commit()
    
    def record_learning_metric(self, metric: LearningMetric):
        """Record a learning metric."""
        with sqlite3.connect(self.analytics_db_path) as conn:
            conn.execute("""
                INSERT INTO learning_metrics 
                (timestamp, metric_type, value, context, session_id, word_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                metric.timestamp,
                metric.metric_type.value,
                metric.value,
                json.dumps(metric.context),
                metric.session_id,
                metric.word_id
            ))
            conn.commit()
        
        # Invalidate relevant caches
        cache_key = f"{metric.metric_type.value}_metrics"
        if cache_key in self.metrics_cache:
            del self.metrics_cache[cache_key]
    
    def get_comprehensive_analysis(self, timeframe: AnalyticsTimeframe = AnalyticsTimeframe.MONTHLY,
                                  force_refresh: bool = False) -> ComprehensiveAnalysis:
        """Generate comprehensive learning analysis."""
        cache_key = f"analysis_{timeframe.value}_{datetime.now().strftime('%Y%m%d')}"
        
        # Check cache first
        if not force_refresh and cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        # Check database cache
        cached_analysis = self._get_cached_analysis(cache_key)
        if cached_analysis and not force_refresh:
            return cached_analysis
        
        # Generate new analysis
        analysis = self._generate_comprehensive_analysis(timeframe)
        
        # Cache results
        self.analysis_cache[cache_key] = analysis
        self._cache_analysis(cache_key, analysis)
        
        return analysis
    
    def _generate_comprehensive_analysis(self, timeframe: AnalyticsTimeframe) -> ComprehensiveAnalysis:
        """Generate comprehensive analysis from scratch."""
        end_date = datetime.now()
        
        # Determine date range
        if timeframe == AnalyticsTimeframe.DAILY:
            start_date = end_date - timedelta(days=1)
        elif timeframe == AnalyticsTimeframe.WEEKLY:
            start_date = end_date - timedelta(weeks=1)
        elif timeframe == AnalyticsTimeframe.MONTHLY:
            start_date = end_date - timedelta(days=30)
        elif timeframe == AnalyticsTimeframe.QUARTERLY:
            start_date = end_date - timedelta(days=90)
        elif timeframe == AnalyticsTimeframe.YEARLY:
            start_date = end_date - timedelta(days=365)
        else:  # ALL_TIME
            start_date = datetime(2020, 1, 1)  # Far enough back
        
        # Gather data
        metrics = self._get_metrics_in_range(start_date, end_date)
        vocabulary_entries = list(self.vocabulary_manager.vocabulary_cache.values())
        
        # Calculate core metrics
        overall_progress_score = self._calculate_overall_progress(vocabulary_entries)
        learning_velocity = self._calculate_learning_velocity(metrics, vocabulary_entries)
        retention_rate = self._calculate_retention_rate(vocabulary_entries)
        consistency_score = self._calculate_consistency_score(metrics)
        
        # Analyze trends
        performance_trends = self._analyze_performance_trends(metrics, timeframe)
        
        # Detailed breakdowns
        theme_performance = self._analyze_theme_performance(vocabulary_entries)
        difficulty_progression = self._analyze_difficulty_progression(vocabulary_entries)
        temporal_patterns = self._analyze_temporal_patterns(metrics)
        
        # Generate insights
        insights = self._generate_insights(
            vocabulary_entries, metrics, theme_performance, performance_trends
        )
        
        # Study recommendations
        next_study_recommendations = self._generate_study_recommendations(
            vocabulary_entries, theme_performance, insights
        )
        
        # Predictions
        predicted_mastery_dates = self._predict_mastery_dates(vocabulary_entries)
        estimated_study_time = self._estimate_study_time_needed(theme_performance)
        
        # Benchmarking
        percentile_rankings = self._calculate_percentile_rankings(overall_progress_score, learning_velocity)
        benchmark_comparisons = self._get_benchmark_comparisons(metrics)
        
        return ComprehensiveAnalysis(
            user_id=self.preferences_manager.user_id,
            analysis_date=datetime.now().isoformat(),
            timeframe=timeframe,
            overall_progress_score=overall_progress_score,
            learning_velocity=learning_velocity,
            retention_rate=retention_rate,
            consistency_score=consistency_score,
            performance_trends=performance_trends,
            theme_performance=theme_performance,
            difficulty_progression=difficulty_progression,
            temporal_patterns=temporal_patterns,
            insights=insights,
            next_study_recommendations=next_study_recommendations,
            predicted_mastery_dates=predicted_mastery_dates,
            estimated_study_time_needed=estimated_study_time,
            percentile_rankings=percentile_rankings,
            benchmark_comparisons=benchmark_comparisons
        )
    
    def _get_metrics_in_range(self, start_date: datetime, end_date: datetime) -> List[LearningMetric]:
        """Get learning metrics within date range."""
        metrics = []
        
        with sqlite3.connect(self.analytics_db_path) as conn:
            rows = conn.execute("""
                SELECT timestamp, metric_type, value, context, session_id, word_id
                FROM learning_metrics
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp
            """, (start_date.isoformat(), end_date.isoformat())).fetchall()
            
            for row in rows:
                metric = LearningMetric(
                    timestamp=row[0],
                    metric_type=MetricType(row[1]),
                    value=row[2],
                    context=json.loads(row[3]) if row[3] else {},
                    session_id=row[4],
                    word_id=row[5]
                )
                metrics.append(metric)
        
        return metrics
    
    def _calculate_overall_progress(self, entries: List) -> float:
        """Calculate overall learning progress score (0-100)."""
        if not entries:
            return 0.0
        
        total_score = 0.0
        
        for entry in entries:
            # Base score from learning status
            status_scores = {
                'new': 0,
                'learning': 25,
                'reviewing': 50,
                'mastered': 100
            }
            base_score = status_scores.get(entry.status.value, 0)
            
            # Adjust for accuracy
            accuracy = entry.frequency_data.calculate_accuracy()
            accuracy_multiplier = accuracy / 100.0
            
            # Adjust for study frequency
            study_sessions = entry.frequency_data.study_sessions
            frequency_bonus = min(study_sessions / 10.0, 1.0) * 10  # Up to 10 bonus points
            
            entry_score = (base_score * accuracy_multiplier) + frequency_bonus
            total_score += entry_score
        
        return min(total_score / len(entries), 100.0)
    
    def _calculate_learning_velocity(self, metrics: List[LearningMetric], entries: List) -> float:
        """Calculate words mastered per hour of study."""
        if not metrics or not entries:
            return 0.0
        
        # Count mastered words
        mastered_words = sum(1 for entry in entries if entry.status.value == 'mastered')
        
        # Calculate total study time from metrics
        study_time_metrics = [m for m in metrics if m.metric_type == MetricType.SESSION_LENGTH]
        total_study_hours = sum(m.value for m in study_time_metrics) / 60.0  # Convert to hours
        
        if total_study_hours == 0:
            return 0.0
        
        return mastered_words / total_study_hours
    
    def _calculate_retention_rate(self, entries: List) -> float:
        """Calculate overall retention rate."""
        if not entries:
            return 0.0
        
        total_accuracy = sum(entry.frequency_data.calculate_accuracy() for entry in entries)
        return total_accuracy / len(entries)
    
    def _calculate_consistency_score(self, metrics: List[LearningMetric]) -> float:
        """Calculate study consistency score."""
        if not metrics:
            return 0.0
        
        # Group metrics by date
        daily_sessions = defaultdict(int)
        for metric in metrics:
            date = metric.timestamp[:10]  # YYYY-MM-DD
            if metric.metric_type == MetricType.SESSION_LENGTH:
                daily_sessions[date] += 1
        
        if not daily_sessions:
            return 0.0
        
        # Calculate consistency (lower variance = higher consistency)
        session_counts = list(daily_sessions.values())
        if len(session_counts) <= 1:
            return 100.0
        
        mean_sessions = statistics.mean(session_counts)
        std_dev = statistics.stdev(session_counts)
        
        # Convert to 0-100 scale (lower std dev = higher score)
        consistency = max(0, 100 - (std_dev / mean_sessions * 50))
        return min(consistency, 100.0)
    
    def _analyze_performance_trends(self, metrics: List[LearningMetric], 
                                  timeframe: AnalyticsTimeframe) -> List[PerformanceTrend]:
        """Analyze performance trends for different metrics."""
        trends = []
        
        for metric_type in MetricType:
            metric_data = [m for m in metrics if m.metric_type == metric_type]
            if len(metric_data) < 2:
                continue
            
            # Group by time periods
            time_groups = self._group_metrics_by_time(metric_data, timeframe)
            if len(time_groups) < 2:
                continue
            
            # Calculate trend
            time_points = sorted(time_groups.keys())
            values = [statistics.mean(time_groups[tp]) for tp in time_points]
            
            # Linear regression for trend
            x = np.array(range(len(values))).reshape(-1, 1)
            y = np.array(values)
            
            model = LinearRegression().fit(x, y)
            trend_strength = model.coef_[0]
            
            # Determine trend direction
            if abs(trend_strength) < 0.1:
                direction = "stable"
            elif trend_strength > 0:
                direction = "improving"
            else:
                direction = "declining"
            
            # Statistical confidence (R-squared)
            confidence = model.score(x, y)
            
            trend = PerformanceTrend(
                metric=metric_type,
                timeframe=timeframe,
                trend_direction=direction,
                trend_strength=trend_strength,
                current_value=values[-1] if values else 0,
                change_from_previous=values[-1] - values[-2] if len(values) >= 2 else 0,
                data_points=list(zip(time_points, values)),
                statistical_confidence=confidence
            )
            trends.append(trend)
        
        return trends
    
    def _group_metrics_by_time(self, metrics: List[LearningMetric], 
                             timeframe: AnalyticsTimeframe) -> Dict[str, List[float]]:
        """Group metrics by time periods."""
        groups = defaultdict(list)
        
        for metric in metrics:
            timestamp = datetime.fromisoformat(metric.timestamp)
            
            if timeframe == AnalyticsTimeframe.DAILY:
                key = timestamp.strftime('%Y-%m-%d')
            elif timeframe == AnalyticsTimeframe.WEEKLY:
                # ISO week
                key = f"{timestamp.year}-W{timestamp.isocalendar()[1]:02d}"
            elif timeframe == AnalyticsTimeframe.MONTHLY:
                key = timestamp.strftime('%Y-%m')
            else:
                key = timestamp.strftime('%Y-%m-%d')
            
            groups[key].append(metric.value)
        
        return groups
    
    def _analyze_theme_performance(self, entries: List) -> Dict[str, Dict[str, float]]:
        """Analyze performance by theme."""
        theme_stats = defaultdict(lambda: {'total': 0, 'accuracy': 0, 'mastered': 0})
        
        for entry in entries:
            for theme in entry.themes:
                theme_stats[theme]['total'] += 1
                theme_stats[theme]['accuracy'] += entry.frequency_data.calculate_accuracy()
                
                if entry.status.value == 'mastered':
                    theme_stats[theme]['mastered'] += 1
        
        # Calculate final statistics
        theme_performance = {}
        for theme, stats in theme_stats.items():
            if stats['total'] > 0:
                theme_performance[theme] = {
                    'average_accuracy': stats['accuracy'] / stats['total'],
                    'mastery_rate': (stats['mastered'] / stats['total']) * 100,
                    'total_words': stats['total'],
                    'mastered_words': stats['mastered']
                }
        
        return theme_performance
    
    def _analyze_difficulty_progression(self, entries: List) -> Dict[str, float]:
        """Analyze progression through difficulty levels."""
        difficulty_stats = defaultdict(int)
        difficulty_mastered = defaultdict(int)
        
        for entry in entries:
            difficulty = entry.difficulty.name
            difficulty_stats[difficulty] += 1
            
            if entry.status.value == 'mastered':
                difficulty_mastered[difficulty] += 1
        
        progression = {}
        for difficulty, total in difficulty_stats.items():
            mastered = difficulty_mastered[difficulty]
            progression[difficulty] = (mastered / total) * 100 if total > 0 else 0
        
        return progression
    
    def _analyze_temporal_patterns(self, metrics: List[LearningMetric]) -> Dict[str, Any]:
        """Analyze temporal learning patterns."""
        if not metrics:
            return {}
        
        # Hour of day analysis
        hourly_performance = defaultdict(list)
        daily_sessions = defaultdict(int)
        
        for metric in metrics:
            timestamp = datetime.fromisoformat(metric.timestamp)
            hour = timestamp.hour
            day = timestamp.strftime('%A')
            
            if metric.metric_type == MetricType.ACCURACY:
                hourly_performance[hour].append(metric.value)
            elif metric.metric_type == MetricType.SESSION_LENGTH:
                daily_sessions[day] += 1
        
        # Calculate best study hours
        best_hours = []
        for hour, accuracies in hourly_performance.items():
            if len(accuracies) >= 3:  # Minimum data points
                avg_accuracy = statistics.mean(accuracies)
                best_hours.append((hour, avg_accuracy))
        
        best_hours.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'best_study_hours': [hour for hour, acc in best_hours[:3]],
            'daily_session_distribution': dict(daily_sessions),
            'hourly_performance': {hour: statistics.mean(accs) 
                                 for hour, accs in hourly_performance.items()}
        }
    
    def _generate_insights(self, entries: List, metrics: List[LearningMetric],
                          theme_performance: Dict, trends: List[PerformanceTrend]) -> List[LearningInsight]:
        """Generate personalized learning insights."""
        insights = []
        
        # Analyze strengths
        if theme_performance:
            best_theme = max(theme_performance.items(), key=lambda x: x[1]['average_accuracy'])
            if best_theme[1]['average_accuracy'] > 80:
                insights.append(LearningInsight(
                    insight_id=f"strength_theme_{best_theme[0]}",
                    category="strength",
                    title=f"Excellent performance in {best_theme[0]}",
                    description=f"You're doing great with {best_theme[0]} vocabulary! "
                               f"Average accuracy: {best_theme[1]['average_accuracy']:.1f}%",
                    confidence=0.9,
                    actionable_steps=[
                        f"Continue practicing {best_theme[0]} words regularly",
                        "Consider teaching these words to reinforce learning",
                        "Use your success in this theme as motivation for others"
                    ],
                    supporting_data={'theme_stats': best_theme[1]},
                    priority=3
                ))
        
        # Identify weaknesses
        if theme_performance:
            worst_theme = min(theme_performance.items(), key=lambda x: x[1]['average_accuracy'])
            if worst_theme[1]['average_accuracy'] < 60:
                insights.append(LearningInsight(
                    insight_id=f"weakness_theme_{worst_theme[0]}",
                    category="weakness",
                    title=f"{worst_theme[0]} needs attention",
                    description=f"Your accuracy with {worst_theme[0]} vocabulary is below average. "
                               f"Current accuracy: {worst_theme[1]['average_accuracy']:.1f}%",
                    confidence=0.85,
                    actionable_steps=[
                        f"Dedicate extra study time to {worst_theme[0]} words",
                        "Try different study methods (visual aids, context sentences)",
                        "Break down complex words into smaller components",
                        "Practice these words more frequently"
                    ],
                    supporting_data={'theme_stats': worst_theme[1]},
                    priority=1
                ))
        
        # Consistency insights
        consistency_trend = next((t for t in trends if t.metric == MetricType.STUDY_FREQUENCY), None)
        if consistency_trend:
            if consistency_trend.trend_direction == "declining":
                insights.append(LearningInsight(
                    insight_id="consistency_declining",
                    category="warning",
                    title="Study frequency is declining",
                    description="Your study sessions have become less frequent recently. "
                               "Consistency is key to vocabulary retention.",
                    confidence=0.8,
                    actionable_steps=[
                        "Set a daily study reminder",
                        "Start with shorter, more manageable sessions",
                        "Find a consistent time that works for your schedule",
                        "Track your study streaks for motivation"
                    ],
                    supporting_data={'trend_data': consistency_trend},
                    priority=2
                ))
        
        # Learning velocity insights
        velocity = self._calculate_learning_velocity(metrics, entries)
        if velocity < 0.5:  # Less than 0.5 words per hour
            insights.append(LearningInsight(
                insight_id="low_learning_velocity",
                category="opportunity",
                title="Learning velocity could be improved",
                description=f"You're currently mastering {velocity:.1f} words per hour. "
                           "There's room for improvement in learning efficiency.",
                confidence=0.7,
                actionable_steps=[
                    "Focus on high-priority words first",
                    "Use spaced repetition more effectively",
                    "Reduce session length but increase frequency",
                    "Try active recall techniques"
                ],
                supporting_data={'current_velocity': velocity},
                priority=2
            ))
        
        # Difficulty progression insights
        beginner_entries = [e for e in entries if e.difficulty.value == 1]
        expert_entries = [e for e in entries if e.difficulty.value == 5]
        
        if len(beginner_entries) > len(expert_entries) * 3:
            insights.append(LearningInsight(
                insight_id="difficulty_progression",
                category="opportunity",
                title="Ready to tackle harder words",
                description="You have a good foundation with easier words. "
                           "Consider gradually introducing more challenging vocabulary.",
                confidence=0.75,
                actionable_steps=[
                    "Add some intermediate-level words to your study list",
                    "Challenge yourself with complex themes",
                    "Practice using beginner words in advanced contexts"
                ],
                supporting_data={
                    'beginner_count': len(beginner_entries),
                    'expert_count': len(expert_entries)
                },
                priority=3
            ))
        
        return sorted(insights, key=lambda x: x.priority)
    
    def _generate_study_recommendations(self, entries: List, theme_performance: Dict,
                                      insights: List[LearningInsight]) -> List[Dict[str, Any]]:
        """Generate specific study recommendations."""
        recommendations = []
        
        # Recommend words due for review
        due_words = [e for e in entries if e.is_due_for_review()]
        if due_words:
            recommendations.append({
                'type': 'review_due_words',
                'title': f"Review {len(due_words)} overdue words",
                'description': "These words are scheduled for review to maintain retention",
                'word_count': len(due_words),
                'estimated_time': len(due_words) * 0.5,  # 30 seconds per word
                'priority': 1
            })
        
        # Recommend weak theme focus
        weak_themes = [
            theme for theme, stats in theme_performance.items()
            if stats['average_accuracy'] < 70 and stats['total_words'] >= 5
        ]
        
        if weak_themes:
            theme = weak_themes[0]  # Focus on worst theme
            theme_words = [
                e for e in entries 
                if theme in e.themes and e.frequency_data.calculate_accuracy() < 70
            ]
            
            recommendations.append({
                'type': 'focus_weak_theme',
                'title': f"Focus on {theme} vocabulary",
                'description': f"Improve your {theme} vocabulary accuracy",
                'theme': theme,
                'word_count': len(theme_words),
                'current_accuracy': theme_performance[theme]['average_accuracy'],
                'estimated_time': len(theme_words) * 0.75,
                'priority': 2
            })
        
        # Recommend new words if learning velocity is good
        new_words = [e for e in entries if e.status.value == 'new']
        learning_words = [e for e in entries if e.status.value == 'learning']
        
        if len(learning_words) < 10 and new_words:  # Not overloaded with learning words
            recommendations.append({
                'type': 'introduce_new_words',
                'title': f"Learn {min(5, len(new_words))} new words",
                'description': "Add some fresh vocabulary to your study routine",
                'word_count': min(5, len(new_words)),
                'available_new_words': len(new_words),
                'estimated_time': 10,  # 2 minutes per new word
                'priority': 3
            })
        
        # Time-based recommendations
        now = datetime.now()
        if 9 <= now.hour <= 11:  # Morning
            recommendations.append({
                'type': 'morning_boost',
                'title': "Morning vocabulary boost",
                'description': "Great time for learning new words with a fresh mind",
                'suggested_focus': 'new_words',
                'estimated_time': 15,
                'priority': 2
            })
        
        return sorted(recommendations, key=lambda x: x['priority'])
    
    def _predict_mastery_dates(self, entries: List) -> Dict[str, str]:
        """Predict when words will be mastered."""
        predictions = {}
        
        for entry in entries:
            if entry.status.value == 'mastered':
                continue
            
            # Simple prediction based on current progress
            current_accuracy = entry.frequency_data.calculate_accuracy()
            study_sessions = entry.frequency_data.study_sessions
            
            if study_sessions == 0:
                sessions_needed = 10  # Estimate for new words
            else:
                # Estimate based on current progress
                progress_rate = current_accuracy / study_sessions if study_sessions > 0 else 5
                sessions_needed = max(1, int((95 - current_accuracy) / progress_rate))
            
            # Assume 2 sessions per week
            weeks_needed = sessions_needed / 2
            predicted_date = datetime.now() + timedelta(weeks=weeks_needed)
            
            predictions[entry.id] = predicted_date.strftime('%Y-%m-%d')
        
        return predictions
    
    def _estimate_study_time_needed(self, theme_performance: Dict) -> Dict[str, int]:
        """Estimate study time needed for each theme."""
        estimates = {}
        
        for theme, stats in theme_performance.items():
            accuracy = stats['average_accuracy']
            total_words = stats['total_words']
            
            # Time based on current accuracy and word count
            if accuracy >= 90:
                minutes_per_word = 0.5  # Maintenance mode
            elif accuracy >= 70:
                minutes_per_word = 1.0  # Regular practice
            else:
                minutes_per_word = 2.0  # Intensive study
            
            estimates[theme] = int(total_words * minutes_per_word)
        
        return estimates
    
    def _calculate_percentile_rankings(self, progress_score: float, velocity: float) -> Dict[str, float]:
        """Calculate user's percentile rankings (simulated - would use actual benchmark data)."""
        # Simulated benchmarks - in reality these would come from aggregated user data
        return {
            'overall_progress': min(progress_score / 80.0 * 100, 100),  # Assuming 80 is good
            'learning_velocity': min(velocity / 1.0 * 100, 100),  # Assuming 1.0 word/hour is good
            'consistency': 75,  # Placeholder
            'retention': min(85, 100)  # Placeholder
        }
    
    def _get_benchmark_comparisons(self, metrics: List[LearningMetric]) -> Dict[str, Dict[str, float]]:
        """Get benchmark comparisons (simulated)."""
        return {
            'accuracy': {
                'your_average': 82.5,
                'global_average': 75.0,
                'top_10_percent': 95.0
            },
            'study_frequency': {
                'your_sessions_per_week': 4.2,
                'global_average': 3.1,
                'top_10_percent': 6.5
            },
            'learning_velocity': {
                'your_words_per_hour': 0.8,
                'global_average': 0.6,
                'top_10_percent': 1.2
            }
        }
    
    def _get_cached_analysis(self, cache_key: str) -> Optional[ComprehensiveAnalysis]:
        """Get cached analysis from database."""
        with sqlite3.connect(self.analytics_db_path) as conn:
            row = conn.execute("""
                SELECT analysis_data FROM analysis_cache 
                WHERE cache_key = ? AND expiry_date > datetime('now')
            """, (cache_key,)).fetchone()
            
            if row:
                try:
                    data = json.loads(row[0])
                    return ComprehensiveAnalysis(**data)
                except:
                    pass
        
        return None
    
    def _cache_analysis(self, cache_key: str, analysis: ComprehensiveAnalysis):
        """Cache analysis results."""
        # Set expiry to 24 hours from now
        expiry_date = (datetime.now() + timedelta(hours=24)).isoformat()
        
        with sqlite3.connect(self.analytics_db_path) as conn:
            # Convert analysis to serializable format
            analysis_dict = {
                'user_id': analysis.user_id,
                'analysis_date': analysis.analysis_date,
                'timeframe': analysis.timeframe.value,
                'overall_progress_score': analysis.overall_progress_score,
                'learning_velocity': analysis.learning_velocity,
                'retention_rate': analysis.retention_rate,
                'consistency_score': analysis.consistency_score,
                'theme_performance': analysis.theme_performance,
                'difficulty_progression': analysis.difficulty_progression,
                'temporal_patterns': analysis.temporal_patterns,
                'predicted_mastery_dates': analysis.predicted_mastery_dates,
                'estimated_study_time_needed': analysis.estimated_study_time_needed,
                'percentile_rankings': analysis.percentile_rankings,
                'benchmark_comparisons': analysis.benchmark_comparisons
                # Note: Some complex objects like trends and insights are not cached
            }
            
            conn.execute("""
                INSERT OR REPLACE INTO analysis_cache 
                (cache_key, analysis_data, expiry_date)
                VALUES (?, ?, ?)
            """, (cache_key, json.dumps(analysis_dict), expiry_date))
            conn.commit()
    
    def generate_progress_visualization(self, analysis: ComprehensiveAnalysis, 
                                      output_path: Optional[Path] = None) -> Path:
        """Generate progress visualization charts."""
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Set up the plot
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Vocabulary Learning Progress - {analysis.timeframe.value.title()}', fontsize=16)
        
        # 1. Theme Performance
        if analysis.theme_performance:
            themes = list(analysis.theme_performance.keys())
            accuracies = [stats['average_accuracy'] for stats in analysis.theme_performance.values()]
            
            axes[0, 0].barh(themes, accuracies)
            axes[0, 0].set_title('Theme Performance')
            axes[0, 0].set_xlabel('Average Accuracy (%)')
            axes[0, 0].set_xlim(0, 100)
        
        # 2. Difficulty Progression
        if analysis.difficulty_progression:
            difficulties = list(analysis.difficulty_progression.keys())
            mastery_rates = list(analysis.difficulty_progression.values())
            
            axes[0, 1].bar(difficulties, mastery_rates)
            axes[0, 1].set_title('Difficulty Level Mastery')
            axes[0, 1].set_ylabel('Mastery Rate (%)')
            axes[0, 1].set_ylim(0, 100)
            plt.setp(axes[0, 1].xaxis.get_majorticklabels(), rotation=45)
        
        # 3. Performance Trends
        if analysis.performance_trends:
            # Show accuracy trend as example
            accuracy_trend = next((t for t in analysis.performance_trends 
                                 if t.metric == MetricType.ACCURACY), None)
            if accuracy_trend and accuracy_trend.data_points:
                dates, values = zip(*accuracy_trend.data_points)
                axes[1, 0].plot(dates, values, marker='o')
                axes[1, 0].set_title('Accuracy Trend')
                axes[1, 0].set_ylabel('Accuracy (%)')
                plt.setp(axes[1, 0].xaxis.get_majorticklabels(), rotation=45)
        
        # 4. Overall Progress Gauge
        progress = analysis.overall_progress_score
        
        # Create a gauge-like visualization
        ax = axes[1, 1]
        ax.pie([progress, 100-progress], 
               labels=['Progress', 'Remaining'],
               startangle=90,
               colors=['#4CAF50', '#E0E0E0'],
               counterclock=False)
        ax.set_title(f'Overall Progress\n{progress:.1f}%')
        
        plt.tight_layout()
        
        # Save or show
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            return output_path
        else:
            default_path = Path(f'vocabulary_progress_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
            plt.savefig(default_path, dpi=300, bbox_inches='tight')
            return default_path
    
    def export_analytics_report(self, analysis: ComprehensiveAnalysis, 
                               format_type: str = 'json') -> str:
        """Export comprehensive analytics report."""
        if format_type == 'json':
            # Convert to serializable format
            report = {
                'analysis_metadata': {
                    'user_id': analysis.user_id,
                    'analysis_date': analysis.analysis_date,
                    'timeframe': analysis.timeframe.value
                },
                'key_metrics': {
                    'overall_progress_score': analysis.overall_progress_score,
                    'learning_velocity': analysis.learning_velocity,
                    'retention_rate': analysis.retention_rate,
                    'consistency_score': analysis.consistency_score
                },
                'performance_analysis': {
                    'theme_performance': analysis.theme_performance,
                    'difficulty_progression': analysis.difficulty_progression,
                    'temporal_patterns': analysis.temporal_patterns
                },
                'insights': [
                    {
                        'id': insight.insight_id,
                        'category': insight.category,
                        'title': insight.title,
                        'description': insight.description,
                        'confidence': insight.confidence,
                        'actionable_steps': insight.actionable_steps,
                        'priority': insight.priority
                    }
                    for insight in analysis.insights
                ],
                'recommendations': analysis.next_study_recommendations,
                'predictions': {
                    'mastery_dates': analysis.predicted_mastery_dates,
                    'study_time_estimates': analysis.estimated_study_time_needed
                },
                'benchmarking': {
                    'percentile_rankings': analysis.percentile_rankings,
                    'comparisons': analysis.benchmark_comparisons
                }
            }
            
            return json.dumps(report, indent=2)
        
        elif format_type == 'html':
            # Generate HTML report
            html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Vocabulary Learning Analytics Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        .header { background: #f4f4f4; padding: 20px; border-radius: 5px; }
        .metric-card { background: white; border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .insight { margin: 10px 0; padding: 10px; border-left: 4px solid #007cba; background: #f9f9f9; }
        .strength { border-left-color: #4CAF50; }
        .weakness { border-left-color: #F44336; }
        .opportunity { border-left-color: #FF9800; }
        .warning { border-left-color: #FF5722; }
        .progress-bar { background: #e0e0e0; border-radius: 10px; height: 20px; margin: 5px 0; }
        .progress-fill { background: #4CAF50; height: 100%; border-radius: 10px; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Vocabulary Learning Analytics Report</h1>
        <p>Generated: {analysis_date}</p>
        <p>Timeframe: {timeframe}</p>
        <p>User: {user_id}</p>
    </div>
    
    <h2>Key Metrics</h2>
    <div class="metric-card">
        <h3>Overall Progress: {overall_progress:.1f}%</h3>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {overall_progress:.1f}%"></div>
        </div>
    </div>
    
    <div class="metric-card">
        <h3>Learning Velocity: {learning_velocity:.2f} words/hour</h3>
        <h3>Retention Rate: {retention_rate:.1f}%</h3>
        <h3>Consistency Score: {consistency_score:.1f}%</h3>
    </div>
    
    <h2>Learning Insights</h2>
    {insights_html}
    
    <h2>Theme Performance</h2>
    <table>
        <tr><th>Theme</th><th>Accuracy</th><th>Mastery Rate</th><th>Total Words</th></tr>
        {theme_performance_html}
    </table>
    
    <h2>Study Recommendations</h2>
    <ul>
        {recommendations_html}
    </ul>
    
</body>
</html>
            """
            
            # Generate insights HTML
            insights_html = ""
            for insight in analysis.insights:
                insights_html += f'''
                <div class="insight {insight.category}">
                    <h4>{insight.title}</h4>
                    <p>{insight.description}</p>
                    <ul>
                        {''.join(f'<li>{step}</li>' for step in insight.actionable_steps)}
                    </ul>
                </div>
                '''
            
            # Generate theme performance HTML
            theme_performance_html = ""
            for theme, stats in analysis.theme_performance.items():
                theme_performance_html += f'''
                <tr>
                    <td>{theme}</td>
                    <td>{stats['average_accuracy']:.1f}%</td>
                    <td>{stats['mastery_rate']:.1f}%</td>
                    <td>{stats['total_words']}</td>
                </tr>
                '''
            
            # Generate recommendations HTML
            recommendations_html = ""
            for rec in analysis.next_study_recommendations:
                recommendations_html += f"<li><strong>{rec['title']}</strong>: {rec['description']}</li>"
            
            return html_template.format(
                analysis_date=analysis.analysis_date,
                timeframe=analysis.timeframe.value.title(),
                user_id=analysis.user_id,
                overall_progress=analysis.overall_progress_score,
                learning_velocity=analysis.learning_velocity,
                retention_rate=analysis.retention_rate,
                consistency_score=analysis.consistency_score,
                insights_html=insights_html,
                theme_performance_html=theme_performance_html,
                recommendations_html=recommendations_html
            )
        
        return json.dumps({'error': f'Unsupported format: {format_type}'})
    
    def clear_cache(self):
        """Clear analytics cache."""
        self.metrics_cache.clear()
        self.analysis_cache.clear()
        
        with sqlite3.connect(self.analytics_db_path) as conn:
            conn.execute("DELETE FROM analysis_cache WHERE expiry_date < datetime('now')")
            conn.commit()