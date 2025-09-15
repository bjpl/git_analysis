"""
Fixed Open-Source Search Enrichment with better error handling and alternative methods
"""

import asyncio
import aiohttp
import json
import re
import ssl
import certifi
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import logging
from urllib.parse import quote
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Search result with discovered URLs"""
    query: str
    source: str
    urls_found: Dict[str, List[str]] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = False
    error: Optional[str] = None


class AlternativeSearchEnricher:
    """
    Alternative search methods that are more reliable
    """
    
    def __init__(self):
        # Create SSL context that accepts more certificates
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        self.session = None
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        self.current_ua_index = 0
    
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        self.session = aiohttp.ClientSession(connector=connector)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_user_agent(self) -> str:
        """Rotate user agents"""
        ua = self.user_agents[self.current_ua_index]
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
        return ua
    
    def _extract_social_urls(self, text: str) -> Dict[str, List[str]]:
        """Extract social media URLs from text"""
        found = {
            'instagram': [],
            'youtube': [],
            'twitter': [],
            'facebook': [],
            'tiktok': [],
            'linkedin': [],
            'website': []
        }
        
        # Instagram patterns
        instagram_patterns = [
            r'instagram\.com/([a-zA-Z0-9_.]+)',
            r'instagr\.am/([a-zA-Z0-9_.]+)',
            r'@([a-zA-Z0-9_.]+)\s*(?:on\s+)?(?:Instagram|IG)'
        ]
        
        for pattern in instagram_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if not any(skip in match for skip in ['explore', 'p/', 'reel', 'tv']):
                    url = f"https://instagram.com/{match}"
                    if url not in found['instagram']:
                        found['instagram'].append(url)
        
        # YouTube patterns
        youtube_patterns = [
            r'youtube\.com/(?:c/|channel/|user/|@)([a-zA-Z0-9_-]+)',
            r'youtube\.com/([a-zA-Z0-9_-]+)',
            r'youtu\.be/([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in youtube_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) > 11:  # Skip video IDs
                    url = f"https://youtube.com/@{match}"
                    if url not in found['youtube']:
                        found['youtube'].append(url)
        
        # Twitter/X patterns
        twitter_patterns = [
            r'(?:twitter|x)\.com/([a-zA-Z0-9_]+)',
            r'@([a-zA-Z0-9_]+)\s*(?:on\s+)?(?:Twitter|X)'
        ]
        
        for pattern in twitter_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                url = f"https://twitter.com/{match}"
                if url not in found['twitter']:
                    found['twitter'].append(url)
        
        return found
    
    async def search_bing_html(self, query: str) -> SearchResult:
        """
        Use Bing HTML search (no API needed)
        """
        result = SearchResult(query=query, source='bing_html')
        
        try:
            url = f"https://www.bing.com/search?q={quote(query)}"
            headers = {
                'User-Agent': self._get_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            async with self.session.get(url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Extract URLs from Bing results
                    result.urls_found = self._extract_social_urls(html)
                    result.success = True
                    
                    total_found = sum(len(urls) for urls in result.urls_found.values())
                    logger.info(f"Bing search for '{query}' found {total_found} URLs")
                else:
                    result.error = f"HTTP {response.status}"
        
        except Exception as e:
            result.error = str(e)
            logger.warning(f"Bing search failed for '{query}': {e}")
        
        # Rate limiting
        await asyncio.sleep(2)
        
        return result
    
    async def search_startpage(self, query: str) -> SearchResult:
        """
        Use Startpage (privacy-focused Google results)
        """
        result = SearchResult(query=query, source='startpage')
        
        try:
            url = f"https://www.startpage.com/do/search"
            headers = {
                'User-Agent': self._get_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            params = {
                'q': query,
                'cat': 'web',
                'language': 'spanish'
            }
            
            async with self.session.get(url, headers=headers, params=params, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    result.urls_found = self._extract_social_urls(html)
                    result.success = True
                    
                    total_found = sum(len(urls) for urls in result.urls_found.values())
                    logger.info(f"Startpage search for '{query}' found {total_found} URLs")
                else:
                    result.error = f"HTTP {response.status}"
        
        except Exception as e:
            result.error = str(e)
            logger.warning(f"Startpage search failed for '{query}': {e}")
        
        await asyncio.sleep(2)
        
        return result
    
    async def search_qwant(self, query: str) -> SearchResult:
        """
        Use Qwant search (European privacy-focused)
        """
        result = SearchResult(query=query, source='qwant')
        
        try:
            url = "https://api.qwant.com/v3/search/web"
            headers = {
                'User-Agent': self._get_user_agent(),
            }
            params = {
                'q': query,
                'count': 20,
                'locale': 'es_ES',
                't': 'web'
            }
            
            async with self.session.get(url, headers=headers, params=params, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract text from results
                    all_text = []
                    if 'data' in data and 'result' in data['data']:
                        for item in data['data']['result'].get('items', []):
                            all_text.append(item.get('url', ''))
                            all_text.append(item.get('desc', ''))
                            all_text.append(item.get('title', ''))
                    
                    combined_text = ' '.join(all_text)
                    result.urls_found = self._extract_social_urls(combined_text)
                    result.success = True
                    
                    total_found = sum(len(urls) for urls in result.urls_found.values())
                    logger.info(f"Qwant search for '{query}' found {total_found} URLs")
                else:
                    result.error = f"HTTP {response.status}"
        
        except Exception as e:
            result.error = str(e)
            logger.warning(f"Qwant search failed for '{query}': {e}")
        
        await asyncio.sleep(2)
        
        return result
    
    async def search_yandex(self, query: str) -> SearchResult:
        """
        Use Yandex search (good for international content)
        """
        result = SearchResult(query=query, source='yandex')
        
        try:
            url = f"https://yandex.com/search/?text={quote(query)}&lr=169"  # lr=169 is Spain
            headers = {
                'User-Agent': self._get_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            async with self.session.get(url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    result.urls_found = self._extract_social_urls(html)
                    result.success = True
                    
                    total_found = sum(len(urls) for urls in result.urls_found.values())
                    logger.info(f"Yandex search for '{query}' found {total_found} URLs")
                else:
                    result.error = f"HTTP {response.status}"
        
        except Exception as e:
            result.error = str(e)
            logger.warning(f"Yandex search failed for '{query}': {e}")
        
        await asyncio.sleep(2)
        
        return result
    
    async def direct_platform_search(self, account_name: str, platform: str) -> Optional[str]:
        """
        Try to directly construct and verify platform URLs
        """
        # Clean account name for URL
        clean_name = re.sub(r'[^\w\s-]', '', account_name.lower())
        clean_name = re.sub(r'[-\s]+', '', clean_name)
        
        variations = [
            clean_name,
            clean_name.replace(' ', ''),
            clean_name.replace(' ', '_'),
            clean_name.replace(' ', '.'),
            clean_name + 'oficial',
            clean_name + 'official',
            clean_name + 'colombia',
            clean_name + 'mexico'
        ]
        
        found_urls = []
        
        for variant in variations[:5]:  # Limit attempts
            if platform == 'instagram':
                url = f"https://instagram.com/{variant}"
            elif platform == 'youtube':
                url = f"https://youtube.com/@{variant}"
            elif platform == 'twitter':
                url = f"https://twitter.com/{variant}"
            else:
                continue
            
            # Quick check if URL might exist
            try:
                headers = {'User-Agent': self._get_user_agent()}
                async with self.session.head(url, headers=headers, timeout=5, allow_redirects=True) as response:
                    if response.status in [200, 301, 302]:
                        found_urls.append(url)
                        logger.info(f"Direct check found: {url}")
                        return url
            except:
                continue
            
            await asyncio.sleep(0.5)
        
        return None
    
    async def multi_search(self, query: str, methods: List[str] = None) -> Dict[str, List[str]]:
        """
        Aggregate results from multiple search methods
        """
        if methods is None:
            methods = ['bing', 'qwant']  # Most reliable free options
        
        aggregated = {
            'instagram': set(),
            'youtube': set(),
            'twitter': set(),
            'facebook': set(),
            'tiktok': set(),
            'linkedin': set(),
            'website': set()
        }
        
        for method in methods:
            try:
                if method == 'bing':
                    result = await self.search_bing_html(query)
                elif method == 'startpage':
                    result = await self.search_startpage(query)
                elif method == 'qwant':
                    result = await self.search_qwant(query)
                elif method == 'yandex':
                    result = await self.search_yandex(query)
                else:
                    continue
                
                if result.success:
                    for platform, urls in result.urls_found.items():
                        aggregated[platform].update(urls)
            
            except Exception as e:
                logger.warning(f"Search method {method} failed: {e}")
                continue
        
        # Convert sets to lists
        return {k: list(v)[:5] for k, v in aggregated.items()}  # Limit to 5 per platform


class SmartAccountDiscovery:
    """
    Smart discovery system for Spanish accounts
    """
    
    def __init__(self):
        self.discovered = {}
        self.stats = {
            'searches': 0,
            'found': 0,
            'verified': 0
        }
    
    async def discover_account_urls(self, account: Dict) -> Dict[str, Any]:
        """
        Discover URLs for a single account using multiple strategies
        """
        discoveries = {
            'account': account,
            'discovered_urls': {},
            'search_queries': [],
            'timestamp': datetime.now().isoformat()
        }
        
        async with AlternativeSearchEnricher() as enricher:
            # Strategy 1: Direct platform check
            if account.get('handle'):
                handle = account['handle'].replace('@', '')
                
                # Try direct Instagram URL
                if not account.get('existing_instagram'):
                    direct_ig = await enricher.direct_platform_search(handle, 'instagram')
                    if direct_ig:
                        discoveries['discovered_urls']['instagram'] = {
                            'url': direct_ig,
                            'method': 'direct',
                            'confidence': 0.9
                        }
                
                # Try direct YouTube URL
                if not account.get('existing_youtube'):
                    direct_yt = await enricher.direct_platform_search(handle, 'youtube')
                    if direct_yt:
                        discoveries['discovered_urls']['youtube'] = {
                            'url': direct_yt,
                            'method': 'direct',
                            'confidence': 0.9
                        }
            
            # Strategy 2: Search queries
            queries = []
            
            if account.get('name'):
                # Build targeted queries
                name = account['name']
                queries.append(f'"{name}" instagram oficial')
                queries.append(f'"{name}" youtube channel')
                queries.append(f'"{name}" redes sociales')
            
            if account.get('handle'):
                handle = account['handle'].replace('@', '')
                queries.append(f'{handle} instagram youtube')
            
            # Execute searches
            for query in queries[:2]:  # Limit queries
                self.stats['searches'] += 1
                discoveries['search_queries'].append(query)
                
                try:
                    results = await enricher.multi_search(query, methods=['bing', 'qwant'])
                    
                    # Process Instagram results
                    if results.get('instagram') and not discoveries['discovered_urls'].get('instagram'):
                        for url in results['instagram']:
                            # Simple confidence based on name matching
                            confidence = 0.7 if account['name'].lower() in url.lower() else 0.5
                            discoveries['discovered_urls']['instagram'] = {
                                'url': url,
                                'method': 'search',
                                'query': query,
                                'confidence': confidence
                            }
                            self.stats['found'] += 1
                            break
                    
                    # Process YouTube results
                    if results.get('youtube') and not discoveries['discovered_urls'].get('youtube'):
                        for url in results['youtube']:
                            confidence = 0.7 if account['name'].lower() in url.lower() else 0.5
                            discoveries['discovered_urls']['youtube'] = {
                                'url': url,
                                'method': 'search',
                                'query': query,
                                'confidence': confidence
                            }
                            self.stats['found'] += 1
                            break
                    
                    # Bonus: Twitter
                    if results.get('twitter'):
                        for url in results['twitter'][:1]:
                            discoveries['discovered_urls']['twitter'] = {
                                'url': url,
                                'method': 'search',
                                'query': query,
                                'confidence': 0.6
                            }
                            self.stats['found'] += 1
                            break
                
                except Exception as e:
                    logger.error(f"Search failed for {query}: {e}")
                
                # Rate limiting
                await asyncio.sleep(3)
        
        return discoveries


# Test function
async def test_search():
    """Test the improved search functionality"""
    
    test_accounts = [
        {
            'handle': '@mincultura',
            'name': 'MinCultura Colombia',
            'existing_instagram': None,
            'existing_youtube': None
        },
        {
            'handle': '@realmadrid',
            'name': 'Real Madrid',
            'existing_instagram': None,
            'existing_youtube': None
        }
    ]
    
    discovery = SmartAccountDiscovery()
    
    for account in test_accounts:
        print(f"\n🔍 Searching for: {account['name']}")
        result = await discovery.discover_account_urls(account)
        
        if result['discovered_urls']:
            print(f"✅ Found URLs:")
            for platform, data in result['discovered_urls'].items():
                print(f"  - {platform}: {data['url']} (confidence: {data['confidence']:.2f})")
        else:
            print("❌ No URLs found")
    
    print(f"\n📊 Statistics:")
    print(f"  Searches performed: {discovery.stats['searches']}")
    print(f"  URLs found: {discovery.stats['found']}")


if __name__ == "__main__":
    # Test with known accounts
    asyncio.run(test_search())