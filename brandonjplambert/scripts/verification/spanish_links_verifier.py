"""
Spanish Social Media Links Verifier & Enricher
A comprehensive system for validating and enriching Spanish account links across platforms
"""

import asyncio
import aiohttp
import re
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
from enum import Enum
import time
from collections import defaultdict
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Platform(Enum):
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    WEBSITE = "website"
    LINKEDIN = "linkedin"
    UNKNOWN = "unknown"


class VerificationStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PRIVATE = "private"
    SUSPENDED = "suspended"
    NOT_FOUND = "not_found"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    PENDING = "pending"


@dataclass
class LinkMetadata:
    """Rich metadata for each verified link"""
    url: str
    platform: Platform
    username: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    post_count: Optional[int] = None
    verification_status: VerificationStatus = VerificationStatus.PENDING
    is_spanish: Optional[bool] = None
    language_confidence: float = 0.0
    last_post_date: Optional[datetime] = None
    engagement_rate: Optional[float] = None
    content_categories: List[str] = field(default_factory=list)
    location: Optional[str] = None
    external_links: List[str] = field(default_factory=list)
    email: Optional[str] = None
    phone: Optional[str] = None
    verified_badge: bool = False
    created_date: Optional[datetime] = None
    last_verified: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    quality_score: float = 0.0
    enrichment_sources: List[str] = field(default_factory=list)
    
    def calculate_quality_score(self) -> float:
        """Calculate data quality score based on completeness and freshness"""
        score = 0.0
        weights = {
            'has_username': 0.1,
            'has_display_name': 0.1,
            'has_bio': 0.15,
            'has_followers': 0.15,
            'is_active': 0.2,
            'is_spanish_confirmed': 0.15,
            'has_recent_activity': 0.1,
            'has_location': 0.05
        }
        
        if self.username: score += weights['has_username']
        if self.display_name: score += weights['has_display_name']
        if self.bio: score += weights['has_bio']
        if self.follower_count is not None: score += weights['has_followers']
        if self.verification_status == VerificationStatus.ACTIVE: score += weights['is_active']
        if self.is_spanish and self.language_confidence > 0.7: score += weights['is_spanish_confirmed']
        if self.last_post_date and (datetime.now() - self.last_post_date).days < 30:
            score += weights['has_recent_activity']
        if self.location: score += weights['has_location']
        
        self.quality_score = score
        return score


class PlatformDetector:
    """Intelligent platform detection from URLs"""
    
    PLATFORM_PATTERNS = {
        Platform.INSTAGRAM: [
            r'(?:https?://)?(?:www\.)?instagram\.com/([^/?]+)',
            r'(?:https?://)?(?:www\.)?instagr\.am/([^/?]+)'
        ],
        Platform.YOUTUBE: [
            r'(?:https?://)?(?:www\.)?youtube\.com/(?:c/|channel/|user/|@)([^/?]+)',
            r'(?:https?://)?(?:www\.)?youtu\.be/([^/?]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&]+)'
        ],
        Platform.TIKTOK: [
            r'(?:https?://)?(?:www\.)?tiktok\.com/@([^/?]+)',
            r'(?:https?://)?(?:vm\.)?tiktok\.com/([^/?]+)'
        ],
        Platform.TWITTER: [
            r'(?:https?://)?(?:www\.)?twitter\.com/([^/?]+)',
            r'(?:https?://)?(?:www\.)?x\.com/([^/?]+)'
        ],
        Platform.FACEBOOK: [
            r'(?:https?://)?(?:www\.)?facebook\.com/([^/?]+)',
            r'(?:https?://)?(?:www\.)?fb\.com/([^/?]+)'
        ],
        Platform.LINKEDIN: [
            r'(?:https?://)?(?:www\.)?linkedin\.com/(?:in|company)/([^/?]+)'
        ]
    }
    
    @classmethod
    def detect(cls, url: str) -> Tuple[Platform, Optional[str]]:
        """Detect platform and extract username/ID"""
        for platform, patterns in cls.PLATFORM_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, url, re.IGNORECASE)
                if match:
                    return platform, match.group(1)
        
        if re.match(r'^https?://', url):
            return Platform.WEBSITE, None
        
        return Platform.UNKNOWN, None


