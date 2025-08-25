#Requires -Version 5.1

<#
.SYNOPSIS
    Advanced PowerShell Build Script for Unsplash Image Search & GPT Tool

.DESCRIPTION
    Comprehensive build automation with Git integration, versioning, and GitHub release preparation.
    Supports multiple build profiles, automatic version detection, and advanced features.

.PARAMETER Profile
    Build profile: Development, Production, Debug (default: Production)

.PARAMETER Clean
    Perform clean build by removing previous build artifacts

.PARAMETER SkipTests
    Skip running tests before building

.PARAMETER Version
    Override version detection (format: x.y.z)

.PARAMETER CreateInstaller
    Create installer after building executable

.PARAMETER UploadArtifacts
    Prepare artifacts for GitHub release upload

.PARAMETER Compress
    Create compressed archive of build artifacts

.PARAMETER Verbose
    Enable detailed logging

.EXAMPLE
    .\Build-Advanced.ps1 -Profile Production -Clean -CreateInstaller

.EXAMPLE
    .\Build-Advanced.ps1 -Profile Debug -SkipTests -Verbose

.NOTES
    Author: Build Automation System
    Version: 2.0.0
    Requires: PowerShell 5.1+, Python 3.8+, Git
#>

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet('Development', 'Production', 'Debug')]
    [string]$Profile = 'Production',
    
    [Parameter()]
    [switch]$Clean,
    
    [Parameter()]
    [switch]$SkipTests,
    
    [Parameter()]
    [string]$Version,
    
    [Parameter()]
    [switch]$CreateInstaller,
    
    [Parameter()]
    [switch]$UploadArtifacts,
    
    [Parameter()]
    [switch]$Compress,
    
    [Parameter()]
    [switch]$Verbose
)

# Set error action preference
$ErrorActionPreference = 'Stop'

# Initialize build configuration
$BuildConfig = @{
    ProjectRoot = Split-Path -Parent $PSScriptRoot
    BuildDir = $null
    DistDir = $null
    LogFile = $null
    StartTime = Get-Date
    ErrorCount = 0
    Warnings = @()
    GitInfo = @{}
    VersionInfo = @{}
    BuildArtifacts = @()
}

# Initialize paths
$BuildConfig.BuildDir = Join-Path $BuildConfig.ProjectRoot 'build'
$BuildConfig.DistDir = Join-Path $BuildConfig.ProjectRoot 'dist'
$BuildConfig.LogFile = Join-Path $BuildConfig.ProjectRoot "build-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

# Configure logging
function Write-BuildLog {
    param(
        [string]$Message,
        [ValidateSet('INFO', 'WARNING', 'ERROR', 'SUCCESS')]
        [string]$Level = 'INFO',
        [switch]$NoConsole
    )
    
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # Write to log file
    Add-Content -Path $BuildConfig.LogFile -Value $logEntry -Encoding UTF8
    
    # Write to console unless suppressed
    if (-not $NoConsole) {
        switch ($Level) {
            'ERROR' { Write-Host $logEntry -ForegroundColor Red }
            'WARNING' { Write-Host $logEntry -ForegroundColor Yellow }
            'SUCCESS' { Write-Host $logEntry -ForegroundColor Green }
            'INFO' { Write-Host $logEntry -ForegroundColor White }
        }
    }
}

function Test-Requirement {
    param(
        [string]$Name,
        [scriptblock]$Test,
        [string]$ErrorMessage
    )
    
    Write-BuildLog "Checking requirement: $Name"
    
    try {
        $result = & $Test
        if ($result) {
            Write-BuildLog "$Name - OK" -Level SUCCESS
            return $true
        } else {
            Write-BuildLog "$Name - FAILED: $ErrorMessage" -Level ERROR
            $BuildConfig.ErrorCount++
            return $false
        }
    }
    catch {
        Write-BuildLog "$Name - FAILED: $($_.Exception.Message)" -Level ERROR
        $BuildConfig.ErrorCount++
        return $false
    }
}

