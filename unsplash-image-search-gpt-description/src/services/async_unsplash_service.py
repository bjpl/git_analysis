"""
Async Unsplash Service

Fully async implementation of Unsplash API integration with proper error handling,
retry logic, and cancellation support. Fixes the sync/async mixing issues.
"""

import aiohttp
import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json

from .base_service import BaseService, ServiceError, RateLimitError


@dataclass
class UnsplashImage:
    """Represents an Unsplash image with metadata."""
    id: str
    description: Optional[str]
    alt_description: Optional[str]
    urls: Dict[str, str]
    user: Dict[str, Any]
    width: int
    height: int
    likes: int
    downloads: Optional[int] = None
    location: Optional[Dict[str, Any]] = None
    tags: List[str] = field(default_factory=list)
    color: Optional[str] = None
    created_at: Optional[str] = None


@dataclass  
class SearchResult:
    """Represents search results from Unsplash."""
    results: List[UnsplashImage]
    total: int
    total_pages: int
    current_page: int
    per_page: int
    query: str
    execution_time: float = 0.0


class AsyncUnsplashService(BaseService):
    """
    Fully async Unsplash API service.
    
    Provides:
    - Async image search with pagination
    - Async image download with progress
    - Proper error handling and retries
    - Request cancellation support
    - Rate limiting compliance
    """
    
    def __init__(
        self, 
        access_key: str,
        timeout: int = 30,
        max_retries: int = 3,
        enable_caching: bool = True
    ):
        super().__init__(
            name="unsplash",
            base_url="https://api.unsplash.com",
            api_key=access_key,
            timeout=timeout,
            enable_caching=enable_caching
        )
        
        self.headers = {
            "Authorization": f"Client-ID {access_key}",
            "Accept": "application/json",
            "Accept-Version": "v1"
        }
        
        self.logger = logging.getLogger(f"{__name__}.AsyncUnsplashService")
        
        # Track API usage for rate limiting
        self.requests_made = 0
        self.last_reset = datetime.now()
    
    async def search_photos(
        self, 
        query: str, 
        page: int = 1, 
        per_page: int = 10,
        orientation: Optional[str] = None,
        category: Optional[str] = None,
        order_by: str = "relevant",
        color: Optional[str] = None,
        content_filter: str = "low"
    ) -> SearchResult:
        """
        Search for photos asynchronously.
        
        Args:
            query: Search query
            page: Page number (1-based)
            per_page: Results per page (1-30, default 10)
            orientation: 'landscape', 'portrait', 'squarish'
            category: Category filter
            order_by: 'relevant', 'latest', 'popular'
            color: Color filter
            content_filter: 'low', 'high'
            
        Returns:
            SearchResult with images and metadata
        """
        start_time = asyncio.get_event_loop().time() if hasattr(asyncio.get_event_loop(), 'time') else 0
        
        # Validate parameters
        if per_page > 30:
            per_page = 30
        if page < 1:
            page = 1
        
        # Build query parameters
        params = {
            "query": query,
            "page": page,
            "per_page": per_page,
            "order_by": order_by,
            "content_filter": content_filter
        }
        
        if orientation:
            params["orientation"] = orientation
        if category:
            params["category"] = category
        if color:
            params["color"] = color
        
        # Create cache key
        cache_key = self._generate_cache_key("search_photos", params)
        
        # Check cache first
        if self.enable_caching:
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                self.logger.debug(f"Cache hit for search: {query}")
                return self._parse_search_result(cached_result, query, start_time)
        
        try:
            self.logger.info(f"Searching photos: '{query}' (page {page}, per_page {per_page})")
            
            # Make API request
            response = await self.get("/search/photos", params=params)
            
            # Parse and cache result
            if self.enable_caching:
                self._cache_result(cache_key, response)
            
            # Track API usage
            self.requests_made += 1
            
            return self._parse_search_result(response, query, start_time)
            
        except aiohttp.ClientResponseError as e:
            if e.status == 403:
                raise RateLimitError("Unsplash API rate limit exceeded")
            elif e.status == 401:
                raise ServiceError("Invalid Unsplash API key")
            else:
                raise ServiceError(f"Unsplash API error: {e}")
        except Exception as e:
            self.logger.error(f"Search failed for '{query}': {e}")
            raise ServiceError(f"Search failed: {e}")
    
    async def download_image(
        self, 
        image_url: str,
        progress_callback: Optional[callable] = None
    ) -> bytes:
        """
        Download image asynchronously with progress tracking.
        
        Args:
            image_url: URL of image to download
            progress_callback: Optional callback for progress updates
                              Called with (downloaded_bytes, total_bytes)
            
        Returns:
            Image data as bytes
        """
        try:
            self.logger.debug(f"Downloading image: {image_url[:50]}...")
            
            async with self._get_session() as session:
                async with session.get(image_url, timeout=self.timeout) as response:
                    response.raise_for_status()
                    
                    # Get content length for progress tracking
                    content_length = response.headers.get('content-length')
                    total_size = int(content_length) if content_length else 0
                    
                    downloaded = 0
                    chunks = []
                    
                    async for chunk in response.content.iter_chunked(8192):
                        chunks.append(chunk)
                        downloaded += len(chunk)
                        
                        # Report progress
                        if progress_callback and total_size > 0:
                            progress_callback(downloaded, total_size)
                    
                    image_data = b''.join(chunks)
                    
                    self.logger.debug(f"Downloaded {len(image_data)} bytes")
                    return image_data
                    
        except aiohttp.ClientError as e:
            self.logger.error(f"Download failed for {image_url}: {e}")
            raise ServiceError(f"Image download failed: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected download error: {e}")
            raise ServiceError(f"Download error: {e}")
    
    async def get_image_details(self, image_id: str) -> UnsplashImage:
        """
        Get detailed information about a specific image.
        
        Args:
            image_id: Unsplash image ID
            
        Returns:
            UnsplashImage with full details
        """
        cache_key = f"image_details_{image_id}"
        
        # Check cache
        if self.enable_caching:
            cached = self._get_cached_result(cache_key)
            if cached:
                return self._parse_image_data(cached)
        
        try:
            self.logger.debug(f"Getting image details: {image_id}")
            
            response = await self.get(f"/photos/{image_id}")
            
            # Cache result
            if self.enable_caching:
                self._cache_result(cache_key, response)
            
            return self._parse_image_data(response)
            
        except Exception as e:
            self.logger.error(f"Failed to get image details: {e}")
            raise ServiceError(f"Image details error: {e}")
    
    async def trigger_download(self, download_url: str) -> None:
        """
        Trigger download tracking (required by Unsplash API).
        
        Args:
            download_url: Download URL from image data
        """
        try:
            await self.get(download_url.replace('https://api.unsplash.com', ''))
            self.logger.debug("Download trigger sent")
        except Exception as e:
            # Don't fail the main operation if trigger fails
            self.logger.warning(f"Download trigger failed: {e}")
    
    def _parse_search_result(
        self, 
        response: Dict[str, Any], 
        query: str, 
        start_time: float
    ) -> SearchResult:
        """Parse API response into SearchResult object."""
        
        images = []
        for img_data in response.get("results", []):
            try:
                image = self._parse_image_data(img_data)
                images.append(image)
            except Exception as e:
                self.logger.warning(f"Failed to parse image data: {e}")
                continue
        
        execution_time = 0
        if hasattr(asyncio.get_event_loop(), 'time'):
            execution_time = asyncio.get_event_loop().time() - start_time
        
        return SearchResult(
            results=images,
            total=response.get("total", 0),
            total_pages=response.get("total_pages", 0),
            current_page=1,  # API doesn't return current page
            per_page=len(images),
            query=query,
            execution_time=execution_time
        )
    
    def _parse_image_data(self, img_data: Dict[str, Any]) -> UnsplashImage:
        """Parse individual image data from API response."""
        
        # Extract user info
        user_data = img_data.get("user", {})
        user_info = {
            "id": user_data.get("id", ""),
            "username": user_data.get("username", ""),
            "name": user_data.get("name", ""),
            "profile_image": user_data.get("profile_image", {}).get("medium", "")
        }
        
        # Extract tags
        tags = []
        for tag in img_data.get("tags", []):
            if isinstance(tag, dict):
                tags.append(tag.get("title", ""))
            else:
                tags.append(str(tag))
        
        # Extract location if available
        location = None
        if "location" in img_data and img_data["location"]:
            location = {
                "name": img_data["location"].get("name"),
                "city": img_data["location"].get("city"),
                "country": img_data["location"].get("country")
            }
        
        return UnsplashImage(
            id=img_data["id"],
            description=img_data.get("description"),
            alt_description=img_data.get("alt_description"),
            urls=img_data.get("urls", {}),
            user=user_info,
            width=img_data.get("width", 0),
            height=img_data.get("height", 0),
            likes=img_data.get("likes", 0),
            downloads=img_data.get("downloads"),
            location=location,
            tags=tags,
            color=img_data.get("color"),
            created_at=img_data.get("created_at")
        )
    
    def _generate_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key for request."""
        key_data = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_result(self, key: str) -> Optional[Dict[str, Any]]:
        """Get result from cache if available and not expired."""
        if key in self._cache:
            cached_item = self._cache[key]
            
            # Check if expired
            if (datetime.now() - cached_item["timestamp"]).seconds < self.cache_ttl:
                return cached_item["data"]
            else:
                # Remove expired item
                del self._cache[key]
        
        return None
    
    def _cache_result(self, key: str, data: Dict[str, Any]) -> None:
        """Cache API result."""
        self._cache[key] = {
            "data": data,
            "timestamp": datetime.now()
        }
        
        # Simple cache cleanup - remove oldest if too many items
        if len(self._cache) > 100:
            oldest_key = min(
                self._cache.keys(), 
                key=lambda k: self._cache[k]["timestamp"]
            )
            del self._cache[oldest_key]
    
    def get_api_usage(self) -> Dict[str, Any]:
        """Get API usage statistics."""
        return {
            "requests_made": self.requests_made,
            "last_reset": self.last_reset.isoformat(),
            "cached_items": len(self._cache)
        }
    
    def reset_api_usage(self) -> None:
        """Reset API usage counter (called hourly)."""
        self.requests_made = 0
        self.last_reset = datetime.now()
        self.logger.info("API usage counter reset")