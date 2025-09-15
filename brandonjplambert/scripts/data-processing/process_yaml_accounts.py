"""
YAML Spanish Accounts Processor
Parses YAML file and verifies/enriches all Spanish social media accounts
"""

import yaml
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from collections import defaultdict
import pandas as pd

# Add parent directories to path for cross-directory imports
sys.path.append(str(Path(__file__).parent.parent / "verification"))

from spanish_links_verifier import DatasetVerifier, LinkMetadata
from advanced_enrichment import (
    ContentAnalyzer, 
    DataQualityScorer,
    LocationExtractor,
    EmailFinder
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class YAMLAccountsProcessor:
    """Process Spanish accounts from YAML file"""
    
    def __init__(self, yaml_file: str, output_dir: str = None):
        self.yaml_file = Path(yaml_file)
        self.output_dir = Path(output_dir) if output_dir else self.yaml_file.parent
        self.output_dir.mkdir(exist_ok=True)
        
        self.accounts_data = []
        self.urls_to_verify = []
        self.category_stats = defaultdict(int)
        self.platform_stats = defaultdict(int)
        self.verification_results = {}
        
        self.verifier = DatasetVerifier(youtube_api_key=None)
        self.quality_scorer = DataQualityScorer()
        
    def load_yaml(self) -> Dict:
        """Load and parse YAML file"""
        logger.info(f"Loading YAML file: {self.yaml_file}")
        
        with open(self.yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return data
    
    def extract_accounts(self, data: Dict) -> List[Dict]:
        """Extract account information from YAML structure"""
        accounts = []
        
        if 'accounts' in data:
            for account in data['accounts']:
                if account is None:
                    continue
                    
                processed_account = {
                    'handle': account.get('handle', ''),
                    'name': account.get('name', ''),
                    'category': account.get('category', 'Unknown'),
                    'description': account.get('description', ''),
                    'urls': [],
                    'platforms': []
                }
                
                # Extract Instagram URL
                if 'instagram_url' in account:
                    processed_account['urls'].append(account['instagram_url'])
                    processed_account['platforms'].append('instagram')
                    self.platform_stats['instagram'] += 1
                
                # Extract YouTube URL
                if 'youtube_url' in account:
                    processed_account['urls'].append(account['youtube_url'])
                    processed_account['platforms'].append('youtube')
                    self.platform_stats['youtube'] += 1
                
                # Extract any other URL fields
                for key, value in account.items():
                    if 'url' in key.lower() and key not in ['instagram_url', 'youtube_url']:
                        if value:
                            processed_account['urls'].append(value)
                            platform = key.replace('_url', '').replace('url', '')
                            processed_account['platforms'].append(platform)
                            self.platform_stats[platform] += 1
                
                # Track category statistics
                self.category_stats[processed_account['category']] += 1
                
                accounts.append(processed_account)
                
                # Add URLs to verification list
                for url in processed_account['urls']:
                    self.urls_to_verify.append({
                        'url': url,
                        'account_handle': processed_account['handle'],
                        'account_name': processed_account['name'],
                        'category': processed_account['category']
                    })
        
        logger.info(f"Extracted {len(accounts)} accounts with {len(self.urls_to_verify)} URLs")
        return accounts
    
    async def verify_all_urls(self) -> Dict[str, Any]:
        """Verify all extracted URLs"""
        logger.info(f"Starting verification of {len(self.urls_to_verify)} URLs")
        
        # Extract just the URLs for verification
        urls_list = [item['url'] for item in self.urls_to_verify]
        
        # Verify URLs in batches
        results = await self.verifier.verify_and_enrich(
            urls_list,
            batch_size=20  # Smaller batch size for better rate limiting
        )
        
        # Map results back to original account data
        for i, result in enumerate(results):
            if i < len(self.urls_to_verify):
                url_info = self.urls_to_verify[i]
                
                # Enrich with original YAML data
                enriched_result = {
                    'url': result.url,
                    'account_handle': url_info['account_handle'],
                    'account_name': url_info['account_name'],
                    'category': url_info['category'],
                    'platform': result.platform.value,
                    'verification_status': result.verification_status.value,
                    'username': result.username,
                    'display_name': result.display_name,
                    'bio': result.bio,
                    'follower_count': result.follower_count,
                    'following_count': result.following_count,
                    'post_count': result.post_count,
                    'is_spanish': result.is_spanish,
                    'language_confidence': result.language_confidence,
                    'location': result.location,
                    'verified_badge': result.verified_badge,
                    'external_links': result.external_links,
                    'quality_score': result.quality_score,
                    'last_verified': result.last_verified.isoformat() if result.last_verified else None
                }
                
                # Additional enrichment
                if result.bio:
                    categories = ContentAnalyzer.categorize_content(result.bio)
                    enriched_result['content_categories'] = categories
                    
                    emails = EmailFinder.find_emails(result.bio)
                    if emails:
                        enriched_result['discovered_emails'] = emails
                
                # Calculate comprehensive quality scores
                quality_scores = self.quality_scorer.calculate_comprehensive_score(enriched_result)
                enriched_result['quality_scores'] = quality_scores
                
                # Store by URL for easy lookup
                self.verification_results[result.url] = enriched_result
        
        return self.verification_results
    
    def generate_reports(self):
        """Generate comprehensive reports in multiple formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Detailed JSON report
        json_output = self.output_dir / f"verified_accounts_{timestamp}.json"
        self._save_json_report(json_output)
        
        # 2. Excel report with multiple sheets
        excel_output = self.output_dir / f"spanish_accounts_analysis_{timestamp}.xlsx"
        self._save_excel_report(excel_output)
        
        # 3. Category summary
        category_output = self.output_dir / f"category_analysis_{timestamp}.json"
        self._save_category_analysis(category_output)
        
        # 4. Quality assessment report
        quality_output = self.output_dir / f"quality_assessment_{timestamp}.csv"
        self._save_quality_assessment(quality_output)
        
        # 5. Failed verifications report
        failed_output = self.output_dir / f"failed_verifications_{timestamp}.csv"
        self._save_failed_verifications(failed_output)
        
        logger.info(f"Reports generated in {self.output_dir}")
        
        return {
            'json_report': str(json_output),
            'excel_report': str(excel_output),
            'category_analysis': str(category_output),
            'quality_assessment': str(quality_output),
            'failed_verifications': str(failed_output)
        }
    
    def _save_json_report(self, output_file: Path):
        """Save detailed JSON report"""
        report = {
            'metadata': {
                'source_file': str(self.yaml_file),
                'processed_at': datetime.now().isoformat(),
                'total_accounts': len(self.accounts_data),
                'total_urls': len(self.urls_to_verify),
                'verified_urls': len(self.verification_results)
            },
            'statistics': {
                'by_category': dict(self.category_stats),
                'by_platform': dict(self.platform_stats),
                'verification_summary': self._get_verification_summary()
            },
            'accounts': self.accounts_data,
            'verification_results': list(self.verification_results.values())
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    def _save_excel_report(self, output_file: Path):
        """Save multi-sheet Excel report"""
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Sheet 1: Account Overview
            accounts_df = pd.DataFrame(self.accounts_data)
            accounts_df.to_excel(writer, sheet_name='Accounts', index=False)
            
            # Sheet 2: Verification Results
            if self.verification_results:
                results_df = pd.DataFrame(list(self.verification_results.values()))
                # Select important columns for readability
                important_cols = [
                    'account_name', 'account_handle', 'category', 'platform',
                    'verification_status', 'follower_count', 'is_spanish',
                    'language_confidence', 'quality_score'
                ]
                available_cols = [col for col in important_cols if col in results_df.columns]
                results_df[available_cols].to_excel(writer, sheet_name='Verification Results', index=False)
            
            # Sheet 3: Category Statistics
            category_df = pd.DataFrame([
                {'Category': cat, 'Count': count}
                for cat, count in self.category_stats.items()
            ])
            category_df.to_excel(writer, sheet_name='Categories', index=False)
            
            # Sheet 4: Platform Statistics
            platform_df = pd.DataFrame([
                {'Platform': plat, 'Count': count}
                for plat, count in self.platform_stats.items()
            ])
            platform_df.to_excel(writer, sheet_name='Platforms', index=False)
    
    def _save_category_analysis(self, output_file: Path):
        """Save detailed category analysis"""
        category_analysis = {}
        
        for category in self.category_stats.keys():
            category_urls = [
                url for url in self.verification_results.values()
                if url.get('category') == category
            ]
            
            if category_urls:
                active_count = sum(1 for u in category_urls if u.get('verification_status') == 'active')
                avg_followers = sum(u.get('follower_count', 0) for u in category_urls) / len(category_urls)
                spanish_confirmed = sum(1 for u in category_urls if u.get('is_spanish'))
                
                category_analysis[category] = {
                    'total_accounts': self.category_stats[category],
                    'urls_verified': len(category_urls),
                    'active_accounts': active_count,
                    'average_followers': int(avg_followers),
                    'spanish_confirmed': spanish_confirmed,
                    'top_accounts': sorted(
                        [{'name': u['account_name'], 'followers': u.get('follower_count', 0)}
                         for u in category_urls],
                        key=lambda x: x['followers'] or 0,
                        reverse=True
                    )[:5]
                }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(category_analysis, f, ensure_ascii=False, indent=2)
    
    def _save_quality_assessment(self, output_file: Path):
        """Save quality assessment CSV"""
        quality_data = []
        
        for result in self.verification_results.values():
            quality_scores = result.get('quality_scores', {})
            quality_data.append({
                'Account': result['account_name'],
                'Handle': result['account_handle'],
                'Platform': result['platform'],
                'Category': result['category'],
                'Overall Quality': quality_scores.get('overall', 0),
                'Completeness': quality_scores.get('completeness', 0),
                'Accuracy': quality_scores.get('accuracy', 0),
                'Freshness': quality_scores.get('freshness', 0),
                'Consistency': quality_scores.get('consistency', 0),
                'Relevance': quality_scores.get('relevance', 0),
                'Followers': result.get('follower_count', 0),
                'Status': result['verification_status']
            })
        
        df = pd.DataFrame(quality_data)
        df.sort_values('Overall Quality', ascending=False, inplace=True)
        df.to_csv(output_file, index=False)
    
    def _save_failed_verifications(self, output_file: Path):
        """Save report of failed verifications"""
        failed = []
        
        for result in self.verification_results.values():
            if result['verification_status'] not in ['active', 'private']:
                failed.append({
                    'Account': result['account_name'],
                    'Handle': result['account_handle'],
                    'URL': result['url'],
                    'Platform': result['platform'],
                    'Category': result['category'],
                    'Status': result['verification_status'],
                    'Error': result.get('error_message', 'N/A')
                })
        
        if failed:
            df = pd.DataFrame(failed)
            df.to_csv(output_file, index=False)
            logger.warning(f"Found {len(failed)} failed verifications")
    
    def _get_verification_summary(self) -> Dict:
        """Get verification statistics summary"""
        if not self.verification_results:
            return {}
        
        statuses = defaultdict(int)
        spanish_count = 0
        high_quality = 0
        total_followers = 0
        verified_badges = 0
        
        for result in self.verification_results.values():
            statuses[result['verification_status']] += 1
            if result.get('is_spanish'):
                spanish_count += 1
            if result.get('quality_score', 0) > 0.7:
                high_quality += 1
            total_followers += result.get('follower_count', 0)
            if result.get('verified_badge'):
                verified_badges += 1
        
        return {
            'status_breakdown': dict(statuses),
            'spanish_confirmed': spanish_count,
            'high_quality_accounts': high_quality,
            'total_followers': total_followers,
            'verified_badges': verified_badges,
            'average_quality': sum(r.get('quality_score', 0) for r in self.verification_results.values()) / len(self.verification_results)
        }
    
    def print_summary(self):
        """Print processing summary to console"""
        print("\n" + "="*70)
        print("SPANISH ACCOUNTS VERIFICATION SUMMARY")
        print("="*70)
        
        print(f"\nSource File: {self.yaml_file.name}")
        print(f"Total Accounts: {len(self.accounts_data)}")
        print(f"Total URLs: {len(self.urls_to_verify)}")
        print(f"Verified URLs: {len(self.verification_results)}")
        
        print("\n--- Categories ---")
        for category, count in sorted(self.category_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count}")
        
        print("\n--- Platforms ---")
        for platform, count in sorted(self.platform_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {platform}: {count}")
        
        if self.verification_results:
            summary = self._get_verification_summary()
            
            print("\n--- Verification Status ---")
            for status, count in summary['status_breakdown'].items():
                percentage = (count / len(self.verification_results)) * 100
                print(f"  {status}: {count} ({percentage:.1f}%)")
            
            print(f"\n--- Quality Metrics ---")
            print(f"  Spanish Confirmed: {summary['spanish_confirmed']}")
            print(f"  High Quality (>70%): {summary['high_quality_accounts']}")
            print(f"  Verified Badges: {summary['verified_badges']}")
            print(f"  Total Followers: {summary['total_followers']:,}")
            print(f"  Average Quality Score: {summary['average_quality']:.2f}")
        
        print("="*70 + "\n")


async def main():
    """Main execution function"""
    # Configuration
    yaml_file = r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml"
    output_dir = r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\verification_results"
    
    # Create processor
    processor = YAMLAccountsProcessor(yaml_file, output_dir)
    
    # Load and parse YAML
    yaml_data = processor.load_yaml()
    processor.accounts_data = processor.extract_accounts(yaml_data)
    
    # Print initial statistics
    print(f"\n📊 Loaded {len(processor.accounts_data)} accounts from YAML")
    print(f"📍 Found {len(processor.urls_to_verify)} URLs to verify")
    print(f"📂 Categories: {', '.join(processor.category_stats.keys())}")
    
    # Verify all URLs
    print("\n🔍 Starting verification process...")
    print("⏳ This may take several minutes depending on the number of URLs...")
    
    await processor.verify_all_urls()
    
    # Generate reports
    print("\n📝 Generating reports...")
    report_files = processor.generate_reports()
    
    # Print summary
    processor.print_summary()
    
    # Print output files
    print("\n✅ Verification complete! Reports saved to:")
    for report_type, file_path in report_files.items():
        print(f"  - {report_type}: {file_path}")
    
    return processor


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())