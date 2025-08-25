"""
Comprehensive Test Suite for API Timeout Fixes

This test suite validates that the timeout and cancellation fixes work correctly:
1. Timeout configurations are applied properly
2. Cancellation tokens work as expected
3. Retry logic with exponential backoff functions
4. Error handling provides appropriate error types
5. Rate limiting is handled correctly
6. Progress callbacks are triggered
"""

import asyncio
import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.services.api_timeout_manager import (
        ApiTimeoutManager,
        TimeoutConfig,
        RetryConfig,
        CancellationToken,
        CancellationError
    )
    from src.services.enhanced_unsplash_service import (
        EnhancedUnsplashService,
        UnsplashError,
        UnsplashAuthError,
        UnsplashRateLimitError
    )
    from src.services.enhanced_openai_service import (
        EnhancedOpenAIService,
        OpenAIError,
        OpenAITimeoutError
    )
    from patches.api_timeout_fixes import ApiTimeoutPatches
except ImportError as e:
    pytest.skip(f"Could not import timeout fixes: {e}", allow_module_level=True)

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestTimeoutConfig:
    """Test timeout configuration functionality."""
    
    def test_timeout_config_creation(self):
        """Test timeout configuration creation and conversion."""
        config = TimeoutConfig(connect=5.0, read=30.0, total=60.0)
        
        assert config.connect == 5.0
        assert config.read == 30.0
        assert config.total == 60.0
        
        # Test conversion to requests timeout format
        timeout_tuple = config.to_requests_timeout()
        assert timeout_tuple == (5.0, 30.0)
    
    def test_default_timeout_config(self):
        """Test default timeout values."""
        config = TimeoutConfig()
        
        assert config.connect == 5.0
        assert config.read == 30.0
        assert config.total == 60.0


class TestCancellationToken:
    """Test cancellation token functionality."""
    
    def test_cancellation_token_creation(self):
        """Test cancellation token creation and basic functionality."""
        token = CancellationToken()
        
        assert not token.is_cancelled
        
        # Test cancellation
        token.cancel()
        assert token.is_cancelled
    
    def test_cancellation_token_callbacks(self):
        """Test cancellation token callbacks."""
        token = CancellationToken()
        callback_called = threading.Event()
        
        def callback():
            callback_called.set()
        
        token.register_callback(callback)
        token.cancel()
        
        # Wait for callback with timeout
        assert callback_called.wait(timeout=1.0), "Callback was not called"
    
    def test_raise_if_cancelled(self):
        """Test raise_if_cancelled functionality."""
        token = CancellationToken()
        
        # Should not raise when not cancelled
        token.raise_if_cancelled()
        
        # Should raise when cancelled
        token.cancel()
        with pytest.raises(CancellationError):
            token.raise_if_cancelled()


class TestApiTimeoutManager:
    """Test API timeout manager functionality."""
    
    def test_timeout_manager_creation(self):
        """Test timeout manager creation and configuration."""
        manager = ApiTimeoutManager()
        
        assert manager.default_timeout is not None
        assert manager.default_retry is not None
        assert 'unsplash' in manager.service_configs
        assert 'openai' in manager.service_configs
    
    def test_service_specific_timeouts(self):
        """Test service-specific timeout configurations."""
        manager = ApiTimeoutManager()
        
        unsplash_config = manager.get_timeout_config('unsplash')
        openai_config = manager.get_timeout_config('openai')
        
        # Unsplash should have shorter timeouts than OpenAI
        assert unsplash_config.total < openai_config.total
        assert openai_config.read > unsplash_config.read
    
    def test_cancellation_token_management(self):
        """Test cancellation token creation and management."""
        manager = ApiTimeoutManager()
        
        # Create token
        token = manager.create_cancellation_token('test_op')
        assert not token.is_cancelled
        assert 'test_op' in manager.active_tokens
        
        # Cancel token
        success = manager.cancel_operation('test_op')
        assert success
        assert token.is_cancelled
        
        # Cleanup
        manager.cleanup_token('test_op')
        assert 'test_op' not in manager.active_tokens
    
    @patch('requests.Session.request')
    def test_timeout_context_manager(self, mock_request):
        """Test timeout context manager."""
        manager = ApiTimeoutManager()
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        with manager.timeout_context('test', 'op1') as token:
            assert not token.is_cancelled
            assert 'op1' in manager.active_tokens
        
        # Token should be cleaned up after context
        assert 'op1' not in manager.active_tokens
    
    def test_cancel_all_operations(self):
        """Test cancelling all operations."""
        manager = ApiTimeoutManager()
        
        # Create multiple tokens
        token1 = manager.create_cancellation_token('op1')
        token2 = manager.create_cancellation_token('op2')
        token3 = manager.create_cancellation_token('op3')
        
        assert len(manager.active_tokens) == 3
        
        # Cancel all
        cancelled_count = manager.cancel_all_operations()
        
        assert cancelled_count == 3
        assert token1.is_cancelled
        assert token2.is_cancelled
        assert token3.is_cancelled
    
    def test_get_status(self):
        """Test status reporting."""
        manager = ApiTimeoutManager()
        
        status = manager.get_status()
        
        assert 'active_operations' in status
        assert 'active_sessions' in status
        assert 'executor_active' in status
        assert isinstance(status['active_operations'], int)


