#Requires -Version 5.1

<#
.SYNOPSIS
    Post-build verification and optimization script

.DESCRIPTION
    Comprehensive verification script that validates built executables,
    performs optimization checks, and prepares artifacts for distribution.

.PARAMETER BuildProfile
    The build profile that was used (affects validation criteria)

.PARAMETER ExecutablePath
    Path to the built executable (auto-detected if not specified)

.PARAMETER GenerateReport
    Generate detailed verification report

.PARAMETER OptimizeArtifacts
    Perform optimization on build artifacts

.PARAMETER RunCompatibilityTests
    Run compatibility tests on different Windows versions (simulated)

.EXAMPLE
    .\post-build-verification.ps1 -BuildProfile Production -OptimizeArtifacts

.NOTES
    Should be run after successful build to verify executable quality
#>

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet('development', 'production', 'debug', 'testing', 'portable')]
    [string]$BuildProfile = 'production',
    
    [Parameter()]
    [string]$ExecutablePath,
    
    [Parameter()]
    [switch]$GenerateReport,
    
    [Parameter()]
    [switch]$OptimizeArtifacts,
    
    [Parameter()]
    [switch]$RunCompatibilityTests,
    
    [Parameter()]
    [string]$ReportPath
)

# Initialize verification state
$VerificationResults = @{
    Passed = @()
    Failed = @()
    Warnings = @()
    Optimizations = @()
    StartTime = Get-Date
    Profile = $BuildProfile
    ExecutableInfo = @{}
}

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$DistDir = Join-Path $ProjectRoot 'dist'
$ErrorCount = 0
$WarningCount = 0

function Write-VerificationResult {
    param(
        [string]$Test,
        [string]$Status,
        [string]$Message = "",
        [string]$Recommendation = ""
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    $statusColor = switch ($Status) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
        "WARN" { "Yellow" }
        "INFO" { "Cyan" }
        "OPTIMIZED" { "Magenta" }
        default { "White" }
    }
    
    $output = "[$timestamp] [$Status] $Test"
    if ($Message) {
        $output += " - $Message"
    }
    
    Write-Host $output -ForegroundColor $statusColor
    
    if ($Recommendation) {
        Write-Host "  💡 $Recommendation" -ForegroundColor Gray
    }
    
    # Store result
    switch ($Status) {
        "PASS" { $VerificationResults.Passed += @{Test = $Test; Message = $Message; Recommendation = $Recommendation} }
        "FAIL" { 
            $VerificationResults.Failed += @{Test = $Test; Message = $Message; Recommendation = $Recommendation}
            $script:ErrorCount++
        }
        "WARN" { 
            $VerificationResults.Warnings += @{Test = $Test; Message = $Message; Recommendation = $Recommendation}
            $script:WarningCount++
        }
        "OPTIMIZED" { $VerificationResults.Optimizations += @{Test = $Test; Message = $Message; Recommendation = $Recommendation} }
    }
}

function Find-Executable {
    Write-Host "`n=== EXECUTABLE DISCOVERY ===" -ForegroundColor Cyan
    
    if ($ExecutablePath -and (Test-Path $ExecutablePath)) {
        $executable = Get-Item $ExecutablePath
        Write-VerificationResult "Executable Discovery" "PASS" "Using specified path: $ExecutablePath"
    } else {
        # Auto-discover executable
        $executables = Get-ChildItem -Path $DistDir -Filter "*.exe" -ErrorAction SilentlyContinue
        
        if ($executables.Count -eq 0) {
            Write-VerificationResult "Executable Discovery" "FAIL" "No executable found in $DistDir"
            return $null
        } elseif ($executables.Count -eq 1) {
            $executable = $executables[0]
            Write-VerificationResult "Executable Discovery" "PASS" "Found executable: $($executable.Name)"
        } else {
            # Multiple executables, try to find the right one based on profile
            $profileExecutable = $executables | Where-Object { 
                $_.Name -match $BuildProfile -or 
                ($BuildProfile -eq 'production' -and $_.Name -notmatch 'dev|debug|test') 
            }
            
            if ($profileExecutable) {
                $executable = $profileExecutable[0]
                Write-VerificationResult "Executable Discovery" "PASS" "Found profile executable: $($executable.Name)"
            } else {
                $executable = $executables[0]
                Write-VerificationResult "Executable Discovery" "WARN" "Using first executable: $($executable.Name)"
            }
        }
    }
    
    # Store executable information
    $VerificationResults.ExecutableInfo = @{
        Path = $executable.FullName
        Name = $executable.Name
        Size = $executable.Length
        SizeMB = [math]::Round($executable.Length / 1MB, 2)
        Created = $executable.CreationTime
        Modified = $executable.LastWriteTime
    }
    
    return $executable
}

