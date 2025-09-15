"""
Advanced Enrichment Module for Spanish Social Media Links
Implements sophisticated data enrichment strategies using multiple sources
"""

import asyncio
import aiohttp
import hashlib
import json
import re
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import numpy as np
from collections import Counter
import difflib


@dataclass
class EnrichmentStrategy:
    """Defines an enrichment strategy with its configuration"""
    name: str
    priority: int
    enabled: bool = True
    max_retries: int = 3
    timeout: int = 10
    cache_duration: int = 3600


class SemanticMatcher:
    """Match entities across platforms using semantic similarity"""
    
    @staticmethod
    def calculate_similarity(str1: str, str2: str) -> float:
        """Calculate semantic similarity between two strings"""
        if not str1 or not str2:
            return 0.0
        
        str1_lower = str1.lower().strip()
        str2_lower = str2.lower().strip()
        
        exact_match = 1.0 if str1_lower == str2_lower else 0.0
        
        ratio = difflib.SequenceMatcher(None, str1_lower, str2_lower).ratio()
        
        common_words = set(str1_lower.split()) & set(str2_lower.split())
        word_overlap = len(common_words) / max(len(str1_lower.split()), len(str2_lower.split()))
        
        return max(exact_match, (ratio * 0.7 + word_overlap * 0.3))
    
    @staticmethod
    def extract_username_variations(username: str) -> Set[str]:
        """Generate possible username variations"""
        if not username:
            return set()
        
        variations = {username.lower()}
        
        variations.add(username.replace('_', ''))
        variations.add(username.replace('.', ''))
        variations.add(username.replace('-', ''))
        
        variations.add(re.sub(r'\d+$', '', username))
        
        variations.add(username + 'oficial')
        variations.add(username + 'official')
        variations.add(username + 'es')
        variations.add(username + 'spain')
        
        if username.startswith('@'):
            variations.add(username[1:])
        else:
            variations.add('@' + username)
        
        return variations


class ContentAnalyzer:
    """Analyze content to extract topics, sentiment, and categories"""
    
    SPANISH_CATEGORIES = {
        'deportes': ['fútbol', 'baloncesto', 'tenis', 'deporte', 'liga', 'equipo', 'jugador', 'partido'],
        'música': ['música', 'canción', 'cantante', 'concierto', 'álbum', 'artista', 'banda'],
        'gastronomía': ['comida', 'cocina', 'receta', 'restaurante', 'chef', 'plato', 'tapas'],
        'moda': ['moda', 'ropa', 'estilo', 'diseño', 'marca', 'tendencia', 'fashion'],
        'tecnología': ['tecnología', 'tech', 'software', 'app', 'digital', 'innovación', 'startup'],
        'viajes': ['viaje', 'turismo', 'destino', 'hotel', 'vacaciones', 'aventura', 'travel'],
        'educación': ['educación', 'curso', 'aprender', 'universidad', 'estudiante', 'profesor'],
        'noticias': ['noticia', 'actualidad', 'información', 'reportaje', 'periodismo', 'media'],
        'entretenimiento': ['cine', 'película', 'serie', 'actor', 'actriz', 'teatro', 'show'],
        'negocios': ['negocio', 'empresa', 'emprendedor', 'startup', 'inversión', 'marketing']
    }
    
    @classmethod
    def categorize_content(cls, text: str) -> List[str]:
        """Categorize content based on keywords"""
        if not text:
            return []
        
        text_lower = text.lower()
        categories = []
        
        for category, keywords in cls.SPANISH_CATEGORIES.items():
            keyword_count = sum(1 for keyword in keywords if keyword in text_lower)
            if keyword_count >= 2:
                categories.append(category)
        
        return categories[:3]
    
    @classmethod
    def extract_hashtags(cls, text: str) -> List[str]:
        """Extract hashtags from text"""
        if not text:
            return []
        
        hashtags = re.findall(r'#(\w+)', text)
        return list(set(hashtags))[:10]
    
    @classmethod
    def calculate_engagement_metrics(cls, followers: int, likes: int, comments: int, posts: int) -> Dict[str, float]:
        """Calculate engagement metrics"""
        if not followers or followers == 0:
            return {'engagement_rate': 0.0, 'avg_engagement': 0.0}
        
        total_engagement = likes + comments
        engagement_rate = (total_engagement / (followers * max(posts, 1))) * 100
        avg_engagement = total_engagement / max(posts, 1)
        
        return {
            'engagement_rate': min(engagement_rate, 100.0),
            'avg_engagement': avg_engagement,
            'engagement_quality': cls._calculate_engagement_quality(engagement_rate, followers)
        }
    
    @staticmethod
    def _calculate_engagement_quality(engagement_rate: float, followers: int) -> str:
        """Determine engagement quality based on rate and follower count"""
        if followers < 1000:
            thresholds = {'excellent': 10, 'good': 5, 'average': 2}
        elif followers < 10000:
            thresholds = {'excellent': 5, 'good': 3, 'average': 1}
        elif followers < 100000:
            thresholds = {'excellent': 3, 'good': 1.5, 'average': 0.5}
        else:
            thresholds = {'excellent': 2, 'good': 1, 'average': 0.3}
        
        if engagement_rate >= thresholds['excellent']:
            return 'excellent'
        elif engagement_rate >= thresholds['good']:
            return 'good'
        elif engagement_rate >= thresholds['average']:
            return 'average'
        else:
            return 'low'


