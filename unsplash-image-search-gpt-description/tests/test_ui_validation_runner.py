"""
Comprehensive UI validation test runner.
This script runs all UI-related tests and provides a summary of UI rendering health.
"""

import pytest
import sys
import os
import subprocess
import time
import threading
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
from contextlib import contextmanager

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))


class UIValidationRunner:
    """Runs comprehensive UI validation tests and reports results."""
    
    def __init__(self):
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': [],
            'test_duration': 0
        }
        
    def run_all_ui_tests(self):
        """Run all UI-related tests and collect results."""
        print("🔍 Starting comprehensive UI validation tests...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test suites to run
        test_suites = [
            {
                'name': 'UI Rendering Tests',
                'path': 'tests/unit/test_ui_rendering.py',
                'description': 'Tests widget creation, packing, and visibility'
            },
            {
                'name': 'UI Accessibility Tests', 
                'path': 'tests/integration/test_ui_accessibility.py',
                'description': 'Tests focus handling, keyboard navigation, and themes'
            },
            {
                'name': 'Main Application Tests',
                'path': 'tests/test_main.py',
                'description': 'Tests main application initialization'
            }
        ]
        
        all_results = []
        
        for suite in test_suites:
            print(f"\n🧪 Running: {suite['name']}")
            print(f"   {suite['description']}")
            print("-" * 40)
            
            result = self._run_test_suite(suite['path'])
            all_results.append({
                'suite': suite['name'],
                'result': result
            })
            
            if result['success']:
                print(f"✅ {suite['name']}: PASSED ({result['passed']} tests)")
            else:
                print(f"❌ {suite['name']}: FAILED ({result['failed']} failures)")
                if result['errors']:
                    for error in result['errors'][:3]:  # Show first 3 errors
                        print(f"   • {error}")
        
        end_time = time.time()
        self.results['test_duration'] = end_time - start_time
        
        # Compile overall results
        self._compile_results(all_results)
        self._print_summary()
        
        return self.results
    
    def _run_test_suite(self, test_path):
        """Run a specific test suite and capture results."""
        test_file = project_root / test_path
        
        if not test_file.exists():
            return {
                'success': False,
                'passed': 0,
                'failed': 1,
                'skipped': 0,
                'errors': [f'Test file not found: {test_path}']
            }
        
        try:
            # Run pytest with specific flags for UI testing
            cmd = [
                sys.executable, '-m', 'pytest',
                str(test_file),
                '-v',
                '--tb=short',
                '--no-header',
                '-x',  # Stop on first failure for UI tests
                '--disable-warnings',  # Reduce noise in output
            ]
            
            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=120  # 2-minute timeout for UI tests
            )
            
            return self._parse_pytest_output(result)
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'passed': 0,
                'failed': 1,
                'skipped': 0,
                'errors': ['Test suite timed out (UI may be hanging)']
            }
        except Exception as e:
            return {
                'success': False,
                'passed': 0,
                'failed': 1,
                'skipped': 0,
                'errors': [f'Failed to run test suite: {str(e)}']
            }
    
    def _parse_pytest_output(self, result):
        """Parse pytest output to extract test results."""
        output = result.stdout + result.stderr
        
        # Extract test counts from pytest output
        passed = output.count(' PASSED')
        failed = output.count(' FAILED') + output.count(' ERROR')
        skipped = output.count(' SKIPPED')
        
        # Extract error messages
        errors = []
        if result.returncode != 0:
            lines = output.split('\n')
            for i, line in enumerate(lines):
                if 'FAILED' in line or 'ERROR' in line:
                    errors.append(line.strip())
                elif 'AssertionError' in line or 'Exception' in line:
                    errors.append(line.strip())
        
        return {
            'success': result.returncode == 0,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'errors': errors[:5]  # Limit to first 5 errors
        }
    
    def _compile_results(self, all_results):
        """Compile results from all test suites."""
        for suite_result in all_results:
            result = suite_result['result']
            self.results['total_tests'] += result['passed'] + result['failed'] + result['skipped']
            self.results['passed'] += result['passed']
            self.results['failed'] += result['failed']
            self.results['skipped'] += result['skipped']
            self.results['errors'].extend(result['errors'])
    
    def _print_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "=" * 60)
        print("🏁 UI VALIDATION SUMMARY")
        print("=" * 60)
        
        total = self.results['total_tests']
        passed = self.results['passed']
        failed = self.results['failed']
        skipped = self.results['skipped']
        
        if total == 0:
            print("⚠️  No tests were executed!")
            return
        
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"📊 Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"⏱️  Duration: {self.results['test_duration']:.2f}s")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL UI TESTS PASSED!")
            print("✨ The UI should load correctly without rendering issues.")
        else:
            print(f"\n⚠️  {failed} test(s) failed.")
            print("🔧 UI may have rendering or functionality issues.")
            
            if self.results['errors']:
                print("\n🐛 Key Issues Found:")
                for i, error in enumerate(self.results['errors'][:5], 1):
                    print(f"   {i}. {error}")
                if len(self.results['errors']) > 5:
                    print(f"   ... and {len(self.results['errors']) - 5} more")
        
        print("\n💡 Recommendations:")
        if failed > 0:
            print("   • Check that all required dependencies are installed")
            print("   • Verify API keys are properly configured")
            print("   • Ensure X11 forwarding is enabled for headless environments")
            print("   • Run individual test files for detailed error information")
        else:
            print("   • UI validation complete - application should start normally")
            print("   • Consider running with real API keys for full integration testing")


