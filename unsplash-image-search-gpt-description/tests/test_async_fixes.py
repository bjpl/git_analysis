"""
Test suite for async/await fixes validation.

Tests the async coordinator, thread safety utilities, and async services
to ensure all async-related bugs have been resolved.
"""

import pytest
import asyncio
import threading
import time
import tkinter as tk
from unittest.mock import Mock, AsyncMock, patch
from concurrent.futures import Future

from src.utils.async_coordinator import AsyncCoordinator, get_coordinator, async_task
from src.utils.ui_thread_safe import (
    ThreadSafeUI, ui_thread_safe, is_main_thread, 
    create_thread_safe_callback, AsyncUIUpdater
)
from src.services.async_unsplash_service import (
    AsyncUnsplashService, UnsplashImage, SearchResult
)
from src.services.async_openai_service import (
    AsyncOpenAIService, ImageAnalysisRequest, AnalysisResult, 
    VocabularyExtractionRequest, VocabularyResult
)


class TestAsyncCoordinator:
    """Test the AsyncCoordinator for proper async/thread integration."""
    
    def test_coordinator_lifecycle(self):
        """Test starting and stopping the coordinator."""
        coordinator = AsyncCoordinator()
        
        assert not coordinator.is_running()
        
        # Start coordinator
        coordinator.start()
        time.sleep(0.1)  # Allow startup
        
        assert coordinator.is_running()
        
        # Stop coordinator
        coordinator.stop()
        time.sleep(0.1)  # Allow shutdown
        
        assert not coordinator.is_running()
    
    @pytest.mark.asyncio
    async def test_run_async_operation(self):
        """Test running async operations through coordinator."""
        coordinator = AsyncCoordinator()
        coordinator.start()
        
        try:
            result_container = {"value": None, "error": None}
            
            async def test_coro():
                await asyncio.sleep(0.01)
                return "success"
            
            def on_success(result):
                result_container["value"] = result
            
            def on_error(error):
                result_container["error"] = error
            
            # Run async operation
            future = coordinator.run_async(
                test_coro(),
                callback=on_success,
                error_callback=on_error
            )
            
            # Wait for completion
            await asyncio.sleep(0.1)
            
            assert result_container["value"] == "success"
            assert result_container["error"] is None
            
        finally:
            coordinator.stop()
    
    def test_run_sync_in_executor(self):
        """Test running sync operations in executor."""
        coordinator = AsyncCoordinator()
        coordinator.start()
        
        try:
            result_container = {"value": None}
            
            def sync_operation(x, y):
                return x + y
            
            def on_complete(result):
                result_container["value"] = result
            
            # Run sync operation
            coordinator.run_sync_in_executor(
                sync_operation, 5, 10,
                callback=on_complete
            )
            
            # Wait for completion
            time.sleep(0.2)
            
            assert result_container["value"] == 15
            
        finally:
            coordinator.stop()
    
    def test_error_handling(self):
        """Test error handling in async operations."""
        coordinator = AsyncCoordinator()
        coordinator.start()
        
        try:
            error_container = {"error": None}
            
            async def failing_coro():
                await asyncio.sleep(0.01)
                raise ValueError("Test error")
            
            def on_error(error):
                error_container["error"] = error
            
            # Run failing operation
            coordinator.run_async(
                failing_coro(),
                error_callback=on_error
            )
            
            # Wait for completion
            time.sleep(0.2)
            
            assert error_container["error"] is not None
            assert isinstance(error_container["error"], ValueError)
            
        finally:
            coordinator.stop()
    
    def test_global_coordinator(self):
        """Test global coordinator functions."""
        from src.utils.async_coordinator import start_global_coordinator, stop_global_coordinator
        
        coordinator = get_coordinator()
        assert coordinator is not None
        
        start_global_coordinator()
        assert coordinator.is_running()
        
        stop_global_coordinator()
        # Note: global coordinator is set to None after stop


