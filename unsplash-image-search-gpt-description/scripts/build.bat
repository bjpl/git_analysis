@echo off
setlocal enabledelayedexpansion

REM ===================================================================
REM Comprehensive Build Script for Unsplash Image Search & GPT Tool
REM Batch version with validation, testing, and multiple build profiles
REM ===================================================================

echo.
echo ========================================
echo   Unsplash GPT Tool Build System
echo ========================================
echo.

REM Initialize variables
set "PROJECT_ROOT=%~dp0.."
set "BUILD_DIR=%PROJECT_ROOT%\build"
set "DIST_DIR=%PROJECT_ROOT%\dist"
set "SCRIPTS_DIR=%PROJECT_ROOT%\scripts"
set "BUILD_LOG=%PROJECT_ROOT%\build.log"
set "ERROR_COUNT=0"
set "BUILD_PROFILE=production"

REM Parse command line arguments
:parse_args
if "%~1"=="" goto args_done
if /i "%~1"=="--profile" (
    set "BUILD_PROFILE=%~2"
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--clean" (
    set "CLEAN_BUILD=1"
    shift
    goto parse_args
)
if /i "%~1"=="--skip-tests" (
    set "SKIP_TESTS=1"
    shift
    goto parse_args
)
if /i "%~1"=="--verbose" (
    set "VERBOSE=1"
    shift
    goto parse_args
)
if /i "%~1"=="--help" (
    echo Usage: build.bat [options]
    echo.
    echo Options:
    echo   --profile ^<dev^|prod^|debug^>  Build profile (default: production)
    echo   --clean                     Clean previous builds
    echo   --skip-tests               Skip test execution
    echo   --verbose                  Enable verbose output
    echo   --help                     Show this help
    echo.
    echo Build Profiles:
    echo   dev        - Development build with console and debug info
    echo   prod       - Production build, optimized, no console
    echo   debug      - Debug build with symbols and console
    echo.
    exit /b 0
)
shift
goto parse_args
:args_done

REM Redirect output to log file if not verbose
if not defined VERBOSE (
    echo Build started at %date% %time% > "%BUILD_LOG%"
    echo Command: %0 %* >> "%BUILD_LOG%"
    echo. >> "%BUILD_LOG%"
)

REM Change to project directory
cd /d "%PROJECT_ROOT%"

echo [INFO] Starting build process...
echo [INFO] Build Profile: %BUILD_PROFILE%
echo [INFO] Project Root: %PROJECT_ROOT%
echo.

REM ===================================================================
REM PRE-BUILD VALIDATION
REM ===================================================================

echo [STEP 1/8] Pre-build validation...

REM Check Python version
echo [INFO] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    set /a ERROR_COUNT+=1
    goto error_exit
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Python version: %PYTHON_VERSION%

REM Validate Python version (3.8+)
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)
if %MAJOR% lss 3 (
    echo [ERROR] Python 3.8+ required, found %PYTHON_VERSION%
    set /a ERROR_COUNT+=1
    goto error_exit
)
if %MAJOR% equ 3 if %MINOR% lss 8 (
    echo [ERROR] Python 3.8+ required, found %PYTHON_VERSION%
    set /a ERROR_COUNT+=1
    goto error_exit
)

REM Check if virtual environment exists
echo [INFO] Checking virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo [WARNING] Virtual environment not found, creating one...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        set /a ERROR_COUNT+=1
        goto error_exit
    )
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    set /a ERROR_COUNT+=1
    goto error_exit
)

REM Check required files
echo [INFO] Checking required files...
set "REQUIRED_FILES=main.py version_info.py config_manager.py pyproject.toml main.spec"
for %%f in (%REQUIRED_FILES%) do (
    if not exist "%%f" (
        echo [ERROR] Required file not found: %%f
        set /a ERROR_COUNT+=1
    )
)

if %ERROR_COUNT% gtr 0 goto error_exit

REM Check for hardcoded paths (basic check)
echo [INFO] Checking for hardcoded paths...
findstr /r /c:"C:\\" /c:"D:\\" /c:"E:\\" *.py >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Potential hardcoded paths found in Python files
    echo [INFO] Please review the following files:
    findstr /r /c:"C:\\" /c:"D:\\" /c:"E:\\" *.py
    echo.
)

REM ===================================================================
REM DEPENDENCY INSTALLATION
REM ===================================================================

echo [STEP 2/8] Installing dependencies...

REM Update pip
echo [INFO] Updating pip...
python -m pip install --upgrade pip >>"%BUILD_LOG%" 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to update pip
    set /a ERROR_COUNT+=1
    goto error_exit
)

