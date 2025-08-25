"""
Memory management utilities for efficient resource handling.
"""

import gc
import weakref
import threading
import time
from typing import Dict, Any, Optional, Set, TypeVar, Generic
from collections import OrderedDict
import psutil
from PIL import Image


T = TypeVar('T')


class LRUCache(Generic[T]):
    """Thread-safe LRU cache with size and memory limits."""
    
    def __init__(self, max_size: int = 100, max_memory_mb: float = 100.0):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: OrderedDict[str, T] = OrderedDict()
        self.memory_usage: Dict[str, int] = {}
        self.total_memory = 0
        self._lock = threading.RLock()
        
    def get(self, key: str) -> Optional[T]:
        """Get item from cache."""
        with self._lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
            
    def put(self, key: str, value: T, size_bytes: Optional[int] = None):
        """Put item in cache."""
        with self._lock:
            # Calculate memory usage if not provided
            if size_bytes is None:
                size_bytes = self._estimate_size(value)
                
            # Remove existing item if updating
            if key in self.cache:
                self.total_memory -= self.memory_usage[key]
                
            # Ensure we have space
            self._make_space(size_bytes)
            
            # Add new item
            self.cache[key] = value
            self.memory_usage[key] = size_bytes
            self.total_memory += size_bytes
            
            # Move to end
            self.cache.move_to_end(key)
            
    def remove(self, key: str) -> bool:
        """Remove item from cache."""
        with self._lock:
            if key in self.cache:
                self.total_memory -= self.memory_usage[key]
                del self.cache[key]
                del self.memory_usage[key]
                return True
            return False
            
    def clear(self):
        """Clear all items from cache."""
        with self._lock:
            self.cache.clear()
            self.memory_usage.clear()
            self.total_memory = 0
            
    def _make_space(self, needed_bytes: int):
        """Make space for new item by removing LRU items."""
        while (len(self.cache) >= self.max_size or 
               self.total_memory + needed_bytes > self.max_memory_bytes):
            if not self.cache:
                break
                
            # Remove least recently used item
            lru_key, _ = self.cache.popitem(last=False)
            self.total_memory -= self.memory_usage[lru_key]
            del self.memory_usage[lru_key]
            
    def _estimate_size(self, value: T) -> int:
        """Estimate memory size of value."""
        if isinstance(value, Image.Image):
            # PIL Image size estimation
            return value.width * value.height * len(value.getbands()) * 4
        elif isinstance(value, bytes):
            return len(value)
        elif isinstance(value, str):
            return len(value.encode('utf-8'))
        else:
            # Rough estimation for other objects
            return 1024  # 1KB default
            
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'memory_usage_mb': self.total_memory / 1024 / 1024,
                'memory_limit_mb': self.max_memory_bytes / 1024 / 1024,
                'hit_ratio': 0  # TODO: Implement hit tracking
            }


class WeakReferenceManager:
    """Manages weak references to objects for automatic cleanup."""
    
    def __init__(self):
        self._refs: Set[weakref.ref] = set()
        self._cleanup_callbacks: Dict[int, callable] = {}
        
    def add_reference(self, obj: Any, cleanup_callback: Optional[callable] = None):
        """Add weak reference to object with optional cleanup callback."""
        def on_delete(ref):
            self._refs.discard(ref)
            if cleanup_callback:
                cleanup_callback()
                
        ref = weakref.ref(obj, on_delete)
        self._refs.add(ref)
        
        if cleanup_callback:
            self._cleanup_callbacks[id(obj)] = cleanup_callback
            
    def cleanup_dead_references(self):
        """Clean up dead references."""
        dead_refs = {ref for ref in self._refs if ref() is None}
        self._refs -= dead_refs
        
    def get_live_count(self) -> int:
        """Get count of live references."""
        return sum(1 for ref in self._refs if ref() is not None)


