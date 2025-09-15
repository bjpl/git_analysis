# Safe PowerShell Script to Reorganize Project_Workspace using Symbolic Links
# This preserves original locations to avoid breaking code dependencies
# Run as Administrator: .\safe_reorganize_workspace.ps1

Write-Host "Safe Project Workspace Reorganization (Using Symbolic Links)" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "This approach creates an organized view without moving files" -ForegroundColor Yellow
Write-Host ""

# Check if running as Administrator (required for symlinks on Windows)
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script requires Administrator privileges for creating symbolic links." -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Red
    exit 1
}

# Set the base directory
$baseDir = "C:\Users\brand\Development\Project_Workspace"
Set-Location $baseDir

# Create organized view directory
$organizedDir = "_organized_view"
Write-Host "Creating organized view in '$organizedDir' folder..." -ForegroundColor Yellow

# Remove existing organized view if it exists
if (Test-Path $organizedDir) {
    Write-Host "Removing existing organized view..." -ForegroundColor Gray
    Remove-Item -Path $organizedDir -Recurse -Force
}

# Create new directory structure
$directories = @(
    "$organizedDir\spanish-learning\core-apps",
    "$organizedDir\spanish-learning\flashcard-tools",
    "$organizedDir\spanish-learning\media-learning",
    "$organizedDir\spanish-learning\cli-tools",
    "$organizedDir\spanish-learning\scripts",
    "$organizedDir\web-projects",
    "$organizedDir\lifestyle-apps",
    "$organizedDir\data-exploration",
    "$organizedDir\engineering",
    "$organizedDir\course-materials",
    "$organizedDir\data-files",
    "$organizedDir\pdf-generators",
    "$organizedDir\config-files"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    Write-Host "  Created: $dir" -ForegroundColor Gray
}

# Function to create symbolic link safely
function Create-SafeSymLink {
    param(
        [string]$Source,
        [string]$Destination
    )
    
    if (Test-Path $Source) {
        # Check if source is a directory or file
        $item = Get-Item $Source
        if ($item.PSIsContainer) {
            New-Item -ItemType SymbolicLink -Path $Destination -Target $Source -Force | Out-Null
        } else {
            New-Item -ItemType SymbolicLink -Path $Destination -Target $Source -Force | Out-Null
        }
        Write-Host "  Linked: $Source -> $Destination" -ForegroundColor Gray
        return $true
    } else {
        Write-Host "  Skipped: $Source (not found)" -ForegroundColor DarkGray
        return $false
    }
}

Write-Host "`nCreating symbolic links for Spanish learning tools..." -ForegroundColor Yellow

# Spanish learning core apps
$spanishCoreApps = @{
    "MySpanishApp" = "$organizedDir\spanish-learning\core-apps\MySpanishApp"
    "conjugation_gui" = "$organizedDir\spanish-learning\core-apps\conjugation_gui"
    "subjunctive_practice" = "$organizedDir\spanish-learning\core-apps\subjunctive_practice"
}

foreach ($app in $spanishCoreApps.GetEnumerator()) {
    $sourcePath = Join-Path $baseDir $app.Key
    Create-SafeSymLink -Source $sourcePath -Destination $app.Value
}

# Flashcard tools
Write-Host "`nLinking flashcard tools..." -ForegroundColor Yellow

$flashcardTools = @{
    "anki_generator" = "$organizedDir\spanish-learning\flashcard-tools\anki_generator"
    "add_tags" = "$organizedDir\spanish-learning\flashcard-tools\add_tags"
    "merge_gui" = "$organizedDir\spanish-learning\flashcard-tools\merge_gui"
}

foreach ($tool in $flashcardTools.GetEnumerator()) {
    $sourcePath = Join-Path $baseDir $tool.Key
    Create-SafeSymLink -Source $sourcePath -Destination $tool.Value
}

# Media learning tools
Write-Host "`nLinking media learning tools..." -ForegroundColor Yellow

