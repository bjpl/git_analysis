# Enhanced Installer System for Unsplash Image Search GPT Description

This directory contains a comprehensive installer system designed for professional deployment of the Unsplash Image Search GPT Description application. The system supports multiple installation types, enterprise deployment, and modern user experience.

## 🚀 Features

### Core Installer Features
- **Modern UI** with custom branding and wizard pages
- **Multiple Installation Types**: Full, Minimal, Portable, Enterprise
- **API Key Configuration** during installation
- **Prerequisite Checking** and automatic installation (.NET Framework, VC++ Redistributable)
- **Previous Installation Detection** with migration support
- **File Associations** for .uigd session files and .uiconfig files
- **Multi-language Support** (English, Spanish, French, German)

### Enterprise Features
- **Silent Installation** with XML configuration files
- **MSI Wrapper** for Group Policy deployment
- **Registry Settings** for centralized management
- **Advanced Security Options** and policy enforcement
- **Automated Update Management**
- **Comprehensive Logging** and audit trails

### User Experience
- **Configuration Wizard** with API key validation
- **Progress Indicators** for long operations
- **Detailed Error Messages** with troubleshooting guidance
- **Backup and Migration** tools for upgrades
- **Uninstaller** with data preservation options

## 📁 Directory Structure

```
installer/
├── installer_enhanced.iss          # Main Inno Setup script
├── installer.iss                   # Original installer (preserved)
├── installer.nsi                   # NSIS installer (alternative)
├── build_installer.bat             # Windows batch build script
├── build_installer.ps1             # PowerShell build script (advanced)
├── README.md                       # This documentation
├── INSTALLER_ASSETS_GUIDE.md       # Asset creation guide
│
├── assets/                         # Visual assets and resources
│   ├── app_icon.ico                # Application icon (required)
│   ├── wizard_left.bmp             # Wizard banner (164x314)
│   ├── wizard_small.bmp            # Wizard header icon (55x58)
│   ├── uninstall_banner.bmp        # Uninstaller banner
│   ├── config.ini.template         # Configuration template
│   ├── info_before.txt             # Pre-installation information
│   ├── info_after.txt              # Post-installation information
│   └── samples/                    # Sample files and examples
│
├── config/                         # Configuration files
│   ├── silent_install.xml          # Silent installation settings
│   └── enterprise_config.json      # Enterprise deployment config
│
├── dependencies/                   # Dependency management
│   └── CodeDependencies.iss        # Prerequisites installer
│
├── scripts/                        # Support scripts
│   ├── migrate_settings.py         # Settings migration
│   └── post_install.py             # Post-installation tasks
│
├── tools/                          # Build and packaging tools
│   └── create_msi.ps1              # MSI wrapper creation
│
└── output/                         # Build output directory
    ├── *.exe                       # Built installers
    ├── *.msi                       # MSI packages
    ├── *.zip                       # Portable packages
    └── Distribution/               # Complete deployment package
```

## 🛠️ Building Installers

### Prerequisites

