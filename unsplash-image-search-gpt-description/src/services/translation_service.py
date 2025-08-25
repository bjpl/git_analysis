"""
Translation service with context-aware translation and intelligent caching.
Extracts and refactors translation logic from main application.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
import json
import hashlib
from pathlib import Path

from .base_service import BaseService, ServiceError
from .openai_service import OpenAIService


@dataclass
class TranslationRequest:
    """Request for translation."""
    text: str
    source_lang: str = "Spanish"
    target_lang: str = "English"
    context: Optional[str] = None
    category: Optional[str] = None  # e.g., "noun", "verb", "phrase"


@dataclass
class TranslationResult:
    """Result of translation."""
    original: str
    translated: str
    source_lang: str
    target_lang: str
    context: Optional[str]
    category: Optional[str]
    confidence: float  # 0-1 confidence score
    timestamp: datetime = field(default_factory=datetime.now)
    from_cache: bool = False


@dataclass
class BatchTranslationResult:
    """Result of batch translation."""
    results: List[TranslationResult]
    total_count: int
    cached_count: int
    translated_count: int
    processing_time: float


class TranslationCache:
    """Persistent cache for translations."""
    
    def __init__(self, cache_file: Optional[Path] = None):
        self.cache_file = cache_file or Path("data/translation_cache.json")
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._dirty = False
        self.load_cache()
    
    def _get_cache_key(self, request: TranslationRequest) -> str:
        """Generate cache key for translation request."""
        key_data = f"{request.text}|{request.source_lang}|{request.target_lang}|{request.context or ''}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    def load_cache(self) -> None:
        """Load cache from file."""
        if not self.cache_file.exists():
            return
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                self._cache = json.load(f)
            logging.info(f"Loaded {len(self._cache)} cached translations")
        except Exception as e:
            logging.warning(f"Failed to load translation cache: {e}")
            self._cache = {}
    
    def save_cache(self) -> None:
        """Save cache to file."""
        if not self._dirty:
            return
        
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
            self._dirty = False
            logging.debug("Translation cache saved")
        except Exception as e:
            logging.error(f"Failed to save translation cache: {e}")
    
    def get(self, request: TranslationRequest) -> Optional[TranslationResult]:
        """Get cached translation."""
        cache_key = self._get_cache_key(request)
        
        if cache_key not in self._cache:
            return None
        
        cached = self._cache[cache_key]
        
        # Check if cache entry is still valid (30 days)
        cache_time = datetime.fromisoformat(cached['timestamp'])
        if datetime.now() - cache_time > timedelta(days=30):
            del self._cache[cache_key]
            self._dirty = True
            return None
        
        return TranslationResult(
            original=cached['original'],
            translated=cached['translated'],
            source_lang=cached['source_lang'],
            target_lang=cached['target_lang'],
            context=cached.get('context'),
            category=cached.get('category'),
            confidence=cached.get('confidence', 0.9),
            timestamp=cache_time,
            from_cache=True
        )
    
    def put(self, request: TranslationRequest, result: TranslationResult) -> None:
        """Cache translation result."""
        cache_key = self._get_cache_key(request)
        
        self._cache[cache_key] = {
            'original': result.original,
            'translated': result.translated,
            'source_lang': result.source_lang,
            'target_lang': result.target_lang,
            'context': result.context,
            'category': result.category,
            'confidence': result.confidence,
            'timestamp': result.timestamp.isoformat(),
        }
        self._dirty = True
    
    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()
        self._dirty = True
        logging.info("Translation cache cleared")
    
    def cleanup_old_entries(self, days: int = 30) -> int:
        """Remove old cache entries."""
        cutoff = datetime.now() - timedelta(days=days)
        old_keys = []
        
        for key, cached in self._cache.items():
            cache_time = datetime.fromisoformat(cached['timestamp'])
            if cache_time < cutoff:
                old_keys.append(key)
        
        for key in old_keys:
            del self._cache[key]
        
        if old_keys:
            self._dirty = True
            logging.info(f"Cleaned up {len(old_keys)} old cache entries")
        
        return len(old_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self._cache:
            return {'size': 0, 'oldest': None, 'newest': None}
        
        timestamps = [
            datetime.fromisoformat(entry['timestamp'])
            for entry in self._cache.values()
        ]
        
        return {
            'size': len(self._cache),
            'oldest': min(timestamps).isoformat(),
            'newest': max(timestamps).isoformat(),
        }


class TranslationService(BaseService):
    """
    Advanced translation service with context awareness and caching.
    
    Features:
    - Context-aware translations for better accuracy
    - Intelligent caching to reduce API calls
    - Batch translation support
    - Category-specific translations (nouns, verbs, etc.)
    - Translation confidence scoring
    - Persistent cache storage
    """
    
    def __init__(
        self,
        openai_client: OpenAIService,
        cache_file: Optional[Path] = None,
        default_model: str = "gpt-4-turbo",
        enable_caching: bool = True,
    ):
        super().__init__(
            name="translation",
            enable_caching=enable_caching,
        )
        
        self.openai_client = openai_client
        self.default_model = default_model
        self.cache = TranslationCache(cache_file)
        
        # Common words that shouldn't be translated
        self.skip_words = {
            'spanish': {'el', 'la', 'los', 'las', 'de', 'que', 'y', 'a', 'en', 'es', 'son', 'un', 'una'},
            'english': {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'is', 'are'},
        }
        
        # Translation quality patterns
        self.quality_indicators = {
            'high': [
                'specific_context', 'technical_term', 'idiomatic_expression',
                'cultural_reference', 'domain_specific'
            ],
            'medium': [
                'common_word', 'basic_grammar', 'standard_usage'
            ],
            'low': [
                'ambiguous', 'multiple_meanings', 'context_dependent'
            ]
        }
        
        self.logger.info("Translation service initialized")
    
    def _should_skip_translation(self, text: str, source_lang: str) -> bool:
        """Check if text should be skipped (too common/simple)."""
        text_lower = text.lower().strip()
        skip_set = self.skip_words.get(source_lang.lower(), set())
        return text_lower in skip_set or len(text_lower) < 2
    
    def _estimate_confidence(
        self,
        request: TranslationRequest,
        translated: str
    ) -> float:
        """Estimate translation confidence based on various factors."""
        confidence = 0.7  # Base confidence
        
        # Context increases confidence
        if request.context:
            confidence += 0.15
        
        # Category information helps
        if request.category:
            confidence += 0.1
        
        # Length and complexity
        if len(request.text) > 10:
            confidence += 0.05
        
        # Check for obvious problems
        if translated.lower() == request.text.lower():
            confidence = 0.3  # Probably failed to translate
        elif len(translated) < 2:
            confidence = 0.2  # Too short
        elif translated.count('?') > 2:
            confidence = 0.4  # Uncertain translation
        
        return min(1.0, confidence)
    
    async def translate(self, request: TranslationRequest) -> TranslationResult:
        """
        Translate a single text with context awareness.
        
        Args:
            request: TranslationRequest object
            
        Returns:
            TranslationResult with translation and metadata
        """
        # Check cache first
        cached_result = self.cache.get(request)
        if cached_result:
            self.logger.debug(f"Using cached translation for '{request.text}'")
            return cached_result
        
        # Skip very common words
        if self._should_skip_translation(request.text, request.source_lang):
            self.logger.debug(f"Skipping translation for common word: '{request.text}'")
            return TranslationResult(
                original=request.text,
                translated=request.text,
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                context=request.context,
                category=request.category,
                confidence=0.1,
                from_cache=False
            )
        
        try:
            # Build context-aware prompt
            prompt = self._build_translation_prompt(request)
            
            # Create OpenAI request
            text_request = TextRequest(
                prompt=prompt,
                model=self.default_model,
                max_tokens=100,
                temperature=0.1,  # Low temperature for consistent translations
            )
            
            # Get translation
            result = await self.openai_client.process_text(text_request)
            translated = result.content.strip()
            
            # Clean up translation (remove quotes, extra text)
            translated = self._clean_translation(translated)
            
            # Estimate confidence
            confidence = self._estimate_confidence(request, translated)
            
            # Create result
            translation_result = TranslationResult(
                original=request.text,
                translated=translated,
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                context=request.context,
                category=request.category,
                confidence=confidence,
                from_cache=False
            )
            
            # Cache the result
            self.cache.put(request, translation_result)
            
            self.logger.info(f"Translated '{request.text}' -> '{translated}' (confidence: {confidence:.2f})")
            return translation_result
            
        except Exception as e:
            self.logger.error(f"Translation failed for '{request.text}': {e}")
            raise ServiceError(f"Translation failed: {e}")
    
    def _build_translation_prompt(self, request: TranslationRequest) -> str:
        """Build context-aware translation prompt."""
        prompt = f"Translate the {request.source_lang} text '{request.text}' into {request.target_lang}."
        
        # Add context
        if request.context:
            prompt += f" This text appears in the following context: '{request.context[:200]}'"
        
        # Add category-specific instructions
        if request.category:
            category_instructions = {
                'noun': 'If this is a noun, include the appropriate article if needed.',
                'verb': 'If this is a verb, provide the most common form or infinitive.',
                'adjective': 'If this is an adjective, provide the basic form.',
                'phrase': 'This is a phrase or expression, translate it naturally.',
                'idiom': 'This is an idiomatic expression, find the equivalent meaning.',
            }
            
            instruction = category_instructions.get(request.category.lower())
            if instruction:
                prompt += f" {instruction}"
        
        # Add quality instructions
        prompt += " Provide only the translation without quotes, explanations, or additional text."
        
        return prompt
    
    def _clean_translation(self, translation: str) -> str:
        """Clean and normalize translation result."""
        # Remove common prefixes/suffixes that AI might add
        prefixes = ['"', "'", "Translation:", "Answer:", "Result:"]
        suffixes = ['"', "'", ".", "(", "["]
        
        cleaned = translation.strip()
        
        # Remove prefixes
        for prefix in prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        
        # Remove suffixes (but keep meaningful punctuation)
        for suffix in suffixes:
            if cleaned.endswith(suffix) and suffix not in ['.']:
                cleaned = cleaned[:-len(suffix)].strip()
        
        # Handle quotes properly
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1]
        
        return cleaned
    
    async def batch_translate(
        self,
        requests: List[TranslationRequest],
        batch_size: int = 10,
        max_concurrent: int = 3
    ) -> BatchTranslationResult:
        """
        Translate multiple texts in efficient batches.
        
        Args:
            requests: List of TranslationRequest objects
            batch_size: Size of each batch for processing
            max_concurrent: Maximum concurrent batch processes
            
        Returns:
            BatchTranslationResult with all translations and statistics
        """
        start_time = asyncio.get_event_loop().time()
        
        # Separate cached and non-cached requests
        cached_results = []
        pending_requests = []
        
        for request in requests:
            cached = self.cache.get(request)
            if cached:
                cached_results.append(cached)
            else:
                pending_requests.append(request)
        
        self.logger.info(f"Batch translation: {len(cached_results)} cached, {len(pending_requests)} to translate")
        
        # Process non-cached requests
        translated_results = []
        if pending_requests:
            # Create semaphore to limit concurrent operations
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def process_batch(batch):
                async with semaphore:
                    return await asyncio.gather(
                        *[self.translate(req) for req in batch],
                        return_exceptions=True
                    )
            
            # Split into batches
            batches = [
                pending_requests[i:i + batch_size]
                for i in range(0, len(pending_requests), batch_size)
            ]
            
            # Process all batches concurrently
            batch_results = await asyncio.gather(
                *[process_batch(batch) for batch in batches],
                return_exceptions=True
            )
            
            # Flatten results and handle exceptions
            for batch_result in batch_results:
                if isinstance(batch_result, Exception):
                    self.logger.error(f"Batch processing failed: {batch_result}")
                    continue
                
                for result in batch_result:
                    if isinstance(result, Exception):
                        self.logger.error(f"Translation failed: {result}")
                        continue
                    
                    translated_results.append(result)
        
        # Combine all results
        all_results = cached_results + translated_results
        
        # Sort results to match original order
        result_map = {
            (r.original, r.source_lang, r.target_lang, r.context or ""): r
            for r in all_results
        }
        
        ordered_results = []
        for request in requests:
            key = (request.text, request.source_lang, request.target_lang, request.context or "")
            if key in result_map:
                ordered_results.append(result_map[key])
            else:
                # Create failure result
                ordered_results.append(TranslationResult(
                    original=request.text,
                    translated=request.text,  # Fallback to original
                    source_lang=request.source_lang,
                    target_lang=request.target_lang,
                    context=request.context,
                    category=request.category,
                    confidence=0.0,
                    from_cache=False
                ))
        
        processing_time = asyncio.get_event_loop().time() - start_time
        
        # Save cache
        self.cache.save_cache()
        
        result = BatchTranslationResult(
            results=ordered_results,
            total_count=len(requests),
            cached_count=len(cached_results),
            translated_count=len(translated_results),
            processing_time=processing_time
        )
        
        self.logger.info(
            f"Batch translation completed: {result.total_count} total, "
            f"{result.cached_count} cached, {result.translated_count} translated "
            f"in {processing_time:.2f}s"
        )
        
        return result
    
    async def translate_vocabulary(
        self,
        vocabulary_dict: Dict[str, List[str]],
        context: Optional[str] = None,
        source_lang: str = "Spanish",
        target_lang: str = "English"
    ) -> Dict[str, List[TranslationResult]]:
        """
        Translate vocabulary organized by categories.
        
        Args:
            vocabulary_dict: Dictionary of {category: [words/phrases]}
            context: Context for translations
            source_lang: Source language
            target_lang: Target language
            
        Returns:
            Dictionary of {category: [TranslationResult]}
        """
        # Create translation requests
        all_requests = []
        category_mapping = {}
        
        for category, items in vocabulary_dict.items():
            for item in items:
                request = TranslationRequest(
                    text=item,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    context=context,
                    category=category.lower()
                )
                all_requests.append(request)
                category_mapping[item] = category
        
        # Perform batch translation
        batch_result = await self.batch_translate(all_requests)
        
        # Organize results by category
        categorized_results = {category: [] for category in vocabulary_dict.keys()}
        
        for result in batch_result.results:
            original_category = category_mapping.get(result.original)
            if original_category:
                categorized_results[original_category].append(result)
        
        return categorized_results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get translation cache statistics."""
        return self.cache.get_stats()
    
    def clear_cache(self) -> None:
        """Clear translation cache."""
        self.cache.clear()
        self.cache.save_cache()
    
    def cleanup_old_cache_entries(self, days: int = 30) -> int:
        """Clean up old cache entries."""
        cleaned = self.cache.cleanup_old_entries(days)
        if cleaned > 0:
            self.cache.save_cache()
        return cleaned
    
    async def close(self) -> None:
        """Close service and save cache."""
        self.cache.save_cache()
        await super().close()
    
    async def health_check(self) -> bool:
        """Check if translation service is healthy."""
        try:
            # Try a simple translation
            request = TranslationRequest(
                text="test",
                source_lang="English",
                target_lang="Spanish"
            )
            await self.translate(request)
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False