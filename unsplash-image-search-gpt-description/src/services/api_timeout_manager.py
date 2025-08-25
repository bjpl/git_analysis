"""
API Timeout and Cancellation Manager
Provides centralized timeout management, cancellation tokens, and enhanced error handling.
"""

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor, Future, TimeoutError as FutureTimeoutError
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Optional, Set, Union
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import logging


class TimeoutType(Enum):
    """Types of timeouts."""
    CONNECT = "connect"
    READ = "read"
    TOTAL = "total"


@dataclass
class TimeoutConfig:
    """Configuration for different types of timeouts."""
    connect: float = 5.0  # Connection timeout
    read: float = 30.0    # Read timeout
    total: float = 60.0   # Total timeout
    
    def to_requests_timeout(self) -> tuple:
        """Convert to requests timeout tuple."""
        return (self.connect, self.read)


@dataclass
class RetryConfig:
    """Configuration for retry logic."""
    total: int = 3
    backoff_factor: float = 0.3
    status_forcelist: tuple = (500, 502, 504, 429)
    allowed_methods: tuple = ("HEAD", "GET", "OPTIONS", "PUT", "DELETE", "POST")


class CancellationToken:
    """Token to signal cancellation of long-running operations."""
    
    def __init__(self):
        self._cancelled = threading.Event()
        self._callbacks: Set[Callable] = set()
    
    def cancel(self) -> None:
        """Cancel the operation and notify callbacks."""
        if not self._cancelled.is_set():
            self._cancelled.set()
            for callback in self._callbacks:
                try:
                    callback()
                except Exception as e:
                    logging.warning(f"Error in cancellation callback: {e}")
    
    @property
    def is_cancelled(self) -> bool:
        """Check if operation is cancelled."""
        return self._cancelled.is_set()
    
    def raise_if_cancelled(self) -> None:
        """Raise CancellationError if cancelled."""
        if self.is_cancelled:
            raise CancellationError("Operation was cancelled")
    
    def register_callback(self, callback: Callable) -> None:
        """Register callback to be called on cancellation."""
        self._callbacks.add(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister cancellation callback."""
        self._callbacks.discard(callback)


class CancellationError(Exception):
    """Raised when an operation is cancelled."""
    pass


class ApiTimeoutManager:
    """Centralized manager for API timeouts and cancellation."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ApiTimeoutManager")
        self.sessions: Dict[str, requests.Session] = {}
        self.active_tokens: Dict[str, CancellationToken] = {}
        self.executor = ThreadPoolExecutor(max_workers=8, thread_name_prefix="api-timeout")
        
        # Default configurations
        self.default_timeout = TimeoutConfig()
        self.default_retry = RetryConfig()
        
        # Service-specific configurations
        self.service_configs = {
            'unsplash': {
                'timeout': TimeoutConfig(connect=10.0, read=20.0, total=45.0),
                'retry': RetryConfig(total=3, backoff_factor=0.5)
            },
            'openai': {
                'timeout': TimeoutConfig(connect=10.0, read=60.0, total=120.0),
                'retry': RetryConfig(total=2, backoff_factor=1.0)
            },
            'download': {
                'timeout': TimeoutConfig(connect=5.0, read=30.0, total=120.0),
                'retry': RetryConfig(total=3, backoff_factor=0.3)
            }
        }
    
    def get_session(self, service: str) -> requests.Session:
        """Get or create HTTP session for service with proper configuration."""
        if service not in self.sessions:
            session = requests.Session()
            
            # Configure retry strategy
            config = self.service_configs.get(service, {})
            retry_config = config.get('retry', self.default_retry)
            
            retry_strategy = Retry(
                total=retry_config.total,
                backoff_factor=retry_config.backoff_factor,
                status_forcelist=retry_config.status_forcelist,
                allowed_methods=retry_config.allowed_methods,
                raise_on_status=False
            )
            
            adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            self.sessions[service] = session
        
        return self.sessions[service]
    
    def get_timeout_config(self, service: str) -> TimeoutConfig:
        """Get timeout configuration for service."""
        return self.service_configs.get(service, {}).get('timeout', self.default_timeout)
    
    def create_cancellation_token(self, operation_id: str) -> CancellationToken:
        """Create and register a cancellation token."""
        token = CancellationToken()
        self.active_tokens[operation_id] = token
        return token
    
    def cancel_operation(self, operation_id: str) -> bool:
        """Cancel operation by ID."""
        if operation_id in self.active_tokens:
            self.active_tokens[operation_id].cancel()
            return True
        return False
    
    def cleanup_token(self, operation_id: str) -> None:
        """Clean up completed operation token."""
        self.active_tokens.pop(operation_id, None)
    
    def cancel_all_operations(self) -> int:
        """Cancel all active operations."""
        count = 0
        for token in self.active_tokens.values():
            if not token.is_cancelled:
                token.cancel()
                count += 1
        return count
    
    @contextmanager
    def timeout_context(self, service: str, operation_id: str):
        """Context manager for timeout and cancellation handling."""
        token = self.create_cancellation_token(operation_id)
        try:
            yield token
        finally:
            self.cleanup_token(operation_id)
    
    def make_request_with_timeout(
        self, 
        service: str,
        method: str,
        url: str,
        operation_id: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> requests.Response:
        """Make HTTP request with proper timeout and cancellation support."""
        if not operation_id:
            operation_id = f"{service}_{method}_{int(time.time())}"
        
        session = self.get_session(service)
        timeout_config = self.get_timeout_config(service)
        
        with self.timeout_context(service, operation_id) as token:
            # Set timeout in kwargs
            kwargs.setdefault('timeout', timeout_config.to_requests_timeout())
            
            if progress_callback:
                progress_callback(f"Making {method} request to {service}...")
            
            try:
                # Check for cancellation before request
                token.raise_if_cancelled()
                
                response = session.request(method, url, **kwargs)
                
                # Check for cancellation after request
                token.raise_if_cancelled()
                
                if progress_callback:
                    progress_callback(f"Request completed successfully")
                
                return response
                
            except requests.exceptions.Timeout as e:
                error_msg = f"Timeout after {timeout_config.total}s for {service} {method} request"
                self.logger.warning(error_msg)
                raise TimeoutError(error_msg) from e
            except requests.exceptions.ConnectionError as e:
                error_msg = f"Connection error for {service}: {str(e)}"
                self.logger.error(error_msg)
                raise ConnectionError(error_msg) from e
    
    def download_with_progress(
        self,
        url: str,
        operation_id: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
        chunk_size: int = 8192
    ) -> bytes:
        """Download content with progress tracking and cancellation support."""
        if not operation_id:
            operation_id = f"download_{int(time.time())}"
        
        with self.timeout_context('download', operation_id) as token:
            session = self.get_session('download')
            timeout_config = self.get_timeout_config('download')
            
            if progress_callback:
                progress_callback("Starting download...")
            
            response = session.get(
                url, 
                stream=True, 
                timeout=timeout_config.to_requests_timeout()
            )
            response.raise_for_status()
            
            content_length = response.headers.get('content-length')
            total_size = int(content_length) if content_length else None
            downloaded = 0
            chunks = []
            
            for chunk in response.iter_content(chunk_size=chunk_size):
                # Check for cancellation during download
                token.raise_if_cancelled()
                
                if chunk:
                    chunks.append(chunk)
                    downloaded += len(chunk)
                    
                    if progress_callback and total_size:
                        progress = int((downloaded / total_size) * 100)
                        progress_callback(f"Downloaded {progress}% ({downloaded:,} bytes)")
            
            if progress_callback:
                progress_callback(f"Download completed: {downloaded:,} bytes")
            
            return b''.join(chunks)
    
    def execute_with_timeout(
        self,
        func: Callable,
        timeout: float,
        operation_id: Optional[str] = None,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with timeout using thread pool."""
        if not operation_id:
            operation_id = f"exec_{int(time.time())}"
        
        token = self.create_cancellation_token(operation_id)
        
        try:
            # Submit to thread pool
            future = self.executor.submit(func, *args, **kwargs)
            
            # Register cancellation callback
            def cancel_future():
                future.cancel()
            token.register_callback(cancel_future)
            
            try:
                result = future.result(timeout=timeout)
                token.raise_if_cancelled()
                return result
            except FutureTimeoutError:
                token.cancel()
                raise TimeoutError(f"Operation {operation_id} timed out after {timeout}s")
            
        finally:
            self.cleanup_token(operation_id)
    
    def get_status(self) -> Dict[str, Any]:
        """Get manager status information."""
        return {
            'active_operations': len(self.active_tokens),
            'active_sessions': len(self.sessions),
            'executor_active': not self.executor._shutdown,
            'thread_count': self.executor._threads and len(self.executor._threads) or 0
        }
    
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown manager and cleanup resources."""
        # Cancel all active operations
        self.cancel_all_operations()
        
        # Close sessions
        for session in self.sessions.values():
            session.close()
        self.sessions.clear()
        
        # Shutdown executor
        self.executor.shutdown(wait=wait)
        
        # Clear tokens
        self.active_tokens.clear()


# Global instance
api_timeout_manager = ApiTimeoutManager()
