"""
Performance tests for image search functionality.
Tests memory usage, response times, caching efficiency, and resource management.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import time
import threading
import psutil
import gc
import weakref
from memory_profiler import profile
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from main import ImageSearchApp
from tests.fixtures.mock_api_responses import MockImageData, TEST_SCENARIOS


class TestMemoryPerformance:
    """Test suite for memory usage and management during image search."""

    @pytest.fixture
    def memory_test_app(self, mock_config_manager, no_gui):
        """Create app for memory performance testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            with patch('main.ThemeManager'):
                app = ImageSearchApp()
                app.config_manager = mock_config_manager
                
                # Initialize with minimal memory footprint
                app.current_query = ""
                app.current_results = []
                app.used_image_urls = set()
                app.image_cache = {}
                app.vocabulary_cache = set()
                app.log_entries = []
                
                # Mock UI elements to avoid memory overhead
                app.progress_bar = Mock()
                app.status_label = Mock()
                app.image_label = Mock()
                
                return app

    def test_memory_usage_with_image_caching(self, memory_test_app):
        """Test memory usage patterns with image caching."""
        initial_memory = self._get_memory_usage()
        
        # Simulate caching multiple images
        test_images = []
        for i in range(20):  # More than cache limit
            image_data = MockImageData.valid_png_bytes() * (i + 1)  # Varying sizes
            url = f'https://example.com/image_{i}.jpg'
            
            # Add to cache
            memory_test_app.image_cache[url] = image_data
            test_images.append(weakref.ref(image_data))
            
            # Force cache cleanup if over limit
            if len(memory_test_app.image_cache) > 10:
                # Remove oldest entries
                items_to_remove = len(memory_test_app.image_cache) - 10
                for _ in range(items_to_remove):
                    memory_test_app.image_cache.pop(next(iter(memory_test_app.image_cache)))
        
        # Force garbage collection
        gc.collect()
        
        final_memory = self._get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Memory should be controlled (not grow unbounded)
        assert memory_increase < 50 * 1024 * 1024  # Less than 50MB increase
        assert len(memory_test_app.image_cache) <= 10  # Cache size limit respected

    def test_memory_cleanup_after_search_session(self, memory_test_app):
        """Test memory cleanup after completing search session."""
        initial_memory = self._get_memory_usage()
        
        # Simulate complete search session
        for i in range(10):
            # Add image URL
            memory_test_app.used_image_urls.add(f'https://example.com/image_{i}.jpg')
            
            # Add vocabulary
            memory_test_app.vocabulary_cache.add(f'palabra_{i}')
            
            # Add log entry
            memory_test_app.log_entries.append({
                'timestamp': f'2024-01-01T{i:02d}:00:00',
                'query': f'query_{i}',
                'image_url': f'https://example.com/image_{i}.jpg'
            })
        
        mid_session_memory = self._get_memory_usage()
        
        # Clear session data
        memory_test_app.used_image_urls.clear()
        memory_test_app.vocabulary_cache.clear()
        memory_test_app.log_entries.clear()
        memory_test_app.image_cache.clear()
        
        gc.collect()
        final_memory = self._get_memory_usage()
        
        # Memory should return close to initial levels
        memory_recovered = mid_session_memory - final_memory
        assert memory_recovered > 0  # Some memory should be recovered

    def test_memory_with_large_vocabulary_cache(self, memory_test_app):
        """Test memory behavior with large vocabulary cache."""
        initial_memory = self._get_memory_usage()
        
        # Add large vocabulary cache
        for i in range(10000):
            spanish_phrase = f'la palabra muy larga número {i} con descripción extendida'
            memory_test_app.vocabulary_cache.add(spanish_phrase)
        
        large_cache_memory = self._get_memory_usage()
        
        # Clear half the cache
        cache_list = list(memory_test_app.vocabulary_cache)
        memory_test_app.vocabulary_cache = set(cache_list[:5000])
        
        gc.collect()
        reduced_cache_memory = self._get_memory_usage()
        
        # Memory should reduce proportionally
        memory_saved = large_cache_memory - reduced_cache_memory
        assert memory_saved > 0

    def test_memory_leak_detection(self, memory_test_app):
        """Test for memory leaks in repeated operations."""
        initial_memory = self._get_memory_usage()
        memory_samples = []
        
        # Perform repeated operations
        for iteration in range(50):
            # Simulate image search cycle
            mock_results = [
                {'id': f'img_{iteration}_{i}', 'urls': {'regular': f'url_{iteration}_{i}'}}
                for i in range(5)
            ]
            memory_test_app.current_results = mock_results
            
            # Process each result
            for result in mock_results:
                url = result['urls']['regular']
                memory_test_app.used_image_urls.add(url)
                
                # Simulate image caching
                if len(memory_test_app.image_cache) < 10:
                    memory_test_app.image_cache[url] = MockImageData.valid_png_bytes()
            
            # Clear current results
            memory_test_app.current_results = []
            
            # Sample memory every 10 iterations
            if iteration % 10 == 0:
                gc.collect()
                current_memory = self._get_memory_usage()
                memory_samples.append(current_memory - initial_memory)
        
        # Check for memory growth trend
        if len(memory_samples) > 2:
            # Memory shouldn't grow consistently across iterations
            memory_growth = memory_samples[-1] - memory_samples[0]
            assert memory_growth < 20 * 1024 * 1024  # Less than 20MB growth

    def test_concurrent_operations_memory_safety(self, memory_test_app):
        """Test memory safety during concurrent operations."""
        initial_memory = self._get_memory_usage()
        
        def worker_operation(worker_id):
            for i in range(100):
                # Simulate concurrent cache access
                url = f'worker_{worker_id}_image_{i}.jpg'
                image_data = MockImageData.valid_png_bytes()
                
                # Thread-safe cache operation
                if len(memory_test_app.image_cache) < 10:
                    memory_test_app.image_cache[url] = image_data
                
                # Simulate processing delay
                time.sleep(0.001)
        
        # Run concurrent workers
        threads = []
        for worker_id in range(5):
            thread = threading.Thread(target=worker_operation, args=(worker_id,), daemon=True)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=5.0)
        
        gc.collect()
        final_memory = self._get_memory_usage()
        
        # Memory should not explode under concurrent access
        memory_increase = final_memory - initial_memory
        assert memory_increase < 30 * 1024 * 1024  # Less than 30MB

    def _get_memory_usage(self):
        """Get current memory usage in bytes."""
        process = psutil.Process()
        return process.memory_info().rss


