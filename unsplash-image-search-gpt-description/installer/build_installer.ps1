# PowerShell Build Script for Unsplash Image Search GPT Description Installer
# This script provides more advanced build options and cross-platform compatibility

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("x86", "x64", "both")]
    [string]$Architecture = "both",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("development", "testing", "production")]
    [string]$Configuration = "production",
    
    [Parameter(Mandatory=$false)]
    [string]$Version = "1.0.0",
    
    [Parameter(Mandatory=$false)]
    [switch]$CreateMSI = $true,
    
    [Parameter(Mandatory=$false)]
    [switch]$SignInstaller = $false,
    
    [Parameter(Mandatory=$false)]
    [string]$CertificatePath = "",
    
    [Parameter(Mandatory=$false)]
    [string]$CertificatePassword = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$CreatePortable = $true,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipValidation = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose = $false
)

# Script configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

if ($Verbose) {
    $VerbosePreference = "Continue"
}

# Paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$OutputDir = Join-Path $ScriptDir "output"
$AssetsDir = Join-Path $ScriptDir "assets"
$DistDir = Join-Path $ProjectRoot "dist"

# Application information
$AppName = "Unsplash Image Search GPT Description"
$AppPublisher = "Image Search Tools"
$AppUrl = "https://github.com/your-username/unsplash-image-search-gpt-description"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Unsplash Image Search Installer Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Version: $Version" -ForegroundColor Yellow
Write-Host "Architecture: $Architecture" -ForegroundColor Yellow
Write-Host "Configuration: $Configuration" -ForegroundColor Yellow
Write-Host ""

# Function to check prerequisites
function Test-Prerequisites {
    Write-Host "Checking prerequisites..." -ForegroundColor Green
    
    $issues = @()
    
    # Check for Inno Setup
    $innoPath = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
    
    if (-not $innoPath) {
        $issues += "Inno Setup 6.2 or later is required. Download from https://jrsoftware.org/isinfo.php"
    } else {
        Write-Verbose "Found Inno Setup: $innoPath"
        $script:InnoSetupPath = $innoPath
    }
    
    # Check for built application
    $exePath = Join-Path $DistDir "unsplash-image-search.exe"
    if (-not (Test-Path $exePath)) {
        $issues += "Application not found at $exePath. Please build the application first using PyInstaller."
    }
    
    # Check for WiX Toolset if MSI creation is requested
    if ($CreateMSI) {
        $candlePath = Get-Command "candle.exe" -ErrorAction SilentlyContinue
        if (-not $candlePath) {
            Write-Warning "WiX Toolset not found. MSI creation will be skipped."
            $script:CreateMSI = $false
        } else {
            Write-Verbose "Found WiX Toolset: $($candlePath.Source)"
        }
    }
    
    # Check for code signing certificate
    if ($SignInstaller) {
        if (-not (Test-Path $CertificatePath)) {
            $issues += "Certificate file not found: $CertificatePath"
        }
    }
    
    if ($issues.Count -gt 0) {
        Write-Host "Prerequisites check failed:" -ForegroundColor Red
        $issues | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
        throw "Prerequisites not met"
    }
    
    Write-Host "Prerequisites check passed!" -ForegroundColor Green
}