function Get-GitInformation {
    Write-BuildLog "Gathering Git information..."
    
    try {
        # Check if we're in a Git repository
        $gitStatus = git status --porcelain 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-BuildLog "Not a Git repository or Git not available" -Level WARNING
            return @{
                IsGitRepo = $false
                Branch = 'unknown'
                Commit = 'unknown'
                Tag = 'unknown'
                IsDirty = $false
            }
        }
        
        $BuildConfig.GitInfo = @{
            IsGitRepo = $true
            Branch = (git rev-parse --abbrev-ref HEAD).Trim()
            Commit = (git rev-parse HEAD).Trim()
            CommitShort = (git rev-parse --short HEAD).Trim()
            Tag = (git describe --tags --exact-match HEAD 2>$null) ?? 'no-tag'
            IsDirty = [bool]$gitStatus
            RemoteUrl = (git config --get remote.origin.url 2>$null) ?? 'no-remote'
        }
        
        Write-BuildLog "Git Branch: $($BuildConfig.GitInfo.Branch)"
        Write-BuildLog "Git Commit: $($BuildConfig.GitInfo.CommitShort)"
        Write-BuildLog "Git Tag: $($BuildConfig.GitInfo.Tag)"
        Write-BuildLog "Working Directory Clean: $(-not $BuildConfig.GitInfo.IsDirty)"
        
    }
    catch {
        Write-BuildLog "Error gathering Git information: $($_.Exception.Message)" -Level WARNING
        $BuildConfig.GitInfo.IsGitRepo = $false
    }
}

function Get-VersionInformation {
    Write-BuildLog "Determining version information..."
    
    # Priority order: Parameter -> Git tag -> version_info.py -> pyproject.toml -> fallback
    
    if ($Version) {
        $BuildConfig.VersionInfo.Version = $Version
        $BuildConfig.VersionInfo.Source = 'parameter'
        Write-BuildLog "Using version from parameter: $Version"
    }
    elseif ($BuildConfig.GitInfo.IsGitRepo -and $BuildConfig.GitInfo.Tag -ne 'no-tag') {
        # Extract version from Git tag (e.g., v1.2.3 -> 1.2.3)
        $tagVersion = $BuildConfig.GitInfo.Tag -replace '^v', ''
        if ($tagVersion -match '^\d+\.\d+\.\d+') {
            $BuildConfig.VersionInfo.Version = $tagVersion
            $BuildConfig.VersionInfo.Source = 'git-tag'
            Write-BuildLog "Using version from Git tag: $tagVersion"
        }
    }
    
    if (-not $BuildConfig.VersionInfo.Version) {
        # Try to get version from version_info.py
        $versionFile = Join-Path $BuildConfig.ProjectRoot 'version_info.py'
        if (Test-Path $versionFile) {
            try {
                $versionContent = Get-Content $versionFile -Raw
                if ($versionContent -match 'APP_VERSION\s*=\s*["\']([^"\']+)["\']') {
                    $BuildConfig.VersionInfo.Version = $matches[1]
                    $BuildConfig.VersionInfo.Source = 'version_info.py'
                    Write-BuildLog "Using version from version_info.py: $($matches[1])"
                }
            }
            catch {
                Write-BuildLog "Error reading version_info.py: $($_.Exception.Message)" -Level WARNING
            }
        }
    }
    
    if (-not $BuildConfig.VersionInfo.Version) {
        # Try pyproject.toml
        $pyprojectFile = Join-Path $BuildConfig.ProjectRoot 'pyproject.toml'
        if (Test-Path $pyprojectFile) {
            try {
                $pyprojectContent = Get-Content $pyprojectFile -Raw
                if ($pyprojectContent -match 'version\s*=\s*["\']([^"\']+)["\']') {
                    $BuildConfig.VersionInfo.Version = $matches[1]
                    $BuildConfig.VersionInfo.Source = 'pyproject.toml'
                    Write-BuildLog "Using version from pyproject.toml: $($matches[1])"
                }
            }
            catch {
                Write-BuildLog "Error reading pyproject.toml: $($_.Exception.Message)" -Level WARNING
            }
        }
    }
    
    # Fallback version
    if (-not $BuildConfig.VersionInfo.Version) {
        $BuildConfig.VersionInfo.Version = '1.0.0'
        $BuildConfig.VersionInfo.Source = 'fallback'
        Write-BuildLog "Using fallback version: 1.0.0" -Level WARNING
    }
    
    # Generate build number
    $buildNumber = Get-Date -Format 'yyyyMMdd'
    if ($BuildConfig.GitInfo.IsGitRepo) {
        $buildNumber += "-$($BuildConfig.GitInfo.CommitShort)"
    }
    
    $BuildConfig.VersionInfo.BuildNumber = $buildNumber
    $BuildConfig.VersionInfo.FullVersion = "$($BuildConfig.VersionInfo.Version)+$buildNumber"
}

