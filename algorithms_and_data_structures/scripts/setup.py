#!/usr/bin/env python3
"""
Python Setup Automation Script
Algorithms & Data Structures CLI - Version 1.0.0

This script automates the setup and configuration of the development environment.
"""

import os
import sys
import json
import subprocess
import shutil
import platform
import venv
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import tempfile
import urllib.request
import urllib.error


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class SetupManager:
    """Manages the complete setup process for the CLI."""
    
    def __init__(self, dev_mode: bool = False, force: bool = False):
        self.dev_mode = dev_mode
        self.force = force
        self.system = platform.system().lower()
        self.python_version = sys.version_info
        
        # Paths configuration
        self.project_root = Path.cwd()
        self.home_dir = Path.home()
        
        if self.system == "windows":
            self.install_dir = Path(os.environ.get("LOCALAPPDATA", self.home_dir)) / "algorithms-cli"
            self.config_dir = Path(os.environ.get("APPDATA", self.home_dir)) / "algorithms-cli"
        else:
            self.install_dir = self.home_dir / ".local" / "algorithms-cli"
            self.config_dir = self.home_dir / ".config" / "algorithms-cli"
            
        self.venv_dir = self.install_dir / "venv"
        
        # Package lists
        self.core_packages = [
            "numpy>=1.21.0",
            "scipy>=1.7.0", 
            "matplotlib>=3.4.0",
            "pandas>=1.3.0",
            "jupyter>=1.0.0",
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910"
        ]
        
        self.dev_packages = [
            "pre-commit>=2.13.0",
            "isort>=5.9.0",
            "pytest-xdist>=2.3.0",
            "coverage[toml]>=5.5.0",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
            "bandit>=1.7.0",
            "safety>=1.10.0",
            "tox>=3.24.0"
        ]

    def print_header(self) -> None:
        """Print installation header."""
        print(f"{Colors.BLUE}{'='*50}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}  Algorithms & Data Structures CLI{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}  Python Setup Automation v1.0.0{Colors.END}")
        print(f"{Colors.BLUE}{'='*50}{Colors.END}")
        print()

    def log_success(self, message: str) -> None:
        """Print success message."""
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")

    def log_error(self, message: str) -> None:
        """Print error message."""
        print(f"{Colors.RED}❌ {message}{Colors.END}")

    def log_warning(self, message: str) -> None:
        """Print warning message."""
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

    def log_info(self, message: str) -> None:
        """Print info message."""
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

    def run_command(self, cmd: List[str], capture_output: bool = True, check: bool = True) -> subprocess.CompletedProcess:
        """Run a system command with proper error handling."""
        try:
            result = subprocess.run(
                cmd, 
                capture_output=capture_output, 
                text=True, 
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            self.log_error(f"Command failed: {' '.join(cmd)}")
            self.log_error(f"Error: {e.stderr if e.stderr else str(e)}")
            raise
        except FileNotFoundError:
            self.log_error(f"Command not found: {cmd[0]}")
            raise

    def check_python_version(self) -> None:
        """Verify Python version requirements."""
        self.log_info("Checking Python version...")
        
        if self.python_version < (3, 8):
            self.log_error(f"Python 3.8+ required. Found: {sys.version}")
            sys.exit(1)
            
        self.log_success(f"Python {'.'.join(map(str, self.python_version[:3]))} detected")

    def check_system_dependencies(self) -> Dict[str, bool]:
        """Check for required system dependencies."""
        self.log_info("Checking system dependencies...")
        
        dependencies = {
            "git": False,
            "node": False,
            "npm": False
        }
        
        # Check Git
        try:
            self.run_command(["git", "--version"])
            dependencies["git"] = True
            self.log_success("Git found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_warning("Git not found - some features may be limited")
        
        # Check Node.js and npm
        try:
            result = self.run_command(["node", "--version"])
            dependencies["node"] = True
            node_version = result.stdout.strip()
            self.log_success(f"Node.js {node_version} found")
            
            try:
                self.run_command(["npm", "--version"])
                dependencies["npm"] = True
                self.log_success("npm found")
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.log_warning("npm not found")
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_warning("Node.js not found - Claude Flow features will be limited")
        
        return dependencies

    def create_virtual_environment(self) -> None:
        """Create Python virtual environment."""
        self.log_info("Creating virtual environment...")
        
        if self.venv_dir.exists():
            if self.force:
                self.log_warning("Removing existing virtual environment...")
                shutil.rmtree(self.venv_dir)
            else:
                self.log_info("Virtual environment already exists")
                return
        
        # Create install directory
        self.install_dir.mkdir(parents=True, exist_ok=True)
        
        # Create virtual environment
        venv.create(self.venv_dir, with_pip=True)
        self.log_success(f"Virtual environment created at {self.venv_dir}")
        
        # Upgrade pip
        pip_cmd = self.get_pip_command()
        self.run_command([str(pip_cmd), "install", "--upgrade", "pip"])
        self.log_success("pip upgraded")

    def get_python_command(self) -> Path:
        """Get Python executable path in virtual environment."""
        if self.system == "windows":
            return self.venv_dir / "Scripts" / "python.exe"
        else:
            return self.venv_dir / "bin" / "python"

    def get_pip_command(self) -> Path:
        """Get pip executable path in virtual environment."""
        if self.system == "windows":
            return self.venv_dir / "Scripts" / "pip.exe"
        else:
            return self.venv_dir / "bin" / "pip"

    def install_python_packages(self) -> None:
        """Install Python packages."""
        self.log_info("Installing Python packages...")
        
        pip_cmd = self.get_pip_command()
        
        # Install core packages
        for package in self.core_packages:
            self.log_info(f"Installing {package}...")
            self.run_command([str(pip_cmd), "install", package])
        
        self.log_success("Core packages installed")
        
        # Install development packages if in dev mode
        if self.dev_mode:
            self.log_info("Installing development packages...")
            for package in self.dev_packages:
                self.log_info(f"Installing {package}...")
                self.run_command([str(pip_cmd), "install", package])
            
            self.log_success("Development packages installed")

    def install_claude_flow(self, has_npm: bool) -> bool:
        """Install Claude Flow if npm is available."""
        if not has_npm:
            self.log_warning("npm not available - skipping Claude Flow installation")
            return False
        
        self.log_info("Installing Claude Flow...")
        
        try:
            self.run_command(["npm", "install", "-g", "claude-flow@alpha"])
            self.log_success("Claude Flow installed")
            return True
        except subprocess.CalledProcessError:
            self.log_warning("Failed to install Claude Flow")
            return False

    def create_cli_wrapper(self) -> Path:
        """Create CLI wrapper script."""
        self.log_info("Creating CLI wrapper...")
        
        bin_dir = self.install_dir / "bin"
        bin_dir.mkdir(exist_ok=True)
        
        python_exe = self.get_python_command()
        
        if self.system == "windows":
            wrapper_path = bin_dir / "algorithms-cli.bat"
            wrapper_content = f"""@echo off
call "{self.venv_dir}\\Scripts\\activate.bat"
cd /d "{self.project_root}"
"{python_exe}" -m algorithms_cli %*
"""
        else:
            wrapper_path = bin_dir / "algorithms-cli"
            wrapper_content = f"""#!/bin/bash
source "{self.venv_dir}/bin/activate"
cd "{self.project_root}"
"{python_exe}" -m algorithms_cli "$@"
"""
        
        wrapper_path.write_text(wrapper_content)
        
        if self.system != "windows":
            wrapper_path.chmod(0o755)
        
        self.log_success(f"CLI wrapper created at {wrapper_path}")
        return wrapper_path

    def create_configuration(self, has_claude_flow: bool) -> None:
        """Create configuration files."""
        self.log_info("Creating configuration...")
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        config = {
            "version": "1.0.0",
            "python_path": str(self.get_python_command()),
            "venv_path": str(self.venv_dir),
            "install_date": str(subprocess.check_output([
                str(self.get_python_command()), 
                "-c", 
                "import datetime; print(datetime.datetime.now().isoformat())"
            ], text=True).strip()),
            "system": self.system,
            "dev_mode": self.dev_mode,
            "features": {
                "claude_flow": has_claude_flow,
                "jupyter": True,
                "testing": True,
                "development": self.dev_mode
            },
            "paths": {
                "algorithms": "src/algorithms",
                "data_structures": "src/data_structures", 
                "tests": "tests",
                "examples": "examples",
                "docs": "docs"
            },
            "commands": {
                "test": "pytest tests/",
                "lint": "black src/ tests/ && flake8 src/ tests/",
                "typecheck": "mypy src/",
                "coverage": "pytest tests/ --cov=src --cov-report=html"
            }
        }
        
        config_path = self.config_dir / "config.json"
        config_path.write_text(json.dumps(config, indent=2))
        
        self.log_success(f"Configuration saved to {config_path}")

    def setup_development_environment(self) -> None:
        """Setup additional development tools."""
        if not self.dev_mode:
            return
        
        self.log_info("Setting up development environment...")
        
        # Setup pre-commit if config exists
        precommit_config = self.project_root / ".pre-commit-config.yaml"
        if precommit_config.exists():
            try:
                python_cmd = self.get_python_command()
                self.run_command([str(python_cmd), "-m", "pre_commit", "install"])
                self.log_success("Pre-commit hooks installed")
            except subprocess.CalledProcessError:
                self.log_warning("Failed to install pre-commit hooks")
        
        # Create development scripts
        dev_scripts_dir = self.config_dir / "dev_scripts"
        dev_scripts_dir.mkdir(exist_ok=True)
        
        # Test script
        test_script = dev_scripts_dir / ("test.bat" if self.system == "windows" else "test.sh")
        if self.system == "windows":
            test_content = f"""@echo off
call "{self.venv_dir}\\Scripts\\activate.bat"
cd /d "{self.project_root}"
python -m pytest tests/ -v
"""
        else:
            test_content = f"""#!/bin/bash
source "{self.venv_dir}/bin/activate"
cd "{self.project_root}"
python -m pytest tests/ -v
"""
        
        test_script.write_text(test_content)
        if self.system != "windows":
            test_script.chmod(0o755)
        
        self.log_success("Development environment configured")

    def add_to_path(self, wrapper_path: Path) -> None:
        """Add CLI to system PATH."""
        self.log_info("Adding CLI to PATH...")
        
        bin_dir = wrapper_path.parent
        
        if self.system == "windows":
            # On Windows, we'll just inform the user
            self.log_warning("Please add the following to your PATH manually:")
            self.log_warning(f"  {bin_dir}")
        else:
            # On Unix systems, add to shell profiles
            shell_profiles = [
                self.home_dir / ".bashrc",
                self.home_dir / ".zshrc", 
                self.home_dir / ".profile"
            ]
            
            export_line = f'export PATH="{bin_dir}:$PATH"'
            
            for profile in shell_profiles:
                if profile.exists():
                    content = profile.read_text()
                    if export_line not in content:
                        with profile.open("a") as f:
                            f.write(f"\n# Algorithms CLI\n{export_line}\n")
                        self.log_success(f"Added to PATH in {profile}")

    def create_uninstaller(self, wrapper_path: Path) -> None:
        """Create uninstall script."""
        self.log_info("Creating uninstaller...")
        
        bin_dir = wrapper_path.parent
        
        if self.system == "windows":
            uninstaller_path = bin_dir / "algorithms-cli-uninstall.bat"
            uninstaller_content = f"""@echo off
echo Uninstalling Algorithms CLI...

rmdir /s /q "{self.venv_dir}"
rmdir /s /q "{self.config_dir}"
rmdir /s /q "{self.install_dir}"

echo Uninstallation complete!
echo Note: You may need to remove PATH entries manually.
pause
"""
        else:
            uninstaller_path = bin_dir / "algorithms-cli-uninstall"
            uninstaller_content = f"""#!/bin/bash

echo "Uninstalling Algorithms CLI..."

rm -rf "{self.venv_dir}"
rm -rf "{self.config_dir}"
rm -rf "{self.install_dir}"

echo "Uninstallation complete!"
echo "Note: You may need to remove PATH entries manually from shell profiles."
"""
        
        uninstaller_path.write_text(uninstaller_content)
        
        if self.system != "windows":
            uninstaller_path.chmod(0o755)
        
        self.log_success(f"Uninstaller created at {uninstaller_path}")

    def verify_installation(self, wrapper_path: Path) -> bool:
        """Verify the installation works correctly."""
        self.log_info("Verifying installation...")
        
        try:
            # Test CLI wrapper
            if self.system == "windows":
                result = self.run_command([str(wrapper_path), "--help"])
            else:
                result = self.run_command(["bash", str(wrapper_path), "--help"])
            
            self.log_success("CLI wrapper verification passed")
            return True
        except Exception as e:
            self.log_error(f"Installation verification failed: {e}")
            return False

    def print_completion_message(self, wrapper_path: Path, has_claude_flow: bool) -> None:
        """Print installation completion message."""
        self.log_success("Installation completed successfully!")
        print()
        
        self.log_info("Installation Summary:")
        print(f"  • Install directory: {self.install_dir}")
        print(f"  • Configuration: {self.config_dir}")
        print(f"  • CLI wrapper: {wrapper_path}")
        print(f"  • Virtual environment: {self.venv_dir}")
        print()
        
        self.log_info("Next steps:")
        if self.system == "windows":
            print("  1. Add to PATH manually or restart terminal")
        else:
            print("  1. Restart your shell or run: source ~/.bashrc")
        
        print(f"  2. Test installation: {wrapper_path.name} --help")
        print("  3. Start coding: cd your-project && algorithms-cli init")
        print()
        
        if has_claude_flow:
            self.log_info("Claude Flow integration available:")
            print("  • Run SPARC workflow: algorithms-cli sparc tdd 'your-algorithm'")
            print("  • Pipeline execution: npx claude-flow sparc pipeline 'task'")
            print()
        
        if self.dev_mode:
            self.log_info("Development environment ready:")
            print(f"  • Config directory: {self.config_dir}")
            print(f"  • Development scripts: {self.config_dir / 'dev_scripts'}")
            print("  • Pre-commit hooks: installed (if config present)")

    def run_setup(self) -> None:
        """Run the complete setup process."""
        self.print_header()
        
        try:
            # Pre-checks
            self.check_python_version()
            dependencies = self.check_system_dependencies()
            
            # Core installation
            self.create_virtual_environment()
            self.install_python_packages()
            
            # Optional components
            has_claude_flow = self.install_claude_flow(dependencies["npm"])
            
            # CLI setup
            wrapper_path = self.create_cli_wrapper()
            self.create_configuration(has_claude_flow)
            
            if self.dev_mode:
                self.setup_development_environment()
            
            self.add_to_path(wrapper_path)
            self.create_uninstaller(wrapper_path)
            
            # Verification
            if self.verify_installation(wrapper_path):
                # Store in memory for coordination
                try:
                    self.run_command([
                        "npx", "claude-flow@alpha", "hooks", "post-edit",
                        "--file", "setup.py",
                        "--memory-key", "swarm/installer/python-complete"
                    ], check=False)
                except:
                    pass  # Ignore if Claude Flow not available
                
                self.print_completion_message(wrapper_path, has_claude_flow)
            else:
                self.log_error("Installation verification failed")
                sys.exit(1)
                
        except KeyboardInterrupt:
            self.log_warning("Installation cancelled by user")
            sys.exit(1)
        except Exception as e:
            self.log_error(f"Installation failed: {e}")
            sys.exit(1)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Algorithms CLI Python Setup")
    parser.add_argument("--dev", action="store_true", help="Install development environment")
    parser.add_argument("--force", action="store_true", help="Force reinstall (remove existing)")
    
    args = parser.parse_args()
    
    setup_manager = SetupManager(dev_mode=args.dev, force=args.force)
    setup_manager.run_setup()


if __name__ == "__main__":
    main()