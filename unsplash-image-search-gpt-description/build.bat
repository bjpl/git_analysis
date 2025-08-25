@echo off
setlocal EnableDelayedExpansion

REM =============================================================================
REM Optimized Build Script for Unsplash Image Search & GPT Tool
REM Supports multiple build configurations: onefile, portable, debug
REM =============================================================================

echo.
echo ===============================================================================
echo UNSPLASH IMAGE SEARCH ^& GPT TOOL - OPTIMIZED BUILD SYSTEM
echo ===============================================================================
echo.

REM Parse command line arguments
set BUILD_MODE=onefile
set SPEC_FILE=installer\production.spec
set CLEAN=true
set UPX_ENABLED=true

if "%1"=="--help" (
    goto :show_help
)

if "%1"=="help" (
    goto :show_help
)

if "%1"=="portable" (
    set BUILD_MODE=onedir
    echo Build mode: PORTABLE DIRECTORY
) else if "%1"=="onefile" (
    set BUILD_MODE=onefile
    echo Build mode: SINGLE FILE EXECUTABLE
) else if "%1"=="debug" (
    set BUILD_MODE=onefile
    set SPEC_FILE=installer\debug.spec
    echo Build mode: DEBUG BUILD
) else if "%1"=="legacy" (
    set SPEC_FILE=UnsplashGPT.spec
    echo Build mode: LEGACY SPEC
) else if not "%1"=="" (
    echo Warning: Unknown build mode '%1', using default 'onefile'
)

if "%2"=="--no-clean" set CLEAN=false
if "%2"=="--no-upx" set UPX_ENABLED=false

echo Configuration:
echo   Build Mode: %BUILD_MODE%
echo   Spec File:  %SPEC_FILE%
echo   Clean Build: %CLEAN%
echo   UPX Compression: %UPX_ENABLED%
echo.

REM Check for required dependencies
echo Checking build dependencies...
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python and ensure it's added to PATH
    pause
    exit /b 1
)

pyinstaller --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: PyInstaller not found
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Clean previous builds
if "%CLEAN%"=="true" (
    echo Cleaning previous build artifacts...
    if exist dist rmdir /s /q dist 2>nul
    if exist build rmdir /s /q build 2>nul
    if exist __pycache__ rmdir /s /q __pycache__ 2>nul
    for /r %%i in (*.pyc) do del "%%i" 2>nul
    echo   Cleaned build directories
)

REM Create necessary directories
if not exist data mkdir data
if not exist installer mkdir installer
if not exist assets mkdir assets

REM Generate icons if needed
echo Checking application icons...
if not exist "installer\app_icon.ico" (
    echo Generating application icons...
    python installer\icon_generator.py generate
    if errorlevel 1 (
        echo Warning: Icon generation failed, continuing without custom icons
    )
)

REM Set environment variable for build mode
set BUILD_MODE=%BUILD_MODE%

REM Create version file
echo Creating version information...
python version_info.py > nul 2>&1
if errorlevel 1 (
    echo Warning: Could not create version file
)

REM Build executable
echo.
echo ===============================================================================
echo STARTING PYINSTALLER BUILD
echo ===============================================================================
echo.
echo Command: pyinstaller "%SPEC_FILE%"
echo Working Directory: %CD%
echo.

REM Run PyInstaller with progress indication
echo [%TIME%] Starting build process...
pyinstaller "%SPEC_FILE%" --clean --noconfirm

set BUILD_RESULT=%ERRORLEVEL%

echo [%TIME%] Build process completed with exit code: %BUILD_RESULT%
echo.

if %BUILD_RESULT% neq 0 (
    echo ===============================================================================
    echo BUILD FAILED!
    echo ===============================================================================
    echo.
    echo Common solutions:
    echo 1. Check that all dependencies are installed: pip install -r requirements.txt
    echo 2. Ensure all source files are present and accessible
    echo 3. Check for any import errors in the application
    echo 4. Review the error messages above for specific issues
    echo.
    echo For detailed debugging, try:
    echo   python main.py    (test the application directly)
    echo   build debug       (create a debug build with console output)
    echo.
    pause
    exit /b %BUILD_RESULT%
)

REM Post-build operations
echo ===============================================================================
echo BUILD SUCCESSFUL!
echo ===============================================================================
echo.

REM Find and display output files
echo Locating build outputs...
for /f "delims=" %%i in ('dir /b /s dist\*.exe 2^>nul') do (
    set "EXE_FILE=%%i"
    echo   Executable: %%i
    for %%j in ("%%i") do echo   Size: %%~zj bytes (%%~zj bytes = !tmp! MB)
)

if exist "dist" (
    for /d %%i in (dist\*_Portable) do (
        echo   Portable Directory: %%i
    )
)

REM Calculate build time and show summary
echo.
echo ===============================================================================
echo BUILD SUMMARY
echo ===============================================================================
echo Build Mode: %BUILD_MODE%
echo Spec File: %SPEC_FILE%
echo Build Time: [Build completed at %TIME%]
echo Output Directory: %CD%\dist\
echo.

REM Show distribution instructions
echo DISTRIBUTION INSTRUCTIONS:
echo.
if "%BUILD_MODE%"=="onefile" (
    echo SINGLE FILE DISTRIBUTION:
    echo 1. Distribute the .exe file from the dist\ folder
    echo 2. Users can run it directly without installation
    echo 3. First run will prompt for API key configuration
    echo 4. Configuration will be saved in user's home directory
) else (
    echo PORTABLE DIRECTORY DISTRIBUTION:
    echo 1. Distribute the entire folder from dist\ directory
    echo 2. Users should run the .exe from within the folder
    echo 3. Faster startup time compared to single file
    echo 4. Easier to debug if issues occur
)
echo.
echo API SETUP:
echo - Users need OpenAI API key from: https://platform.openai.com/api-keys
echo - Users need Unsplash API key from: https://unsplash.com/developers
echo - Keys can be configured through the application's setup wizard
echo.

REM Optional: Open dist folder
set /p "OPEN_FOLDER=Open output folder? (y/n): "
if /i "!OPEN_FOLDER!"=="y" start explorer "dist"

echo.
echo Build process completed successfully!
echo Press any key to exit...
pause > nul
exit /b 0

:show_help
echo.
echo USAGE: build.bat [mode] [options]
echo.
echo BUILD MODES:
echo   onefile    - Create single executable file (default)
echo   portable   - Create directory with all files (faster startup)
echo   debug      - Create debug build with console output
echo   legacy     - Use legacy build configuration
echo.
echo OPTIONS:
echo   --no-clean - Skip cleaning previous builds
echo   --no-upx   - Disable UPX compression
echo.
echo EXAMPLES:
echo   build.bat                    # Default single file build
echo   build.bat portable           # Create portable directory
echo   build.bat debug              # Debug build with console
echo   build.bat onefile --no-clean # Single file without cleaning
echo.
echo For more information, see installer\README.md
echo.
pause
exit /b 0