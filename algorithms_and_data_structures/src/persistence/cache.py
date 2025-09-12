"""
Caching Layer for Persistence

Provides LRU cache implementation for frequently accessed data.
"""

import threading
import time
from typing import Any, Dict, Optional, Tuple
from collections import OrderedDict


class LRUCache:
    """
    Thread-safe Least Recently Used (LRU) cache implementation.
    """
    
    def __init__(self, max_size: int = 100, ttl: Optional[int] = None):
        """
        Initialize LRU cache.
        
        Args:
            max_size: Maximum number of items to store
            ttl: Time-to-live in seconds (None for no expiration)
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            value, timestamp = self._cache[key]
            
            # Check TTL expiration
            if self.ttl and time.time() - timestamp > self.ttl:
                del self._cache[key]
                self._misses += 1
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return value
    
    def put(self, key: str, value: Any) -> None:
        """
        Store value in cache.
        
        Args:
            key: Cache key
            value: Value to store
        """
        with self._lock:
            current_time = time.time()
            
            if key in self._cache:
                # Update existing key
                self._cache[key] = (value, current_time)
                self._cache.move_to_end(key)
            else:
                # Add new key
                self._cache[key] = (value, current_time)
                
                # Evict oldest item if cache is full
                if len(self._cache) > self.max_size:
                    self._cache.popitem(last=False)
    
    def delete(self, key: str) -> bool:
        """
        Remove key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was present and removed
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cached items."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
    
    def cleanup_expired(self) -> int:
        """
        Remove expired items from cache.
        
        Returns:
            Number of items removed
        """
        if not self.ttl:
            return 0
            
        with self._lock:
            current_time = time.time()
            expired_keys = []
            
            for key, (_, timestamp) in self._cache.items():
                if current_time - timestamp > self.ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)
    
    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self._cache)
    
    def __len__(self) -> int:
        """Get current cache size."""
        return self.size()
    
    @property
    def hit_rate(self) -> float:
        """Get cache hit rate as percentage."""
        with self._lock:
            total = self._hits + self._misses
            return (self._hits / total * 100) if total > 0 else 0.0
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': self.hit_rate,
                'ttl': self.ttl
            }
    
    def keys(self) -> list:
        """Get list of cached keys."""
        with self._lock:
            return list(self._cache.keys())


class CacheManager:
    """
    Manages multiple named caches with different configurations.
    """
    
    def __init__(self):
        self._caches: Dict[str, LRUCache] = {}
        self._lock = threading.RLock()
    
    def create_cache(self, name: str, max_size: int = 100, ttl: Optional[int] = None) -> LRUCache:
        """
        Create a named cache.
        
        Args:
            name: Cache name
            max_size: Maximum cache size
            ttl: Time-to-live in seconds
            
        Returns:
            Created LRUCache instance
        """
        with self._lock:
            cache = LRUCache(max_size, ttl)
            self._caches[name] = cache
            return cache
    
    def get_cache(self, name: str) -> Optional[LRUCache]:
        """
        Get cache by name.
        
        Args:
            name: Cache name
            
        Returns:
            LRUCache instance or None if not found
        """
        with self._lock:
            return self._caches.get(name)
    
    def delete_cache(self, name: str) -> bool:
        """
        Delete cache by name.
        
        Args:
            name: Cache name
            
        Returns:
            True if cache existed and was deleted
        """
        with self._lock:
            if name in self._caches:
                del self._caches[name]
                return True
            return False
    
    def clear_all(self) -> None:
        """Clear all caches."""
        with self._lock:
            for cache in self._caches.values():
                cache.clear()
    
    def cleanup_expired_all(self) -> Dict[str, int]:
        """
        Cleanup expired items from all caches.
        
        Returns:
            Dictionary mapping cache names to number of expired items removed
        """
        with self._lock:
            results = {}
            for name, cache in self._caches.items():
                results[name] = cache.cleanup_expired()
            return results
    
    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all caches."""
        with self._lock:
            return {name: cache.stats for name, cache in self._caches.items()}
    
    def list_caches(self) -> list:
        """Get list of cache names."""
        with self._lock:
            return list(self._caches.keys())


# Global cache manager instance
cache_manager = CacheManager()