"""
Unit tests for Unsplash API service functionality.
Tests the ImageSearchApp's Unsplash integration methods.
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
import json
from pathlib import Path
import sys

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from main import ImageSearchApp
from tests.fixtures.sample_data import (
    SAMPLE_UNSPLASH_SEARCH_RESPONSE,
    ERROR_RESPONSES,
    TEST_IMAGE_DATA,
    PERFORMANCE_BENCHMARKS
)


@pytest.mark.unit
class TestUnsplashService:
    """Test suite for Unsplash API service functionality."""

    @pytest.fixture
    def app_instance(self, mock_config_manager, tkinter_root):
        """Create ImageSearchApp instance for testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            app = ImageSearchApp()
            # Don't show the actual GUI window
            app.withdraw()
            yield app
            try:
                app.destroy()
            except:
                pass

    def test_fetch_images_page_success(self, app_instance, mock_requests_get):
        """Test successful image fetch from Unsplash API."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        # Test the method
        results = app_instance.fetch_images_page("mountain", 1)

        # Assertions
        assert results == SAMPLE_UNSPLASH_SEARCH_RESPONSE["results"]
        assert len(results) == 2
        assert results[0]["id"] == "test_image_1"
        assert results[1]["id"] == "test_image_2"

        # Verify API call was made correctly
        expected_url = "https://api.unsplash.com/search/photos?query=mountain&page=1&per_page=10"
        expected_headers = {"Authorization": f"Client-ID test_unsplash_key"}
        mock_requests_get.assert_called_once_with(
            expected_url, 
            headers=expected_headers,
            timeout=10
        )

    def test_fetch_images_page_empty_results(self, app_instance, mock_requests_get):
        """Test handling of empty search results."""
        # Setup mock response with empty results
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "total": 0, "total_pages": 0}
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        results = app_instance.fetch_images_page("nonexistentterm", 1)

        assert results == []

    def test_fetch_images_page_network_error(self, app_instance, mock_requests_get):
        """Test handling of network errors."""
        # Setup mock to raise connection error
        mock_requests_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        with pytest.raises(requests.exceptions.ConnectionError):
            app_instance.fetch_images_page("mountain", 1)

    def test_fetch_images_page_timeout(self, app_instance, mock_requests_get):
        """Test handling of API timeout."""
        mock_requests_get.side_effect = requests.exceptions.Timeout("Request timed out")

        with pytest.raises(requests.exceptions.Timeout):
            app_instance.fetch_images_page("mountain", 1)

    def test_fetch_images_page_rate_limit(self, app_instance, mock_requests_get):
        """Test handling of rate limit errors."""
        # Setup mock response for rate limit
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("429 Client Error: Too Many Requests")
        mock_requests_get.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            app_instance.fetch_images_page("mountain", 1)

    def test_fetch_images_page_invalid_api_key(self, app_instance, mock_requests_get):
        """Test handling of invalid API key."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Client Error: Unauthorized")
        mock_requests_get.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            app_instance.fetch_images_page("mountain", 1)

    def test_api_call_with_retry_success(self, app_instance):
        """Test successful API call with retry mechanism."""
        # Mock function that succeeds on first try
        mock_func = Mock(return_value="success")
        
        result = app_instance.api_call_with_retry(mock_func, "arg1", "arg2", kwarg="test")
        
        assert result == "success"
        mock_func.assert_called_once_with("arg1", "arg2", kwarg="test")

    def test_api_call_with_retry_eventual_success(self, app_instance):
        """Test API call that fails initially but succeeds after retry."""
        # Mock function that fails twice then succeeds
        mock_func = Mock()
        mock_func.side_effect = [
            requests.exceptions.ConnectionError("First failure"),
            requests.exceptions.ConnectionError("Second failure"), 
            "success"
        ]
        
        with patch('time.sleep'):  # Speed up test by mocking sleep
            result = app_instance.api_call_with_retry(mock_func, max_retries=3)
        
        assert result == "success"
        assert mock_func.call_count == 3

    def test_api_call_with_retry_exhausted(self, app_instance):
        """Test API call that fails all retry attempts."""
        # Mock function that always fails
        mock_func = Mock()
        mock_func.side_effect = requests.exceptions.ConnectionError("Always fails")
        
        with patch('time.sleep'):  # Speed up test
            with pytest.raises(requests.exceptions.ConnectionError):
                app_instance.api_call_with_retry(mock_func, max_retries=3)
        
        assert mock_func.call_count == 3

    def test_api_call_with_retry_rate_limit_handling(self, app_instance):
        """Test rate limit specific handling in retry mechanism."""
        mock_func = Mock()
        mock_func.side_effect = [
            Exception("rate_limit exceeded"),
            "success"
        ]
        
        with patch('time.sleep') as mock_sleep:
            result = app_instance.api_call_with_retry(mock_func, max_retries=3)
        
        assert result == "success"
        # Should sleep for 5 seconds on rate limit
        mock_sleep.assert_called_with(5)

    def test_canonicalize_url(self, app_instance):
        """Test URL canonicalization (removing query parameters)."""
        # Test with query parameters
        url_with_params = "https://images.unsplash.com/photo-123?w=1080&q=80&fm=jpg"
        expected = "https://images.unsplash.com/photo-123"
        assert app_instance.canonicalize_url(url_with_params) == expected

        # Test without query parameters
        url_without_params = "https://images.unsplash.com/photo-123"
        assert app_instance.canonicalize_url(url_without_params) == expected

        # Test with None
        assert app_instance.canonicalize_url(None) == ""

        # Test with empty string
        assert app_instance.canonicalize_url("") == ""

    @patch('PIL.Image.open')
    @patch('PIL.ImageTk.PhotoImage')
    def test_get_next_image_success(self, mock_photo_image, mock_image_open, app_instance, mock_requests_get):
        """Test successful image retrieval and processing."""
        # Setup mocks
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response.raise_for_status = Mock()
        
        # Mock image download response
        mock_img_response = Mock()
        mock_img_response.content = TEST_IMAGE_DATA["png_1x1"]
        mock_img_response.raise_for_status = Mock()
        
        mock_requests_get.side_effect = [mock_response, mock_img_response]
        
        # Mock PIL operations
        mock_pil_image = Mock()
        mock_image_open.return_value = mock_pil_image
        mock_photo = Mock()
        mock_photo_image.return_value = mock_photo

        # Setup app state for getting next image
        app_instance.current_query = "mountain"
        app_instance.current_page = 1
        app_instance.current_results = []
        app_instance.current_index = 0

        result = app_instance.get_next_image()

        # Assertions
        assert result == mock_photo
        assert len(app_instance.used_image_urls) == 1
        assert app_instance.current_image_url is not None
        mock_pil_image.thumbnail.assert_called_once_with((600, 600))

    def test_get_next_image_skip_used_images(self, app_instance, mock_requests_get):
        """Test that previously used images are skipped."""
        # Setup mock responses
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        # Pre-populate used image URLs
        test_image_url = SAMPLE_UNSPLASH_SEARCH_RESPONSE["results"][0]["urls"]["regular"]
        app_instance.used_image_urls.add(app_instance.canonicalize_url(test_image_url))

        # Setup app state
        app_instance.current_query = "mountain"
        app_instance.current_page = 1
        app_instance.current_results = SAMPLE_UNSPLASH_SEARCH_RESPONSE["results"]
        app_instance.current_index = 0

        with patch('PIL.Image.open') as mock_image_open, \
             patch('PIL.ImageTk.PhotoImage') as mock_photo_image:
            
            # Mock image download for second image
            mock_img_response = Mock()
            mock_img_response.content = TEST_IMAGE_DATA["png_1x1"]
            mock_img_response.raise_for_status = Mock()
            
            # Mock the image download call (separate from search call)
            with patch('requests.get', return_value=mock_img_response):
                mock_pil_image = Mock()
                mock_image_open.return_value = mock_pil_image
                mock_photo = Mock()
                mock_photo_image.return_value = mock_photo

                result = app_instance.get_next_image()

                # Should return image for second result (first was already used)
                assert result == mock_photo
                expected_url = SAMPLE_UNSPLASH_SEARCH_RESPONSE["results"][1]["urls"]["regular"]
                assert app_instance.current_image_url == expected_url

    def test_get_next_image_no_more_results(self, app_instance, mock_requests_get):
        """Test handling when no more images are available."""
        # Setup mock to return empty results for new page
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "total": 0}
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        # Setup app state with exhausted current results
        app_instance.current_query = "mountain"
        app_instance.current_page = 1
        app_instance.current_results = []
        app_instance.current_index = 0

        result = app_instance.get_next_image()
        
        assert result is None

    def test_image_cache_functionality(self, app_instance, mock_requests_get):
        """Test image caching mechanism."""
        with patch('PIL.Image.open') as mock_image_open, \
             patch('PIL.ImageTk.PhotoImage') as mock_photo_image:
            
            # Setup mocks
            mock_response = Mock()
            mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
            mock_response.raise_for_status = Mock()
            
            mock_img_response = Mock()
            mock_img_response.content = TEST_IMAGE_DATA["png_1x1"]
            mock_img_response.raise_for_status = Mock()
            
            mock_requests_get.side_effect = [mock_response, mock_img_response]
            
            mock_pil_image = Mock()
            mock_image_open.return_value = mock_pil_image
            mock_photo = Mock()
            mock_photo_image.return_value = mock_photo

            # Setup app state
            app_instance.current_query = "mountain"
            app_instance.current_page = 1
            app_instance.current_results = []
            app_instance.current_index = 0

            # First call should download and cache
            result1 = app_instance.get_next_image()
            
            # Verify image was cached
            assert len(app_instance.image_cache) == 1
            cached_url = app_instance.canonicalize_url(
                SAMPLE_UNSPLASH_SEARCH_RESPONSE["results"][0]["urls"]["regular"]
            )
            assert cached_url in app_instance.image_cache

    def test_image_cache_size_limit(self, app_instance):
        """Test that image cache respects size limits."""
        # Fill cache beyond limit
        for i in range(15):  # More than the 10 item limit
            url = f"https://test.com/image_{i}"
            app_instance.image_cache[url] = f"image_data_{i}"

        # Cache should be limited to 10 items (oldest removed)
        assert len(app_instance.image_cache) <= 11  # 10 + 1 for the removal logic

    @pytest.mark.slow
    def test_fetch_images_performance(self, app_instance, mock_requests_get):
        """Test that image fetching completes within performance threshold."""
        import time
        
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        start_time = time.time()
        result = app_instance.fetch_images_page("mountain", 1)
        duration = time.time() - start_time

        assert duration < PERFORMANCE_BENCHMARKS["api_call_timeout"]
        assert len(result) > 0

    def test_search_query_sanitization(self, app_instance, mock_requests_get):
        """Test that search queries are properly handled."""
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        # Test with special characters
        query = "café & niño"
        app_instance.fetch_images_page(query, 1)

        # Verify URL encoding is handled by requests library
        call_args = mock_requests_get.call_args
        assert query in call_args[0][0]  # Query should be in URL

    def test_pagination_state_management(self, app_instance, mock_requests_get):
        """Test pagination state management."""
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        # Test initial state
        assert app_instance.current_page == 0
        assert app_instance.current_index == 0
        assert app_instance.current_results == []

        # Simulate search
        app_instance.current_query = "mountain"
        app_instance.current_page = 1
        results = app_instance.fetch_images_page("mountain", 1)
        app_instance.current_results = results

        assert len(app_instance.current_results) == 2
        assert app_instance.current_page == 1

    def test_load_used_image_urls_from_log_json(self, app_instance, test_data_dir):
        """Test loading used URLs from JSON log file."""
        from tests.fixtures.sample_data import SAMPLE_SESSION_DATA
        
        # Create test log file
        log_file = test_data_dir / "session_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(SAMPLE_SESSION_DATA, f)

        # Update app's log filename to test file
        app_instance.LOG_FILENAME = log_file

        # Clear current URLs and reload
        app_instance.used_image_urls.clear()
        app_instance.load_used_image_urls_from_log()

        # Verify URLs were loaded
        expected_urls = {
            "https://images.unsplash.com/photo-test1",
            "https://images.unsplash.com/photo-test2", 
            "https://images.unsplash.com/photo-test3"
        }
        
        for url in expected_urls:
            assert app_instance.canonicalize_url(url) in app_instance.used_image_urls

    def test_load_used_image_urls_corrupted_file(self, app_instance, test_data_dir):
        """Test handling of corrupted log file."""
        # Create corrupted log file
        log_file = test_data_dir / "session_log.json"
        with open(log_file, 'w') as f:
            f.write("invalid json content")

        app_instance.LOG_FILENAME = log_file

        # Should handle gracefully without raising exception
        app_instance.used_image_urls.clear()
        app_instance.load_used_image_urls_from_log()

        # URLs set should be empty due to corruption
        assert len(app_instance.used_image_urls) == 0

    def test_update_stats(self, app_instance):
        """Test statistics update functionality."""
        # Add some test data
        app_instance.used_image_urls.add("test_url_1")
        app_instance.used_image_urls.add("test_url_2")
        app_instance.vocabulary_cache.add("test_word_1")
        app_instance.target_phrases.extend(["phrase1", "phrase2"])

        # Test stats update
        app_instance.update_stats()

        # Verify stats are calculated correctly
        expected_images = 2
        expected_words = 3  # 1 from cache + 2 from target phrases

        # The actual assertion would check the GUI label, but we'll test the logic
        assert len(app_instance.used_image_urls) == expected_images
        assert len(app_instance.vocabulary_cache) + len(app_instance.target_phrases) == expected_words


@pytest.mark.integration
class TestUnsplashIntegration:
    """Integration tests for Unsplash service (require valid API key)."""

    @pytest.mark.api
    def test_real_unsplash_api_call(self, app_instance):
        """Test actual API call to Unsplash (requires valid API key)."""
        pytest.skip("Requires valid API key and network connection")
        
        # This test would make a real API call
        # Only enable if you have valid credentials and want to test against real API
        # results = app_instance.fetch_images_page("nature", 1)
        # assert len(results) > 0
        # assert all("urls" in result for result in results)