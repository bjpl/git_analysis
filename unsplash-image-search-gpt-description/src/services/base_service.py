"""
Base service class providing common functionality for all API services.
Includes retry mechanisms, circuit breaker pattern, logging, and error handling.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Optional, Union
import aiohttp
import json
from datetime import datetime, timedelta


class ServiceError(Exception):
    """Base exception for service errors."""
    pass


class RateLimitError(ServiceError):
    """Raised when rate limit is exceeded."""
    pass


class AuthenticationError(ServiceError):
    """Raised when authentication fails."""
    pass


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class RetryConfig:
    """Configuration for retry logic."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    success_threshold: int = 3


class BaseService(ABC):
    """
    Base class for all API services.
    Provides common functionality: retry logic, circuit breaker, caching, and logging.
    """
    
    def __init__(
        self,
        name: str,
        base_url: str = "",
        api_key: Optional[str] = None,
        timeout: int = 30,
        retry_config: Optional[RetryConfig] = None,
        circuit_config: Optional[CircuitBreakerConfig] = None,
        enable_caching: bool = True,
        cache_ttl: int = 300,  # 5 minutes
    ):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.retry_config = retry_config or RetryConfig()
        self.circuit_config = circuit_config or CircuitBreakerConfig()
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        
        # Circuit breaker state
        self._circuit_state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
        
        # Cache
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        # HTTP session
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Setup logging
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.logger.setLevel(logging.INFO)
        
        # Rate limiting
        self._rate_limit_reset: Optional[datetime] = None
        self._rate_limit_remaining: Optional[int] = None
    
    async def __aenter__(self):
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _ensure_session(self) -> None:
        """Ensure HTTP session is created."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self._get_default_headers()
            )
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for requests."""
        headers = {
            'User-Agent': f'{self.name}-client/1.0',
            'Content-Type': 'application/json',
        }
        if self.api_key:
            headers.update(self._get_auth_headers())
        return headers
    
    @abstractmethod
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers. Must be implemented by subclasses."""
        pass
    
    def _get_cache_key(self, method: str, url: str, params: Optional[Dict] = None) -> str:
        """Generate cache key for request."""
        key_parts = [method.upper(), url]
        if params:
            sorted_params = sorted(params.items())
            key_parts.append(str(sorted_params))
        return "|".join(key_parts)
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if valid."""
        if not self.enable_caching or cache_key not in self._cache:
            return None
        
        cached = self._cache[cache_key]
        if datetime.now() - cached['timestamp'] > timedelta(seconds=self.cache_ttl):
            del self._cache[cache_key]
            return None
        
        self.logger.debug(f"Cache hit for {cache_key}")
        return cached['data']
    
    def _cache_response(self, cache_key: str, data: Any) -> None:
        """Cache response data."""
        if not self.enable_caching:
            return
        
        self._cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }
        
        # Simple cache cleanup - keep only last 100 entries
        if len(self._cache) > 100:
            oldest_key = min(self._cache.keys(), 
                           key=lambda k: self._cache[k]['timestamp'])
            del self._cache[oldest_key]
    
    def _can_execute(self) -> bool:
        """Check if request can be executed based on circuit breaker state."""
        now = datetime.now()
        
        if self._circuit_state == CircuitState.CLOSED:
            return True
        elif self._circuit_state == CircuitState.OPEN:
            if (self._last_failure_time and 
                now - self._last_failure_time > timedelta(seconds=self.circuit_config.recovery_timeout)):
                self._circuit_state = CircuitState.HALF_OPEN
                self._success_count = 0
                self.logger.info("Circuit breaker moving to HALF_OPEN state")
                return True
            return False
        elif self._circuit_state == CircuitState.HALF_OPEN:
            return True
        
        return False
    
    def _on_success(self) -> None:
        """Handle successful request for circuit breaker."""
        if self._circuit_state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.circuit_config.success_threshold:
                self._circuit_state = CircuitState.CLOSED
                self._failure_count = 0
                self.logger.info("Circuit breaker moving to CLOSED state")
        else:
            self._failure_count = max(0, self._failure_count - 1)
    
    def _on_failure(self, error: Exception) -> None:
        """Handle failed request for circuit breaker."""
        self._failure_count += 1
        self._last_failure_time = datetime.now()
        
        if (self._circuit_state == CircuitState.CLOSED and 
            self._failure_count >= self.circuit_config.failure_threshold):
            self._circuit_state = CircuitState.OPEN
            self.logger.warning("Circuit breaker moving to OPEN state")
        elif self._circuit_state == CircuitState.HALF_OPEN:
            self._circuit_state = CircuitState.OPEN
            self.logger.warning("Circuit breaker moving back to OPEN state")
    
    def _should_retry(self, error: Exception, attempt: int) -> bool:
        """Determine if request should be retried."""
        if attempt >= self.retry_config.max_retries:
            return False
        
        # Don't retry authentication errors
        if isinstance(error, AuthenticationError):
            return False
        
        # Don't retry if circuit is open
        if self._circuit_state == CircuitState.OPEN:
            return False
        
        # Retry on specific HTTP errors
        if isinstance(error, aiohttp.ClientError):
            return True
        
        # Retry on rate limit errors after delay
        if isinstance(error, RateLimitError):
            return True
        
        return False
    
    async def _calculate_delay(self, attempt: int, error: Optional[Exception] = None) -> float:
        """Calculate delay before retry."""
        if isinstance(error, RateLimitError) and self._rate_limit_reset:
            # Wait until rate limit resets
            reset_time = self._rate_limit_reset
            now = datetime.now()
            if reset_time > now:
                return (reset_time - now).total_seconds()
        
        # Exponential backoff with jitter
        delay = min(
            self.retry_config.base_delay * (self.retry_config.exponential_base ** attempt),
            self.retry_config.max_delay
        )
        
        if self.retry_config.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)  # Add 0-50% jitter
        
        return delay
    
    async def _make_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic and circuit breaker."""
        if not self._can_execute():
            raise ServiceError(f"Service {self.name} is unavailable (circuit breaker open)")
        
        await self._ensure_session()
        
        # Check cache first for GET requests
        cache_key = None
        if method.upper() == 'GET':
            cache_key = self._get_cache_key(method, url, kwargs.get('params'))
            cached = self._get_cached_response(cache_key)
            if cached is not None:
                return cached
        
        last_error = None
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                self.logger.debug(f"Making {method} request to {url} (attempt {attempt + 1})")
                
                async with self._session.request(method, url, **kwargs) as response:
                    # Update rate limit info from headers
                    self._update_rate_limit_info(response.headers)
                    
                    # Check for rate limiting
                    if response.status == 429:
                        raise RateLimitError("Rate limit exceeded")
                    
                    # Check for authentication errors
                    if response.status == 401:
                        raise AuthenticationError("Authentication failed")
                    
                    # Check for other HTTP errors
                    if response.status >= 400:
                        error_text = await response.text()
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=error_text
                        )
                    
                    # Parse response
                    if response.content_type == 'application/json':
                        data = await response.json()
                    else:
                        data = {'content': await response.read()}
                    
                    # Cache successful GET responses
                    if cache_key and method.upper() == 'GET':
                        self._cache_response(cache_key, data)
                    
                    self._on_success()
                    return data
                    
            except Exception as error:
                last_error = error
                self._on_failure(error)
                
                if not self._should_retry(error, attempt):
                    break
                
                if attempt < self.retry_config.max_retries:
                    delay = await self._calculate_delay(attempt, error)
                    self.logger.warning(
                        f"Request failed (attempt {attempt + 1}), retrying in {delay:.2f}s: {error}"
                    )
                    await asyncio.sleep(delay)
        
        # All retries exhausted
        self.logger.error(f"Request failed after {self.retry_config.max_retries + 1} attempts: {last_error}")
        raise last_error or ServiceError("Request failed")
    
    def _update_rate_limit_info(self, headers: Dict[str, str]) -> None:
        """Update rate limit information from response headers."""
        # Common rate limit headers
        remaining = headers.get('X-RateLimit-Remaining') or headers.get('X-Rate-Limit-Remaining')
        reset = headers.get('X-RateLimit-Reset') or headers.get('X-Rate-Limit-Reset')
        
        if remaining:
            try:
                self._rate_limit_remaining = int(remaining)
            except ValueError:
                pass
        
        if reset:
            try:
                reset_timestamp = int(reset)
                self._rate_limit_reset = datetime.fromtimestamp(reset_timestamp)
            except ValueError:
                pass
    
    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make GET request."""
        return await self._make_request('GET', url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make POST request."""
        return await self._make_request('POST', url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make PUT request."""
        return await self._make_request('PUT', url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make DELETE request."""
        return await self._make_request('DELETE', url, **kwargs)
    
    async def close(self) -> None:
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status information."""
        return {
            'name': self.name,
            'circuit_state': self._circuit_state.value,
            'failure_count': self._failure_count,
            'cache_size': len(self._cache),
            'rate_limit_remaining': self._rate_limit_remaining,
            'rate_limit_reset': self._rate_limit_reset.isoformat() if self._rate_limit_reset else None,
        }
    
    def clear_cache(self) -> None:
        """Clear service cache."""
        self._cache.clear()
        self.logger.info("Cache cleared")