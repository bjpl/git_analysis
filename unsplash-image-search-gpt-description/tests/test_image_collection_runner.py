"""
Comprehensive test runner for image collection functionality.
Executes all tests and generates detailed reports with validation results.
"""

import pytest
import sys
import json
import time
import psutil
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import traceback
import subprocess


@dataclass
class TestResult:
    """Test result data structure."""
    test_name: str
    status: str  # passed, failed, skipped, error
    duration: float
    memory_usage: int
    error_message: Optional[str] = None
    traceback: Optional[str] = None


@dataclass
class TestSuiteResult:
    """Test suite result data structure."""
    suite_name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    total_duration: float
    peak_memory: int
    results: List[TestResult]


class MemoryMonitor:
    """Monitor memory usage during test execution."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss
        self.peak_memory = self.initial_memory
        self.monitoring = False
    
    def start(self):
        """Start monitoring memory usage."""
        self.monitoring = True
        self.initial_memory = self.process.memory_info().rss
        self.peak_memory = self.initial_memory
    
    def update(self):
        """Update peak memory usage."""
        if self.monitoring:
            current_memory = self.process.memory_info().rss
            self.peak_memory = max(self.peak_memory, current_memory)
    
    def stop(self) -> int:
        """Stop monitoring and return peak memory usage."""
        self.monitoring = False
        return self.peak_memory - self.initial_memory


class ImageCollectionTestRunner:
    """Comprehensive test runner for image collection functionality."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_dir = project_root / "tests"
        self.memory_monitor = MemoryMonitor()
        self.results: Dict[str, TestSuiteResult] = {}
        
        # Ensure test directories exist
        self.test_dir.mkdir(exist_ok=True)
        (self.test_dir / "unit").mkdir(exist_ok=True)
        (self.test_dir / "integration").mkdir(exist_ok=True)
        (self.test_dir / "fixtures").mkdir(exist_ok=True)
    
    def run_all_tests(self) -> Dict[str, TestSuiteResult]:
        """Run all image collection tests."""
        print("🚀 Starting Comprehensive Image Collection Test Suite")
        print("=" * 60)
        
        # Define test suites to run
        test_suites = [
            {
                "name": "Unit Tests - Image Collection",
                "path": self.test_dir / "unit" / "test_image_collection.py",
                "markers": ["unit", "not slow"]
            },
            {
                "name": "Unit Tests - Unsplash Service", 
                "path": self.test_dir / "unit" / "test_services" / "test_unsplash_service.py",
                "markers": ["unit", "not slow"]
            },
            {
                "name": "Integration Tests - Image Collection",
                "path": self.test_dir / "integration" / "test_image_collection_integration.py",
                "markers": ["integration", "not slow"]
            },
            {
                "name": "Performance Tests",
                "path": self.test_dir / "unit" / "test_image_collection.py",
                "markers": ["performance"]
            },
            {
                "name": "Memory Tests",
                "path": self.test_dir / "unit" / "test_image_collection.py",
                "markers": ["unit", "TestMemoryManagement"]
            },
            {
                "name": "Error Handling Tests",
                "path": self.test_dir / "unit" / "test_image_collection.py",
                "markers": ["unit", "TestNetworkErrorHandling"]
            }
        ]
        
        overall_start_time = time.time()
        
        for suite_config in test_suites:
            if suite_config["path"].exists():
                result = self.run_test_suite(
                    suite_config["name"],
                    suite_config["path"],
                    suite_config["markers"]
                )
                self.results[suite_config["name"]] = result
            else:
                print(f"⚠️  Skipping {suite_config['name']} - test file not found")
        
        overall_duration = time.time() - overall_start_time
        
        # Generate comprehensive report
        self.generate_report(overall_duration)
        
        return self.results
    
    def run_test_suite(
        self, 
        suite_name: str, 
        test_path: Path, 
        markers: List[str]
    ) -> TestSuiteResult:
        """Run a specific test suite."""
        print(f"\n🧪 Running: {suite_name}")
        print(f"📁 Path: {test_path}")
        print(f"🏷️  Markers: {', '.join(markers)}")
        
        self.memory_monitor.start()
        start_time = time.time()
        
        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_path),
            "-v",
            "--tb=short",
            "--json-report",
            f"--json-report-file={self.test_dir / (suite_name.lower().replace(' ', '_') + '_report.json')}",
            "--strict-markers"
        ]
        
        # Add marker filters
        for marker in markers:
            if marker.startswith("not "):
                cmd.extend(["-m", f"not {marker[4:]}"])
            else:
                cmd.extend(["-m", marker])
        
        # Add coverage if requested
        if os.getenv("COVERAGE", "false").lower() == "true":
            cmd.extend([
                "--cov=.",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov"
            ])
        
        try:
            # Run tests
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            duration = time.time() - start_time
            peak_memory = self.memory_monitor.stop()
            
            # Parse results
            suite_result = self.parse_test_results(
                suite_name, 
                result, 
                duration, 
                peak_memory
            )
            
            # Print summary
            self.print_suite_summary(suite_result)
            
            return suite_result
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            peak_memory = self.memory_monitor.stop()
            
            print(f"❌ {suite_name} timed out after 5 minutes")
            
            return TestSuiteResult(
                suite_name=suite_name,
                total_tests=0,
                passed=0,
                failed=1,
                skipped=0,
                errors=0,
                total_duration=duration,
                peak_memory=peak_memory,
                results=[TestResult(
                    test_name="timeout",
                    status="error",
                    duration=duration,
                    memory_usage=peak_memory,
                    error_message="Test suite timed out"
                )]
            )
        
        except Exception as e:
            duration = time.time() - start_time
            peak_memory = self.memory_monitor.stop()
            
            print(f"❌ Error running {suite_name}: {str(e)}")
            
            return TestSuiteResult(
                suite_name=suite_name,
                total_tests=0,
                passed=0,
                failed=0,
                skipped=0,
                errors=1,
                total_duration=duration,
                peak_memory=peak_memory,
                results=[TestResult(
                    test_name="execution_error",
                    status="error",
                    duration=duration,
                    memory_usage=peak_memory,
                    error_message=str(e),
                    traceback=traceback.format_exc()
                )]
            )
    
    def parse_test_results(
        self, 
        suite_name: str, 
        result: subprocess.CompletedProcess,
        duration: float,
        peak_memory: int
    ) -> TestSuiteResult:
        """Parse test results from pytest output."""
        
        # Try to load JSON report first
        json_report_file = self.test_dir / f"{suite_name.lower().replace(' ', '_')}_report.json"
        if json_report_file.exists():
            try:
                with open(json_report_file, 'r') as f:
                    json_data = json.load(f)
                return self.parse_json_report(suite_name, json_data, duration, peak_memory)
            except Exception as e:
                print(f"⚠️  Could not parse JSON report: {e}")
        
        # Fall back to parsing text output
        return self.parse_text_output(suite_name, result, duration, peak_memory)
    
    def parse_json_report(
        self, 
        suite_name: str, 
        json_data: Dict[str, Any],
        duration: float,
        peak_memory: int
    ) -> TestSuiteResult:
        """Parse JSON test report."""
        summary = json_data.get("summary", {})
        tests = json_data.get("tests", [])
        
        test_results = []
        for test in tests:
            test_results.append(TestResult(
                test_name=test.get("nodeid", "unknown"),
                status=test.get("outcome", "unknown"),
                duration=test.get("duration", 0.0),
                memory_usage=0,  # Not available in JSON report
                error_message=test.get("call", {}).get("longrepr", None) if test.get("outcome") == "failed" else None
            ))
        
        return TestSuiteResult(
            suite_name=suite_name,
            total_tests=summary.get("total", 0),
            passed=summary.get("passed", 0),
            failed=summary.get("failed", 0),
            skipped=summary.get("skipped", 0),
            errors=summary.get("error", 0),
            total_duration=duration,
            peak_memory=peak_memory,
            results=test_results
        )
    
    def parse_text_output(
        self, 
        suite_name: str, 
        result: subprocess.CompletedProcess,
        duration: float,
        peak_memory: int
    ) -> TestSuiteResult:
        """Parse text output from pytest."""
        output = result.stdout + result.stderr
        
        # Extract basic statistics
        passed = output.count("PASSED")
        failed = output.count("FAILED")
        skipped = output.count("SKIPPED")
        errors = output.count("ERROR")
        total_tests = passed + failed + skipped + errors
        
        # Create basic test results
        test_results = []
        if total_tests > 0:
            # Try to extract individual test results
            lines = output.split('\n')
            for line in lines:
                if " PASSED " in line or " FAILED " in line or " SKIPPED " in line or " ERROR " in line:
                    parts = line.split(' ')
                    test_name = parts[0] if parts else "unknown"
                    status = "unknown"
                    
                    if " PASSED " in line:
                        status = "passed"
                    elif " FAILED " in line:
                        status = "failed"
                    elif " SKIPPED " in line:
                        status = "skipped"
                    elif " ERROR " in line:
                        status = "error"
                    
                    test_results.append(TestResult(
                        test_name=test_name,
                        status=status,
                        duration=0.0,  # Not available from text output
                        memory_usage=0,
                        error_message=line if status in ["failed", "error"] else None
                    ))
        
        return TestSuiteResult(
            suite_name=suite_name,
            total_tests=total_tests,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            total_duration=duration,
            peak_memory=peak_memory,
            results=test_results
        )
    
    def print_suite_summary(self, result: TestSuiteResult):
        """Print summary for a test suite."""
        print(f"📊 Results for {result.suite_name}:")
        print(f"   ✅ Passed: {result.passed}")
        print(f"   ❌ Failed: {result.failed}")
        print(f"   ⏭️  Skipped: {result.skipped}")
        print(f"   💥 Errors: {result.errors}")
        print(f"   ⏱️  Duration: {result.total_duration:.2f}s")
        print(f"   💾 Peak Memory: {result.peak_memory / 1024 / 1024:.1f}MB")
        
        if result.failed > 0 or result.errors > 0:
            print("   🔍 Failures/Errors:")
            for test_result in result.results:
                if test_result.status in ["failed", "error"]:
                    print(f"     - {test_result.test_name}: {test_result.error_message}")
    
    def generate_report(self, overall_duration: float):
        """Generate comprehensive test report."""
        print("\n" + "=" * 80)
        print("📋 COMPREHENSIVE IMAGE COLLECTION TEST REPORT")
        print("=" * 80)
        
        # Overall statistics
        total_tests = sum(result.total_tests for result in self.results.values())
        total_passed = sum(result.passed for result in self.results.values())
        total_failed = sum(result.failed for result in self.results.values())
        total_skipped = sum(result.skipped for result in self.results.values())
        total_errors = sum(result.errors for result in self.results.values())
        peak_memory = max((result.peak_memory for result in self.results.values()), default=0)
        
        print(f"\n📈 OVERALL STATISTICS:")
        print(f"   Total Test Suites: {len(self.results)}")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {total_passed}")
        print(f"   ❌ Failed: {total_failed}")
        print(f"   ⏭️  Skipped: {total_skipped}")
        print(f"   💥 Errors: {total_errors}")
        print(f"   ⏱️  Total Duration: {overall_duration:.2f}s")
        print(f"   💾 Peak Memory Usage: {peak_memory / 1024 / 1024:.1f}MB")
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        print(f"   🎯 Success Rate: {success_rate:.1f}%")
        
        # Detailed results by suite
        print(f"\n📊 DETAILED RESULTS BY SUITE:")
        for suite_name, result in self.results.items():
            status_icon = "✅" if result.failed == 0 and result.errors == 0 else "❌"
            print(f"   {status_icon} {suite_name}:")
            print(f"      Tests: {result.total_tests} | Passed: {result.passed} | Failed: {result.failed} | Errors: {result.errors}")
            print(f"      Duration: {result.total_duration:.2f}s | Memory: {result.peak_memory / 1024 / 1024:.1f}MB")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        
        if total_failed == 0 and total_errors == 0:
            print("   🎉 All tests passed successfully!")
            print("   ✨ Image collection functionality is working correctly")
        else:
            print(f"   ⚠️  {total_failed + total_errors} tests failed or had errors")
            print("   🔧 Review failed tests and fix issues before deployment")
        
        # Performance insights
        if peak_memory > 500 * 1024 * 1024:  # > 500MB
            print("   💾 High memory usage detected - review memory management")
        else:
            print("   💾 Memory usage within acceptable limits")
        
        if overall_duration > 60:  # > 1 minute
            print("   ⏱️  Long test duration - consider optimizing slow tests")
        else:
            print("   ⏱️  Test execution time acceptable")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if total_failed > 0:
            print("   1. Fix failing tests before proceeding with deployment")
            print("   2. Review error messages and stack traces")
            print("   3. Consider adding more specific assertions")
        
        if total_skipped > total_tests * 0.2:  # > 20% skipped
            print("   4. High number of skipped tests - review test requirements")
        
        if success_rate < 90:
            print("   5. Success rate below 90% - improve test stability")
        
        print("   6. Run tests regularly during development")
        print("   7. Add more edge case tests as new scenarios are discovered")
        print("   8. Monitor memory usage in production")
        
        # Save report to file
        self.save_report_to_file(overall_duration)
        
        print(f"\n📄 Full report saved to: {self.test_dir / 'image_collection_test_report.json'}")
        print("=" * 80)
    
    def save_report_to_file(self, overall_duration: float):
        """Save detailed report to JSON file."""
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "overall_duration": overall_duration,
            "summary": {
                "total_suites": len(self.results),
                "total_tests": sum(result.total_tests for result in self.results.values()),
                "total_passed": sum(result.passed for result in self.results.values()),
                "total_failed": sum(result.failed for result in self.results.values()),
                "total_skipped": sum(result.skipped for result in self.results.values()),
                "total_errors": sum(result.errors for result in self.results.values()),
                "peak_memory_mb": max((result.peak_memory for result in self.results.values()), default=0) / 1024 / 1024
            },
            "suites": {}
        }
        
        for suite_name, result in self.results.items():
            report_data["suites"][suite_name] = {
                "total_tests": result.total_tests,
                "passed": result.passed,
                "failed": result.failed,
                "skipped": result.skipped,
                "errors": result.errors,
                "duration": result.total_duration,
                "peak_memory_mb": result.peak_memory / 1024 / 1024,
                "test_results": [
                    {
                        "name": test.test_name,
                        "status": test.status,
                        "duration": test.duration,
                        "error_message": test.error_message
                    }
                    for test in result.results
                ]
            }
        
        report_file = self.test_dir / "image_collection_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)


def main():
    """Main entry point for test runner."""
    print("🎯 Image Collection Test Suite Runner")
    print("=====================================\n")
    
    # Get project root directory
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    
    print(f"📁 Project Root: {project_root}")
    print(f"🧪 Test Directory: {current_dir}")
    
    # Initialize and run test runner
    runner = ImageCollectionTestRunner(project_root)
    
    try:
        results = runner.run_all_tests()
        
        # Determine exit code
        total_failed = sum(result.failed for result in results.values())
        total_errors = sum(result.errors for result in results.values())
        
        if total_failed > 0 or total_errors > 0:
            print(f"\n❌ Tests failed - exit code 1")
            sys.exit(1)
        else:
            print(f"\n✅ All tests passed - exit code 0")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()