# Unsplash Image Search GPT Tool - User Manual

## Table of Contents
- [Installation Instructions](#installation-instructions)
- [First-Time Setup](#first-time-setup)
- [Feature Documentation](#feature-documentation)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Troubleshooting Guide](#troubleshooting-guide)
- [FAQ](#frequently-asked-questions)
- [API Key Setup Guide](#api-key-setup-guide)
- [Data Export/Import](#data-export-and-import)

## Installation Instructions

### Option 1: Windows Installer (Recommended)

1. **Download the Installer**
   - Go to the [Releases page](https://github.com/yourusername/unsplash-image-search-gpt-description/releases)
   - Download `UnsplashGPTTool-Setup.exe`
   - File size: approximately 150MB

2. **Run the Installer**
   - Double-click the downloaded installer
   - If Windows SmartScreen appears, click "More info" → "Run anyway"
   - Follow the installation wizard
   - Default installation location: `C:\Program Files\UnsplashGPTTool\`

3. **First Launch**
   - Launch from Start Menu or Desktop shortcut
   - The application will open the Setup Wizard automatically

### Option 2: Portable Version

1. **Download the Portable Package**
   - Download `UnsplashGPTTool-Portable.zip` from releases
   - Extract to any folder (e.g., `C:\Tools\UnsplashGPTTool\`)

2. **Run the Application**
   - Navigate to the extracted folder
   - Double-click `UnsplashGPTTool.exe`
   - No installation required

### Option 3: Run from Source Code

1. **Prerequisites**
   - Python 3.8 or higher
   - Git (optional)

2. **Download and Setup**
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/unsplash-image-search-gpt-description.git
   cd unsplash-image-search-gpt-description
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run the application
   python main.py
   ```

### System Requirements

- **Operating System**: Windows 10/11, macOS 10.14+, Linux Ubuntu 18.04+
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 200MB free space
- **Internet**: Required for API calls and image downloads
- **Display**: 1024x768 minimum resolution

## First-Time Setup

### Setup Wizard Walkthrough

When you first launch the application, the Setup Wizard will guide you through configuration:

#### Step 1: Welcome Screen
- Click "Get Started" to begin setup
- Review the application overview

#### Step 2: API Keys Configuration
The application requires two API keys:

1. **Unsplash Access Key**
   - Used for searching and downloading images
   - Free tier: 50 requests per hour
   - Enter your key in the first field

2. **OpenAI API Key**
   - Used for generating descriptions and translations
   - Pay-per-use model
   - Enter your key in the second field (masked for security)

3. **GPT Model Selection**
   - `gpt-4o-mini`: Best value option (~$0.001 per description)
   - `gpt-4o`: Higher quality (~$0.01 per description)
   - `gpt-4-turbo`: Advanced features (~$0.02 per description)

#### Step 3: Data Storage Location
- Choose where to save your data
- Default: `Documents/UnsplashGPTTool/`
- Recommended: Keep default unless you have specific needs

#### Step 4: Language Preferences
- Primary language: Spanish (for descriptions)
- Secondary language: English (for translations)
- Interface language: English

#### Step 5: Complete Setup
- Review your settings
- Click "Finish Setup" to save configuration
- The main application window will open

### Configuration Files Location

Your settings are stored in:
- **Windows**: `%APPDATA%\UnsplashGPTTool\config.ini`
- **macOS**: `~/Library/Application Support/UnsplashGPTTool/config.ini`
- **Linux**: `~/.config/UnsplashGPTTool/config.ini`

## Feature Documentation

### 1. Image Search

#### Basic Search
1. Enter a search term in the search bar (e.g., "mountain", "coffee", "architecture")
2. Click "Buscar Imagen" or press Enter
3. The application will find and display a relevant image from Unsplash

#### Search Tips
- **Use specific terms**: "red sports car" instead of just "car"
- **Try different languages**: Works with Spanish, English, and other languages
- **Use descriptive phrases**: "sunset over ocean" for better results
- **Avoid very specific brand names**: Generic terms work better

#### Image Navigation
- **Another Image**: Click "Otra Imagen" to get a different image for the same search
- **New Search**: Click "Nueva Búsqueda" to clear everything and start fresh
- **Image Quality**: Images are displayed in medium resolution for faster loading

### 2. AI-Generated Descriptions

#### Generating Descriptions
1. Load an image using the search function
2. (Optional) Add notes or context in the "Tus Notas" area
3. Click "Generar Descripción" or press Ctrl+G
4. Wait for the GPT model to analyze the image
5. The description appears in Spanish in the "Descripción Generada por GPT" section

#### Description Features
- **Detailed Analysis**: GPT-4 Vision provides comprehensive image descriptions
- **Spanish Language**: All descriptions are generated in Spanish
- **Context Aware**: Uses your notes to provide more relevant descriptions
- **Copy Function**: Click "📋 Copiar" to copy the description to clipboard

#### Customizing Descriptions
Add context notes to get better descriptions:
- "Describe the colors and mood"
- "Focus on the architectural details"
- "Explain what the person might be feeling"
- "Describe this for a language learner"

### 3. Vocabulary Extraction and Learning

#### Automatic Vocabulary Extraction
After generating a description, the application automatically:
1. Identifies key nouns, verbs, and adjectives
2. Groups them by word type
3. Displays them in clickable cards
4. Excludes common words to focus on vocabulary worth learning

#### Adding Words to Your Collection
1. Click any phrase in the "Frases Extraídas" section
2. The application will translate it to English
3. The Spanish-English pair is added to your vocabulary list
4. All vocabulary is automatically saved

#### Vocabulary Categories
- **Sustantivos (Nouns)**: Objects, people, places
- **Verbos (Verbs)**: Actions and states
- **Adjetivos (Adjectives)**: Descriptive words
- **Frases (Phrases)**: Useful expressions

### 4. Translation System

#### Click-to-Translate
- Click any Spanish phrase to get an instant English translation
- Translations consider context from the image description
- High-quality translations using GPT models

#### Translation Accuracy
- Uses the same OpenAI model as descriptions
- Context-aware translations
- Considers cultural and regional variations
- Provides natural, conversational English

### 5. Data Management

#### Session Tracking
- Every image search and description is automatically saved
- Session data includes: search query, image URL, notes, description, timestamp
- View statistics in the status bar: "Images: X | Words: Y"

#### Vocabulary Database
- All Spanish-English pairs are saved to `vocabulary.csv`
- Includes context, source image, and date added
- Prevents duplicate entries automatically
- Searchable and filterable

#### Cache System
- Recently viewed images are cached for faster access
- Cache clears automatically to save disk space
- Improves performance when browsing multiple images

### 6. Export and Sharing

#### Export Options
Click "Exportar" to access export features:

1. **Vocabulary Export**
   - CSV format for spreadsheets
   - JSON format for other applications
   - Anki-compatible format for flashcards

2. **Session Export**
   - Complete session history
   - Includes images, descriptions, and timestamps
   - Perfect for creating study materials

3. **PDF Report**
   - Visual summary of your learning session
   - Images with descriptions and vocabulary
   - Great for offline review

## Keyboard Shortcuts

### Global Shortcuts
- `Enter`: Start image search
- `Ctrl+G`: Generate description for current image
- `Ctrl+N`: New search (clear everything)
- `Ctrl+E`: Open export dialog
- `Ctrl+Q`: Quit application
- `F1`: Open help system
- `Esc`: Cancel current operation

### Text Editing
- `Ctrl+A`: Select all text in notes area
- `Ctrl+C`: Copy selected text
- `Ctrl+V`: Paste text
- `Ctrl+Z`: Undo in notes area

### Navigation
- `Tab`: Move between interface elements
- `Shift+Tab`: Move backward between elements
- `Space`: Activate focused button
- `Arrow Keys`: Navigate vocabulary cards

### Advanced Shortcuts
- `Ctrl+Shift+D`: Toggle debug mode
- `Ctrl+Shift+C`: Clear image cache
- `Ctrl+Shift+R`: Reload application settings
- `F5`: Refresh current image search

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. "API Key Not Found" Error

**Symptoms**:
- Error message on startup
- Unable to search images or generate descriptions

**Solutions**:
1. **Re-run Setup Wizard**: Go to Settings → Configuration
2. **Check API Keys**: Ensure keys are correctly entered
3. **Verify File Permissions**: Make sure config.ini can be written
4. **Reset Configuration**: Delete config.ini and restart application

**Prevention**:
- Don't share your API keys
- Keep backups of your configuration

#### 2. Images Not Loading

**Symptoms**:
- Blank image area
- "Failed to load image" message
- Slow loading times

**Solutions**:
1. **Check Internet Connection**: Verify network connectivity
2. **Try Different Search Terms**: Some terms may have limited results
3. **Clear Image Cache**: Settings → Clear Cache
4. **Restart Application**: Close and reopen the program
5. **Check Unsplash API Status**: Visit [status.unsplash.com](https://status.unsplash.com)

#### 3. Rate Limit Exceeded

**Symptoms**:
- "Rate limit exceeded" error messages
- Unable to search new images
- API calls failing

**Solutions**:
1. **Unsplash Limits**: Wait 1 hour for limits to reset (50 requests/hour)
2. **OpenAI Limits**: Check your account at [platform.openai.com](https://platform.openai.com)
3. **Reduce Usage**: Use cached images when possible
4. **Upgrade API Plan**: Consider paid tiers for higher limits

#### 4. Descriptions Not Generating

**Symptoms**:
- "Generate Description" button does nothing
- Error messages when clicking generate
- Incomplete or strange descriptions

**Solutions**:
1. **Verify OpenAI API Key**: Check key validity
2. **Check Account Credits**: Ensure sufficient OpenAI credits
3. **Try Different GPT Model**: Switch to gpt-4o-mini for lower cost
4. **Check Image URL**: Ensure image loaded properly
5. **Restart Application**: Close and reopen

#### 5. Application Won't Start

**Symptoms**:
- Application crashes on startup
- Windows error messages
- Blank window appears

**Solutions**:
1. **Run as Administrator**: Right-click → "Run as administrator"
2. **Check System Requirements**: Verify Windows version compatibility
3. **Antivirus Interference**: Add application to antivirus exclusions
4. **Reinstall Application**: Download fresh copy and reinstall
5. **Check Dependencies**: Ensure all required libraries are present

#### 6. Slow Performance

**Symptoms**:
- Slow image loading
- Delayed description generation
- UI freezing or lag

**Solutions**:
1. **Close Other Applications**: Free up system memory
2. **Clear Cache**: Settings → Clear All Data
3. **Restart Computer**: Fresh system state
4. **Check Internet Speed**: Ensure adequate bandwidth
5. **Lower Image Quality**: Use smaller image sizes

### Advanced Troubleshooting

#### Debug Mode
Enable debug mode for detailed error information:
1. Press `Ctrl+Shift+D` to toggle debug mode
2. Reproduce the issue
3. Check the debug output in the console
4. Share debug information when reporting bugs

#### Log Files
Application logs are stored in:
- **Windows**: `%APPDATA%\UnsplashGPTTool\logs\`
- **macOS**: `~/Library/Logs/UnsplashGPTTool/`
- **Linux**: `~/.local/share/UnsplashGPTTool/logs/`

#### Configuration Reset
To completely reset the application:
1. Close the application
2. Delete the configuration directory
3. Restart the application
4. Complete setup wizard again

## Frequently Asked Questions

### General Usage

**Q: Is this application free to use?**
A: The application is free, but you need API keys from Unsplash (free tier) and OpenAI (paid service). Typical usage costs $1-5 per month for OpenAI.

**Q: Do I need internet connection?**
A: Yes, the application requires internet for API calls and image downloads. Your data is stored locally.

**Q: What image formats are supported?**
A: The application displays JPEG and PNG images from Unsplash. All images are web-optimized.

**Q: Can I use this for commercial purposes?**
A: Check Unsplash's license terms for image usage. The application itself can be used commercially.

### API Keys and Costs

**Q: How much does OpenAI cost?**
A: Costs vary by model:
- gpt-4o-mini: ~$0.001 per description (recommended)
- gpt-4o: ~$0.01 per description
- gpt-4-turbo: ~$0.02 per description

**Q: What if I exceed my Unsplash rate limit?**
A: Free tier allows 50 requests per hour. Wait for reset or upgrade to paid plan.

**Q: Are my API keys secure?**
A: Keys are stored locally in encrypted configuration files and never transmitted except to official APIs.

### Learning and Vocabulary

**Q: Can I export my vocabulary to other apps?**
A: Yes! Export to CSV, JSON, or Anki-compatible formats. Perfect for flashcard apps.

**Q: Why are some words not extracted?**
A: The system filters out common words (articles, prepositions) to focus on vocabulary worth learning.

**Q: Can I add my own translations?**
A: Currently, translations are automatic. Manual editing is planned for future versions.

### Technical Questions

**Q: Which operating systems are supported?**
A: Windows 10/11 (primary), macOS 10.14+, and Linux Ubuntu 18.04+.

**Q: Can I run multiple instances?**
A: No, only one instance can run at a time to prevent conflicts.

**Q: How much storage does the app use?**
A: Base application: ~150MB. Data files grow based on usage, typically 10-50MB.

### Troubleshooting

**Q: The application is slow, what can I do?**
A: Clear cache, close other programs, check internet speed, and restart the application.

**Q: I get SSL errors, how to fix?**
A: Update your system, check firewall settings, and try running as administrator.

**Q: Can I backup my data?**
A: Yes! Export your vocabulary and copy your data directory for complete backup.

## API Key Setup Guide

### Getting Your Unsplash API Key

1. **Create Unsplash Account**
   - Visit [unsplash.com](https://unsplash.com)
   - Sign up for a free account
   - Verify your email address

2. **Register as Developer**
   - Go to [unsplash.com/developers](https://unsplash.com/developers)
   - Click "Register as a developer"
   - Accept the API Terms of Service

3. **Create New Application**
   - Click "New Application"
   - Fill out application details:
     - Application name: "My Image Search Tool"
     - Description: "Personal image search and learning tool"
   - Accept guidelines

4. **Get Your Access Key**
   - Copy the "Access Key" (starts with underscore)
   - Keep this key private and secure
   - Never share or commit to version control

### Getting Your OpenAI API Key

1. **Create OpenAI Account**
   - Visit [platform.openai.com](https://platform.openai.com)
   - Sign up for an account
   - Verify phone number for security

2. **Add Payment Method**
   - Go to Billing → Payment methods
   - Add a credit card or payment method
   - OpenAI requires payment info even for free tier

3. **Create API Key**
   - Navigate to API Keys section
   - Click "Create new secret key"
   - Give it a descriptive name: "Image Description Tool"
   - Copy the key immediately (won't be shown again)

4. **Set Usage Limits (Recommended)**
   - Go to Billing → Usage limits
   - Set monthly limit (e.g., $10) to control costs
   - Enable email notifications

### Security Best Practices

**Protecting Your API Keys**:
- Never share keys with others
- Don't post keys online or in code
- Use different keys for different applications
- Regularly rotate keys for security
- Monitor usage for unauthorized access

**Key Storage**:
- Keys are stored locally in encrypted format
- Only you have access to your configuration
- Backup your configuration securely
- Use a password manager for additional security

### Usage Monitoring

**Unsplash Usage**:
- Monitor at [unsplash.com/developers](https://unsplash.com/developers)
- Free tier: 50 requests per hour
- Track remaining requests in app status bar

**OpenAI Usage**:
- Monitor at [platform.openai.com/usage](https://platform.openai.com/usage)
- View costs and token consumption
- Set up billing alerts

## Data Export and Import

### Export Formats

#### 1. Vocabulary Export

**CSV Format** (Default):
```csv
Spanish,English,Context,Source,Date,Query
"el paisaje","the landscape","Beautiful mountain view","https://...","2024-01-15","mountains"
"las montañas","the mountains","Snow-capped peaks","https://...","2024-01-15","mountains"
```

**JSON Format** (For developers):
```json
{
  "vocabulary": [
    {
      "spanish": "el paisaje",
      "english": "the landscape",
      "context": "Beautiful mountain view",
      "source": "https://...",
      "date": "2024-01-15",
      "query": "mountains"
    }
  ]
}
```

**Anki Format** (For flashcards):
```csv
Front,Back,Extra
"el paisaje","the landscape","Beautiful mountain view (mountains)"
"las montañas","the mountains","Snow-capped peaks (mountains)"
```

#### 2. Session Export

**Complete Session Data**:
```json
{
  "session_id": "session_2024-01-15_14-30",
  "date": "2024-01-15T14:30:00",
  "images": [
    {
      "query": "mountains",
      "image_url": "https://...",
      "description": "Un paisaje montañoso...",
      "notes": "User notes here",
      "vocabulary": [...]
    }
  ],
  "statistics": {
    "images_processed": 5,
    "words_learned": 23,
    "session_duration": "45 minutes"
  }
}
```

### Import Options

#### Importing Previous Data
1. **Automatic Migration**: Old data is automatically detected and imported
2. **Manual Import**: Use File → Import to load backup files
3. **Merge Mode**: Combine imported data with existing vocabulary

#### Supported Import Formats
- **CSV files**: Vocabulary lists from spreadsheets
- **JSON files**: Previous exports and backups
- **Text files**: Simple word lists (one per line)

### Backup and Restore

#### Creating Backups
1. **Automatic Backup**: Application creates daily backups automatically
2. **Manual Backup**: Export all data before major changes
3. **Cloud Backup**: Copy exports to cloud storage for safety

#### Backup Locations
- **Windows**: `%USERPROFILE%\Documents\UnsplashGPTTool\Backups\`
- **macOS**: `~/Documents/UnsplashGPTTool/Backups/`
- **Linux**: `~/Documents/UnsplashGPTTool/Backups/`

#### Restore Process
1. Locate backup files
2. Use File → Import → Select backup file
3. Choose merge or replace options
4. Restart application to complete restore

### Integration with Other Tools

#### Anki Flashcards
1. Export vocabulary in Anki format
2. Import into Anki deck
3. Customize card templates as needed

#### Language Learning Apps
- Export to CSV for import into other apps
- Use JSON format for custom integrations
- Share vocabulary lists with study groups

#### Spreadsheet Applications
- Open CSV files in Excel, Google Sheets, or LibreOffice
- Create custom study materials
- Track learning progress over time

---

## Support and Resources

### Getting Help
- **In-app Help**: Press F1 or Help → User Manual
- **GitHub Issues**: [Report bugs and request features](https://github.com/yourusername/unsplash-image-search-gpt-description/issues)
- **Documentation**: Latest docs at [project website]
- **Community**: Join our Discord server for help and tips

### Contributing
- **Bug Reports**: Use GitHub issues with detailed information
- **Feature Requests**: Describe your use case and needs
- **Code Contributions**: See CONTRIBUTING.md for guidelines
- **Translations**: Help translate the interface to other languages

### Version History
Check the [Releases page](https://github.com/yourusername/unsplash-image-search-gpt-description/releases) for:
- Latest version information
- New features and improvements
- Bug fixes and security updates
- Migration guides for major updates

---

*Last updated: January 2024 | Version 1.0.0*