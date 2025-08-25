"""
Pytest configuration and shared fixtures.
"""
import pytest
from unittest.mock import Mock, MagicMock
import tkinter as tk
import tempfile
import os
from pathlib import Path


@pytest.fixture
def mock_config_manager():
    """Mock ConfigManager for testing."""
    mock = Mock()
    mock.get_api_keys.return_value = {
        'unsplash': 'test_unsplash_key',
        'openai': 'test_openai_key'
    }
    mock.get_paths.return_value = {
        'session_log': 'test_data/session_log.json',
        'vocabulary_csv': 'test_data/vocabulary.csv',
        'data_dir': 'test_data'
    }
    mock.get_settings.return_value = {
        'gpt_model': 'gpt-4o-mini',
        'max_description_length': 500
    }
    return mock


@pytest.fixture
def mock_api_response():
    """Mock API response data."""
    return {
        'results': [
            {
                'id': 'test_image_1',
                'urls': {
                    'small': 'https://example.com/small.jpg',
                    'regular': 'https://example.com/regular.jpg'
                },
                'alt_description': 'Test image description',
                'user': {'name': 'Test User'},
                'description': 'A test image'
            }
        ],
        'total': 1,
        'total_pages': 1
    }


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Esta es una descripción de prueba en español."
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_config_file(temp_data_dir):
    """Create a sample configuration file."""
    config_path = temp_data_dir / "config.ini"
    config_content = """
[API_KEYS]
unsplash_access_key = test_unsplash_key
openai_api_key = test_openai_key

[SETTINGS]
gpt_model = gpt-4o-mini
max_description_length = 500
"""
    config_path.write_text(config_content)
    return config_path


@pytest.fixture
def mock_requests_session():
    """Mock requests session for API calls."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'results': [],
        'total': 0,
        'total_pages': 0
    }
    mock_session.get.return_value = mock_response
    return mock_session


@pytest.fixture
def mock_image_response():
    """Mock image response for PIL testing."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\xcc\xdb\xd2\x00\x00\x00\x00IEND\xaeB`\x82'
    return mock_response


@pytest.fixture
def mock_search_results():
    """Mock search results for image search testing."""
    return [
        {
            'id': f'test_image_{i}',
            'urls': {
                'regular': f'https://images.unsplash.com/photo-{i}?w=400',
                'small': f'https://images.unsplash.com/photo-{i}?w=200'
            },
            'alt_description': f'Test image {i}',
            'user': {'name': f'Test User {i}'},
            'description': f'Description for image {i}'
        }
        for i in range(1, 11)
    ]


@pytest.fixture
def mock_large_vocabulary_cache():
    """Mock large vocabulary cache for performance testing."""
    return {f'palabra_{i}': f'word_{i}' for i in range(10000)}


@pytest.fixture
def mock_api_error_responses():
    """Mock API error responses for testing."""
    return {
        'rate_limit': requests.exceptions.HTTPError("429 Too Many Requests"),
        'unauthorized': requests.exceptions.HTTPError("401 Unauthorized"),
        'forbidden': requests.exceptions.HTTPError("403 Forbidden"),
        'timeout': requests.exceptions.Timeout("Request timed out"),
        'connection_error': requests.exceptions.ConnectionError("Failed to connect"),
        'server_error': requests.exceptions.HTTPError("500 Internal Server Error")
    }


@pytest.fixture
def performance_test_config():
    """Configuration for performance testing."""
    return {
        'max_memory_mb': 50,
        'max_response_time_seconds': 1.0,
        'min_cache_hit_rate': 0.7,
        'max_concurrent_threads': 10,
        'cache_size_limit': 10
    }


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv('UNSPLASH_ACCESS_KEY', 'test_unsplash_key')
    monkeypatch.setenv('OPENAI_API_KEY', 'test_openai_key')
    monkeypatch.setenv('GPT_MODEL', 'gpt-4o-mini')


@pytest.fixture
def no_gui(monkeypatch):
    """Disable GUI for headless testing."""
    def mock_mainloop():
        pass
    
    def mock_destroy():
        pass
    
    def mock_geometry(geometry_string):
        pass
    
    def mock_protocol(protocol, callback):
        pass
    
    def mock_bind(event, callback):
        pass
    
    def mock_focus_set():
        pass
    
    def mock_update_idletasks():
        pass
    
    def mock_after(delay, callback=None):
        return "mock_after_id"
    
    def mock_after_cancel(after_id):
        pass
    
    monkeypatch.setattr(tk.Tk, 'mainloop', mock_mainloop)
    monkeypatch.setattr(tk.Tk, 'destroy', mock_destroy)
    monkeypatch.setattr(tk.Tk, 'geometry', mock_geometry)
    monkeypatch.setattr(tk.Tk, 'protocol', mock_protocol)
    monkeypatch.setattr(tk.Tk, 'bind', mock_bind)
    monkeypatch.setattr(tk.Tk, 'focus_set', mock_focus_set)
    monkeypatch.setattr(tk.Tk, 'update_idletasks', mock_update_idletasks)
    monkeypatch.setattr(tk.Tk, 'after', mock_after)
    monkeypatch.setattr(tk.Tk, 'after_cancel', mock_after_cancel)


# Pytest markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "gui: mark test as requiring GUI"
    )
    config.addinivalue_line(
        "markers", "api: mark test as requiring external API"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "memory: mark test as memory usage test"
    )
    config.addinivalue_line(
        "markers", "timeout: mark test as timeout/rate limit test"
    )
    config.addinivalue_line(
        "markers", "edge_case: mark test as edge case test"
    )
    config.addinivalue_line(
        "markers", "infinite_collection: mark test as infinite collection prevention test"
    )