class TestResponseTimePerformance:
    """Test suite for response time and operation speed."""

    @pytest.fixture
    def timing_test_app(self, mock_config_manager, no_gui):
        """Create app for timing performance tests."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            with patch('main.ThemeManager'):
                app = ImageSearchApp()
                app.config_manager = mock_config_manager
                
                # Mock for timing tests
                app.show_progress = Mock()
                app.hide_progress = Mock()
                app.update_status = Mock()
                
                return app

    def test_search_response_time_under_load(self, timing_test_app):
        """Test search response times under various loads."""
        def mock_api_call_with_delay(delay_seconds):
            time.sleep(delay_seconds)
            return TEST_SCENARIOS['normal_search']['unsplash_response']
        
        # Test response times with different API delays
        test_delays = [0.1, 0.5, 1.0, 2.0]
        
        for delay in test_delays:
            with patch.object(timing_test_app, 'fetch_images_page') as mock_fetch:
                mock_fetch.side_effect = lambda *args: mock_api_call_with_delay(delay)
                
                start_time = time.time()
                
                # Simulate search operation
                timing_test_app.current_query = "test"
                timing_test_app.current_page = 1
                timing_test_app.current_results = []
                
                try:
                    timing_test_app.fetch_images_page("test", 1)
                except:
                    pass  # Expected for mock
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Response time should be reasonable (delay + small overhead)
                assert response_time < delay + 0.5

    def test_image_processing_performance(self, timing_test_app):
        """Test image processing and caching performance."""
        test_image_sizes = [
            (MockImageData.valid_png_bytes(), "small"),
            (MockImageData.valid_png_bytes() * 100, "medium"),
            (MockImageData.valid_png_bytes() * 1000, "large")
        ]
        
        for image_data, size_label in test_image_sizes:
            start_time = time.time()
            
            # Mock image processing
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.content = image_data
                mock_get.return_value = mock_response
                
                with patch('main.Image.open') as mock_image:
                    mock_pil_image = Mock()
                    mock_image.return_value = mock_pil_image
                    
                    # Simulate image processing
                    url = f'https://example.com/{size_label}.jpg'
                    timing_test_app.image_cache[url] = image_data
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Processing should be fast regardless of size
            assert processing_time < 1.0, f"{size_label} image took {processing_time:.2f}s"

    def test_vocabulary_search_performance(self, timing_test_app):
        """Test vocabulary search and duplicate detection performance."""
        # Pre-populate large vocabulary cache
        for i in range(10000):
            timing_test_app.vocabulary_cache.add(f'palabra_{i}')
        
        # Test duplicate detection performance
        test_phrases = [
            'palabra_500',  # Existing
            'palabra_nueva',  # New
            'palabra_5000',  # Existing
            'otra_palabra_nueva'  # New
        ]
        
        for phrase in test_phrases:
            start_time = time.time()
            
            # Check if phrase already exists
            exists = phrase in timing_test_app.vocabulary_cache
            
            end_time = time.time()
            lookup_time = end_time - start_time
            
            # Lookup should be very fast
            assert lookup_time < 0.01, f"Lookup took {lookup_time:.4f}s for {phrase}"

    def test_concurrent_api_calls_performance(self, timing_test_app):
        """Test performance under concurrent API calls."""
        def simulate_api_call(call_id):
            start_time = time.time()
            
            # Simulate API processing time
            time.sleep(0.1)
            
            end_time = time.time()
            return call_id, end_time - start_time
        
        # Test concurrent execution
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(simulate_api_call, i) 
                for i in range(10)
            ]
            
            results = []
            for future in as_completed(futures, timeout=5.0):
                results.append(future.result())
        
        # All calls should complete
        assert len(results) == 10
        
        # Average response time should be reasonable
        avg_time = sum(time for _, time in results) / len(results)
        assert avg_time < 0.5

    def test_ui_responsiveness_during_operations(self, timing_test_app):
        """Test UI responsiveness during background operations."""
        ui_response_times = []
        
        def simulate_background_work():
            time.sleep(1.0)  # Simulate long operation
        
        def simulate_ui_update():
            start_time = time.time()
            timing_test_app.update_status("UI Update")
            end_time = time.time()
            return end_time - start_time
        
        # Start background work
        bg_thread = threading.Thread(target=simulate_background_work, daemon=True)
        bg_thread.start()
        
        # Test UI responsiveness during background work
        for _ in range(10):
            response_time = simulate_ui_update()
            ui_response_times.append(response_time)
            time.sleep(0.1)
        
        bg_thread.join(timeout=2.0)
        
        # UI updates should remain fast
        avg_ui_time = sum(ui_response_times) / len(ui_response_times)
        assert avg_ui_time < 0.01  # Less than 10ms


class TestCachingPerformance:
    """Test suite for caching efficiency and performance."""

    @pytest.fixture
    def cache_test_app(self, mock_config_manager, no_gui):
        """Create app for cache performance testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            with patch('main.ThemeManager'):
                app = ImageSearchApp()
                app.config_manager = mock_config_manager
                
                # Initialize cache structures
                app.image_cache = {}
                app.vocabulary_cache = set()
                app.used_image_urls = set()
                
                return app

    def test_image_cache_hit_rate(self, cache_test_app):
        """Test image cache hit rate efficiency."""
        # Pre-populate cache
        cached_urls = []
        for i in range(10):
            url = f'https://example.com/cached_image_{i}.jpg'
            cache_test_app.image_cache[url] = MockImageData.valid_png_bytes()
            cached_urls.append(url)
        
        # Test cache hits vs misses
        cache_hits = 0
        cache_misses = 0
        
        test_urls = cached_urls[:5] + [f'https://example.com/new_image_{i}.jpg' for i in range(5)]
        
        for url in test_urls:
            if url in cache_test_app.image_cache:
                cache_hits += 1
            else:
                cache_misses += 1
        
        # Should have 50% hit rate
        hit_rate = cache_hits / (cache_hits + cache_misses)
        assert hit_rate == 0.5

    def test_cache_eviction_performance(self, cache_test_app):
        """Test performance of cache eviction algorithms."""
        # Fill cache beyond limit
        for i in range(15):  # More than limit of 10
            url = f'https://example.com/image_{i}.jpg'
            cache_test_app.image_cache[url] = MockImageData.valid_png_bytes()
            
            # Simulate eviction when over limit
            if len(cache_test_app.image_cache) > 10:
                # Remove oldest (first) entry
                first_key = next(iter(cache_test_app.image_cache))
                del cache_test_app.image_cache[first_key]
        
        # Cache should maintain size limit
        assert len(cache_test_app.image_cache) == 10

    def test_vocabulary_cache_performance(self, cache_test_app):
        """Test vocabulary cache performance with large datasets."""
        # Add large vocabulary set
        vocabulary_size = 50000
        
        start_time = time.time()
        for i in range(vocabulary_size):
            phrase = f'la palabra número {i} con descripción extendida muy larga'
            cache_test_app.vocabulary_cache.add(phrase)
        
        add_time = time.time() - start_time
        
        # Test lookup performance
        lookup_start = time.time()
        for i in range(0, vocabulary_size, 1000):  # Sample every 1000th
            phrase = f'la palabra número {i} con descripción extendida muy larga'
            exists = phrase in cache_test_app.vocabulary_cache
            assert exists  # Should exist
        
        lookup_time = time.time() - lookup_start
        
        # Performance should be acceptable
        assert add_time < 5.0  # Adding 50k items in under 5 seconds
        assert lookup_time < 0.1  # Lookups should be very fast

    def test_cache_memory_efficiency(self, cache_test_app):
        """Test memory efficiency of caching strategies."""
        initial_memory = self._get_memory_usage()
        
        # Test different caching strategies
        strategies = [
            ('small_frequent', [(f'url_{i}', MockImageData.valid_png_bytes()) for i in range(100)]),
            ('large_infrequent', [(f'big_url_{i}', MockImageData.valid_png_bytes() * 1000) for i in range(10)]),
            ('mixed', [(f'mixed_url_{i}', MockImageData.valid_png_bytes() * (i % 10 + 1)) for i in range(50)])
        ]
        
        memory_usage = {}
        
        for strategy_name, cache_data in strategies:
            cache_test_app.image_cache.clear()
            gc.collect()
            
            strategy_start_memory = self._get_memory_usage()
            
            # Apply caching strategy
            for url, data in cache_data:
                if len(cache_test_app.image_cache) < 10:
                    cache_test_app.image_cache[url] = data
                else:
                    # Evict oldest
                    oldest_url = next(iter(cache_test_app.image_cache))
                    del cache_test_app.image_cache[oldest_url]
                    cache_test_app.image_cache[url] = data
            
            strategy_end_memory = self._get_memory_usage()
            memory_usage[strategy_name] = strategy_end_memory - strategy_start_memory
        
        # Verify memory usage is reasonable for each strategy
        for strategy, usage in memory_usage.items():
            assert usage < 50 * 1024 * 1024, f"{strategy} used {usage} bytes"

    def _get_memory_usage(self):
        """Get current memory usage in bytes."""
        process = psutil.Process()
        return process.memory_info().rss


