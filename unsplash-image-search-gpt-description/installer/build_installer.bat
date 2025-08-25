@echo off
REM Build script for Unsplash Image Search GPT Description Installer
REM This script builds both 32-bit and 64-bit installers using Inno Setup

setlocal enabledelayedexpansion

echo ========================================
echo Unsplash Image Search Installer Builder
echo ========================================

REM Configuration
set APP_NAME=Unsplash Image Search GPT Description
set APP_VERSION=1.0.0
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set OUTPUT_DIR=%SCRIPT_DIR%output
set ASSETS_DIR=%SCRIPT_DIR%assets
set DIST_DIR=%PROJECT_ROOT%\dist

REM Check if Inno Setup is installed
echo Checking for Inno Setup...
set INNO_SETUP_PATH=
for %%i in ("C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "C:\Program Files\Inno Setup 6\ISCC.exe") do (
    if exist %%i (
        set INNO_SETUP_PATH=%%i
        goto :found_inno
    )
)

echo ERROR: Inno Setup not found!
echo Please install Inno Setup 6.2 or later from https://jrsoftware.org/isinfo.php
pause
exit /b 1

:found_inno
echo Found Inno Setup: !INNO_SETUP_PATH!

REM Check if application is built
echo Checking for built application...
if not exist "%DIST_DIR%\unsplash-image-search.exe" (
    echo ERROR: Application not found in dist directory!
    echo Please run the build process first:
    echo   python -m PyInstaller main.spec
    pause
    exit /b 1
)

REM Create output directory
if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
)

REM Create assets directory if it doesn't exist
if not exist "%ASSETS_DIR%" (
    mkdir "%ASSETS_DIR%"
    echo WARNING: Assets directory created. Please add the following files:
    echo   - app_icon.ico          ^(Application icon^)
    echo   - wizard_left.bmp       ^(Wizard banner image - 164x314 pixels^)
    echo   - wizard_small.bmp      ^(Wizard header image - 55x58 pixels^)
    echo   - uninstall_banner.bmp  ^(Uninstaller banner^)
    echo.
)

REM Check for required asset files
set ASSETS_MISSING=0
if not exist "%ASSETS_DIR%\app_icon.ico" (
    echo WARNING: Missing app_icon.ico - using default
    set ASSETS_MISSING=1
)
if not exist "%ASSETS_DIR%\wizard_left.bmp" (
    echo WARNING: Missing wizard_left.bmp - using default
    set ASSETS_MISSING=1
)
if not exist "%ASSETS_DIR%\wizard_small.bmp" (
    echo WARNING: Missing wizard_small.bmp - using default
    set ASSETS_MISSING=1
)

if !ASSETS_MISSING! == 1 (
    echo.
    echo Some asset files are missing. The installer will use defaults.
    echo Press any key to continue or Ctrl+C to cancel...
    pause > nul
)

echo.
echo ========================================
echo Building Enhanced Installer
echo ========================================

REM Build enhanced installer
echo Building enhanced installer...
"!INNO_SETUP_PATH!" "%SCRIPT_DIR%installer_enhanced.iss" /O"%OUTPUT_DIR%" /Q
if !ERRORLEVEL! neq 0 (
    echo ERROR: Failed to build enhanced installer
    pause
    exit /b 1
)

echo Enhanced installer built successfully!

REM Check if PowerShell and WiX are available for MSI creation
echo.
echo Checking for MSI creation tools...
where powershell.exe > nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo WARNING: PowerShell not found - skipping MSI creation
    goto :skip_msi
)

where candle.exe > nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo WARNING: WiX Toolset not found - skipping MSI creation
    echo Install WiX Toolset from https://wixtoolset.org/releases/
    goto :skip_msi
)

REM Create MSI wrapper
echo Creating MSI wrapper for enterprise deployment...
set INSTALLER_EXE=
for %%f in ("%OUTPUT_DIR%\unsplash-image-search-setup-*.exe") do (
    set INSTALLER_EXE=%%f
)

if "!INSTALLER_EXE!" == "" (
    echo WARNING: Installer executable not found - skipping MSI creation
    goto :skip_msi
)

powershell.exe -ExecutionPolicy Bypass -File "%SCRIPT_DIR%tools\create_msi.ps1" -InputExe "!INSTALLER_EXE!" -OutputMsi "%OUTPUT_DIR%\unsplash-image-search-%APP_VERSION%.msi"

if !ERRORLEVEL! neq 0 (
    echo WARNING: MSI creation failed
    goto :skip_msi
)

echo MSI package created successfully!

:skip_msi

REM Create distribution package
echo.
echo ========================================
echo Creating Distribution Package
echo ========================================

set DIST_PACKAGE_DIR=%OUTPUT_DIR%\Distribution
if exist "%DIST_PACKAGE_DIR%" (
    rmdir /s /q "%DIST_PACKAGE_DIR%"
)
mkdir "%DIST_PACKAGE_DIR%"

