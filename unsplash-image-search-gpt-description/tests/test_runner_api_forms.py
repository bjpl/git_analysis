"""
Test runner specifically for API key form tests.

Runs all API key form-related tests and generates a comprehensive report.
"""

import unittest
import sys
import time
from pathlib import Path
from io import StringIO
import traceback

# Add paths for test imports
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir / 'unit'))
sys.path.insert(0, str(test_dir / 'integration'))
sys.path.insert(0, str(test_dir.parent / 'src'))
sys.path.insert(0, str(test_dir.parent))

# Import test modules
try:
    from test_api_key_form import (
        TestAPIKeyValidation,
        TestSubmitButtonFunctionality,
        TestKeyboardNavigation,
        TestErrorHandling,
        TestFormCancellation,
        TestSettingsPersistence,
        TestFirstRunExperience,
        TestAccessibilityFeatures,
        TestAPIKeyVisibilityToggle
    )
except ImportError as e:
    print(f"Warning: Could not import basic form tests: {e}")

try:
    from test_secure_setup_wizard import (
        TestSecureSetupWizardForm,
        TestKeyboardNavigationSecure,
        TestValidationIntegration
    )
except ImportError as e:
    print(f"Warning: Could not import secure wizard tests: {e}")

try:
    from test_api_setup_wizard import (
        TestAPISetupWizardInterface,
        TestAPIKeyFormFunctionality,
        TestHelpSystemFunctionality,
        TestWizardCompletion,
        TestAccessibilityAndUsability
    )
except ImportError as e:
    print(f"Warning: Could not import API setup wizard tests: {e}")

try:
    from test_api_key_form_integration import (
        TestAPIKeyFormIntegration,
        TestAPIValidationIntegration,
        TestFormStatePersistence,
        TestConcurrentFormOperations,
        TestErrorHandlingIntegration
    )
except ImportError as e:
    print(f"Warning: Could not import integration tests: {e}")


