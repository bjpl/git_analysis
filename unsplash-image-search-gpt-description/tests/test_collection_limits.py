#!/usr/bin/env python3
"""
Test script for collection limit functionality in the Unsplash Image Search app.
Tests the new safety controls that prevent infinite image collection.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the Python path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import ImageSearchApp
import tkinter as tk

class TestCollectionLimits(unittest.TestCase):
    """Test collection limit functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the test window
        
        # Mock the config manager to avoid API key setup
        with patch('main.ensure_api_keys_configured') as mock_ensure:
            from pathlib import Path
            mock_config = Mock()
            mock_config.get_api_keys.return_value = {
                'unsplash': 'test_key',
                'openai': 'test_key',
                'gpt_model': 'gpt-4o-mini'
            }
            mock_config.get_paths.return_value = {
                'data_dir': Path('/tmp/test_data'),
                'log_file': Path('/tmp/test_data/session_log.json'),
                'vocabulary_file': Path('/tmp/test_data/vocabulary.csv')
            }
            mock_config.config = Mock()
            mock_config.config.get.return_value = '30'  # max_images_per_search
            mock_ensure.return_value = mock_config
            
            self.app = ImageSearchApp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.app:
            self.app.destroy()
        self.root.destroy()
    
    def test_initial_collection_state(self):
        """Test initial collection state variables."""
        self.assertEqual(self.app.images_collected_count, 0)
        self.assertEqual(self.app.max_images_per_search, 30)
        self.assertFalse(self.app.search_cancelled)
        self.assertEqual(self.app.search_state, 'idle')
    
    def test_reset_search_state(self):
        """Test search state reset functionality."""
        # Set some values
        self.app.images_collected_count = 15
        self.app.search_cancelled = True
        self.app.search_state = 'searching'
        
        # Reset
        self.app.reset_search_state()
        
        # Check reset values
        self.assertEqual(self.app.images_collected_count, 0)
        self.assertFalse(self.app.search_cancelled)
        self.assertEqual(self.app.search_state, 'idle')
    
    def test_collection_limit_reached(self):
        """Test collection limit detection."""
        # Set count to limit
        self.app.images_collected_count = self.app.max_images_per_search
        
        # Mock get_next_image to test limit checking
        with patch.object(self.app, 'show_collection_limit_reached') as mock_show:
            result = self.app.get_next_image()
            
            # Should return None when limit reached
            self.assertIsNone(result)
            mock_show.assert_called_once()
    
    def test_search_cancellation(self):
        """Test search cancellation functionality."""
        # Start search state
        self.app.search_state = 'searching'
        self.app.search_cancelled = False
        
        # Cancel search
        self.app.stop_search()
        
        # Check state
        self.assertTrue(self.app.search_cancelled)
        self.assertEqual(self.app.search_state, 'cancelled')
    
    def test_progress_tracking(self):
        """Test progress tracking updates."""
        self.app.images_collected_count = 5
        self.app.max_images_per_search = 30
        
        # Test progress update
        self.app.update_search_progress()
        
        # Check progress bar value
        self.assertEqual(self.app.progress_var.get(), 5)
    
    @patch('main.messagebox.showinfo')
    def test_show_collection_limit_reached(self, mock_msgbox):
        """Test collection limit reached message."""
        self.app.images_collected_count = 30
        self.app.max_images_per_search = 30
        
        self.app.show_collection_limit_reached()
        
        # Check state changes
        self.assertEqual(self.app.search_state, 'completed')
        self.assertEqual(self.app.another_button.cget('text'), 'Load More (30)')
        mock_msgbox.assert_called_once()
    
    def test_load_more_functionality(self):
        """Test load more images functionality."""
        original_limit = self.app.max_images_per_search
        
        # Mock another_image to avoid actual API calls
        with patch.object(self.app, 'another_image') as mock_another:
            self.app.load_more_images()
            
            # Check limit increased
            self.assertEqual(self.app.max_images_per_search, original_limit + 30)
            
            # Check button text reset
            self.assertEqual(self.app.another_button.cget('text'), 'Otra Imagen')
            
            # Check another_image was called
            mock_another.assert_called_once()
    
    def test_handle_another_image_click(self):
        """Test another image button click handling."""
        # Test normal state
        with patch.object(self.app, 'another_image') as mock_another:
            self.app.handle_another_image_click()
            mock_another.assert_called_once()
        
        # Test load more state
        self.app.another_button.config(text='Load More (30)')
        with patch.object(self.app, 'load_more_images') as mock_load_more:
            self.app.handle_another_image_click()
            mock_load_more.assert_called_once()
    
    @patch('main.requests.get')
    def test_get_next_image_with_limits(self, mock_requests):
        """Test get_next_image with collection limits."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'fake_image_data'
        mock_requests.return_value = mock_response
        
        # Set up test data
        self.app.current_query = 'test'
        self.app.current_results = [{
            'urls': {'regular': 'http://test.com/image.jpg'}
        }]
        self.app.current_index = 0
        self.app.images_collected_count = 0
        
        # Mock PIL Image
        with patch('main.Image.open') as mock_image_open, \
             patch('main.ImageTk.PhotoImage') as mock_photo:
            
            mock_pil_image = Mock()
            mock_pil_image.copy.return_value = mock_pil_image
            mock_image_open.return_value = mock_pil_image
            
            mock_photo_instance = Mock()
            mock_photo.return_value = mock_photo_instance
            
            # Mock apply_zoom_to_image
            with patch.object(self.app, 'apply_zoom_to_image', return_value=mock_pil_image):
                result = self.app.get_next_image()
                
                # Should succeed and increment counter
                self.assertIsNotNone(result)
                self.assertEqual(self.app.images_collected_count, 1)
    
    def test_search_state_management(self):
        """Test search state management."""
        # Test start_search_session
        self.app.start_search_session()
        self.assertEqual(self.app.search_state, 'searching')
        self.assertFalse(self.app.search_cancelled)
        self.assertEqual(self.app.images_collected_count, 0)
        
        # Test stop_search
        self.app.stop_search()
        self.assertTrue(self.app.search_cancelled)
        self.assertEqual(self.app.search_state, 'cancelled')

class TestCollectionLimitsIntegration(unittest.TestCase):
    """Integration tests for collection limits."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Mock config manager with specific test values
        with patch('main.ensure_api_keys_configured') as mock_ensure:
            from pathlib import Path
            mock_config = Mock()
            mock_config.get_api_keys.return_value = {
                'unsplash': 'test_key',
                'openai': 'test_key', 
                'gpt_model': 'gpt-4o-mini'
            }
            mock_config.get_paths.return_value = {
                'data_dir': Path('/tmp/test_data'),
                'log_file': Path('/tmp/test_data/session_log.json'),
                'vocabulary_file': Path('/tmp/test_data/vocabulary.csv')
            }
            # Set a small limit for testing
            mock_config.config = Mock()
            mock_config.config.get.side_effect = lambda section, key, fallback=None: {
                ('Search', 'max_images_per_search'): '5',
                ('UI', 'zoom_level'): '100'
            }.get((section, key), fallback)
            
            mock_ensure.return_value = mock_config
            
            self.app = ImageSearchApp()
    
    def tearDown(self):
        """Clean up integration test fixtures."""
        if self.app:
            self.app.destroy()
        self.root.destroy()
    
    def test_full_search_cycle_with_limits(self):
        """Test complete search cycle with collection limits."""
        # Set small limit for testing
        self.app.max_images_per_search = 3
        
        # Mock API responses
        with patch.object(self.app, 'fetch_images_page') as mock_fetch, \
             patch('main.requests.get') as mock_requests, \
             patch('main.Image.open') as mock_image_open, \
             patch('main.ImageTk.PhotoImage') as mock_photo:
            
            # Set up mocks
            mock_fetch.return_value = [
                {'urls': {'regular': f'http://test.com/image{i}.jpg'}}
                for i in range(5)
            ]
            
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.content = b'fake_image_data'
            mock_requests.return_value = mock_response
            
            mock_pil_image = Mock()
            mock_pil_image.copy.return_value = mock_pil_image
            mock_image_open.return_value = mock_pil_image
            
            mock_photo.return_value = Mock()
            
            with patch.object(self.app, 'apply_zoom_to_image', return_value=mock_pil_image), \
                 patch.object(self.app, 'show_collection_limit_reached') as mock_limit_reached:
                
                self.app.current_query = 'test'
                self.app.current_results = mock_fetch.return_value
                self.app.current_index = 0
                
                # Simulate collecting images up to limit
                for i in range(4):  # One more than limit to test
                    result = self.app.get_next_image()
                    if i < 3:  # Within limit
                        self.assertIsNotNone(result)
                    else:  # Exceeds limit
                        self.assertIsNone(result)
                        mock_limit_reached.assert_called_once()
                        break

if __name__ == '__main__':
    # Create test directory
    os.makedirs('/tmp/test_data', exist_ok=True)
    
    # Run tests
    unittest.main(verbosity=2)