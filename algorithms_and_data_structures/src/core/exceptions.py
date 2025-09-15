#!/usr/bin/env python3
"""
Core Exceptions - Custom exception classes for the CLI system

This module provides:
- Hierarchical exception structure
- Error categorization
- Context-aware error messages
- Error recovery hints
"""

from typing import Optional, Dict, Any, List
from enum import Enum


class ErrorCategory(Enum):
    """Error categories for classification"""
    COMMAND = "command"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    PLUGIN = "plugin"
    NETWORK = "network"
    DATABASE = "database"
    FILESYSTEM = "filesystem"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    SYSTEM = "system"


class CLIError(Exception):
    """Base exception class for all CLI errors"""
    
    def __init__(self, 
                 message: str,
                 category: ErrorCategory = ErrorCategory.SYSTEM,
                 exit_code: int = 1,
                 context: Optional[Dict[str, Any]] = None,
                 suggestions: Optional[List[str]] = None,
                 cause: Optional[Exception] = None):
        """Initialize CLI error
        
        Args:
            message: Error message
            category: Error category
            exit_code: Exit code for the error
            context: Additional context information
            suggestions: Suggested fixes or actions
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.category = category
        self.exit_code = exit_code
        self.context = context or {}
        self.suggestions = suggestions or []
        self.cause = cause
    
    def __str__(self) -> str:
        """String representation of the error"""
        parts = [f"[{self.category.value.upper()}] {self.message}"]
        
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")
        
        if self.suggestions:
            suggestions_str = "\n  - ".join(self.suggestions)
            parts.append(f"Suggestions:\n  - {suggestions_str}")
        
        if self.cause:
            parts.append(f"Caused by: {self.cause}")
        
        return "\n".join(parts)


class CommandError(CLIError):
    """Error in command execution"""
    
    def __init__(self, message: str, command_name: Optional[str] = None, **kwargs):
        super().__init__(message, category=ErrorCategory.COMMAND, **kwargs)
        if command_name:
            self.context['command'] = command_name


class CommandNotFoundError(CommandError):
    """Command not found error"""
    
    def __init__(self, command_name: str, available_commands: Optional[List[str]] = None):
        message = f"Command '{command_name}' not found"
        suggestions = []
        
        if available_commands:
            # Find similar commands
            similar = self._find_similar_commands(command_name, available_commands)
            if similar:
                suggestions.append(f"Did you mean: {', '.join(similar[:3])}?")
            
            suggestions.append(f"Use 'help' to see all available commands")
        
        super().__init__(
            message=message,
            command_name=command_name,
            suggestions=suggestions,
            exit_code=2
        )
    
    @staticmethod
    def _find_similar_commands(command: str, available: List[str]) -> List[str]:
        """Find similar command names using simple string distance"""
        def distance(s1: str, s2: str) -> int:
            # Simple Levenshtein distance calculation
            if len(s1) < len(s2):
                return distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        # Find commands with distance <= 2
        similar = []
        for cmd in available:
            if distance(command.lower(), cmd.lower()) <= 2:
                similar.append(cmd)
        
        return sorted(similar, key=lambda x: distance(command.lower(), x.lower()))


class ValidationError(CLIError):
    """Validation error"""
    
    def __init__(self, message: str, field: Optional[str] = None, 
                 value: Optional[Any] = None, **kwargs):
        super().__init__(message, category=ErrorCategory.VALIDATION, **kwargs)
        if field:
            self.context['field'] = field
        if value is not None:
            self.context['value'] = str(value)


class ConfigurationError(CLIError):
    """Configuration error"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, 
                 config_file: Optional[str] = None, **kwargs):
        super().__init__(message, category=ErrorCategory.CONFIGURATION, **kwargs)
        if config_key:
            self.context['config_key'] = config_key
        if config_file:
            self.context['config_file'] = config_file


class PluginError(CLIError):
    """Plugin-related error"""
    
    def __init__(self, message: str, plugin_name: Optional[str] = None, **kwargs):
        super().__init__(message, category=ErrorCategory.PLUGIN, **kwargs)
        if plugin_name:
            self.context['plugin'] = plugin_name


class NetworkError(CLIError):
    """Network-related error"""
    
    def __init__(self, message: str, url: Optional[str] = None, **kwargs):
        super().__init__(message, category=ErrorCategory.NETWORK, **kwargs)
        if url:
            self.context['url'] = url


class DatabaseError(CLIError):
    """Database-related error"""
    
    def __init__(self, message: str, query: Optional[str] = None, **kwargs):
        super().__init__(message, category=ErrorCategory.DATABASE, **kwargs)
        if query:
            self.context['query'] = query


class FileSystemError(CLIError):
    """Filesystem-related error"""
    
    def __init__(self, message: str, path: Optional[str] = None, **kwargs):
        super().__init__(message, category=ErrorCategory.FILESYSTEM, **kwargs)
        if path:
            self.context['path'] = path


