#!/usr/bin/env python3
"""
Base Command Interface - Abstract command pattern implementation

This module provides:
- Abstract base class for all CLI commands
- Command result standardization
- Argument parsing helpers
- Validation and error handling patterns
- Command metadata and documentation
"""

import asyncio
import argparse
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum


class CommandCategory(Enum):
    """Command categories for organization"""
    CURRICULUM = "curriculum"
    CONTENT = "content"
    USER = "user"
    ADMIN = "admin"
    SYSTEM = "system"
    PLUGIN = "plugin"


@dataclass
class CommandResult:
    """Standardized command execution result"""
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None
    exit_code: int = 0
    
    def __post_init__(self):
        if not self.success and self.exit_code == 0:
            self.exit_code = 1


@dataclass
class CommandMetadata:
    """Command metadata for documentation and help"""
    name: str
    description: str
    category: CommandCategory
    aliases: List[str] = None
    examples: List[str] = None
    see_also: List[str] = None
    version: str = "1.0.0"
    author: Optional[str] = None
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []
        if self.examples is None:
            self.examples = []
        if self.see_also is None:
            self.see_also = []


class BaseCommand(ABC):
    """Abstract base class for all CLI commands"""
    
    def __init__(self):
        """Initialize the command"""
        self._metadata = self.get_metadata()
        self._parser: Optional[argparse.ArgumentParser] = None
    
    @property
    def name(self) -> str:
        """Command name"""
        return self._metadata.name
    
    @property
    def description(self) -> str:
        """Command description"""
        return self._metadata.description
    
    @property
    def category(self) -> CommandCategory:
        """Command category"""
        return self._metadata.category
    
    @property
    def aliases(self) -> List[str]:
        """Command aliases"""
        return self._metadata.aliases
    
    @property
    def examples(self) -> List[str]:
        """Usage examples"""
        return self._metadata.examples
    
    @abstractmethod
    def get_metadata(self) -> CommandMetadata:
        """Get command metadata
        
        Returns:
            Command metadata object
        """
        pass
    
    @abstractmethod
    def setup_parser(self, subparsers) -> argparse.ArgumentParser:
        """Setup command argument parser
        
        Args:
            subparsers: Subparsers object from main parser
            
        Returns:
            Command-specific argument parser
        """
        pass
    
    @abstractmethod
    async def execute(self, context, args: List[str]) -> CommandResult:
        """Execute the command
        
        Args:
            context: CLI context object
            args: Command arguments
            
        Returns:
            Command execution result
        """
        pass
    
    def get_help(self) -> str:
        """Get detailed help text for the command
        
        Returns:
            Formatted help text
        """
        help_text = []
        
        # Basic info
        help_text.append(f"Command: {self.name}")
        help_text.append(f"Description: {self.description}")
        help_text.append(f"Category: {self.category.value}")
        
        # Aliases
        if self.aliases:
            help_text.append(f"Aliases: {', '.join(self.aliases)}")
        
        # Examples
        if self.examples:
            help_text.append("\nExamples:")
            for example in self.examples:
                help_text.append(f"  {example}")
        
        # See also
        if self._metadata.see_also:
            help_text.append(f"\nSee also: {', '.join(self._metadata.see_also)}")
        
        return "\n".join(help_text)
    
    def validate_args(self, args: argparse.Namespace) -> List[str]:
        """Validate parsed arguments
        
        Args:
            args: Parsed arguments
            
        Returns:
            List of validation error messages
        """
        # Override in subclasses for custom validation
        return []
    
    def create_subparser(self, subparsers, **kwargs) -> argparse.ArgumentParser:
        """Helper to create subparser with standard options
        
        Args:
            subparsers: Subparsers object
            **kwargs: Additional arguments for add_parser
            
        Returns:
            Created subparser
        """
        parser_kwargs = {
            'help': self.description,
            'description': self.description,
            'formatter_class': argparse.RawDescriptionHelpFormatter,
            **kwargs
        }
        
        parser = subparsers.add_parser(self.name, **parser_kwargs)
        
        # Add aliases
        for alias in self.aliases:
            subparsers.add_parser(alias, parents=[parser], add_help=False)
        
        # Add common options
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force execution without confirmation prompts'
        )
        parser.add_argument(
            '--quiet', '-q',
            action='store_true',
            help='Suppress non-error output'
        )
        
        self._parser = parser
        return parser
    
    def parse_args(self, args: List[str]) -> argparse.Namespace:
        """Parse command arguments
        
        Args:
            args: Raw arguments list
            
        Returns:
            Parsed arguments
            
        Raises:
            SystemExit: If parsing fails
        """
        if not self._parser:
            raise RuntimeError("Parser not initialized. Call setup_parser() first.")
        
        return self._parser.parse_args(args)
    
    async def run_with_error_handling(self, context, args: List[str]) -> CommandResult:
        """Execute command with comprehensive error handling
        
        Args:
            context: CLI context
            args: Command arguments
            
        Returns:
            Command result with error handling
        """
        try:
            # Parse arguments
            if not self._parser:
                return CommandResult(
                    success=False,
                    message="Command parser not initialized",
                    exit_code=2
                )
            
            parsed_args = self.parse_args(args)
            
            # Validate arguments
            validation_errors = self.validate_args(parsed_args)
            if validation_errors:
                return CommandResult(
                    success=False,
                    message="Validation errors:\n" + "\n".join(validation_errors),
                    exit_code=2
                )
            
            # Execute command
            return await self.execute(context, args)
            
        except KeyboardInterrupt:
            return CommandResult(
                success=False,
                message="Command interrupted by user",
                exit_code=130
            )
        except Exception as e:
            if context.debug:
                raise
            return CommandResult(
                success=False,
                message=f"Command failed: {e}",
                error=e,
                exit_code=1
            )
    
    def confirm_action(self, message: str, default: bool = False) -> bool:
        """Ask user for confirmation
        
        Args:
            message: Confirmation message
            default: Default response if user just presses enter
            
        Returns:
            True if user confirms, False otherwise
        """
        suffix = " [Y/n]" if default else " [y/N]"
        
        try:
            response = input(f"{message}{suffix}: ").strip().lower()
            if not response:
                return default
            return response in ['y', 'yes']
        except (KeyboardInterrupt, EOFError):
            return False
    
    def format_table_data(self, data: List[Dict[str, Any]], headers: List[str]) -> str:
        """Format data as a table
        
        Args:
            data: List of data dictionaries
            headers: Table headers
            
        Returns:
            Formatted table string
        """
        if not data:
            return "No data to display"
        
        # Calculate column widths
        widths = {}
        for header in headers:
            widths[header] = len(header)
        
        for row in data:
            for header in headers:
                value = str(row.get(header, ''))
                widths[header] = max(widths[header], len(value))
        
        # Format table
        lines = []
        
        # Header
        header_line = " | ".join(header.ljust(widths[header]) for header in headers)
        lines.append(header_line)
        lines.append("-" * len(header_line))
        
        # Data rows
        for row in data:
            row_line = " | ".join(
                str(row.get(header, '')).ljust(widths[header]) 
                for header in headers
            )
            lines.append(row_line)
        
        return "\n".join(lines)


