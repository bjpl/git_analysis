#!/usr/bin/env python3
"""
Quick launcher for the interactive menu system
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Force color output on Windows
os.environ["FORCE_COLOR"] = "1"
os.environ["COLORTERM"] = "truecolor"


def main():
    """Launch the interactive menu system directly"""
    try:
        from src.main_menu import MainMenuSystem
        
        # Create and run the menu system
        menu_system = MainMenuSystem()
        
        # Show welcome message
        print(menu_system.formatter.header("🎓 Welcome to Algorithm Learning Platform!", level=1))
        print(menu_system.formatter.info("Master algorithms and data structures with interactive learning"))
        print(menu_system.formatter.success("Now with arrow key navigation! Use ↑↓ or number keys."))
        input("\nPress Enter to start...")
        
        # Run the menu system
        asyncio.run(menu_system.run())
        
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for learning! See you next time!")
        sys.exit(0)
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nMake sure all dependencies are installed:")
        print("  pip install colorama")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()