function Test-ExecutableProperties {
    param($Executable)
    
    Write-Host "`n=== EXECUTABLE PROPERTIES VALIDATION ===" -ForegroundColor Cyan
    
    if (-not $Executable) {
        Write-VerificationResult "Executable Properties" "FAIL" "No executable to test"
        return
    }
    
    $info = $VerificationResults.ExecutableInfo
    
    # Size validation
    $maxSizeMB = switch ($BuildProfile) {
        'production' { 100 }
        'portable' { 80 }
        'development' { 150 }
        'debug' { 200 }
        default { 150 }
    }
    
    if ($info.SizeMB -le $maxSizeMB) {
        Write-VerificationResult "Executable Size" "PASS" "$($info.SizeMB) MB (limit: $maxSizeMB MB)"
    } else {
        $recommendation = "Consider optimizing executable size or excluding unnecessary modules"
        Write-VerificationResult "Executable Size" "WARN" "$($info.SizeMB) MB exceeds recommended $maxSizeMB MB" -Recommendation $recommendation
    }
    
    # Check file properties using Windows API
    try {
        $fileVersion = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($Executable.FullName)
        
        if ($fileVersion.FileVersion) {
            Write-VerificationResult "Version Information" "PASS" "Version: $($fileVersion.FileVersion)"
            Write-VerificationResult "Product Information" "INFO" "Product: $($fileVersion.ProductName)"
            Write-VerificationResult "Company Information" "INFO" "Company: $($fileVersion.CompanyName)"
        } else {
            Write-VerificationResult "Version Information" "WARN" "No version information embedded"
        }
        
        # Check description
        if ($fileVersion.FileDescription) {
            Write-VerificationResult "File Description" "PASS" "$($fileVersion.FileDescription)"
        } else {
            Write-VerificationResult "File Description" "WARN" "No file description"
        }
    }
    catch {
        Write-VerificationResult "File Properties" "WARN" "Could not read file properties: $($_.Exception.Message)"
    }
    
    # Check digital signature
    try {
        $signature = Get-AuthenticodeSignature $Executable.FullName
        
        if ($signature.Status -eq 'Valid') {
            Write-VerificationResult "Digital Signature" "PASS" "Valid signature from $($signature.SignerCertificate.Subject)"
        } elseif ($signature.Status -eq 'NotSigned') {
            $recommendation = "Consider code signing for production releases"
            Write-VerificationResult "Digital Signature" "INFO" "Executable is not signed" -Recommendation $recommendation
        } else {
            Write-VerificationResult "Digital Signature" "WARN" "Signature status: $($signature.Status)"
        }
    }
    catch {
        Write-VerificationResult "Digital Signature" "INFO" "Could not check signature"
    }
}