REM Install poetry if pyproject.toml exists
if exist "pyproject.toml" (
    echo [INFO] Installing poetry dependencies...
    pip install poetry >>"%BUILD_LOG%" 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to install poetry
        set /a ERROR_COUNT+=1
        goto error_exit
    )
    
    poetry install >>"%BUILD_LOG%" 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to install poetry dependencies
        set /a ERROR_COUNT+=1
        goto error_exit
    )
) else (
    REM Install from requirements.txt
    if exist "requirements.txt" (
        echo [INFO] Installing pip dependencies...
        pip install -r requirements.txt >>"%BUILD_LOG%" 2>&1
        if errorlevel 1 (
            echo [ERROR] Failed to install dependencies
            set /a ERROR_COUNT+=1
            goto error_exit
        )
    ) else (
        echo [ERROR] No dependency file found (pyproject.toml or requirements.txt)
        set /a ERROR_COUNT+=1
        goto error_exit
    )
)

REM Install PyInstaller
echo [INFO] Installing PyInstaller...
pip install pyinstaller >>"%BUILD_LOG%" 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to install PyInstaller
    set /a ERROR_COUNT+=1
    goto error_exit
)

REM ===================================================================
REM CLEAN PREVIOUS BUILDS
REM ===================================================================

echo [STEP 3/8] Cleaning previous builds...

if defined CLEAN_BUILD (
    echo [INFO] Performing clean build...
    if exist "%BUILD_DIR%" (
        echo [INFO] Removing build directory...
        rmdir /s /q "%BUILD_DIR%"
    )
    if exist "%DIST_DIR%" (
        echo [INFO] Removing dist directory...
        rmdir /s /q "%DIST_DIR%"
    )
    if exist "__pycache__" (
        echo [INFO] Removing Python cache...
        rmdir /s /q "__pycache__"
    )
    if exist "*.pyc" del /q "*.pyc"
)

REM Create directories
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

REM ===================================================================
REM RUN TESTS
REM ===================================================================

echo [STEP 4/8] Running tests...

if not defined SKIP_TESTS (
    echo [INFO] Running test suite...
    
    REM Check if pytest is available
    python -m pytest --version >nul 2>&1
    if not errorlevel 1 (
        echo [INFO] Running tests with pytest...
        python -m pytest tests/ -v >>"%BUILD_LOG%" 2>&1
        if errorlevel 1 (
            echo [ERROR] Tests failed
            echo [INFO] Check %BUILD_LOG% for details
            set /a ERROR_COUNT+=1
            goto error_exit
        )
        echo [INFO] All tests passed!
    ) else (
        REM Fallback to basic test runner
        if exist "run_tests.py" (
            echo [INFO] Running basic tests...
            python run_tests.py >>"%BUILD_LOG%" 2>&1
            if errorlevel 1 (
                echo [ERROR] Tests failed
                set /a ERROR_COUNT+=1
                goto error_exit
            )
        ) else (
            echo [WARNING] No test framework found, skipping tests
        )
    )
) else (
    echo [INFO] Skipping tests (--skip-tests specified)
)

REM ===================================================================
REM CODE QUALITY CHECKS
REM ===================================================================

echo [STEP 5/8] Code quality checks...

REM Run basic syntax check
echo [INFO] Checking Python syntax...
python -m py_compile main.py
if errorlevel 1 (
    echo [ERROR] Syntax errors found in main.py
    set /a ERROR_COUNT+=1
    goto error_exit
)

REM ===================================================================
REM BUILD VERSION FILE
REM ===================================================================

echo [STEP 6/8] Generating version info...

echo [INFO] Creating version file...
python version_info.py >>"%BUILD_LOG%" 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to create version file
    set /a ERROR_COUNT+=1
    goto error_exit
)

REM ===================================================================
REM BUILD EXECUTABLE
REM ===================================================================

echo [STEP 7/8] Building executable...

REM Set build options based on profile
set "PYINSTALLER_OPTS=--noconfirm --log-level WARN"

if /i "%BUILD_PROFILE%"=="dev" (
    echo [INFO] Building development version...
    set "PYINSTALLER_OPTS=%PYINSTALLER_OPTS% --console --debug=bootloader"
    set "SPEC_FILE=main_dev.spec"
) else if /i "%BUILD_PROFILE%"=="debug" (
    echo [INFO] Building debug version...
    set "PYINSTALLER_OPTS=%PYINSTALLER_OPTS% --console --debug=all"
    set "SPEC_FILE=main_debug.spec"
) else (
    echo [INFO] Building production version...
    set "PYINSTALLER_OPTS=%PYINSTALLER_OPTS% --windowed --optimize=2"
    set "SPEC_FILE=main.spec"
)

