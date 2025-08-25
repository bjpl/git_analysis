#!/usr/bin/env python3
"""
Advanced Build Configuration Manager for Unsplash Image Search & GPT Tool

This module provides comprehensive build configuration management including:
- Multiple build profiles (development, production, portable)
- Automated dependency analysis and optimization
- Icon generation and resource management
- Build artifact organization
- Cross-platform compatibility
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class BuildProfile(Enum):
    """Build profile types with different optimization strategies."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    PORTABLE = "portable"
    DEBUG = "debug"


@dataclass
class BuildConfig:
    """Complete build configuration settings."""
    profile: BuildProfile
    app_name: str
    version: str
    output_dir: Path
    enable_upx: bool
    enable_console: bool
    enable_debug: bool
    icon_file: Optional[Path]
    manifest_file: Optional[Path]
    version_file: Optional[Path]
    additional_data: List[Tuple[str, str]]
    hidden_imports: List[str]
    excludes: List[str]
    upx_exclude: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert Path objects to strings
        data['profile'] = self.profile.value
        data['output_dir'] = str(self.output_dir)
        data['icon_file'] = str(self.icon_file) if self.icon_file else None
        data['manifest_file'] = str(self.manifest_file) if self.manifest_file else None
        data['version_file'] = str(self.version_file) if self.version_file else None
        return data


