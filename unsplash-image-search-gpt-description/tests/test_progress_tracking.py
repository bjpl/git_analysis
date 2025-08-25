"""
Tests for progress tracking functionality during image collection.
Tests progress bars, status updates, collection limits, and user feedback.
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
from pathlib import Path
import tempfile
import shutil
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config_manager import ConfigManager
from main import ImageSearchApp

class TestProgressBarFunctionality(unittest.TestCase):
    """Test progress bar display and updates."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.setup_mock_app()
        
    def tearDown(self):
        """Clean up."""
        try:
            if hasattr(self, 'app'):
                self.app.destroy()
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
    
    def setup_mock_app(self):
        """Set up mock app for testing."""
        config_manager = Mock(spec=ConfigManager)
        config_manager.get_api_keys.return_value = {
            'unsplash': 'test_key',
            'openai': 'test_key',
            'gpt_model': 'gpt-4o-mini'
        }
        config_manager.get_paths.return_value = {
            'data_dir': self.temp_dir,
            'log_file': self.temp_dir / 'test_log.json',
            'vocabulary_file': self.temp_dir / 'test_vocab.csv'
        }
        
        mock_config = Mock()
        mock_config.get.return_value = '10'  # Small limit for testing
        config_manager.config = mock_config
        
        with patch('main.ThemeManager'), \
             patch('main.ensure_api_keys_configured', return_value=config_manager):
            self.app = ImageSearchApp()
            self.app.max_images_per_search = 10  # Set small limit
    
    def test_progress_bar_show_hide(self):
        """Test showing and hiding progress bar."""
        # Initially hidden
        # Note: In headless testing, we can't reliably test visibility
        # but we can test the method calls
        
        # Show progress
        self.app.show_progress("Testing progress")
        # Progress bar should be configured for display
        
        # Hide progress  
        self.app.hide_progress()
        # Loading animation should be stopped
        self.assertIsNone(self.app.loading_animation_id)
    
    def test_progress_modes(self):
        """Test different progress bar modes."""
        # Test indeterminate mode (initial search)
        self.app.search_state = 'idle'
        self.app.images_collected_count = 0
        self.app.show_progress("Searching...")
        
        # Should be in indeterminate mode
        # (We can't easily test the actual mode in headless environment)
        
        # Test determinate mode (during collection)
        self.app.search_state = 'searching'
        self.app.images_collected_count = 5
        self.app.show_progress("Collecting images...")
        
        # Progress variable should be updated
        self.assertEqual(self.app.progress_var.get(), 5)
    
    def test_loading_animation(self):
        """Test loading animation text."""
        # Start animation
        self.app.start_loading_animation("Loading")
        
        # Should have base message
        self.assertEqual(self.app.loading_base_message, "Loading")
        self.assertIsNotNone(self.app.loading_animation_id)
        
        # Stop animation
        self.app.stop_loading_animation()
        self.assertIsNone(self.app.loading_animation_id)
    
    def test_progress_with_cancellation(self):
        """Test progress handling when operation is cancelled."""
        # Start progress
        self.app.show_progress("Testing cancellation")
        self.app.start_loading_animation("Working")
        
        # Cancel
        self.app.search_cancelled = True
        self.app.hide_progress()
        
        # Animation should be stopped
        self.assertIsNone(self.app.loading_animation_id)

