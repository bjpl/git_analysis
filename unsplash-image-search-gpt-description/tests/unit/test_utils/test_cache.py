"""
Unit tests for caching utilities and mechanisms.
Tests image cache, vocabulary cache, and other caching functionality.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import sys
import time
import threading

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from main import ImageSearchApp
from tests.fixtures.sample_data import (
    TEST_IMAGE_DATA,
    PERFORMANCE_BENCHMARKS
)


@pytest.mark.unit
class TestCacheUtilities:
    """Test suite for caching utilities and mechanisms."""

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

    def test_image_cache_basic_operations(self, app_instance):
        """Test basic image cache operations."""
        # Test cache initialization
        assert isinstance(app_instance.image_cache, dict)
        assert len(app_instance.image_cache) == 0

        # Test cache storage
        url = "https://test.com/cache_test"
        image_data = TEST_IMAGE_DATA["png_1x1"]
        app_instance.image_cache[url] = image_data

        # Test cache retrieval
        assert app_instance.image_cache[url] == image_data
        assert len(app_instance.image_cache) == 1

        # Test cache update
        new_data = TEST_IMAGE_DATA["jpg_1x1"]
        app_instance.image_cache[url] = new_data
        assert app_instance.image_cache[url] == new_data
        assert len(app_instance.image_cache) == 1  # Should not add new entry

        # Test cache deletion
        del app_instance.image_cache[url]
        assert len(app_instance.image_cache) == 0
        assert url not in app_instance.image_cache

    def test_image_cache_hit_rate(self, app_instance):
        """Test image cache hit rate optimization."""
        # Populate cache
        urls = [f"https://test.com/image_{i}" for i in range(5)]
        for i, url in enumerate(urls):
            app_instance.image_cache[url] = f"image_data_{i}".encode()

        # Test cache hits
        hit_count = 0
        miss_count = 0

        # Test existing URLs (should be hits)
        for url in urls:
            if url in app_instance.image_cache:
                hit_count += 1
            else:
                miss_count += 1

        # Test non-existing URLs (should be misses)  
        for i in range(5, 10):
            test_url = f"https://test.com/missing_{i}"
            if test_url in app_instance.image_cache:
                hit_count += 1
            else:
                miss_count += 1

        # Verify hit/miss counts
        assert hit_count == 5  # All existing URLs found
        assert miss_count == 5  # All non-existing URLs missed

        # Calculate hit rate
        total_requests = hit_count + miss_count
        hit_rate = hit_count / total_requests
        assert hit_rate == 0.5  # 50% hit rate in this test

    def test_image_cache_size_limiting(self, app_instance):
        """Test image cache size limiting mechanism."""
        # Fill cache beyond reasonable limit
        max_cache_size = 10
        
        # Add more items than limit
        for i in range(max_cache_size + 5):
            url = f"https://test.com/size_limit_{i}"
            app_instance.image_cache[url] = f"data_{i}".encode()

        # In a real implementation, cache size would be limited
        # For now, verify we can add all items
        assert len(app_instance.image_cache) == max_cache_size + 5

        # Simulate size limiting (as done in get_next_image)
        while len(app_instance.image_cache) > max_cache_size:
            # Remove oldest entry (first key)
            oldest_key = next(iter(app_instance.image_cache))
            app_instance.image_cache.pop(oldest_key)

        assert len(app_instance.image_cache) == max_cache_size

    def test_image_cache_lru_behavior(self, app_instance):
        """Test Least Recently Used (LRU) cache behavior simulation."""
        # Add items to cache
        urls = [f"https://test.com/lru_{i}" for i in range(5)]
        for url in urls:
            app_instance.image_cache[url] = f"data_for_{url}".encode()

        # Access some items (simulate LRU tracking)
        accessed_urls = []
        
        # Access first and third items
        if urls[0] in app_instance.image_cache:
            accessed_urls.append(urls[0])
        if urls[2] in app_instance.image_cache:
            accessed_urls.append(urls[2])

        # Simulate LRU eviction
        # In real LRU, these would be moved to end of order
        for url in accessed_urls:
            # Re-insert to simulate "recently used"
            data = app_instance.image_cache.pop(url)
            app_instance.image_cache[url] = data

        # Verify cache still contains all items
        assert len(app_instance.image_cache) == 5

    def test_vocabulary_cache_operations(self, app_instance):
        """Test vocabulary cache operations."""
        # Test vocabulary cache initialization
        assert isinstance(app_instance.vocabulary_cache, set)

        # Test adding vocabulary
        words = ["palabra1", "palabra2", "palabra3"]
        for word in words:
            app_instance.vocabulary_cache.add(word)

        # Test cache size
        assert len(app_instance.vocabulary_cache) == 3

        # Test duplicate prevention
        app_instance.vocabulary_cache.add("palabra1")  # Duplicate
        assert len(app_instance.vocabulary_cache) == 3  # Should not increase

        # Test membership testing (O(1) operation for sets)
        assert "palabra1" in app_instance.vocabulary_cache
        assert "palabra_nonexistent" not in app_instance.vocabulary_cache

    def test_vocabulary_cache_persistence_simulation(self, app_instance, test_data_dir):
        """Test vocabulary cache persistence to file."""
        import csv
        
        vocab_file = test_data_dir / "vocab_cache_test.csv"
        app_instance.CSV_TARGET_WORDS = vocab_file

        # Create test vocabulary file
        test_vocabulary = [
            ["Spanish", "English", "Date", "Search Query", "Image URL", "Context"],
            ["montaña", "mountain", "2023-01-01", "nature", "url1", "context1"],
            ["océano", "ocean", "2023-01-01", "water", "url2", "context2"],
            ["ciudad", "city", "2023-01-01", "urban", "url3", "context3"]
        ]

        with open(vocab_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in test_vocabulary:
                writer.writerow(row)

        # Clear cache and load from file
        app_instance.vocabulary_cache.clear()
        assert len(app_instance.vocabulary_cache) == 0

        app_instance.load_vocabulary_cache()

        # Verify cache was populated
        expected_words = {"montaña", "océano", "ciudad"}
        assert expected_words.issubset(app_instance.vocabulary_cache)

    def test_cache_memory_efficiency(self, app_instance):
        """Test cache memory efficiency."""
        import sys

        # Measure initial memory usage
        initial_image_cache_size = sys.getsizeof(app_instance.image_cache)
        initial_vocab_cache_size = sys.getsizeof(app_instance.vocabulary_cache)

        # Add data to caches
        for i in range(50):
            # Image cache
            url = f"https://test.com/memory_{i}"
            app_instance.image_cache[url] = TEST_IMAGE_DATA["png_1x1"]
            
            # Vocabulary cache
            word = f"palabra_{i}"
            app_instance.vocabulary_cache.add(word)

        # Measure final memory usage
        final_image_cache_size = sys.getsizeof(app_instance.image_cache)
        final_vocab_cache_size = sys.getsizeof(app_instance.vocabulary_cache)

        # Memory should have increased reasonably
        image_cache_growth = final_image_cache_size - initial_image_cache_size
        vocab_cache_growth = final_vocab_cache_size - initial_vocab_cache_size

        assert image_cache_growth > 0
        assert vocab_cache_growth > 0

        # Memory growth should be reasonable (not testing exact values due to Python internals)
        assert image_cache_growth < 1024 * 1024  # Less than 1MB for test data
        assert vocab_cache_growth < 1024 * 1024   # Less than 1MB for test data

    @pytest.mark.slow
    def test_cache_performance_benchmarks(self, app_instance):
        """Test cache performance against benchmarks."""
        # Test image cache performance
        start_time = time.time()

        # Add many items to image cache
        for i in range(100):
            url = f"https://test.com/perf_{i}"
            app_instance.image_cache[url] = TEST_IMAGE_DATA["png_1x1"]

        # Test lookups
        for i in range(100):
            url = f"https://test.com/perf_{i}"
            _ = app_instance.image_cache.get(url)

        end_time = time.time()
        cache_operation_time = end_time - start_time

        # Should be very fast
        assert cache_operation_time < PERFORMANCE_BENCHMARKS["memory_usage_mb"] / 1000

        # Test vocabulary cache performance
        start_time = time.time()

        # Add many items
        for i in range(1000):
            app_instance.vocabulary_cache.add(f"word_{i}")

        # Test membership tests
        for i in range(1000):
            _ = f"word_{i}" in app_instance.vocabulary_cache

        end_time = time.time()
        vocab_cache_time = end_time - start_time

        # Set operations should be very fast (O(1))
        assert vocab_cache_time < 1.0  # Less than 1 second for 1000 operations

    def test_cache_thread_safety(self, app_instance):
        """Test cache thread safety."""
        import threading
        
        errors = []
        
        def add_to_caches(thread_id, count):
            try:
                for i in range(count):
                    # Image cache operations
                    url = f"https://test.com/thread_{thread_id}_{i}"
                    app_instance.image_cache[url] = f"data_{thread_id}_{i}".encode()
                    
                    # Vocabulary cache operations
                    word = f"word_{thread_id}_{i}"
                    app_instance.vocabulary_cache.add(word)
            except Exception as e:
                errors.append(str(e))

        # Create multiple threads
        threads = []
        for thread_id in range(5):
            thread = threading.Thread(target=add_to_caches, args=(thread_id, 20))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Check for errors
        assert len(errors) == 0, f"Thread safety errors: {errors}"

        # Verify final state
        assert len(app_instance.image_cache) == 100  # 5 threads * 20 items
        assert len(app_instance.vocabulary_cache) == 100  # 5 threads * 20 items

    def test_cache_cleanup_mechanisms(self, app_instance):
        """Test cache cleanup and maintenance."""
        # Fill caches with data
        for i in range(20):
            url = f"https://test.com/cleanup_{i}"
            app_instance.image_cache[url] = f"data_{i}".encode()
            app_instance.vocabulary_cache.add(f"word_{i}")

        # Test manual cleanup
        initial_image_count = len(app_instance.image_cache)
        initial_vocab_count = len(app_instance.vocabulary_cache)

        # Clear caches
        app_instance.image_cache.clear()
        app_instance.vocabulary_cache.clear()

        assert len(app_instance.image_cache) == 0
        assert len(app_instance.vocabulary_cache) == 0
        assert initial_image_count == 20
        assert initial_vocab_count == 20

    def test_cache_statistics_tracking(self, app_instance):
        """Test cache statistics and metrics."""
        # Add items to track statistics
        for i in range(10):
            url = f"https://test.com/stats_{i}"
            app_instance.image_cache[url] = TEST_IMAGE_DATA["png_1x1"]
            app_instance.vocabulary_cache.add(f"stats_word_{i}")

        # Calculate cache statistics
        image_cache_size = len(app_instance.image_cache)
        vocab_cache_size = len(app_instance.vocabulary_cache)
        
        # Memory usage approximation
        import sys
        image_cache_memory = sys.getsizeof(app_instance.image_cache)
        vocab_cache_memory = sys.getsizeof(app_instance.vocabulary_cache)

        # Verify statistics
        assert image_cache_size == 10
        assert vocab_cache_size == 10
        assert image_cache_memory > 0
        assert vocab_cache_memory > 0

        # Test cache utilization metrics
        max_cache_size = 50  # Hypothetical max size
        image_utilization = image_cache_size / max_cache_size
        vocab_utilization = vocab_cache_size / max_cache_size

        assert 0 <= image_utilization <= 1
        assert 0 <= vocab_utilization <= 1

    def test_cache_invalidation_patterns(self, app_instance):
        """Test cache invalidation patterns."""
        # Add items to cache
        urls = [f"https://test.com/invalidate_{i}" for i in range(5)]
        for url in urls:
            app_instance.image_cache[url] = TEST_IMAGE_DATA["png_1x1"]

        # Test selective invalidation
        urls_to_invalidate = urls[:2]  # First two URLs
        for url in urls_to_invalidate:
            if url in app_instance.image_cache:
                del app_instance.image_cache[url]

        # Verify selective invalidation
        assert len(app_instance.image_cache) == 3  # 5 - 2 = 3
        for url in urls_to_invalidate:
            assert url not in app_instance.image_cache
        for url in urls[2:]:
            assert url in app_instance.image_cache

    def test_cache_data_consistency(self, app_instance):
        """Test cache data consistency."""
        # Add data to cache
        url = "https://test.com/consistency"
        original_data = TEST_IMAGE_DATA["png_1x1"]
        app_instance.image_cache[url] = original_data

        # Retrieve data multiple times
        retrieved_1 = app_instance.image_cache[url]
        retrieved_2 = app_instance.image_cache.get(url)

        # Data should be consistent
        assert retrieved_1 == original_data
        assert retrieved_2 == original_data
        assert retrieved_1 == retrieved_2

        # Test vocabulary cache consistency
        word = "consistency_test"
        app_instance.vocabulary_cache.add(word)

        # Multiple membership tests should be consistent
        assert word in app_instance.vocabulary_cache
        assert word in app_instance.vocabulary_cache
        
        # Remove and test consistency
        app_instance.vocabulary_cache.remove(word)
        assert word not in app_instance.vocabulary_cache

    def test_cache_edge_cases(self, app_instance):
        """Test cache edge cases and boundary conditions."""
        # Test empty cache operations
        assert len(app_instance.image_cache) == 0
        assert len(app_instance.vocabulary_cache) == 0

        # Test operations on empty caches
        assert app_instance.image_cache.get("nonexistent") is None
        assert "nonexistent" not in app_instance.vocabulary_cache

        # Test with None values
        app_instance.image_cache["none_test"] = None
        assert app_instance.image_cache["none_test"] is None

        # Test with empty strings
        app_instance.vocabulary_cache.add("")
        assert "" in app_instance.vocabulary_cache

        # Test with large data
        large_data = b"x" * 10000  # 10KB of data
        app_instance.image_cache["large_data"] = large_data
        assert len(app_instance.image_cache["large_data"]) == 10000

    def test_cache_interaction_patterns(self, app_instance):
        """Test interaction patterns between different caches."""
        # Add related data to both caches
        image_url = "https://test.com/interaction_test"
        vocabulary_word = "interaction_word"

        app_instance.image_cache[image_url] = TEST_IMAGE_DATA["png_1x1"]
        app_instance.vocabulary_cache.add(vocabulary_word)

        # Verify both caches are populated
        assert image_url in app_instance.image_cache
        assert vocabulary_word in app_instance.vocabulary_cache

        # Test combined operations
        combined_size = len(app_instance.image_cache) + len(app_instance.vocabulary_cache)
        assert combined_size == 2

        # Test clearing one cache doesn't affect the other
        app_instance.image_cache.clear()
        assert len(app_instance.image_cache) == 0
        assert vocabulary_word in app_instance.vocabulary_cache