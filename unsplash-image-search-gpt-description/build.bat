@echo off
echo Building Unsplash GPT Tool executable...
echo.

REM Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM Create data directory structure
if not exist data mkdir data

REM Build executable with PyInstaller
pyinstaller --onefile ^
    --windowed ^
    --name "unsplash-gpt-tool" ^
    --icon "icon.ico" ^
    --add-data ".env.example;." ^
    --add-data "README.md;." ^
    --hidden-import "tkinter" ^
    --hidden-import "PIL" ^
    --hidden-import "openai" ^
    --hidden-import "dotenv" ^
    main.py

echo.
echo Build complete! Executable is in dist/unsplash-gpt-tool.exe
echo.
echo To distribute:
echo 1. Copy dist/unsplash-gpt-tool.exe to a new folder
echo 2. Users will be prompted for API keys on first run
echo.
pause