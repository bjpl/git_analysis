#!/usr/bin/env python3
"""
Interactive Quickstart Wizard
Algorithms & Data Structures CLI - Version 1.0.0

This script provides an interactive setup and configuration wizard for new users.
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil
import textwrap


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class QuickstartWizard:
    """Interactive quickstart wizard for CLI setup and first project."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.project_root = Path.cwd()
        self.home_dir = Path.home()
        
        # Configuration paths
        if self.system == "windows":
            self.config_dir = Path(os.environ.get("APPDATA", self.home_dir)) / "algorithms-cli"
        else:
            self.config_dir = self.home_dir / ".config" / "algorithms-cli"
        
        self.user_preferences = {}
        self.project_config = {}

    def print_header(self) -> None:
        """Print wizard header."""
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}🚀 Algorithms & Data Structures CLI - Quickstart Wizard{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        print()
        print(f"{Colors.BLUE}Welcome! This wizard will help you get started with the CLI.{Colors.END}")
        print(f"{Colors.BLUE}We'll configure your environment and create your first project.{Colors.END}")
        print()

    def log_success(self, message: str) -> None:
        """Print success message."""
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")

    def log_error(self, message: str) -> None:
        """Print error message."""
        print(f"{Colors.RED}❌ {message}{Colors.END}")

    def log_warning(self, message: str) -> None:
        """Print warning message."""
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

    def log_info(self, message: str) -> None:
        """Print info message."""
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

    def ask_question(self, question: str, default: Optional[str] = None, 
                    options: Optional[List[str]] = None) -> str:
        """Ask user a question with optional default and validation."""
        if options:
            print(f"\n{Colors.YELLOW}{question}{Colors.END}")
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            
            while True:
                try:
                    choice_str = input(f"Enter choice (1-{len(options)}): ").strip()
                    if not choice_str and default:
                        return default
                    
                    choice = int(choice_str)
                    if 1 <= choice <= len(options):
                        return options[choice - 1]
                    else:
                        print(f"{Colors.RED}Please enter a number between 1 and {len(options)}{Colors.END}")
                except (ValueError, KeyboardInterrupt):
                    if default:
                        return default
                    print(f"{Colors.RED}Invalid input. Please try again.{Colors.END}")
        else:
            prompt = f"\n{Colors.YELLOW}{question}{Colors.END}"
            if default:
                prompt += f" (default: {default})"
            prompt += ": "
            
            try:
                answer = input(prompt).strip()
                return answer if answer else (default or "")
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Wizard cancelled by user{Colors.END}")
                sys.exit(0)

    def ask_yes_no(self, question: str, default: bool = True) -> bool:
        """Ask a yes/no question."""
        default_str = "Y/n" if default else "y/N"
        answer = self.ask_question(f"{question} ({default_str})")
        
        if not answer:
            return default
        
        return answer.lower() in ['y', 'yes', 'true', '1']

    def check_installation(self) -> Dict[str, Any]:
        """Check CLI installation status."""
        self.log_info("Checking CLI installation...")
        
        status = {
            "installed": False,
            "config_exists": False,
            "claude_flow": False,
            "python_env": False
        }
        
        # Check config file
        config_file = self.config_dir / "config.json"
        if config_file.exists():
            status["config_exists"] = True
            try:
                with open(config_file) as f:
                    config = json.load(f)
                    status["claude_flow"] = config.get("features", {}).get("claude_flow", False)
                    status["python_env"] = Path(config.get("venv_path", "")).exists()
                    status["installed"] = True
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return status

    def run_installation(self) -> None:
        """Run installation process."""
        self.log_info("Starting installation process...")
        
        # Determine installation script
        if self.system == "windows":
            install_script = self.project_root / "install.ps1"
            if install_script.exists():
                cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(install_script)]
            else:
                self.log_error("install.ps1 not found. Please run installation manually.")
                return
        else:
            install_script = self.project_root / "install.sh"
            if install_script.exists():
                cmd = ["bash", str(install_script)]
            else:
                self.log_error("install.sh not found. Please run installation manually.")
                return
        
        # Ask for development mode
        dev_mode = self.ask_yes_no("Install development tools and dependencies?", default=False)
        if dev_mode:
            cmd.append("--dev")
        
        try:
            subprocess.run(cmd, check=True)
            self.log_success("Installation completed!")
        except subprocess.CalledProcessError:
            self.log_error("Installation failed. Please check the error messages above.")
            sys.exit(1)

    def configure_user_preferences(self) -> None:
        """Configure user preferences."""
        print(f"\n{Colors.PURPLE}{Colors.BOLD}🎯 User Preferences Configuration{Colors.END}")
        
        # Programming experience
        experience_levels = ["Beginner", "Intermediate", "Advanced", "Expert"]
        experience = self.ask_question(
            "What's your programming experience level?",
            options=experience_levels
        )
        
        # Preferred languages
        languages = ["Python", "JavaScript", "Java", "C++", "Go", "Rust", "TypeScript"]
        print(f"\n{Colors.YELLOW}Which programming languages do you work with? (comma-separated){Colors.END}")
        for i, lang in enumerate(languages, 1):
            print(f"  {i}. {lang}")
        
        lang_input = input("Enter numbers or language names (e.g., 1,3,Python): ").strip()
        preferred_languages = self.parse_language_selection(lang_input, languages)
        
        # Learning goals
        goals = [
            "Prepare for coding interviews",
            "Improve algorithm knowledge", 
            "Learn data structures",
            "Solve competitive programming",
            "Build real-world applications",
            "Academic study/research"
        ]
        
        learning_goals = self.ask_question(
            "What are your primary learning goals?",
            options=goals
        )
        
        # Difficulty preference
        difficulty_levels = ["Easy first", "Mixed difficulty", "Challenge me", "Adaptive"]
        difficulty = self.ask_question(
            "Preferred problem difficulty progression?",
            options=difficulty_levels
        )
        
        # Testing preferences
        test_style = self.ask_question(
            "Preferred testing approach?",
            options=["TDD (Test-Driven Development)", "Test after coding", "Minimal testing", "Comprehensive testing"]
        )
        
        self.user_preferences = {
            "experience_level": experience.lower(),
            "preferred_languages": preferred_languages,
            "learning_goals": learning_goals,
            "difficulty_preference": difficulty.lower().replace(" ", "_"),
            "test_style": test_style.lower().replace(" ", "_").replace("-", "_"),
            "setup_date": subprocess.check_output([
                sys.executable, "-c", 
                "import datetime; print(datetime.datetime.now().isoformat())"
            ], text=True).strip()
        }
        
        self.log_success("User preferences configured!")

    def parse_language_selection(self, input_str: str, available_languages: List[str]) -> List[str]:
        """Parse user language selection input."""
        if not input_str:
            return ["Python"]  # Default
        
        selections = []
        parts = [part.strip() for part in input_str.split(",")]
        
        for part in parts:
            # Try as number
            try:
                num = int(part)
                if 1 <= num <= len(available_languages):
                    selections.append(available_languages[num - 1])
            except ValueError:
                # Try as language name
                for lang in available_languages:
                    if lang.lower() == part.lower():
                        selections.append(lang)
                        break
        
        return selections if selections else ["Python"]

    def create_first_project(self) -> None:
        """Guide user through creating their first project."""
        print(f"\n{Colors.PURPLE}{Colors.BOLD}📁 First Project Creation{Colors.END}")
        
        # Ask if they want to create a project
        create_project = self.ask_yes_no("Would you like to create your first algorithms project?")
        
        if not create_project:
            self.log_info("Skipping project creation. You can create one later with: algorithms-cli init")
            return
        
        # Project name
        default_name = "my-algorithms"
        project_name = self.ask_question("Project name", default=default_name)
        if not project_name:
            project_name = default_name
        
        # Project type
        project_types = [
            "General algorithms & data structures",
            "Interview preparation focused",
            "Competitive programming",
            "Research/academic project",
            "Learning playground"
        ]
        
        project_type = self.ask_question("Project type", options=project_types)
        
        # Initial algorithms to include
        algorithms = [
            "Sorting algorithms (bubble, quick, merge)",
            "Search algorithms (binary, linear)",
            "Graph algorithms (BFS, DFS, Dijkstra)",
            "Tree operations (traversal, balancing)",
            "Dynamic programming examples",
            "Hash table implementations"
        ]
        
        print(f"\n{Colors.YELLOW}Which algorithm categories would you like to start with?{Colors.END}")
        print("(You can select multiple by entering numbers separated by commas)")
        for i, alg in enumerate(algorithms, 1):
            print(f"  {i}. {alg}")
        
        alg_input = input("Enter numbers (e.g., 1,2,3): ").strip()
        selected_algorithms = self.parse_algorithm_selection(alg_input, algorithms)
        
        # Create project
        self.create_project_structure(project_name, project_type, selected_algorithms)

    def parse_algorithm_selection(self, input_str: str, available_algorithms: List[str]) -> List[str]:
        """Parse algorithm selection input."""
        if not input_str:
            return [available_algorithms[0]]  # Default to first one
        
        selections = []
        parts = [part.strip() for part in input_str.split(",")]
        
        for part in parts:
            try:
                num = int(part)
                if 1 <= num <= len(available_algorithms):
                    selections.append(available_algorithms[num - 1])
            except ValueError:
                continue
        
        return selections if selections else [available_algorithms[0]]

    def create_project_structure(self, name: str, project_type: str, algorithms: List[str]) -> None:
        """Create the actual project structure."""
        self.log_info(f"Creating project: {name}")
        
        project_dir = Path(name)
        if project_dir.exists():
            if not self.ask_yes_no(f"Directory '{name}' already exists. Continue?"):
                return
        
        # Create directory structure
        directories = [
            project_dir / "src" / "algorithms",
            project_dir / "src" / "data_structures", 
            project_dir / "tests",
            project_dir / "examples",
            project_dir / "docs",
            project_dir / "benchmarks"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create project configuration
        project_config = {
            "name": name,
            "type": project_type,
            "created_date": subprocess.check_output([
                sys.executable, "-c", 
                "import datetime; print(datetime.datetime.now().isoformat())"
            ], text=True).strip(),
            "algorithms": algorithms,
            "structure": {
                "src": "Source code",
                "tests": "Unit tests", 
                "examples": "Example usage",
                "docs": "Documentation",
                "benchmarks": "Performance tests"
            },
            "preferences": self.user_preferences
        }
        
        config_file = project_dir / "project.json"
        with open(config_file, 'w') as f:
            json.dump(project_config, f, indent=2)
        
        # Create README
        readme_content = self.generate_readme(name, project_type, algorithms)
        readme_file = project_dir / "README.md"
        readme_file.write_text(readme_content)
        
        # Create example files based on selected algorithms
        self.create_example_files(project_dir, algorithms)
        
        # Create basic test structure
        self.create_test_structure(project_dir)
        
        self.log_success(f"Project '{name}' created successfully!")
        self.log_info(f"Next steps:")
        print(f"  1. cd {name}")
        print(f"  2. algorithms-cli run sort")
        print(f"  3. algorithms-cli test")

    def generate_readme(self, name: str, project_type: str, algorithms: List[str]) -> str:
        """Generate README content for the project."""
        return f"""# {name}

## Project Overview

**Type:** {project_type}

This project was created using the Algorithms & Data Structures CLI quickstart wizard.

## Included Algorithm Categories

{chr(10).join(f"- {alg}" for alg in algorithms)}

## Project Structure

```
{name}/
├── src/
│   ├── algorithms/          # Algorithm implementations
│   └── data_structures/     # Data structure implementations
├── tests/                   # Unit tests
├── examples/               # Usage examples
├── docs/                   # Documentation
├── benchmarks/             # Performance tests
└── project.json           # Project configuration
```

## Getting Started

### Running Algorithms

```bash
# Run a specific algorithm
algorithms-cli run <algorithm-name>

# Run tests
algorithms-cli test

# Benchmark performance  
algorithms-cli benchmark <algorithm-name>

# Visualize algorithm
algorithms-cli visualize <algorithm-name>
```

### SPARC Workflow (if Claude Flow is installed)

```bash
# Test-driven development
algorithms-cli sparc tdd "implement binary search tree"

# Full pipeline
npx claude-flow sparc pipeline "optimize sorting algorithm"
```

## Available Commands

- `algorithms-cli help` - Show all available commands
- `algorithms-cli run` - Execute algorithms
- `algorithms-cli test` - Run test suite
- `algorithms-cli benchmark` - Performance testing
- `algorithms-cli analyze` - Code analysis
- `algorithms-cli visualize` - Algorithm visualization

## Contributing

1. Write tests first (TDD approach recommended)
2. Follow the existing code structure
3. Add documentation for new algorithms
4. Run benchmarks to verify performance

## Resources

- [CLI Documentation](https://github.com/brandonjplambert/algorithms_and_data_structures)
- [Algorithm Analysis Guide](docs/analysis.md)
- [Testing Best Practices](docs/testing.md)

---

*Generated by Algorithms CLI v1.0.0 Quickstart Wizard*
"""

    def create_example_files(self, project_dir: Path, algorithms: List[str]) -> None:
        """Create example algorithm files."""
        src_dir = project_dir / "src" / "algorithms"
        
        # Sorting algorithms
        if any("sorting" in alg.lower() for alg in algorithms):
            sorting_file = src_dir / "sorting.py"
            sorting_content = '''"""
Sorting Algorithm Implementations
"""

def bubble_sort(arr):
    """Bubble sort implementation with O(n²) time complexity."""
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def quick_sort(arr):
    """Quick sort implementation with O(n log n) average time complexity."""
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)


def merge_sort(arr):
    """Merge sort implementation with O(n log n) time complexity."""
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)


def merge(left, right):
    """Helper function for merge sort."""
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    
    return result
'''
            sorting_file.write_text(sorting_content)
        
        # Search algorithms
        if any("search" in alg.lower() for alg in algorithms):
            search_file = src_dir / "search.py"
            search_content = '''"""
Search Algorithm Implementations
"""

def binary_search(arr, target):
    """Binary search implementation with O(log n) time complexity."""
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1


def linear_search(arr, target):
    """Linear search implementation with O(n) time complexity."""
    for i, value in enumerate(arr):
        if value == target:
            return i
    return -1
'''
            search_file.write_text(search_content)

    def create_test_structure(self, project_dir: Path) -> None:
        """Create basic test structure."""
        test_dir = project_dir / "tests"
        
        # Test configuration
        test_init = test_dir / "__init__.py"
        test_init.write_text("")
        
        # Example test file
        test_sorting = test_dir / "test_sorting.py"
        test_content = '''"""
Tests for sorting algorithms
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from algorithms.sorting import bubble_sort, quick_sort, merge_sort


class TestSorting:
    """Test cases for sorting algorithms."""
    
    def test_bubble_sort(self):
        """Test bubble sort with various inputs."""
        assert bubble_sort([64, 34, 25, 12, 22, 11, 90]) == [11, 12, 22, 25, 34, 64, 90]
        assert bubble_sort([]) == []
        assert bubble_sort([1]) == [1]
        assert bubble_sort([3, 1, 2]) == [1, 2, 3]
    
    def test_quick_sort(self):
        """Test quick sort with various inputs."""
        assert quick_sort([64, 34, 25, 12, 22, 11, 90]) == [11, 12, 22, 25, 34, 64, 90]
        assert quick_sort([]) == []
        assert quick_sort([1]) == [1]
        assert quick_sort([3, 1, 2]) == [1, 2, 3]
    
    def test_merge_sort(self):
        """Test merge sort with various inputs."""
        assert merge_sort([64, 34, 25, 12, 22, 11, 90]) == [11, 12, 22, 25, 34, 64, 90]
        assert merge_sort([]) == []
        assert merge_sort([1]) == [1]
        assert merge_sort([3, 1, 2]) == [1, 2, 3]
'''
        test_sorting.write_text(test_content)

    def show_next_steps(self, installation_status: Dict[str, Any]) -> None:
        """Show user next steps based on their setup."""
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Quickstart Complete!{Colors.END}")
        
        print(f"\n{Colors.BLUE}What you can do now:{Colors.END}")
        
        if installation_status["claude_flow"]:
            print("🤖 SPARC Workflow (Recommended):")
            print("   algorithms-cli sparc tdd 'implement heap sort'")
            print("   npx claude-flow sparc pipeline 'optimize binary search'")
            print()
        
        print("🔧 Basic Commands:")
        print("   algorithms-cli run sort")
        print("   algorithms-cli test")
        print("   algorithms-cli benchmark quick_sort")
        print("   algorithms-cli visualize merge_sort")
        print()
        
        print("📚 Learning Resources:")
        print("   algorithms-cli help")
        print("   algorithms-cli analyze complexity")
        print("   algorithms-cli examples")
        print()
        
        if self.user_preferences.get("experience_level") == "beginner":
            print("🎓 Beginner Tips:")
            print("   • Start with sorting algorithms")
            print("   • Use the visualize command to understand algorithms")
            print("   • Run tests frequently to verify your implementations")
            print("   • Check out the examples directory for guidance")
            print()
        
        print("📖 Documentation & Support:")
        print("   • CLI Help: algorithms-cli help")
        print("   • Project Examples: algorithms-cli examples")
        print("   • GitHub Issues: Report bugs and request features")

    def save_user_config(self) -> None:
        """Save user configuration to config directory."""
        if not self.user_preferences:
            return
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        user_config_file = self.config_dir / "user_preferences.json"
        
        try:
            with open(user_config_file, 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
            self.log_success("User preferences saved!")
        except Exception as e:
            self.log_warning(f"Could not save user preferences: {e}")

    def run_wizard(self) -> None:
        """Run the complete quickstart wizard."""
        try:
            self.print_header()
            
            # Check installation
            installation_status = self.check_installation()
            
            if not installation_status["installed"]:
                install_now = self.ask_yes_no("CLI is not installed. Would you like to install it now?")
                if install_now:
                    self.run_installation()
                    installation_status = self.check_installation()
                else:
                    self.log_warning("Please run the installation first, then return to this wizard.")
                    return
            
            # Configure user preferences
            self.configure_user_preferences()
            self.save_user_config()
            
            # Create first project
            self.create_first_project()
            
            # Store wizard completion in memory
            try:
                subprocess.run([
                    "npx", "claude-flow@alpha", "hooks", "post-edit",
                    "--file", "quickstart.py", 
                    "--memory-key", "swarm/installer/quickstart-complete"
                ], check=False, capture_output=True)
            except:
                pass  # Ignore if Claude Flow not available
            
            # Show next steps
            self.show_next_steps(installation_status)
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Quickstart wizard cancelled. You can restart it anytime with:{Colors.END}")
            print("python scripts/quickstart.py")
        except Exception as e:
            self.log_error(f"Wizard failed: {e}")
            sys.exit(1)


def main():
    """Main entry point."""
    wizard = QuickstartWizard()
    wizard.run_wizard()


if __name__ == "__main__":
    main()