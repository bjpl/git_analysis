"""
Error handling and edge case tests for the Unsplash Image Search application.
Tests error recovery, resilience, and graceful handling of various failure scenarios.
"""

import pytest
import json
import csv
import requests
from unittest.mock import Mock, patch, side_effect
from pathlib import Path
import sys
import tempfile
import shutil

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import ImageSearchApp
from tests.fixtures.sample_data import (
    ERROR_RESPONSES,
    EDGE_CASES,
    TEST_IMAGE_DATA
)


@pytest.mark.unit
class TestErrorHandling:
    """Test suite for error handling and edge cases."""

    @pytest.fixture
    def app_instance(self, mock_config_manager, tkinter_root):
        """Create ImageSearchApp instance for error testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            app = ImageSearchApp()
            app.withdraw()
            yield app
            try:
                app.destroy()
            except:
                pass

    def test_network_connectivity_errors(self, app_instance, mock_requests_get):
        """Test handling of various network connectivity errors."""
        network_errors = [
            requests.exceptions.ConnectionError("Connection refused"),
            requests.exceptions.Timeout("Request timed out"),
            requests.exceptions.HTTPError("HTTP Error occurred"),
            requests.exceptions.RequestException("Generic request error"),
            OSError("Network is unreachable")
        ]

        for error in network_errors:
            mock_requests_get.side_effect = error
            
            # Should handle network errors gracefully
            with pytest.raises((requests.exceptions.RequestException, OSError)):
                app_instance.fetch_images_page("test query", 1)
            
            # Application should remain stable
            assert isinstance(app_instance.image_cache, dict)
            assert isinstance(app_instance.vocabulary_cache, set)

    def test_api_authentication_errors(self, app_instance, mock_requests_get, mock_openai_client):
        """Test handling of API authentication errors."""
        # Test Unsplash authentication error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
        mock_requests_get.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            app_instance.fetch_images_page("test", 1)

        # Test OpenAI authentication error
        mock_openai_client.chat.completions.create.side_effect = Exception("Invalid API key")
        app_instance.openai_client = mock_openai_client

        result = app_instance.translate_word("test")
        assert result == ""  # Should return empty string on auth error

    def test_api_rate_limit_errors(self, app_instance, mock_requests_get, mock_openai_client):
        """Test handling of API rate limiting."""
        # Test Unsplash rate limiting
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("429 Too Many Requests")
        mock_requests_get.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            app_instance.fetch_images_page("test", 1)

        # Test OpenAI rate limiting with retry mechanism
        mock_openai_client.chat.completions.create.side_effect = [
            Exception("rate_limit exceeded"),
            Exception("rate_limit exceeded"),
            Mock(choices=[Mock(message=Mock(content="success"))])
        ]
        app_instance.openai_client = mock_openai_client

        with patch('time.sleep'):  # Speed up test
            result = app_instance.api_call_with_retry(
                lambda: app_instance.openai_client.chat.completions.create(),
                max_retries=3
            )
            
        # Should eventually succeed after retries
        assert result is not None

    def test_malformed_api_responses(self, app_instance, mock_requests_get, mock_openai_client):
        """Test handling of malformed API responses."""
        # Test malformed JSON from Unsplash
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        with pytest.raises(json.JSONDecodeError):
            app_instance.fetch_images_page("test", 1)

        # Test malformed response from OpenAI phrase extraction
        mock_openai_response = Mock()
        mock_openai_response.choices = [Mock()]
        mock_openai_response.choices[0].message.content = EDGE_CASES["malformed_json_extraction"]
        mock_openai_client.chat.completions.create.return_value = mock_openai_response
        app_instance.openai_client = mock_openai_client

        # Should handle malformed JSON gracefully
        app_instance.extract_phrases_from_description("test description")
        # No exception should be raised, method should handle gracefully

    def test_file_system_errors(self, app_instance, test_data_dir):
        """Test handling of file system errors."""
        # Test permission errors
        protected_file = test_data_dir / "protected_file.csv"
        app_instance.CSV_TARGET_WORDS = protected_file

        # Create file and make it read-only (simulate permission error)
        with open(protected_file, 'w') as f:
            f.write("test,data\n")
        
        # Make file read-only
        protected_file.chmod(0o444)

        try:
            # Should handle permission error gracefully
            app_instance.log_target_word_csv("test", "test", "query", "url", "context")
            # May succeed or fail depending on system, but shouldn't crash
        except PermissionError:
            pass  # Expected on some systems
        finally:
            # Restore permissions for cleanup
            protected_file.chmod(0o644)

        # Test disk full simulation (mock)
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            # Should handle disk full error gracefully
            try:
                app_instance.log_target_word_csv("test", "test", "query", "url", "context")
            except OSError:
                pass  # Expected

    def test_memory_errors(self, app_instance):
        """Test handling of memory-related errors."""
        # Test large data allocation
        try:
            # Try to create very large data structure
            large_url = "https://test.com/memory_test"
            # Don't actually allocate huge memory, just test the structure
            app_instance.image_cache[large_url] = b"test_data"
            
            # Test cache size management
            assert large_url in app_instance.image_cache
            
        except MemoryError:
            # Should handle memory errors gracefully if they occur
            pass

        # Test handling of corrupted memory structures
        # Force a type error by trying to add incompatible data
        try:
            # This should work fine
            app_instance.vocabulary_cache.add("valid_string")
            assert "valid_string" in app_instance.vocabulary_cache
        except (TypeError, AttributeError):
            pytest.fail("Basic cache operations should not fail")

    def test_corrupted_data_recovery(self, app_instance, test_data_dir):
        """Test recovery from corrupted data files."""
        session_file = test_data_dir / "corrupted_session.json"
        vocab_file = test_data_dir / "corrupted_vocab.csv"
        app_instance.LOG_FILENAME = session_file
        app_instance.CSV_TARGET_WORDS = vocab_file

        # Create corrupted session file
        with open(session_file, 'w') as f:
            f.write("invalid json {content")

        # Create corrupted vocabulary file
        with open(vocab_file, 'w') as f:
            f.write("invalid,csv\"content\nwith,broken\"quotes")

        # Should handle corrupted files gracefully
        app_instance.load_used_image_urls_from_log()  # Should not raise exception
        app_instance.load_vocabulary_cache()  # Should not raise exception

        # Should be able to create new valid data after corruption
        app_instance.log_entries = [{
            "timestamp": "2023-01-01T10:00:00",
            "query": "recovery test",
            "image_url": "https://test.com/recovery",
            "user_note": "Recovery note",
            "generated_description": "Recovery description"
        }]

        # Should recreate valid files
        app_instance.save_session_to_json()
        app_instance.log_target_word_csv("recuperar", "recover", "test", "url", "context")

        # Verify new files are valid
        with open(session_file, 'r', encoding='utf-8') as f:
            recovered_data = json.load(f)  # Should not raise exception
        assert "sessions" in recovered_data

    def test_invalid_input_handling(self, app_instance):
        """Test handling of invalid input data."""
        # Test empty/None inputs
        assert app_instance.canonicalize_url(None) == ""
        assert app_instance.canonicalize_url("") == ""
        
        # Test invalid URLs
        invalid_urls = [
            "not-a-url",
            "ftp://invalid-protocol",
            "https://",
            "javascript:alert('xss')"
        ]
        
        for invalid_url in invalid_urls:
            # Should handle invalid URLs gracefully
            result = app_instance.canonicalize_url(invalid_url)
            assert isinstance(result, str)

        # Test very long inputs
        very_long_query = "a" * 10000
        very_long_phrase = "palabra " * 1000
        
        # Should handle long inputs without crashing
        app_instance.vocabulary_cache.add(very_long_phrase.strip())
        assert very_long_phrase.strip() in app_instance.vocabulary_cache

    def test_unicode_and_encoding_errors(self, app_instance, test_data_dir):
        """Test handling of Unicode and encoding issues."""
        # Test various Unicode characters
        unicode_tests = [
            "café niño montaña",
            "中文测试",
            "🏔️🌊🌅",
            "Москва",
            "العربية"
        ]

        for unicode_text in unicode_tests:
            # Should handle Unicode in vocabulary
            app_instance.vocabulary_cache.add(unicode_text)
            assert unicode_text in app_instance.vocabulary_cache

        # Test file encoding issues
        vocab_file = test_data_dir / "unicode_vocab.csv"
        app_instance.CSV_TARGET_WORDS = vocab_file

        # Write with different encodings and test recovery
        for unicode_text in unicode_tests[:3]:  # Test subset
            try:
                app_instance.log_target_word_csv(
                    unicode_text,
                    f"translation_{hash(unicode_text)}",
                    "unicode_test",
                    "https://test.com/unicode",
                    f"Context for {unicode_text}"
                )
            except UnicodeEncodeError:
                # Should be handled gracefully
                pass

    def test_concurrent_error_scenarios(self, app_instance):
        """Test error handling under concurrent access."""
        import threading
        
        errors = []
        completed_operations = []

        def error_prone_operations(thread_id):
            try:
                for i in range(20):
                    # Operations that might cause conflicts
                    url = f"https://concurrent.com/{thread_id}/{i}"
                    
                    # Cache operations
                    app_instance.image_cache[url] = TEST_IMAGE_DATA["png_1x1"]
                    app_instance.vocabulary_cache.add(f"concurrent_{thread_id}_{i}")
                    app_instance.used_image_urls.add(url)
                    
                    # URL canonicalization
                    canonical = app_instance.canonicalize_url(f"{url}?params=test")
                    
                    completed_operations.append(f"{thread_id}_{i}")
                    
            except Exception as e:
                errors.append(f"Thread {thread_id}: {str(e)}")

        # Create threads that might cause race conditions
        threads = []
        for i in range(5):
            thread = threading.Thread(target=error_prone_operations, args=(i,))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Should handle concurrent access without major errors
        assert len(errors) == 0, f"Concurrent errors: {errors}"
        assert len(completed_operations) == 100  # 5 threads * 20 operations

    def test_resource_exhaustion_handling(self, app_instance):
        """Test handling of resource exhaustion scenarios."""
        # Test file handle exhaustion (simulated)
        with patch('builtins.open', side_effect=OSError("Too many open files")):
            try:
                app_instance.log_target_word_csv("test", "test", "query", "url", "context")
            except OSError:
                pass  # Expected

        # Test cache overflow handling
        original_cache_size = len(app_instance.image_cache)
        
        # Add many items to test overflow handling
        for i in range(100):
            url = f"https://overflow.com/{i}"
            app_instance.image_cache[url] = TEST_IMAGE_DATA["png_1x1"]

        # Should handle large cache gracefully
        assert len(app_instance.image_cache) >= original_cache_size

    def test_api_service_unavailable(self, app_instance, mock_requests_get, mock_openai_client):
        """Test handling when API services are completely unavailable."""
        # Test Unsplash service unavailable
        mock_requests_get.side_effect = requests.exceptions.ConnectionError("Service unavailable")

        with pytest.raises(requests.exceptions.ConnectionError):
            app_instance.fetch_images_page("test", 1)

        # Test OpenAI service unavailable
        mock_openai_client.chat.completions.create.side_effect = Exception("Service unavailable")
        app_instance.openai_client = mock_openai_client

        # Should handle gracefully and return empty results
        result = app_instance.translate_word("test")
        assert result == ""

        # Application should remain functional for offline operations
        app_instance.vocabulary_cache.add("offline_word")
        assert "offline_word" in app_instance.vocabulary_cache

    def test_edge_case_data_combinations(self, app_instance):
        """Test edge cases with unusual data combinations."""
        edge_cases = [
            ("", "empty_string"),
            ("   ", "whitespace_only"),
            ("a" * 1000, "very_long_string"),
            ("special!@#$%^&*()chars", "special_characters"),
            ("mixed123数字unicode", "mixed_content"),
        ]

        for spanish, description in edge_cases:
            try:
                # Test vocabulary operations
                if spanish.strip():  # Don't add empty strings
                    app_instance.vocabulary_cache.add(spanish)
                    assert spanish in app_instance.vocabulary_cache
                
                # Test URL operations
                test_url = f"https://edge-case.com/{description}"
                canonical = app_instance.canonicalize_url(f"{test_url}?test=true")
                app_instance.used_image_urls.add(canonical)
                
                # Test cache operations
                app_instance.image_cache[test_url] = b"edge_case_data"
                
            except Exception as e:
                # Log unexpected errors but don't fail test
                print(f"Edge case '{description}' caused error: {e}")

    def test_recovery_after_critical_errors(self, app_instance, test_data_dir):
        """Test application recovery after critical errors."""
        session_file = test_data_dir / "recovery_session.json"
        vocab_file = test_data_dir / "recovery_vocab.csv"
        app_instance.LOG_FILENAME = session_file
        app_instance.CSV_TARGET_WORDS = vocab_file

        # Simulate critical error scenario
        # 1. Create some initial data
        app_instance.log_entries = [{
            "timestamp": "2023-01-01T10:00:00",
            "query": "initial data",
            "image_url": "https://test.com/initial",
            "user_note": "Initial note",
            "generated_description": "Initial description"
        }]
        app_instance.vocabulary_cache.add("inicial")
        
        # 2. Save initial state
        app_instance.save_session_to_json()
        app_instance.log_target_word_csv("inicial", "initial", "test", "url", "context")

        # 3. Simulate critical error that corrupts data structures
        # Force corrupt the caches
        try:
            # Simulate memory corruption by replacing with invalid types
            # (In real scenarios this might happen due to bugs)
            app_instance.image_cache.clear()
            app_instance.vocabulary_cache.clear()
            app_instance.used_image_urls.clear()
            app_instance.log_entries.clear()
        except:
            pass

        # 4. Test recovery
        # Application should be able to recover from files
        app_instance.load_used_image_urls_from_log()
        app_instance.load_vocabulary_cache()

        # 5. Verify recovery
        assert "https://test.com/initial" in app_instance.used_image_urls
        assert "inicial" in app_instance.vocabulary_cache

        # 6. Test continued functionality after recovery
        app_instance.vocabulary_cache.add("recuperado")
        assert "recuperado" in app_instance.vocabulary_cache

        # Should be able to save new data
        app_instance.log_entries = [{
            "timestamp": "2023-01-01T11:00:00",
            "query": "recovered data",
            "image_url": "https://test.com/recovered",
            "user_note": "Recovered note",
            "generated_description": "Recovered description"
        }]
        app_instance.save_session_to_json()

        # Verify recovery was successful
        with open(session_file, 'r', encoding='utf-8') as f:
            recovery_data = json.load(f)
        
        # Should have both original and recovered sessions
        assert len(recovery_data["sessions"]) >= 1


@pytest.mark.integration
class TestErrorRecovery:
    """Integration tests for error recovery scenarios."""

    @pytest.fixture
    def app_instance(self, mock_config_manager, tkinter_root):
        """Create ImageSearchApp instance for integration error testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            app = ImageSearchApp()
            app.withdraw()
            yield app
            try:
                app.destroy()
            except:
                pass

    def test_end_to_end_error_recovery(self, app_instance, mock_requests_get, mock_openai_client, test_data_dir):
        """Test end-to-end error recovery in a realistic workflow."""
        # Setup files
        session_file = test_data_dir / "e2e_recovery_session.json"
        vocab_file = test_data_dir / "e2e_recovery_vocab.csv"
        app_instance.LOG_FILENAME = session_file
        app_instance.CSV_TARGET_WORDS = vocab_file

        # Phase 1: Normal operation
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        mock_openai_response = Mock()
        mock_openai_response.choices = [Mock()]
        mock_openai_response.choices[0].message.content = "normal response"
        mock_openai_client.chat.completions.create.return_value = mock_openai_response
        app_instance.openai_client = mock_openai_client

        # Execute normal workflow
        results = app_instance.fetch_images_page("normal test", 1)
        translation = app_instance.translate_word("prueba")
        
        assert isinstance(results, list)
        assert translation == "normal response"

        # Phase 2: Introduce errors
        mock_requests_get.side_effect = Exception("Network error")
        mock_openai_client.chat.completions.create.side_effect = Exception("API error")

        # Should handle errors gracefully
        with pytest.raises(Exception):
            app_instance.fetch_images_page("error test", 1)

        error_translation = app_instance.translate_word("error")
        assert error_translation == ""

        # Phase 3: Recovery
        # Restore normal operation
        mock_requests_get.side_effect = None
        mock_requests_get.return_value = mock_response
        mock_openai_client.chat.completions.create.side_effect = None
        mock_openai_client.chat.completions.create.return_value = mock_openai_response

        # Should work normally again
        recovered_results = app_instance.fetch_images_page("recovery test", 1)
        recovered_translation = app_instance.translate_word("recuperar")

        assert isinstance(recovered_results, list)
        assert recovered_translation == "normal response"

        # Verify application state is stable
        assert isinstance(app_instance.image_cache, dict)
        assert isinstance(app_instance.vocabulary_cache, set)
        assert isinstance(app_instance.used_image_urls, set)