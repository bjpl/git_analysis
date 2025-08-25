# Quick Start Guide - Unsplash Image Search with GPT

Get started with the Unsplash Image Search with GPT application in just a few minutes!

## Table of Contents

- [Installation](#installation)
- [First Time Setup](#first-time-setup)
- [Basic Usage](#basic-usage)
- [Features Overview](#features-overview)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

## Installation

### Option 1: Download Pre-built Installer (Recommended)

1. **Download**: Go to [Releases](https://github.com/your-username/unsplash-image-search-gpt-description/releases)
2. **Choose**:
   - `unsplash-image-search-nsis-setup.exe` - Full installer with wizard
   - `unsplash-gpt-tool-portable.zip` - Portable version
3. **Install**: Run the installer and follow the wizard
4. **Launch**: Use desktop shortcut or Start Menu

### Option 2: Run from Source (Developers)

```bash
git clone https://github.com/your-username/unsplash-image-search-gpt-description.git
cd unsplash-image-search-gpt-description
pip install -r requirements.txt
python main.py
```

## First Time Setup

### Step 1: Get API Keys (Free Setup)

**Unsplash API Key** (Free - 50 searches/hour):
1. Visit [unsplash.com/developers](https://unsplash.com/developers)
2. Create a free account
3. Click "New Application"
4. Fill out the form (use "Personal Project" for description)
5. Copy your "Access Key"

**OpenAI API Key** (Paid - ~$0.001 per description):
1. Visit [platform.openai.com](https://platform.openai.com/signup)
2. Create an account and add payment method
3. Go to "API Keys" section
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)

### Step 2: Configure the Application

**Method A: Setup Wizard (Recommended)**
1. Launch the application
2. The setup wizard opens automatically
3. Paste your API keys when prompted
4. Choose data storage location
5. Click "Save Configuration"

**Method B: Manual Configuration**
Create `config.ini` in the application directory:
```ini
[UNSPLASH]
ACCESS_KEY=your_unsplash_access_key_here

[OPENAI]
API_KEY=your_openai_api_key_here
MODEL=gpt-4o-mini

[SETTINGS]
DATA_DIR=data
THEME=system
```

## Basic Usage

### Your First Search

1. **Launch** the application
2. **Enter a search term** in the text box (e.g., "mountain sunset")
3. **Click "Buscar Imagen"** or press Enter
4. **Wait** for an image to load (2-5 seconds)

*[Screenshot placeholder: Main window with search box and loaded image]*

### Generate Spanish Description

1. **Add notes** (optional) in the "Tus Notas" text area
2. **Click "Generar Descripción"** 
3. **Wait** for AI analysis (5-15 seconds)
4. **View** the Spanish description on the right

*[Screenshot placeholder: Generated description with extracted phrases]*

### Learn Vocabulary

1. **Click any blue phrase** in the extracted phrases section
2. **View translation** in the "Frases Objetivo" list
3. **Repeat** for other interesting phrases
4. **Export vocabulary** when ready using the Export button

*[Screenshot placeholder: Vocabulary section with clickable phrases]*

## Features Overview

### 🔍 Image Search
- **Search Unsplash**: 2+ million free images
- **Navigate results**: "Otra Imagen" for more options
- **High quality**: Professional photography
- **Zoom controls**: +/- buttons and mouse wheel

### 🤖 AI-Powered Descriptions
- **GPT-4 Vision**: Advanced image analysis
- **Spanish descriptions**: Natural, detailed text
- **Contextual**: Uses your notes for better descriptions
- **Educational focus**: Perfect for language learning

### 📚 Vocabulary Building
- **Auto-extraction**: Finds nouns, verbs, adjectives
- **Smart translation**: Context-aware English translations
- **Categories**: Organized by word type
- **No duplicates**: Automatic deduplication

### 📤 Export Options
- **Anki flashcards**: Tab-delimited format
- **Plain text**: Simple word lists
- **CSV format**: Spreadsheet-compatible
- **Context included**: Original search terms and context

### 🎨 User Experience
- **Light/Dark themes**: Toggle with Ctrl+T
- **Keyboard shortcuts**: Full keyboard navigation
- **Progress indicators**: Visual feedback during operations
- **Statistics tracking**: Images viewed and words learned

## Keyboard Shortcuts

### Essential Shortcuts
| Shortcut | Action |
|----------|--------|
| `Enter` | Search for images |
| `Ctrl+G` | Generate description |
| `Ctrl+N` | New search |
| `Ctrl+E` | Export vocabulary |
| `F1` | Show help |

### Navigation
| Shortcut | Action |
|----------|--------|
| `Tab` | Move to next field |
| `Shift+Tab` | Move to previous field |
| `Esc` | Clear current search |
| `Ctrl+Q` | Quit application |

### View Controls
| Shortcut | Action |
|----------|--------|
| `Ctrl+T` | Toggle light/dark theme |
| `Ctrl++` | Zoom in image |
| `Ctrl+-` | Zoom out image |
| `Ctrl+0` | Reset zoom to 100% |

*Tip: Hold Ctrl and scroll mouse wheel over image to zoom*

## Troubleshooting

### Common Issues

#### "API key not found" Error
- **Check**: Config file exists and contains valid keys
- **Verify**: No extra spaces or characters in keys
- **Test**: Keys work on respective service websites
- **Solution**: Re-run setup wizard

#### "Rate limit exceeded"
- **Unsplash**: Wait 1 hour (free tier: 50 requests/hour)
- **OpenAI**: Check billing and usage at platform.openai.com
- **Temporary**: Try a different search term

#### Images won't load
- **Check**: Internet connection is stable
- **Verify**: Unsplash API key is valid
- **Try**: Different search terms
- **Restart**: Close and reopen application

#### Slow performance
- **Memory**: Close other applications
- **Network**: Check internet speed (1+ Mbps needed)
- **Cache**: Clear data/cache folder
- **Zoom**: Reduce image zoom level

### Getting Help

1. **Built-in Help**: Press F1 for keyboard shortcuts and tips
2. **Documentation**: Check docs/ folder for detailed guides
3. **GitHub Issues**: [Report problems](https://github.com/your-username/unsplash-image-search-gpt-description/issues)
4. **Community**: GitHub Discussions for questions

## Next Steps

### Explore Advanced Features
- **Export to Anki**: Create flashcard decks for spaced repetition
- **Theme customization**: Switch between light and dark themes
- **Session tracking**: Review your learning progress
- **Batch searches**: Search multiple terms efficiently

### Optimize Your Workflow
- **Use specific search terms**: "Spanish architecture" vs "building"
- **Add context notes**: Help AI generate better descriptions
- **Regular vocabulary export**: Keep your learning organized
- **Explore categories**: Learn different types of vocabulary

### Language Learning Tips
- **Start simple**: Begin with concrete nouns (objects, animals)
- **Add context**: Use the notes field to specify what you want to learn
- **Practice regularly**: Short daily sessions work better than long ones
- **Export frequently**: Review vocabulary in other tools

### Advanced Usage
- **Custom searches**: Try specific themes like "food", "nature", "architecture"
- **Vocabulary goals**: Aim for 10-20 new words per session
- **Context learning**: Pay attention to how words are used in descriptions
- **Progressive difficulty**: Start with simple images, move to complex scenes

### Integration with Other Tools
- **Anki**: Import vocabulary for spaced repetition
- **Language apps**: Use vocabulary in Duolingo, Babbel, etc.
- **Note-taking**: Import to Notion, Obsidian, or other systems
- **Spreadsheets**: Analyze learning progress with exported CSV data

---

## Example Workflow

### Sample Session: Learning Food Vocabulary

1. **Search**: "Spanish paella"
2. **Generate**: Get AI description in Spanish
3. **Learn**: Click on food-related words (ingredientes, arroz, mariscos)
4. **Context**: Add note "traditional Spanish dish from Valencia"
5. **Continue**: Try "tapas", "jamón ibérico", "gazpacho"
6. **Export**: Save 15-20 food terms to Anki

**Result**: Rich vocabulary around Spanish cuisine with visual context!

### Time Investment
- **Setup**: 5-10 minutes (one time)
- **Per search**: 30-60 seconds
- **Per description**: 10-30 seconds
- **Vocabulary building**: 2-5 words per image
- **Export**: 1-2 minutes

**Total**: 15-20 minutes for 30-50 new vocabulary words with visual context

---

## Support

Need help? We're here for you:

- 📖 **Documentation**: Check the `docs/` folder
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/your-username/unsplash-image-search-gpt-description/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/your-username/unsplash-image-search-gpt-description/discussions)
- ❓ **Questions**: Community discussions or documentation

**Happy learning! ¡Buena suerte con el español!** 🇪🇸