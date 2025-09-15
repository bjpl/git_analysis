"""
Fix incorrectly mapped YouTube URLs that are actually Instagram URLs
"""

import yaml
from pathlib import Path
from datetime import datetime

def fix_youtube_urls():
    """Remove YouTube URLs that are actually Instagram URLs"""
    
    yaml_file = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml")
    
    print("Loading YAML file...")
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    fixed_count = 0
    removed_urls = []
    
    print("Checking and fixing YouTube URLs...")
    for account in data.get('accounts', []):
        if not account:
            continue
            
        # Check if YouTube URL is actually an Instagram URL
        youtube_url = account.get('youtube_url', '')
        if youtube_url and 'instagram.com' in youtube_url:
            # This is wrong - remove it
            removed_urls.append({
                'name': account.get('name', 'Unknown'),
                'wrong_url': youtube_url
            })
            
            # Remove the incorrect YouTube URL
            del account['youtube_url']
            
            # Also remove related YouTube fields that were incorrectly added
            if 'youtube_verified' in account:
                del account['youtube_verified']
            if 'youtube_discovered' in account:
                del account['youtube_discovered']
            if 'youtube_subscribers' in account:
                del account['youtube_subscribers']
                
            fixed_count += 1
            
            # Update the last_updated field
            account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
    
    print(f"\nFixed {fixed_count} incorrect YouTube URLs")
    
    if fixed_count > 0:
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = yaml_file.parent / f"{yaml_file.stem}_backup_before_fix_{timestamp}.yml"
        
        print(f"Creating backup: {backup_file}")
        with open(backup_file, 'w', encoding='utf-8') as f:
            with open(yaml_file, 'r', encoding='utf-8') as orig:
                f.write(orig.read())
        
        # Save fixed YAML
        print(f"Saving fixed YAML to: {yaml_file}")
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f,
                     default_flow_style=False,
                     allow_unicode=True,
                     sort_keys=False,
                     width=1000)
        
        # Save report of removed URLs
        report_file = yaml_file.parent / f"removed_youtube_urls_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("REMOVED INCORRECT YOUTUBE URLs\n")
            f.write("=" * 50 + "\n")
            f.write(f"Total removed: {fixed_count}\n\n")
            
            for item in removed_urls[:10]:  # Show first 10 as examples
                f.write(f"{item['name']}: {item['wrong_url']}\n")
            
            if len(removed_urls) > 10:
                f.write(f"\n... and {len(removed_urls) - 10} more\n")
        
        print(f"Report saved to: {report_file}")
        
        # Show summary
        print("\n" + "=" * 60)
        print("FIX COMPLETE")
        print("=" * 60)
        print(f"✓ Removed {fixed_count} incorrect YouTube URLs")
        print(f"✓ All were Instagram URLs wrongly mapped as YouTube")
        print(f"✓ Backup created before changes")
        print(f"✓ YAML file has been fixed")
        
        # Count remaining valid YouTube URLs
        valid_youtube = sum(1 for acc in data['accounts'] 
                          if acc and acc.get('youtube_url') and 'youtube.com' in acc.get('youtube_url', ''))
        print(f"\n📊 Remaining valid YouTube URLs: {valid_youtube}")
    else:
        print("No incorrect YouTube URLs found - nothing to fix")
    
    return fixed_count

if __name__ == "__main__":
    fix_youtube_urls()