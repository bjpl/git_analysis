#Requires -Version 5.1

<#
.SYNOPSIS
    Pre-build validation script for Unsplash GPT Tool

.DESCRIPTION
    Comprehensive validation script that checks all prerequisites before building.
    Validates Python environment, dependencies, code quality, and project structure.

.PARAMETER Strict
    Enable strict validation mode (fails on warnings)

.PARAMETER FixIssues
    Attempt to automatically fix detected issues

.PARAMETER Profile
    Build profile to validate against (affects validation criteria)

.PARAMETER OutputReport
    Generate detailed validation report

.EXAMPLE
    .\pre-build-validation.ps1 -Profile Production -FixIssues

.NOTES
    Should be run before any build process to ensure environment is ready
#>

[CmdletBinding()]
param(
    [Parameter()]
    [switch]$Strict,
    
    [Parameter()]
    [switch]$FixIssues,
    
    [Parameter()]
    [ValidateSet('development', 'production', 'debug', 'testing', 'portable')]
    [string]$Profile = 'production',
    
    [Parameter()]
    [switch]$OutputReport,
    
    [Parameter()]
    [string]$ReportPath
)

# Initialize validation state
$ValidationResults = @{
    Passed = @()
    Failed = @()
    Warnings = @()
    Fixed = @()
    StartTime = Get-Date
    Profile = $Profile
}

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ErrorCount = 0
$WarningCount = 0

function Write-ValidationResult {
    param(
        [string]$Test,
        [string]$Status,
        [string]$Message = "",
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    $statusColor = switch ($Status) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
        "WARN" { "Yellow" }
        "INFO" { "Cyan" }
        "FIXED" { "Magenta" }
        default { "White" }
    }
    
    $output = "[$timestamp] [$Status] $Test"
    if ($Message) {
        $output += " - $Message"
    }
    
    Write-Host $output -ForegroundColor $statusColor
    
    # Store result
    switch ($Status) {
        "PASS" { $ValidationResults.Passed += @{Test = $Test; Message = $Message} }
        "FAIL" { 
            $ValidationResults.Failed += @{Test = $Test; Message = $Message}
            $script:ErrorCount++
        }
        "WARN" { 
            $ValidationResults.Warnings += @{Test = $Test; Message = $Message}
            $script:WarningCount++
        }
        "FIXED" { $ValidationResults.Fixed += @{Test = $Test; Message = $Message} }
    }
}

function Test-PythonEnvironment {
    Write-Host "`n=== PYTHON ENVIRONMENT VALIDATION ===" -ForegroundColor Cyan
    
    # Check Python installation
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            if ($pythonVersion -match 'Python (\d+)\.(\d+)\.(\d+)') {
                $major = [int]$matches[1]
                $minor = [int]$matches[2]
                $patch = [int]$matches[3]
                
                $versionString = "$major.$minor.$patch"
                
                if ($major -ge 3 -and $minor -ge 8) {
                    Write-ValidationResult "Python Version" "PASS" "Found Python $versionString"
                    
                    # Check if it's 64-bit
                    $pythonArch = python -c "import platform; print(platform.architecture()[0])" 2>$null
                    if ($pythonArch -eq "64bit") {
                        Write-ValidationResult "Python Architecture" "PASS" "64-bit Python detected"
                    } else {
                        Write-ValidationResult "Python Architecture" "WARN" "32-bit Python detected, 64-bit recommended"
                    }
                } else {
                    Write-ValidationResult "Python Version" "FAIL" "Python 3.8+ required, found $versionString"
                }
            } else {
                Write-ValidationResult "Python Version" "FAIL" "Could not parse Python version: $pythonVersion"
            }
        } else {
            Write-ValidationResult "Python Installation" "FAIL" "Python not found in PATH"
            return $false
        }
    }
    catch {
        Write-ValidationResult "Python Installation" "FAIL" $_.Exception.Message
        return $false
    }
    
    # Check pip
    try {
        $pipVersion = python -m pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ValidationResult "Pip Installation" "PASS" "Pip available"
            
            # Check if pip is up to date
            $pipCheck = python -m pip list --outdated --format=json 2>$null | ConvertFrom-Json
            $pipOutdated = $pipCheck | Where-Object { $_.name -eq "pip" }
            
            if ($pipOutdated) {
                if ($FixIssues) {
                    Write-Host "Updating pip..." -ForegroundColor Yellow
                    python -m pip install --upgrade pip --quiet
                    if ($LASTEXITCODE -eq 0) {
                        Write-ValidationResult "Pip Update" "FIXED" "Pip updated successfully"
                    } else {
                        Write-ValidationResult "Pip Update" "WARN" "Failed to update pip"
                    }
                } else {
                    Write-ValidationResult "Pip Version" "WARN" "Pip update available"
                }
            }
        } else {
            Write-ValidationResult "Pip Installation" "FAIL" "Pip not available"
        }
    }
    catch {
        Write-ValidationResult "Pip Installation" "FAIL" $_.Exception.Message
    }
    
    return $true
}

