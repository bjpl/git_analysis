"""
Optimized verification with better rate limit handling
Processes YouTube URLs first (higher limits) then Instagram carefully
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent))

# Add parent directories to path for cross-directory imports
sys.path.append(str(Path(__file__).parent.parent / "data-processing"))

from spanish_links_verifier import DatasetVerifier
from process_yaml_accounts import YAMLAccountsProcessor


async def run_optimized():
    """Run verification with optimized rate limit handling"""
    
    yaml_file = r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml"
    output_dir = r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\verification_results"
    
    print("="*70)
    print("OPTIMIZED SPANISH ACCOUNTS VERIFICATION")
    print("="*70)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Create processor with smaller batch size
        processor = YAMLAccountsProcessor(yaml_file, output_dir)
        
        # Load YAML data
        print("\n⏳ Loading YAML data...")
        yaml_data = processor.load_yaml()
        processor.accounts_data = processor.extract_accounts(yaml_data)
        
        print(f"\n✅ Loaded {len(processor.accounts_data)} accounts")
        print(f"   - Instagram URLs: {processor.platform_stats.get('instagram', 0)}")
        print(f"   - YouTube URLs: {processor.platform_stats.get('youtube', 0)}")
        
        # Separate URLs by platform for smarter processing
        instagram_urls = []
        youtube_urls = []
        other_urls = []
        
        for url_info in processor.urls_to_verify:
            url = url_info['url']
            if 'instagram.com' in url:
                instagram_urls.append(url_info)
            elif 'youtube.com' in url or 'youtu.be' in url:
                youtube_urls.append(url_info)
            else:
                other_urls.append(url_info)
        
        print(f"\n📊 URL Distribution:")
        print(f"   - Instagram: {len(instagram_urls)} URLs")
        print(f"   - YouTube: {len(youtube_urls)} URLs")
        print(f"   - Other: {len(other_urls)} URLs")
        
        all_results = {}
        
        # Process YouTube first (higher rate limits)
        if youtube_urls:
            print("\n🎬 Processing YouTube URLs first (better rate limits)...")
            youtube_verifier = DatasetVerifier()
            youtube_url_list = [item['url'] for item in youtube_urls]
            
            # Process YouTube in larger batches
            youtube_results = await youtube_verifier.verify_and_enrich(
                youtube_url_list[:50],  # First 50 YouTube URLs
                batch_size=10
            )
            
            for i, result in enumerate(youtube_results):
                if i < len(youtube_urls):
                    url_info = youtube_urls[i]
                    all_results[result.url] = {
                        'url': result.url,
                        'account_handle': url_info['account_handle'],
                        'account_name': url_info['account_name'],
                        'category': url_info['category'],
                        'platform': 'youtube',
                        'verification_status': result.verification_status.value,
                        'follower_count': result.follower_count,
                        'display_name': result.display_name,
                        'bio': result.bio
                    }
            
            print(f"   ✅ Processed {len(youtube_results)} YouTube URLs")
        
        # Process Instagram with very small batches
        if instagram_urls:
            print("\n📸 Processing Instagram URLs (careful rate limiting)...")
            instagram_verifier = DatasetVerifier()
            instagram_url_list = [item['url'] for item in instagram_urls]
            
            # Process only first 30 Instagram URLs to avoid rate limits
            instagram_results = await instagram_verifier.verify_and_enrich(
                instagram_url_list[:30],  # Limited Instagram processing
                batch_size=5  # Very small batches
            )
            
            for i, result in enumerate(instagram_results):
                if i < len(instagram_urls):
                    url_info = instagram_urls[i]
                    all_results[result.url] = {
                        'url': result.url,
                        'account_handle': url_info['account_handle'],
                        'account_name': url_info['account_name'],
                        'category': url_info['category'],
                        'platform': 'instagram',
                        'verification_status': result.verification_status.value,
                        'follower_count': result.follower_count,
                        'display_name': result.display_name,
                        'bio': result.bio
                    }
            
            print(f"   ✅ Processed {len(instagram_results)} Instagram URLs")
            
            if len(instagram_urls) > 30:
                print(f"   ⚠️  {len(instagram_urls) - 30} Instagram URLs skipped due to rate limits")
                print("      (Run again later to process remaining URLs)")
        
        # Save quick results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        quick_results_file = Path(output_dir) / f"quick_verification_{timestamp}.json"
        
        Path(output_dir).mkdir(exist_ok=True)
        
        with open(quick_results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'processed_at': datetime.now().isoformat(),
                    'total_urls_processed': len(all_results),
                    'youtube_processed': len([r for r in all_results.values() if r['platform'] == 'youtube']),
                    'instagram_processed': len([r for r in all_results.values() if r['platform'] == 'instagram'])
                },
                'results': list(all_results.values())
            }, f, ensure_ascii=False, indent=2)
        
        # Print summary
        print("\n" + "="*70)
        print("VERIFICATION SUMMARY")
        print("="*70)
        
        active_count = sum(1 for r in all_results.values() if r['verification_status'] == 'active')
        print(f"\n✅ Successfully verified: {active_count} accounts")
        
        # Category breakdown
        category_counts = {}
        for result in all_results.values():
            cat = result['category']
            if cat not in category_counts:
                category_counts[cat] = 0
            category_counts[cat] += 1
        
        print("\n📊 By Category:")
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   - {cat}: {count}")
        
        # Top accounts by followers
        sorted_accounts = sorted(
            [r for r in all_results.values() if r.get('follower_count')],
            key=lambda x: x['follower_count'] or 0,
            reverse=True
        )
        
        if sorted_accounts:
            print("\n🏆 Top Accounts by Followers:")
            for acc in sorted_accounts[:5]:
                followers = acc.get('follower_count', 0)
                if followers:
                    print(f"   - {acc['account_name']}: {followers:,} followers")
        
        print(f"\n📁 Results saved to: {quick_results_file}")
        print(f"🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return str(quick_results_file)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("\n🚀 Spanish Accounts Quick Verification (Rate-Limit Optimized)")
    result_file = asyncio.run(run_optimized())
    if result_file:
        print(f"\n✅ Verification complete! Check: {result_file}")