1. **Inno Setup 6.2+**: Download from [jrsoftware.org](https://jrsoftware.org/isinfo.php)
2. **WiX Toolset 3.11+**: Download from [wixtoolset.org](https://wixtoolset.org/releases/) (for MSI creation)
3. **PowerShell 5.1+**: For advanced build script
4. **Built Application**: Run `python -m PyInstaller main.spec` first

### Quick Build (Windows)

```batch
# Navigate to installer directory
cd installer

# Run the build script
build_installer.bat
```

### Advanced Build (PowerShell)

```powershell
# Build for all architectures with MSI and signing
.\build_installer.ps1 -Architecture both -CreateMSI -SignInstaller -CertificatePath "cert.pfx"

# Build portable version only
.\build_installer.ps1 -CreatePortable -SkipValidation

# Build for specific configuration
.\build_installer.ps1 -Configuration production -Version "1.0.1"
```

### Build Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `-Architecture` | Target architecture (x86, x64, both) | both |
| `-Configuration` | Build configuration (development, testing, production) | production |
| `-Version` | Version number | 1.0.0 |
| `-CreateMSI` | Generate MSI wrapper | true |
| `-SignInstaller` | Code sign the installer | false |
| `-CreatePortable` | Generate portable package | true |
| `-SkipValidation` | Skip installer validation | false |

## 📦 Installation Types

### 1. Standard Installation
- Full interactive installer with wizard
- User can select components and configure settings
- Creates desktop shortcuts and file associations
- Suitable for individual users

```batch
unsplash-image-search-setup-1.0.0.exe
```

### 2. Silent Installation
- No user interaction required
- Uses predefined configuration
- Ideal for automated deployment

```batch
# Basic silent install
unsplash-image-search-setup-1.0.0.exe /VERYSILENT /NORESTART

# With custom configuration
unsplash-image-search-setup-1.0.0.exe /VERYSILENT /CONFIG="config\silent_install.xml"

# With logging
unsplash-image-search-setup-1.0.0.exe /VERYSILENT /LOG="install.log"
```

### 3. Enterprise Deployment (MSI)
- Group Policy and SCCM compatible
- Centralized configuration management
- Advanced deployment options

```batch
# Silent MSI installation
msiexec /i unsplash-image-search-1.0.0.msi /quiet /norestart

# With logging
msiexec /i unsplash-image-search-1.0.0.msi /quiet /norestart /l*v install.log

# Uninstall
msiexec /x {B8F4A2C1-9D3E-4F7A-8B2C-1E5A6D9F3C8B} /quiet
```

### 4. Portable Installation
- No installation required
- Runs from any location
- All data stored in application folder

```batch
# Extract and run
unzip unsplash-image-search-portable-1.0.0.zip
cd unsplash-image-search-portable
unsplash-image-search.exe
```

## ⚙️ Configuration

### Silent Installation Configuration

Edit `config/silent_install.xml` to customize silent installations:

```xml
<SilentInstallConfig>
  <General>
    <InstallType>full</InstallType>
    <AcceptLicense>true</AcceptLicense>
  </General>
  
  <Configuration>
    <UnsplashAPIKey>your-api-key-here</UnsplashAPIKey>
    <OpenAIAPIKey>your-openai-key-here</OpenAIAPIKey>
    <DefaultLanguage>English</DefaultLanguage>
  </Configuration>
  
  <Tasks>
    <DesktopIcon>true</DesktopIcon>
    <FileAssociations>true</FileAssociations>
    <AutoUpdater>true</AutoUpdater>
  </Tasks>
</SilentInstallConfig>
```

### Enterprise Configuration

Edit `config/enterprise_config.json` for enterprise deployment:

```json
{
  "security": {
    "allow_user_configuration": false,
    "require_admin_for_settings": true,
    "encrypt_api_keys": true
  },
  "deployment": {
    "silent_install_parameters": [
      "/VERYSILENT",
      "/NORESTART",
      "/TASKS=\"startmenu,firewall\""
    ]
  }
}
```

## 🎨 Customization

### Visual Assets

Create custom installer branding by adding these files to `assets/`:

- **app_icon.ico**: Application icon (multi-size ICO format)
- **wizard_left.bmp**: Wizard banner (164×314 pixels)
- **wizard_small.bmp**: Wizard header icon (55×58 pixels)
- **uninstall_banner.bmp**: Uninstaller banner

See [INSTALLER_ASSETS_GUIDE.md](INSTALLER_ASSETS_GUIDE.md) for detailed specifications.

### Localization

Add localized license files:
- `assets/LICENSE_es.txt` (Spanish)
- `assets/LICENSE_fr.txt` (French)
- `assets/LICENSE_de.txt` (German)

### Custom Pages

The installer includes several custom wizard pages:
- **Installation Type Selection**: Choose between installation modes
- **API Configuration**: Enter API keys with validation
- **Data Directory Selection**: Choose user data location
- **Migration Options**: Import from previous versions

## 🏢 Enterprise Deployment

### Group Policy Deployment

1. **Prepare MSI Package**:
   ```powershell
   .\build_installer.ps1 -CreateMSI
   ```

2. **Configure Group Policy**:
   - Copy MSI to network share
   - Create/edit GPO
   - Add to Software Installation
   - Configure as "Assigned" deployment

3. **Advanced Configuration**:
   - Pre-configure enterprise_config.json
   - Set registry policies
   - Configure automatic updates

### SCCM Deployment

1. **Create Application**:
   - Use MSI as installation source
   - Configure detection methods
   - Set system requirements

2. **Distribution**:
   - Distribute to distribution points
   - Deploy to device collections
   - Monitor deployment status

### Command-Line Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `/SILENT` | Silent with progress bar | `/SILENT` |
| `/VERYSILENT` | Completely silent | `/VERYSILENT` |
| `/NORESTART` | Suppress restart prompts | `/NORESTART` |
| `/LOG` | Enable logging | `/LOG="install.log"` |
| `/CONFIG` | Use configuration file | `/CONFIG="config.xml"` |
| `/LOADINF` | Load settings from file | `/LOADINF="setup.inf"` |
| `/SAVEINF` | Save settings to file | `/SAVEINF="setup.inf"` |
| `/TASKS` | Select tasks | `/TASKS="desktopicon,startmenu"` |
| `/COMPONENTS` | Select components | `/COMPONENTS="core,docs"` |

## 🔧 Troubleshooting

### Common Issues

1. **Prerequisites Installation Failed**:
   - Check internet connection
   - Run as administrator
   - Manually install .NET Framework 4.8

2. **MSI Creation Failed**:
   - Install WiX Toolset
   - Check PATH environment variable
   - Verify PowerShell execution policy

3. **Code Signing Failed**:
   - Verify certificate path and password
   - Check certificate validity
   - Ensure SignTool.exe is available

4. **Assets Not Found**:
   - Check assets directory
   - See INSTALLER_ASSETS_GUIDE.md
   - Use default assets (warnings only)

### Debug Mode

Enable verbose logging:

```batch
# Batch script with debug output
set DEBUG=1
build_installer.bat

# PowerShell with verbose output
.\build_installer.ps1 -Verbose
```

### Log Analysis

Check log files:
- Installation: `%TEMP%\Setup Log YYYY-MM-DD #NNN.txt`
- MSI: `install.log` (if specified)
- Build: Console output or build logs

## 📋 Testing Checklist

### Pre-Release Testing

- [ ] Test on clean Windows 7, 10, 11 systems
- [ ] Verify silent installation works
- [ ] Test MSI deployment
- [ ] Check portable version functionality
- [ ] Validate API key configuration
- [ ] Test uninstaller data options
- [ ] Verify file associations work
- [ ] Check prerequisites installation
- [ ] Test upgrade from previous version
- [ ] Validate multilingual support

### Quality Assurance

- [ ] All visual assets display correctly
- [ ] No broken links or missing files
- [ ] Installer size is reasonable (<100MB)
- [ ] Code signing verification passes
- [ ] Registry entries are correct
- [ ] Shortcuts work properly
- [ ] Uninstaller removes all components
- [ ] Configuration files are valid
- [ ] Documentation is up to date

## 🔄 Maintenance

### Version Updates

1. Update version numbers in:
   - `installer_enhanced.iss` (`MyAppVersion`)
   - `build_installer.ps1` (`$Version` default)
   - Configuration files

2. Update prerequisites if needed:
   - Check for newer runtime versions
   - Update download URLs
   - Test compatibility

3. Refresh assets:
   - Update screenshots in documentation
   - Refresh wizard images if rebranding
   - Update copyright years

### Release Process

1. **Build and Test**:
   ```powershell
   .\build_installer.ps1 -Configuration production -SignInstaller
   ```

2. **Quality Assurance**:
   - Run full test suite
   - Test on multiple platforms
   - Validate enterprise deployment

3. **Distribution**:
   - Upload to release repository
   - Update documentation
   - Notify deployment teams

## 📞 Support

For installer-related issues:

1. **Check Documentation**: Review this README and asset guide
2. **Search Issues**: Look for similar problems in repository issues
3. **Create Issue**: Provide detailed information including:
   - Windows version and architecture
   - Installation method attempted
   - Error messages and log files
   - Steps to reproduce

## 📄 License

This installer system is part of the Unsplash Image Search GPT Description project and follows the same license terms.

---

**Note**: This installer system is designed to be professional, user-friendly, and enterprise-ready. Customize the configuration files and assets to match your deployment requirements.