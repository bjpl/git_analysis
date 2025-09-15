"""
Add more confirmed Instagram accounts with corrected handles
"""

import yaml
from pathlib import Path
from datetime import datetime

def add_more_instagram_accounts():
    """Add additional confirmed Instagram URLs to accounts"""
    
    yaml_file = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml")
    
    # Define the Instagram URLs to add with follower counts
    instagram_updates = {
        # TV/Media accounts
        '@canal11': {'url': 'https://instagram.com/canaloncetv', 'followers': 373000},
        '@canal22': {'url': 'https://instagram.com/canal22oficial', 'followers': 276000},
        '@lasestrellas': {'url': 'https://instagram.com/canalestrellas', 'followers': 4000000},
        '@imagentv': {'url': 'https://instagram.com/imagentvmex', 'followers': None},
        '@imagennoticias': {'url': 'https://instagram.com/imagentvnoticias', 'followers': 121000},
        '@multimedios': {'url': 'https://instagram.com/multimediostv', 'followers': 928000},
        '@univision': {'url': 'https://instagram.com/univision', 'followers': 7000000},
        '@tudn': {'url': 'https://instagram.com/tudnmex', 'followers': 2000000},
        '@telemundo': {'url': 'https://instagram.com/telemundo', 'followers': 15000000},
        '@ipn': {'url': 'https://instagram.com/ipn_oficial', 'followers': 205000},
        
        # Universities
        '@unal': {'url': 'https://instagram.com/unaloficial', 'followers': 125000},
        '@uniandes': {'url': 'https://instagram.com/uniandes', 'followers': 149000},
        '@javeriana': {'url': 'https://instagram.com/unijaveriana', 'followers': 107000},
        '@pucchile': {'url': 'https://instagram.com/ucatolicaoficial', 'followers': 122000},
        '@pucp': {'url': 'https://instagram.com/pucp', 'followers': 144000},
        '@usp': {'url': 'https://instagram.com/usp.oficial', 'followers': 451000},
        
        # News outlets
        '@milenio': {'url': 'https://instagram.com/milenio', 'followers': 979000},
        '@excelsior': {'url': 'https://instagram.com/periodicoexcelsior', 'followers': 204000},
        '@elfinanciero': {'url': 'https://instagram.com/elfinanciero_mx', 'followers': 464000},
        '@eltiempo': {'url': 'https://instagram.com/eltiempo', 'followers': 3000000},
        '@elespectador': {'url': 'https://instagram.com/elespectador', 'followers': 2000000},
        '@elcomercio': {'url': 'https://instagram.com/elcomercio', 'followers': 2000000},
        '@elmercurio': {'url': 'https://instagram.com/elmercurio_dep', 'followers': None},
        '@latercera': {'url': 'https://instagram.com/laterceracom', 'followers': 678000},
        
        # Sports/Football federations
        '@afa': {'url': 'https://instagram.com/afaseleccion', 'followers': 15000000},
        '@anfp': {'url': 'https://instagram.com/anfp_chile', 'followers': None},
        '@fpf': {'url': 'https://instagram.com/tufpf_oficial', 'followers': 37000},
        '@fedmexfut': {'url': 'https://instagram.com/fmf', 'followers': 340000},
        
        # Transportation/Business
        '@avianca': {'url': 'https://instagram.com/avianca', 'followers': 1000000},
        '@scotiabank': {'url': 'https://instagram.com/scotiabankmx', 'followers': 24000},
        '@metrosantiago': {'url': 'https://instagram.com/metrodesantiago', 'followers': 376000},
        '@metrolima': {'url': 'https://instagram.com/linea1oficial', 'followers': 12000},
        '@transmilenio': {'url': 'https://instagram.com/transmilenio', 'followers': 73000}
    }
    
    print("Loading YAML file...")
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    added_count = 0
    updated_count = 0
    not_found = []
    
    print("\nProcessing Instagram URLs...")
    for account in data.get('accounts', []):
        if not account:
            continue
        
        handle = account.get('handle', '')
        
        # Check if this account needs an Instagram URL update
        if handle in instagram_updates:
            update_info = instagram_updates[handle]
            
            # Check if URL needs to be added or updated
            current_url = account.get('instagram_url', '')
            new_url = update_info['url']
            
            if not current_url:
                # Add new Instagram URL
                account['instagram_url'] = new_url
                if update_info['followers']:
                    account['instagram_followers'] = update_info['followers']
                account['instagram_manually_added'] = True
                account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                added_count += 1
                print(f"✓ Added Instagram for: {account.get('name', handle)} ({update_info.get('followers', 'N/A')} followers)")
            elif current_url != new_url:
                # Update existing URL if different
                account['instagram_url'] = new_url
                if update_info['followers']:
                    account['instagram_followers'] = update_info['followers']
                account['instagram_corrected'] = True
                account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                updated_count += 1
                print(f"✓ Updated Instagram for: {account.get('name', handle)} ({update_info.get('followers', 'N/A')} followers)")
    
    # Check if any handles weren't found
    found_handles = set(acc.get('handle', '') for acc in data['accounts'] if acc)
    for handle in instagram_updates.keys():
        if handle not in found_handles:
            not_found.append(handle)
    
    print(f"\n📊 Results:")
    print(f"  - Added Instagram URLs: {added_count}")
    print(f"  - Updated Instagram URLs: {updated_count}")
    print(f"  - Handles not found: {len(not_found)}")
    
    if not_found:
        print(f"\n⚠️  Handles not found in dataset:")
        for handle in not_found:
            print(f"  - {handle}")
    
    if added_count + updated_count > 0:
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = yaml_file.parent / f"{yaml_file.stem}_backup_more_instagram_{timestamp}.yml"
        
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
        report_file = yaml_file.parent / f"instagram_additions_batch2_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("INSTAGRAM ACCOUNTS ADDED/UPDATED - BATCH 2\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total added: {added_count}\n")
            f.write(f"Total updated: {updated_count}\n\n")
            
            f.write("Accounts with high follower counts:\n")
            for account in data['accounts']:
                if account and (account.get('instagram_manually_added') or account.get('instagram_corrected')):
                    followers = account.get('instagram_followers', 0)
                    if followers and followers > 100000:
                        f.write(f"- {account.get('name', 'Unknown')}: {followers:,} followers\n")
        
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
        print(f"  - Net increase: +{added_count} new accounts")
        
        # Show top accounts by followers
        print(f"\n🌟 Top accounts added (by followers):")
        top_accounts = []
        for acc in data['accounts']:
            if acc and (acc.get('instagram_manually_added') or acc.get('instagram_corrected')):
                if acc.get('instagram_followers'):
                    top_accounts.append((acc.get('name'), acc['instagram_followers']))
        
        top_accounts.sort(key=lambda x: x[1], reverse=True)
        for name, followers in top_accounts[:5]:
            print(f"  - {name}: {followers:,} followers")
    else:
        print("\nNo Instagram URLs added or updated")
    
    return added_count + updated_count

if __name__ == "__main__":
    add_more_instagram_accounts()