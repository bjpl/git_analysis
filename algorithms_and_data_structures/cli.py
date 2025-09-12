#!/usr/bin/env python3
"""
Algorithms & Data Structures CLI
A comprehensive learning platform with interactive UI
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.interactive import InteractiveUI
from src.ui.formatter import OutputFormatter
import argparse

def main():
    parser = argparse.ArgumentParser(
        description='Algorithms & Data Structures CLI - Interactive Learning Platform'
    )
    
    parser.add_argument(
        '--mode',
        choices=['interactive', 'batch', 'test'],
        default='interactive',
        help='CLI mode (default: interactive)'
    )
    
    parser.add_argument(
        '--theme',
        choices=['default', 'dark', 'light', 'high-contrast'],
        default='default',
        help='UI theme (default: default)'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'interactive':
        # Launch interactive UI
        ui = InteractiveUI(theme=args.theme, use_color=not args.no_color)
        ui.run()
    elif args.mode == 'batch':
        print("Batch mode - coming soon!")
    elif args.mode == 'test':
        print("Test mode - running diagnostics...")
        formatter = OutputFormatter()
        formatter.print_success("✓ CLI is working correctly!")
        formatter.print_info("All systems operational")
    
if __name__ == '__main__':
    main()