class TestUIThreadSafety:
    """Test UI thread safety utilities."""
    
    def test_is_main_thread(self):
        """Test main thread detection."""
        assert is_main_thread() == True
        
        result_container = {"in_main": None}
        
        def thread_func():
            result_container["in_main"] = is_main_thread()
        
        thread = threading.Thread(target=thread_func)
        thread.start()
        thread.join()
        
        assert result_container["in_main"] == False
    
    def test_ui_thread_safe_decorator(self):
        """Test UI thread safe decorator."""
        
        class MockWidget:
            def __init__(self):
                self.after_calls = []
                self.method_calls = []
            
            def after(self, delay, callback):
                self.after_calls.append((delay, callback))
                # Simulate immediate execution for test
                callback()
            
            @ui_thread_safe
            def update_ui(self, message):
                self.method_calls.append(message)
        
        widget = MockWidget()
        
        # Call from main thread (should execute directly)
        widget.update_ui("direct")
        assert "direct" in widget.method_calls
        
        # Call from background thread (should use after())
        def thread_func():
            widget.update_ui("threaded")
        
        thread = threading.Thread(target=thread_func)
        thread.start()
        thread.join()
        
        # Should have scheduled via after()
        assert len(widget.after_calls) > 0
        assert "threaded" in widget.method_calls
    
    def test_thread_safe_ui_mixin(self):
        """Test ThreadSafeUI mixin."""
        
        class MockApp(ThreadSafeUI, tk.Tk):
            def __init__(self):
                super().__init__()
                self.status_updates = []
                self.status_label = Mock()
                self.status_label.config = Mock(side_effect=self._track_status)
                self.update_idletasks = Mock()
            
            def _track_status(self, text):
                self.status_updates.append(text)
        
        app = MockApp()
        
        # Test safe status update
        app.update_status_safe("Test message")
        
        app.status_label.config.assert_called_with(text="Test message")
        assert "Test message" in app.status_updates
        
        app.destroy()
    
    def test_async_ui_updater(self):
        """Test AsyncUIUpdater for coordinated updates."""
        
        class MockRoot:
            def __init__(self):
                self.after_calls = []
            
            def after(self, delay, callback):
                self.after_calls.append((delay, callback))
                callback()  # Execute immediately for test
        
        root = MockRoot()
        updater = AsyncUIUpdater(root)
        
        call_results = []
        
        def test_callback(value):
            call_results.append(value)
        
        # Schedule multiple updates
        updater.schedule_update(test_callback, "first")
        updater.schedule_update(test_callback, "second")
        
        # Should have processed all updates
        assert "first" in call_results
        assert "second" in call_results
        assert len(root.after_calls) > 0


