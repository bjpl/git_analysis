"""
Comprehensive test runner for image collection fix validation.
Runs all test suites and generates a detailed report.
"""

import unittest
import sys
import time
import json
from pathlib import Path
from io import StringIO
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import test modules
from tests.test_image_collection_comprehensive import *
from tests.test_timeout_scenarios import *
from tests.test_cancellation_comprehensive import *
from tests.test_progress_tracking import *

class TestResult:
    """Container for test results."""
    
    def __init__(self):
        self.total_tests = 0
        self.passed = 0
        self.failed = 0
        self.errors = 0
        self.skipped = 0
        self.failures = []
        self.errors_list = []
        self.start_time = None
        self.end_time = None
    
    def add_result(self, result):
        """Add unittest result to our tracking."""
        self.total_tests += result.testsRun
        self.failed += len(result.failures)
        self.errors += len(result.errors)
        self.skipped += len(result.skipped)
        self.passed = self.total_tests - self.failed - self.errors - self.skipped
        
        self.failures.extend(result.failures)
        self.errors_list.extend(result.errors)
    
    @property
    def success_rate(self):
        """Calculate success rate percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed / self.total_tests) * 100
    
    @property
    def duration(self):
        """Calculate test duration."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0

class ComprehensiveTestRunner:
    """Runs all image collection tests and generates report."""
    
    def __init__(self):
        self.result = TestResult()
        self.test_suites = [
            ('Timeout Scenarios', TestConnectionTimeouts, TestReadTimeouts, TestTimeoutRecovery),
            ('API Failure Handling', TestAPIFailureHandling),
            ('Progress Updates', TestProgressBarFunctionality, TestStatusUpdates, 
             TestCollectionLimits, TestSessionStatistics),
            ('Cancellation', TestUserCancellation, TestThreadCancellation, 
             TestCancellationEdgeCases, TestCancellationIntegration),
            ('Image Collection Core', TestImageCollectionTimeouts, TestSearchStateManagement,
             TestManualApplicationFlow)
        ]
    
    def run_all_tests(self, verbosity=2):
        """Run all test suites."""
        print("=" * 80)
        print("COMPREHENSIVE IMAGE COLLECTION TESTS")
        print("=" * 80)
        print(f"Starting test run at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        self.result.start_time = time.time()
        
        for suite_name, *test_classes in self.test_suites:
            print(f"\n{'='*60}")
            print(f"Running {suite_name} Tests")
            print(f"{'='*60}")
            
            # Create test suite
            suite = unittest.TestSuite()
            for test_class in test_classes:
                tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
                suite.addTests(tests)
            
            # Run tests with custom result collector
            stream = StringIO()
            runner = unittest.TextTestRunner(
                stream=stream, 
                verbosity=verbosity,
                buffer=True
            )
            
            suite_result = runner.run(suite)
            self.result.add_result(suite_result)
            
            # Print results for this suite
            print(f"Suite Results: {suite_result.testsRun} tests, "
                  f"{len(suite_result.failures)} failures, "
                  f"{len(suite_result.errors)} errors")
            
            # Print detailed output if requested
            if verbosity >= 2:
                output = stream.getvalue()
                if output.strip():
                    print(output)
        
        self.result.end_time = time.time()
        
        # Generate final report
        self.generate_report()
        
        return self.result.passed == self.result.total_tests
    
    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n" + "="*80)
        print("FINAL TEST REPORT")
        print("="*80)
        
        print(f"Total Tests Run: {self.result.total_tests}")
        print(f"Passed: {self.result.passed}")
        print(f"Failed: {self.result.failed}")
        print(f"Errors: {self.result.errors}")
        print(f"Skipped: {self.result.skipped}")
        print(f"Success Rate: {self.result.success_rate:.1f}%")
        print(f"Duration: {self.result.duration:.2f} seconds")
        
        # Test coverage summary
        print(f"\nTEST COVERAGE SUMMARY:")
        print(f"✓ Timeout scenarios: Connection, read, and recovery timeouts")
        print(f"✓ API failure handling: 403, 429, malformed responses, network errors")
        print(f"✓ Progress tracking: Progress bars, status updates, collection limits")
        print(f"✓ Cancellation: User cancellation, thread cleanup, edge cases")
        print(f"✓ Integration: State management, UI updates, data preservation")
        
        # Detailed failure/error reporting
        if self.result.failures:
            print(f"\nFAILURES ({len(self.result.failures)}):")
            print("-" * 50)
            for test, traceback in self.result.failures:
                print(f"FAILED: {test}")
                print(traceback)
                print()
        
        if self.result.errors_list:
            print(f"\nERRORS ({len(self.result.errors_list)}):")
            print("-" * 50)
            for test, traceback in self.result.errors_list:
                print(f"ERROR: {test}")
                print(traceback)
                print()
        
        # Recommendations based on results
        self.generate_recommendations()
        
        # Save report to file
        self.save_report_to_file()
    
    def generate_recommendations(self):
        """Generate recommendations based on test results."""
        print("\nRECOMMENDATIONS:")
        print("-" * 50)
        
        if self.result.success_rate == 100:
            print("✅ All tests passed! Image collection functionality is robust.")
            print("✅ Timeout handling is working correctly")
            print("✅ Error recovery mechanisms are functioning")
            print("✅ Progress tracking and cancellation are reliable")
            print("✅ Ready for production use")
            
        elif self.result.success_rate >= 90:
            print("⚠️  Most tests passed, but some issues detected:")
            print("   - Review failed tests for potential edge cases")
            print("   - Consider additional error handling for failed scenarios")
            print("   - Test manually in production-like environment")
            
        elif self.result.success_rate >= 75:
            print("⚠️  Significant issues detected:")
            print("   - Multiple test failures indicate systemic problems")
            print("   - Focus on timeout and error handling improvements")
            print("   - Manual testing required before release")
            
        else:
            print("❌ Critical issues detected:")
            print("   - Major functionality problems identified")
            print("   - Code review and debugging required")
            print("   - Do not deploy until issues are resolved")
        
        # Specific recommendations
        if any("timeout" in str(f[0]).lower() for f in self.result.failures + self.result.errors_list):
            print("🔍 Timeout Issues: Review timeout values and retry logic")
            
        if any("cancel" in str(f[0]).lower() for f in self.result.failures + self.result.errors_list):
            print("🔍 Cancellation Issues: Review thread management and cleanup")
            
        if any("progress" in str(f[0]).lower() for f in self.result.failures + self.result.errors_list):
            print("🔍 Progress Issues: Review UI update mechanisms")
    
    def save_report_to_file(self):
        """Save detailed report to file."""
        report_file = Path(__file__).parent / "test_results_report.json"
        
        report_data = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "summary": {
                "total_tests": self.result.total_tests,
                "passed": self.result.passed,
                "failed": self.result.failed,
                "errors": self.result.errors,
                "skipped": self.result.skipped,
                "success_rate": self.result.success_rate,
                "duration": self.result.duration
            },
            "test_suites": [suite[0] for suite in self.test_suites],
            "failures": [{"test": str(f[0]), "traceback": f[1]} for f in self.result.failures],
            "errors": [{"test": str(e[0]), "traceback": e[1]} for e in self.result.errors_list],
            "coverage_areas": [
                "timeout_scenarios",
                "api_failure_handling", 
                "progress_tracking",
                "cancellation_functionality",
                "integration_testing"
            ]
        }
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2)
            print(f"\n📄 Detailed report saved to: {report_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save report file: {e}")

