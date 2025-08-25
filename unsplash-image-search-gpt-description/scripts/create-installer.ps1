#Requires -Version 5.1

<#
.SYNOPSIS
    Automated installer creation script for Unsplash GPT Tool

.DESCRIPTION
    Creates Windows installers using NSIS and/or Inno Setup with automatic configuration
    generation, dependency checking, and installation testing.

.PARAMETER InstallerType
    Type of installer to create: NSIS, InnoSetup, or Both

.PARAMETER ExecutablePath
    Path to the executable to package (auto-detected if not specified)

.PARAMETER Version
    Version string to use in installer (auto-detected from executable if not specified)

.PARAMETER OutputDir
    Directory to place generated installers (defaults to project root)

.PARAMETER TestInstaller
    Test the created installer in a sandbox environment

.PARAMETER CreatePortableInstaller
    Create a portable/self-extracting version

.EXAMPLE
    .\create-installer.ps1 -InstallerType Both -TestInstaller

.NOTES
    Requires NSIS (makensis.exe) and/or Inno Setup (iscc.exe) to be in PATH
#>

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet('NSIS', 'InnoSetup', 'Both')]
    [string]$InstallerType = 'Both',
    
    [Parameter()]
    [string]$ExecutablePath,
    
    [Parameter()]
    [string]$Version,
    
    [Parameter()]
    [string]$OutputDir,
    
    [Parameter()]
    [switch]$TestInstaller,
    
    [Parameter()]
    [switch]$CreatePortableInstaller
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$DistDir = Join-Path $ProjectRoot 'dist'
$InstallerDir = Join-Path $ProjectRoot 'installer'
$ScriptsDir = Join-Path $ProjectRoot 'scripts'

$InstallerResults = @{
    Created = @()
    Failed = @()
    Tested = @()
    StartTime = Get-Date
}

