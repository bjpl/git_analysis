#!/usr/bin/env python
"""
Quick smoke test for Image Manager
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """Test if all imports work"""
    try:
        from image_manager import ImageDatabase, ImageScanner, ImageOrganizer
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_database_create():
    """Test database creation"""
    try:
        from image_manager import ImageDatabase
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db = ImageDatabase(db_path)
        db.close()
        os.unlink(db_path)
        
        print("✓ Database creation successful")
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_ui_creation():
    """Test UI creation without showing"""
    try:
        import tkinter as tk
        from image_manager import ImageOrganizer
        
        # Create a root window but don't show it
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # This should create the UI without errors
        app = ImageOrganizer()
        app.withdraw()  # Hide this too
        
        # Clean up
        app.destroy()
        root.destroy()
        
        print("✓ UI creation successful")
        return True
    except Exception as e:
        print(f"✗ UI creation failed: {e}")
        return False

if __name__ == "__main__":
    print("Image Manager - Quick Test")
    print("=" * 40)
    
    tests = [test_import, test_database_create, test_ui_creation]
    results = []
    
    for test in tests:
        results.append(test())
    
    passed = sum(results)
    total = len(results)
    
    print("=" * 40)
    print(f"Quick Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All tests passed - Application ready!")
    else:
        print("✗ Some tests failed")
    
    sys.exit(0 if passed == total else 1)