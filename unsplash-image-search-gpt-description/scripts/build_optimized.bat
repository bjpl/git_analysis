@echo off
setlocal EnableDelayedExpansion

REM =============================================================================
REM Optimized Build Script for UnsplashGPT-Enhanced
REM Features: Multiple build modes, comprehensive optimization, error handling
REM =============================================================================

echo.
echo ===============================================================================
echo UNSPLASHGPT-ENHANCED - OPTIMIZED BUILD SYSTEM v2.1
echo ===============================================================================
echo.

REM Set default values
set "BUILD_MODE=onefile"
set "DEBUG_MODE=0"
set "CLEAN_BUILD=1"
set "SKIP_TESTS=0"
set "OPEN_DIST=0"
set "UPX_COMPRESS=1"
set "PROFILE_BUILD=0"

REM Parse command line arguments
:parse_args
if "%1"=="" goto :args_done
if "%1"=="--help" goto :show_help
if "%1"=="help" goto :show_help
if "%1"=="onefile" set "BUILD_MODE=onefile"
if "%1"=="onedir" set "BUILD_MODE=onedir"
if "%1"=="portable" set "BUILD_MODE=onedir"
if "%1"=="debug" (
    set "BUILD_MODE=debug"
    set "DEBUG_MODE=1"
    set "UPX_COMPRESS=0"
)
if "%1"=="--debug" set "DEBUG_MODE=1"
if "%1"=="--no-clean" set "CLEAN_BUILD=0"
if "%1"=="--no-upx" set "UPX_COMPRESS=0"
if "%1"=="--test" set "SKIP_TESTS=0"
if "%1"=="--no-test" set "SKIP_TESTS=1"
if "%1"=="--open" set "OPEN_DIST=1"
if "%1"=="--profile" set "PROFILE_BUILD=1"
shift
goto :parse_args
:args_done

echo Build Configuration:
echo   Mode: %BUILD_MODE%
echo   Debug: %DEBUG_MODE%
echo   Clean Build: %CLEAN_BUILD%
echo   Skip Tests: %SKIP_TESTS%
echo   UPX Compression: %UPX_COMPRESS%
echo   Profile Build: %PROFILE_BUILD%
echo.

REM Check Python installation
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH
    echo Please install Python 3.8+ and ensure it's added to PATH
    echo Download from: https://python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Found Python %PYTHON_VERSION%

REM Check PyInstaller
echo [INFO] Checking PyInstaller...
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo [WARN] PyInstaller not found, installing...
    pip install pyinstaller>=6.0
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller
        pause
        exit /b 1
    )
)

for /f "tokens=1" %%i in ('pyinstaller --version 2^>^&1') do set PYINSTALLER_VERSION=%%i
echo [INFO] Found PyInstaller %PYINSTALLER_VERSION%

REM Check UPX (optional)
if "%UPX_COMPRESS%"=="1" (
    echo [INFO] Checking UPX compression...
    upx --version >nul 2>&1
    if errorlevel 1 (
        echo [WARN] UPX not found - compression will be limited
        echo [INFO] Download UPX from: https://upx.github.io/
        set "UPX_COMPRESS=0"
    ) else (
        echo [INFO] UPX compression available
    )
)

REM Validate project structure
echo [INFO] Validating project structure...
if not exist "main.py" (
    echo [ERROR] main.py not found in current directory
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

if not exist "UnsplashGPT-Enhanced-Optimized.spec" (
    echo [ERROR] UnsplashGPT-Enhanced-Optimized.spec not found
    echo Please ensure the optimized spec file is present
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo [WARN] requirements.txt not found
) else (
    echo [INFO] Checking dependencies...
    pip check >nul 2>&1
    if errorlevel 1 (
        echo [WARN] Some dependencies may be missing or incompatible
        echo [INFO] Installing/updating dependencies...
        pip install -r requirements.txt
    )
)

echo [INFO] Project structure validated

REM Pre-build tests (if not skipped)
if "%SKIP_TESTS%"=="0" (
    echo [INFO] Running pre-build validation...
    python -c "import main; print('Main module imports successfully')" >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Main module has import errors
        echo [INFO] Testing imports...
        python -c "import main"
        pause
        exit /b 1
    )
    echo [INFO] Pre-build validation passed
)

REM Clean previous builds
if "%CLEAN_BUILD%"=="1" (
    echo [INFO] Cleaning previous build artifacts...
    if exist "dist" (
        echo   Removing dist/
        rmdir /s /q "dist" >nul 2>&1
    )
    if exist "build" (
        echo   Removing build/
        rmdir /s /q "build" >nul 2>&1
    )
    
    REM Clean Python cache
    for /r %%i in (__pycache__) do (
        if exist "%%i" rmdir /s /q "%%i" >nul 2>&1
    )
    for /r %%i in (*.pyc) do del "%%i" >nul 2>&1
    for /r %%i in (*.pyo) do del "%%i" >nul 2>&1
    
    echo [INFO] Build artifacts cleaned
)

