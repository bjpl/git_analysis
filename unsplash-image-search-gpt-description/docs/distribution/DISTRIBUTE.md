# Distribution Guide for Developers and Packagers

This guide covers building, packaging, and distributing the Unsplash Image Search with GPT application.

## Table of Contents

- [Overview](#overview)
- [Build Requirements](#build-requirements)
- [Building from Source](#building-from-source)
- [Creating Installers](#creating-installers)
- [Distribution Platforms](#distribution-platforms)
- [Continuous Integration](#continuous-integration)
- [Release Process](#release-process)
- [Packaging Guidelines](#packaging-guidelines)
- [Platform-Specific Notes](#platform-specific-notes)

## Overview

### Supported Distribution Methods

1. **Windows Installer (NSIS)** - Full-featured installer with wizard
2. **Portable Executable** - Single-file distribution
3. **Source Distribution** - For developers and custom builds
4. **Package Managers** - Chocolatey, Scoop (future)
5. **Container Images** - Docker (future)

### Build Artifacts

- `unsplash-gpt-tool.exe` - Main executable (Windows)
- `unsplash-image-search-nsis-setup.exe` - Windows installer
- `unsplash-gpt-tool-portable.zip` - Portable version
- `source-dist.tar.gz` - Source distribution

## Build Requirements

### Development Environment

**Required Software**:
- Python 3.8+ (3.11 recommended)
- Git for version control
- PyInstaller 6.0+
- NSIS 3.0+ (for Windows installer)
- Inno Setup 6.0+ (alternative installer)

**Python Dependencies**:
```bash
# Core dependencies
pip install -r requirements.txt

# Build dependencies  
pip install -r requirements-dev.txt

# Additional build tools
pip install pyinstaller cx_Freeze auto-py-to-exe
```

**System Requirements**:
- **RAM**: 8 GB minimum (16 GB recommended)
- **Storage**: 5 GB free space for build artifacts
- **Network**: High-speed internet for dependency downloads

### Platform-Specific Requirements

#### Windows
```cmd
# Install Windows SDK (for advanced features)
choco install windows-sdk-10-version-2004-all

# Install NSIS
choco install nsis

# Install Inno Setup
choco install innosetup
```

#### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install create-dmg for macOS distributions
brew install create-dmg
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt install build-essential python3-dev

# Install AppImage tools
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
```

## Building from Source

### Clone Repository

```bash
git clone https://github.com/your-username/unsplash-image-search-gpt-description.git
cd unsplash-image-search-gpt-description
```

### Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Build Executable

#### Windows

```cmd
# Quick build (uses build.bat)
build.bat

# Manual build with PyInstaller
pyinstaller --clean ^  
    --onefile ^  
    --windowed ^  
    --name "unsplash-gpt-tool" ^  
    --icon "assets\icon.ico" ^  
    --add-data ".env.example;." ^  
    --add-data "README.md;." ^  
    --hidden-import "tkinter" ^  
    --hidden-import "PIL" ^  
    --hidden-import "openai" ^  
    main.py
```

#### Linux/macOS

```bash
# Quick build (uses build.sh)
./build.sh

# Manual build with PyInstaller
pyinstaller --clean \
    --onefile \
    --windowed \
    --name "unsplash-gpt-tool" \
    --icon "assets/icon.ico" \
    --add-data ".env.example:." \
    --add-data "README.md:." \
    --hidden-import "tkinter" \
    --hidden-import "PIL" \
    --hidden-import "openai" \
    main.py
```

### Advanced Build Options

#### Optimized Build

```bash
# Enable UPX compression (smaller file size)
pyinstaller --upx-dir=/path/to/upx \
    --clean --onefile \
    # ... other options
    main.py

# Enable debug mode for troubleshooting
pyinstaller --debug=all \
    # ... other options
    main.py
```

#### Custom Spec File

Create `main.spec` for advanced configuration:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('.env.example', '.'),
        ('README.md', '.'),
        ('docs', 'docs'),
        ('examples', 'examples')
    ],
    hiddenimports=['tkinter', 'PIL', 'openai', 'dotenv'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'sphinx'],
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
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'
)
```

Build with spec file:
```bash
pyinstaller main.spec
```

## Creating Installers

### Windows NSIS Installer

**Prerequisites**:
- NSIS 3.0+ installed
- Built executable in `dist/` folder
- Assets in `assets/` folder

**Build Process**:
```cmd
# 1. Build the executable first
build.bat

# 2. Compile NSIS installer
"C:\Program Files (x86)\NSIS\makensis.exe" installer\installer.nsi

# 3. Output: installer\output\unsplash-image-search-nsis-setup.exe
```

**Customization**:
Edit `installer/installer.nsi` to customize:
- Installation directory
- Start menu entries
- File associations
- Registry entries
- Custom pages

### Windows Inno Setup Installer

**Alternative to NSIS with different features**:

```cmd
# Compile with Inno Setup
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\installer.iss
```

Features:
- Code signing support
- Custom actions
- Web downloads
- Multilingual support

### Portable Version

**Create portable ZIP**:
```cmd
# Windows batch script
create-portable.bat

# Manual process
mkdir portable\UnsplashGPT
copy dist\unsplash-gpt-tool.exe portable\UnsplashGPT\
copy README.md portable\UnsplashGPT\
copy .env.example portable\UnsplashGPT\
mkdir portable\UnsplashGPT\data

# Create ZIP
7z a -tzip unsplash-gpt-tool-portable.zip portable\UnsplashGPT\*
```

### macOS Distribution

#### App Bundle

```bash
# Build app bundle
python setup.py py2app

# Create DMG
create-dmg \
    --volname "Unsplash GPT Tool" \
    --volicon "assets/icon.icns" \
    --window-pos 200 120 \
    --window-size 800 400 \
    --icon-size 100 \
    --icon "UnsplashGPTTool.app" 200 190 \
    --hide-extension "UnsplashGPTTool.app" \
    --app-drop-link 600 185 \
    "UnsplashGPTTool.dmg" \
    "dist/"
```

#### Code Signing (Optional)

```bash
# Sign the app
codesign --force --deep --sign "Developer ID Application: Your Name" \
    dist/UnsplashGPTTool.app

# Verify signature
codesign --verify --deep --strict dist/UnsplashGPTTool.app
```

### Linux Distribution

#### AppImage

```bash
# Create AppDir structure
mkdir -p UnsplashGPTTool.AppDir/usr/bin
cp dist/unsplash-gpt-tool UnsplashGPTTool.AppDir/usr/bin/

# Create desktop file
cat > UnsplashGPTTool.AppDir/UnsplashGPTTool.desktop << EOF
[Desktop Entry]
Name=Unsplash GPT Tool
Exec=unsplash-gpt-tool
Icon=unsplash-gpt-tool
Type=Application
Categories=Graphics;Photography;Education;
EOF

# Create AppImage
./appimagetool-x86_64.AppImage UnsplashGPTTool.AppDir
```

#### Debian Package

```bash
# Create package structure
mkdir -p deb/unsplash-gpt-tool/DEBIAN
mkdir -p deb/unsplash-gpt-tool/usr/bin
mkdir -p deb/unsplash-gpt-tool/usr/share/applications

# Copy files
cp dist/unsplash-gpt-tool deb/unsplash-gpt-tool/usr/bin/
cp assets/unsplash-gpt-tool.desktop deb/unsplash-gpt-tool/usr/share/applications/

# Create control file
cat > deb/unsplash-gpt-tool/DEBIAN/control << EOF
Package: unsplash-gpt-tool
Version: 1.0.0
Section: graphics
Priority: optional
Architecture: amd64
Maintainer: Your Name <your.email@example.com>
Description: AI-powered image search and description tool
EOF

# Build package
dpkg-deb --build deb/unsplash-gpt-tool
```

## Distribution Platforms

### GitHub Releases

**Automated with GitHub Actions**:

```yaml
# .github/workflows/release.yml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller
      
      - name: Build executable
        run: build.bat
      
      - name: Build installer
        run: |
          choco install nsis -y
          makensis installer/installer.nsi
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: windows-builds
          path: |
            dist/unsplash-gpt-tool.exe
            installer/output/*.exe
```

### Package Managers

#### Chocolatey (Windows)

**Package Definition** (`chocolatey/unsplash-gpt-tool.nuspec`):

```xml
<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2015/06/nuspec.xsd">
  <metadata>
    <id>unsplash-gpt-tool</id>
    <version>1.0.0</version>
    <packageSourceUrl>https://github.com/your-username/unsplash-image-search-gpt-description</packageSourceUrl>
    <owners>YourName</owners>
    <title>Unsplash GPT Tool</title>
    <authors>YourName</authors>
    <projectUrl>https://github.com/your-username/unsplash-image-search-gpt-description</projectUrl>
    <iconUrl>https://cdn.jsdelivr.net/gh/your-username/unsplash-image-search-gpt-description@main/assets/icon.png</iconUrl>
    <copyright>2024 YourName</copyright>
    <licenseUrl>https://github.com/your-username/unsplash-image-search-gpt-description/blob/main/LICENSE</licenseUrl>
    <requireLicenseAcceptance>false</requireLicenseAcceptance>
    <projectSourceUrl>https://github.com/your-username/unsplash-image-search-gpt-description</projectSourceUrl>
    <summary>AI-powered image search and description tool</summary>
    <description>Search Unsplash images and generate detailed Spanish descriptions using GPT-4 Vision. Perfect for language learning and vocabulary building.</description>
    <tags>unsplash images ai gpt language-learning spanish vocabulary</tags>
  </metadata>
  <files>
    <file src="tools\**" target="tools" />
  </files>
</package>
```

#### Scoop (Windows)

**Manifest** (`scoop/unsplash-gpt-tool.json`):

```json
{
    "version": "1.0.0",
    "description": "AI-powered image search and description tool",
    "homepage": "https://github.com/your-username/unsplash-image-search-gpt-description",
    "license": "MIT",
    "url": "https://github.com/your-username/unsplash-image-search-gpt-description/releases/download/v1.0.0/unsplash-gpt-tool-portable.zip",
    "hash": "sha256:...",
    "extract_dir": "UnsplashGPT",
    "bin": "unsplash-gpt-tool.exe",
    "shortcuts": [
        [
            "unsplash-gpt-tool.exe",
            "Unsplash GPT Tool"
        ]
    ],
    "checkver": {
        "github": "https://github.com/your-username/unsplash-image-search-gpt-description"
    },
    "autoupdate": {
        "url": "https://github.com/your-username/unsplash-image-search-gpt-description/releases/download/v$version/unsplash-gpt-tool-portable.zip"
    }
}
```

## Continuous Integration

### GitHub Actions Workflow

**Complete CI/CD Pipeline**:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]

env:
  PYTHON_VERSION: '3.11'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: |
          pytest --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  build:
    needs: test
    strategy:
      matrix:
        os: [windows-latest, ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller
      
      - name: Build executable (Windows)
        if: matrix.os == 'windows-latest'
        run: |
          build.bat
          
      - name: Build executable (Unix)
        if: matrix.os != 'windows-latest'
        run: |
          chmod +x build.sh
          ./build.sh
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.os }}-executable
          path: dist/

  package:
    needs: build
    if: startsWith(github.ref, 'refs/tags/')
    runs-on: windows-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Download Windows executable
        uses: actions/download-artifact@v3
        with:
          name: windows-latest-executable
          path: dist/
      
      - name: Install NSIS
        run: choco install nsis -y
      
      - name: Build installer
        run: makensis installer/installer.nsi
      
      - name: Create portable version
        run: |
          mkdir portable\UnsplashGPT
          copy dist\unsplash-gpt-tool.exe portable\UnsplashGPT\
          copy README.md portable\UnsplashGPT\
          7z a -tzip unsplash-gpt-tool-portable.zip portable\UnsplashGPT\*
      
      - name: Create release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            installer/output/*.exe
            unsplash-gpt-tool-portable.zip
          draft: false
          prerelease: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Release Process

### Version Management

**Semantic Versioning**:
- `MAJOR.MINOR.PATCH` (e.g., 1.2.3)
- Major: Breaking changes
- Minor: New features
- Patch: Bug fixes

**Version Files to Update**:
1. `version_info.py` - Application version
2. `pyproject.toml` - Package metadata
3. `installer/installer.nsi` - Installer version
4. `installer/installer.iss` - Inno Setup version

### Release Checklist

**Pre-Release**:
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Version numbers updated
- [ ] CHANGELOG.md updated
- [ ] Security scan completed
- [ ] Performance tests passed

**Release Process**:
1. **Create release branch**: `git checkout -b release/v1.2.3`
2. **Update version numbers** in all relevant files
3. **Update CHANGELOG.md** with new features and fixes
4. **Test build process** on all platforms
5. **Merge to main**: Create PR and merge
6. **Create tag**: `git tag v1.2.3`
7. **Push tag**: `git push origin v1.2.3`
8. **Automated build** triggers via GitHub Actions
9. **Manual testing** of release artifacts
10. **Publish release** on GitHub
11. **Update package managers** (if applicable)

**Post-Release**:
- [ ] Verify download links
- [ ] Update documentation sites
- [ ] Announce on social media
- [ ] Monitor for issues

## Packaging Guidelines

### File Structure

**Installer Package**:
```
unsplash-image-search-gpt-description/
├── unsplash-image-search.exe     # Main executable
├── config.ini                  # Default configuration
├── README.md                   # User documentation
├── LICENSE                     # License file
├── data/                       # Data directory
│   └── .gitkeep
├── docs/                       # Documentation
│   ├── USER_MANUAL.md
│   └── QUICK_START.md
└── examples/                   # Example files
    └── sample_session.json
```

**Portable Package**:
```
UnsplashGPT/
├── unsplash-gpt-tool.exe       # Main executable
├── portable.txt                # Indicates portable version
├── README.md                   # Quick start guide
├── .env.example                # Environment template
└── data/                       # Local data directory
    └── .gitkeep
```

### Metadata Requirements

**Application Metadata**:
- Product name and version
- Description and keywords
- Author and contact information
- License and copyright
- Homepage and documentation URLs
- System requirements
- Installation size estimate

**Digital Signatures** (Recommended):
- Code signing certificate for executables
- GPG signatures for source distributions
- SHA256 checksums for all artifacts

### Quality Assurance

**Automated Testing**:
- Unit tests with >80% coverage
- Integration tests for API workflows
- UI tests with automation tools
- Performance benchmarks
- Security scans (bandit, safety)

**Manual Testing**:
- Fresh installation testing
- Upgrade testing from previous versions
- Uninstallation testing
- Cross-platform compatibility
- Different system configurations

## Platform-Specific Notes

### Windows

**Installer Features**:
- Custom installation directory
- Start Menu shortcuts
- Desktop shortcuts
- File associations (.uigd files)
- Uninstaller with data cleanup options
- Registry entries for proper integration

**Code Signing**:
```cmd
# Sign executable (requires certificate)
signtool sign /f certificate.pfx /p password /t http://timestamp.sectigo.com unsplash-gpt-tool.exe

# Verify signature
signtool verify /pa unsplash-gpt-tool.exe
```

### macOS

**App Bundle Requirements**:
- Proper Info.plist configuration
- Icon files in multiple resolutions
- Codesigning for Gatekeeper
- Notarization for distribution

**DMG Creation**:
```bash
# Create attractive DMG with background
create-dmg \
    --volname "Unsplash GPT Tool" \
    --background "assets/dmg-background.png" \
    --window-pos 200 120 \
    --window-size 800 600 \
    --icon-size 100 \
    --icon "UnsplashGPTTool.app" 200 300 \
    --hide-extension "UnsplashGPTTool.app" \
    --app-drop-link 600 300 \
    "UnsplashGPTTool.dmg" \
    "dist/"
```

### Linux

**Desktop Integration**:
```ini
# /usr/share/applications/unsplash-gpt-tool.desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=Unsplash GPT Tool
Comment=AI-powered image search and description tool
Exec=unsplash-gpt-tool
Icon=unsplash-gpt-tool
Terminal=false
Categories=Graphics;Photography;Education;
MimeType=application/x-uigd;
```

**Package Dependencies**:
- Python 3.8+ (for source installations)
- tkinter (python3-tk)
- Additional system libraries as needed

---

## Support and Troubleshooting

### Build Issues

**Common Problems**:
- Missing dependencies: Check requirements.txt
- Path issues: Use absolute paths in build scripts
- Permission errors: Run with appropriate privileges
- Memory issues: Increase available RAM or use swap

**Debug Build**:
```bash
# Enable debug mode
pyinstaller --debug=all main.py

# Check imports
python -c "import tkinter; import PIL; import openai; print('OK')"

# Test minimal build
pyinstaller --onefile --console main.py
```

### Distribution Issues

**Installer Problems**:
- Test on clean virtual machines
- Verify all dependencies are included
- Check file permissions and paths
- Test uninstall process thoroughly

**Platform Compatibility**:
- Test on multiple OS versions
- Verify 32-bit vs 64-bit compatibility
- Check for missing system libraries
- Validate file associations work

For distribution support, contact the development team or create an issue on GitHub.