function Invoke-PreBuildValidation {
    Write-BuildLog "=== PRE-BUILD VALIDATION ===" -Level INFO
    
    # Check Python
    $pythonOK = Test-Requirement -Name "Python 3.8+" -Test {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $pythonVersion -match 'Python (\d+)\.(\d+)') {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            return ($major -gt 3) -or ($major -eq 3 -and $minor -ge 8)
        }
        return $false
    } -ErrorMessage "Python 3.8 or higher is required"
    
    # Check Git (optional but recommended)
    Test-Requirement -Name "Git" -Test {
        git --version 2>$null
        return $LASTEXITCODE -eq 0
    } -ErrorMessage "Git is recommended for version management"
    
    # Check required files
    $requiredFiles = @('main.py', 'version_info.py', 'pyproject.toml')
    foreach ($file in $requiredFiles) {
        Test-Requirement -Name "File: $file" -Test {
            return Test-Path (Join-Path $BuildConfig.ProjectRoot $file)
        } -ErrorMessage "Required file $file not found"
    }
    
    # Check virtual environment
    $venvPath = Join-Path $BuildConfig.ProjectRoot 'venv'
    if (-not (Test-Path $venvPath)) {
        Write-BuildLog "Creating Python virtual environment..." -Level INFO
        python -m venv $venvPath
        if ($LASTEXITCODE -ne 0) {
            Write-BuildLog "Failed to create virtual environment" -Level ERROR
            $BuildConfig.ErrorCount++
            return
        }
    }
    
    # Activate virtual environment
    $activateScript = Join-Path $venvPath 'Scripts\Activate.ps1'
    if (Test-Path $activateScript) {
        Write-BuildLog "Activating virtual environment..."
        & $activateScript
    } else {
        Write-BuildLog "Virtual environment activation script not found" -Level WARNING
    }
    
    # Check for hardcoded paths
    Write-BuildLog "Scanning for potential hardcoded paths..."
    $pythonFiles = Get-ChildItem -Path $BuildConfig.ProjectRoot -Filter "*.py" -Recurse | Where-Object { $_.Name -notlike "*test*" }
    $hardcodedPaths = @()
    
    foreach ($file in $pythonFiles) {
        $content = Get-Content $file.FullName -Raw
        if ($content -match '[C-Z]:\\') {
            $hardcodedPaths += $file.Name
        }
    }
    
    if ($hardcodedPaths.Count -gt 0) {
        Write-BuildLog "Potential hardcoded paths found in: $($hardcodedPaths -join ', ')" -Level WARNING
        $BuildConfig.Warnings += "Hardcoded paths detected"
    }
    
    if ($BuildConfig.ErrorCount -gt 0) {
        throw "Pre-build validation failed with $($BuildConfig.ErrorCount) errors"
    }
}

