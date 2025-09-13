#!/usr/bin/env python3
"""
CLI Engine - Core command routing and parsing system

This module provides the main CLI engine with:
- Command parsing and routing
- Interactive and non-interactive modes  
- Plugin system integration
- Beautiful terminal UI
- Error handling and validation
"""

import sys
import argparse
import asyncio
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import importlib
import inspect
from dataclasses import dataclass

from .config import CLIConfig
from .commands.base import BaseCommand, CommandResult
from .ui.formatter import TerminalFormatter
from .ui.interactive import InteractiveSession
from .core.plugin_manager import PluginManager
from .core.exceptions import CLIError, CommandNotFoundError


@dataclass
class CLIContext:
    """Context object passed to all commands"""
    config: CLIConfig
    formatter: TerminalFormatter
    interactive: bool = False
    verbose: bool = False
    debug: bool = False
    

class CLIEngine:
    """Main CLI engine handling command routing and execution"""
    
    def __init__(self, config: Optional[CLIConfig] = None):
        """Initialize the CLI engine
        
        Args:
            config: Optional configuration object
        """
        self.config = config or CLIConfig()
        self.formatter = TerminalFormatter()
        self.plugin_manager = PluginManager()
        self.commands: Dict[str, BaseCommand] = {}
        self.aliases: Dict[str, str] = {}
        self.context = CLIContext(
            config=self.config,
            formatter=self.formatter
        )
        
        # Load built-in commands
        self._load_built_in_commands()
        
        # Load plugins
        self._load_plugins()
    
    def _load_built_in_commands(self):
        """Load built-in commands from commands directory"""
        commands_dir = Path(__file__).parent / "commands"
        
        for command_file in commands_dir.glob("*.py"):
            if command_file.name.startswith("_") or command_file.name == "base.py":
                continue
                
            module_name = f"src.commands.{command_file.stem}"
            try:
                module = importlib.import_module(module_name)
                self._register_commands_from_module(module)
            except ImportError as e:
                self.formatter.warning(f"Failed to load command module {module_name}: {e}")
    
    def _load_plugins(self):
        """Load plugins using the plugin manager"""
        plugins = self.plugin_manager.load_all_plugins()
        for plugin in plugins:
            if hasattr(plugin, 'commands'):
                for command in plugin.commands:
                    self.register_command(command)
    
    def _register_commands_from_module(self, module):
        """Register all command classes from a module"""
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, BaseCommand) and 
                obj != BaseCommand):
                command = obj()
                self.register_command(command)
    
    def register_command(self, command: BaseCommand):
        """Register a command with the engine
        
        Args:
            command: Command instance to register
        """
        self.commands[command.name] = command
        
        # Register aliases
        if hasattr(command, 'aliases'):
            for alias in command.aliases:
                self.aliases[alias] = command.name
    
    def get_command(self, name: str) -> Optional[BaseCommand]:
        """Get a command by name or alias
        
        Args:
            name: Command name or alias
            
        Returns:
            Command instance or None if not found
        """
        # Check direct command name
        if name in self.commands:
            return self.commands[name]
        
        # Check aliases
        if name in self.aliases:
            return self.commands[self.aliases[name]]
        
        return None
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser
        
        Returns:
            Configured argument parser
        """
        parser = argparse.ArgumentParser(
            prog='curriculum-cli',
            description='Beautiful curriculum and content management CLI',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Global options
        parser.add_argument(
            '--config', '-c',
            type=Path,
            help='Path to configuration file'
        )
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Enable verbose output'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug mode'
        )
        parser.add_argument(
            '--no-color',
            action='store_true',
            help='Disable colored output'
        )
        parser.add_argument(
            '--interactive', '-i',
            action='store_true',
            help='Start interactive mode'
        )
        
        # Subcommands
        subparsers = parser.add_subparsers(
            dest='command',
            title='Available commands',
            description='Use <command> --help for command-specific options'
        )
        
        # Add each registered command
        for command in self.commands.values():
            command.setup_parser(subparsers)
        
        return parser
    
    async def execute_command(self, command_name: str, args: List[str]) -> CommandResult:
        """Execute a command with given arguments
        
        Args:
            command_name: Name of command to execute
            args: Command arguments
            
        Returns:
            Command execution result
            
        Raises:
            CommandNotFoundError: If command doesn't exist
        """
        command = self.get_command(command_name)
        if not command:
            raise CommandNotFoundError(f"Command '{command_name}' not found")
        
        try:
            result = await command.execute(self.context, args)
            return result
        except Exception as e:
            if self.context.debug:
                raise
            return CommandResult(
                success=False,
                message=str(e),
                error=e
            )
    
    async def run_interactive(self):
        """Run the CLI in interactive mode"""
        self.context.interactive = True
        
        session = InteractiveSession(self)
        await session.run()
    
    async def run_single_command(self, args: List[str]) -> int:
        """Run a single command and exit
        
        Args:
            args: Command line arguments
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        parser = self.create_parser()
        
        try:
            parsed_args = parser.parse_args(args)
        except SystemExit:
            return 1
        
        # Update context with parsed global options
        if parsed_args.config:
            self.config.load_from_file(parsed_args.config)
        
        self.context.verbose = parsed_args.verbose
        self.context.debug = parsed_args.debug
        
        if parsed_args.no_color:
            self.formatter.disable_color()
        
        # Handle interactive mode
        if parsed_args.interactive:
            await self.run_interactive()
            return 0
        
        # Handle no command specified
        if not parsed_args.command:
            parser.print_help()
            return 0
        
        # Execute the command
        try:
            result = await self.execute_command(
                parsed_args.command,
                sys.argv[2:]  # Skip program name and command name
            )
            
            if result.message:
                if result.success:
                    self.formatter.success(result.message)
                else:
                    self.formatter.error(result.message)
            
            return 0 if result.success else 1
            
        except CLIError as e:
            self.formatter.error(str(e))
            return 1
        except KeyboardInterrupt:
            self.formatter.warning("\nOperation cancelled by user")
            return 130
        except Exception as e:
            if self.context.debug:
                raise
            self.formatter.error(f"Unexpected error: {e}")
            return 1
    
    def list_commands(self) -> List[str]:
        """Get list of available command names
        
        Returns:
            Sorted list of command names
        """
        return sorted(self.commands.keys())
    
    def get_command_help(self, command_name: str) -> Optional[str]:
        """Get help text for a specific command
        
        Args:
            command_name: Name of command
            
        Returns:
            Help text or None if command not found
        """
        command = self.get_command(command_name)
        if command:
            return command.get_help()
        return None


async def main():
    """Main entry point for the CLI"""
    engine = CLIEngine()
    exit_code = await engine.run_single_command(sys.argv[1:])
    sys.exit(exit_code)


if __name__ == '__main__':
    asyncio.run(main())
