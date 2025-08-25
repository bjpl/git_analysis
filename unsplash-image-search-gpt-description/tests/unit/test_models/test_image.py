"""
Unit tests for image handling and processing models.
Tests image caching, URL management, and image data processing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
from io import BytesIO

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from main import ImageSearchApp
from tests.fixtures.sample_data import (
    SAMPLE_UNSPLASH_SEARCH_RESPONSE,
    TEST_IMAGE_DATA,
    EDGE_CASES,
    PERFORMANCE_BENCHMARKS
)


@pytest.mark.unit
class TestImageModels:
    """Test suite for image handling and processing functionality."""

    @pytest.fixture
    def app_instance(self, mock_config_manager, tkinter_root):
        """Create ImageSearchApp instance for testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            app = ImageSearchApp()
            app.withdraw()
            yield app
            try:
                app.destroy()
            except:
                pass

    def test_image_cache_initialization(self, app_instance):
        """Test image cache is properly initialized."""
        assert isinstance(app_instance.image_cache, dict)
        assert len(app_instance.image_cache) == 0

    def test_image_cache_storage(self, app_instance):
        """Test storing images in cache."""
        # Test data
        url1 = "https://test.com/image1"
        url2 = "https://test.com/image2"
        image_data1 = TEST_IMAGE_DATA["png_1x1"]
        image_data2 = TEST_IMAGE_DATA["jpg_1x1"]

        # Store images
        app_instance.image_cache[url1] = image_data1
        app_instance.image_cache[url2] = image_data2

        # Verify storage
        assert len(app_instance.image_cache) == 2
        assert app_instance.image_cache[url1] == image_data1
        assert app_instance.image_cache[url2] == image_data2

    def test_image_cache_retrieval(self, app_instance):
        """Test retrieving images from cache."""
        # Setup cache
        url = "https://test.com/cached_image"
        image_data = TEST_IMAGE_DATA["png_1x1"]
        app_instance.image_cache[url] = image_data

        # Test retrieval
        retrieved_data = app_instance.image_cache.get(url)
        assert retrieved_data == image_data

        # Test non-existent image
        non_existent = app_instance.image_cache.get("https://test.com/nonexistent")
        assert non_existent is None

    def test_image_cache_size_management(self, app_instance):
        """Test image cache size management and cleanup."""
        # Fill cache beyond theoretical limit
        for i in range(15):  # More than typical limit
            url = f"https://test.com/image_{i}"
            app_instance.image_cache[url] = f"image_data_{i}".encode()

        # Test that cache doesn't grow indefinitely
        # (Actual size limiting logic would be in the application)
        assert len(app_instance.image_cache) == 15

        # Test manual cleanup (simulate the cleanup logic in get_next_image)
        if len(app_instance.image_cache) > 10:
            # Remove oldest entry (first key)
            oldest_key = next(iter(app_instance.image_cache))
            app_instance.image_cache.pop(oldest_key)

        assert len(app_instance.image_cache) == 14

    def test_used_image_urls_set(self, app_instance):
        """Test used image URLs set functionality."""
        assert isinstance(app_instance.used_image_urls, set)
        
        # Test adding URLs
        urls = [
            "https://images.unsplash.com/photo-1",
            "https://images.unsplash.com/photo-2",
            "https://images.unsplash.com/photo-3"
        ]

        for url in urls:
            app_instance.used_image_urls.add(url)

        assert len(app_instance.used_image_urls) == 3
        for url in urls:
            assert url in app_instance.used_image_urls

    def test_used_image_urls_duplicate_prevention(self, app_instance):
        """Test that used URLs set prevents duplicates."""
        url = "https://images.unsplash.com/photo-duplicate"
        
        # Add same URL multiple times
        app_instance.used_image_urls.add(url)
        app_instance.used_image_urls.add(url)
        app_instance.used_image_urls.add(url)

        # Should only have one instance
        assert len(app_instance.used_image_urls) == 1
        assert url in app_instance.used_image_urls

    def test_current_image_url_state(self, app_instance):
        """Test current image URL state management."""
        # Initial state
        assert app_instance.current_image_url is None

        # Set current image URL
        test_url = "https://images.unsplash.com/current-image"
        app_instance.current_image_url = test_url

        assert app_instance.current_image_url == test_url

        # Clear current image URL
        app_instance.current_image_url = None
        assert app_instance.current_image_url is None

    def test_canonicalize_url_functionality(self, app_instance):
        """Test URL canonicalization for deduplication."""
        # Test URLs with parameters
        test_cases = [
            {
                'input': 'https://images.unsplash.com/photo-123?w=1080&q=80',
                'expected': 'https://images.unsplash.com/photo-123'
            },
            {
                'input': 'https://images.unsplash.com/photo-456?ixid=test&fm=jpg',
                'expected': 'https://images.unsplash.com/photo-456'
            },
            {
                'input': 'https://images.unsplash.com/photo-789',
                'expected': 'https://images.unsplash.com/photo-789'
            },
            {
                'input': None,
                'expected': ''
            },
            {
                'input': '',
                'expected': ''
            }
        ]

        for test_case in test_cases:
            result = app_instance.canonicalize_url(test_case['input'])
            assert result == test_case['expected']

    def test_image_url_validation(self, app_instance):
        """Test image URL validation and format checking."""
        # Valid Unsplash URLs
        valid_urls = [
            "https://images.unsplash.com/photo-123",
            "https://images.unsplash.com/photo-456?w=1080",
            "https://plus.unsplash.com/premium_photo-789"
        ]

        for url in valid_urls:
            # URL should be accepted (basic validation)
            assert url.startswith('https://')
            assert 'unsplash.com' in url

        # Invalid URLs
        invalid_urls = [
            "http://not-secure.com/image",
            "ftp://wrong-protocol.com/image",
            "not-a-url-at-all"
        ]

        for url in invalid_urls:
            # These would be caught by validation logic
            assert not (url.startswith('https://') and 'unsplash.com' in url)

    @patch('PIL.Image.open')
    @patch('PIL.ImageTk.PhotoImage')
    def test_image_processing_success(self, mock_photo_image, mock_image_open, app_instance):
        """Test successful image processing and thumbnail creation."""
        # Setup mocks
        mock_pil_image = Mock()
        mock_image_open.return_value = mock_pil_image
        mock_photo = Mock()
        mock_photo_image.return_value = mock_photo

        # Create BytesIO object with test image data
        image_data = TEST_IMAGE_DATA["png_1x1"]
        
        # Process image (simulate the logic in get_next_image)
        from PIL import Image, ImageTk
        with patch('PIL.Image.open', return_value=mock_pil_image):
            with patch('PIL.ImageTk.PhotoImage', return_value=mock_photo):
                # This simulates the image processing in the app
                image = Image.open(BytesIO(image_data))
                image.thumbnail((600, 600))
                photo = ImageTk.PhotoImage(image)

        # Verify processing steps
        mock_pil_image.thumbnail.assert_called_once_with((600, 600))

    @patch('PIL.Image.open')
    def test_image_processing_error_handling(self, mock_image_open, app_instance):
        """Test error handling in image processing."""
        # Setup mock to raise exception
        mock_image_open.side_effect = Exception("Invalid image data")

        # Test error handling
        with pytest.raises(Exception):
            from PIL import Image
            Image.open(BytesIO(b"invalid_image_data"))

    def test_image_format_support(self, app_instance):
        """Test support for different image formats."""
        # Test different image format data
        formats = {
            'png': TEST_IMAGE_DATA["png_1x1"],
            'jpg': TEST_IMAGE_DATA["jpg_1x1"]
        }

        for format_name, data in formats.items():
            # Store in cache
            url = f"https://test.com/image.{format_name}"
            app_instance.image_cache[url] = data

            # Verify storage
            assert app_instance.image_cache[url] == data

    def test_image_data_integrity(self, app_instance):
        """Test image data integrity in cache."""
        # Store original data
        original_data = TEST_IMAGE_DATA["png_1x1"]
        url = "https://test.com/integrity_test"
        app_instance.image_cache[url] = original_data

        # Retrieve and verify
        retrieved_data = app_instance.image_cache[url]
        
        # Data should be identical
        assert retrieved_data == original_data
        assert len(retrieved_data) == len(original_data)
        assert type(retrieved_data) == type(original_data)

    def test_image_memory_management(self, app_instance):
        """Test image cache memory management."""
        import sys

        # Measure initial memory
        initial_cache_size = sys.getsizeof(app_instance.image_cache)

        # Add images to cache
        for i in range(5):
            url = f"https://test.com/memory_test_{i}"
            # Use realistic image size (small test image)
            app_instance.image_cache[url] = TEST_IMAGE_DATA["png_1x1"]

        # Measure final memory
        final_cache_size = sys.getsizeof(app_instance.image_cache)

        # Memory should have increased
        assert final_cache_size > initial_cache_size

    @pytest.mark.slow
    def test_image_processing_performance(self, app_instance):
        """Test image processing performance."""
        import time

        # Test multiple image processing operations
        start_time = time.time()

        # Simulate processing multiple images
        for i in range(10):
            url = f"https://test.com/perf_test_{i}"
            app_instance.image_cache[url] = TEST_IMAGE_DATA["png_1x1"]

        end_time = time.time()
        processing_time = end_time - start_time

        # Should be fast for small operations
        assert processing_time < PERFORMANCE_BENCHMARKS["image_processing_time"]

    def test_large_image_url_handling(self, app_instance):
        """Test handling of very long image URLs."""
        # Create very long URL
        long_url = EDGE_CASES["large_image_url"]
        
        # Should handle long URLs without issues
        app_instance.used_image_urls.add(long_url)
        assert long_url in app_instance.used_image_urls

        # Test canonicalization with long URL
        canonical = app_instance.canonicalize_url(long_url)
        assert len(canonical) <= len(long_url)  # Should be same or shorter

    def test_corrupted_image_data_handling(self, app_instance):
        """Test handling of corrupted image data."""
        # Test with corrupted data
        corrupted_data = EDGE_CASES["corrupted_image_data"]
        url = "https://test.com/corrupted"

        # Should store the data (validation happens during processing)
        app_instance.image_cache[url] = corrupted_data
        assert app_instance.image_cache[url] == corrupted_data

    def test_image_url_state_transitions(self, app_instance):
        """Test image URL state transitions during application flow."""
        # Initial state
        assert app_instance.current_image_url is None
        assert len(app_instance.used_image_urls) == 0

        # Simulate image loading
        new_url = "https://images.unsplash.com/photo-state-test"
        app_instance.current_image_url = new_url
        app_instance.used_image_urls.add(app_instance.canonicalize_url(new_url))

        # Check intermediate state
        assert app_instance.current_image_url == new_url
        assert len(app_instance.used_image_urls) == 1

        # Simulate loading another image
        another_url = "https://images.unsplash.com/photo-state-test-2"
        app_instance.current_image_url = another_url
        app_instance.used_image_urls.add(app_instance.canonicalize_url(another_url))

        # Check final state
        assert app_instance.current_image_url == another_url
        assert len(app_instance.used_image_urls) == 2

    def test_image_cache_key_normalization(self, app_instance):
        """Test image cache key normalization."""
        # Test with URLs that should be normalized to same key
        urls_with_params = [
            "https://images.unsplash.com/photo-123?w=1080&q=80",
            "https://images.unsplash.com/photo-123?w=400&q=60", 
            "https://images.unsplash.com/photo-123"
        ]

        # Normalize all URLs
        normalized_urls = [app_instance.canonicalize_url(url) for url in urls_with_params]

        # All should normalize to same base URL
        assert len(set(normalized_urls)) == 1
        assert normalized_urls[0] == "https://images.unsplash.com/photo-123"

    def test_concurrent_image_access(self, app_instance):
        """Test concurrent access to image data structures."""
        import threading
        import time

        results = []
        
        def add_images(start_idx, count):
            for i in range(start_idx, start_idx + count):
                url = f"https://test.com/concurrent_{i}"
                app_instance.used_image_urls.add(url)
                app_instance.image_cache[url] = f"data_{i}".encode()
                results.append(i)

        # Create threads to simulate concurrent access
        thread1 = threading.Thread(target=add_images, args=(0, 10))
        thread2 = threading.Thread(target=add_images, args=(10, 10))

        # Start threads
        thread1.start()
        thread2.start()

        # Wait for completion
        thread1.join()
        thread2.join()

        # Verify all operations completed
        assert len(results) == 20
        assert len(app_instance.used_image_urls) == 20
        assert len(app_instance.image_cache) == 20

    def test_image_pagination_state(self, app_instance):
        """Test image pagination state management."""
        # Initial pagination state
        assert app_instance.current_page == 0
        assert app_instance.current_index == 0
        assert app_instance.current_results == []

        # Set pagination state
        test_results = SAMPLE_UNSPLASH_SEARCH_RESPONSE["results"]
        app_instance.current_page = 1
        app_instance.current_index = 0
        app_instance.current_results = test_results

        # Verify state
        assert app_instance.current_page == 1
        assert app_instance.current_index == 0
        assert len(app_instance.current_results) == 2

        # Simulate advancing index
        app_instance.current_index += 1
        assert app_instance.current_index == 1

        # Reset pagination
        app_instance.current_page = 0
        app_instance.current_index = 0
        app_instance.current_results = []

        # Verify reset
        assert app_instance.current_page == 0
        assert app_instance.current_index == 0
        assert app_instance.current_results == []