$mediaTools = @{
    "YouTubeTranscriptGPT" = "$organizedDir\spanish-learning\media-learning\YouTubeTranscriptGPT"
    "image-questionnaire-gpt" = "$organizedDir\spanish-learning\media-learning\image-questionnaire-gpt"
    "unsplash-image-search-gpt-description" = "$organizedDir\spanish-learning\media-learning\unsplash-image-search-gpt-description"
    "celebrity_gui" = "$organizedDir\spanish-learning\media-learning\celebrity_gui"
}

foreach ($tool in $mediaTools.GetEnumerator()) {
    $sourcePath = Join-Path $baseDir $tool.Key
    Create-SafeSymLink -Source $sourcePath -Destination $tool.Value
}

# CLI tools
Write-Host "`nLinking CLI tools..." -ForegroundColor Yellow
Create-SafeSymLink -Source "$baseDir\langtool" -Destination "$organizedDir\spanish-learning\cli-tools\langtool"

# Spanish learning scripts
Write-Host "`nLinking Spanish learning scripts..." -ForegroundColor Yellow

$spanishScripts = @(
    "optimize_anki_cards.py",
    "shuffle_subjunctive.py",
    "convert_anki_csv.py",
    "convert_to_csv.py"
)

foreach ($script in $spanishScripts) {
    $sourcePath = Join-Path $baseDir $script
    $destPath = "$organizedDir\spanish-learning\scripts\$script"
    Create-SafeSymLink -Source $sourcePath -Destination $destPath
}

# Web projects
Write-Host "`nLinking web projects..." -ForegroundColor Yellow

$webProjects = @{
    "portfolio_site" = "$organizedDir\web-projects\portfolio_site"
    "fluids-visualization" = "$organizedDir\web-projects\fluids-visualization"
}

foreach ($project in $webProjects.GetEnumerator()) {
    $sourcePath = Join-Path $baseDir $project.Key
    Create-SafeSymLink -Source $sourcePath -Destination $project.Value
}

# Lifestyle apps
Write-Host "`nLinking lifestyle applications..." -ForegroundColor Yellow

$lifestyleApps = @{
    "nutriplan" = "$organizedDir\lifestyle-apps\nutriplan"
    "mealplanner_and_pantry_manager" = "$organizedDir\lifestyle-apps\mealplanner_and_pantry_manager"
    "home_inventory_manager" = "$organizedDir\lifestyle-apps\home_inventory_manager"
}

foreach ($app in $lifestyleApps.GetEnumerator()) {
    $sourcePath = Join-Path $baseDir $app.Key
    Create-SafeSymLink -Source $sourcePath -Destination $app.Value
}

# Data exploration tools
Write-Host "`nLinking data exploration tools..." -ForegroundColor Yellow

$dataTools = @{
    "movie_explorer_full" = "$organizedDir\data-exploration\movie_explorer_full"
    "city_map_explorer" = "$organizedDir\data-exploration\city_map_explorer"
    "map-description" = "$organizedDir\data-exploration\map-description"
}

foreach ($tool in $dataTools.GetEnumerator()) {
    $sourcePath = Join-Path $baseDir $tool.Key
    Create-SafeSymLink -Source $sourcePath -Destination $tool.Value
}

# Engineering files
Write-Host "`nLinking engineering files..." -ForegroundColor Yellow

Create-SafeSymLink -Source "$baseDir\fluids.py" -Destination "$organizedDir\engineering\fluids.py"
Create-SafeSymLink -Source "$baseDir\flujo_en_tubería" -Destination "$organizedDir\engineering\flujo_en_tubería"

# PDF files
Write-Host "`nLinking course materials..." -ForegroundColor Yellow

$pdfFiles = @(
    "Module1_Unobtrusive_Environmental_Awareness.pdf",
    "Module2_Subtle_Social_Observation.pdf",
    "Module3_Temporal_and_Contextual_Dynamics.pdf",
    "Module4_Micro_Contextual_Observations.pdf",
    "Module5_Narrative_Synthesis_and_Situational_Storylines.pdf"
)

