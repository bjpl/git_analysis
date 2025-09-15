"""
Setup script for Anki Card Generator project.
Run this script to create the project structure and initialize the environment.
"""

import os
import subprocess
import sys
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path("C:/Users/brand/Development/Project_Workspace/anki_generator")

# Project structure
PROJECT_STRUCTURE = {
    # Core module
    "anki_generator/core": [
        "__init__.py",
        "config.py",
        "models.py",
        "registry.py",
    ],
    
    # Processors module
    "anki_generator/processors": [
        "__init__.py",
        "text_processor.py",
        "language_detector.py",
        "content_classifier.py",
    ],
    
    # Extractors module
    "anki_generator/extractors": [
        "__init__.py",
        "base_extractor.py",
        "pattern_extractor.py",
        "nlp_extractor.py",
        "custom_extractors/__init__.py",
    ],
    
    # Generators module
    "anki_generator/generators": [
        "__init__.py",
        "card_generator.py",
        "gpt_generator.py",
        "field_enhancer.py",
        "template_engine.py",
    ],
    
    # Formatters module
    "anki_generator/formatters": [
        "__init__.py",
        "csv_formatter.py",
        "template_formatter.py",
        "package_builder.py",
    ],
    
    # Utils module
    "anki_generator/utils": [
        "__init__.py",
        "text_utils.py",
        "ai_client.py",
        "file_utils.py",
        "logging_utils.py",
    ],
    
    # CLI module
    "anki_generator/cli": [
        "__init__.py",
        "app.py",
        "validators.py",
    ],
    
    # Tests
    "tests": [
        "__init__.py",
        "test_processors/__init__.py",
        "test_extractors/__init__.py",
        "test_generators/__init__.py",
        "test_formatters/__init__.py",
        "test_utils/__init__.py",
    ],
    
    # Project root
    "": [
        "pyproject.toml",
        "README.md",
        ".env",
        ".gitignore",
    ],
}

# File templates
FILE_TEMPLATES = {
    "README.md": """# Anki Card Generator

Generate Anki cards from unstructured language learning notes using GPT-4o.

## Features

- Process unstructured language learning notes in any language
- Extract vocabulary, grammar rules, expressions, and more
- Generate high-quality Anki cards with examples and context
- Export to CSV files compatible with Anki
- Customize card templates and fields

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/anki_generator.git
cd anki_generator

# Install with Poetry
poetry install
```

## Usage

```bash
# Generate cards from a notes file
anki-gen generate notes.txt

# List available templates
anki-gen templates

# Show current configuration
anki-gen config
```

## Configuration

Create a `.env` file with the following variables:

```
OPENAI_API_KEY =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
OPENAI_MODEL=gpt-4o
LOG_LEVEL=INFO
OUTPUT_DIR=./output
```

## License

MIT
""",
    
    ".env": """# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o

# Application Configuration
LOG_LEVEL=INFO
OUTPUT_DIR=./output
""",
    
    ".gitignore": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Poetry
poetry.lock

# Environment
.env
.venv
env/
venv/
ENV/

# Output
output/
*.csv
*.apkg

# IDE
.idea/
.vscode/
*.swp
*.swo
""",
    
    "pyproject.toml": """[tool.poetry]
name = "anki-generator"
version = "0.1.0"
description = "Generate Anki cards from unstructured language learning notes"
authors = ["Your Name <your.email@example.com>"]
readme = "README.md"
packages = [{include = "anki_generator"}]

[tool.poetry.dependencies]
python = "^3.10"
openai = "^1.15.0"
python-dotenv = "^1.0.1"
pandas = "^2.2.0"
typer = "^0.9.0"
rich = "^13.7.0"
pydantic = "^2.6.3"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
pytest-cov = "^4.1.0"
black = "^24.2.0"
isort = "^5.13.2"
mypy = "^1.8.0"
ruff = "^0.2.1"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.scripts]
anki-gen = "anki_generator.cli.app:app"
""",
    
    "anki_generator/__init__.py": """\"\"\"Anki Card Generator package.\"\"\"

__version__ = "0.1.0"
""",
    
    "anki_generator/core/__init__.py": """\"\"\"Core module for Anki Card Generator.\"\"\"
""",
    
    "anki_generator/processors/__init__.py": """\"\"\"Processors module for Anki Card Generator.\"\"\"
""",
    
    "anki_generator/extractors/__init__.py": """\"\"\"Extractors module for Anki Card Generator.\"\"\"
""",
    
    "anki_generator/generators/__init__.py": """\"\"\"Generators module for Anki Card Generator.\"\"\"
""",
    
    "anki_generator/formatters/__init__.py": """\"\"\"Formatters module for Anki Card Generator.\"\"\"
""",
    
    "anki_generator/utils/__init__.py": """\"\"\"Utilities module for Anki Card Generator.\"\"\"
""",
    
    "anki_generator/cli/__init__.py": """\"\"\"CLI module for Anki Card Generator.\"\"\"
""",
}


def create_project_structure():
    """Create the project directory structure."""
    print(f"Creating project structure in {PROJECT_ROOT}...")
    
    # Create directories
    for directory in PROJECT_STRUCTURE:
        dir_path = PROJECT_ROOT / directory
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    # Create files
    for directory, files in PROJECT_STRUCTURE.items():
        for file in files:
            file_path = PROJECT_ROOT / directory / file
            
            # Skip if file already exists
            if file_path.exists():
                print(f"File already exists: {file_path}")
                continue
            
            # Create parent directory if it doesn't exist
            os.makedirs(file_path.parent, exist_ok=True)
            
            # Check if we have a template for this file
            full_path = f"{directory}/{file}" if directory else file
            if full_path in FILE_TEMPLATES:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(FILE_TEMPLATES[full_path])
                print(f"Created file with template: {file_path}")
            else:
                # Create empty file
                with open(file_path, "w", encoding="utf-8") as f:
                    pass
                print(f"Created empty file: {file_path}")


def setup_poetry():
    """Set up Poetry environment."""
    print("\nSetting up Poetry environment...")
    
    # Change to project directory
    os.chdir(PROJECT_ROOT)
    
    try:
        # Check if Poetry is installed
        subprocess.run(["poetry", "--version"], check=True, capture_output=True)
        
        # Initialize Poetry
        subprocess.run(["poetry", "install"], check=True)
        print("Poetry environment set up successfully.")
        
    except subprocess.CalledProcessError:
        print("Error: Poetry is not installed or an error occurred during setup.")
        print("Please install Poetry (https://python-poetry.org/docs/#installation) and try again.")
        return False
    
    except Exception as e:
        print(f"Error setting up Poetry environment: {e}")
        return False
    
    return True


def main():
    """Main function to set up the project."""
    print("Anki Card Generator - Project Setup\n")
    
    # Create project structure
    create_project_structure()
    
    # Set up Poetry environment
    if setup_poetry():
        print("\nProject setup completed successfully!")
        print(f"\nTo get started, navigate to the project directory:")
        print(f"cd {PROJECT_ROOT}")
        print("\nActivate the Poetry environment:")
        print("poetry shell")
        print("\nRun the CLI:")
        print("anki-gen --help")
    else:
        print("\nProject files created, but Poetry setup failed.")
        print("You'll need to set up the environment manually.")


if __name__ == "__main__":
    main()