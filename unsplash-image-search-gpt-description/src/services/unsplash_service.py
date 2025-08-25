"""
Unsplash API service for image search and download.
"""

import requests
import time
import threading
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor, Future, TimeoutError as FutureTimeoutError
import logging


class UnsplashService:
    """Service for interacting with the Unsplash API with cancellation support."""
    
    def __init__(self, access_key):
        self.access_key = access_key
        self.headers = {"Authorization": f"Client-ID {access_key}"}
        self.base_url = "https://api.unsplash.com"
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="unsplash")
        self._active_requests: Dict[str, Future] = {}
        self._cancelled_requests = set()
        self.logger = logging.getLogger(f"{__name__}.UnsplashService")
        
        # Default timeouts (configurable)
        self.search_timeout = 15
        self.download_timeout = 30
        self.info_timeout = 10
    
    def search_photos(self, query, page=1, per_page=10, request_id: Optional[str] = None, 
                     progress_callback: Optional[Callable[[str], None]] = None):
        """Search for photos on Unsplash with cancellation support."""
        if request_id and request_id in self._cancelled_requests:
            raise CancellationError(f"Request {request_id} was cancelled")
        
        url = f"{self.base_url}/search/photos"
        params = {
            "query": query,
            "page": page,
            "per_page": per_page
        }
        
        if progress_callback:
            progress_callback(f"Searching for '{query}' (page {page})...")
        
        response = requests.get(
            url, 
            headers=self.headers, 
            params=params, 
            timeout=self.search_timeout
        )
        response.raise_for_status()
        
        if progress_callback:
            progress_callback(f"Found results for '{query}'")
        
        return response.json()
    
    def download_image(self, image_url, request_id: Optional[str] = None,
                      progress_callback: Optional[Callable[[str], None]] = None):
        """Download image from URL with progress tracking."""
        if request_id and request_id in self._cancelled_requests:
            raise CancellationError(f"Request {request_id} was cancelled")
        
        if progress_callback:
            progress_callback(f"Downloading image...")
        
        response = requests.get(
            image_url, 
            timeout=self.download_timeout,
            stream=True  # Enable streaming for large images
        )
        response.raise_for_status()
        
        # Download with progress tracking
        content_length = response.headers.get('content-length')
        if content_length and progress_callback:
            total_size = int(content_length)
            downloaded = 0
            chunks = []
            
            for chunk in response.iter_content(chunk_size=8192):
                if request_id and request_id in self._cancelled_requests:
                    raise CancellationError(f"Download {request_id} was cancelled")
                    
                chunks.append(chunk)
                downloaded += len(chunk)
                
                if progress_callback and total_size > 0:
                    progress = int((downloaded / total_size) * 100)
                    progress_callback(f"Downloading... {progress}%")
            
            return b''.join(chunks)
        else:
            return response.content
    
    def get_image_info(self, photo_id, request_id: Optional[str] = None):
        """Get detailed information about a specific photo."""
        if request_id and request_id in self._cancelled_requests:
            raise CancellationError(f"Request {request_id} was cancelled")
            
        url = f"{self.base_url}/photos/{photo_id}"
        response = requests.get(url, headers=self.headers, timeout=self.info_timeout)
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def canonicalize_url(url):
        """Return the base URL without query parameters."""
        return url.split('?')[0] if url else ""
    
    def handle_rate_limit_error(self, error):
        """Handle rate limit errors with helpful messages."""
        error_str = str(error)
        
        if "403" in error_str:
            return "Unsplash API key may be invalid. Please check your configuration."
        elif "rate" in error_str.lower() or "429" in error_str:
            # Calculate time until reset (Unsplash resets hourly)
            next_hour = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0)
            minutes_left = int((next_hour - datetime.now()).seconds / 60)
            return f"Unsplash rate limit reached (50/hour).\n\nTry again in {minutes_left} minutes."
        else:
            return f"Error al buscar imágenes:\n{error}"