def run_manual_validation():
    """Run manual validation tests."""
    print("\n" + "="*80)
    print("MANUAL VALIDATION CHECKLIST")
    print("="*80)
    print("""
Please manually verify the following scenarios:

1. APPLICATION STARTUP:
   □ App starts without hanging
   □ UI loads completely
   □ All buttons are responsive

2. SEARCH OPERATIONS:
   □ Search completes within reasonable time
   □ Progress bar shows during search
   □ Status updates are visible
   □ Images load successfully

3. TIMEOUT HANDLING:
   □ App handles slow network gracefully
   □ Timeout errors display appropriate messages
   □ App doesn't freeze during timeouts

4. CANCELLATION:
   □ Stop button works during search
   □ Cancelled searches clean up properly
   □ UI returns to normal state after cancellation

5. ERROR RECOVERY:
   □ Network errors show appropriate messages
   □ App recovers from API failures
   □ Rate limiting is handled gracefully

6. COLLECTION LIMITS:
   □ Collection limit reached message appears
   □ Load More button works correctly
   □ Progress tracking is accurate

Run the application and test these scenarios manually.
Report any issues or unexpected behavior.
""")

def main():
    """Main test runner entry point."""
    runner = ComprehensiveTestRunner()
    
    print("Image Collection Fix - Comprehensive Test Suite")
    print("This will run all tests for timeout handling, error recovery,")
    print("progress tracking, and cancellation functionality.\n")
    
    # Run automated tests
    success = runner.run_all_tests(verbosity=2)
    
    # Manual validation reminder
    run_manual_validation()
    
    # Final status
    print("\n" + "="*80)
    if success:
        print("🎉 ALL TESTS PASSED - Image collection fix is working correctly!")
        print("✅ Ready for production deployment")
    else:
        print("❌ SOME TESTS FAILED - Review issues before deployment")
        print("🔍 Check the detailed report and fix identified problems")
    
    print("="*80)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())