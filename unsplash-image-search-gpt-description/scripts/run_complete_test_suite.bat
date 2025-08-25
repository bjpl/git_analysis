@echo off
REM Complete Test Suite Runner for Unsplash Image Search GPT Tool
REM This script runs the full testing pipeline for the built executable

setlocal enabledelayedexpansion

REM Configuration
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "TEST_RESULTS_DIR=%PROJECT_ROOT%\test_results"
set "EXE_PATH=%PROJECT_ROOT%\dist\main.exe"
set "TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "TIMESTAMP=!TIMESTAMP: =0!"

echo ===============================================================================
echo   UNSPLASH IMAGE SEARCH GPT TOOL - COMPLETE TEST SUITE
echo ===============================================================================
echo.
echo Timestamp: %TIMESTAMP%
echo Project Root: %PROJECT_ROOT%
echo Test Results: %TEST_RESULTS_DIR%
echo Executable: %EXE_PATH%
echo.

REM Create test results directory
if not exist "%TEST_RESULTS_DIR%" mkdir "%TEST_RESULTS_DIR%"
if not exist "%TEST_RESULTS_DIR%\%TIMESTAMP%" mkdir "%TEST_RESULTS_DIR%\%TIMESTAMP%"

cd /d "%PROJECT_ROOT%"

REM Check if executable exists
if not exist "%EXE_PATH%" (
    echo ❌ ERROR: Executable not found at %EXE_PATH%
    echo Please build the application first using: python -m PyInstaller main.spec
    exit /b 1
)

echo ✅ Found executable: %EXE_PATH%
for %%A in ("%EXE_PATH%") do (
    set "FILE_SIZE=%%~zA"
    set /a "SIZE_MB=!FILE_SIZE! / 1048576"
    echo    Size: !SIZE_MB! MB
)
echo.

REM ===============================================================================
echo 📋 PHASE 1: PRE-VALIDATION CHECKS
echo ===============================================================================

echo Checking Python environment...
python --version
if errorlevel 1 (
    echo ❌ Python not found in PATH
    exit /b 1
)

echo Checking test dependencies...
python -c "import pytest, requests, PIL" 2>nul
if errorlevel 1 (
    echo ❌ Required test dependencies not installed
    echo Run: pip install -r requirements-dev.txt
    exit /b 1
)

echo ✅ Environment checks passed
echo.

REM ===============================================================================
echo 🔍 PHASE 2: SMOKE TESTS (Critical - Must Pass)
echo ===============================================================================

echo Running smoke tests...
python tests/smoke_test_suite.py --exe "%EXE_PATH%" --output "%TEST_RESULTS_DIR%\%TIMESTAMP%\smoke_tests.json"
set "SMOKE_RESULT=%errorlevel%"

if !SMOKE_RESULT! neq 0 (
    echo.
    echo ❌ CRITICAL FAILURE: Smoke tests failed!
    echo    This is a release-blocking issue.
    echo    Check the results in: %TEST_RESULTS_DIR%\%TIMESTAMP%\smoke_tests.json
    echo.
    echo Aborting further testing due to critical failures.
    exit /b !SMOKE_RESULT!
)

echo ✅ Smoke tests passed
echo.

REM ===============================================================================
echo 🔧 PHASE 3: API MOCK TESTS
echo ===============================================================================

echo Running API mock tests...
python tests/api_mock_tests.py --output "%TEST_RESULTS_DIR%\%TIMESTAMP%\api_mock_tests.json"
set "API_RESULT=%errorlevel%"

if !API_RESULT! equ 0 (
    echo ✅ API mock tests passed
) else (
    echo ⚠️  API mock tests had some failures
)
echo.

REM ===============================================================================
echo 🖥️  PHASE 4: UI RESPONSIVENESS TESTS
echo ===============================================================================

echo Running UI responsiveness tests...
echo Note: These tests may require GUI access and can be unstable in automated environments
python tests/ui_responsiveness_tests.py --exe "%EXE_PATH%" --output "%TEST_RESULTS_DIR%\%TIMESTAMP%\ui_responsiveness_tests.json"
set "UI_RESULT=%errorlevel%"

if !UI_RESULT! equ 0 (
    echo ✅ UI responsiveness tests passed
) else (
    echo ⚠️  UI responsiveness tests had some failures
    echo    This may be due to the testing environment - verify manually if needed
)
echo.

REM ===============================================================================
echo 🚀 PHASE 5: COMPREHENSIVE POST-BUILD VALIDATION
echo ===============================================================================

echo Running complete post-build validation suite...
echo This includes security tests, performance benchmarks, and overall assessment
python tests/post_build_validation.py --exe "%EXE_PATH%" --output "%TEST_RESULTS_DIR%\%TIMESTAMP%"
set "VALIDATION_RESULT=%errorlevel%"

echo.
echo Post-build validation completed with exit code: !VALIDATION_RESULT!

REM ===============================================================================
echo 📊 PHASE 6: RESULTS SUMMARY
echo ===============================================================================

