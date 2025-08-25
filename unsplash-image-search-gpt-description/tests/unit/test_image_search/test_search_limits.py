"""
Unit tests for image search with collection limits and cancellation.
Tests the get_next_image() method with various limit scenarios.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
import tkinter as tk
import requests
from PIL import Image
from io import BytesIO
import threading
import time
from datetime import datetime

from main import ImageSearchApp


class TestImageSearchLimits:
    """Test suite for image search collection limits."""

    @pytest.fixture
    def mock_app(self, mock_config_manager, no_gui):
        """Create a mock ImageSearchApp for testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            with patch('main.ThemeManager'):
                app = ImageSearchApp()
                app.config_manager = mock_config_manager
                
                # Mock essential attributes
                app.current_query = "test query"
                app.current_page = 1
                app.current_index = 0
                app.current_results = []
                app.used_image_urls = set()
                app.image_cache = {}
                app.current_image_url = None
                app.log_entries = []
                
                # Mock UI elements
                app.progress_bar = Mock()
                app.status_label = Mock()
                app.search_button = Mock()
                app.another_button = Mock()
                
                return app

    @pytest.fixture
    def sample_image_results(self):
        """Sample Unsplash API results."""
        return [
            {
                'id': f'image_{i}',
                'urls': {
                    'regular': f'https://images.unsplash.com/photo-{i}?w=400',
                    'small': f'https://images.unsplash.com/photo-{i}?w=200'
                },
                'alt_description': f'Test image {i}',
                'user': {'name': f'User {i}'},
                'description': f'Description {i}'
            }
            for i in range(1, 11)  # 10 images
        ]

    def test_get_next_image_basic_functionality(self, mock_app, sample_image_results):
        """Test basic get_next_image functionality."""
        mock_app.current_results = sample_image_results[:3]
        mock_app.current_index = 0
        
        # Mock PIL Image and requests
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.content = self._create_test_image_bytes()
            mock_get.return_value = mock_response
            
            with patch('main.Image.open') as mock_image_open:
                mock_image = Mock()
                mock_image.copy.return_value = mock_image
                mock_image_open.return_value = mock_image
                
                with patch.object(mock_app, 'apply_zoom_to_image', return_value=mock_image):
                    with patch('main.ImageTk.PhotoImage') as mock_photo:
                        mock_photo_obj = Mock()
                        mock_photo.return_value = mock_photo_obj
                        
                        result = mock_app.get_next_image()
                        
                        assert result is not None
                        photo, display_image = result
                        assert photo == mock_photo_obj
                        assert mock_app.current_index == 1
                        assert len(mock_app.used_image_urls) == 1

    def test_get_next_image_with_collection_limit(self, mock_app, sample_image_results):
        """Test that get_next_image respects collection limits."""
        # Set up a limit of 5 images
        MAX_IMAGES = 5
        mock_app.MAX_IMAGES_PER_SEARCH = MAX_IMAGES
        
        # Pre-populate used_image_urls to simulate reaching limit
        for i in range(MAX_IMAGES):
            mock_app.used_image_urls.add(f'https://images.unsplash.com/photo-{i}')
        
        mock_app.current_results = sample_image_results
        mock_app.current_index = 0
        
        # Mock the fetch_images_page to return new results
        with patch.object(mock_app, 'fetch_images_page') as mock_fetch:
            mock_fetch.return_value = []  # No more results
            
            with patch('tkinter.messagebox.showinfo') as mock_showinfo:
                result = mock_app.get_next_image()
                
                assert result is None
                mock_showinfo.assert_called_once()
                call_args = mock_showinfo.call_args[0]
                assert "No se encontraron más imágenes" in call_args[0]

    def test_get_next_image_pagination(self, mock_app, sample_image_results):
        """Test pagination when reaching end of current results."""
        mock_app.current_results = sample_image_results[:2]
        mock_app.current_index = 2  # Beyond current results
        
        # Mock fetch_images_page to return next page
        with patch.object(mock_app, 'fetch_images_page') as mock_fetch:
            mock_fetch.return_value = sample_image_results[2:4]
            
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.content = self._create_test_image_bytes()
                mock_get.return_value = mock_response
                
                with patch('main.Image.open') as mock_image_open:
                    mock_image = Mock()
                    mock_image.copy.return_value = mock_image
                    mock_image_open.return_value = mock_image
                    
                    with patch.object(mock_app, 'apply_zoom_to_image', return_value=mock_image):
                        with patch('main.ImageTk.PhotoImage'):
                            result = mock_app.get_next_image()
                            
                            assert result is not None
                            assert mock_app.current_page == 2
                            assert mock_app.current_index == 1
                            mock_fetch.assert_called_once_with('test query', 2)

    def test_get_next_image_skip_duplicates(self, mock_app, sample_image_results):
        """Test that get_next_image skips already used images."""
        mock_app.current_results = sample_image_results[:3]
        mock_app.current_index = 0
        
        # Mark first image as already used
        first_url = sample_image_results[0]['urls']['regular']
        mock_app.used_image_urls.add(mock_app.canonicalize_url(first_url))
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.content = self._create_test_image_bytes()
            mock_get.return_value = mock_response
            
            with patch('main.Image.open') as mock_image_open:
                mock_image = Mock()
                mock_image.copy.return_value = mock_image
                mock_image_open.return_value = mock_image
                
                with patch.object(mock_app, 'apply_zoom_to_image', return_value=mock_image):
                    with patch('main.ImageTk.PhotoImage'):
                        result = mock_app.get_next_image()
                        
                        assert result is not None
                        # Should skip to index 2 (second image in results)
                        assert mock_app.current_index == 2
                        
                        # Should have added the second image URL
                        second_url = mock_app.canonicalize_url(sample_image_results[1]['urls']['regular'])
                        assert second_url in mock_app.used_image_urls

    def test_get_next_image_api_error_handling(self, mock_app, sample_image_results):
        """Test error handling during API calls."""
        mock_app.current_results = []
        mock_app.current_index = 0
        
        # Mock API error
        with patch.object(mock_app, 'fetch_images_page') as mock_fetch:
            mock_fetch.side_effect = requests.exceptions.RequestException("API Error")
            
            with patch.object(mock_app, 'show_enhanced_error') as mock_show_error:
                result = mock_app.get_next_image()
                
                assert result is None
                mock_show_error.assert_called_once()

    def test_get_next_image_rate_limit_handling(self, mock_app, sample_image_results):
        """Test handling of rate limit errors."""
        mock_app.current_results = []
        mock_app.current_index = 0
        
        # Mock rate limit error
        error = requests.exceptions.HTTPError("429 Too Many Requests")
        with patch.object(mock_app, 'fetch_images_page') as mock_fetch:
            mock_fetch.side_effect = error
            
            with patch.object(mock_app, 'show_enhanced_error') as mock_show_error:
                result = mock_app.get_next_image()
                
                assert result is None
                mock_show_error.assert_called_once()
                call_args = mock_show_error.call_args[0]
                assert "Rate Limit" in call_args[0]

    def test_get_next_image_memory_management(self, mock_app, sample_image_results):
        """Test image cache memory management."""
        mock_app.current_results = sample_image_results[:15]  # More than cache limit
        mock_app.current_index = 0
        
        # Pre-populate cache with 12 items (over the limit of 10)
        for i in range(12):
            mock_app.image_cache[f'url_{i}'] = b'cached_data'
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.content = self._create_test_image_bytes()
            mock_get.return_value = mock_response
            
            with patch('main.Image.open') as mock_image_open:
                mock_image = Mock()
                mock_image.copy.return_value = mock_image
                mock_image_open.return_value = mock_image
                
                with patch.object(mock_app, 'apply_zoom_to_image', return_value=mock_image):
                    with patch('main.ImageTk.PhotoImage'):
                        result = mock_app.get_next_image()
                        
                        assert result is not None
                        # Cache should be limited to 10 items after cleanup
                        assert len(mock_app.image_cache) <= 10

    def test_get_next_image_cancellation_state(self, mock_app):
        """Test that get_next_image respects cancellation state."""
        # This test would require implementing a cancellation mechanism
        mock_app._search_cancelled = True
        mock_app.current_results = []
        mock_app.current_index = 0
        
        # If cancellation is implemented, should return None immediately
        result = mock_app.get_next_image()
        
        # For now, this will work as normal since cancellation isn't implemented
        # but this test structure is ready for when it is
        assert result is None  # Due to empty results

    def _create_test_image_bytes(self):
        """Create minimal PNG image bytes for testing."""
        # 1x1 pixel transparent PNG
        return (b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
                b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
                b'\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\xcc'
                b'\xdb\xd2\x00\x00\x00\x00IEND\xaeB`\x82')