REM Create necessary directories
if not exist "assets" mkdir "assets" >nul 2>&1
if not exist "config" mkdir "config" >nul 2>&1
if not exist "data" mkdir "data" >nul 2>&1

REM Set environment variables for build
set "BUILD_MODE=%BUILD_MODE%"
set "DEBUG_MODE=%DEBUG_MODE%"
if "%UPX_COMPRESS%"=="0" set "NOUPX=1"

REM Generate version file
echo [INFO] Creating version information...
if exist "version_info.py" (
    python version_info.py >nul 2>&1
    if errorlevel 1 (
        echo [WARN] Could not generate version file
    ) else (
        echo [INFO] Version file created
    )
)

REM Start build process
echo.
echo ===============================================================================
echo STARTING PYINSTALLER BUILD
echo ===============================================================================
echo.
echo [INFO] Build started at %DATE% %TIME%
echo [INFO] Using spec: UnsplashGPT-Enhanced-Optimized.spec
echo [INFO] Working directory: %CD%
echo.

REM Build with timing
set "BUILD_START_TIME=%TIME%"

if "%PROFILE_BUILD%"=="1" (
    echo [INFO] Profiling build performance...
    python -m cProfile -o build_profile.prof -c "import subprocess; subprocess.run(['pyinstaller', 'UnsplashGPT-Enhanced-Optimized.spec', '--clean', '--noconfirm'])"
    set BUILD_RESULT=%ERRORLEVEL%
) else (
    pyinstaller UnsplashGPT-Enhanced-Optimized.spec --clean --noconfirm
    set BUILD_RESULT=%ERRORLEVEL%
)

set "BUILD_END_TIME=%TIME%"

REM Calculate build time (approximate)
echo.
echo [INFO] Build completed at %BUILD_END_TIME%
echo.

if %BUILD_RESULT% neq 0 (
    echo ===============================================================================
    echo BUILD FAILED!
    echo ===============================================================================
    echo.
    echo [ERROR] PyInstaller exited with code %BUILD_RESULT%
    echo.
    echo Common solutions:
    echo 1. Check that all dependencies are installed:
    echo    pip install -r requirements.txt
    echo 2. Verify all source files are accessible
    echo 3. Check for import errors:
    echo    python main.py
    echo 4. Review console output above for specific errors
    echo 5. Try debug build for more information:
    echo    build_optimized debug
    echo.
    echo For more help, check the build logs or run:
    echo   python -c "import main"  # Test imports
    echo   build_optimized debug    # Debug build
    echo.
    if "%DEBUG_MODE%"=="0" (
        echo Tip: Try debug mode for more detailed error information
    )
    pause
    exit /b %BUILD_RESULT%
)

REM Post-build validation and reporting
echo ===============================================================================
echo BUILD SUCCESSFUL!
echo ===============================================================================
echo.

REM Find and report output files
echo [INFO] Locating build outputs...
set "OUTPUT_FOUND=0"
set "TOTAL_SIZE=0"

if exist "dist\*.exe" (
    for %%F in (dist\*.exe) do (
        set "OUTPUT_FOUND=1"
        set "EXE_NAME=%%~nF"
        set "EXE_SIZE=%%~zF"
        set /a "SIZE_MB=!EXE_SIZE!/1048576"
        echo   [FOUND] Executable: %%F
        echo           Size: !EXE_SIZE! bytes (~!SIZE_MB! MB)
        set /a "TOTAL_SIZE+=!EXE_SIZE!"
    )
)

if exist "dist\*_Portable" (
    for /d %%D in (dist\*_Portable) do (
        set "OUTPUT_FOUND=1"
        echo   [FOUND] Portable Directory: %%D
        
        REM Count files in portable directory
        set "FILE_COUNT=0"
        for /r "%%D" %%F in (*) do set /a "FILE_COUNT+=1"
        echo           Files: !FILE_COUNT!
        
        REM Calculate directory size
        for /f "tokens=3" %%S in ('dir "%%D" /s /-c ^| findstr /C:" bytes"') do (
            set "DIR_SIZE=%%S"
            set /a "DIR_SIZE_MB=!DIR_SIZE!/1048576"
            echo           Total Size: !DIR_SIZE! bytes (~!DIR_SIZE_MB! MB)
            set /a "TOTAL_SIZE+=!DIR_SIZE!"
        )
    )
)

