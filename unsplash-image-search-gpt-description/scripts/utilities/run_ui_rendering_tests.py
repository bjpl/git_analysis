#!/usr/bin/env python3
"""
Test runner for UI rendering tests.

This script runs the comprehensive UI rendering test suite to verify:
- Main window renders correctly with all widgets
- API configuration modal works properly
- Application functions with and without API keys
- UI responsiveness and theme system

Usage:
    python run_ui_rendering_tests.py

Returns exit code 0 for success, 1 for failure.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Run the UI rendering test suite."""
    print("=" * 80)
    print("UI RENDERING TEST RUNNER")
    print("=" * 80)
    
    try:
        # Import and run the test suite
        from src.tests.test_ui_rendering import UIRenderingTest
        
        test_suite = UIRenderingTest()
        success = test_suite.run_all_tests()
        
        if success:
            print("\n🎉 All UI rendering tests passed!")
            print("The application UI is working correctly.")
            return 0
        else:
            print("\n❌ Some UI rendering tests failed.")
            print("Please review the test output above for details.")
            return 1
            
    except ImportError as e:
        print(f"Error: Could not import test modules: {e}")
        print("Please ensure all dependencies are installed.")
        return 1
    except Exception as e:
        print(f"Error: Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())