"""
Add massive batch of verified Instagram and YouTube accounts
"""

import yaml
from pathlib import Path
from datetime import datetime

def add_massive_verified_accounts():
    """Add large batch of verified accounts across multiple categories"""
    
    yaml_file = Path(r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml")
    
    # Comprehensive list of new accounts to add
    new_accounts = [
        # Government & Diplomatic
        {'handle': '@policianacional', 'name': 'Policía Nacional Colombia', 'instagram_url': 'https://instagram.com/policianalcolombia', 'category': 'Government', 'description': 'Colombian National Police'},
        {'handle': '@ejercitocol', 'name': 'Ejército Colombia', 'instagram_url': 'https://instagram.com/ejercitocolombia', 'category': 'Government', 'description': 'Colombian Army official account'},
        {'handle': '@conacyt', 'name': 'CONACYT México', 'instagram_url': 'https://instagram.com/conacyt_mx', 'category': 'Government', 'description': 'National Council of Science and Technology Mexico'},
        {'handle': '@profeco', 'name': 'PROFECO', 'instagram_url': 'https://instagram.com/profeco', 'category': 'Government', 'description': 'Federal Consumer Protection Agency Mexico'},
        
        # International Media
        {'handle': '@cnnespanol', 'name': 'CNN Español', 'instagram_url': 'https://instagram.com/cnnespanol', 'youtube_url': 'https://youtube.com/@cnnespanol', 'category': 'Media', 'description': 'CNN en Español'},
        {'handle': '@bbcmundo', 'name': 'BBC Mundo', 'instagram_url': 'https://instagram.com/bbcmundo', 'youtube_url': 'https://youtube.com/@bbcmundo', 'category': 'Media', 'description': 'BBC World Service Spanish'},
        {'handle': '@dwespanol', 'name': 'DW Español', 'instagram_url': 'https://instagram.com/dw_espanol', 'youtube_url': 'https://youtube.com/@dwespanol', 'category': 'Media', 'description': 'Deutsche Welle Spanish'},
        
        # Colombian Media
        {'handle': '@noticiascaracol', 'name': 'Noticias Caracol', 'instagram_url': 'https://instagram.com/noticiascaracol', 'youtube_url': 'https://youtube.com/@noticiascaracol', 'category': 'Media', 'description': 'Caracol Noticias Colombia'},
        {'handle': '@noticiasrcn', 'name': 'Noticias RCN', 'instagram_url': 'https://instagram.com/noticiasrcn', 'category': 'Media', 'description': 'RCN Noticias Colombia'},
        
        # Museums
        {'handle': '@museotamayo', 'name': 'Museo Tamayo', 'instagram_url': 'https://instagram.com/museotamayo', 'category': 'Culture', 'description': 'Museo Tamayo Mexico City'},
        {'handle': '@museosoumaya', 'name': 'Museo Soumaya', 'instagram_url': 'https://instagram.com/museosoumaya', 'category': 'Culture', 'description': 'Museo Soumaya Mexico'},
        
        # Football Clubs
        {'handle': '@clubamericaoficial', 'name': 'Club América', 'instagram_url': 'https://instagram.com/clubamericaoficial', 'category': 'Sports', 'description': 'Club América Mexico football'},
        {'handle': '@bocajrsoficial', 'name': 'Boca Juniors', 'instagram_url': 'https://instagram.com/bocajrsoficial', 'category': 'Sports', 'description': 'Boca Juniors Argentina'},
        {'handle': '@riverplateoficial', 'name': 'River Plate', 'instagram_url': 'https://instagram.com/riverplateoficial', 'category': 'Sports', 'description': 'River Plate Argentina'},
        {'handle': '@millonarios', 'name': 'Millonarios FC', 'instagram_url': 'https://instagram.com/millonariosfcoficial', 'category': 'Sports', 'description': 'Millonarios FC Colombia'},
        {'handle': '@atleticonacional', 'name': 'Atlético Nacional', 'instagram_url': 'https://instagram.com/nacionaloficial', 'category': 'Sports', 'description': 'Atlético Nacional Colombia'},
        
        # Airlines
        {'handle': '@aeromexico', 'name': 'Aeroméxico', 'instagram_url': 'https://instagram.com/aeromexico', 'youtube_url': 'https://youtube.com/@aeromexico', 'category': 'Transportation', 'description': 'Aeroméxico airline'},
        
        # E-commerce & Tech
        {'handle': '@mercadolibre', 'name': 'MercadoLibre', 'instagram_url': 'https://instagram.com/mercadolibre', 'youtube_url': 'https://youtube.com/@mercadolibre', 'category': 'Technology', 'description': 'Latin America e-commerce platform'},
        {'handle': '@rappi', 'name': 'Rappi', 'instagram_url': 'https://instagram.com/rappi', 'category': 'Technology', 'description': 'Latin American delivery app'},
        
        # Colombian Regional Governments
        {'handle': '@alcaldiacali', 'name': 'Alcaldía de Cali', 'instagram_url': 'https://instagram.com/alcaldiadecali', 'category': 'Government', 'description': 'Cali Mayor\'s Office'},
        {'handle': '@alcaldiabquilla', 'name': 'Alcaldía de Barranquilla', 'instagram_url': 'https://instagram.com/alcaldiabquilla', 'category': 'Government', 'description': 'Barranquilla Mayor\'s Office'},
        {'handle': '@alcaldiacartagena', 'name': 'Alcaldía de Cartagena', 'instagram_url': 'https://instagram.com/alcaldiadecartagena', 'category': 'Government', 'description': 'Cartagena Mayor\'s Office'},
        
        # Colombian Security Forces
        {'handle': '@armadacol', 'name': 'Armada Colombia', 'instagram_url': 'https://instagram.com/armadacolombia', 'category': 'Government', 'description': 'Colombian Navy'},
        {'handle': '@fuerzaaerea', 'name': 'Fuerza Aérea Colombia', 'instagram_url': 'https://instagram.com/fuerzaaereacol', 'category': 'Government', 'description': 'Colombian Air Force'},
        {'handle': '@migracioncol', 'name': 'Migración Colombia', 'instagram_url': 'https://instagram.com/migracioncolombia', 'category': 'Government', 'description': 'Colombian Migration Authority'},
        
        # Colombian Media
        {'handle': '@bluradio', 'name': 'Blu Radio', 'instagram_url': 'https://instagram.com/bluradio_co', 'category': 'Media', 'description': 'Blu Radio Colombia'},
        {'handle': '@lafm', 'name': 'La FM', 'instagram_url': 'https://instagram.com/lafm', 'category': 'Media', 'description': 'La FM Radio Colombia'},
        
        # Venezuelan Government
        {'handle': '@presidencialven', 'name': 'Presidencia Venezuela', 'instagram_url': 'https://instagram.com/presidencialven', 'category': 'Government', 'description': 'Venezuelan Presidency'},
        {'handle': '@cancilleriaven', 'name': 'Cancillería Venezuela', 'instagram_url': 'https://instagram.com/cancilleriavenezuela', 'category': 'Government', 'description': 'Venezuelan Foreign Ministry'},
        
        # Venezuelan Media
        {'handle': '@venevision', 'name': 'Venevisión', 'instagram_url': 'https://instagram.com/venevision', 'youtube_url': 'https://youtube.com/@venevision', 'category': 'Media', 'description': 'Venevisión TV network'},
        {'handle': '@globovision', 'name': 'Globovisión', 'instagram_url': 'https://instagram.com/globovision', 'youtube_url': 'https://youtube.com/@globovision', 'category': 'Media', 'description': 'Globovisión news'},
        
        # Colombian Beer Brands
        {'handle': '@aguilacerveza', 'name': 'Águila Cerveza', 'instagram_url': 'https://instagram.com/aguila_cerveza', 'category': 'Food & Beverage', 'description': 'Águila beer Colombia'},
        {'handle': '@clubcolombiabeer', 'name': 'Club Colombia', 'instagram_url': 'https://instagram.com/clubcolombia', 'category': 'Food & Beverage', 'description': 'Club Colombia beer'},
        {'handle': '@pokerbeer', 'name': 'Poker Beer', 'instagram_url': 'https://instagram.com/pokercolombiana', 'category': 'Food & Beverage', 'description': 'Poker beer Colombia'},
        {'handle': '@ponymalta', 'name': 'Pony Malta', 'instagram_url': 'https://instagram.com/ponymalta', 'category': 'Food & Beverage', 'description': 'Pony Malta beverage'},
        
        # Colombian Coffee
        {'handle': '@cafedecolombia', 'name': 'Café de Colombia', 'instagram_url': 'https://instagram.com/cafedecolombia', 'category': 'Food & Beverage', 'description': 'Colombian Coffee Federation'},
        {'handle': '@pergaminocafe', 'name': 'Pergamino Café', 'instagram_url': 'https://instagram.com/pergaminocafe', 'category': 'Food & Beverage', 'description': 'Pergamino Coffee'},
        
        # Colombian Restaurants
        {'handle': '@andrescarnederes', 'name': 'Andrés Carne de Res', 'instagram_url': 'https://instagram.com/andrescarnederes', 'category': 'Food & Beverage', 'description': 'Famous Colombian restaurant'},
        {'handle': '@wokco', 'name': 'Wok', 'instagram_url': 'https://instagram.com/wokco', 'category': 'Food & Beverage', 'description': 'Wok restaurant chain Colombia'},
        
        # Mexican Beer
        {'handle': '@tecate', 'name': 'Tecate', 'instagram_url': 'https://instagram.com/tecatecerveza', 'category': 'Food & Beverage', 'description': 'Tecate beer'},
        {'handle': '@dossequis', 'name': 'Dos Equis', 'instagram_url': 'https://instagram.com/dossequis', 'category': 'Food & Beverage', 'description': 'Dos Equis beer'},
        
        # Fast Food Chains
        {'handle': '@starbuckscol', 'name': 'Starbucks Colombia', 'instagram_url': 'https://instagram.com/starbucks_co', 'category': 'Food & Beverage', 'description': 'Starbucks Colombia'},
        {'handle': '@mcdonaldscol', 'name': 'McDonald\'s Colombia', 'instagram_url': 'https://instagram.com/mcdonalds_col', 'category': 'Food & Beverage', 'description': 'McDonald\'s Colombia'},
        {'handle': '@burgerkingcol', 'name': 'Burger King Colombia', 'instagram_url': 'https://instagram.com/burgerking_col', 'category': 'Food & Beverage', 'description': 'Burger King Colombia'},
        
        # Healthcare
        {'handle': '@compensar', 'name': 'Compensar', 'instagram_url': 'https://instagram.com/compensarcolombia', 'category': 'Healthcare', 'description': 'Compensar health services'},
        {'handle': '@saludtotal', 'name': 'Salud Total', 'instagram_url': 'https://instagram.com/saludtotaleps', 'category': 'Healthcare', 'description': 'Salud Total EPS Colombia'},
        {'handle': '@cruzverde', 'name': 'Cruz Verde', 'instagram_url': 'https://instagram.com/cruzverdecolombia', 'category': 'Healthcare', 'description': 'Cruz Verde pharmacy chain'},
        
        # Fashion
        {'handle': '@arturocalle', 'name': 'Arturo Calle', 'instagram_url': 'https://instagram.com/arturo_calle', 'category': 'Fashion', 'description': 'Arturo Calle Colombian fashion'},
        {'handle': '@studiof', 'name': 'Studio F', 'instagram_url': 'https://instagram.com/studiofco', 'category': 'Fashion', 'description': 'Studio F Colombia fashion'},
        {'handle': '@velez', 'name': 'Vélez', 'instagram_url': 'https://instagram.com/velez_leather', 'category': 'Fashion', 'description': 'Vélez leather goods'},
        
        # Entertainment
        {'handle': '@hbomaxla', 'name': 'HBO Max LATAM', 'instagram_url': 'https://instagram.com/hbomaxla', 'category': 'Entertainment', 'description': 'HBO Max Latin America'},
        {'handle': '@paramountplusla', 'name': 'Paramount+ LATAM', 'instagram_url': 'https://instagram.com/paramountplusla', 'category': 'Entertainment', 'description': 'Paramount+ Latin America'},
        
        # Hotels
        {'handle': '@decameron', 'name': 'Decameron Hotels', 'instagram_url': 'https://instagram.com/decameron', 'category': 'Tourism', 'description': 'Decameron Hotels chain'},
        {'handle': '@hotelesdann', 'name': 'Hoteles Dann', 'instagram_url': 'https://instagram.com/hotelesdann', 'category': 'Tourism', 'description': 'Hoteles Dann chain'},
        
        # Sports Organizations
        {'handle': '@dimayor', 'name': 'DIMAYOR', 'instagram_url': 'https://instagram.com/dimayor', 'category': 'Sports', 'description': 'Colombian football division'},
        {'handle': '@fedecoltenis', 'name': 'Fedecoltenis', 'instagram_url': 'https://instagram.com/fedecoltenis', 'category': 'Sports', 'description': 'Colombian Tennis Federation'}
    ]
    
    print("Loading YAML file...")
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if 'accounts' not in data:
        data['accounts'] = []
    
    # Check existing accounts
    existing_handles = set(acc.get('handle', '') for acc in data['accounts'] if acc)
    existing_instagram = set(acc.get('instagram_url', '') for acc in data['accounts'] if acc and acc.get('instagram_url'))
    
    added_count = 0
    skipped_count = 0
    
    print("\nAdding new verified accounts...")
    for new_account in new_accounts:
        # Add timestamp
        new_account['instagram_manually_added'] = True
        new_account['last_updated'] = datetime.now().strftime("%Y-%m-%d")
        
        # Check if already exists
        if new_account['handle'] in existing_handles or new_account['instagram_url'] in existing_instagram:
            skipped_count += 1
            continue
        
        # Add new account
        data['accounts'].append(new_account)
        added_count += 1
        if added_count <= 10:  # Show first 10
            print(f"✓ Added: {new_account['name']}")
    
    print(f"\n📊 Results:")
    print(f"  - New accounts added: {added_count}")
    print(f"  - Skipped (duplicates): {skipped_count}")
    
    if added_count > 0:
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = yaml_file.parent / f"{yaml_file.stem}_backup_massive_{timestamp}.yml"
        
        print(f"\nCreating backup: {backup_file}")
        with open(backup_file, 'w', encoding='utf-8') as f:
            with open(yaml_file, 'r', encoding='utf-8') as orig:
                f.write(orig.read())
        
        # Save updated YAML
        print(f"Saving updated YAML...")
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
        
        # Count coverage
        total_accounts = len([a for a in data['accounts'] if a])
        instagram_count = sum(1 for acc in data['accounts'] if acc and acc.get('instagram_url'))
        youtube_count = sum(1 for acc in data['accounts'] if acc and acc.get('youtube_url'))
        
        print("\n" + "=" * 60)
        print("MASSIVE UPDATE COMPLETE")
        print("=" * 60)
        print(f"\n📊 Updated dataset:")
        print(f"  - Total accounts: {total_accounts} (+{added_count})")
        print(f"  - Instagram coverage: {instagram_count}/{total_accounts} ({instagram_count/total_accounts*100:.1f}%)")
        print(f"  - YouTube coverage: {youtube_count}/{total_accounts} ({youtube_count/total_accounts*100:.1f}%)")
    
    return added_count

if __name__ == "__main__":
    add_massive_verified_accounts()