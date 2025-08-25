@echo off
REM Windows Batch Script for Building Unsplash Image Search & GPT Tool
REM This script demonstrates various build commands and options

setlocal enabledelayedexpansion

REM Set color codes for output
set "RED=[31m"
set "GREEN=[32m"
set "YELLOW=[33m"
set "BLUE=[34m"
set "RESET=[0m"

echo %BLUE%===========================================%RESET%
echo %BLUE%  Unsplash GPT Tool - Build Script%RESET%
echo %BLUE%===========================================%RESET%
echo.

REM Change to project directory
cd /d "%~dp0.."

REM Check if we're in the right directory
if not exist "main.py" (
    echo %RED%Error: main.py not found. Please run this script from the project root.%RESET%
    pause
    exit /b 1
)

REM Parse command line arguments
set "BUILD_PROFILE=production"
set "SKIP_TESTS=false"
set "CREATE_INSTALLER=false"
set "VERBOSE=false"

:parse_args
if "%1"=="" goto :args_done
if "%1"=="--profile" set "BUILD_PROFILE=%2" & shift & shift & goto :parse_args
if "%1"=="--skip-tests" set "SKIP_TESTS=true" & shift & goto :parse_args
if "%1"=="--installer" set "CREATE_INSTALLER=true" & shift & goto :parse_args
if "%1"=="--verbose" set "VERBOSE=true" & shift & goto :parse_args
if "%1"=="--help" goto :show_help
shift
goto :parse_args

:args_done

echo %BLUE%Build Configuration:%RESET%
echo   Profile: %BUILD_PROFILE%
echo   Skip Tests: %SKIP_TESTS%
echo   Create Installer: %CREATE_INSTALLER%
echo   Verbose: %VERBOSE%
echo.

REM Check Python installation
echo %YELLOW%Checking Python installation...%RESET%
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%Error: Python not found. Please install Python 3.8 or later.%RESET%
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo %GREEN%Python %PYTHON_VERSION% detected%RESET%

REM Check PyInstaller installation
echo %YELLOW%Checking PyInstaller...%RESET%
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%PyInstaller not found. Installing...%RESET%
    pip install pyinstaller
    if errorlevel 1 (
        echo %RED%Error: Failed to install PyInstaller%RESET%
        pause
        exit /b 1
    )
)

for /f "tokens=1" %%i in ('pyinstaller --version 2^>^&1') do set "PYINSTALLER_VERSION=%%i"
echo %GREEN%PyInstaller %PYINSTALLER_VERSION% detected%RESET%

REM Check for optional tools
echo %YELLOW%Checking optional tools...%RESET%

upx --version >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%UPX not found (optional compression tool)%RESET%
    set "UPX_AVAILABLE=false"
) else (
    for /f "tokens=1" %%i in ('upx --version 2^>^&1 ^| findstr "upx"') do set "UPX_VERSION=%%i"
    echo %GREEN%UPX !UPX_VERSION! detected%RESET%
    set "UPX_AVAILABLE=true"
)

REM Generate Windows resources
echo.
echo %YELLOW%Generating Windows resources...%RESET%
python installer\version_info_windows.py
if errorlevel 1 (
    echo %YELLOW%Warning: Could not generate version info%RESET%
)

REM Generate icons
echo %YELLOW%Generating application icons...%RESET%
python installer\icon_generator.py generate
if errorlevel 1 (
    echo %YELLOW%Warning: Could not generate icons%RESET%
)

REM Run build automation
echo.
echo %BLUE%Starting automated build...%RESET%
echo.

set "BUILD_CMD=python installer\build_automation.py %BUILD_PROFILE%"
if "%SKIP_TESTS%"=="true" set "BUILD_CMD=!BUILD_CMD! --skip-tests"

if "%VERBOSE%"=="true" (
    echo %BLUE%Running: !BUILD_CMD!%RESET%
    !BUILD_CMD!
) else (
    !BUILD_CMD! >build_output.tmp 2>&1
)

if errorlevel 1 (
    echo %RED%Build failed!%RESET%
    if "%VERBOSE%"=="false" (
        echo %YELLOW%Last 20 lines of build output:%RESET%
        type build_output.tmp | more +20
    )
    echo.
    echo %YELLOW%Full build log available in build.log%RESET%
    pause
    exit /b 1
) else (
    echo %GREEN%Build completed successfully!%RESET%
)

REM Clean up temporary files
if exist "build_output.tmp" del "build_output.tmp"

REM Display build results
echo.
echo %BLUE%Build Results:%RESET%
if exist "dist\*.exe" (
    for %%f in (dist\*.exe) do (
        set "filesize=%%~zf"
        set /a "filesizeMB=!filesize!/1024/1024"
        echo   Executable: %%~nxf (!filesizeMB! MB)
    )
)

if exist "dist\*.zip" (
    for %%f in (dist\*.zip) do (
        set "filesize=%%~zf"
        set /a "filesizeMB=!filesize!/1024/1024"
        echo   Portable: %%~nxf (!filesizeMB! MB)
    )
)

if exist "dist\checksums.json" (
    echo   Checksums: checksums.json
)

REM Create installer if requested
if "%CREATE_INSTALLER%"=="true" (
    echo.
    echo %YELLOW%Creating installer...%RESET%
    
    REM Check for Inno Setup
    where iscc >nul 2>&1
    if not errorlevel 1 (
        echo %YELLOW%Creating Inno Setup installer...%RESET%
        iscc installer\setup_inno.iss
        if not errorlevel 1 (
            echo %GREEN%Inno Setup installer created%RESET%
        ) else (
            echo %RED%Inno Setup installer failed%RESET%
        )
    ) else (
        echo %YELLOW%Inno Setup not found, skipping installer creation%RESET%
    )
    
    REM Check for NSIS
    where makensis >nul 2>&1
    if not errorlevel 1 (
        echo %YELLOW%Creating NSIS installer...%RESET%
        makensis installer\setup_nsis.nsi
        if not errorlevel 1 (
            echo %GREEN%NSIS installer created%RESET%
        ) else (
            echo %RED%NSIS installer failed%RESET%
        )
    ) else (
        echo %YELLOW%NSIS not found, skipping installer creation%RESET%
    )
)

REM Final summary
echo.
echo %GREEN%===========================================%RESET%
echo %GREEN%  Build Process Complete%RESET%
echo %GREEN%===========================================%RESET%
echo.
echo %BLUE%Output directory: %CD%\dist%RESET%
echo.
echo %YELLOW%Next steps:%RESET%
echo   1. Test the executable in dist\ directory
echo   2. Verify all features work correctly
echo   3. Create installer if needed
echo   4. Distribute to end users
echo.

REM Ask if user wants to run the executable
set /p "RUN_APP=Do you want to run the application now? (y/N): "
if /i "%RUN_APP%"=="y" (
    echo %YELLOW%Launching application...%RESET%
    for %%f in (dist\*.exe) do (
        start "" "%%f"
        goto :app_launched
    )
    echo %RED%No executable found%RESET%
    :app_launched
)

goto :end

:show_help
echo Usage: %0 [options]
echo.
echo Options:
echo   --profile PROFILE    Build profile: development, production, portable, debug
echo   --skip-tests        Skip pre-build testing
echo   --installer         Create installer packages after build
echo   --verbose           Show detailed build output
echo   --help              Show this help message
echo.
echo Examples:
echo   %0 --profile production
echo   %0 --profile debug --verbose
echo   %0 --profile production --installer
echo   %0 --skip-tests --profile portable
echo.
goto :end

:end
if "%VERBOSE%"=="true" pause
