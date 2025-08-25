"""
Async OpenAI Service

Fully async implementation of OpenAI API integration with proper error handling,
retry logic, and cancellation support. Fixes async/await issues in GPT operations.
"""

import aiohttp
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import time

from .base_service import BaseService, ServiceError, RateLimitError, AuthenticationError


@dataclass
class ImageAnalysisRequest:
    """Request for image analysis."""
    image_url: str
    prompt: str
    model: str = "gpt-4-vision-preview"
    max_tokens: int = 600
    temperature: float = 0.7
    context: Optional[str] = None
    language: str = "Spanish"


@dataclass
class TokenUsage:
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class CostEstimate:
    """Cost estimation for API usage."""
    prompt_cost: float
    completion_cost: float
    total_cost: float
    currency: str = "USD"


@dataclass
class AnalysisResult:
    """Result of image analysis."""
    content: str
    model: str
    token_usage: TokenUsage
    cost_estimate: CostEstimate
    request_id: Optional[str] = None
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    from_cache: bool = False


@dataclass
class VocabularyExtractionRequest:
    """Request for vocabulary extraction."""
    text: str
    target_language: str = "Spanish"
    max_words_per_category: int = 10
    avoid_common_words: bool = True
    include_context: bool = True


@dataclass
class VocabularyResult:
    """Result of vocabulary extraction."""
    categories: Dict[str, List[str]]
    total_words: int
    processing_time: float
    request_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class AsyncOpenAIService(BaseService):
    """
    Fully async OpenAI API service.
    
    Provides:
    - Async image analysis with GPT-4 Vision
    - Async vocabulary extraction
    - Async translation
    - Proper error handling and retries
    - Cost tracking and estimation
    - Request caching
    """
    
    # Token pricing (per 1K tokens) - update as needed
    PRICING = {
        "gpt-4-vision-preview": {
            "prompt": 0.01,      # $0.01 per 1K prompt tokens
            "completion": 0.03    # $0.03 per 1K completion tokens
        },
        "gpt-4": {
            "prompt": 0.03,
            "completion": 0.06
        },
        "gpt-3.5-turbo": {
            "prompt": 0.001,
            "completion": 0.002
        }
    }
    
    def __init__(
        self, 
        api_key: str,
        default_model: str = "gpt-4-vision-preview",
        timeout: int = 60,
        max_retries: int = 3,
        enable_caching: bool = True
    ):
        super().__init__(
            name="openai",
            base_url="https://api.openai.com/v1",
            api_key=api_key,
            timeout=timeout,
            enable_caching=enable_caching
        )
        
        self.default_model = default_model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        self.logger = logging.getLogger(f"{__name__}.AsyncOpenAIService")
        
        # Track API usage and costs
        self.total_tokens_used = 0
        self.estimated_cost = 0.0
        self.requests_made = 0
    
    async def analyze_image(self, request: ImageAnalysisRequest) -> AnalysisResult:
        """
        Analyze image with GPT-4 Vision asynchronously.
        
        Args:
            request: ImageAnalysisRequest with analysis parameters
            
        Returns:
            AnalysisResult with description and metadata
        """
        start_time = time.time()
        
        # Build prompt
        prompt = self._build_analysis_prompt(request)
        
        # Create cache key
        cache_key = self._generate_cache_key("analyze_image", {
            "image_url": request.image_url,
            "prompt": prompt,
            "model": request.model
        })
        
        # Check cache first
        if self.enable_caching:
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                self.logger.debug("Cache hit for image analysis")
                cached_result["from_cache"] = True
                return AnalysisResult(**cached_result)
        
        # Build API payload
        payload = {
            "model": request.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url", 
                            "image_url": {
                                "url": request.image_url, 
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }
        
        try:
            self.logger.info(f"Analyzing image with {request.model}")
            
            response = await self.post("/chat/completions", json=payload)
            
            # Parse response
            result = self._parse_analysis_response(
                response, 
                request.model, 
                start_time
            )
            
            # Cache result
            if self.enable_caching:
                cache_data = {
                    "content": result.content,
                    "model": result.model,
                    "token_usage": result.token_usage.__dict__,
                    "cost_estimate": result.cost_estimate.__dict__,
                    "processing_time": result.processing_time
                }
                self._cache_result(cache_key, cache_data)
            
            # Update usage tracking
            self.total_tokens_used += result.token_usage.total_tokens
            self.estimated_cost += result.cost_estimate.total_cost
            self.requests_made += 1
            
            return result
            
        except aiohttp.ClientResponseError as e:
            await self._handle_api_error(e)
        except Exception as e:
            self.logger.error(f"Image analysis failed: {e}")
            raise ServiceError(f"Image analysis error: {e}")
    
    async def extract_vocabulary(
        self, 
        request: VocabularyExtractionRequest
    ) -> VocabularyResult:
        """
        Extract vocabulary from text asynchronously.
        
        Args:
            request: VocabularyExtractionRequest with extraction parameters
            
        Returns:
            VocabularyResult with categorized vocabulary
        """
        start_time = time.time()
        
        # Build extraction prompt
        prompt = self._build_vocabulary_prompt(request)
        
        # Create cache key
        cache_key = self._generate_cache_key("extract_vocabulary", {
            "text": request.text[:100],  # First 100 chars for key
            "language": request.target_language,
            "max_words": request.max_words_per_category
        })
        
        # Check cache
        if self.enable_caching:
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return VocabularyResult(**cached_result)
        
        # Build API payload
        payload = {
            "model": "gpt-4",  # Use GPT-4 for better vocabulary extraction
            "messages": [
                {
                    "role": "system", 
                    "content": "You return only valid JSON. No disclaimers, no code fences."
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 800,
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }
        
        try:
            self.logger.info(f"Extracting vocabulary from {len(request.text)} chars")
            
            response = await self.post("/chat/completions", json=payload)
            
            # Parse vocabulary response
            result = self._parse_vocabulary_response(response, start_time)
            
            # Cache result
            if self.enable_caching:
                cache_data = result.__dict__.copy()
                del cache_data["timestamp"]  # Don't cache timestamp
                self._cache_result(cache_key, cache_data)
            
            # Update tracking
            if "usage" in response:
                tokens = response["usage"]["total_tokens"]
                self.total_tokens_used += tokens
                cost = self._calculate_cost("gpt-4", tokens, 0)
                self.estimated_cost += cost.total_cost
            
            self.requests_made += 1
            
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response for vocabulary extraction: {e}")
            # Return empty result instead of failing
            return VocabularyResult(
                categories={},
                total_words=0,
                processing_time=time.time() - start_time
            )
        except Exception as e:
            self.logger.error(f"Vocabulary extraction failed: {e}")
            raise ServiceError(f"Vocabulary extraction error: {e}")
    
    async def translate_text(
        self, 
        text: str,
        source_lang: str = "Spanish",
        target_lang: str = "English",
        context: Optional[str] = None
    ) -> str:
        """
        Translate text asynchronously.
        
        Args:
            text: Text to translate
            source_lang: Source language
            target_lang: Target language  
            context: Optional context for better translation
            
        Returns:
            Translated text
        """
        # Build translation prompt
        if context:
            prompt = (
                f"Translate the {source_lang} text '{text}' into {target_lang} "
                f"considering this context: {context}. "
                f"Provide only the translation."
            )
        else:
            prompt = (
                f"Translate the {source_lang} text '{text}' into {target_lang}. "
                f"Provide only the translation without additional text."
            )
        
        # Create cache key
        cache_key = self._generate_cache_key("translate", {
            "text": text,
            "source": source_lang,
            "target": target_lang,
            "context": context or ""
        })
        
        # Check cache
        if self.enable_caching:
            cached = self._get_cached_result(cache_key)
            if cached:
                return cached["translation"]
        
        payload = {
            "model": "gpt-3.5-turbo",  # Cheaper for translations
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100,
            "temperature": 0.0
        }
        
        try:
            response = await self.post("/chat/completions", json=payload)
            translation = response["choices"][0]["message"]["content"].strip()
            
            # Cache result
            if self.enable_caching:
                self._cache_result(cache_key, {"translation": translation})
            
            # Update tracking
            if "usage" in response:
                tokens = response["usage"]["total_tokens"]
                self.total_tokens_used += tokens
                cost = self._calculate_cost("gpt-3.5-turbo", tokens, 0)
                self.estimated_cost += cost.total_cost
            
            self.requests_made += 1
            
            return translation
            
        except Exception as e:
            self.logger.error(f"Translation failed for '{text}': {e}")
            raise ServiceError(f"Translation error: {e}")
    
    def _build_analysis_prompt(self, request: ImageAnalysisRequest) -> str:
        """Build prompt for image analysis."""
        
        base_prompt = f"""Analiza la imagen y descríbela en {request.language}.
        
IMPORTANTE: Describe SOLO lo que ves en esta imagen específica:
- ¿Qué objetos, personas o animales aparecen?
- ¿Cuáles son los colores predominantes?
- ¿Qué está sucediendo en la escena?
- ¿Dónde parece estar ubicada (interior/exterior)?
- ¿Qué detalles destacan?

Escribe 1-2 párrafos descriptivos y naturales."""
        
        if request.context:
            base_prompt += f"\n\nContexto adicional del usuario: {request.context}"
        
        return base_prompt
    
    def _build_vocabulary_prompt(self, request: VocabularyExtractionRequest) -> str:
        """Build prompt for vocabulary extraction."""
        
        prompt = f"""Del siguiente texto en {request.target_language}, extrae vocabulario útil para aprender el idioma.

TEXTO: {request.text}

Devuelve un JSON con estas categorías (pueden estar vacías si no hay ejemplos):
- "Sustantivos": incluye el artículo (el/la), máximo {request.max_words_per_category}
- "Verbos": forma conjugada encontrada, máximo {request.max_words_per_category}
- "Adjetivos": con concordancia de género si aplica, máximo {request.max_words_per_category}
- "Adverbios": solo los más relevantes, máximo 5
- "Frases clave": expresiones de 2-4 palabras que sean útiles, máximo {request.max_words_per_category}

"""
        
        if request.avoid_common_words:
            prompt += "Evita palabras muy comunes como: el, la, de, que, y, a, en, es, son\n"
        
        prompt += "Solo devuelve el JSON, sin comentarios adicionales."
        
        return prompt
    
    def _parse_analysis_response(
        self, 
        response: Dict[str, Any], 
        model: str, 
        start_time: float
    ) -> AnalysisResult:
        """Parse image analysis response."""
        
        content = response["choices"][0]["message"]["content"].strip()
        
        # Parse token usage
        usage_data = response.get("usage", {})
        token_usage = TokenUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0)
        )
        
        # Calculate cost estimate
        cost_estimate = self._calculate_cost(
            model, 
            token_usage.prompt_tokens, 
            token_usage.completion_tokens
        )
        
        return AnalysisResult(
            content=content,
            model=model,
            token_usage=token_usage,
            cost_estimate=cost_estimate,
            request_id=response.get("id"),
            processing_time=time.time() - start_time
        )
    
    def _parse_vocabulary_response(
        self, 
        response: Dict[str, Any], 
        start_time: float
    ) -> VocabularyResult:
        """Parse vocabulary extraction response."""
        
        content = response["choices"][0]["message"]["content"].strip()
        
        try:
            categories = json.loads(content)
            
            # Ensure expected categories exist
            expected_categories = ['Sustantivos', 'Verbos', 'Adjetivos', 'Adverbios', 'Frases clave']
            for category in expected_categories:
                if category not in categories:
                    categories[category] = []
            
            # Count total words
            total_words = sum(len(words) for words in categories.values())
            
            return VocabularyResult(
                categories=categories,
                total_words=total_words,
                processing_time=time.time() - start_time,
                request_id=response.get("id")
            )
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse vocabulary JSON: {e}")
            return VocabularyResult(
                categories={},
                total_words=0,
                processing_time=time.time() - start_time
            )
    
    def _calculate_cost(
        self, 
        model: str, 
        prompt_tokens: int, 
        completion_tokens: int
    ) -> CostEstimate:
        """Calculate cost estimate for API usage."""
        
        pricing = self.PRICING.get(model, self.PRICING["gpt-4"])
        
        prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing["completion"]
        total_cost = prompt_cost + completion_cost
        
        return CostEstimate(
            prompt_cost=prompt_cost,
            completion_cost=completion_cost,
            total_cost=total_cost
        )
    
    async def _handle_api_error(self, error: aiohttp.ClientResponseError) -> None:
        """Handle OpenAI API errors."""
        
        if error.status == 401:
            raise AuthenticationError("Invalid OpenAI API key")
        elif error.status == 429:
            raise RateLimitError("OpenAI API rate limit exceeded")
        elif error.status == 400:
            error_data = await error.json() if hasattr(error, 'json') else {}
            error_msg = error_data.get("error", {}).get("message", "Bad request")
            raise ServiceError(f"OpenAI API error: {error_msg}")
        else:
            raise ServiceError(f"OpenAI API error: HTTP {error.status}")
    
    def _generate_cache_key(self, operation: str, params: Dict[str, Any]) -> str:
        """Generate cache key for operation."""
        key_data = f"{operation}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_result(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired."""
        if key in self._cache:
            cached_item = self._cache[key]
            
            # Check if expired
            age_seconds = (datetime.now() - cached_item["timestamp"]).total_seconds()
            if age_seconds < self.cache_ttl:
                return cached_item["data"]
            else:
                del self._cache[key]
        
        return None
    
    def _cache_result(self, key: str, data: Dict[str, Any]) -> None:
        """Cache API result."""
        self._cache[key] = {
            "data": data,
            "timestamp": datetime.now()
        }
        
        # Simple cache cleanup
        if len(self._cache) > 50:  # Keep cache smaller for OpenAI
            oldest_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k]["timestamp"]
            )
            del self._cache[oldest_key]
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics."""
        return {
            "requests_made": self.requests_made,
            "total_tokens_used": self.total_tokens_used,
            "estimated_cost": round(self.estimated_cost, 4),
            "cached_items": len(self._cache)
        }