#!/usr/bin/env python3
"""
Project Cleanup and Reorganization Script
Cleans up redundant files and organizes the project structure
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Tuple

# Define the target directory structure
TARGET_STRUCTURE = {
    "src": {
        "description": "Main source code",
        "subdirs": {
            "core": "Core business logic",
            "ui": "User interface components",
            "commands": "CLI commands",
            "services": "Service layer",
            "models": "Data models",
            "persistence": "Database and storage",
            "utils": "Utility functions",
            "integrations": "External integrations"
        }
    },
    "tests": {
        "description": "Test files",
        "subdirs": {
            "unit": "Unit tests",
            "integration": "Integration tests",
            "fixtures": "Test fixtures and data"
        }
    },
    "docs": {
        "description": "Documentation",
        "subdirs": {}
    },
    "scripts": {
        "description": "Utility scripts",
        "subdirs": {}
    },
    "config": {
        "description": "Configuration files",
        "subdirs": {}
    },
    "data": {
        "description": "Data files and curricula",
        "subdirs": {
            "curriculum": "Course content",
            "progress": "User progress data"
        }
    },
    "archive": {
        "description": "Archived old files",
        "subdirs": {
            "old_cli": "Old CLI implementations",
            "test_files": "Old test files"
        }
    }
}

# Files to keep in root (main entry points only)
ROOT_KEEP = [
    "main.py",           # Main entry point
    "README.md",         # Project documentation
    "requirements.txt",  # Dependencies
    "setup.py",         # Setup script
    ".gitignore",       # Git ignore
    ".env",            # Environment variables
    "CLAUDE.md",       # Claude configuration
    "curriculum.db"    # Database
]

# Mapping of files to their new locations
FILE_MAPPINGS = {
    # Old CLI files to archive
    "curriculum_cli.py": "archive/old_cli/curriculum_cli_v1.py",
    "curriculum_cli_complete.py": "archive/old_cli/curriculum_cli_complete.py",
    "curriculum_cli_enhanced.py": "archive/old_cli/curriculum_cli_enhanced.py",
    "claude_integrated_cli.py": "archive/old_cli/claude_integrated_cli.py",
    "claude_learning_session.py": "archive/old_cli/claude_learning_session.py",
    "demo_enhanced_cli.py": "archive/old_cli/demo_enhanced_cli.py",
    "demo_simplified_cli.py": "archive/old_cli/demo_simplified_cli.py",
    "simple_cli.py": "archive/old_cli/simple_cli.py",
    
    # Test files to tests directory
    "test_*.py": "tests/",
    "fix_notes_system.py": "archive/test_files/",
    
    # Launch scripts to scripts
    "launch_beautiful.py": "scripts/launch_beautiful.py",
    "launch_menu.py": "scripts/launch_menu.py",
    "load_full_curriculum.py": "scripts/load_curriculum.py",
    
    # Keep the fixed version as the main CLI
    "curriculum_cli_fixed.py": "src/cli.py",
    
    # Other utility files
    "algo_cli.py": "archive/old_cli/algo_cli.py",
    "algo_teach.py": "archive/old_cli/algo_teach.py",
    "learn.py": "archive/old_cli/learn.py",
    "cli.py": "archive/old_cli/old_cli.py"
}

# Files to delete (duplicates, temp files, etc.)
FILES_TO_DELETE = [
    "*.pyc",
    "__pycache__",
    ".pytest_cache",
    "*.tmp",
    "*.log",
    "test_*.py",  # After moving to tests
    "demo_*.py",  # After archiving
]


class ProjectCleaner:
    """Clean and reorganize the project structure"""
    
    def __init__(self, project_root: Path):
        self.root = project_root
        self.actions_log = []
        
    def create_directory_structure(self):
        """Create the target directory structure"""
        print("🏗️ Creating directory structure...")
        
        for dir_name, dir_info in TARGET_STRUCTURE.items():
            dir_path = self.root / dir_name
            
            # Create main directory
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                self.log_action(f"Created directory: {dir_name}/")
            
            # Create subdirectories
            for subdir_name in dir_info.get("subdirs", {}).keys():
                subdir_path = dir_path / subdir_name
                if not subdir_path.exists():
                    subdir_path.mkdir(parents=True, exist_ok=True)
                    self.log_action(f"Created subdirectory: {dir_name}/{subdir_name}/")
    
    def identify_files_to_move(self) -> Dict[str, str]:
        """Identify which files need to be moved where"""
        moves = {}
        
        # Get all Python files in root
        root_files = list(self.root.glob("*.py"))
        
        for file_path in root_files:
            file_name = file_path.name
            
            # Check if file should be kept in root
            if file_name in ["main.py", "setup.py"]:
                continue
            
            # Check mappings
            for pattern, destination in FILE_MAPPINGS.items():
                if pattern.startswith("*") and file_name.endswith(pattern[1:]):
                    moves[str(file_path)] = str(self.root / destination / file_name)
                elif pattern == file_name:
                    if destination.endswith(".py"):
                        moves[str(file_path)] = str(self.root / destination)
                    else:
                        moves[str(file_path)] = str(self.root / destination / file_name)
        
        return moves
    
    def move_files(self, moves: Dict[str, str]):
        """Move files to their new locations"""
        print(f"📦 Moving {len(moves)} files...")
        
        for source, destination in moves.items():
            source_path = Path(source)
            dest_path = Path(destination)
            
            if source_path.exists():
                # Create destination directory if needed
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move the file
                try:
                    shutil.move(str(source_path), str(dest_path))
                    self.log_action(f"Moved: {source_path.name} → {dest_path.relative_to(self.root)}")
                except Exception as e:
                    self.log_action(f"ERROR moving {source_path.name}: {e}")
    
    def clean_test_files(self):
        """Move test files to tests directory"""
        print("🧪 Organizing test files...")
        
        test_files = list(self.root.glob("test_*.py"))
        tests_dir = self.root / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        for test_file in test_files:
            dest = tests_dir / test_file.name
            try:
                shutil.move(str(test_file), str(dest))
                self.log_action(f"Moved test: {test_file.name} → tests/")
            except Exception as e:
                self.log_action(f"ERROR moving test {test_file.name}: {e}")
    
    def create_main_entry_point(self):
        """Create a clean main.py entry point"""
        print("🚀 Creating main entry point...")
        
        main_content = '''#!/usr/bin/env python3
"""
Algorithm Learning System
Main entry point for the application
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Main entry point"""
    from cli import CurriculumCLI
    
    try:
        app = CurriculumCLI()
        app.run()
    except KeyboardInterrupt:
        print("\\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
        
        main_path = self.root / "main.py"
        main_path.write_text(main_content)
        self.log_action("Created main.py entry point")
    
    def create_readme(self):
        """Create or update README with new structure"""
        print("📝 Creating README...")
        
        readme_content = '''# Algorithm Learning System

A comprehensive, interactive CLI-based learning system for algorithms and data structures.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 📁 Project Structure

```
algorithms_and_data_structures/
├── main.py              # Main entry point
├── src/                 # Source code
│   ├── core/           # Core business logic
│   ├── ui/             # User interface components
│   ├── commands/       # CLI commands
│   ├── services/       # Service layer
│   ├── models/         # Data models
│   ├── persistence/    # Database and storage
│   ├── utils/          # Utility functions
│   └── integrations/   # External integrations
├── tests/              # Test files
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   └── fixtures/      # Test data
├── docs/              # Documentation
├── scripts/           # Utility scripts
├── config/            # Configuration files
├── data/              # Data and curriculum
│   ├── curriculum/    # Course content
│   └── progress/      # User progress
└── archive/           # Archived old implementations
```

## ✨ Features

- **Interactive Learning**: Step-by-step lessons with examples
- **Progress Tracking**: Save your learning progress
- **Note Taking**: Take notes while learning
- **Comprehension Checks**: Test your understanding
- **Beautiful UI**: Clean, colorful terminal interface
- **Code Examples**: Syntax-highlighted code samples

## 🎯 Learning Topics

- Big O Notation
- Arrays and Strings
- Linked Lists
- Stacks and Queues
- Trees and Graphs
- Sorting Algorithms
- Searching Algorithms
- Dynamic Programming
- System Design

## 🛠️ Development

```bash
# Run tests
python -m pytest tests/

# Run with debug mode
python main.py --debug
```

## 📚 Documentation

See the `docs/` directory for detailed documentation.

## 📄 License

MIT License - See LICENSE file for details.
'''
        
        readme_path = self.root / "README.md"
        readme_path.write_text(readme_content)
        self.log_action("Created README.md")
    
    def log_action(self, message: str):
        """Log an action taken"""
        self.actions_log.append(message)
        print(f"  ✓ {message}")
    
    def save_cleanup_report(self):
        """Save a report of all actions taken"""
        print("📊 Saving cleanup report...")
        
        report_path = self.root / "CLEANUP_REPORT.md"
        report_content = f"""# Project Cleanup Report

