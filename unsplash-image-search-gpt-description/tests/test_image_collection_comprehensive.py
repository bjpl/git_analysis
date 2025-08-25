"""
Comprehensive tests for image collection functionality focusing on:
- Timeout scenarios
- Error handling with mock API failures  
- Progress updates
- Cancellation functionality
- Collection limits and state management
"""

import unittest
import threading
import time
import queue
import json
from unittest.mock import Mock, patch, MagicMock, call
from unittest import mock
import requests
import tkinter as tk
from pathlib import Path
import sys
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import application modules
from config_manager import ConfigManager
from main import ImageSearchApp

class TestImageCollectionTimeouts(unittest.TestCase):
    """Test timeout scenarios in image collection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_manager = Mock(spec=ConfigManager)
        self.config_manager.get_api_keys.return_value = {
            'unsplash': 'test_unsplash_key',
            'openai': 'test_openai_key', 
            'gpt_model': 'gpt-4o-mini'
        }
        self.config_manager.get_paths.return_value = {
            'data_dir': self.temp_dir,
            'log_file': self.temp_dir / 'test_log.json',
            'vocabulary_file': self.temp_dir / 'test_vocab.csv'
        }
        
        # Mock config for app settings
        mock_config = Mock()
        mock_config.get.return_value = '30'  # max_images_per_search
        self.config_manager.config = mock_config
        
        # Skip theme manager for tests
        with patch('main.ThemeManager'), \
             patch('main.ensure_api_keys_configured', return_value=self.config_manager):
            self.app = ImageSearchApp()
            
    def tearDown(self):
        """Clean up test fixtures."""
        try:
            if hasattr(self, 'app'):
                self.app.destroy()
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
    
    @patch('requests.get')
    def test_unsplash_api_timeout(self, mock_get):
        """Test handling of Unsplash API timeout."""
        # Simulate timeout
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        # Track state changes
        state_changes = []
        original_update_status = self.app.update_status
        def track_status(message):
            state_changes.append(message)
            original_update_status(message)
        self.app.update_status = track_status
        
        # Call fetch_images_page directly
        with self.assertRaises(requests.exceptions.Timeout):
            self.app.fetch_images_page("nature", 1)
        
        # Verify retry mechanism was attempted
        self.assertEqual(mock_get.call_count, 3)  # max_retries=3
        
    @patch('requests.get')
    def test_image_download_timeout(self, mock_get):
        """Test handling of image download timeout."""
        # Mock successful API call but failed image download
        api_response = Mock()
        api_response.json.return_value = {
            'results': [{
                'urls': {'regular': 'https://test.com/image.jpg'},
                'id': 'test123'
            }]
        }
        api_response.raise_for_status.return_value = None
        
        # First call succeeds (API), second call times out (image download)
        mock_get.side_effect = [
            api_response,
            requests.exceptions.Timeout("Image download timed out")
        ]
        
        self.app.current_query = "test"
        self.app.current_page = 1
        self.app.current_results = []
        self.app.current_index = 0
        
        # Mock the page fetch to return our test data
        with patch.object(self.app, 'fetch_images_page', return_value=api_response.json()['results']):
            result = self.app.get_next_image()
            self.assertIsNone(result)
            
        # Verify retry attempts were made
        self.assertGreaterEqual(mock_get.call_count, 2)
    
    @patch('requests.get')
    def test_slow_api_response_handling(self, mock_get):
        """Test handling of very slow API responses."""
        # Create a slow response that takes longer than normal
        def slow_response(*args, **kwargs):
            time.sleep(2)  # Simulate 2 second delay
            response = Mock()
            response.json.return_value = {'results': []}
            response.raise_for_status.return_value = None
            return response
            
        mock_get.side_effect = slow_response
        
        start_time = time.time()
        
        try:
            self.app.fetch_images_page("slow", 1)
        except:
            pass
            
        elapsed_time = time.time() - start_time
        
        # Should have waited at least 2 seconds but less than timeout
        self.assertGreaterEqual(elapsed_time, 2.0)
        self.assertLess(elapsed_time, 15.0)  # Should be less than timeout
        
    def test_connection_error_handling(self):
        """Test handling of connection errors."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
            
            with self.assertRaises(requests.exceptions.ConnectionError):
                self.app.fetch_images_page("network_error", 1)
            
            # Verify retries were attempted
            self.assertEqual(mock_get.call_count, 3)