function Test-VirtualEnvironment {
    Write-Host "`n=== VIRTUAL ENVIRONMENT VALIDATION ===" -ForegroundColor Cyan
    
    $venvPath = Join-Path $ProjectRoot "venv"
    
    if (Test-Path $venvPath) {
        Write-ValidationResult "Virtual Environment" "PASS" "Virtual environment found at: $venvPath"
        
        # Check if virtual environment is activated
        if ($env:VIRTUAL_ENV) {
            Write-ValidationResult "VEnv Activation" "PASS" "Virtual environment is active"
        } else {
            if ($FixIssues) {
                # Attempt to activate virtual environment
                $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
                if (Test-Path $activateScript) {
                    try {
                        & $activateScript
                        Write-ValidationResult "VEnv Activation" "FIXED" "Virtual environment activated"
                    }
                    catch {
                        Write-ValidationResult "VEnv Activation" "WARN" "Failed to activate virtual environment"
                    }
                }
            } else {
                Write-ValidationResult "VEnv Activation" "WARN" "Virtual environment not activated"
            }
        }
        
        # Check virtual environment Python version
        $venvPython = Join-Path $venvPath "Scripts\python.exe"
        if (Test-Path $venvPython) {
            try {
                $venvPythonVersion = & $venvPython --version 2>&1
                Write-ValidationResult "VEnv Python" "PASS" "Virtual environment Python: $venvPythonVersion"
            }
            catch {
                Write-ValidationResult "VEnv Python" "WARN" "Could not check virtual environment Python version"
            }
        }
    } else {
        if ($FixIssues) {
            Write-Host "Creating virtual environment..." -ForegroundColor Yellow
            python -m venv $venvPath
            if ($LASTEXITCODE -eq 0) {
                Write-ValidationResult "Virtual Environment" "FIXED" "Virtual environment created"
            } else {
                Write-ValidationResult "Virtual Environment" "FAIL" "Failed to create virtual environment"
            }
        } else {
            Write-ValidationResult "Virtual Environment" "FAIL" "Virtual environment not found"
        }
    }
}

function Test-ProjectStructure {
    Write-Host "`n=== PROJECT STRUCTURE VALIDATION ===" -ForegroundColor Cyan
    
    # Required files
    $requiredFiles = @{
        'main.py' = 'Main application entry point'
        'version_info.py' = 'Version information module'
        'config_manager.py' = 'Configuration management module'
        'pyproject.toml' = 'Project configuration file'
    }
    
    foreach ($file in $requiredFiles.Keys) {
        $filePath = Join-Path $ProjectRoot $file
        if (Test-Path $filePath) {
            Write-ValidationResult "Required File: $file" "PASS" $requiredFiles[$file]
        } else {
            Write-ValidationResult "Required File: $file" "FAIL" "Missing: $($requiredFiles[$file])"
        }
    }
    
    # Check directory structure
    $requiredDirs = @{
        'src' = 'Source code directory'
        'tests' = 'Test files directory'
        'scripts' = 'Build and utility scripts'
    }
    
    foreach ($dir in $requiredDirs.Keys) {
        $dirPath = Join-Path $ProjectRoot $dir
        if (Test-Path $dirPath -PathType Container) {
            $fileCount = (Get-ChildItem $dirPath -Recurse -File).Count
            Write-ValidationResult "Directory: $dir" "PASS" "$($requiredDirs[$dir]) ($fileCount files)"
        } else {
            Write-ValidationResult "Directory: $dir" "WARN" "Optional directory missing: $($requiredDirs[$dir])"
        }
    }
    
    # Check for assets
    $assetsDir = Join-Path $ProjectRoot "assets"
    if (Test-Path $assetsDir) {
        $iconFile = Join-Path $assetsDir "app_icon.ico"
        if (Test-Path $iconFile) {
            Write-ValidationResult "Application Icon" "PASS" "Icon file found"
        } else {
            Write-ValidationResult "Application Icon" "WARN" "No application icon found"
        }
    }
}

