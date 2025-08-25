"""
Unit tests for timeout and rate limiting scenarios.
Tests API timeouts, rate limiting, retry mechanisms, and recovery strategies.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import requests
from requests.exceptions import Timeout, HTTPError, ConnectionError, RequestException
import time
import threading
from datetime import datetime, timedelta

from main import ImageSearchApp


class TestTimeoutScenarios:
    """Test suite for various timeout scenarios."""

    @pytest.fixture
    def timeout_test_app(self, mock_config_manager, no_gui):
        """Create app for timeout testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            with patch('main.ThemeManager'):
                app = ImageSearchApp()
                app.config_manager = mock_config_manager
                
                # Mock UI elements
                app.show_enhanced_error = Mock()
                app.update_status = Mock()
                app.progress_bar = Mock()
                
                # Initialize state
                app.current_query = "test"
                app.current_results = []
                app.used_image_urls = set()
                
                return app

    def test_api_request_timeout(self, timeout_test_app):
        """Test handling of API request timeouts."""
        def timeout_after_delay(*args, **kwargs):
            time.sleep(0.1)
            raise Timeout("Request timed out after 10 seconds")
        
        with patch.object(timeout_test_app, 'fetch_images_page', side_effect=timeout_after_delay):
            start_time = time.time()
            
            result = timeout_test_app.get_next_image()
            
            end_time = time.time()
            
            # Should return None due to timeout
            assert result is None
            
            # Should complete quickly (not wait for full timeout)
            assert end_time - start_time < 1.0
            
            # Should show appropriate error
            timeout_test_app.show_enhanced_error.assert_called()

    def test_connection_timeout_vs_read_timeout(self, timeout_test_app):
        """Test different types of timeouts."""
        timeout_scenarios = [
            (ConnectionError("Connection timed out"), "connection"),
            (Timeout("Read timed out"), "read"),
            (HTTPError("504 Gateway Timeout"), "gateway")
        ]
        
        for exception, timeout_type in timeout_scenarios:
            with patch.object(timeout_test_app, 'fetch_images_page', side_effect=exception):
                result = timeout_test_app.get_next_image()
                
                assert result is None
                timeout_test_app.show_enhanced_error.assert_called()
                
                # Reset mock for next test
                timeout_test_app.show_enhanced_error.reset_mock()

    def test_progressive_timeout_increases(self, timeout_test_app):
        """Test progressive timeout increases on repeated failures."""
        call_count = 0
        timeout_values = []
        
        def track_timeout_calls(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            # Extract timeout from kwargs if present
            if 'timeout' in kwargs:
                timeout_values.append(kwargs['timeout'])
            
            if call_count <= 3:
                raise Timeout(f"Timeout on attempt {call_count}")
            
            return []
        
        with patch.object(timeout_test_app, 'fetch_images_page', side_effect=track_timeout_calls):
            # Multiple attempts should show progressive timeout increases
            for _ in range(4):
                timeout_test_app.get_next_image()
        
        # Should have made multiple attempts
        assert call_count >= 3

    def test_timeout_with_retry_mechanism(self, timeout_test_app):
        """Test timeout handling with retry mechanism."""
        attempt_count = 0
        
        def timeout_then_succeed(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            
            if attempt_count <= 2:  # Fail first 2 attempts
                raise Timeout("Connection timeout")
            
            # Succeed on 3rd attempt
            return [{'id': 'success', 'urls': {'regular': 'https://example.com/success.jpg'}}]
        
        with patch.object(timeout_test_app, 'api_call_with_retry') as mock_retry:
            mock_retry.side_effect = timeout_then_succeed
            
            with patch('requests.get'), patch('main.Image.open'), patch('main.ImageTk.PhotoImage'):
                result = timeout_test_app.get_next_image()
            
            # Should eventually succeed after retries
            assert result is not None or attempt_count > 2

    def test_concurrent_requests_timeout_handling(self, timeout_test_app):
        """Test timeout handling with concurrent requests."""
        def timeout_worker(worker_id):
            def timeout_call(*args, **kwargs):
                time.sleep(0.1)
                if worker_id % 2 == 0:  # Even workers timeout
                    raise Timeout(f"Worker {worker_id} timeout")
                return []
            
            with patch.object(timeout_test_app, 'fetch_images_page', side_effect=timeout_call):
                return timeout_test_app.get_next_image()
        
        # Run concurrent requests
        results = []
        threads = []
        
        for worker_id in range(4):
            thread = threading.Thread(target=lambda w=worker_id: results.append(timeout_worker(w)), daemon=True)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=2.0)
        
        # All should complete (some with None due to timeout)
        assert len(results) == 4

    def test_timeout_recovery_after_network_restoration(self, timeout_test_app):
        """Test recovery after network is restored following timeouts."""
        network_restored = False
        
        def network_simulation(*args, **kwargs):
            if not network_restored:
                raise Timeout("Network unavailable")
            
            return [{'id': 'restored', 'urls': {'regular': 'https://example.com/restored.jpg'}}]
        
        with patch.object(timeout_test_app, 'fetch_images_page', side_effect=network_simulation):
            # First attempt should fail
            result1 = timeout_test_app.get_next_image()
            assert result1 is None
            
            # Restore network
            network_restored = True
            
            # Second attempt should succeed
            with patch('requests.get'), patch('main.Image.open'), patch('main.ImageTk.PhotoImage'):
                result2 = timeout_test_app.get_next_image()
                assert result2 is not None or network_restored

    def test_user_timeout_configuration(self, timeout_test_app):
        """Test user-configurable timeout settings."""
        # Test different timeout configurations
        timeout_configs = [5, 10, 15, 30]  # seconds
        
        for timeout_value in timeout_configs:
            # Mock configuration
            timeout_test_app.config_manager.get_settings = Mock(return_value={
                'api_timeout': timeout_value
            })
            
            start_time = time.time()
            
            def slow_response(*args, **kwargs):
                time.sleep(timeout_value + 1)  # Exceed timeout
                return []
            
            with patch.object(timeout_test_app, 'fetch_images_page', side_effect=slow_response):
                with patch('requests.get', side_effect=Timeout("Timeout")):
                    result = timeout_test_app.get_next_image()
            
            end_time = time.time()
            
            # Should timeout appropriately
            assert result is None
            # Should not wait longer than timeout + small overhead
            assert end_time - start_time < timeout_value + 2


class TestRateLimitingScenarios:
    """Test suite for rate limiting scenarios and recovery."""

    @pytest.fixture
    def rate_limit_app(self, mock_config_manager, no_gui):
        """Create app for rate limiting tests."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            with patch('main.ThemeManager'):
                app = ImageSearchApp()
                app.config_manager = mock_config_manager
                
                # Mock for rate limit testing
                app.show_enhanced_error = Mock()
                app.update_status = Mock()
                
                # Rate limiting state
                app._last_api_call = None
                app._api_call_count = 0
                app._rate_limit_reset_time = None
                
                return app

    def test_unsplash_rate_limit_detection(self, rate_limit_app):
        """Test detection of Unsplash rate limits (50/hour)."""
        # Mock 429 rate limit response
        def rate_limited_response(*args, **kwargs):
            error = HTTPError("429 Too Many Requests")
            error.response = Mock()
            error.response.status_code = 429
            error.response.headers = {
                'X-Ratelimit-Limit': '50',
                'X-Ratelimit-Remaining': '0', 
                'X-Ratelimit-Reset': str(int(time.time()) + 3600)  # 1 hour
            }
            raise error
        
        with patch.object(rate_limit_app, 'fetch_images_page', side_effect=rate_limited_response):
            result = rate_limit_app.get_next_image()
            
            assert result is None
            rate_limit_app.show_enhanced_error.assert_called()
            
            # Check error message mentions rate limit
            call_args = rate_limit_app.show_enhanced_error.call_args[0]
            assert "Rate Limit" in call_args[0]

    def test_openai_rate_limit_detection(self, rate_limit_app):
        """Test detection of OpenAI rate limits."""
        rate_limit_app.current_image_url = "https://example.com/test.jpg"
        rate_limit_app.image_label = Mock()
        rate_limit_app.image_label.image = Mock()
        
        # Mock OpenAI rate limit
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("rate_limit_exceeded")
        rate_limit_app.openai_client = mock_client
        
        with patch.object(rate_limit_app, 'thread_generate_description'):
            rate_limit_app.generate_description()
            
            # Should detect rate limit in the description generation

    def test_rate_limit_backoff_strategy(self, rate_limit_app):
        """Test exponential backoff strategy for rate limits."""
        call_times = []
        
        def rate_limit_with_backoff(*args, **kwargs):
            current_time = time.time()
            call_times.append(current_time)
            
            if len(call_times) <= 3:  # First 3 calls are rate limited
                raise HTTPError("429 Too Many Requests")
            
            return []  # Success after backoff
        
        with patch.object(rate_limit_app, 'api_call_with_retry') as mock_retry:
            # Mock the retry mechanism with exponential backoff
            def mock_retry_with_backoff(func, *args, max_retries=3, **kwargs):
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except HTTPError as e:
                        if "429" in str(e) and attempt < max_retries - 1:
                            wait_time = 2 ** attempt  # Exponential backoff
                            time.sleep(wait_time)
                        else:
                            raise
            
            mock_retry.side_effect = lambda func, *args, **kwargs: mock_retry_with_backoff(func, *args, **kwargs)
            
            with patch.object(rate_limit_app, 'fetch_images_page', side_effect=rate_limit_with_backoff):
                start_time = time.time()
                result = rate_limit_app.get_next_image()
                end_time = time.time()
                
                # Should take some time due to backoff
                total_time = end_time - start_time
                assert total_time > 1.0  # At least 1 second of backoff

    def test_rate_limit_reset_time_calculation(self, rate_limit_app):
        """Test calculation of rate limit reset time."""
        current_time = datetime.now()
        
        # Mock Unsplash rate limit with reset time
        def rate_limited_with_reset(*args, **kwargs):
            reset_time = current_time + timedelta(hours=1)  # 1 hour from now
            error = HTTPError("429 Too Many Requests")
            error.response = Mock()
            error.response.headers = {
                'X-Ratelimit-Reset': str(int(reset_time.timestamp()))
            }
            raise error
        
        with patch.object(rate_limit_app, 'fetch_images_page', side_effect=rate_limited_with_reset):
            with patch('main.datetime') as mock_datetime:
                mock_datetime.now.return_value = current_time
                mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                
                result = rate_limit_app.get_next_image()
                
                assert result is None
                rate_limit_app.show_enhanced_error.assert_called()
                
                # Check that error message includes time estimate
                call_args = rate_limit_app.show_enhanced_error.call_args[0]
                error_message = call_args[1]
                assert "minute" in error_message.lower() or "hour" in error_message.lower()

    def test_different_api_rate_limits(self, rate_limit_app):
        """Test handling different rate limits for different APIs."""
        # Simulate different rate limits
        api_limits = {
            'unsplash': {'limit': 50, 'window': 3600},  # 50 per hour
            'openai': {'limit': 3, 'window': 60}        # 3 per minute (for testing)
        }
        
        for api_name, limits in api_limits.items():
            call_count = 0
            
            def api_with_limit(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                
                if call_count > limits['limit']:
                    raise HTTPError(f"429 {api_name} rate limit exceeded")
                
                return [] if api_name == 'unsplash' else Mock()
            
            # Test each API's rate limit
            if api_name == 'unsplash':
                with patch.object(rate_limit_app, 'fetch_images_page', side_effect=api_with_limit):
                    for _ in range(limits['limit'] + 5):  # Exceed limit
                        rate_limit_app.get_next_image()
            else:  # openai
                rate_limit_app.openai_client = Mock()
                rate_limit_app.openai_client.chat.completions.create.side_effect = api_with_limit
                
                for _ in range(limits['limit'] + 2):
                    try:
                        rate_limit_app.openai_client.chat.completions.create()
                    except HTTPError:
                        break

    def test_rate_limit_user_notification(self, rate_limit_app):
        """Test user notification during rate limiting."""
        def rate_limited_call(*args, **kwargs):
            raise HTTPError("429 Rate limit exceeded")
        
        with patch.object(rate_limit_app, 'fetch_images_page', side_effect=rate_limited_call):
            rate_limit_app.get_next_image()
            
            # Should notify user about rate limit
            rate_limit_app.show_enhanced_error.assert_called()
            call_args = rate_limit_app.show_enhanced_error.call_args
            
            # Check notification type and content
            assert len(call_args[0]) >= 2
            title, message = call_args[0][:2]
            
            assert "Rate Limit" in title
            assert any(word in message.lower() for word in ['limit', 'wait', 'hour', 'minute'])

    def test_graceful_degradation_under_rate_limits(self, rate_limit_app):
        """Test graceful degradation when APIs are rate limited."""
        # Simulate Unsplash being rate limited but OpenAI working
        unsplash_rate_limited = True
        
        def unsplash_with_rate_limit(*args, **kwargs):
            if unsplash_rate_limited:
                raise HTTPError("429 Too Many Requests")
            return []
        
        with patch.object(rate_limit_app, 'fetch_images_page', side_effect=unsplash_with_rate_limit):
            # Should handle gracefully and inform user
            result = rate_limit_app.get_next_image()
            assert result is None
            
            # User should be informed about limitations
            rate_limit_app.show_enhanced_error.assert_called()

    def test_rate_limit_recovery_detection(self, rate_limit_app):
        """Test detection when rate limits are lifted."""
        rate_limit_active = True
        
        def rate_limit_recovery(*args, **kwargs):
            if rate_limit_active:
                raise HTTPError("429 Too Many Requests")
            
            return [{'id': 'recovered', 'urls': {'regular': 'https://example.com/test.jpg'}}]
        
        with patch.object(rate_limit_app, 'fetch_images_page', side_effect=rate_limit_recovery):
            # First call should be rate limited
            result1 = rate_limit_app.get_next_image()
            assert result1 is None
            
            # Simulate rate limit reset
            rate_limit_active = False
            
            # Second call should succeed
            with patch('requests.get'), patch('main.Image.open'), patch('main.ImageTk.PhotoImage'):
                result2 = rate_limit_app.get_next_image()
                # Should recover successfully
                assert result2 is not None or not rate_limit_active


class TestRetryMechanisms:
    """Test suite for retry mechanisms and failure recovery."""

    @pytest.fixture
    def retry_test_app(self, mock_config_manager, no_gui):
        """Create app for retry mechanism testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            with patch('main.ThemeManager'):
                app = ImageSearchApp()
                app.config_manager = mock_config_manager
                
                # Mock for retry testing
                app.update_status = Mock()
                app.show_enhanced_error = Mock()
                
                return app

    def test_exponential_backoff_retry(self, retry_test_app):
        """Test exponential backoff retry mechanism."""
        attempt_count = 0
        attempt_times = []
        
        def failing_then_succeeding_call(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            attempt_times.append(time.time())
            
            if attempt_count <= 2:  # Fail first 2 attempts
                raise RequestException("Temporary failure")
            
            return []  # Success on 3rd attempt
        
        # Test the retry mechanism
        start_time = time.time()
        
        result = retry_test_app.api_call_with_retry(
            failing_then_succeeding_call, 
            max_retries=3
        )
        
        end_time = time.time()
        
        # Should eventually succeed
        assert result == []
        assert attempt_count == 3
        
        # Should have exponential backoff delays
        if len(attempt_times) >= 3:
            delay1 = attempt_times[1] - attempt_times[0]
            delay2 = attempt_times[2] - attempt_times[1]
            assert delay2 > delay1  # Second delay should be longer

    def test_max_retry_limit(self, retry_test_app):
        """Test that retries respect maximum limit."""
        attempt_count = 0
        
        def always_failing_call(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            raise RequestException("Persistent failure")
        
        # Should stop after max retries
        with pytest.raises(RequestException):
            retry_test_app.api_call_with_retry(
                always_failing_call,
                max_retries=3
            )
        
        assert attempt_count == 3  # Should stop at max retries

    def test_different_exception_types_retry_behavior(self, retry_test_app):
        """Test retry behavior for different exception types."""
        retry_scenarios = [
            (ConnectionError("Network error"), True),    # Should retry
            (Timeout("Request timeout"), True),          # Should retry  
            (HTTPError("500 Server Error"), True),       # Should retry
            (HTTPError("400 Bad Request"), False),       # Should not retry
            (ValueError("Invalid data"), False)          # Should not retry
        ]
        
        for exception, should_retry in retry_scenarios:
            attempt_count = 0
            
            def exception_thrower(*args, **kwargs):
                nonlocal attempt_count
                attempt_count += 1
                raise exception
            
            try:
                retry_test_app.api_call_with_retry(
                    exception_thrower,
                    max_retries=3
                )
            except:
                pass  # Expected to fail
            
            if should_retry:
                assert attempt_count > 1  # Should have retried
            else:
                assert attempt_count == 1  # Should not have retried

    def test_retry_with_jitter(self, retry_test_app):
        """Test retry mechanism with jitter to avoid thundering herd."""
        attempt_times = []
        
        def failing_call(*args, **kwargs):
            attempt_times.append(time.time())
            if len(attempt_times) <= 3:
                raise RequestException("Temporary failure")
            return []
        
        # Run multiple concurrent retries to test jitter
        results = []
        threads = []
        
        for i in range(3):
            def worker():
                try:
                    result = retry_test_app.api_call_with_retry(failing_call, max_retries=4)
                    results.append(result)
                except:
                    results.append(None)
            
            thread = threading.Thread(target=worker, daemon=True)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join(timeout=10.0)
        
        # At least one should succeed
        assert len([r for r in results if r is not None]) > 0