class AuthenticationError(CLIError):
    """Authentication error"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        suggestions = [
            "Check your credentials",
            "Verify your API key or token",
            "Ensure you're logged in"
        ]
        super().__init__(
            message, 
            category=ErrorCategory.AUTHENTICATION,
            suggestions=suggestions,
            exit_code=401,
            **kwargs
        )


class AuthorizationError(CLIError):
    """Authorization error"""
    
    def __init__(self, message: str = "Access denied", resource: Optional[str] = None, **kwargs):
        suggestions = [
            "Check your permissions",
            "Contact an administrator",
            "Verify you have access to this resource"
        ]
        super().__init__(
            message,
            category=ErrorCategory.AUTHORIZATION,
            suggestions=suggestions,
            exit_code=403,
            **kwargs
        )
        if resource:
            self.context['resource'] = resource


class InterruptedError(CLIError):
    """Operation was interrupted"""
    
    def __init__(self, message: str = "Operation interrupted", **kwargs):
        super().__init__(message, exit_code=130, **kwargs)


class TimeoutError(CLIError):
    """Operation timed out"""
    
    def __init__(self, message: str = "Operation timed out", 
                 timeout_seconds: Optional[float] = None, **kwargs):
        super().__init__(message, **kwargs)
        if timeout_seconds:
            self.context['timeout'] = f"{timeout_seconds}s"


class DependencyError(CLIError):
    """Dependency-related error"""
    
    def __init__(self, message: str, dependency: Optional[str] = None, 
                 version_required: Optional[str] = None, **kwargs):
        suggestions = []
        if dependency:
            suggestions.append(f"Install {dependency}")
            if version_required:
                suggestions.append(f"Ensure version {version_required} or higher")
        
        super().__init__(message, suggestions=suggestions, **kwargs)
        
        if dependency:
            self.context['dependency'] = dependency
        if version_required:
            self.context['version_required'] = version_required


class ResourceNotFoundError(CLIError):
    """Resource not found error"""
    
    def __init__(self, message: str, resource_type: Optional[str] = None,
                 resource_id: Optional[str] = None, **kwargs):
        super().__init__(message, exit_code=404, **kwargs)
        if resource_type:
            self.context['resource_type'] = resource_type
        if resource_id:
            self.context['resource_id'] = resource_id


class ConflictError(CLIError):
    """Resource conflict error"""
    
    def __init__(self, message: str, **kwargs):
        suggestions = [
            "Use --force to override",
            "Choose a different name or identifier",
            "Update the existing resource instead"
        ]
        super().__init__(message, suggestions=suggestions, exit_code=409, **kwargs)


class RateLimitError(NetworkError):
    """Rate limit exceeded error"""
    
    def __init__(self, message: str = "Rate limit exceeded", 
                 retry_after: Optional[int] = None, **kwargs):
        suggestions = [
            "Wait before retrying",
            "Use a different API key if available",
            "Contact support to increase rate limits"
        ]
        
        if retry_after:
            suggestions.insert(0, f"Retry after {retry_after} seconds")
            kwargs.setdefault('context', {})['retry_after'] = retry_after
        
        super().__init__(message, suggestions=suggestions, exit_code=429, **kwargs)


def format_exception_for_user(error: Exception, debug: bool = False) -> str:
    """Format an exception for user-friendly display
    
    Args:
        error: Exception to format
        debug: Whether to include debug information
        
    Returns:
        Formatted error message
    """
    if isinstance(error, CLIError):
        return str(error)
    
    # Handle common built-in exceptions
    if isinstance(error, KeyboardInterrupt):
        return "Operation cancelled by user"
    elif isinstance(error, FileNotFoundError):
        return f"File not found: {error.filename or str(error)}"
    elif isinstance(error, PermissionError):
        return f"Permission denied: {error.filename or str(error)}"
    elif isinstance(error, ConnectionError):
        return f"Connection error: {str(error)}"
    elif isinstance(error, ImportError):
        return f"Missing dependency: {str(error)}"
    
    # Generic error formatting
    error_type = type(error).__name__
    error_message = str(error)
    
    if debug:
        import traceback
        return f"{error_type}: {error_message}\n\nTraceback:\n{traceback.format_exc()}"
    else:
        return f"{error_type}: {error_message}"


def handle_exception(error: Exception, debug: bool = False) -> int:
    """Handle an exception and return appropriate exit code
    
    Args:
        error: Exception to handle
        debug: Whether to show debug information
        
    Returns:
        Exit code
    """
    if isinstance(error, CLIError):
        return error.exit_code
    elif isinstance(error, KeyboardInterrupt):
        return 130  # Standard Unix exit code for SIGINT
    elif isinstance(error, (FileNotFoundError, PermissionError)):
        return 2
    elif isinstance(error, ImportError):
        return 127  # Command not found
    else:
        return 1  # Generic error
