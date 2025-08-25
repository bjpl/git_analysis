"""
Input debouncing utilities for performance optimization.
"""

import threading
import time
from typing import Callable, Any, Optional, Dict


class Debouncer:
    """
    Debounces function calls to reduce unnecessary executions.
    
    Useful for search inputs, API calls, and other user-triggered events
    that shouldn't fire on every keystroke.
    """
    
    def __init__(self, delay: float = 0.5):
        """
        Initialize debouncer.
        
        Args:
            delay: Delay in seconds before executing the debounced function
        """
        self.delay = delay
        self.timers: Dict[str, threading.Timer] = {}
        self.lock = threading.Lock()
        
    def debounce(
        self,
        key: str,
        func: Callable,
        *args,
        **kwargs
    ):
        """
        Debounce a function call.
        
        Args:
            key: Unique identifier for this debounced function
            func: Function to execute after delay
            *args: Arguments to pass to function
            **kwargs: Keyword arguments to pass to function
        """
        with self.lock:
            # Cancel existing timer for this key
            if key in self.timers:
                self.timers[key].cancel()
                
            # Create new timer
            timer = threading.Timer(
                self.delay,
                self._execute_debounced,
                args=(key, func, args, kwargs)
            )
            self.timers[key] = timer
            timer.start()
            
    def _execute_debounced(self, key: str, func: Callable, args: tuple, kwargs: dict):
        """Execute debounced function and clean up timer."""
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(f"Error in debounced function {key}: {e}")
        finally:
            with self.lock:
                if key in self.timers:
                    del self.timers[key]
                    
    def cancel(self, key: str):
        """Cancel a pending debounced call."""
        with self.lock:
            if key in self.timers:
                self.timers[key].cancel()
                del self.timers[key]
                
    def cancel_all(self):
        """Cancel all pending debounced calls."""
        with self.lock:
            for timer in self.timers.values():
                timer.cancel()
            self.timers.clear()
            
    def is_pending(self, key: str) -> bool:
        """Check if a debounced call is pending."""
        with self.lock:
            return key in self.timers
            
    def set_delay(self, delay: float):
        """Update the debounce delay."""
        self.delay = delay
        
    def get_pending_count(self) -> int:
        """Get number of pending debounced calls."""
        with self.lock:
            return len(self.timers)


class SearchDebouncer(Debouncer):
    """
    Specialized debouncer for search inputs with additional features.
    """
    
    def __init__(self, delay: float = 0.3, min_length: int = 2):
        """
        Initialize search debouncer.
        
        Args:
            delay: Delay before search execution
            min_length: Minimum search term length to trigger search
        """
        super().__init__(delay)
        self.min_length = min_length
        self.last_search_term = ""
        self.search_history = []
        
    def debounce_search(
        self,
        search_term: str,
        search_func: Callable[[str], Any],
        force: bool = False
    ):
        """
        Debounce search with additional logic.
        
        Args:
            search_term: Current search term
            search_func: Function to call with search term
            force: Force search even if term hasn't changed
        """
        # Clean up search term
        search_term = search_term.strip()
        
        # Skip if term too short
        if len(search_term) < self.min_length and not force:
            self.cancel("search")
            return
            
        # Skip if same as last search (unless forced)
        if search_term == self.last_search_term and not force:
            return
            
        # Update last search term
        self.last_search_term = search_term
        
        # Add to history
        if search_term and search_term not in self.search_history:
            self.search_history.append(search_term)
            # Keep only last 20 searches
            if len(self.search_history) > 20:
                self.search_history.pop(0)
                
        # Debounce the search
        self.debounce("search", search_func, search_term)
        
    def get_search_history(self) -> list:
        """Get search history."""
        return self.search_history.copy()
        
    def clear_history(self):
        """Clear search history."""
        self.search_history.clear()


class APICallDebouncer(Debouncer):
    """
    Specialized debouncer for API calls with rate limiting awareness.
    """
    
    def __init__(
        self,
        delay: float = 1.0,
        rate_limit: Optional[int] = None,
        rate_window: float = 60.0
    ):
        """
        Initialize API call debouncer.
        
        Args:
            delay: Delay before API call
            rate_limit: Maximum calls per rate_window (None for no limit)
            rate_window: Time window for rate limiting in seconds
        """
        super().__init__(delay)
        self.rate_limit = rate_limit
        self.rate_window = rate_window
        self.call_timestamps = []
        self.call_count = 0
        
    def debounce_api_call(
        self,
        key: str,
        api_func: Callable,
        *args,
        **kwargs
    ):
        """
        Debounce API call with rate limiting.
        
        Args:
            key: Unique identifier for the API call
            api_func: API function to call
            *args: Arguments for API function
            **kwargs: Keyword arguments for API function
        """
        # Check rate limit
        if self.rate_limit and not self._can_make_call():
            print(f"Rate limit exceeded for API call {key}")
            return False
            
        # Wrap API function to track calls
        def tracked_api_call(*args, **kwargs):
            self._record_call()
            return api_func(*args, **kwargs)
            
        # Debounce the call
        self.debounce(key, tracked_api_call, *args, **kwargs)
        return True
        
    def _can_make_call(self) -> bool:
        """Check if we can make an API call within rate limits."""
        if not self.rate_limit:
            return True
            
        current_time = time.time()
        # Remove old timestamps
        cutoff_time = current_time - self.rate_window
        self.call_timestamps = [
            ts for ts in self.call_timestamps if ts > cutoff_time
        ]
        
        return len(self.call_timestamps) < self.rate_limit
        
    def _record_call(self):
        """Record an API call timestamp."""
        self.call_timestamps.append(time.time())
        self.call_count += 1
        
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        current_time = time.time()
        cutoff_time = current_time - self.rate_window
        recent_calls = [ts for ts in self.call_timestamps if ts > cutoff_time]
        
        return {
            'calls_in_window': len(recent_calls),
            'rate_limit': self.rate_limit,
            'window_seconds': self.rate_window,
            'can_make_call': self._can_make_call(),
            'total_calls': self.call_count,
            'next_reset': cutoff_time + self.rate_window if recent_calls else current_time
        }
        
    def reset_rate_limit(self):
        """Reset rate limit counters."""
        self.call_timestamps.clear()


# Utility functions for common debouncing patterns

def create_search_debouncer(
    delay: float = 0.3,
    min_length: int = 2
) -> SearchDebouncer:
    """Create a search debouncer with common settings."""
    return SearchDebouncer(delay, min_length)


def create_api_debouncer(
    delay: float = 1.0,
    calls_per_minute: Optional[int] = None
) -> APICallDebouncer:
    """Create an API debouncer with rate limiting."""
    return APICallDebouncer(delay, calls_per_minute, 60.0)


# Decorator for debouncing methods
def debounced(delay: float = 0.5):
    """
    Decorator to debounce method calls.
    
    Usage:
        @debounced(0.3)
        def search(self, term):
            # This will be debounced
            pass
    """
    def decorator(func):
        debouncer = Debouncer(delay)
        
        def wrapper(self, *args, **kwargs):
            # Use method name + instance id as key
            key = f"{func.__name__}_{id(self)}"
            debouncer.debounce(key, func, self, *args, **kwargs)
            
        wrapper._debouncer = debouncer
        return wrapper
    return decorator