class SpanishLanguageDetector:
    """Detect Spanish language content with confidence scoring"""
    
    SPANISH_INDICATORS = {
        'strong': [
            r'\b(?:el|la|los|las|un|una|unos|unas)\b',
            r'\b(?:de|del|al|para|por|con|sin|sobre)\b',
            r'\b(?:que|qué|como|cómo|cuando|cuándo|donde|dónde)\b',
            r'\b(?:está|están|estoy|estamos|estáis)\b',
            r'\b(?:soy|eres|es|somos|sois|son)\b'
        ],
        'moderate': [
            r'\b(?:muy|mucho|poco|todo|nada|algo|siempre|nunca)\b',
            r'\b(?:aquí|ahí|allí|ahora|hoy|ayer|mañana)\b',
            r'[áéíóúñü]',
            r'(?:ción|sión|dad|tad|mente|miento)$'
        ],
        'location': [
            r'\b(?:España|Madrid|Barcelona|Valencia|Sevilla|México|Argentina|Colombia|Chile|Perú)\b',
            r'\b(?:CDMX|Buenos Aires|Bogotá|Lima|Santiago)\b'
        ]
    }
    
    @classmethod
    def analyze(cls, text: str, location: str = None) -> Tuple[bool, float]:
        """Analyze text for Spanish language with confidence score"""
        if not text:
            return False, 0.0
        
        text_lower = text.lower()
        confidence = 0.0
        
        for pattern in cls.SPANISH_INDICATORS['strong']:
            matches = len(re.findall(pattern, text_lower))
            confidence += matches * 0.1
        
        for pattern in cls.SPANISH_INDICATORS['moderate']:
            matches = len(re.findall(pattern, text_lower))
            confidence += matches * 0.05
        
        if location:
            for pattern in cls.SPANISH_INDICATORS['location']:
                if re.search(pattern, location, re.IGNORECASE):
                    confidence += 0.3
                    break
        
        confidence = min(confidence, 1.0)
        is_spanish = confidence > 0.3
        
        return is_spanish, confidence


class RateLimiter:
    """Intelligent rate limiting with exponential backoff"""
    
    def __init__(self):
        self.limits = {
            Platform.INSTAGRAM: {'calls': 200, 'window': 3600},
            Platform.YOUTUBE: {'calls': 10000, 'window': 86400},
            Platform.TWITTER: {'calls': 300, 'window': 900},
            Platform.TIKTOK: {'calls': 100, 'window': 3600},
            Platform.FACEBOOK: {'calls': 200, 'window': 3600},
            Platform.WEBSITE: {'calls': 10, 'window': 1}
        }
        self.calls = defaultdict(list)
        self.backoff = defaultdict(lambda: 1)
    
    async def check_rate_limit(self, platform: Platform) -> bool:
        """Check if we can make a request to this platform"""
        now = time.time()
        limit = self.limits.get(platform, {'calls': 10, 'window': 1})
        
        self.calls[platform] = [
            t for t in self.calls[platform] 
            if now - t < limit['window']
        ]
        
        if len(self.calls[platform]) >= limit['calls']:
            wait_time = self.backoff[platform]
            logger.warning(f"Rate limit reached for {platform.value}. Waiting {wait_time}s")
            await asyncio.sleep(wait_time)
            self.backoff[platform] = min(self.backoff[platform] * 2, 300)
            return False
        
        self.calls[platform].append(now)
        self.backoff[platform] = 1
        return True


