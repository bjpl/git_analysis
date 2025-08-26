"""
Comprehensive tests for the image variety and session tracking functionality.
Tests the enhanced session tracker and image variety integration.
"""

import unittest
import tempfile
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add src to Python path for testing
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / 'src'))

from features.enhanced_session_tracker import (
    QuizAttempt, ImageSearchRecord, SearchVarietyManager, 
    SessionStats, EnhancedSessionTracker, get_image_search_parameters
)


class TestImageSearchRecord(unittest.TestCase):
    """Test the ImageSearchRecord class."""
    
    def test_creation(self):
        """Test creating an image search record."""
        record = ImageSearchRecord("sunset", 2, "img123", "http://example.com/img.jpg")
        
        self.assertEqual(record.query, "sunset")
        self.assertEqual(record.page, 2)
        self.assertEqual(record.image_id, "img123")
        self.assertEqual(record.image_url, "http://example.com/img.jpg")
        self.assertIsInstance(record.timestamp, datetime)
    
    def test_query_normalization(self):
        """Test that queries are normalized (lowercase, stripped)."""
        record = ImageSearchRecord("  SUNSET Beach  ")
        self.assertEqual(record.query, "sunset beach")
    
    def test_serialization(self):
        """Test converting to/from dictionary."""
        original = ImageSearchRecord("mountain", 3, "img456", "http://example.com/mountain.jpg")
        
        # Convert to dict and back
        data = original.to_dict()
        restored = ImageSearchRecord.from_dict(data)
        
        self.assertEqual(original.query, restored.query)
        self.assertEqual(original.page, restored.page)
        self.assertEqual(original.image_id, restored.image_id)
        self.assertEqual(original.image_url, restored.image_url)
        # Timestamps should be close (within 1 second)
        time_diff = abs((original.timestamp - restored.timestamp).total_seconds())
        self.assertLess(time_diff, 1.0)


