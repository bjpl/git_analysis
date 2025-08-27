@echo off
REM UI Rendering Test Runner for Unsplash Image Search Application
REM This script runs comprehensive UI validation tests

echo.
echo ==========================================
echo    UI Rendering Test Suite
echo ==========================================
echo.

REM Check if we're in the right directory
if not exist "main.py" (
    echo ERROR: Please run this script from the project root directory
    echo Expected to find main.py in current directory
    pause
    exit /b 1
)

REM Check Python availability
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not available in PATH
    echo Please install Python or add it to your PATH
    pause
    exit /b 1
)

REM Parse command line arguments
set MODE=quick
if "%1"=="--full" set MODE=full
if "%1"=="--help" goto :show_help

echo Running UI tests in %MODE% mode...
echo.

REM Run the appropriate test mode
if "%MODE%"=="full" (
    echo Running comprehensive UI test suite...
    python tests/test_ui_validation_runner.py --full
) else (
    echo Running quick health check...
    python tests/test_ui_validation_runner.py --quick
)

set RESULT=%ERRORLEVEL%

echo.
if %RESULT%==0 (
    echo ==========================================
    echo    ✅ UI Tests PASSED
    echo ==========================================
    echo The UI should load correctly without issues.
) else (
    echo ==========================================
    echo    ❌ UI Tests FAILED  
    echo ==========================================
    echo Please check the output above for specific issues.
    echo.
    echo Common solutions:
    echo  • Ensure all dependencies are installed: pip install -r requirements.txt
    echo  • Verify API keys are configured properly
    echo  • Check that the display is available for GUI testing
)

echo.
echo Press any key to exit...
pause >nul
exit /b %RESULT%

:show_help
echo.
echo Usage: run_ui_tests.bat [--full] [--help]
echo.
echo Options:
echo   --quick    Run quick health check only (default)
echo   --full     Run comprehensive UI test suite
echo   --help     Show this help message
echo.
echo Examples:
echo   run_ui_tests.bat           # Quick health check
echo   run_ui_tests.bat --quick   # Quick health check
echo   run_ui_tests.bat --full    # Full test suite
echo.
pause
exit /b 0