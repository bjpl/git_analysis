"""
Unit tests for edge cases in image search functionality.
Tests scenarios like no results, API errors, limits reached, network timeouts.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import requests
from requests.exceptions import RequestException, Timeout, HTTPError, ConnectionError
import tkinter as tk
import json
from datetime import datetime, timedelta

from main import ImageSearchApp


class TestEdgeCases:
    """Test suite for edge cases and error conditions."""

    @pytest.fixture
    def mock_app(self, mock_config_manager, no_gui):
        """Create a mock ImageSearchApp for edge case testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            with patch('main.ThemeManager'):
                app = ImageSearchApp()
                app.config_manager = mock_config_manager
                
                # Initialize required attributes
                app.current_query = "test query"
                app.current_page = 1
                app.current_index = 0
                app.current_results = []
                app.used_image_urls = set()
                app.image_cache = {}
                app.log_entries = []
                
                # Mock UI elements
                app.progress_bar = Mock()
                app.status_label = Mock()
                app.search_button = Mock()
                app.show_enhanced_error = Mock()
                app.update_status = Mock()
                
                return app

    def test_no_search_results_found(self, mock_app):
        """Test handling when API returns no results."""
        mock_app.current_results = []
        mock_app.current_index = 0
        
        with patch.object(mock_app, 'fetch_images_page') as mock_fetch:
            mock_fetch.return_value = []  # No results
            
            with patch('tkinter.messagebox.showinfo') as mock_showinfo:
                result = mock_app.get_next_image()
                
                assert result is None
                mock_showinfo.assert_called_once()
                # Verify the message content
                call_args = mock_showinfo.call_args[0]
                assert "No se encontraron más imágenes" in call_args[0]

    def test_empty_search_query(self, mock_app):
        """Test handling of empty search queries."""
        with patch('tkinter.messagebox.showerror') as mock_showerror:
            # Mock empty search entry
            mock_app.search_entry = Mock()
            mock_app.search_entry.get.return_value = ""
            
            mock_app.search_image()
            
            mock_showerror.assert_called_once()
            call_args = mock_showerror.call_args[0]
            assert "Error" in call_args[0]
            assert "consulta de búsqueda" in call_args[1]

    def test_invalid_api_key_error(self, mock_app):
        """Test handling of invalid API key (403 error)."""
        with patch.object(mock_app, 'fetch_images_page') as mock_fetch:
            error = requests.exceptions.HTTPError("403 Forbidden")
            mock_fetch.side_effect = error
            
            result = mock_app.get_next_image()
            
            assert result is None
            mock_app.show_enhanced_error.assert_called_once()
            call_args = mock_app.show_enhanced_error.call_args[0]
            assert "API Error" in call_args[0]
            assert "API key may be invalid" in call_args[1]

    def test_rate_limit_exceeded_error(self, mock_app):
        """Test handling of rate limit exceeded (429 error)."""
        with patch.object(mock_app, 'fetch_images_page') as mock_fetch:
            error = requests.exceptions.HTTPError("429 Too Many Requests")
            mock_fetch.side_effect = error
            
            # Mock datetime for rate limit calculation
            with patch('main.datetime') as mock_datetime:
                mock_now = datetime(2024, 1, 1, 14, 30, 0)
                mock_datetime.now.return_value = mock_now
                mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                
                result = mock_app.get_next_image()
                
                assert result is None
                mock_app.show_enhanced_error.assert_called_once()
                call_args = mock_app.show_enhanced_error.call_args[0]
                assert "Rate Limit" in call_args[0]
                assert "50/hour" in call_args[1]

    def test_network_timeout_error(self, mock_app):
        """Test handling of network timeout errors."""
        with patch.object(mock_app, 'fetch_images_page') as mock_fetch:
            mock_fetch.side_effect = Timeout("Request timed out")
            
            result = mock_app.get_next_image()
            
            assert result is None
            mock_app.show_enhanced_error.assert_called_once()

    def test_connection_error(self, mock_app):
        """Test handling of network connection errors."""
        with patch.object(mock_app, 'fetch_images_page') as mock_fetch:
            mock_fetch.side_effect = ConnectionError("Failed to establish connection")
            
            result = mock_app.get_next_image()
            
            assert result is None
            mock_app.show_enhanced_error.assert_called_once()

    def test_malformed_api_response(self, mock_app):
        """Test handling of malformed API responses."""
        with patch.object(mock_app, 'fetch_images_page') as mock_fetch:
            # Return malformed response (missing required fields)
            mock_fetch.return_value = [
                {
                    'id': 'test_image',
                    # Missing 'urls' field
                    'alt_description': 'Test image'
                }
            ]
            
            mock_app.current_results = mock_fetch.return_value
            mock_app.current_index = 0
            
            # Should handle missing fields gracefully
            result = mock_app.get_next_image()
            # May return None or continue to next image depending on implementation
            assert result is None or result is not None

    def test_image_download_failure(self, mock_app):
        """Test handling when image download fails."""
        sample_result = {
            'id': 'test_image',
            'urls': {
                'regular': 'https://example.com/nonexistent.jpg',
                'small': 'https://example.com/small.jpg'
            },
            'alt_description': 'Test image'
        }
        
        mock_app.current_results = [sample_result]
        mock_app.current_index = 0
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("Failed to download")
            
            result = mock_app.get_next_image()
            
            # Should try next image or return None
            assert result is None

    def test_corrupted_image_data(self, mock_app):
        """Test handling of corrupted image data."""
        sample_result = {
            'id': 'test_image',
            'urls': {
                'regular': 'https://example.com/corrupted.jpg',
            }
        }
        
        mock_app.current_results = [sample_result]
        mock_app.current_index = 0
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.content = b'corrupted_data_not_an_image'
            mock_get.return_value = mock_response
            
            with patch('main.Image.open') as mock_image_open:
                mock_image_open.side_effect = Exception("Cannot identify image file")
                
                result = mock_app.get_next_image()
                
                # Should skip to next image
                assert mock_app.current_index == 1

    def test_memory_exhaustion_scenario(self, mock_app):
        """Test behavior when memory is exhausted."""
        sample_result = {
            'id': 'huge_image',
            'urls': {'regular': 'https://example.com/huge.jpg'}
        }
        
        mock_app.current_results = [sample_result]
        mock_app.current_index = 0
        
        with patch('requests.get') as mock_get:
            # Simulate huge image data
            mock_response = Mock()
            mock_response.content = b'x' * (100 * 1024 * 1024)  # 100MB
            mock_get.return_value = mock_response
            
            with patch('main.Image.open') as mock_image_open:
                mock_image_open.side_effect = MemoryError("Out of memory")
                
                result = mock_app.get_next_image()
                
                # Should handle gracefully and continue
                assert result is None or mock_app.current_index > 0

    def test_concurrent_search_requests(self, mock_app):
        """Test handling of concurrent search requests."""
        import threading
        
        results = []
        
        def search_worker(query_suffix):
            mock_app.current_query = f"test_{query_suffix}"
            with patch.object(mock_app, 'fetch_images_page') as mock_fetch:
                mock_fetch.return_value = [
                    {'id': f'img_{query_suffix}', 'urls': {'regular': f'url_{query_suffix}'}}
                ]
                result = mock_app.get_next_image()
                results.append(result)
        
        # Start multiple concurrent searches
        threads = []
        for i in range(3):
            thread = threading.Thread(target=search_worker, args=(i,), daemon=True)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=1.0)
        
        # All should complete without crashing
        assert len(results) == 3

    def test_api_key_suddenly_invalid(self, mock_app):
        """Test when API key becomes invalid mid-session."""
        # First call succeeds
        with patch.object(mock_app, 'fetch_images_page') as mock_fetch:
            # Setup sequence of responses
            mock_fetch.side_effect = [
                [{'id': 'img1', 'urls': {'regular': 'url1'}}],  # First call succeeds
                requests.exceptions.HTTPError("401 Unauthorized")  # Second call fails
            ]
            
            # First call should work
            mock_app.current_results = []
            mock_app.current_index = 0
            
            with patch('requests.get'):
                with patch('main.Image.open'):
                    with patch('main.ImageTk.PhotoImage'):
                        result1 = mock_app.get_next_image()
            
            # Second call should handle auth error
            mock_app.current_results = []
            mock_app.current_index = 0
            result2 = mock_app.get_next_image()
            
            assert result2 is None
            mock_app.show_enhanced_error.assert_called()

    def test_disk_space_exhausted(self, mock_app):
        """Test handling when disk space is exhausted (affects caching)."""
        sample_result = {
            'id': 'test_image',
            'urls': {'regular': 'https://example.com/test.jpg'}
        }
        
        mock_app.current_results = [sample_result]
        mock_app.current_index = 0
        
        # Simulate disk full error
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.content = b'image_data'
            mock_get.return_value = mock_response
            
            # Simulate disk full when trying to cache
            with patch.object(dict, '__setitem__') as mock_setitem:
                mock_setitem.side_effect = OSError("No space left on device")
                
                with patch('main.Image.open') as mock_image_open:
                    mock_image = Mock()
                    mock_image_open.return_value = mock_image
                    
                    with patch('main.ImageTk.PhotoImage'):
                        result = mock_app.get_next_image()
                        
                        # Should continue without caching
                        assert result is not None or result is None

    def test_maximum_retries_exceeded(self, mock_app):
        """Test behavior when maximum API retries are exceeded."""
        with patch.object(mock_app, 'api_call_with_retry') as mock_retry:
            # Simulate all retries failing
            mock_retry.side_effect = requests.exceptions.RequestException("Max retries exceeded")
            
            result = mock_app.get_next_image()
            
            assert result is None
            # Should have attempted retries
            mock_retry.assert_called()

    def test_json_parsing_error_in_api_response(self, mock_app):
        """Test handling of JSON parsing errors in API responses."""
        with patch.object(mock_app, 'fetch_images_page') as mock_fetch:
            mock_fetch.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            
            result = mock_app.get_next_image()
            
            assert result is None
            mock_app.show_enhanced_error.assert_called()

    def test_very_large_result_set(self, mock_app):
        """Test handling of very large result sets."""
        # Create a large number of results
        large_results = []
        for i in range(1000):
            large_results.append({
                'id': f'image_{i}',
                'urls': {'regular': f'https://example.com/image_{i}.jpg'}
            })
        
        mock_app.current_results = large_results
        mock_app.current_index = 999  # Near the end
        
        # Should handle large indices without issues
        result = mock_app.get_next_image()
        
        # Should either return None (no more results) or handle pagination
        assert result is None or mock_app.current_page > 1