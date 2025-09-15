"""
Fix TransMilenio Instagram URL to the correct handle
"""

import yaml
from pathlib import Path
from datetime import datetime

def fix_transmilenio_instagram():
    """Update TransMilenio with the correct Instagram handle"""
    
    yaml_file = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml")
    
    print("Loading YAML file...")
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    updated = False
    
    print("\nSearching for TransMilenio account...")
    for account in data.get('accounts', []):
        if not account:
            continue
        
        # Look for TransMilenio by name or handle
        if ('transmilenio' in account.get('name', '').lower() or 
            'transmilenio' in account.get('handle', '').lower() or
            'transmilenio' in account.get('instagram_url', '').lower()):
            
            print(f"Found: {account.get('name', 'Unknown')}")
            print(f"  Current Instagram: {account.get('instagram_url', 'None')}")
            
            # Update to correct Instagram URL
            old_url = account.get('instagram_url', '')
            new_url = 'https://instagram.com/oficialtransmilenio'
            
            if old_url != new_url:
                account['instagram_url'] = new_url
                account['instagram_corrected'] = True
                account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                
                # Update handle if needed
                if account.get('handle') != '@transmilenio':
                    account['handle'] = '@transmilenio'
                
                updated = True
                print(f"  ✓ Updated to: {new_url}")
                print(f"  ✓ Corrected handle: @transmilenio")
            else:
                print("  Already has correct URL")
            
            break
    else:
        print("TransMilenio account not found in dataset")
    
    if updated:
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = yaml_file.parent / f"{yaml_file.stem}_backup_transmilenio_{timestamp}.yml"
        
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
        print("TRANSMILENIO INSTAGRAM FIXED")
        print("=" * 60)
        print("✓ Updated to correct handle: @oficialtransmilenio")
        print("✓ URL: https://instagram.com/oficialtransmilenio")
        
        # Count current coverage
        total_accounts = len([a for a in data['accounts'] if a])
        instagram_count = sum(1 for acc in data['accounts'] 
                             if acc and acc.get('instagram_url'))
        
        print(f"\n📊 Dataset statistics remain:")
        print(f"  - Total accounts: {total_accounts}")
        print(f"  - Instagram coverage: {instagram_count}/{total_accounts} ({instagram_count/total_accounts*100:.1f}%)")
    else:
        print("\nNo updates needed")
    
    return updated

if __name__ == "__main__":
    fix_transmilenio_instagram()