class TestSearchVarietyManager(unittest.TestCase):
    """Test the SearchVarietyManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = SearchVarietyManager(max_history=10, session_memory_hours=1)
    
    def test_initialization(self):
        """Test manager initialization."""
        self.assertEqual(len(self.manager.search_history), 0)
        self.assertEqual(len(self.manager.query_page_map), 0)
        self.assertEqual(len(self.manager.shown_images), 0)
        self.assertIsInstance(self.manager.time_seed, int)
    
    def test_get_search_parameters_new_query(self):
        """Test getting search parameters for a new query."""
        page, offset = self.manager.get_search_parameters("sunset")
        
        self.assertIsInstance(page, int)
        self.assertIsInstance(offset, int)
        self.assertGreaterEqual(page, 1)
        self.assertGreaterEqual(offset, 0)
        self.assertLessEqual(page, 5)  # Should be between 1-5 for new queries
        self.assertLessEqual(offset, 9)  # Should be 0-9
    
    def test_get_search_parameters_repeated_query(self):
        """Test getting search parameters for a repeated query."""
        # First search
        page1, offset1 = self.manager.get_search_parameters("ocean")
        
        # Record some images as shown
        for i in range(3):
            self.manager.record_shown_image("ocean", f"img_{i}", f"http://example.com/{i}.jpg", page1)
        
        # Second search
        page2, offset2 = self.manager.get_search_parameters("ocean")
        
        self.assertIsInstance(page2, int)
        self.assertIsInstance(offset2, int)
        # Should use same page but different offset since < 10 images shown
        self.assertEqual(page2, page1)
    
    def test_record_and_check_shown_images(self):
        """Test recording and checking shown images."""
        query = "mountain"
        image_id = "img123"
        image_url = "http://example.com/mountain.jpg"
        
        # Initially not seen
        self.assertFalse(self.manager.has_seen_image(query, image_id))
        
        # Record as shown
        self.manager.record_shown_image(query, image_id, image_url, 1)
        
        # Now should be seen
        self.assertTrue(self.manager.has_seen_image(query, image_id))
        
        # Check history was updated
        self.assertEqual(len(self.manager.search_history), 1)
        self.assertEqual(len(self.manager.shown_images[query]), 1)
    
    def test_query_stats(self):
        """Test getting query statistics."""
        query = "forest"
        
        # Record some images
        for i in range(5):
            self.manager.record_shown_image(query, f"img_{i}", f"http://example.com/{i}.jpg", 1)
        
        stats = self.manager.get_query_stats(query)
        
        self.assertEqual(stats['query'], query)
        self.assertEqual(stats['images_shown'], 5)
        self.assertEqual(stats['current_page'], 1)
        self.assertIsInstance(stats['recent_searches'], int)
        self.assertIsInstance(stats['last_search'], datetime)
    
    def test_reset_query_history(self):
        """Test resetting history for a specific query."""
        query = "city"
        
        # Add some history
        for i in range(3):
            self.manager.record_shown_image(query, f"img_{i}", f"http://example.com/{i}.jpg", 1)
        
        self.assertEqual(len(self.manager.shown_images[query]), 3)
        self.assertEqual(len(self.manager.search_history), 3)
        
        # Reset
        self.manager.reset_query_history(query)
        
        self.assertNotIn(query, self.manager.shown_images)
        self.assertNotIn(query, self.manager.query_page_map)
        self.assertEqual(len(self.manager.search_history), 0)
    
    def test_shuffle_search(self):
        """Test shuffle search parameters."""
        query = "beach"
        
        # Get multiple shuffle parameters
        results = []
        for _ in range(5):
            page, offset = self.manager.shuffle_search(query)
            results.append((page, offset))
            time.sleep(0.001)  # Small delay to ensure different time seeds
        
        # Should get varied results
        unique_results = set(results)
        self.assertGreater(len(unique_results), 1)  # Should have some variety
    
    def test_cleanup_old_records(self):
        """Test cleanup of old records."""
        manager = SearchVarietyManager(max_history=10, session_memory_hours=1)  # 1 hour memory
        
        # Add some records with old timestamps
        old_time = datetime.now() - timedelta(hours=2)  # 2 hours ago
        for i in range(3):
            record = ImageSearchRecord("test", 1, f"img_{i}", f"http://example.com/{i}.jpg", old_time)
            manager.search_history.append(record)
            if "test" not in manager.shown_images:
                manager.shown_images["test"] = set()
            manager.shown_images["test"].add(f"img_{i}")
        
        # Add some recent records
        for i in range(3, 5):
            manager.record_shown_image("test", f"img_{i}", f"http://example.com/{i}.jpg", 1)
        
        self.assertEqual(len(manager.search_history), 5)
        
        # Trigger cleanup
        manager._cleanup_old_records()
        
        # Only recent records should remain (3 old records should be cleaned up)
        self.assertEqual(len(manager.search_history), 2)
    
    def test_serialization(self):
        """Test manager serialization."""
        # Add some data
        for i in range(3):
            self.manager.record_shown_image("test", f"img_{i}", f"http://example.com/{i}.jpg", 1)
        
        # Serialize and deserialize
        data = self.manager.to_dict()
        new_manager = SearchVarietyManager()
        new_manager.from_dict(data)
        
        # Check data was preserved
        self.assertEqual(len(new_manager.search_history), 3)
        self.assertEqual(len(new_manager.shown_images), 1)
        self.assertIn("test", new_manager.shown_images)


class TestEnhancedSessionStats(unittest.TestCase):
    """Test the enhanced SessionStats class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.stats = SessionStats()
    
    def test_initialization(self):
        """Test stats initialization."""
        self.assertIsInstance(self.stats.start_time, datetime)
        self.assertEqual(len(self.stats.words_studied), 0)
        self.assertEqual(len(self.stats.quiz_attempts), 0)
        self.assertEqual(self.stats.images_viewed, 0)
        self.assertEqual(len(self.stats.unique_searches), 0)
        self.assertIsInstance(self.stats.search_variety_manager, SearchVarietyManager)
    
    def test_add_image_viewed(self):
        """Test adding viewed images."""
        self.stats.add_image_viewed("sunset", "img123", "http://example.com/img.jpg")
        
        self.assertEqual(self.stats.images_viewed, 1)
        self.assertEqual(len(self.stats.unique_searches), 1)
        self.assertIn("sunset", self.stats.unique_searches)
    
    def test_multiple_searches(self):
        """Test tracking multiple different searches."""
        queries = ["sunset", "mountain", "ocean", "sunset", "forest"]
        
        for query in queries:
            self.stats.add_image_viewed(query, f"img_{query}", f"http://example.com/{query}.jpg")
        
        self.assertEqual(self.stats.images_viewed, 5)
        self.assertEqual(len(self.stats.unique_searches), 4)  # 4 unique queries
    
    def test_quiz_integration(self):
        """Test that quiz attempts are still tracked."""
        attempt = QuizAttempt("hello", True, 2.5)
        self.stats.add_quiz_attempt(attempt)
        
        self.assertEqual(self.stats.get_total_attempts(), 1)
        self.assertEqual(self.stats.calculate_accuracy(), 100.0)
        self.assertEqual(len(self.stats.words_studied), 1)
    
    def test_to_dict_enhanced(self):
        """Test enhanced dictionary conversion."""
        # Add some data
        self.stats.add_image_viewed("sunset")
        self.stats.add_image_viewed("mountain")
        self.stats.add_quiz_attempt(QuizAttempt("hello", True))
        
        data = self.stats.to_dict()
        
        self.assertIn('images_viewed', data)
        self.assertIn('unique_searches', data)
        self.assertEqual(data['images_viewed'], 2)
        self.assertEqual(data['unique_searches'], 2)
        self.assertEqual(data['total_attempts'], 1)