function Test-Dependencies {
    Write-Host "`n=== DEPENDENCY VALIDATION ===" -ForegroundColor Cyan
    
    # Check core dependencies
    $coreDependencies = @{
        'requests' = 'HTTP library for API calls'
        'Pillow' = 'Image processing library'
        'openai' = 'OpenAI API client'
        'python-dotenv' = 'Environment variable management'
    }
    
    foreach ($package in $coreDependencies.Keys) {
        try {
            python -c "import $($package.ToLower().Replace('-', '_'))" 2>$null
            if ($LASTEXITCODE -eq 0) {
                # Get version info
                $version = python -c "import $($package.ToLower().Replace('-', '_')); print(getattr($($package.ToLower().Replace('-', '_')), '__version__', 'unknown'))" 2>$null
                Write-ValidationResult "Dependency: $package" "PASS" "$($coreDependencies[$package]) (v$version)"
            } else {
                Write-ValidationResult "Dependency: $package" "FAIL" "Missing: $($coreDependencies[$package])"
            }
        }
        catch {
            Write-ValidationResult "Dependency: $package" "FAIL" "Import error: $($_.Exception.Message)"
        }
    }
    
    # Check development dependencies
    if ($Profile -in @('development', 'debug', 'testing')) {
        $devDependencies = @{
            'pytest' = 'Testing framework'
            'pyinstaller' = 'Executable builder'
        }
        
        foreach ($package in $devDependencies.Keys) {
            try {
                python -c "import $package" 2>$null
                if ($LASTEXITCODE -eq 0) {
                    Write-ValidationResult "Dev Dependency: $package" "PASS" $devDependencies[$package]
                } else {
                    if ($FixIssues) {
                        Write-Host "Installing $package..." -ForegroundColor Yellow
                        python -m pip install $package --quiet
                        if ($LASTEXITCODE -eq 0) {
                            Write-ValidationResult "Dev Dependency: $package" "FIXED" "Installed $package"
                        } else {
                            Write-ValidationResult "Dev Dependency: $package" "FAIL" "Failed to install $package"
                        }
                    } else {
                        Write-ValidationResult "Dev Dependency: $package" "WARN" "Missing: $($devDependencies[$package])"
                    }
                }
            }
            catch {
                Write-ValidationResult "Dev Dependency: $package" "WARN" $_.Exception.Message
            }
        }
    }
    
    # Install PyInstaller if not present (required for all builds)
    try {
        python -c "import PyInstaller" 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pyinstallerVersion = python -c "import PyInstaller; print(PyInstaller.__version__)" 2>$null
            Write-ValidationResult "PyInstaller" "PASS" "Version $pyinstallerVersion"
        } else {
            if ($FixIssues) {
                Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
                python -m pip install pyinstaller --quiet
                if ($LASTEXITCODE -eq 0) {
                    Write-ValidationResult "PyInstaller" "FIXED" "PyInstaller installed"
                } else {
                    Write-ValidationResult "PyInstaller" "FAIL" "Failed to install PyInstaller"
                }
            } else {
                Write-ValidationResult "PyInstaller" "FAIL" "PyInstaller not installed"
            }
        }
    }
    catch {
        Write-ValidationResult "PyInstaller" "FAIL" $_.Exception.Message
    }
}

