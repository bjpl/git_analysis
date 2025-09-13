#!/usr/bin/env python3
"""
Main entry point for the Algorithms & Data Structures Learning Platform
Uses the new unified CLI with proper state management
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.cli import UnifiedCLI


def main():
    """Main entry point"""
    try:
        # Create and run the unified CLI
        cli = UnifiedCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for learning! See you next time!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        if "--debug" in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()