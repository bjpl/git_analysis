"""
Complete verification and YouTube URL discovery for remaining accounts
Handles rate limiting carefully and processes in small batches
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


class CompleteVerificationProcessor:
    """
    Carefully process remaining unverified accounts and find missing YouTube URLs
    """
    
    def __init__(self, yaml_file: str):
        self.yaml_file = Path(yaml_file)
        self.yaml_data = None
        self.pattern_generator = SpanishPatternGenerator()
        self.verifier = DatasetVerifier()
        
        # Track what needs processing
        self.unverified_accounts = []
        self.accounts_missing_youtube = []
        self.urls_to_verify = []
        
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
        
        # Analyze what needs processing
        for i, account in enumerate(self.yaml_data.get('accounts', [])):
            if not account:
                continue
            
            self.stats['total_accounts'] += 1
            
            # Check if account needs verification
            needs_verification = False
            
            # Instagram URL exists but not verified
            if account.get('instagram_url') and not account.get('instagram_verified'):
                needs_verification = True
                self.unverified_accounts.append({
                    'index': i,
                    'account': account,
                    'platform': 'instagram',
                    'url': account['instagram_url']
                })
            
            # YouTube URL exists but not verified
            if account.get('youtube_url') and not account.get('youtube_verified'):
                needs_verification = True
                self.unverified_accounts.append({
                    'index': i,
                    'account': account,
                    'platform': 'youtube',
                    'url': account['youtube_url']
                })
            
            # Missing YouTube URL
            if not account.get('youtube_url'):
                self.accounts_missing_youtube.append({
                    'index': i,
                    'account': account
                })
                self.stats['missing_youtube_count'] += 1
            
            if needs_verification:
                self.stats['unverified_count'] += 1
        
        logger.info(f"Analysis complete:")
        logger.info(f"  - Total accounts: {self.stats['total_accounts']}")
        logger.info(f"  - Unverified URLs: {len(self.unverified_accounts)}")
        logger.info(f"  - Missing YouTube: {self.stats['missing_youtube_count']}")
    
    async def verify_existing_urls(self, batch_size: int = 10, max_urls: int = None):
        """
        Verify existing but unverified URLs
        """
        logger.info(f"Starting verification of {len(self.unverified_accounts)} unverified URLs")
        
        # Limit processing if requested
        urls_to_process = self.unverified_accounts
        if max_urls:
            urls_to_process = urls_to_process[:max_urls]
        
        # Process in batches
        for i in range(0, len(urls_to_process), batch_size):
            batch = urls_to_process[i:i + batch_size]
            
            # Extract URLs for verification
            batch_urls = [item['url'] for item in batch]
            
            logger.info(f"Verifying batch {i//batch_size + 1}/{(len(urls_to_process) + batch_size - 1)//batch_size}")
            
            try:
                # Verify URLs
                results = await self.verifier.verify_and_enrich(
                    batch_urls,
                    batch_size=min(5, batch_size)  # Smaller internal batch for rate limiting
                )
                
                # Store results
                for j, result in enumerate(results):
                    if j < len(batch):
                        item = batch[j]
                        account_index = item['index']
                        platform = item['platform']
                        
                        # Store verification result
                        if account_index not in self.verification_results:
                            self.verification_results[account_index] = {}
                        
                        self.verification_results[account_index][platform] = {
                            'url': result.url,
                            'status': result.verification_status.value,
                            'is_active': result.verification_status == VerificationStatus.ACTIVE,
                            'follower_count': result.follower_count,
                            'display_name': result.display_name,
                            'bio': result.bio
                        }
                        
                        self.stats['urls_verified'] += 1
                        if result.verification_status == VerificationStatus.ACTIVE:
                            self.stats['urls_found_active'] += 1
                            logger.info(f"  ✓ Verified: {result.url} - ACTIVE")
                        else:
                            logger.warning(f"  ✗ Verified: {result.url} - {result.verification_status.value}")
            
            except Exception as e:
                logger.error(f"Error verifying batch: {e}")
                self.stats['errors'] += 1
            
            # Rate limiting between batches
            if i + batch_size < len(urls_to_process):
                logger.info("Pausing for rate limiting (10 seconds)...")
                await asyncio.sleep(10)
    
    async def discover_missing_youtube_urls(self, max_accounts: int = None):
        """
        Generate and verify YouTube URLs for accounts missing them
        """
        logger.info(f"Discovering YouTube URLs for {len(self.accounts_missing_youtube)} accounts")
        
        accounts_to_process = self.accounts_missing_youtube
        if max_accounts:
            accounts_to_process = accounts_to_process[:max_accounts]
        
        discovered_count = 0
        
        for i, item in enumerate(accounts_to_process):
            account = item['account']
            account_index = item['index']
            
            logger.info(f"Processing {i+1}/{len(accounts_to_process)}: {account.get('name', 'Unknown')}")
            
            # Generate YouTube URL patterns
            youtube_patterns = self.pattern_generator.generate_youtube_patterns(account)
            
            if not youtube_patterns:
                logger.warning(f"  No patterns generated for {account.get('name')}")
                continue
            
            # Verify patterns (limit to top 5)
            patterns_to_verify = youtube_patterns[:5]
            urls_to_verify = [url for url, _ in patterns_to_verify]
            
            try:
                # Verify generated URLs
                results = await self.verifier.verify_and_enrich(
                    urls_to_verify,
                    batch_size=5
                )
                
                # Find first active URL
                for j, result in enumerate(results):
                    if result.verification_status == VerificationStatus.ACTIVE:
                        # Found active YouTube channel!
                        confidence = patterns_to_verify[j][1] if j < len(patterns_to_verify) else 0.5
                        
                        self.discovered_youtube_urls[account_index] = {
                            'url': result.url,
                            'confidence': confidence,
                            'follower_count': result.follower_count,
                            'display_name': result.display_name,
                            'verified': True
                        }
                        
                        discovered_count += 1
                        self.stats['youtube_urls_discovered'] += 1
                        
                        logger.info(f"  ✓ FOUND YouTube: {result.url} (confidence: {confidence:.2f})")
                        break
                else:
                    logger.info(f"  ✗ No active YouTube URL found")
            
            except Exception as e:
                logger.error(f"  Error discovering YouTube for {account.get('name')}: {e}")
                self.stats['errors'] += 1
            
            # Rate limiting between accounts
            if (i + 1) % 5 == 0 and i + 1 < len(accounts_to_process):
                logger.info("Pausing for rate limiting (15 seconds)...")
                await asyncio.sleep(15)
        
        logger.info(f"Discovered {discovered_count} new YouTube URLs")
    
    def update_yaml_with_results(self):
        """
        Update YAML file with verification results and discovered URLs
        """
        logger.info("Updating YAML with new results")
        
        updates_made = 0
        
        # Update verification results
        for account_index, platforms in self.verification_results.items():
            account = self.yaml_data['accounts'][account_index]
            
            for platform, result in platforms.items():
                if result['is_active']:
                    # Mark as verified
                    if platform == 'instagram':
                        account['instagram_verified'] = True
                        if result.get('follower_count'):
                            account['instagram_followers'] = result['follower_count']
                        updates_made += 1
                    elif platform == 'youtube':
                        account['youtube_verified'] = True
                        if result.get('follower_count'):
                            account['youtube_subscribers'] = result['follower_count']
                        updates_made += 1
                else:
                    # Mark as inactive/not found
                    if platform == 'instagram':
                        account['instagram_status'] = result['status']
                    elif platform == 'youtube':
                        account['youtube_status'] = result['status']
            
            # Add last updated timestamp
            account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
        
        # Add discovered YouTube URLs
        for account_index, youtube_data in self.discovered_youtube_urls.items():
            account = self.yaml_data['accounts'][account_index]
            
            # Add YouTube URL
            account['youtube_url'] = youtube_data['url']
            account['youtube_verified'] = youtube_data['verified']
            account['youtube_discovery_confidence'] = youtube_data['confidence']
            
            if youtube_data.get('follower_count'):
                account['youtube_subscribers'] = youtube_data['follower_count']
            
            account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
            updates_made += 1
        
        logger.info(f"Made {updates_made} updates to accounts")
        
        return updates_made
    
    def save_yaml(self):
        """
        Save updated YAML with backup
        """
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.yaml_file.parent / f"{self.yaml_file.stem}_backup_{timestamp}.yml"
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            with open(self.yaml_file, 'r', encoding='utf-8') as orig:
                f.write(orig.read())
        
        logger.info(f"Created backup: {backup_file}")
        
        # Save updated YAML
        with open(self.yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.yaml_data, f,
                     default_flow_style=False,
                     allow_unicode=True,
                     sort_keys=False,
                     width=1000)
        
        logger.info(f"Updated YAML saved to: {self.yaml_file}")
    
    def generate_report(self) -> str:
        """
        Generate processing report
        """
        report = []
        report.append("="*70)
        report.append("COMPLETE VERIFICATION REPORT")
        report.append("="*70)
        report.append(f"Processed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        report.append(f"\n📊 STATISTICS:")
        report.append(f"  Total accounts: {self.stats['total_accounts']}")
        report.append(f"  URLs verified: {self.stats['urls_verified']}")
        report.append(f"  Active URLs found: {self.stats['urls_found_active']}")
        report.append(f"  YouTube URLs discovered: {self.stats['youtube_urls_discovered']}")
        
        if self.stats['urls_verified'] > 0:
            success_rate = (self.stats['urls_found_active'] / self.stats['urls_verified']) * 100
            report.append(f"  Verification success rate: {success_rate:.1f}%")
        
        if self.stats['errors'] > 0:
            report.append(f"  Errors encountered: {self.stats['errors']}")
        
        # Calculate new completion rates
        instagram_complete = sum(1 for acc in self.yaml_data['accounts'] 
                                if acc and acc.get('instagram_verified'))
        youtube_complete = sum(1 for acc in self.yaml_data['accounts'] 
                              if acc and acc.get('youtube_url'))
        
        report.append(f"\n📈 COMPLETION RATES:")
        report.append(f"  Instagram verified: {instagram_complete}/{self.stats['total_accounts']} "
                     f"({instagram_complete/self.stats['total_accounts']*100:.1f}%)")
        report.append(f"  YouTube URLs: {youtube_complete}/{self.stats['total_accounts']} "
                     f"({youtube_complete/self.stats['total_accounts']*100:.1f}%)")
        
        report.append("\n" + "="*70)
        
        return "\n".join(report)


async def main():
    """
    Main execution - carefully process remaining accounts
    """
    yaml_file = r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml"
    
    print("\n🔍 Complete Verification & YouTube Discovery")
    print("="*60)
    print("Processing remaining unverified accounts and finding YouTube URLs")
    print("="*60)
    
    processor = CompleteVerificationProcessor(yaml_file)
    
    print(f"\n📊 Current Status:")
    print(f"  - Unverified URLs: {len(processor.unverified_accounts)}")
    print(f"  - Missing YouTube: {processor.stats['missing_youtube_count']}")
    
    print("\n⚠️  IMPORTANT:")
    print("  - This will make many API requests")
    print("  - Rate limiting will cause pauses")
    print("  - Processing in small batches to avoid blocks")
    print("  - Estimated time: 30-60 minutes")
    
    response = input("\nProceed with verification? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("Verification cancelled")
        return
    
    # Phase 1: Verify existing unverified URLs (limit to 50 for safety)
    print("\n📍 Phase 1: Verifying existing URLs...")
    await processor.verify_existing_urls(batch_size=10, max_urls=50)
    
    # Phase 2: Discover missing YouTube URLs (limit to 30 for safety)
    print("\n📍 Phase 2: Discovering missing YouTube URLs...")
    await processor.discover_missing_youtube_urls(max_accounts=30)
    
    # Update YAML with results
    print("\n💾 Updating YAML with results...")
    updates = processor.update_yaml_with_results()
    
    if updates > 0:
        processor.save_yaml()
        print(f"✅ Successfully updated {updates} accounts")
    else:
        print("ℹ️  No updates to save")
    
    # Generate and display report
    report = processor.generate_report()
    print("\n" + report)
    
    # Save report
    report_file = Path(yaml_file).parent / f"verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())