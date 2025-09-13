#!/usr/bin/env python3
"""
Command Router System
Handles routing of CLI commands to appropriate handlers with beautiful display
"""

import sys
import argparse
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path


class CommandContext:
    """Context object passed to command handlers"""
    
    def __init__(self, formatter, curriculum_manager):
        self.formatter = formatter
        self.curriculum_manager = curriculum_manager
        self.interactive_session = None


class CommandRouter:
    """Main command router for the CLI system"""
    
    def __init__(self):
        # Lazy import to avoid circular imports
        from .ui.windows_formatter import WindowsFormatter
        
        self.formatter = WindowsFormatter()
        self.curriculum_manager = None  # Initialize later to avoid circular imports
        self.context = None
        self.command_aliases = self._build_aliases()
    
    def _get_curriculum_commands(self):
        """Get curriculum commands with lazy loading"""
        from .commands.curriculum_commands import (
            CurriculumListCommand,
            CurriculumCreateCommand,
            CurriculumShowCommand,
            CurriculumUpdateCommand,
            CurriculumDeleteCommand
        )
        
        return {
            'list': CurriculumListCommand(),
            'create': CurriculumCreateCommand(),
            'show': CurriculumShowCommand(), 
            'update': CurriculumUpdateCommand(),
            'delete': CurriculumDeleteCommand(),
        }
    
    def _build_aliases(self) -> Dict[str, str]:
        """Build command alias mappings"""
        aliases = {
            # Curriculum aliases
            'curr': 'curriculum',
            'curriculum-list': 'curriculum list',
            'curr-list': 'curriculum list',
            'list-curr': 'curriculum list',
            'curriculum-create': 'curriculum create',
            'curr-create': 'curriculum create', 
            'create-curr': 'curriculum create',
            'curriculum-show': 'curriculum show',
            'curr-show': 'curriculum show',
            'show-curr': 'curriculum show',
            'curriculum-update': 'curriculum update',
            'curr-update': 'curriculum update',
            'update-curr': 'curriculum update',
            'curriculum-delete': 'curriculum delete',
            'curr-delete': 'curriculum delete',
            'delete-curr': 'curriculum delete',
        }
        
        return aliases
    
    def parse_command(self, args: List[str]) -> tuple[str, List[str]]:
        """Parse command line arguments into command and args"""
        if not args:
            return 'help', []
        
        # Handle aliases first - but only exact matches or word-boundary matches
        full_command = ' '.join(args)
        for alias, command in self.command_aliases.items():
            # Only match if alias is a complete word at the start
            if full_command == alias or full_command.startswith(alias + ' '):
                remaining = full_command[len(alias):].strip()
                new_args = command.split() + (remaining.split() if remaining else [])
                return command.split()[0], command.split()[1:] + (remaining.split() if remaining else [])
        
        # Parse normal commands
        command = args[0]
        remaining_args = args[1:] if len(args) > 1 else []
        
        return command, remaining_args
    
    async def route_command(self, command: str, args: List[str]) -> bool:
        """Route command to appropriate handler"""
        try:
            # Handle special commands
            if command == 'help' or command == '--help':
                self.show_help()
                return True
            elif command == 'version' or command == '--version':
                self.show_version()
                return True
            
            # Handle curriculum commands
            if command == 'curriculum' or command == 'curr':
                return await self._handle_curriculum_command(args)
            
            # Handle direct curriculum subcommands
            curriculum_subcommands = ['list', 'create', 'show', 'update', 'delete']
            if command in curriculum_subcommands:
                return await self._handle_curriculum_command([command] + args)
            
            # Handle learn command
            if command == 'learn':
                return await self._handle_learn_command(args)
            
            # Unknown command
            self.formatter.error(f"Unknown command: {command}")
            self.formatter.info("Use 'help' to see available commands")
            return False
            
        except Exception as e:
            self.formatter.error(f"Error executing command: {e}")
            if hasattr(sys, 'ps1'):  # Interactive mode
                import traceback
                traceback.print_exc()
            return False
    
    async def _handle_curriculum_command(self, args: List[str]) -> bool:
        """Handle curriculum-related commands"""
        if not args:
            # Show curriculum help
            self._show_curriculum_help()
            return True
        
        subcommand = args[0]
        subcommand_args = args[1:] if len(args) > 1 else []
        
        try:
            # Handle curriculum commands directly to avoid complex command loading
            if subcommand == 'list':
                return await self._handle_curriculum_list(subcommand_args)
            elif subcommand == 'show':
                return await self._handle_curriculum_show(subcommand_args)
            elif subcommand == 'create':
                return await self._handle_curriculum_create(subcommand_args)
            elif subcommand == 'update':
                return await self._handle_curriculum_update(subcommand_args)
            elif subcommand == 'delete':
                return await self._handle_curriculum_delete(subcommand_args)
            else:
                self.formatter.error(f"Unknown curriculum command: {subcommand}")
                self._show_curriculum_help()
                return False
                
        except Exception as e:
            self.formatter.error(f"Error executing curriculum command: {e}")
            return False
    
    def _show_curriculum_help(self):
        """Show curriculum command help"""
        self.formatter.header("📚 Curriculum Commands", level=2)
        
        commands = [
            ("list", "List all curricula with filtering and sorting"),
            ("create", "Create a new curriculum interactively"),
            ("show [ID/NAME]", "Show detailed information about a curriculum"),
            ("update [ID]", "Update an existing curriculum"),
            ("delete [ID/NAME]", "Delete a curriculum with confirmation")
        ]
        
        for cmd, desc in commands:
            cmd_colored = self.formatter._color(f"curriculum {cmd}", 
                                               self.formatter.theme.primary)
            print(f"  {cmd_colored:<30} {desc}")
        
        print("\nAliases:")
        aliases = [
            ("curr", "Short for 'curriculum'"),
            ("curriculum-list", "Direct alias for 'curriculum list'"),
            ("curr-list", "Short alias for 'curriculum list'")
        ]
        
        for alias, desc in aliases:
            alias_colored = self.formatter._color(alias, self.formatter.theme.secondary)
            print(f"  {alias_colored:<30} {desc}")
    
    def show_help(self):
        """Show general help information"""
        # Beautiful ASCII art header
        self.formatter.clear_screen()
        
        header = """
╔══════════════════════════════════════════════════════════════════╗
║                 ALGORITHMS & DATA STRUCTURES CLI                 ║
║                    Command Reference Guide                       ║
╚══════════════════════════════════════════════════════════════════╝
        """
        print(self.formatter._color(header, self.formatter.theme.primary))
        
        print("\n📋 AVAILABLE COMMANDS:\n")
        
        # Command categories
        categories = [
            ("📚 CURRICULUM MANAGEMENT", [
                ("curriculum list", "List all curricula with filtering options"),
                ("curriculum create", "Create new curriculum interactively"),
                ("curriculum show [ID]", "Show detailed curriculum information"),
                ("curriculum update [ID]", "Update existing curriculum"),
                ("curriculum delete [ID]", "Delete curriculum with confirmation")
            ]),
            ("🔧 SYSTEM COMMANDS", [
                ("help", "Show this help message"),
                ("version", "Show version information")
            ]),
            ("⚡ QUICK ALIASES", [
                ("curr", "Short for 'curriculum'"),
                ("curr-list", "Quick curriculum listing"),
                ("list-curr", "Alternative curriculum listing")
            ])
        ]
        
        for category_name, commands in categories:
            print(self.formatter._color(category_name, self.formatter.theme.warning))
            for cmd, desc in commands:
                cmd_colored = self.formatter._color(f"  {cmd:<20}", 
                                                   self.formatter.theme.success)
                print(f"{cmd_colored} {desc}")
            print()
        
        print("📝 EXAMPLES:")
        examples = [
            "python cli.py curriculum list",
            "python cli.py curriculum list --status active",
            "python cli.py curriculum show 1",
            "python cli.py curriculum create --interactive",
            "python cli.py curr-list --format json"
        ]
        
        for example in examples:
            print(f"  {self.formatter._color(example, self.formatter.theme.info)}")
        
        print("\n💡 TIP: Use 'python cli.py' without arguments to start interactive mode\n")
    
    def show_version(self):
        """Show version information"""
        version_info = """
╔══════════════════════════════════════════════════════════════════╗
║             Algorithms & Data Structures CLI v2.0               ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  🎓 Comprehensive learning platform for algorithms & DS         ║
║  📚 Interactive curriculum management                           ║
║  🤖 Claude AI integration for enhanced learning                ║
║  📊 Progress tracking and analytics                             ║
║  🎯 Practice problems and challenges                            ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
        """
        print(self.formatter._color(version_info, self.formatter.theme.primary))
    
    async def handle_interactive_command_async(self, command_line: str) -> bool:
        """Handle command entered in interactive mode (async version)"""
        if not command_line.strip():
            return True
        
        # Parse the command line
        args = command_line.strip().split()
        command, remaining_args = self.parse_command(args)
        
        # Route to appropriate handler
        return await self.route_command(command, remaining_args)
    
    def handle_interactive_command(self, command_line: str) -> bool:
        """Handle command entered in interactive mode (sync version)"""
        if not command_line.strip():
            return True
        
        # Parse the command line
        args = command_line.strip().split()
        command, remaining_args = self.parse_command(args)
        
        # Route to appropriate handler
        import asyncio
        try:
            return asyncio.run(self.route_command(command, remaining_args))
        except RuntimeError as e:
            if "asyncio.run() cannot be called from a running event loop" in str(e):
                # We're already in an async context, create a task instead
                loop = asyncio.get_running_loop()
                task = loop.create_task(self.route_command(command, remaining_args))
                return asyncio.run_coroutine_threadsafe(task, loop).result()
            raise
    
    async def _handle_curriculum_list(self, args: List[str]) -> bool:
        """Handle curriculum list command"""
        try:
            # Initialize curriculum manager lazily
            if not self.curriculum_manager:
                from .curriculum_manager import CurriculumManager
                self.curriculum_manager = CurriculumManager()
            
            # Parse basic arguments
            format_type = "table"
            status_filter = None
            difficulty_filter = None
            
            # Simple argument parsing
            i = 0
            while i < len(args):
                if args[i] == '--format' and i + 1 < len(args):
                    format_type = args[i + 1]
                    i += 2
                elif args[i] == '--status' and i + 1 < len(args):
                    status_filter = args[i + 1]
                    i += 2
                elif args[i] == '--difficulty' and i + 1 < len(args):
                    difficulty_filter = args[i + 1]
                    i += 2
                else:
                    i += 1
            
            # Build filters
            filters = {}
            if status_filter:
                filters['status'] = status_filter
            if difficulty_filter:
                filters['difficulty'] = difficulty_filter
            
            # Get curricula
            curricula = self.curriculum_manager.get_curricula(filters)
            
            # Display curricula
            self.curriculum_manager.display_curriculum_list(curricula, format_type)
            
            return True
            
        except Exception as e:
            self.formatter.error(f"Failed to list curricula: {e}")
            return False
    
    async def _handle_curriculum_show(self, args: List[str]) -> bool:
        """Handle curriculum show command"""
        try:
            # Initialize curriculum manager lazily
            if not self.curriculum_manager:
                from .curriculum_manager import CurriculumManager
                self.curriculum_manager = CurriculumManager()
            
            if not args:
                self.formatter.error("Please specify curriculum ID or name")
                return False
            
            identifier = args[0]
            include_modules = '--include-modules' in args
            include_stats = '--include-stats' in args
            
            # Try to find curriculum by ID or name
            curriculum = None
            if identifier.isdigit():
                curriculum = self.curriculum_manager.find_curriculum_by_id(int(identifier))
            else:
                curriculum = self.curriculum_manager.find_curriculum_by_name(identifier)
            
            if not curriculum:
                self.formatter.error(f"Curriculum '{identifier}' not found")
                return False
            
            # Display curriculum details
            self.curriculum_manager.display_curriculum_details(curriculum, include_modules, include_stats)
            
            return True
            
        except Exception as e:
            self.formatter.error(f"Failed to show curriculum: {e}")
            return False
    
    async def _handle_curriculum_create(self, args: List[str]) -> bool:
        """Handle curriculum create command"""
        self.formatter.info("🚧 Curriculum creation feature coming soon!")
        self.formatter.info("This will allow you to create new curricula interactively.")
        return True
    
    async def _handle_curriculum_update(self, args: List[str]) -> bool:
        """Handle curriculum update command"""
        self.formatter.info("🚧 Curriculum update feature coming soon!")
        self.formatter.info("This will allow you to modify existing curricula.")
        return True
    
    async def _handle_curriculum_delete(self, args: List[str]) -> bool:
        """Handle curriculum delete command"""
        self.formatter.info("🚧 Curriculum deletion feature coming soon!")
        self.formatter.info("This will allow you to safely remove curricula with confirmation.")
        return True
    
    async def _handle_learn_command(self, args: List[str]) -> bool:
        """Handle learn command - launch the interactive learning platform"""
        try:
            self.formatter.info("🎓 Launching Interactive Learning Platform...")
            
            # Import the enhanced CLI to launch interactive mode
            from .enhanced_cli import EnhancedCLI
            
            # Create CLI with appropriate options
            cli_options = {}
            if '--cloud' in args:
                cli_options['cloud_mode'] = True
            if '--offline' in args:
                cli_options['offline_mode'] = True
            if '--debug' in args:
                cli_options['debug_mode'] = True
            
            # Create and run the enhanced CLI
            cli = EnhancedCLI(**cli_options)
            
            # If cloud mode requested, initialize cloud features
            if cli_options.get('cloud_mode'):
                await cli.initialize_cloud_features()
            
            # Run the interactive CLI
            await cli.run()
            return True
            
        except Exception as e:
            self.formatter.error(f"Failed to launch learning platform: {e}")
            self.formatter.info("Try running: python learn.py")
            return False
