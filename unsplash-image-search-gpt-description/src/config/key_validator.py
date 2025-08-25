"""
API Key Validator

Validates API keys for Unsplash and OpenAI services before storing them.
Provides real-time feedback on key validity and service availability.
"""

import re
import logging
import asyncio
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Try to import aiohttp, fall back to requests if not available
try:
    import aiohttp
    ASYNC_HTTP_AVAILABLE = True
except ImportError:
    import requests
    ASYNC_HTTP_AVAILABLE = False

logger = logging.getLogger(__name__)

class ValidationStatus(Enum):
    """API key validation status codes."""
    VALID = "valid"
    INVALID = "invalid"
    NETWORK_ERROR = "network_error"
    RATE_LIMITED = "rate_limited"
    UNKNOWN_ERROR = "unknown_error"

@dataclass
class ValidationResult:
    """Result of API key validation."""
    status: ValidationStatus
    message: str
    details: Optional[Dict] = None
    
    @property
    def is_valid(self) -> bool:
        return self.status == ValidationStatus.VALID

class APIKeyValidator:
    """Validates API keys for external services."""
    
    # API key format patterns
    UNSPLASH_KEY_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{43}$')
    OPENAI_KEY_PATTERN = re.compile(r'^sk-[a-zA-Z0-9]{48,}$')
    
    # Test endpoints
    UNSPLASH_TEST_URL = "https://api.unsplash.com/me"
    OPENAI_TEST_URL = "https://api.openai.com/v1/models"
    
    def __init__(self, timeout: int = 10):
        """
        Initialize validator with timeout settings.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
    
    def validate_key_format(self, service: str, key: str) -> ValidationResult:
        """
        Validate API key format without making network calls.
        
        Args:
            service: Service name ('unsplash' or 'openai')
            key: API key to validate
            
        Returns:
            ValidationResult with format validation status
        """
        if not key or not isinstance(key, str):
            return ValidationResult(
                status=ValidationStatus.INVALID,
                message="API key cannot be empty"
            )
        
        key = key.strip()
        
        if service.lower() == 'unsplash':
            if not self.UNSPLASH_KEY_PATTERN.match(key):
                return ValidationResult(
                    status=ValidationStatus.INVALID,
                    message="Invalid Unsplash key format. Expected 43-character alphanumeric string."
                )
        
        elif service.lower() == 'openai':
            if not self.OPENAI_KEY_PATTERN.match(key):
                return ValidationResult(
                    status=ValidationStatus.INVALID,
                    message="Invalid OpenAI key format. Expected 'sk-' prefix followed by 48+ characters."
                )
        
        else:
            return ValidationResult(
                status=ValidationStatus.INVALID,
                message=f"Unknown service: {service}"
            )
        
        return ValidationResult(
            status=ValidationStatus.VALID,
            message="Key format is valid"
        )
    
    async def validate_unsplash_key(self, key: str) -> ValidationResult:
        """
        Validate Unsplash API key by making a test request.
        
        Args:
            key: Unsplash access key
            
        Returns:
            ValidationResult with validation status
        """
        # First check format
        format_result = self.validate_key_format('unsplash', key)
        if not format_result.is_valid:
            return format_result
        
        try:
            if ASYNC_HTTP_AVAILABLE:
                # Use aiohttp for async requests
                headers = {
                    'Authorization': f'Client-ID {key.strip()}',
                    'Accept': 'application/json'
                }
                
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(self.UNSPLASH_TEST_URL, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            username = data.get('username', 'Unknown')
                            return ValidationResult(
                                status=ValidationStatus.VALID,
                                message=f"Valid Unsplash key for user: {username}",
                                details={'username': username, 'user_id': data.get('id')}
                            )
                        
                        elif response.status == 401:
                            return ValidationResult(
                                status=ValidationStatus.INVALID,
                                message="Invalid Unsplash API key. Please check your key."
                            )
                        
                        elif response.status == 403:
                            return ValidationResult(
                                status=ValidationStatus.RATE_LIMITED,
                                message="Unsplash API rate limit exceeded. Try again later."
                            )
                        
                        else:
                            error_text = await response.text()
                            return ValidationResult(
                                status=ValidationStatus.UNKNOWN_ERROR,
                                message=f"Unsplash API error (HTTP {response.status}): {error_text}"
                            )
            else:
                # Fallback to synchronous requests
                return await self._validate_unsplash_key_sync(key)
        
        except asyncio.TimeoutError:
            return ValidationResult(
                status=ValidationStatus.NETWORK_ERROR,
                message=f"Request timeout ({self.timeout}s). Check your internet connection."
            )
        
        except Exception as e:
            if ASYNC_HTTP_AVAILABLE and 'aiohttp' in str(type(e).__module__):
                return ValidationResult(
                    status=ValidationStatus.NETWORK_ERROR,
                    message=f"Network error: {str(e)}"
                )
            else:
                return await self._validate_unsplash_key_sync(key)
        
        except Exception as e:
            logger.error(f"Unexpected error validating Unsplash key: {e}")
            return ValidationResult(
                status=ValidationStatus.UNKNOWN_ERROR,
                message=f"Unexpected error: {str(e)}"
            )
    
    async def _validate_unsplash_key_sync(self, key: str) -> ValidationResult:
        """Fallback synchronous validation for Unsplash key."""
        try:
            headers = {
                'Authorization': f'Client-ID {key.strip()}',
                'Accept': 'application/json'
            }
            
            response = requests.get(self.UNSPLASH_TEST_URL, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                username = data.get('username', 'Unknown')
                return ValidationResult(
                    status=ValidationStatus.VALID,
                    message=f"Valid Unsplash key for user: {username}",
                    details={'username': username, 'user_id': data.get('id')}
                )
            
            elif response.status_code == 401:
                return ValidationResult(
                    status=ValidationStatus.INVALID,
                    message="Invalid Unsplash API key. Please check your key."
                )
            
            elif response.status_code == 403:
                return ValidationResult(
                    status=ValidationStatus.RATE_LIMITED,
                    message="Unsplash API rate limit exceeded. Try again later."
                )
            
            else:
                return ValidationResult(
                    status=ValidationStatus.UNKNOWN_ERROR,
                    message=f"Unsplash API error (HTTP {response.status_code}): {response.text}"
                )
        
        except requests.exceptions.Timeout:
            return ValidationResult(
                status=ValidationStatus.NETWORK_ERROR,
                message=f"Request timeout ({self.timeout}s). Check your internet connection."
            )
        
        except requests.exceptions.RequestException as e:
            return ValidationResult(
                status=ValidationStatus.NETWORK_ERROR,
                message=f"Network error: {str(e)}"
            )
        
        except Exception as e:
            logger.error(f"Unexpected error in sync validation: {e}")
            return ValidationResult(
                status=ValidationStatus.UNKNOWN_ERROR,
                message=f"Unexpected error: {str(e)}"
            )
    
    async def validate_openai_key(self, key: str, model: str = "gpt-4o-mini") -> ValidationResult:
        """
        Validate OpenAI API key by making a test request.
        
        Args:
            key: OpenAI API key
            model: Model to test access for
            
        Returns:
            ValidationResult with validation status
        """
        # First check format
        format_result = self.validate_key_format('openai', key)
        if not format_result.is_valid:
            return format_result
        
        try:
            if ASYNC_HTTP_AVAILABLE:
                headers = {
                    'Authorization': f'Bearer {key.strip()}',
                    'Content-Type': 'application/json'
                }
                
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    # First, list available models
                    async with session.get(self.OPENAI_TEST_URL, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            models = [m['id'] for m in data.get('data', [])]
                            
                            # Check if the specified model is available
                            if model not in models:
                                return ValidationResult(
                                    status=ValidationStatus.VALID,
                                    message=f"Valid OpenAI key, but model '{model}' not available. Using gpt-3.5-turbo.",
                                    details={'available_models': models[:10]}  # Limit to first 10
                                )
                            
                            return ValidationResult(
                                status=ValidationStatus.VALID,
                                message=f"Valid OpenAI key with access to {len(models)} models including {model}",
                                details={'model_count': len(models), 'has_model': model in models}
                            )
                        
                        elif response.status == 401:
                            error_data = await response.json()
                            error_msg = error_data.get('error', {}).get('message', 'Invalid API key')
                            return ValidationResult(
                                status=ValidationStatus.INVALID,
                                message=f"Invalid OpenAI API key: {error_msg}"
                            )
                        
                        elif response.status == 429:
                            return ValidationResult(
                                status=ValidationStatus.RATE_LIMITED,
                                message="OpenAI API rate limit exceeded. Try again later."
                            )
                        
                        elif response.status == 403:
                            return ValidationResult(
                                status=ValidationStatus.INVALID,
                                message="OpenAI API key lacks required permissions or billing is not set up."
                            )
                        
                        else:
                            error_text = await response.text()
                            return ValidationResult(
                                status=ValidationStatus.UNKNOWN_ERROR,
                                message=f"OpenAI API error (HTTP {response.status}): {error_text}"
                            )
            else:
                # Fallback to synchronous validation
                return await self._validate_openai_key_sync(key, model)
        
        except asyncio.TimeoutError:
            return ValidationResult(
                status=ValidationStatus.NETWORK_ERROR,
                message=f"Request timeout ({self.timeout}s). Check your internet connection."
            )
        
        except Exception as e:
            if ASYNC_HTTP_AVAILABLE and 'aiohttp' in str(type(e).__module__):
                return ValidationResult(
                    status=ValidationStatus.NETWORK_ERROR,
                    message=f"Network error: {str(e)}"
                )
            else:
                return await self._validate_openai_key_sync(key, model)
        
        except Exception as e:
            logger.error(f"Unexpected error validating OpenAI key: {e}")
            return ValidationResult(
                status=ValidationStatus.UNKNOWN_ERROR,
                message=f"Unexpected error: {str(e)}"
            )
    
    async def _validate_openai_key_sync(self, key: str, model: str = "gpt-4o-mini") -> ValidationResult:
        """Fallback synchronous validation for OpenAI key."""
        try:
            headers = {
                'Authorization': f'Bearer {key.strip()}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(self.OPENAI_TEST_URL, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                models = [m['id'] for m in data.get('data', [])]
                
                # Check if the specified model is available
                if model not in models:
                    return ValidationResult(
                        status=ValidationStatus.VALID,
                        message=f"Valid OpenAI key, but model '{model}' not available. Using gpt-3.5-turbo.",
                        details={'available_models': models[:10]}  # Limit to first 10
                    )
                
                return ValidationResult(
                    status=ValidationStatus.VALID,
                    message=f"Valid OpenAI key with access to {len(models)} models including {model}",
                    details={'model_count': len(models), 'has_model': model in models}
                )
            
            elif response.status_code == 401:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Invalid API key')
                except:
                    error_msg = 'Invalid API key'
                return ValidationResult(
                    status=ValidationStatus.INVALID,
                    message=f"Invalid OpenAI API key: {error_msg}"
                )
            
            elif response.status_code == 429:
                return ValidationResult(
                    status=ValidationStatus.RATE_LIMITED,
                    message="OpenAI API rate limit exceeded. Try again later."
                )
            
            elif response.status_code == 403:
                return ValidationResult(
                    status=ValidationStatus.INVALID,
                    message="OpenAI API key lacks required permissions or billing is not set up."
                )
            
            else:
                return ValidationResult(
                    status=ValidationStatus.UNKNOWN_ERROR,
                    message=f"OpenAI API error (HTTP {response.status_code}): {response.text}"
                )
        
        except requests.exceptions.Timeout:
            return ValidationResult(
                status=ValidationStatus.NETWORK_ERROR,
                message=f"Request timeout ({self.timeout}s). Check your internet connection."
            )
        
        except requests.exceptions.RequestException as e:
            return ValidationResult(
                status=ValidationStatus.NETWORK_ERROR,
                message=f"Network error: {str(e)}"
            )
        
        except Exception as e:
            logger.error(f"Unexpected error in sync OpenAI validation: {e}")
            return ValidationResult(
                status=ValidationStatus.UNKNOWN_ERROR,
                message=f"Unexpected error: {str(e)}"
            )
    
    async def validate_all_keys(self, unsplash_key: str, openai_key: str, 
                               gpt_model: str = "gpt-4o-mini") -> Dict[str, ValidationResult]:
        """
        Validate both API keys concurrently.
        
        Args:
            unsplash_key: Unsplash access key
            openai_key: OpenAI API key  
            gpt_model: GPT model to validate access for
            
        Returns:
            Dictionary with validation results for each service
        """
        tasks = [
            self.validate_unsplash_key(unsplash_key),
            self.validate_openai_key(openai_key, gpt_model)
        ]
        
        try:
            unsplash_result, openai_result = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            if isinstance(unsplash_result, Exception):
                unsplash_result = ValidationResult(
                    status=ValidationStatus.UNKNOWN_ERROR,
                    message=f"Error validating Unsplash key: {str(unsplash_result)}"
                )
            
            if isinstance(openai_result, Exception):
                openai_result = ValidationResult(
                    status=ValidationStatus.UNKNOWN_ERROR,
                    message=f"Error validating OpenAI key: {str(openai_result)}"
                )
            
            return {
                'unsplash': unsplash_result,
                'openai': openai_result
            }
        
        except Exception as e:
            logger.error(f"Error in concurrent validation: {e}")
            return {
                'unsplash': ValidationResult(
                    status=ValidationStatus.UNKNOWN_ERROR,
                    message=f"Validation error: {str(e)}"
                ),
                'openai': ValidationResult(
                    status=ValidationStatus.UNKNOWN_ERROR,
                    message=f"Validation error: {str(e)}"
                )
            }
    
    def get_validation_tips(self, service: str) -> str:
        """
        Get tips for obtaining API keys for a service.
        
        Args:
            service: Service name ('unsplash' or 'openai')
            
        Returns:
            Helpful tips for getting API keys
        """
        if service.lower() == 'unsplash':
            return (
                "To get an Unsplash API key:\n"
                "1. Go to https://unsplash.com/developers\n"
                "2. Create a developer account (free)\n"
                "3. Create a new application\n"
                "4. Copy the 'Access Key' (43 characters)\n\n"
                "Note: Free tier allows 50 requests per hour"
            )
        
        elif service.lower() == 'openai':
            return (
                "To get an OpenAI API key:\n"
                "1. Go to https://platform.openai.com/api-keys\n"
                "2. Sign in or create an account\n"
                "3. Click 'Create new secret key'\n"
                "4. Copy the key (starts with 'sk-')\n\n"
                "Note: Requires billing setup for usage beyond free tier"
            )
        
        return f"Unknown service: {service}"