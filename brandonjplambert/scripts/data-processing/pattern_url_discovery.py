"""
Pattern-based URL Discovery with Verification
Generates probable social media URLs from account data and verifies them
"""

import asyncio
import re
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

# Import your existing verifier
# Add parent directories to path for cross-directory imports
sys.path.append(str(Path(__file__).parent.parent / "verification"))

from spanish_links_verifier import DatasetVerifier, Platform, VerificationStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GeneratedURL:
    """Represents a generated URL with metadata"""
    url: str
    platform: str
    pattern_used: str
    confidence: float
    verification_status: Optional[str] = None
    is_active: bool = False
    follower_count: Optional[int] = None


class SpanishPatternGenerator:
    """
    Generates URLs based on Spanish naming conventions and patterns
    """
    
    # Common Spanish government/organization patterns
    SPANISH_PATTERNS = {
        'government': {
            'prefixes': ['', 'gob', 'gobierno', 'min'],
            'suffixes': ['', 'mx', 'col', 'colombia', 'mexico', 'es', 'esp', 'oficial', 'gob'],
            'separators': ['', '_', '.']
        },
        'diplomatic': {
            'prefixes': ['', 'emb', 'embajada', 'consulado', 'consul'],
            'suffixes': ['', 'mx', 'mex', 'mexico', 'usa', 'eeuu', 'es', 'esp'],
            'separators': ['', '_', '.']
        },
        'cultural': {
            'prefixes': ['', 'cultura', 'museo', 'biblioteca'],
            'suffixes': ['', 'mx', 'col', 'oficial', 'cultura'],
            'separators': ['', '_', '.']
        },
        'tourism': {
            'prefixes': ['', 'visit', 'turismo', 'tour'],
            'suffixes': ['', 'mx', 'mexico', 'colombia', 'oficial'],
            'separators': ['', '_', '.']
        },
        'media': {
            'prefixes': ['', 'noticias', 'radio', 'tv'],
            'suffixes': ['', 'mx', 'col', 'news', 'oficial'],
            'separators': ['', '_', '.']
        }
    }
    
    @staticmethod
    def clean_name(name: str) -> str:
        """Clean account name for URL generation"""
        # Remove common words
        stop_words = ['de', 'del', 'la', 'el', 'los', 'las', 'en', 'y', 'of', 'the', 'in']
        
        # Convert to lowercase and remove special chars
        clean = re.sub(r'[^\w\s-]', '', name.lower())
        
        # Remove stop words
        words = clean.split()
        words = [w for w in words if w not in stop_words]
        
        return ''.join(words)
    
    @staticmethod
    def extract_acronym(name: str) -> str:
        """Extract acronym from organization name"""
        # For names like "MinCultura Colombia" -> "mincultura"
        words = name.split()
        
        # Check if first word is already an acronym
        if words and words[0].startswith('Min'):
            return words[0].lower()
        
        # Create acronym from capital letters
        acronym = ''.join([w[0] for w in words if w[0].isupper()])
        return acronym.lower() if len(acronym) > 2 else None
    
    @classmethod
    def generate_instagram_patterns(cls, account: Dict) -> List[Tuple[str, float]]:
        """Generate possible Instagram URLs with confidence scores"""
        patterns = []
        
        # Extract base elements
        handle = account.get('handle', '').replace('@', '').lower()
        name = account.get('name', '')
        category = account.get('category', '').lower()
        
        # Direct handle match (highest confidence)
        if handle:
            patterns.append((f"https://instagram.com/{handle}", 0.9))
            patterns.append((f"https://instagram.com/{handle}oficial", 0.7))
            patterns.append((f"https://instagram.com/{handle}_oficial", 0.7))
        
        # Clean name variations
        if name:
            clean = cls.clean_name(name)
            patterns.append((f"https://instagram.com/{clean}", 0.8))
            
            # Add category-specific patterns
            if category in cls.SPANISH_PATTERNS:
                cat_patterns = cls.SPANISH_PATTERNS[category]
                
                for prefix in cat_patterns['prefixes'][:2]:
                    for suffix in cat_patterns['suffixes'][:3]:
                        for sep in cat_patterns['separators'][:2]:
                            if prefix:
                                variant = f"{prefix}{sep}{clean}"
                            else:
                                variant = clean
                            if suffix:
                                variant = f"{variant}{sep}{suffix}"
                            
                            patterns.append((f"https://instagram.com/{variant}", 0.6))
            
            # Acronym patterns
            acronym = cls.extract_acronym(name)
            if acronym:
                patterns.append((f"https://instagram.com/{acronym}", 0.7))
                patterns.append((f"https://instagram.com/{acronym}oficial", 0.6))
                
                # Country-specific acronyms
                if 'colombia' in name.lower():
                    patterns.append((f"https://instagram.com/{acronym}col", 0.7))
                    patterns.append((f"https://instagram.com/{acronym}co", 0.6))
                elif 'mexico' in name.lower() or 'méxico' in name.lower():
                    patterns.append((f"https://instagram.com/{acronym}mx", 0.7))
                    patterns.append((f"https://instagram.com/{acronym}mex", 0.6))
        
        # Remove duplicates while preserving order and confidence
        seen = set()
        unique_patterns = []
        for url, conf in patterns:
            if url not in seen:
                seen.add(url)
                unique_patterns.append((url, conf))
        
        # Sort by confidence
        return sorted(unique_patterns, key=lambda x: x[1], reverse=True)[:10]
    
    @classmethod
    def generate_youtube_patterns(cls, account: Dict) -> List[Tuple[str, float]]:
        """Generate possible YouTube URLs with confidence scores"""
        patterns = []
        
        handle = account.get('handle', '').replace('@', '').lower()
        name = account.get('name', '')
        category = account.get('category', '').lower()
        
        # YouTube has different URL formats
        if handle:
            patterns.append((f"https://youtube.com/@{handle}", 0.9))
            patterns.append((f"https://youtube.com/c/{handle}", 0.8))
            patterns.append((f"https://youtube.com/user/{handle}", 0.7))
            patterns.append((f"https://youtube.com/@{handle}oficial", 0.7))
        
        if name:
            clean = cls.clean_name(name)
            
            # YouTube often uses full names with capitals
            name_variant = name.replace(' ', '')
            patterns.append((f"https://youtube.com/@{name_variant}", 0.7))
            patterns.append((f"https://youtube.com/c/{name_variant}", 0.6))
            
            # Clean version
            patterns.append((f"https://youtube.com/@{clean}", 0.8))
            patterns.append((f"https://youtube.com/c/{clean}", 0.7))
            
            # With channel prefix
            patterns.append((f"https://youtube.com/channel/{clean}", 0.5))
            
            # Government channels often use full ministry names
            if 'ministerio' in name.lower() or 'ministry' in name.lower():
                ministry_name = name.replace(' ', '')
                patterns.append((f"https://youtube.com/@{ministry_name}", 0.8))
                patterns.append((f"https://youtube.com/c/Ministerio{clean}", 0.7))
            
            # Embassy channels
            if 'embajada' in name.lower() or 'embassy' in name.lower():
                patterns.append((f"https://youtube.com/@Embajada{clean}", 0.7))
                patterns.append((f"https://youtube.com/@Embassy{clean}", 0.6))
        
        # Remove duplicates
        seen = set()
        unique_patterns = []
        for url, conf in patterns:
            if url not in seen:
                seen.add(url)
                unique_patterns.append((url, conf))
        
        return sorted(unique_patterns, key=lambda x: x[1], reverse=True)[:10]
    
    @classmethod
    def generate_twitter_patterns(cls, account: Dict) -> List[Tuple[str, float]]:
        """Generate possible Twitter/X URLs"""
        patterns = []
        
        handle = account.get('handle', '').replace('@', '').lower()
        name = account.get('name', '')
        
        if handle:
            patterns.append((f"https://twitter.com/{handle}", 0.9))
            patterns.append((f"https://x.com/{handle}", 0.9))
        
        if name:
            clean = cls.clean_name(name)
            patterns.append((f"https://twitter.com/{clean}", 0.7))
            
            acronym = cls.extract_acronym(name)
            if acronym:
                patterns.append((f"https://twitter.com/{acronym}", 0.6))
        
        return patterns[:5]


