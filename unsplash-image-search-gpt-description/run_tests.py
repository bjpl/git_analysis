#!/usr/bin/env python3
"""
Test runner script for the Unsplash Image Search GPT Description application.
Provides convenient commands to run different test suites.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    if description:
        print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"Command not found: {cmd[0]}")
        print("Make sure pytest is installed: pip install pytest")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run tests for Unsplash Image Search application")
    parser.add_argument("--suite", choices=[
        "unit", "integration", "performance", "error", "all", "quick", "coverage"
    ], default="quick", help="Test suite to run (default: quick)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--parallel", "-n", type=int, help="Number of parallel workers")
    parser.add_argument("--coverage", action="store_true", help="Include coverage report")
    parser.add_argument("--html-report", action="store_true", help="Generate HTML coverage report")
    parser.add_argument("--markers", "-m", help="Run tests with specific markers")
    parser.add_argument("--keyword", "-k", help="Run tests matching keyword")
    parser.add_argument("--failed", action="store_true", help="Run only previously failed tests")
    
    args = parser.parse_args()

    # Base command
    cmd = ["python", "-m", "pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    
    # Add parallel execution
    if args.parallel:
        cmd.extend(["-n", str(args.parallel)])
    
    # Add coverage
    if args.coverage or args.suite == "coverage":
        cmd.extend(["--cov=main", "--cov=config_manager", "--cov-report=term-missing"])
        if args.html_report:
            cmd.append("--cov-report=html")
    
    # Add markers
    if args.markers:
        cmd.extend(["-m", args.markers])
    
    # Add keyword filtering
    if args.keyword:
        cmd.extend(["-k", args.keyword])
    
    # Add failed tests only
    if args.failed:
        cmd.append("--lf")

    # Determine test paths based on suite
    if args.suite == "unit":
        cmd.append("tests/unit")
        description = "Unit Tests"
    elif args.suite == "integration":
        cmd.append("tests/integration")
        description = "Integration Tests"
    elif args.suite == "performance":
        cmd.extend(["-m", "slow"])
        cmd.append("tests/test_performance.py")
        description = "Performance Tests"
    elif args.suite == "error":
        cmd.append("tests/test_error_handling.py")
        description = "Error Handling Tests"
    elif args.suite == "quick":
        cmd.extend(["-m", "not slow"])
        cmd.append("tests/")
        description = "Quick Tests (excluding slow tests)"
    elif args.suite == "coverage":
        cmd.extend([
            "--cov=main", 
            "--cov=config_manager", 
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-fail-under=80"
        ])
        cmd.append("tests/")
        description = "All Tests with Coverage Report"
    else:  # all
        cmd.append("tests/")
        description = "All Tests"

    # Run the tests
    success = run_command(cmd, description)
    
    if success:
        print(f"\n✅ {description} completed successfully!")
        if args.coverage or args.suite == "coverage":
            print("\n📊 Coverage report:")
            print("- Terminal report shown above")
            if args.html_report or args.suite == "coverage":
                html_path = Path("htmlcov/index.html")
                if html_path.exists():
                    print(f"- HTML report: {html_path.absolute()}")
    else:
        print(f"\n❌ {description} failed!")
        sys.exit(1)


if __name__ == "__main__":
    # Ensure we're in the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("Unsplash Image Search GPT Description - Test Runner")
    print(f"Working directory: {Path.cwd()}")
    
    # Check if pytest is available
    try:
        subprocess.run(["python", "-m", "pytest", "--version"], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n❌ pytest not found!")
        print("Install test dependencies with:")
        print("  pip install -r requirements-dev.txt")
        sys.exit(1)
    
    main()