class InstagramVerifier:
    """Instagram-specific verification and enrichment"""
    
    def __init__(self, session: aiohttp.ClientSession, rate_limiter: RateLimiter):
        self.session = session
        self.rate_limiter = rate_limiter
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def verify(self, username: str, metadata: LinkMetadata) -> LinkMetadata:
        """Verify Instagram account and enrich metadata"""
        if not await self.rate_limiter.check_rate_limit(Platform.INSTAGRAM):
            metadata.verification_status = VerificationStatus.RATE_LIMITED
            return metadata
        
        try:
            url = f"https://www.instagram.com/{username}/"
            async with self.session.get(url, headers=self.headers, timeout=10) as response:
                if response.status == 404:
                    metadata.verification_status = VerificationStatus.NOT_FOUND
                elif response.status == 200:
                    text = await response.text()
                    metadata = await self._parse_instagram_data(text, metadata)
                    metadata.verification_status = VerificationStatus.ACTIVE
                else:
                    metadata.verification_status = VerificationStatus.ERROR
                    metadata.error_message = f"HTTP {response.status}"
        
        except asyncio.TimeoutError:
            metadata.verification_status = VerificationStatus.ERROR
            metadata.error_message = "Timeout"
        except Exception as e:
            metadata.verification_status = VerificationStatus.ERROR
            metadata.error_message = str(e)
        
        metadata.enrichment_sources.append("instagram_web")
        return metadata
    
    async def _parse_instagram_data(self, html: str, metadata: LinkMetadata) -> LinkMetadata:
        """Extract data from Instagram HTML"""
        patterns = {
            'followers': r'"edge_followed_by":\{"count":(\d+)\}',
            'following': r'"edge_follow":\{"count":(\d+)\}',
            'posts': r'"edge_owner_to_timeline_media":\{"count":(\d+)',
            'bio': r'"biography":"([^"]*)"',
            'display_name': r'"full_name":"([^"]*)"',
            'is_verified': r'"is_verified":(true|false)',
            'external_url': r'"external_url":"([^"]*)"'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, html)
            if match:
                if key == 'followers':
                    metadata.follower_count = int(match.group(1))
                elif key == 'following':
                    metadata.following_count = int(match.group(1))
                elif key == 'posts':
                    metadata.post_count = int(match.group(1))
                elif key == 'bio':
                    bio = match.group(1).encode().decode('unicode-escape')
                    metadata.bio = bio
                    is_spanish, confidence = SpanishLanguageDetector.analyze(bio)
                    metadata.is_spanish = is_spanish
                    metadata.language_confidence = confidence
                elif key == 'display_name':
                    metadata.display_name = match.group(1).encode().decode('unicode-escape')
                elif key == 'is_verified':
                    metadata.verified_badge = match.group(1) == 'true'
                elif key == 'external_url':
                    metadata.external_links.append(match.group(1))
        
        return metadata