function Test-CodeQuality {
    Write-Host "`n=== CODE QUALITY VALIDATION ===" -ForegroundColor Cyan
    
    # Basic syntax check
    $pythonFiles = Get-ChildItem -Path $ProjectRoot -Filter "*.py" | Where-Object { $_.Name -ne "test_*.py" }
    
    foreach ($file in $pythonFiles) {
        try {
            python -m py_compile $file.FullName 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-ValidationResult "Syntax: $($file.Name)" "PASS" "No syntax errors"
            } else {
                Write-ValidationResult "Syntax: $($file.Name)" "FAIL" "Syntax errors detected"
            }
        }
        catch {
            Write-ValidationResult "Syntax: $($file.Name)" "FAIL" $_.Exception.Message
        }
    }
    
    # Check for hardcoded paths
    Write-Host "Scanning for hardcoded paths..."
    $hardcodedIssues = @()
    
    foreach ($file in $pythonFiles) {
        $content = Get-Content $file.FullName -Raw
        $lines = $content -split "`n"
        
        for ($i = 0; $i -lt $lines.Count; $i++) {
            $line = $lines[$i]
            if ($line -match '[C-Z]:\\|/home/|/Users/') {
                $hardcodedIssues += @{
                    File = $file.Name
                    Line = $i + 1
                    Content = $line.Trim()
                }
            }
        }
    }
    
    if ($hardcodedIssues.Count -eq 0) {
        Write-ValidationResult "Hardcoded Paths" "PASS" "No hardcoded paths detected"
    } else {
        foreach ($issue in $hardcodedIssues) {
            Write-ValidationResult "Hardcoded Path" "WARN" "$($issue.File):$($issue.Line) - $($issue.Content)"
        }
    }
    
    # Check import structure
    try {
        python -c "import main" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ValidationResult "Import Structure" "PASS" "Main module imports successfully"
        } else {
            Write-ValidationResult "Import Structure" "FAIL" "Main module has import issues"
        }
    }
    catch {
        Write-ValidationResult "Import Structure" "FAIL" $_.Exception.Message
    }
}

function Test-Configuration {
    Write-Host "`n=== CONFIGURATION VALIDATION ===" -ForegroundColor Cyan
    
    # Check environment file
    $envFile = Join-Path $ProjectRoot ".env"
    $envExampleFile = Join-Path $ProjectRoot ".env.example"
    
    if (Test-Path $envFile) {
        Write-ValidationResult "Environment File" "PASS" ".env file found"
        
        # Check if .env has required keys (basic check)
        $envContent = Get-Content $envFile -Raw
        $requiredKeys = @('OPENAI_API_KEY', 'UNSPLASH_API_KEY')
        
        foreach ($key in $requiredKeys) {
            if ($envContent -match "$key\s*=") {
                Write-ValidationResult "Env Key: $key" "PASS" "Environment key configured"
            } else {
                Write-ValidationResult "Env Key: $key" "WARN" "Environment key not found"
            }
        }
    } else {
        if (Test-Path $envExampleFile) {
            if ($FixIssues) {
                Copy-Item $envExampleFile $envFile
                Write-ValidationResult "Environment File" "FIXED" "Created .env from template"
            } else {
                Write-ValidationResult "Environment File" "WARN" ".env file missing, template available"
            }
        } else {
            Write-ValidationResult "Environment File" "FAIL" "No .env or .env.example file found"
        }
    }
    
    # Check configuration manager
    try {
        python -c "import config_manager; cm = config_manager.ConfigManager()" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ValidationResult "Config Manager" "PASS" "Configuration manager loads successfully"
        } else {
            Write-ValidationResult "Config Manager" "FAIL" "Configuration manager has issues"
        }
    }
    catch {
        Write-ValidationResult "Config Manager" "FAIL" $_.Exception.Message
    }
}