REM Copy installers
copy "%OUTPUT_DIR%\*.exe" "%DIST_PACKAGE_DIR%\" > nul
if exist "%OUTPUT_DIR%\*.msi" (
    copy "%OUTPUT_DIR%\*.msi" "%DIST_PACKAGE_DIR%\" > nul
)

REM Copy configuration files
mkdir "%DIST_PACKAGE_DIR%\Config"
copy "%SCRIPT_DIR%config\*" "%DIST_PACKAGE_DIR%\Config\" > nul

REM Copy documentation
copy "%PROJECT_ROOT%\README.md" "%DIST_PACKAGE_DIR%\README.txt" > nul
copy "%PROJECT_ROOT%\LICENSE" "%DIST_PACKAGE_DIR%\LICENSE.txt" > nul

if exist "%PROJECT_ROOT%\docs\*.pdf" (
    copy "%PROJECT_ROOT%\docs\*.pdf" "%DIST_PACKAGE_DIR%\" > nul
)

REM Create deployment guide
echo Creating deployment guide...
(
echo Deployment Guide for %APP_NAME%
echo ========================================
echo.
echo This package contains the following files:
echo.
echo Installers:
echo   unsplash-image-search-setup-%APP_VERSION%.exe  - Standard installer
echo   unsplash-image-search-%APP_VERSION%.msi         - MSI package for enterprise
echo.
echo Configuration:
echo   Config\silent_install.xml       - Silent installation configuration
echo   Config\enterprise_config.json   - Enterprise deployment settings
echo.
echo Documentation:
echo   README.txt                      - Application overview and features
echo   LICENSE.txt                     - License information
echo.
echo Installation Types:
echo ==================
echo.
echo Interactive Installation:
echo   Run: unsplash-image-search-setup-%APP_VERSION%.exe
echo.
echo Silent Installation:
echo   Run: unsplash-image-search-setup-%APP_VERSION%.exe /VERYSILENT /NORESTART
echo   With config: unsplash-image-search-setup-%APP_VERSION%.exe /VERYSILENT /CONFIG="Config\silent_install.xml"
echo.
echo Enterprise Deployment ^(MSI^):
echo   Run: msiexec /i unsplash-image-search-%APP_VERSION%.msi /quiet /norestart
echo   With logging: msiexec /i unsplash-image-search-%APP_VERSION%.msi /quiet /norestart /l*v install.log
echo.
echo System Requirements:
echo ===================
echo - Windows 7 SP1 or later
echo - .NET Framework 4.8 ^(auto-installed if missing^)
echo - Visual C++ Redistributable 2019 ^(auto-installed if missing^)
echo - 100 MB free disk space
echo - Internet connection for API access
echo.
echo For technical support, visit: https://github.com/your-username/unsplash-image-search-gpt-description
) > "%DIST_PACKAGE_DIR%\Deployment_Guide.txt"

REM Create ZIP package
echo Creating distribution archive...
if exist "%OUTPUT_DIR%\unsplash-image-search-distribution-%APP_VERSION%.zip" (
    del "%OUTPUT_DIR%\unsplash-image-search-distribution-%APP_VERSION%.zip"
)

REM Use PowerShell to create ZIP if available
where powershell.exe > nul 2>&1
if !ERRORLEVEL! == 0 (
    powershell.exe -command "Compress-Archive -Path '%DIST_PACKAGE_DIR%\*' -DestinationPath '%OUTPUT_DIR%\unsplash-image-search-distribution-%APP_VERSION%.zip'"
    if !ERRORLEVEL! == 0 (
        echo Distribution archive created: unsplash-image-search-distribution-%APP_VERSION%.zip
    )
)

REM Calculate file sizes and create summary
echo.
echo ========================================
echo Build Summary
echo ========================================

for %%f in ("%OUTPUT_DIR%\*.exe") do (
    set /a SIZE=%%~zf/1024/1024
    echo Standard Installer: %%~nxf ^(!SIZE! MB^)
)

for %%f in ("%OUTPUT_DIR%\*.msi") do (
    set /a SIZE=%%~zf/1024/1024
    echo MSI Package:       %%~nxf ^(!SIZE! MB^)
)

for %%f in ("%OUTPUT_DIR%\*.zip") do (
    set /a SIZE=%%~zf/1024/1024
    echo Distribution:      %%~nxf ^(!SIZE! MB^)
)

echo.
echo All files have been created in: %OUTPUT_DIR%
echo.
echo Next steps:
echo 1. Test the installer on a clean system
echo 2. Update any missing asset files for better branding
echo 3. Configure silent_install.xml and enterprise_config.json for your environment
echo 4. Deploy using your preferred method ^(Group Policy, SCCM, etc.^)
echo.
echo Build completed successfully!

REM Open output directory
echo Opening output directory...
explorer "%OUTPUT_DIR%"

pause
endlocal