class TestStatusUpdates(unittest.TestCase):
    """Test status message updates during operations."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.setup_mock_app()
        self.status_messages = []
        
        # Track status updates
        original_update_status = self.app.update_status
        def track_status(message):
            self.status_messages.append(message)
            original_update_status(message)
        self.app.update_status = track_status
        
    def tearDown(self):
        """Clean up."""
        try:
            if hasattr(self, 'app'):
                self.app.destroy()
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
    
    def setup_mock_app(self):
        """Set up mock app."""
        config_manager = Mock(spec=ConfigManager)
        config_manager.get_api_keys.return_value = {
            'unsplash': 'test_key',
            'openai': 'test_key',
            'gpt_model': 'gpt-4o-mini'
        }
        config_manager.get_paths.return_value = {
            'data_dir': self.temp_dir,
            'log_file': self.temp_dir / 'test_log.json',
            'vocabulary_file': self.temp_dir / 'test_vocab.csv'
        }
        
        mock_config = Mock()
        mock_config.get.return_value = '30'
        config_manager.config = mock_config
        
        with patch('main.ThemeManager'), \
             patch('main.ensure_api_keys_configured', return_value=config_manager):
            self.app = ImageSearchApp()
    
    def test_status_during_search(self):
        """Test status updates during search process."""
        self.app.update_status("Starting search...")
        self.app.update_status("Fetching results...")
        self.app.update_status("Loading image...")
        
        # Should have recorded all status messages
        self.assertIn("Starting search...", self.status_messages)
        self.assertIn("Fetching results...", self.status_messages)
        self.assertIn("Loading image...", self.status_messages)
    
    def test_status_with_progress_count(self):
        """Test status updates that include progress count."""
        self.app.images_collected_count = 5
        self.app.update_search_progress()
        
        # Should have progress in status
        current_status = self.app.status_label.cget('text')
        self.assertIn("5/", current_status)
    
    def test_error_status_messages(self):
        """Test status messages for error conditions."""
        # Simulate API error
        self.app.update_status("API error, retrying in 1s... (attempt 1/3)")
        
        # Should record error message
        error_messages = [msg for msg in self.status_messages if "error" in msg.lower()]
        self.assertGreater(len(error_messages), 0)
    
    def test_completion_status_messages(self):
        """Test status messages for completion."""
        self.app.update_status("Image loaded successfully")
        self.app.update_status("Description generated successfully")
        
        # Should have success messages
        success_messages = [msg for msg in self.status_messages if "success" in msg.lower()]
        self.assertGreaterEqual(len(success_messages), 2)

class TestCollectionLimits(unittest.TestCase):
    """Test collection limit functionality and progress tracking."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.setup_mock_app()
        
    def tearDown(self):
        """Clean up."""
        try:
            if hasattr(self, 'app'):
                self.app.destroy()
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
    
    def setup_mock_app(self):
        """Set up mock app."""
        config_manager = Mock(spec=ConfigManager)
        config_manager.get_api_keys.return_value = {
            'unsplash': 'test_key',
            'openai': 'test_key',
            'gpt_model': 'gpt-4o-mini'
        }
        config_manager.get_paths.return_value = {
            'data_dir': self.temp_dir,
            'log_file': self.temp_dir / 'test_log.json',
            'vocabulary_file': self.temp_dir / 'test_vocab.csv'
        }
        
        mock_config = Mock()
        mock_config.get.return_value = '5'  # Very small limit for testing
        config_manager.config = mock_config
        
        with patch('main.ThemeManager'), \
             patch('main.ensure_api_keys_configured', return_value=config_manager):
            self.app = ImageSearchApp()
            self.app.max_images_per_search = 5
    
    def test_collection_limit_detection(self):
        """Test detection when collection limit is reached."""
        # Simulate reaching limit
        self.app.images_collected_count = self.app.max_images_per_search
        
        # Check limit
        limit_reached = self.app.images_collected_count >= self.app.max_images_per_search
        self.assertTrue(limit_reached)
    
    def test_limit_reached_ui_changes(self):
        """Test UI changes when limit is reached."""
        # Trigger limit reached
        self.app.show_collection_limit_reached()
        
        # Button should change to "Load More"
        self.assertEqual(self.app.another_button.cget('text'), "Load More (30)")
        
        # Search state should be completed
        self.assertEqual(self.app.search_state, 'completed')
    
    def test_load_more_increases_limit(self):
        """Test that load more increases the collection limit."""
        original_limit = self.app.max_images_per_search
        
        # Load more
        self.app.load_more_images()
        
        # Limit should increase
        self.assertEqual(self.app.max_images_per_search, original_limit + 30)
        
        # Button should reset
        self.assertEqual(self.app.another_button.cget('text'), "Otra Imagen")
    
    def test_progress_tracking_with_limits(self):
        """Test progress tracking respects collection limits."""
        # Set progress
        self.app.images_collected_count = 3
        self.app.progress_var.set(3)
        
        # Update progress
        self.app.update_search_progress()
        
        # Should show current progress
        self.assertEqual(self.app.progress_var.get(), 3)
        
        # Stats should reflect progress
        stats_text = self.app.stats_label.cget('text')
        self.assertIn("3/5", stats_text)
    
    def test_multiple_load_more_cycles(self):
        """Test multiple load more cycles."""
        original_limit = self.app.max_images_per_search
        
        # First load more
        self.app.load_more_images()
        self.assertEqual(self.app.max_images_per_search, original_limit + 30)
        
        # Reach limit again
        self.app.images_collected_count = self.app.max_images_per_search
        self.app.show_collection_limit_reached()
        
        # Second load more  
        self.app.load_more_images()
        self.assertEqual(self.app.max_images_per_search, original_limit + 60)