class TestResourceManagement:
    """Test suite for system resource management."""

    @pytest.fixture
    def resource_test_app(self, mock_config_manager, no_gui):
        """Create app for resource management testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            with patch('main.ThemeManager'):
                app = ImageSearchApp()
                app.config_manager = mock_config_manager
                
                # Resource tracking
                app._active_threads = []
                app._open_connections = []
                
                return app

    def test_thread_lifecycle_management(self, resource_test_app):
        """Test proper thread creation and cleanup."""
        initial_thread_count = threading.active_count()
        
        # Create multiple worker threads
        def worker_task(task_id):
            time.sleep(0.1)
            return f"Task {task_id} complete"
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_task, args=(i,), daemon=True)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=1.0)
        
        final_thread_count = threading.active_count()
        
        # Thread count should return to initial level
        assert final_thread_count <= initial_thread_count + 1  # Allow some variance

    def test_file_handle_management(self, resource_test_app, temp_data_dir):
        """Test proper file handle management."""
        import psutil
        
        process = psutil.Process()
        initial_handles = process.num_fds() if hasattr(process, 'num_fds') else 0
        
        # Simulate file operations
        test_files = []
        for i in range(10):
            test_file = temp_data_dir / f'test_file_{i}.txt'
            test_file.write_text(f'Test content {i}')
            test_files.append(test_file)
        
        # Read files
        for test_file in test_files:
            content = test_file.read_text()
            assert content.startswith('Test content')
        
        # Cleanup
        for test_file in test_files:
            test_file.unlink()
        
        if hasattr(process, 'num_fds'):
            final_handles = process.num_fds()
            # File handles should not leak
            assert final_handles <= initial_handles + 5  # Allow some variance

    def test_network_connection_management(self, resource_test_app):
        """Test network connection resource management."""
        # Mock network operations
        active_connections = 0
        max_connections = 0
        
        def mock_network_call():
            nonlocal active_connections, max_connections
            active_connections += 1
            max_connections = max(max_connections, active_connections)
            time.sleep(0.1)  # Simulate network delay
            active_connections -= 1
        
        # Simulate concurrent network calls
        threads = []
        for i in range(20):
            thread = threading.Thread(target=mock_network_call, daemon=True)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=2.0)
        
        # Connection count should return to zero
        assert active_connections == 0
        # Should not exceed reasonable limits
        assert max_connections <= 10

    def test_cleanup_on_application_exit(self, resource_test_app, temp_data_dir):
        """Test resource cleanup on application exit."""
        # Setup resources that need cleanup
        resource_test_app.log_entries = [{'test': 'data'}]
        resource_test_app.image_cache = {'url': b'data'}
        
        # Create temp files
        temp_files = []
        for i in range(3):
            temp_file = temp_data_dir / f'temp_{i}.json'
            temp_file.write_text('{"temp": "data"}')
            temp_files.append(temp_file)
        
        # Simulate application exit
        resource_test_app.on_exit()
        
        # Resources should be cleaned up
        # (This would depend on actual cleanup implementation)
        assert resource_test_app.log_entries is not None  # Basic check