"""
Performance tests for the Unsplash Image Search application.
Tests system performance under various load conditions and validates against benchmarks.
"""

import pytest
import time
import threading
import resource
import sys
import gc
from unittest.mock import Mock, patch
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import ImageSearchApp
from tests.fixtures.sample_data import (
    SAMPLE_UNSPLASH_SEARCH_RESPONSE,
    SAMPLE_OPENAI_DESCRIPTION_RESPONSES,
    TEST_IMAGE_DATA,
    PERFORMANCE_BENCHMARKS
)


@pytest.mark.slow
@pytest.mark.performance
class TestPerformanceBenchmarks:
    """Performance benchmark tests for the application."""

    @pytest.fixture
    def app_instance(self, mock_config_manager, tkinter_root):
        """Create ImageSearchApp instance for performance testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            app = ImageSearchApp()
            app.withdraw()
            yield app
            try:
                app.destroy()
            except:
                pass

    def test_api_call_performance(self, app_instance, mock_requests_get):
        """Test API call performance meets benchmarks."""
        # Setup fast mock response
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        # Measure API call performance
        start_time = time.time()
        
        for i in range(10):
            results = app_instance.fetch_images_page(f"query_{i}", 1)
            assert len(results) > 0

        end_time = time.time()
        total_time = end_time - start_time
        average_time = total_time / 10

        # Should meet performance benchmark
        assert average_time < PERFORMANCE_BENCHMARKS["api_call_timeout"]
        assert total_time < PERFORMANCE_BENCHMARKS["api_call_timeout"] * 2  # Total should be reasonable

    def test_image_processing_performance(self, app_instance, mock_requests_get):
        """Test image processing performance."""
        # Setup mocks
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response.raise_for_status = Mock()
        
        mock_img_response = Mock()
        mock_img_response.content = TEST_IMAGE_DATA["png_1x1"]
        mock_img_response.raise_for_status = Mock()
        
        mock_requests_get.side_effect = [mock_response, mock_img_response]

        with patch('PIL.Image.open') as mock_image_open, \
             patch('PIL.ImageTk.PhotoImage') as mock_photo_image:
            
            mock_pil_image = Mock()
            mock_image_open.return_value = mock_pil_image
            mock_photo = Mock()
            mock_photo_image.return_value = mock_photo

            # Setup app state
            app_instance.current_query = "performance test"
            app_instance.current_page = 1
            app_instance.current_results = []
            app_instance.current_index = 0

            # Measure image processing time
            start_time = time.time()
            photo = app_instance.get_next_image()
            end_time = time.time()

            processing_time = end_time - start_time

            # Verify result and performance
            assert photo == mock_photo
            assert processing_time < PERFORMANCE_BENCHMARKS["image_processing_time"]

    def test_openai_response_performance(self, app_instance, mock_openai_client):
        """Test OpenAI API response performance."""
        # Setup fast mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Quick response"
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        app_instance.openai_client = mock_openai_client

        # Test translation performance
        start_time = time.time()
        
        translations = []
        for i in range(5):
            result = app_instance.translate_word(f"palabra_{i}")
            translations.append(result)

        end_time = time.time()
        total_time = end_time - start_time
        average_time = total_time / 5

        # Verify results and performance
        assert all(t == "Quick response" for t in translations)
        assert average_time < PERFORMANCE_BENCHMARKS["translation_timeout"]

    def test_memory_usage_performance(self, app_instance):
        """Test memory usage stays within acceptable limits."""
        # Get initial memory usage
        gc.collect()  # Force garbage collection
        initial_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        # Add significant amount of data to caches
        for i in range(100):
            # Add to image cache
            url = f"https://test.com/memory_test_{i}"
            app_instance.image_cache[url] = TEST_IMAGE_DATA["png_1x1"] * 10  # Make it larger
            
            # Add to vocabulary cache
            app_instance.vocabulary_cache.add(f"memoria_palabra_{i}")
            
            # Add to used URLs
            app_instance.used_image_urls.add(f"https://test.com/used_{i}")
            
            # Add to target phrases
            app_instance.target_phrases.append(f"frase_{i} - phrase_{i}")

        # Force garbage collection and measure
        gc.collect()
        final_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        # Calculate memory increase (in KB on Linux, bytes on macOS)
        memory_increase = final_memory - initial_memory
        
        # Convert to MB for comparison (handling platform differences)
        if sys.platform == 'darwin':  # macOS reports in bytes
            memory_increase_mb = memory_increase / (1024 * 1024)
        else:  # Linux reports in KB
            memory_increase_mb = memory_increase / 1024

        # Should stay within benchmark
        assert memory_increase_mb < PERFORMANCE_BENCHMARKS["memory_usage_mb"]

    def test_concurrent_operations_performance(self, app_instance, mock_requests_get, mock_openai_client):
        """Test performance under concurrent operations."""
        # Setup mocks
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        mock_openai_response = Mock()
        mock_openai_response.choices = [Mock()]
        mock_openai_response.choices[0].message.content = "Concurrent response"
        mock_openai_client.chat.completions.create.return_value = mock_openai_response
        app_instance.openai_client = mock_openai_client

        results = []
        start_time = time.time()

        def concurrent_operations(thread_id, operation_count):
            thread_results = []
            for i in range(operation_count):
                # API call
                api_result = app_instance.fetch_images_page(f"concurrent_{thread_id}_{i}", 1)
                thread_results.append(len(api_result))
                
                # Translation
                translation = app_instance.translate_word(f"concurrent_{thread_id}_{i}")
                thread_results.append(len(translation))
                
                # Cache operations
                app_instance.image_cache[f"concurrent_{thread_id}_{i}"] = TEST_IMAGE_DATA["png_1x1"]
                app_instance.vocabulary_cache.add(f"concurrent_{thread_id}_{i}")
                
            results.extend(thread_results)

        # Create and start threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=concurrent_operations, args=(i, 5))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        end_time = time.time()
        total_time = end_time - start_time

        # Verify all operations completed successfully
        assert len(results) == 30  # 3 threads * 5 operations * 2 results per operation
        assert all(r > 0 for r in results)

        # Performance should be reasonable even with concurrency
        assert total_time < 10.0  # Should complete within 10 seconds

    def test_large_dataset_performance(self, app_instance):
        """Test performance with large datasets."""
        # Create large dataset
        large_dataset_size = 1000

        start_time = time.time()

        # Add large amount of data
        for i in range(large_dataset_size):
            url = f"https://test.com/large_dataset_{i}"
            app_instance.image_cache[url] = TEST_IMAGE_DATA["png_1x1"]
            app_instance.vocabulary_cache.add(f"large_word_{i}")
            app_instance.used_image_urls.add(url)

        creation_time = time.time() - start_time

        # Test lookup performance
        start_time = time.time()
        
        # Perform lookups
        for i in range(100):  # Sample of lookups
            lookup_url = f"https://test.com/large_dataset_{i * 10}"
            lookup_word = f"large_word_{i * 10}"
            
            # These should be O(1) operations
            assert lookup_url in app_instance.image_cache
            assert lookup_word in app_instance.vocabulary_cache
            assert lookup_url in app_instance.used_image_urls

        lookup_time = time.time() - start_time

        # Performance should be acceptable
        assert creation_time < 5.0  # Creation should be under 5 seconds
        assert lookup_time < 1.0    # Lookups should be under 1 second

    def test_file_io_performance(self, app_instance, test_data_dir):
        """Test file I/O performance for session and vocabulary data."""
        import csv
        import json
        
        # Setup file paths
        session_file = test_data_dir / "performance_session.json"
        vocab_file = test_data_dir / "performance_vocab.csv"
        app_instance.LOG_FILENAME = session_file
        app_instance.CSV_TARGET_WORDS = vocab_file

        # Create substantial amount of data
        session_entries = []
        for i in range(50):
            entry = {
                "timestamp": f"2023-01-01T10:{i:02d}:00",
                "query": f"performance_query_{i}",
                "image_url": f"https://test.com/performance_image_{i}",
                "user_note": f"Performance test note {i} with additional content to make it more realistic",
                "generated_description": f"Descripción de rendimiento número {i} con contenido extenso para simular descripciones reales que pueden ser bastante largas y detalladas, incluyendo muchos detalles sobre la imagen."
            }
            session_entries.append(entry)

        app_instance.log_entries = session_entries

        # Test session save performance
        start_time = time.time()
        app_instance.save_session_to_json()
        session_save_time = time.time() - start_time

        # Test vocabulary save performance
        start_time = time.time()
        for i in range(100):
            app_instance.log_target_word_csv(
                f"rendimiento_{i}",
                f"performance_{i}",
                f"query_{i}",
                f"https://test.com/perf_image_{i}",
                f"Context for performance word {i}"
            )
        vocab_save_time = time.time() - start_time

        # Test load performance
        app_instance.log_entries = []
        app_instance.used_image_urls.clear()
        app_instance.vocabulary_cache.clear()

        start_time = time.time()
        app_instance.load_used_image_urls_from_log()
        session_load_time = time.time() - start_time

        start_time = time.time()
        app_instance.load_vocabulary_cache()
        vocab_load_time = time.time() - start_time

        # Verify performance benchmarks
        assert session_save_time < PERFORMANCE_BENCHMARKS["file_operations_time"]
        assert vocab_save_time < PERFORMANCE_BENCHMARKS["file_operations_time"] * 2  # More operations
        assert session_load_time < PERFORMANCE_BENCHMARKS["file_operations_time"]
        assert vocab_load_time < PERFORMANCE_BENCHMARKS["file_operations_time"]

        # Verify data was loaded correctly
        assert len(app_instance.used_image_urls) == 50
        assert len(app_instance.vocabulary_cache) == 100

    def test_ui_responsiveness_simulation(self, app_instance):
        """Test UI responsiveness under load (simulated)."""
        # Simulate UI operations that should remain responsive
        operations_count = 100
        max_operation_time = PERFORMANCE_BENCHMARKS["ui_response_time"]

        for i in range(operations_count):
            start_time = time.time()
            
            # Simulate UI operations
            app_instance.update_stats()
            app_instance.canonicalize_url(f"https://test.com/ui_test_{i}?param=value")
            
            # Cache operations (should be fast)
            test_url = f"https://test.com/ui_cache_{i}"
            app_instance.image_cache[test_url] = b"test_data"
            _ = app_instance.image_cache.get(test_url)
            
            app_instance.vocabulary_cache.add(f"ui_word_{i}")
            _ = f"ui_word_{i}" in app_instance.vocabulary_cache

            operation_time = time.time() - start_time
            
            # Each operation should be very fast to maintain UI responsiveness
            assert operation_time < max_operation_time

    @pytest.mark.benchmark
    def test_performance_regression(self, app_instance, mock_requests_get, mock_openai_client):
        """Test for performance regression against baseline."""
        # This test would compare against saved baseline metrics
        # For demonstration, we'll use the current benchmarks as baseline
        
        # Setup mocks for consistent testing
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_UNSPLASH_SEARCH_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        mock_openai_response = Mock()
        mock_openai_response.choices = [Mock()]
        mock_openai_response.choices[0].message.content = "Baseline response"
        mock_openai_client.chat.completions.create.return_value = mock_openai_response
        app_instance.openai_client = mock_openai_client

        # Run performance test suite
        performance_metrics = {}

        # API call performance
        start_time = time.time()
        for i in range(5):
            app_instance.fetch_images_page(f"baseline_{i}", 1)
        performance_metrics['api_calls'] = (time.time() - start_time) / 5

        # Translation performance
        start_time = time.time()
        for i in range(5):
            app_instance.translate_word(f"baseline_{i}")
        performance_metrics['translations'] = (time.time() - start_time) / 5

        # Cache performance
        start_time = time.time()
        for i in range(100):
            app_instance.image_cache[f"baseline_{i}"] = TEST_IMAGE_DATA["png_1x1"]
            app_instance.vocabulary_cache.add(f"baseline_word_{i}")
        performance_metrics['cache_operations'] = (time.time() - start_time) / 100

        # Compare against benchmarks (acting as baseline)
        assert performance_metrics['api_calls'] < PERFORMANCE_BENCHMARKS["api_call_timeout"]
        assert performance_metrics['translations'] < PERFORMANCE_BENCHMARKS["translation_timeout"]
        assert performance_metrics['cache_operations'] < 0.001  # Should be very fast

        # Log performance metrics for monitoring
        print(f"\nPerformance Metrics:")
        print(f"API Calls: {performance_metrics['api_calls']:.4f}s avg")
        print(f"Translations: {performance_metrics['translations']:.4f}s avg")
        print(f"Cache Operations: {performance_metrics['cache_operations']:.6f}s avg")


@pytest.mark.slow
@pytest.mark.stress
class TestStressTests:
    """Stress tests for the application under extreme conditions."""

    @pytest.fixture
    def app_instance(self, mock_config_manager, tkinter_root):
        """Create ImageSearchApp instance for stress testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            app = ImageSearchApp()
            app.withdraw()
            yield app
            try:
                app.destroy()
            except:
                pass

    def test_cache_stress(self, app_instance):
        """Test cache behavior under stress conditions."""
        # Fill caches to capacity and beyond
        stress_size = 1000

        # Test image cache stress
        for i in range(stress_size):
            url = f"https://test.com/stress_image_{i}"
            # Use larger data to stress memory
            app_instance.image_cache[url] = TEST_IMAGE_DATA["png_1x1"] * (i % 10 + 1)

        # Test vocabulary cache stress
        for i in range(stress_size):
            word = f"stress_word_{i}_with_longer_content_to_test_memory_usage"
            app_instance.vocabulary_cache.add(word)

        # Test URL set stress
        for i in range(stress_size):
            url = f"https://test.com/stress_url_{i}?param=value&other=param"
            app_instance.used_image_urls.add(url)

        # Verify caches still function correctly
        assert len(app_instance.image_cache) == stress_size
        assert len(app_instance.vocabulary_cache) == stress_size
        assert len(app_instance.used_image_urls) == stress_size

        # Test cache access performance under stress
        start_time = time.time()
        
        for i in range(100):  # Sample accesses
            test_url = f"https://test.com/stress_image_{i}"
            test_word = f"stress_word_{i}_with_longer_content_to_test_memory_usage"
            test_used_url = f"https://test.com/stress_url_{i}?param=value&other=param"
            
            assert test_url in app_instance.image_cache
            assert test_word in app_instance.vocabulary_cache
            assert test_used_url in app_instance.used_image_urls

        access_time = time.time() - start_time
        
        # Access should still be fast even under stress
        assert access_time < 1.0

    def test_concurrent_stress(self, app_instance):
        """Test application under concurrent stress."""
        import threading
        
        errors = []
        completed_operations = []
        
        def stress_operations(thread_id, operation_count):
            try:
                for i in range(operation_count):
                    # Multiple types of operations
                    app_instance.image_cache[f"stress_{thread_id}_{i}"] = TEST_IMAGE_DATA["png_1x1"]
                    app_instance.vocabulary_cache.add(f"stress_word_{thread_id}_{i}")
                    app_instance.used_image_urls.add(f"https://stress.com/{thread_id}/{i}")
                    
                    # URL operations
                    test_url = f"https://test.com/stress?id={thread_id}&item={i}"
                    canonical = app_instance.canonicalize_url(test_url)
                    
                    completed_operations.append(f"{thread_id}_{i}")
                    
                    # Small delay to simulate real usage
                    time.sleep(0.001)
                    
            except Exception as e:
                errors.append(f"Thread {thread_id}: {str(e)}")

        # Create many concurrent threads
        threads = []
        for i in range(10):  # 10 concurrent threads
            thread = threading.Thread(target=stress_operations, args=(i, 50))  # 50 operations each
            threads.append(thread)

        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()
        end_time = time.time()

        # Verify stress test results
        assert len(errors) == 0, f"Concurrent stress errors: {errors}"
        assert len(completed_operations) == 500  # 10 threads * 50 operations
        
        # Should complete within reasonable time even under stress
        total_time = end_time - start_time
        assert total_time < 30.0  # Should complete within 30 seconds

        # Verify final state integrity
        assert len(app_instance.image_cache) == 500
        assert len(app_instance.vocabulary_cache) == 500
        assert len(app_instance.used_image_urls) == 500

    def test_memory_pressure_stress(self, app_instance):
        """Test application under memory pressure."""
        # Create memory pressure by allocating large amounts of data
        large_data_chunks = []
        
        try:
            # Allocate memory in chunks
            for i in range(50):  # Adjust based on available memory
                # Create large data chunk (1MB each)
                chunk = b"x" * (1024 * 1024)
                large_data_chunks.append(chunk)
                
                # Continue normal application operations under memory pressure
                app_instance.image_cache[f"memory_stress_{i}"] = TEST_IMAGE_DATA["png_1x1"]
                app_instance.vocabulary_cache.add(f"memory_word_{i}")
                
                # Force some garbage collection occasionally
                if i % 10 == 0:
                    gc.collect()

            # Verify application still functions under memory pressure
            assert len(app_instance.image_cache) == 50
            assert len(app_instance.vocabulary_cache) == 50
            
            # Test cache access under memory pressure
            for i in range(50):
                assert f"memory_stress_{i}" in app_instance.image_cache
                assert f"memory_word_{i}" in app_instance.vocabulary_cache

        finally:
            # Clean up large allocations
            large_data_chunks.clear()
            gc.collect()

    def test_long_running_stress(self, app_instance):
        """Test application stability over extended operation."""
        # Simulate long-running application usage
        operation_cycles = 100
        operations_per_cycle = 10
        
        for cycle in range(operation_cycles):
            # Simulate typical usage pattern
            for op in range(operations_per_cycle):
                operation_id = cycle * operations_per_cycle + op
                
                # Cache operations
                app_instance.image_cache[f"longrun_{operation_id}"] = TEST_IMAGE_DATA["png_1x1"]
                app_instance.vocabulary_cache.add(f"longrun_word_{operation_id}")
                
                # URL operations
                url = f"https://longrun.com/image_{operation_id}?cycle={cycle}"
                canonical = app_instance.canonicalize_url(url)
                app_instance.used_image_urls.add(canonical)
                
                # Simulate cache cleanup (as would happen in real usage)
                if len(app_instance.image_cache) > PERFORMANCE_BENCHMARKS["cache_size_limit"]:
                    # Remove some oldest entries
                    keys_to_remove = list(app_instance.image_cache.keys())[:10]
                    for key in keys_to_remove:
                        del app_instance.image_cache[key]

            # Periodic cleanup and verification
            if cycle % 20 == 0:
                gc.collect()
                
                # Verify application state is still consistent
                assert isinstance(app_instance.image_cache, dict)
                assert isinstance(app_instance.vocabulary_cache, set)
                assert isinstance(app_instance.used_image_urls, set)

        # Final verification after long run
        total_operations = operation_cycles * operations_per_cycle
        print(f"\nCompleted {total_operations} operations across {operation_cycles} cycles")
        
        # Caches should be functional (may not contain all items due to cleanup)
        assert len(app_instance.image_cache) > 0
        assert len(app_instance.vocabulary_cache) == total_operations  # Set should contain all
        assert len(app_instance.used_image_urls) == total_operations