function Install-Dependencies {
    Write-BuildLog "=== DEPENDENCY INSTALLATION ===" -Level INFO
    
    # Update pip
    Write-BuildLog "Updating pip..."
    python -m pip install --upgrade pip --quiet
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to update pip"
    }
    
    # Install dependencies based on available files
    if (Test-Path (Join-Path $BuildConfig.ProjectRoot 'pyproject.toml')) {
        Write-BuildLog "Installing Poetry dependencies..."
        pip install poetry --quiet
        poetry install --quiet
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install Poetry dependencies"
        }
    }
    elseif (Test-Path (Join-Path $BuildConfig.ProjectRoot 'requirements.txt')) {
        Write-BuildLog "Installing pip dependencies..."
        pip install -r requirements.txt --quiet
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install pip dependencies"
        }
    }
    
    # Install PyInstaller
    Write-BuildLog "Installing PyInstaller..."
    pip install pyinstaller --quiet
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install PyInstaller"
    }
}

function Invoke-CleanBuild {
    if ($Clean) {
        Write-BuildLog "=== CLEANING PREVIOUS BUILDS ===" -Level INFO
        
        @($BuildConfig.BuildDir, $BuildConfig.DistDir) | ForEach-Object {
            if (Test-Path $_) {
                Write-BuildLog "Removing directory: $_"
                Remove-Item $_ -Recurse -Force
            }
        }
        
        # Clean Python cache
        Get-ChildItem -Path $BuildConfig.ProjectRoot -Name "__pycache__" -Recurse | ForEach-Object {
            $cachePath = Join-Path $BuildConfig.ProjectRoot $_
            Write-BuildLog "Removing Python cache: $cachePath"
            Remove-Item $cachePath -Recurse -Force -ErrorAction SilentlyContinue
        }
        
        # Clean .pyc files
        Get-ChildItem -Path $BuildConfig.ProjectRoot -Filter "*.pyc" -Recurse | Remove-Item -Force -ErrorAction SilentlyContinue
    }
    
    # Ensure directories exist
    @($BuildConfig.BuildDir, $BuildConfig.DistDir) | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -Path $_ -ItemType Directory -Force | Out-Null
        }
    }
}

function Invoke-Tests {
    if ($SkipTests) {
        Write-BuildLog "Skipping tests (--SkipTests specified)" -Level WARNING
        return
    }
    
    Write-BuildLog "=== RUNNING TESTS ===" -Level INFO
    
    # Check for pytest
    $pytestAvailable = $false
    try {
        python -m pytest --version 2>$null | Out-Null
        $pytestAvailable = ($LASTEXITCODE -eq 0)
    }
    catch {
        $pytestAvailable = $false
    }
    
    if ($pytestAvailable) {
        Write-BuildLog "Running tests with pytest..."
        python -m pytest tests/ -v --tb=short 2>&1 | Tee-Object -FilePath $BuildConfig.LogFile -Append
        if ($LASTEXITCODE -ne 0) {
            throw "Tests failed"
        }
        Write-BuildLog "All tests passed!" -Level SUCCESS
    }
    elseif (Test-Path (Join-Path $BuildConfig.ProjectRoot 'run_tests.py')) {
        Write-BuildLog "Running basic test runner..."
        python run_tests.py 2>&1 | Tee-Object -FilePath $BuildConfig.LogFile -Append
        if ($LASTEXITCODE -ne 0) {
            throw "Tests failed"
        }
    }
    else {
        Write-BuildLog "No test framework found, skipping tests" -Level WARNING
    }
}

function Invoke-CodeQualityChecks {
    Write-BuildLog "=== CODE QUALITY CHECKS ===" -Level INFO
    
    # Basic syntax check
    Write-BuildLog "Checking Python syntax..."
    python -m py_compile main.py
    if ($LASTEXITCODE -ne 0) {
        throw "Syntax errors found in main.py"
    }
    
    # Check imports
    Write-BuildLog "Checking imports..."
    python -c "import main" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-BuildLog "Import check failed - may indicate missing dependencies" -Level WARNING
    }
}

function New-VersionFile {
    Write-BuildLog "=== GENERATING VERSION INFO ===" -Level INFO
    
    Write-BuildLog "Creating version file..."
    python version_info.py 2>&1 | Tee-Object -FilePath $BuildConfig.LogFile -Append
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create version file"
    }
}

