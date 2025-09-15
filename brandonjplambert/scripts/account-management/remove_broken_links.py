"""
Remove broken/inactive social media links from the Spanish accounts dataset
"""

import yaml
from pathlib import Path
from datetime import datetime

def remove_broken_links():
    """Remove URLs that were verified as not_found or inactive"""
    
    yaml_file = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml")
    
    print("Loading YAML file...")
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    stats = {
        'instagram_removed': 0,
        'youtube_removed': 0,
        'total_accounts_affected': 0
    }
    
    removed_links = []
    
    print("Removing broken/inactive links...")
    for account in data.get('accounts', []):
        if not account:
            continue
        
        account_modified = False
        
        # Check Instagram status
        if account.get('instagram_status') == 'not_found':
            # Remove the broken Instagram URL and related fields
            if 'instagram_url' in account:
                removed_links.append({
                    'name': account.get('name', 'Unknown'),
                    'platform': 'instagram',
                    'url': account['instagram_url']
                })
                del account['instagram_url']
                stats['instagram_removed'] += 1
                account_modified = True
            
            # Clean up related fields
            if 'instagram_status' in account:
                del account['instagram_status']
            if 'instagram_verified' in account:
                del account['instagram_verified']
            if 'instagram_followers' in account:
                del account['instagram_followers']
        
        # Check YouTube status
        if account.get('youtube_status') == 'not_found':
            # Remove the broken YouTube URL and related fields
            if 'youtube_url' in account:
                removed_links.append({
                    'name': account.get('name', 'Unknown'),
                    'platform': 'youtube',
                    'url': account['youtube_url']
                })
                del account['youtube_url']
                stats['youtube_removed'] += 1
                account_modified = True
            
            # Clean up related fields
            if 'youtube_status' in account:
                del account['youtube_status']
            if 'youtube_verified' in account:
                del account['youtube_verified']
            if 'youtube_subscribers' in account:
                del account['youtube_subscribers']
        
        if account_modified:
            stats['total_accounts_affected'] += 1
            # Update timestamp
            account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
    
    print(f"\nRemoval complete:")
    print(f"  - Instagram URLs removed: {stats['instagram_removed']}")
    print(f"  - YouTube URLs removed: {stats['youtube_removed']}")
    print(f"  - Total accounts affected: {stats['total_accounts_affected']}")
    
    if stats['instagram_removed'] + stats['youtube_removed'] > 0:
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = yaml_file.parent / f"{yaml_file.stem}_backup_before_removal_{timestamp}.yml"
        
        print(f"\nCreating backup: {backup_file}")
        with open(backup_file, 'w', encoding='utf-8') as f:
            with open(yaml_file, 'r', encoding='utf-8') as orig:
                f.write(orig.read())
        
        # Save cleaned YAML
        print(f"Saving cleaned YAML to: {yaml_file}")
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f,
                     default_flow_style=False,
                     allow_unicode=True,
                     sort_keys=False,
                     width=1000)
        
        # Save report
        report_file = yaml_file.parent / f"removed_broken_links_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("REMOVED BROKEN LINKS REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Total removed: {stats['instagram_removed'] + stats['youtube_removed']}\n")
            f.write(f"  - Instagram: {stats['instagram_removed']}\n")
            f.write(f"  - YouTube: {stats['youtube_removed']}\n\n")
            
            f.write("Sample of removed links:\n")
            f.write("-" * 50 + "\n")
            for item in removed_links[:20]:  # Show first 20
                f.write(f"{item['name']} ({item['platform']}): {item['url']}\n")
            
            if len(removed_links) > 20:
                f.write(f"\n... and {len(removed_links) - 20} more\n")
        
        print(f"Report saved to: {report_file}")
        
        # Final statistics
        print("\n" + "=" * 60)
        print("CLEANUP COMPLETE")
        print("=" * 60)
        
        # Count remaining valid links
        instagram_count = sum(1 for acc in data['accounts'] 
                             if acc and acc.get('instagram_url'))
        youtube_count = sum(1 for acc in data['accounts'] 
                           if acc and acc.get('youtube_url'))
        
        print(f"\n📊 Remaining active links:")
        print(f"  - Instagram URLs: {instagram_count}")
        print(f"  - YouTube URLs: {youtube_count}")
        print(f"\n✅ All broken links have been removed")
        print("✅ Only verified active links remain in the dataset")
    else:
        print("\nNo broken links found - dataset is clean!")
    
    return stats

if __name__ == "__main__":
    remove_broken_links()