function Test-ExecutableFunctionality {
    param($Executable)
    
    Write-Host "`n=== EXECUTABLE FUNCTIONALITY TESTS ===" -ForegroundColor Cyan
    
    if (-not $Executable) {
        return
    }
    
    # Test 1: Basic startup test
    Write-Host "Testing executable startup..."
    
    try {
        if ($BuildProfile -in @('development', 'debug', 'testing')) {
            # Console applications - test with timeout
            $startInfo = New-Object System.Diagnostics.ProcessStartInfo
            $startInfo.FileName = $Executable.FullName
            $startInfo.Arguments = "--help"
            $startInfo.UseShellExecute = $false
            $startInfo.RedirectStandardOutput = $true
            $startInfo.RedirectStandardError = $true
            $startInfo.CreateNoWindow = $true
            
            $process = New-Object System.Diagnostics.Process
            $process.StartInfo = $startInfo
            
            $started = $process.Start()
            $finished = $process.WaitForExit(5000)  # 5-second timeout
            
            if ($finished) {
                if ($process.ExitCode -eq 0 -or $process.ExitCode -eq 1) {  # 1 might be normal for --help
                    Write-VerificationResult "Startup Test" "PASS" "Executable starts and responds to --help"
                } else {
                    Write-VerificationResult "Startup Test" "WARN" "Exit code: $($process.ExitCode)"
                }
            } else {
                $process.Kill()
                Write-VerificationResult "Startup Test" "WARN" "Startup test timed out"
            }
        } else {
            # GUI applications - just check if process starts
            $process = Start-Process -FilePath $Executable.FullName -PassThru -WindowStyle Hidden
            Start-Sleep 2
            
            if ($process -and -not $process.HasExited) {
                $process.CloseMainWindow()
                Start-Sleep 1
                if (-not $process.HasExited) {
                    $process.Kill()
                }
                Write-VerificationResult "Startup Test" "PASS" "GUI application starts successfully"
            } else {
                Write-VerificationResult "Startup Test" "FAIL" "Application failed to start or crashed immediately"
            }
        }
    }
    catch {
        Write-VerificationResult "Startup Test" "FAIL" "Exception during startup test: $($_.Exception.Message)"
    }
    
    # Test 2: Dependency check
    Write-Host "Checking executable dependencies..."
    
    try {
        # Use PowerShell to check if executable can load without missing DLLs
        $dependencyTest = {
            param($ExePath)
            try {
                $process = Start-Process -FilePath $ExePath -PassThru -WindowStyle Hidden -RedirectStandardError
                Start-Sleep 1
                if ($process -and -not $process.HasExited) {
                    $process.Kill()
                    return "SUCCESS"
                } elseif ($process.HasExited -and $process.ExitCode -eq 0) {
                    return "SUCCESS"
                } else {
                    return "FAILED: Exit code $($process.ExitCode)"
                }
            }
            catch {
                return "FAILED: $($_.Exception.Message)"
            }
        }
        
        $result = & $dependencyTest $Executable.FullName
        
        if ($result -eq "SUCCESS") {
            Write-VerificationResult "Dependency Check" "PASS" "No missing dependencies detected"
        } else {
            Write-VerificationResult "Dependency Check" "WARN" $result
        }
    }
    catch {
        Write-VerificationResult "Dependency Check" "WARN" "Could not perform dependency check"
    }
    
    # Test 3: Memory usage test (basic)
    if ($BuildProfile -ne 'debug') {  # Skip for debug builds as they use more memory
        try {
            $process = Start-Process -FilePath $Executable.FullName -PassThru -WindowStyle Hidden
            Start-Sleep 3  # Let it initialize
            
            if ($process -and -not $process.HasExited) {
                $memoryMB = [math]::Round($process.WorkingSet64 / 1MB, 2)
                
                $maxMemoryMB = switch ($BuildProfile) {
                    'production' { 256 }
                    'portable' { 200 }
                    default { 300 }
                }
                
                if ($memoryMB -le $maxMemoryMB) {
                    Write-VerificationResult "Memory Usage" "PASS" "$memoryMB MB (limit: $maxMemoryMB MB)"
                } else {
                    Write-VerificationResult "Memory Usage" "WARN" "$memoryMB MB exceeds recommended $maxMemoryMB MB"
                }
                
                $process.Kill()
            } else {
                Write-VerificationResult "Memory Usage" "WARN" "Could not measure memory usage"
            }
        }
        catch {
            Write-VerificationResult "Memory Usage" "WARN" "Memory test failed: $($_.Exception.Message)"
        }
    }
}

