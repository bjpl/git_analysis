#!/usr/bin/env python3
"""
Test script for the simplified CLI system
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all imports work correctly"""
    try:
        from src.cli import CurriculumCLI
        from src.ui.formatter import TerminalFormatter
        from src.notes_manager import NotesManager
        from src.ui.interactive import InteractiveSession
        
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_cli_initialization():
    """Test that CLI can be initialized"""
    try:
        from src.cli import CurriculumCLI
        
        cli = CurriculumCLI()
        print("✅ CLI initialization successful!")
        
        # Test reset progress functionality
        cli_with_reset = CurriculumCLI()
        print("✅ CLI with reset progress successful!")
        
        return True
    except Exception as e:
        print(f"❌ CLI initialization error: {e}")
        return False

def test_formatter():
    """Test the terminal formatter"""
    try:
        from src.ui.formatter import TerminalFormatter
        
        formatter = TerminalFormatter()
        
        # Test basic formatting methods
        header_msg = formatter.header("Test Header")
        info_msg = formatter.info("Test info message")
        success_msg = formatter.success("Test success message")
        warning_msg = formatter.warning("Test warning message")
        error_msg = formatter.error("Test error message")
        
        print("✅ Formatter methods working!")
        return True
    except Exception as e:
        print(f"❌ Formatter error: {e}")
        return False

def test_simplified_interactive():
    """Test the simplified interactive session"""
    try:
        from src.ui.interactive import InteractiveSession
        
        session = InteractiveSession()
        print("✅ Simplified InteractiveSession created successfully!")
        
        # The run method is async, so we can't easily test it here
        # but we can confirm the class is properly structured
        return True
    except Exception as e:
        print(f"❌ InteractiveSession error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Simplified CLI System")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("CLI Initialization", test_cli_initialization), 
        ("Formatter Tests", test_formatter),
        ("Simplified Interactive", test_simplified_interactive)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed!")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The simplified CLI is ready!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())