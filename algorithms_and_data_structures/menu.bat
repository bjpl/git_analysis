@echo off
:: Algorithm Learning Platform - Quick Launch Menu
:: Clean and simple launcher for Windows

:: Set window title
title Algorithm Learning Platform

:: Clear screen for clean start
cls

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

:: Launch the menu directly with cli.py
python cli.py --menu

:: Keep window open if there was an error
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application failed to start
    pause
)