# Function to prepare build environment
function Initialize-BuildEnvironment {
    Write-Host "Initializing build environment..." -ForegroundColor Green
    
    # Create output directory
    if (Test-Path $OutputDir) {
        Remove-Item $OutputDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
    
    # Create assets directory if missing
    if (-not (Test-Path $AssetsDir)) {
        New-Item -ItemType Directory -Path $AssetsDir | Out-Null
        Write-Warning "Assets directory created. Please add the required image files."
    }
    
    # Check for asset files and create defaults if missing
    $assetFiles = @(
        @{ Name = "app_icon.ico"; Size = "256x256"; Description = "Application icon" },
        @{ Name = "wizard_left.bmp"; Size = "164x314"; Description = "Wizard side banner" },
        @{ Name = "wizard_small.bmp"; Size = "55x58"; Description = "Wizard header icon" },
        @{ Name = "uninstall_banner.bmp"; Size = "164x314"; Description = "Uninstaller banner" }
    )
    
    $missingAssets = @()
    foreach ($asset in $assetFiles) {
        $assetPath = Join-Path $AssetsDir $asset.Name
        if (-not (Test-Path $assetPath)) {
            $missingAssets += $asset
            # Create placeholder file
            New-Item -ItemType File -Path $assetPath -Force | Out-Null
        }
    }
    
    if ($missingAssets.Count -gt 0) {
        Write-Warning "Missing asset files (placeholders created):"
        $missingAssets | ForEach-Object {
            Write-Host "  - $($_.Name) ($($_.Size)) - $($_.Description)" -ForegroundColor Yellow
        }
    }
    
    Write-Host "Build environment initialized!" -ForegroundColor Green
}

# Function to build installer with specific configuration
function Build-Installer {
    param(
        [string]$Arch,
        [string]$Config
    )
    
    Write-Host "Building installer for $Arch architecture..." -ForegroundColor Green
    
    $issFile = Join-Path $ScriptDir "installer_enhanced.iss"
    $outputName = "unsplash-image-search-setup-$Version-$Arch"
    
    # Prepare Inno Setup parameters
    $innoParams = @(
        $issFile,
        "/O`"$OutputDir`"",
        "/F`"$outputName`"",
        "/DMyAppVersion=$Version",
        "/DMyAppArchitecture=$Arch",
        "/DMyAppConfiguration=$Config"
    )
    
    if (-not $Verbose) {
        $innoParams += "/Q"
    }
    
    Write-Verbose "Inno Setup command: `"$InnoSetupPath`" $($innoParams -join ' ')"
    
    # Execute Inno Setup
    $process = Start-Process -FilePath $InnoSetupPath -ArgumentList $innoParams -Wait -PassThru -NoNewWindow
    
    if ($process.ExitCode -ne 0) {
        throw "Inno Setup failed with exit code $($process.ExitCode)"
    }
    
    $installerPath = Join-Path $OutputDir "$outputName.exe"
    if (Test-Path $installerPath) {
        Write-Host "Installer created successfully: $outputName.exe" -ForegroundColor Green
        return $installerPath
    } else {
        throw "Installer file not found after build"
    }
}

# Function to sign installer
function Set-InstallerSignature {
    param([string]$InstallerPath)
    
    if (-not $SignInstaller) {
        return
    }
    
    Write-Host "Signing installer..." -ForegroundColor Green
    
    $signtoolPath = Get-Command "signtool.exe" -ErrorAction SilentlyContinue
    if (-not $signtoolPath) {
        Write-Warning "SignTool not found. Installer will not be signed."
        return
    }
    
    $signParams = @(
        "sign",
        "/f", "`"$CertificatePath`"",
        "/p", $CertificatePassword,
        "/t", "http://timestamp.digicert.com",
        "/d", "`"$AppName Installer`"",
        "/du", "`"$AppUrl`"",
        "`"$InstallerPath`""
    )
    
    $process = Start-Process -FilePath $signtoolPath.Source -ArgumentList $signParams -Wait -PassThru -NoNewWindow
    
    if ($process.ExitCode -eq 0) {
        Write-Host "Installer signed successfully!" -ForegroundColor Green
    } else {
        Write-Warning "Failed to sign installer (exit code: $($process.ExitCode))"
    }
}

# Function to create MSI wrapper
function New-MSIWrapper {
    param([string]$InstallerPath)
    
    if (-not $CreateMSI) {
        return
    }
    
    Write-Host "Creating MSI wrapper..." -ForegroundColor Green
    
    $msiPath = [System.IO.Path]::ChangeExtension($InstallerPath, ".msi")
    $createMsiScript = Join-Path $ScriptDir "tools\create_msi.ps1"
    
    if (-not (Test-Path $createMsiScript)) {
        Write-Warning "MSI creation script not found. Skipping MSI creation."
        return
    }
    
    try {
        & $createMsiScript -InputExe $InstallerPath -OutputMsi $msiPath -ProductVersion $Version
        Write-Host "MSI wrapper created successfully!" -ForegroundColor Green
    } catch {
        Write-Warning "Failed to create MSI wrapper: $($_.Exception.Message)"
    }
}

# Function to create portable package
function New-PortablePackage {
    if (-not $CreatePortable) {
        return
    }
    
    Write-Host "Creating portable package..." -ForegroundColor Green
    
    $portableDir = Join-Path $OutputDir "Portable"
    $portableArchive = Join-Path $OutputDir "unsplash-image-search-portable-$Version.zip"
    
    if (Test-Path $portableDir) {
        Remove-Item $portableDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $portableDir | Out-Null
    
    # Copy application files
    Copy-Item "$DistDir\*" $portableDir -Recurse
    
    # Create portable configuration
    $portableIni = Join-Path $portableDir "portable.ini"
    $portableConfig = @"
[Portable]
Enabled=true
DataPath=.\Data
ConfigPath=.\Config

[Settings]
FirstRun=true
UseRelativePaths=true
"@
    Set-Content -Path $portableIni -Value $portableConfig
    
    # Create data directories
    $dataDir = Join-Path $portableDir "Data"
    New-Item -ItemType Directory -Path $dataDir | Out-Null
    @("sessions", "cache", "exports", "vocabulary", "logs") | ForEach-Object {
        New-Item -ItemType Directory -Path (Join-Path $dataDir $_) | Out-Null
    }
    
    # Create README for portable version
    $readmePath = Join-Path $portableDir "README_PORTABLE.txt"
    $readmeContent = @"
$AppName - Portable Version
========================================

This is a portable version of $AppName that doesn't require installation.
Simply extract to any folder and run unsplash-image-search.exe.

Features:
- No installation required
- No registry entries
- All data stored in application folder
- Can run from USB drive or network share

Directory Structure:
- unsplash-image-search.exe  - Main application
- portable.ini               - Portable configuration
- Data\                      - User data directory
  - sessions\                - Saved sessions
  - cache\                   - Image cache
  - exports\                 - Exported files
  - vocabulary\              - Vocabulary lists
  - logs\                    - Application logs

Configuration:
1. Edit config.ini to add your API keys
2. Customize settings through the application interface
3. All settings are saved relative to the application folder

System Requirements:
- Windows 7 SP1 or later
- .NET Framework 4.8
- Internet connection for API access

For more information, visit: $AppUrl
"@
    Set-Content -Path $readmePath -Value $readmeContent
    
    # Create ZIP archive
    try {
        Compress-Archive -Path "$portableDir\*" -DestinationPath $portableArchive -CompressionLevel Optimal
        Write-Host "Portable package created: $(Split-Path $portableArchive -Leaf)" -ForegroundColor Green
    } catch {
        Write-Warning "Failed to create portable archive: $($_.Exception.Message)"
    }
}

# Function to validate installers
function Test-Installers {
    if ($SkipValidation) {
        return
    }
    
    Write-Host "Validating installers..." -ForegroundColor Green
    
    $installers = Get-ChildItem $OutputDir -Filter "*.exe" | Where-Object { $_.Name -match "setup" }
    
    foreach ($installer in $installers) {
        Write-Host "Validating $($installer.Name)..." -ForegroundColor Yellow
        
        # Check file size
        $sizeMB = [math]::Round($installer.Length / 1MB, 2)
        if ($sizeMB -lt 10) {
            Write-Warning "$($installer.Name) seems too small ($sizeMB MB)"
        } elseif ($sizeMB -gt 500) {
            Write-Warning "$($installer.Name) seems too large ($sizeMB MB)"
        } else {
            Write-Verbose "$($installer.Name) size check passed ($sizeMB MB)"
        }
        
        # Check if file is executable
        try {
            $fileInfo = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($installer.FullName)
            if ($fileInfo.ProductName -ne $AppName) {
                Write-Warning "$($installer.Name) has incorrect product name: $($fileInfo.ProductName)"
            }
        } catch {
            Write-Warning "Could not read version info from $($installer.Name)"
        }
    }
    
    Write-Host "Installer validation completed!" -ForegroundColor Green
}

# Function to create deployment package
function New-DeploymentPackage {
    Write-Host "Creating deployment package..." -ForegroundColor Green
    
    $deploymentDir = Join-Path $OutputDir "Deployment"
    if (Test-Path $deploymentDir) {
        Remove-Item $deploymentDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $deploymentDir | Out-Null
    
    # Copy all installers and packages
    Get-ChildItem $OutputDir -Include "*.exe", "*.msi", "*.zip" | ForEach-Object {
        Copy-Item $_.FullName $deploymentDir
    }
    
    # Copy configuration files
    $configDir = Join-Path $deploymentDir "Config"
    New-Item -ItemType Directory -Path $configDir | Out-Null
    Copy-Item (Join-Path $ScriptDir "config\*") $configDir -Recurse
    
    # Copy documentation
    $docsSource = Join-Path $ProjectRoot "README.md"
    if (Test-Path $docsSource) {
        Copy-Item $docsSource (Join-Path $deploymentDir "README.txt")
    }
    
    $licenseSource = Join-Path $ProjectRoot "LICENSE"
    if (Test-Path $licenseSource) {
        Copy-Item $licenseSource (Join-Path $deploymentDir "LICENSE.txt")
    }
    
    # Create deployment guide
    $deploymentGuide = Join-Path $deploymentDir "DEPLOYMENT_GUIDE.md"
    $guideContent = @"
# Deployment Guide for $AppName v$Version

## Package Contents

This deployment package contains the following components:

### Installers
- **Standard Installer** (`.exe`): Interactive installer with full UI
- **MSI Package** (`.msi`): Enterprise deployment package for Group Policy/SCCM
- **Portable Package** (`.zip`): No-installation portable version

### Configuration Files
- **Config/silent_install.xml**: Silent installation configuration
- **Config/enterprise_config.json**: Enterprise settings and policies

## Deployment Methods

### 1. Interactive Installation
For end users who can install software interactively:
``````bash
unsplash-image-search-setup-$Version.exe
``````

### 2. Silent Installation
For automated deployment without user interaction:
``````bash
unsplash-image-search-setup-$Version.exe /VERYSILENT /NORESTART
``````

With custom configuration:
``````bash
unsplash-image-search-setup-$Version.exe /VERYSILENT /CONFIG="Config\silent_install.xml"
``````

### 3. Enterprise Deployment (MSI)
Using Group Policy or SCCM:
``````bash
msiexec /i unsplash-image-search-$Version.msi /quiet /norestart
``````

With logging:
``````bash
msiexec /i unsplash-image-search-$Version.msi /quiet /norestart /l*v install.log
``````

### 4. Portable Deployment
Extract the portable ZIP to any location and run the executable.

## System Requirements
- Windows 7 SP1 or later (Windows 10/11 recommended)
- .NET Framework 4.8 (automatically installed if missing)
- Visual C++ Redistributable 2019 (automatically installed if missing)
- 100 MB free disk space
- Internet connection for API access

## Configuration
1. Edit the configuration files in the `Config` directory
2. Distribute with your preferred deployment method
3. API keys can be configured during installation or afterwards

## Support
For technical support and documentation, visit: $AppUrl
"@
    
    Set-Content -Path $deploymentGuide -Value $guideContent
    
    # Create final distribution archive
    $finalArchive = Join-Path $OutputDir "unsplash-image-search-distribution-$Version.zip"
    try {
        Compress-Archive -Path "$deploymentDir\*" -DestinationPath $finalArchive -CompressionLevel Optimal
        Write-Host "Distribution package created: $(Split-Path $finalArchive -Leaf)" -ForegroundColor Green
    } catch {
        Write-Warning "Failed to create distribution archive: $($_.Exception.Message)"
    }
}

# Function to display build summary
function Show-BuildSummary {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Build Summary" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    $files = Get-ChildItem $OutputDir -Include "*.exe", "*.msi", "*.zip" -Recurse
    
    if ($files.Count -eq 0) {
        Write-Host "No output files found!" -ForegroundColor Red
        return
    }
    
    Write-Host ""
    Write-Host "Generated Files:" -ForegroundColor Green
    $totalSize = 0
    
    foreach ($file in $files) {
        $sizeMB = [math]::Round($file.Length / 1MB, 2)
        $totalSize += $file.Length
        $type = switch ($file.Extension) {
            ".exe" { "Installer" }
            ".msi" { "MSI Package" }
            ".zip" { "Archive" }
            default { "Unknown" }
        }
        Write-Host "  $type`: $($file.Name) ($sizeMB MB)" -ForegroundColor White
    }
    
    $totalSizeMB = [math]::Round($totalSize / 1MB, 2)
    Write-Host ""
    Write-Host "Total size: $totalSizeMB MB" -ForegroundColor Yellow
    Write-Host "Output directory: $OutputDir" -ForegroundColor Yellow
    
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Green
    Write-Host "1. Test installers on clean systems" -ForegroundColor White
    Write-Host "2. Update configuration files for your environment" -ForegroundColor White
    Write-Host "3. Deploy using your preferred method" -ForegroundColor White
    Write-Host ""
    Write-Host "Build completed successfully!" -ForegroundColor Green
}

# Main execution
try {
    Test-Prerequisites
    Initialize-BuildEnvironment
    
    $builtInstallers = @()
    
    if ($Architecture -eq "both") {
        $architectures = @("x86", "x64")
    } else {
        $architectures = @($Architecture)
    }
    
    foreach ($arch in $architectures) {
        $installerPath = Build-Installer -Arch $arch -Config $Configuration
        Set-InstallerSignature -InstallerPath $installerPath
        New-MSIWrapper -InstallerPath $installerPath
        $builtInstallers += $installerPath
    }
    
    New-PortablePackage
    Test-Installers
    New-DeploymentPackage
    Show-BuildSummary
    
    # Open output directory
    if ($IsWindows -or $PSVersionTable.PSVersion.Major -lt 6) {
        Start-Process -FilePath "explorer.exe" -ArgumentList $OutputDir
    }
    
} catch {
    Write-Host ""
    Write-Host "Build failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    if ($Verbose) {
        Write-Host "Stack trace:" -ForegroundColor Red
        Write-Host $_.ScriptStackTrace -ForegroundColor Red
    }
    exit 1
}