function Test-BuildRequirements {
    Write-Host "`n=== BUILD REQUIREMENTS VALIDATION ===" -ForegroundColor Cyan
    
    # Check disk space
    $drive = Split-Path $ProjectRoot -Qualifier
    $driveInfo = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DeviceID -eq $drive }
    $freeSpaceGB = [math]::Round($driveInfo.FreeSpace / 1GB, 2)
    
    if ($freeSpaceGB -gt 1) {
        Write-ValidationResult "Disk Space" "PASS" "$freeSpaceGB GB available"
    } else {
        Write-ValidationResult "Disk Space" "WARN" "Low disk space: $freeSpaceGB GB"
    }
    
    # Check memory
    $memory = Get-WmiObject -Class Win32_ComputerSystem
    $totalMemoryGB = [math]::Round($memory.TotalPhysicalMemory / 1GB, 2)
    
    if ($totalMemoryGB -ge 4) {
        Write-ValidationResult "System Memory" "PASS" "$totalMemoryGB GB total memory"
    } else {
        Write-ValidationResult "System Memory" "WARN" "Limited memory: $totalMemoryGB GB"
    }
    
    # Check Windows version
    $osVersion = (Get-WmiObject -Class Win32_OperatingSystem).Version
    $windowsVersion = [System.Environment]::OSVersion.Version
    
    if ($windowsVersion.Major -ge 10) {
        Write-ValidationResult "Windows Version" "PASS" "Windows 10/11 detected"
    } else {
        Write-ValidationResult "Windows Version" "WARN" "Older Windows version: $($windowsVersion.ToString())"
    }
    
    # Check for required build tools
    $buildTools = @{
        'git' = 'Version control system'
        'makensis' = 'NSIS installer creator (optional)'
        'iscc' = 'Inno Setup compiler (optional)'
    }
    
    foreach ($tool in $buildTools.Keys) {
        $toolPath = Get-Command $tool -ErrorAction SilentlyContinue
        if ($toolPath) {
            Write-ValidationResult "Build Tool: $tool" "PASS" "$($buildTools[$tool]) found"
        } else {
            $level = if ($tool -eq 'git') { "WARN" } else { "INFO" }
            Write-ValidationResult "Build Tool: $tool" $level "$($buildTools[$tool]) not found"
        }
    }
}

function Test-SecuritySettings {
    Write-Host "`n=== SECURITY VALIDATION ===" -ForegroundColor Cyan
    
    # Check execution policy
    $executionPolicy = Get-ExecutionPolicy
    if ($executionPolicy -in @('RemoteSigned', 'Unrestricted')) {
        Write-ValidationResult "PowerShell Execution Policy" "PASS" "Policy: $executionPolicy"
    } else {
        Write-ValidationResult "PowerShell Execution Policy" "WARN" "Restrictive policy: $executionPolicy"
    }
    
    # Check for sensitive data in code
    $pythonFiles = Get-ChildItem -Path $ProjectRoot -Filter "*.py" -Recurse
    $sensitivePatterns = @(
        'password\s*=\s*["\'][^"\']+["\']',
        'api_key\s*=\s*["\'][^"\']+["\']',
        'secret\s*=\s*["\'][^"\']+["\']',
        'token\s*=\s*["\'][^"\']+["\']'
    )
    
    $sensitiveIssues = @()
    foreach ($file in $pythonFiles) {
        $content = Get-Content $file.FullName -Raw
        foreach ($pattern in $sensitivePatterns) {
            if ($content -match $pattern) {
                $sensitiveIssues += @{
                    File = $file.Name
                    Pattern = $pattern
                }
            }
        }
    }
    
    if ($sensitiveIssues.Count -eq 0) {
        Write-ValidationResult "Sensitive Data Check" "PASS" "No hardcoded secrets detected"
    } else {
        foreach ($issue in $sensitiveIssues) {
            Write-ValidationResult "Sensitive Data" "WARN" "Potential secret in $($issue.File)"
        }
    }
}

