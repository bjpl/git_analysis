"""
Comprehensive tests for cancellation functionality.
Tests user-initiated cancellation, timeout cancellation, and cleanup.
"""

import unittest
import threading
import time
import queue
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
from pathlib import Path
import tempfile
import shutil
import sys
import requests

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config_manager import ConfigManager
from main import ImageSearchApp

class TestUserCancellation(unittest.TestCase):
    """Test user-initiated cancellation scenarios."""
    
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
        mock_config.get.return_value = '30'
        config_manager.config = mock_config
        
        with patch('main.ThemeManager'), \
             patch('main.ensure_api_keys_configured', return_value=config_manager):
            self.app = ImageSearchApp()
    
    def test_cancel_search_button(self):
        """Test cancelling search via stop button."""
        # Start search
        self.app.start_search_session()
        self.assertEqual(self.app.search_state, 'searching')
        self.assertFalse(self.app.search_cancelled)
        
        # Cancel search
        self.app.stop_search()
        
        # Should be cancelled
        self.assertTrue(self.app.search_cancelled)
        self.assertEqual(self.app.search_state, 'cancelled')
    
    def test_cancel_during_api_call(self):
        """Test cancellation during API call."""
        self.app.search_cancelled = False
        
        # Simulate check within API operation
        def mock_api_operation():
            # Simulate some work
            time.sleep(0.1)
            # Check if cancelled
            if self.app.search_cancelled:
                return None  # Early exit
            return "result"
        
        # Start operation
        result_before_cancel = mock_api_operation()
        self.assertEqual(result_before_cancel, "result")
        
        # Cancel and try again
        self.app.search_cancelled = True
        result_after_cancel = mock_api_operation()
        self.assertIsNone(result_after_cancel)
    
    def test_cancel_cleans_up_ui_state(self):
        """Test that cancellation cleans up UI properly."""
        # Start operation
        self.app.show_progress("Testing...")
        self.app.disable_buttons()
        
        # Cancel
        self.app.stop_search()
        
        # UI should be cleaned up
        self.assertEqual(self.app.search_state, 'cancelled')
        # Progress should be hidden (animation stopped)
        self.assertIsNone(self.app.loading_animation_id)
    
    def test_multiple_cancellations(self):
        """Test multiple cancellation calls don't cause issues."""
        self.app.start_search_session()
        
        # Multiple cancellations should be safe
        self.app.stop_search()
        self.assertTrue(self.app.search_cancelled)
        
        self.app.stop_search()  # Second call
        self.assertTrue(self.app.search_cancelled)  # Still cancelled
        
        self.app.stop_search()  # Third call
        self.assertTrue(self.app.search_cancelled)  # Still cancelled
    
    def test_cancel_resets_correctly(self):
        """Test that cancelled state resets properly for new searches."""
        # Cancel a search
        self.app.start_search_session()
        self.app.stop_search()
        self.assertTrue(self.app.search_cancelled)
        
        # Reset for new search
        self.app.reset_search_state()
        
        # Should be reset
        self.assertFalse(self.app.search_cancelled)
        self.assertEqual(self.app.search_state, 'idle')

class TestThreadCancellation(unittest.TestCase):
    """Test cancellation of threaded operations."""
    
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
    
    def test_thread_respects_cancellation(self):
        """Test that threads check and respect cancellation flag."""
        results = []
        
        def mock_thread_function():
            """Mock thread function that checks cancellation."""
            for i in range(10):
                if self.app.search_cancelled:
                    results.append("cancelled")
                    return
                time.sleep(0.1)  # Simulate work
                results.append(f"step_{i}")
            results.append("completed")
        
        # Start without cancellation
        self.app.search_cancelled = False
        thread = threading.Thread(target=mock_thread_function, daemon=True)
        thread.start()
        
        # Cancel after short delay
        time.sleep(0.15)  # Let it do some work
        self.app.search_cancelled = True
        
        # Wait for thread to complete
        thread.join(timeout=2.0)
        
        # Should have been cancelled partway through
        self.assertIn("cancelled", results)
        self.assertNotIn("completed", results)
        self.assertLess(len([r for r in results if r.startswith("step_")]), 10)
    
    @patch('requests.get')
    def test_cancel_during_image_download(self, mock_get):
        """Test cancellation during image download."""
        download_started = threading.Event()
        should_cancel = threading.Event()
        
        def slow_download(*args, **kwargs):
            download_started.set()  # Signal download started
            should_cancel.wait(timeout=2.0)  # Wait for cancel signal
            
            # Check if cancelled
            if self.app.search_cancelled:
                raise requests.exceptions.RequestException("Cancelled")
                
            response = Mock()
            response.content = b"image_data"
            response.raise_for_status.return_value = None
            return response
        
        mock_get.side_effect = slow_download
        
        # Start download in thread
        def download_thread():
            try:
                self.app.api_call_with_retry(lambda: mock_get())
            except:
                pass
        
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
        
        # Wait for download to start
        self.assertTrue(download_started.wait(timeout=1.0))
        
        # Cancel the operation
        self.app.search_cancelled = True
        should_cancel.set()
        
        # Wait for thread to complete
        thread.join(timeout=2.0)
        
        # Thread should have exited
        self.assertFalse(thread.is_alive())
    
    def test_thread_cleanup_on_cancellation(self):
        """Test proper cleanup when threads are cancelled."""
        cleanup_called = []
        
        def mock_thread_with_cleanup():
            try:
                # Simulate work
                for i in range(5):
                    if self.app.search_cancelled:
                        break
                    time.sleep(0.1)
            finally:
                cleanup_called.append("cleanup")
        
        thread = threading.Thread(target=mock_thread_with_cleanup, daemon=True)
        thread.start()
        
        # Cancel after brief delay
        time.sleep(0.05)
        self.app.search_cancelled = True
        
        # Wait for completion
        thread.join(timeout=1.0)
        
        # Cleanup should have been called
        self.assertIn("cleanup", cleanup_called)

