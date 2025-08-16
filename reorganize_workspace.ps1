# PowerShell Script to Reorganize Project_Workspace
# This script will clean up and organize your development workspace
# Run with: .\reorganize_workspace.ps1

Write-Host "Starting Project Workspace Reorganization..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Set the base directory
$baseDir = "C:\Users\brand\Development\Project_Workspace"
Set-Location $baseDir

# Create new directory structure
Write-Host "`nCreating new directory structure..." -ForegroundColor Yellow

$directories = @(
    "spanish-learning\core-apps",
    "spanish-learning\flashcard-tools",
    "spanish-learning\media-learning",
    "spanish-learning\cli-tools",
    "spanish-learning\scripts",
    "web-projects",
    "lifestyle-apps",
    "data-exploration",
    "engineering",
    "course-materials",
    "data",
    "pdf-generators",
    "config",
    "archive"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Gray
    }
}

# Move Spanish learning core apps
Write-Host "`nMoving Spanish learning core applications..." -ForegroundColor Yellow

$spanishCoreApps = @{
    "MySpanishApp" = "spanish-learning\core-apps\MySpanishApp"
    "conjugation_gui" = "spanish-learning\core-apps\conjugation_gui"
    "subjunctive_practice" = "spanish-learning\core-apps\subjunctive_practice"
}

foreach ($app in $spanishCoreApps.GetEnumerator()) {
    if ((Test-Path $app.Key) -and !(Test-Path $app.Value)) {
        Move-Item -Path $app.Key -Destination $app.Value -Force
        Write-Host "  Moved: $($app.Key) -> $($app.Value)" -ForegroundColor Gray
    }
}

# Move flashcard tools
Write-Host "`nMoving flashcard tools..." -ForegroundColor Yellow

$flashcardTools = @{
    "anki_generator" = "spanish-learning\flashcard-tools\anki_generator"
    "add_tags" = "spanish-learning\flashcard-tools\add_tags"
    "merge_gui" = "spanish-learning\flashcard-tools\merge_gui"
}

foreach ($tool in $flashcardTools.GetEnumerator()) {
    if ((Test-Path $tool.Key) -and !(Test-Path $tool.Value)) {
        Move-Item -Path $tool.Key -Destination $tool.Value -Force
        Write-Host "  Moved: $($tool.Key) -> $($tool.Value)" -ForegroundColor Gray
    }
}

# Move media learning tools
Write-Host "`nMoving media learning tools..." -ForegroundColor Yellow

$mediaTools = @{
    "YouTubeTranscriptGPT" = "spanish-learning\media-learning\YouTubeTranscriptGPT"
    "image-questionnaire-gpt" = "spanish-learning\media-learning\image-questionnaire-gpt"
    "unsplash-image-search-gpt-description" = "spanish-learning\media-learning\unsplash-image-search-gpt-description"
    "celebrity_gui" = "spanish-learning\media-learning\celebrity_gui"
}

foreach ($tool in $mediaTools.GetEnumerator()) {
    if ((Test-Path $tool.Key) -and !(Test-Path $tool.Value)) {
        Move-Item -Path $tool.Key -Destination $tool.Value -Force
        Write-Host "  Moved: $($tool.Key) -> $($tool.Value)" -ForegroundColor Gray
    }
}

# Move CLI tools
Write-Host "`nMoving CLI tools..." -ForegroundColor Yellow

if ((Test-Path "langtool") -and !(Test-Path "spanish-learning\cli-tools\langtool")) {
    Move-Item -Path "langtool" -Destination "spanish-learning\cli-tools\langtool" -Force
    Write-Host "  Moved: langtool -> spanish-learning\cli-tools\langtool" -ForegroundColor Gray
}

# Move Spanish learning scripts
Write-Host "`nMoving Spanish learning scripts..." -ForegroundColor Yellow

$spanishScripts = @(
    "optimize_anki_cards.py",
    "shuffle_subjunctive.py",
    "convert_anki_csv.py",
    "convert_to_csv.py"
)

foreach ($script in $spanishScripts) {
    if ((Test-Path $script) -and !(Test-Path "spanish-learning\scripts\$script")) {
        Move-Item -Path $script -Destination "spanish-learning\scripts\$script" -Force
        Write-Host "  Moved: $script -> spanish-learning\scripts\$script" -ForegroundColor Gray
    }
}

# Move web projects
Write-Host "`nMoving web projects..." -ForegroundColor Yellow

$webProjects = @{
    "portfolio_site" = "web-projects\portfolio_site"
    "fluids-visualization" = "web-projects\fluids-visualization"
}

foreach ($project in $webProjects.GetEnumerator()) {
    if ((Test-Path $project.Key) -and !(Test-Path $project.Value)) {
        Move-Item -Path $project.Key -Destination $project.Value -Force
        Write-Host "  Moved: $($project.Key) -> $($project.Value)" -ForegroundColor Gray
    }
}

# Move lifestyle apps
Write-Host "`nMoving lifestyle applications..." -ForegroundColor Yellow

$lifestyleApps = @{
    "nutriplan" = "lifestyle-apps\nutriplan"
    "mealplanner_and_pantry_manager" = "lifestyle-apps\mealplanner_and_pantry_manager"
    "home_inventory_manager" = "lifestyle-apps\home_inventory_manager"
}

foreach ($app in $lifestyleApps.GetEnumerator()) {
    if ((Test-Path $app.Key) -and !(Test-Path $app.Value)) {
        Move-Item -Path $app.Key -Destination $app.Value -Force
        Write-Host "  Moved: $($app.Key) -> $($app.Value)" -ForegroundColor Gray
    }
}