foreach ($pdf in $pdfFiles) {
    $sourcePath = Join-Path $baseDir $pdf
    $destPath = "$organizedDir\course-materials\$pdf"
    Create-SafeSymLink -Source $sourcePath -Destination $destPath
}

# PDF generators
Write-Host "`nLinking PDF generator scripts..." -ForegroundColor Yellow

$pdfGenerators = @(
    "generate_pdf.py",
    "generate_pdf_module2.py",
    "generate_pdf_module3.py",
    "generate_pdf_module4.py",
    "generate_pdf_module5.py"
)

foreach ($generator in $pdfGenerators) {
    $sourcePath = Join-Path $baseDir $generator
    $destPath = "$organizedDir\pdf-generators\$generator"
    Create-SafeSymLink -Source $sourcePath -Destination $destPath
}

# Data files
Write-Host "`nLinking data files..." -ForegroundColor Yellow

$dataFiles = @(
    "Anki_Cards.csv",
    "Anki_Cards.txt",
    "Review Cards - Sheet1.csv",
    "ORIGINAL Review Cards - Sheet1.csv",
    "output.csv",
    "subjunctive_scenes.txt",
    "shuffled_scenes.txt"
)

foreach ($file in $dataFiles) {
    $sourcePath = Join-Path $baseDir $file
    $destPath = "$organizedDir\data-files\$file"
    Create-SafeSymLink -Source $sourcePath -Destination $destPath
}

# Config files
Write-Host "`nLinking configuration files..." -ForegroundColor Yellow

$configFiles = @(
    "poetry.lock",
    "pyproject.toml",
    "setup.py",
    "LICENSE",
    ".gitignore"
)

foreach ($file in $configFiles) {
    $sourcePath = Join-Path $baseDir $file
    $destPath = "$organizedDir\config-files\$file"
    Create-SafeSymLink -Source $sourcePath -Destination $destPath
}

# Create a README in the organized view
$readmeContent = @"
# Organized View of Project Workspace

This folder contains symbolic links to the actual projects, providing an organized view without moving any files.

## Why Symbolic Links?

Moving project folders can break:
- Relative imports in Python code
- Path references in configuration files
- Git repositories and their history
- Virtual environments
- IDE project settings

## How to Use

1. Browse projects through this organized structure
2. Open and edit files normally - changes affect the original files
3. Run projects from their original locations to ensure all paths work

## Original Structure Preserved

All projects remain in their original locations. This is just an organized view for easier navigation.

## Removing This View

To remove this organized view without affecting any projects:
``````powershell
Remove-Item -Path "_organized_view" -Recurse -Force
``````

## Note

Symbolic links require Administrator privileges on Windows.
"@

Set-Content -Path "$organizedDir\README.md" -Value $readmeContent

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "Safe Reorganization Complete!" -ForegroundColor Green
Write-Host "`nWhat was created:" -ForegroundColor Yellow
Write-Host "  - Organized view in '_organized_view' folder" -ForegroundColor Gray
Write-Host "  - All original files remain untouched" -ForegroundColor Gray
Write-Host "  - Symbolic links provide organized navigation" -ForegroundColor Gray
Write-Host "`nBenefits:" -ForegroundColor Yellow
Write-Host "  - No broken imports or paths" -ForegroundColor Gray
Write-Host "  - Git repositories remain intact" -ForegroundColor Gray
Write-Host "  - Virtual environments continue working" -ForegroundColor Gray
Write-Host "  - Can be removed anytime without impact" -ForegroundColor Gray
Write-Host "`nItems to manually review for deletion:" -ForegroundColor Yellow
Write-Host "  - anki_generator.zip" -ForegroundColor Gray
Write-Host "  - anki_generator (2).zip" -ForegroundColor Gray
Write-Host "  - anki_generator (3).zip" -ForegroundColor Gray
Write-Host "  - anki_generator (3)\" -ForegroundColor Gray
Write-Host "  - Project_Workspace\ (nested duplicate)" -ForegroundColor Gray