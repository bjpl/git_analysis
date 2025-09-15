"""
Update YAML data with all verification and discovery results
Merges verified URLs, discovered URLs, and cleans the data
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YAMLDataUpdater:
    """
    Updates YAML accounts data with verification and discovery results
    """
    
    def __init__(self, yaml_file: str):
        self.yaml_file = Path(yaml_file)
        self.yaml_data = None
        self.accounts_by_handle = {}
        self.accounts_by_name = {}
        
        # Statistics
        self.stats = {
            'total_accounts': 0,
            'urls_added': 0,
            'urls_verified': 0,
            'urls_removed': 0,
            'accounts_updated': 0,
            'instagram_added': 0,
            'youtube_added': 0,
            'twitter_added': 0,
            'websites_added': 0,
            'verification_status_added': 0
        }
        
        # Load original YAML
        self.load_yaml()
    
    def load_yaml(self):
        """Load original YAML file"""
        logger.info(f"Loading original YAML from {self.yaml_file}")
        
        with open(self.yaml_file, 'r', encoding='utf-8') as f:
            self.yaml_data = yaml.safe_load(f)
        
        # Create lookup dictionaries
        if 'accounts' in self.yaml_data:
            for i, account in enumerate(self.yaml_data['accounts']):
                if account:
                    self.stats['total_accounts'] += 1
                    
                    # Index by handle
                    if account.get('handle'):
                        handle = account['handle'].lower()
                        self.accounts_by_handle[handle] = i
                    
                    # Index by name
                    if account.get('name'):
                        name = account['name'].lower()
                        self.accounts_by_name[name] = i
    
    def load_verification_results(self, results_dir: str) -> Dict:
        """Load all verification result files"""
        results_path = Path(results_dir)
        all_results = {}
        
        # Load verification results
        for json_file in results_path.glob("*.json"):
            logger.info(f"Loading results from {json_file.name}")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Process different result formats
                if 'results' in data:
                    # Verification results format
                    for result in data['results']:
                        # Create a key for matching
                        if 'account_name' in result:
                            key = result['account_name'].lower()
                        elif 'name' in result:
                            key = result['name'].lower()
                        else:
                            continue
                        
                        if key not in all_results:
                            all_results[key] = {}
                        
                        # Store platform-specific data
                        platform = result.get('platform', '')
                        if platform and result.get('url'):
                            all_results[key][platform] = {
                                'url': result['url'],
                                'verification_status': result.get('verification_status', 'unknown'),
                                'follower_count': result.get('follower_count'),
                                'is_active': result.get('verification_status') == 'active',
                                'verified_date': data.get('metadata', {}).get('processed_at')
                            }
                
                # Pattern discovery results format
                elif 'results' in data and isinstance(data['results'], list):
                    for item in data['results']:
                        if 'account' in item and 'discovered_urls' in item:
                            account = item['account']
                            key = account.get('name', '').lower()
                            
                            if key and key not in all_results:
                                all_results[key] = {}
                            
                            for platform, url_data in item['discovered_urls'].items():
                                if isinstance(url_data, dict) and url_data.get('url'):
                                    all_results[key][platform] = {
                                        'url': url_data['url'],
                                        'confidence': url_data.get('confidence', 0.5),
                                        'is_active': url_data.get('is_active', False),
                                        'follower_count': url_data.get('followers'),
                                        'discovered_via': 'pattern_matching'
                                    }
        
        return all_results
    
    def clean_url(self, url: str) -> str:
        """Clean and standardize URL format"""
        if not url:
            return url
        
        # Ensure https://
        if url.startswith('http://'):
            url = url.replace('http://', 'https://', 1)
        elif not url.startswith('https://'):
            url = 'https://' + url
        
        # Remove trailing slashes
        url = url.rstrip('/')
        
        # Fix common issues
        url = url.replace('instagram.com//', 'instagram.com/')
        url = url.replace('youtube.com//', 'youtube.com/')
        
        return url
    
    def update_account_with_results(self, account: Dict, results: Dict) -> Tuple[Dict, bool]:
        """Update single account with verification/discovery results"""
        updated = False
        
        # Check for Instagram updates
        if 'instagram' in results:
            ig_data = results['instagram']
            if ig_data.get('is_active', False) or ig_data.get('verification_status') == 'active':
                new_url = self.clean_url(ig_data['url'])
                
                # Add or update Instagram URL
                if not account.get('instagram_url') or account['instagram_url'] != new_url:
                    account['instagram_url'] = new_url
                    self.stats['instagram_added'] += 1
                    self.stats['urls_added'] += 1
                    updated = True
                    logger.info(f"Added Instagram for {account.get('name')}: {new_url}")
                
                # Add verification metadata
                if 'instagram_verified' not in account:
                    account['instagram_verified'] = True
                    account['instagram_followers'] = ig_data.get('follower_count')
                    self.stats['verification_status_added'] += 1
                    updated = True
        
        # Check for YouTube updates
        if 'youtube' in results:
            yt_data = results['youtube']
            if yt_data.get('is_active', False) or yt_data.get('verification_status') == 'active':
                new_url = self.clean_url(yt_data['url'])
                
                # Add or update YouTube URL
                if not account.get('youtube_url') or account['youtube_url'] != new_url:
                    account['youtube_url'] = new_url
                    self.stats['youtube_added'] += 1
                    self.stats['urls_added'] += 1
                    updated = True
                    logger.info(f"Added YouTube for {account.get('name')}: {new_url}")
                
                # Add verification metadata
                if 'youtube_verified' not in account:
                    account['youtube_verified'] = True
                    account['youtube_subscribers'] = yt_data.get('follower_count')
                    self.stats['verification_status_added'] += 1
                    updated = True
        
        # Check for Twitter updates
        if 'twitter' in results:
            tw_data = results['twitter']
            if tw_data.get('is_active', False) or tw_data.get('verification_status') == 'active':
                new_url = self.clean_url(tw_data['url'])
                
                # Add Twitter URL (new field)
                if 'twitter_url' not in account:
                    account['twitter_url'] = new_url
                    self.stats['twitter_added'] += 1
                    self.stats['urls_added'] += 1
                    updated = True
                    logger.info(f"Added Twitter for {account.get('name')}: {new_url}")
        
        # Check for website updates
        if 'website' in results or 'websites' in results:
            web_data = results.get('website') or results.get('websites')
            if web_data:
                if isinstance(web_data, list) and web_data:
                    web_url = self.clean_url(web_data[0].get('url') if isinstance(web_data[0], dict) else web_data[0])
                elif isinstance(web_data, dict) and web_data.get('url'):
                    web_url = self.clean_url(web_data['url'])
                else:
                    web_url = None
                
                if web_url and 'website_url' not in account:
                    account['website_url'] = web_url
                    self.stats['websites_added'] += 1
                    self.stats['urls_added'] += 1
                    updated = True
                    logger.info(f"Added website for {account.get('name')}: {web_url}")
        
        # Add last updated timestamp
        if updated:
            account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
            self.stats['accounts_updated'] += 1
        
        return account, updated
    
    def update_all_accounts(self, results: Dict):
        """Update all accounts with results"""
        logger.info(f"Updating {len(self.yaml_data['accounts'])} accounts with results")
        
        updated_count = 0
        
        for i, account in enumerate(self.yaml_data['accounts']):
            if not account:
                continue
            
            # Try to find results by name
            account_name = account.get('name', '').lower()
            account_handle = account.get('handle', '').lower()
            
            account_results = {}
            
            # Check by name
            if account_name in results:
                account_results.update(results[account_name])
            
            # Check by handle
            if account_handle in results:
                account_results.update(results[account_handle])
            
            # Update account if we have results
            if account_results:
                updated_account, was_updated = self.update_account_with_results(account, account_results)
                self.yaml_data['accounts'][i] = updated_account
                
                if was_updated:
                    updated_count += 1
        
        logger.info(f"Updated {updated_count} accounts")
    
    def clean_account_data(self):
        """Clean and standardize all account data"""
        logger.info("Cleaning and standardizing account data")
        
        for account in self.yaml_data['accounts']:
            if not account:
                continue
            
            # Clean URLs
            if account.get('instagram_url'):
                account['instagram_url'] = self.clean_url(account['instagram_url'])
            
            if account.get('youtube_url'):
                account['youtube_url'] = self.clean_url(account['youtube_url'])
            
            if account.get('twitter_url'):
                account['twitter_url'] = self.clean_url(account['twitter_url'])
            
            if account.get('website_url'):
                account['website_url'] = self.clean_url(account['website_url'])
            
            # Ensure handle starts with @
            if account.get('handle') and not account['handle'].startswith('@'):
                account['handle'] = '@' + account['handle']
            
            # Clean up empty fields
            keys_to_remove = []
            for key, value in account.items():
                if value in [None, '', []]:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del account[key]
    
    def save_updated_yaml(self, output_file: str = None):
        """Save updated YAML file"""
        if not output_file:
            # Create backup and update original
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.yaml_file.parent / f"{self.yaml_file.stem}_backup_{timestamp}.yml"
            
            # Save backup
            with open(backup_file, 'w', encoding='utf-8') as f:
                with open(self.yaml_file, 'r', encoding='utf-8') as orig:
                    f.write(orig.read())
            logger.info(f"Created backup: {backup_file}")
            
            output_file = self.yaml_file
        else:
            output_file = Path(output_file)
        
        # Save updated YAML
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.yaml_data, f, 
                     default_flow_style=False, 
                     allow_unicode=True,
                     sort_keys=False,
                     width=1000)
        
        logger.info(f"Saved updated YAML to: {output_file}")
        return output_file
    
    def generate_update_report(self) -> str:
        """Generate summary report of updates"""
        report = []
        report.append("="*70)
        report.append("YAML UPDATE SUMMARY REPORT")
        report.append("="*70)
        report.append(f"\nProcessed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Original file: {self.yaml_file}")
        
        report.append(f"\n📊 STATISTICS:")
        report.append(f"  Total accounts: {self.stats['total_accounts']}")
        report.append(f"  Accounts updated: {self.stats['accounts_updated']}")
        report.append(f"  Total URLs added: {self.stats['urls_added']}")
        
        report.append(f"\n🔗 URLs ADDED BY PLATFORM:")
        report.append(f"  Instagram URLs added: {self.stats['instagram_added']}")
        report.append(f"  YouTube URLs added: {self.stats['youtube_added']}")
        report.append(f"  Twitter URLs added: {self.stats['twitter_added']}")
        report.append(f"  Website URLs added: {self.stats['websites_added']}")
        
        report.append(f"\n✅ VERIFICATION DATA:")
        report.append(f"  Verification statuses added: {self.stats['verification_status_added']}")
        
        # Calculate completion rates
        total_possible_urls = self.stats['total_accounts'] * 2  # Instagram + YouTube
        instagram_complete = sum(1 for acc in self.yaml_data['accounts'] 
                                if acc and acc.get('instagram_url'))
        youtube_complete = sum(1 for acc in self.yaml_data['accounts'] 
                              if acc and acc.get('youtube_url'))
        
        report.append(f"\n📈 COMPLETION RATES:")
        report.append(f"  Instagram: {instagram_complete}/{self.stats['total_accounts']} "
                     f"({instagram_complete/self.stats['total_accounts']*100:.1f}%)")
        report.append(f"  YouTube: {youtube_complete}/{self.stats['total_accounts']} "
                     f"({youtube_complete/self.stats['total_accounts']*100:.1f}%)")
        
        report.append("\n" + "="*70)
        
        return "\n".join(report)


def main():
    """Main execution"""
    # Configuration
    yaml_file = r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml"
    verification_results_dir = r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\verification_results"
    pattern_results_dir = r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\pattern_discovery"
    
    print("\n🔄 YAML Data Update Process")
    print("="*60)
    print("Merging all verification and discovery results into YAML")
    print("="*60)
    
    # Create updater
    updater = YAMLDataUpdater(yaml_file)
    
    # Load all results
    print("\n📂 Loading verification results...")
    all_results = {}
    
    # Load from verification results directory
    if Path(verification_results_dir).exists():
        verification_results = updater.load_verification_results(verification_results_dir)
        all_results.update(verification_results)
        print(f"  Loaded {len(verification_results)} account results from verification")
    
    # Load from pattern discovery directory
    if Path(pattern_results_dir).exists():
        pattern_results = updater.load_verification_results(pattern_results_dir)
        all_results.update(pattern_results)
        print(f"  Loaded {len(pattern_results)} account results from pattern discovery")
    
    print(f"\n📊 Total unique accounts with results: {len(all_results)}")
    
    # Update accounts
    print("\n✏️ Updating accounts with results...")
    updater.update_all_accounts(all_results)
    
    # Clean data
    print("\n🧹 Cleaning and standardizing data...")
    updater.clean_account_data()
    
    # Save updated YAML
    print("\n💾 Saving updated YAML...")
    output_file = updater.save_updated_yaml()
    
    # Generate and print report
    report = updater.generate_update_report()
    print("\n" + report)
    
    # Save report
    report_file = Path(yaml_file).parent / f"update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: {report_file}")
    print(f"✅ YAML updated successfully: {output_file}")
    
    # Show sample of updated accounts
    print("\n📋 Sample of updated accounts:")
    sample_count = 0
    for account in updater.yaml_data['accounts']:
        if account and account.get('last_updated'):
            print(f"  - {account['name']}: Instagram={bool(account.get('instagram_url'))}, "
                  f"YouTube={bool(account.get('youtube_url'))}")
            sample_count += 1
            if sample_count >= 5:
                break


if __name__ == "__main__":
    main()