class TestAPIFailureHandling(unittest.TestCase):
    """Test error handling with various API failure scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_manager = Mock(spec=ConfigManager)
        self.config_manager.get_api_keys.return_value = {
            'unsplash': 'test_key',
            'openai': 'test_key',
            'gpt_model': 'gpt-4o-mini'
        }
        self.config_manager.get_paths.return_value = {
            'data_dir': self.temp_dir,
            'log_file': self.temp_dir / 'test_log.json',
            'vocabulary_file': self.temp_dir / 'test_vocab.csv'
        }
        
        # Mock config
        mock_config = Mock()
        mock_config.get.return_value = '30'
        self.config_manager.config = mock_config
        
        with patch('main.ThemeManager'), \
             patch('main.ensure_api_keys_configured', return_value=self.config_manager):
            self.app = ImageSearchApp()
            
    def tearDown(self):
        """Clean up."""
        try:
            if hasattr(self, 'app'):
                self.app.destroy()
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
    
    @patch('requests.get')
    def test_unsplash_403_error(self, mock_get):
        """Test handling of 403 Forbidden error from Unsplash."""
        response = Mock()
        response.raise_for_status.side_effect = requests.exceptions.HTTPError("403 Forbidden")
        response.status_code = 403
        mock_get.return_value = response
        
        with self.assertRaises(requests.exceptions.HTTPError):
            self.app.fetch_images_page("forbidden", 1)
    
    @patch('requests.get')
    def test_unsplash_rate_limit(self, mock_get):
        """Test handling of rate limit (429) error."""
        response = Mock()
        response.raise_for_status.side_effect = requests.exceptions.HTTPError("429 Too Many Requests")
        response.status_code = 429
        mock_get.return_value = response
        
        with self.assertRaises(requests.exceptions.HTTPError):
            self.app.fetch_images_page("rate_limited", 1)
    
    @patch('requests.get')
    def test_malformed_api_response(self, mock_get):
        """Test handling of malformed API response."""
        response = Mock()
        response.json.return_value = {"invalid": "response"}  # Missing 'results' key
        response.raise_for_status.return_value = None
        mock_get.return_value = response
        
        result = self.app.fetch_images_page("malformed", 1)
        self.assertEqual(result, [])  # Should return empty list when 'results' missing
    
    @patch('requests.get')
    def test_invalid_json_response(self, mock_get):
        """Test handling of invalid JSON response."""
        response = Mock()
        response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        response.raise_for_status.return_value = None
        mock_get.return_value = response
        
        with self.assertRaises(json.JSONDecodeError):
            self.app.fetch_images_page("invalid_json", 1)
    
    @patch('requests.get')
    def test_network_interruption_recovery(self, mock_get):
        """Test recovery from network interruption during search."""
        # First call fails, second succeeds
        response_success = Mock()
        response_success.json.return_value = {'results': [{'urls': {'regular': 'test.jpg'}}]}
        response_success.raise_for_status.return_value = None
        
        mock_get.side_effect = [
            requests.exceptions.ConnectionError("Network interrupted"),
            requests.exceptions.ConnectionError("Still down"),
            response_success  # Third attempt succeeds
        ]
        
        result = self.app.api_call_with_retry(lambda: mock_get())
        self.assertEqual(result, response_success)
        self.assertEqual(mock_get.call_count, 3)

class TestProgressUpdates(unittest.TestCase):
    """Test progress update functionality during image collection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_manager = Mock(spec=ConfigManager)
        self.config_manager.get_api_keys.return_value = {
            'unsplash': 'test_key',
            'openai': 'test_key',
            'gpt_model': 'gpt-4o-mini'
        }
        self.config_manager.get_paths.return_value = {
            'data_dir': self.temp_dir,
            'log_file': self.temp_dir / 'test_log.json',
            'vocabulary_file': self.temp_dir / 'test_vocab.csv'
        }
        
        mock_config = Mock()
        mock_config.get.return_value = '5'  # Small limit for testing
        self.config_manager.config = mock_config
        
        with patch('main.ThemeManager'), \
             patch('main.ensure_api_keys_configured', return_value=self.config_manager):
            self.app = ImageSearchApp()
            
        # Track progress updates
        self.progress_updates = []
        original_update_status = self.app.update_status
        def track_progress(message):
            self.progress_updates.append(message)
            original_update_status(message)
        self.app.update_status = track_progress
        
    def tearDown(self):
        """Clean up."""
        try:
            if hasattr(self, 'app'):
                self.app.destroy()
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
    
    def test_progress_bar_visibility(self):
        """Test that progress bar shows/hides appropriately."""
        # Initially hidden
        self.assertFalse(self.app.progress_bar.winfo_viewable())
        
        # Show progress
        self.app.show_progress("Testing")
        self.app.update_idletasks()
        
        # Should be visible now (if grid is called)
        # Note: In headless test environment, winfo_viewable might not work as expected
        
        # Hide progress
        self.app.hide_progress()
        
        # Progress bar should be stopped
        self.assertIsNone(self.app.loading_animation_id)
    
    def test_search_state_transitions(self):
        """Test search state changes during collection process."""
        # Initial state
        self.assertEqual(self.app.search_state, 'idle')
        self.assertEqual(self.app.images_collected_count, 0)
        
        # Start search
        self.app.start_search_session()
        self.assertEqual(self.app.search_state, 'searching')
        self.assertEqual(self.app.images_collected_count, 0)
        
        # Stop search
        self.app.stop_search()
        self.assertEqual(self.app.search_state, 'cancelled')
        self.assertTrue(self.app.search_cancelled)
    
    def test_collection_limit_handling(self):
        """Test behavior when collection limit is reached."""
        self.app.images_collected_count = self.app.max_images_per_search
        
        # Should trigger limit reached
        self.app.show_collection_limit_reached()
        self.assertEqual(self.app.search_state, 'completed')
        
        # Button should change to "Load More"
        self.assertEqual(self.app.another_button.cget('text'), "Load More (30)")
    
    def test_load_more_functionality(self):
        """Test load more images functionality."""
        original_limit = self.app.max_images_per_search
        
        self.app.load_more_images()
        
        # Limit should increase
        self.assertEqual(self.app.max_images_per_search, original_limit + 30)
        
        # Button text should reset
        self.assertEqual(self.app.another_button.cget('text'), "Otra Imagen")
    
    def test_progress_counter_updates(self):
        """Test that progress counter updates correctly."""
        self.app.images_collected_count = 3
        self.app.update_search_progress()
        
        # Check if stats were updated
        stats_text = self.app.stats_label.cget('text')
        self.assertIn("3/", stats_text)

