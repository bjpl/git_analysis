# Installation Guide - Unsplash Image Search with GPT

This guide covers installation options for the Unsplash Image Search with GPT application.

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Installation (Recommended)](#quick-installation-recommended)
- [Installation from Source](#installation-from-source)
- [API Key Setup](#api-key-setup)
- [First Run](#first-run)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 (64-bit) or later
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 500 MB free disk space (plus space for vocabulary data)
- **Internet**: Required for API access to Unsplash and OpenAI
- **Display**: 1024x768 minimum resolution

### Supported Platforms
- ✅ Windows 10/11 (64-bit) - Primary platform
- ✅ Windows 10/11 (32-bit) - Limited support
- ⚠️ macOS 10.14+ - Source installation only
- ⚠️ Linux (Ubuntu 18.04+) - Source installation only

### Dependencies (Pre-installed in executable)
- Python 3.8+ (for source installations)
- Tkinter (GUI framework)
- PIL/Pillow (image processing)
- OpenAI SDK (GPT integration)
- Requests (HTTP client)

## Quick Installation (Recommended)

### Option 1: Windows Installer (NSIS)

**Best for most users - includes setup wizard and automatic configuration**

1. **Download the installer**:
   - Go to [Releases](https://github.com/your-username/unsplash-image-search-gpt-description/releases)
   - Download `unsplash-image-search-nsis-setup.exe`

2. **Run the installer**:
   - Right-click the downloaded file → "Run as administrator" (recommended)
   - Follow the installation wizard
   - Choose installation directory (default: `C:\Program Files\Unsplash Image Search GPT Description`)

3. **Configure during installation**:
   - **API Keys**: Optionally enter your Unsplash and OpenAI API keys
   - **Data Directory**: Choose where to store sessions and vocabulary
   - **Language**: Select default search language

4. **Complete installation**:
   - Click "Finish" to launch the application
   - Desktop and Start Menu shortcuts are created automatically

### Option 2: Portable Executable

**Best for users who want a portable installation**

1. **Download the portable version**:
   - Go to [Releases](https://github.com/your-username/unsplash-image-search-gpt-description/releases)
   - Download `unsplash-gpt-tool-portable.zip`

2. **Extract and run**:
   ```cmd
   # Extract to desired location
   # Example: C:\Tools\UnsplashGPT
   
   # Run the executable
   unsplash-gpt-tool.exe
   ```

3. **First run setup**:
   - The application will prompt for API keys
   - Data will be stored in the same directory as the executable

## Installation from Source

### Prerequisites

1. **Install Python 3.8+**:
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   - Verify installation:
     ```cmd
     python --version
     pip --version
     ```

2. **Install Git** (optional):
   - Download from [git-scm.com](https://git-scm.com/downloads)
   - Or download ZIP from GitHub

### Installation Steps

1. **Get the source code**:
   ```bash
   # Option A: Clone with Git
   git clone https://github.com/your-username/unsplash-image-search-gpt-description.git
   cd unsplash-image-search-gpt-description
   
   # Option B: Download and extract ZIP
   # Extract to a folder and navigate to it in terminal
   ```

2. **Install dependencies**:
   ```bash
   # Install required packages
   pip install -r requirements.txt
   
   # Optional: Install development dependencies
   pip install -r requirements-dev.txt
   ```

3. **Verify installation**:
   ```bash
   # Run the application
   python main.py
   ```

### Building Your Own Executable

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Build executable**:
   ```bash
   # Windows
   build.bat
   
   # Linux/macOS
   ./build.sh
   ```

3. **Find your executable**:
   - Location: `dist/unsplash-gpt-tool.exe` (Windows)
   - Location: `dist/unsplash-gpt-tool` (Linux/macOS)

## API Key Setup

### Required API Keys

You need API keys from two services:

1. **Unsplash API Key** (Free)
   - Create account at [unsplash.com/developers](https://unsplash.com/developers)
   - Create a new application
   - Copy your "Access Key"
   - **Rate Limit**: 50 requests per hour (free tier)

2. **OpenAI API Key** (Paid)
   - Create account at [platform.openai.com](https://platform.openai.com)
   - Go to API Keys section
   - Create a new secret key
   - **Cost**: ~$0.001-0.01 per image description

### Setup Methods

#### Method 1: Setup Wizard (First Run)
1. Launch the application
2. The setup wizard will appear automatically
3. Enter your API keys when prompted
4. Keys are saved securely in `config.ini`

#### Method 2: Environment Variables
```bash
# Windows Command Prompt
set UNSPLASH_ACCESS_KEY=your_unsplash_key_here
set OPENAI_API_KEY=your_openai_key_here
set GPT_MODEL=gpt-4o-mini

# Windows PowerShell
$env:UNSPLASH_ACCESS_KEY="your_unsplash_key_here"
$env:OPENAI_API_KEY="your_openai_key_here"
$env:GPT_MODEL="gpt-4o-mini"

# Linux/macOS
export UNSPLASH_ACCESS_KEY="your_unsplash_key_here"
export OPENAI_API_KEY="your_openai_key_here"
export GPT_MODEL="gpt-4o-mini"
```

#### Method 3: Configuration File
Create or edit `config.ini` in the application directory:
```ini
[UNSPLASH]
ACCESS_KEY=your_unsplash_key_here

[OPENAI]
API_KEY=your_openai_key_here
MODEL=gpt-4o-mini

[SETTINGS]
DATA_DIR=data
THEME=system
ZOOM_LEVEL=100
```

## First Run

### Launch the Application

**Windows Installer Version**:
- Use desktop shortcut or Start Menu
- Or run from: `C:\Program Files\Unsplash Image Search GPT Description\unsplash-image-search.exe`

**Portable Version**:
- Navigate to extraction folder
- Double-click `unsplash-gpt-tool.exe`

**Source Installation**:
- Open terminal in project directory
- Run: `python main.py`

### Initial Configuration

1. **API Key Setup**: If not configured during installation, you'll see the setup wizard
2. **Data Directory**: Choose where to store your vocabulary and sessions
3. **Theme Selection**: Choose light or dark theme
4. **Test Connection**: The app will verify your API keys

### First Search

1. **Enter a search term** (e.g., "mountain landscape")
2. **Click "Buscar Imagen"** to search
3. **View the image** in the left panel
4. **Add notes** (optional) in the top-right text area
5. **Click "Generar Descripción"** to get AI-generated Spanish description
6. **Click blue phrases** to add them to your vocabulary
7. **Export vocabulary** when ready

## Verification

### Test Basic Functionality

1. **Search Test**:
   - Enter "cat" in search box
   - Click "Buscar Imagen"
   - Verify image loads successfully

2. **API Test**:
   - Click "Generar Descripción"
   - Verify Spanish description appears
   - Check for extracted phrases below description

3. **Vocabulary Test**:
   - Click on a blue phrase
   - Verify it appears in "Frases Objetivo" list
   - Check that translation is generated

4. **Export Test**:
   - Click "Export" button
   - Try exporting to Anki format
   - Verify file is created in data directory

### Performance Check

- **Memory Usage**: Should be under 200MB during normal use
- **Response Time**: Image search should complete in 2-5 seconds
- **Description Generation**: Should complete in 5-15 seconds
- **File Size**: Executable should be 50-100MB

## Troubleshooting

### Common Issues

#### "API key not found" Error
**Cause**: Missing or incorrect API configuration
**Solution**:
1. Check that `config.ini` exists in application directory
2. Verify API keys are correctly entered (no extra spaces)
3. Test API keys using online tools
4. Restart the application

#### "Rate limit exceeded" Error
**Cause**: Too many API requests
**Solution**:
- **Unsplash**: Wait 1 hour for limit reset (50 requests/hour)
- **OpenAI**: Check your account billing and usage limits
- Try using a different search term

#### Images not loading
**Cause**: Network or API issues
**Solution**:
1. Check internet connection
2. Verify Unsplash API key is valid
3. Try searching for a different term
4. Restart the application

#### Application won't start
**Cause**: Missing dependencies or corrupted installation
**Solution**:
1. **Installer version**: Uninstall and reinstall
2. **Portable version**: Re-extract from ZIP
3. **Source version**: Reinstall dependencies
   ```bash
   pip install --force-reinstall -r requirements.txt
   ```

#### Slow performance
**Cause**: System resources or network issues
**Solution**:
1. Close other applications to free RAM
2. Check internet speed (minimum 1 Mbps recommended)
3. Clear application cache:
   - Delete contents of `data/cache/` folder
4. Reduce image zoom level

### Error Codes

| Error Code | Description | Solution |
|------------|-------------|----------|
| HTTP 401 | Invalid API key | Check and re-enter API keys |
| HTTP 403 | API access forbidden | Verify account status and billing |
| HTTP 429 | Rate limit exceeded | Wait for limit reset |
| HTTP 500 | Server error | Try again later |
| JSON Error | Invalid response format | Check API key and try again |
| Network Error | Connection failed | Check internet connection |

### Log Files

Check these files for detailed error information:
- **Session Log**: `data/session_log.json` - Application activity
- **Error Log**: `data/error.log` - Detailed error messages (if created)
- **Configuration**: `config.ini` - Current settings

### Support Resources

- **GitHub Issues**: [Report bugs and request features](https://github.com/your-username/unsplash-image-search-gpt-description/issues)
- **Documentation**: Check `docs/` folder for detailed guides
- **FAQ**: See `docs/distribution/FAQ.md`
- **Community**: Discussions tab on GitHub repository

## Uninstallation

### Windows Installer Version

1. **Using Control Panel**:
   - Open "Apps & Features" or "Programs and Features"
   - Find "Unsplash Image Search GPT Description"
   - Click "Uninstall"
   - Follow the uninstaller prompts

2. **Using Uninstaller**:
   - Go to installation directory
   - Run `uninst.exe`
   - Choose whether to keep user data

### Portable Version

1. **Delete Application Folder**:
   - Simply delete the folder where you extracted the application
   - User data is stored in the same folder

2. **Clean Registry** (optional):
   - No registry entries are created for portable version

### Source Installation

1. **Delete Project Folder**:
   ```bash
   # Remove the entire project directory
   rm -rf unsplash-image-search-gpt-description
   ```

2. **Uninstall Python Packages** (optional):
   ```bash
   pip uninstall -r requirements.txt
   ```

### Data Cleanup

**User Data Locations**:
- **Installer**: Usually in `%USERPROFILE%\Documents\Unsplash Image Search GPT Description\`
- **Portable**: Same folder as executable
- **Source**: `data/` folder in project directory

**Files to Remove**:
- `session_log.json` - Search and description history
- `vocabulary.csv` - Your learned vocabulary
- `config.ini` - Application settings
- `cache/` folder - Cached images
- `exports/` folder - Exported vocabulary files

**Backup Before Removal**:
Consider backing up your vocabulary file before uninstalling:
```cmd
copy "path\to\vocabulary.csv" "C:\Backup\my_vocabulary.csv"
```

---

## Quick Reference

### File Locations
- **Executable**: Installation directory or extracted folder
- **Configuration**: `config.ini` in application directory
- **User Data**: `data/` subdirectory or user documents
- **Vocabulary**: `vocabulary.csv` in data directory
- **Session Log**: `session_log.json` in data directory

### Default Directories
- **Windows Installer**: `C:\Program Files\Unsplash Image Search GPT Description\`
- **User Data**: `%USERPROFILE%\Documents\Unsplash Image Search GPT Description\`
- **Portable**: Same as executable location

### Support
For installation issues, please check the [FAQ](FAQ.md) or create an issue on GitHub with:
- Operating system and version
- Installation method used
- Error message (if any)
- Steps you tried