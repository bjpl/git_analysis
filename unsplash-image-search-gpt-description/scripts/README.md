# Build Scripts Documentation

This directory contains comprehensive build automation scripts for the Unsplash Image Search & GPT Tool project. These scripts provide professional-grade build automation with validation, testing, optimization, and deployment capabilities.

## 📁 Script Overview

### Core Build Scripts

| Script | Type | Purpose |
|--------|------|---------|
| `build.bat` | Batch | Basic build script with validation and testing |
| `Build-Advanced.ps1` | PowerShell | Advanced build with Git integration and automation |
| `pre-build-validation.ps1` | PowerShell | Comprehensive environment validation |
| `post-build-verification.ps1` | PowerShell | Executable verification and optimization |
| `create-installer.ps1` | PowerShell | Automated installer creation (NSIS/Inno Setup) |

### Configuration Files

| File | Purpose |
|------|---------|
| `build-profiles.json` | Build profile definitions and quality gates |
| `build-profile-loader.py` | Python utility for profile management |

## 🚀 Quick Start

### Basic Build (Batch)
```batch
# Simple production build
scripts\build.bat

# Development build with console
scripts\build.bat --profile dev

# Clean build skipping tests
scripts\build.bat --clean --skip-tests
```

### Advanced Build (PowerShell)
```powershell
# Production build with all features
.\scripts\Build-Advanced.ps1 -Profile Production -Clean -CreateInstaller -Compress

# Debug build with testing
.\scripts\Build-Advanced.ps1 -Profile Debug -RunCompatibilityTests -GenerateReport

# Quick development build
.\scripts\Build-Advanced.ps1 -Profile Development -SkipTests
```

## 🔧 Build Profiles

### Available Profiles

| Profile | Description | Use Case |
|---------|-------------|----------|
| **Production** | Optimized, no console, UPX compressed | Final releases |
| **Development** | Fast build, console enabled, debug info | Development work |
| **Debug** | Full debug symbols, verbose output | Troubleshooting |
| **Testing** | Optimized for CI/CD testing | Automated builds |
| **Portable** | Self-contained, minimal dependencies | Portable distribution |

### Profile Configuration

Profiles are defined in `build-profiles.json` with these key settings:

```json
{
  "production": {
    "optimization_level": 2,
    "console_mode": false,
    "upx_compression": true,
    "create_installer": true,
    "quality_gates": {
      "run_tests": true,
      "security_scan": true,
      "performance_test": true
    }
  }
}
```

## 📋 Pre-Build Validation

The `pre-build-validation.ps1` script performs comprehensive environment checks:

### Validation Categories

- **Python Environment**: Version, virtual environment, pip status
- **Dependencies**: Required packages, development tools
- **Project Structure**: Required files, directory layout
- **Code Quality**: Syntax checks, import validation, hardcoded paths
- **Configuration**: Environment files, config manager
- **Build Requirements**: Disk space, memory, system compatibility
- **Security**: Execution policies, sensitive data checks

### Usage Examples

```powershell
# Basic validation
.\scripts\pre-build-validation.ps1

# Strict mode with auto-fix
.\scripts\pre-build-validation.ps1 -Strict -FixIssues -Profile Production

# Generate HTML report
.\scripts\pre-build-validation.ps1 -OutputReport -ReportPath validation.html
```

## ✅ Post-Build Verification

The `post-build-verification.ps1` script validates built executables:

### Verification Tests

- **Executable Properties**: Size, version info, digital signatures
- **Functionality Tests**: Startup, dependency checks, memory usage
- **Security Validation**: DEP/ASLR support, security scanning
- **Compatibility**: Windows versions, architecture, .NET dependencies
- **Optimization**: UPX compression, artifact cleanup

### Usage Examples

```powershell
# Full verification with optimization
.\scripts\post-build-verification.ps1 -BuildProfile Production -OptimizeArtifacts -GenerateReport

# Compatibility testing
.\scripts\post-build-verification.ps1 -RunCompatibilityTests -GenerateReport
```

## 📦 Installer Creation

The `create-installer.ps1` script creates professional Windows installers:

### Supported Formats

- **NSIS**: Nullsoft Scriptable Install System
- **Inno Setup**: Feature-rich installer creator
- **Portable**: Self-extracting archives (7-Zip)

### Features

- Automatic script generation
- Version detection from executables
- Registry entries and uninstaller
- Start Menu and Desktop shortcuts
- File associations
- Windows version checking
- Installer testing

### Usage Examples

```powershell
# Create both NSIS and Inno Setup installers
.\scripts\create-installer.ps1 -InstallerType Both -TestInstaller

# Create portable installer only
.\scripts\create-installer.ps1 -CreatePortableInstaller -OutputDir "release"
```

## ⚙️ Build Profile Management

### Using the Profile Loader

```python
# List available profiles
python scripts/build-profile-loader.py list

# Show profile details
python scripts/build-profile-loader.py show --profile production

# Validate profile configuration
python scripts/build-profile-loader.py validate --profile production

# Generate PyInstaller spec
python scripts/build-profile-loader.py generate-spec --profile production --output main_prod.spec

# Generate build script
python scripts/build-profile-loader.py generate-script --profile production --script-type powershell
```

### Creating Custom Profiles

1. Edit `build-profiles.json`
2. Add your profile configuration
3. Validate with the profile loader
4. Test with the build scripts

Example custom profile:
```json
{
  "my-profile": {
    "name": "My Custom Profile",
    "description": "Custom build configuration",
    "pyinstaller_options": ["--onefile", "--console"],
    "optimization_level": 1,
    "console_mode": true,
    "output": {
      "executable_name": "MyApp.exe",
      "create_portable": true
    }
  }
}
```

