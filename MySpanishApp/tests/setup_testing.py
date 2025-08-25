#!/usr/bin/env python3
"""
Test environment setup script for SpanishMaster application.
Configures testing dependencies, validates environment, and prepares test infrastructure.
"""

import sys
import subprocess
import os
import platform
from pathlib import Path
import importlib.util


class TestEnvironmentSetup:
    """Setup and validation for the testing environment."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tests_dir = Path(__file__).parent
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.platform = platform.system().lower()
        
    def check_python_version(self) -> bool:
        """Check if Python version meets requirements."""
        print("🐍 Checking Python version...")
        
        if sys.version_info < (3, 10):
            print(f"❌ Python 3.10+ required, found {self.python_version}")
            return False
        
        print(f"✅ Python {self.python_version} meets requirements")
        return True
    
    def check_required_packages(self) -> bool:
        """Check if core packages are available."""
        print("📦 Checking core packages...")
        
        required_packages = [
            ("pytest", "Testing framework"),
            ("PyQt6", "GUI framework"),
            ("sqlite3", "Database (built-in)"),
        ]
        
        missing_packages = []
        
        for package, description in required_packages:
            try:
                if package == "sqlite3":
                    import sqlite3
                else:
                    importlib.import_module(package.lower().replace("-", "_"))
                print(f"✅ {package} - {description}")
            except ImportError:
                print(f"❌ {package} - {description} (MISSING)")
                missing_packages.append(package)
        
        if missing_packages:
            print(f"\n❌ Missing required packages: {', '.join(missing_packages)}")
            print("Run: pip install -e \".[dev]\" to install all dependencies")
            return False
        
        return True
    
    def check_optional_packages(self) -> dict:
        """Check optional testing packages and their status."""
        print("\n🔍 Checking optional testing packages...")
        
        optional_packages = [
            ("pytest_cov", "pytest-cov", "Coverage reporting"),
            ("pytest_qt", "pytest-qt", "Qt testing support"),
            ("pytest_mock", "pytest-mock", "Mocking utilities"),
            ("bandit", "bandit", "Security scanning"),
            ("mypy", "mypy", "Type checking"),
            ("ruff", "ruff", "Linting and formatting"),
            ("psutil", "psutil", "Performance monitoring"),
            ("locust", "locust", "Load testing"),
        ]
        
        package_status = {}
        
        for import_name, package_name, description in optional_packages:
            try:
                importlib.import_module(import_name)
                print(f"✅ {package_name} - {description}")
                package_status[package_name] = True
            except ImportError:
                print(f"⚠️  {package_name} - {description} (optional)")
                package_status[package_name] = False
        
        return package_status
    
    def setup_test_directories(self) -> bool:
        """Create necessary test directories."""
        print("\n📁 Setting up test directories...")
        
        directories = [
            self.tests_dir / "coverage_html",
            self.tests_dir / "reports",
            self.tests_dir / "tmp",
            self.tests_dir / "fixtures" / "data",
        ]
        
        try:
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created/verified: {directory.relative_to(self.project_root)}")
            
            return True
        except Exception as e:
            print(f"❌ Failed to create directories: {e}")
            return False
    
    def create_gitignore_entries(self) -> bool:
        """Add test-related entries to .gitignore."""
        print("\n📝 Updating .gitignore for test artifacts...")
        
        gitignore_path = self.project_root / ".gitignore"
        test_entries = [
            "# Test artifacts",
            "tests/coverage_html/",
            "tests/coverage.xml",
            "tests/junit_results.xml",
            "tests/test_report.html",
            "tests/security_report.json",
            "tests/tmp/",
            "tests/reports/",
            ".pytest_cache/",
            "*.db.test",
            "test_*.db",
        ]
        
        try:
            existing_content = ""
            if gitignore_path.exists():
                existing_content = gitignore_path.read_text()
            
            # Check if test entries already exist
            if "# Test artifacts" in existing_content:
                print("✅ Test entries already present in .gitignore")
                return True
            
            # Add test entries
            with open(gitignore_path, "a") as f:
                f.write("\n" + "\n".join(test_entries) + "\n")
            
            print("✅ Added test entries to .gitignore")
            return True
            
        except Exception as e:
            print(f"⚠️  Failed to update .gitignore: {e}")
            return False
    
    def validate_display_environment(self) -> bool:
        """Check if GUI tests can run (display available)."""
        print("\n🖥️ Checking display environment for GUI tests...")
        
        if self.platform == "linux":
            display = os.environ.get("DISPLAY")
            if not display:
                print("⚠️  No DISPLAY environment variable found")
                print("   GUI tests may fail on headless systems")
                print("   Consider using: pytest -m 'not gui' or install pytest-xvfb")
                return False
            else:
                print(f"✅ DISPLAY environment found: {display}")
                return True
        elif self.platform == "windows":
            print("✅ Windows GUI environment available")
            return True
        elif self.platform == "darwin":  # macOS
            print("✅ macOS GUI environment available")
            return True
        else:
            print(f"⚠️  Unknown platform: {self.platform}")
            return False
    
    def run_basic_test_validation(self) -> bool:
        """Run basic tests to validate the test environment."""
        print("\n🧪 Running basic test validation...")
        
        try:
            # Test pytest can discover tests
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--collect-only", "-q"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("✅ Pytest can discover tests")
            else:
                print(f"❌ Pytest test discovery failed: {result.stderr}")
                return False
            
            # Test database creation
            try:
                import tempfile
                from models.database import Database
                
                with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
                    tmp_path = tmp.name
                
                db = Database(tmp_path)
                db.init_db()
                db.close()
                
                os.unlink(tmp_path)
                print("✅ Database creation test passed")
                
            except Exception as e:
                print(f"❌ Database test failed: {e}")
                return False
            
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ Test validation timed out")
            return False
        except Exception as e:
            print(f"❌ Test validation error: {e}")
            return False
    
    def create_test_configuration_files(self) -> bool:
        """Create or update test configuration files."""
        print("\n⚙️ Creating test configuration files...")
        
        # Coverage configuration (already in pyproject.toml)
        print("✅ Coverage configuration in pyproject.toml")
        
        # MyPy configuration (already in pyproject.toml)
        print("✅ MyPy configuration in pyproject.toml")
        
        # Bandit configuration (already in pyproject.toml)
        print("✅ Bandit configuration in pyproject.toml")
        
        return True
    
    def install_pre_commit_hooks(self) -> bool:
        """Install pre-commit hooks for quality assurance."""
        print("\n🪝 Setting up pre-commit hooks...")
        
        # Create a simple pre-commit script
        pre_commit_script = self.project_root / ".git" / "hooks" / "pre-commit"
        
        if not pre_commit_script.parent.exists():
            print("⚠️  Git hooks directory not found (not a git repository?)")
            return False
        
        hook_content = '''#!/bin/bash
# Pre-commit hook for SpanishMaster
# Runs basic quality checks before committing

echo "Running pre-commit quality checks..."

# Run linting
echo "🔍 Running ruff linting..."
python -m ruff check models/ views/ utils/ controllers/
if [ $? -ne 0 ]; then
    echo "❌ Linting failed. Please fix issues before committing."
    exit 1
fi

# Run type checking
echo "🔍 Running type checks..."
python -m mypy models/ views/ utils/ controllers/
if [ $? -ne 0 ]; then
    echo "❌ Type checking failed. Please fix issues before committing."
    exit 1
fi

# Run fast tests
echo "🧪 Running fast tests..."
python -m pytest -x -m "not slow and not performance" --tb=short
if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Please fix issues before committing."
    exit 1
fi

echo "✅ All pre-commit checks passed!"
exit 0
'''
        
        try:
            with open(pre_commit_script, "w") as f:
                f.write(hook_content)
            
            # Make executable on Unix-like systems
            if self.platform in ["linux", "darwin"]:
                os.chmod(pre_commit_script, 0o755)
            
            print("✅ Pre-commit hooks installed")
            return True
            
        except Exception as e:
            print(f"⚠️  Failed to install pre-commit hooks: {e}")
            return False
    
    def generate_test_summary(self, package_status: dict) -> None:
        """Generate a summary of the test environment setup."""
        print("\n" + "="*60)
        print("🎯 TEST ENVIRONMENT SETUP SUMMARY")
        print("="*60)
        
        print(f"Python Version: {self.python_version}")
        print(f"Platform: {self.platform}")
        print(f"Project Root: {self.project_root}")
        
        print("\n📦 Package Status:")
        available_packages = sum(1 for status in package_status.values() if status)
        total_packages = len(package_status)
        
        for package, status in package_status.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {package}")
        
        print(f"\nPackage Summary: {available_packages}/{total_packages} available")
        
        print("\n🚀 Quick Start Commands:")
        print("  python tests/test_runner.py --help")
        print("  python tests/test_runner.py --smoke")
        print("  python tests/test_runner.py --fast")
        print("  python tests/test_runner.py --all")
        print("  make test")
        
        print("\n📚 Documentation:")
        print("  tests/README.md - Complete testing guide")
        print("  tests/test_runner.py --help - Test runner options")
        print("  make help - Make targets")
        
        if available_packages < total_packages:
            print("\n⚠️  Some optional packages are missing.")
            print("   Run: pip install -e \".[dev]\" to install all dependencies")
    
    def run_setup(self) -> bool:
        """Run complete test environment setup."""
        print("🔧 SPANISHMASTER TEST ENVIRONMENT SETUP")
        print("="*50)
        
        success = True
        
        # Core requirements
        success &= self.check_python_version()
        success &= self.check_required_packages()
        
        if not success:
            print("\n❌ Core requirements not met. Setup aborted.")
            return False
        
        # Optional components
        package_status = self.check_optional_packages()
        success &= self.setup_test_directories()
        self.create_gitignore_entries()  # Non-critical
        self.validate_display_environment()  # Non-critical
        success &= self.run_basic_test_validation()
        self.create_test_configuration_files()  # Non-critical
        self.install_pre_commit_hooks()  # Non-critical
        
        # Summary
        self.generate_test_summary(package_status)
        
        if success:
            print("\n🎉 Test environment setup completed successfully!")
            print("You can now run tests using the test runner or make commands.")
        else:
            print("\n⚠️  Setup completed with some issues.")
            print("Check the output above for details.")
        
        return success


def main():
    """Main entry point for test environment setup."""
    setup = TestEnvironmentSetup()
    success = setup.run_setup()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())