class MemoryManager:
    """
    Comprehensive memory management system.
    
    Features:
    - Image cache with automatic eviction
    - Weak reference management
    - Memory monitoring and cleanup
    - Garbage collection optimization
    """
    
    def __init__(self, image_cache_size: int = 50, image_cache_memory_mb: float = 200.0):
        self.image_cache = LRUCache[bytes](image_cache_size, image_cache_memory_mb)
        self.processed_image_cache = LRUCache[Image.Image](100, 300.0)
        self.weak_refs = WeakReferenceManager()
        
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._memory_threshold_mb = 500.0  # Warning threshold
        self._cleanup_threshold_mb = 800.0  # Aggressive cleanup threshold
        
        # Memory statistics
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'cleanups_performed': 0,
            'peak_memory_mb': 0.0
        }
        
    def start_monitoring(self, interval: float = 30.0):
        """Start background memory monitoring."""
        if self._monitoring:
            return
            
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop memory monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
            
    def _monitor_loop(self, interval: float):
        """Memory monitoring loop."""
        while self._monitoring:
            try:
                current_memory = self.get_memory_usage_mb()
                self.stats['peak_memory_mb'] = max(self.stats['peak_memory_mb'], current_memory)
                
                if current_memory > self._cleanup_threshold_mb:
                    self.perform_aggressive_cleanup()
                elif current_memory > self._memory_threshold_mb:
                    self.perform_cleanup()
                    
            except Exception as e:
                print(f"Error in memory monitoring: {e}")
                
            time.sleep(interval)
            
    def get_image_from_cache(self, url: str) -> Optional[bytes]:
        """Get image data from cache."""
        result = self.image_cache.get(url)
        if result:
            self.stats['cache_hits'] += 1
        else:
            self.stats['cache_misses'] += 1
        return result
        
    def put_image_in_cache(self, url: str, data: bytes):
        """Put image data in cache."""
        self.image_cache.put(url, data, len(data))
        
    def get_processed_image_from_cache(self, key: str) -> Optional[Image.Image]:
        """Get processed PIL image from cache."""
        return self.processed_image_cache.get(key)
        
    def put_processed_image_in_cache(self, key: str, image: Image.Image):
        """Put processed PIL image in cache."""
        self.processed_image_cache.put(key, image)
        
    def register_for_cleanup(self, obj: Any, cleanup_callback: Optional[callable] = None):
        """Register object for automatic cleanup."""
        self.weak_refs.add_reference(obj, cleanup_callback)
        
    def perform_cleanup(self):
        """Perform memory cleanup."""
        # Clean up dead weak references
        self.weak_refs.cleanup_dead_references()
        
        # Force garbage collection
        collected = gc.collect()
        
        self.stats['cleanups_performed'] += 1
        
        print(f"Memory cleanup: collected {collected} objects")
        
    def perform_aggressive_cleanup(self):
        """Perform aggressive memory cleanup."""
        print("Performing aggressive memory cleanup...")
        
        # Clear half of image cache
        current_size = len(self.image_cache.cache)
        for i, key in enumerate(list(self.image_cache.cache.keys())):
            if i >= current_size // 2:
                break
            self.image_cache.remove(key)
            
        # Clear processed image cache
        self.processed_image_cache.clear()
        
        # Regular cleanup
        self.perform_cleanup()
        
        # Multiple GC passes
        for _ in range(3):
            gc.collect()
            
        print(f"Aggressive cleanup completed. Memory: {self.get_memory_usage_mb():.1f}MB")
        
    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0
            
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get memory and cache statistics."""
        return {
            'memory_usage_mb': self.get_memory_usage_mb(),
            'peak_memory_mb': self.stats['peak_memory_mb'],
            'image_cache': self.image_cache.get_stats(),
            'processed_cache': self.processed_image_cache.get_stats(),
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'hit_ratio': (self.stats['cache_hits'] / 
                         max(1, self.stats['cache_hits'] + self.stats['cache_misses'])),
            'cleanups_performed': self.stats['cleanups_performed'],
            'live_references': self.weak_refs.get_live_count()
        }
        
    def set_memory_thresholds(self, warning_mb: float, cleanup_mb: float):
        """Set memory usage thresholds for automatic cleanup."""
        self._memory_threshold_mb = warning_mb
        self._cleanup_threshold_mb = cleanup_mb
        
    def clear_all_caches(self):
        """Clear all caches."""
        self.image_cache.clear()
        self.processed_image_cache.clear()
        self.perform_cleanup()