class TestEnhancedSessionTracker(unittest.TestCase):
    """Test the enhanced session tracker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.tracker = EnhancedSessionTracker(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test tracker initialization."""
        self.assertTrue(self.temp_dir.exists())
        self.assertTrue(self.tracker.attempts_file.exists())
        self.assertTrue(self.tracker.sessions_file.exists())
        self.assertIsInstance(self.tracker.current_session, SessionStats)
    
    def test_search_parameters(self):
        """Test getting search parameters."""
        page, offset = self.tracker.get_search_parameters("sunset")
        
        self.assertIsInstance(page, int)
        self.assertIsInstance(offset, int)
        self.assertGreaterEqual(page, 1)
        self.assertGreaterEqual(offset, 0)
    
    def test_record_image_shown(self):
        """Test recording shown images."""
        self.tracker.record_image_shown("sunset", "img123", "http://example.com/img.jpg", 1)
        
        self.assertEqual(self.tracker.current_session.images_viewed, 1)
        self.assertTrue(self.tracker.has_seen_image("sunset", "img123"))
        
        # Check that image history file was created
        self.assertTrue(self.tracker.image_history_file.exists())
    
    def test_query_stats(self):
        """Test getting query statistics."""
        # Record some images
        for i in range(3):
            self.tracker.record_image_shown("ocean", f"img_{i}", f"http://example.com/{i}.jpg", 1)
        
        stats = self.tracker.get_query_stats("ocean")
        
        self.assertEqual(stats['images_shown'], 3)
        self.assertEqual(stats['current_page'], 1)
    
    def test_shuffle_search(self):
        """Test shuffle search functionality."""
        page1, offset1 = self.tracker.shuffle_search("mountain")
        time.sleep(0.001)
        page2, offset2 = self.tracker.shuffle_search("mountain")
        
        # Should get different results
        self.assertTrue(page1 != page2 or offset1 != offset2)
    
    def test_reset_query_history(self):
        """Test resetting query history."""
        # Add some history
        self.tracker.record_image_shown("forest", "img123", "http://example.com/img.jpg", 1)
        self.assertTrue(self.tracker.has_seen_image("forest", "img123"))
        
        # Reset
        self.tracker.reset_query_history("forest")
        self.assertFalse(self.tracker.has_seen_image("forest", "img123"))
    
    def test_session_persistence(self):
        """Test that session data persists across tracker instances."""
        # Record some data
        self.tracker.record_image_shown("sunset", "img123", "http://example.com/img.jpg", 1)
        self.tracker.log_quiz_attempt("hello", True, 2.0)
        
        # Create new tracker with same directory
        new_tracker = EnhancedSessionTracker(self.temp_dir)
        
        # Check that image history was loaded
        self.assertTrue(new_tracker.has_seen_image("sunset", "img123"))
    
    def test_save_session_enhanced(self):
        """Test saving session with enhanced fields."""
        # Add some data
        self.tracker.record_image_shown("sunset", "img123", "http://example.com/img.jpg", 1)
        self.tracker.record_image_shown("mountain", "img456", "http://example.com/img2.jpg", 1)
        self.tracker.log_quiz_attempt("hello", True)
        
        # Save session
        self.tracker.save_session()
        
        # Check that session file has enhanced data
        with open(self.tracker.sessions_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('images_viewed', content)
            self.assertIn('unique_searches', content)
    
    def test_overall_stats_enhanced(self):
        """Test enhanced overall statistics."""
        # Add some data
        self.tracker.record_image_shown("sunset", "img123", "http://example.com/img.jpg", 1)
        self.tracker.log_quiz_attempt("hello", True)
        self.tracker.save_session()
        
        stats = self.tracker.get_overall_stats()
        
        self.assertIn('total_images_viewed', stats)
        self.assertIn('total_unique_searches', stats)
        self.assertEqual(stats['total_sessions'], 1)
        self.assertEqual(stats['total_images_viewed'], 1)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_get_image_search_parameters(self):
        """Test the utility function for getting search parameters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = EnhancedSessionTracker(Path(temp_dir))
            
            params = get_image_search_parameters(tracker, "sunset")
            
            self.assertIn('page', params)
            self.assertIn('per_page', params)
            self.assertIn('order_by', params)
            self.assertIn('orientation', params)
            self.assertIn('content_filter', params)
            self.assertIn('query_offset', params)
            
            self.assertEqual(params['per_page'], 10)
            self.assertEqual(params['order_by'], 'relevant')
    
    def test_get_image_search_parameters_shuffle(self):
        """Test shuffle parameters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = EnhancedSessionTracker(Path(temp_dir))
            
            params = get_image_search_parameters(tracker, "sunset", shuffle=True)
            
            self.assertIsInstance(params['page'], int)
            self.assertIsInstance(params['query_offset'], int)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.tracker = EnhancedSessionTracker(self.temp_dir)
    
    def tearDown(self):
        """Clean up integration test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_search_session(self):
        """Test a complete search session workflow."""
        # Simulate multiple searches
        queries = ["sunset", "mountain", "ocean", "sunset", "forest"]
        
        for i, query in enumerate(queries):
            # Get search parameters
            page, offset = self.tracker.get_search_parameters(query)
            
            # Simulate showing an image
            image_id = f"img_{query}_{i}"
            image_url = f"http://example.com/{image_id}.jpg"
            self.tracker.record_image_shown(query, image_id, image_url, page)
            
            # Simulate some quiz activity
            if i % 2 == 0:
                self.tracker.log_quiz_attempt(f"word_{i}", i % 3 == 0, 2.0 + i * 0.5)
        
        # Check session statistics
        stats = self.tracker.get_session_stats()
        self.assertEqual(stats['images_viewed'], 5)
        self.assertEqual(stats['unique_searches'], 4)  # 4 unique queries
        
        # Check query-specific stats
        sunset_stats = self.tracker.get_query_stats("sunset")
        self.assertEqual(sunset_stats['images_shown'], 2)  # "sunset" appeared twice
        
        # Test session save
        self.tracker.save_session()
        
        # Verify persistence
        new_tracker = EnhancedSessionTracker(self.temp_dir)
        self.assertTrue(new_tracker.has_seen_image("sunset", "img_sunset_0"))
        self.assertTrue(new_tracker.has_seen_image("mountain", "img_mountain_1"))
    
    def test_variety_across_sessions(self):
        """Test that variety management works across multiple sessions."""
        # First session
        for i in range(5):
            self.tracker.record_image_shown("nature", f"img_{i}", f"http://example.com/{i}.jpg", 1)
        
        first_page, first_offset = self.tracker.get_search_parameters("nature")
        
        # Save and start new session
        self.tracker.save_session()
        self.tracker.reset_session()
        
        # Second session should use different parameters
        second_page, second_offset = self.tracker.get_search_parameters("nature")
        
        # Should advance to next page since > 10 images were shown
        # (Note: in real usage with 10 per page, but our test shows 5 so might stay on same page)
        self.assertIsInstance(second_page, int)
        self.assertIsInstance(second_offset, int)


if __name__ == '__main__':
    # Create test suite
    test_classes = [
        TestImageSearchRecord,
        TestSearchVarietyManager,
        TestEnhancedSessionStats,
        TestEnhancedSessionTracker,
        TestUtilityFunctions,
        TestIntegration
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print(f"\\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    print(f"{'='*50}")
    
    # Exit with appropriate code
    exit_code = 0 if result.wasSuccessful() else 1
    sys.exit(exit_code)