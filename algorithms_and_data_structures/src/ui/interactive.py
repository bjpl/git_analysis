#!/usr/bin/env python3
"""
Interactive Session - Interactive CLI mode implementation

This module provides:
- Interactive command-line interface
- Command completion and history
- Multi-line input support
- Context-aware suggestions
- Session persistence
"""

import sys
import os
import asyncio
from typing import List, Optional, Dict, Any, Set
from pathlib import Path
import readline
import atexit
from dataclasses import dataclass

from .formatter import TerminalFormatter
from ..core.exceptions import CLIError


@dataclass
class SessionState:
    """Interactive session state"""
    history_file: Optional[Path] = None
    command_history: List[str] = None
    variables: Dict[str, Any] = None
    last_result: Optional[Any] = None
    
    def __post_init__(self):
        if self.command_history is None:
            self.command_history = []
        if self.variables is None:
            self.variables = {}


class InteractiveSession:
    """Interactive CLI session manager"""
    
    def __init__(self, cli_engine):
        """Initialize interactive session
        
        Args:
            cli_engine: CLI engine instance
        """
        self.cli_engine = cli_engine
        self.formatter = cli_engine.formatter
        self.running = False
        
        # Session state
        self.state = SessionState()
        self.state.history_file = Path.home() / ".curriculum-cli" / "history"
        
        # Command completion
        self.available_commands: Set[str] = set()
        self._setup_completion()
        
        # Load history
        self._load_history()
        
        # Register cleanup
        atexit.register(self._save_history)
    
    def _setup_completion(self):
        """Setup command completion"""
        try:
            # Configure readline
            readline.set_completer_delims(" \t\n;")
            readline.set_completer(self._completer)
            readline.parse_and_bind("tab: complete")
            
            # Enable history search
            readline.parse_and_bind("\e[A: history-search-backward")
            readline.parse_and_bind("\e[B: history-search-forward")
            
            # Update available commands
            self.available_commands = set(self.cli_engine.list_commands())
            
        except ImportError:
            # readline not available (e.g., on Windows without pyreadline)
            pass
    
    def _completer(self, text: str, state: int) -> Optional[str]:
        """Command completion function
        
        Args:
            text: Current text being completed
            state: Completion state
            
        Returns:
            Next completion or None
        """
        line = readline.get_line_buffer()
        words = line.split()
        
        if not words or (len(words) == 1 and not line.endswith(' ')):
            # Complete command names
            matches = [cmd for cmd in self.available_commands 
                      if cmd.startswith(text)]
        else:
            # Complete subcommands or arguments
            command_name = words[0]
            command = self.cli_engine.get_command(command_name)
            
            if command and hasattr(command, 'get_completions'):
                matches = command.get_completions(words[1:], text)
            else:
                matches = []
        
        try:
            return matches[state]
        except IndexError:
            return None
    
    def _load_history(self):
        """Load command history from file"""
        if self.state.history_file and self.state.history_file.exists():
            try:
                readline.read_history_file(str(self.state.history_file))
                
                # Load into our state as well
                with open(self.state.history_file, 'r') as f:
                    self.state.command_history = [
                        line.strip() for line in f.readlines()
                    ]
            except (IOError, OSError) as e:
                self.formatter.debug(f"Could not load history: {e}")
    
    def _save_history(self):
        """Save command history to file"""
        if self.state.history_file:
            try:
                # Ensure directory exists
                self.state.history_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Save readline history
                readline.write_history_file(str(self.state.history_file))
                
            except (IOError, OSError) as e:
                self.formatter.debug(f"Could not save history: {e}")
    
    async def run(self):
        """Run the interactive session"""
        self.running = True
        
        # Welcome message
        self._show_welcome()
        
        try:
            while self.running:
                try:
                    # Get user input
                    line = await self._get_input()
                    
                    if not line.strip():
                        continue
                    
                    # Process command
                    await self._process_command(line.strip())
                    
                except KeyboardInterrupt:
                    self.formatter.info("\nUse 'exit' or 'quit' to leave")
                    continue
                except EOFError:
                    self.formatter.info("\nGoodbye!")
                    break
                    
        except Exception as e:
            self.formatter.error(f"Session error: {e}")
        finally:
            self.running = False
            self._save_history()
    
    def _show_welcome(self):
        """Show welcome message"""
        self.formatter.header("Curriculum CLI - Interactive Mode", level=1)
        
        # Show available commands
        commands = sorted(self.cli_engine.list_commands())
        self.formatter.info("Available commands:")
        self.formatter.list_items(commands[:10])  # Show first 10
        
        if len(commands) > 10:
            self.formatter.info(f"... and {len(commands) - 10} more. Use 'help' to see all.")
        
        self.formatter.rule()
        self.formatter.info("Type 'help' for more information or 'exit' to quit.")
        print()
    
    async def _get_input(self) -> str:
        """Get input from user with prompt
        
        Returns:
            User input string
        """
        # Create dynamic prompt
        prompt = self._create_prompt()
        
        # Get input (in thread to avoid blocking)
        loop = asyncio.get_event_loop()
        
        try:
            line = await loop.run_in_executor(None, input, prompt)
            return line
        except (KeyboardInterrupt, EOFError):
            raise
    
    def _create_prompt(self) -> str:
        """Create dynamic prompt string
        
        Returns:
            Formatted prompt string
        """
        # Base prompt
        prompt_parts = []
        
        # Add context indicators
        if self.state.variables:
            var_count = len(self.state.variables)
            prompt_parts.append(f"[vars:{var_count}]")
        
        # Add last command result indicator
        if self.state.last_result is not None:
            if hasattr(self.state.last_result, 'success'):
                status = "✓" if self.state.last_result.success else "✗"
                prompt_parts.append(f"[{status}]")
        
        # Main prompt
        context_str = " ".join(prompt_parts)
        if context_str:
            base_prompt = f"curriculum {context_str} "
        else:
            base_prompt = "curriculum "
        
        # Colorize if possible
        if self.formatter.color_enabled:
            colored_prompt = self.formatter._colorize(
                base_prompt, 
                self.formatter.theme.primary
            ) + self.formatter._colorize("❯ ", self.formatter.theme.secondary)
            return colored_prompt
        else:
            return base_prompt + "> "
    
    async def _process_command(self, line: str):
        """Process a command line
        
        Args:
            line: Command line to process
        """
        # Add to history
        self.state.command_history.append(line)
        
        # Handle special commands
        if await self._handle_special_commands(line):
            return
        
        # Handle variable assignments
        if await self._handle_variable_assignment(line):
            return
        
        # Parse command and arguments
        parts = line.split()
        if not parts:
            return
        
        command_name = parts[0]
        args = parts[1:]
        
        # Execute command
        try:
            result = await self.cli_engine.execute_command(command_name, args)
            self.state.last_result = result
            
            # Display result if needed
            if result.data and not result.message:
                self._display_result_data(result.data)
                
        except CLIError as e:
            self.formatter.error(str(e))
        except Exception as e:
            if self.cli_engine.context.debug:
                raise
            self.formatter.error(f"Command failed: {e}")
    
    async def _handle_special_commands(self, line: str) -> bool:
        """Handle special interactive commands
        
        Args:
            line: Command line
            
        Returns:
            True if command was handled
        """
        parts = line.split()
        command = parts[0].lower()
        
        if command in ['exit', 'quit', 'q']:
            self.formatter.info("Goodbye!")
            self.running = False
            return True
        
        elif command == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear')
            return True
        
        elif command == 'history':
            self._show_history()
            return True
        
        elif command == 'vars':
            self._show_variables()
            return True
        
        elif command == 'help':
            await self._show_help(parts[1:] if len(parts) > 1 else [])
            return True
        
        elif command == 'commands':
            self._show_commands()
            return True
        
        elif command == 'status':
            self._show_status()
            return True
        
        return False
    
    async def _handle_variable_assignment(self, line: str) -> bool:
        """Handle variable assignments (var = value)
        
        Args:
            line: Command line
            
        Returns:
            True if line was a variable assignment
        """
        if '=' in line and not line.strip().startswith('#'):
            try:
                var_name, var_value = line.split('=', 1)
                var_name = var_name.strip()
                var_value = var_value.strip()
                
                # Simple validation
                if not var_name.isidentifier():
                    self.formatter.error(f"Invalid variable name: {var_name}")
                    return True
                
                # Try to evaluate the value (safely)
                try:
                    # Simple literal evaluation
                    if (var_value.startswith('"') and var_value.endswith('"')) or \
                       (var_value.startswith("'") and var_value.endswith("'")):
                        evaluated_value = var_value[1:-1]
                    elif var_value.isdigit():
                        evaluated_value = int(var_value)
                    elif var_value.replace('.', '', 1).isdigit():
                        evaluated_value = float(var_value)
                    elif var_value.lower() in ['true', 'false']:
                        evaluated_value = var_value.lower() == 'true'
                    else:
                        evaluated_value = var_value
                    
                    self.state.variables[var_name] = evaluated_value
                    
                    self.formatter.success(
                        f"Variable '{var_name}' set to: {evaluated_value}"
                    )
                    
                except Exception as e:
                    self.formatter.error(f"Error evaluating value: {e}")
                
                return True
                
            except ValueError:
                pass
        
        return False
    
    def _display_result_data(self, data: Dict[str, Any]):
        """Display command result data
        
        Args:
            data: Result data to display
        """
        if isinstance(data, dict):
            self.formatter.key_value_pairs(data)
        elif isinstance(data, list):
            if data and isinstance(data[0], dict):
                self.formatter.table(data)
            else:
                self.formatter.list_items([str(item) for item in data])
        else:
            self.formatter.info(str(data))
    
    def _show_history(self):
        """Show command history"""
        self.formatter.header("Command History", level=2)
        
        if not self.state.command_history:
            self.formatter.info("No commands in history")
            return
        
        # Show last 20 commands
        recent_history = self.state.command_history[-20:]
        for i, cmd in enumerate(recent_history, 1):
            self.formatter.info(f"{i:2d}. {cmd}")
    
    def _show_variables(self):
        """Show session variables"""
        self.formatter.header("Session Variables", level=2)
        
        if not self.state.variables:
            self.formatter.info("No variables defined")
            return
        
        self.formatter.key_value_pairs(self.state.variables)
    
    async def _show_help(self, args: List[str]):
        """Show help information
        
        Args:
            args: Help command arguments
        """
        if args:
            # Help for specific command
            command_name = args[0]
            help_text = self.cli_engine.get_command_help(command_name)
            
            if help_text:
                self.formatter.header(f"Help: {command_name}", level=2)
                self.formatter.info(help_text)
            else:
                self.formatter.error(f"No help available for '{command_name}'")
        else:
            # General help
            self.formatter.header("Interactive Mode Help", level=2)
            
            help_sections = {
                "Special Commands": [
                    "exit, quit, q - Exit interactive mode",
                    "clear - Clear the screen",
                    "history - Show command history",
                    "vars - Show session variables",
                    "help [command] - Show help",
                    "commands - List all commands",
                    "status - Show session status"
                ],
                "Variables": [
                    "var_name = value - Set a variable",
                    "Variables can be strings, numbers, or booleans",
                    "Use vars to see all defined variables"
                ],
                "Tips": [
                    "Use TAB for command completion",
                    "Use UP/DOWN arrows for history navigation",
                    "Ctrl+C to cancel current input",
                    "Ctrl+D to exit"
                ]
            }
            
            for section, items in help_sections.items():
                self.formatter.header(section, level=3)
                self.formatter.list_items(items)
                print()
    
    def _show_commands(self):
        """Show all available commands"""
        self.formatter.header("Available Commands", level=2)
        
        commands = self.cli_engine.list_commands()
        
        # Group commands by category if possible
        command_info = []
        for cmd_name in sorted(commands):
            command = self.cli_engine.get_command(cmd_name)
            if command:
                command_info.append({
                    'Command': cmd_name,
                    'Category': command.category.value if hasattr(command, 'category') else 'general',
                    'Description': command.description if hasattr(command, 'description') else ''
                })
        
        if command_info:
            self.formatter.table(command_info)
        else:
            self.formatter.list_items(commands)
    
    def _show_status(self):
        """Show session status"""
        self.formatter.header("Session Status", level=2)
        
        status_info = {
            'Commands in history': len(self.state.command_history),
            'Variables defined': len(self.state.variables),
            'Available commands': len(self.available_commands),
            'Color support': 'Yes' if self.formatter.color_enabled else 'No',
            'History file': str(self.state.history_file) if self.state.history_file else 'None'
        }
        
        if self.state.last_result:
            status_info['Last command status'] = (
                'Success' if self.state.last_result.success else 'Failed'
            )
        
        self.formatter.key_value_pairs(status_info)
