"""
Add verified batch of Instagram accounts including regional accounts
"""

import yaml
from pathlib import Path
from datetime import datetime

def add_verified_batch_accounts():
    """Add verified Instagram accounts including regional Latin America accounts"""
    
    yaml_file = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml")
    
    # New accounts to add (that don't exist yet)
    new_accounts = [
        {
            'handle': '@loreallatam',
            'name': 'L\'Oréal Latin America',
            'instagram_url': 'https://instagram.com/lorealgroupe_latam',
            'instagram_followers': 120000,
            'category': 'Beauty',
            'description': 'L\'Oréal Group official account for Latin America region'
        },
        {
            'handle': '@headandshouldersla',
            'name': 'Head & Shoulders LATAM',
            'instagram_url': 'https://instagram.com/headandshouldersla',
            'instagram_followers': 98000,
            'category': 'Beauty',
            'description': 'Head & Shoulders official account for Latin America'
        },
        {
            'handle': '@panteneco',
            'name': 'Pantene Colombia',
            'instagram_url': 'https://instagram.com/panteneco',
            'instagram_followers': 45000,
            'category': 'Beauty',
            'description': 'Pantene official account for Colombia'
        },
        {
            'handle': '@mercedesbenzcol',
            'name': 'Mercedes-Benz Colombia',
            'instagram_url': 'https://instagram.com/mercedesbenzcolombia',
            'instagram_followers': 141000,
            'category': 'Automotive',
            'description': 'Mercedes-Benz official account for Colombia'
        },
        {
            'handle': '@audicol',
            'name': 'Audi Colombia',
            'instagram_url': 'https://instagram.com/audi.colombia',
            'instagram_followers': 97000,
            'category': 'Automotive',
            'description': 'Audi official account for Colombia'
        },
        {
            'handle': '@bancolombia',
            'name': 'Bancolombia',
            'instagram_url': 'https://instagram.com/bancolombia',
            'instagram_followers': 496000,
            'category': 'Banking',
            'description': 'Bancolombia - Leading Colombian bank'
        },
        {
            'handle': '@bancocajasocial',
            'name': 'Banco Caja Social',
            'instagram_url': 'https://instagram.com/bancocajasocial',
            'instagram_followers': 58000,
            'category': 'Banking',
            'description': 'Banco Caja Social - Colombian social bank'
        },
        {
            'handle': '@itaucol',
            'name': 'Itaú Colombia',
            'instagram_url': 'https://instagram.com/itaucol',
            'instagram_followers': 26000,
            'category': 'Banking',
            'description': 'Itaú Bank Colombia'
        },
        {
            'handle': '@tigocol',
            'name': 'Tigo Colombia',
            'instagram_url': 'https://instagram.com/tigocolombia',
            'instagram_followers': 139000,
            'category': 'Telecommunications',
            'description': 'Tigo telecommunications services in Colombia'
        }
    ]
    
    # Accounts to update (that might already exist)
    updates_to_existing = {
        '@avianca': {
            'instagram_url': 'https://instagram.com/avianca',
            'instagram_followers': 1000000
        },
        '@davivienda': {
            'instagram_url': 'https://instagram.com/davivienda',
            'instagram_followers': 168000
        }
    }
    
    print("Loading YAML file...")
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if 'accounts' not in data:
        data['accounts'] = []
    
    # Check existing accounts
    existing_handles = set(acc.get('handle', '') for acc in data['accounts'] if acc)
    existing_instagram = set(acc.get('instagram_url', '') for acc in data['accounts'] if acc and acc.get('instagram_url'))
    
    added_count = 0
    updated_count = 0
    skipped_count = 0
    
    print("\nAdding new accounts...")
    for new_account in new_accounts:
        # Add timestamp
        new_account['instagram_manually_added'] = True
        new_account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
        
        # Check if already exists
        if new_account['handle'] in existing_handles:
            # Try to update existing account
            for acc in data['accounts']:
                if acc and acc.get('handle') == new_account['handle']:
                    if not acc.get('instagram_url'):
                        acc['instagram_url'] = new_account['instagram_url']
                        acc['instagram_followers'] = new_account['instagram_followers']
                        acc['instagram_manually_added'] = True
                        acc['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                        updated_count += 1
                        print(f"✓ Updated existing: {new_account['name']} ({new_account['instagram_followers']:,} followers)")
                    else:
                        print(f"⚠️  Skipping {new_account['name']} - already has Instagram")
                        skipped_count += 1
                    break
        elif new_account['instagram_url'] in existing_instagram:
            print(f"⚠️  Skipping {new_account['name']} - Instagram URL already exists")
            skipped_count += 1
        else:
            # Add new account
            data['accounts'].append(new_account)
            added_count += 1
            print(f"✓ Added: {new_account['name']} ({new_account['instagram_followers']:,} followers)")
            existing_handles.add(new_account['handle'])
            existing_instagram.add(new_account['instagram_url'])
    
    print("\nUpdating existing accounts...")
    for handle, update_info in updates_to_existing.items():
        for acc in data['accounts']:
            if acc and acc.get('handle') == handle:
                if not acc.get('instagram_url') or acc.get('instagram_url') != update_info['instagram_url']:
                    acc['instagram_url'] = update_info['instagram_url']
                    acc['instagram_followers'] = update_info['instagram_followers']
                    acc['instagram_manually_added'] = True
                    acc['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                    updated_count += 1
                    print(f"✓ Updated: {acc.get('name', handle)} ({update_info['instagram_followers']:,} followers)")
                else:
                    print(f"⚠️  {acc.get('name', handle)} already up to date")
                break
    
    print(f"\n📊 Results:")
    print(f"  - New accounts added: {added_count}")
    print(f"  - Existing accounts updated: {updated_count}")
    print(f"  - Skipped (duplicates): {skipped_count}")
    
    if added_count + updated_count > 0:
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = yaml_file.parent / f"{yaml_file.stem}_backup_verified_{timestamp}.yml"
        
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
        report_file = yaml_file.parent / f"verified_batch_report_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("VERIFIED BATCH INSTAGRAM ACCOUNTS\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total added: {added_count}\n")
            f.write(f"Total updated: {updated_count}\n\n")
            
            f.write("Top accounts by followers:\n")
            all_accounts = []
            for acc in new_accounts:
                all_accounts.append((acc['name'], acc.get('instagram_followers', 0)))
            for handle, info in updates_to_existing.items():
                for acc in data['accounts']:
                    if acc and acc.get('handle') == handle:
                        all_accounts.append((acc.get('name', handle), info['instagram_followers']))
                        break
            
            all_accounts.sort(key=lambda x: x[1], reverse=True)
            for name, followers in all_accounts[:10]:
                f.write(f"- {name}: {followers:,} followers\n")
        
        print(f"Report saved to: {report_file}")
        
        # Final statistics
        print("\n" + "=" * 60)
        print("VERIFIED BATCH UPDATE COMPLETE")
        print("=" * 60)
        
        # Count current coverage
        total_accounts = len([a for a in data['accounts'] if a])
        instagram_count = sum(1 for acc in data['accounts'] 
                             if acc and acc.get('instagram_url'))
        
        print(f"\n📊 Updated dataset statistics:")
        print(f"  - Total accounts: {total_accounts}")
        print(f"  - Instagram coverage: {instagram_count}/{total_accounts} ({instagram_count/total_accounts*100:.1f}%)")
        
        # Show top accounts
        print(f"\n🌟 Top accounts in this batch:")
        for name, followers in all_accounts[:5]:
            if followers > 0:
                print(f"  - {name}: {followers:,} followers")
    else:
        print("\nNo changes made to the dataset")
    
    return added_count + updated_count

if __name__ == "__main__":
    add_verified_batch_accounts()