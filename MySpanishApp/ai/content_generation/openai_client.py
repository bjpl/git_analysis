"""
OpenAI Client with Retry Logic and Rate Limiting
Handles GPT-4 integration for content generation
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import hashlib
import os

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI library not installed. Install with: pip install openai")


@dataclass
class GenerationRequest:
    """Request for content generation"""
    prompt: str
    content_type: str
    difficulty_level: str
    user_level: str
    max_tokens: int = 500
    temperature: float = 0.7
    context: Optional[Dict] = None


@dataclass
class GenerationResponse:
    """Response from content generation"""
    content: str
    request_id: str
    timestamp: datetime
    tokens_used: int
    cost_estimate: float
    cached: bool = False


class TokenBucket:
    """Token bucket for rate limiting"""
    
    def __init__(self, capacity: int, refill_rate: int):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from bucket"""
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = int(elapsed * self.refill_rate)
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now


class OpenAIClient:
    """OpenAI client with retry logic, caching, and rate limiting"""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 model: str = "gpt-4",
                 max_retries: int = 3,
                 retry_delay: float = 1.0,
                 cache_size: int = 1000,
                 requests_per_minute: int = 50):
        """
        Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
            model: Model to use for generation
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries in seconds
            cache_size: Maximum number of cached responses
            requests_per_minute: Rate limiting
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library is required. Install with: pip install openai")
        
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Rate limiting
        self.rate_limiter = TokenBucket(capacity=requests_per_minute, refill_rate=requests_per_minute / 60)
        
        # Response cache
        self.cache: Dict[str, GenerationResponse] = {}
        self.cache_size = cache_size
        
        # Usage tracking
        self.total_tokens_used = 0
        self.total_requests = 0
        self.failed_requests = 0
        
        self.logger = logging.getLogger(__name__)
    
    async def generate_content(self, request: GenerationRequest) -> GenerationResponse:
        """
        Generate content using GPT-4
        
        Args:
            request: Generation request
            
        Returns:
            Generated content response
        """
        # Check cache first
        cache_key = self._generate_cache_key(request)
        if cache_key in self.cache:
            cached_response = self.cache[cache_key]
            cached_response.cached = True
            return cached_response
        
        # Rate limiting
        if not self.rate_limiter.consume():
            raise Exception("Rate limit exceeded. Please wait before making more requests.")
        
        self.total_requests += 1
        request_id = f"req_{int(time.time())}_{hash(request.prompt) % 10000}"
        
        for attempt in range(self.max_retries):
            try:
                response = await self._make_api_call(request, request_id)
                
                # Cache successful response
                self._cache_response(cache_key, response)
                
                return response
                
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt == self.max_retries - 1:
                    self.failed_requests += 1
                    raise Exception(f"Failed to generate content after {self.max_retries} attempts: {str(e)}")
                
                # Exponential backoff
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
    
    async def _make_api_call(self, request: GenerationRequest, request_id: str) -> GenerationResponse:
        """Make actual API call to OpenAI"""
        messages = [
            {
                "role": "system",
                "content": self._build_system_message(request)
            },
            {
                "role": "user",
                "content": request.prompt
            }
        ]
        
        # Add context if provided
        if request.context:
            context_message = f"Context: {json.dumps(request.context, indent=2)}"
            messages.insert(1, {"role": "user", "content": context_message})
        
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        
        content = response.choices[0].message.content.strip()
        tokens_used = response.usage.total_tokens
        cost_estimate = self._estimate_cost(tokens_used)
        
        self.total_tokens_used += tokens_used
        
        return GenerationResponse(
            content=content,
            request_id=request_id,
            timestamp=datetime.now(),
            tokens_used=tokens_used,
            cost_estimate=cost_estimate,
            cached=False
        )
    
    def _build_system_message(self, request: GenerationRequest) -> str:
        """Build system message based on request parameters"""
        base_message = "You are an expert Spanish language teacher and content creator."
        
        level_descriptions = {
            "beginner": "Create content for absolute beginners who know very basic vocabulary and present tense.",
            "elementary": "Create content for students who know basic grammar and can form simple sentences.",
            "intermediate": "Create content for students who understand past/future tenses and can express opinions.",
            "advanced": "Create content for students who can discuss complex topics and need nuanced language practice.",
            "native": "Create content at native speaker level with idiomatic expressions and cultural nuances."
        }
        
        difficulty_instructions = {
            "easy": "Keep the language simple and provide clear explanations.",
            "medium": "Use moderate complexity with some challenging elements.",
            "hard": "Include complex grammar structures and advanced vocabulary."
        }
        
        content_type_instructions = {
            "vocabulary": "Focus on practical vocabulary with usage examples and memory aids.",
            "grammar": "Explain grammar rules clearly with examples and common mistakes to avoid.",
            "conversation": "Create natural dialogue with cultural context and conversation tips.",
            "exercise": "Design engaging exercises that test comprehension and application.",
            "story": "Write compelling stories that illustrate language concepts naturally.",
            "explanation": "Provide clear, comprehensive explanations with examples."
        }
        
        system_message = f"""
{base_message}

