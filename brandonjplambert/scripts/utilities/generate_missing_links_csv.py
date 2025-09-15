"""
Generate CSV lists of accounts missing Instagram or YouTube URLs
"""

import yaml
import csv
from pathlib import Path
from datetime import datetime

def generate_missing_links_csv():
    """Create CSV files for accounts missing social media links"""
    
    yaml_file = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml")
    
    print("Loading YAML file...")
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    missing_instagram = []
    missing_youtube = []
    
    print("Analyzing accounts...")
    for i, account in enumerate(data.get('accounts', [])):
        if not account:
            continue
        
        # Check for missing Instagram
        if not account.get('instagram_url'):
            missing_instagram.append({
                'index': i + 1,
                'handle': account.get('handle', ''),
                'name': account.get('name', ''),
                'category': account.get('category', ''),
                'description': account.get('description', ''),
                'has_youtube': 'Yes' if account.get('youtube_url') else 'No'
            })
        
        # Check for missing YouTube
        if not account.get('youtube_url'):
            missing_youtube.append({
                'index': i + 1,
                'handle': account.get('handle', ''),
                'name': account.get('name', ''),
                'category': account.get('category', ''),
                'description': account.get('description', ''),
                'has_instagram': 'Yes' if account.get('instagram_url') else 'No'
            })
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create exports directory path
    exports_dir = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\data\exports")
    exports_dir.mkdir(parents=True, exist_ok=True)
    
    # Write missing Instagram CSV
    instagram_csv = exports_dir / f"missing_instagram_{timestamp}.csv"
    print(f"\nWriting missing Instagram accounts to: {instagram_csv}")
    
    with open(instagram_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['index', 'handle', 'name', 'category', 'description', 'has_youtube'])
        writer.writeheader()
        writer.writerows(missing_instagram)
    
    # Write missing YouTube CSV
    youtube_csv = exports_dir / f"missing_youtube_{timestamp}.csv"
    print(f"Writing missing YouTube accounts to: {youtube_csv}")
    
    with open(youtube_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['index', 'handle', 'name', 'category', 'description', 'has_instagram'])
        writer.writeheader()
        writer.writerows(missing_youtube)
    
    # Print summary
    print("\n" + "=" * 60)
    print("CSV FILES GENERATED")
    print("=" * 60)
    print(f"\n📊 Missing Instagram: {len(missing_instagram)} accounts")
    print(f"   File: {instagram_csv}")
    print(f"\n📊 Missing YouTube: {len(missing_youtube)} accounts")
    print(f"   File: {youtube_csv}")
    
    # Print sample of missing accounts
    print("\n" + "-" * 60)
    print("SAMPLE OF MISSING INSTAGRAM (first 5):")
    print("-" * 60)
    for acc in missing_instagram[:5]:
        print(f"{acc['name']} ({acc['handle']}) - Category: {acc['category']}")
    
    if len(missing_instagram) > 5:
        print(f"... and {len(missing_instagram) - 5} more")
    
    print("\n" + "-" * 60)
    print("SAMPLE OF MISSING YOUTUBE (first 5):")
    print("-" * 60)
    for acc in missing_youtube[:5]:
        print(f"{acc['name']} ({acc['handle']}) - Category: {acc['category']}")
    
    if len(missing_youtube) > 5:
        print(f"... and {len(missing_youtube) - 5} more")
    
    # Calculate statistics
    total_accounts = len([a for a in data.get('accounts', []) if a])
    has_both = len([a for a in data.get('accounts', []) 
                    if a and a.get('instagram_url') and a.get('youtube_url')])
    has_instagram_only = len([a for a in data.get('accounts', []) 
                             if a and a.get('instagram_url') and not a.get('youtube_url')])
    has_youtube_only = len([a for a in data.get('accounts', []) 
                           if a and a.get('youtube_url') and not a.get('instagram_url')])
    has_neither = len([a for a in data.get('accounts', []) 
                      if a and not a.get('instagram_url') and not a.get('youtube_url')])
    
    print("\n" + "=" * 60)
    print("OVERALL STATISTICS")
    print("=" * 60)
    print(f"Total accounts: {total_accounts}")
    print(f"Has both Instagram & YouTube: {has_both} ({has_both/total_accounts*100:.1f}%)")
    print(f"Has Instagram only: {has_instagram_only} ({has_instagram_only/total_accounts*100:.1f}%)")
    print(f"Has YouTube only: {has_youtube_only} ({has_youtube_only/total_accounts*100:.1f}%)")
    print(f"Has neither: {has_neither} ({has_neither/total_accounts*100:.1f}%)")
    
    return missing_instagram, missing_youtube

if __name__ == "__main__":
    generate_missing_links_csv()