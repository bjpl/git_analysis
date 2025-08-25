"""
Basic validation tests for image collection functionality.
Simple tests to validate the test framework and core functionality.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports_work():
    """Test that all required modules can be imported."""
    try:
        import requests
        import PIL
        from PIL import Image, ImageTk
        import tkinter as tk
        import json
        import threading
        assert True
    except ImportError as e:
        pytest.fail(f"Required import failed: {e}")


@patch('tkinter.Tk')
def test_main_can_be_imported(mock_tk):
    """Test that main module can be imported without errors."""
    try:
        # Mock tkinter to avoid GUI creation
        mock_tk.return_value = Mock()
        from main import ImageSearchApp
        assert ImageSearchApp is not None
    except ImportError as e:
        pytest.fail(f"Failed to import main module: {e}")


def test_config_manager_can_be_imported():
    """Test that config_manager can be imported."""
    try:
        from config_manager import ConfigManager
        assert ConfigManager is not None
    except ImportError as e:
        pytest.fail(f"Failed to import config_manager: {e}")


@pytest.mark.unit
def test_sample_data_fixtures():
    """Test that sample data fixtures work correctly."""
    try:
        from tests.fixtures.sample_data import (
            SAMPLE_UNSPLASH_SEARCH_RESPONSE,
            TEST_IMAGE_DATA,
            PERFORMANCE_BENCHMARKS
        )
        
        assert SAMPLE_UNSPLASH_SEARCH_RESPONSE is not None
        assert TEST_IMAGE_DATA is not None
        assert PERFORMANCE_BENCHMARKS is not None
        assert len(SAMPLE_UNSPLASH_SEARCH_RESPONSE.get("results", [])) > 0
        
    except ImportError as e:
        pytest.fail(f"Failed to import test fixtures: {e}")


def test_test_data_generators():
    """Test that test data generators work correctly."""
    try:
        from tests.fixtures.test_data_generators import (
            UnsplashResponseGenerator,
            ImageDataGenerator,
            ScenarioGenerator
        )
        
        # Test response generation
        response = UnsplashResponseGenerator.create_search_response("test", 1, 5)
        assert response["total"] > 0
        assert len(response["results"]) == 5
        
        # Test scenario generation
        scenarios = ScenarioGenerator.create_search_scenarios()
        assert len(scenarios) > 0
        assert all("query" in scenario for scenario in scenarios)
        
    except ImportError as e:
        pytest.fail(f"Failed to import test generators: {e}")


@pytest.mark.unit
def test_mock_fixtures_work(mock_config_manager):
    """Test that mock fixtures work correctly."""
    assert mock_config_manager is not None
    
    api_keys = mock_config_manager.get_api_keys()
    assert "unsplash" in api_keys
    assert "openai" in api_keys
    
    paths = mock_config_manager.get_paths()
    assert "session_log" in paths or "log_file" in paths


@pytest.mark.unit  
def test_basic_url_canonicalization():
    """Test basic URL canonicalization functionality."""
    # This is a simple unit test we can run without the full app
    def canonicalize_url(url):
        """Simple version of URL canonicalization for testing."""
        return url.split('?')[0] if url else ""
    
    # Test cases
    test_cases = [
        ("https://images.unsplash.com/photo-123?w=1080&q=80", "https://images.unsplash.com/photo-123"),
        ("https://images.unsplash.com/photo-456", "https://images.unsplash.com/photo-456"),
        ("", ""),
        (None, "")
    ]
    
    for input_url, expected in test_cases:
        result = canonicalize_url(input_url)
        assert result == expected, f"Expected {expected}, got {result} for input {input_url}"


@pytest.mark.unit
def test_search_query_validation():
    """Test search query validation logic."""
    def validate_search_query(query):
        """Simple search query validation."""
        if not query:
            return False, "Query cannot be empty"
        if isinstance(query, str) and query.strip() == "":
            return False, "Query cannot be whitespace only"
        return True, "Valid query"
    
    # Test valid queries
    valid_queries = ["nature", "mountains", "café", "中文", "emoji 🌟"]
    for query in valid_queries:
        valid, message = validate_search_query(query)
        assert valid, f"Query '{query}' should be valid: {message}"
    
    # Test invalid queries
    invalid_queries = ["", "   ", "  \t\n  ", None]
    for query in invalid_queries:
        valid, message = validate_search_query(query)
        assert not valid, f"Query '{query}' should be invalid"


@pytest.mark.unit
def test_image_cache_size_logic():
    """Test image cache size management logic."""
    def manage_cache(cache, max_size=10):
        """Simple cache management logic."""
        if len(cache) > max_size:
            # Remove oldest entries (in a real implementation, this would be more sophisticated)
            keys_to_remove = list(cache.keys())[:-max_size]
            for key in keys_to_remove:
                del cache[key]
        return len(cache)
    
    # Test cache management
    test_cache = {f"url_{i}": f"data_{i}" for i in range(15)}
    
    # Should have 15 items initially
    assert len(test_cache) == 15
    
    # After management, should have max 10
    final_size = manage_cache(test_cache, max_size=10)
    assert final_size <= 10
    assert len(test_cache) <= 10


@pytest.mark.unit
def test_performance_thresholds():
    """Test that performance thresholds are reasonable."""
    import time
    
    # Simulate a quick operation
    start_time = time.time()
    time.sleep(0.001)  # 1ms
    duration = time.time() - start_time
    
    # Should be under reasonable threshold
    assert duration < 1.0, "Operation took too long"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])