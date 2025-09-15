#!/usr/bin/env python3
"""
Improved main entry point for the Algorithm Learning System.
Handles both interactive and non-interactive modes gracefully.
"""

import sys
import os
from pathlib import Path
from typing import Optional
import argparse
import logging
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from cli import AlgorithmLearningCLI
    from config import Config
except ImportError:
    from src.cli import AlgorithmLearningCLI
    from src.config import Config


class RunMode(Enum):
    """Application run modes"""
    INTERACTIVE = "interactive"
    COMMAND = "command"
    BATCH = "batch"
    TEST = "test"


class ImprovedApplication:
    """Improved application controller with better error handling and modes"""
    
    def __init__(self, mode: RunMode = RunMode.INTERACTIVE):
        self.mode = mode
        self.config = Config()
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging based on mode"""
        log_level = logging.DEBUG if self.mode == RunMode.TEST else logging.INFO
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Create logs directory if it doesn't exist
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_dir / "app.log"),
                logging.StreamHandler(sys.stdout) if self.mode == RunMode.TEST else logging.NullHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def run_interactive(self) -> int:
        """Run in interactive mode with full CLI"""
        try:
            self.logger.info("Starting interactive mode")
            cli = AlgorithmLearningCLI()
            
            # Check if running in a proper terminal
            if not sys.stdin.isatty():
                print("Warning: Not running in an interactive terminal.")
                print("Please run this application in a proper terminal for the best experience.")
                return 1
                
            cli.run()
            return 0
            
        except KeyboardInterrupt:
            print("\n\n[yellow]Interrupted by user. Goodbye![/yellow]")
            return 0
        except EOFError:
            print("\n[red]Error: No input available. Please run in an interactive terminal.[/red]")
            return 1
        except Exception as e:
            self.logger.exception("Unexpected error in interactive mode")
            print(f"\n[red]An unexpected error occurred: {e}[/red]")
            print("Please check the logs for more details.")
            return 1
            
    def run_command(self, command: str, *args) -> int:
        """Run a specific command without interactive menu"""
        try:
            self.logger.info(f"Running command: {command} with args: {args}")
            cli = AlgorithmLearningCLI()
            
            commands = {
                "continue": cli.continue_learning,
                "progress": cli.show_progress,
                "notes": cli.show_notes,
                "lesson": lambda: cli.start_lesson(args[0] if args else None),
                "review": cli.review_completed_lessons,
                "help": self.show_help
            }
            
            if command in commands:
                commands[command]()
                return 0
            else:
                print(f"Unknown command: {command}")
                self.show_help()
                return 1
                
        except Exception as e:
            self.logger.exception(f"Error running command {command}")
            print(f"Error: {e}")
            return 1
            
    def run_batch(self, script_file: str) -> int:
        """Run commands from a batch file"""
        try:
            self.logger.info(f"Running batch file: {script_file}")
            
            script_path = Path(script_file)
            if not script_path.exists():
                print(f"Batch file not found: {script_file}")
                return 1
                
            with open(script_path, 'r') as f:
                commands = f.readlines()
                
            cli = AlgorithmLearningCLI()
            for line in commands:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split()
                    if parts:
                        command = parts[0]
                        args = parts[1:]
                        print(f"Executing: {line}")
                        self.run_command(command, *args)
                        
            return 0
            
        except Exception as e:
            self.logger.exception(f"Error running batch file {script_file}")
            print(f"Error: {e}")
            return 1
            
    def run_test(self) -> int:
        """Run in test mode for automated testing"""
        try:
            self.logger.info("Running in test mode")
            
            # Quick smoke test of core functionality
            cli = AlgorithmLearningCLI()
            
            # Test that we can initialize
            assert cli is not None
            assert cli.curriculum_service is not None
            
            # Test that we can get curriculum
            topics = cli.curriculum_service.get_all_topics()
            assert len(topics) > 0
            
            print("✅ Test mode: All basic checks passed")
            return 0
            
        except Exception as e:
            self.logger.exception("Test mode failed")
            print(f"❌ Test mode failed: {e}")
            return 1
            
    def show_help(self):
        """Display help information"""
        help_text = """
Algorithm Learning System - Command Line Interface

Usage:
    python main.py [options] [command] [args]

Options:
    -m, --mode MODE      Run mode: interactive|command|batch|test (default: interactive)
    -c, --command CMD    Run a specific command
    -b, --batch FILE     Run commands from a batch file
    -t, --test          Run in test mode
    -h, --help          Show this help message

Commands:
    continue            Continue learning from where you left off
    progress            View your learning progress
    notes              Review your notes
    lesson [ID]        Start a specific lesson
    review             Review completed lessons
    help               Show this help message

Examples:
    python main.py                           # Interactive mode
    python main.py -c progress               # Show progress and exit
    python main.py -c lesson arrays_intro    # Start specific lesson
    python main.py -b commands.txt           # Run batch commands
    python main.py -t                        # Run tests

Batch File Format:
    # Comments start with #
    continue
    progress
    notes
    lesson arrays_intro
    review
        """
        print(help_text)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Algorithm Learning System - Learn Data Structures & Algorithms",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-m', '--mode',
        type=str,
        choices=['interactive', 'command', 'batch', 'test'],
        default='interactive',
        help='Run mode (default: interactive)'
    )
    
    parser.add_argument(
        '-c', '--command',
        type=str,
        help='Run a specific command'
    )
    
    parser.add_argument(
        '-b', '--batch',
        type=str,
        help='Run commands from a batch file'
    )
    
    parser.add_argument(
        '-t', '--test',
        action='store_true',
        help='Run in test mode'
    )
    
    parser.add_argument(
        'args',
        nargs='*',
        help='Additional arguments for commands'
    )
    
    return parser.parse_args()


def main():
    """Main entry point with improved error handling and modes"""
    args = parse_arguments()
    
    # Determine run mode
    if args.test:
        mode = RunMode.TEST
    elif args.batch:
        mode = RunMode.BATCH
    elif args.command:
        mode = RunMode.COMMAND
    else:
        mode = RunMode.INTERACTIVE
    
    # Create and run application
    app = ImprovedApplication(mode)
    
    # Execute based on mode
    if mode == RunMode.TEST:
        return app.run_test()
    elif mode == RunMode.BATCH:
        return app.run_batch(args.batch)
    elif mode == RunMode.COMMAND:
        return app.run_command(args.command, *args.args)
    else:
        return app.run_interactive()


if __name__ == "__main__":
    sys.exit(main())