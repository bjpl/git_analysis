"""
Enhanced Unsplash Service with proper timeout handling and cancellation support.
"""

import requests
import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable, List
import logging
import json

from .api_timeout_manager import api_timeout_manager, CancellationError, TimeoutError


class EnhancedUnsplashService:
    """Enhanced Unsplash API service with robust timeout and error handling."""
    
    def __init__(self, access_key: str):
        self.access_key = access_key
        self.base_url = "https://api.unsplash.com"
        self.logger = logging.getLogger(f"{__name__}.EnhancedUnsplashService")
        
        # Rate limiting tracking
        self.rate_limit_remaining = None
        self.rate_limit_reset = None
        
        # Cache for avoiding duplicates
        self.used_image_urls = set()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authorization."""
        return {
            "Authorization": f"Client-ID {self.access_key}",
            "User-Agent": "UnsplashImageSearch/1.0",
            "Accept": "application/json"
        }
    
    def _update_rate_limit_info(self, response: requests.Response) -> None:
        """Update rate limit information from response headers."""
        try:
            self.rate_limit_remaining = int(response.headers.get('X-Ratelimit-Remaining', 0))
            reset_time = response.headers.get('X-Ratelimit-Reset')
            if reset_time:
                self.rate_limit_reset = datetime.fromtimestamp(int(reset_time))
        except (ValueError, TypeError):
            pass
    
    def _check_rate_limit(self) -> None:
        """Check if we're approaching rate limits."""
        if (self.rate_limit_remaining is not None and 
            self.rate_limit_remaining < 5):
            
            if self.rate_limit_reset:
                wait_time = (self.rate_limit_reset - datetime.now()).total_seconds()
                if wait_time > 0:
                    self.logger.warning(f"Approaching rate limit. {self.rate_limit_remaining} requests remaining")
                    raise RateLimitApproachingError(
                        f"Rate limit approaching. {self.rate_limit_remaining} requests remaining. "
                        f"Resets in {int(wait_time)} seconds."
                    )
    
    def _handle_response_errors(self, response: requests.Response, url: str) -> None:
        """Handle HTTP response errors with detailed messages."""
        if response.status_code == 200:
            return
        
        error_details = {
            'status_code': response.status_code,
            'url': url,
            'headers': dict(response.headers)
        }
        
        try:
            error_body = response.json()
            error_details['error_body'] = error_body
        except:
            error_details['error_text'] = response.text
        
        if response.status_code == 401:
            raise UnsplashAuthError(
                "Invalid Unsplash API key. Please check your configuration.",
                error_details
            )
        elif response.status_code == 403:
            raise UnsplashAuthError(
                "Access forbidden. Check your API key permissions.",
                error_details
            )
        elif response.status_code == 429:
            # Extract reset time from headers
            reset_time = response.headers.get('X-Ratelimit-Reset')
            if reset_time:
                reset_dt = datetime.fromtimestamp(int(reset_time))
                wait_minutes = max(1, int((reset_dt - datetime.now()).total_seconds() / 60))
                raise UnsplashRateLimitError(
                    f"Rate limit exceeded. Try again in {wait_minutes} minutes.",
                    error_details
                )
            else:
                raise UnsplashRateLimitError(
                    "Rate limit exceeded. Please wait before making more requests.",
                    error_details
                )
        elif response.status_code >= 500:
            raise UnsplashServerError(
                f"Unsplash server error (HTTP {response.status_code}). Please try again later.",
                error_details
            )
        else:
            raise UnsplashAPIError(
                f"Unsplash API error (HTTP {response.status_code}): {response.text[:200]}",
                error_details
            )
    
    def search_photos(
        self,
        query: str,
        page: int = 1,
        per_page: int = 10,
        operation_id: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """Search for photos with enhanced error handling and cancellation."""
        if not operation_id:
            operation_id = f"search_{query.replace(' ', '_')}_{page}_{int(time.time())}"
        
        # Check rate limits before making request
        self._check_rate_limit()
        
        url = f"{self.base_url}/search/photos"
        params = {
            "query": query,
            "page": page,
            "per_page": min(per_page, 30)  # Unsplash max is 30
        }
        
        self.logger.info(f"Searching Unsplash for '{query}' (page {page}, per_page {per_page})")
        
        try:
            response = api_timeout_manager.make_request_with_timeout(
                service='unsplash',
                method='GET',
                url=url,
                operation_id=operation_id,
                progress_callback=progress_callback,
                headers=self._get_headers(),
                params=params
            )
            
            # Update rate limit info
            self._update_rate_limit_info(response)
            
            # Handle errors
            self._handle_response_errors(response, url)
            
            data = response.json()
            
            self.logger.info(
                f"Found {data.get('total', 0)} total results for '{query}' "
                f"(showing {len(data.get('results', []))} on page {page})"
            )
            
            return data
            
        except (TimeoutError, CancellationError):
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error during search: {e}")
            raise UnsplashNetworkError(f"Network error: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error during search: {e}")
            raise UnsplashAPIError(f"Unexpected error: {str(e)}") from e
    
    def download_image(
        self,
        image_url: str,
        operation_id: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> bytes:
        """Download image with progress tracking and proper error handling."""
        if not operation_id:
            operation_id = f"download_{int(time.time())}"
        
        self.logger.info(f"Downloading image: {image_url[:100]}...")
        
        try:
            # Use the timeout manager's download method with progress
            image_data = api_timeout_manager.download_with_progress(
                url=image_url,
                operation_id=operation_id,
                progress_callback=progress_callback,
                chunk_size=8192
            )
            
            self.logger.info(f"Successfully downloaded image ({len(image_data):,} bytes)")
            return image_data
            
        except (TimeoutError, CancellationError):
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error during image download: {e}")
            raise UnsplashNetworkError(f"Download failed: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error during download: {e}")
            raise UnsplashAPIError(f"Download error: {str(e)}") from e
    
    def get_photo_info(
        self,
        photo_id: str,
        operation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed photo information."""
        if not operation_id:
            operation_id = f"photo_info_{photo_id}_{int(time.time())}"
        
        url = f"{self.base_url}/photos/{photo_id}"
        
        try:
            response = api_timeout_manager.make_request_with_timeout(
                service='unsplash',
                method='GET',
                url=url,
                operation_id=operation_id,
                headers=self._get_headers()
            )
            
            self._update_rate_limit_info(response)
            self._handle_response_errors(response, url)
            
            return response.json()
            
        except (TimeoutError, CancellationError):
            raise
        except requests.exceptions.RequestException as e:
            raise UnsplashNetworkError(f"Network error: {str(e)}") from e
        except Exception as e:
            raise UnsplashAPIError(f"Error getting photo info: {str(e)}") from e
    
    def get_next_unique_image(
        self,
        query: str,
        page_start: int = 1,
        max_pages: int = 10,
        operation_id: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get next unique image that hasn't been used before."""
        if not operation_id:
            operation_id = f"unique_search_{query.replace(' ', '_')}_{int(time.time())}"
        
        for page in range(page_start, page_start + max_pages):
            try:
                # Check for cancellation
                if operation_id in api_timeout_manager.active_tokens:
                    api_timeout_manager.active_tokens[operation_id].raise_if_cancelled()
                
                if progress_callback:
                    progress_callback(f"Searching page {page} for unique images...")
                
                results = self.search_photos(
                    query=query,
                    page=page,
                    per_page=10,
                    operation_id=f"{operation_id}_page_{page}",
                    progress_callback=progress_callback
                )
                
                photos = results.get('results', [])
                if not photos:
                    self.logger.info(f"No more photos found for '{query}' at page {page}")
                    return None
                
                # Find first unused image
                for photo in photos:
                    image_url = photo['urls']['regular']
                    canonical_url = self.canonicalize_url(image_url)
                    
                    if canonical_url not in self.used_image_urls:
                        self.used_image_urls.add(canonical_url)
                        self.logger.info(f"Found unique image: {photo.get('id', 'unknown')}")
                        return photo
                
                if progress_callback:
                    progress_callback(f"All images on page {page} already used, trying next page...")
                    
            except (UnsplashRateLimitError, UnsplashAuthError):
                raise  # Don't retry these
            except Exception as e:
                self.logger.warning(f"Error on page {page}: {e}")
                continue
        
        self.logger.info(f"No unique images found for '{query}' in {max_pages} pages")
        return None
    
    @staticmethod
    def canonicalize_url(url: str) -> str:
        """Return base URL without query parameters."""
        return url.split('?')[0] if url else ""
    
    def add_used_image_url(self, url: str) -> None:
        """Add URL to used images set."""
        self.used_image_urls.add(self.canonicalize_url(url))
    
    def load_used_image_urls(self, urls: set) -> None:
        """Load set of used image URLs."""
        self.used_image_urls.update(urls)
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        return {
            'remaining': self.rate_limit_remaining,
            'reset_time': self.rate_limit_reset.isoformat() if self.rate_limit_reset else None,
            'reset_in_seconds': (
                int((self.rate_limit_reset - datetime.now()).total_seconds())
                if self.rate_limit_reset else None
            )
        }
    
    def cancel_operation(self, operation_id: str) -> bool:
        """Cancel specific operation."""
        return api_timeout_manager.cancel_operation(operation_id)
    
    def cancel_all_operations(self) -> int:
        """Cancel all active operations."""
        return api_timeout_manager.cancel_all_operations()


# Custom exceptions
class UnsplashError(Exception):
    """Base Unsplash API error."""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message)
        self.details = details or {}


class UnsplashAuthError(UnsplashError):
    """Authentication error."""
    pass


class UnsplashRateLimitError(UnsplashError):
    """Rate limit exceeded error."""
    pass


class UnsplashServerError(UnsplashError):
    """Server error (5xx)."""
    pass


class UnsplashNetworkError(UnsplashError):
    """Network/connection error."""
    pass


class UnsplashAPIError(UnsplashError):
    """General API error."""
    pass


class RateLimitApproachingError(UnsplashError):
    """Rate limit approaching warning."""
    pass
