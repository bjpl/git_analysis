# PowerShell script to create MSI wrapper for Group Policy deployment
# This script converts the Inno Setup installer to MSI format for enterprise deployment

param(
    [Parameter(Mandatory=$true)]
    [string]$InputExe,
    
    [Parameter(Mandatory=$true)]
    [string]$OutputMsi,
    
    [string]$ProductName = "Unsplash Image Search GPT Description",
    [string]$ProductVersion = "1.0.0",
    [string]$Manufacturer = "Image Search Tools",
    [string]$ProductCode = "{B8F4A2C1-9D3E-4F7A-8B2C-1E5A6D9F3C8B}",
    [string]$UpgradeCode = "{A7E3B1D0-8C2F-4E6A-9B1D-2F4E6A8C0E2F}"
)

# Check if WiX Toolset is installed
$wixPath = Get-Command "candle.exe" -ErrorAction SilentlyContinue
if (-not $wixPath) {
    Write-Error "WiX Toolset is required but not found in PATH. Please install WiX Toolset v3.11 or later."
    Write-Host "Download from: https://wixtoolset.org/releases/"
    exit 1
}

# Check if input file exists
if (-not (Test-Path $InputExe)) {
    Write-Error "Input file not found: $InputExe"
    exit 1
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$tempDir = Join-Path $env:TEMP "UnsplashImageSearchMSI"
$wxsFile = Join-Path $tempDir "installer.wxs"
$wixobjFile = Join-Path $tempDir "installer.wixobj"

# Create temporary directory
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

Write-Host "Creating MSI wrapper for $InputExe..."

# Create WiX source file
$wxsContent = @"
<?xml version='1.0' encoding='windows-1252'?>
<Wix xmlns='http://schemas.microsoft.com/wix/2006/wi'>
  <Product Name='$ProductName' 
           Id='$ProductCode'
           UpgradeCode='$UpgradeCode'
           Language='1033' 
           Codepage='1252' 
           Version='$ProductVersion' 
           Manufacturer='$Manufacturer'>

    <Package Id='*' 
             Keywords='Installer' 
             Description='$ProductName Installer'
             Comments='MSI wrapper for enterprise deployment'
             Manufacturer='$Manufacturer' 
             InstallerVersion='100' 
             Languages='1033' 
             Compressed='yes' 
             SummaryCodepage='1252' />

    <Media Id='1' Cabinet='media1.cab' EmbedCab='yes' />

    <!-- Upgrade settings -->
    <MajorUpgrade DowngradeErrorMessage="A newer version of $ProductName is already installed." />

    <!-- Directory structure -->
    <Directory Id='TARGETDIR' Name='SourceDir'>
      <Directory Id='ProgramFilesFolder'>
        <Directory Id='INSTALLFOLDER' Name='$ProductName'>
          <Component Id='MainExecutable' Guid='{D1E2F3A4-B5C6-7D8E-9F0A-1B2C3D4E5F6A}'>
            <File Id='InstallerExe' Name='setup.exe' Source='$InputExe' KeyPath='yes'>
              <Shortcut Id="DesktopShortcut"
                        Directory="DesktopFolder"
                        Name="$ProductName Setup"
                        WorkingDirectory="INSTALLFOLDER"
                        Icon="ApplicationIcon.exe"
                        IconIndex="0"
                        Advertise="yes" />
              <Shortcut Id="StartMenuShortcut"
                        Directory="ProgramMenuDir"
                        Name="$ProductName Setup"
                        WorkingDirectory="INSTALLFOLDER"
                        Icon="ApplicationIcon.exe"
                        IconIndex="0"
                        Advertise="yes" />
            </File>
          </Component>
        </Directory>
      </Directory>

      <Directory Id="ProgramMenuFolder">
        <Directory Id="ProgramMenuDir" Name="$ProductName" />
      </Directory>

      <Directory Id="DesktopFolder" />
    </Directory>

    <!-- Icon definition -->
    <Icon Id="ApplicationIcon.exe" SourceFile="$InputExe" />

    <!-- Features -->
    <Feature Id='Complete' Level='1' Title='$ProductName' Description='Complete installation'>
      <ComponentRef Id='MainExecutable' />
    </Feature>

    <!-- Custom actions to run the installer -->
    <CustomAction Id='RunInstaller'
                  FileKey='InstallerExe'
                  ExeCommand='/VERYSILENT /NORESTART /SP- /LOG="[%TEMP]\UnsplashImageSearch_Install.log"'
                  Execute='deferred'
                  Impersonate='no'
                  Return='check' />

    <CustomAction Id='SetRunInstallerArgs'
                  Property='RunInstaller'
                  Value='"/VERYSILENT /NORESTART /SP- /LOG="[%TEMP]\UnsplashImageSearch_Install.log""'
                  Execute='immediate' />

    <!-- Installation sequence -->
    <InstallExecuteSequence>
      <Custom Action='SetRunInstallerArgs' After='CostFinalize'>NOT Installed</Custom>
      <Custom Action='RunInstaller' After='InstallFiles'>NOT Installed</Custom>
    </InstallExecuteSequence>

    <!-- Uninstall custom action -->
    <CustomAction Id='UninstallApp'
                  Directory='INSTALLFOLDER'
                  ExeCommand='cmd.exe /c "for /f "tokens=*" %i in ('"'"'reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" /s /k /f "$ProductName"'"'"') do (for /f "tokens=2*" %j in ('"'"'reg query "%i" /v "UninstallString"'"'"') do ("%k" /VERYSILENT))"'
                  Execute='deferred'
                  Impersonate='no'
                  Return='ignore' />

    <InstallExecuteSequence>
      <Custom Action='UninstallApp' After='RemoveFiles'>Installed AND NOT UPGRADINGPRODUCTCODE</Custom>
    </InstallExecuteSequence>

    <!-- Properties for Group Policy deployment -->
    <Property Id="ALLUSERS" Value="1" />
    <Property Id="MSIINSTALLPERUSER" Value="0" />
    <Property Id="ARPSYSTEMCOMPONENT" Value="1" />
    
    <!-- Installation UI settings -->
    <Property Id="WIXUI_INSTALLDIR" Value="INSTALLFOLDER" />
    
    <!-- Condition to check Windows version -->
    <Condition Message="This application requires Windows 7 SP1 or later.">
      <![CDATA[Installed OR (VersionNT >= 601)]]>
    </Condition>

  </Product>
</Wix>
"@

# Write WiX source file
$wxsContent | Out-File -FilePath $wxsFile -Encoding UTF8

Write-Host "Compiling WiX source..."

# Compile WiX source
$candleArgs = @(
    "-out", $wixobjFile,
    $wxsFile
)
& candle.exe $candleArgs

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to compile WiX source"
    exit 1
}

