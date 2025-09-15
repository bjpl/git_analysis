"""
Add final batch of confirmed Instagram accounts and remove unconfirmed ones
"""

import yaml
from pathlib import Path
from datetime import datetime

def add_final_instagram_batch():
    """Add final confirmed Instagram URLs and remove unconfirmed accounts"""
    
    yaml_file = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml")
    
    # Define confirmed Instagram URLs with follower counts
    instagram_updates = {
        # Cultural institutions
        '@cenart': {'url': 'https://instagram.com/cenartmx', 'followers': None},
        '@ccemx': {'url': 'https://instagram.com/ccemx_', 'followers': None},
        
        # Retail stores
        '@liverpool': {'url': 'https://instagram.com/liverpool_mexico', 'followers': 2000000},
        '@elpalaciodehierro': {'url': 'https://instagram.com/elpalaciodehierro', 'followers': 649000},
        '@sanborns': {'url': 'https://instagram.com/solosanborns', 'followers': 363000},
        '@coppel': {'url': 'https://instagram.com/coppel', 'followers': 644000},
        '@falabella': {'url': 'https://instagram.com/falabella_cl', 'followers': 1000000},
        '@grupoexito': {'url': 'https://instagram.com/grupoexito', 'followers': 67000},
        '@exito': {'url': 'https://instagram.com/exito', 'followers': 599000},
        
        # Regional governments
        '@veracruz': {'url': 'https://instagram.com/gobiernodeveracruz', 'followers': 8956},
        '@guanajuato': {'url': 'https://instagram.com/gobiernogto', 'followers': 31000},
        '@cundinamarca': {'url': 'https://instagram.com/cundinamarcagob', 'followers': 62000},
        '@antioquia': {'url': 'https://instagram.com/gobantioquia', 'followers': 247000},
        '@vallegob': {'url': 'https://instagram.com/gobvalle', 'followers': 139000},
        '@atlantico': {'url': 'https://instagram.com/gobatlantico', 'followers': 138000},
        
        # Institutions
        '@casareal': {'url': 'https://instagram.com/casareal.es', 'followers': None},
        '@canalcongreso': {'url': 'https://instagram.com/canalcongresomx', 'followers': 30000},
        '@policiacol': {'url': 'https://instagram.com/policiadecolombia', 'followers': 657000},
        '@guardiamx': {'url': 'https://instagram.com/gn_mexico_', 'followers': 179000},
        
        # Festivals
        '@cervantino': {'url': 'https://instagram.com/cervantino', 'followers': 67000},
        '@vivelatino': {'url': 'https://instagram.com/vivelatino', 'followers': 522000},
        '@rockalparque': {'url': 'https://instagram.com/rockalparqueoficial', 'followers': 196000},
        
        # Football clubs
        '@clubamerica': {'url': 'https://instagram.com/clubamerica', 'followers': 6000000},
        '@chivas': {'url': 'https://instagram.com/chivas', 'followers': 4000000},
        '@pumas': {'url': 'https://instagram.com/pumasmx', 'followers': 1000000},
        '@bocajuniors': {'url': 'https://instagram.com/bocajrs', 'followers': 10000000},
        '@riverplate': {'url': 'https://instagram.com/riverplate', 'followers': 9000000},
        
        # Radio stations
        '@wradio': {'url': 'https://instagram.com/wradioco', 'followers': 899000},
        '@radioformula': {'url': 'https://instagram.com/radioformulamx', 'followers': 497000},
        '@caracolradio': {'url': 'https://instagram.com/caracolradio', 'followers': 921000},
        
        # Brands and Companies
        '@bancolombia': {'url': 'https://instagram.com/bancolombia', 'followers': 496000},
        '@bimbo': {'url': 'https://instagram.com/bimbo_mexico', 'followers': 119000},
        '@cocacolacol': {'url': 'https://instagram.com/cocacolacol', 'followers': 248000},
        '@pepsicol': {'url': 'https://instagram.com/pepsicolombia', 'followers': 66000},
        '@oreocol': {'url': 'https://instagram.com/oreo.colombia', 'followers': 67000},
        '@redbullcol': {'url': 'https://instagram.com/redbullcol', 'followers': 373000},
        '@gatoradecol': {'url': 'https://instagram.com/gatoradecolombia', 'followers': 84000},
        '@huaweicol': {'url': 'https://instagram.com/huaweimobileco', 'followers': 387000},
        '@xiaomicol': {'url': 'https://instagram.com/xiaomi.colombia', 'followers': 492000},
        '@pumacol': {'url': 'https://instagram.com/pumacolombia', 'followers': 445000},
        '@northfacecol': {'url': 'https://instagram.com/thenorthfacecol', 'followers': 148000},
        '@netflixlat': {'url': 'https://instagram.com/netflixlat', 'followers': 25000000}
    }
    
    # Accounts to remove (couldn't be confirmed or don't exist)
    accounts_to_remove = [
        '@chiapas',  # No official Instagram found
        '@santander',  # No specific Instagram found
        '@bolivar',  # No specific Instagram found
        '@institutocervantes',  # No main account found
        '@tvsenado',  # No Instagram found
        '@ejercitomx',  # No specific Instagram found
        '@grupomodelo',  # No official Instagram found
        '@corona',  # No separate official Instagram
        '@applecol',  # No official Apple Colombia Instagram
        '@nikecol',  # No official Nike Colombia Instagram
        '@monstercol',  # Inactive account with 0 posts
        '@netflixcol',  # Private/inactive account
        '@columbiasportswear',  # Unable to verify
        '@disneyplus',  # Unable to verify
        '@universalpictures',  # Unable to verify
        '@sonypictures'  # Unable to verify
    ]
    
    print("Loading YAML file...")
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    added_count = 0
    updated_count = 0
    removed_count = 0
    not_found = []
    
    print("\nProcessing Instagram additions...")
    for account in data.get('accounts', []):
        if not account:
            continue
        
        handle = account.get('handle', '')
        
        # Check if this account needs an Instagram URL
        if handle in instagram_updates:
            update_info = instagram_updates[handle]
            
            if not account.get('instagram_url'):
                # Add new Instagram URL
                account['instagram_url'] = update_info['url']
                if update_info['followers']:
                    account['instagram_followers'] = update_info['followers']
                account['instagram_manually_added'] = True
                account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                added_count += 1
                print(f"✓ Added Instagram for: {account.get('name', handle)} ({update_info.get('followers', 'N/A')} followers)")
            elif account.get('instagram_url') != update_info['url']:
                # Update existing URL
                account['instagram_url'] = update_info['url']
                if update_info['followers']:
                    account['instagram_followers'] = update_info['followers']
                account['instagram_corrected'] = True
                account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                updated_count += 1
                print(f"✓ Updated Instagram for: {account.get('name', handle)}")
    
    print("\nRemoving unconfirmed accounts...")
    # Remove unconfirmed accounts
    accounts_to_keep = []
    for account in data.get('accounts', []):
        if not account:
            continue
        
        handle = account.get('handle', '')
        
        if handle in accounts_to_remove:
            # Remove Instagram URL if it exists
            if account.get('instagram_url'):
                print(f"✗ Removing unconfirmed Instagram for: {account.get('name', handle)}")
                del account['instagram_url']
                if 'instagram_followers' in account:
                    del account['instagram_followers']
                if 'instagram_verified' in account:
                    del account['instagram_verified']
                if 'instagram_manually_added' in account:
                    del account['instagram_manually_added']
                account['instagram_removed'] = True
                account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                removed_count += 1
        
        accounts_to_keep.append(account)
    
    data['accounts'] = accounts_to_keep
    
    # Check if any handles weren't found
    found_handles = set(acc.get('handle', '') for acc in data['accounts'] if acc)
    for handle in instagram_updates.keys():
        if handle not in found_handles:
            not_found.append(handle)
    
    print(f"\n📊 Results:")
    print(f"  - Added Instagram URLs: {added_count}")
    print(f"  - Updated Instagram URLs: {updated_count}")
    print(f"  - Removed unconfirmed URLs: {removed_count}")
    print(f"  - Handles not found: {len(not_found)}")
    
    if not_found:
        print(f"\n⚠️  Handles not found in dataset:")
        for handle in not_found:
            print(f"  - {handle}")
    
    if added_count + updated_count + removed_count > 0:
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = yaml_file.parent / f"{yaml_file.stem}_backup_final_{timestamp}.yml"
        
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
        report_file = yaml_file.parent / f"instagram_final_batch_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("FINAL INSTAGRAM BATCH UPDATE\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total added: {added_count}\n")
            f.write(f"Total updated: {updated_count}\n")
            f.write(f"Total removed: {removed_count}\n\n")
            
            f.write("Top accounts by followers:\n")
            top_accounts = []
            for acc in data['accounts']:
                if acc and acc.get('instagram_followers'):
                    top_accounts.append((acc.get('name'), acc['instagram_followers']))
            
            top_accounts.sort(key=lambda x: x[1], reverse=True)
            for name, followers in top_accounts[:10]:
                f.write(f"- {name}: {followers:,} followers\n")
            
            f.write(f"\nRemoved accounts (unconfirmed):\n")
            for handle in accounts_to_remove:
                f.write(f"- {handle}\n")
        
        print(f"Report saved to: {report_file}")
        
        # Final statistics
        print("\n" + "=" * 60)
        print("FINAL UPDATE COMPLETE")
        print("=" * 60)
        
        # Count current Instagram coverage
        instagram_count = sum(1 for acc in data['accounts'] 
                             if acc and acc.get('instagram_url'))
        total_accounts = len([a for a in data['accounts'] if a])
        
        print(f"\n📊 Final Instagram coverage:")
        print(f"  - Total Instagram URLs: {instagram_count}/{total_accounts} ({instagram_count/total_accounts*100:.1f}%)")
        print(f"  - Net change: +{added_count} added, -{removed_count} removed")
        
        # Show top accounts
        print(f"\n🌟 Highest follower accounts added:")
        high_follower = []
        for handle, info in instagram_updates.items():
            if info.get('followers') and info['followers'] > 500000:
                for acc in data['accounts']:
                    if acc and acc.get('handle') == handle:
                        high_follower.append((acc.get('name'), info['followers']))
                        break
        
        high_follower.sort(key=lambda x: x[1], reverse=True)
        for name, followers in high_follower[:5]:
            print(f"  - {name}: {followers:,} followers")
    else:
        print("\nNo changes made")
    
    return added_count, updated_count, removed_count

if __name__ == "__main__":
    add_final_instagram_batch()