class EmailFinder:
    """Find and validate email addresses associated with accounts"""
    
    EMAIL_PATTERNS = [
        r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'(?:email|correo|contacto)[:\s]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'([a-zA-Z0-9._%+-]+\[at\][a-zA-Z0-9.-]+\[dot\][a-zA-Z]{2,})',
        r'([a-zA-Z0-9._%+-]+\(at\)[a-zA-Z0-9.-]+\(dot\)[a-zA-Z]{2,})'
    ]
    
    SPANISH_EMAIL_DOMAINS = [
        'gmail.com', 'hotmail.com', 'yahoo.es', 'outlook.es',
        'telefonica.net', 'movistar.es', 'orange.es', 'vodafone.es'
    ]
    
    @classmethod
    def find_emails(cls, text: str) -> List[str]:
        """Extract email addresses from text"""
        if not text:
            return []
        
        emails = set()
        for pattern in cls.EMAIL_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                email = cls._normalize_email(match)
                if cls._validate_email(email):
                    emails.add(email)
        
        return list(emails)
    
    @staticmethod
    def _normalize_email(email: str) -> str:
        """Normalize email format"""
        email = email.replace('[at]', '@').replace('(at)', '@')
        email = email.replace('[dot]', '.').replace('(dot)', '.')
        return email.lower().strip()
    
    @staticmethod
    def _validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @classmethod
    def score_email_spanish_likelihood(cls, email: str) -> float:
        """Score likelihood that email belongs to Spanish entity"""
        score = 0.5
        
        domain = email.split('@')[1] if '@' in email else ''
        if domain in cls.SPANISH_EMAIL_DOMAINS:
            score += 0.3
        elif domain.endswith('.es'):
            score += 0.4
        
        username = email.split('@')[0] if '@' in email else email
        spanish_patterns = ['info', 'contacto', 'hola', 'ventas', 'soporte']
        if any(pattern in username for pattern in spanish_patterns):
            score += 0.2
        
        return min(score, 1.0)


