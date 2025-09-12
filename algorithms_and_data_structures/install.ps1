# CLI Installation Script for Windows PowerShell
# Version: 1.0.0
# Requires: PowerShell 5.1+ and Administrator privileges for some features

param(
    [switch]$Dev,
    [switch]$NoNode,
    [string]$InstallPath = "$env:LOCALAPPDATA\algorithms-cli"
)

# Enable strict mode
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Configuration
$CliName = "algorithms-cli"
$RepoUrl = "https://github.com/brandonjplambert/algorithms_and_data_structures"
$ConfigDir = "$env:APPDATA\$CliName"
$VenvDir = "$InstallPath\venv"

# Colors for output
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    White = "White"
}

function Write-Header {
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host "  Algorithms & Data Structures CLI     " -ForegroundColor Blue
    Write-Host "  Installation Script v1.0.0           " -ForegroundColor Blue
    Write-Host "  Windows PowerShell Edition            " -ForegroundColor Blue
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-SystemInfo {
    Write-Info "Detecting system information..."
    
    $osInfo = Get-CimInstance Win32_OperatingSystem
    $architecture = $env:PROCESSOR_ARCHITECTURE
    
    Write-Info "OS: $($osInfo.Caption) ($architecture)"
    Write-Info "PowerShell Version: $($PSVersionTable.PSVersion)"
    
    return @{
        OS = $osInfo.Caption
        Architecture = $architecture
        PSVersion = $PSVersionTable.PSVersion
    }
}

function Test-PythonInstallation {
    Write-Info "Checking Python installation..."
    
    $pythonCommands = @("python", "python3", "py")
    $pythonCmd = $null
    
    foreach ($cmd in $pythonCommands) {
        try {
            $version = & $cmd --version 2>$null
            if ($version -match "Python (\d+)\.(\d+)\.(\d+)") {
                $major = [int]$Matches[1]
                $minor = [int]$Matches[2]
                
                if ($major -ge 3 -and $minor -ge 8) {
                    $pythonCmd = $cmd
                    Write-Success "Python $version found"
                    break
                }
                else {
                    Write-Warning "Python $version is too old (3.8+ required)"
                }
            }
        }
        catch {
            # Command not found, continue
        }
    }
    
    if (-not $pythonCmd) {
        Write-Error "Python 3.8+ is not installed or not in PATH"
        Write-Info "Please install Python from https://www.python.org/downloads/"
        Write-Info "Make sure to check 'Add Python to PATH' during installation"
        exit 1
    }
    
    return $pythonCmd
}

function Test-NodeInstallation {
    if ($NoNode) {
        Write-Info "Skipping Node.js check (--NoNode specified)"
        return $false
    }
    
    Write-Info "Checking Node.js for Claude Flow integration..."
    
    try {
        $nodeVersion = node --version 2>$null
        if ($nodeVersion) {
            Write-Success "Node.js $nodeVersion found"
            return $true
        }
    }
    catch {
        Write-Warning "Node.js not found. Claude Flow features will be limited."
        Write-Info "Install Node.js from https://nodejs.org/ for full functionality"
        return $false
    }
    
    return $false
}

function Install-Chocolatey {
    Write-Info "Installing Chocolatey package manager..."
    
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Success "Chocolatey installed"
        return $true
    }
    catch {
        Write-Warning "Failed to install Chocolatey: $_"
        return $false
    }
}

function Install-Dependencies {
    Write-Info "Installing system dependencies..."
    
    # Try to install Git if not present
    try {
        git --version | Out-Null
        Write-Success "Git is already installed"
    }
    catch {
        Write-Warning "Git not found. Attempting to install..."
        
        if (Get-Command choco -ErrorAction SilentlyContinue) {
            choco install git -y
        }
        else {
            $hasChoco = Install-Chocolatey
            if ($hasChoco) {
                choco install git -y
            }
            else {
                Write-Warning "Please install Git manually from https://git-scm.com/download/win"
            }
        }
    }
}

function New-VirtualEnvironment {
    param([string]$PythonCmd)
    
    Write-Info "Creating virtual environment..."
    
    # Remove existing venv if present
    if (Test-Path $VenvDir) {
        Write-Warning "Virtual environment already exists. Removing..."
        Remove-Item -Path $VenvDir -Recurse -Force
    }
    
    # Create directory structure
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    
    # Create virtual environment
    & $PythonCmd -m venv $VenvDir
    
    if (-not $?) {
        Write-Error "Failed to create virtual environment"
        exit 1
    }
    
    # Activate and upgrade pip
    $activateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
    . $activateScript
    
    python -m pip install --upgrade pip
    
    Write-Success "Virtual environment created at $VenvDir"
    
    return $activateScript
}

