"""
Add additional confirmed Instagram accounts from latest batch
Only adding accounts that have been verified to exist
"""

import yaml
from pathlib import Path
from datetime import datetime

def add_additional_instagram_accounts():
    """Add additional confirmed Instagram URLs"""
    
    yaml_file = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml")
    
    # Only confirmed Instagram URLs with follower counts
    instagram_updates = {
        # Beauty/Cosmetics
        '@loreallatam': {'url': 'https://instagram.com/lorealgroupe_latam', 'followers': 120000},
        '@maccosmeticsco': {'url': 'https://instagram.com/maccosmeticsco', 'followers': 85000},
        
        # Automotive
        '@toyotacol': {'url': 'https://instagram.com/toyotacolombia', 'followers': 158000},
        '@nissancol': {'url': 'https://instagram.com/nissancolombia', 'followers': 130000},
        
        # Retail/Furniture
        '@ikeacol': {'url': 'https://instagram.com/ikeacolombia', 'followers': 298000},
        
        # Banking/Financial
        '@davivienda': {'url': 'https://instagram.com/davivienda', 'followers': 168000},
        
        # Telecommunications
        '@clarocol': {'url': 'https://instagram.com/clarocolombia', 'followers': 237000},
        
        # Retail (already tried but checking again)
        '@grupoexito': {'url': 'https://instagram.com/grupoexito', 'followers': 67000},
        
        # Beverages/Food
        '@postobon': {'url': 'https://instagram.com/postobonempresa', 'followers': 79000},
        '@juanvaldez': {'url': 'https://instagram.com/juanvaldezcafe', 'followers': 564000},
        
        # Insurance
        '@segurossura': {'url': 'https://instagram.com/segurossura', 'followers': 98000},
        
        # Universities
        '@unalbogota': {'url': 'https://instagram.com/bogotaunal', 'followers': 25000}
    }
    
    # Accounts that could NOT be verified (for documentation)
    unverified_accounts = [
        '@loreal_colombia',  # No specific Colombian account
        '@headandshoulders_colombia',  # Unable to verify
        '@pantene_colombia',  # Unable to verify
        '@mercedes_colombia',  # Unable to verify
        '@audi_colombia',  # Unable to verify
        '@hm_colombia',  # No official Instagram found
        '@massimodutti_colombia',  # Unable to verify
        '@gap_colombia',  # Unable to verify
        '@banco_caja_social',  # Unable to verify
        '@itau_colombia',  # Unable to verify
        '@copa_airlines_colombia',  # No official Instagram found
        '@ultra_air',  # Unable to verify
        '@ada_aerolinea',  # Unable to verify
        '@tigo_colombia',  # Unable to verify
        '@directv_colombia',  # Unable to verify
        '@clarotv_colombia',  # Unable to verify
        '@jumbo_colombia',  # Unable to verify
        '@d1_colombia',  # Unable to verify
        '@ara_colombia',  # Unable to verify
        '@epm',  # Unable to verify
        '@isa_colombia',  # Unable to verify
        '@xm_colombia',  # Unable to verify
        '@bavaria',  # No official Instagram found
        '@colanta',  # No official Instagram found
        '@diana',  # Unable to verify
        '@oma_cafe',  # Unable to verify
        '@crepes_waffles',  # Unable to verify
        '@sandwich_qbano',  # Unable to verify
        '@seguros_bolivar',  # Unable to verify
        '@liberty_seguros_colombia',  # Unable to verify
        '@aseguradora_solidaria'  # Unable to verify
    ]
    
    print("Loading YAML file...")
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    added_count = 0
    updated_count = 0
    not_found = []
    already_exists = []
    
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
                print(f"✓ Added Instagram for: {account.get('name', handle)} ({update_info.get('followers', 'N/A'):,} followers)")
            else:
                # Check if it's the same URL
                if account.get('instagram_url') == update_info['url']:
                    already_exists.append(account.get('name', handle))
                else:
                    # Update if different
                    account['instagram_url'] = update_info['url']
                    if update_info['followers']:
                        account['instagram_followers'] = update_info['followers']
                    account['instagram_corrected'] = True
                    account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                    updated_count += 1
                    print(f"✓ Updated Instagram for: {account.get('name', handle)}")
    
    # Check if any handles weren't found
    found_handles = set(acc.get('handle', '') for acc in data['accounts'] if acc)
    for handle in instagram_updates.keys():
        if handle not in found_handles:
            not_found.append(handle)
    
    print(f"\n📊 Results:")
    print(f"  - Added Instagram URLs: {added_count}")
    print(f"  - Updated Instagram URLs: {updated_count}")
    print(f"  - Already exists: {len(already_exists)}")
    print(f"  - Handles not found: {len(not_found)}")
    print(f"  - Unverified (not added): {len(unverified_accounts)}")
    
    if not_found:
        print(f"\n⚠️  Handles not found in dataset:")
        for handle in not_found:
            print(f"  - {handle}")
    
    if already_exists:
        print(f"\n✅ Already have Instagram for:")
        for name in already_exists[:5]:
            print(f"  - {name}")
        if len(already_exists) > 5:
            print(f"  ... and {len(already_exists) - 5} more")
    
    if added_count + updated_count > 0:
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = yaml_file.parent / f"{yaml_file.stem}_backup_additional_{timestamp}.yml"
        
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
        report_file = yaml_file.parent / f"instagram_additional_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("ADDITIONAL INSTAGRAM ACCOUNTS REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"CONFIRMED AND ADDED ({added_count + updated_count}):\n")
            for handle, info in instagram_updates.items():
                f.write(f"✓ {handle}: {info['followers']:,} followers\n")
            
            f.write(f"\nNOT VERIFIED/NOT ADDED ({len(unverified_accounts)}):\n")
            for handle in unverified_accounts[:10]:
                f.write(f"✗ {handle}\n")
            if len(unverified_accounts) > 10:
                f.write(f"... and {len(unverified_accounts) - 10} more\n")
        
        print(f"Report saved to: {report_file}")
        
        # Final statistics
        print("\n" + "=" * 60)
        print("ADDITIONAL UPDATE COMPLETE")
        print("=" * 60)
        
        # Count current Instagram coverage
        instagram_count = sum(1 for acc in data['accounts'] 
                             if acc and acc.get('instagram_url'))
        total_accounts = len([a for a in data['accounts'] if a])
        
        print(f"\n📊 Updated Instagram coverage:")
        print(f"  - Total Instagram URLs: {instagram_count}/{total_accounts} ({instagram_count/total_accounts*100:.1f}%)")
        print(f"  - Net change: +{added_count} added")
        
        # Show top accounts by followers
        print(f"\n🌟 Top accounts in this batch:")
        batch_accounts = []
        for handle, info in instagram_updates.items():
            if info.get('followers'):
                batch_accounts.append((handle, info['followers']))
        
        batch_accounts.sort(key=lambda x: x[1], reverse=True)
        for handle, followers in batch_accounts[:5]:
            print(f"  - {handle}: {followers:,} followers")
        
        print(f"\n❌ Accounts NOT added (couldn't verify): {len(unverified_accounts)}")
        print("These accounts either don't exist, are private, or couldn't be confirmed")
    else:
        print("\nNo new Instagram URLs added")
    
    return added_count, updated_count

if __name__ == "__main__":
    add_additional_instagram_accounts()