class PatternURLDiscovery:
    """
    Discovers missing URLs using pattern generation and verification
    """
    
    def __init__(self):
        self.generator = SpanishPatternGenerator()
        self.verifier = DatasetVerifier()
        self.discovered_urls = {}
        self.statistics = {
            'patterns_generated': 0,
            'urls_verified': 0,
            'urls_found_active': 0,
            'instagram_discovered': 0,
            'youtube_discovered': 0,
            'twitter_discovered': 0
        }
    
    async def discover_account_urls(self, account: Dict) -> Dict[str, GeneratedURL]:
        """
        Generate and verify URLs for a single account
        """
        discovered = {}
        
        # Generate patterns for missing platforms
        patterns_to_verify = []
        
        # Instagram patterns
        if not account.get('existing_instagram'):
            ig_patterns = self.generator.generate_instagram_patterns(account)
            for url, confidence in ig_patterns:
                patterns_to_verify.append({
                    'url': url,
                    'platform': 'instagram',
                    'confidence': confidence,
                    'pattern': 'instagram_pattern'
                })
            self.statistics['patterns_generated'] += len(ig_patterns)
        
        # YouTube patterns
        if not account.get('existing_youtube'):
            yt_patterns = self.generator.generate_youtube_patterns(account)
            for url, confidence in yt_patterns:
                patterns_to_verify.append({
                    'url': url,
                    'platform': 'youtube',
                    'confidence': confidence,
                    'pattern': 'youtube_pattern'
                })
            self.statistics['patterns_generated'] += len(yt_patterns)
        
        # Bonus: Twitter patterns
        tw_patterns = self.generator.generate_twitter_patterns(account)
        for url, confidence in tw_patterns[:3]:
            patterns_to_verify.append({
                'url': url,
                'platform': 'twitter',
                'confidence': confidence,
                'pattern': 'twitter_pattern'
            })
        
        # Verify URLs in batches
        if patterns_to_verify:
            logger.info(f"Verifying {len(patterns_to_verify)} generated URLs for {account.get('name')}")
            
            # Extract just URLs for verification
            urls_to_verify = [p['url'] for p in patterns_to_verify]
            
            # Verify with rate limiting
            verification_results = await self.verifier.verify_and_enrich(
                urls_to_verify,
                batch_size=5
            )
            
            self.statistics['urls_verified'] += len(verification_results)
            
            # Match results back to patterns
            for i, result in enumerate(verification_results):
                if i < len(patterns_to_verify):
                    pattern_info = patterns_to_verify[i]
                    
                    # Check if URL is active
                    if result.verification_status == VerificationStatus.ACTIVE:
                        generated_url = GeneratedURL(
                            url=result.url,
                            platform=pattern_info['platform'],
                            pattern_used=pattern_info['pattern'],
                            confidence=pattern_info['confidence'],
                            verification_status='active',
                            is_active=True,
                            follower_count=result.follower_count
                        )
                        
                        # Store the best match for each platform
                        platform = pattern_info['platform']
                        if platform not in discovered or discovered[platform].confidence < pattern_info['confidence']:
                            discovered[platform] = generated_url
                            self.statistics['urls_found_active'] += 1
                            self.statistics[f"{platform}_discovered"] += 1
                            
                            logger.info(f"✅ Found active {platform}: {result.url} ({result.follower_count} followers)")
                            
                            # Stop searching for this platform once found
                            break
        
        return discovered
    
    async def process_yaml_accounts(self, yaml_file: str, max_accounts: int = None) -> Dict:
        """
        Process accounts from YAML file to discover missing URLs
        """
        logger.info(f"Loading accounts from {yaml_file}")
        
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        accounts_to_process = []
        
        if 'accounts' in data:
            for account in data['accounts']:
                if account:
                    # Check what's missing
                    needs_instagram = not account.get('instagram_url')
                    needs_youtube = not account.get('youtube_url')
                    
                    if needs_instagram or needs_youtube:
                        accounts_to_process.append({
                            'handle': account.get('handle', ''),
                            'name': account.get('name', ''),
                            'category': account.get('category', ''),
                            'description': account.get('description', ''),
                            'existing_instagram': account.get('instagram_url'),
                            'existing_youtube': account.get('youtube_url'),
                            'needs_instagram': needs_instagram,
                            'needs_youtube': needs_youtube
                        })
        
        if max_accounts:
            accounts_to_process = accounts_to_process[:max_accounts]
        
        logger.info(f"Processing {len(accounts_to_process)} accounts needing URL discovery")
        
        results = []
        for i, account in enumerate(accounts_to_process):
            logger.info(f"\nProcessing {i+1}/{len(accounts_to_process)}: {account['name']}")
            
            discovered = await self.discover_account_urls(account)
            
            if discovered:
                account_result = {
                    'account': account,
                    'discovered_urls': {}
                }
                
                for platform, url_data in discovered.items():
                    account_result['discovered_urls'][platform] = {
                        'url': url_data.url,
                        'confidence': url_data.confidence,
                        'is_active': url_data.is_active,
                        'followers': url_data.follower_count
                    }
                
                results.append(account_result)
            
            # Rate limiting between accounts
            if i % 5 == 4:
                logger.info("Pausing for rate limiting...")
                await asyncio.sleep(10)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.statistics,
            'results': results
        }


