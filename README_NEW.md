# Project Workspace

A comprehensive collection of development projects focused primarily on Spanish language learning, with additional web development, lifestyle management, and data exploration tools.

## 📁 Directory Structure

```
Project_Workspace/
├── spanish-learning/        # 70% of projects - Spanish language learning tools
├── web-projects/           # Web development projects
├── lifestyle-apps/         # Daily life management applications
├── data-exploration/       # Data analysis and visualization tools
├── engineering/            # Engineering and scientific scripts
├── course-materials/       # Educational PDFs and materials
├── pdf-generators/         # PDF generation utilities
├── data/                   # Shared data files
└── config/                 # Workspace configuration files
```

## 🎯 Project Categories

### 🇪🇸 Spanish Learning Tools
The largest category containing various tools for Spanish language acquisition:

#### Core Applications
- **MySpanishApp** - Comprehensive Spanish learning session tracker with vocabulary and grammar modules
- **conjugation_gui** - Interactive Spanish verb conjugation practice with multiple tenses
- **subjunctive_practice** - Specialized tool for mastering Spanish subjunctive mood

#### Flashcard & Vocabulary Tools
- **anki_generator** - Automated Anki flashcard generation from Spanish content
- **add_tags** - AI-powered semantic tagging for Spanish vocabulary
- **merge_gui** - CSV merger for consolidating vocabulary lists

#### Media-Based Learning
- **YouTubeTranscriptGPT** - Process YouTube transcripts for language learning insights
- **image-questionnaire-gpt** - Visual vocabulary learning with image associations
- **unsplash-image-search-gpt-description** - Generate Spanish descriptions for images
- **celebrity_gui** - Celebrity-based quiz for cultural and language learning

#### Command Line Tools
- **langtool** - Comprehensive CLI for language learning with GPT-4 integration

### 🌐 Web Projects
- **portfolio_site** - Full-stack portfolio website (Hugo + Node.js + SQLite)
- **fluids-visualization** - Interactive fluid dynamics visualizations

### 🏠 Lifestyle Applications
- **nutriplan** - Nutrition and fitness tracker for Alternate Day Fasting
- **mealplanner_and_pantry_manager** - AI-powered meal planning with GPT-4
- **home_inventory_manager** - Home inventory tracking system

### 📊 Data Exploration
- **movie_explorer_full** - Netflix dataset explorer with GPT analysis
- **city_map_explorer** - Interactive city map generator
- **map-description** - Map generation with AI-powered descriptions

### ⚙️ Engineering Tools
- **fluids.py** - Fluid dynamics calculations
- **flujo_en_tubería** - Pipe flow analysis tools

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Poetry (for dependency management)
- OpenAI API key (for GPT-powered tools)
- Node.js 18+ (for web projects)

### Setting Up a Project

Most Python projects use Poetry for dependency management:

```bash
cd spanish-learning/core-apps/MySpanishApp
poetry install
poetry run python main.py
```

For projects with requirements.txt:

```bash
cd project-folder
pip install -r requirements.txt
python main.py
```

### Environment Variables

Many projects require API keys. Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your-api-key-here
UNSPLASH_ACCESS_KEY=your-unsplash-key
```

## 🛠️ Workspace Management

### Reorganization Script
Run the PowerShell script to organize the workspace:

```powershell
.\reorganize_workspace.ps1
```

### Clean Build Artifacts
Remove all build artifacts and temporary files:

```bash
# Linux/Mac
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Windows PowerShell
Get-ChildItem -Path . -Include __pycache__ -Recurse -Directory | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Include *.pyc -Recurse -File | Remove-Item -Force
```

## 📝 Development Guidelines

### Python Projects
- Use Poetry for dependency management when possible
- Follow PEP 8 style guidelines
- Include requirements.txt for compatibility
- Add comprehensive docstrings

### Web Projects
- Use npm/yarn for Node.js dependencies
- Follow ESLint configurations
- Implement proper error handling
- Use environment variables for configuration

### General Best Practices
- Never commit API keys or sensitive data
- Write clear README files for each project
- Include example usage in documentation
- Add .env.example files where needed

## 🔒 Security Notes

- All `.env` files are gitignored
- API keys should never be hardcoded
- Use environment variables for all sensitive configuration
- Regular security audits recommended for web projects

## 📊 Project Statistics

- **Total Projects**: 25+
- **Primary Focus**: Spanish Language Learning (70%)
- **Languages Used**: Python, JavaScript, HTML/CSS
- **Frameworks**: PyQt5/6, Flask, Express, Hugo
- **AI Integration**: OpenAI GPT-4, Local LLMs

## 🤝 Contributing

Each project may have its own contribution guidelines. Generally:
1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

Individual projects may have their own licenses. Check each project's LICENSE file for details.

## 🔍 Finding Projects

### By Technology
- **PyQt/PySide Apps**: Search for `main.py` with Qt imports
- **Web Apps**: Look for `package.json` or `app.py`
- **CLI Tools**: Check for `__main__.py` or Poetry scripts

### By Functionality
- **Language Learning**: `spanish-learning/` directory
- **Data Analysis**: `data-exploration/` directory
- **Productivity Tools**: `lifestyle-apps/` directory

## 🚦 Project Status

Most projects are in active development or maintenance mode. Check individual project README files for specific status information.

## 📮 Contact

For questions about specific projects, refer to their individual documentation or create an issue in the project repository.

---

*Last Updated: January 2025*
*Total Disk Space: ~2GB (estimated)*
*Primary Developer: Brandon Lambert*