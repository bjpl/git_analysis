"""
Add confirmed Instagram accounts to the Spanish accounts dataset
"""

import yaml
from pathlib import Path
from datetime import datetime

def add_instagram_accounts():
    """Add newly confirmed Instagram URLs to accounts"""
    
    yaml_file = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml")
    
    # Define the new Instagram URLs to add
    instagram_updates = {
        # Government accounts
        '@minhacienda': 'https://instagram.com/minhacienda',
        '@minticscolombia': 'https://instagram.com/ministerio_tic',
        '@mintransporteco': 'https://instagram.com/mintransporteco',
        '@presidenciamx': 'https://instagram.com/gobmexico',
        '@hacienda_mexico': 'https://instagram.com/shcp_mx',
        '@sct_mx': 'https://instagram.com/sict_mx',
        '@semarnat_mexico': 'https://instagram.com/semarnat_mexico',
        '@economía.mexico': 'https://instagram.com/secretariaeconomia',
        
        # Cultural institutions
        '@museodeloro': 'https://instagram.com/museodeloro',
        '@elmamm': 'https://instagram.com/elmamm',
        '@bibliotecaluisangelarango': 'https://instagram.com/bibliotecaluisangelarango',
        '@museumofmodernart': 'https://instagram.com/themuseumofmodernart',
        '@parquescolombia': 'https://instagram.com/parquescolombia',
        
        # Tourism accounts
        '@visitarmedellin': 'https://instagram.com/medellin_travel',
        '@medellin_guru': 'https://instagram.com/medellin_guru',
        '@visitperu': 'https://instagram.com/peru',
        '@chiletravel': 'https://instagram.com/chiletravel',
        '@visitcostarica': 'https://instagram.com/visit_costarica',
        '@uruguaynatural': 'https://instagram.com/uruguaynaturalmt',
        
        # Additional museums
        '@mnantropologia': 'https://instagram.com/mnantropologia',
        '@munal': 'https://instagram.com/munalmx',
        '@museoreinasofia': 'https://instagram.com/museoreinasofia',
        '@inahmx': 'https://instagram.com/inahmx',
        '@inbamx': 'https://instagram.com/inbamx',
        '@museofridakahlo': 'https://instagram.com/museofridakahlo',
        '@museodeartelima': 'https://instagram.com/museodeartelima'
    }
    
    print("Loading YAML file...")
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    added_count = 0
    not_found = []
    already_has = []
    
    print("\nAdding Instagram URLs...")
    for account in data.get('accounts', []):
        if not account:
            continue
        
        handle = account.get('handle', '')
        
        # Check if this account needs an Instagram URL
        if handle in instagram_updates:
            if not account.get('instagram_url'):
                # Add the Instagram URL
                account['instagram_url'] = instagram_updates[handle]
                account['instagram_manually_added'] = True
                account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                added_count += 1
                print(f"✓ Added Instagram for: {account.get('name', handle)}")
            else:
                already_has.append(account.get('name', handle))
    
    # Check if any handles weren't found
    found_handles = set(acc.get('handle', '') for acc in data['accounts'] if acc)
    for handle in instagram_updates.keys():
        if handle not in found_handles:
            not_found.append(handle)
    
    print(f"\n📊 Results:")
    print(f"  - Added Instagram URLs: {added_count}")
    print(f"  - Already had Instagram: {len(already_has)}")
    print(f"  - Handles not found: {len(not_found)}")
    
    if not_found:
        print(f"\n⚠️  Handles not found in dataset:")
        for handle in not_found:
            print(f"  - {handle}")
    
    if added_count > 0:
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = yaml_file.parent / f"{yaml_file.stem}_backup_before_instagram_{timestamp}.yml"
        
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
        report_file = yaml_file.parent / f"instagram_additions_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("INSTAGRAM ACCOUNTS ADDED\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total added: {added_count}\n\n")
            
            f.write("Added accounts:\n")
            for account in data['accounts']:
                if account and account.get('instagram_manually_added'):
                    f.write(f"- {account.get('name', 'Unknown')}: {account['instagram_url']}\n")
        
        print(f"Report saved to: {report_file}")
        
        # Final statistics
        print("\n" + "=" * 60)
        print("UPDATE COMPLETE")
        print("=" * 60)
        
        # Count current Instagram coverage
        instagram_count = sum(1 for acc in data['accounts'] 
                             if acc and acc.get('instagram_url'))
        total_accounts = len([a for a in data['accounts'] if a])
        
        print(f"\n📊 New Instagram coverage:")
        print(f"  - Total Instagram URLs: {instagram_count}/{total_accounts} ({instagram_count/total_accounts*100:.1f}%)")
        print(f"  - Increase: +{added_count} accounts")
    else:
        print("\nNo new Instagram URLs added")
    
    return added_count

if __name__ == "__main__":
    add_instagram_accounts()