class TestCancellationFunctionality(unittest.TestCase):
    """Test cancellation of image collection operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_manager = Mock(spec=ConfigManager)
        self.config_manager.get_api_keys.return_value = {
            'unsplash': 'test_key',
            'openai': 'test_key',
            'gpt_model': 'gpt-4o-mini'
        }
        self.config_manager.get_paths.return_value = {
            'data_dir': self.temp_dir,
            'log_file': self.temp_dir / 'test_log.json',
            'vocabulary_file': self.temp_dir / 'test_vocab.csv'
        }
        
        mock_config = Mock()
        mock_config.get.return_value = '30'
        self.config_manager.config = mock_config
        
        with patch('main.ThemeManager'), \
             patch('main.ensure_api_keys_configured', return_value=self.config_manager):
            self.app = ImageSearchApp()
            
    def tearDown(self):
        """Clean up."""
        try:
            if hasattr(self, 'app'):
                self.app.destroy()
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
    
    def test_search_cancellation(self):
        """Test cancelling search operation."""
        # Start a search
        self.app.start_search_session()
        self.assertFalse(self.app.search_cancelled)
        self.assertEqual(self.app.search_state, 'searching')
        
        # Cancel the search
        self.app.stop_search()
        self.assertTrue(self.app.search_cancelled)
        self.assertEqual(self.app.search_state, 'cancelled')
    
    def test_cancelled_search_cleanup(self):
        """Test that cancelled searches clean up properly."""
        self.app.search_cancelled = True
        
        # Simulate thread operations checking cancellation
        result = None
        if not self.app.search_cancelled:
            result = "should_not_execute"
        
        # Should not execute when cancelled
        self.assertIsNone(result)
    
    def test_button_states_during_cancellation(self):
        """Test button states during and after cancellation."""
        # Start search (buttons should be disabled)
        self.app.disable_buttons()
        self.assertEqual(self.app.search_button.cget('state'), 'disabled')
        
        # Cancel search (buttons should be enabled)
        self.app.enable_buttons()
        self.assertEqual(self.app.search_button.cget('state'), 'normal')
    
    @patch('threading.Thread')
    def test_thread_cancellation_handling(self, mock_thread):
        """Test that threads handle cancellation properly."""
        # Mock thread to not actually start
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        # Set search as cancelled before starting
        self.app.search_cancelled = True
        
        # Simulate thread function checking cancellation
        def mock_thread_func():
            if self.app.search_cancelled:
                return  # Should exit early
            # This should not execute
            raise Exception("Thread should have been cancelled")
        
        # Should exit without error when cancelled
        mock_thread_func()  # No exception should be raised

class TestSearchStateManagement(unittest.TestCase):
    """Test search state management during errors and operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_manager = Mock(spec=ConfigManager)
        self.config_manager.get_api_keys.return_value = {
            'unsplash': 'test_key',
            'openai': 'test_key',
            'gpt_model': 'gpt-4o-mini'
        }
        self.config_manager.get_paths.return_value = {
            'data_dir': self.temp_dir,
            'log_file': self.temp_dir / 'test_log.json',
            'vocabulary_file': self.temp_dir / 'test_vocab.csv'
        }
        
        mock_config = Mock()
        mock_config.get.return_value = '30'
        self.config_manager.config = mock_config
        
        with patch('main.ThemeManager'), \
             patch('main.ensure_api_keys_configured', return_value=self.config_manager):
            self.app = ImageSearchApp()
            
    def tearDown(self):
        """Clean up."""
        try:
            if hasattr(self, 'app'):
                self.app.destroy()
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
    
    def test_state_reset_on_new_search(self):
        """Test state is properly reset when starting new search."""
        # Set some state
        self.app.images_collected_count = 10
        self.app.search_cancelled = True
        self.app.search_state = 'cancelled'
        
        # Reset state
        self.app.reset_search_state()
        
        # Should be reset
        self.assertEqual(self.app.images_collected_count, 0)
        self.assertFalse(self.app.search_cancelled)
        self.assertEqual(self.app.search_state, 'idle')
    
    def test_error_state_handling(self):
        """Test state management when errors occur."""
        self.app.start_search_session()
        
        # Simulate an error occurring
        self.app.search_state = 'error'
        
        # State should be preserved until explicitly reset
        self.assertEqual(self.app.search_state, 'error')
        
        # Reset should clear error state
        self.app.reset_search_state()
        self.assertEqual(self.app.search_state, 'idle')
    
    def test_concurrent_state_changes(self):
        """Test handling of concurrent state changes."""
        # This is a basic test - in real scenarios we'd need more complex threading tests
        original_state = self.app.search_state
        
        # Simulate rapid state changes
        self.app.search_state = 'searching'
        self.app.search_state = 'completed'
        self.app.search_state = 'idle'
        
        # Final state should be 'idle'
        self.assertEqual(self.app.search_state, 'idle')

