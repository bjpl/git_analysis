"""
Integration tests for API workflows.
Tests complete workflows involving Unsplash and OpenAI API interactions.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import threading
import time

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from main import ImageSearchApp
from tests.fixtures.sample_data import (
    SAMPLE_UNSPLASH_SEARCH_RESPONSE,
    SAMPLE_OPENAI_DESCRIPTION_RESPONSES,
    SAMPLE_OPENAI_EXTRACTION_RESPONSES,
    SAMPLE_TRANSLATION_RESPONSES,
    TEST_IMAGE_DATA,
    ERROR_RESPONSES,
    PERFORMANCE_BENCHMARKS
)


@pytest.mark.integration
class TestAPIWorkflow:
    """Test suite for complete API workflows and interactions."""

    @pytest.fixture
    def app_instance(self, mock_config_manager, tkinter_root):
        """Create ImageSearchApp instance for integration testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            app = ImageSearchApp()
            app.withdraw()
            yield app
            try:
                app.destroy()
            except:
                pass

    def test_complete_search_to_description_workflow(self, app_instance, mock_requests_get, mock_openai_client):
        """Test complete workflow from image search to description generation."""
        # Setup mocks for Unsplash API
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response.raise_for_status = Mock()
        
        # Mock image download
        mock_img_response = Mock()
        mock_img_response.content = TEST_IMAGE_DATA["png_1x1"]
        mock_img_response.raise_for_status = Mock()
        
        mock_requests_get.side_effect = [mock_response, mock_img_response]

        # Setup mocks for OpenAI API
        mock_description_response = Mock()
        mock_description_response.choices = [Mock()]
        mock_description_response.choices[0].message.content = SAMPLE_OPENAI_DESCRIPTION_RESPONSES["mountain_landscape"]["choices"][0]["message"]["content"]
        
        mock_openai_client.chat.completions.create.return_value = mock_description_response
        app_instance.openai_client = mock_openai_client

        # Setup GUI mocks
        app_instance.search_entry = Mock()
        app_instance.search_entry.get.return_value = "mountain landscape"
        app_instance.note_text = Mock()
        app_instance.note_text.get.return_value = "Beautiful mountain scene"

        # Step 1: Search for images
        query = "mountain landscape"
        results = app_instance.fetch_images_page(query, 1)
        
        assert len(results) == 2
        assert results[0]["id"] == "test_image_1"

        # Step 2: Process image (simulate get_next_image functionality)
        app_instance.current_query = query
        app_instance.current_page = 1
        app_instance.current_results = results
        app_instance.current_index = 0
        
        # Mock PIL operations for image processing
        with patch('PIL.Image.open') as mock_image_open, \
             patch('PIL.ImageTk.PhotoImage') as mock_photo_image:
            
            mock_pil_image = Mock()
            mock_image_open.return_value = mock_pil_image
            mock_photo = Mock()
            mock_photo_image.return_value = mock_photo

            # Get next image (this would normally be called by UI)
            photo = app_instance.get_next_image()
            assert photo == mock_photo
            assert app_instance.current_image_url is not None

        # Step 3: Generate description
        app_instance.thread_generate_description(query, "Beautiful mountain scene")

        # Verify OpenAI API was called correctly
        mock_openai_client.chat.completions.create.assert_called()
        call_args = mock_openai_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "gpt-4o-mini"
        
        # Verify log entry was created and updated
        assert len(app_instance.log_entries) > 0
        last_entry = app_instance.log_entries[-1]
        assert last_entry["query"] == query
        assert last_entry["generated_description"] == SAMPLE_OPENAI_DESCRIPTION_RESPONSES["mountain_landscape"]["choices"][0]["message"]["content"]

    def test_complete_description_to_vocabulary_workflow(self, app_instance, mock_openai_client, test_data_dir):
        """Test complete workflow from description generation to vocabulary extraction and translation."""
        # Setup CSV file
        csv_file = test_data_dir / "workflow_vocabulary.csv"
        app_instance.CSV_TARGET_WORDS = csv_file

        # Setup OpenAI mocks for extraction
        mock_extraction_response = Mock()
        mock_extraction_response.choices = [Mock()]
        mock_extraction_response.choices[0].message.content = SAMPLE_OPENAI_EXTRACTION_RESPONSES["mountain_landscape"]["choices"][0]["message"]["content"]
        
        # Setup OpenAI mocks for translation
        mock_translation_response = Mock()
        mock_translation_response.choices = [Mock()]
        mock_translation_response.choices[0].message.content = "mountain landscape"
        
        # Configure mock to return different responses based on call
        mock_openai_client.chat.completions.create.side_effect = [
            mock_extraction_response,
            mock_translation_response
        ]
        app_instance.openai_client = mock_openai_client

        # Setup GUI mocks
        app_instance.description_text = Mock()
        app_instance.description_text.get.return_value = "Esta imagen muestra un paisaje montañoso espectacular..."
        app_instance.target_listbox = Mock()
        app_instance.update_target_list_display = Mock()
        app_instance.current_query = "mountain"
        app_instance.current_image_url = "https://test.com/image"

        # Step 1: Extract phrases from description
        description = "Esta imagen muestra un paisaje montañoso espectacular con picos nevados..."
        app_instance.extract_phrases_from_description(description)

        # Verify extraction API call
        assert mock_openai_client.chat.completions.create.call_count >= 1

        # Step 2: Add target phrase (this will trigger translation)
        phrase = "paisaje montañoso"
        app_instance.add_target_phrase(phrase)

        # Verify translation API call
        assert mock_openai_client.chat.completions.create.call_count >= 2

        # Verify phrase was added to target phrases
        assert any("mountain landscape" in tp for tp in app_instance.target_phrases)

        # Verify vocabulary was cached
        assert phrase in app_instance.vocabulary_cache

        # Verify CSV was written
        assert csv_file.exists()

    def test_error_recovery_workflow(self, app_instance, mock_requests_get, mock_openai_client):
        """Test workflow error recovery and retry mechanisms."""
        # Setup initial failure then success for Unsplash
        mock_response_fail = Mock()
        mock_response_fail.side_effect = Exception("Network error")
        
        mock_response_success = Mock()
        mock_response_success.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response_success.raise_for_status = Mock()
        
        mock_requests_get.side_effect = [Exception("First failure"), mock_response_success]

        # Test retry mechanism
        with patch('time.sleep'):  # Speed up test
            try:
                # First call should fail
                app_instance.fetch_images_page("mountain", 1)
            except Exception:
                pass  # Expected failure
            
            # Second call should succeed with retry logic
            results = app_instance.api_call_with_retry(
                lambda: app_instance.fetch_images_page("mountain", 1),
                max_retries=2
            )
            
            assert len(results) == 2

    def test_rate_limit_handling_workflow(self, app_instance, mock_requests_get, mock_openai_client):
        """Test rate limit handling across different APIs."""
        # Test Unsplash rate limit
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("rate_limit")
        mock_requests_get.return_value = mock_response

        with patch('time.sleep') as mock_sleep:
            try:
                app_instance.api_call_with_retry(
                    lambda: app_instance.fetch_images_page("mountain", 1),
                    max_retries=2
                )
            except:
                pass  # Expected to fail after retries

            # Should have slept for rate limit handling
            mock_sleep.assert_called()

        # Test OpenAI rate limit
        mock_openai_client.chat.completions.create.side_effect = Exception("rate_limit exceeded")
        app_instance.openai_client = mock_openai_client

        with patch('time.sleep'):
            result = app_instance.translate_word("test word")
            # Should return empty string on consistent failure
            assert result == ""

    def test_concurrent_api_calls_workflow(self, app_instance, mock_requests_get, mock_openai_client):
        """Test handling of concurrent API calls."""
        # Setup mocks
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        mock_openai_response = Mock()
        mock_openai_response.choices = [Mock()]
        mock_openai_response.choices[0].message.content = "translated"
        mock_openai_client.chat.completions.create.return_value = mock_openai_response
        app_instance.openai_client = mock_openai_client

        results = []
        errors = []

        def make_api_calls(thread_id):
            try:
                # Unsplash API call
                unsplash_result = app_instance.fetch_images_page(f"query_{thread_id}", 1)
                
                # OpenAI API call
                openai_result = app_instance.translate_word(f"palabra_{thread_id}")
                
                results.append({
                    'thread_id': thread_id,
                    'unsplash_count': len(unsplash_result),
                    'translation': openai_result
                })
            except Exception as e:
                errors.append(f"Thread {thread_id}: {str(e)}")

        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=make_api_calls, args=(i,))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify results
        assert len(errors) == 0, f"Concurrent API errors: {errors}"
        assert len(results) == 3
        for result in results:
            assert result['unsplash_count'] == 2  # From sample response
            assert result['translation'] == "translated"

    def test_data_consistency_across_workflow(self, app_instance, mock_requests_get, mock_openai_client, test_data_dir):
        """Test data consistency across complete workflow."""
        # Setup test files
        csv_file = test_data_dir / "consistency_vocabulary.csv"
        log_file = test_data_dir / "consistency_session.json"
        app_instance.CSV_TARGET_WORDS = csv_file
        app_instance.LOG_FILENAME = log_file

        # Setup mocks
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response.raise_for_status = Mock()
        
        mock_img_response = Mock()
        mock_img_response.content = TEST_IMAGE_DATA["png_1x1"]
        mock_img_response.raise_for_status = Mock()
        
        mock_requests_get.side_effect = [mock_response, mock_img_response]

        # Setup OpenAI responses
        description_response = Mock()
        description_response.choices = [Mock()]
        description_response.choices[0].message.content = "Descripción de la imagen"
        
        extraction_response = Mock()
        extraction_response.choices = [Mock()]
        extraction_response.choices[0].message.content = json.dumps({
            "Sustantivos": ["la imagen"],
            "Verbos": ["muestra"],
            "Adjetivos": ["hermosa"],
            "Adverbios": [],
            "Frases clave": ["imagen hermosa"]
        })
        
        translation_response = Mock()
        translation_response.choices = [Mock()]
        translation_response.choices[0].message.content = "beautiful image"

        mock_openai_client.chat.completions.create.side_effect = [
            description_response,
            extraction_response,
            translation_response
        ]
        app_instance.openai_client = mock_openai_client

        # Setup GUI mocks
        app_instance.search_entry = Mock()
        app_instance.search_entry.get.return_value = "test query"
        app_instance.note_text = Mock()
        app_instance.note_text.get.return_value = "test note"
        app_instance.description_text = Mock()
        app_instance.description_text.get.return_value = "Descripción de la imagen"
        app_instance.target_listbox = Mock()
        app_instance.update_target_list_display = Mock()

        # Execute complete workflow
        query = "test query"
        app_instance.current_query = query

        # Step 1: Get images
        with patch('PIL.Image.open'), patch('PIL.ImageTk.PhotoImage'):
            app_instance.current_results = app_instance.fetch_images_page(query, 1)
            photo = app_instance.get_next_image()

        # Step 2: Generate description
        app_instance.thread_generate_description(query, "test note")

        # Step 3: Extract and translate
        app_instance.extract_phrases_from_description("Descripción de la imagen")
        app_instance.add_target_phrase("imagen hermosa")

        # Step 4: Save session
        app_instance.save_session_to_json()

        # Verify data consistency across all storage mechanisms
        
        # Check log entries
        assert len(app_instance.log_entries) > 0
        log_entry = app_instance.log_entries[-1]
        assert log_entry["query"] == query
        assert log_entry["generated_description"] == "Descripción de la imagen"

        # Check vocabulary
        assert "imagen hermosa" in app_instance.vocabulary_cache
        assert any("beautiful image" in phrase for phrase in app_instance.target_phrases)

        # Check saved session file
        assert log_file.exists()
        with open(log_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        assert "sessions" in session_data
        assert len(session_data["sessions"]) > 0
        saved_entry = session_data["sessions"][-1]["entries"][-1]
        assert saved_entry["query"] == query

        # Check vocabulary CSV
        assert csv_file.exists()
        import csv
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) > 0
        vocab_row = rows[-1]
        assert vocab_row["Spanish"] == "imagen hermosa"
        assert vocab_row["English"] == "beautiful image"
        assert vocab_row["Search Query"] == query

    @pytest.mark.slow
    def test_workflow_performance_benchmarks(self, app_instance, mock_requests_get, mock_openai_client):
        """Test that complete workflows meet performance benchmarks."""
        # Setup fast mocks
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        mock_openai_response = Mock()
        mock_openai_response.choices = [Mock()]
        mock_openai_response.choices[0].message.content = "Quick response"
        mock_openai_client.chat.completions.create.return_value = mock_openai_response
        app_instance.openai_client = mock_openai_client

        # Measure workflow performance
        start_time = time.time()

        # Execute workflow steps
        results = app_instance.fetch_images_page("performance test", 1)
        translation = app_instance.translate_word("test word")

        end_time = time.time()
        total_time = end_time - start_time

        # Verify performance
        assert len(results) > 0
        assert translation == "Quick response"
        assert total_time < PERFORMANCE_BENCHMARKS["api_call_timeout"]

    def test_workflow_memory_management(self, app_instance, mock_requests_get, mock_openai_client):
        """Test memory management during intensive workflows."""
        import sys
        import gc

        # Setup mocks
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        mock_openai_response = Mock()
        mock_openai_response.choices = [Mock()]
        mock_openai_response.choices[0].message.content = "Response"
        mock_openai_client.chat.completions.create.return_value = mock_openai_response
        app_instance.openai_client = mock_openai_client

        # Measure initial memory
        gc.collect()
        initial_memory = sys.getsizeof(app_instance.image_cache) + sys.getsizeof(app_instance.vocabulary_cache)

        # Execute multiple workflow iterations
        for i in range(20):
            # Simulate workflow
            results = app_instance.fetch_images_page(f"query_{i}", 1)
            translation = app_instance.translate_word(f"palabra_{i}")
            
            # Add to caches
            url = f"https://test.com/memory_{i}"
            app_instance.image_cache[url] = TEST_IMAGE_DATA["png_1x1"]
            app_instance.vocabulary_cache.add(f"word_{i}")

        # Measure final memory
        gc.collect()
        final_memory = sys.getsizeof(app_instance.image_cache) + sys.getsizeof(app_instance.vocabulary_cache)

        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable
        assert memory_growth > 0  # Should have grown
        assert memory_growth < PERFORMANCE_BENCHMARKS["memory_usage_mb"] * 1024 * 1024  # Should not exceed benchmark


