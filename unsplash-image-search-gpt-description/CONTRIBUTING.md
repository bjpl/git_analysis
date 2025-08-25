# Contributing to Unsplash Image Search with GPT Description Generator

Thank you for your interest in contributing to this project! This document provides guidelines and information for contributors.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style Guide](#code-style-guide)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Issue Reporting](#issue-reporting)
- [Development Workflow](#development-workflow)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A GitHub account
- Unsplash API key (for testing)
- OpenAI API key (for testing)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/unsplash-image-search-gpt-description.git
   cd unsplash-image-search-gpt-description
   ```

2. **Set up Virtual Environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install pytest pytest-cov pytest-mock black flake8 mypy isort pre-commit
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

5. **Set up Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys for testing
   ```

6. **Run Tests**
   ```bash
   pytest tests/
   ```

## Code Style Guide

This project follows strict code formatting and quality standards.

### Python Code Style

- **Line Length**: Maximum 88 characters (Black default)
- **Formatting**: Use [Black](https://black.readthedocs.io/) for automatic code formatting
- **Import Sorting**: Use [isort](https://pycqa.github.io/isort/) for import organization
- **Linting**: Follow [flake8](https://flake8.pycqa.org/) guidelines
- **Type Hints**: Add type hints where possible (checked with [mypy](https://mypy.readthedocs.io/))

### Code Formatting Tools

All formatting is automated through pre-commit hooks:

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Check linting with flake8
flake8 .

# Run type checking with mypy
mypy .
```

### Documentation Standards

- Use clear, descriptive function and variable names
- Add docstrings to all public functions and classes
- Include type hints for function parameters and return values
- Comment complex logic and algorithms

Example:
```python
def search_images(query: str, per_page: int = 10) -> Dict[str, Any]:
    """
    Search for images using the Unsplash API.
    
    Args:
        query: Search term for images
        per_page: Number of images to return (max 30)
        
    Returns:
        Dictionary containing search results and metadata
        
    Raises:
        APIError: If the API request fails
        ValidationError: If parameters are invalid
    """
    # Implementation here
    pass
```

## Testing Guidelines

### Test Structure

Tests are located in the `tests/` directory with the following structure:

```
tests/
├── __init__.py
├── conftest.py              # pytest configuration and fixtures
├── test_main.py            # Main application tests
├── test_config_manager.py  # Configuration management tests
├── test_api_clients.py     # API client tests
├── test_ui_components.py   # UI component tests
└── integration/
    ├── __init__.py
    └── test_full_workflow.py
```

### Writing Tests

- Use descriptive test names: `test_should_return_error_when_api_key_missing()`
- Follow the Arrange-Act-Assert pattern
- Mock external API calls
- Test both success and failure scenarios
- Aim for >80% code coverage

Example test:
```python
import pytest
from unittest.mock import Mock, patch
from main import ImageSearchApp

class TestImageSearchApp:
    def test_should_initialize_with_valid_config(self, mock_config):
        """Test that app initializes properly with valid configuration."""
        # Arrange
        mock_config.get_api_keys.return_value = {
            'unsplash': 'test_key',
            'openai': 'test_key'
        }
        
        # Act
        app = ImageSearchApp()
        
        # Assert
        assert app.config_manager is not None
        assert app.UNSPLASH_ACCESS_KEY == 'test_key'
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_main.py

# Run with specific marker
pytest -m "not integration"

# Run in verbose mode
pytest -v
```

## Submitting Changes

### Pull Request Process

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-number-description
   ```

2. **Make Changes**
   - Write code following the style guide
   - Add tests for new functionality
   - Update documentation if needed

3. **Run Quality Checks**
   ```bash
   # Run all checks
   pytest
   flake8 .
   black --check .
   mypy .
   
   # Or use pre-commit to run all checks
   pre-commit run --all-files
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add feature: brief description of changes"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a pull request on GitHub.

### Commit Message Format

Use conventional commit format:

```
type(scope): brief description

Detailed explanation if needed

- List any breaking changes
- Reference related issues (#123)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Build/tooling changes

Examples:
```
feat(ui): add image pagination controls

fix(api): handle rate limit errors gracefully

docs(readme): update installation instructions
```

## Issue Reporting

### Bug Reports

When reporting bugs, include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**: OS, Python version, package versions
6. **Screenshots**: If applicable
7. **Logs**: Relevant error messages or logs

### Feature Requests

For feature requests, include:

1. **Use Case**: Why is this feature needed?
2. **Description**: Detailed description of the proposed feature
3. **Examples**: Examples of how it would work
4. **Alternatives**: Alternative solutions you've considered

## Development Workflow

### Branch Strategy

- `main`: Production-ready code
- `develop`: Development branch (if used)
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Critical fixes for production

### Code Review Process

1. All changes require a pull request
2. At least one code review is required
3. All CI checks must pass
4. No merge conflicts allowed
5. Squash commits when merging

### Release Process

Releases are automated through GitHub Actions:

1. Create a version tag: `git tag v1.0.0`
2. Push tag: `git push origin v1.0.0`
3. GitHub Actions will build and release automatically

## Development Tools

### Recommended IDE Setup

**Visual Studio Code** with extensions:
- Python
- Black Formatter
- Pylance
- Python Docstring Generator
- GitLens

**PyCharm** configuration:
- Enable Black as external tool
- Configure flake8 as code inspector
- Set up pytest as test runner

### Debugging

For GUI debugging:
```python
# Add debug prints
print(f"Debug: {variable_name}")

# Use Python debugger
import pdb; pdb.set_trace()

# For pytest debugging
pytest --pdb
```

## Getting Help

- **Documentation**: Check existing docs and inline comments
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: Ask specific questions in PR comments

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions
- README acknowledgments

Thank you for contributing to make this project better!