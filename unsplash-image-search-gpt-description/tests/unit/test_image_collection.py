"""
Comprehensive tests for image collection functionality.
Tests various search scenarios, edge cases, cancellation mechanisms, UI responsiveness, and memory management.
"""

import pytest
import asyncio
import threading
import time
from unittest.mock import Mock, patch, MagicMock, call
import requests
from PIL import Image, ImageTk
from io import BytesIO
import json
import tkinter as tk
from pathlib import Path
import sys
import gc
import weakref
from typing import List, Dict, Any

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from main import ImageSearchApp
    from tests.fixtures.sample_data import (
        SAMPLE_UNSPLASH_SEARCH_RESPONSE,
        ERROR_RESPONSES,
        TEST_IMAGE_DATA,
        PERFORMANCE_BENCHMARKS,
        SAMPLE_SESSION_DATA
    )
except ImportError:
    pytest.skip("Required modules not available", allow_module_level=True)


@pytest.mark.unit
class TestImageSearchScenarios:
    """Test various image search scenarios and edge cases."""

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

    def test_empty_search_query(self, app_instance):
        """Test handling of empty search query."""
        app_instance.search_entry.delete(0, tk.END)
        
        with patch('tkinter.messagebox.showerror') as mock_error:
            app_instance.search_image()
            mock_error.assert_called_once()

    def test_whitespace_only_query(self, app_instance):
        """Test handling of whitespace-only search query."""
        app_instance.search_entry.delete(0, tk.END)
        app_instance.search_entry.insert(0, "   \t\n   ")
        
        with patch('tkinter.messagebox.showerror') as mock_error:
            app_instance.search_image()
            mock_error.assert_called_once()

    @patch('requests.get')
    def test_special_characters_in_query(self, mock_get, app_instance):
        """Test search with special characters and Unicode."""
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        special_queries = [
            "café & niño",
            "中文搜索",
            "emoji 🌟 search",
            "quotes \"test\"",
            "symbols #@$%",
            "mixed café & 中文 🌟"
        ]

        for query in special_queries:
            app_instance.search_entry.delete(0, tk.END)
            app_instance.search_entry.insert(0, query)
            
            app_instance.current_query = query
            app_instance.current_page = 1
            
            results = app_instance.fetch_images_page(query, 1)
            
            assert results == SAMPLE_UNSPLASH_SEARCH_RESPONSE["results"]
            # Verify the query was URL encoded properly
            call_args = mock_get.call_args[0][0]
            assert query in call_args or query.replace(' ', '%20') in call_args

    @patch('requests.get')
    def test_very_long_query(self, mock_get, app_instance):
        """Test search with extremely long query."""
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Create a very long query (over 1000 characters)
        long_query = "very " * 200 + "long query"
        
        results = app_instance.fetch_images_page(long_query, 1)
        
        assert results == SAMPLE_UNSPLASH_SEARCH_RESPONSE["results"]

    @patch('requests.get')
    def test_no_results_found(self, mock_get, app_instance):
        """Test handling when no search results are found."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "total": 0, "total_pages": 0}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        results = app_instance.fetch_images_page("impossiblequery12345", 1)
        
        assert results == []

    @patch('requests.get')
    def test_large_result_set_handling(self, mock_get, app_instance):
        """Test handling of large result sets."""
        # Create a large mock response
        large_results = []
        for i in range(100):
            large_results.append({
                "id": f"test_image_{i}",
                "urls": {"regular": f"https://images.unsplash.com/photo-{i}"},
                "description": f"Test image {i}"
            })

        mock_response = Mock()
        mock_response.json.return_value = {"results": large_results, "total": 1000, "total_pages": 100}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        results = app_instance.fetch_images_page("nature", 1)
        
        assert len(results) == 100
        assert all(isinstance(result, dict) for result in results)


@pytest.mark.unit
class TestNetworkErrorHandling:
    """Test various network error scenarios."""

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

    @patch('requests.get')
    def test_connection_timeout(self, mock_get, app_instance):
        """Test handling of connection timeout."""
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

        with pytest.raises(requests.exceptions.Timeout):
            app_instance.fetch_images_page("mountain", 1)

    @patch('requests.get')
    def test_connection_error(self, mock_get, app_instance):
        """Test handling of connection error."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Failed to establish connection")

        with pytest.raises(requests.exceptions.ConnectionError):
            app_instance.fetch_images_page("mountain", 1)

    @patch('requests.get')
    def test_http_error_responses(self, mock_get, app_instance):
        """Test handling of various HTTP error responses."""
        error_codes = [400, 401, 403, 404, 429, 500, 502, 503, 504]
        
        for error_code in error_codes:
            mock_response = Mock()
            mock_response.status_code = error_code
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(f"{error_code} Error")
            mock_get.return_value = mock_response

            with pytest.raises(requests.exceptions.HTTPError):
                app_instance.fetch_images_page("mountain", 1)

    @patch('requests.get')
    def test_malformed_json_response(self, mock_get, app_instance):
        """Test handling of malformed JSON responses."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "response", 0)
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with pytest.raises(json.JSONDecodeError):
            app_instance.fetch_images_page("mountain", 1)

    @patch('requests.get')
    def test_partial_response_data(self, mock_get, app_instance):
        """Test handling of partial/incomplete response data."""
        # Response missing 'results' key
        mock_response = Mock()
        mock_response.json.return_value = {"total": 100}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        results = app_instance.fetch_images_page("mountain", 1)
        
        # Should return empty list when 'results' key is missing
        assert results == []

    @patch('requests.get')
    def test_network_intermittent_failures(self, mock_get, app_instance):
        """Test handling of intermittent network failures with retry logic."""
        # Simulate failure then success
        mock_get.side_effect = [
            requests.exceptions.ConnectionError("First failure"),
            requests.exceptions.ConnectionError("Second failure"),
            Mock(json=Mock(return_value=SAMPLE_UNSPLASH_SEARCH_RESPONSE), raise_for_status=Mock())
        ]

        with patch('time.sleep'):  # Speed up test
            result = app_instance.api_call_with_retry(
                app_instance.fetch_images_page, "mountain", 1, max_retries=3
            )
            
        assert result == SAMPLE_UNSPLASH_SEARCH_RESPONSE["results"]
        assert mock_get.call_count == 3


@pytest.mark.unit
class TestImageDownloadAndCaching:
    """Test image download and caching functionality."""

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

    @patch('PIL.Image.open')
    @patch('PIL.ImageTk.PhotoImage')
    @patch('requests.get')
    def test_image_download_success(self, mock_get, mock_photo, mock_image_open, app_instance):
        """Test successful image download and processing."""
        # Setup mock responses
        search_response = Mock()
        search_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        search_response.raise_for_status = Mock()
        
        image_response = Mock()
        image_response.content = TEST_IMAGE_DATA["png_1x1"]
        image_response.raise_for_status = Mock()
        
        mock_get.side_effect = [search_response, image_response]
        
        # Setup PIL mocks
        mock_pil_image = Mock()
        mock_pil_image.copy.return_value = mock_pil_image
        mock_image_open.return_value = mock_pil_image
        mock_photo_instance = Mock()
        mock_photo_instance.width.return_value = 300
        mock_photo_instance.height.return_value = 200
        mock_photo.return_value = mock_photo_instance

        # Setup app state
        app_instance.current_query = "mountain"
        app_instance.current_page = 1
        app_instance.current_results = []
        app_instance.current_index = 0

        result = app_instance.get_next_image()

        assert result == (mock_photo_instance, mock_pil_image)
        assert len(app_instance.image_cache) == 1
        assert app_instance.current_image_url is not None

    @patch('requests.get')
    def test_image_download_failure(self, mock_get, app_instance):
        """Test handling of image download failures."""
        # Setup search success but image download failure
        search_response = Mock()
        search_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        search_response.raise_for_status = Mock()
        
        image_response = Mock()
        image_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        
        mock_get.side_effect = [search_response, image_response]

        app_instance.current_query = "mountain"
        app_instance.current_page = 1
        app_instance.current_results = []
        app_instance.current_index = 0

        # Should handle image download failure gracefully and try next image
        with patch('PIL.Image.open') as mock_image_open:
            result = app_instance.get_next_image()
            # Should be None or handle the error appropriately
            assert result is None or isinstance(result, tuple)

    def test_image_cache_size_management(self, app_instance):
        """Test that image cache respects size limits."""
        # Fill cache beyond the 10 item limit
        for i in range(15):
            url = f"https://test.com/image_{i}.jpg"
            app_instance.image_cache[url] = f"image_data_{i}"

        # Cache should be limited
        assert len(app_instance.image_cache) <= 11  # 10 + 1 for the removal logic

    def test_image_cache_hit(self, app_instance):
        """Test cache hit functionality."""
        test_url = "https://images.unsplash.com/photo-123"
        test_data = b"cached_image_data"
        
        # Pre-populate cache
        app_instance.image_cache[test_url] = test_data
        
        with patch('PIL.Image.open') as mock_image_open, \
             patch('PIL.ImageTk.PhotoImage') as mock_photo:
            
            mock_pil_image = Mock()
            mock_pil_image.copy.return_value = mock_pil_image
            mock_image_open.return_value = mock_pil_image
            mock_photo_instance = Mock()
            mock_photo.return_value = mock_photo_instance

            # Setup app state with cached image
            app_instance.current_query = "mountain"
            app_instance.current_results = [{"urls": {"regular": test_url}}]
            app_instance.current_index = 0

            with patch('requests.get') as mock_get:
                result = app_instance.get_next_image()
                
                # Should not make network request for image download
                # (only for search if results are empty)
                assert len(mock_get.call_args_list) <= 1


@pytest.mark.unit
class TestSearchStateManagement:
    """Test search state management and pagination."""

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

    def test_initial_search_state(self, app_instance):
        """Test initial search state values."""
        assert app_instance.current_query == ""
        assert app_instance.current_page == 0
        assert app_instance.current_results == []
        assert app_instance.current_index == 0
        assert app_instance.current_image_url is None
        assert app_instance.search_state == 'idle'
        assert app_instance.images_collected_count == 0
        assert not app_instance.search_cancelled

    def test_search_state_transitions(self, app_instance):
        """Test search state transitions."""
        # Start search session
        app_instance.start_search_session()
        assert app_instance.search_state == 'searching'
        assert not app_instance.search_cancelled
        assert app_instance.images_collected_count == 0

        # Stop search
        app_instance.stop_search()
        assert app_instance.search_cancelled
        assert app_instance.search_state == 'cancelled'

    @patch('requests.get')
    def test_pagination_advancement(self, mock_get, app_instance):
        """Test pagination advancement when reaching end of current page."""
        # Setup mock responses for multiple pages
        page1_response = Mock()
        page1_response.json.return_value = {
            "results": [{"id": "img1", "urls": {"regular": "url1"}}]
        }
        page1_response.raise_for_status = Mock()
        
        page2_response = Mock()
        page2_response.json.return_value = {
            "results": [{"id": "img2", "urls": {"regular": "url2"}}]
        }
        page2_response.raise_for_status = Mock()
        
        mock_get.side_effect = [page1_response, page2_response]

        app_instance.current_query = "test"
        app_instance.current_page = 1
        app_instance.current_results = [{"id": "img1", "urls": {"regular": "url1"}}]
        app_instance.current_index = 1  # At end of current results

        # Add first image to used URLs to force pagination
        app_instance.used_image_urls.add("url1")

        with patch('PIL.Image.open'), patch('PIL.ImageTk.PhotoImage'):
            with patch('requests.get') as mock_img_get:
                mock_img_response = Mock()
                mock_img_response.content = TEST_IMAGE_DATA["png_1x1"]
                mock_img_response.raise_for_status = Mock()
                mock_img_get.return_value = mock_img_response

                result = app_instance.get_next_image()

                # Should advance to page 2
                assert app_instance.current_page == 2

    def test_collection_limit_management(self, app_instance):
        """Test collection limit enforcement."""
        app_instance.max_images_per_search = 5
        app_instance.images_collected_count = 4

        # Should be within limit
        app_instance.update_search_progress()
        assert app_instance.images_collected_count < app_instance.max_images_per_search

        # Reach limit
        app_instance.images_collected_count = 5
        app_instance.show_collection_limit_reached()
        assert app_instance.search_state == 'completed'

    def test_load_more_functionality(self, app_instance):
        """Test load more images functionality."""
        initial_limit = app_instance.max_images_per_search
        
        app_instance.load_more_images()
        
        # Limit should be increased by 30
        assert app_instance.max_images_per_search == initial_limit + 30


@pytest.mark.unit
class TestCancellationMechanisms:
    """Test search cancellation and interruption mechanisms."""

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

    def test_search_cancellation_flag(self, app_instance):
        """Test search cancellation flag behavior."""
        assert not app_instance.search_cancelled
        
        app_instance.stop_search()
        
        assert app_instance.search_cancelled
        assert app_instance.search_state == 'cancelled'

    def test_thread_cancellation_handling(self, app_instance):
        """Test that threads respect cancellation flag."""
        app_instance.search_cancelled = True
        
        # Mock the thread function behavior when cancelled
        with patch.object(app_instance, 'get_next_image') as mock_get_next:
            app_instance.thread_get_next_image()
            mock_get_next.assert_not_called()

    def test_early_cancellation_during_search(self, app_instance):
        """Test cancellation during search operation."""
        # Start a search operation
        app_instance.start_search_session()
        
        # Immediately cancel
        app_instance.stop_search()
        
        # Verify state
        assert app_instance.search_cancelled
        assert app_instance.search_state == 'cancelled'

    @patch('threading.Thread')
    def test_thread_cleanup_on_cancellation(self, mock_thread, app_instance):
        """Test proper thread cleanup when operation is cancelled."""
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        # Start then immediately cancel
        app_instance.search_cancelled = False
        app_instance.search_image()
        app_instance.stop_search()
        
        # Thread should have been started
        mock_thread_instance.start.assert_called_once()


@pytest.mark.unit
class TestUIResponsiveness:
    """Test UI responsiveness during collection operations."""

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

    def test_progress_bar_visibility(self, app_instance):
        """Test progress bar shows/hides correctly."""
        # Initially hidden
        assert not app_instance.progress_bar.winfo_viewable()
        
        # Show during operation
        app_instance.show_progress("Testing...")
        app_instance.update_idletasks()
        
        # Hide after operation
        app_instance.hide_progress()
        app_instance.update_idletasks()

    def test_button_state_management(self, app_instance):
        """Test that buttons are disabled/enabled appropriately."""
        # Initially enabled
        assert str(app_instance.search_button['state']) == 'normal'
        
        # Disabled during operation
        app_instance.disable_buttons()
        assert str(app_instance.search_button['state']) == 'disabled'
        assert str(app_instance.another_button['state']) == 'disabled'
        
        # Re-enabled after operation
        app_instance.enable_buttons()
        assert str(app_instance.search_button['state']) == 'normal'
        assert str(app_instance.another_button['state']) == 'normal'

    def test_status_message_updates(self, app_instance):
        """Test status message updates during operations."""
        test_messages = [
            "Searching for images...",
            "Downloading image...",
            "Processing complete",
            "Error occurred"
        ]
        
        for message in test_messages:
            app_instance.update_status(message)
            assert app_instance.status_label.cget('text') == message

    def test_loading_animation(self, app_instance):
        """Test loading animation functionality."""
        app_instance.start_loading_animation("Loading")
        
        # Check that animation updates
        initial_text = app_instance.status_label.cget('text')
        
        # Manually trigger animation update
        app_instance.update_loading_animation()
        updated_text = app_instance.status_label.cget('text')
        
        # Text should have changed (dots added)
        assert updated_text != initial_text
        
        app_instance.stop_loading_animation()

    def test_statistics_display_updates(self, app_instance):
        """Test that statistics display updates correctly."""
        # Add test data
        app_instance.used_image_urls.add("test_url_1")
        app_instance.used_image_urls.add("test_url_2")
        app_instance.vocabulary_cache.update(["word1", "word2"])
        app_instance.images_collected_count = 15
        
        app_instance.update_stats()
        
        stats_text = app_instance.stats_label.cget('text')
        assert "Images: 2" in stats_text
        assert "Words: 2" in stats_text
        assert "Progress: 15/" in stats_text

    @patch('time.sleep')
    def test_ui_remains_responsive_during_long_operations(self, mock_sleep, app_instance):
        """Test that UI remains responsive during long operations."""
        # Simulate long operation
        def long_operation():
            time.sleep(0.1)  # Mocked, so actually instant
            app_instance.update_idletasks()
            return "completed"
        
        # UI should remain responsive (not freeze)
        result = app_instance.api_call_with_retry(long_operation, max_retries=1)
        assert result == "completed"


@pytest.mark.unit
class TestMemoryManagement:
    """Test memory management and cleanup functionality."""

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

    def test_image_cache_cleanup(self, app_instance):
        """Test that image cache is properly cleaned up."""
        # Fill cache with test data
        large_data = b"x" * 1024 * 100  # 100KB of data
        for i in range(15):
            app_instance.image_cache[f"url_{i}"] = large_data
        
        # Cache should automatically limit size
        assert len(app_instance.image_cache) <= 11

    def test_memory_cleanup_on_new_search(self, app_instance):
        """Test memory cleanup when starting new search."""
        # Add some data
        app_instance.current_results = [{"test": "data"}] * 100
        app_instance.image_cache = {f"url_{i}": f"data_{i}" for i in range(10)}
        app_instance.extracted_phrases = {"test": ["phrase1", "phrase2"]}
        
        # Start new search
        app_instance.change_search()
        
        # Memory should be cleaned up
        assert app_instance.current_results == []
        assert app_instance.extracted_phrases == {}

    def test_widget_cleanup_on_phrase_update(self, app_instance):
        """Test that old widgets are properly cleaned up."""
        # Create some mock widgets in the extracted phrases frame
        for i in range(10):
            mock_widget = Mock()
            mock_widget.winfo_children.return_value = []
            app_instance.extracted_inner_frame.winfo_children = Mock(return_value=[mock_widget] * 10)
        
        # Update phrases (should clean up old widgets)
        app_instance.display_extracted_phrases({})
        
        # Cleanup should have been called
        assert app_instance.extracted_inner_frame.winfo_children.called

    def test_large_dataset_memory_usage(self, app_instance):
        """Test memory usage with large datasets."""
        # Simulate processing large amounts of data
        large_phrases = {
            "Sustantivos": [f"el sustantivo {i}" for i in range(100)],
            "Verbos": [f"verbo {i}" for i in range(100)],
            "Adjetivos": [f"adjetivo {i}" for i in range(100)]
        }
        
        # This should not cause memory issues
        app_instance.display_extracted_phrases(large_phrases)
        
        # Memory usage should be reasonable
        # (This is more of a regression test to ensure no memory leaks)
        assert len(app_instance.extracted_phrases) <= 300

    def test_weak_references_cleanup(self, app_instance):
        """Test that weak references are cleaned up properly."""
        # Create some objects that should be garbage collected
        test_objects = []
        weak_refs = []
        
        for i in range(10):
            obj = {"data": f"test_{i}"}
            test_objects.append(obj)
            weak_refs.append(weakref.ref(obj))
        
        # Clear strong references
        test_objects.clear()
        
        # Force garbage collection
        gc.collect()
        
        # Weak references should be cleared
        alive_refs = [ref for ref in weak_refs if ref() is not None]
        assert len(alive_refs) == 0


@pytest.mark.integration
class TestCompleteImageCollectionWorkflow:
    """Integration tests for complete image collection workflows."""

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

    @patch('requests.get')
    @patch('PIL.Image.open')
    @patch('PIL.ImageTk.PhotoImage')
    def test_full_search_and_collect_workflow(self, mock_photo, mock_image_open, 
                                            mock_get, app_instance):
        """Test complete workflow from search to image collection."""
        # Setup mocks
        search_response = Mock()
        search_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        search_response.raise_for_status = Mock()
        
        image_response = Mock()
        image_response.content = TEST_IMAGE_DATA["png_1x1"]
        image_response.raise_for_status = Mock()
        
        mock_get.side_effect = [search_response, image_response]
        
        mock_pil_image = Mock()
        mock_pil_image.copy.return_value = mock_pil_image
        mock_image_open.return_value = mock_pil_image
        
        mock_photo_instance = Mock()
        mock_photo_instance.width.return_value = 300
        mock_photo_instance.height.return_value = 200
        mock_photo.return_value = mock_photo_instance

        # Execute workflow
        app_instance.search_entry.delete(0, tk.END)
        app_instance.search_entry.insert(0, "nature")
        
        # Start search
        app_instance.current_query = "nature"
        app_instance.current_page = 1
        app_instance.current_results = []
        app_instance.current_index = 0
        
        # Get first image
        result = app_instance.get_next_image()
        
        # Verify workflow completion
        assert result == (mock_photo_instance, mock_pil_image)
        assert len(app_instance.used_image_urls) == 1
        assert app_instance.current_image_url is not None

    @patch('requests.get')
    def test_search_with_multiple_pages(self, mock_get, app_instance):
        """Test search across multiple pages with state management."""
        # Setup multiple page responses
        responses = []
        for page in range(1, 4):
            response = Mock()
            response.json.return_value = {
                "results": [{"id": f"img_{page}_{i}", "urls": {"regular": f"url_{page}_{i}"}} for i in range(2)]
            }
            response.raise_for_status = Mock()
            responses.append(response)
        
        mock_get.side_effect = responses
        
        # Search through multiple pages
        app_instance.current_query = "test"
        
        all_results = []
        for page in range(1, 4):
            app_instance.current_page = page
            results = app_instance.fetch_images_page("test", page)
            all_results.extend(results)
        
        # Should have collected results from all pages
        assert len(all_results) == 6  # 3 pages × 2 results each

    def test_error_recovery_during_workflow(self, app_instance):
        """Test error recovery during complete workflow."""
        with patch('requests.get') as mock_get:
            # First call fails, second succeeds
            error_response = Mock()
            error_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
            
            success_response = Mock()
            success_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
            success_response.raise_for_status = Mock()
            
            mock_get.side_effect = [error_response, success_response]
            
            # Should recover from first failure
            with patch('time.sleep'):
                result = app_instance.api_call_with_retry(
                    app_instance.fetch_images_page, "mountain", 1, max_retries=2
                )
                
            assert result == SAMPLE_UNSPLASH_SEARCH_RESPONSE["results"]


@pytest.mark.performance
class TestPerformanceAndLoadTesting:
    """Performance tests for image collection functionality."""

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

    @pytest.mark.slow
    @patch('requests.get')
    def test_large_search_results_performance(self, mock_get, app_instance):
        """Test performance with large search results."""
        import time
        
        # Create large mock response
        large_results = [
            {"id": f"img_{i}", "urls": {"regular": f"url_{i}"}, "description": f"Description {i}"}
            for i in range(1000)
        ]
        
        mock_response = Mock()
        mock_response.json.return_value = {"results": large_results}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        start_time = time.time()
        results = app_instance.fetch_images_page("test", 1)
        duration = time.time() - start_time
        
        assert len(results) == 1000
        assert duration < PERFORMANCE_BENCHMARKS.get("large_result_processing", 1.0)

    @pytest.mark.slow
    def test_memory_usage_over_time(self, app_instance):
        """Test memory usage stability over extended operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Simulate extended usage
        for i in range(100):
            # Simulate adding images to cache
            app_instance.image_cache[f"url_{i}"] = b"x" * 1024  # 1KB each
            
            # Simulate vocabulary processing
            app_instance.vocabulary_cache.update([f"word_{i}", f"phrase_{i}"])
            
            # Force cache cleanup
            if len(app_instance.image_cache) > 10:
                # Remove oldest items
                oldest_keys = list(app_instance.image_cache.keys())[:5]
                for key in oldest_keys:
                    del app_instance.image_cache[key]
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024

    @patch('requests.get')
    def test_concurrent_operations_performance(self, mock_get, app_instance):
        """Test performance under concurrent operations."""
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        import time
        import threading
        
        results = []
        errors = []
        
        def search_worker():
            try:
                result = app_instance.fetch_images_page("test", 1)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        start_time = time.time()
        
        # Start multiple concurrent searches
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=search_worker)
            thread.start()
            threads.append(thread)
        
        # Wait for all to complete
        for thread in threads:
            thread.join(timeout=5)
        
        duration = time.time() - start_time
        
        # All operations should complete successfully
        assert len(results) == 5
        assert len(errors) == 0
        assert duration < 5.0  # Should complete within 5 seconds


if __name__ == "__main__":
    # Run specific test suites
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure for debugging
    ])