async def main():
    """
    Main execution for pattern-based URL discovery
    """
    yaml_file = r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml"
    output_dir = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\pattern_discovery")
    output_dir.mkdir(exist_ok=True)
    
    print("\n🔍 Pattern-Based URL Discovery System")
    print("="*60)
    print("Generating and verifying probable social media URLs")
    print("="*60)
    
    discovery = PatternURLDiscovery()
    
    # Process first 10 accounts as test
    results = await discovery.process_yaml_accounts(yaml_file, max_accounts=10)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"pattern_discoveries_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("DISCOVERY SUMMARY")
    print("="*60)
    
    stats = results['statistics']
    print(f"\n📊 Statistics:")
    print(f"  Patterns Generated: {stats['patterns_generated']}")
    print(f"  URLs Verified: {stats['urls_verified']}")
    print(f"  Active URLs Found: {stats['urls_found_active']}")
    print(f"  Instagram Discovered: {stats['instagram_discovered']}")
    print(f"  YouTube Discovered: {stats['youtube_discovered']}")
    print(f"  Twitter Discovered: {stats['twitter_discovered']}")
    
    if stats['urls_verified'] > 0:
        success_rate = (stats['urls_found_active'] / stats['urls_verified']) * 100
        print(f"  Success Rate: {success_rate:.1f}%")
    
    print(f"\n✅ Results saved to: {output_file}")
    
    # Show discovered URLs
    if results['results']:
        print("\n🎯 Discovered URLs:")
        for item in results['results'][:5]:
            account_name = item['account']['name']
            print(f"\n  {account_name}:")
            for platform, data in item['discovered_urls'].items():
                print(f"    - {platform}: {data['url']}")
                if data.get('followers'):
                    print(f"      Followers: {data['followers']:,}")


if __name__ == "__main__":
    asyncio.run(main())