class BuildConfigManager:
    """Manages build configurations for different deployment scenarios."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.installer_dir = project_root / "installer"
        self.src_dir = project_root / "src"
        self.assets_dir = project_root / "assets"
        self.build_dir = project_root / "build"
        self.dist_dir = project_root / "dist"
        
        # Ensure directories exist
        self.installer_dir.mkdir(exist_ok=True)
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        
        # Load version information
        self._load_version_info()
    
    def _load_version_info(self):
        """Load version information from version_info.py."""
        try:
            sys.path.insert(0, str(self.project_root))
            import version_info
            self.app_name = version_info.APP_NAME
            self.version = version_info.APP_VERSION
            self.executable_name = version_info.EXECUTABLE_NAME
            self.features = version_info.FEATURES
        except ImportError:
            print("Warning: version_info.py not found, using defaults")
            self.app_name = "Unsplash Image Search GPT Tool"
            self.version = "2.0.0"
            self.executable_name = f"{self.app_name.replace(' ', '_')}_v{self.version}.exe"
            self.features = {}
    
    def get_base_hidden_imports(self) -> List[str]:
        """Get base list of hidden imports required by the application."""
        return [
            # Core dependencies
            'requests', 'requests.adapters', 'requests.auth', 'requests.exceptions',
            'urllib3', 'urllib3.poolmanager',
            
            # Image processing
            'PIL', 'PIL.Image', 'PIL.ImageTk', 'PIL.ImageEnhance',
            'PIL._tkinter_finder', 'PIL.ImageOps',
            
            # OpenAI
            'openai', 'openai.types', 'openai.resources',
            'openai._client', 'openai._base_client',
            
            # GUI
            'tkinter', 'tkinter.ttk', 'tkinter.messagebox',
            'tkinter.filedialog', 'tkinter.scrolledtext',
            
            # System
            'pathlib', 'json', 'csv', 'datetime', 'threading',
            'configparser', 'dotenv', 'ssl', 'certifi',
            
            # App modules
            'config_manager',
        ]
    
    def get_src_modules(self) -> List[str]:
        """Discover all Python modules in the src directory."""
        modules = []
        if not self.src_dir.exists():
            return modules
        
        for py_file in self.src_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            rel_path = py_file.relative_to(self.project_root)
            module_path = str(rel_path.with_suffix('')).replace(os.sep, '.')
            modules.append(module_path)
        
        return modules
    
    def get_base_excludes(self) -> List[str]:
        """Get base list of modules to exclude for size optimization."""
        return [
            # Development tools
            'pytest', 'pytest_cov', 'unittest', 'doctest', 'pdb',
            'black', 'flake8', 'mypy', 'isort', 'bandit',
            
            # Build tools
            'setuptools', 'pip', 'wheel', 'poetry', 'distutils',
            
            # Alternative frameworks
            'PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'wx', 'kivy',
            'django', 'flask', 'tornado', 'aiohttp',
            
            # Scientific computing
            'numpy', 'pandas', 'scipy', 'matplotlib', 'tensorflow',
            
            # Database
            'sqlite3', 'psycopg2', 'sqlalchemy',
            
            # Unused protocols
            'ftplib', 'imaplib', 'poplib', 'smtplib',
        ]
    
    def get_upx_excludes(self) -> List[str]:
        """Get list of files to exclude from UPX compression."""
        return [
            'vcruntime*.dll', 'msvcp*.dll', 'api-ms-*.dll',
            'python*.dll', '_ctypes.pyd', '_socket.pyd',
            'libssl*.dll', 'libcrypto*.dll', '_ssl.pyd',
            'tk*.dll', 'tcl*.dll', '_tkinter.pyd',
        ]
    
    def find_icon_file(self) -> Optional[Path]:
        """Find application icon file."""
        icon_paths = [
            self.installer_dir / "app_icon.ico",
            self.assets_dir / "app_icon.ico",
            self.assets_dir / "icon.ico",
            self.project_root / "icon.ico",
        ]
        
        for icon_path in icon_paths:
            if icon_path.exists():
                return icon_path
        
        return None
    
    def create_manifest_file(self, dpi_aware: bool = True) -> Path:
        """Create Windows application manifest for DPI awareness."""
        manifest_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="{self.version}.0"
    processorArchitecture="amd64"
    name="{self.app_name}"
    type="win32"
  />
  <description>{self.app_name} - AI-powered image search and vocabulary tool</description>
  
  <!-- Windows 10/11 compatibility -->
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <!-- Windows 10 -->
      <supportedOS Id="{{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}}"/>
      <!-- Windows 8.1 -->
      <supportedOS Id="{{1f676c76-80e1-4239-95bb-83d0f6d0da78}}"/>
      <!-- Windows 8 -->
      <supportedOS Id="{{4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38}}"/>
      <!-- Windows 7 -->
      <supportedOS Id="{{35138b9a-5d96-4fbd-8e2d-a2440225f93a}}"/>
    </application>
  </compatibility>
  
  <!-- DPI Awareness -->
  {'<application xmlns="urn:schemas-microsoft-com:asm.v3">' if dpi_aware else ''}
  {'<windowsSettings>' if dpi_aware else ''}
  {'<dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true</dpiAware>' if dpi_aware else ''}
  {'<dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2</dpiAwareness>' if dpi_aware else ''}
  {'</windowsSettings>' if dpi_aware else ''}
  {'</application>' if dpi_aware else ''}
  
  <!-- Request administrator privileges if needed -->
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v2">
    <security>
      <requestedPrivileges xmlns="urn:schemas-microsoft-com:asm.v3">
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
  
  <!-- Enable common controls -->
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="Microsoft.Windows.Common-Controls"
        version="6.0.0.0"
        processorArchitecture="*"
        publicKeyToken="6595b64144ccf1df"
        language="*"
      />
    </dependentAssembly>
  </dependency>
</assembly>'''
        
        manifest_file = self.installer_dir / "app.manifest"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            f.write(manifest_content)
        
        return manifest_file
    
    def create_build_config(self, profile: BuildProfile) -> BuildConfig:
        """Create build configuration for specified profile."""
        base_config = {
            'app_name': self.app_name,
            'version': self.version,
            'output_dir': self.dist_dir,
            'additional_data': [],
            'hidden_imports': self.get_base_hidden_imports() + self.get_src_modules(),
            'excludes': self.get_base_excludes(),
            'upx_exclude': self.get_upx_excludes(),
            'icon_file': self.find_icon_file(),
            'manifest_file': self.create_manifest_file(),
            'version_file': None,
        }
        
        # Profile-specific configurations
        profile_configs = {
            BuildProfile.DEVELOPMENT: {
                'enable_upx': False,
                'enable_console': True,
                'enable_debug': True,
            },
            BuildProfile.PRODUCTION: {
                'enable_upx': True,
                'enable_console': False,
                'enable_debug': False,
            },
            BuildProfile.PORTABLE: {
                'enable_upx': True,
                'enable_console': False,
                'enable_debug': False,
            },
            BuildProfile.DEBUG: {
                'enable_upx': False,
                'enable_console': True,
                'enable_debug': True,
            },
        }
        
        config = {**base_config, **profile_configs[profile]}
        config['profile'] = profile
        
        return BuildConfig(**config)
    
    def save_config(self, config: BuildConfig, filename: str = "build_config.json"):
        """Save build configuration to JSON file."""
        config_file = self.installer_dir / filename
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
        
        print(f"Build configuration saved: {config_file}")
    
    def generate_spec_file(self, config: BuildConfig, spec_filename: str = "generated.spec") -> Path:
        """Generate PyInstaller spec file from build configuration."""
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# Auto-generated PyInstaller spec file for {config.app_name}
# Profile: {config.profile.value}
# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

import os
from pathlib import Path

# Project configuration
project_dir = Path(r"{self.project_root}")
src_dir = project_dir / "src"

# Data files
data_files = [
    (str(src_dir), "src"),
    (str(project_dir / "config_manager.py"), "."),
]

# Add additional data files
for src_file, dest_dir in {config.additional_data}:
    file_path = project_dir / src_file
    if file_path.exists():
        data_files.append((str(file_path), dest_dir))

# Hidden imports
hidden_imports = {config.hidden_imports}

# Exclusions
excludes = {config.excludes}

# PyInstaller configuration
a = Analysis(
    [str(project_dir / "main.py")],
    pathex=[str(project_dir), str(src_dir)],
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
    optimize=2,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="{config.app_name.replace(' ', '_')}_v{config.version}{'_' + config.profile.value if config.profile != BuildProfile.PRODUCTION else ''}",
    debug={str(config.enable_debug).lower()},
    bootloader_ignore_signals=False,
    strip=False,
    upx={str(config.enable_upx).lower()},
    upx_exclude={config.upx_exclude},
    runtime_tmpdir=None,
    console={str(config.enable_console).lower()},
    disable_windowed_traceback={str(not config.enable_debug).lower()},
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r"{config.icon_file}" if config.icon_file else None,
    version=r"{config.version_file}" if config.version_file else None,
    uac_admin=False,
    uac_uiaccess=False,
    manifest=r"{config.manifest_file}" if config.manifest_file else None,
)
'''
        
        spec_file = self.installer_dir / spec_filename
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"Spec file generated: {spec_file}")
        return spec_file
    
    def create_icon_placeholder(self) -> Path:
        """Create a placeholder icon file if none exists."""
        icon_file = self.installer_dir / "app_icon.ico"
        
        if icon_file.exists():
            return icon_file
        
        # Create a simple text-based placeholder
        # In a real implementation, you would use PIL or similar to create an actual icon
        placeholder_content = b'''
# This is a placeholder for the application icon
# Replace this file with a proper .ico file for the application
# Recommended sizes: 16x16, 32x32, 48x48, 256x256
'''
        
        with open(icon_file, 'wb') as f:
            f.write(placeholder_content)
        
        print(f"Created icon placeholder: {icon_file}")
        print("Warning: Replace with actual .ico file for proper branding")
        
        return icon_file
    
    def optimize_build_artifacts(self, build_dir: Path):
        """Clean up and optimize build artifacts."""
        if not build_dir.exists():
            return
        
        # Remove unnecessary files
        patterns_to_remove = [
            '*.pyc', '*.pyo', '__pycache__',
            '*.log', '*.tmp', 'debug_*',
        ]
        
        removed_count = 0
        for pattern in patterns_to_remove:
            for file_path in build_dir.rglob(pattern):
                try:
                    if file_path.is_dir():
                        shutil.rmtree(file_path)
                    else:
                        file_path.unlink()
                    removed_count += 1
                except OSError:
                    pass
        
        print(f"Cleaned up {removed_count} temporary files")


def main():
    """Main entry point for build configuration management."""
    if len(sys.argv) < 2:
        print("Usage: python build_config.py <profile> [spec_name]")
        print("Profiles: development, production, portable, debug")
        return 1
    
    profile_name = sys.argv[1].lower()
    spec_name = sys.argv[2] if len(sys.argv) > 2 else f"{profile_name}.spec"
    
    try:
        profile = BuildProfile(profile_name)
    except ValueError:
        print(f"Invalid profile: {profile_name}")
        print("Available profiles: development, production, portable, debug")
        return 1
    
    # Initialize build config manager
    project_root = Path(__file__).parent.parent
    manager = BuildConfigManager(project_root)
    
    # Create configuration
    config = manager.create_build_config(profile)
    
    # Save configuration
    manager.save_config(config, f"{profile_name}_config.json")
    
    # Generate spec file
    manager.generate_spec_file(config, spec_name)
    
    # Create icon placeholder if needed
    manager.create_icon_placeholder()
    
    print(f"\nBuild configuration ready for profile: {profile.value}")
    print(f"Spec file: {manager.installer_dir / spec_name}")
    print(f"To build: pyinstaller {manager.installer_dir / spec_name}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
