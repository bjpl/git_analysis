"""
Add Team Foods Mexico Instagram URL
"""

import yaml
from pathlib import Path
from datetime import datetime

def add_teamfoods_instagram():
    """Add Team Foods Mexico with correct Instagram URL"""
    
    yaml_file = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml")
    
    print("Loading YAML file...")
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Check if Team Foods already exists
    found = False
    for account in data.get('accounts', []):
        if not account:
            continue
        
        if 'teamfoods' in account.get('handle', '').lower() or 'team foods' in account.get('name', '').lower():
            found = True
            print(f"Found existing: {account.get('name')}")
            account['instagram_url'] = 'https://instagram.com/teamfoodsmx'
            account['instagram_manually_added'] = True
            account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
            print("✓ Updated Instagram URL")
            break
    
    if not found:
        # Add new account
        new_account = {
            'handle': '@teamfoods',
            'name': 'Team Foods Mexico',
            'instagram_url': 'https://instagram.com/teamfoodsmx',
            'category': 'Food & Beverage',
            'description': 'Team Foods Mexico - Food products company',
            'instagram_manually_added': True,
            'last_updated': datetime.now().strftime("%Y-%m-%d")
        }
        
        data['accounts'].append(new_account)
        print("✓ Added new account: Team Foods Mexico")
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = yaml_file.parent / f"{yaml_file.stem}_backup_teamfoods_{timestamp}.yml"
    
    print(f"\nCreating backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        with open(yaml_file, 'r', encoding='utf-8') as orig:
            f.write(orig.read())
    
    # Save updated YAML
    print(f"Saving updated YAML...")
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
    
    print("\n" + "=" * 60)
    print("TEAM FOODS ADDED")
    print("=" * 60)
    print("✓ Instagram URL: https://instagram.com/teamfoodsmx")
    
    # Count coverage
    total_accounts = len([a for a in data['accounts'] if a])
    instagram_count = sum(1 for acc in data['accounts'] if acc and acc.get('instagram_url'))
    
    print(f"\n📊 Dataset statistics:")
    print(f"  - Total accounts: {total_accounts}")
    print(f"  - Instagram coverage: {instagram_count}/{total_accounts} ({instagram_count/total_accounts*100:.1f}%)")

if __name__ == "__main__":
    add_teamfoods_instagram()