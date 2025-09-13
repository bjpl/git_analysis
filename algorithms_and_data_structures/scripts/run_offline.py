#!/usr/bin/env python3
"""
Simple offline launcher for the Algorithms & Data Structures CLI
Bypasses all cloud features and runs in pure local mode
"""

import sys
import os
from pathlib import Path

# Add parent to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_offline_cli():
    """Run the CLI in pure offline mode"""
    print("🎓 Algorithms & Data Structures Learning Platform")
    print("=" * 60)
    print("📚 Welcome to your personal algorithms tutor!")
    print("Running in local mode - all features work offline\n")
    
    # Import after path setup
    from src.enhanced_cli import EnhancedCLI
    
    # Create CLI with offline settings
    cli = EnhancedCLI(
        cloud_mode=False,
        offline_mode=True,
        debug_mode=False
    )
    
    # Skip cloud initialization entirely
    cli.flow_nexus_integration = None
    cli.collaboration_manager = None
    
    # Run the main CLI
    try:
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for learning! See you next time!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    run_offline_cli()