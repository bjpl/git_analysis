@echo off
echo ============================================
echo Starting Unsplash Image Search App
echo ============================================
echo.
echo This version includes UI rendering fixes:
echo - Main window renders immediately
echo - API configuration doesn't block UI
echo - Works with or without API keys
echo.
echo Starting application...
python main.py
if errorlevel 1 (
    echo.
    echo Error starting application.
    echo Trying with Python 3...
    python3 main.py
)
pause