Write-Host "Linking MSI package..."

# Link MSI
$lightArgs = @(
    "-out", $OutputMsi,
    "-ext", "WixUIExtension",
    $wixobjFile
)
& light.exe $lightArgs

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to link MSI package"
    exit 1
}

# Clean up temporary files
Remove-Item $tempDir -Recurse -Force

if (Test-Path $OutputMsi) {
    Write-Host "MSI package created successfully: $OutputMsi" -ForegroundColor Green
    
    # Display MSI information
    $msiInfo = Get-ItemProperty $OutputMsi
    Write-Host "File size: $([math]::Round($msiInfo.Length / 1MB, 2)) MB"
    Write-Host "Created: $($msiInfo.CreationTime)"
    
    # Create deployment instructions
    $instructionsFile = [System.IO.Path]::ChangeExtension($OutputMsi, ".txt")
    $instructions = @"
MSI Deployment Instructions for $ProductName
============================================

This MSI package is a wrapper around the original Inno Setup installer.
It can be deployed using Group Policy, SCCM, or other enterprise deployment tools.

Installation Commands:
---------------------
Silent Installation:
  msiexec /i "$([System.IO.Path]::GetFileName($OutputMsi))" /quiet /norestart

Interactive Installation:
  msiexec /i "$([System.IO.Path]::GetFileName($OutputMsi))" /passive

Installation with Logging:
  msiexec /i "$([System.IO.Path]::GetFileName($OutputMsi))" /quiet /norestart /l*v install.log

Uninstallation:
  msiexec /x "$ProductCode" /quiet /norestart

Group Policy Deployment:
-----------------------
1. Copy the MSI file to a network share accessible by all target computers
2. Open Group Policy Management Console
3. Create or edit a Group Policy Object (GPO)
4. Navigate to Computer Configuration > Policies > Software Settings > Software Installation
5. Right-click and select New > Package
6. Browse to the MSI file on the network share
7. Select "Assigned" deployment method
8. Configure any additional settings as needed
9. Link the GPO to the appropriate Organizational Unit (OU)

SCCM Deployment:
---------------
1. Copy the MSI file to the SCCM content library
2. Create a new Application in SCCM
3. Use the MSI file as the installation source
4. Configure detection methods, requirements, and dependencies
5. Distribute to distribution points
6. Deploy to target collections

Prerequisites:
-------------
- Windows 7 SP1 or later
- Administrative privileges for installation
- Network access for downloading dependencies (if not cached)

Notes:
------
- This MSI wrapper will launch the original Inno Setup installer silently
- All configuration options should be pre-configured using enterprise_config.json
- Log files will be created in %TEMP%\UnsplashImageSearch_Install.log
- The application will be installed to Program Files by default

For technical support, please contact: support@image-search-tools.com
"@

    $instructions | Out-File -FilePath $instructionsFile -Encoding UTF8
    Write-Host "Deployment instructions created: $instructionsFile"
    
} else {
    Write-Error "Failed to create MSI package"
    exit 1
}

Write-Host "MSI wrapper creation completed successfully!" -ForegroundColor Green