class APIFormTestResult:
    """Custom test result collector for API form tests."""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
    def start_timing(self):
        """Start timing the test run."""
        self.start_time = time.time()
        
    def end_timing(self):
        """End timing the test run."""
        self.end_time = time.time()
        
    def add_result(self, test_class_name, result):
        """Add a test class result."""
        self.test_results[test_class_name] = {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'success_rate': self._calculate_success_rate(result),
            'failure_details': result.failures,
            'error_details': result.errors
        }
    
    def _calculate_success_rate(self, result):
        """Calculate success rate for a test result."""
        if result.testsRun == 0:
            return 0.0
        return (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    
    def get_summary(self):
        """Get overall summary of test results."""
        total_tests = sum(r['tests_run'] for r in self.test_results.values())
        total_failures = sum(r['failures'] for r in self.test_results.values())
        total_errors = sum(r['errors'] for r in self.test_results.values())
        
        overall_success_rate = 0.0
        if total_tests > 0:
            overall_success_rate = (total_tests - total_failures - total_errors) / total_tests * 100
        
        duration = 0.0
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            
        return {
            'total_tests': total_tests,
            'total_failures': total_failures,
            'total_errors': total_errors,
            'overall_success_rate': overall_success_rate,
            'duration': duration,
            'test_classes': len(self.test_results)
        }


class APIFormTestRunner:
    """Custom test runner for API form tests."""
    
    def __init__(self):
        self.result = APIFormTestResult()
        
    def run_test_class(self, test_class, class_name):
        """Run a single test class and capture results."""
        print(f"\nRunning {class_name}...")
        print("=" * 60)
        
        # Capture output
        output_buffer = StringIO()
        
        try:
            # Create test suite for this class
            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
            
            # Run tests with custom runner
            runner = unittest.TextTestRunner(
                stream=output_buffer,
                verbosity=2,
                buffer=True
            )
            
            test_result = runner.run(suite)
            
            # Add to our results
            self.result.add_result(class_name, test_result)
            
            # Print summary for this class
            success_rate = self.result.test_results[class_name]['success_rate']
            print(f"Tests run: {test_result.testsRun}")
            print(f"Failures: {len(test_result.failures)}")
            print(f"Errors: {len(test_result.errors)}")
            print(f"Success rate: {success_rate:.1f}%")
            
            if test_result.failures:
                print(f"\nFailures in {class_name}:")
                for test, trace in test_result.failures:
                    print(f"  - {test.id()}")
                    
            if test_result.errors:
                print(f"\nErrors in {class_name}:")
                for test, trace in test_result.errors:
                    print(f"  - {test.id()}")
                    
        except Exception as e:
            print(f"ERROR: Failed to run {class_name}: {e}")
            traceback.print_exc()
            
    def run_all_tests(self):
        """Run all API form tests."""
        print("API Key Form Test Suite")
        print("=" * 60)
        print("Testing comprehensive API key form functionality")
        print("=" * 60)
        
        self.result.start_timing()
        
        # Define test categories and their classes
        test_categories = {
            "Basic Form Validation": [
                ('TestAPIKeyValidation', TestAPIKeyValidation),
                ('TestSubmitButtonFunctionality', TestSubmitButtonFunctionality),
                ('TestKeyboardNavigation', TestKeyboardNavigation),
            ],
            "Error Handling & Recovery": [
                ('TestErrorHandling', TestErrorHandling),
                ('TestFormCancellation', TestFormCancellation),
            ],
            "Configuration & Persistence": [
                ('TestSettingsPersistence', TestSettingsPersistence),
                ('TestFirstRunExperience', TestFirstRunExperience),
            ],
            "Accessibility & Usability": [
                ('TestAccessibilityFeatures', TestAccessibilityFeatures),
                ('TestAPIKeyVisibilityToggle', TestAPIKeyVisibilityToggle),
            ],
            "Secure Setup Wizard": [
                ('TestSecureSetupWizardForm', TestSecureSetupWizardForm),
                ('TestKeyboardNavigationSecure', TestKeyboardNavigationSecure),
                ('TestValidationIntegration', TestValidationIntegration),
            ],
            "API Setup Wizard": [
                ('TestAPISetupWizardInterface', TestAPISetupWizardInterface),
                ('TestAPIKeyFormFunctionality', TestAPIKeyFormFunctionality),
                ('TestHelpSystemFunctionality', TestHelpSystemFunctionality),
                ('TestWizardCompletion', TestWizardCompletion),
                ('TestAccessibilityAndUsability', TestAccessibilityAndUsability),
            ],
            "Integration Tests": [
                ('TestAPIKeyFormIntegration', TestAPIKeyFormIntegration),
                ('TestAPIValidationIntegration', TestAPIValidationIntegration),
                ('TestFormStatePersistence', TestFormStatePersistence),
                ('TestConcurrentFormOperations', TestConcurrentFormOperations),
                ('TestErrorHandlingIntegration', TestErrorHandlingIntegration),
            ]
        }
        
        # Run tests by category
        for category, test_classes in test_categories.items():
            print(f"\n{'='*20} {category} {'='*20}")
            
            for class_name, test_class in test_classes:
                try:
                    # Check if class exists (handle import failures)
                    if test_class and hasattr(test_class, '__name__'):
                        self.run_test_class(test_class, class_name)
                    else:
                        print(f"SKIPPED: {class_name} (not available)")
                except NameError:
                    print(f"SKIPPED: {class_name} (import failed)")
                except Exception as e:
                    print(f"ERROR: {class_name} failed: {e}")
        
        self.result.end_timing()
        
    def generate_report(self):
        """Generate comprehensive test report."""
        summary = self.result.get_summary()
        
        print("\n" + "="*80)
        print("API KEY FORM TEST REPORT")
        print("="*80)
        
        # Overall Summary
        print(f"Test Duration: {summary['duration']:.2f} seconds")
        print(f"Test Classes: {summary['test_classes']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Total Failures: {summary['total_failures']}")
        print(f"Total Errors: {summary['total_errors']}")
        print(f"Overall Success Rate: {summary['overall_success_rate']:.1f}%")
        
        # Detailed Results by Test Class
        print(f"\nDETAILED RESULTS BY TEST CLASS:")
        print("-" * 80)
        
        for class_name, result in self.result.test_results.items():
            status = "PASS" if result['failures'] == 0 and result['errors'] == 0 else "FAIL"
            print(f"{class_name:<40} {status:>6} ({result['success_rate']:>5.1f}%) "
                  f"Tests: {result['tests_run']:>3} F: {result['failures']:>2} E: {result['errors']:>2}")
        
        # Test Coverage Analysis
        print(f"\nTEST COVERAGE ANALYSIS:")
        print("-" * 80)
        
        coverage_areas = {
            "Form Validation Logic": ["TestAPIKeyValidation"],
            "Submit Button Functionality": ["TestSubmitButtonFunctionality"],
            "Keyboard Navigation": ["TestKeyboardNavigation", "TestKeyboardNavigationSecure"],
            "Error Handling": ["TestErrorHandling", "TestErrorHandlingIntegration"],
            "Form Cancellation": ["TestFormCancellation"],
            "Settings Persistence": ["TestSettingsPersistence", "TestFormStatePersistence"],
            "First Run Experience": ["TestFirstRunExperience"],
            "Accessibility": ["TestAccessibilityFeatures", "TestAccessibilityAndUsability"],
            "API Key Visibility": ["TestAPIKeyVisibilityToggle"],
            "Integration Testing": ["TestAPIKeyFormIntegration", "TestAPIValidationIntegration"],
            "Concurrent Operations": ["TestConcurrentFormOperations"],
            "Wizard Interfaces": ["TestSecureSetupWizardForm", "TestAPISetupWizardInterface"],
            "Help System": ["TestHelpSystemFunctionality"],
        }
        
        for area, test_classes in coverage_areas.items():
            covered_tests = [tc for tc in test_classes if tc in self.result.test_results]
            total_tests = sum(self.result.test_results[tc]['tests_run'] 
                            for tc in covered_tests)
            failed_tests = sum(self.result.test_results[tc]['failures'] + 
                             self.result.test_results[tc]['errors'] 
                             for tc in covered_tests)
            
            coverage_status = "COVERED" if total_tests > 0 else "NOT COVERED"
            success_rate = (total_tests - failed_tests) / total_tests * 100 if total_tests > 0 else 0
            
            print(f"{area:<30} {coverage_status:>12} "
                  f"Tests: {total_tests:>3} Success: {success_rate:>5.1f}%")
        
        # Recommendations
        print(f"\nRECOMMENDATIONS:")
        print("-" * 80)
        
        if summary['overall_success_rate'] < 80:
            print("❌ Overall success rate is below 80%. Priority fixes needed.")
        elif summary['overall_success_rate'] < 95:
            print("⚠️  Overall success rate is below 95%. Some improvements recommended.")
        else:
            print("✅ Excellent test success rate! API forms are well-tested.")
            
        if summary['total_errors'] > 0:
            print(f"🔧 {summary['total_errors']} test errors need investigation.")
            
        if summary['total_failures'] > 0:
            print(f"🐛 {summary['total_failures']} test failures need fixing.")
        
        # Priority Issues
        high_failure_classes = [
            name for name, result in self.result.test_results.items()
            if result['success_rate'] < 50
        ]
        
        if high_failure_classes:
            print(f"\nHIGH PRIORITY (< 50% success rate):")
            for class_name in high_failure_classes:
                result = self.result.test_results[class_name]
                print(f"  - {class_name}: {result['success_rate']:.1f}% success")
        
        print("\n" + "="*80)
        return summary


def main():
    """Main entry point for API form test runner."""
    try:
        # Create and run test runner
        runner = APIFormTestRunner()
        
        print("Starting API Key Form Test Suite...")
        runner.run_all_tests()
        
        # Generate comprehensive report
        summary = runner.generate_report()
        
        # Save results to file
        try:
            report_file = Path(__file__).parent / "api_form_test_results.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                # Capture the report output
                original_stdout = sys.stdout
                sys.stdout = f
                runner.generate_report()
                sys.stdout = original_stdout
            
            print(f"\nTest report saved to: {report_file}")
        except Exception as e:
            print(f"Warning: Could not save report to file: {e}")
        
        # Exit with appropriate code
        if summary['total_failures'] > 0 or summary['total_errors'] > 0:
            print("\n❌ Some tests failed. Check the detailed report above.")
            sys.exit(1)
        else:
            print("\n✅ All tests passed successfully!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\nTest run interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nFATAL ERROR: Test runner failed: {e}")
        traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()