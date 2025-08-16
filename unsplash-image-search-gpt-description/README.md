# Unsplash Image Search with GPT Description Generator

A desktop application that searches Unsplash for images and uses OpenAI's GPT-4 Vision to generate detailed Spanish descriptions. Perfect for language learning, content creation, and vocabulary building.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- 🖼️ **Image Search**: Search and browse images from Unsplash with pagination
- 🤖 **AI Descriptions**: Generate detailed Spanish descriptions using GPT-4 Vision
- 📝 **Vocabulary Extraction**: Automatically extract nouns, verbs, adjectives, and key phrases
- 🌐 **Translation**: Click any Spanish phrase to translate it to English
- 💾 **Data Export**: Save vocabulary and session data for later review
- 🎨 **Clean UI**: Simple, intuitive interface built with Tkinter

## Quick Start

### Option 1: Download Pre-built Executable (Windows)

1. Download the latest release from [Releases](../../releases)
2. Extract the zip file
3. Run `unsplash-gpt-tool.exe`
4. Enter your API keys when prompted (first run only)

### Option 2: Run from Source

#### Prerequisites
- Python 3.8 or higher
- Unsplash API key ([Get one free](https://unsplash.com/developers))
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

#### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/unsplash-image-search-gpt-description.git
cd unsplash-image-search-gpt-description
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API keys:

   **Method A: Using .env file (Recommended for development)**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

   **Method B: Using the Setup Wizard**
   - Just run the app and it will prompt for keys on first launch

4. Run the application:
```bash
python main.py
```

## Configuration

### API Keys

On first run, the application will open a setup wizard to configure your API keys. Keys are stored locally in `config.ini` and never shared.

You can also set keys via environment variables:
- `UNSPLASH_ACCESS_KEY`: Your Unsplash API access key
- `OPENAI_API_KEY`: Your OpenAI API key
- `GPT_MODEL`: Model to use (default: `gpt-4o-mini`)

### Data Storage

The application stores data in the `data/` directory:
- `session_log.json`: Complete session history
- `vocabulary.csv`: Extracted Spanish-English word pairs

## Building from Source

To create your own executable:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the executable:
```bash
# Windows
build.bat

# Linux/Mac
./build.sh
```

The executable will be created in the `dist/` directory.

## Usage Guide

1. **Search Images**: Enter a search term and click "Buscar Imagen"
2. **Add Notes**: Optionally add context or notes about what you see
3. **Generate Description**: Click "Generar Descripción" to get an AI-generated Spanish description
4. **Extract Vocabulary**: Phrases are automatically extracted and categorized
5. **Translate**: Click any Spanish phrase to translate it to English
6. **Save Data**: All sessions and vocabulary are automatically saved

### Keyboard Shortcuts
- `Enter`: Search for images
- `Ctrl+G`: Generate description
- `Ctrl+N`: New search
- `Esc`: Clear current search

## API Usage & Costs

### Unsplash API
- **Free Tier**: 50 requests per hour
- **Rate Limits**: The app handles rate limiting automatically

### OpenAI API
- **GPT-4o-mini**: ~$0.001 per description
- **GPT-4o**: ~$0.01 per description
- Costs vary based on description length and model choice

## Troubleshooting

### "API key not found"
- Ensure your API keys are correctly entered in the setup wizard
- Check that the `config.ini` file exists in the application directory

### "Rate limit exceeded"
- Unsplash: Wait an hour for the limit to reset
- OpenAI: Check your account credits at [platform.openai.com](https://platform.openai.com)

### Images not loading
- Check your internet connection
- Verify Unsplash API key is valid
- Try a different search term

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Unsplash](https://unsplash.com) for providing free access to beautiful images
- [OpenAI](https://openai.com) for GPT-4 Vision API
- Contributors and users of this tool

## Support

If you encounter any issues or have questions:
- Open an issue on [GitHub Issues](../../issues)
- Check existing issues for solutions
- Include error messages and steps to reproduce

---

Made with ❤️ for language learners and content creators