function Invoke-BuildExecutable {
    Write-BuildLog "=== BUILDING EXECUTABLE ===" -Level INFO
    
    # Set PyInstaller options based on profile
    $pyinstallerOpts = @('--noconfirm', '--log-level', 'WARN')
    $specFile = 'main.spec'
    
    switch ($Profile) {
        'Development' {
            Write-BuildLog "Building development version..."
            $pyinstallerOpts += @('--console', '--debug=bootloader')
            $specFile = 'main_dev.spec'
        }
        'Debug' {
            Write-BuildLog "Building debug version..."
            $pyinstallerOpts += @('--console', '--debug=all')
            $specFile = 'main_debug.spec'
        }
        'Production' {
            Write-BuildLog "Building production version..."
            $pyinstallerOpts += @('--windowed', '--optimize=2')
            # Use existing main.spec
        }
    }
    
    # Check if spec file exists
    $specPath = Join-Path $BuildConfig.ProjectRoot $specFile
    if (-not (Test-Path $specPath)) {
        if ($Profile -ne 'Production') {
            Write-BuildLog "Generating spec file for $Profile profile..."
            # Generate basic spec file for non-production builds
            $tempName = "Unsplash_GPT_Tool_$Profile"
            pyinstaller --onefile main.py --name=$tempName --distpath=dist --workpath=build --specpath=. 2>&1 | Tee-Object -FilePath $BuildConfig.LogFile -Append
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to generate spec file"
            }
            Move-Item "$tempName.spec" $specPath
        } else {
            throw "Production spec file main.spec not found"
        }
    }
    
    # Build the executable
    Write-BuildLog "Running PyInstaller with spec file: $specFile"
    pyinstaller $pyinstallerOpts $specPath 2>&1 | Tee-Object -FilePath $BuildConfig.LogFile -Append
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed"
    }
}

function Invoke-PostBuildVerification {
    Write-BuildLog "=== POST-BUILD VERIFICATION ===" -Level INFO
    
    # Find executable
    $executable = Get-ChildItem -Path $BuildConfig.DistDir -Filter "*.exe" | Select-Object -First 1
    if (-not $executable) {
        throw "No executable found in dist directory"
    }
    
    $BuildConfig.BuildArtifacts += @{
        Type = 'Executable'
        Path = $executable.FullName
        Name = $executable.Name
        Size = $executable.Length
    }
    
    $fileSizeMB = [Math]::Round($executable.Length / 1MB, 2)
    Write-BuildLog "Executable created: $($executable.Name)" -Level SUCCESS
    Write-BuildLog "Executable size: $fileSizeMB MB"
    
    # Generate checksums
    Write-BuildLog "Generating checksums..."
    $sha256 = Get-FileHash -Path $executable.FullName -Algorithm SHA256
    $checksumFile = "$($executable.FullName).sha256"
    "$($sha256.Hash.ToLower())  $($executable.Name)" | Out-File -FilePath $checksumFile -Encoding ASCII
    
    $BuildConfig.BuildArtifacts += @{
        Type = 'Checksum'
        Path = $checksumFile
        Name = "$($executable.Name).sha256"
        Size = (Get-Item $checksumFile).Length
    }
    
    Write-BuildLog "SHA256 checksum generated"
    
    # Test executable (basic check)
    if ($Profile -ne 'Production') {
        Write-BuildLog "Testing executable..."
        try {
            $testProcess = Start-Process -FilePath $executable.FullName -ArgumentList "--help" -Wait -PassThru -WindowStyle Hidden
            if ($testProcess.ExitCode -eq 0 -or $testProcess.ExitCode -eq 1) { # 1 might be normal for help
                Write-BuildLog "Executable test passed" -Level SUCCESS
            }
        }
        catch {
            Write-BuildLog "Executable test failed: $($_.Exception.Message)" -Level WARNING
        }
    }
}