function Install-CLI {
    param([string]$ActivateScript, [bool]$HasNode)
    
    Write-Info "Installing CLI and dependencies..."
    
    # Activate virtual environment
    . $ActivateScript
    
    # Install core Python dependencies
    $corePackages = @(
        "numpy",
        "scipy", 
        "matplotlib",
        "pandas",
        "jupyter",
        "pytest",
        "pytest-cov",
        "black",
        "flake8",
        "mypy"
    )
    
    foreach ($package in $corePackages) {
        Write-Info "Installing $package..."
        pip install $package
    }
    
    # Install Claude Flow if Node.js is available
    if ($HasNode) {
        try {
            npm install -g claude-flow@alpha
            Write-Success "Claude Flow installed"
        }
        catch {
            Write-Warning "Failed to install Claude Flow: $_"
        }
    }
    
    # Create CLI wrapper script
    $binDir = Join-Path $InstallPath "bin"
    New-Item -ItemType Directory -Path $binDir -Force | Out-Null
    
    $wrapperScript = @"
@echo off
call "$VenvDir\Scripts\activate.bat"
cd /d "%~dp0..\..\algorithms_and_data_structures"
python -m algorithms_cli %*
"@
    
    $wrapperPath = Join-Path $binDir "$CliName.bat"
    $wrapperScript | Out-File -FilePath $wrapperPath -Encoding ASCII
    
    Write-Success "CLI installed to $wrapperPath"
    
    return $wrapperPath
}

function New-Configuration {
    param([bool]$HasNode)
    
    Write-Info "Setting up configuration..."
    
    New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null
    
    $config = @{
        version = "1.0.0"
        python_path = Join-Path $VenvDir "Scripts\python.exe"
        venv_path = $VenvDir
        install_date = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
        features = @{
            claude_flow = $HasNode
            jupyter = $true
            testing = $true
        }
        paths = @{
            algorithms = "src\algorithms"
            data_structures = "src\data_structures"
            tests = "tests"
            examples = "examples"
        }
    } | ConvertTo-Json -Depth 3
    
    $configPath = Join-Path $ConfigDir "config.json"
    $config | Out-File -FilePath $configPath -Encoding UTF8
    
    Write-Success "Configuration saved to $configPath"
}

function Add-ToPath {
    param([string]$BinPath)
    
    Write-Info "Adding CLI to PATH..."
    
    $binDir = Split-Path $BinPath -Parent
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    
    if ($currentPath -notlike "*$binDir*") {
        $newPath = "$currentPath;$binDir"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        
        # Add to current session
        $env:PATH += ";$binDir"
        
        Write-Success "Added to user PATH"
    }
    else {
        Write-Info "Already in PATH"
    }
}