@pytest.mark.integration
class TestAPIErrorHandling:
    """Test suite for API error handling in workflows."""

    @pytest.fixture
    def app_instance(self, mock_config_manager, tkinter_root):
        """Create ImageSearchApp instance for error handling testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            app = ImageSearchApp()
            app.withdraw()
            yield app
            try:
                app.destroy()
            except:
                pass

    def test_unsplash_api_error_recovery(self, app_instance, mock_requests_get):
        """Test recovery from Unsplash API errors."""
        # Test different error scenarios
        error_scenarios = [
            Exception("Network timeout"),
            Exception("Connection refused"),
            Exception("403 Forbidden"),
            Exception("429 Too Many Requests"),
            Exception("500 Internal Server Error")
        ]

        for error in error_scenarios:
            mock_requests_get.side_effect = error
            
            with pytest.raises(Exception):
                app_instance.fetch_images_page("test", 1)

    def test_openai_api_error_recovery(self, app_instance, mock_openai_client):
        """Test recovery from OpenAI API errors."""
        error_scenarios = [
            Exception("api_key invalid"),
            Exception("rate_limit exceeded"),
            Exception("insufficient_quota"),
            Exception("model_not_found"),
            Exception("Network error")
        ]

        app_instance.openai_client = mock_openai_client

        for error in error_scenarios:
            mock_openai_client.chat.completions.create.side_effect = error
            
            # Should return empty string on error
            result = app_instance.translate_word("test")
            assert result == ""

    def test_mixed_api_error_scenarios(self, app_instance, mock_requests_get, mock_openai_client):
        """Test scenarios where some APIs fail and others succeed."""
        # Unsplash fails, OpenAI succeeds
        mock_requests_get.side_effect = Exception("Unsplash error")
        
        mock_openai_response = Mock()
        mock_openai_response.choices = [Mock()]
        mock_openai_response.choices[0].message.content = "Translation success"
        mock_openai_client.chat.completions.create.return_value = mock_openai_response
        app_instance.openai_client = mock_openai_client

        # Unsplash should fail
        with pytest.raises(Exception):
            app_instance.fetch_images_page("test", 1)

        # OpenAI should succeed
        result = app_instance.translate_word("test")
        assert result == "Translation success"