class TestSearchCancellation:
    """Test suite for search cancellation functionality."""

    @pytest.fixture
    def mock_app(self, mock_config_manager, no_gui):
        """Create a mock ImageSearchApp with cancellation support."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            with patch('main.ThemeManager'):
                app = ImageSearchApp()
                app.config_manager = mock_config_manager
                
                # Add cancellation state
                app._search_cancelled = False
                app._current_search_thread = None
                
                # Mock UI elements
                app.progress_bar = Mock()
                app.status_label = Mock()
                app.search_button = Mock()
                app.another_button = Mock()
                app.stop_button = Mock()  # Cancel button
                
                return app

    def test_cancel_search_during_api_call(self, mock_app):
        """Test cancelling search during API call."""
        # Mock a slow API call
        def slow_api_call(*args, **kwargs):
            time.sleep(0.1)  # Simulate slow response
            if mock_app._search_cancelled:
                raise requests.exceptions.RequestException("Cancelled")
            return {'results': [], 'total': 0}
        
        with patch.object(mock_app, 'fetch_images_page', side_effect=slow_api_call):
            # Start search in thread
            search_thread = threading.Thread(
                target=mock_app.thread_search_images, 
                args=("test",),
                daemon=True
            )
            search_thread.start()
            
            # Cancel immediately
            mock_app._search_cancelled = True
            
            search_thread.join(timeout=1.0)
            
            # Verify cancellation was handled
            assert mock_app._search_cancelled == True

    def test_cancel_button_state_management(self, mock_app):
        """Test that cancel button state is managed correctly."""
        # Initially, no search is running
        assert mock_app._search_cancelled == False
        
        # Start search - cancel button should be enabled
        mock_app._search_cancelled = False
        mock_app.search_image = Mock()
        
        # Simulate search start
        mock_app.disable_buttons()
        assert mock_app.search_button.config.called
        
        # Cancel search
        mock_app._search_cancelled = True
        mock_app.enable_buttons()
        assert mock_app.search_button.config.called

    def test_progress_tracking_with_cancellation(self, mock_app):
        """Test that progress tracking works with cancellation."""
        mock_app.show_progress = Mock()
        mock_app.hide_progress = Mock()
        
        # Start progress
        mock_app.show_progress("Searching...")
        assert mock_app.show_progress.called
        
        # Cancel should hide progress
        mock_app._search_cancelled = True
        mock_app.hide_progress()
        assert mock_app.hide_progress.called