class YouTubeVerifier:
    """YouTube-specific verification and enrichment"""
    
    def __init__(self, session: aiohttp.ClientSession, rate_limiter: RateLimiter, api_key: Optional[str] = None):
        self.session = session
        self.rate_limiter = rate_limiter
        self.api_key = api_key
    
    async def verify(self, channel_id: str, metadata: LinkMetadata) -> LinkMetadata:
        """Verify YouTube channel and enrich metadata"""
        if not await self.rate_limiter.check_rate_limit(Platform.YOUTUBE):
            metadata.verification_status = VerificationStatus.RATE_LIMITED
            return metadata
        
        if self.api_key:
            return await self._verify_via_api(channel_id, metadata)
        else:
            return await self._verify_via_scraping(channel_id, metadata)
    
    async def _verify_via_api(self, channel_id: str, metadata: LinkMetadata) -> LinkMetadata:
        """Use YouTube Data API for verification"""
        try:
            url = "https://www.googleapis.com/youtube/v3/channels"
            params = {
                'part': 'snippet,statistics,brandingSettings',
                'id': channel_id,
                'key': self.api_key
            }
            
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['items']:
                        item = data['items'][0]
                        metadata.display_name = item['snippet']['title']
                        metadata.bio = item['snippet'].get('description', '')
                        metadata.follower_count = int(item['statistics'].get('subscriberCount', 0))
                        metadata.post_count = int(item['statistics'].get('videoCount', 0))
                        metadata.location = item['snippet'].get('country')
                        
                        is_spanish, confidence = SpanishLanguageDetector.analyze(
                            f"{metadata.display_name} {metadata.bio}",
                            metadata.location
                        )
                        metadata.is_spanish = is_spanish
                        metadata.language_confidence = confidence
                        metadata.verification_status = VerificationStatus.ACTIVE
                    else:
                        metadata.verification_status = VerificationStatus.NOT_FOUND
                else:
                    metadata.verification_status = VerificationStatus.ERROR
                    metadata.error_message = f"API Error: {response.status}"
        
        except Exception as e:
            metadata.verification_status = VerificationStatus.ERROR
            metadata.error_message = str(e)
        
        metadata.enrichment_sources.append("youtube_api")
        return metadata
    
    async def _verify_via_scraping(self, channel_id: str, metadata: LinkMetadata) -> LinkMetadata:
        """Fallback to web scraping for YouTube verification"""
        try:
            url = f"https://www.youtube.com/@{channel_id}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    
                    patterns = {
                        'subscribers': r'"subscriberCountText":\{"simpleText":"([^"]*)"',
                        'channel_name': r'"title":"([^"]*)"',
                        'description': r'"description":\{"simpleText":"([^"]*)"'
                    }
                    
                    for key, pattern in patterns.items():
                        match = re.search(pattern, text)
                        if match:
                            if key == 'subscribers':
                                sub_text = match.group(1)
                                metadata.follower_count = self._parse_subscriber_count(sub_text)
                            elif key == 'channel_name':
                                metadata.display_name = match.group(1)
                            elif key == 'description':
                                metadata.bio = match.group(1)
                    
                    if metadata.bio or metadata.display_name:
                        is_spanish, confidence = SpanishLanguageDetector.analyze(
                            f"{metadata.display_name or ''} {metadata.bio or ''}"
                        )
                        metadata.is_spanish = is_spanish
                        metadata.language_confidence = confidence
                    
                    metadata.verification_status = VerificationStatus.ACTIVE
                elif response.status == 404:
                    metadata.verification_status = VerificationStatus.NOT_FOUND
                else:
                    metadata.verification_status = VerificationStatus.ERROR
        
        except Exception as e:
            metadata.verification_status = VerificationStatus.ERROR
            metadata.error_message = str(e)
        
        metadata.enrichment_sources.append("youtube_web")
        return metadata
    
    def _parse_subscriber_count(self, text: str) -> Optional[int]:
        """Parse subscriber count from text like '1.2M subscribers'"""
        match = re.search(r'([\d.]+)([KMB])?', text)
        if match:
            num = float(match.group(1))
            multiplier = {'K': 1000, 'M': 1000000, 'B': 1000000000}.get(match.group(2), 1)
            return int(num * multiplier)
        return None