## Actions Taken

Total actions: {len(self.actions_log)}

### Detailed Log

"""
        for action in self.actions_log:
            report_content += f"- {action}\n"
        
        report_content += """
## New Structure

The project has been reorganized with:
- Clean directory structure
- All test files in tests/
- Old implementations archived
- Single main entry point
- Organized source code in src/

## Next Steps

1. Run `python main.py` to test the application
2. Run tests with `pytest tests/`
3. Remove archive/ directory when comfortable
"""
        
        report_path.write_text(report_content)
        print(f"  ✓ Report saved to CLEANUP_REPORT.md")
    
    def run(self):
        """Run the complete cleanup process"""
        print("\n🧹 Starting Project Cleanup\n")
        print("=" * 50)
        
        # Create directory structure
        self.create_directory_structure()
        
        # Clean test files
        self.clean_test_files()
        
        # Identify and move files
        moves = self.identify_files_to_move()
        if moves:
            self.move_files(moves)
        
        # Create main entry point
        self.create_main_entry_point()
        
        # Create README
        self.create_readme()
        
        # Save report
        self.save_cleanup_report()
        
        print("\n" + "=" * 50)
        print("✅ Cleanup Complete!")
        print(f"📊 {len(self.actions_log)} actions performed")
        print("📄 See CLEANUP_REPORT.md for details")


if __name__ == "__main__":
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Run cleanup
    cleaner = ProjectCleaner(project_root)
    cleaner.run()