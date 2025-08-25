"""
Enhanced OpenAI Service with proper timeout handling and cancellation support.
"""

import json
import re
import time
from typing import Optional, Dict, Any, Callable
import logging
from openai import OpenAI
from openai._exceptions import (
    APIError,
    RateLimitError,
    APITimeoutError,
    APIConnectionError,
    AuthenticationError,
    BadRequestError
)

from .api_timeout_manager import api_timeout_manager, CancellationError, TimeoutError


class EnhancedOpenAIService:
    """Enhanced OpenAI service with robust timeout and error handling."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.logger = logging.getLogger(f"{__name__}.EnhancedOpenAIService")
        
        # Configure OpenAI client with timeout
        self.client = OpenAI(
            api_key=api_key,
            timeout=120.0,  # 2 minutes total timeout
            max_retries=2   # Built-in retries
        )
        
        # Track usage
        self.total_tokens_used = 0
        self.request_count = 0
    
    def _handle_openai_error(self, error: Exception, operation: str) -> None:
        """Handle OpenAI API errors with detailed messages."""
        error_msg = str(error)
        
        if isinstance(error, AuthenticationError):
            raise OpenAIAuthError(
                "Invalid OpenAI API key. Please check your configuration."
            ) from error
        elif isinstance(error, RateLimitError):
            raise OpenAIRateLimitError(
                "OpenAI rate limit exceeded. Please wait before making more requests."
            ) from error
        elif isinstance(error, APITimeoutError):
            raise OpenAITimeoutError(
                f"OpenAI API timeout during {operation}. The request took too long to complete."
            ) from error
        elif isinstance(error, APIConnectionError):
            raise OpenAINetworkError(
                f"Network error connecting to OpenAI during {operation}: {error_msg}"
            ) from error
        elif isinstance(error, BadRequestError):
            raise OpenAIAPIError(
                f"Bad request to OpenAI API during {operation}: {error_msg}"
            ) from error
        elif "insufficient_quota" in error_msg.lower():
            raise OpenAIQuotaError(
                "OpenAI API quota exceeded. Please check your account billing."
            ) from error
        else:
            raise OpenAIAPIError(
                f"OpenAI API error during {operation}: {error_msg}"
            ) from error
    
    def _execute_with_timeout(
        self,
        func: Callable,
        timeout: float,
        operation_id: str,
        *args,
        **kwargs
    ) -> Any:
        """Execute OpenAI API call with timeout and cancellation support."""
        try:
            result = api_timeout_manager.execute_with_timeout(
                func=func,
                timeout=timeout,
                operation_id=operation_id,
                *args,
                **kwargs
            )
            
            # Track token usage if response has usage info
            if hasattr(result, 'usage') and result.usage:
                self.total_tokens_used += result.usage.total_tokens
            
            self.request_count += 1
            return result
            
        except TimeoutError:
            self.logger.error(f"OpenAI operation {operation_id} timed out after {timeout}s")
            raise
        except CancellationError:
            self.logger.info(f"OpenAI operation {operation_id} was cancelled")
            raise
    
    def generate_image_description(
        self,
        image_url: str,
        user_note: str = "",
        operation_id: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> str:
        """Generate Spanish description of image using GPT Vision with timeout handling."""
        if not operation_id:
            operation_id = f"description_{int(time.time())}"
        
        # Validate image URL format
        if not image_url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid image URL format: {image_url}")
        
        if not image_url.startswith('https://images.unsplash.com/'):
            self.logger.warning(f"Unexpected image URL format: {image_url[:50]}...")
        
        self.logger.info(f"Generating description for image: {image_url[:50]}...")
        
        if progress_callback:
            progress_callback(f"Analyzing image with {self.model}...")
        
        # Create the prompt
        text_prompt = """Analiza la imagen que te estoy mostrando y descríbela en español latinoamericano.
        
IMPORTANTE: Describe SOLO lo que ves en esta imagen específica:
- ¿Qué objetos, personas o animales aparecen?
- ¿Cuáles son los colores predominantes?
- ¿Qué está sucediendo en la escena?
- ¿Dónde parece estar ubicada (interior/exterior)?
- ¿Qué detalles destacan?

Escribe 1-2 párrafos descriptivos y naturales."""
        
        if user_note:
            text_prompt += f"\n\nContexto adicional del usuario: {user_note}"
        
        def make_request():
            return self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": text_prompt},
                            {"type": "image_url", "image_url": {"url": image_url, "detail": "high"}}
                        ]
                    }
                ],
                max_tokens=600,
                temperature=0.7,
            )
        
        try:
            response = self._execute_with_timeout(
                func=make_request,
                timeout=120.0,  # 2 minutes for vision analysis
                operation_id=operation_id
            )
            
            description = response.choices[0].message.content.strip()
            
            if progress_callback:
                progress_callback("Description generated successfully")
            
            self.logger.info(f"Generated description ({len(description)} characters)")
            return description
            
        except Exception as e:
            self._handle_openai_error(e, "image description generation")
    
    def extract_vocabulary(
        self,
        description: str,
        operation_id: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, list]:
        """Extract vocabulary from Spanish description with timeout handling."""
        if not operation_id:
            operation_id = f"extract_{int(time.time())}"
        
        if not description.strip():
            return {}
        
        self.logger.info(f"Extracting vocabulary from description ({len(description)} chars)")
        
        if progress_callback:
            progress_callback("Extracting vocabulary with AI...")
        
        system_msg = (
            "You are a helpful assistant that returns only valid JSON. "
            "No disclaimers, no code fences, no extra text. If you have no data, return '{}'."
        )
        
        user_msg = f"""Del siguiente texto en español, extrae vocabulario útil para aprender el idioma.
        