function Write-InstallerLog {
    param(
        [string]$Message,
        [ValidateSet('INFO', 'SUCCESS', 'WARNING', 'ERROR')]
        [string]$Level = 'INFO'
    )
    
    $timestamp = Get-Date -Format 'HH:mm:ss'
    $color = switch ($Level) {
        'SUCCESS' { 'Green' }
        'WARNING' { 'Yellow' }
        'ERROR' { 'Red' }
        default { 'White' }
    }
    
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Get-ApplicationInfo {
    Write-InstallerLog "Gathering application information..."
    
    # Find executable
    if ($ExecutablePath -and (Test-Path $ExecutablePath)) {
        $executable = Get-Item $ExecutablePath
    } else {
        $executables = Get-ChildItem -Path $DistDir -Filter "*.exe" | Where-Object { 
            $_.Name -notmatch 'setup|install|debug|test' 
        }
        if ($executables.Count -gt 0) {
            $executable = $executables[0]
        } else {
            throw "No executable found in $DistDir"
        }
    }
    
    Write-InstallerLog "Found executable: $($executable.Name)" -Level SUCCESS
    
    # Get version information
    $versionInfo = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($executable.FullName)
    $appVersion = if ($Version) { 
        $Version 
    } elseif ($versionInfo.FileVersion) { 
        $versionInfo.FileVersion 
    } else { 
        "1.0.0" 
    }
    
    # Load additional info from version_info.py if available
    $versionInfoPy = Join-Path $ProjectRoot 'version_info.py'
    $appInfo = @{
        ExecutablePath = $executable.FullName
        ExecutableName = $executable.Name
        ExecutableBaseName = $executable.BaseName
        Version = $appVersion
        Size = $executable.Length
        SizeMB = [math]::Round($executable.Length / 1MB, 2)
        AppName = "Unsplash Image Search & GPT Tool"
        Publisher = "Language Learning Tools"
        AppID = "UnsplashGPTTool"
        Description = "AI-powered image search and Spanish vocabulary learning tool"
        Website = "https://github.com/yourusername/unsplash-image-search-gpt"
        SupportURL = "https://github.com/yourusername/unsplash-image-search-gpt/issues"
        UpdateURL = "https://github.com/yourusername/unsplash-image-search-gpt/releases"
    }
    
    if (Test-Path $versionInfoPy) {
        try {
            $versionContent = Get-Content $versionInfoPy -Raw
            if ($versionContent -match 'APP_NAME\s*=\s*["\']([^"\']+)["\']') {
                $appInfo.AppName = $matches[1]
            }
            if ($versionContent -match 'COMPANY_NAME\s*=\s*["\']([^"\']+)["\']') {
                $appInfo.Publisher = $matches[1]
            }
            if ($versionContent -match 'APP_DESCRIPTION\s*=\s*["\']([^"\']+)["\']') {
                $appInfo.Description = $matches[1]
            }
        }
        catch {
            Write-InstallerLog "Could not read version_info.py: $($_.Exception.Message)" -Level WARNING
        }
    }
    
    Write-InstallerLog "Application: $($appInfo.AppName) v$($appInfo.Version)"
    Write-InstallerLog "Executable size: $($appInfo.SizeMB) MB"
    
    return $appInfo
}

function Test-InstallerTools {
    Write-InstallerLog "Checking installer creation tools..."
    
    $availableTools = @{}
    
    # Check NSIS
    $nsisPath = Get-Command "makensis" -ErrorAction SilentlyContinue
    if ($nsisPath) {
        try {
            $nsisVersion = & makensis /VERSION 2>$null
            $availableTools.NSIS = @{
                Path = $nsisPath.Source
                Version = $nsisVersion.Trim()
                Available = $true
            }
            Write-InstallerLog "NSIS found: $($nsisVersion.Trim())" -Level SUCCESS
        }
        catch {
            $availableTools.NSIS = @{ Available = $false }
            Write-InstallerLog "NSIS found but version check failed" -Level WARNING
        }
    } else {
        $availableTools.NSIS = @{ Available = $false }
        Write-InstallerLog "NSIS not found in PATH" -Level WARNING
    }
    
    # Check Inno Setup
    $innoPath = Get-Command "iscc" -ErrorAction SilentlyContinue
    if ($innoPath) {
        try {
            $innoVersion = & iscc /? 2>$null | Select-String "Inno Setup" | Select-Object -First 1
            $availableTools.InnoSetup = @{
                Path = $innoPath.Source
                Version = if ($innoVersion) { $innoVersion.ToString().Trim() } else { "Unknown" }
                Available = $true
            }
            Write-InstallerLog "Inno Setup found: $($innoPath.Source)" -Level SUCCESS
        }
        catch {
            $availableTools.InnoSetup = @{ Available = $false }
            Write-InstallerLog "Inno Setup found but version check failed" -Level WARNING
        }
    } else {
        $availableTools.InnoSetup = @{ Available = $false }
        Write-InstallerLog "Inno Setup not found in PATH" -Level WARNING
    }
    
    return $availableTools
}

function New-NSISScript {
    param($AppInfo, $OutputPath)
    
    Write-InstallerLog "Generating NSIS installer script..."
    
    # Ensure installer directory exists
    if (-not (Test-Path $InstallerDir)) {
        New-Item -Path $InstallerDir -ItemType Directory -Force | Out-Null
    }
    
    $nsisScript = @"
; NSIS Script for $($AppInfo.AppName)
; Auto-generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

!include MUI2.nsh
!include FileFunc.nsh
!include LogicLib.nsh

; General settings
Name "$($AppInfo.AppName)"
OutFile "$OutputPath"
Unicode True
InstallDir `$PROGRAMFILES64\$($AppInfo.AppName.Replace(' ', ''))
InstallDirRegKey HKLM "Software\$($AppInfo.Publisher)\$($AppInfo.AppName)" "InstallDir"
RequestExecutionLevel admin

; Version information
VIProductVersion "$($AppInfo.Version).0"
VIAddVersionKey "ProductName" "$($AppInfo.AppName)"
VIAddVersionKey "ProductVersion" "$($AppInfo.Version)"
VIAddVersionKey "CompanyName" "$($AppInfo.Publisher)"
VIAddVersionKey "FileDescription" "$($AppInfo.Description)"
VIAddVersionKey "LegalCopyright" "© 2024 $($AppInfo.Publisher)"

; Modern UI Configuration
!define MUI_ABORTWARNING
!define MUI_ICON "`${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "`${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Welcome page
!define MUI_WELCOMEPAGE_TITLE "Welcome to $($AppInfo.AppName) Setup"
!define MUI_WELCOMEPAGE_TEXT "This wizard will guide you through the installation of $($AppInfo.AppName).$\r$\n$\r$\n$($AppInfo.Description)$\r$\n$\r$\nClick Next to continue."

; License page (if license file exists)
!ifdef LICENSE_FILE
!insertmacro MUI_PAGE_LICENSE "`${LICENSE_FILE}"
!endif

; Directory page
!insertmacro MUI_PAGE_DIRECTORY

; Components page
!insertmacro MUI_PAGE_COMPONENTS

; Installation page
!insertmacro MUI_PAGE_INSTFILES

; Finish page
!define MUI_FINISHPAGE_RUN "`$INSTDIR\$($AppInfo.ExecutableName)"
!define MUI_FINISHPAGE_RUN_TEXT "Launch $($AppInfo.AppName)"
!define MUI_FINISHPAGE_LINK "Visit our website"
!define MUI_FINISHPAGE_LINK_LOCATION "$($AppInfo.Website)"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installation sections
Section "Core Application" SEC_CORE
    SectionIn RO
    
    ; Set output path
    SetOutPath "`$INSTDIR"
    
    ; Install main executable
    File "$($AppInfo.ExecutablePath)"
    
    ; Install additional files if they exist
    IfFileExists "$($ProjectRoot)\README.md" 0 +2
    File "$($ProjectRoot)\README.md"
    
    IfFileExists "$($ProjectRoot)\LICENSE" 0 +2
    File "$($ProjectRoot)\LICENSE"
    
    ; Create uninstaller
    WriteUninstaller "`$INSTDIR\Uninstall.exe"
    
    ; Registry entries
    WriteRegStr HKLM "Software\$($AppInfo.Publisher)\$($AppInfo.AppName)" "InstallDir" "`$INSTDIR"
    WriteRegStr HKLM "Software\$($AppInfo.Publisher)\$($AppInfo.AppName)" "Version" "$($AppInfo.Version)"
    
    ; Add/Remove Programs registry entries
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\$($AppInfo.AppID)" "DisplayName" "$($AppInfo.AppName)"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\$($AppInfo.AppID)" "DisplayVersion" "$($AppInfo.Version)"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\$($AppInfo.AppID)" "Publisher" "$($AppInfo.Publisher)"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\$($AppInfo.AppID)" "UninstallString" "`$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\$($AppInfo.AppID)" "InstallLocation" "`$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\$($AppInfo.AppID)" "DisplayIcon" "`$INSTDIR\$($AppInfo.ExecutableName)"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\$($AppInfo.AppID)" "HelpLink" "$($AppInfo.SupportURL)"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\$($AppInfo.AppID)" "URLUpdateInfo" "$($AppInfo.UpdateURL)"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\$($AppInfo.AppID)" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\$($AppInfo.AppID)" "NoRepair" 1
    
    ; Estimate size
    `${GetSize} "`$INSTDIR" "/S=0K" `$0 `$1 `$2
    IntFmt `$0 "0x%08X" `$0
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\$($AppInfo.AppID)" "EstimatedSize" "`$0"
    
SectionEnd

Section "Start Menu Shortcuts" SEC_SHORTCUTS
    CreateDirectory "`$SMPROGRAMS\$($AppInfo.AppName)"
    CreateShortcut "`$SMPROGRAMS\$($AppInfo.AppName)\$($AppInfo.AppName).lnk" "`$INSTDIR\$($AppInfo.ExecutableName)" "" "`$INSTDIR\$($AppInfo.ExecutableName)" 0
    CreateShortcut "`$SMPROGRAMS\$($AppInfo.AppName)\Uninstall.lnk" "`$INSTDIR\Uninstall.exe"
    
    ; Desktop shortcut
    CreateShortcut "`$DESKTOP\$($AppInfo.AppName).lnk" "`$INSTDIR\$($AppInfo.ExecutableName)"
SectionEnd

Section "File Associations" SEC_ASSOC
    ; Add file associations if needed
    ; WriteRegStr HKCR ".ext" "" "$($AppInfo.AppID)File"
SectionEnd

; Section descriptions
LangString DESC_SEC_CORE `${LANG_ENGLISH} "Core application files (required)"
LangString DESC_SEC_SHORTCUTS `${LANG_ENGLISH} "Start Menu and Desktop shortcuts"
LangString DESC_SEC_ASSOC `${LANG_ENGLISH} "File type associations"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT `${SEC_CORE} `$(DESC_SEC_CORE)
    !insertmacro MUI_DESCRIPTION_TEXT `${SEC_SHORTCUTS} `$(DESC_SEC_SHORTCUTS)
    !insertmacro MUI_DESCRIPTION_TEXT `${SEC_ASSOC} `$(DESC_SEC_ASSOC)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller section
Section "Uninstall"
    ; Remove files
    Delete "`$INSTDIR\$($AppInfo.ExecutableName)"
    Delete "`$INSTDIR\README.md"
    Delete "`$INSTDIR\LICENSE"
    Delete "`$INSTDIR\Uninstall.exe"
    
    ; Remove shortcuts
    Delete "`$SMPROGRAMS\$($AppInfo.AppName)\$($AppInfo.AppName).lnk"
    Delete "`$SMPROGRAMS\$($AppInfo.AppName)\Uninstall.lnk"
    RMDir "`$SMPROGRAMS\$($AppInfo.AppName)"
    Delete "`$DESKTOP\$($AppInfo.AppName).lnk"
    
    ; Remove registry entries
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\$($AppInfo.AppID)"
    DeleteRegKey HKLM "Software\$($AppInfo.Publisher)\$($AppInfo.AppName)"
    
    ; Remove installation directory
    RMDir "`$INSTDIR"
SectionEnd

; Functions
Function .onInit
    ; Check Windows version
    `${IfNot} `${AtLeastWin10}
        MessageBox MB_OK|MB_ICONSTOP "This application requires Windows 10 or later."
        Quit
    `${EndIf}
    
    ; Check if already installed
    ReadRegStr `$R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\$($AppInfo.AppID)" "UninstallString"
    StrCmp `$R0 "" done
    
    MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION "$($AppInfo.AppName) is already installed. `$\n`$\nClick OK to remove the previous version or Cancel to cancel this upgrade." /SD IDOK IDOK uninst
    Abort
    
uninst:
    ClearErrors
    ExecWait '`$R0 /S _?=`$INSTDIR'
    IfErrors no_remove_uninstaller done
    IfFileExists "`$INSTDIR\Uninstall.exe" 0 no_remove_uninstaller
    Delete "`$R0"
    RMDir "`$INSTDIR"
    
no_remove_uninstaller:
done:
FunctionEnd
"@

    $scriptPath = Join-Path $InstallerDir "installer.nsi"
    $nsisScript | Out-File -FilePath $scriptPath -Encoding UTF8
    
    Write-InstallerLog "NSIS script generated: $scriptPath" -Level SUCCESS
    return $scriptPath
}

function New-InnoSetupScript {
    param($AppInfo, $OutputPath)
    
    Write-InstallerLog "Generating Inno Setup installer script..."
    
    # Ensure installer directory exists
    if (-not (Test-Path $InstallerDir)) {
        New-Item -Path $InstallerDir -ItemType Directory -Force | Out-Null
    }
    
    $innoScript = @"
; Inno Setup Script for $($AppInfo.AppName)
; Auto-generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

[Setup]
AppId={{$([System.Guid]::NewGuid().ToString().ToUpper())}
AppName=$($AppInfo.AppName)
AppVersion=$($AppInfo.Version)
AppPublisher=$($AppInfo.Publisher)
AppPublisherURL=$($AppInfo.Website)
AppSupportURL=$($AppInfo.SupportURL)
AppUpdatesURL=$($AppInfo.UpdateURL)
DefaultDirName={autopf}\$($AppInfo.AppName.Replace(' ', ''))
DefaultGroupName=$($AppInfo.AppName)
AllowNoIcons=yes
OutputDir=$($OutputDir -replace '\\', '/')
OutputBaseFilename=$([System.IO.Path]::GetFileNameWithoutExtension($OutputPath))
SetupIconFile={srcexe}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
MinVersion=10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "$($AppInfo.ExecutablePath -replace '\\', '\\')"; DestDir: "{app}"; Flags: ignoreversion
"@

    # Add optional files if they exist
    $optionalFiles = @('README.md', 'LICENSE', 'CHANGELOG.md')
    foreach ($file in $optionalFiles) {
        $filePath = Join-Path $ProjectRoot $file
        if (Test-Path $filePath) {
            $innoScript += "`nSource: `"$($filePath -replace '\\', '\\')`"; DestDir: `"{app}`"; Flags: ignoreversion"
        }
    }

    $innoScript += @"

[Icons]
Name: "{group}\$($AppInfo.AppName)"; Filename: "{app}\$($AppInfo.ExecutableName)"
Name: "{group}\{cm:UninstallProgram,$($AppInfo.AppName)}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\$($AppInfo.AppName)"; Filename: "{app}\$($AppInfo.ExecutableName)"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\$($AppInfo.AppName)"; Filename: "{app}\$($AppInfo.ExecutableName)"; Tasks: quicklaunchicon

[Registry]
Root: HKLM; Subkey: "Software\$($AppInfo.Publisher)\$($AppInfo.AppName)"; ValueType: string; ValueName: "InstallDir"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\$($AppInfo.Publisher)\$($AppInfo.AppName)"; ValueType: string; ValueName: "Version"; ValueData: "$($AppInfo.Version)"; Flags: uninsdeletekey

[Run]
Filename: "{app}\$($AppInfo.ExecutableName)"; Description: "{cm:LaunchProgram,$($AppInfo.AppName)}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);
  if Version.Major < 10 then
  begin
    MsgBox('This application requires Windows 10 or later.', mbCriticalError, MB_OK);
    Result := False;
  end
  else
    Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    { Add any post-installation tasks here }
  end;
end;
"@

    $scriptPath = Join-Path $InstallerDir "installer.iss"
    $innoScript | Out-File -FilePath $scriptPath -Encoding UTF8
    
    Write-InstallerLog "Inno Setup script generated: $scriptPath" -Level SUCCESS
    return $scriptPath
}

function Invoke-NSISBuild {
    param($ScriptPath, $AppInfo)
    
    Write-InstallerLog "Building NSIS installer..."
    
    try {
        # Build the installer
        $output = & makensis $ScriptPath 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            # Find the created installer
            $installerName = "$($AppInfo.AppName.Replace(' ', '_'))_Setup_v$($AppInfo.Version).exe"
            $installerPath = Join-Path $OutputDir $installerName
            
            if (Test-Path $installerPath) {
                $installerSize = (Get-Item $installerPath).Length
                $installerSizeMB = [math]::Round($installerSize / 1MB, 2)
                
                $InstallerResults.Created += @{
                    Type = 'NSIS'
                    Path = $installerPath
                    Name = $installerName
                    Size = $installerSize
                    SizeMB = $installerSizeMB
                }
                
                Write-InstallerLog "NSIS installer created successfully: $installerName ($installerSizeMB MB)" -Level SUCCESS
                return $installerPath
            } else {
                Write-InstallerLog "NSIS build succeeded but installer not found" -Level ERROR
                return $null
            }
        } else {
            Write-InstallerLog "NSIS build failed:" -Level ERROR
            $output | ForEach-Object { Write-InstallerLog "  $_" -Level ERROR }
            return $null
        }
    }
    catch {
        Write-InstallerLog "NSIS build exception: $($_.Exception.Message)" -Level ERROR
        return $null
    }
}

function Invoke-InnoSetupBuild {
    param($ScriptPath, $AppInfo)
    
    Write-InstallerLog "Building Inno Setup installer..."
    
    try {
        # Build the installer
        $output = & iscc $ScriptPath 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            # Find the created installer
            $installerName = "$($AppInfo.AppName.Replace(' ', '_'))_Setup_v$($AppInfo.Version).exe"
            $installerPath = Join-Path $OutputDir $installerName
            
            if (Test-Path $installerPath) {
                $installerSize = (Get-Item $installerPath).Length
                $installerSizeMB = [math]::Round($installerSize / 1MB, 2)
                
                $InstallerResults.Created += @{
                    Type = 'InnoSetup'
                    Path = $installerPath
                    Name = $installerName
                    Size = $installerSize
                    SizeMB = $installerSizeMB
                }
                
                Write-InstallerLog "Inno Setup installer created successfully: $installerName ($installerSizeMB MB)" -Level SUCCESS
                return $installerPath
            } else {
                Write-InstallerLog "Inno Setup build succeeded but installer not found" -Level ERROR
                return $null
            }
        } else {
            Write-InstallerLog "Inno Setup build failed:" -Level ERROR
            $output | ForEach-Object { Write-InstallerLog "  $_" -Level ERROR }
            return $null
        }
    }
    catch {
        Write-InstallerLog "Inno Setup build exception: $($_.Exception.Message)" -Level ERROR
        return $null
    }
}

function New-PortableInstaller {
    param($AppInfo)
    
    if (-not $CreatePortableInstaller) {
        return
    }
    
    Write-InstallerLog "Creating portable installer..."
    
    try {
        $portableDir = Join-Path $DistDir "Portable"
        $portableName = "$($AppInfo.AppName.Replace(' ', '_'))_Portable_v$($AppInfo.Version).exe"
        $portablePath = Join-Path $OutputDir $portableName
        
        if (Test-Path $portableDir) {
            # Create self-extracting archive using 7-Zip if available
            $sevenZipPath = Get-Command "7z" -ErrorAction SilentlyContinue
            if ($sevenZipPath) {
                & 7z a -sfx7z.sfx "$portablePath" "$portableDir\*" 2>$null
                
                if ($LASTEXITCODE -eq 0) {
                    $portableSize = (Get-Item $portablePath).Length
                    $portableSizeMB = [math]::Round($portableSize / 1MB, 2)
                    
                    $InstallerResults.Created += @{
                        Type = 'Portable'
                        Path = $portablePath
                        Name = $portableName
                        Size = $portableSize
                        SizeMB = $portableSizeMB
                    }
                    
                    Write-InstallerLog "Portable installer created: $portableName ($portableSizeMB MB)" -Level SUCCESS
                } else {
                    Write-InstallerLog "Failed to create portable installer with 7-Zip" -Level ERROR
                }
            } else {
                Write-InstallerLog "7-Zip not found, skipping portable installer" -Level WARNING
            }
        } else {
            Write-InstallerLog "Portable directory not found: $portableDir" -Level WARNING
        }
    }
    catch {
        Write-InstallerLog "Portable installer creation failed: $($_.Exception.Message)" -Level ERROR
    }
}

function Test-InstallerFunctionality {
    if (-not $TestInstaller) {
        return
    }
    
    Write-InstallerLog "Testing created installers..."
    
    foreach ($installer in $InstallerResults.Created) {
        if ($installer.Type -in @('NSIS', 'InnoSetup')) {
            Write-InstallerLog "Testing $($installer.Type) installer: $($installer.Name)"
            
            try {
                # Basic validation - check if installer starts
                $testProcess = Start-Process -FilePath $installer.Path -ArgumentList "/?" -Wait -PassThru -WindowStyle Hidden -ErrorAction Stop
                
                # Most installers return 0 or 1 for help command
                if ($testProcess.ExitCode -in @(0, 1, 2)) {
                    $InstallerResults.Tested += @{
                        Type = $installer.Type
                        Name = $installer.Name
                        Status = 'PASS'
                        Message = 'Installer responds to help command'
                    }
                    Write-InstallerLog "$($installer.Type) installer test PASSED" -Level SUCCESS
                } else {
                    $InstallerResults.Tested += @{
                        Type = $installer.Type
                        Name = $installer.Name
                        Status = 'WARN'
                        Message = "Unexpected exit code: $($testProcess.ExitCode)"
                    }
                    Write-InstallerLog "$($installer.Type) installer test WARNING: Exit code $($testProcess.ExitCode)" -Level WARNING
                }
            }
            catch {
                $InstallerResults.Tested += @{
                    Type = $installer.Type
                    Name = $installer.Name
                    Status = 'FAIL'
                    Message = $_.Exception.Message
                }
                Write-InstallerLog "$($installer.Type) installer test FAILED: $($_.Exception.Message)" -Level ERROR
            }
        }
    }
}

function New-InstallerChecksums {
    Write-InstallerLog "Generating checksums for installers..."
    
    foreach ($installer in $InstallerResults.Created) {
        try {
            # Generate SHA256 checksum
            $sha256 = Get-FileHash -Path $installer.Path -Algorithm SHA256
            $checksumPath = "$($installer.Path).sha256"
            "$($sha256.Hash.ToLower())  $($installer.Name)" | Out-File -FilePath $checksumPath -Encoding ASCII
            
            Write-InstallerLog "Checksum generated for $($installer.Name)" -Level SUCCESS
        }
        catch {
            Write-InstallerLog "Failed to generate checksum for $($installer.Name): $($_.Exception.Message)" -Level ERROR
        }
    }
}

# Main execution
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   INSTALLER CREATION STARTED" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

try {
    # Set output directory
    if (-not $OutputDir) {
        $OutputDir = $ProjectRoot
    }
    
    Write-InstallerLog "Installer Type: $InstallerType"
    Write-InstallerLog "Output Directory: $OutputDir"
    
    # Get application information
    $appInfo = Get-ApplicationInfo
    
    # Check available installer tools
    $installerTools = Test-InstallerTools
    
    # Validate installer type availability
    if ($InstallerType -in @('NSIS', 'Both') -and -not $installerTools.NSIS.Available) {
        if ($InstallerType -eq 'NSIS') {
            throw "NSIS not available but specifically requested"
        } else {
            Write-InstallerLog "NSIS not available, will only create Inno Setup installer" -Level WARNING
            $InstallerType = 'InnoSetup'
        }
    }
    
    if ($InstallerType -in @('InnoSetup', 'Both') -and -not $installerTools.InnoSetup.Available) {
        if ($InstallerType -eq 'InnoSetup') {
            throw "Inno Setup not available but specifically requested"
        } else {
            Write-InstallerLog "Inno Setup not available, will only create NSIS installer" -Level WARNING
            $InstallerType = 'NSIS'
        }
    }
    
    if ($InstallerType -eq 'Both' -and -not $installerTools.NSIS.Available -and -not $installerTools.InnoSetup.Available) {
        throw "Neither NSIS nor Inno Setup available"
    }
    
    # Create NSIS installer
    if ($InstallerType -in @('NSIS', 'Both') -and $installerTools.NSIS.Available) {
        $nsisOutputPath = Join-Path $OutputDir "$($appInfo.AppName.Replace(' ', '_'))_Setup_v$($appInfo.Version).exe"
        $nsisScript = New-NSISScript -AppInfo $appInfo -OutputPath $nsisOutputPath
        $nsisInstaller = Invoke-NSISBuild -ScriptPath $nsisScript -AppInfo $appInfo
        
        if ($nsisInstaller) {
            $InstallerResults.Created += @{
                Type = 'NSIS'
                Path = $nsisInstaller
                Name = [System.IO.Path]::GetFileName($nsisInstaller)
                Size = (Get-Item $nsisInstaller).Length
            }
        } else {
            $InstallerResults.Failed += @{Type = 'NSIS'; Reason = 'Build failed'}
        }
    }
    
    # Create Inno Setup installer
    if ($InstallerType -in @('InnoSetup', 'Both') -and $installerTools.InnoSetup.Available) {
        $innoOutputPath = Join-Path $OutputDir "$($appInfo.AppName.Replace(' ', '_'))_Setup_v$($appInfo.Version).exe"
        $innoScript = New-InnoSetupScript -AppInfo $appInfo -OutputPath $innoOutputPath
        $innoInstaller = Invoke-InnoSetupBuild -ScriptPath $innoScript -AppInfo $appInfo
        
        if ($innoInstaller) {
            $InstallerResults.Created += @{
                Type = 'InnoSetup'
                Path = $innoInstaller
                Name = [System.IO.Path]::GetFileName($innoInstaller)
                Size = (Get-Item $innoInstaller).Length
            }
        } else {
            $InstallerResults.Failed += @{Type = 'InnoSetup'; Reason = 'Build failed'}
        }
    }
    
    # Create portable installer if requested
    New-PortableInstaller -AppInfo $appInfo
    
    # Test installers
    Test-InstallerFunctionality
    
    # Generate checksums
    New-InstallerChecksums
    
    # Final results
    $duration = (Get-Date) - $InstallerResults.StartTime
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "   INSTALLER CREATION COMPLETED" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Results Summary:" -ForegroundColor White
    Write-Host "  Created: $($InstallerResults.Created.Count) installers" -ForegroundColor Green
    Write-Host "  Failed: $($InstallerResults.Failed.Count) installers" -ForegroundColor Red
    Write-Host "  Tested: $($InstallerResults.Tested.Count) installers" -ForegroundColor Cyan
    Write-Host "  Duration: $([math]::Round($duration.TotalSeconds, 2)) seconds" -ForegroundColor White
    Write-Host ""
    
    if ($InstallerResults.Created.Count -gt 0) {
        Write-Host "Created Installers:" -ForegroundColor Green
        foreach ($installer in $InstallerResults.Created) {
            $sizeMB = [math]::Round($installer.Size / 1MB, 2)
            Write-Host "  [$($installer.Type)] $($installer.Name) ($sizeMB MB)" -ForegroundColor White
        }
        Write-Host ""
    }
    
    if ($InstallerResults.Failed.Count -gt 0) {
        Write-Host "Failed Installers:" -ForegroundColor Red
        foreach ($failed in $InstallerResults.Failed) {
            Write-Host "  [$($failed.Type)] $($failed.Reason)" -ForegroundColor Red
        }
        Write-Host ""
    }
    
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Test installers on clean systems" -ForegroundColor White
    Write-Host "  2. Verify installation and uninstallation process" -ForegroundColor White
    Write-Host "  3. Test on different Windows versions" -ForegroundColor White
    Write-Host "  4. Consider code signing for production" -ForegroundColor White
    
    if ($InstallerResults.Created.Count -eq 0) {
        Write-Host "❌ No installers were created successfully" -ForegroundColor Red
        exit 1
    } else {
        Write-Host "✅ Installer creation completed successfully!" -ForegroundColor Green
        exit 0
    }
}
catch {
    Write-InstallerLog "Installer creation failed: $($_.Exception.Message)" -Level ERROR
    exit 1
}