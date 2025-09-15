"""
Enrich YAML accounts with discovered social media URLs using open-source search
"""

import asyncio
import yaml
import json
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent))

# Add parent directories to path for cross-directory imports
sys.path.append(str(Path(__file__).parent.parent / "verification"))

from opensearch_enrichment import EnrichmentPipeline, OpenSearchEnricher, AccountMatcher
from spanish_links_verifier import DatasetVerifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class YAMLEnrichmentProcessor:
    """
    Process YAML accounts and discover missing social media URLs
    """
    
    def __init__(self, yaml_file: str, output_dir: str = None):
        self.yaml_file = Path(yaml_file)
        self.output_dir = Path(output_dir) if output_dir else self.yaml_file.parent / "enrichment_results"
        self.output_dir.mkdir(exist_ok=True)
        
        self.accounts = []
        self.enrichment_results = []
        self.discovery_stats = {
            'total_accounts': 0,
            'accounts_missing_instagram': 0,
            'accounts_missing_youtube': 0,
            'new_instagram_found': 0,
            'new_youtube_found': 0,
            'new_twitter_found': 0,
            'new_websites_found': 0,
            'total_new_urls': 0
        }
    
    def load_yaml(self) -> List[Dict]:
        """Load accounts from YAML file"""
        logger.info(f"Loading YAML file: {self.yaml_file}")
        
        with open(self.yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        accounts = []
        if 'accounts' in data:
            for account in data['accounts']:
                if account:
                    # Check what's missing
                    has_instagram = 'instagram_url' in account and account['instagram_url']
                    has_youtube = 'youtube_url' in account and account['youtube_url']
                    
                    account_data = {
                        'handle': account.get('handle', ''),
                        'name': account.get('name', ''),
                        'category': account.get('category', ''),
                        'description': account.get('description', ''),
                        'existing_instagram': account.get('instagram_url'),
                        'existing_youtube': account.get('youtube_url'),
                        'needs_instagram': not has_instagram,
                        'needs_youtube': not has_youtube,
                        'needs_enrichment': not has_instagram or not has_youtube
                    }
                    
                    accounts.append(account_data)
                    
                    if not has_instagram:
                        self.discovery_stats['accounts_missing_instagram'] += 1
                    if not has_youtube:
                        self.discovery_stats['accounts_missing_youtube'] += 1
        
        self.discovery_stats['total_accounts'] = len(accounts)
        logger.info(f"Loaded {len(accounts)} accounts")
        logger.info(f"  - Missing Instagram: {self.discovery_stats['accounts_missing_instagram']}")
        logger.info(f"  - Missing YouTube: {self.discovery_stats['accounts_missing_youtube']}")
        
        return accounts
    
    async def discover_missing_urls(self, accounts: List[Dict], max_accounts: int = None) -> List[Dict]:
        """
        Discover missing social media URLs for accounts
        """
        # Filter to only accounts that need enrichment
        accounts_to_enrich = [acc for acc in accounts if acc.get('needs_enrichment')]
        
        if max_accounts:
            accounts_to_enrich = accounts_to_enrich[:max_accounts]
        
        logger.info(f"Starting URL discovery for {len(accounts_to_enrich)} accounts")
        
        enriched_accounts = []
        
        async with OpenSearchEnricher() as enricher:
            for i, account in enumerate(accounts_to_enrich):
                logger.info(f"Processing {i+1}/{len(accounts_to_enrich)}: {account['name']}")
                
                # Build targeted search queries
                queries = []
                
                # If missing Instagram
                if account['needs_instagram']:
                    if account['name']:
                        queries.append(f'"{account["name"]}" site:instagram.com')
                        queries.append(f'"{account["name"]}" instagram oficial')
                    if account['handle']:
                        handle = account['handle'].replace('@', '')
                        queries.append(f'"{handle}" instagram')
                
                # If missing YouTube
                if account['needs_youtube']:
                    if account['name']:
                        queries.append(f'"{account["name"]}" site:youtube.com')
                        queries.append(f'"{account["name"]}" youtube channel')
                    if account['handle']:
                        handle = account['handle'].replace('@', '')
                        queries.append(f'"{handle}" youtube')
                
                # Also search for general social media presence
                if account['name']:
                    queries.append(f'"{account["name"]}" redes sociales')
                
                # Perform searches
                discovered_urls = {
                    'instagram': [],
                    'youtube': [],
                    'twitter': [],
                    'facebook': [],
                    'tiktok': [],
                    'websites': []
                }
                
                for query in queries[:3]:  # Limit queries per account
                    try:
                        results = await enricher.aggregate_search(query)
                        
                        for platform, urls in results.items():
                            for url in urls:
                                # Calculate match confidence
                                confidence = AccountMatcher.match_url_to_account(url, account)
                                
                                if confidence >= 0.5:  # Lower threshold for discovery
                                    url_data = {
                                        'url': url,
                                        'confidence': confidence,
                                        'query': query
                                    }
                                    
                                    if url_data not in discovered_urls[platform]:
                                        discovered_urls[platform].append(url_data)
                    
                    except Exception as e:
                        logger.error(f"Search error for {account['name']}: {e}")
                    
                    # Small delay between searches
                    await asyncio.sleep(1)
                
                # Process discoveries
                enriched_account = account.copy()
                enriched_account['discovered_urls'] = {}
                
                # Check Instagram discoveries
                if account['needs_instagram'] and discovered_urls['instagram']:
                    best_instagram = max(discovered_urls['instagram'], key=lambda x: x['confidence'])
                    if best_instagram['confidence'] >= 0.6:
                        enriched_account['discovered_urls']['instagram'] = best_instagram
                        self.discovery_stats['new_instagram_found'] += 1
                        self.discovery_stats['total_new_urls'] += 1
                        logger.info(f"  ✓ Found Instagram: {best_instagram['url']} (confidence: {best_instagram['confidence']:.2f})")
                
                # Check YouTube discoveries
                if account['needs_youtube'] and discovered_urls['youtube']:
                    best_youtube = max(discovered_urls['youtube'], key=lambda x: x['confidence'])
                    if best_youtube['confidence'] >= 0.6:
                        enriched_account['discovered_urls']['youtube'] = best_youtube
                        self.discovery_stats['new_youtube_found'] += 1
                        self.discovery_stats['total_new_urls'] += 1
                        logger.info(f"  ✓ Found YouTube: {best_youtube['url']} (confidence: {best_youtube['confidence']:.2f})")
                
                # Bonus: Check for other platforms
                if discovered_urls['twitter']:
                    best_twitter = max(discovered_urls['twitter'], key=lambda x: x['confidence'])
                    if best_twitter['confidence'] >= 0.7:
                        enriched_account['discovered_urls']['twitter'] = best_twitter
                        self.discovery_stats['new_twitter_found'] += 1
                        self.discovery_stats['total_new_urls'] += 1
                
                if discovered_urls['websites']:
                    for website_data in discovered_urls['websites'][:3]:
                        if website_data['confidence'] >= 0.5:
                            if 'websites' not in enriched_account['discovered_urls']:
                                enriched_account['discovered_urls']['websites'] = []
                            enriched_account['discovered_urls']['websites'].append(website_data)
                            self.discovery_stats['new_websites_found'] += 1
                            self.discovery_stats['total_new_urls'] += 1
                
                enriched_account['enrichment_timestamp'] = datetime.now().isoformat()
                enriched_accounts.append(enriched_account)
                
                # Rate limiting
                if i % 5 == 4:
                    logger.info("Pausing for rate limiting...")
                    await asyncio.sleep(5)
        
        return enriched_accounts
    
    async def verify_discovered_urls(self, enriched_accounts: List[Dict]) -> List[Dict]:
        """
        Verify discovered URLs to confirm they're active
        """
        logger.info("Verifying discovered URLs...")
        
        verifier = DatasetVerifier()
        urls_to_verify = []
        url_mapping = {}
        
        # Collect all discovered URLs
        for account in enriched_accounts:
            if 'discovered_urls' in account:
                for platform, data in account['discovered_urls'].items():
                    if platform == 'websites' and isinstance(data, list):
                        for website in data:
                            urls_to_verify.append(website['url'])
                            url_mapping[website['url']] = (account['name'], platform)
                    elif isinstance(data, dict) and 'url' in data:
                        urls_to_verify.append(data['url'])
                        url_mapping[data['url']] = (account['name'], platform)
        
        if urls_to_verify:
            logger.info(f"Verifying {len(urls_to_verify)} discovered URLs")
            
            # Verify in small batches
            verification_results = await verifier.verify_and_enrich(
                urls_to_verify[:20],  # Limit to avoid rate limits
                batch_size=5
            )
            
            # Add verification status to accounts
            for result in verification_results:
                if result.url in url_mapping:
                    account_name, platform = url_mapping[result.url]
                    
                    # Find the account and update verification status
                    for account in enriched_accounts:
                        if account['name'] == account_name:
                            if 'discovered_urls' in account:
                                if platform in account['discovered_urls']:
                                    if isinstance(account['discovered_urls'][platform], dict):
                                        account['discovered_urls'][platform]['verified'] = result.verification_status.value
                                        account['discovered_urls'][platform]['is_active'] = result.verification_status.value == 'active'
        
        return enriched_accounts
    
    def save_results(self, enriched_accounts: List[Dict]):
        """
        Save enrichment results to multiple formats
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed JSON report
        json_file = self.output_dir / f"enriched_accounts_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'source_file': str(self.yaml_file),
                    'processed_at': datetime.now().isoformat(),
                    'statistics': self.discovery_stats
                },
                'accounts': enriched_accounts
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Results saved to: {json_file}")
        
        # Save discovered URLs in simple format
        discovered_file = self.output_dir / f"discovered_urls_{timestamp}.txt"
        with open(discovered_file, 'w', encoding='utf-8') as f:
            f.write("DISCOVERED SOCIAL MEDIA URLs\n")
            f.write("="*50 + "\n\n")
            
            for account in enriched_accounts:
                if 'discovered_urls' in account and account['discovered_urls']:
                    f.write(f"{account['name']} ({account['handle']})\n")
                    f.write(f"Category: {account['category']}\n")
                    
                    for platform, data in account['discovered_urls'].items():
                        if platform == 'websites' and isinstance(data, list):
                            for website in data:
                                f.write(f"  - Website: {website['url']} (confidence: {website['confidence']:.2f})\n")
                        elif isinstance(data, dict):
                            verified = data.get('verified', 'not_verified')
                            f.write(f"  - {platform.title()}: {data['url']} (confidence: {data['confidence']:.2f}, status: {verified})\n")
                    
                    f.write("\n")
        
        logger.info(f"Discovered URLs saved to: {discovered_file}")
        
        return json_file, discovered_file
    
    def print_summary(self):
        """
        Print discovery summary
        """
        print("\n" + "="*70)
        print("URL DISCOVERY SUMMARY")
        print("="*70)
        
        print(f"\nAccounts Processed: {self.discovery_stats['total_accounts']}")
        print(f"Accounts Missing Instagram: {self.discovery_stats['accounts_missing_instagram']}")
        print(f"Accounts Missing YouTube: {self.discovery_stats['accounts_missing_youtube']}")
        
        print(f"\n✅ DISCOVERIES:")
        print(f"  New Instagram URLs: {self.discovery_stats['new_instagram_found']}")
        print(f"  New YouTube URLs: {self.discovery_stats['new_youtube_found']}")
        print(f"  New Twitter URLs: {self.discovery_stats['new_twitter_found']}")
        print(f"  New Websites: {self.discovery_stats['new_websites_found']}")
        print(f"  Total New URLs: {self.discovery_stats['total_new_urls']}")
        
        if self.discovery_stats['accounts_missing_instagram'] > 0:
            instagram_success = (self.discovery_stats['new_instagram_found'] / 
                               self.discovery_stats['accounts_missing_instagram']) * 100
            print(f"\nInstagram Discovery Rate: {instagram_success:.1f}%")
        
        if self.discovery_stats['accounts_missing_youtube'] > 0:
            youtube_success = (self.discovery_stats['new_youtube_found'] / 
                             self.discovery_stats['accounts_missing_youtube']) * 100
            print(f"YouTube Discovery Rate: {youtube_success:.1f}%")
        
        print("="*70)


async def main():
    """
    Main execution
    """
    yaml_file = r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml"
    output_dir = r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\enrichment_results"
    
    print("\n🔍 Spanish Accounts URL Discovery System")
    print("="*50)
    print("Using open-source search to find missing social media URLs")
    print("="*50)
    
    processor = YAMLEnrichmentProcessor(yaml_file, output_dir)
    
    # Load accounts
    accounts = processor.load_yaml()
    
    # Filter to accounts that need enrichment
    accounts_needing_urls = [acc for acc in accounts if acc['needs_enrichment']]
    
    print(f"\n📊 Found {len(accounts_needing_urls)} accounts needing URL discovery")
    print("⚠️  Note: This process will use DuckDuckGo and Searx for discovery")
    print("    Processing first 10 accounts as demonstration...")
    
    # Discover missing URLs (limit to 10 for demo)
    enriched_accounts = await processor.discover_missing_urls(accounts, max_accounts=10)
    
    # Verify discovered URLs
    enriched_accounts = await processor.verify_discovered_urls(enriched_accounts)
    
    # Save results
    json_file, txt_file = processor.save_results(enriched_accounts)
    
    # Print summary
    processor.print_summary()
    
    print(f"\n📁 Results saved to:")
    print(f"  - {json_file}")
    print(f"  - {txt_file}")


if __name__ == "__main__":
    # Install required package
    print("\n📦 Checking dependencies...")
    try:
        import bs4
    except ImportError:
        print("Installing beautifulsoup4...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
    
    asyncio.run(main())