#!/usr/bin/env python3
"""
QA Test Suite for Unsplash GPT Tool
Run this before release to ensure everything works.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all required imports."""
    print("Testing imports...")
    errors = []
    
    try:
        import tkinter
        print("✅ tkinter")
    except ImportError as e:
        errors.append(f"❌ tkinter: {e}")
    
    try:
        import requests
        print("✅ requests")
    except ImportError as e:
        errors.append(f"❌ requests: {e}")
    
    try:
        from PIL import Image, ImageTk
        print("✅ PIL/Pillow")
    except ImportError as e:
        errors.append(f"❌ Pillow: {e}")
    
    try:
        from openai import OpenAI
        print("✅ openai (new SDK)")
    except ImportError as e:
        errors.append(f"❌ openai: {e}")
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv")
    except ImportError as e:
        print(f"⚠️  python-dotenv (optional): {e}")
    
    return errors


def test_config():
    """Test configuration system."""
    print("\nTesting configuration...")
    errors = []
    
    try:
        from config_manager import ConfigManager
        config = ConfigManager()
        print("✅ ConfigManager loads")
        
        keys = config.get_api_keys()
        if keys['unsplash']:
            print("✅ Unsplash key configured")
        else:
            print("⚠️  No Unsplash key configured")
        
        if keys['openai']:
            print("✅ OpenAI key configured")
        else:
            print("⚠️  No OpenAI key configured")
        
        paths = config.get_paths()
        if paths['data_dir'].exists():
            print(f"✅ Data directory exists: {paths['data_dir']}")
        else:
            print(f"⚠️  Data directory missing: {paths['data_dir']}")
            
    except Exception as e:
        errors.append(f"❌ Config error: {e}")
    
    return errors


def test_main_app():
    """Test main application can initialize."""
    print("\nTesting main application...")
    errors = []
    
    try:
        # Test imports without running GUI
        from main import ImageSearchApp
        print("✅ Main app imports successfully")
        
        # Check critical functions exist
        required_methods = [
            'search_image',
            'generate_description',
            'extract_phrases_from_description',
            'translate_word',
            'export_vocabulary',
            'save_session_to_json'
        ]
        
        for method in required_methods:
            if hasattr(ImageSearchApp, method):
                print(f"✅ Method exists: {method}")
            else:
                errors.append(f"❌ Missing method: {method}")
                
    except Exception as e:
        errors.append(f"❌ Main app error: {e}")
    
    return errors


def test_data_files():
    """Test data file handling."""
    print("\nTesting data files...")
    errors = []
    
    # Test CSV operations
    try:
        import csv
        from datetime import datetime
        
        test_csv = Path("test_vocabulary.csv")
        
        # Write test data
        with open(test_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
            writer.writerow(['el café', 'coffee', datetime.now().strftime("%Y-%m-%d %H:%M"), 
                           'coffee shop', 'https://test.url', 'Test context'])
        
        # Read test data
        with open(test_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            if row['Spanish'] == 'el café':
                print("✅ CSV read/write works")
            else:
                errors.append("❌ CSV data mismatch")
        
        # Cleanup
        test_csv.unlink()
        
    except Exception as e:
        errors.append(f"❌ CSV error: {e}")
    
    # Test JSON operations
    try:
        import json
        
        test_json = Path("test_session.json")
        test_data = {
            "sessions": [{
                "session_start": "2024-01-01T10:00:00",
                "entries": [],
                "vocabulary_learned": 0
            }]
        }
        
        # Write JSON
        with open(test_json, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
        
        # Read JSON
        with open(test_json, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
            if loaded['sessions'][0]['session_start'] == "2024-01-01T10:00:00":
                print("✅ JSON read/write works")
            else:
                errors.append("❌ JSON data mismatch")
        
        # Cleanup
        test_json.unlink()
        
    except Exception as e:
        errors.append(f"❌ JSON error: {e}")
    
    return errors


def test_export_formats():
    """Test export functionality."""
    print("\nTesting export formats...")
    errors = []
    
    try:
        from pathlib import Path
        import csv
        
        # Create test vocabulary file
        test_csv = Path("test_export.csv")
        with open(test_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
            writer.writerow(['el perro', 'the dog', '2024-01-01', 'animals', 'http://test', 'Un perro negro'])
            writer.writerow(['la casa', 'the house', '2024-01-01', 'buildings', 'http://test2', 'Una casa grande'])
        
        # Test Anki format
        anki_output = []
        with open(test_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                spanish = row['Spanish']
                english = row['English']
                context = row.get('Context', '')[:50]
                anki_output.append(f"{spanish}\t{english} | {context}")
        
        if len(anki_output) == 2:
            print("✅ Anki export format works")
        else:
            errors.append(f"❌ Anki export produced {len(anki_output)} lines, expected 2")
        
        # Cleanup
        test_csv.unlink()
        
    except Exception as e:
        errors.append(f"❌ Export test error: {e}")
    
    return errors


def main():
    """Run all QA tests."""
    print("=" * 60)
    print("UNSPLASH GPT TOOL - QA TEST SUITE")
    print("=" * 60)
    
    all_errors = []
    
    # Run tests
    all_errors.extend(test_imports())
    all_errors.extend(test_config())
    all_errors.extend(test_main_app())
    all_errors.extend(test_data_files())
    all_errors.extend(test_export_formats())
    
    # Summary
    print("\n" + "=" * 60)
    if all_errors:
        print("❌ QA FAILED - Issues found:")
        for error in all_errors:
            print(f"  {error}")
        return 1
    else:
        print("✅ ALL QA TESTS PASSED!")
        print("\nThe application is ready for release.")
        print("\nNext steps:")
        print("1. Test with real API keys using: python test_setup.py")
        print("2. Run the app: python main.py")
        print("3. Build executable: build.bat")
        return 0


if __name__ == "__main__":
    sys.exit(main())