"""
Performance Tracker for Spaced Repetition System
Tracks user learning patterns and performance metrics
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics
import json

from .sm2_algorithm import ResponseQuality


@dataclass
class SessionMetrics:
    """Metrics for a single study session"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_reviews: int = 0
    correct_reviews: int = 0
    response_times: List[float] = field(default_factory=list)
    quality_scores: List[int] = field(default_factory=list)
    content_types_reviewed: Dict[str, int] = field(default_factory=dict)
    
    @property
    def duration_minutes(self) -> float:
        """Calculate session duration in minutes"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 60
        return 0.0
    
    @property
    def accuracy_rate(self) -> float:
        """Calculate accuracy rate for session"""
        if self.total_reviews == 0:
            return 0.0
        return self.correct_reviews / self.total_reviews
    
    @property
    def average_response_time(self) -> float:
        """Calculate average response time in seconds"""
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)
    
    @property
    def average_quality_score(self) -> float:
        """Calculate average quality score"""
        if not self.quality_scores:
            return 0.0
        return statistics.mean(self.quality_scores)


@dataclass
class LearningTrends:
    """Learning trend analysis"""
    accuracy_trend: float = 0.0  # Positive = improving, Negative = declining
    speed_trend: float = 0.0     # Positive = getting faster, Negative = slower
    consistency_score: float = 0.0  # 0-1, higher = more consistent
    learning_velocity: float = 1.0  # Multiplier for learning speed
    difficulty_preference: str = "medium"  # easy, medium, hard
    optimal_session_length: int = 20  # minutes
    peak_performance_times: List[int] = field(default_factory=list)  # Hours of day


class PerformanceTracker:
    """Tracks and analyzes user learning performance"""
    
    def __init__(self, window_size: int = 50):
        """
        Initialize performance tracker
        
        Args:
            window_size: Number of recent reviews to consider for trends
        """
        self.window_size = window_size
        self.sessions: Dict[str, SessionMetrics] = {}
        self.current_session: Optional[SessionMetrics] = None
        
        # Rolling windows for trend analysis
        self.recent_accuracies = deque(maxlen=window_size)
        self.recent_response_times = deque(maxlen=window_size)
        self.recent_quality_scores = deque(maxlen=window_size)
        
        # Performance metrics by content type
        self.content_performance: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: {'accuracy': [], 'response_time': [], 'quality': []}
        )
        
        # Long-term statistics
        self.total_reviews = 0
        self.total_correct = 0
        self.total_study_time_minutes = 0.0
        
    def start_session(self, session_id: str = None) -> str:
        """Start a new study session"""
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = SessionMetrics(
            session_id=session_id,
            start_time=datetime.now()
        )
        self.sessions[session_id] = self.current_session
        
        return session_id
    
    def end_session(self) -> Optional[SessionMetrics]:
        """End the current study session"""
        if self.current_session:
            self.current_session.end_time = datetime.now()
            self.total_study_time_minutes += self.current_session.duration_minutes
            
            session = self.current_session
            self.current_session = None
            return session
        return None
    
    def record_review(self, 
                     card_id: str,
                     response_quality: ResponseQuality,
                     response_time_seconds: float,
                     content_type: str = "vocab",
                     card_difficulty: str = "medium") -> None:
        """
        Record a single review event
        
        Args:
            card_id: Identifier for the reviewed card
            response_quality: Quality of the response
            response_time_seconds: Time taken to respond
            content_type: Type of content (vocab, grammar, etc.)
            card_difficulty: Difficulty level of the card
        """
        if not self.current_session:
            self.start_session()
        
        # Update session metrics
        self.current_session.total_reviews += 1
        if response_quality.value >= 3:  # Correct responses
            self.current_session.correct_reviews += 1
            self.total_correct += 1
        
        self.current_session.response_times.append(response_time_seconds)
        self.current_session.quality_scores.append(response_quality.value)
        
        # Update content type tracking
        if content_type not in self.current_session.content_types_reviewed:
            self.current_session.content_types_reviewed[content_type] = 0
        self.current_session.content_types_reviewed[content_type] += 1
        
        # Update rolling windows
        self.recent_accuracies.append(1 if response_quality.value >= 3 else 0)
        self.recent_response_times.append(response_time_seconds)
        self.recent_quality_scores.append(response_quality.value)
        
        # Update content-specific performance
        accuracy = 1 if response_quality.value >= 3 else 0
        self.content_performance[content_type]['accuracy'].append(accuracy)
        self.content_performance[content_type]['response_time'].append(response_time_seconds)
        self.content_performance[content_type]['quality'].append(response_quality.value)
        
        # Keep content performance lists manageable
        for metric_list in self.content_performance[content_type].values():
            if len(metric_list) > self.window_size:
                metric_list.pop(0)
        
        self.total_reviews += 1
    
    def get_current_performance(self) -> Dict:
        """Get current performance metrics"""
        if not self.recent_accuracies:
            return {
                'current_accuracy': 0.0,
                'current_speed': 0.0,
                'current_quality': 0.0,
                'session_reviews': 0
            }
        
        current_accuracy = statistics.mean(self.recent_accuracies)
        current_speed = statistics.mean(self.recent_response_times)
        current_quality = statistics.mean(self.recent_quality_scores)
        
        return {
            'current_accuracy': current_accuracy,
            'current_speed': current_speed,
            'current_quality': current_quality,
            'session_reviews': self.current_session.total_reviews if self.current_session else 0,
            'reviews_in_window': len(self.recent_accuracies)
        }
    
    def calculate_learning_trends(self) -> LearningTrends:
        """Calculate learning trends and patterns"""
        trends = LearningTrends()
        
        if len(self.recent_accuracies) < 10:
            return trends  # Not enough data
        
        # Calculate accuracy trend using linear regression slope
        trends.accuracy_trend = self._calculate_trend(list(self.recent_accuracies))
        trends.speed_trend = -self._calculate_trend(list(self.recent_response_times))  # Negative because faster is better
        
        # Calculate consistency score (inverse of standard deviation)
        if len(self.recent_quality_scores) > 1:
            quality_std = statistics.stdev(self.recent_quality_scores)
            trends.consistency_score = max(0, 1 - quality_std / 5.0)  # Normalized by max quality
        
        # Calculate learning velocity based on recent performance
        recent_accuracy = statistics.mean(list(self.recent_accuracies)[-20:]) if len(self.recent_accuracies) >= 20 else statistics.mean(self.recent_accuracies)
        recent_speed = statistics.mean(list(self.recent_response_times)[-20:]) if len(self.recent_response_times) >= 20 else statistics.mean(self.recent_response_times)
        
        # Learning velocity combines accuracy and speed
        speed_factor = max(0.5, min(2.0, 10 / max(1, recent_speed)))  # Optimal around 10 seconds
        trends.learning_velocity = min(2.0, recent_accuracy * speed_factor)
        
        # Determine difficulty preference based on performance patterns
        trends.difficulty_preference = self._determine_difficulty_preference()
        
        # Calculate optimal session length based on performance decay
        trends.optimal_session_length = self._calculate_optimal_session_length()
        
        # Find peak performance times
        trends.peak_performance_times = self._find_peak_performance_times()
        
        return trends
    
    def get_content_analysis(self) -> Dict[str, Dict]:
        """Analyze performance by content type"""
        analysis = {}
        
        for content_type, metrics in self.content_performance.items():
            if not metrics['accuracy']:
                continue
            
            analysis[content_type] = {
                'accuracy': statistics.mean(metrics['accuracy']),
                'avg_response_time': statistics.mean(metrics['response_time']),
                'avg_quality': statistics.mean(metrics['quality']),
                'total_reviews': len(metrics['accuracy']),
                'improvement_trend': self._calculate_trend(metrics['accuracy']),
                'difficulty_level': self._assess_content_difficulty(metrics),
                'mastery_level': self._calculate_mastery_level(metrics)
            }
        
        return analysis
    
    def get_session_history(self, days: int = 7) -> List[SessionMetrics]:
        """Get session history for the past N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_sessions = [
            session for session in self.sessions.values()
            if session.start_time >= cutoff_date and session.end_time is not None
        ]
        
        return sorted(recent_sessions, key=lambda s: s.start_time, reverse=True)
    
    def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        trends = self.calculate_learning_trends()
        content_analysis = self.get_content_analysis()
        current_performance = self.get_current_performance()
        recent_sessions = self.get_session_history()
        
        # Calculate overall statistics
        overall_accuracy = self.total_correct / max(1, self.total_reviews)
        avg_session_length = statistics.mean([s.duration_minutes for s in recent_sessions]) if recent_sessions else 0
        
        return {
            'overall_stats': {
                'total_reviews': self.total_reviews,
                'total_correct': self.total_correct,
                'overall_accuracy': overall_accuracy,
                'total_study_time_hours': self.total_study_time_minutes / 60,
                'average_session_length_minutes': avg_session_length
            },
            'current_performance': current_performance,
            'learning_trends': {
                'accuracy_trend': trends.accuracy_trend,
                'speed_trend': trends.speed_trend,
                'consistency_score': trends.consistency_score,
                'learning_velocity': trends.learning_velocity,
                'difficulty_preference': trends.difficulty_preference,
                'optimal_session_length': trends.optimal_session_length
            },
            'content_analysis': content_analysis,
            'recent_sessions': len(recent_sessions),
            'recommendations': self._generate_recommendations(trends, content_analysis)
        }
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend using simple linear regression slope"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x_values = list(range(n))
        
        # Calculate slope
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)
        
        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _determine_difficulty_preference(self) -> str:
        """Determine user's preferred difficulty level"""
        if not self.recent_quality_scores:
            return "medium"
        
        avg_quality = statistics.mean(self.recent_quality_scores)
        
        if avg_quality >= 4.5:
            return "hard"  # User is finding content too easy
        elif avg_quality <= 2.5:
            return "easy"  # User is struggling
        else:
            return "medium"
    
    def _calculate_optimal_session_length(self) -> int:
        """Calculate optimal session length based on performance decay"""
        if not self.sessions:
            return 20  # Default
        
        # Analyze performance within sessions
        performance_by_duration = []
        for session in self.sessions.values():
            if session.end_time and session.duration_minutes > 5:
                performance_by_duration.append((session.duration_minutes, session.accuracy_rate))
        
        if len(performance_by_duration) < 3:
            return 20  # Default
        
        # Find duration with best performance
        sorted_by_performance = sorted(performance_by_duration, key=lambda x: x[1], reverse=True)
        optimal_durations = [duration for duration, _ in sorted_by_performance[:3]]
        
        return int(statistics.mean(optimal_durations))
    
    def _find_peak_performance_times(self) -> List[int]:
        """Find hours of day with peak performance"""
        hourly_performance = defaultdict(list)
        
        for session in self.sessions.values():
            if session.end_time:
                hour = session.start_time.hour
                hourly_performance[hour].append(session.accuracy_rate)
        
        if not hourly_performance:
            return []
        
        # Calculate average performance by hour
        avg_performance_by_hour = {
            hour: statistics.mean(performances) 
            for hour, performances in hourly_performance.items()
            if len(performances) >= 2
        }
        
        if not avg_performance_by_hour:
            return []
        
        # Find top performing hours
        sorted_hours = sorted(avg_performance_by_hour.items(), key=lambda x: x[1], reverse=True)
        return [hour for hour, _ in sorted_hours[:3]]
    
    def _assess_content_difficulty(self, metrics: Dict[str, List[float]]) -> str:
        """Assess difficulty level of content type"""
        if not metrics['accuracy']:
            return "unknown"
        
        avg_accuracy = statistics.mean(metrics['accuracy'])
        avg_response_time = statistics.mean(metrics['response_time'])
        
        # Combine accuracy and response time to assess difficulty
        if avg_accuracy >= 0.8 and avg_response_time <= 15:
            return "easy"
        elif avg_accuracy <= 0.6 or avg_response_time >= 30:
            return "hard"
        else:
            return "medium"
    
    def _calculate_mastery_level(self, metrics: Dict[str, List[float]]) -> float:
        """Calculate mastery level (0-1) for content type"""
        if not metrics['accuracy']:
            return 0.0
        
        # Consider recent performance more heavily
        recent_accuracy = statistics.mean(metrics['accuracy'][-10:]) if len(metrics['accuracy']) >= 10 else statistics.mean(metrics['accuracy'])
        recent_quality = statistics.mean(metrics['quality'][-10:]) if len(metrics['quality']) >= 10 else statistics.mean(metrics['quality'])
        
        # Normalize quality score (0-5 -> 0-1)
        normalized_quality = recent_quality / 5.0
        
        # Combine accuracy and quality for mastery score
        mastery = (recent_accuracy * 0.7) + (normalized_quality * 0.3)
        return min(1.0, mastery)
    
    def _generate_recommendations(self, trends: LearningTrends, content_analysis: Dict) -> List[str]:
        """Generate personalized learning recommendations"""
        recommendations = []
        
        # Accuracy recommendations
        if trends.accuracy_trend < -0.01:
            recommendations.append("Consider taking a break - your accuracy is declining. Review fundamentals.")
        elif trends.accuracy_trend > 0.01:
            recommendations.append("Great progress! Consider increasing difficulty or introducing new content.")
        
        # Speed recommendations
        if trends.speed_trend < -0.1:
            recommendations.append("You're getting faster! This shows improving familiarity with the material.")
        elif trends.speed_trend > 0.1:
            recommendations.append("Take your time - accuracy is more important than speed.")
        
        # Session length recommendations
        if trends.optimal_session_length < 15:
            recommendations.append("Consider shorter, more frequent study sessions for better retention.")
        elif trends.optimal_session_length > 30:
            recommendations.append("You maintain focus well in longer sessions. Consider deeper content exploration.")
        
        # Content-specific recommendations
        weak_areas = [
            content_type for content_type, analysis in content_analysis.items()
            if analysis['mastery_level'] < 0.6
        ]
        
        if weak_areas:
            recommendations.append(f"Focus on improving: {', '.join(weak_areas)}")
        
        strong_areas = [
            content_type for content_type, analysis in content_analysis.items()
            if analysis['mastery_level'] > 0.8
        ]
        
        if strong_areas:
            recommendations.append(f"Consider advanced content in: {', '.join(strong_areas)}")
        
        return recommendations
    
    def export_performance_data(self) -> str:
        """Export performance data as JSON"""
        export_data = {
            'total_reviews': self.total_reviews,
            'total_correct': self.total_correct,
            'total_study_time_minutes': self.total_study_time_minutes,
            'sessions': {},
            'content_performance': dict(self.content_performance),
            'recent_data': {
                'accuracies': list(self.recent_accuracies),
                'response_times': list(self.recent_response_times),
                'quality_scores': list(self.recent_quality_scores)
            }
        }
        
        # Export session data
        for session_id, session in self.sessions.items():
            export_data['sessions'][session_id] = {
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'total_reviews': session.total_reviews,
                'correct_reviews': session.correct_reviews,
                'response_times': session.response_times,
                'quality_scores': session.quality_scores,
                'content_types_reviewed': session.content_types_reviewed
            }
        
        return json.dumps(export_data, indent=2)