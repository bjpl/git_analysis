# My Spanish App

A PyQt6-based desktop application for tracking Spanish learning sessions with vocabulary and grammar notes.

## Setup

1. **Install Python 3.10+**

2. **Install Poetry** (if not installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies**:
   ```bash
   poetry install
   ```

4. **Run the application**:
   ```bash
   poetry run python main.py
   ```

## Testing

Run tests with:
```bash
poetry run pytest tests/
```

## Features

- **Plan**: Schedule Spanish tutoring sessions
- **Track**: Record vocabulary and grammar during sessions
- **Review**: View past sessions and learning progress
- **Database**: SQLite storage with session, vocabulary, and grammar tracking

## Project Structure

```
MySpanishApp/
├── main.py              # Application entry point
├── config.py            # Configuration settings
├── models/              # Database models
├── views/               # PyQt6 UI components
├── utils/               # Logging utilities
└── tests/               # Test suite
```