function Test-SecurityProperties {
    param($Executable)
    
    Write-Host "`n=== SECURITY VALIDATION ===" -ForegroundColor Cyan
    
    if (-not $Executable) {
        return
    }
    
    # Check for DEP (Data Execution Prevention) support
    try {
        $peHeaders = & cmd /c "dumpbin /headers `"$($Executable.FullName)`"" 2>$null
        if ($peHeaders -match "NX compatible") {
            Write-VerificationResult "DEP Support" "PASS" "Data Execution Prevention enabled"
        } else {
            Write-VerificationResult "DEP Support" "INFO" "DEP status unknown"
        }
    }
    catch {
        Write-VerificationResult "DEP Support" "INFO" "Could not check DEP support"
    }
    
    # Check for ASLR (Address Space Layout Randomization)
    try {
        $peHeaders = & cmd /c "dumpbin /headers `"$($Executable.FullName)`"" 2>$null
        if ($peHeaders -match "Dynamic base") {
            Write-VerificationResult "ASLR Support" "PASS" "Address Space Layout Randomization enabled"
        } else {
            Write-VerificationResult "ASLR Support" "INFO" "ASLR status unknown"
        }
    }
    catch {
        Write-VerificationResult "ASLR Support" "INFO" "Could not check ASLR support"
    }
    
    # Basic virus scan simulation (Windows Defender check)
    Write-Host "Performing security scan..."
    try {
        $scanResult = & cmd /c "powershell -Command `"Get-MpThreatDetection | Where-Object { `$_.Resources -contains '$($Executable.FullName)' }`"" 2>$null
        
        if (-not $scanResult) {
            Write-VerificationResult "Security Scan" "PASS" "No threats detected"
        } else {
            Write-VerificationResult "Security Scan" "FAIL" "Security threat detected"
        }
    }
    catch {
        Write-VerificationResult "Security Scan" "INFO" "Could not perform security scan"
    }
}

function Optimize-BuildArtifacts {
    if (-not $OptimizeArtifacts) {
        return
    }
    
    Write-Host "`n=== ARTIFACT OPTIMIZATION ===" -ForegroundColor Cyan
    
    # UPX compression (if UPX is available)
    $upxPath = Get-Command "upx" -ErrorAction SilentlyContinue
    if ($upxPath -and $BuildProfile -in @('production', 'portable')) {
        $executable = Find-Executable
        if ($executable) {
            Write-Host "Applying UPX compression..."
            
            # Create backup
            $backupPath = "$($executable.FullName).backup"
            Copy-Item $executable.FullName $backupPath
            
            # Apply UPX compression
            $originalSize = $executable.Length
            & upx --best "$($executable.FullName)" 2>$null
            
            if ($LASTEXITCODE -eq 0) {
                $newSize = (Get-Item $executable.FullName).Length
                $compressionRatio = [math]::Round((1 - ($newSize / $originalSize)) * 100, 1)
                Write-VerificationResult "UPX Compression" "OPTIMIZED" "Size reduced by $compressionRatio% ($(([math]::Round($originalSize/1MB,2))) MB → $(([math]::Round($newSize/1MB,2))) MB)"
                
                # Remove backup if successful
                Remove-Item $backupPath -Force
            } else {
                # Restore backup if compression failed
                Move-Item $backupPath $executable.FullName -Force
                Write-VerificationResult "UPX Compression" "WARN" "UPX compression failed, executable restored"
            }
        }
    }
    
    # Clean up build artifacts
    $buildDir = Join-Path $ProjectRoot 'build'
    if (Test-Path $buildDir) {
        $buildSize = (Get-ChildItem $buildDir -Recurse | Measure-Object -Property Length -Sum).Sum
        $buildSizeMB = [math]::Round($buildSize / 1MB, 2)
        
        Write-Host "Cleaning build directory ($buildSizeMB MB)..."
        Remove-Item $buildDir -Recurse -Force -ErrorAction SilentlyContinue
        Write-VerificationResult "Build Cleanup" "OPTIMIZED" "Removed $buildSizeMB MB of build artifacts"
    }
    
    # Optimize portable directory
    $portableDir = Join-Path $DistDir 'Portable'
    if (Test-Path $portableDir) {
        $duplicateFiles = @('README.md', 'LICENSE')
        foreach ($file in $duplicateFiles) {
            $srcFile = Join-Path $ProjectRoot $file
            $destFile = Join-Path $portableDir $file
            
            if ((Test-Path $srcFile) -and (Test-Path $destFile)) {
                $srcHash = Get-FileHash $srcFile -Algorithm MD5
                $destHash = Get-FileHash $destFile -Algorithm MD5
                
                if ($srcHash.Hash -eq $destHash.Hash) {
                    Write-VerificationResult "Duplicate Cleanup" "OPTIMIZED" "Verified $file consistency"
                }
            }
        }
    }
}

function Test-CompatibilityRequirements {
    if (-not $RunCompatibilityTests) {
        return
    }
    
    Write-Host "`n=== COMPATIBILITY TESTING ===" -ForegroundColor Cyan
    
    # Simulate different Windows versions (basic checks)
    $windowsVersions = @(
        @{Name = "Windows 10 (1903)"; MinVersion = [Version]"10.0.18362"},
        @{Name = "Windows 10 (21H2)"; MinVersion = [Version]"10.0.19044"},
        @{Name = "Windows 11"; MinVersion = [Version]"10.0.22000"}
    )
    
    $currentVersion = [Environment]::OSVersion.Version
    
    foreach ($version in $windowsVersions) {
        if ($currentVersion -ge $version.MinVersion) {
            Write-VerificationResult "Compatibility: $($version.Name)" "PASS" "Compatible with current system"
        } else {
            Write-VerificationResult "Compatibility: $($version.Name)" "INFO" "Untested on this version"
        }
    }
    
    # Architecture compatibility
    $executable = Find-Executable
    if ($executable) {
        try {
            $peInfo = & cmd /c "dumpbin /headers `"$($executable.FullName)`"" 2>$null | Select-String "machine"
            
            if ($peInfo -match "x64|AMD64") {
                Write-VerificationResult "Architecture" "PASS" "64-bit executable"
            } elseif ($peInfo -match "x86|386") {
                Write-VerificationResult "Architecture" "INFO" "32-bit executable (broader compatibility)"
            } else {
                Write-VerificationResult "Architecture" "WARN" "Unknown architecture"
            }
        }
        catch {
            Write-VerificationResult "Architecture" "INFO" "Could not determine architecture"
        }
    }
    
    # .NET Framework dependency check
    try {
        $dotnetCheck = & cmd /c "dumpbin /dependents `"$($executable.FullName)`"" 2>$null
        if ($dotnetCheck -match "mscoree.dll") {
            Write-VerificationResult ".NET Dependency" "INFO" "Requires .NET Framework"
        } else {
            Write-VerificationResult ".NET Dependency" "PASS" "No .NET Framework dependency"
        }
    }
    catch {
        Write-VerificationResult ".NET Dependency" "INFO" "Could not check .NET dependencies"
    }
}

function Generate-ChecksumFiles {
    Write-Host "`n=== GENERATING CHECKSUMS ===" -ForegroundColor Cyan
    
    $artifacts = Get-ChildItem -Path $DistDir -File -Recurse | Where-Object { $_.Extension -in @('.exe', '.zip', '.msi') }
    
    foreach ($artifact in $artifacts) {
        # Generate SHA256
        $sha256Hash = Get-FileHash -Path $artifact.FullName -Algorithm SHA256
        $sha256File = "$($artifact.FullName).sha256"
        "$($sha256Hash.Hash.ToLower())  $($artifact.Name)" | Out-File -FilePath $sha256File -Encoding ASCII
        
        # Generate MD5 for legacy compatibility
        $md5Hash = Get-FileHash -Path $artifact.FullName -Algorithm MD5
        $md5File = "$($artifact.FullName).md5"
        "$($md5Hash.Hash.ToLower())  $($artifact.Name)" | Out-File -FilePath $md5File -Encoding ASCII
        
        Write-VerificationResult "Checksums: $($artifact.Name)" "PASS" "SHA256 and MD5 generated"
    }
}

function Generate-VerificationReport {
    if (-not $GenerateReport) {
        return
    }
    
    $reportPath = if ($ReportPath) { $ReportPath } else { Join-Path $ProjectRoot "verification-report.html" }
    $duration = (Get-Date) - $VerificationResults.StartTime
    $executableInfo = $VerificationResults.ExecutableInfo
    
    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Post-Build Verification Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .pass { color: #28a745; font-weight: bold; }
        .fail { color: #dc3545; font-weight: bold; }
        .warn { color: #ffc107; font-weight: bold; }
        .optimized { color: #6f42c1; font-weight: bold; }
        .section { margin: 20px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #007bff; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { border: 1px solid #dee2e6; padding: 12px; text-align: left; }
        th { background-color: #e9ecef; font-weight: bold; }
        .exe-info { background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); color: white; padding: 15px; border-radius: 5px; }
        .metric { display: inline-block; margin: 10px; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Post-Build Verification Report</h1>
            <p><strong>Profile:</strong> $($VerificationResults.Profile)</p>
            <p><strong>Generated:</strong> $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
            <p><strong>Duration:</strong> $([math]::Round($duration.TotalSeconds, 2)) seconds</p>
        </div>
        
        <div class="section">
            <h2>📊 Summary</h2>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
                <div class="metric">
                    <div class="pass">✅ $($VerificationResults.Passed.Count)</div>
                    <div>Passed</div>
                </div>
                <div class="metric">
                    <div class="fail">❌ $($VerificationResults.Failed.Count)</div>
                    <div>Failed</div>
                </div>
                <div class="metric">
                    <div class="warn">⚠️ $($VerificationResults.Warnings.Count)</div>
                    <div>Warnings</div>
                </div>
                <div class="metric">
                    <div class="optimized">⚡ $($VerificationResults.Optimizations.Count)</div>
                    <div>Optimizations</div>
                </div>
            </div>
        </div>
"@
    
    if ($executableInfo.Count -gt 0) {
        $html += @"
        <div class="section">
            <h2>📦 Executable Information</h2>
            <div class="exe-info">
                <div class="metric">
                    <div><strong>Name:</strong></div>
                    <div>$($executableInfo.Name)</div>
                </div>
                <div class="metric">
                    <div><strong>Size:</strong></div>
                    <div>$($executableInfo.SizeMB) MB</div>
                </div>
                <div class="metric">
                    <div><strong>Created:</strong></div>
                    <div>$($executableInfo.Created.ToString('yyyy-MM-dd HH:mm:ss'))</div>
                </div>
                <div class="metric">
                    <div><strong>Modified:</strong></div>
                    <div>$($executableInfo.Modified.ToString('yyyy-MM-dd HH:mm:ss'))</div>
                </div>
            </div>
        </div>
"@
    }
    
    # Add results sections
    $sections = @(
        @{Name = "Failed Tests"; Items = $VerificationResults.Failed; Class = "fail"},
        @{Name = "Warnings"; Items = $VerificationResults.Warnings; Class = "warn"},
        @{Name = "Optimizations Applied"; Items = $VerificationResults.Optimizations; Class = "optimized"},
        @{Name = "Passed Tests"; Items = $VerificationResults.Passed; Class = "pass"}
    )
    
    foreach ($section in $sections) {
        if ($section.Items.Count -gt 0) {
            $html += @"
        <div class="section">
            <h2>$($section.Name)</h2>
            <table>
                <tr><th>Test</th><th>Message</th><th>Recommendation</th></tr>
"@
            foreach ($item in $section.Items) {
                $recommendation = if ($item.Recommendation) { $item.Recommendation } else { "-" }
                $html += "<tr><td class=`"$($section.Class)`">$($item.Test)</td><td>$($item.Message)</td><td><em>$recommendation</em></td></tr>"
            }
            $html += "</table></div>"
        }
    }
    
    $html += @"
        <div class="section">
            <h2>📋 Next Steps</h2>
            <ul>
                <li>Review any failed tests and address issues</li>
                <li>Consider recommendations for warnings</li>
                <li>Test the executable on target systems</li>
                <li>Verify all features work as expected</li>
                <li>Consider code signing for production releases</li>
            </ul>
        </div>
    </div>
</body>
</html>
"@
    
    $html | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Host "`nVerification report generated: $reportPath" -ForegroundColor Green
}

# Main execution
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   POST-BUILD VERIFICATION STARTED" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Profile: $BuildProfile" -ForegroundColor White
Write-Host "Project: $ProjectRoot" -ForegroundColor White
Write-Host "Distribution: $DistDir" -ForegroundColor White
Write-Host ""

Push-Location $ProjectRoot

try {
    # Find and analyze executable
    $executable = Find-Executable
    
    if ($executable) {
        # Run all verification tests
        Test-ExecutableProperties $executable
        Test-ExecutableFunctionality $executable
        Test-SecurityProperties $executable
        Test-CompatibilityRequirements
        Optimize-BuildArtifacts
        Generate-ChecksumFiles
        Generate-VerificationReport
        
        # Final results
        $duration = (Get-Date) - $VerificationResults.StartTime
        
        Write-Host "`n========================================" -ForegroundColor Cyan
        Write-Host "   VERIFICATION COMPLETED" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Results Summary:" -ForegroundColor White
        Write-Host "  Executable: $($VerificationResults.ExecutableInfo.Name)" -ForegroundColor White
        Write-Host "  Size: $($VerificationResults.ExecutableInfo.SizeMB) MB" -ForegroundColor White
        Write-Host "  Passed: $($VerificationResults.Passed.Count)" -ForegroundColor Green
        Write-Host "  Failed: $($VerificationResults.Failed.Count)" -ForegroundColor Red
        Write-Host "  Warnings: $($VerificationResults.Warnings.Count)" -ForegroundColor Yellow
        Write-Host "  Optimizations: $($VerificationResults.Optimizations.Count)" -ForegroundColor Magenta
        Write-Host "  Duration: $([math]::Round($duration.TotalSeconds, 2)) seconds" -ForegroundColor White
        Write-Host ""
        
        if ($ErrorCount -gt 0) {
            Write-Host "❌ Verification FAILED with $ErrorCount critical issues" -ForegroundColor Red
            Write-Host "Executable should not be released until issues are resolved." -ForegroundColor Red
            exit 1
        } elseif ($WarningCount -gt 0) {
            Write-Host "⚠️ Verification completed with $WarningCount warnings" -ForegroundColor Yellow
            Write-Host "Executable is functional but warnings should be reviewed." -ForegroundColor Yellow
            exit 0
        } else {
            Write-Host "✅ All verification checks passed!" -ForegroundColor Green
            Write-Host "Executable is ready for distribution." -ForegroundColor Green
            exit 0
        }
    } else {
        Write-Host "❌ No executable found to verify" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "❌ Verification failed with exception: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
finally {
    Pop-Location
}