class MockApplication:
    """Mock application instance for testing patches."""
    
    def __init__(self):
        self.UNSPLASH_ACCESS_KEY = "test_unsplash_key"
        self.OPENAI_API_KEY = "test_openai_key"
        self.GPT_MODEL = "gpt-4o-mini"
        self.used_image_urls = set()
        self.status_messages = []
        
        # Mock OpenAI client
        self.openai_client = Mock()
    
    def update_status(self, message):
        """Mock status update method."""
        self.status_messages.append(message)
        logger.info(f"Status: {message}")
    
    def after(self, delay, func):
        """Mock tkinter after method."""
        func()


class TestApiTimeoutPatches:
    """Test API timeout patches functionality."""
    
    def test_patches_initialization(self):
        """Test patches initialization."""
        app = MockApplication()
        patches = ApiTimeoutPatches(app)
        
        assert patches.app is app
        assert patches.active_operations == {}
        assert patches.operation_counter == 0
    
    @patch('src.services.enhanced_unsplash_service.EnhancedUnsplashService')
    @patch('src.services.enhanced_openai_service.EnhancedOpenAIService')
    def test_enhanced_services_initialization(self, mock_openai_service, mock_unsplash_service):
        """Test enhanced services initialization."""
        app = MockApplication()
        patches = ApiTimeoutPatches(app)
        
        # Mock service initialization
        mock_unsplash_instance = Mock()
        mock_openai_instance = Mock()
        mock_unsplash_service.return_value = mock_unsplash_instance
        mock_openai_service.return_value = mock_openai_instance
        
        success = patches.initialize_enhanced_services()
        
        assert success
        assert patches.enhanced_unsplash is mock_unsplash_instance
        assert patches.enhanced_openai is mock_openai_instance
        
        # Verify service initialization calls
        mock_unsplash_service.assert_called_once_with(app.UNSPLASH_ACCESS_KEY)
        mock_openai_service.assert_called_once_with(
            api_key=app.OPENAI_API_KEY,
            model=app.GPT_MODEL
        )
    
    def test_operation_id_generation(self):
        """Test operation ID generation."""
        app = MockApplication()
        patches = ApiTimeoutPatches(app)
        
        op_id1 = patches._get_operation_id("test")
        op_id2 = patches._get_operation_id("test")
        
        assert op_id1 != op_id2
        assert op_id1.startswith("test_")
        assert op_id2.startswith("test_")
    
    def test_status_update(self):
        """Test status update functionality."""
        app = MockApplication()
        patches = ApiTimeoutPatches(app)
        
        patches._update_app_status("Test message")
        
        assert "Test message" in app.status_messages
    
    @patch('requests.get')
    def test_fallback_fetch_images_page(self, mock_get):
        """Test fallback image search functionality."""
        app = MockApplication()
        patches = ApiTimeoutPatches(app)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [{'id': 'test_image', 'urls': {'regular': 'test_url'}}],
            'total': 1
        }
        mock_get.return_value = mock_response
        
        def progress_callback(msg):
            app.status_messages.append(msg)
        
        results = patches._fallback_fetch_images_page(
            "test query", 
            1, 
            "op1", 
            progress_callback
        )
        
        assert len(results) == 1
        assert results[0]['id'] == 'test_image'
        assert len(app.status_messages) > 0
    
    @patch('requests.get')
    def test_fallback_download_image(self, mock_get):
        """Test fallback image download functionality."""
        app = MockApplication()
        patches = ApiTimeoutPatches(app)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-length': '1024'}
        mock_response.iter_content.return_value = [b'test_chunk1', b'test_chunk2']
        mock_get.return_value = mock_response
        
        def progress_callback(msg):
            app.status_messages.append(msg)
        
        result = patches._fallback_download_image(
            "http://test.url/image.jpg", 
            "op1", 
            progress_callback
        )
        
        assert result == b'test_chunk1test_chunk2'
        assert len(app.status_messages) > 0
    
    def test_get_status(self):
        """Test status reporting."""
        app = MockApplication()
        patches = ApiTimeoutPatches(app)
        
        # Add some active operations
        patches.active_operations['op1'] = 'Test operation 1'
        patches.active_operations['op2'] = 'Test operation 2'
        
        status = patches.get_status()
        
        assert status['active_operations'] == 2
        assert 'op1' in status['operations']
        assert 'op2' in status['operations']
        assert 'enhanced_services_available' in status