TEXTO: {description}

Devuelve un JSON con estas categorías (pueden estar vacías si no hay ejemplos):
- "Sustantivos": incluye el artículo (el/la), máximo 10
- "Verbos": forma conjugada encontrada, máximo 10
- "Adjetivos": con concordancia de género si aplica, máximo 10
- "Adverbios": solo los más relevantes, máximo 5
- "Frases clave": expresiones de 2-4 palabras que sean útiles, máximo 10

Evita palabras muy comunes como: el, la, de, que, y, a, en, es, son
Solo devuelve el JSON, sin comentarios adicionales."""
        
        def make_request():
            return self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                max_tokens=600,
                temperature=0.3,
                response_format={"type": "json_object"}  # Force JSON response
            )
        
        try:
            response = self._execute_with_timeout(
                func=make_request,
                timeout=60.0,  # 1 minute for vocabulary extraction
                operation_id=operation_id
            )
            
            raw_str = response.choices[0].message.content.strip()
            self.logger.debug(f"Raw GPT response: {raw_str[:200]}...")
            
            # Parse JSON response
            try:
                groups = json.loads(raw_str)
            except json.JSONDecodeError as je:
                self.logger.error(f"JSON decode error: {je}. Raw response: {raw_str}")
                return {}
            
            # Ensure all expected keys exist
            expected_keys = ['Sustantivos', 'Verbos', 'Adjetivos', 'Adverbios', 'Frases clave']
            for key in expected_keys:
                if key not in groups:
                    groups[key] = []
            
            vocab_count = sum(len(v) for v in groups.values() if isinstance(v, list))
            
            if progress_callback:
                progress_callback(f"Extracted {vocab_count} vocabulary items")
            
            self.logger.info(f"Extracted vocabulary: {vocab_count} total items")
            return groups
            
        except Exception as e:
            self.logger.error(f"Error extracting vocabulary: {e}")
            self._handle_openai_error(e, "vocabulary extraction")
            return {}
    
    def translate_word(
        self,
        word: str,
        context: str = "",
        operation_id: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> str:
        """Translate Spanish word to US English with timeout handling."""
        if not operation_id:
            operation_id = f"translate_{word}_{int(time.time())}"
        
        if not word.strip():
            return ""
        
        self.logger.info(f"Translating word: '{word}'")
        
        if progress_callback:
            progress_callback(f"Translating '{word}'...")
        
        if context:
            prompt = (
                f"Translate the Latin American Spanish word '{word}' into US English "
                f"as used in the following sentence:\n\n{context}\n\nProvide only the translation."
            )
        else:
            prompt = f"Translate the Latin American Spanish word '{word}' into US English without additional text."
        
        def make_request():
            return self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.0,
            )
        
        try:
            response = self._execute_with_timeout(
                func=make_request,
                timeout=30.0,  # 30 seconds for translation
                operation_id=operation_id
            )
            
            translation = response.choices[0].message.content.strip()
            
            if progress_callback:
                progress_callback(f"Translated: {word} → {translation}")
            
            self.logger.info(f"Translation: '{word}' → '{translation}'")
            return translation
            
        except Exception as e:
            self.logger.error(f"Translation error for '{word}': {e}")
            self._handle_openai_error(e, "translation")
            return ""
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get service usage statistics."""
        return {
            'total_tokens_used': self.total_tokens_used,
            'request_count': self.request_count,
            'model': self.model
        }
    
    def cancel_operation(self, operation_id: str) -> bool:
        """Cancel specific operation."""
        return api_timeout_manager.cancel_operation(operation_id)
    
    def cancel_all_operations(self) -> int:
        """Cancel all active operations."""
        return api_timeout_manager.cancel_all_operations()


# Custom exceptions
class OpenAIError(Exception):
    """Base OpenAI service error."""
    pass


class OpenAIAuthError(OpenAIError):
    """OpenAI authentication error."""
    pass


class OpenAIRateLimitError(OpenAIError):
    """OpenAI rate limit error."""
    pass


class OpenAITimeoutError(OpenAIError):
    """OpenAI timeout error."""
    pass


class OpenAINetworkError(OpenAIError):
    """OpenAI network error."""
    pass


class OpenAIQuotaError(OpenAIError):
    """OpenAI quota exceeded error."""
    pass


class OpenAIAPIError(OpenAIError):
    """General OpenAI API error."""
    pass
