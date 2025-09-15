"""
Export complete Spanish accounts data to CSV
"""

import yaml
import csv
from pathlib import Path
from datetime import datetime

def export_spanish_accounts_to_csv():
    """Export all Spanish account data to a comprehensive CSV file"""
    
    yaml_file = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml")
    
    print("Loading YAML file...")
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Prepare CSV data
    csv_data = []
    
    print("Processing accounts...")
    for i, account in enumerate(data.get('accounts', []), 1):
        if not account:
            continue
        
        row = {
            'index': i,
            'handle': account.get('handle', ''),
            'name': account.get('name', ''),
            'category': account.get('category', ''),
            'description': account.get('description', ''),
            'instagram_url': account.get('instagram_url', ''),
            'instagram_followers': account.get('instagram_followers', ''),
            'instagram_verified': account.get('instagram_verified', ''),
            'youtube_url': account.get('youtube_url', ''),
            'youtube_subscribers': account.get('youtube_subscribers', ''),
            'youtube_verified': account.get('youtube_verified', ''),
            'website': account.get('website', ''),
            'twitter_url': account.get('twitter_url', ''),
            'facebook_url': account.get('facebook_url', ''),
            'last_updated': account.get('last_updated', ''),
            'has_instagram': 'Yes' if account.get('instagram_url') else 'No',
            'has_youtube': 'Yes' if account.get('youtube_url') else 'No',
            'has_both': 'Yes' if (account.get('instagram_url') and account.get('youtube_url')) else 'No'
        }
        csv_data.append(row)
    
    # Create CSV filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create exports directory path
    exports_dir = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\data\exports")
    exports_dir.mkdir(parents=True, exist_ok=True)
    
    csv_file = exports_dir / f"spanish_accounts_complete_{timestamp}.csv"
    
    print(f"\nWriting to CSV: {csv_file}")
    
    # Write CSV file
    fieldnames = [
        'index', 'handle', 'name', 'category', 'description',
        'instagram_url', 'instagram_followers', 'instagram_verified',
        'youtube_url', 'youtube_subscribers', 'youtube_verified',
        'website', 'twitter_url', 'facebook_url',
        'last_updated', 'has_instagram', 'has_youtube', 'has_both'
    ]
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    
    # Calculate statistics
    total_accounts = len(csv_data)
    has_instagram = sum(1 for row in csv_data if row['has_instagram'] == 'Yes')
    has_youtube = sum(1 for row in csv_data if row['has_youtube'] == 'Yes')
    has_both = sum(1 for row in csv_data if row['has_both'] == 'Yes')
    has_neither = total_accounts - has_instagram - has_youtube + has_both
    
    # Categories breakdown
    categories = {}
    for row in csv_data:
        cat = row['category'] or 'Uncategorized'
        categories[cat] = categories.get(cat, 0) + 1
    
    # Print summary
    print("\n" + "=" * 60)
    print("SPANISH ACCOUNTS CSV EXPORT COMPLETE")
    print("=" * 60)
    print(f"✓ Exported {total_accounts} accounts to: {csv_file}")
    
    print(f"\n📊 ACCOUNT STATISTICS:")
    print(f"  Total accounts: {total_accounts}")
    print(f"  Has Instagram: {has_instagram} ({has_instagram/total_accounts*100:.1f}%)")
    print(f"  Has YouTube: {has_youtube} ({has_youtube/total_accounts*100:.1f}%)")
    print(f"  Has both: {has_both} ({has_both/total_accounts*100:.1f}%)")
    print(f"  Has neither: {has_neither} ({has_neither/total_accounts*100:.1f}%)")
    
    print(f"\n📂 TOP CATEGORIES:")
    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
    for cat, count in sorted_categories[:10]:
        print(f"  {cat}: {count} accounts")
    
    # Accounts with most followers
    print(f"\n🌟 TOP INSTAGRAM ACCOUNTS (by followers):")
    instagram_accounts = [(row['name'], int(row['instagram_followers'])) 
                         for row in csv_data 
                         if row['instagram_followers'] and str(row['instagram_followers']).isdigit()]
    instagram_accounts.sort(key=lambda x: x[1], reverse=True)
    
    for name, followers in instagram_accounts[:5]:
        print(f"  {name}: {followers:,} followers")
    
    print(f"\n📺 TOP YOUTUBE ACCOUNTS (by subscribers):")
    youtube_accounts = [(row['name'], int(row['youtube_subscribers'])) 
                       for row in csv_data 
                       if row['youtube_subscribers'] and str(row['youtube_subscribers']).isdigit()]
    youtube_accounts.sort(key=lambda x: x[1], reverse=True)
    
    for name, subscribers in youtube_accounts[:5]:
        print(f"  {name}: {subscribers:,} subscribers")
    
    print(f"\n✅ CSV file ready for use: {csv_file}")
    print("  - UTF-8 encoded")
    print("  - Contains all account data")
    print("  - Includes social media URLs and metrics")
    
    return csv_file

if __name__ == "__main__":
    export_spanish_accounts_to_csv()