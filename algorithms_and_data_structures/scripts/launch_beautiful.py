#!/usr/bin/env python3
"""
Launch the Beautiful CLI Application
Combines the best of Version 1 (Elegant Academic) and Version 5 (Professional Documentation)
Optimized for Windows PowerShell
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Launch the beautiful CLI"""
    # Enable Windows color support
    if sys.platform == 'win32':
        try:
            import colorama
            colorama.init(autoreset=False, convert=True, strip=False)
            print("✓ Windows color support enabled")
        except ImportError:
            print("! Install colorama for better Windows support: pip install colorama")
    
    try:
        # Import and run the beautiful CLI
        from src.ui.beautiful_cli import BeautifulCLI
        
        print("\n🎨 Launching Beautiful CLI Experience...")
        print("Optimized for Windows PowerShell\n")
        
        # Create and run the CLI
        cli = BeautifulCLI()
        
        # Show main demonstration
        cli.demo_all_features()
        
        # Interactive mode
        from src.ui.beautiful_cli import Color
        
        while True:
            print("\n" + cli.colorize("Options:", Color.BRIGHT_CYAN))
            print("1. View Arrays Lesson")
            print("2. View Sorting Algorithms")
            print("3. View Data Structures")
            print("4. Run Progress Animation")
            print("5. Show Professional Documentation")
            print("Q. Quit")
            
            choice = input("\n" + cli.colorize("Enter choice: ", Color.BRIGHT_GREEN)).strip().upper()
            
            if choice == "Q":
                print(cli.colorize("\n👋 Thank you for using Beautiful CLI!", Color.BRIGHT_MAGENTA))
                break
            elif choice == "1":
                cli.create_header_v1_style("Arrays Deep Dive", "Master the fundamentals")
                cli.create_learning_journey_box([
                    ("", "Basics", "Understanding array indexing"),
                    ("", "Advanced", "Dynamic arrays and resizing"),
                    ("", "Expert", "Cache-friendly algorithms")
                ])
            elif choice == "2":
                cli.create_header_v1_style("Sorting Algorithms", "From O(n²) to O(n log n)")
                performance_data = [
                    ("Bubble Sort", "O(n²)", "O(n²)"),
                    ("Quick Sort", "O(n log n)", "O(n²)"),
                    ("Merge Sort", "O(n log n)", "O(n log n)"),
                    ("Heap Sort", "O(n log n)", "O(n log n)")
                ]
                cli.create_performance_table(performance_data)
            elif choice == "3":
                sections = {
                    "Linear Structures": ["Arrays", "Linked Lists", "Stacks", "Queues"],
                    "Tree Structures": ["Binary Trees", "BST", "AVL Trees", "B-Trees"],
                    "Graph Structures": ["Directed Graphs", "Undirected Graphs", "Weighted Graphs"],
                    "Hash Structures": ["Hash Tables", "Hash Maps", "Hash Sets"]
                }
                cli.create_professional_section_v5("DATA STRUCTURES OVERVIEW", sections)
            elif choice == "4":
                cli.animated_progress_bar(30, "Learning Progress")
            elif choice == "5":
                cli.create_definition_box("Algorithm", 
                    "A step-by-step procedure for solving a problem or accomplishing a task")
                cli.create_key_insight_box(
                    "Algorithms are recipes for computers",
                    "Each step must be precise and unambiguous"
                )
        
    except KeyboardInterrupt:
        print("\n\n👋 Session interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please ensure all dependencies are installed.")
        sys.exit(1)

if __name__ == "__main__":
    main()