class WebsiteVerifier:
    """General website verification and enrichment"""
    
    def __init__(self, session: aiohttp.ClientSession, rate_limiter: RateLimiter):
        self.session = session
        self.rate_limiter = rate_limiter
    
    async def verify(self, url: str, metadata: LinkMetadata) -> LinkMetadata:
        """Verify website and extract metadata"""
        if not await self.rate_limiter.check_rate_limit(Platform.WEBSITE):
            metadata.verification_status = VerificationStatus.RATE_LIMITED
            return metadata
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Compatible; LinkVerifier/1.0)'}
            async with self.session.get(url, headers=headers, timeout=10, allow_redirects=True) as response:
                if response.status == 200:
                    text = await response.text()
                    metadata = await self._extract_website_data(text, metadata)
                    metadata.verification_status = VerificationStatus.ACTIVE
                elif response.status == 404:
                    metadata.verification_status = VerificationStatus.NOT_FOUND
                else:
                    metadata.verification_status = VerificationStatus.ERROR
                    metadata.error_message = f"HTTP {response.status}"
        
        except asyncio.TimeoutError:
            metadata.verification_status = VerificationStatus.ERROR
            metadata.error_message = "Timeout"
        except Exception as e:
            metadata.verification_status = VerificationStatus.ERROR
            metadata.error_message = str(e)
        
        metadata.enrichment_sources.append("website_scraping")
        return metadata
    
    async def _extract_website_data(self, html: str, metadata: LinkMetadata) -> LinkMetadata:
        """Extract metadata from website HTML"""
        patterns = {
            'title': r'<title>([^<]+)</title>',
            'description': r'<meta\s+name="description"\s+content="([^"]+)"',
            'og_title': r'<meta\s+property="og:title"\s+content="([^"]+)"',
            'og_description': r'<meta\s+property="og:description"\s+content="([^"]+)"',
            'twitter_handle': r'(?:twitter\.com/|@)([A-Za-z0-9_]+)',
            'instagram_handle': r'instagram\.com/([A-Za-z0-9_.]+)',
            'email': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            'phone': r'(\+?34[\s.-]?[0-9]{2,3}[\s.-]?[0-9]{3}[\s.-]?[0-9]{3})'
        }
        
        extracted_text = []
        
        for key, pattern in patterns.items():
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                if key in ['title', 'og_title'] and not metadata.display_name:
                    metadata.display_name = match.group(1)
                    extracted_text.append(match.group(1))
                elif key in ['description', 'og_description'] and not metadata.bio:
                    metadata.bio = match.group(1)
                    extracted_text.append(match.group(1))
                elif key == 'twitter_handle':
                    metadata.external_links.append(f"https://twitter.com/{match.group(1)}")
                elif key == 'instagram_handle':
                    metadata.external_links.append(f"https://instagram.com/{match.group(1)}")
                elif key == 'email' and not metadata.email:
                    metadata.email = match.group(1)
                elif key == 'phone' and not metadata.phone:
                    metadata.phone = match.group(1)
        
        if extracted_text:
            is_spanish, confidence = SpanishLanguageDetector.analyze(' '.join(extracted_text))
            metadata.is_spanish = is_spanish
            metadata.language_confidence = confidence
        
        return metadata


class CrossPlatformEnricher:
    """Enrich data by cross-referencing multiple platforms"""
    
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.search_engines = ['google', 'bing']
    
    async def enrich_from_search(self, metadata: LinkMetadata) -> LinkMetadata:
        """Use search engines to find additional information"""
        if not metadata.username and not metadata.display_name:
            return metadata
        
        search_query = metadata.display_name or metadata.username
        search_query = f'"{search_query}" site:instagram.com OR site:youtube.com OR site:twitter.com OR site:linkedin.com'
        
        try:
            url = f"https://www.google.com/search?q={search_query}"
            headers = {'User-Agent': 'Mozilla/5.0 (Compatible; LinkEnricher/1.0)'}
            
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    
                    social_patterns = {
                        'instagram': r'instagram\.com/([A-Za-z0-9_.]+)',
                        'youtube': r'youtube\.com/(?:c/|channel/|user/|@)([^/?]+)',
                        'twitter': r'twitter\.com/([A-Za-z0-9_]+)',
                        'linkedin': r'linkedin\.com/(?:in|company)/([^/?]+)'
                    }
                    
                    for platform, pattern in social_patterns.items():
                        matches = re.findall(pattern, text)
                        for match in matches[:2]:
                            link = f"https://{platform}.com/{match}"
                            if link not in metadata.external_links:
                                metadata.external_links.append(link)
            
            metadata.enrichment_sources.append("search_engine_discovery")
        
        except Exception as e:
            logger.error(f"Search enrichment failed: {e}")
        
        return metadata
    
    async def validate_cross_references(self, metadata: LinkMetadata) -> LinkMetadata:
        """Validate that discovered links actually reference the main account"""
        validated_links = []
        
        for link in metadata.external_links:
            try:
                async with self.session.get(link, timeout=5) as response:
                    if response.status == 200:
                        text = await response.text()
                        if metadata.username and metadata.username.lower() in text.lower():
                            validated_links.append(link)
                        elif metadata.display_name and metadata.display_name.lower() in text.lower():
                            validated_links.append(link)
            except:
                continue
        
        metadata.external_links = validated_links
        return metadata


