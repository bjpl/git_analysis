"""
Fix Domino's Colombia Instagram URL
"""

import yaml
from pathlib import Path
from datetime import datetime

def fix_dominos_instagram():
    """Update Domino's Colombia with the correct Instagram handle"""
    
    yaml_file = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml")
    
    print("Loading YAML file...")
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    updated = False
    found = False
    
    print("\nSearching for Domino's accounts...")
    for account in data.get('accounts', []):
        if not account:
            continue
        
        # Look for Domino's by various possible names/handles
        name_lower = account.get('name', '').lower()
        handle_lower = account.get('handle', '').lower()
        instagram_lower = account.get('instagram_url', '').lower()
        
        if ('domino' in name_lower or 
            'domino' in handle_lower or
            'dominos_col' in instagram_lower or
            'dominosco' in instagram_lower):
            
            found = True
            print(f"Found: {account.get('name', 'Unknown')}")
            print(f"  Handle: {account.get('handle', 'Unknown')}")
            print(f"  Current Instagram: {account.get('instagram_url', 'None')}")
            
            # Update to correct Instagram URL
            old_url = account.get('instagram_url', '')
            new_url = 'https://instagram.com/dominospizzacol'
            
            if old_url != new_url:
                account['instagram_url'] = new_url
                account['instagram_corrected'] = True
                account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                
                # Update name if needed
                if 'domino' in name_lower and account.get('name') != "Domino's Pizza Colombia":
                    account['name'] = "Domino's Pizza Colombia"
                
                updated = True
                print(f"  ✓ Updated to: {new_url}")
                print(f"  ✓ Name: Domino's Pizza Colombia")
            else:
                print("  Already has correct URL")
    
    if not found:
        # Domino's doesn't exist, let's add it as a new account
        print("Domino's not found. Adding as new account...")
        
        new_account = {
            'handle': '@dominospizzacol',
            'name': "Domino's Pizza Colombia",
            'instagram_url': 'https://instagram.com/dominospizzacol',
            'category': 'Food & Beverage',
            'description': "Domino's Pizza Colombia - International pizza delivery chain",
            'instagram_manually_added': True,
            'last_updated': datetime.now().strftime("%Y-%m-%d")
        }
        
        data['accounts'].append(new_account)
        updated = True
        print(f"✓ Added new account: Domino's Pizza Colombia")
    
    if updated:
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = yaml_file.parent / f"{yaml_file.stem}_backup_dominos_{timestamp}.yml"
        
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
        print("DOMINO'S INSTAGRAM FIXED/ADDED")
        print("=" * 60)
        print("✓ Instagram URL: https://instagram.com/dominospizzacol")
        print("✓ Handle: @dominospizzacol")
        
        # Count current coverage
        total_accounts = len([a for a in data['accounts'] if a])
        instagram_count = sum(1 for acc in data['accounts'] 
                             if acc and acc.get('instagram_url'))
        youtube_count = sum(1 for acc in data['accounts'] 
                           if acc and acc.get('youtube_url'))
        
        print(f"\n📊 Dataset statistics:")
        print(f"  - Total accounts: {total_accounts}")
        print(f"  - Instagram coverage: {instagram_count}/{total_accounts} ({instagram_count/total_accounts*100:.1f}%)")
        print(f"  - YouTube coverage: {youtube_count}/{total_accounts} ({youtube_count/total_accounts*100:.1f}%)")
    else:
        print("\nNo updates needed")
    
    return updated

if __name__ == "__main__":
    fix_dominos_instagram()