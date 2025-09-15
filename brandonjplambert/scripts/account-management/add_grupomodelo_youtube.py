"""
Add Grupo Modelo YouTube URL to the dataset
"""

import yaml
from pathlib import Path
from datetime import datetime

def add_grupomodelo_youtube():
    """Add YouTube URL for Grupo Modelo"""
    
    yaml_file = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml")
    
    print("Loading YAML file...")
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    updated = False
    found = False
    
    print("\nSearching for Grupo Modelo account...")
    for account in data.get('accounts', []):
        if not account:
            continue
        
        # Look for Grupo Modelo by handle or name
        if ('grupomodelo' in account.get('handle', '').lower() or 
            'grupo modelo' in account.get('name', '').lower()):
            
            found = True
            print(f"Found: {account.get('name', 'Unknown')}")
            print(f"  Handle: {account.get('handle', 'Unknown')}")
            print(f"  Current YouTube: {account.get('youtube_url', 'None')}")
            
            # Add or update YouTube URL
            if not account.get('youtube_url'):
                account['youtube_url'] = 'https://www.youtube.com/@grupomodelo7363'
                account['youtube_manually_added'] = True
                account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                updated = True
                print(f"  ✓ Added YouTube URL: https://www.youtube.com/@grupomodelo7363")
            elif account.get('youtube_url') != 'https://www.youtube.com/@grupomodelo7363':
                account['youtube_url'] = 'https://www.youtube.com/@grupomodelo7363'
                account['youtube_corrected'] = True
                account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                updated = True
                print(f"  ✓ Updated YouTube URL to: https://www.youtube.com/@grupomodelo7363")
            else:
                print("  Already has correct YouTube URL")
            
            break
    
    if not found:
        # Grupo Modelo doesn't exist, let's add it as a new account
        print("Grupo Modelo not found. Adding as new account...")
        
        new_account = {
            'handle': '@grupomodelo',
            'name': 'Grupo Modelo',
            'youtube_url': 'https://www.youtube.com/@grupomodelo7363',
            'category': 'Beverages',
            'description': 'Grupo Modelo - Mexican brewery company, makers of Corona beer',
            'youtube_manually_added': True,
            'last_updated': datetime.now().strftime("%Y-%m-%d")
        }
        
        data['accounts'].append(new_account)
        updated = True
        print(f"✓ Added new account: Grupo Modelo with YouTube URL")
    
    if updated:
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = yaml_file.parent / f"{yaml_file.stem}_backup_grupomodelo_{timestamp}.yml"
        
        print(f"\nCreating backup: {backup_file}")
        with open(backup_file, 'w', encoding='utf-8') as f:
            with open(yaml_file, 'r', encoding='utf-8') as orig:
                f.write(orig.read())
        
        # Save updated YAML
        print(f"Saving updated YAML to: {yaml_file}")
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f,
                     default_flow_style=False,
                     allow_unicode=True,
                     sort_keys=False,
                     width=1000)
        
        print("\n" + "=" * 60)
        print("GRUPO MODELO YOUTUBE ADDED")
        print("=" * 60)
        print("✓ YouTube URL: https://www.youtube.com/@grupomodelo7363")
        
        # Count current coverage
        total_accounts = len([a for a in data['accounts'] if a])
        youtube_count = sum(1 for acc in data['accounts'] 
                           if acc and acc.get('youtube_url'))
        instagram_count = sum(1 for acc in data['accounts'] 
                             if acc and acc.get('instagram_url'))
        
        print(f"\n📊 Updated dataset statistics:")
        print(f"  - Total accounts: {total_accounts}")
        print(f"  - YouTube coverage: {youtube_count}/{total_accounts} ({youtube_count/total_accounts*100:.1f}%)")
        print(f"  - Instagram coverage: {instagram_count}/{total_accounts} ({instagram_count/total_accounts*100:.1f}%)")
    else:
        print("\nNo updates needed")
    
    return updated

if __name__ == "__main__":
    add_grupomodelo_youtube()