function New-PortableVersion {
    Write-BuildLog "=== CREATING PORTABLE VERSION ===" -Level INFO
    
    $portableDir = Join-Path $BuildConfig.DistDir 'Portable'
    if (-not (Test-Path $portableDir)) {
        New-Item -Path $portableDir -ItemType Directory -Force | Out-Null
    }
    
    # Copy executable
    $executable = Get-ChildItem -Path $BuildConfig.DistDir -Filter "*.exe" | Select-Object -First 1
    if ($executable) {
        Copy-Item $executable.FullName $portableDir
        
        # Copy additional files
        @('README.md', 'LICENSE') | ForEach-Object {
            $file = Join-Path $BuildConfig.ProjectRoot $_
            if (Test-Path $file) {
                Copy-Item $file $portableDir
            }
        }
        
        # Create portable info file
        $portableInfo = @"
Application: Unsplash Image Search & GPT Tool
Version: $($BuildConfig.VersionInfo.Version)
Build: $($BuildConfig.VersionInfo.BuildNumber)
Built: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Profile: $Profile

This is a portable version that doesn't require installation.
Simply run the executable file to start the application.

System Requirements:
- Windows 10 or later
- Internet connection for API access
- At least 512MB RAM

For support and updates, visit:
https://github.com/yourusername/unsplash-image-search-gpt
"@
        
        $portableInfo | Out-File -FilePath (Join-Path $portableDir 'PORTABLE_INFO.txt') -Encoding UTF8
        
        $BuildConfig.BuildArtifacts += @{
            Type = 'Portable'
            Path = $portableDir
            Name = 'Portable'
            Size = (Get-ChildItem $portableDir -Recurse | Measure-Object -Property Length -Sum).Sum
        }
        
        Write-BuildLog "Portable version created in: $portableDir" -Level SUCCESS
    }
}

function New-Installer {
    if (-not $CreateInstaller) {
        return
    }
    
    Write-BuildLog "=== CREATING INSTALLER ===" -Level INFO
    
    # Check for NSIS
    $nsisPath = Get-Command makensis -ErrorAction SilentlyContinue
    if ($nsisPath) {
        Write-BuildLog "Creating NSIS installer..."
        $installerScript = Join-Path $BuildConfig.ProjectRoot 'installer\installer.nsi'
        if (Test-Path $installerScript) {
            makensis $installerScript 2>&1 | Tee-Object -FilePath $BuildConfig.LogFile -Append
            if ($LASTEXITCODE -eq 0) {
                Write-BuildLog "NSIS installer created successfully" -Level SUCCESS
                # Find installer file
                $installer = Get-ChildItem -Path $BuildConfig.ProjectRoot -Filter "*Setup*.exe" | Select-Object -First 1
                if ($installer) {
                    $BuildConfig.BuildArtifacts += @{
                        Type = 'Installer'
                        Path = $installer.FullName
                        Name = $installer.Name
                        Size = $installer.Length
                    }
                }
            } else {
                Write-BuildLog "NSIS installer creation failed" -Level WARNING
            }
        } else {
            Write-BuildLog "NSIS installer script not found" -Level WARNING
        }
    }
    
    # Check for Inno Setup
    $innoPath = Get-Command iscc -ErrorAction SilentlyContinue
    if ($innoPath) {
        Write-BuildLog "Creating Inno Setup installer..."
        $innoScript = Join-Path $BuildConfig.ProjectRoot 'installer\installer.iss'
        if (Test-Path $innoScript) {
            iscc $innoScript 2>&1 | Tee-Object -FilePath $BuildConfig.LogFile -Append
            if ($LASTEXITCODE -eq 0) {
                Write-BuildLog "Inno Setup installer created successfully" -Level SUCCESS
            } else {
                Write-BuildLog "Inno Setup installer creation failed" -Level WARNING
            }
        }
    }
    
    if (-not $nsisPath -and -not $innoPath) {
        Write-BuildLog "No installer creator found (NSIS or Inno Setup)" -Level WARNING
    }
}