class DatasetVerifier:
    """Main orchestrator for dataset verification and enrichment"""
    
    def __init__(self, youtube_api_key: Optional[str] = None):
        self.youtube_api_key = youtube_api_key
        self.rate_limiter = RateLimiter()
        self.results = []
        self.stats = defaultdict(int)
    
    async def verify_and_enrich(self, urls: List[str], batch_size: int = 10) -> List[LinkMetadata]:
        """Main entry point for verification and enrichment"""
        logger.info(f"Starting verification of {len(urls)} URLs")
        
        async with aiohttp.ClientSession() as session:
            instagram_verifier = InstagramVerifier(session, self.rate_limiter)
            youtube_verifier = YouTubeVerifier(session, self.rate_limiter, self.youtube_api_key)
            website_verifier = WebsiteVerifier(session, self.rate_limiter)
            cross_enricher = CrossPlatformEnricher(session)
            
            verifiers = {
                Platform.INSTAGRAM: instagram_verifier,
                Platform.YOUTUBE: youtube_verifier,
                Platform.WEBSITE: website_verifier
            }
            
            for i in range(0, len(urls), batch_size):
                batch = urls[i:i + batch_size]
                tasks = []
                
                for url in batch:
                    platform, username = PlatformDetector.detect(url)
                    metadata = LinkMetadata(
                        url=url,
                        platform=platform,
                        username=username
                    )
                    
                    if platform in verifiers:
                        verifier = verifiers[platform]
                        if platform == Platform.INSTAGRAM:
                            task = verifier.verify(username, metadata)
                        elif platform == Platform.YOUTUBE:
                            task = verifier.verify(username or url, metadata)
                        elif platform == Platform.WEBSITE:
                            task = verifier.verify(url, metadata)
                        else:
                            task = asyncio.create_task(self._mark_unsupported(metadata))
                        tasks.append(task)
                    else:
                        tasks.append(asyncio.create_task(self._mark_unsupported(metadata)))
                
                batch_results = await asyncio.gather(*tasks)
                
                enrichment_tasks = [
                    cross_enricher.enrich_from_search(metadata) 
                    for metadata in batch_results
                ]
                enriched_results = await asyncio.gather(*enrichment_tasks)
                
                for metadata in enriched_results:
                    metadata.calculate_quality_score()
                    self.results.append(metadata)
                    self.stats[metadata.verification_status] += 1
                
                logger.info(f"Processed batch {i//batch_size + 1}/{(len(urls) + batch_size - 1)//batch_size}")
                await asyncio.sleep(1)
        
        return self.results
    
    async def _mark_unsupported(self, metadata: LinkMetadata) -> LinkMetadata:
        """Mark unsupported platforms"""
        metadata.verification_status = VerificationStatus.ERROR
        metadata.error_message = f"Platform {metadata.platform.value} not supported"
        return metadata
    
    def export_results(self, output_file: str, format: str = 'json'):
        """Export verification results to file"""
        if format == 'json':
            self._export_json(output_file)
        elif format == 'csv':
            self._export_csv(output_file)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_json(self, output_file: str):
        """Export results as JSON"""
        # Create exports directory path
        exports_dir = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\data\exports")
        exports_dir.mkdir(parents=True, exist_ok=True)
        
        # Use exports directory if just filename is provided
        if not Path(output_file).is_absolute():
            output_path = exports_dir / output_file
        else:
            output_path = Path(output_file)
        
        data = []
        for metadata in self.results:
            data.append({
                'url': metadata.url,
                'platform': metadata.platform.value,
                'username': metadata.username,
                'display_name': metadata.display_name,
                'bio': metadata.bio,
                'follower_count': metadata.follower_count,
                'verification_status': metadata.verification_status.value,
                'is_spanish': metadata.is_spanish,
                'language_confidence': metadata.language_confidence,
                'quality_score': metadata.quality_score,
                'external_links': metadata.external_links,
                'last_verified': metadata.last_verified.isoformat(),
                'enrichment_sources': metadata.enrichment_sources
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _export_csv(self, output_file: str):
        """Export results as CSV"""
        import csv
        
        # Create exports directory path
        exports_dir = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\data\exports")
        exports_dir.mkdir(parents=True, exist_ok=True)
        
        # Use exports directory if just filename is provided
        if not Path(output_file).is_absolute():
            output_path = exports_dir / output_file
        else:
            output_path = Path(output_file)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'URL', 'Platform', 'Username', 'Display Name', 'Followers',
                'Status', 'Is Spanish', 'Language Confidence', 'Quality Score',
                'External Links Count', 'Last Verified'
            ])
            
            for metadata in self.results:
                writer.writerow([
                    metadata.url,
                    metadata.platform.value,
                    metadata.username or '',
                    metadata.display_name or '',
                    metadata.follower_count or '',
                    metadata.verification_status.value,
                    metadata.is_spanish,
                    f"{metadata.language_confidence:.2f}",
                    f"{metadata.quality_score:.2f}",
                    len(metadata.external_links),
                    metadata.last_verified.isoformat()
                ])
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get verification statistics"""
        total = len(self.results)
        spanish_count = sum(1 for r in self.results if r.is_spanish)
        high_quality = sum(1 for r in self.results if r.quality_score > 0.7)
        
        return {
            'total_processed': total,
            'status_breakdown': dict(self.stats),
            'spanish_accounts': spanish_count,
            'spanish_percentage': (spanish_count / total * 100) if total > 0 else 0,
            'high_quality_accounts': high_quality,
            'average_quality_score': sum(r.quality_score for r in self.results) / total if total > 0 else 0,
            'platforms': defaultdict(int, {r.platform.value: 1 for r in self.results})
        }


async def main():
    """Example usage"""
    urls = [
        "https://www.instagram.com/realmadrid",
        "https://www.youtube.com/@ElRubiusOMG",
        "https://twitter.com/marca",
        "https://www.elpais.com",
        "https://www.instagram.com/fcbarcelona",
        "https://www.tiktok.com/@laliga"
    ]
    
    verifier = DatasetVerifier(youtube_api_key=None)
    
    results = await verifier.verify_and_enrich(urls, batch_size=5)
    
    verifier.export_results('verified_spanish_accounts.json', format='json')
    verifier.export_results('verified_spanish_accounts.csv', format='csv')
    
    stats = verifier.get_statistics()
    print("\n=== Verification Statistics ===")
    print(f"Total Processed: {stats['total_processed']}")
    print(f"Spanish Accounts: {stats['spanish_accounts']} ({stats['spanish_percentage']:.1f}%)")
    print(f"High Quality: {stats['high_quality_accounts']}")
    print(f"Average Quality Score: {stats['average_quality_score']:.2f}")
    print(f"\nStatus Breakdown:")
    for status, count in stats['status_breakdown'].items():
        print(f"  {status.value}: {count}")


if __name__ == "__main__":
    asyncio.run(main())