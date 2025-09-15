# Files and Folders Safe to Delete

## ⚠️ Review Before Deleting
Please review each item before deletion. Make backups if unsure.

## 🗑️ Definitely Safe to Delete

### Duplicate Archives
These are compressed versions of folders that already exist extracted:
- `anki_generator.zip` - Keep the extracted `anki_generator/` folder
- `anki_generator (2).zip` - Duplicate archive
- `anki_generator (3).zip` - Duplicate archive  
- `anki_generator (3)/` - Duplicate extracted folder

### Nested Duplicate Folder
- `Project_Workspace/` - This is a complete duplicate of the root structure
  - Before deleting, verify no unique files exist inside
  - Check specifically for any unique versions of projects

### Build Artifacts (Safe to Delete)
These are generated files that can be recreated:
- All `__pycache__/` directories
- All `*.pyc` files
- All `build/` directories
- All `dist/` directories
- All `.egg-info/` directories
- `nul` files (Windows null device accidentally created)

### Log Files (Optional - Keep Recent Ones)
Review dates and keep recent logs if needed for debugging:
- `logs/application-*.log.gz` - Compressed old logs
- `logs/error-*.log.gz` - Compressed old error logs
- `revision_log.txt` - If old
- `session_log.txt` - If old
- `technical_log.txt` - If old
- `content_log.txt` - If old
- `exercise_log.txt` - If old
- `recipe_log.txt` - If old
- `app.log` - If old
- `inventory_app.log` - If old
- `subjunctive_practice.log` - If old

### Generated Output Files (Review First)
Check if these contain important data before deleting:
- `YouTubeTranscriptGPT/outputs/` - Old processed transcripts (keep if valuable)
- `YouTubeTranscriptGPT/transcripts/` - Raw transcripts (regeneratable)
- Multiple duplicate outputs with same content but different timestamps

### Temporary Files
- Any `*.tmp` files
- Any `*.bak` files
- Any `*.backup` files
- Any `cache/` directories
- Any `temp/` or `tmp/` directories

### OS-Generated Files
- `desktop.ini` files
- `Thumbs.db` files
- `.DS_Store` files (if on Mac)

## ⚡ Quick Cleanup Commands

### Windows PowerShell (Run as Administrator):
```powershell
# Remove Python cache files
Get-ChildItem -Path . -Include __pycache__ -Recurse -Directory | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Include *.pyc -Recurse -File | Remove-Item -Force

# Remove build artifacts
Get-ChildItem -Path . -Include build,dist -Recurse -Directory | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Include *.egg-info -Recurse -Directory | Remove-Item -Recurse -Force

# Remove temporary files
Get-ChildItem -Path . -Include *.tmp,*.bak,*.backup -Recurse -File | Remove-Item -Force

# Remove OS files
Get-ChildItem -Path . -Include desktop.ini,Thumbs.db -Recurse -File -Force | Remove-Item -Force

# Remove old compressed logs
Get-ChildItem -Path . -Include *.log.gz -Recurse -File | Remove-Item -Force

# Remove zip archives (after verifying extracted versions exist)
Get-ChildItem -Path . -Filter "anki_generator*.zip" | Remove-Item -Force
```

### Linux/Mac Bash:
```bash
# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# Remove build artifacts  
find . -type d -name "build" -exec rm -rf {} + 2>/dev/null
find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null

# Remove temporary files
find . -type f \( -name "*.tmp" -o -name "*.bak" -o -name "*.backup" \) -delete

# Remove OS files
find . -type f \( -name "desktop.ini" -o -name "Thumbs.db" -o -name ".DS_Store" \) -delete

# Remove old compressed logs
find . -type f -name "*.log.gz" -delete

# Remove zip archives
rm -f anki_generator*.zip
```

## 📊 Estimated Space Savings

- Zip archives: ~50-100 MB
- Nested Project_Workspace: ~500 MB - 1 GB
- Build artifacts: ~100-200 MB
- Cache and temp files: ~50-100 MB
- Old logs: ~10-50 MB

**Total potential savings: 700 MB - 1.5 GB**

## ⚠️ DO NOT DELETE

These files should be kept even if they seem redundant:
- Any `.env` files (contain API keys)
- Any `poetry.lock` files in project roots (dependency locks)
- Any `.git/` directories (version control)
- Any virtual environment folders (`venv/`, `.venv/`)
- Database files (`.db`, `.sqlite`, `.sqlite3`)
- Original source code files
- Configuration files in use
- Recent log files (last 30 days)

## 🔄 After Cleanup

1. Run the safe reorganization script to create organized view
2. Test a few projects to ensure they still work
3. Commit the cleaned workspace to git if using version control
4. Consider setting up automated cleanup in CI/CD