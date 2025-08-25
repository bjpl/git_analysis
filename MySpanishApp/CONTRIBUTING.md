# Contributing to MySpanishApp

Thank you for your interest in contributing to MySpanishApp! This document provides guidelines and instructions for contributing to the project.

## 🤝 Code of Conduct

By participating in this project, you agree to:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Accept feedback gracefully

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/MySpanishApp.git
   cd MySpanishApp
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/MySpanishApp.git
   ```
4. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 💻 Development Setup

1. **Install Poetry** (recommended):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   ```

3. **Run the application**:
   ```bash
   poetry run python main.py
   ```

4. **Run tests**:
   ```bash
   poetry run pytest tests/
   ```

## 📝 Making Changes

### Before You Start

- Check existing [issues](https://github.com/OWNER/MySpanishApp/issues) to avoid duplicates
- For major changes, open an issue first to discuss your ideas
- Make sure your fork is up-to-date with the main branch

### Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use meaningful variable and function names
- Add type hints where appropriate
- Maximum line length: 100 characters
- Use docstrings for all public functions and classes

Example:
```python
def add_vocabulary_item(word: str, translation: str, session_id: int) -> bool:
    """
    Add a new vocabulary item to the database.
    
    Args:
        word: The Spanish word or phrase
        translation: The English translation
        session_id: The ID of the associated session
        
    Returns:
        True if successful, False otherwise
    """
    # Implementation here
```

### Commit Messages

Use clear and descriptive commit messages:
- Start with a verb in present tense (e.g., "Add", "Fix", "Update")
- Keep the first line under 50 characters
- Add detailed description if needed after a blank line

Examples:
```
Add export functionality for vocabulary data

- Implement CSV export for vocab items
- Add JSON export option
- Include filtering by date range
```

### Testing

- Write tests for new features
- Ensure all tests pass before submitting
- Aim for at least 80% code coverage for new code
- Use pytest for testing:

```python
# tests/test_vocab.py
def test_add_vocabulary():
    """Test adding vocabulary items."""
    vocab = VocabModel(db)
    result = vocab.add_item("hola", "hello", session_id=1)
    assert result is True
```

## 🔄 Submitting Changes

1. **Push your changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub:
   - Use a clear title describing the change
   - Reference any related issues (e.g., "Fixes #123")
   - Describe what changes were made and why
   - Include screenshots for UI changes

3. **Pull Request Checklist**:
   - [ ] Code follows project style guidelines
   - [ ] Tests pass locally
   - [ ] New features have tests
   - [ ] Documentation is updated if needed
   - [ ] Commit messages are clear

## 🐛 Reporting Issues

### Bug Reports

Include:
- Python version
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages/logs
- Screenshots if applicable

### Feature Requests

Include:
- Clear description of the feature
- Use case/motivation
- Possible implementation approach
- Mockups/examples if applicable

## 📚 Areas for Contribution

### Good First Issues

Look for issues labeled `good first issue`:
- Documentation improvements
- Simple bug fixes
- Test coverage improvements
- UI text corrections

### Priority Areas

- **Testing**: Increase test coverage
- **Documentation**: Improve user guides and API docs
- **UI/UX**: Enhance user interface and experience
- **Performance**: Optimize database queries and UI responsiveness
- **Features**: Implement roadmap items from README

### Non-Code Contributions

- Report bugs
- Suggest features
- Improve documentation
- Answer questions in issues
- Review pull requests
- Create tutorials or blog posts

## 🏗️ Project Structure

```
MySpanishApp/
├── models/       # Database models (business logic)
├── views/        # UI components (PyQt6)
├── utils/        # Utility functions
├── tests/        # Test files
├── config.py     # Configuration
└── main.py       # Entry point
```

### Key Files

- `models/database.py` - Database connection and schema
- `views/main_window.py` - Main application window
- `views/plan_view.py` - Session planning interface
- `views/track_view.py` - Learning tracking interface

## 📋 Review Process

1. Maintainers will review your PR
2. Address any feedback or requested changes
3. Once approved, your PR will be merged
4. Your contribution will be acknowledged!

## ❓ Getting Help

- Open an issue for questions
- Check existing documentation
- Review similar PRs for examples
- Ask in PR comments if unclear about feedback

## 🎉 Recognition

Contributors will be:
- Listed in the project's contributors section
- Mentioned in release notes for significant contributions
- Given credit in commit messages

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to MySpanishApp! 🇪🇸 ¡Gracias!