function New-CompressedArchive {
    if (-not $Compress) {
        return
    }
    
    Write-BuildLog "=== CREATING COMPRESSED ARCHIVE ===" -Level INFO
    
    $archiveName = "Unsplash_GPT_Tool_v$($BuildConfig.VersionInfo.Version)_$($Profile)_Build$($BuildConfig.VersionInfo.BuildNumber).zip"
    $archivePath = Join-Path (Split-Path $BuildConfig.DistDir) $archiveName
    
    try {
        # Create ZIP archive of dist folder
        Compress-Archive -Path "$($BuildConfig.DistDir)\*" -DestinationPath $archivePath -Force
        
        $BuildConfig.BuildArtifacts += @{
            Type = 'Archive'
            Path = $archivePath
            Name = $archiveName
            Size = (Get-Item $archivePath).Length
        }
        
        Write-BuildLog "Compressed archive created: $archiveName" -Level SUCCESS
    }
    catch {
        Write-BuildLog "Failed to create compressed archive: $($_.Exception.Message)" -Level WARNING
    }
}

function Invoke-ArtifactPreparation {
    if (-not $UploadArtifacts) {
        return
    }
    
    Write-BuildLog "=== PREPARING ARTIFACTS FOR UPLOAD ===" -Level INFO
    
    $uploadDir = Join-Path (Split-Path $BuildConfig.DistDir) 'upload'
    if (-not (Test-Path $uploadDir)) {
        New-Item -Path $uploadDir -ItemType Directory -Force | Out-Null
    }
    
    # Copy artifacts to upload directory
    foreach ($artifact in $BuildConfig.BuildArtifacts) {
        if ($artifact.Type -in @('Executable', 'Installer', 'Archive', 'Checksum')) {
            $destPath = Join-Path $uploadDir $artifact.Name
            if (Test-Path $artifact.Path) {
                Copy-Item $artifact.Path $destPath -Force
                Write-BuildLog "Prepared for upload: $($artifact.Name)"
            }
        }
    }
    
    # Create release notes
    $releaseNotes = @"
# Release Notes - Version $($BuildConfig.VersionInfo.Version)

**Build Information:**
- Version: $($BuildConfig.VersionInfo.Version)
- Build Number: $($BuildConfig.VersionInfo.BuildNumber)
- Profile: $Profile
- Built: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Git Branch: $($BuildConfig.GitInfo.Branch)
- Git Commit: $($BuildConfig.GitInfo.Commit)

**Artifacts:**
"@
    
    foreach ($artifact in ($BuildConfig.BuildArtifacts | Where-Object { $_.Type -in @('Executable', 'Installer', 'Archive') })) {
        $sizeMB = [Math]::Round($artifact.Size / 1MB, 2)
        $releaseNotes += "`n- $($artifact.Name) ($sizeMB MB)"
    }
    
    $releaseNotes += @"

**System Requirements:**
- Windows 10 or later (64-bit)
- Internet connection
- 512MB RAM minimum

**Installation:**
1. Download the appropriate file for your needs
2. For portable version: Extract and run the executable
3. For installer: Run the setup and follow the wizard

**Verification:**
Each file includes a SHA256 checksum for integrity verification.
"@
    
    $releaseNotes | Out-File -FilePath (Join-Path $uploadDir 'RELEASE_NOTES.md') -Encoding UTF8
    
    Write-BuildLog "Artifacts prepared for upload in: $uploadDir" -Level SUCCESS
    Write-BuildLog "Upload directory contains $($BuildConfig.BuildArtifacts.Count) artifacts"
}

