"""
Quick analysis of verification results
"""

import json
from pathlib import Path
from collections import defaultdict

def analyze_results():
    """Analyze the verification results"""
    
    # Find the latest results file
    results_dir = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\verification_results")
    json_files = list(results_dir.glob("*.json"))
    
    if not json_files:
        print("No results files found")
        return
    
    latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
    print(f"📊 Analyzing: {latest_file.name}")
    print("="*70)
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data['results']
    
    # Basic statistics
    print(f"\n📈 OVERVIEW")
    print(f"   Total URLs processed: {len(results)}")
    print(f"   YouTube URLs: {data['metadata']['youtube_processed']}")
    print(f"   Instagram URLs: {data['metadata']['instagram_processed']}")
    
    # Verification status breakdown
    status_counts = defaultdict(int)
    for r in results:
        status_counts[r['verification_status']] += 1
    
    print(f"\n✅ VERIFICATION STATUS")
    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(results)) * 100
        print(f"   {status}: {count} ({percentage:.1f}%)")
    
    # Category analysis
    category_counts = defaultdict(int)
    category_active = defaultdict(int)
    for r in results:
        category = r['category']
        category_counts[category] += 1
        if r['verification_status'] == 'active':
            category_active[category] += 1
    
    print(f"\n📂 TOP CATEGORIES")
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        active = category_active[category]
        print(f"   {category}: {count} URLs ({active} active)")
    
    # Platform success rates
    platform_stats = defaultdict(lambda: {'total': 0, 'active': 0})
    for r in results:
        platform = r['platform']
        platform_stats[platform]['total'] += 1
        if r['verification_status'] == 'active':
            platform_stats[platform]['active'] += 1
    
    print(f"\n🌐 PLATFORM SUCCESS RATES")
    for platform, stats in platform_stats.items():
        success_rate = (stats['active'] / stats['total']) * 100 if stats['total'] > 0 else 0
        print(f"   {platform}: {stats['active']}/{stats['total']} ({success_rate:.1f}% success)")
    
    # Accounts with followers data
    accounts_with_followers = [r for r in results if r.get('follower_count')]
    if accounts_with_followers:
        sorted_by_followers = sorted(accounts_with_followers, key=lambda x: x['follower_count'], reverse=True)
        
        print(f"\n🏆 TOP ACCOUNTS BY FOLLOWERS")
        for acc in sorted_by_followers[:10]:
            followers = acc['follower_count']
            name = acc['account_name']
            platform = acc['platform']
            print(f"   {name} ({platform}): {followers:,} followers")
        
        total_followers = sum(r['follower_count'] for r in accounts_with_followers)
        avg_followers = total_followers / len(accounts_with_followers) if accounts_with_followers else 0
        print(f"\n   Total reach: {total_followers:,} followers")
        print(f"   Average per account: {avg_followers:,.0f} followers")
    
    # Failed verifications
    failed = [r for r in results if r['verification_status'] in ['not_found', 'error', 'rate_limited']]
    if failed:
        print(f"\n⚠️ FAILED VERIFICATIONS: {len(failed)}")
        for f in failed[:5]:
            print(f"   - {f['account_name']} ({f['platform']}): {f['verification_status']}")
        if len(failed) > 5:
            print(f"   ... and {len(failed) - 5} more")
    
    # Summary insights
    print(f"\n💡 KEY INSIGHTS")
    active_rate = (status_counts.get('active', 0) / len(results)) * 100
    print(f"   • {active_rate:.1f}% of verified URLs are active")
    
    gov_diplomatic = category_active.get('Government', 0) + category_active.get('Diplomatic', 0)
    print(f"   • {gov_diplomatic} Government/Diplomatic accounts verified")
    
    if accounts_with_followers:
        print(f"   • {len(accounts_with_followers)} accounts provided follower data")
    
    print(f"\n📅 Data freshness: {data['metadata']['processed_at']}")
    print("="*70)

if __name__ == "__main__":
    analyze_results()