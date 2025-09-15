"""
Fixed complete verification - properly processes all accounts without repetition
"""

import yaml
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple
import re
import time

# Add parent directories to path for cross-directory imports
sys.path.append(str(Path(__file__).parent.parent / "data-processing"))

from spanish_links_verifier import DatasetVerifier, Platform, VerificationStatus
from pattern_url_discovery import SpanishPatternGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FixedCompleteVerificationProcessor:
    """
    Fixed version that properly processes all accounts without repetition
    """
    
    def __init__(self, yaml_file: str):
        self.yaml_file = Path(yaml_file)
        self.yaml_data = None
        self.pattern_generator = SpanishPatternGenerator()
        self.verifier = DatasetVerifier()
        
        # Track what needs processing
        self.unverified_urls = []  # List of URLs to verify
        self.accounts_missing_youtube = []
        
        # Results tracking
        self.verification_results = {}
        self.discovered_youtube_urls = {}
        
        # Statistics
        self.stats = {
            'total_accounts': 0,
            'unverified_count': 0,
            'missing_youtube_count': 0,
            'urls_verified': 0,
            'urls_found_active': 0,
            'youtube_urls_discovered': 0,
            'instagram_verified': 0,
            'errors': 0
        }
        
        # Load YAML
        self.load_yaml()
    
    def load_yaml(self):
        """Load and analyze YAML file"""
        logger.info(f"Loading YAML from {self.yaml_file}")
        
        with open(self.yaml_file, 'r', encoding='utf-8') as f:
            self.yaml_data = yaml.safe_load(f)
        
        # Analyze what needs processing - FIXED to avoid duplicates
        seen_urls = set()
        
        for i, account in enumerate(self.yaml_data.get('accounts', [])):
            if not account:
                continue
            
            self.stats['total_accounts'] += 1
            
            # Check Instagram URL
            if account.get('instagram_url') and not account.get('instagram_verified'):
                url = account['instagram_url']
                if url not in seen_urls:
                    self.unverified_urls.append({
                        'url': url,
                        'index': i,
                        'platform': 'instagram',
                        'account_name': account.get('name', 'Unknown')
                    })
                    seen_urls.add(url)
                    self.stats['unverified_count'] += 1
            
            # Check YouTube URL  
            if account.get('youtube_url') and not account.get('youtube_verified'):
                url = account['youtube_url']
                if url not in seen_urls:
                    self.unverified_urls.append({
                        'url': url,
                        'index': i,
                        'platform': 'youtube',
                        'account_name': account.get('name', 'Unknown')
                    })
                    seen_urls.add(url)
                    self.stats['unverified_count'] += 1
            
            # Missing YouTube URL
            if not account.get('youtube_url'):
                self.accounts_missing_youtube.append({
                    'index': i,
                    'account': account
                })
                self.stats['missing_youtube_count'] += 1
        
        logger.info(f"Analysis complete:")
        logger.info(f"  - Total accounts: {self.stats['total_accounts']}")
        logger.info(f"  - Unique unverified URLs: {len(self.unverified_urls)}")
        logger.info(f"  - Missing YouTube: {self.stats['missing_youtube_count']}")
    
    async def verify_all_urls(self):
        """
        Verify all unverified URLs without repetition
        """
        total_urls = len(self.unverified_urls)
        logger.info(f"Starting verification of {total_urls} unique URLs")
        
        if total_urls == 0:
            logger.info("No URLs to verify")
            return
        
        batch_size = 10
        
        for batch_start in range(0, total_urls, batch_size):
            batch_end = min(batch_start + batch_size, total_urls)
            batch = self.unverified_urls[batch_start:batch_end]
            
            logger.info(f"Processing batch {batch_start//batch_size + 1}/{(total_urls + batch_size - 1)//batch_size}")
            logger.info(f"  URLs {batch_start+1}-{batch_end} of {total_urls}")
            
            # Extract just URLs for verification
            batch_urls = [item['url'] for item in batch]
            
            try:
                # Verify this batch of URLs
                results = await self.verifier.verify_and_enrich(
                    batch_urls,
                    batch_size=5
                )
                
                # Process results
                for j, result in enumerate(results):
                    if j < len(batch):
                        item = batch[j]
                        
                        # Store result
                        if item['index'] not in self.verification_results:
                            self.verification_results[item['index']] = {}
                        
                        self.verification_results[item['index']][item['platform']] = {
                            'url': result.url,
                            'status': result.verification_status.value,
                            'is_active': result.verification_status == VerificationStatus.ACTIVE,
                            'follower_count': result.follower_count
                        }
                        
                        self.stats['urls_verified'] += 1
                        
                        if result.verification_status == VerificationStatus.ACTIVE:
                            self.stats['urls_found_active'] += 1
                            logger.info(f"  ✓ {item['account_name']}: {item['platform']} ACTIVE")
                        else:
                            logger.info(f"  ✗ {item['account_name']}: {item['platform']} {result.verification_status.value}")
            
            except Exception as e:
                logger.error(f"Error in batch: {e}")
                self.stats['errors'] += 1
            
            # Rate limiting between batches
            if batch_end < total_urls:
                logger.info("Pausing 15 seconds for rate limiting...")
                await asyncio.sleep(15)
        
        logger.info(f"Verification complete: {self.stats['urls_verified']} URLs processed")
    
    async def discover_missing_youtube_urls(self):
        """
        Discover YouTube URLs for accounts missing them
        """
        total_missing = len(self.accounts_missing_youtube)
        logger.info(f"Discovering YouTube URLs for {total_missing} accounts")
        
        if total_missing == 0:
            logger.info("No missing YouTube URLs to find")
            return
        
        batch_size = 5
        discovered_count = 0
        
        for batch_start in range(0, total_missing, batch_size):
            batch_end = min(batch_start + batch_size, total_missing)
            batch = self.accounts_missing_youtube[batch_start:batch_end]
            
            logger.info(f"YouTube discovery batch {batch_start//batch_size + 1}: accounts {batch_start+1}-{batch_end}")
            
            for item in batch:
                account = item['account']
                account_name = account.get('name', 'Unknown')
                
                # Generate YouTube patterns
                patterns = self.pattern_generator.generate_youtube_patterns(account)[:3]
                
                if not patterns:
                    logger.info(f"  No patterns for {account_name}")
                    continue
                
                urls_to_try = [url for url, _ in patterns]
                
                try:
                    # Verify generated URLs
                    results = await self.verifier.verify_and_enrich(urls_to_try, batch_size=3)
                    
                    # Find first active URL
                    for j, result in enumerate(results):
                        if result.verification_status == VerificationStatus.ACTIVE:
                            self.discovered_youtube_urls[item['index']] = {
                                'url': result.url,
                                'confidence': patterns[j][1] if j < len(patterns) else 0.5,
                                'verified': True
                            }
                            discovered_count += 1
                            self.stats['youtube_urls_discovered'] += 1
                            logger.info(f"  ✓ Found YouTube for {account_name}: {result.url}")
                            break
                    else:
                        logger.info(f"  ✗ No YouTube found for {account_name}")
                
                except Exception as e:
                    logger.error(f"  Error for {account_name}: {e}")
                    self.stats['errors'] += 1
                
                # Small pause between accounts
                await asyncio.sleep(2)
            
            # Longer pause between batches
            if batch_end < total_missing:
                logger.info("Pausing 20 seconds between YouTube batches...")
                await asyncio.sleep(20)
        
        logger.info(f"YouTube discovery complete: found {discovered_count} channels")
    
    def update_yaml_with_results(self):
        """Update YAML with all results"""
        logger.info("Updating YAML with results")
        updates = 0
        
        # Update verification results
        for idx, platforms in self.verification_results.items():
            account = self.yaml_data['accounts'][idx]
            
            for platform, result in platforms.items():
                if result['is_active']:
                    if platform == 'instagram':
                        account['instagram_verified'] = True
                        if result.get('follower_count'):
                            account['instagram_followers'] = result['follower_count']
                    elif platform == 'youtube':
                        account['youtube_verified'] = True
                        if result.get('follower_count'):
                            account['youtube_subscribers'] = result['follower_count']
                    updates += 1
                else:
                    # Mark status for inactive/not found
                    if platform == 'instagram':
                        account['instagram_status'] = result['status']
                    elif platform == 'youtube':
                        account['youtube_status'] = result['status']
            
            account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
        
        # Add discovered YouTube URLs
        for idx, youtube_data in self.discovered_youtube_urls.items():
            account = self.yaml_data['accounts'][idx]
            account['youtube_url'] = youtube_data['url']
            account['youtube_verified'] = True
            account['youtube_discovered'] = True
            account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
            updates += 1
        
        logger.info(f"Made {updates} updates")
        return updates
    
    def save_yaml(self):
        """Save updated YAML"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.yaml_file.parent / f"{self.yaml_file.stem}_backup_{timestamp}.yml"
        
        # Create backup
        with open(backup_file, 'w', encoding='utf-8') as f:
            with open(self.yaml_file, 'r', encoding='utf-8') as orig:
                f.write(orig.read())
        logger.info(f"Backup created: {backup_file}")
        
        # Save updated YAML
        with open(self.yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.yaml_data, f,
                     default_flow_style=False,
                     allow_unicode=True,
                     sort_keys=False,
                     width=1000)
        logger.info(f"YAML updated: {self.yaml_file}")


async def main():
    """Main execution"""
    yaml_file = r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml"
    
    print("\n🚀 FIXED COMPLETE VERIFICATION")
    print("="*60)
    
    processor = FixedCompleteVerificationProcessor(yaml_file)
    
    print(f"\n📊 Scope:")
    print(f"  - Unique URLs to verify: {len(processor.unverified_urls)}")
    print(f"  - Missing YouTube URLs: {processor.stats['missing_youtube_count']}")
    
    start_time = datetime.now()
    
    # Phase 1: Verify all URLs
    print("\n📍 Phase 1: Verifying all unverified URLs...")
    await processor.verify_all_urls()
    
    print(f"\n✅ Phase 1 complete: {processor.stats['urls_verified']} verified, {processor.stats['urls_found_active']} active")
    
    # Phase 2: Discover YouTube URLs
    print("\n📍 Phase 2: Discovering missing YouTube URLs...")
    await processor.discover_missing_youtube_urls()
    
    print(f"\n✅ Phase 2 complete: {processor.stats['youtube_urls_discovered']} YouTube URLs found")
    
    # Save results
    print("\n💾 Saving results...")
    updates = processor.update_yaml_with_results()
    
    if updates > 0:
        processor.save_yaml()
        print(f"✅ Saved {updates} updates to YAML")
    
    elapsed = datetime.now() - start_time
    print(f"\n⏱️ Total time: {elapsed}")
    print(f"\n📊 Final statistics:")
    print(f"  - URLs verified: {processor.stats['urls_verified']}")
    print(f"  - Active URLs: {processor.stats['urls_found_active']}")
    print(f"  - YouTube discovered: {processor.stats['youtube_urls_discovered']}")
    print(f"  - Errors: {processor.stats['errors']}")
    
    print("\n✨ Complete!")


if __name__ == "__main__":
    asyncio.run(main())