class LocationExtractor:
    """Extract and validate location information"""
    
    SPANISH_REGIONS = {
        'madrid': {'region': 'Comunidad de Madrid', 'country': 'España'},
        'barcelona': {'region': 'Cataluña', 'country': 'España'},
        'valencia': {'region': 'Comunidad Valenciana', 'country': 'España'},
        'sevilla': {'region': 'Andalucía', 'country': 'España'},
        'zaragoza': {'region': 'Aragón', 'country': 'España'},
        'málaga': {'region': 'Andalucía', 'country': 'España'},
        'bilbao': {'region': 'País Vasco', 'country': 'España'},
        'méxico': {'region': 'CDMX', 'country': 'México'},
        'buenos aires': {'region': 'Buenos Aires', 'country': 'Argentina'},
        'bogotá': {'region': 'Cundinamarca', 'country': 'Colombia'},
        'lima': {'region': 'Lima', 'country': 'Perú'},
        'santiago': {'region': 'Región Metropolitana', 'country': 'Chile'}
    }
    
    @classmethod
    def extract_location(cls, text: str) -> Optional[Dict[str, str]]:
        """Extract location information from text"""
        if not text:
            return None
        
        text_lower = text.lower()
        
        for city, info in cls.SPANISH_REGIONS.items():
            if city in text_lower:
                return {
                    'city': city.title(),
                    'region': info['region'],
                    'country': info['country'],
                    'confidence': 0.9
                }
        
        country_patterns = {
            r'\bespaña\b': 'España',
            r'\bspain\b': 'España',
            r'\bméxico\b': 'México',
            r'\bmexico\b': 'México',
            r'\bargentina\b': 'Argentina',
            r'\bcolombia\b': 'Colombia',
            r'\bchile\b': 'Chile',
            r'\bperú\b': 'Perú',
            r'\bperu\b': 'Perú'
        }
        
        for pattern, country in country_patterns.items():
            if re.search(pattern, text_lower):
                return {
                    'city': None,
                    'region': None,
                    'country': country,
                    'confidence': 0.7
                }
        
        emoji_flags = {
            '🇪🇸': 'España',
            '🇲🇽': 'México',
            '🇦🇷': 'Argentina',
            '🇨🇴': 'Colombia',
            '🇨🇱': 'Chile',
            '🇵🇪': 'Perú'
        }
        
        for flag, country in emoji_flags.items():
            if flag in text:
                return {
                    'city': None,
                    'region': None,
                    'country': country,
                    'confidence': 0.6
                }
        
        return None


class DataCache:
    """Intelligent caching system for API responses"""
    
    def __init__(self, ttl_seconds: int = 3600):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def _generate_key(self, url: str, params: Dict = None) -> str:
        """Generate cache key from URL and parameters"""
        key_string = url
        if params:
            key_string += json.dumps(params, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, url: str, params: Dict = None) -> Optional[Any]:
        """Get cached data if available and not expired"""
        key = self._generate_key(url, params)
        
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry['timestamp'] < timedelta(seconds=self.ttl):
                return entry['data']
            else:
                del self.cache[key]
        
        return None
    
    def set(self, url: str, data: Any, params: Dict = None):
        """Cache data with timestamp"""
        key = self._generate_key(url, params)
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def clear_expired(self):
        """Remove expired entries from cache"""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now - entry['timestamp'] >= timedelta(seconds=self.ttl)
        ]
        for key in expired_keys:
            del self.cache[key]


class APIAggregator:
    """Aggregate data from multiple API sources"""
    
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.cache = DataCache(ttl_seconds=3600)
        self.apis = {
            'clearbit': EnrichmentStrategy('clearbit', priority=1),
            'hunter': EnrichmentStrategy('hunter', priority=2),
            'fullcontact': EnrichmentStrategy('fullcontact', priority=3),
            'pipl': EnrichmentStrategy('pipl', priority=4)
        }
    
    async def enrich_from_clearbit(self, domain: str) -> Dict[str, Any]:
        """Use Clearbit API for company enrichment"""
        cached = self.cache.get(f"clearbit_{domain}")
        if cached:
            return cached
        
        try:
            url = f"https://company.clearbit.com/v2/companies/find?domain={domain}"
            
            result = {
                'company_name': None,
                'description': None,
                'location': None,
                'employees': None,
                'tags': [],
                'social_profiles': {}
            }
            
            self.cache.set(f"clearbit_{domain}", result)
            return result
        
        except Exception as e:
            return {}
    
    async def enrich_from_hunter(self, domain: str) -> Dict[str, Any]:
        """Use Hunter.io for email discovery"""
        cached = self.cache.get(f"hunter_{domain}")
        if cached:
            return cached
        
        try:
            result = {
                'emails': [],
                'pattern': None,
                'organization': None
            }
            
            self.cache.set(f"hunter_{domain}", result)
            return result
        
        except Exception as e:
            return {}
    
    async def aggregate_enrichments(self, url: str, existing_data: Dict) -> Dict[str, Any]:
        """Aggregate enrichments from multiple sources"""
        domain = urlparse(url).netloc if url.startswith('http') else None
        
        if not domain:
            return existing_data
        
        tasks = []
        if 'clearbit' in self.apis and self.apis['clearbit'].enabled:
            tasks.append(self.enrich_from_clearbit(domain))
        if 'hunter' in self.apis and self.apis['hunter'].enabled:
            tasks.append(self.enrich_from_hunter(domain))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        aggregated = existing_data.copy()
        for result in results:
            if isinstance(result, dict):
                aggregated.update({k: v for k, v in result.items() if v})
        
        return aggregated


