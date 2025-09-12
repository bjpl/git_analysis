#!/usr/bin/env python3
"""
Commands Package - CLI Command Registry

This package contains all CLI command implementations following
the Command pattern with the base classes defined in base.py.
"""

from .base import BaseCommand, AsyncCommand, SyncCommand, CompositeBECommand
from .base import CommandResult, CommandMetadata, CommandCategory

# Import all command modules
from .curriculum_commands import (
    CurriculumListCommand,
    CurriculumCreateCommand,
    CurriculumShowCommand,
    CurriculumUpdateCommand,
    CurriculumDeleteCommand
)

from .content_commands import (
    ContentListCommand,
    ContentCreateCommand,
    ContentShowCommand,
    ContentUpdateCommand,
    ContentDeleteCommand
)

from .progress_commands import (
    ProgressListCommand,
    ProgressShowCommand,
    ProgressTrackCommand,
    ProgressAnalyticsCommand
)

from .search_commands import (
    SearchCommand,
    SavedSearchCommand,
    SearchAnalyticsCommand
)

from .admin_commands import (
    UserManagementCommand,
    SystemConfigCommand,
    SystemHealthCommand
)

# Registry of all available commands
ALL_COMMANDS = [
    # Curriculum management
    CurriculumListCommand,
    CurriculumCreateCommand,
    CurriculumShowCommand,
    CurriculumUpdateCommand,
    CurriculumDeleteCommand,
    
    # Content management
    ContentListCommand,
    ContentCreateCommand,
    ContentShowCommand,
    ContentUpdateCommand,
    ContentDeleteCommand,
    
    # Progress tracking
    ProgressListCommand,
    ProgressShowCommand,
    ProgressTrackCommand,
    ProgressAnalyticsCommand,
    
    # Search and discovery
    SearchCommand,
    SavedSearchCommand,
    SearchAnalyticsCommand,
    
    # Administrative
    UserManagementCommand,
    SystemConfigCommand,
    SystemHealthCommand,
]

__all__ = [
    'BaseCommand',
    'AsyncCommand', 
    'SyncCommand',
    'CompositeBECommand',
    'CommandResult',
    'CommandMetadata',
    'CommandCategory',
    'ALL_COMMANDS',
    # Curriculum commands
    'CurriculumListCommand',
    'CurriculumCreateCommand',
    'CurriculumShowCommand',
    'CurriculumUpdateCommand',
    'CurriculumDeleteCommand',
    # Content commands
    'ContentListCommand',
    'ContentCreateCommand',
    'ContentShowCommand',
    'ContentUpdateCommand',
    'ContentDeleteCommand',
    # Progress commands
    'ProgressListCommand',
    'ProgressShowCommand',
    'ProgressTrackCommand',
    'ProgressAnalyticsCommand',
    # Search commands
    'SearchCommand',
    'SavedSearchCommand',
    'SearchAnalyticsCommand',
    # Admin commands
    'UserManagementCommand',
    'SystemConfigCommand',
    'SystemHealthCommand',
]


def get_all_commands():
    """Get all available command classes
    
    Returns:
        List[BaseCommand]: List of all command classes
    """
    return ALL_COMMANDS


def get_commands_by_category(category: CommandCategory):
    """Get commands filtered by category
    
    Args:
        category: Command category to filter by
        
    Returns:
        List[BaseCommand]: List of command classes in the category
    """
    return [cmd for cmd in ALL_COMMANDS if cmd().category == category]


def get_command_by_name(name: str):
    """Get command class by name or alias
    
    Args:
        name: Command name or alias
        
    Returns:
        Optional[BaseCommand]: Command class if found, None otherwise
    """
    for cmd_class in ALL_COMMANDS:
        cmd = cmd_class()
        if cmd.name == name or name in cmd.aliases:
            return cmd_class
    return None