function Generate-ValidationReport {
    if (-not $OutputReport) {
        return
    }
    
    $reportPath = if ($ReportPath) { $ReportPath } else { Join-Path $ProjectRoot "validation-report.html" }
    
    $duration = (Get-Date) - $ValidationResults.StartTime
    
    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Pre-Build Validation Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 15px; border-radius: 5px; }
        .pass { color: green; }
        .fail { color: red; }
        .warn { color: orange; }
        .fixed { color: purple; }
        .section { margin: 20px 0; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Pre-Build Validation Report</h1>
        <p><strong>Profile:</strong> $($ValidationResults.Profile)</p>
        <p><strong>Generated:</strong> $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
        <p><strong>Duration:</strong> $([math]::Round($duration.TotalSeconds, 2)) seconds</p>
    </div>
    
    <div class="section">
        <h2>Summary</h2>
        <ul>
            <li><span class="pass">Passed:</span> $($ValidationResults.Passed.Count) tests</li>
            <li><span class="fail">Failed:</span> $($ValidationResults.Failed.Count) tests</li>
            <li><span class="warn">Warnings:</span> $($ValidationResults.Warnings.Count) tests</li>
            <li><span class="fixed">Fixed:</span> $($ValidationResults.Fixed.Count) issues</li>
        </ul>
    </div>
"@
    
    if ($ValidationResults.Failed.Count -gt 0) {
        $html += @"
    <div class="section">
        <h2>Failed Tests</h2>
        <table>
            <tr><th>Test</th><th>Message</th></tr>
"@
        foreach ($fail in $ValidationResults.Failed) {
            $html += "<tr><td>$($fail.Test)</td><td>$($fail.Message)</td></tr>"
        }
        $html += "</table></div>"
    }
    
    if ($ValidationResults.Warnings.Count -gt 0) {
        $html += @"
    <div class="section">
        <h2>Warnings</h2>
        <table>
            <tr><th>Test</th><th>Message</th></tr>
"@
        foreach ($warn in $ValidationResults.Warnings) {
            $html += "<tr><td>$($warn.Test)</td><td>$($warn.Message)</td></tr>"
        }
        $html += "</table></div>"
    }
    
    $html += "</body></html>"
    
    $html | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Host "`nValidation report generated: $reportPath" -ForegroundColor Green
}

# Main execution
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   PRE-BUILD VALIDATION STARTED" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Profile: $Profile" -ForegroundColor White
Write-Host "Project: $ProjectRoot" -ForegroundColor White
Write-Host "Strict Mode: $Strict" -ForegroundColor White
Write-Host "Fix Issues: $FixIssues" -ForegroundColor White
Write-Host ""

Push-Location $ProjectRoot

try {
    # Run validation tests
    Test-PythonEnvironment
    Test-VirtualEnvironment
    Test-ProjectStructure
    Test-Dependencies
    Test-CodeQuality
    Test-Configuration
    Test-BuildRequirements
    Test-SecuritySettings
    
    # Generate report if requested
    Generate-ValidationReport
    
    # Final results
    $duration = (Get-Date) - $ValidationResults.StartTime
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "   VALIDATION COMPLETED" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Results Summary:" -ForegroundColor White
    Write-Host "  Passed: $($ValidationResults.Passed.Count)" -ForegroundColor Green
    Write-Host "  Failed: $($ValidationResults.Failed.Count)" -ForegroundColor Red
    Write-Host "  Warnings: $($ValidationResults.Warnings.Count)" -ForegroundColor Yellow
    Write-Host "  Fixed: $($ValidationResults.Fixed.Count)" -ForegroundColor Magenta
    Write-Host "  Duration: $([math]::Round($duration.TotalSeconds, 2)) seconds" -ForegroundColor White
    Write-Host ""
    
    if ($ErrorCount -gt 0) {
        Write-Host "❌ Validation FAILED with $ErrorCount errors" -ForegroundColor Red
        Write-Host "Build should not proceed until issues are resolved." -ForegroundColor Red
        exit 1
    } elseif ($WarningCount -gt 0 -and $Strict) {
        Write-Host "⚠️ Validation completed with $WarningCount warnings (Strict mode)" -ForegroundColor Yellow
        Write-Host "Build blocked due to strict mode." -ForegroundColor Yellow
        exit 1
    } elseif ($WarningCount -gt 0) {
        Write-Host "⚠️ Validation completed with $WarningCount warnings" -ForegroundColor Yellow
        Write-Host "Build can proceed but warnings should be addressed." -ForegroundColor Yellow
        exit 0
    } else {
        Write-Host "✅ All validation checks passed!" -ForegroundColor Green
        Write-Host "Environment is ready for building." -ForegroundColor Green
        exit 0
    }
}
catch {
    Write-Host "❌ Validation failed with exception: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
finally {
    Pop-Location
}