"""
Tests for Spaced Repetition System
Tests SM2 algorithm, review scheduling, and performance tracking
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.spaced_repetition.sm2_algorithm import SM2Algorithm, CardMetrics, ResponseQuality
from ai.spaced_repetition.review_scheduler import ReviewScheduler, ReviewType
from ai.spaced_repetition.performance_tracker import PerformanceTracker


class TestSM2Algorithm:
    """Test the SM2 algorithm implementation"""
    
    def setup_method(self):
        """Setup test environment"""
        self.sm2 = SM2Algorithm()
        self.initial_metrics = CardMetrics()
    
    def test_algorithm_initialization(self):
        """Test SM2 algorithm initialization"""
        assert self.sm2.min_easiness == 1.3
        assert self.sm2.max_easiness == 4.0
        assert self.sm2.initial_interval == 1
    
    def test_perfect_response_progression(self):
        """Test progression with perfect responses"""
        card_metrics = CardMetrics()
        
        # First review - perfect
        updated_metrics, next_review = self.sm2.calculate_next_review(
            "test_card", ResponseQuality.PERFECT, card_metrics
        )
        
        assert updated_metrics.repetitions == 1
        assert updated_metrics.interval == 1
        assert updated_metrics.consecutive_correct == 1
        assert updated_metrics.easiness_factor > 2.5
        
        # Second review - perfect
        updated_metrics, next_review = self.sm2.calculate_next_review(
            "test_card", ResponseQuality.PERFECT, updated_metrics
        )
        
        assert updated_metrics.repetitions == 2
        assert updated_metrics.interval >= 4
        assert updated_metrics.consecutive_correct == 2
    
    def test_incorrect_response_reset(self):
        """Test that incorrect responses reset the repetition counter"""
        card_metrics = CardMetrics(repetitions=3, consecutive_correct=3, interval=10)
        
        updated_metrics, next_review = self.sm2.calculate_next_review(
            "test_card", ResponseQuality.INCORRECT, card_metrics
        )
        
        assert updated_metrics.repetitions == 0
        assert updated_metrics.consecutive_correct == 0
        assert updated_metrics.interval == 1
    
    def test_easiness_factor_bounds(self):
        """Test that easiness factor stays within bounds"""
        card_metrics = CardMetrics(easiness_factor=1.3)
        
        # Try to decrease below minimum
        updated_metrics, _ = self.sm2.calculate_next_review(
            "test_card", ResponseQuality.BLACKOUT, card_metrics
        )
        
        assert updated_metrics.easiness_factor >= self.sm2.min_easiness
        
        # Test maximum bound
        card_metrics = CardMetrics(easiness_factor=3.8)
        updated_metrics, _ = self.sm2.calculate_next_review(
            "test_card", ResponseQuality.PERFECT, card_metrics
        )
        
        assert updated_metrics.easiness_factor <= self.sm2.max_easiness
    
    def test_review_priority_calculation(self):
        """Test review priority calculation"""
        now = datetime.now()
        
        # Overdue card should have high priority
        overdue_metrics = CardMetrics(
            next_review=now - timedelta(days=2),
            difficulty_penalty=0.7
        )
        overdue_priority = self.sm2.get_review_priority(overdue_metrics, now)
        
        # Not due card should have lower priority
        future_metrics = CardMetrics(
            next_review=now + timedelta(days=1),
            difficulty_penalty=1.0
        )
        future_priority = self.sm2.get_review_priority(future_metrics, now)
        
        assert overdue_priority > future_priority
    
    def test_graduation_criteria(self):
        """Test card graduation criteria"""
        graduated_metrics = CardMetrics(
            consecutive_correct=3,
            repetitions=3,
            total_reviews=5,
            total_correct=4
        )
        
        not_graduated_metrics = CardMetrics(
            consecutive_correct=1,
            repetitions=1,
            total_reviews=3,
            total_correct=1
        )
        
        assert self.sm2.should_graduate(graduated_metrics)
        assert not self.sm2.should_graduate(not_graduated_metrics)
    
    def test_retention_prediction(self):
        """Test retention probability prediction"""
        good_metrics = CardMetrics(
            current_level=0.8,
            total_reviews=10,
            total_correct=9,
            last_review=datetime.now() - timedelta(days=1)
        )
        
        poor_metrics = CardMetrics(
            current_level=0.3,
            total_reviews=10,
            total_correct=3,
            last_review=datetime.now() - timedelta(days=7)
        )
        
        good_retention = self.sm2.get_retention_prediction(good_metrics, 3)
        poor_retention = self.sm2.get_retention_prediction(poor_metrics, 3)
        
        assert good_retention > poor_retention
        assert 0 <= good_retention <= 1
        assert 0 <= poor_retention <= 1


class TestReviewScheduler:
    """Test the review scheduler"""
    
    def setup_method(self):
        """Setup test environment"""
        self.scheduler = ReviewScheduler(max_daily_reviews=20)
    
    def test_scheduler_initialization(self):
        """Test scheduler initialization"""
        assert self.scheduler.max_daily_reviews == 20
        assert self.scheduler.daily_reviews_completed == 0
        assert len(self.scheduler.review_queue) == 0
    
    def test_add_new_card(self):
        """Test adding new cards to the review system"""
        self.scheduler.add_new_card("card_1", "vocabulary")
        self.scheduler.add_new_card("card_2", "grammar")
        
        assert len(self.scheduler.review_queue) == 2
        
        # Get next reviews
        next_reviews = self.scheduler.get_next_reviews(limit=5)
        assert len(next_reviews) == 2
        assert all(item.review_type == ReviewType.NEW for item in next_reviews)
    
    def test_review_processing(self):
        """Test processing review responses"""
        self.scheduler.add_new_card("card_1", "vocabulary")
        
        # Process a correct response
        result = self.scheduler.process_review_response(
            "card_1", ResponseQuality.EASY, review_duration_seconds=10
        )
        
        assert "card_1" in result["card_id"]
        assert result["interval_days"] > 0
        assert "next_review" in result
        assert self.scheduler.daily_reviews_completed == 1
    
    def test_daily_review_stats(self):
        """Test daily review statistics"""
        self.scheduler.add_new_card("card_1", "vocabulary")
        self.scheduler.add_new_card("card_2", "grammar")
        
        stats = self.scheduler.get_daily_review_stats()
        
        assert stats["total_due"] >= 2
        assert stats["new_cards"] >= 2
        assert stats["completed_today"] == 0
        assert stats["remaining_capacity"] == 20
    
    def test_upcoming_schedule(self):
        """Test upcoming review schedule"""
        self.scheduler.add_new_card("card_1", "vocabulary")
        self.scheduler.process_review_response("card_1", ResponseQuality.EASY)
        
        schedule = self.scheduler.get_upcoming_schedule(days_ahead=7)
        
        assert isinstance(schedule, dict)
        assert len(schedule) == 7
        assert all(isinstance(count, int) for count in schedule.values())
    
    def test_daily_limit_adjustment(self):
        """Test daily limit adjustment"""
        self.scheduler.adjust_daily_limit(50)
        assert self.scheduler.max_daily_reviews == 50
        
        # Test minimum limit
        self.scheduler.adjust_daily_limit(-10)
        assert self.scheduler.max_daily_reviews == 1
    
    def test_queue_state_export(self):
        """Test queue state export"""
        self.scheduler.add_new_card("card_1", "vocabulary")
        export_data = self.scheduler.export_queue_state()
        
        import json
        parsed_data = json.loads(export_data)
        
        assert "queue" in parsed_data
        assert "daily_reviews_completed" in parsed_data
        assert "user_performance_factor" in parsed_data


class TestPerformanceTracker:
    """Test the performance tracker"""
    
    def setup_method(self):
        """Setup test environment"""
        self.tracker = PerformanceTracker()
    
    def test_tracker_initialization(self):
        """Test performance tracker initialization"""
        assert self.tracker.window_size == 50
        assert len(self.tracker.sessions) == 0
        assert self.tracker.current_session is None
        assert self.tracker.total_reviews == 0
    
    def test_session_management(self):
        """Test session start and end"""
        session_id = self.tracker.start_session()
        assert self.tracker.current_session is not None
        assert session_id in self.tracker.sessions
        
        ended_session = self.tracker.end_session()
        assert ended_session is not None
        assert ended_session.end_time is not None
        assert self.tracker.current_session is None
    
    def test_review_recording(self):
        """Test recording reviews"""
        self.tracker.start_session()
        
        # Record several reviews
        for i in range(5):
            self.tracker.record_review(
                f"card_{i}",
                ResponseQuality.EASY,
                response_time_seconds=8.0,
                content_type="vocabulary"
            )
        
        assert self.tracker.total_reviews == 5
        assert self.tracker.current_session.total_reviews == 5
        assert len(self.tracker.recent_accuracies) == 5
    
    def test_performance_calculation(self):
        """Test current performance calculation"""
        self.tracker.start_session()
        
        # Record mixed performance
        performances = [ResponseQuality.PERFECT, ResponseQuality.EASY, ResponseQuality.INCORRECT]
        for i, quality in enumerate(performances):
            self.tracker.record_review(f"card_{i}", quality, 10.0)
        
        current_performance = self.tracker.get_current_performance()
        
        assert "current_accuracy" in current_performance
        assert "current_speed" in current_performance
        assert "current_quality" in current_performance
        assert 0 <= current_performance["current_accuracy"] <= 1
    
    def test_learning_trends_calculation(self):
        """Test learning trends calculation"""
        self.tracker.start_session()
        
        # Simulate improving performance
        for i in range(20):
            quality = ResponseQuality.PERFECT if i > 10 else ResponseQuality.EASY
            self.tracker.record_review(f"card_{i}", quality, 10.0 - i * 0.2)
        
        trends = self.tracker.calculate_learning_trends()
        
        assert hasattr(trends, 'accuracy_trend')
        assert hasattr(trends, 'speed_trend')
        assert hasattr(trends, 'consistency_score')
        assert hasattr(trends, 'learning_velocity')
        assert 0 <= trends.consistency_score <= 1
    
    def test_content_analysis(self):
        """Test content type performance analysis"""
        self.tracker.start_session()
        
        # Record different content types
        content_types = ["vocabulary", "grammar", "vocabulary", "grammar", "conversation"]
        for i, content_type in enumerate(content_types):
            quality = ResponseQuality.EASY if i % 2 == 0 else ResponseQuality.PERFECT
            self.tracker.record_review(f"card_{i}", quality, 10.0, content_type)
        
        analysis = self.tracker.get_content_analysis()
        
        assert "vocabulary" in analysis
        assert "grammar" in analysis
        
        vocab_analysis = analysis["vocabulary"]
        assert "accuracy" in vocab_analysis
        assert "avg_response_time" in vocab_analysis
        assert "mastery_level" in vocab_analysis
    
    def test_performance_report_generation(self):
        """Test comprehensive performance report"""
        self.tracker.start_session()
        
        # Create some performance data
        for i in range(10):
            self.tracker.record_review(
                f"card_{i}",
                ResponseQuality.EASY,
                10.0,
                "vocabulary" if i % 2 == 0 else "grammar"
            )
        
        self.tracker.end_session()
        
        report = self.tracker.generate_performance_report()
        
        assert "overall_stats" in report
        assert "current_performance" in report
        assert "learning_trends" in report
        assert "content_analysis" in report
        assert "recommendations" in report
        
        # Verify overall stats
        overall = report["overall_stats"]
        assert overall["total_reviews"] == 10
        assert overall["total_correct"] == 10  # All EASY responses
        assert overall["overall_accuracy"] == 1.0
    
    def test_session_history(self):
        """Test session history retrieval"""
        # Create multiple sessions
        for day in range(3):
            session_id = self.tracker.start_session()
            # Simulate some reviews
            for i in range(5):
                self.tracker.record_review(f"card_{day}_{i}", ResponseQuality.EASY, 10.0)
            self.tracker.end_session()
        
        history = self.tracker.get_session_history(days=7)
        assert len(history) == 3
        
        # Test with shorter timeframe
        history_short = self.tracker.get_session_history(days=1)
        assert len(history_short) <= 3  # Should be same or fewer
    
    def test_performance_data_export(self):
        """Test performance data export"""
        self.tracker.start_session()
        self.tracker.record_review("card_1", ResponseQuality.EASY, 10.0)
        self.tracker.end_session()
        
        export_data = self.tracker.export_performance_data()
        
        import json
        parsed_data = json.loads(export_data)
        
        assert "total_reviews" in parsed_data
        assert "sessions" in parsed_data
        assert "content_performance" in parsed_data
        assert "recent_data" in parsed_data


class TestIntegration:
    """Integration tests for spaced repetition system"""
    
    def setup_method(self):
        """Setup integrated system"""
        self.sm2 = SM2Algorithm()
        self.scheduler = ReviewScheduler(sm2_algorithm=self.sm2)
        self.tracker = PerformanceTracker()
    
    def test_full_review_cycle(self):
        """Test complete review cycle"""
        # Start tracking session
        self.tracker.start_session()
        
        # Add new cards
        self.scheduler.add_new_card("vocab_1", "vocabulary")
        self.scheduler.add_new_card("grammar_1", "grammar")
        
        # Get next reviews
        next_reviews = self.scheduler.get_next_reviews(limit=2)
        assert len(next_reviews) == 2
        
        # Process reviews and track performance
        for review_item in next_reviews:
            # Simulate review process
            response_quality = ResponseQuality.EASY
            response_time = 12.0
            
            # Process in scheduler
            result = self.scheduler.process_review_response(
                review_item.card_id, response_quality, int(response_time)
            )
            
            # Track in performance tracker
            self.tracker.record_review(
                review_item.card_id, response_quality, response_time, 
                review_item.content_type
            )
            
            assert "next_review" in result
            assert result["interval_days"] > 0
        
        # End session and get report
        self.tracker.end_session()
        report = self.tracker.generate_performance_report()
        
        assert report["overall_stats"]["total_reviews"] == 2
        assert len(report["content_analysis"]) == 2  # vocab and grammar
    
    def test_adaptive_difficulty_integration(self):
        """Test integration with adaptive difficulty"""
        self.tracker.start_session()
        
        # Simulate declining performance
        for i in range(10):
            quality = ResponseQuality.INCORRECT if i > 5 else ResponseQuality.EASY
            self.tracker.record_review(f"card_{i}", quality, 15.0)
        
        trends = self.tracker.calculate_learning_trends()
        
        # Learning velocity should be affected by poor performance
        assert trends.learning_velocity < 1.0
        
        # Generate recommendations
        report = self.tracker.generate_performance_report()
        recommendations = report["recommendations"]
        
        assert len(recommendations) > 0
        assert any("break" in rec.lower() or "review" in rec.lower() for rec in recommendations)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])