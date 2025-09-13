#!/usr/bin/env python3
"""
Simple wrapper to launch the learning platform
Usage: python learn.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Launch the learning platform"""
    # Import and initialize colorama FIRST before any other imports
    import colorama
    colorama.init(autoreset=False, convert=True, strip=False)
    
    # Set environment variable to force color
    os.environ['FORCE_COLOR'] = '1'
    os.environ['COLORAMA_FORCE_COLOR'] = '1'
    
    # Now import the CLI
    from src.enhanced_cli import EnhancedCLI
    
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("🎓 Algorithms & Data Structures Learning Platform")
    print("Your Journey to Mastery Begins Here!")
    print("=" * 60)
    print()
    
    try:
        # Create and run CLI
        cli = EnhancedCLI()
        cli.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 Thank you for learning! See you next time!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("2. Try running: python algo_cli.py")
        print("3. Check that data files exist in the data/ directory")
        sys.exit(1)

if __name__ == '__main__':
    main()