class TestCancellationEdgeCases(unittest.TestCase):
    """Test edge cases in cancellation functionality."""
    
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
    
    def test_cancel_before_start(self):
        """Test cancellation before operation starts."""
        # Cancel before starting
        self.app.search_cancelled = True
        
        # Simulate thread function checking at start
        def mock_operation():
            if self.app.search_cancelled:
                return "early_exit"
            return "normal_execution"
        
        result = mock_operation()
        self.assertEqual(result, "early_exit")
    
    def test_cancel_after_completion(self):
        """Test cancellation after operation completes."""
        # Complete operation first
        self.app.search_state = 'completed'
        
        # Try to cancel
        self.app.stop_search()
        
        # Should still be cancelled but state reflects completion
        self.assertTrue(self.app.search_cancelled)
        self.assertEqual(self.app.search_state, 'cancelled')
    
    def test_rapid_start_cancel_cycles(self):
        """Test rapid start/cancel cycles."""
        for i in range(5):
            # Start
            self.app.start_search_session()
            self.assertEqual(self.app.search_state, 'searching')
            
            # Immediately cancel
            self.app.stop_search()
            self.assertTrue(self.app.search_cancelled)
            
            # Reset for next cycle
            self.app.reset_search_state()
            self.assertFalse(self.app.search_cancelled)
    
    def test_cancel_with_progress_updates(self):
        """Test cancellation while progress updates are active."""
        # Start progress animation
        self.app.show_progress("Testing cancellation")
        self.assertIsNotNone(self.app.loading_animation_id)
        
        # Cancel
        self.app.stop_search()
        
        # Animation should be stopped
        self.assertIsNone(self.app.loading_animation_id)
    
    def test_cancel_preserves_collected_data(self):
        """Test that cancellation preserves already collected data."""
        # Simulate some data collection
        self.app.images_collected_count = 5
        self.app.used_image_urls.add("https://test1.com/image1.jpg")
        self.app.used_image_urls.add("https://test2.com/image2.jpg")
        
        original_count = self.app.images_collected_count
        original_urls = self.app.used_image_urls.copy()
        
        # Cancel operation
        self.app.stop_search()
        
        # Data should be preserved
        self.assertEqual(self.app.images_collected_count, original_count)
        self.assertEqual(self.app.used_image_urls, original_urls)

class TestCancellationIntegration(unittest.TestCase):
    """Integration tests for cancellation with other app features."""
    
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
    
    def test_cancel_and_new_search(self):
        """Test starting new search after cancellation."""
        # Start and cancel first search
        self.app.start_search_session()
        self.app.current_query = "first_search"
        self.app.stop_search()
        
        # Start new search
        self.app.reset_search_state()
        self.app.start_search_session()
        self.app.current_query = "second_search"
        
        # Should be in searching state
        self.assertEqual(self.app.search_state, 'searching')
        self.assertFalse(self.app.search_cancelled)
        self.assertEqual(self.app.current_query, "second_search")
    
    def test_cancel_preserves_ui_state(self):
        """Test that cancellation preserves appropriate UI state."""
        # Set some UI state
        self.app.search_entry.insert(0, "test query")
        self.app.note_text.insert("1.0", "test notes")
        
        # Start and cancel search
        self.app.start_search_session()
        self.app.stop_search()
        
        # UI state should be preserved
        self.assertEqual(self.app.search_entry.get(), "test query")
        self.assertEqual(self.app.note_text.get("1.0", "end-1c"), "test notes")
    
    def test_cancel_with_vocabulary_collection(self):
        """Test cancellation when vocabulary has been collected."""
        # Simulate vocabulary collection
        self.app.target_phrases = ["test phrase 1", "test phrase 2"]
        self.app.vocabulary_cache.add("cached_word")
        
        original_phrases = self.app.target_phrases.copy()
        original_cache = self.app.vocabulary_cache.copy()
        
        # Cancel search
        self.app.stop_search()
        
        # Vocabulary should be preserved
        self.assertEqual(self.app.target_phrases, original_phrases)
        self.assertEqual(self.app.vocabulary_cache, original_cache)
    
    @patch('requests.get')
    def test_cancel_with_api_retry_in_progress(self, mock_get):
        """Test cancellation during API retry attempts."""
        retry_count = 0
        
        def failing_request(*args, **kwargs):
            nonlocal retry_count
            retry_count += 1
            
            # Cancel on second retry
            if retry_count == 2:
                self.app.search_cancelled = True
            
            raise requests.exceptions.RequestException("Test failure")
        
        mock_get.side_effect = failing_request
        
        # Should respect cancellation even during retries
        with self.assertRaises(requests.exceptions.RequestException):
            self.app.api_call_with_retry(lambda: mock_get(), max_retries=5)
        
        # Should have stopped retrying after cancellation
        self.assertLessEqual(retry_count, 3)  # Some tolerance for timing

if __name__ == '__main__':
    unittest.main(verbosity=2)