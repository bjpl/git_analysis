#!/usr/bin/env python3
"""
Build Profile Loader for Unsplash GPT Tool
Loads and applies build profiles from JSON configuration
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
import logging


class BuildProfileLoader:
    """Manages build profiles and configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the build profile loader."""
        self.script_dir = Path(__file__).parent
        self.project_root = self.script_dir.parent
        
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = self.script_dir / "build-profiles.json"
            
        self.profiles = {}
        self.build_matrix = {}
        self.quality_gates = {}
        self.notifications = {}
        self.artifacts = {}
        
        self.logger = self._setup_logging()
        self._load_configuration()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('BuildProfileLoader')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_configuration(self) -> None:
        """Load build configuration from JSON file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.profiles = config.get('profiles', {})
            self.build_matrix = config.get('build_matrix', {})
            self.quality_gates = config.get('quality_gates', {})
            self.notifications = config.get('notifications', {})
            self.artifacts = config.get('artifacts', {})
            
            self.logger.info(f"Loaded {len(self.profiles)} build profiles")
            
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in configuration file: {e}")
            sys.exit(1)
    
    def list_profiles(self) -> List[str]:
        """Get list of available profiles."""
        return list(self.profiles.keys())
    
    def get_profile(self, profile_name: str) -> Dict[str, Any]:
        """Get a specific build profile."""
        if profile_name not in self.profiles:
            available = ", ".join(self.list_profiles())
            raise ValueError(f"Profile '{profile_name}' not found. Available: {available}")
        
        return self.profiles[profile_name]
    
    def get_default_profile(self, platform: str = "windows") -> str:
        """Get the default profile for a platform."""
        if platform in self.build_matrix:
            return self.build_matrix[platform].get('default_profile', 'production')
        return 'production'
    
    def validate_profile(self, profile_name: str) -> bool:
        """Validate that a profile has required fields."""
        try:
            profile = self.get_profile(profile_name)
            
            required_fields = [
                'name', 'description', 'pyinstaller_options',
                'optimization_level', 'console_mode', 'output'
            ]
            
            for field in required_fields:
                if field not in profile:
                    self.logger.error(f"Profile '{profile_name}' missing required field: {field}")
                    return False
            
            # Validate output section
            output = profile.get('output', {})
            if 'executable_name' not in output:
                self.logger.error(f"Profile '{profile_name}' missing executable_name in output section")
                return False
            
            return True
            
        except ValueError as e:
            self.logger.error(str(e))
            return False
    
    def generate_pyinstaller_spec(self, profile_name: str, output_path: Optional[str] = None) -> str:
        """Generate PyInstaller spec file content for a profile."""
        profile = self.get_profile(profile_name)
        
        if output_path is None:
            output_path = self.project_root / f"main_{profile_name}.spec"
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# Auto-generated PyInstaller spec file for profile: {profile_name}
# Generated on: {self._get_timestamp()}

import os
import sys
from pathlib import Path

# Profile: {profile['name']}
# Description: {profile['description']}

# Import version information
try:
    from version_info import VERSION_INFO, APP_VERSION, APP_NAME
except ImportError:
    APP_VERSION = "2.0.0"
    APP_NAME = "Unsplash Image Search & GPT Tool"
    VERSION_INFO = None

# Get the current directory
spec_dir = Path(SPECPATH)
project_dir = spec_dir

# Define paths
src_dir = project_dir / "src"
data_dir = project_dir / "data"
docs_dir = project_dir / "docs"

# Create data files list
data_files = []

# Add profile-specific data files
profile_data = {profile.get('include_data', [])}
for data_file in profile_data:
    file_path = project_dir / data_file
    if file_path.exists():
        if file_path.is_file():
            data_files.append((str(file_path), os.path.dirname(data_file) or "."))
        elif file_path.is_dir():
            data_files.append((str(file_path), data_file))

# Add src directory if exists
if src_dir.exists():
    data_files.append((str(src_dir), "src"))

# Hidden imports - comprehensive list
hidden_imports = [
    # Core dependencies
    'requests', 'PIL', 'PIL._tkinter_finder', 'openai', 'dotenv',
    
    # Tkinter modules
    'tkinter', 'tkinter.ttk', 'tkinter.font', 'tkinter.messagebox',
    'tkinter.filedialog', 'tkinter.colorchooser', 'tkinter.scrolledtext',
    
    # Application modules
    'config_manager', 'src.ui.main_window', 'src.ui.theme_manager',
    'src.services.openai_service', 'src.services.unsplash_service',
    'src.models.image', 'src.models.session', 'src.utils.cache'
]