if "%OUTPUT_FOUND%"=="0" (
    echo [WARN] No output files found in dist/ directory
    echo This may indicate a build issue
)

REM Post-build tests
if "%SKIP_TESTS%"=="0" (
    echo.
    echo [INFO] Running post-build validation...
    
    REM Test executable launch (quick test)
    if exist "dist\*.exe" (
        for %%F in (dist\*.exe) do (
            echo [TEST] Testing executable launch: %%F
            timeout /t 1 /nobreak >nul
            start "" /wait "%%F" --help >nul 2>&1
            if errorlevel 1 (
                echo [WARN] Executable may have startup issues
            ) else (
                echo [PASS] Executable launches successfully
            )
            goto :test_done
        )
    )
    :test_done
)

REM Build summary
echo.
echo ===============================================================================
echo BUILD SUMMARY
echo ===============================================================================
echo Application: UnsplashGPT-Enhanced v2.1.0
echo Build Mode: %BUILD_MODE%
echo Debug Mode: %DEBUG_MODE%
echo Python Version: %PYTHON_VERSION%
echo PyInstaller: %PYINSTALLER_VERSION%
echo UPX Compression: %UPX_COMPRESS%
echo Output Directory: %CD%\dist\
if "%TOTAL_SIZE%"=="0" (
    echo Total Size: Unknown
) else (
    set /a "TOTAL_MB=%TOTAL_SIZE%/1048576"
    echo Total Size: %TOTAL_SIZE% bytes (~!TOTAL_MB! MB)
)
echo Build Time: %BUILD_START_TIME% to %BUILD_END_TIME%
echo.

REM Usage instructions
echo DISTRIBUTION INSTRUCTIONS:
echo.
if "%BUILD_MODE%"=="onefile" (
    echo SINGLE-FILE DISTRIBUTION:
    echo • Distribute the .exe file from dist\ folder
    echo • Users can run it directly - no installation needed
    echo • First run will show API key setup wizard
    echo • Slower initial startup but easier distribution
) else if "%BUILD_MODE%"=="onedir" (
    echo PORTABLE DIRECTORY DISTRIBUTION:
    echo • Distribute entire *_Portable folder from dist\
    echo • Users run the .exe from within the folder
    echo • Faster startup time than single-file
    echo • Easier to troubleshoot if issues occur
) else (
    echo DEBUG BUILD:
    echo • Use for testing and troubleshooting only
    echo • Console output enabled for debugging
    echo • Not optimized for distribution
)
echo.
echo API REQUIREMENTS:
echo • OpenAI API key: https://platform.openai.com/api-keys
echo • Unsplash API key: https://unsplash.com/developers
echo • Both can be configured through the app's setup wizard
echo.

REM Optional operations
if "%OPEN_DIST%"=="1" (
    echo [INFO] Opening dist folder...
    start explorer "dist"
)

echo Build completed successfully!
echo.

REM Cleanup and exit
if "%PROFILE_BUILD%"=="1" (
    if exist "build_profile.prof" (
        echo [INFO] Build profile saved to build_profile.prof
        echo [INFO] Analyze with: python -m pstats build_profile.prof
    )
)

echo Press any key to exit...
pause >nul
exit /b 0

:show_help
echo.
echo USAGE: build_optimized.bat [mode] [options]
echo.
echo BUILD MODES:
echo   onefile     Create single executable file (default, slower startup)
echo   onedir      Create portable directory (faster startup, more files)
echo   portable    Alias for onedir
echo   debug       Debug build with console output (for troubleshooting)
echo.
echo OPTIONS:
echo   --debug     Enable debug mode (console output)
echo   --no-clean  Skip cleaning previous builds (faster rebuild)
echo   --no-upx    Disable UPX compression (if UPX is available)
echo   --no-test   Skip pre/post build tests (faster but less safe)
echo   --test      Force run tests (default)
echo   --open      Open dist folder after successful build
echo   --profile   Profile build performance (creates build_profile.prof)
echo   --help      Show this help message
echo.
echo EXAMPLES:
echo   build_optimized                    # Default single-file build
echo   build_optimized onedir --open      # Portable directory, open after
echo   build_optimized debug              # Debug build with console
echo   build_optimized onefile --no-clean # Fast rebuild without cleaning
echo   build_optimized --profile          # Profile build performance
echo.
echo REQUIREMENTS:
echo   • Python 3.8+ with pip
echo   • PyInstaller 6.0+ (auto-installed if missing)
echo   • UPX (optional, for better compression)
echo   • All project dependencies installed
echo.
echo For more information:
echo   • Check README.md for detailed build instructions
echo   • Visit project documentation for troubleshooting
echo   • Use debug mode if build fails
echo.
pause
exit /b 0