class TestAsyncUnsplashService:
    """Test AsyncUnsplashService."""
    
    @pytest.fixture
    def mock_service(self):
        """Create mock service for testing."""
        with patch('aiohttp.ClientSession') as mock_session:
            service = AsyncUnsplashService("test_key")
            service._session = mock_session
            yield service
    
    @pytest.mark.asyncio
    async def test_search_photos(self, mock_service):
        """Test photo search functionality."""
        # Mock API response
        mock_response = {
            "results": [
                {
                    "id": "test_id",
                    "description": "Test image",
                    "alt_description": "Alt description",
                    "urls": {"regular": "https://test.com/image.jpg"},
                    "user": {"id": "user_id", "username": "test_user", "name": "Test User"},
                    "width": 1920,
                    "height": 1080,
                    "likes": 100,
                    "tags": []
                }
            ],
            "total": 1,
            "total_pages": 1
        }
        
        with patch.object(mock_service, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            
            result = await mock_service.search_photos("test query")
            
            assert isinstance(result, SearchResult)
            assert len(result.results) == 1
            assert result.results[0].id == "test_id"
            assert result.query == "test query"
            
            # Verify API was called correctly
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "/search/photos" in call_args[0]
    
    @pytest.mark.asyncio
    async def test_download_image(self, mock_service):
        """Test image download functionality."""
        test_image_data = b"fake_image_data"
        
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.content.iter_chunked.return_value = [test_image_data]
        mock_response.headers = {"content-length": str(len(test_image_data))}
        mock_response.raise_for_status = Mock()
        
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        with patch.object(mock_service, '_get_session') as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session
            
            progress_calls = []
            def progress_callback(downloaded, total):
                progress_calls.append((downloaded, total))
            
            result = await mock_service.download_image(
                "https://test.com/image.jpg",
                progress_callback
            )
            
            assert result == test_image_data
            assert len(progress_calls) > 0


class TestAsyncOpenAIService:
    """Test AsyncOpenAIService."""
    
    @pytest.fixture
    def mock_service(self):
        """Create mock OpenAI service."""
        service = AsyncOpenAIService("test_key")
        return service
    
    @pytest.mark.asyncio
    async def test_analyze_image(self, mock_service):
        """Test image analysis functionality."""
        # Mock API response
        mock_response = {
            "choices": [{
                "message": {
                    "content": "This is a test image description."
                }
            }],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            },
            "id": "test_request_id"
        }
        
        with patch.object(mock_service, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            request = ImageAnalysisRequest(
                image_url="https://test.com/image.jpg",
                prompt="Describe this image"
            )
            
            result = await mock_service.analyze_image(request)
            
            assert isinstance(result, AnalysisResult)
            assert result.content == "This is a test image description."
            assert result.token_usage.total_tokens == 150
            assert result.cost_estimate.total_cost > 0
            
            # Verify API was called
            mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extract_vocabulary(self, mock_service):
        """Test vocabulary extraction functionality."""
        # Mock API response
        mock_response = {
            "choices": [{
                "message": {
                    "content": '{"Sustantivos": ["el perro", "la casa"], "Verbos": ["correr", "saltar"]}'
                }
            }],
            "usage": {
                "total_tokens": 100
            }
        }
        
        with patch.object(mock_service, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            request = VocabularyExtractionRequest(
                text="El perro corre y salta en la casa",
                target_language="Spanish"
            )
            
            result = await mock_service.extract_vocabulary(request)
            
            assert isinstance(result, VocabularyResult)
            assert "Sustantivos" in result.categories
            assert "Verbos" in result.categories
            assert result.total_words == 4
    
    @pytest.mark.asyncio
    async def test_translate_text(self, mock_service):
        """Test text translation functionality."""
        mock_response = {
            "choices": [{
                "message": {
                    "content": "The dog"
                }
            }],
            "usage": {
                "total_tokens": 20
            }
        }
        
        with patch.object(mock_service, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            result = await mock_service.translate_text(
                "el perro",
                source_lang="Spanish",
                target_lang="English"
            )
            
            assert result == "The dog"


class TestAsyncTaskDecorator:
    """Test the @async_task decorator."""
    
    def test_async_task_decorator(self):
        """Test async task decorator functionality."""
        
        class MockClass:
            def __init__(self):
                self.results = []
                self.errors = []
            
            @async_task(timeout=5)
            def perform_async_operation(self, value):
                async def coro():
                    await asyncio.sleep(0.01)
                    return value * 2
                
                def on_success(result):
                    self.results.append(result)
                
                def on_error(error):
                    self.errors.append(error)
                
                return coro(), on_success, on_error
        
        # Mock the coordinator
        with patch('src.utils.async_coordinator.get_coordinator') as mock_get_coordinator:
            mock_coordinator = Mock()
            mock_coordinator.is_running.return_value = True
            mock_coordinator.run_async = Mock()
            mock_get_coordinator.return_value = mock_coordinator
            
            obj = MockClass()
            obj.perform_async_operation(5)
            
            # Verify coordinator was used
            mock_coordinator.run_async.assert_called_once()


class TestIntegrationScenarios:
    """Test integration scenarios that caused the original bugs."""
    
    def test_no_event_loop_conflicts(self):
        """Test that multiple coordinators don't conflict."""
        coordinator1 = AsyncCoordinator()
        coordinator2 = AsyncCoordinator()
        
        coordinator1.start()
        coordinator2.start()
        
        time.sleep(0.1)
        
        # Both should be running independently
        assert coordinator1.is_running()
        assert coordinator2.is_running()
        
        coordinator1.stop()
        coordinator2.stop()
    
    def test_ui_thread_not_blocked(self):
        """Test that UI thread doesn't get blocked by async operations."""
        coordinator = AsyncCoordinator()
        coordinator.start()
        
        try:
            ui_blocked = False
            
            async def long_running_operation():
                await asyncio.sleep(0.5)  # Simulate long operation
                return "completed"
            
            # Start async operation
            start_time = time.time()
            coordinator.run_async(long_running_operation())
            
            # UI thread should be responsive immediately
            ui_response_time = time.time() - start_time
            assert ui_response_time < 0.1, "UI thread was blocked"
            
        finally:
            coordinator.stop()
    
    def test_proper_cleanup_on_shutdown(self):
        """Test that all resources are properly cleaned up."""
        coordinator = AsyncCoordinator()
        coordinator.start()
        
        # Start some operations
        async def dummy_coro():
            await asyncio.sleep(1.0)
            return "done"
        
        future1 = coordinator.run_async(dummy_coro())
        future2 = coordinator.run_async(dummy_coro())
        
        time.sleep(0.1)  # Let operations start
        
        # Stop coordinator (should cancel operations)
        coordinator.stop()
        
        # Futures should be cancelled or completed
        time.sleep(0.1)
        assert future1.cancelled() or future1.done()
        assert future2.cancelled() or future2.done()


if __name__ == "__main__":
    # Run basic smoke tests
    print("Running async fixes smoke tests...")
    
    # Test coordinator
    coordinator = AsyncCoordinator()
    coordinator.start()
    print("✓ AsyncCoordinator started")
    
    coordinator.stop()
    print("✓ AsyncCoordinator stopped")
    
    # Test thread safety
    def test_ui_safe():
        class TestWidget:
            def __init__(self):
                self.updates = []
            
            def after(self, delay, callback):
                callback()
            
            @ui_thread_safe  
            def update(self, msg):
                self.updates.append(msg)
        
        widget = TestWidget()
        widget.update("test")
        return len(widget.updates) == 1
    
    assert test_ui_safe()
    print("✓ UI thread safety works")
    
    print("All smoke tests passed! ✓")