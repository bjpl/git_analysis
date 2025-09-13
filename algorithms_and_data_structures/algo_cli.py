#!/usr/bin/env python3
"""
Algorithms & Data Structures Learning Platform
Fixed CLI with proper command handling and formatting
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main entry point that launches the enhanced CLI directly"""
    # Force colorama initialization for Windows
    try:
        import colorama
        colorama.init(autoreset=False, convert=True, strip=False)
    except ImportError:
        pass
    
    # Import after colorama init
    from src.enhanced_cli import EnhancedCLI
    
    # Clear screen first
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Simple startup message
    print("🎓 Algorithms & Data Structures Learning Platform")
    print("=" * 50)
    print()
    
    try:
        # Initialize CLI with default settings
        cli = EnhancedCLI()
        
        # Run the CLI directly
        cli.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! See you next time!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

if __name__ == '__main__':
    main()