class QuickUIHealthCheck:
    """Quick health check for UI components."""
    
    @staticmethod
    def check_tkinter_availability():
        """Check if tkinter is available and working."""
        try:
            root = tk.Tk()
            root.withdraw()
            root.destroy()
            return True, "Tkinter is available and working"
        except Exception as e:
            return False, f"Tkinter error: {str(e)}"
    
    @staticmethod
    def check_imports():
        """Check if critical UI modules can be imported."""
        critical_imports = [
            ('config_manager', 'ConfigManager'),
            ('main', 'ImageSearchApp'),
        ]
        
        issues = []
        
        for module_name, class_name in critical_imports:
            try:
                module = __import__(module_name)
                if hasattr(module, class_name):
                    getattr(module, class_name)
                else:
                    issues.append(f"Class {class_name} not found in {module_name}")
            except ImportError as e:
                issues.append(f"Cannot import {module_name}: {str(e)}")
            except Exception as e:
                issues.append(f"Error with {module_name}.{class_name}: {str(e)}")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def check_config_structure():
        """Check if configuration structure is valid."""
        try:
            from config_manager import ConfigManager
            config = ConfigManager()
            
            # Test basic operations
            api_keys = config.get_api_keys()
            paths = config.get_paths()
            
            required_keys = ['unsplash', 'openai', 'gpt_model']
            required_paths = ['data_dir', 'log_file', 'vocabulary_file']
            
            missing_keys = [key for key in required_keys if key not in api_keys]
            missing_paths = [path for path in required_paths if path not in paths]
            
            issues = []
            if missing_keys:
                issues.append(f"Missing API key fields: {missing_keys}")
            if missing_paths:
                issues.append(f"Missing path fields: {missing_paths}")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Configuration error: {str(e)}"]
    
    def run_health_check(self):
        """Run complete health check."""
        print("🏥 Running Quick UI Health Check...")
        print("-" * 40)
        
        checks = [
            ("Tkinter Availability", self.check_tkinter_availability),
            ("Critical Imports", self.check_imports),
            ("Configuration Structure", self.check_config_structure)
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            try:
                success, result = check_func()
                
                if success:
                    print(f"✅ {check_name}: OK")
                    if isinstance(result, str):
                        print(f"   {result}")
                else:
                    print(f"❌ {check_name}: FAILED")
                    all_passed = False
                    
                    if isinstance(result, list):
                        for issue in result:
                            print(f"   • {issue}")
                    else:
                        print(f"   {result}")
                        
            except Exception as e:
                print(f"❌ {check_name}: ERROR - {str(e)}")
                all_passed = False
        
        print("-" * 40)
        if all_passed:
            print("🎉 Health Check Passed!")
            print("✨ UI components should initialize correctly.")
        else:
            print("⚠️  Health Check Issues Found!")
            print("🔧 Please resolve issues before running full tests.")
        
        return all_passed


def main():
    """Main entry point for UI validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='UI Validation Test Runner')
    parser.add_argument(
        '--quick', 
        action='store_true', 
        help='Run quick health check only'
    )
    parser.add_argument(
        '--full',
        action='store_true',
        help='Run full test suite (default)'
    )
    
    args = parser.parse_args()
    
    if args.quick:
        # Run quick health check
        health_checker = QuickUIHealthCheck()
        success = health_checker.run_health_check()
        sys.exit(0 if success else 1)
    else:
        # Run full test suite
        print("🚀 UI Validation Test Runner")
        print("Testing UI rendering, accessibility, and functionality...")
        print()
        
        # First run health check
        health_checker = QuickUIHealthCheck()
        health_passed = health_checker.run_health_check()
        
        if not health_passed:
            print("\n⚠️  Health check failed. Skipping full tests.")
            print("Fix health check issues and try again.")
            sys.exit(1)
        
        print("\n🏃 Proceeding to full test suite...\n")
        
        # Run full validation
        runner = UIValidationRunner()
        results = runner.run_all_ui_tests()
        
        # Exit with appropriate code
        sys.exit(0 if results['failed'] == 0 else 1)


if __name__ == '__main__':
    main()