class AsyncCommand(BaseCommand):
    """Base class for asynchronous commands"""
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        """Execute async command
        
        Args:
            context: CLI context
            args: Command arguments
            
        Returns:
            Command result
        """
        return await self.async_execute(context, args)
    
    @abstractmethod
    async def async_execute(self, context, args: List[str]) -> CommandResult:
        """Async command execution implementation
        
        Args:
            context: CLI context
            args: Command arguments
            
        Returns:
            Command result
        """
        pass


class SyncCommand(BaseCommand):
    """Base class for synchronous commands"""
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        """Execute sync command in async context
        
        Args:
            context: CLI context
            args: Command arguments
            
        Returns:
            Command result
        """
        # Run sync command in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.sync_execute, context, args)
    
    @abstractmethod
    def sync_execute(self, context, args: List[str]) -> CommandResult:
        """Sync command execution implementation
        
        Args:
            context: CLI context
            args: Command arguments
            
        Returns:
            Command result
        """
        pass


class CompositeBECommand(BaseCommand):
    """Base class for commands that combine multiple sub-operations"""
    
    def __init__(self):
        super().__init__()
        self.sub_commands: Dict[str, BaseCommand] = {}
    
    def add_sub_command(self, command: BaseCommand):
        """Add a sub-command
        
        Args:
            command: Sub-command to add
        """
        self.sub_commands[command.name] = command
        
        # Also add by aliases
        for alias in command.aliases:
            self.sub_commands[alias] = command
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        """Execute composite command
        
        Args:
            context: CLI context
            args: Command arguments
            
        Returns:
            Command result
        """
        if not args:
            return CommandResult(
                success=False,
                message=f"Sub-command required. Available: {list(self.sub_commands.keys())}",
                exit_code=2
            )
        
        sub_command_name = args[0]
        sub_command = self.sub_commands.get(sub_command_name)
        
        if not sub_command:
            return CommandResult(
                success=False,
                message=f"Unknown sub-command '{sub_command_name}'. Available: {list(self.sub_commands.keys())}",
                exit_code=2
            )
        
        return await sub_command.execute(context, args[1:])