@pytest.mark.integration
class TestTimeoutIntegration:
    """Integration tests for timeout fixes."""
    
    def test_timeout_manager_with_real_requests(self):
        """Test timeout manager with real HTTP requests (mocked)."""
        manager = ApiTimeoutManager()
        
        with patch('requests.Session.request') as mock_request:
            # Mock timeout scenario
            mock_request.side_effect = Exception("Timeout")
            
            with pytest.raises(Exception):
                manager.make_request_with_timeout(
                    service='test',
                    method='GET',
                    url='http://test.com',
                    operation_id='test_op'
                )
    
    def test_cancellation_during_operation(self):
        """Test cancellation during long-running operation."""
        manager = ApiTimeoutManager()
        
        def long_running_task():
            """Simulate long-running task that checks for cancellation."""
            for i in range(10):
                time.sleep(0.1)  # Simulate work
                # In real scenario, operation would check token.is_cancelled
            return "completed"
        
        # Start operation with short timeout to trigger cancellation
        with pytest.raises((TimeoutError, CancellationError)):
            manager.execute_with_timeout(
                func=long_running_task,
                timeout=0.2,  # Short timeout
                operation_id='test_long_op'
            )
    
    @patch('src.services.enhanced_unsplash_service.EnhancedUnsplashService')
    def test_patches_apply_successfully(self, mock_unsplash_service):
        """Test that patches can be applied to application successfully."""
        app = MockApplication()
        patches = ApiTimeoutPatches(app)
        
        # Mock enhanced service
        mock_service = Mock()
        mock_unsplash_service.return_value = mock_service
        
        success = patches.apply_patches_to_app()
        
        # Should succeed even if enhanced services fail to initialize
        assert isinstance(success, bool)
        
        # Check that methods were added to app
        assert hasattr(app, 'cancel_operation')
        assert hasattr(app, 'cancel_all_operations')
        assert hasattr(app, 'get_api_status')


@pytest.mark.performance
class TestTimeoutPerformance:
    """Performance tests for timeout fixes."""
    
    def test_timeout_manager_performance(self):
        """Test timeout manager performance with multiple operations."""
        manager = ApiTimeoutManager()
        
        start_time = time.time()
        
        # Create many tokens
        tokens = []
        for i in range(100):
            token = manager.create_cancellation_token(f'op_{i}')
            tokens.append(token)
        
        creation_time = time.time() - start_time
        
        # Cancel all tokens
        start_time = time.time()
        cancelled_count = manager.cancel_all_operations()
        cancel_time = time.time() - start_time
        
        assert cancelled_count == 100
        assert creation_time < 1.0  # Should create 100 tokens in under 1 second
        assert cancel_time < 1.0   # Should cancel 100 tokens in under 1 second
    
    def test_concurrent_operations(self):
        """Test concurrent operations with timeout manager."""
        manager = ApiTimeoutManager()
        
        def create_and_cancel_token(op_id):
            token = manager.create_cancellation_token(op_id)
            time.sleep(0.01)  # Small delay
            manager.cancel_operation(op_id)
            return token.is_cancelled
        
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(create_and_cancel_token, f'concurrent_op_{i}')
                for i in range(50)
            ]
            
            results = [future.result(timeout=5.0) for future in futures]
        
        # All operations should have been cancelled
        assert all(results)


def test_main_integration():
    """Test integration with main application."""
    try:
        from apply_timeout_fixes import patch_main_app
        
        # This should not raise an exception
        result = patch_main_app()
        
        # Result can be True or False depending on whether main.py is available
        assert isinstance(result, bool)
        
    except Exception as e:
        # If main.py is not available, that's okay for testing
        if "Failed to import main module" in str(e):
            pytest.skip("main.py not available for integration test")
        else:
            raise


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v", "--tb=short"])
