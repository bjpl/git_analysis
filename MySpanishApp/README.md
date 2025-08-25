# MySpanishApp 🇪🇸

A comprehensive desktop application for tracking and managing Spanish language learning through tutoring sessions. Built with PyQt6 and SQLite for a seamless learning experience.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.8.1-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## 📋 Features

- **📅 Plan Sessions**: Schedule and manage Spanish tutoring sessions with an intuitive calendar interface
- **📝 Track Learning**: Record vocabulary, grammar patterns, challenges, and comfort areas during sessions
- **📊 Review Progress**: Analyze learning patterns and track progress over time
- **💾 Local Database**: All data stored locally using SQLite for privacy and offline access
- **🎨 Modern UI**: Clean, responsive interface built with PyQt6
- **⌨️ Keyboard Shortcuts**: Quick navigation with Ctrl+1/2/3/4 and other shortcuts

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Git (for cloning the repository)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/MySpanishApp.git
cd MySpanishApp
```

2. **Install dependencies**

Using Poetry (recommended):
```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install
```

Using pip:
```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. **Run the application**

Using Poetry:
```bash
poetry run python main.py
```

Using pip:
```bash
python main.py
```

## 📖 Usage Guide

### Planning Sessions
1. Navigate to the **Plan** tab (Ctrl+1)
2. Click on a date in the calendar
3. Click "Add Session" to schedule a new tutoring session
4. Right-click existing sessions to change their status

### Tracking Learning
1. Navigate to the **Track** tab (Ctrl+2)
2. Select the active session from the dropdown
3. Use tabs to record:
   - **Vocabulary**: New words and phrases with translations
   - **Grammar**: Grammar patterns and explanations
   - **Challenges**: Areas of difficulty
   - **Comfort**: Topics you're confident with

### Reviewing Progress
1. Navigate to the **Review** tab (Ctrl+3)
2. View statistics including total sessions and vocabulary count
3. Filter sessions by status (All/Completed/Planned)
4. See recent vocabulary additions

### Keyboard Shortcuts
- `Ctrl+1` - Plan view
- `Ctrl+2` - Track view
- `Ctrl+3` - Review view
- `Ctrl+4` - Settings view
- `Ctrl+Q` - Quit application
- `F1` - Show help

## 🗂️ Project Structure

```
MySpanishApp/
├── main.py              # Application entry point
├── config.py            # Configuration settings
├── models/              # Database models
│   ├── database.py      # SQLite connection manager
│   ├── session_model.py # Session CRUD operations
│   ├── vocab_model.py   # Vocabulary management
│   └── grammar_model.py # Grammar tracking
├── views/               # PyQt6 UI components
│   ├── main_window.py   # Main application window
│   ├── plan_view.py     # Session planning interface
│   ├── track_view.py    # Learning tracking interface
│   ├── review_view.py   # Progress review interface
│   └── track_tabs/      # Sub-components for tracking
├── utils/               # Utility modules
│   ├── logger.py        # Logging configuration
│   └── export.py        # Data export functionality
└── tests/               # Test suite
```

## 🔧 Configuration

The application can be configured through `config.py`:

- **Database location**: Default is `my_spanish_app.db` in the project root
- **Window size**: Default is 1200x800 pixels
- **Log level**: Default is DEBUG for development
- **Log file**: Located in `logs/app.log`

## 🧪 Testing

Run the test suite:

```bash
# Using Poetry
poetry run pytest tests/

# Using pip
pytest tests/
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Run tests to ensure everything works
5. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

## 📝 Database Schema

The application uses SQLite with the following main tables:
- `sessions` - Tutoring session records
- `vocab` - Vocabulary entries
- `grammar` - Grammar patterns and rules
- `challenges` - Learning challenges
- `comfort` - Areas of confidence
- `teachers` - Teacher information

See [SPECIFICATIONS.md](SPECIFICATIONS.md) for complete schema details.

## 🚦 Roadmap

- [ ] Cloud sync for backup
- [ ] Export to Anki/Quizlet formats
- [ ] Spaced repetition system
- [ ] Audio recording for pronunciation
- [ ] Mobile companion app
- [ ] Dark mode theme
- [ ] Multi-language support

## 🐛 Troubleshooting

### Common Issues

**Application won't start:**
- Ensure Python 3.10+ is installed: `python --version`
- Verify all dependencies are installed
- Check `logs/app.log` for error messages

**Database errors:**
- Ensure write permissions in the application directory
- Delete `my_spanish_app.db` to reset the database (warning: loses all data)

**UI issues:**
- Update PyQt6: `pip install --upgrade PyQt6`
- Check display scaling settings on high-DPI monitors

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- Database powered by [SQLite](https://www.sqlite.org/)
- Package management with [Poetry](https://python-poetry.org/)

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

Made with ❤️ for Spanish language learners