function Install-PowerShellCompletion {
    Write-Info "Setting up PowerShell completion..."
    
    $profilePath = $PROFILE
    $completionScript = @"

# Algorithms CLI completion
Register-ArgumentCompleter -CommandName '$CliName' -ScriptBlock {
    param(`$commandName, `$wordToComplete, `$cursorPosition)
    
    `$commands = @('run', 'test', 'benchmark', 'analyze', 'visualize', 'sparc', 'help', 'version')
    
    if (`$wordToComplete) {
        `$commands | Where-Object { `$_ -like "`$wordToComplete*" }
    }
    else {
        `$commands
    }
}
"@
    
    if (Test-Path $profilePath) {
        $profileContent = Get-Content $profilePath -Raw
        if ($profileContent -notlike "*Algorithms CLI completion*") {
            Add-Content -Path $profilePath -Value $completionScript
            Write-Success "PowerShell completion installed"
        }
    }
    else {
        New-Item -ItemType File -Path $profilePath -Force | Out-Null
        Set-Content -Path $profilePath -Value $completionScript
        Write-Success "PowerShell completion installed (new profile created)"
    }
}

function Install-DevEnvironment {
    param([string]$ActivateScript)
    
    Write-Info "Setting up development environment..."
    
    . $ActivateScript
    
    # Install additional dev dependencies
    $devPackages = @(
        "pre-commit",
        "black",
        "isort", 
        "mypy",
        "pytest-xdist",
        "coverage[toml]"
    )
    
    foreach ($package in $devPackages) {
        pip install $package
    }
    
    # Setup pre-commit hooks if config exists
    if (Test-Path ".pre-commit-config.yaml") {
        pre-commit install
        Write-Success "Pre-commit hooks installed"
    }
    
    # Create development PowerShell aliases
    $devAliasesPath = Join-Path $ConfigDir "dev_aliases.ps1"
    $devAliases = @"
# Development aliases for Algorithms CLI
function alg-test { python -m pytest tests\ -v }
function alg-cov { python -m pytest tests\ --cov=src --cov-report=html }
function alg-lint { 
    black src\ tests\
    isort src\ tests\
    mypy src\
}
function alg-sparc { npx claude-flow sparc `$args }

Write-Host "Development aliases loaded" -ForegroundColor Green
"@
    
    $devAliases | Out-File -FilePath $devAliasesPath -Encoding UTF8
    Write-Success "Development environment configured"
}

function New-Uninstaller {
    param([string]$WrapperPath)
    
    $binDir = Split-Path $WrapperPath -Parent
    $uninstallerPath = Join-Path $binDir "$CliName-uninstall.bat"
    
    $uninstaller = @"
@echo off
echo Uninstalling $CliName...

REM Remove virtual environment
if exist "$VenvDir" (
    rmdir /s /q "$VenvDir"
    echo Removed virtual environment
)

REM Remove configuration
if exist "$ConfigDir" (
    rmdir /s /q "$ConfigDir"  
    echo Removed configuration
)

REM Remove installation directory
if exist "$InstallPath" (
    rmdir /s /q "$InstallPath"
    echo Removed installation directory
)

echo Uninstallation complete!
echo Note: You may need to remove PATH entries manually from Environment Variables.
pause
"@
    
    $uninstaller | Out-File -FilePath $uninstallerPath -Encoding ASCII
    Write-Success "Uninstaller created at $uninstallerPath"
}

function Main {
    Write-Header
    
    # Check for administrator privileges for system-wide installs
    if (-not (Test-Administrator)) {
        Write-Warning "Running without administrator privileges"
        Write-Info "Some features may require elevated permissions"
    }
    
    # Parse development mode
    if ($Dev) {
        Write-Info "Installing in development mode"
    }
    
    # Run installation steps
    $systemInfo = Get-SystemInfo
    $pythonCmd = Test-PythonInstallation
    $hasNode = Test-NodeInstallation
    
    Install-Dependencies
    $activateScript = New-VirtualEnvironment -PythonCmd $pythonCmd
    $wrapperPath = Install-CLI -ActivateScript $activateScript -HasNode $hasNode
    New-Configuration -HasNode $hasNode
    Add-ToPath -BinPath $wrapperPath
    Install-PowerShellCompletion
    
    if ($Dev) {
        Install-DevEnvironment -ActivateScript $activateScript
    }
    
    New-Uninstaller -WrapperPath $wrapperPath
    
    # Store installation info in memory
    try {
        npx claude-flow@alpha hooks post-edit --file "install.ps1" --memory-key "swarm/installer/windows-complete" 2>$null
    }
    catch {
        # Ignore if Claude Flow not available
    }
    
    Write-Success "Installation completed successfully!"
    Write-Host ""
    Write-Info "Next steps:"
    Write-Host "  1. Restart PowerShell or reload your profile: . `$PROFILE"
    Write-Host "  2. Test the installation: $CliName version"
    Write-Host "  3. Run the quickstart guide: $CliName help"
    Write-Host ""
    
    if ($hasNode) {
        Write-Info "Claude Flow integration available:"
        Write-Host "  • Run: $CliName sparc tdd 'your-algorithm'"
        Write-Host "  • Full pipeline: npx claude-flow sparc pipeline 'task'"
    }
    
    if ($Dev) {
        Write-Host ""
        Write-Info "Development tools installed:"
        Write-Host "  • Load dev aliases: . '$ConfigDir\dev_aliases.ps1'"
        Write-Host "  • Run tests: alg-test"
        Write-Host "  • Coverage: alg-cov" 
        Write-Host "  • Lint: alg-lint"
    }
    
    Write-Host ""
    Write-Info "Installation directory: $InstallPath"
    Write-Info "Configuration directory: $ConfigDir"
}

# Entry point
try {
    Main
}
catch {
    Write-Error "Installation failed: $_"
    Write-Info "Please check the error message and try again"
    exit 1
}