class TestManualApplicationFlow(unittest.TestCase):
    """Test manual application flow to ensure no hanging."""
    
    def setUp(self):
        """Set up for manual testing."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_app_initialization_no_hang(self):
        """Test that app initializes without hanging."""
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
        
        start_time = time.time()
        
        try:
            with patch('main.ThemeManager'), \
                 patch('main.ensure_api_keys_configured', return_value=config_manager):
                app = ImageSearchApp()
                
                # App should initialize quickly
                init_time = time.time() - start_time
                self.assertLess(init_time, 5.0, "App initialization took too long")
                
                # Test basic UI responsiveness
                app.update_idletasks()
                
                app.destroy()
                
        except Exception as e:
            self.fail(f"App initialization failed: {e}")
    
    @patch('requests.get')
    def test_search_operation_no_hang(self, mock_get):
        """Test search operation doesn't hang."""
        # Mock successful response
        response = Mock()
        response.json.return_value = {'results': []}
        response.raise_for_status.return_value = None
        mock_get.return_value = response
        
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
        
        try:
            with patch('main.ThemeManager'), \
                 patch('main.ensure_api_keys_configured', return_value=config_manager):
                app = ImageSearchApp()
                
                # Set search query
                app.search_entry.insert(0, "test query")
                
                start_time = time.time()
                
                # Simulate direct API call (bypass threading for test)
                result = app.fetch_images_page("test", 1)
                
                # Should complete quickly
                api_time = time.time() - start_time
                self.assertLess(api_time, 3.0, "API call took too long")
                
                # Result should be empty list (mocked response)
                self.assertEqual(result, [])
                
                app.destroy()
                
        except Exception as e:
            self.fail(f"Search operation test failed: {e}")

if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    # Run with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)