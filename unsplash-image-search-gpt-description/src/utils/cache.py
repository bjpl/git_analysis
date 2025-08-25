"""
LRU cache implementation for image data and API responses.
"""

from collections import OrderedDict
from typing import Any, Optional, Dict


class LRUCache:
    """Least Recently Used cache implementation."""
    
    def __init__(self, max_size: int = 10):
        self.max_size = max_size
        self.cache: OrderedDict[str, Any] = OrderedDict()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache and mark as recently used."""
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def put(self, key: str, value: Any) -> None:
        """Put item in cache, removing oldest if necessary."""
        if key in self.cache:
            # Update existing key
            self.cache.move_to_end(key)
            self.cache[key] = value
        else:
            # Add new key
            if len(self.cache) >= self.max_size:
                # Remove oldest item
                self.cache.popitem(last=False)
            self.cache[key] = value
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)
    
    def is_full(self) -> bool:
        """Check if cache is at maximum capacity."""
        return len(self.cache) >= self.max_size
    
    def contains(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self.cache
    
    def remove(self, key: str) -> bool:
        """Remove specific key from cache."""
        if key in self.cache:
            del self.cache[key]
            return True
        return False


class ImageCache(LRUCache):
    """Specialized cache for image data."""
    
    def __init__(self, max_size: int = 10):
        super().__init__(max_size)
    
    def cache_image(self, url: str, image_data: bytes) -> None:
        """Cache image data by URL."""
        self.put(url, image_data)
    
    def get_image(self, url: str) -> Optional[bytes]:
        """Get cached image data by URL."""
        return self.get(url)
    
    def is_image_cached(self, url: str) -> bool:
        """Check if image is cached."""
        return self.contains(url)


class SearchCache(LRUCache):
    """Specialized cache for search results."""
    
    def __init__(self, max_size: int = 20):
        super().__init__(max_size)
    
    def cache_search_results(self, query: str, page: int, results: Dict[str, Any]) -> None:
        """Cache search results by query and page."""
        cache_key = f"{query}:{page}"
        self.put(cache_key, results)
    
    def get_search_results(self, query: str, page: int) -> Optional[Dict[str, Any]]:
        """Get cached search results."""
        cache_key = f"{query}:{page}"
        return self.get(cache_key)
    
    def is_search_cached(self, query: str, page: int) -> bool:
        """Check if search results are cached."""
        cache_key = f"{query}:{page}"
        return self.contains(cache_key)