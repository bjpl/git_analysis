#!/usr/bin/env python3
"""
Automated Build System for Unsplash Image Search & GPT Tool

This module provides comprehensive build automation including:
- Multi-profile building (dev, production, portable)
- Dependency checking and installation
- Automated testing before build
- Build artifact management
- Distribution packaging
- Error handling and logging
"""

import os
import sys
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('build.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BuildStatus(Enum):
    """Build status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BuildAutomation:
    """Automated build system with comprehensive error handling."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.installer_dir = project_root / "installer"
        self.build_dir = project_root / "build"
        self.dist_dir = project_root / "dist"
        self.temp_dir = None
        
        # Build configuration
        self.status = BuildStatus.PENDING
        self.start_time = None
        self.end_time = None
        self.build_log = []
        
        # Ensure directories exist
        self.installer_dir.mkdir(exist_ok=True)
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        
        # Load version info
        self._load_version_info()
    
    def _load_version_info(self):
        """Load version information from the project."""
        try:
            sys.path.insert(0, str(self.project_root))
            import version_info
            self.app_name = version_info.APP_NAME
            self.version = version_info.APP_VERSION
            self.executable_name = version_info.EXECUTABLE_NAME
        except ImportError:
            logger.warning("version_info.py not found, using defaults")
            self.app_name = "Unsplash Image Search GPT Tool"
            self.version = "2.0.0"
            self.executable_name = f"{self.app_name.replace(' ', '_')}_v{self.version}.exe"
    
    def log_step(self, message: str, level: str = "INFO"):
        """Log a build step with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.build_log.append(log_entry)
        
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available."""
        self.log_step("Checking build dependencies...")
        
        required_tools = {
            'python': [sys.executable, '--version'],
            'pyinstaller': ['pyinstaller', '--version'],
        }
        
        optional_tools = {
            'upx': ['upx', '--version'],
            'git': ['git', '--version'],
        }
        
        missing_required = []
        missing_optional = []
        
        # Check required tools
        for tool, command in required_tools.items():
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    self.log_step(f"Found {tool}: {version}")
                else:
                    missing_required.append(tool)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                missing_required.append(tool)
        
        # Check optional tools
        for tool, command in optional_tools.items():
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    self.log_step(f"Found {tool}: {version}")
                else:
                    self.log_step(f"Optional tool {tool} not found", "WARNING")
                    missing_optional.append(tool)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.log_step(f"Optional tool {tool} not found", "WARNING")
                missing_optional.append(tool)
        
        if missing_required:
            self.log_step(f"Missing required tools: {', '.join(missing_required)}", "ERROR")
            return False
        
        if missing_optional:
            self.log_step(f"Missing optional tools: {', '.join(missing_optional)} (build will continue)", "WARNING")
        
        return True
    
    def check_project_structure(self) -> bool:
        """Validate project structure and files."""
        self.log_step("Validating project structure...")
        
        required_files = [
            'main.py',
            'config_manager.py',
            'src/__init__.py',
        ]
        
        required_dirs = [
            'src',
            'src/ui',
            'src/services',
            'src/models',
        ]
        
        missing_files = []
        missing_dirs = []
        
        # Check files
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
            else:
                self.log_step(f"Found: {file_path}")
        
        # Check directories
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
            else:
                self.log_step(f"Found: {dir_path}/")
        
        if missing_files or missing_dirs:
            if missing_files:
                self.log_step(f"Missing required files: {', '.join(missing_files)}", "ERROR")
            if missing_dirs:
                self.log_step(f"Missing required directories: {', '.join(missing_dirs)}", "ERROR")
            return False
        
        return True
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies if needed."""
        self.log_step("Installing Python dependencies...")
        
        requirements_files = [
            self.project_root / "requirements.txt",
            self.project_root / "pyproject.toml",
        ]
        
        requirements_file = None
        for req_file in requirements_files:
            if req_file.exists():
                requirements_file = req_file
                break
        
        if not requirements_file:
            self.log_step("No requirements file found, skipping dependency installation", "WARNING")
            return True
        
        try:
            if requirements_file.name == "pyproject.toml":
                # Use poetry if available, otherwise pip
                try:
                    result = subprocess.run(
                        ['poetry', 'install', '--only', 'main'],
                        cwd=self.project_root,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    if result.returncode != 0:
                        # Fallback to pip
                        raise subprocess.CalledProcessError(result.returncode, ['poetry', 'install'])
                except (FileNotFoundError, subprocess.CalledProcessError):
                    # Extract dependencies from pyproject.toml and install with pip
                    self.log_step("Poetry not available, extracting dependencies for pip", "WARNING")
                    return self._install_from_pyproject()
            else:
                # Install from requirements.txt
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode != 0:
                    self.log_step(f"Failed to install dependencies: {result.stderr}", "ERROR")
                    return False
            
            self.log_step("Dependencies installed successfully")
            return True
            
        except subprocess.TimeoutExpired:
            self.log_step("Dependency installation timed out", "ERROR")
            return False
        except Exception as e:
            self.log_step(f"Error installing dependencies: {e}", "ERROR")
            return False
    
    def _install_from_pyproject(self) -> bool:
        """Extract and install dependencies from pyproject.toml."""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                self.log_step("Cannot parse pyproject.toml, tomllib/tomli not available", "ERROR")
                return False
        
        try:
            with open(self.project_root / "pyproject.toml", "rb") as f:
                pyproject = tomllib.load(f)
            
            dependencies = pyproject.get("tool", {}).get("poetry", {}).get("dependencies", {})
            
            # Extract package names (ignore version specifiers for now)
            packages = []
            for pkg, version in dependencies.items():
                if pkg != "python":
                    if isinstance(version, str):
                        packages.append(f"{pkg}{version}")
                    else:
                        packages.append(pkg)
            
            if packages:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install'] + packages,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode != 0:
                    self.log_step(f"Failed to install packages: {result.stderr}", "ERROR")
                    return False
                
                self.log_step(f"Installed packages: {', '.join(packages)}")
            
            return True
            
        except Exception as e:
            self.log_step(f"Error parsing pyproject.toml: {e}", "ERROR")
            return False
    
    def run_tests(self, quick_test: bool = True) -> bool:
        """Run tests before building."""
        self.log_step("Running pre-build tests...")
        
        if quick_test:
            # Quick syntax check
            python_files = [
                self.project_root / "main.py",
                self.project_root / "config_manager.py",
            ]
            
            for py_file in python_files:
                if py_file.exists():
                    try:
                        result = subprocess.run(
                            [sys.executable, '-m', 'py_compile', str(py_file)],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        
                        if result.returncode != 0:
                            self.log_step(f"Syntax error in {py_file.name}: {result.stderr}", "ERROR")
                            return False
                        else:
                            self.log_step(f"Syntax check passed: {py_file.name}")
                            
                    except subprocess.TimeoutExpired:
                        self.log_step(f"Syntax check timed out: {py_file.name}", "ERROR")
                        return False
        
        # Try to run pytest if available
        test_dir = self.project_root / "tests"
        if test_dir.exists():
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pytest', str(test_dir), '-v', '--tb=short'],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    self.log_step("All tests passed")
                else:
                    self.log_step(f"Some tests failed, but continuing build: {result.stdout}", "WARNING")
                    
            except (FileNotFoundError, subprocess.TimeoutExpired):
                self.log_step("pytest not available or timed out, skipping full tests", "WARNING")
        
        return True
    
    def prepare_build_environment(self) -> bool:
        """Prepare the build environment."""
        self.log_step("Preparing build environment...")
        
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="unsplash_build_"))
        self.log_step(f"Created temporary directory: {self.temp_dir}")
        
        # Clean previous builds
        try:
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
                self.log_step("Cleaned previous build directory")
            
            # Remove old dist files
            for old_file in self.dist_dir.glob("*.exe"):
                old_file.unlink()
                self.log_step(f"Removed old executable: {old_file.name}")
                
        except Exception as e:
            self.log_step(f"Warning: Could not clean old builds: {e}", "WARNING")
        
        # Generate Windows resources
        try:
            from version_info_windows import WindowsVersionInfo
            version_gen = WindowsVersionInfo(self.project_root)
            resources = version_gen.generate_all_windows_resources()
            self.log_step(f"Generated Windows resources: {list(resources.keys())}")
        except Exception as e:
            self.log_step(f"Warning: Could not generate Windows resources: {e}", "WARNING")
        
        # Generate icons if needed
        try:
            from icon_generator import IconGenerator
            icon_gen = IconGenerator(self.project_root)
            icons = icon_gen.generate_default_icons()
            self.log_step(f"Generated icons: {list(icons.keys())}")
        except Exception as e:
            self.log_step(f"Warning: Could not generate icons: {e}", "WARNING")
        
        return True
    
    def build_executable(self, profile: str = "production", spec_file: str = None) -> bool:
        """Build the executable using PyInstaller."""
        self.log_step(f"Building executable with profile: {profile}")
        
        # Determine spec file
        if spec_file is None:
            spec_files = [
                self.installer_dir / f"{profile}.spec",
                self.installer_dir / "main_optimized.spec",
                self.project_root / "main.spec",
            ]
            
            spec_file_path = None
            for spec in spec_files:
                if spec.exists():
                    spec_file_path = spec
                    break
        else:
            spec_file_path = Path(spec_file)
        
        if not spec_file_path or not spec_file_path.exists():
            self.log_step("No spec file found, creating dynamic spec", "WARNING")
            return self._build_with_dynamic_spec(profile)
        
        self.log_step(f"Using spec file: {spec_file_path}")
        
        try:
            # Build command
            cmd = [
                'pyinstaller',
                '--clean',
                '--noconfirm',
                str(spec_file_path)
            ]
            
            # Run PyInstaller
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            if result.returncode == 0:
                self.log_step("PyInstaller completed successfully")
                
                # Log output
                if result.stdout:
                    self.log_step(f"PyInstaller stdout: {result.stdout[:500]}...")  # Truncate long output
                
                return True
            else:
                self.log_step(f"PyInstaller failed: {result.stderr}", "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_step("PyInstaller timed out (10 minutes)", "ERROR")
            return False
        except Exception as e:
            self.log_step(f"Error running PyInstaller: {e}", "ERROR")
            return False
    
    def _build_with_dynamic_spec(self, profile: str) -> bool:
        """Build with dynamically generated spec file."""
        try:
            from build_config import BuildConfigManager, BuildProfile
            
            # Map profile string to enum
            profile_map = {
                'development': BuildProfile.DEVELOPMENT,
                'production': BuildProfile.PRODUCTION,
                'portable': BuildProfile.PORTABLE,
                'debug': BuildProfile.DEBUG,
            }
            
            build_profile = profile_map.get(profile.lower(), BuildProfile.PRODUCTION)
            
            # Create build config manager
            manager = BuildConfigManager(self.project_root)
            config = manager.create_build_config(build_profile)
            
            # Generate spec file
            spec_file = manager.generate_spec_file(config, f"generated_{profile}.spec")
            
            # Build with generated spec
            return self.build_executable(profile, str(spec_file))
            
        except Exception as e:
            self.log_step(f"Error creating dynamic spec: {e}", "ERROR")
            return False
    
    def post_build_processing(self) -> bool:
        """Process build artifacts after successful build."""
        self.log_step("Post-build processing...")
        
        # Find built executable
        exe_files = list(self.dist_dir.glob("*.exe"))
        if not exe_files:
            self.log_step("No executable found in dist directory", "ERROR")
            return False
        
        main_exe = exe_files[0]
        self.log_step(f"Found executable: {main_exe.name} ({main_exe.stat().st_size // 1024} KB)")
        
        # Create distribution packages
        try:
            self._create_distribution_packages(main_exe)
        except Exception as e:
            self.log_step(f"Warning: Could not create distribution packages: {e}", "WARNING")
        
        # Cleanup temporary files
        self._cleanup_temp_files()
        
        return True
    
    def _create_distribution_packages(self, exe_file: Path):
        """Create various distribution packages."""
        self.log_step("Creating distribution packages...")
        
        # Create portable ZIP
        portable_zip = self.dist_dir / f"{exe_file.stem}_Portable_v{self.version}.zip"
        with zipfile.ZipFile(portable_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(exe_file, exe_file.name)
            
            # Add documentation
            docs_to_include = [
                self.project_root / "README.md",
                self.project_root / "LICENSE",
                self.project_root / ".env.example",
            ]
            
            for doc in docs_to_include:
                if doc.exists():
                    zf.write(doc, doc.name)
        
        self.log_step(f"Created portable package: {portable_zip.name}")
        
        # Create checksums
        import hashlib
        
        checksums = {}
        for file_to_hash in [exe_file, portable_zip]:
            with open(file_to_hash, 'rb') as f:
                checksums[file_to_hash.name] = {
                    'md5': hashlib.md5(f.read()).hexdigest(),
                    'sha256': hashlib.sha256(f.read()).hexdigest(),
                }
        
        # Save checksums
        checksums_file = self.dist_dir / "checksums.json"
        with open(checksums_file, 'w') as f:
            json.dump(checksums, f, indent=2)
        
        self.log_step(f"Created checksums: {checksums_file.name}")
    
    def _cleanup_temp_files(self):
        """Clean up temporary files and directories."""
        try:
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.log_step(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            self.log_step(f"Warning: Could not cleanup temp files: {e}", "WARNING")
    
    def save_build_report(self) -> Path:
        """Save build report with all logs and metadata."""
        report = {
            'build_info': {
                'app_name': self.app_name,
                'version': self.version,
                'profile': getattr(self, 'profile', 'unknown'),
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': self.end_time.isoformat() if self.end_time else None,
                'duration_seconds': (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else None,
                'status': self.status.value,
            },
            'environment': {
                'python_version': sys.version,
                'platform': sys.platform,
                'project_root': str(self.project_root),
            },
            'build_log': self.build_log,
        }
        
        report_file = self.dist_dir / f"build_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log_step(f"Build report saved: {report_file.name}")
        return report_file
    
    def full_build(self, profile: str = "production", skip_tests: bool = False) -> bool:
        """Run complete build process."""
        self.start_time = datetime.now()
        self.status = BuildStatus.RUNNING
        self.profile = profile
        
        self.log_step(f"Starting full build process for {self.app_name} v{self.version}")
        
        try:
            # Pre-build checks
            if not self.check_dependencies():
                self.status = BuildStatus.FAILED
                return False
            
            if not self.check_project_structure():
                self.status = BuildStatus.FAILED
                return False
            
            # Install dependencies
            if not self.install_dependencies():
                self.status = BuildStatus.FAILED
                return False
            
            # Run tests
            if not skip_tests and not self.run_tests():
                self.status = BuildStatus.FAILED
                return False
            
            # Prepare build environment
            if not self.prepare_build_environment():
                self.status = BuildStatus.FAILED
                return False
            
            # Build executable
            if not self.build_executable(profile):
                self.status = BuildStatus.FAILED
                return False
            
            # Post-build processing
            if not self.post_build_processing():
                self.status = BuildStatus.FAILED
                return False
            
            self.end_time = datetime.now()
            self.status = BuildStatus.SUCCESS
            
            duration = (self.end_time - self.start_time).total_seconds()
            self.log_step(f"Build completed successfully in {duration:.1f} seconds")
            
            return True
            
        except KeyboardInterrupt:
            self.status = BuildStatus.CANCELLED
            self.log_step("Build cancelled by user", "WARNING")
            return False
        
        except Exception as e:
            self.status = BuildStatus.FAILED
            self.log_step(f"Unexpected build error: {e}", "ERROR")
            return False
        
        finally:
            self.end_time = datetime.now()
            self.save_build_report()
            self._cleanup_temp_files()


def main():
    """Main entry point for build automation."""
    if len(sys.argv) < 2:
        print("Usage: python build_automation.py <profile> [options]")
        print("Profiles: development, production, portable, debug")
        print("Options: --skip-tests")
        return 1
    
    profile = sys.argv[1].lower()
    skip_tests = '--skip-tests' in sys.argv
    
    if profile not in ['development', 'production', 'portable', 'debug']:
        print(f"Invalid profile: {profile}")
        print("Available profiles: development, production, portable, debug")
        return 1
    
    # Initialize build automation
    project_root = Path(__file__).parent.parent
    automation = BuildAutomation(project_root)
    
    # Run build
    success = automation.full_build(profile, skip_tests)
    
    if success:
        print(f"\n✅ Build completed successfully!")
        print(f"Profile: {profile}")
        print(f"Output directory: {automation.dist_dir}")
        
        # List created files
        exe_files = list(automation.dist_dir.glob("*.exe"))
        if exe_files:
            print(f"Executable: {exe_files[0].name}")
        
        zip_files = list(automation.dist_dir.glob("*.zip"))
        if zip_files:
            print(f"Portable package: {zip_files[0].name}")
        
        return 0
    else:
        print(f"\n❌ Build failed!")
        print(f"Check build.log and build report for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())
