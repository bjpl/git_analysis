"""
Add new Instagram accounts that don't exist in the dataset yet
"""

import yaml
from pathlib import Path
from datetime import datetime

def add_new_instagram_accounts():
    """Add new accounts with Instagram URLs to the dataset"""
    
    yaml_file = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml")
    
    # New accounts to add to the dataset
    new_accounts = [
        {
            'handle': '@maccosmeticsco',
            'name': 'MAC Cosmetics Colombia',
            'instagram_url': 'https://instagram.com/maccosmeticsco',
            'instagram_followers': 85000,
            'category': 'Beauty',
            'description': 'MAC Cosmetics official account for Colombia'
        },
        {
            'handle': '@toyotacol',
            'name': 'Toyota Colombia',
            'instagram_url': 'https://instagram.com/toyotacolombia',
            'instagram_followers': 158000,
            'category': 'Automotive',
            'description': 'Toyota official account for Colombia'
        },
        {
            'handle': '@nissancol',
            'name': 'Nissan Colombia',
            'instagram_url': 'https://instagram.com/nissancolombia',
            'instagram_followers': 130000,
            'category': 'Automotive',
            'description': 'Nissan official account for Colombia'
        },
        {
            'handle': '@ikeacol',
            'name': 'IKEA Colombia',
            'instagram_url': 'https://instagram.com/ikeacolombia',
            'instagram_followers': 298000,
            'category': 'Retail',
            'description': 'IKEA furniture and home goods in Colombia'
        },
        {
            'handle': '@clarocol',
            'name': 'Claro Colombia',
            'instagram_url': 'https://instagram.com/clarocolombia',
            'instagram_followers': 237000,
            'category': 'Telecommunications',
            'description': 'Claro telecommunications services in Colombia'
        },
        {
            'handle': '@grupoexito',
            'name': 'Grupo Éxito',
            'instagram_url': 'https://instagram.com/grupoexito',
            'instagram_followers': 67000,
            'category': 'Retail',
            'description': 'Grupo Éxito retail corporation'
        },
        {
            'handle': '@postobon',
            'name': 'Postobón',
            'instagram_url': 'https://instagram.com/postobonempresa',
            'instagram_followers': 79000,
            'category': 'Beverages',
            'description': 'Postobón beverages company'
        },
        {
            'handle': '@juanvaldez',
            'name': 'Juan Valdez Café',
            'instagram_url': 'https://instagram.com/juanvaldezcafe',
            'instagram_followers': 564000,
            'category': 'Food & Beverage',
            'description': 'Juan Valdez Colombian coffee shops and products'
        },
        {
            'handle': '@segurossura',
            'name': 'Seguros SURA',
            'instagram_url': 'https://instagram.com/segurossura',
            'instagram_followers': 98000,
            'category': 'Insurance',
            'description': 'SURA insurance services in Colombia'
        },
        {
            'handle': '@unalbogota',
            'name': 'UNAL Bogotá',
            'instagram_url': 'https://instagram.com/bogotaunal',
            'instagram_followers': 25000,
            'category': 'Education',
            'description': 'Universidad Nacional de Colombia - Bogotá campus'
        }
    ]
    
    print("Loading YAML file...")
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if 'accounts' not in data:
        data['accounts'] = []
    
    # Add timestamp to new accounts
    for account in new_accounts:
        account['instagram_manually_added'] = True
        account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
    
    # Check for duplicates before adding
    existing_handles = set(acc.get('handle', '') for acc in data['accounts'] if acc)
    existing_instagram = set(acc.get('instagram_url', '') for acc in data['accounts'] if acc and acc.get('instagram_url'))
    
    added_count = 0
    skipped_count = 0
    
    print("\nAdding new accounts...")
    for new_account in new_accounts:
        # Check if handle or Instagram URL already exists
        if new_account['handle'] in existing_handles:
            print(f"⚠️  Skipping {new_account['name']} - handle already exists")
            skipped_count += 1
        elif new_account['instagram_url'] in existing_instagram:
            print(f"⚠️  Skipping {new_account['name']} - Instagram URL already exists")
            skipped_count += 1
        else:
            # Add the new account
            data['accounts'].append(new_account)
            added_count += 1
            print(f"✓ Added: {new_account['name']} ({new_account['instagram_followers']:,} followers)")
            existing_handles.add(new_account['handle'])
            existing_instagram.add(new_account['instagram_url'])
    
    print(f"\n📊 Results:")
    print(f"  - New accounts added: {added_count}")
    print(f"  - Skipped (duplicates): {skipped_count}")
    
    if added_count > 0:
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = yaml_file.parent / f"{yaml_file.stem}_backup_new_accounts_{timestamp}.yml"
        
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
        
        # Generate report
        report_file = yaml_file.parent / f"new_accounts_report_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("NEW ACCOUNTS ADDED TO DATASET\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total new accounts: {added_count}\n\n")
            
            f.write("Accounts added (sorted by followers):\n")
            added_sorted = sorted(new_accounts, key=lambda x: x.get('instagram_followers', 0), reverse=True)
            for account in added_sorted:
                f.write(f"- {account['name']}: {account.get('instagram_followers', 0):,} followers\n")
                f.write(f"  Category: {account['category']}\n")
                f.write(f"  Instagram: {account['instagram_url']}\n\n")
        
        print(f"Report saved to: {report_file}")
        
        # Final statistics
        print("\n" + "=" * 60)
        print("NEW ACCOUNTS ADDED SUCCESSFULLY")
        print("=" * 60)
        
        # Count current coverage
        total_accounts = len([a for a in data['accounts'] if a])
        instagram_count = sum(1 for acc in data['accounts'] 
                             if acc and acc.get('instagram_url'))
        
        print(f"\n📊 Updated dataset statistics:")
        print(f"  - Total accounts: {total_accounts} (+{added_count})")
        print(f"  - Instagram coverage: {instagram_count}/{total_accounts} ({instagram_count/total_accounts*100:.1f}%)")
        
        # Show top new accounts
        print(f"\n🌟 Top new accounts by followers:")
        for account in added_sorted[:5]:
            print(f"  - {account['name']}: {account.get('instagram_followers', 0):,} followers")
    else:
        print("\nNo new accounts were added")
    
    return added_count

if __name__ == "__main__":
    add_new_instagram_accounts()