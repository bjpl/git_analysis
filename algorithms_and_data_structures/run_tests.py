#!/usr/bin/env python3
"""
Test runner script for CLI application with comprehensive testing options.

This script provides easy access to different test suites and configurations:
- Run all tests or specific test categories
- Cross-platform compatibility testing
- Performance benchmarking
- Generate detailed reports
- CI/CD integration support
"""

import sys
import os
import subprocess
import argparse
import platform
from pathlib import Path
from typing import List, Dict, Any


class TestRunner:
    """Comprehensive test runner for the CLI application"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_dir = self.project_root / "tests"
        self.reports_dir = self.project_root / "test_reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Platform information
        self.platform = platform.system().lower()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        
        # Test categories
        self.test_categories = {
            'unit': 'Unit tests for individual components',
            'integration': 'Integration tests for component interaction',
            'ui': 'UI component and formatting tests',
            'formatter': 'Terminal formatter functionality tests',
            'terminal': 'Cross-platform terminal compatibility tests',
            'cloud': 'Cloud integration and MCP tool tests',
            'performance': 'Performance and benchmark tests',
            'slow': 'Slow-running comprehensive tests',
            'cross_platform': 'Cross-platform compatibility tests'
        }
    
    def run_command(self, cmd: List[str], capture_output: bool = False) -> subprocess.CompletedProcess:
        """Run a command and handle errors"""
        try:
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=capture_output,
                text=True,
                check=False
            )
            return result
        except FileNotFoundError as e:
            print(f"Error: {e}")
            print("Make sure pytest is installed: pip install pytest pytest-cov pytest-asyncio")
            sys.exit(1)
    
    def install_dependencies(self):
        """Install test dependencies if needed"""
        dependencies = [
            'pytest>=6.0',
            'pytest-cov',
            'pytest-asyncio',
            'pytest-timeout',
            'pytest-xdist',  # For parallel execution
            'pytest-html',   # For HTML reports
            'pytest-mock',   # For advanced mocking
        ]
        
        print("Installing test dependencies...")
        cmd = [sys.executable, '-m', 'pip', 'install'] + dependencies
        result = self.run_command(cmd, capture_output=True)
        
        if result.returncode != 0:
            print(f"Warning: Could not install some dependencies: {result.stderr}")
    
    def run_all_tests(self, args: argparse.Namespace):
        """Run all tests with comprehensive reporting"""
        print("🚀 Running comprehensive test suite...")
        
        cmd = [
            'python', '-m', 'pytest',
            str(self.test_dir),
            '--verbose',
            '--tb=short',
            f'--cov=src',
            '--cov-report=term-missing',
            f'--cov-report=html:{self.reports_dir}/coverage_html',
            f'--cov-report=xml:{self.reports_dir}/coverage.xml',
            '--cov-fail-under=75',
            f'--html={self.reports_dir}/test_report.html',
            '--self-contained-html',
            '--durations=10'
        ]
        
        if args.parallel:
            cmd.extend(['-n', 'auto'])
        
        if args.timeout:
            cmd.extend(['--timeout', str(args.timeout)])
        
        result = self.run_command(cmd)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed.")
            print(f"📊 Test report available at: {self.reports_dir}/test_report.html")
        
        return result.returncode
    
    def run_category_tests(self, category: str, args: argparse.Namespace):
        """Run tests for a specific category"""
        if category not in self.test_categories:
            print(f"❌ Unknown test category: {category}")
            print(f"Available categories: {', '.join(self.test_categories.keys())}")
            return 1
        
        print(f"🧪 Running {category} tests: {self.test_categories[category]}")
        
        cmd = [
            'python', '-m', 'pytest',
            str(self.test_dir),
            '-m', category,
            '--verbose',
            '--tb=short'
        ]
        
        if args.coverage:
            cmd.extend([
                '--cov=src',
                '--cov-report=term-missing',
                f'--cov-report=html:{self.reports_dir}/coverage_{category}'
            ])
        
        if args.parallel and category not in ['slow', 'performance']:
            cmd.extend(['-n', 'auto'])
        
        result = self.run_command(cmd)
        return result.returncode
    
    def run_specific_tests(self, test_files: List[str], args: argparse.Namespace):
        """Run specific test files"""
        print(f"🎯 Running specific tests: {', '.join(test_files)}")
        
        # Validate test files exist
        valid_files = []
        for test_file in test_files:
            if not test_file.startswith('test_'):
                test_file = f"test_{test_file}"
            if not test_file.endswith('.py'):
                test_file = f"{test_file}.py"
            
            full_path = self.test_dir / test_file
            if full_path.exists():
                valid_files.append(str(full_path))
            else:
                print(f"⚠️ Test file not found: {full_path}")
        
        if not valid_files:
            print("❌ No valid test files found")
            return 1
        
        cmd = [
            'python', '-m', 'pytest',
            *valid_files,
            '--verbose',
            '--tb=short'
        ]
        
        if args.coverage:
            cmd.extend(['--cov=src', '--cov-report=term-missing'])
        
        result = self.run_command(cmd)
        return result.returncode
    
    def run_cross_platform_tests(self, args: argparse.Namespace):
        """Run cross-platform compatibility tests"""
        print(f"🌐 Running cross-platform tests on {self.platform}...")
        
        # Platform-specific test selection
        platform_markers = {
            'windows': 'windows or cross_platform',
            'linux': 'linux or cross_platform',
            'darwin': 'macos or cross_platform'
        }
        
        marker = platform_markers.get(self.platform, 'cross_platform')
        
        cmd = [
            'python', '-m', 'pytest',
            str(self.test_dir),
            '-m', marker,
            '--verbose',
            '--tb=short',
            f'--html={self.reports_dir}/cross_platform_report.html',
            '--self-contained-html'
        ]
        
        if args.coverage:
            cmd.extend([
                '--cov=src',
                f'--cov-report=html:{self.reports_dir}/coverage_cross_platform'
            ])
        
        result = self.run_command(cmd)
        
        if result.returncode == 0:
            print(f"✅ Cross-platform tests passed on {self.platform}")
        else:
            print(f"❌ Some cross-platform tests failed on {self.platform}")
        
        return result.returncode
    
    def run_performance_tests(self, args: argparse.Namespace):
        """Run performance and benchmark tests"""
        print("⚡ Running performance tests...")
        
        cmd = [
            'python', '-m', 'pytest',
            str(self.test_dir),
            '-m', 'performance',
            '--verbose',
            '--tb=short',
            '--durations=0',  # Show all durations
            f'--html={self.reports_dir}/performance_report.html',
            '--self-contained-html'
        ]
        
        # Longer timeout for performance tests
        if args.timeout:
            cmd.extend(['--timeout', str(args.timeout * 2)])
        
        result = self.run_command(cmd)
        return result.returncode
    
    def run_ci_tests(self, args: argparse.Namespace):
        """Run tests optimized for CI/CD environments"""
        print("🤖 Running CI-optimized tests...")
        
        cmd = [
            'python', '-m', 'pytest',
            str(self.test_dir),
            '--verbose',
            '--tb=short',
            '--maxfail=10',  # Fail fast in CI
            '--cov=src',
            '--cov-report=xml',
            '--cov-fail-under=75',
            '-m', 'not slow'  # Skip slow tests in CI
        ]
        
        if args.parallel:
            cmd.extend(['-n', 'auto'])
        
        if args.timeout:
            cmd.extend(['--timeout', str(args.timeout)])
        
        result = self.run_command(cmd)
        
        # Generate JUnit XML for CI systems
        if result.returncode == 0:
            junit_cmd = cmd + ['--junitxml=test-results.xml']
            self.run_command(junit_cmd)
        
        return result.returncode
    
    def run_smoke_tests(self, args: argparse.Namespace):
        """Run quick smoke tests"""
        print("💨 Running smoke tests...")
        
        # Run a subset of critical tests quickly
        smoke_tests = [
            'test_ui_formatter.py::TestTerminalCompatibility::test_color_detection_linux_bash',
            'test_ui_components.py::TestInteractiveSessionCore::test_session_initialization',
            'test_terminal_compat.py::TestPlatformCompatibility::test_linux_bash_compatibility'
        ]
        
        cmd = [
            'python', '-m', 'pytest',
            *[str(self.test_dir / test) for test in smoke_tests],
            '--verbose',
            '--tb=short',
            '--maxfail=1'
        ]
        
        result = self.run_command(cmd)
        
        if result.returncode == 0:
            print("✅ Smoke tests passed - basic functionality works")
        else:
            print("❌ Smoke tests failed - check basic functionality")
        
        return result.returncode
    
    def list_tests(self):
        """List available tests and categories"""
        print("📋 Available test categories:")
        for category, description in self.test_categories.items():
            print(f"  • {category:15} - {description}")
        
        print("\n📁 Available test files:")
        for test_file in sorted(self.test_dir.glob("test_*.py")):
            print(f"  • {test_file.name}")
        
        print(f"\n🖥️  Platform: {self.platform}")
        print(f"🐍 Python: {self.python_version}")
    
    def clean_reports(self):
        """Clean up old test reports"""
        print("🧹 Cleaning up old test reports...")
        
        import shutil
        if self.reports_dir.exists():
            shutil.rmtree(self.reports_dir)
            self.reports_dir.mkdir()
        
        # Clean up root-level reports
        root_reports = [
            'test-results.xml',
            'coverage.xml',
            '.coverage',
            'htmlcov'
        ]
        
        for report in root_reports:
            path = self.project_root / report
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
        
        print("✅ Reports cleaned")


def main():
    """Main entry point for test runner"""
    parser = argparse.ArgumentParser(
        description="Comprehensive test runner for CLI application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                          # Run all tests
  python run_tests.py --category ui            # Run UI tests only
  python run_tests.py --files formatter        # Run formatter tests
  python run_tests.py --cross-platform         # Run cross-platform tests
  python run_tests.py --performance            # Run performance tests
  python run_tests.py --ci                     # Run CI-optimized tests
  python run_tests.py --smoke                  # Run quick smoke tests
  python run_tests.py --list                   # List available tests
        """
    )
    
    # Main commands
    parser.add_argument('--category', '-c', 
                       help='Run tests for specific category')
    parser.add_argument('--files', '-f', nargs='+',
                       help='Run specific test files')
    parser.add_argument('--cross-platform', action='store_true',
                       help='Run cross-platform compatibility tests')
    parser.add_argument('--performance', action='store_true',
                       help='Run performance tests')
    parser.add_argument('--ci', action='store_true',
                       help='Run CI-optimized tests')
    parser.add_argument('--smoke', action='store_true',
                       help='Run quick smoke tests')
    parser.add_argument('--list', action='store_true',
                       help='List available tests and categories')
    
    # Options
    parser.add_argument('--coverage', action='store_true',
                       help='Generate coverage reports')
    parser.add_argument('--parallel', '-p', action='store_true',
                       help='Run tests in parallel')
    parser.add_argument('--timeout', type=int, default=300,
                       help='Test timeout in seconds (default: 300)')
    parser.add_argument('--install-deps', action='store_true',
                       help='Install test dependencies')
    parser.add_argument('--clean', action='store_true',
                       help='Clean up old test reports')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Handle utility commands first
    if args.clean:
        runner.clean_reports()
        return 0
    
    if args.install_deps:
        runner.install_dependencies()
        return 0
    
    if args.list:
        runner.list_tests()
        return 0
    
    # Run tests based on arguments
    if args.smoke:
        return runner.run_smoke_tests(args)
    elif args.ci:
        return runner.run_ci_tests(args)
    elif args.performance:
        return runner.run_performance_tests(args)
    elif args.cross_platform:
        return runner.run_cross_platform_tests(args)
    elif args.category:
        return runner.run_category_tests(args.category, args)
    elif args.files:
        return runner.run_specific_tests(args.files, args)
    else:
        # Default: run all tests
        return runner.run_all_tests(args)


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)