class TestSessionStatistics(unittest.TestCase):
    """Test session statistics and progress tracking."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.setup_mock_app()
        
    def tearDown(self):
        """Clean up."""
        try:
            if hasattr(self, 'app'):
                self.app.destroy()
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
    
    def setup_mock_app(self):
        """Set up mock app."""
        config_manager = Mock(spec=ConfigManager)
        config_manager.get_api_keys.return_value = {
            'unsplash': 'test_key',
            'openai': 'test_key',
            'gpt_model': 'gpt-4o-mini'
        }
        config_manager.get_paths.return_value = {
            'data_dir': self.temp_dir,
            'log_file': self.temp_dir / 'test_log.json',
            'vocabulary_file': self.temp_dir / 'test_vocab.csv'
        }
        
        mock_config = Mock()
        mock_config.get.return_value = '30'
        config_manager.config = mock_config
        
        with patch('main.ThemeManager'), \
             patch('main.ensure_api_keys_configured', return_value=config_manager):
            self.app = ImageSearchApp()
    
    def test_image_count_tracking(self):
        """Test tracking of image count."""
        # Add some URLs to simulate image collection
        self.app.used_image_urls.add("https://test1.com/image1.jpg")
        self.app.used_image_urls.add("https://test2.com/image2.jpg")
        self.app.used_image_urls.add("https://test3.com/image3.jpg")
        
        # Update stats
        self.app.update_stats()
        
        # Should show correct count
        stats_text = self.app.stats_label.cget('text')
        self.assertIn("Images: 3", stats_text)
    
    def test_vocabulary_count_tracking(self):
        """Test tracking of vocabulary count."""
        # Add vocabulary
        self.app.vocabulary_cache.add("word1")
        self.app.vocabulary_cache.add("word2")
        self.app.target_phrases = ["phrase1 - translation1", "phrase2 - translation2"]
        
        # Update stats
        self.app.update_stats()
        
        # Should show correct count (cache + target phrases)
        stats_text = self.app.stats_label.cget('text')
        self.assertIn("Words: 4", stats_text)  # 2 cached + 2 target
    
    def test_progress_tracking_display(self):
        """Test progress tracking display."""
        self.app.images_collected_count = 15
        self.app.max_images_per_search = 30
        
        # Update stats
        self.app.update_stats()
        
        # Should show progress
        stats_text = self.app.stats_label.cget('text')
        self.assertIn("Progress: 15/30", stats_text)
    
    def test_stats_update_frequency(self):
        """Test that stats update appropriately."""
        original_stats = self.app.stats_label.cget('text')
        
        # Add some data
        self.app.used_image_urls.add("https://new.com/image.jpg")
        
        # Update should change stats
        self.app.update_stats()
        new_stats = self.app.stats_label.cget('text')
        
        # Stats should have changed
        self.assertNotEqual(original_stats, new_stats)
    
    def test_reset_stats_on_new_search(self):
        """Test that relevant stats reset on new search."""
        # Set some progress
        self.app.images_collected_count = 10
        
        # Reset search state
        self.app.reset_search_state()
        
        # Progress count should reset
        self.assertEqual(self.app.images_collected_count, 0)
        
        # But used URLs should be preserved (session-wide)
        # This is correct behavior - we don't want duplicate images across searches

if __name__ == '__main__':
    unittest.main(verbosity=2)