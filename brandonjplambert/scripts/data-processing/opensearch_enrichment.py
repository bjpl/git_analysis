"""
Open-Source Search API Enrichment Module
Discovers missing social media URLs using free search APIs
"""

import asyncio
import aiohttp
import json
import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
from urllib.parse import quote, urlparse
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a search result with social media URLs"""
    query: str
    source: str
    urls_found: List[str] = field(default_factory=list)
    instagram_urls: List[str] = field(default_factory=list)
    youtube_urls: List[str] = field(default_factory=list)
    twitter_urls: List[str] = field(default_factory=list)
    facebook_urls: List[str] = field(default_factory=list)
    tiktok_urls: List[str] = field(default_factory=list)
    website_urls: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class OpenSearchEnricher:
    """
    Multi-source search enrichment using open-source APIs
    """
    
    SOCIAL_PATTERNS = {
        'instagram': [
            r'(?:https?://)?(?:www\.)?instagram\.com/([A-Za-z0-9_.]+)',
            r'(?:https?://)?(?:www\.)?instagr\.am/([A-Za-z0-9_.]+)'
        ],
        'youtube': [
            r'(?:https?://)?(?:www\.)?youtube\.com/(?:c/|channel/|user/|@)([A-Za-z0-9_-]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([A-Za-z0-9_-]+)',
            r'(?:https?://)?(?:www\.)?youtu\.be/([A-Za-z0-9_-]+)'
        ],
        'twitter': [
            r'(?:https?://)?(?:www\.)?twitter\.com/([A-Za-z0-9_]+)',
            r'(?:https?://)?(?:www\.)?x\.com/([A-Za-z0-9_]+)'
        ],
        'facebook': [
            r'(?:https?://)?(?:www\.)?facebook\.com/([A-Za-z0-9.]+)',
            r'(?:https?://)?(?:www\.)?fb\.com/([A-Za-z0-9.]+)'
        ],
        'tiktok': [
            r'(?:https?://)?(?:www\.)?tiktok\.com/@([A-Za-z0-9_.]+)'
        ]
    }
    
    def __init__(self, cache_ttl: int = 86400):
        self.session = None
        self.cache = {}
        self.cache_ttl = cache_ttl
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_cache_key(self, query: str, source: str) -> str:
        """Generate cache key for search query"""
        return hashlib.md5(f"{query}_{source}".encode()).hexdigest()
    
    def _get_from_cache(self, query: str, source: str) -> Optional[SearchResult]:
        """Get cached search result if available"""
        key = self._get_cache_key(query, source)
        if key in self.cache:
            result, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                return result
        return None
    
    def _save_to_cache(self, query: str, source: str, result: SearchResult):
        """Save search result to cache"""
        key = self._get_cache_key(query, source)
        self.cache[key] = (result, datetime.now())
    
    def _extract_social_urls(self, text: str) -> Dict[str, List[str]]:
        """Extract social media URLs from text"""
        found_urls = {
            'instagram': [],
            'youtube': [],
            'twitter': [],
            'facebook': [],
            'tiktok': [],
            'websites': []
        }
        
        for platform, patterns in self.SOCIAL_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if platform == 'instagram':
                        url = f"https://instagram.com/{match}"
                    elif platform == 'youtube':
                        if match.startswith('UC') or len(match) == 11:  # Video ID
                            continue
                        url = f"https://youtube.com/@{match}"
                    elif platform == 'twitter':
                        url = f"https://twitter.com/{match}"
                    elif platform == 'facebook':
                        url = f"https://facebook.com/{match}"
                    elif platform == 'tiktok':
                        url = f"https://tiktok.com/@{match}"
                    else:
                        continue
                    
                    if url not in found_urls[platform]:
                        found_urls[platform].append(url)
        
        # Extract general websites
        website_pattern = r'https?://(?:www\.)?([A-Za-z0-9.-]+\.[A-Za-z]{2,})'
        websites = re.findall(website_pattern, text, re.IGNORECASE)
        for website in websites:
            if not any(social in website for social in ['instagram.com', 'youtube.com', 'twitter.com', 'facebook.com', 'tiktok.com']):
                url = f"https://{website}" if not website.startswith('http') else website
                if url not in found_urls['websites']:
                    found_urls['websites'].append(url)
        
        return found_urls
    
    async def search_duckduckgo(self, query: str) -> SearchResult:
        """
        Search using DuckDuckGo HTML (no API key required)
        DuckDuckGo allows scraping their HTML version
        """
        cached = self._get_from_cache(query, 'duckduckgo')
        if cached:
            return cached
        
        result = SearchResult(query=query, source='duckduckgo')
        
        try:
            # DuckDuckGo HTML search
            url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Parse with BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract all result snippets
                    results_text = []
                    for result_div in soup.find_all('div', class_='result'):
                        # Get URL
                        link = result_div.find('a', class_='result__url')
                        if link:
                            results_text.append(link.get('href', ''))
                        
                        # Get snippet text
                        snippet = result_div.find('a', class_='result__snippet')
                        if snippet:
                            results_text.append(snippet.text)
                    
                    # Extract social URLs from all text
                    all_text = ' '.join(results_text)
                    social_urls = self._extract_social_urls(all_text)
                    
                    result.instagram_urls = social_urls['instagram']
                    result.youtube_urls = social_urls['youtube']
                    result.twitter_urls = social_urls['twitter']
                    result.facebook_urls = social_urls['facebook']
                    result.tiktok_urls = social_urls['tiktok']
                    result.website_urls = social_urls['websites']
                    
                    # Calculate confidence based on results found
                    total_found = sum(len(urls) for urls in social_urls.values())
                    result.confidence_score = min(1.0, total_found * 0.2)
                    
                    logger.info(f"DuckDuckGo search for '{query}' found {total_found} URLs")
        
        except Exception as e:
            logger.error(f"DuckDuckGo search failed for '{query}': {e}")
        
        self._save_to_cache(query, 'duckduckgo', result)
        return result
    
    async def search_searx(self, query: str, searx_instance: str = "https://searx.be") -> SearchResult:
        """
        Search using Searx (open-source metasearch engine)
        Multiple public instances available
        """
        cached = self._get_from_cache(query, 'searx')
        if cached:
            return cached
        
        result = SearchResult(query=query, source='searx')
        
        # List of public Searx instances (fallback options)
        searx_instances = [
            "https://searx.be",
            "https://searx.info",
            "https://search.sapti.me",
            "https://searx.tiekoetter.com"
        ]
        
        for instance in searx_instances:
            try:
                url = f"{instance}/search"
                params = {
                    'q': query,
                    'format': 'json',
                    'engines': 'google,bing,duckduckgo',
                    'categories': 'general'
                }
                
                async with self.session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract URLs from results
                        all_text = []
                        for item in data.get('results', [])[:20]:
                            all_text.append(item.get('url', ''))
                            all_text.append(item.get('content', ''))
                            all_text.append(item.get('title', ''))
                        
                        # Extract social URLs
                        combined_text = ' '.join(all_text)
                        social_urls = self._extract_social_urls(combined_text)
                        
                        result.instagram_urls = social_urls['instagram']
                        result.youtube_urls = social_urls['youtube']
                        result.twitter_urls = social_urls['twitter']
                        result.facebook_urls = social_urls['facebook']
                        result.tiktok_urls = social_urls['tiktok']
                        result.website_urls = social_urls['websites']
                        
                        total_found = sum(len(urls) for urls in social_urls.values())
                        result.confidence_score = min(1.0, total_found * 0.25)
                        
                        logger.info(f"Searx search for '{query}' found {total_found} URLs")
                        break
            
            except Exception as e:
                logger.warning(f"Searx instance {instance} failed: {e}")
                continue
        
        self._save_to_cache(query, 'searx', result)
        return result
    
    async def search_brave(self, query: str) -> SearchResult:
        """
        Search using Brave Search (limited free tier available)
        Requires free API key from https://brave.com/search/api/
        """
        cached = self._get_from_cache(query, 'brave')
        if cached:
            return cached
        
        result = SearchResult(query=query, source='brave')
        
        # Note: You can get a free API key with 2000 queries/month
        # from https://brave.com/search/api/
        api_key = None  # Add your free Brave API key here if available
        
        if api_key:
            try:
                url = "https://api.search.brave.com/res/v1/web/search"
                headers = {
                    'X-Subscription-Token': api_key,
                    'Accept': 'application/json'
                }
                params = {
                    'q': query,
                    'count': 20
                }
                
                async with self.session.get(url, headers=headers, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        all_text = []
                        for item in data.get('web', {}).get('results', []):
                            all_text.append(item.get('url', ''))
                            all_text.append(item.get('description', ''))
                            all_text.append(item.get('title', ''))
                        
                        combined_text = ' '.join(all_text)
                        social_urls = self._extract_social_urls(combined_text)
                        
                        result.instagram_urls = social_urls['instagram']
                        result.youtube_urls = social_urls['youtube']
                        result.twitter_urls = social_urls['twitter']
                        result.facebook_urls = social_urls['facebook']
                        result.tiktok_urls = social_urls['tiktok']
                        result.website_urls = social_urls['websites']
                        
                        total_found = sum(len(urls) for urls in social_urls.values())
                        result.confidence_score = min(1.0, total_found * 0.3)
                        
                        logger.info(f"Brave search for '{query}' found {total_found} URLs")
            
            except Exception as e:
                logger.error(f"Brave search failed for '{query}': {e}")
        
        self._save_to_cache(query, 'brave', result)
        return result
    
    async def search_google_cse(self, query: str, api_key: str = None, cx: str = None) -> SearchResult:
        """
        Google Custom Search Engine (100 free queries/day)
        Get free API key from: https://developers.google.com/custom-search/v1/overview
        """
        cached = self._get_from_cache(query, 'google_cse')
        if cached:
            return cached
        
        result = SearchResult(query=query, source='google_cse')
        
        if api_key and cx:
            try:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    'key': api_key,
                    'cx': cx,
                    'q': query,
                    'num': 10
                }
                
                async with self.session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        all_text = []
                        for item in data.get('items', []):
                            all_text.append(item.get('link', ''))
                            all_text.append(item.get('snippet', ''))
                            all_text.append(item.get('title', ''))
                        
                        combined_text = ' '.join(all_text)
                        social_urls = self._extract_social_urls(combined_text)
                        
                        result.instagram_urls = social_urls['instagram']
                        result.youtube_urls = social_urls['youtube']
                        result.twitter_urls = social_urls['twitter']
                        result.facebook_urls = social_urls['facebook']
                        result.tiktok_urls = social_urls['tiktok']
                        result.website_urls = social_urls['websites']
                        
                        total_found = sum(len(urls) for urls in social_urls.values())
                        result.confidence_score = min(1.0, total_found * 0.35)
                        
                        logger.info(f"Google CSE search for '{query}' found {total_found} URLs")
            
            except Exception as e:
                logger.error(f"Google CSE search failed for '{query}': {e}")
        
        self._save_to_cache(query, 'google_cse', result)
        return result
    
    async def aggregate_search(self, query: str, use_sources: List[str] = None) -> Dict[str, List[str]]:
        """
        Aggregate results from multiple search sources
        """
        if use_sources is None:
            use_sources = ['duckduckgo', 'searx']
        
        tasks = []
        if 'duckduckgo' in use_sources:
            tasks.append(self.search_duckduckgo(query))
        if 'searx' in use_sources:
            tasks.append(self.search_searx(query))
        if 'brave' in use_sources:
            tasks.append(self.search_brave(query))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate all found URLs
        aggregated = {
            'instagram': set(),
            'youtube': set(),
            'twitter': set(),
            'facebook': set(),
            'tiktok': set(),
            'websites': set()
        }
        
        for result in results:
            if isinstance(result, SearchResult):
                aggregated['instagram'].update(result.instagram_urls)
                aggregated['youtube'].update(result.youtube_urls)
                aggregated['twitter'].update(result.twitter_urls)
                aggregated['facebook'].update(result.facebook_urls)
                aggregated['tiktok'].update(result.tiktok_urls)
                aggregated['websites'].update(result.website_urls)
        
        # Convert sets back to lists
        return {k: list(v) for k, v in aggregated.items()}


class AccountMatcher:
    """
    Intelligent matching of discovered URLs to accounts
    """
    
    @staticmethod
    def calculate_name_similarity(name1: str, name2: str) -> float:
        """Calculate similarity between two names"""
        if not name1 or not name2:
            return 0.0
        
        name1_lower = name1.lower().strip()
        name2_lower = name2.lower().strip()
        
        # Exact match
        if name1_lower == name2_lower:
            return 1.0
        
        # One contains the other
        if name1_lower in name2_lower or name2_lower in name1_lower:
            return 0.8
        
        # Common words
        words1 = set(name1_lower.split())
        words2 = set(name2_lower.split())
        if words1 and words2:
            intersection = words1 & words2
            union = words1 | words2
            jaccard = len(intersection) / len(union)
            return jaccard * 0.7
        
        return 0.0
    
    @staticmethod
    def extract_username_from_url(url: str) -> Optional[str]:
        """Extract username from social media URL"""
        patterns = {
            'instagram.com': r'instagram\.com/([A-Za-z0-9_.]+)',
            'youtube.com': r'youtube\.com/(?:@|c/|channel/|user/)([A-Za-z0-9_-]+)',
            'twitter.com': r'(?:twitter|x)\.com/([A-Za-z0-9_]+)',
            'facebook.com': r'facebook\.com/([A-Za-z0-9.]+)',
            'tiktok.com': r'tiktok\.com/@([A-Za-z0-9_.]+)'
        }
        
        for domain, pattern in patterns.items():
            if domain in url:
                match = re.search(pattern, url, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        return None
    
    @classmethod
    def match_url_to_account(cls, url: str, account_data: Dict) -> float:
        """
        Calculate confidence that URL belongs to account
        Returns confidence score 0.0 to 1.0
        """
        confidence = 0.0
        
        # Extract username from URL
        url_username = cls.extract_username_from_url(url)
        if not url_username:
            return 0.0
        
        # Check against account handle
        if account_data.get('handle'):
            handle = account_data['handle'].replace('@', '').lower()
            url_user_lower = url_username.lower()
            
            if handle == url_user_lower:
                confidence = 0.9
            elif handle in url_user_lower or url_user_lower in handle:
                confidence = 0.7
            else:
                # Check similarity
                similarity = cls.calculate_name_similarity(handle, url_username)
                confidence = max(confidence, similarity * 0.6)
        
        # Check against account name
        if account_data.get('name'):
            name_similarity = cls.calculate_name_similarity(
                account_data['name'], 
                url_username.replace('_', ' ').replace('-', ' ')
            )
            confidence = max(confidence, name_similarity * 0.5)
        
        # Boost confidence if category matches common patterns
        if account_data.get('category'):
            category = account_data['category'].lower()
            if category in ['government', 'diplomatic'] and any(
                keyword in url_username.lower() 
                for keyword in ['gov', 'gob', 'min', 'embassy', 'consul']
            ):
                confidence = min(1.0, confidence + 0.2)
        
        return confidence


class EnrichmentPipeline:
    """
    Complete enrichment pipeline using open-source search
    """
    
    def __init__(self, confidence_threshold: float = 0.6):
        self.confidence_threshold = confidence_threshold
        self.discovered_urls = {}
        self.stats = {
            'accounts_processed': 0,
            'searches_performed': 0,
            'urls_discovered': 0,
            'urls_matched': 0
        }
    
    async def enrich_account(self, account: Dict) -> Dict:
        """
        Enrich single account with discovered URLs
        """
        # Build search queries
        queries = []
        
        # Primary query with account name
        if account.get('name'):
            queries.append(f'"{account["name"]}" instagram youtube')
            queries.append(f'"{account["name"]}" social media')
        
        # Secondary query with handle
        if account.get('handle'):
            handle = account['handle'].replace('@', '')
            queries.append(f'"{handle}" site:instagram.com OR site:youtube.com')
        
        # Category-specific query
        if account.get('description'):
            queries.append(f'"{account["description"][:50]}" social media')
        
        discovered = {
            'instagram': [],
            'youtube': [],
            'twitter': [],
            'facebook': [],
            'tiktok': [],
            'websites': []
        }
        
        async with OpenSearchEnricher() as enricher:
            for query in queries[:2]:  # Limit queries per account
                self.stats['searches_performed'] += 1
                
                try:
                    results = await enricher.aggregate_search(query)
                    
                    # Match discovered URLs to account
                    for platform, urls in results.items():
                        for url in urls:
                            confidence = AccountMatcher.match_url_to_account(url, account)
                            
                            if confidence >= self.confidence_threshold:
                                if url not in discovered[platform]:
                                    discovered[platform].append({
                                        'url': url,
                                        'confidence': confidence,
                                        'source_query': query
                                    })
                                    self.stats['urls_discovered'] += 1
                
                except Exception as e:
                    logger.error(f"Search failed for account {account.get('name')}: {e}")
        
        # Add discovered URLs to account
        enriched_account = account.copy()
        
        # Add high-confidence discoveries
        new_urls = []
        for platform, discoveries in discovered.items():
            if discoveries:
                # Sort by confidence and take best match
                best_match = sorted(discoveries, key=lambda x: x['confidence'], reverse=True)[0]
                if best_match['confidence'] >= self.confidence_threshold:
                    new_urls.append({
                        'platform': platform,
                        'url': best_match['url'],
                        'confidence': best_match['confidence'],
                        'discovered_via': 'opensearch'
                    })
                    self.stats['urls_matched'] += 1
        
        if new_urls:
            enriched_account['discovered_urls'] = new_urls
            enriched_account['enrichment_timestamp'] = datetime.now().isoformat()
        
        self.stats['accounts_processed'] += 1
        
        return enriched_account
    
    async def enrich_dataset(self, accounts: List[Dict], batch_size: int = 5) -> List[Dict]:
        """
        Enrich multiple accounts with discovered URLs
        """
        enriched_accounts = []
        
        for i in range(0, len(accounts), batch_size):
            batch = accounts[i:i + batch_size]
            
            tasks = [self.enrich_account(account) for account in batch]
            batch_results = await asyncio.gather(*tasks)
            
            enriched_accounts.extend(batch_results)
            
            logger.info(f"Enriched batch {i//batch_size + 1}/{(len(accounts) + batch_size - 1)//batch_size}")
            
            # Rate limiting between batches
            await asyncio.sleep(2)
        
        return enriched_accounts
    
    def get_statistics(self) -> Dict:
        """Get enrichment statistics"""
        return {
            **self.stats,
            'discovery_rate': (self.stats['urls_matched'] / max(self.stats['accounts_processed'], 1)) * 100
        }


# Example usage for your Spanish accounts
async def enrich_spanish_accounts():
    """
    Example of enriching Spanish accounts with discovered URLs
    """
    # Sample account data
    accounts = [
        {
            'handle': '@mincultura',
            'name': 'MinCultura Colombia',
            'category': 'Government',
            'description': 'Ministry of Culture of Colombia'
        },
        {
            'handle': '@embamexeua',
            'name': 'Mexico in USA',
            'category': 'Diplomatic',
            'description': 'Mexican Embassy in Washington DC'
        }
    ]
    
    pipeline = EnrichmentPipeline(confidence_threshold=0.6)
    enriched = await pipeline.enrich_dataset(accounts)
    
    # Display results
    for account in enriched:
        if 'discovered_urls' in account:
            print(f"\n{account['name']}:")
            for discovery in account['discovered_urls']:
                print(f"  Found {discovery['platform']}: {discovery['url']} (confidence: {discovery['confidence']:.2f})")
    
    stats = pipeline.get_statistics()
    print(f"\nStatistics:")
    print(f"  Accounts processed: {stats['accounts_processed']}")
    print(f"  URLs discovered: {stats['urls_discovered']}")
    print(f"  URLs matched: {stats['urls_matched']}")
    print(f"  Discovery rate: {stats['discovery_rate']:.1f}%")


if __name__ == "__main__":
    # Note: Install required package
    # pip install beautifulsoup4
    
    asyncio.run(enrich_spanish_accounts())