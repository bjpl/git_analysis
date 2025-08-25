@echo off
echo Starting Image Manager...
python image_manager.py
if errorlevel 1 (
    echo.
    echo Error: Python not found or application error.
    echo Make sure Python is installed and requirements are met.
    echo.
    pause
)