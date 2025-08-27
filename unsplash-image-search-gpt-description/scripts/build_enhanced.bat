@echo off
echo Building UnsplashGPT-Enhanced.exe...
echo ====================================

REM Clean up previous build
if exist "dist\UnsplashGPT-Enhanced.exe" del "dist\UnsplashGPT-Enhanced.exe"

REM Simple build with reduced dependencies
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "UnsplashGPT-Enhanced" ^
    --distpath dist ^
    --workpath build ^
    --specpath build ^
    --noconfirm ^
    --clean ^
    --exclude-module matplotlib ^
    --exclude-module pandas ^
    --exclude-module scipy ^
    --exclude-module pytest ^
    --exclude-module IPython ^
    --exclude-module notebook ^
    --exclude-module jedi ^
    --exclude-module tornado ^
    --add-data "src;src" ^
    --add-data "data;data" ^
    main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ====================================
    echo Build successful!
    echo Executable: dist\UnsplashGPT-Enhanced.exe
    echo ====================================
) else (
    echo.
    echo ====================================
    echo Build failed! Check error messages above.
    echo ====================================
    exit /b 1
)