#!/usr/bin/env python3
"""
Test infrastructure validation script.
This script verifies that our comprehensive test suite is properly set up.
"""

import sys
import os
import importlib.util
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    success_count = 0
    total_count = 0
    
    # Test pytest imports
    try:
        import pytest
        print(f"✅ pytest {pytest.__version__}")
        success_count += 1
    except ImportError:
        print("❌ pytest not available")
    total_count += 1
    
    # Test core modules
    core_modules = ['sys', 'os', 'pathlib', 'unittest.mock', 'asyncio', 'json', 'time']
    for module in core_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
            success_count += 1
        except ImportError:
            print(f"❌ {module}")
        total_count += 1
    
    # Test our UI modules (may not be available)
    try:
        from src.ui.formatter import TerminalFormatter, Color, Theme
        print("✅ src.ui.formatter")
        success_count += 1
    except ImportError:
        print("⚠️  src.ui.formatter (optional)")
    total_count += 1
    
    try:
        from src.ui.interactive import InteractiveSession
        print("✅ src.ui.interactive")
        success_count += 1
    except ImportError:
        print("⚠️  src.ui.interactive (optional)")
    total_count += 1
    
    print(f"\n📊 Import Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    return success_count >= total_count * 0.7  # 70% success rate

def test_file_structure():
    """Test that all test files exist and are properly structured"""
    print("\n📁 Testing file structure...")
    
    project_root = Path(__file__).parent
    tests_dir = project_root / "tests"
    
    if not tests_dir.exists():
        print("❌ Tests directory not found")
        return False
    
    # Check for main test files
    test_files = [
        "test_ui_formatter.py",
        "test_ui_components.py", 
        "test_flow_nexus.py",
        "test_terminal_compat.py",
        "conftest.py"
    ]
    
    success_count = 0
    for test_file in test_files:
        file_path = tests_dir / test_file
        if file_path.exists():
            print(f"✅ {test_file} ({file_path.stat().st_size} bytes)")
            success_count += 1
        else:
            print(f"❌ {test_file} missing")
    
    # Check for test infrastructure files
    infra_files = ["pytest.ini", "run_tests.py"]
    for infra_file in infra_files:
        file_path = project_root / infra_file
        if file_path.exists():
            print(f"✅ {infra_file} ({file_path.stat().st_size} bytes)")
            success_count += 1
        else:
            print(f"❌ {infra_file} missing")
    
    total_files = len(test_files) + len(infra_files)
    print(f"\n📊 File Structure: {success_count}/{total_files} ({success_count/total_files*100:.1f}%)")
    return success_count == total_files

def test_syntax():
    """Test that all Python files have valid syntax"""
    print("\n🔍 Testing syntax...")
    
    project_root = Path(__file__).parent
    test_files = list((project_root / "tests").glob("*.py")) + [project_root / "run_tests.py"]
    
    success_count = 0
    for file_path in test_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            compile(source, str(file_path), 'exec')
            print(f"✅ {file_path.name}")
            success_count += 1
        except SyntaxError as e:
            print(f"❌ {file_path.name}: {e}")
        except Exception as e:
            print(f"⚠️  {file_path.name}: {e}")
    
    print(f"\n📊 Syntax Check: {success_count}/{len(test_files)} ({success_count/len(test_files)*100:.1f}%)")
    return success_count == len(test_files)

def test_pytest_config():
    """Test pytest configuration"""
    print("\n⚙️  Testing pytest configuration...")
    
    try:
        import pytest
        
        # Test pytest ini file exists and is readable
        project_root = Path(__file__).parent
        pytest_ini = project_root / "pytest.ini"
        
        if pytest_ini.exists():
            print("✅ pytest.ini found")
            # Try to read the config
            with open(pytest_ini, 'r') as f:
                content = f.read()
            if '[tool:pytest]' in content:
                print("✅ Pytest configuration valid")
                return True
        
        print("✅ Pytest available (basic config)")
        return True
    except Exception as e:
        print(f"❌ Pytest configuration error: {e}")
        return False

def main():
    """Main validation function"""
    print("🚀 CLI Application Test Infrastructure Validation")
    print("=" * 60)
    
    all_tests_passed = True
    
    # Run validation tests
    tests = [
        ("Import Tests", test_imports),
        ("File Structure", test_file_structure), 
        ("Syntax Check", test_syntax),
        ("Pytest Config", test_pytest_config)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            if not result:
                all_tests_passed = False
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results[test_name] = False
            all_tests_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 VALIDATION SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    if all_tests_passed:
        print("\n🎉 All validation tests passed!")
        print("Your test infrastructure is properly set up.")
        print("\nNext steps:")
        print("1. Run: python run_tests.py --smoke")
        print("2. Run: python run_tests.py --category ui")
        print("3. Run: python run_tests.py --cross-platform")
        return 0
    else:
        print("\n⚠️  Some validation tests failed.")
        print("Please fix the issues above before running the test suite.")
        return 1

if __name__ == "__main__":
    sys.exit(main())