#!/usr/bin/env python3
"""
Simple test runner for image search test suite validation.
Verifies that all test modules can be imported and basic functionality works.
"""

import sys
import os
import unittest
from pathlib import Path
import importlib.util
import traceback

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "tests"))

def load_module_from_path(module_name, file_path):
    """Load a module from a file path."""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module, None
    except Exception as e:
        return None, str(e)

def test_module_imports():
    """Test that all test modules can be imported."""
    print("Testing module imports...")
    
    test_modules = [
        ("test_search_limits", "tests/unit/test_image_search/test_search_limits.py"),
        ("test_progress_tracking", "tests/unit/test_image_search/test_progress_tracking.py"),
        ("test_edge_cases", "tests/unit/test_image_search/test_edge_cases.py"),
        ("test_ui_components", "tests/unit/test_image_search/test_ui_components.py"),
        ("test_performance", "tests/unit/test_image_search/test_performance.py"),
        ("test_timeout_scenarios", "tests/unit/test_image_search/test_timeout_scenarios.py"),
        ("test_integration_workflow", "tests/integration/test_image_search_workflow.py"),
        ("mock_api_responses", "tests/fixtures/mock_api_responses.py"),
        ("test_comprehensive", "tests/test_image_search_comprehensive.py")
    ]
    
    results = []
    
    for module_name, file_path in test_modules:
        full_path = project_root / file_path
        if full_path.exists():
            module, error = load_module_from_path(module_name, full_path)
            if module:
                print(f"✅ {module_name}: Import successful")
                results.append((module_name, True, None))
            else:
                print(f"❌ {module_name}: Import failed - {error}")
                results.append((module_name, False, error))
        else:
            print(f"❌ {module_name}: File not found - {full_path}")
            results.append((module_name, False, "File not found"))
    
    return results

def test_mock_data_functionality():
    """Test that mock data structures work correctly."""
    print("\nTesting mock data functionality...")
    
    try:
        # Test importing mock responses
        sys.path.insert(0, str(project_root / "tests" / "fixtures"))
        from mock_api_responses import MockUnsplashAPI, MockOpenAIAPI, MockImageData, TEST_SCENARIOS
        
        # Test MockUnsplashAPI
        response = MockUnsplashAPI.successful_search_response()
        assert 'results' in response
        assert 'total' in response
        assert len(response['results']) > 0
        print("✅ MockUnsplashAPI: Working correctly")
        
        # Test MockOpenAIAPI  
        response = MockOpenAIAPI.successful_description_response()
        assert 'choices' in response
        assert len(response['choices']) > 0
        print("✅ MockOpenAIAPI: Working correctly")
        
        # Test MockImageData
        png_data = MockImageData.valid_png_bytes()
        assert isinstance(png_data, bytes)
        assert len(png_data) > 0
        print("✅ MockImageData: Working correctly")
        
        # Test TEST_SCENARIOS
        assert 'normal_search' in TEST_SCENARIOS
        assert 'empty_search' in TEST_SCENARIOS
        print("✅ TEST_SCENARIOS: Working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Mock data test failed: {e}")
        traceback.print_exc()
        return False

def test_main_app_import():
    """Test that main app can be imported for testing."""
    print("\nTesting main app import...")
    
    try:
        from main import ImageSearchApp
        print("✅ Main app: Import successful")
        
        # Test that we can access key methods
        methods = ['get_next_image', 'search_image', 'generate_description', 
                  'show_progress', 'hide_progress', 'disable_buttons', 'enable_buttons']
        
        for method in methods:
            if hasattr(ImageSearchApp, method):
                print(f"✅ Method {method}: Found")
            else:
                print(f"❌ Method {method}: Missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Main app import failed: {e}")
        traceback.print_exc()
        return False

def test_config_manager_import():
    """Test that config manager can be imported for testing."""
    print("\nTesting config manager import...")
    
    try:
        from config_manager import ConfigManager, ensure_api_keys_configured
        print("✅ Config manager: Import successful")
        return True
        
    except Exception as e:
        print(f"❌ Config manager import failed: {e}")
        traceback.print_exc()
        return False

def validate_test_structure():
    """Validate test directory structure."""
    print("\nValidating test directory structure...")
    
    required_paths = [
        "tests/__init__.py",
        "tests/conftest.py", 
        "tests/unit/__init__.py",
        "tests/unit/test_image_search/__init__.py",
        "tests/integration/__init__.py",
        "tests/fixtures/__init__.py",
        "tests/fixtures/mock_api_responses.py",
        "tests/README_TEST_SUITE.md"
    ]
    
    missing_paths = []
    
    for path in required_paths:
        full_path = project_root / path
        if full_path.exists():
            print(f"✅ {path}: Found")
        else:
            print(f"❌ {path}: Missing")
            missing_paths.append(path)
    
    if missing_paths:
        print(f"\n❌ Missing required files: {missing_paths}")
        return False
    
    print("✅ Test directory structure: Valid")
    return True

def run_basic_test_validation():
    """Run basic validation of test classes."""
    print("\nValidating test classes...")
    
    try:
        # Import a test class and check its structure
        sys.path.insert(0, str(project_root / "tests" / "unit" / "test_image_search"))
        from test_search_limits import TestImageSearchLimits
        
        # Check that test class has expected methods
        expected_methods = [
            'test_get_next_image_basic_functionality',
            'test_get_next_image_with_collection_limit',
            'test_get_next_image_pagination',
            'test_get_next_image_skip_duplicates'
        ]
        
        for method in expected_methods:
            if hasattr(TestImageSearchLimits, method):
                print(f"✅ Test method {method}: Found")
            else:
                print(f"❌ Test method {method}: Missing")
                return False
        
        print("✅ Test class validation: Passed")
        return True
        
    except Exception as e:
        print(f"❌ Test class validation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test runner."""
    print("="*60)
    print("IMAGE SEARCH TEST SUITE VALIDATION")
    print("="*60)
    
    all_tests_passed = True
    
    # Test directory structure
    if not validate_test_structure():
        all_tests_passed = False
    
    # Test module imports
    import_results = test_module_imports()
    failed_imports = [r for r in import_results if not r[1]]
    if failed_imports:
        print(f"\n❌ Failed imports: {len(failed_imports)}")
        all_tests_passed = False
    else:
        print(f"\n✅ All imports successful: {len(import_results)}")
    
    # Test mock data functionality
    if not test_mock_data_functionality():
        all_tests_passed = False
    
    # Test main app import
    if not test_main_app_import():
        all_tests_passed = False
    
    # Test config manager import
    if not test_config_manager_import():
        all_tests_passed = False
    
    # Test basic validation
    if not run_basic_test_validation():
        all_tests_passed = False
    
    # Summary
    print("\n" + "="*60)
    if all_tests_passed:
        print("✅ ALL VALIDATION TESTS PASSED")
        print("The image search test suite is ready for use!")
        print("\nTo run the full test suite with pytest:")
        print("  pip install pytest pytest-cov requests-mock")
        print("  python -m pytest tests/ -v")
        print("\nTo run comprehensive tests:")
        print("  python -m pytest tests/test_image_search_comprehensive.py --comprehensive -v")
    else:
        print("❌ SOME VALIDATION TESTS FAILED")
        print("Please fix the issues above before running the full test suite.")
    
    print("="*60)
    
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    sys.exit(main())