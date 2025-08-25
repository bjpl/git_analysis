@echo off
echo ============================================
echo Starting Fixed Unsplash Image Search App
echo ============================================
echo.
echo This version fixes the UI rendering issues:
echo - Main window renders immediately
echo - API configuration doesn't block UI
echo - Works with or without API keys
echo.
echo Starting application...
python main_fixed.py
if errorlevel 1 (
    echo.
    echo Error starting application.
    echo Trying with Python 3...
    python3 main_fixed.py
)
pause