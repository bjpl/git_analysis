# Algorithm Learning Platform - PowerShell Launcher
# Clean and modern launcher for Windows PowerShell

# Set window title
$host.UI.RawUI.WindowTitle = "Algorithm Learning Platform"

# Clear screen
Clear-Host

# Display banner
Write-Host ""
Write-Host "  ╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║       🎓 ALGORITHM LEARNING PLATFORM - Quick Start 🚀          ║" -ForegroundColor Cyan
Write-Host "  ╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found! Please install Python 3.8+" -ForegroundColor Red
    Write-Host "    Download from: https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "  Starting interactive learning environment..." -ForegroundColor Yellow
Write-Host ""

# Launch the application
python cli.py --menu

# Check exit code
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "  Application exited with an error." -ForegroundColor Red
    Read-Host "Press Enter to close"
}