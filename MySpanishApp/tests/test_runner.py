#!/usr/bin/env python3
"""
Test runner script for SpanishMaster application.
Provides a unified interface for running different types of tests with various configurations.
"""

import argparse
import sys
import subprocess
import os
from pathlib import Path
from typing import List, Optional, Dict, Any


class TestRunner:
    """Main test runner class."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tests_dir = Path(__file__).parent
        
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None) -> int:
        """Run a shell command and return exit code."""
        if cwd is None:
            cwd = self.project_root
            
        print(f"Running: {' '.join(cmd)}")
        print(f"Working directory: {cwd}")
        print("-" * 50)
        
        try:
            result = subprocess.run(cmd, cwd=cwd, check=False)
            return result.returncode
        except KeyboardInterrupt:
            print("\nTest run interrupted by user")
            return 1
        except Exception as e:
            print(f"Error running command: {e}")
            return 1
    
    def run_pytest(self, test_path: str = "", extra_args: List[str] = None) -> int:
        """Run pytest with specified path and arguments."""
        cmd = ["python", "-m", "pytest"]
        
        if test_path:
            cmd.append(test_path)
        
        if extra_args:
            cmd.extend(extra_args)
            
        return self.run_command(cmd)
    
    def run_unit_tests(self, verbose: bool = False) -> int:
        """Run unit tests."""
        args = ["tests/unit/", "-v"] if verbose else ["tests/unit/"]
        return self.run_pytest(extra_args=args)
    
    def run_integration_tests(self, verbose: bool = False) -> int:
        """Run integration tests."""
        args = ["tests/integration/", "-v"] if verbose else ["tests/integration/"]
        return self.run_pytest(extra_args=args)
    
    def run_e2e_tests(self, verbose: bool = False) -> int:
        """Run end-to-end tests."""
        args = ["tests/e2e/", "-v", "--maxfail=3"] if verbose else ["tests/e2e/", "--maxfail=3"]
        return self.run_pytest(extra_args=args)
    
    def run_performance_tests(self, verbose: bool = False) -> int:
        """Run performance tests."""
        args = ["tests/performance/", "-v", "-m", "performance", "--durations=0"]
        if not verbose:
            args.remove("-v")
        return self.run_pytest(extra_args=args)
    
    def run_security_tests(self, verbose: bool = False) -> int:
        """Run security tests."""
        args = ["tests/security/", "-v", "-m", "security"] if verbose else ["tests/security/", "-m", "security"]
        return self.run_pytest(extra_args=args)
    
    def run_accessibility_tests(self, verbose: bool = False) -> int:
        """Run accessibility tests."""
        args = ["tests/accessibility/", "-v", "-m", "accessibility"] if verbose else ["tests/accessibility/", "-m", "accessibility"]
        return self.run_pytest(extra_args=args)
    
    def run_gui_tests(self, verbose: bool = False) -> int:
        """Run GUI tests."""
        args = ["-v", "-m", "gui"] if verbose else ["-m", "gui"]
        return self.run_pytest(extra_args=args)
    
    def run_no_gui_tests(self, verbose: bool = False) -> int:
        """Run non-GUI tests."""
        args = ["-v", "-m", "not gui"] if verbose else ["-m", "not gui"]
        return self.run_pytest(extra_args=args)
    
    def run_coverage_tests(self, html: bool = True, xml: bool = False) -> int:
        """Run tests with coverage reporting."""
        args = ["--cov", "--cov-report=term-missing"]
        
        if html:
            args.append("--cov-report=html:tests/coverage_html")
        
        if xml:
            args.append("--cov-report=xml:tests/coverage.xml")
        
        return self.run_pytest(extra_args=args)
    
    def run_fast_tests(self, verbose: bool = False) -> int:
        """Run fast tests (excluding slow and performance tests)."""
        args = ["-v", "-m", "not slow and not performance"] if verbose else ["-m", "not slow and not performance"]
        return self.run_pytest(extra_args=args)
    
    def run_smoke_tests(self, verbose: bool = False) -> int:
        """Run smoke tests (basic functionality)."""
        smoke_tests = [
            "tests/unit/test_database.py",
            "tests/integration/test_app_integration.py::TestDatabaseModelIntegration::test_session_vocab_integration"
        ]
        
        for test in smoke_tests:
            args = [test, "-v"] if verbose else [test]
            result = self.run_pytest(extra_args=args)
            if result != 0:
                return result
        
        return 0
    
    def run_quality_checks(self) -> int:
        """Run all quality checks (linting, type checking, security)."""
        checks = [
            ("Ruff linting", ["python", "-m", "ruff", "check", "models/", "views/", "utils/", "controllers/"]),
            ("MyPy type checking", ["python", "-m", "mypy", "models/", "views/", "utils/", "controllers/"]),
            ("Bandit security scan", ["python", "-m", "bandit", "-r", "models/", "views/", "utils/", "controllers/"]),
            ("Safety vulnerability check", ["python", "-m", "safety", "check"])
        ]
        
        for check_name, cmd in checks:
            print(f"\n{'='*20} {check_name} {'='*20}")
            result = self.run_command(cmd)
            if result != 0:
                print(f"{check_name} failed with exit code {result}")
                return result
        
        print("\nAll quality checks passed!")
        return 0
    
    def run_all_tests(self, verbose: bool = False) -> int:
        """Run comprehensive test suite."""
        test_suites = [
            ("Unit Tests", self.run_unit_tests),
            ("Integration Tests", self.run_integration_tests),
            ("End-to-End Tests", self.run_e2e_tests),
            ("Security Tests", self.run_security_tests),
            ("Accessibility Tests", self.run_accessibility_tests),
        ]
        
        results = {}
        
        for suite_name, test_function in test_suites:
            print(f"\n{'='*20} Running {suite_name} {'='*20}")
            result = test_function(verbose)
            results[suite_name] = result
            
            if result != 0:
                print(f"❌ {suite_name} failed with exit code {result}")
            else:
                print(f"✅ {suite_name} passed")
        
        # Performance tests (run separately as they might be slow)
        print(f"\n{'='*20} Running Performance Tests {'='*20}")
        perf_result = self.run_performance_tests(verbose)
        results["Performance Tests"] = perf_result
        
        if perf_result != 0:
            print(f"⚠️ Performance Tests had issues (exit code {perf_result})")
        else:
            print("✅ Performance Tests passed")
        
        # Generate coverage report
        print(f"\n{'='*20} Generating Coverage Report {'='*20}")
        coverage_result = self.run_coverage_tests(html=True, xml=True)
        
        # Print summary
        print(f"\n{'='*50}")
        print("TEST SUMMARY")
        print(f"{'='*50}")
        
        failed_suites = []
        for suite, result in results.items():
            status = "✅ PASS" if result == 0 else "❌ FAIL"
            print(f"{suite:<25} {status}")
            if result != 0:
                failed_suites.append(suite)
        
        if failed_suites:
            print(f"\n❌ {len(failed_suites)} test suite(s) failed:")
            for suite in failed_suites:
                print(f"  - {suite}")
            return 1
        else:
            print(f"\n🎉 All test suites passed!")
            return 0
    
    def generate_test_report(self) -> int:
        """Generate comprehensive test report."""
        print("Generating comprehensive test report...")
        
        args = [
            "--html=tests/test_report.html",
            "--self-contained-html",
            "--cov",
            "--cov-report=html:tests/coverage_html",
            "--cov-report=xml:tests/coverage.xml"
        ]
        
        result = self.run_pytest(extra_args=args)
        
        if result == 0:
            print("📊 Test report generated:")
            print(f"  - HTML Report: {self.tests_dir}/test_report.html")
            print(f"  - Coverage Report: {self.tests_dir}/coverage_html/index.html")
            print(f"  - Coverage XML: {self.tests_dir}/coverage.xml")
        
        return result
    
    def list_tests(self) -> int:
        """List all available tests."""
        return self.run_pytest(extra_args=["--collect-only", "-q"])
    
    def list_markers(self) -> int:
        """List all test markers."""
        return self.run_pytest(extra_args=["--markers"])


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="SpanishMaster Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_runner.py --unit --verbose
  python test_runner.py --all
  python test_runner.py --coverage
  python test_runner.py --quality
  python test_runner.py --fast
        """
    )
    
    # Test type arguments
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--security", action="store_true", help="Run security tests")
    parser.add_argument("--accessibility", action="store_true", help="Run accessibility tests")
    parser.add_argument("--gui", action="store_true", help="Run GUI tests")
    parser.add_argument("--no-gui", action="store_true", help="Run non-GUI tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--fast", action="store_true", help="Run fast tests only")
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests")
    
    # Special commands
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--quality", action="store_true", help="Run quality checks")
    parser.add_argument("--report", action="store_true", help="Generate test report")
    parser.add_argument("--list-tests", action="store_true", help="List all tests")
    parser.add_argument("--list-markers", action="store_true", help="List test markers")
    
    # Options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--html", action="store_true", help="Generate HTML coverage report")
    parser.add_argument("--xml", action="store_true", help="Generate XML coverage report")
    
    # Custom test path
    parser.add_argument("--path", type=str, help="Custom test path")
    parser.add_argument("--args", type=str, help="Additional pytest arguments")
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    runner = TestRunner()
    
    # Handle list commands first
    if args.list_tests:
        return runner.list_tests()
    
    if args.list_markers:
        return runner.list_markers()
    
    # Handle special commands
    if args.quality:
        return runner.run_quality_checks()
    
    if args.report:
        return runner.generate_test_report()
    
    if args.coverage:
        return runner.run_coverage_tests(html=args.html or True, xml=args.xml)
    
    # Handle custom path
    if args.path:
        extra_args = []
        if args.verbose:
            extra_args.append("-v")
        if args.args:
            extra_args.extend(args.args.split())
        return runner.run_pytest(args.path, extra_args)
    
    # Handle test types
    if args.all:
        return runner.run_all_tests(args.verbose)
    
    if args.smoke:
        return runner.run_smoke_tests(args.verbose)
    
    if args.fast:
        return runner.run_fast_tests(args.verbose)
    
    if args.unit:
        return runner.run_unit_tests(args.verbose)
    
    if args.integration:
        return runner.run_integration_tests(args.verbose)
    
    if args.e2e:
        return runner.run_e2e_tests(args.verbose)
    
    if args.performance:
        return runner.run_performance_tests(args.verbose)
    
    if args.security:
        return runner.run_security_tests(args.verbose)
    
    if args.accessibility:
        return runner.run_accessibility_tests(args.verbose)
    
    if args.gui:
        return runner.run_gui_tests(args.verbose)
    
    if args.no_gui:
        return runner.run_no_gui_tests(args.verbose)
    
    # If we get here, no test type was specified
    print("No test type specified. Use --help for available options.")
    return 1


if __name__ == "__main__":
    sys.exit(main())