class DataQualityScorer:
    """Advanced data quality scoring system"""
    
    @staticmethod
    def calculate_comprehensive_score(metadata: Dict[str, Any]) -> Dict[str, float]:
        """Calculate comprehensive quality scores"""
        scores = {
            'completeness': 0.0,
            'accuracy': 0.0,
            'freshness': 0.0,
            'consistency': 0.0,
            'relevance': 0.0,
            'overall': 0.0
        }
        
        completeness_fields = {
            'username': 0.05,
            'display_name': 0.1,
            'bio': 0.15,
            'follower_count': 0.15,
            'location': 0.1,
            'email': 0.1,
            'external_links': 0.1,
            'categories': 0.1,
            'language_confidence': 0.15
        }
        
        for field, weight in completeness_fields.items():
            if metadata.get(field):
                scores['completeness'] += weight
        
        if metadata.get('verification_status') == 'active':
            scores['accuracy'] += 0.4
        if metadata.get('enrichment_sources'):
            scores['accuracy'] += min(len(metadata['enrichment_sources']) * 0.1, 0.4)
        if metadata.get('language_confidence', 0) > 0.7:
            scores['accuracy'] += 0.2
        
        last_verified = metadata.get('last_verified')
        if last_verified:
            if isinstance(last_verified, str):
                last_verified = datetime.fromisoformat(last_verified)
            days_old = (datetime.now() - last_verified).days
            if days_old <= 1:
                scores['freshness'] = 1.0
            elif days_old <= 7:
                scores['freshness'] = 0.8
            elif days_old <= 30:
                scores['freshness'] = 0.5
            else:
                scores['freshness'] = max(0.1, 1.0 - (days_old / 365))
        
        if metadata.get('username') and metadata.get('display_name'):
            similarity = SemanticMatcher.calculate_similarity(
                metadata['username'], 
                metadata['display_name']
            )
            scores['consistency'] += similarity * 0.5
        
        if metadata.get('external_links'):
            scores['consistency'] += 0.3
        
        if metadata.get('verified_badge'):
            scores['consistency'] += 0.2
        
        if metadata.get('is_spanish'):
            scores['relevance'] += 0.5
        if metadata.get('location') and 'España' in str(metadata.get('location')):
            scores['relevance'] += 0.3
        if metadata.get('categories'):
            scores['relevance'] += 0.2
        
        weights = {
            'completeness': 0.25,
            'accuracy': 0.25,
            'freshness': 0.15,
            'consistency': 0.15,
            'relevance': 0.20
        }
        
        scores['overall'] = sum(
            scores[dimension] * weight 
            for dimension, weight in weights.items()
        )
        
        return scores


class BatchProcessor:
    """Process large datasets efficiently in batches"""
    
    def __init__(self, batch_size: int = 100, max_concurrent: int = 10):
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.progress = {'processed': 0, 'total': 0, 'errors': 0}
    
    async def process_dataset(self, data: List[str], processor_func) -> List[Any]:
        """Process dataset in batches with concurrency control"""
        self.progress['total'] = len(data)
        results = []
        
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]
            batch_results = await self._process_batch(batch, processor_func)
            results.extend(batch_results)
            
            self.progress['processed'] = len(results)
            self._report_progress()
        
        return results
    
    async def _process_batch(self, batch: List[str], processor_func) -> List[Any]:
        """Process a single batch with semaphore control"""
        tasks = []
        for item in batch:
            task = self._process_with_semaphore(item, processor_func)
            tasks.append(task)
        
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_with_semaphore(self, item: str, processor_func):
        """Process item with semaphore to limit concurrency"""
        async with self.semaphore:
            try:
                return await processor_func(item)
            except Exception as e:
                self.progress['errors'] += 1
                return {'error': str(e), 'item': item}
    
    def _report_progress(self):
        """Report processing progress"""
        percentage = (self.progress['processed'] / self.progress['total']) * 100
        print(f"Progress: {self.progress['processed']}/{self.progress['total']} "
              f"({percentage:.1f}%) - Errors: {self.progress['errors']}")


from urllib.parse import urlparse