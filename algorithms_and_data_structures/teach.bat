@echo off
REM Algorithm Teaching System - Beautiful CLI Launcher
REM Run with beautiful formatting

echo.
echo Starting Algorithm Teaching System...
echo.

REM Set environment for best color support
set FORCE_COLOR=1
set COLORTERM=truecolor
set PYTHONIOENCODING=utf-8

REM Check if first argument is provided
if "%1"=="" (
    python algo_teach.py big-o
) else (
    python algo_teach.py %*
)

echo.
pause