REM Generate spec file if needed
if not exist "%SPEC_FILE%" (
    echo [INFO] Generating PyInstaller spec file...
    if /i "%BUILD_PROFILE%"=="dev" (
        pyinstaller --onefile --console main.py --name="Unsplash_GPT_Tool_Dev" --distpath=dist --workpath=build --specpath=. >>"%BUILD_LOG%" 2>&1
        ren "Unsplash_GPT_Tool_Dev.spec" "main_dev.spec"
    ) else if /i "%BUILD_PROFILE%"=="debug" (
        pyinstaller --onefile --console --debug=all main.py --name="Unsplash_GPT_Tool_Debug" --distpath=dist --workpath=build --specpath=. >>"%BUILD_LOG%" 2>&1
        ren "Unsplash_GPT_Tool_Debug.spec" "main_debug.spec"
    ) else (
        REM Use existing main.spec for production
        if not exist "main.spec" (
            echo [ERROR] Production spec file main.spec not found
            set /a ERROR_COUNT+=1
            goto error_exit
        )
    )
)

REM Build the executable
echo [INFO] Running PyInstaller...
pyinstaller %PYINSTALLER_OPTS% "%SPEC_FILE%" >>"%BUILD_LOG%" 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed
    echo [INFO] Check %BUILD_LOG% for details
    set /a ERROR_COUNT+=1
    goto error_exit
)

REM ===================================================================
REM POST-BUILD VERIFICATION
REM ===================================================================

echo [STEP 8/8] Post-build verification...

REM Check if executable was created
for /f %%i in ('dir /b "%DIST_DIR%\*.exe" 2^>nul') do set "EXECUTABLE=%%i"
if not defined EXECUTABLE (
    echo [ERROR] No executable found in dist directory
    set /a ERROR_COUNT+=1
    goto error_exit
)

echo [INFO] Executable created: %EXECUTABLE%

REM Get file size
for %%i in ("%DIST_DIR%\%EXECUTABLE%") do set "FILE_SIZE=%%~zi"
set /a FILE_SIZE_MB=%FILE_SIZE%/1024/1024
echo [INFO] Executable size: %FILE_SIZE_MB% MB

REM Basic executable test (just check if it starts without crashing)
echo [INFO] Testing executable startup...
timeout 3 > nul
if /i not "%BUILD_PROFILE%"=="prod" (
    REM Can test console versions
    "%DIST_DIR%\%EXECUTABLE%" --help >nul 2>&1
    if errorlevel 9009 (
        echo [WARNING] Executable test failed - may be missing dependencies
    ) else (
        echo [INFO] Executable test passed
    )
)

REM Generate checksums
echo [INFO] Generating checksums...
cd /d "%DIST_DIR%"
certutil -hashfile "%EXECUTABLE%" SHA256 > "%EXECUTABLE%.sha256"
if exist "%EXECUTABLE%.sha256" (
    echo [INFO] SHA256 checksum generated
)

REM ===================================================================
REM CREATE PORTABLE VERSION
REM ===================================================================

echo [INFO] Creating portable version...
set "PORTABLE_DIR=%DIST_DIR%\Portable"
if not exist "%PORTABLE_DIR%" mkdir "%PORTABLE_DIR%"

copy "%EXECUTABLE%" "%PORTABLE_DIR%\" >nul
if exist "README.md" copy "README.md" "%PORTABLE_DIR%\" >nul
if exist "LICENSE" copy "LICENSE" "%PORTABLE_DIR%\" >nul

REM Create portable package info
echo Application: Unsplash Image Search ^& GPT Tool > "%PORTABLE_DIR%\PORTABLE_INFO.txt"
echo Version: Built on %date% %time% >> "%PORTABLE_DIR%\PORTABLE_INFO.txt"
echo. >> "%PORTABLE_DIR%\PORTABLE_INFO.txt"
echo This is a portable version that doesn't require installation. >> "%PORTABLE_DIR%\PORTABLE_INFO.txt"
echo Simply run the executable file to start the application. >> "%PORTABLE_DIR%\PORTABLE_INFO.txt"

REM ===================================================================
REM BUILD SUMMARY
REM ===================================================================

cd /d "%PROJECT_ROOT%"
echo.
echo ========================================
echo          BUILD COMPLETED
echo ========================================
echo.
echo Build Profile: %BUILD_PROFILE%
echo Executable: %EXECUTABLE%
echo Size: %FILE_SIZE_MB% MB
echo Location: %DIST_DIR%
echo Portable: %PORTABLE_DIR%
echo.
echo Build completed successfully at %date% %time%
echo.

if defined VERBOSE (
    echo Log file: %BUILD_LOG%
    echo.
    echo Next steps:
    echo 1. Test the executable thoroughly
    echo 2. Run installer creation script if needed
    echo 3. Upload to release repository
    echo.
)

goto :eof

:error_exit
echo.
echo ========================================
echo        BUILD FAILED
echo ========================================
echo.
echo Errors encountered: %ERROR_COUNT%
echo Check the log file: %BUILD_LOG%
echo.
echo Common solutions:
echo - Ensure Python 3.8+ is installed
echo - Check that all dependencies are available
echo - Verify that required files exist
echo - Check for syntax errors in Python files
echo.
exit /b 1