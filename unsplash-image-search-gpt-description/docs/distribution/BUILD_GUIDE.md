# Developer Build Guide

Comprehensive guide for building the Unsplash Image Search with GPT application from source code.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Building from Source](#building-from-source)
- [Creating Custom Builds](#creating-custom-builds)
- [Cross-Platform Building](#cross-platform-building)
- [Build Customization](#build-customization)
- [Automated Build Process](#automated-build-process)
- [Build Optimization](#build-optimization)
- [Troubleshooting Builds](#troubleshooting-builds)
- [Contributing Guidelines](#contributing-guidelines)

## Development Environment Setup

### Prerequisites

#### Required Software
- **Python 3.8+** (3.11 recommended)
- **Git** for version control
- **Code editor** (VS Code, PyCharm, etc.)
- **Terminal/Command prompt**

#### Platform-Specific Requirements

**Windows**:
```cmd
# Install Python from python.org or Microsoft Store
# Install Git from git-scm.com
# Install Visual Studio Build Tools (for some packages)
winget install Microsoft.VisualStudio.2022.BuildTools
```

**macOS**:
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and Git
brew install python@3.11 git

# Install Xcode Command Line Tools
xcode-select --install
```

**Linux (Ubuntu/Debian)**:
```bash
# Update package list
sudo apt update

# Install Python, pip, and development tools
sudo apt install python3.11 python3.11-pip python3.11-venv python3.11-dev
sudo apt install git build-essential

# Install GUI development libraries
sudo apt install python3-tk python3-pil python3-pil.imagetk
```

### Repository Setup

#### Clone Repository
```bash
# Clone the main repository
git clone https://github.com/your-username/unsplash-image-search-gpt-description.git
cd unsplash-image-search-gpt-description

# Create and activate virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

#### Install Dependencies
```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install build tools
pip install pyinstaller cx_Freeze py2app

# Install additional development tools
pip install black flake8 mypy isort pytest pytest-cov
```

#### Verify Installation
```bash
# Test application runs
python main.py

# Run tests
pytest

# Check code style
black --check .
flake8 .
mypy .
```

## Building from Source

### Quick Build

#### Windows
```cmd
# Use provided build script
build.bat

# Output: dist\unsplash-gpt-tool.exe
```

#### Linux/macOS
```bash
# Make script executable and run
chmod +x build.sh
./build.sh

# Output: dist/unsplash-gpt-tool
```

### Manual Build Process

#### Step 1: Prepare Build Environment
```bash
# Clean previous builds
rm -rf build/ dist/ *.spec

# Ensure virtual environment is active
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Verify dependencies
pip check
```

#### Step 2: Create PyInstaller Spec File
```bash
# Generate initial spec file
pyi-makespec --onefile --windowed --name unsplash-gpt-tool main.py
```

#### Step 3: Customize Spec File

Edit `unsplash-gpt-tool.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

block_cipher = None

# Define paths
project_root = Path('.')
data_files = [
    ('.env.example', '.'),
    ('README.md', '.'),
    ('LICENSE', '.'),
    ('docs', 'docs'),
    ('examples', 'examples'),
]

# Add icon if available
icon_path = project_root / 'assets' / 'icon.ico'
icon_file = str(icon_path) if icon_path.exists() else None

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=data_files,
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'openai',
        'requests',
        'dotenv',
        'csv',
        'json',
        'threading',
        'datetime',
        'pathlib',
        'configparser',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest',
        'sphinx',
        'jupyter',
        'notebook',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='unsplash-gpt-tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)
```

#### Step 4: Build Executable
```bash
# Build using spec file
pyinstaller unsplash-gpt-tool.spec

# Or direct command (less customization)
pyinstaller --clean --onefile --windowed \
    --name unsplash-gpt-tool \
    --icon assets/icon.ico \
    --add-data ".env.example;." \
    --add-data "README.md;." \
    --hidden-import tkinter \
    --hidden-import PIL \
    --hidden-import openai \
    main.py
```

#### Step 5: Test Build
```bash
# Test the executable
./dist/unsplash-gpt-tool  # Linux/macOS
dist\unsplash-gpt-tool.exe # Windows

# Check file size
ls -lh dist/

# Test on clean system (recommended)
```

## Creating Custom Builds

### Build Variants

#### Debug Build
```python
# In spec file, set:
exe = EXE(
    # ... other parameters ...
    debug=True,
    console=True,  # Show console for debugging
    # ... rest of parameters ...
)
```

#### Optimized Build
```bash
# Enable UPX compression (requires UPX installed)
pyinstaller --upx-dir=/usr/bin unsplash-gpt-tool.spec

# Strip debug symbols (Linux/macOS)
strip dist/unsplash-gpt-tool
```

#### Minimal Build
```python
# Exclude unnecessary modules
excludes=[
    'unittest',
    'pdb',
    'doctest',
    'difflib',
    'inspect',
    'calendar',
    'email',
    'html',
    'http',
    'urllib.parse',
    'xml',
]
```

### Feature Customization

#### Build with Specific Features
```bash
# Build with only essential features
pyinstaller --additional-hooks-dir=hooks/ \
    --exclude-module matplotlib \
    --exclude-module numpy \
    --exclude-module scipy \
    unsplash-gpt-tool.spec
```

#### Environment-Specific Builds
```python
# Corporate build with proxy support
hiddenimports += [
    'urllib3',
    'certifi',
    'proxy_tools',
]

# Educational build with additional languages
datas += [
    ('locales', 'locales'),
    ('help_files', 'help'),
]
```

### Version Management

#### Version Information (Windows)

Create `version_info.py`:
```python
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2, 0, 0, 0),
    prodvers=(2, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x4,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable('040904B0', [
        StringStruct('CompanyName', 'Image Search Tools'),
        StringStruct('FileDescription', 'Unsplash Image Search with GPT'),
        StringStruct('FileVersion', '2.0.0.0'),
        StringStruct('InternalName', 'unsplash-gpt-tool'),
        StringStruct('LegalCopyright', '© 2024 Your Name'),
        StringStruct('OriginalFilename', 'unsplash-gpt-tool.exe'),
        StringStruct('ProductName', 'Unsplash GPT Tool'),
        StringStruct('ProductVersion', '2.0.0.0')
      ])
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
```

Add to spec file:
```python
exe = EXE(
    # ... other parameters ...
    version='version_info.py',
    # ... rest of parameters ...
)
```

## Cross-Platform Building

### Build Matrix

| Target Platform | Build Platform | Status | Notes |
|----------------|----------------|--------|---------|
| Windows x64 | Windows | ✅ Native | Full support |
| Windows x64 | Linux (Wine) | ⚠️ Limited | Cross-compilation |
| macOS x64 | macOS | ✅ Native | Intel Macs |
| macOS ARM64 | macOS | ✅ Native | Apple Silicon |
| Linux x64 | Linux | ✅ Native | Most distributions |
| Linux ARM64 | Linux ARM64 | ✅ Native | Raspberry Pi, etc. |

### Windows Builds

#### On Windows (Native)
```cmd
# Standard build
build.bat

# With signing (requires certificate)
signtool sign /f cert.pfx /p password dist\unsplash-gpt-tool.exe
```

#### On Linux (Cross-compile)
```bash
# Install Wine
sudo apt install wine

# Install Python in Wine
wine python-3.11-installer.exe

# Build with PyInstaller in Wine
wine python -m pyinstaller unsplash-gpt-tool.spec
```

### macOS Builds

#### Universal Binary (Intel + Apple Silicon)
```bash
# Install both Python versions
brew install python@3.11
/usr/bin/python3 -m pip install pyinstaller

# Build universal binary
pyinstaller --target-arch universal2 unsplash-gpt-tool.spec
```

#### App Bundle Creation
```bash
# Use py2app instead of PyInstaller
pip install py2app

# Create setup.py for py2app
python setup.py py2app
```

#### Code Signing (macOS)
```bash
# Sign the application
codesign --force --deep --sign "Developer ID Application: Your Name" \
    dist/UnsplashGPTTool.app

# Create DMG
hdiutil create -volname "Unsplash GPT Tool" -srcfolder dist/ \
    -ov -format UDZO UnsplashGPTTool.dmg
```

### Linux Builds

#### AppImage Creation
```bash
# Build standard executable first
pyinstaller unsplash-gpt-tool.spec

# Create AppDir structure
mkdir -p UnsplashGPTTool.AppDir/usr/bin
cp dist/unsplash-gpt-tool UnsplashGPTTool.AppDir/usr/bin/

# Create desktop file
cat > UnsplashGPTTool.AppDir/UnsplashGPTTool.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Unsplash GPT Tool
Exec=unsplash-gpt-tool
Icon=unsplash-gpt-tool
Categories=Graphics;Photography;Education;
EOF

# Create AppImage
./appimagetool-x86_64.AppImage UnsplashGPTTool.AppDir
```

#### Flatpak Package
```yaml
# org.example.UnsplashGPTTool.yaml
app-id: org.example.UnsplashGPTTool
runtime: org.freedesktop.Platform
runtime-version: '22.08'
sdk: org.freedesktop.Sdk
sdk-extensions:
  - org.freedesktop.Sdk.Extension.python3
command: unsplash-gpt-tool
finish-args:
  - --socket=wayland
  - --socket=fallback-x11
  - --share=network
  - --filesystem=home
modules:
  - name: unsplash-gpt-tool
    buildsystem: simple
    build-commands:
      - pip3 install --prefix=/app .
    sources:
      - type: dir
        path: .
```

## Build Customization

### Configuration Options

#### Build Configuration File

Create `build_config.json`:
```json
{
  "build_options": {
    "onefile": true,
    "windowed": true,
    "upx": false,
    "debug": false
  },
  "include_files": [
    ".env.example",
    "README.md",
    "LICENSE"
  ],
  "exclude_modules": [
    "pytest",
    "sphinx",
    "notebook"
  ],
  "hidden_imports": [
    "tkinter",
    "PIL",
    "openai"
  ],
  "icon": "assets/icon.ico",
  "version_info": {
    "version": "2.0.0",
    "company": "Image Search Tools",
    "description": "AI-powered image search tool"
  }
}
```

#### Dynamic Spec Generation

Create `generate_spec.py`:
```python
import json
import sys
from pathlib import Path

def generate_spec(config_file):
    with open(config_file) as f:
        config = json.load(f)
    
    # Generate spec content based on config
    spec_content = f"""
# Auto-generated spec file
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas={config['include_files']},
    hiddenimports={config['hidden_imports']},
    excludes={config['exclude_modules']},
    # ... rest of configuration
)

# ... rest of spec file
"""
    
    with open('auto-generated.spec', 'w') as f:
        f.write(spec_content)

if __name__ == '__main__':
    generate_spec('build_config.json')
```

### Build Profiles

#### Development Profile
```bash
# Quick build for testing
pyinstaller --onedir --console --debug=all main.py
```

#### Release Profile
```bash
# Optimized build for distribution
pyinstaller --onefile --windowed --upx-dir=/usr/bin \
    --clean --noconfirm unsplash-gpt-tool.spec
```

#### Portable Profile
```bash
# Self-contained portable build
pyinstaller --onefile --add-data "portable.txt;." \
    --runtime-tmpdir . unsplash-gpt-tool.spec
```

## Automated Build Process

### GitHub Actions Workflow

Create `.github/workflows/build.yml`:

```yaml
name: Build Application

on:
  push:
    branches: [ main, develop ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
        python-version: ['3.11']
    
    runs-on: ${{ matrix.os }}
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build application (Windows)
      if: matrix.os == 'windows-latest'
      run: |
        pyinstaller --onefile --windowed --name unsplash-gpt-tool \
          --icon assets/icon.ico main.py
    
    - name: Build application (macOS)
      if: matrix.os == 'macos-latest'
      run: |
        pyinstaller --onefile --windowed --name unsplash-gpt-tool \
          --icon assets/icon.icns main.py
    
    - name: Build application (Linux)
      if: matrix.os == 'ubuntu-latest'
      run: |
        sudo apt-get update
        sudo apt-get install -y python3-tk
        pyinstaller --onefile --name unsplash-gpt-tool main.py
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: unsplash-gpt-tool-${{ matrix.os }}
        path: |
          dist/unsplash-gpt-tool*
          !dist/*.app
    
    - name: Upload macOS app bundle
      if: matrix.os == 'macos-latest'
      uses: actions/upload-artifact@v3
      with:
        name: unsplash-gpt-tool-macos-app
        path: dist/*.app
```

### Local Build Scripts

#### Advanced Build Script (build_all.py)

```python
#!/usr/bin/env python3
"""
Advanced build script for Unsplash GPT Tool
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run command and handle errors"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout

def clean_build():
    """Clean previous build artifacts"""
    print("Cleaning build artifacts...")
    for path in ['build', 'dist', '__pycache__']:
        if Path(path).exists():
            shutil.rmtree(path)
    
    # Remove spec files
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    run_command(f"{sys.executable} -m pip install --upgrade pip")
    run_command(f"{sys.executable} -m pip install -r requirements.txt")
    run_command(f"{sys.executable} -m pip install pyinstaller")

def build_application(build_type='release'):
    """Build the application"""
    print(f"Building application ({build_type})...")
    
    # Base command
    cmd = [sys.executable, '-m', 'PyInstaller']
    
    # Common options
    cmd.extend([
        '--clean',
        '--name', 'unsplash-gpt-tool',
        '--add-data', '.env.example;.',
        '--add-data', 'README.md;.',
        '--hidden-import', 'tkinter',
        '--hidden-import', 'PIL',
        '--hidden-import', 'openai',
    ])
    
    # Build type specific options
    if build_type == 'debug':
        cmd.extend(['--onedir', '--console', '--debug=all'])
    else:
        cmd.extend(['--onefile', '--windowed'])
        
        # Add icon if available
        icon_path = None
        for ext in ['.ico', '.icns', '.png']:
            icon_file = Path(f'assets/icon{ext}')
            if icon_file.exists():
                icon_path = str(icon_file)
                break
        
        if icon_path:
            cmd.extend(['--icon', icon_path])
    
    # Add main script
    cmd.append('main.py')
    
    # Run build command
    run_command(' '.join(cmd))

def create_distribution():
    """Create distribution package"""
    print("Creating distribution package...")
    
    dist_dir = Path('release')
    dist_dir.mkdir(exist_ok=True)
    
    # Copy executable
    system = platform.system().lower()
    if system == 'windows':
        exe_name = 'unsplash-gpt-tool.exe'
    else:
        exe_name = 'unsplash-gpt-tool'
    
    exe_path = Path('dist') / exe_name
    if exe_path.exists():
        shutil.copy2(exe_path, dist_dir / exe_name)
    
    # Copy documentation
    for doc in ['README.md', 'LICENSE', '.env.example']:
        if Path(doc).exists():
            shutil.copy2(doc, dist_dir / doc)
    
    # Create archive
    archive_name = f'unsplash-gpt-tool-{system}'
    shutil.make_archive(archive_name, 'zip', dist_dir)
    print(f"Created: {archive_name}.zip")

def main():
    parser = argparse.ArgumentParser(description='Build Unsplash GPT Tool')
    parser.add_argument('--type', choices=['debug', 'release'], default='release',
                       help='Build type')
    parser.add_argument('--clean', action='store_true',
                       help='Clean build artifacts first')
    parser.add_argument('--deps', action='store_true',
                       help='Install dependencies')
    parser.add_argument('--dist', action='store_true',
                       help='Create distribution package')
    
    args = parser.parse_args()
    
    if args.clean:
        clean_build()
    
    if args.deps:
        install_dependencies()
    
    build_application(args.type)
    
    if args.dist:
        create_distribution()
    
    print("Build complete!")

if __name__ == '__main__':
    main()
```

Usage:
```bash
# Full release build
python build_all.py --clean --deps --dist

# Debug build
python build_all.py --type debug

# Quick build
python build_all.py
```

## Build Optimization

### Size Optimization

#### Reduce Executable Size

1. **Exclude unnecessary modules**:
```python
excludes=[
    'tkinter.dnd',
    'tkinter.colorchooser',
    'tkinter.font',
    'turtle',
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'jupyter',
    'notebook',
]
```

2. **Use UPX compression**:
```bash
# Install UPX
sudo apt install upx  # Linux
brew install upx      # macOS
# Download from upx.github.io for Windows

# Enable in PyInstaller
pyinstaller --upx-dir=/usr/bin unsplash-gpt-tool.spec
```

3. **Strip debug symbols** (Linux/macOS):
```bash
strip dist/unsplash-gpt-tool
```

#### Performance Optimization

1. **Optimize imports**:
```python
# main.py - only import what you need
import sys
if sys.platform == 'win32':
    import winsound
```

2. **Lazy loading**:
```python
def get_openai_client():
    # Import only when needed
    from openai import OpenAI
    return OpenAI(api_key=api_key)
```

3. **Precompile Python code**:
```bash
python -m compileall .
```

### Memory Optimization

1. **Limit image cache size**:
```python
# In main.py
MAX_CACHE_SIZE = 50  # Limit cached images
```

2. **Use onedir for development**:
```bash
# Faster startup, more memory efficient
pyinstaller --onedir --windowed main.py
```

## Troubleshooting Builds

### Common Build Errors

#### Import Errors

**Error**: `ModuleNotFoundError: No module named 'tkinter'`
**Solution**:
```bash
# Ensure tkinter is installed
sudo apt install python3-tk  # Linux
brew install python-tk        # macOS
# Included in Windows Python
```

**Error**: Missing hidden imports
**Solution**:
```python
# Add to spec file
hiddenimports=[
    'PIL.ImageTk',
    'tkinter.ttk',
    'json',
    'csv',
    'threading',
]
```

#### File/Path Errors

**Error**: `FileNotFoundError: [Errno 2] No such file or directory`
**Solution**:
```python
# Use proper path handling
from pathlib import Path

# Get application directory
if getattr(sys, 'frozen', False):
    app_dir = Path(sys.executable).parent
else:
    app_dir = Path(__file__).parent

config_path = app_dir / 'config.ini'
```

#### Permission Errors

**Error**: Permission denied during build
**Solution**:
```bash
# Ensure write permissions
chmod 755 .
chmod 644 *.py

# On Windows, run as administrator
```

### Build Debugging

#### Enable Debug Mode
```bash
# Build with debug information
pyinstaller --debug=all --console main.py

# Run and check output
./dist/main/main
```

#### Check Dependencies
```bash
# List all imports
python -c "import main; print('OK')"

# Check specific module
python -c "import tkinter; print(tkinter.__file__)"
```

#### Analyze Build
```bash
# Check executable
file dist/unsplash-gpt-tool      # Linux/macOS

# Check dependencies (Linux)
ldd dist/unsplash-gpt-tool

# Check size
ls -lh dist/
```

### Platform-Specific Issues

#### Windows
- **Antivirus interference**: Exclude build directory
- **Path length limits**: Use short paths
- **Missing DLLs**: Install Visual C++ Redistributable

#### macOS
- **Code signing**: Required for distribution
- **Gatekeeper**: App may be quarantined
- **Python version conflicts**: Use consistent Python

#### Linux
- **Missing libraries**: Install system dependencies
- **Display server**: Test on target desktop environment
- **Distribution compatibility**: Test on target distros

## Contributing Guidelines

### Code Quality

#### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

#### Code Style
```bash
# Format code
black .
isort .

# Lint code
flake8 .

# Type checking
mypy .
```

#### Testing
```bash
# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Test build
python -m pytest tests/test_build.py
```

### Build Testing

#### Test Matrix

1. **Platforms**: Windows, macOS, Linux
2. **Python versions**: 3.8, 3.9, 3.10, 3.11
3. **Build types**: Debug, Release, Portable
4. **Installation methods**: Source, Executable, Package

#### Automated Testing
```yaml
# .github/workflows/test-build.yml
name: Test Builds

on: [push, pull_request]

jobs:
  test-build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.8', '3.11']
        build-type: ['debug', 'release']
    
    runs-on: ${{ matrix.os }}
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Test build
      run: |
        python build_all.py --type ${{ matrix.build-type }} --deps
        # Test executable
        ./dist/unsplash-gpt-tool --help || ./dist/unsplash-gpt-tool.exe --help
```

### Documentation

#### Build Documentation

Update documentation when:
- Adding new build options
- Changing dependencies
- Supporting new platforms
- Modifying build process

#### Change Log

Document in `CHANGELOG.md`:
- Build system changes
- New platform support
- Dependency updates
- Performance improvements

---

## Quick Reference

### Essential Commands

```bash
# Quick build
pyinstaller --onefile --windowed main.py

# Clean build
rm -rf build dist *.spec && python build_all.py

# Debug build
pyinstaller --onedir --console --debug=all main.py

# Test executable
./dist/unsplash-gpt-tool --version
```

### Build Checklist

- [ ] Dependencies installed
- [ ] Virtual environment active
- [ ] Code passes tests
- [ ] Build completes without errors
- [ ] Executable runs successfully
- [ ] File size reasonable
- [ ] All features work
- [ ] Documentation updated

---

**Need help with builds?** Create an issue on GitHub with:
- Your operating system and version
- Python version
- Complete error message
- Build command used
- Any customizations made