Target Level: {request.user_level.title()}
{level_descriptions.get(request.user_level.lower(), '')}

Content Type: {request.content_type.title()}
{content_type_instructions.get(request.content_type.lower(), '')}

Difficulty: {request.difficulty_level.title()}
{difficulty_instructions.get(request.difficulty_level.lower(), '')}

Guidelines:
- Always provide content in Spanish with English translations when helpful
- Include cultural context when relevant
- Make content engaging and practical for real-world use
- Provide pronunciation hints for difficult words
- Structure content clearly with appropriate formatting
- Include memory aids or learning tips when possible

Output Format: Provide well-structured content in JSON format when appropriate, or clear markdown formatting.
"""
        
        return system_message.strip()
    
    def _generate_cache_key(self, request: GenerationRequest) -> str:
        """Generate cache key for request"""
        key_data = {
            'prompt': request.prompt,
            'content_type': request.content_type,
            'difficulty_level': request.difficulty_level,
            'user_level': request.user_level,
            'temperature': request.temperature,
            'context': request.context
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _cache_response(self, cache_key: str, response: GenerationResponse) -> None:
        """Cache response with LRU eviction"""
        if len(self.cache) >= self.cache_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].timestamp)
            del self.cache[oldest_key]
        
        self.cache[cache_key] = response
    
    def _estimate_cost(self, tokens: int) -> float:
        """Estimate cost based on token usage (rough GPT-4 pricing)"""
        # Approximate pricing (as of 2024)
        cost_per_1k_tokens = 0.03  # This varies by model
        return (tokens / 1000) * cost_per_1k_tokens
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        success_rate = (self.total_requests - self.failed_requests) / max(1, self.total_requests)
        
        return {
            'total_requests': self.total_requests,
            'failed_requests': self.failed_requests,
            'success_rate': success_rate,
            'total_tokens_used': self.total_tokens_used,
            'estimated_total_cost': self._estimate_cost(self.total_tokens_used),
            'cache_size': len(self.cache),
            'cache_hit_rate': self._calculate_cache_hit_rate()
        }
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        # This would need to be tracked separately in a real implementation
        # For now, return estimated based on cache size
        if self.total_requests == 0:
            return 0.0
        return min(0.3, len(self.cache) / max(1, self.total_requests))
    
    def clear_cache(self) -> None:
        """Clear response cache"""
        self.cache.clear()
    
    def set_model(self, model: str) -> None:
        """Change the model used for generation"""
        self.model = model
        self.clear_cache()  # Clear cache when changing models
    
    def batch_generate(self, requests: List[GenerationRequest]) -> List[GenerationResponse]:
        """Generate content for multiple requests (synchronous)"""
        async def _batch_generate():
            tasks = [self.generate_content(request) for request in requests]
            return await asyncio.gather(*tasks, return_exceptions=True)
        
        return asyncio.run(_batch_generate())
    
    def test_connection(self) -> bool:
        """Test OpenAI API connection"""
        try:
            test_request = GenerationRequest(
                prompt="Say 'Hello' in Spanish",
                content_type="test",
                difficulty_level="easy",
                user_level="beginner",
                max_tokens=10
            )
            
            response = asyncio.run(self.generate_content(test_request))
            return response.content is not None
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False