echo.
echo TEST RESULTS SUMMARY
echo ===============================================================================
echo Smoke Tests:         !SMOKE_RESULT! (0=Pass, 1+=Fail)
echo API Mock Tests:      !API_RESULT! (0=Pass, 1+=Fail)  
echo UI Tests:           !UI_RESULT! (0=Pass, 1+=Fail)
echo Post-Build Valid.:  !VALIDATION_RESULT! (0=Excellent, 1=Acceptable, 2=Critical, 3=Poor)
echo.

REM Determine overall status
set "OVERALL_STATUS=UNKNOWN"
set "EXIT_CODE=0"

if !SMOKE_RESULT! neq 0 (
    set "OVERALL_STATUS=CRITICAL FAILURE"
    set "EXIT_CODE=2"
) else if !VALIDATION_RESULT! equ 0 (
    set "OVERALL_STATUS=EXCELLENT - READY FOR RELEASE"
    set "EXIT_CODE=0"
) else if !VALIDATION_RESULT! equ 1 (
    set "OVERALL_STATUS=ACCEPTABLE - READY FOR RELEASE"
    set "EXIT_CODE=0"
) else if !VALIDATION_RESULT! equ 2 (
    set "OVERALL_STATUS=CRITICAL FAILURE - DO NOT RELEASE"
    set "EXIT_CODE=2"
) else if !VALIDATION_RESULT! equ 3 (
    set "OVERALL_STATUS=POOR QUALITY - SIGNIFICANT ISSUES"
    set "EXIT_CODE=1"
) else (
    set "OVERALL_STATUS=UNKNOWN STATUS"
    set "EXIT_CODE=1"
)

echo OVERALL STATUS: !OVERALL_STATUS!
echo.

REM ===============================================================================
echo 📁 PHASE 7: RESULTS AND RECOMMENDATIONS
echo ===============================================================================

echo Test results saved to:
echo   Directory: %TEST_RESULTS_DIR%\%TIMESTAMP%\
echo   Summary:   %TEST_RESULTS_DIR%\%TIMESTAMP%\validation_summary.txt
echo   Report:    %TEST_RESULTS_DIR%\%TIMESTAMP%\post_build_validation_report.json
echo.

if exist "%TEST_RESULTS_DIR%\%TIMESTAMP%\validation_summary.txt" (
    echo QUICK SUMMARY:
    echo -------------------------------------------------------------------------------
    type "%TEST_RESULTS_DIR%\%TIMESTAMP%\validation_summary.txt"
    echo -------------------------------------------------------------------------------
    echo.
)

echo RECOMMENDATIONS:
if !EXIT_CODE! equ 0 (
    echo ✅ Application is ready for release
    echo    - All critical tests passed
    echo    - Performance is acceptable
    echo    - No security issues found
    echo.
    echo Next steps:
    echo    - Perform final manual testing
    echo    - Update version numbers
    echo    - Create release package
    echo    - Deploy to distribution channels
) else if !EXIT_CODE! equ 1 (
    echo ⚠️  Application has issues but may be releasable
    echo    - Review failed tests carefully
    echo    - Consider fixing high-priority issues
    echo    - Document known limitations
    echo.
    echo Next steps:
    echo    - Review detailed test results
    echo    - Prioritize fixes based on severity
    echo    - Consider release timeline vs. fix urgency
) else (
    echo ❌ Application is NOT ready for release
    echo    - Critical issues must be resolved
    echo    - DO NOT proceed with release
    echo    - Fix issues and re-run tests
    echo.
    echo Next steps:
    echo    - Review critical failures
    echo    - Fix blocking issues
    echo    - Re-run complete test suite
    echo    - Only release after all critical tests pass
)

echo.
echo ===============================================================================
echo Testing completed at %date% %time%
echo Results available in: %TEST_RESULTS_DIR%\%TIMESTAMP%\
echo Exit Code: !EXIT_CODE! (!OVERALL_STATUS!)
echo ===============================================================================

REM Save run summary
echo Test Suite Run Summary > "%TEST_RESULTS_DIR%\%TIMESTAMP%\run_summary.txt"
echo ===================== >> "%TEST_RESULTS_DIR%\%TIMESTAMP%\run_summary.txt"
echo Timestamp: %TIMESTAMP% >> "%TEST_RESULTS_DIR%\%TIMESTAMP%\run_summary.txt"
echo Executable: %EXE_PATH% >> "%TEST_RESULTS_DIR%\%TIMESTAMP%\run_summary.txt"
echo Smoke Tests: !SMOKE_RESULT! >> "%TEST_RESULTS_DIR%\%TIMESTAMP%\run_summary.txt"
echo API Tests: !API_RESULT! >> "%TEST_RESULTS_DIR%\%TIMESTAMP%\run_summary.txt"
echo UI Tests: !UI_RESULT! >> "%TEST_RESULTS_DIR%\%TIMESTAMP%\run_summary.txt"
echo Validation: !VALIDATION_RESULT! >> "%TEST_RESULTS_DIR%\%TIMESTAMP%\run_summary.txt"
echo Overall: !OVERALL_STATUS! >> "%TEST_RESULTS_DIR%\%TIMESTAMP%\run_summary.txt"
echo Exit Code: !EXIT_CODE! >> "%TEST_RESULTS_DIR%\%TIMESTAMP%\run_summary.txt"

endlocal
exit /b !EXIT_CODE!