# Profile-specific excludes
excludes = {profile.get('exclude_modules', [])}

# Add common excludes for optimization
if {profile.get('optimization_level', 0)} > 0:
    excludes.extend([
        'unittest', 'doctest', 'pdb', 'IPython', 'pytest',
        'black', 'mypy', 'setuptools', 'pip'
    ])

# PyInstaller Analysis
a = Analysis(
    [str(project_dir / 'main.py')],
    pathex=[str(project_dir)],
    binaries=[],
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
    optimize={profile.get('optimization_level', 0)},
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Executable configuration
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="{profile['output']['executable_name'].replace('.exe', '')}",
    debug={str(profile.get('include_debug_info', False)).lower()},
    bootloader_ignore_signals=False,
    strip={'not ' if profile.get('include_debug_info', False) else ''}False,
    upx={str(profile.get('upx_compression', False)).lower()},
    upx_exclude=[
        'vcruntime140.dll', 'python3.dll', 'python38.dll',
        'python39.dll', 'python310.dll', 'python311.dll', 'python312.dll'
    ],
    runtime_tmpdir=None,
    console={str(profile.get('console_mode', False)).lower()},
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_dir / "assets" / "app_icon.ico") if (project_dir / "assets" / "app_icon.ico").exists() else None,
    version=VERSION_INFO,
    uac_admin=False,
    uac_uiaccess=False,
)
'''
        
        return spec_content
    
    def create_build_script(self, profile_name: str, script_type: str = 'batch') -> str:
        """Create a build script for a specific profile."""
        profile = self.get_profile(profile_name)
        
        if script_type == 'batch':
            return self._create_batch_script(profile_name, profile)
        elif script_type == 'powershell':
            return self._create_powershell_script(profile_name, profile)
        else:
            raise ValueError(f"Unsupported script type: {script_type}")
    
    def _create_batch_script(self, profile_name: str, profile: Dict[str, Any]) -> str:
        """Create a batch script for the profile."""
        validation = profile.get('validation', {})
        output = profile.get('output', {})
        
        script = f'''@echo off
REM Auto-generated build script for profile: {profile_name}
REM Profile: {profile['name']}
REM Description: {profile['description']}

echo Building with profile: {profile_name}
echo Profile: {profile['name']}
echo.

set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

REM Activate virtual environment
if exist "venv\\Scripts\\activate.bat" (
    call venv\\Scripts\\activate.bat
    echo Virtual environment activated
) else (
    echo Warning: Virtual environment not found
)

'''
        
        if validation.get('run_tests', False):
            script += '''
echo Running tests...
python -m pytest tests/ -v
if errorlevel 1 (
    echo Tests failed!
    exit /b 1
)
'''
        
        if validation.get('syntax_check', False):
            script += '''
echo Checking Python syntax...
python -m py_compile main.py
if errorlevel 1 (
    echo Syntax check failed!
    exit /b 1
)
'''
        
        script += f'''
echo Generating version file...
python version_info.py

echo Building executable...
pyinstaller main_{profile_name}.spec --noconfirm
if errorlevel 1 (
    echo Build failed!
    exit /b 1
)

echo Build completed successfully!
echo Executable: {output.get('executable_name', 'Unknown')}
'''
        
        if output.get('create_portable', False):
            script += '''
