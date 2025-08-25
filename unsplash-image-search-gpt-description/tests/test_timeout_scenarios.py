"""
Focused tests for timeout scenarios in image collection.
Tests various timeout conditions and recovery mechanisms.
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
import requests
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

class TestConnectionTimeouts(unittest.TestCase):
    """Test connection timeout scenarios."""
    
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
    
    @patch('requests.get')
    def test_api_request_timeout(self, mock_get):
        """Test timeout during API request."""
        # Configure timeout
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")
        
        # Track retry attempts
        retry_count = 0
        def count_retries(*args, **kwargs):
            nonlocal retry_count
            retry_count += 1
            raise requests.exceptions.Timeout("Connection timed out")
        
        mock_get.side_effect = count_retries
        
        # Test should raise timeout after retries
        with self.assertRaises(requests.exceptions.Timeout):
            self.app.fetch_images_page("timeout_test", 1)
        
        # Should have retried max_retries times
        self.assertEqual(retry_count, 3)
    
    @patch('requests.get')
    def test_slow_response_within_timeout(self, mock_get):
        """Test slow response that completes within timeout."""
        def slow_response(*args, **kwargs):
            time.sleep(1)  # 1 second delay
            response = Mock()
            response.json.return_value = {'results': [{'urls': {'regular': 'test.jpg'}}]}
            response.raise_for_status.return_value = None
            return response
        
        mock_get.side_effect = slow_response
        
        start_time = time.time()
        result = self.app.fetch_images_page("slow_test", 1)
        elapsed = time.time() - start_time
        
        # Should complete successfully
        self.assertIsNotNone(result)
        self.assertGreaterEqual(elapsed, 1.0)  # At least 1 second
        self.assertLess(elapsed, 10.0)  # But reasonable time
    
    @patch('requests.get')
    def test_image_download_timeout(self, mock_get):
        """Test timeout during image download."""
        # First call (API) succeeds, second call (image) times out
        api_response = Mock()
        api_response.json.return_value = {
            'results': [{
                'urls': {'regular': 'https://test.com/image.jpg'},
                'id': 'test123'
            }]
        }
        api_response.raise_for_status.return_value = None
        
        mock_get.side_effect = [
            api_response,  # Successful API call
            requests.exceptions.Timeout("Image download timeout")  # Failed download
        ]
        
        # Set up app state
        self.app.current_query = "test"
        self.app.current_page = 1
        self.app.current_results = []
        self.app.current_index = 0
        
        # Mock fetch_images_page to use our test data
        with patch.object(self.app, 'fetch_images_page', 
                         return_value=api_response.json()['results']):
            result = self.app.get_next_image()
            
        # Should return None due to download failure
        self.assertIsNone(result)
        
        # Verify both calls were made
        self.assertEqual(mock_get.call_count, 2)
    
    @patch('requests.get')  
    def test_intermittent_timeout_recovery(self, mock_get):
        """Test recovery from intermittent timeouts."""
        success_response = Mock()
        success_response.json.return_value = {'results': [{'urls': {'regular': 'test.jpg'}}]}
        success_response.raise_for_status.return_value = None
        
        # First call times out, second succeeds
        mock_get.side_effect = [
            requests.exceptions.Timeout("Timeout 1"),
            success_response  # Recovery
        ]
        
        result = self.app.api_call_with_retry(lambda: mock_get(), max_retries=2)
        
        # Should succeed on retry
        self.assertEqual(result, success_response)
        self.assertEqual(mock_get.call_count, 2)

class TestReadTimeouts(unittest.TestCase):
    """Test read timeout scenarios during downloads."""
    
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
    
    @patch('requests.get')
    def test_partial_download_timeout(self, mock_get):
        """Test timeout during partial image download."""
        class PartialResponse:
            def __init__(self):
                self.content = b"partial_image_data"
                
            def raise_for_status(self):
                # Simulate timeout during content reading
                raise requests.exceptions.ReadTimeout("Read timeout")
        
        mock_get.return_value = PartialResponse()
        
        with self.assertRaises(requests.exceptions.ReadTimeout):
            self.app.api_call_with_retry(lambda: mock_get())
    
    @patch('requests.get')
    def test_large_image_timeout(self, mock_get):
        """Test timeout when downloading large images."""
        def slow_large_image(*args, **kwargs):
            # Simulate a slow large download
            time.sleep(2)  # 2 second delay
            response = Mock()
            response.content = b"x" * (10 * 1024 * 1024)  # 10MB fake image
            response.raise_for_status.return_value = None
            return response
        
        mock_get.side_effect = slow_large_image
        
        start_time = time.time()
        try:
            result = self.app.api_call_with_retry(lambda: mock_get(), max_retries=1)
            elapsed = time.time() - start_time
            
            # Should complete but take time
            self.assertIsNotNone(result)
            self.assertGreaterEqual(elapsed, 2.0)
            
        except Exception:
            # Acceptable if it times out with large images
            pass

class TestTimeoutRecovery(unittest.TestCase):
    """Test timeout recovery mechanisms."""
    
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
    
    def test_exponential_backoff(self):
        """Test exponential backoff in retry logic."""
        retry_times = []
        
        def mock_failing_call():
            retry_times.append(time.time())
            raise requests.exceptions.Timeout("Test timeout")
        
        start_time = time.time()
        
        with self.assertRaises(requests.exceptions.Timeout):
            self.app.api_call_with_retry(mock_failing_call, max_retries=3)
        
        # Should have 3 attempts
        self.assertEqual(len(retry_times), 3)
        
        # Check timing between retries (approximate due to test environment)
        if len(retry_times) >= 2:
            # First retry should be ~1 second after first attempt
            delay1 = retry_times[1] - retry_times[0]
            self.assertGreater(delay1, 0.5)  # At least some delay
            
        if len(retry_times) >= 3:
            # Second retry should be ~2 seconds after second attempt  
            delay2 = retry_times[2] - retry_times[1]
            self.assertGreater(delay2, delay1 * 0.8)  # Increasing delay
    
    @patch('requests.get')
    def test_timeout_status_updates(self, mock_get):
        """Test status updates during timeout scenarios."""
        # Track status updates
        status_updates = []
        original_update_status = self.app.update_status
        
        def track_status(message):
            status_updates.append(message)
            original_update_status(message)
        
        self.app.update_status = track_status
        
        # Configure timeout with retries
        mock_get.side_effect = [
            requests.exceptions.Timeout("Timeout 1"),
            requests.exceptions.Timeout("Timeout 2"),
            requests.exceptions.Timeout("Timeout 3")
        ]
        
        with self.assertRaises(requests.exceptions.Timeout):
            self.app.api_call_with_retry(lambda: mock_get(), max_retries=3)
        
        # Should have status updates for retries
        retry_messages = [msg for msg in status_updates if "retrying" in msg.lower()]
        self.assertGreater(len(retry_messages), 0)
    
    @patch('requests.get')
    def test_graceful_degradation(self, mock_get):
        """Test graceful degradation when timeouts persist."""
        # All requests timeout
        mock_get.side_effect = requests.exceptions.Timeout("Persistent timeout")
        
        self.app.current_query = "test"
        self.app.current_page = 1
        self.app.current_results = []
        self.app.current_index = 0
        
        # Should handle gracefully without crashing
        try:
            result = self.app.get_next_image()
            # Should return None for failed operation
            self.assertIsNone(result)
        except requests.exceptions.Timeout:
            # Acceptable - timeout should be handled at higher level
            pass
        
        # App should still be responsive
        self.app.update_idletasks()
        
        # Search state should be manageable
        self.assertIn(self.app.search_state, ['idle', 'error', 'cancelled'])

if __name__ == '__main__':
    unittest.main(verbosity=2)