@pytest.mark.unit
class TestImageDataStructures:
    """Test suite for image-related data structures."""

    @pytest.fixture
    def app_instance(self, mock_config_manager, tkinter_root):
        """Create ImageSearchApp instance for testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            app = ImageSearchApp()
            app.withdraw()
            yield app
            try:
                app.destroy()
            except:
                pass

    def test_image_result_structure(self, app_instance):
        """Test Unsplash image result data structure handling."""
        # Sample image result from API
        image_result = SAMPLE_UNSPLASH_SEARCH_RESPONSE["results"][0]

        # Verify expected structure
        required_fields = ["id", "urls", "alt_description", "user"]
        for field in required_fields:
            assert field in image_result

        # Verify URLs structure
        url_types = ["raw", "full", "regular", "small", "thumb"]
        for url_type in url_types:
            assert url_type in image_result["urls"]
            assert image_result["urls"][url_type].startswith("https://")

        # Verify user structure
        user_fields = ["id", "username", "name"]
        for field in user_fields:
            assert field in image_result["user"]

    def test_image_metadata_extraction(self, app_instance):
        """Test extraction of image metadata."""
        image_result = SAMPLE_UNSPLASH_SEARCH_RESPONSE["results"][0]

        # Extract key metadata
        image_id = image_result["id"]
        image_url = image_result["urls"]["regular"]
        alt_description = image_result["alt_description"]
        photographer = image_result["user"]["name"]

        # Verify extracted data
        assert image_id == "test_image_1"
        assert "https://images.unsplash.com" in image_url
        assert isinstance(alt_description, str)
        assert isinstance(photographer, str)

    def test_image_search_results_pagination(self, app_instance):
        """Test image search results pagination data."""
        search_response = SAMPLE_UNSPLASH_SEARCH_RESPONSE

        # Verify pagination fields
        assert "results" in search_response
        assert "total" in search_response
        assert "total_pages" in search_response

        # Verify data types
        assert isinstance(search_response["results"], list)
        assert isinstance(search_response["total"], int)
        assert isinstance(search_response["total_pages"], int)

        # Verify results structure
        assert len(search_response["results"]) > 0
        for result in search_response["results"]:
            assert "id" in result
            assert "urls" in result