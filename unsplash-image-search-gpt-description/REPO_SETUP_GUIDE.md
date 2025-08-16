# GitHub Repository Setup Guide

This guide will walk you through setting up this project as a GitHub repository for public distribution.

## Pre-Release Checklist

### 1. Clean Sensitive Data
```bash
# Remove any test API keys or personal data
rm -f .env
rm -f config.ini
rm -rf data/
rm -f *.log
rm -f session_log.txt
rm -f target_word_list.csv
```

### 2. Verify Core Files
Ensure these files exist and are updated:
- ✅ `main.py` - Main application
- ✅ `config_manager.py` - Configuration system
- ✅ `requirements.txt` - Python dependencies
- ✅ `.env.example` - API key template
- ✅ `.gitignore` - Excludes sensitive files
- ✅ `README.md` - User documentation
- ✅ `LICENSE` - MIT license
- ✅ `build.bat` / `build.sh` - Build scripts

## Step-by-Step Repository Setup

### Step 1: Initialize Git Repository
```bash
cd unsplash-image-search-gpt-description
git init
```

### Step 2: Configure Git (First Time Only)
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Step 3: Add All Files
```bash
git add .
git status  # Review what will be committed
```

### Step 4: Create Initial Commit
```bash
git commit -m "Initial release: Unsplash GPT Tool v1.0.0

- Image search via Unsplash API
- GPT-4 Vision Spanish descriptions  
- Vocabulary extraction and translation
- Export to Anki/CSV formats
- Cross-platform support (Windows/Mac/Linux)"
```

### Step 5: Create GitHub Repository

1. Go to [GitHub.com](https://github.com/new)
2. Create a new repository:
   - **Name:** `unsplash-gpt-spanish-learning`
   - **Description:** "Desktop app for Spanish vocabulary learning through AI-powered image descriptions"
   - **Public** repository
   - **DO NOT** initialize with README (we have one)
   - **DO NOT** add .gitignore (we have one)
   - **License:** Skip (we have LICENSE file)

### Step 6: Connect to GitHub
```bash
# Replace USERNAME with your GitHub username
git remote add origin https://github.com/USERNAME/unsplash-gpt-spanish-learning.git
git branch -M main
git push -u origin main
```

### Step 7: Create First Release

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. **Tag:** `v1.0.0`
4. **Release title:** "Version 1.0.0 - Initial Release"
5. **Description:**
```markdown
## 🎉 First Public Release

### Features
- 🖼️ Search images from Unsplash
- 🤖 Generate Spanish descriptions with GPT-4 Vision
- 📝 Extract vocabulary automatically
- 🌐 Translate Spanish to English
- 📊 Export to Anki, CSV, or plain text
- 📈 Track learning progress

### Installation

#### Option 1: Run from Source
```bash
git clone https://github.com/USERNAME/unsplash-gpt-spanish-learning.git
cd unsplash-gpt-spanish-learning
pip install -r requirements.txt
python main.py
```

#### Option 2: Download Windows Executable
Download `unsplash-gpt-tool.exe` from the Assets below.

### Requirements
- Unsplash API key (free)
- OpenAI API key (paid)

### Quick Start
1. Run the application
2. Enter your API keys when prompted
3. Search for any image
4. Generate Spanish descriptions
5. Build your vocabulary!

### Tested On
- Windows 10/11 ✅
- Python 3.8-3.13 ✅
- macOS (source only) ✅
- Linux (source only) ✅
```

6. **Attach files** (optional):
   - Build the exe: `build.bat`
   - Upload `dist/unsplash-gpt-tool.exe`

### Step 8: Add Repository Topics

On your GitHub repo page, click the gear icon next to "About" and add topics:
- `spanish-learning`
- `language-learning`
- `gpt-4`
- `unsplash-api`
- `vocabulary`
- `anki`
- `python`
- `tkinter`
- `desktop-app`
- `education`

### Step 9: Update README with Badges

Add these badges to the top of your README.md:
```markdown
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![GitHub release](https://img.shields.io/github/v/release/USERNAME/unsplash-gpt-spanish-learning)
![GitHub stars](https://img.shields.io/github/stars/USERNAME/unsplash-gpt-spanish-learning?style=social)
```

## Ongoing Maintenance

### For Each Update:

1. **Update version** in relevant files
2. **Test thoroughly** with `python qa_test.py`
3. **Commit changes:**
```bash
git add .
git commit -m "feat: description of new feature"
git push
```

4. **Create new release** on GitHub with changelog

### Commit Message Convention:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions
- `chore:` Maintenance tasks

### Handling Issues:

1. **Bug Reports:** Use GitHub Issues
2. **Feature Requests:** Use GitHub Discussions
3. **Security Issues:** Enable GitHub Security Advisories

## Community Guidelines

### Add CONTRIBUTING.md:
```markdown
# Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python qa_test.py`
5. Submit a pull request

Please ensure:
- Code follows existing style
- Tests pass
- Documentation is updated
- No API keys are committed
```

### Add CODE_OF_CONDUCT.md:
Use GitHub's standard Code of Conduct template.

## Marketing Your Repository

### Where to Share:

1. **Reddit:**
   - r/learnspanish
   - r/Python
   - r/languagelearning
   
2. **Discord/Slack:**
   - Python communities
   - Language learning servers
   
3. **Social Media:**
   - Twitter/X with #LearnSpanish #Python #GPT4
   - LinkedIn for professional network
   
4. **Dev Platforms:**
   - dev.to article
   - Medium tutorial
   - YouTube demo video

### Example Announcement Post:
```
🚀 Just released: Unsplash GPT Spanish Learning Tool!

Learn Spanish vocabulary through AI-powered image descriptions.

✨ Features:
- Search any image topic
- Get detailed Spanish descriptions via GPT-4
- Auto-extract vocabulary
- Export to Anki for flashcards
- Track your progress

🔗 GitHub: [your-link]
📖 Free & Open Source (MIT License)

#LearnSpanish #GPT4 #OpenSource #LanguageLearning
```

## Success Metrics

Track your repository's success:
- ⭐ GitHub stars
- 🍴 Forks
- 📥 Release downloads
- 🐛 Issues (engagement)
- 👥 Contributors

## Final Notes

- **Respond quickly** to issues and PRs
- **Document everything** clearly
- **Be welcoming** to contributors
- **Update regularly** with improvements
- **Credit contributors** in releases

Good luck with your open source project! 🎉