class ApiCallRetryMixin:
    """Mixin for API calls with retry logic."""
    
    @staticmethod
    def api_call_with_retry(func, max_retries=3, *args, **kwargs):
        """Execute an API call with exponential backoff retry logic."""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                    print(f"API error, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                continue
            except Exception as e:
                last_exception = e
                if "rate_limit" in str(e).lower():
                    print("Rate limit reached. Please wait a moment...")
                    time.sleep(5)
                    continue
                break
        
        # If all retries failed
        raise last_exception
    
    def search_photos_async(self, query: str, page: int = 1, per_page: int = 10, 
                           request_id: Optional[str] = None,
                           progress_callback: Optional[Callable[[str], None]] = None) -> Future:
        """Async search for photos with cancellation support."""
        if not request_id:
            request_id = f"search_{query}_{page}_{int(time.time())}"
        
        future = self.executor.submit(
            self._search_with_retry, query, page, per_page, request_id, progress_callback
        )
        self._active_requests[request_id] = future
        return future
    
    def download_image_async(self, image_url: str, request_id: Optional[str] = None,
                            progress_callback: Optional[Callable[[str], None]] = None) -> Future:
        """Async download image with cancellation support."""
        if not request_id:
            request_id = f"download_{int(time.time())}"
        
        future = self.executor.submit(
            self._download_with_retry, image_url, request_id, progress_callback
        )
        self._active_requests[request_id] = future
        return future
    
    def cancel_request(self, request_id: str) -> bool:
        """Cancel a specific request."""
        self._cancelled_requests.add(request_id)
        
        if request_id in self._active_requests:
            future = self._active_requests[request_id]
            cancelled = future.cancel()
            if cancelled:
                self.logger.info(f"Successfully cancelled request {request_id}")
            else:
                self.logger.warning(f"Could not cancel request {request_id} (already running)")
            return cancelled
        
        return True
    
    def cancel_all_requests(self) -> int:
        """Cancel all active requests."""
        cancelled_count = 0
        for request_id in list(self._active_requests.keys()):
            if self.cancel_request(request_id):
                cancelled_count += 1
        return cancelled_count
    
    def _search_with_retry(self, query: str, page: int, per_page: int, 
                          request_id: str, progress_callback: Optional[Callable]) -> dict:
        """Search with retry logic and cancellation checks."""
        return self.api_call_with_retry(
            self.search_photos, 
            max_retries=3, 
            query=query, 
            page=page, 
            per_page=per_page,
            request_id=request_id,
            progress_callback=progress_callback
        )
    
    def _download_with_retry(self, image_url: str, request_id: str, 
                            progress_callback: Optional[Callable]) -> bytes:
        """Download with retry logic and cancellation checks."""
        return self.api_call_with_retry(
            self.download_image,
            max_retries=3,
            image_url=image_url,
            request_id=request_id,
            progress_callback=progress_callback
        )
    
    def get_active_requests(self) -> Dict[str, str]:
        """Get status of active requests."""
        status = {}
        for request_id, future in self._active_requests.items():
            if future.done():
                if future.cancelled():
                    status[request_id] = "cancelled"
                elif future.exception():
                    status[request_id] = f"failed: {future.exception()}"
                else:
                    status[request_id] = "completed"
            else:
                status[request_id] = "running"
        return status
    
    def cleanup_completed_requests(self) -> int:
        """Clean up completed requests and return count."""
        completed = []
        for request_id, future in self._active_requests.items():
            if future.done():
                completed.append(request_id)
        
        for request_id in completed:
            del self._active_requests[request_id]
            self._cancelled_requests.discard(request_id)
        
        return len(completed)
    
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the executor and cancel all requests."""
        self.cancel_all_requests()
        self.executor.shutdown(wait=wait)
        self._active_requests.clear()
        self._cancelled_requests.clear()


class CancellationError(Exception):
    """Raised when a request is cancelled."""
    pass