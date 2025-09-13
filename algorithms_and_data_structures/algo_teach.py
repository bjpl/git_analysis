#!/usr/bin/env python3
"""
Algorithm Teaching CLI - Beautiful Formatted Output
Main entry point for the algorithm teaching system
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Force color output on Windows
os.environ["FORCE_COLOR"] = "1"
os.environ["COLORTERM"] = "truecolor"

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="🚀 Algorithm Teaching System - Beautiful CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "topic",
        nargs="?",
        default="big-o",
        choices=["big-o", "sorting", "searching", "graphs", "dp", "recursion"],
        help="Topic to teach (default: big-o)"
    )
    
    parser.add_argument(
        "--flow-nexus",
        action="store_true",
        help="Use Flow Nexus cloud features"
    )
    
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    
    args = parser.parse_args()
    
    # Import and run the teacher
    try:
        from src.flow_nexus_teacher import AlgorithmTeacher
        
        # Initialize teacher
        teacher = AlgorithmTeacher()
        
        # Teach based on topic
        if args.topic == "big-o":
            teacher.teach_big_o_notation()
        else:
            print(f"Teaching {args.topic} - Coming soon!")
        
        return 0
        
    except ImportError as e:
        print(f"Error importing teacher: {e}")
        print("\nTrying fallback mode...")
        
        # Try to install rich if not available
        try:
            import subprocess
            print("Installing rich library...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "rich", "colorama"])
            
            # Try again
            from src.flow_nexus_teacher import AlgorithmTeacher
            teacher = AlgorithmTeacher()
            teacher.teach_big_o_notation()
            return 0
            
        except Exception as install_error:
            print(f"Failed to install dependencies: {install_error}")
            print("\nPlease install manually:")
            print("  pip install rich colorama")
            return 1
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())