echo Creating portable version...
mkdir dist\\Portable 2>nul
copy dist\\*.exe dist\\Portable\\ >nul
'''
        
        return script
    
    def _create_powershell_script(self, profile_name: str, profile: Dict[str, Any]) -> str:
        """Create a PowerShell script for the profile."""
        # This would create a PowerShell version similar to the batch script
        # Implementation would be similar but in PowerShell syntax
        return f"# PowerShell script for {profile_name} (implementation needed)"
    
    def get_quality_gates(self) -> Dict[str, Any]:
        """Get quality gate configuration."""
        return self.quality_gates
    
    def check_quality_gates(self, profile_name: str, build_results: Dict[str, Any]) -> bool:
        """Check if build meets quality gate requirements."""
        gates = self.get_quality_gates()
        profile = self.get_profile(profile_name)
        validation = profile.get('validation', {})
        
        passed = True
        
        # Code coverage check
        if validation.get('run_tests', False) and 'code_coverage' in gates:
            min_coverage = gates['code_coverage'].get('minimum_percentage', 0)
            actual_coverage = build_results.get('coverage_percentage', 0)
            
            if actual_coverage < min_coverage:
                self.logger.error(f"Code coverage {actual_coverage}% below minimum {min_coverage}%")
                if gates['code_coverage'].get('enforce', False):
                    passed = False
        
        # Performance checks
        if 'performance' in gates:
            perf_gates = gates['performance']
            
            if 'startup_time' in build_results:
                max_startup = perf_gates.get('max_startup_time_seconds', float('inf'))
                if build_results['startup_time'] > max_startup:
                    self.logger.error(f"Startup time {build_results['startup_time']}s exceeds maximum {max_startup}s")
                    passed = False
            
            if 'executable_size' in build_results:
                max_size = perf_gates.get('max_executable_size_mb', float('inf')) * 1024 * 1024
                if build_results['executable_size'] > max_size:
                    self.logger.error(f"Executable size exceeds maximum allowed")
                    passed = False
        
        return passed
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def export_profile_summary(self, output_path: Optional[str] = None) -> str:
        """Export a summary of all profiles."""
        if output_path is None:
            output_path = self.script_dir / "profile_summary.md"
        
        summary = "# Build Profiles Summary\n\n"
        
        for name, profile in self.profiles.items():
            summary += f"## {profile['name']} ({name})\n\n"
            summary += f"**Description:** {profile['description']}\n\n"
            
            # Basic settings
            summary += "**Settings:**\n"
            summary += f"- Console Mode: {profile.get('console_mode', False)}\n"
            summary += f"- Optimization: Level {profile.get('optimization_level', 0)}\n"
            summary += f"- Debug Info: {profile.get('include_debug_info', False)}\n"
            summary += f"- UPX Compression: {profile.get('upx_compression', False)}\n\n"
            
            # Output settings
            output = profile.get('output', {})
            summary += "**Output:**\n"
            summary += f"- Executable: {output.get('executable_name', 'N/A')}\n"
            summary += f"- Create Portable: {output.get('create_portable', False)}\n"
            summary += f"- Create Installer: {output.get('create_installer', False)}\n\n"
            
            # Validation
            validation = profile.get('validation', {})
            if validation:
                summary += "**Validation:**\n"
                for check, enabled in validation.items():
                    summary += f"- {check.replace('_', ' ').title()}: {enabled}\n"
                summary += "\n"
            
            summary += "---\n\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        return str(output_path)


def main():
    """Command-line interface for build profile management."""
    parser = argparse.ArgumentParser(description='Build Profile Manager')
    parser.add_argument('action', choices=['list', 'show', 'validate', 'generate-spec', 'generate-script', 'summary'])
    parser.add_argument('--profile', '-p', help='Profile name')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--script-type', choices=['batch', 'powershell'], default='batch')
    parser.add_argument('--config', '-c', help='Config file path')
    
    args = parser.parse_args()
    
    try:
        loader = BuildProfileLoader(args.config)
        
        if args.action == 'list':
            profiles = loader.list_profiles()
            print("Available build profiles:")
            for profile in profiles:
                profile_data = loader.get_profile(profile)
                print(f"  {profile}: {profile_data['name']}")
        
        elif args.action == 'show':
            if not args.profile:
                print("Error: --profile required for 'show' action")
                sys.exit(1)
            
            profile = loader.get_profile(args.profile)
            print(f"Profile: {profile['name']}")
            print(f"Description: {profile['description']}")
            print(f"Console Mode: {profile.get('console_mode', False)}")
            print(f"Optimization: {profile.get('optimization_level', 0)}")
            print(f"Executable: {profile['output']['executable_name']}")
        
        elif args.action == 'validate':
            if not args.profile:
                print("Error: --profile required for 'validate' action")
                sys.exit(1)
            
            if loader.validate_profile(args.profile):
                print(f"Profile '{args.profile}' is valid")
            else:
                print(f"Profile '{args.profile}' is invalid")
                sys.exit(1)
        
        elif args.action == 'generate-spec':
            if not args.profile:
                print("Error: --profile required for 'generate-spec' action")
                sys.exit(1)
            
            spec_content = loader.generate_pyinstaller_spec(args.profile, args.output)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(spec_content)
                print(f"Spec file generated: {args.output}")
            else:
                print(spec_content)
        
        elif args.action == 'generate-script':
            if not args.profile:
                print("Error: --profile required for 'generate-script' action")
                sys.exit(1)
            
            script_content = loader.create_build_script(args.profile, args.script_type)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(script_content)
                print(f"Build script generated: {args.output}")
            else:
                print(script_content)
        
        elif args.action == 'summary':
            summary_path = loader.export_profile_summary(args.output)
            print(f"Profile summary exported: {summary_path}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()