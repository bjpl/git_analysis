#!/usr/bin/env python3
"""
Migration script to update old CSV format to new format with image context.
Run this if you have an existing vocabulary CSV from the old version.
"""

import csv
import os
from pathlib import Path
from datetime import datetime

def migrate_vocabulary_csv(old_csv_path, backup=True):
    """
    Migrate old CSV format to new format with additional context columns.
    
    Old format: Spanish, English, Date, Context
    New format: Spanish, English, Date, Search Query, Image URL, Context
    """
    old_csv_path = Path(old_csv_path)
    
    if not old_csv_path.exists():
        print(f"File not found: {old_csv_path}")
        return False
    
    # Create backup if requested
    if backup:
        backup_path = old_csv_path.with_suffix('.csv.backup')
        print(f"Creating backup: {backup_path}")
        with open(old_csv_path, 'r', encoding='utf-8') as src:
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
    
    # Read old data
    old_data = []
    try:
        with open(old_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            
            # Check if already migrated
            if headers and len(headers) >= 6:
                print("CSV appears to already be in new format!")
                return True
            
            # Read all rows
            for row in reader:
                old_data.append(row)
        
        print(f"Read {len(old_data)} vocabulary entries")
        
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return False
    
    # Write new format
    try:
        with open(old_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write new headers
            writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
            
            # Migrate old data
            for row in old_data:
                if len(row) >= 2:  # Must have at least Spanish and English
                    spanish = row[0] if len(row) > 0 else ""
                    english = row[1] if len(row) > 1 else ""
                    date = row[2] if len(row) > 2 else datetime.now().strftime("%Y-%m-%d %H:%M")
                    context = row[3] if len(row) > 3 else ""
                    
                    # New columns (empty for old data)
                    search_query = ""
                    image_url = ""
                    
                    writer.writerow([spanish, english, date, search_query, image_url, context])
        
        print(f"Successfully migrated {len(old_data)} entries to new format")
        return True
        
    except Exception as e:
        print(f"Error writing new CSV: {e}")
        return False


def main():
    """Main entry point for migration script."""
    print("=" * 50)
    print("VOCABULARY CSV MIGRATION TOOL")
    print("=" * 50)
    
    # Look for CSV files in common locations
    possible_paths = [
        Path("data/vocabulary.csv"),
        Path("target_word_list.csv"),
        Path("C:/Users/brand/Development/Project_Workspace/unsplash-image-search-gpt-description/target_word_list.csv"),
        Path("C:/Users/brand/Development/Project_Workspace/unsplash-image-search-gpt-description/data/vocabulary.csv")
    ]
    
    csv_files = []
    for path in possible_paths:
        if path.exists():
            csv_files.append(path)
    
    if not csv_files:
        print("No vocabulary CSV files found!")
        print("\nPlease specify the path to your CSV file:")
        csv_path = input("Path: ").strip()
        if csv_path:
            csv_files = [Path(csv_path)]
    
    for csv_file in csv_files:
        print(f"\nMigrating: {csv_file}")
        if migrate_vocabulary_csv(csv_file):
            print(f"✅ Migration successful!")
        else:
            print(f"❌ Migration failed!")
    
    print("\nMigration complete!")
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()