## 🔄 CI/CD Integration

### GitHub Actions Workflows

The project includes two comprehensive GitHub Actions workflows:

1. **`build-and-release.yml`**: Complete build pipeline with testing, security scanning, and automated releases
2. **`quality-checks.yml`**: Code quality, security analysis, and documentation validation

### Workflow Features

- Multi-Python version testing
- Security vulnerability scanning
- Code quality analysis
- Automated installer creation
- GitHub release creation
- Artifact management
- Comprehensive reporting

### Triggering Builds

```yaml
# Manual workflow dispatch
on:
  workflow_dispatch:
    inputs:
      build_profile:
        description: 'Build profile to use'
        required: true
        default: 'production'
        type: choice
        options: [production, development, debug, testing, portable]

# Tag-based releases
on:
  push:
    tags: ['v*']
```

## 🛠️ Prerequisites

### Required Software

- **Python 3.8+**: Main runtime environment
- **Poetry or pip**: Dependency management
- **PyInstaller**: Executable creation
- **Git**: Version control (recommended)

### Optional Tools

- **NSIS**: Windows installer creation
- **Inno Setup**: Advanced installer creation
- **7-Zip**: Portable archive creation
- **UPX**: Executable compression
- **Windows SDK**: Advanced executable analysis

### PowerShell Requirements

- **PowerShell 5.1+**: Core scripting environment
- **Execution Policy**: `RemoteSigned` or `Unrestricted`

Set execution policy:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📊 Quality Gates

### Automated Checks

- **Code Coverage**: Minimum 70% (configurable)
- **Security Scan**: No high-severity vulnerabilities
- **Performance**: Maximum startup time and memory usage
- **Executable Size**: Profile-specific size limits
- **Dependencies**: All required packages present

### Configuration

Quality gates are defined in `build-profiles.json`:

```json
{
  "quality_gates": {
    "code_coverage": {
      "minimum_percentage": 70,
      "enforce": true
    },
    "security_scan": {
      "enabled": true,
      "fail_on_high": true
    },
    "performance": {
      "max_startup_time_seconds": 10,
      "max_memory_usage_mb": 256,
      "max_executable_size_mb": 50
    }
  }
}
```

## 🔍 Troubleshooting

### Common Issues

#### Build Failures
```powershell
# Check validation first
.\scripts\pre-build-validation.ps1 -Verbose

# Enable debug logging
.\scripts\Build-Advanced.ps1 -Profile Debug -Verbose
```

#### PyInstaller Issues
```powershell
# Clean build with fresh virtual environment
.\scripts\Build-Advanced.ps1 -Clean -Profile Development
```

#### Missing Dependencies
```powershell
# Auto-fix common issues
.\scripts\pre-build-validation.ps1 -FixIssues
```

#### Permission Issues
```powershell
# Run as administrator for installer creation
Start-Process PowerShell -Verb RunAs
```

### Debug Information

All scripts generate detailed logs:

- **Build logs**: `build-YYYYMMDD-HHMMSS.log`
- **Validation reports**: `validation-report.html`
- **Verification reports**: `verification-report.html`

### Environment Variables

Key environment variables for debugging:

- `VERBOSE=1`: Enable verbose output
- `DEBUG=1`: Enable debug mode
- `SKIP_TESTS=1`: Skip test execution
- `CLEAN_BUILD=1`: Force clean build

## 📈 Performance Optimization

### Build Speed

- Use incremental builds for development
- Skip tests during rapid iteration
- Use faster build profiles for development
- Enable parallel processing where possible

### Executable Size

- Use UPX compression for production builds
- Exclude unnecessary modules in profiles
- Use portable builds for size-sensitive deployments
- Monitor size trends with quality gates

### Memory Usage

- Profile memory usage during development
- Set appropriate limits in quality gates
- Use debug builds for memory analysis
- Monitor runtime memory consumption

## 🔒 Security Considerations

### Code Signing

For production releases, consider code signing:

```powershell
# Configure signing in build profiles
{
  "signing": {
    "enabled": true,
    "certificate_path": "path/to/cert.p12",
    "timestamp_server": "http://timestamp.digicert.com"
  }
}
```

### Security Scanning

Automated security checks include:

- **Bandit**: Python security linting
- **Safety**: Dependency vulnerability scanning
- **Windows Defender**: Malware detection
- **Hardcoded secrets**: Pattern detection

### Best Practices

- Never commit API keys or secrets
- Use environment variables for configuration
- Regularly update dependencies
- Review security scan results
- Enable Windows security features (DEP/ASLR)

## 📝 Customization

### Adding New Profiles

1. Define profile in `build-profiles.json`
2. Test with profile loader
3. Update documentation
4. Add to CI/CD workflows if needed

### Extending Scripts

- Follow existing patterns and conventions
- Add comprehensive error handling
- Include logging and progress reporting
- Document new parameters and features
- Test on multiple systems

### Integration Points

- GitHub Actions workflows
- Local development environments
- CI/CD pipelines
- Release automation
- Quality monitoring

## 📚 Additional Resources

### Documentation

- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [NSIS Documentation](https://nsis.sourceforge.io/Docs/)
- [Inno Setup Documentation](https://jrsoftware.org/ishelp/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

### Community

- [Project Issues](https://github.com/yourusername/unsplash-image-search-gpt/issues)
- [Project Discussions](https://github.com/yourusername/unsplash-image-search-gpt/discussions)
- [Contributing Guide](../CONTRIBUTING.md)

---

*This build system is designed for professional software development with comprehensive automation, validation, and quality assurance. Customize and extend as needed for your specific requirements.*