# Move data exploration tools
Write-Host "`nMoving data exploration tools..." -ForegroundColor Yellow

$dataTools = @{
    "movie_explorer_full" = "data-exploration\movie_explorer_full"
    "city_map_explorer" = "data-exploration\city_map_explorer"
    "map-description" = "data-exploration\map-description"
}

foreach ($tool in $dataTools.GetEnumerator()) {
    if ((Test-Path $tool.Key) -and !(Test-Path $tool.Value)) {
        Move-Item -Path $tool.Key -Destination $tool.Value -Force
        Write-Host "  Moved: $($tool.Key) -> $($tool.Value)" -ForegroundColor Gray
    }
}

# Move engineering files
Write-Host "`nMoving engineering files..." -ForegroundColor Yellow

if ((Test-Path "fluids.py") -and !(Test-Path "engineering\fluids.py")) {
    Move-Item -Path "fluids.py" -Destination "engineering\fluids.py" -Force
    Write-Host "  Moved: fluids.py -> engineering\fluids.py" -ForegroundColor Gray
}

if ((Test-Path "flujo_en_tubería") -and !(Test-Path "engineering\flujo_en_tubería")) {
    Move-Item -Path "flujo_en_tubería" -Destination "engineering\flujo_en_tubería" -Force
    Write-Host "  Moved: flujo_en_tubería -> engineering\flujo_en_tubería" -ForegroundColor Gray
}

# Move PDF modules
Write-Host "`nMoving course materials (PDFs)..." -ForegroundColor Yellow

$pdfFiles = Get-ChildItem -Path $baseDir -Filter "Module*.pdf"
foreach ($pdf in $pdfFiles) {
    $destination = "course-materials\$($pdf.Name)"
    if (!(Test-Path $destination)) {
        Move-Item -Path $pdf.FullName -Destination $destination -Force
        Write-Host "  Moved: $($pdf.Name) -> course-materials\$($pdf.Name)" -ForegroundColor Gray
    }
}

# Move PDF generators
Write-Host "`nMoving PDF generator scripts..." -ForegroundColor Yellow

$pdfGenerators = Get-ChildItem -Path $baseDir -Filter "generate_pdf*.py"
foreach ($generator in $pdfGenerators) {
    $destination = "pdf-generators\$($generator.Name)"
    if (!(Test-Path $destination)) {
        Move-Item -Path $generator.FullName -Destination $destination -Force
        Write-Host "  Moved: $($generator.Name) -> pdf-generators\$($generator.Name)" -ForegroundColor Gray
    }
}

# Move data files
Write-Host "`nMoving data files..." -ForegroundColor Yellow

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
    if ((Test-Path $file) -and !(Test-Path "data\$file")) {
        Move-Item -Path $file -Destination "data\$file" -Force
        Write-Host "  Moved: $file -> data\$file" -ForegroundColor Gray
    }
}

# Move config files
Write-Host "`nMoving configuration files..." -ForegroundColor Yellow

$configFiles = @(
    "poetry.lock",
    "pyproject.toml",
    "setup.py",
    "LICENSE"
)

foreach ($file in $configFiles) {
    if ((Test-Path $file) -and !(Test-Path "config\$file")) {
        Copy-Item -Path $file -Destination "config\$file" -Force
        Write-Host "  Copied: $file -> config\$file" -ForegroundColor Gray
    }
}

# Move items to archive (duplicates and old versions)
Write-Host "`nArchiving old versions and duplicates..." -ForegroundColor Yellow

$archiveItems = @(
    "anki_generator.zip",
    "anki_generator (2).zip",
    "anki_generator (3).zip",
    "anki_generator (3)"
)

foreach ($item in $archiveItems) {
    if (Test-Path $item) {
        Move-Item -Path $item -Destination "archive\$item" -Force
        Write-Host "  Archived: $item" -ForegroundColor Gray
    }
}

# Handle nested Project_Workspace folder
if (Test-Path "Project_Workspace") {
    Write-Host "`nFound nested Project_Workspace folder. Moving unique items..." -ForegroundColor Yellow
    
    # Check for unique files in nested folder before moving to archive
    $nestedPath = "Project_Workspace"
    
    # Move any unique celebrity_gui, city_map_explorer, add_tags if they exist only in nested
    if ((Test-Path "$nestedPath\celebrity_gui") -and !(Test-Path "spanish-learning\media-learning\celebrity_gui")) {
        Move-Item -Path "$nestedPath\celebrity_gui" -Destination "spanish-learning\media-learning\celebrity_gui" -Force
        Write-Host "  Recovered: celebrity_gui from nested folder" -ForegroundColor Gray
    }
    
    # Archive the nested folder
    Move-Item -Path $nestedPath -Destination "archive\Project_Workspace_nested" -Force
    Write-Host "  Archived nested Project_Workspace folder" -ForegroundColor Gray
}

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "Reorganization Complete!" -ForegroundColor Green
Write-Host "`nSummary:" -ForegroundColor Yellow
Write-Host "  - Created organized directory structure" -ForegroundColor Gray
Write-Host "  - Moved projects to appropriate categories" -ForegroundColor Gray
Write-Host "  - Archived old versions and duplicates" -ForegroundColor Gray
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Review the 'archive' folder and delete if not needed" -ForegroundColor Gray
Write-Host "  2. Run 'git init' and add .gitignore if using version control" -ForegroundColor Gray
Write-Host "  3. Review each category folder for further cleanup opportunities" -ForegroundColor Gray