function Show-BuildSummary {
    $buildTime = (Get-Date) - $BuildConfig.StartTime
    
    Write-BuildLog "========================================" -Level SUCCESS
    Write-BuildLog "          BUILD COMPLETED" -Level SUCCESS
    Write-BuildLog "========================================" -Level SUCCESS
    Write-Host ""
    
    Write-Host "Build Summary:" -ForegroundColor Cyan
    Write-Host "  Profile: $Profile" -ForegroundColor White
    Write-Host "  Version: $($BuildConfig.VersionInfo.Version)" -ForegroundColor White
    Write-Host "  Build Number: $($BuildConfig.VersionInfo.BuildNumber)" -ForegroundColor White
    Write-Host "  Build Time: $([Math]::Round($buildTime.TotalMinutes, 2)) minutes" -ForegroundColor White
    Write-Host "  Warnings: $($BuildConfig.Warnings.Count)" -ForegroundColor $(if ($BuildConfig.Warnings.Count -gt 0) { 'Yellow' } else { 'Green' })
    Write-Host ""
    
    Write-Host "Artifacts Created:" -ForegroundColor Cyan
    foreach ($artifact in $BuildConfig.BuildArtifacts) {
        $sizeMB = [Math]::Round($artifact.Size / 1MB, 2)
        Write-Host "  [$($artifact.Type)] $($artifact.Name) ($sizeMB MB)" -ForegroundColor White
    }
    
    if ($BuildConfig.GitInfo.IsGitRepo) {
        Write-Host ""
        Write-Host "Git Information:" -ForegroundColor Cyan
        Write-Host "  Branch: $($BuildConfig.GitInfo.Branch)" -ForegroundColor White
        Write-Host "  Commit: $($BuildConfig.GitInfo.CommitShort)" -ForegroundColor White
        Write-Host "  Clean: $(-not $BuildConfig.GitInfo.IsDirty)" -ForegroundColor $(if ($BuildConfig.GitInfo.IsDirty) { 'Yellow' } else { 'Green' })
    }
    
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Test the executable thoroughly" -ForegroundColor White
    Write-Host "  2. Review the build log: $($BuildConfig.LogFile)" -ForegroundColor White
    if ($CreateInstaller) {
        Write-Host "  3. Test the installer on clean systems" -ForegroundColor White
    }
    if ($UploadArtifacts) {
        Write-Host "  4. Upload artifacts from the upload directory" -ForegroundColor White
    }
    Write-Host ""
    
    if ($BuildConfig.Warnings.Count -gt 0) {
        Write-Host "Warnings:" -ForegroundColor Yellow
        $BuildConfig.Warnings | ForEach-Object {
            Write-Host "  - $_" -ForegroundColor Yellow
        }
        Write-Host ""
    }
}

# Main execution
try {
    Push-Location $BuildConfig.ProjectRoot
    
    Write-BuildLog "========================================" -Level INFO
    Write-BuildLog "   ADVANCED BUILD SYSTEM STARTED" -Level INFO
    Write-BuildLog "========================================" -Level INFO
    Write-BuildLog "Profile: $Profile"
    Write-BuildLog "Project Root: $($BuildConfig.ProjectRoot)"
    Write-BuildLog "Log File: $($BuildConfig.LogFile)"
    Write-BuildLog ""
    
    # Execute build pipeline
    Get-GitInformation
    Get-VersionInformation
    Invoke-PreBuildValidation
    Install-Dependencies
    Invoke-CleanBuild
    Invoke-Tests
    Invoke-CodeQualityChecks
    New-VersionFile
    Invoke-BuildExecutable
    Invoke-PostBuildVerification
    New-PortableVersion
    New-Installer
    New-CompressedArchive
    Invoke-ArtifactPreparation
    
    Show-BuildSummary
    
    Write-BuildLog "Build completed successfully!" -Level SUCCESS
    exit 0
}
catch {
    Write-BuildLog "========================================" -Level ERROR
    Write-BuildLog "        BUILD FAILED" -Level ERROR
    Write-BuildLog "========================================" -Level ERROR
    Write-BuildLog "Error: $($_.Exception.Message)" -Level ERROR
    Write-BuildLog "Location: $($_.InvocationInfo.ScriptName):$($_.InvocationInfo.ScriptLineNumber)" -Level ERROR
    Write-BuildLog ""
    Write-BuildLog "Check the log file for details: $($BuildConfig.LogFile)" -Level ERROR
    
    exit 1
}
finally {
    Pop-Location
}