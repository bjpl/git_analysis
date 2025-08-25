"""
Async/Thread Coordinator for Tkinter Applications

Provides proper async/await integration with Tkinter by managing a dedicated
event loop in a background thread and coordinating between UI thread and async operations.
"""

import asyncio
import threading
import time
import logging
from typing import Callable, Any, Optional, Coroutine, Union
from concurrent.futures import ThreadPoolExecutor, Future
import functools
import weakref


logger = logging.getLogger(__name__)


class AsyncCoordinator:
    """
    Coordinates async operations with Tkinter UI thread.
    
    Solves common issues:
    - Event loop conflicts between threads
    - UI thread blocking during async operations
    - Proper cleanup of async resources
    - Thread-safe callback handling
    """
    
    def __init__(self, max_workers: int = 4):
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers, 
            thread_name_prefix="async_worker"
        )
        self._running = False
        self._shutdown_event = threading.Event()
        
        # Track active operations for cleanup
        self._active_futures: weakref.WeakSet = weakref.WeakSet()
        
        # Thread-safe operation counter
        self._operation_count = 0
        self._count_lock = threading.Lock()
    
    def start(self) -> None:
        """Start the async event loop in a background thread."""
        if self._running:
            logger.warning("AsyncCoordinator already running")
            return
        
        logger.info("Starting AsyncCoordinator")
        
        def run_event_loop():
            """Run event loop in dedicated thread."""
            try:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
                
                # Set up exception handler
                self._loop.set_exception_handler(self._handle_loop_exception)
                
                # Run until shutdown
                self._loop.run_until_complete(self._run_until_shutdown())
                
            except Exception as e:
                logger.error(f"Event loop error: {e}")
            finally:
                logger.info("Event loop stopped")
        
        self._thread = threading.Thread(
            target=run_event_loop, 
            name="AsyncCoordinator", 
            daemon=True
        )
        self._thread.start()
        
        # Wait for loop to be ready (with timeout)
        start_time = time.time()
        while self._loop is None and time.time() - start_time < 5:
            time.sleep(0.01)
        
        if self._loop is None:
            raise RuntimeError("Failed to start async event loop")
        
        self._running = True
        logger.info("AsyncCoordinator started successfully")
    
    def stop(self, timeout: float = 5.0) -> None:
        """Stop the async event loop and cleanup resources."""
        if not self._running:
            return
        
        logger.info("Stopping AsyncCoordinator")
        
        try:
            # Cancel all active operations
            self._cancel_active_operations()
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Stop event loop
            if self._loop and not self._loop.is_closed():
                self._loop.call_soon_threadsafe(self._loop.stop)
            
            # Wait for thread to finish
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=timeout)
                
                if self._thread.is_alive():
                    logger.warning("Event loop thread did not stop gracefully")
            
            # Shutdown executor
            self._executor.shutdown(wait=True, timeout=timeout)
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            self._running = False
            logger.info("AsyncCoordinator stopped")
    
    def is_running(self) -> bool:
        """Check if the coordinator is running."""
        return self._running and self._loop is not None and not self._loop.is_closed()
    
    def run_async(
        self, 
        coro: Coroutine, 
        callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None,
        timeout: Optional[float] = None
    ) -> Future:
        """
        Run async coroutine and optionally call callback with result.
        
        Args:
            coro: Coroutine to run
            callback: Called with result on success: callback(result)
            error_callback: Called on error: error_callback(exception)
            timeout: Optional timeout in seconds
            
        Returns:
            Future object for the operation
        """
        if not self.is_running():
            raise RuntimeError("AsyncCoordinator not running. Call start() first.")
        
        # Increment operation counter
        with self._count_lock:
            self._operation_count += 1
            operation_id = self._operation_count
        
        logger.debug(f"Starting async operation #{operation_id}")
        
        # Submit coroutine to event loop
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        
        # Track active future
        self._active_futures.add(future)
        
        def handle_result():
            """Handle the result of the async operation."""
            try:
                if timeout:
                    result = future.result(timeout=timeout)
                else:
                    result = future.result()
                
                logger.debug(f"Async operation #{operation_id} completed successfully")
                
                if callback:
                    try:
                        callback(result)
                    except Exception as e:
                        logger.error(f"Callback error: {e}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"Async operation #{operation_id} timed out")
                if error_callback:
                    error_callback(asyncio.TimeoutError("Operation timed out"))
                    
            except Exception as e:
                logger.error(f"Async operation #{operation_id} failed: {e}")
                if error_callback:
                    error_callback(e)
        
        # Schedule result handling in executor to avoid blocking
        self._executor.submit(handle_result)
        
        return future
    
    def run_sync_in_executor(
        self, 
        func: Callable, 
        *args, 
        callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None,
        **kwargs
    ) -> Future:
        """
        Run sync function in executor thread pool.
        
        Args:
            func: Function to run
            *args: Arguments for function
            callback: Called with result on success
            error_callback: Called on error
            **kwargs: Keyword arguments for function
            
        Returns:
            Future object for the operation
        """
        with self._count_lock:
            self._operation_count += 1
            operation_id = self._operation_count
        
        logger.debug(f"Starting sync operation #{operation_id}: {func.__name__}")
        
        def wrapped_func():
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Sync operation #{operation_id} completed successfully")
                
                if callback:
                    try:
                        callback(result)
                    except Exception as e:
                        logger.error(f"Callback error: {e}")
                
                return result
                
            except Exception as e:
                logger.error(f"Sync operation #{operation_id} failed: {e}")
                if error_callback:
                    error_callback(e)
                raise
        
        future = self._executor.submit(wrapped_func)
        self._active_futures.add(future)
        
        return future
    
    def create_task(self, coro: Coroutine) -> asyncio.Task:
        """
        Create a task in the async event loop.
        
        Args:
            coro: Coroutine to create task for
            
        Returns:
            Task object
        """
        if not self.is_running():
            raise RuntimeError("AsyncCoordinator not running")
        
        # Create task in the event loop
        task = asyncio.run_coroutine_threadsafe(
            self._create_task_in_loop(coro), 
            self._loop
        ).result()
        
        self._active_futures.add(task)
        return task
    
    async def _create_task_in_loop(self, coro: Coroutine) -> asyncio.Task:
        """Create task within the event loop."""
        return asyncio.create_task(coro)
    
    async def _run_until_shutdown(self) -> None:
        """Run until shutdown is requested."""
        while not self._shutdown_event.is_set():
            await asyncio.sleep(0.1)
    
    def _handle_loop_exception(self, loop, context) -> None:
        """Handle exceptions in the event loop."""
        exception = context.get('exception')
        if exception:
            logger.error(f"Event loop exception: {exception}")
        else:
            logger.error(f"Event loop error: {context}")
    
    def _cancel_active_operations(self) -> None:
        """Cancel all active operations."""
        cancelled_count = 0
        
        for future in list(self._active_futures):
            if not future.done():
                future.cancel()
                cancelled_count += 1
        
        if cancelled_count > 0:
            logger.info(f"Cancelled {cancelled_count} active operations")
    
    def get_stats(self) -> dict:
        """Get statistics about the coordinator."""
        return {
            "running": self.is_running(),
            "operation_count": self._operation_count,
            "active_operations": len(self._active_futures),
            "thread_alive": self._thread.is_alive() if self._thread else False,
            "loop_closed": self._loop.is_closed() if self._loop else True
        }


# Global coordinator instance
_global_coordinator: Optional[AsyncCoordinator] = None


def get_coordinator() -> AsyncCoordinator:
    """Get the global async coordinator instance."""
    global _global_coordinator
    
    if _global_coordinator is None:
        _global_coordinator = AsyncCoordinator()
    
    return _global_coordinator


def start_global_coordinator() -> None:
    """Start the global async coordinator."""
    coordinator = get_coordinator()
    if not coordinator.is_running():
        coordinator.start()


def stop_global_coordinator() -> None:
    """Stop the global async coordinator."""
    global _global_coordinator
    
    if _global_coordinator is not None:
        _global_coordinator.stop()
        _global_coordinator = None


def async_task(
    timeout: Optional[float] = None
) -> Callable:
    """
    Decorator to run async functions using the global coordinator.
    
    Args:
        timeout: Optional timeout in seconds
        
    Example:
        @async_task(timeout=30)
        def my_async_method(self):
            async def coro():
                return await some_async_operation()
            
            def on_success(result):
                self.handle_result(result)
            
            def on_error(error):
                self.handle_error(error)
            
            return coro(), on_success, on_error
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            coordinator = get_coordinator()
            
            if not coordinator.is_running():
                start_global_coordinator()
            
            # Function should return (coroutine, success_callback, error_callback)
            result = func(self, *args, **kwargs)
            
            if isinstance(result, tuple) and len(result) >= 1:
                coro = result[0]
                success_callback = result[1] if len(result) > 1 else None
                error_callback = result[2] if len(result) > 2 else None
                
                return coordinator.run_async(
                    coro, 
                    callback=success_callback,
                    error_callback=error_callback,
                    timeout=timeout
                )
            else:
                raise ValueError(
                    "Decorated function must return (coroutine, success_callback, error_callback)"
                )
        
        return wrapper
    return decorator