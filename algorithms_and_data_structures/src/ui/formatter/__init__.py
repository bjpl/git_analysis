"""
Enhanced Terminal Formatter Package
Windows PowerShell compatible terminal formatting with rich features
"""

# Import enhanced formatter components
from .enhanced_formatter import (
    # Main classes
    EnhancedFormatter,
    Spinner,
    
    # Enums and data classes
    Color,
    HeaderStyle,
    TableStyle,
    BoxChars,
    TerminalCapabilities,
    
    # Quick functions
    quick_header,
    quick_table,
    quick_panel,
    quick_progress,
    get_formatter,
)

# Import legacy formatter for backward compatibility
import sys
import os
legacy_formatter_path = os.path.join(os.path.dirname(__file__), '..', 'formatter.py')
if os.path.exists(legacy_formatter_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("legacy_formatter", legacy_formatter_path)
    legacy_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy_module)
    TerminalFormatter = legacy_module.TerminalFormatter
    Theme = legacy_module.Theme
else:
    # Fallback if legacy formatter not found
    class TerminalFormatter:
        def __init__(self, *args, **kwargs):
            pass
    class Theme:
        def __init__(self, *args, **kwargs):
            pass

# Version and metadata
__version__ = '2.0.0'
__author__ = 'Enhanced Terminal Formatter'
__description__ = 'Windows-safe terminal formatting with rich visual features'

# Default formatter instance
default_formatter = None


def get_default_formatter() -> EnhancedFormatter:
    """Get or create the default formatter instance"""
    global default_formatter
    if default_formatter is None:
        default_formatter = EnhancedFormatter()
    return default_formatter


# Convenience functions using default formatter
def header(title: str, style: str = "banner", color: str = "bright_cyan") -> str:
    """Create header using default formatter"""
    return get_default_formatter().create_header(
        title, 
        HeaderStyle(style) if isinstance(style, str) else style,
        color=Color[color.upper()] if isinstance(color, str) else color
    )


def table(data: list, headers: list = None, style: str = "grid") -> str:
    """Create table using default formatter"""
    return get_default_formatter().create_table(
        data, 
        headers, 
        TableStyle(style) if isinstance(style, str) else style
    )


def panel(title: str, content: str, color: str = "bright_blue") -> str:
    """Create panel using default formatter"""
    return get_default_formatter().create_panel(
        title, 
        content, 
        color=Color[color.upper()] if isinstance(color, str) else color
    )


def progress_bar(progress: float, width: int = 50) -> str:
    """Create progress bar using default formatter"""
    return get_default_formatter().create_progress_bar(progress, width)


def colorize(text: str, color: str, bg_color: str = None, style: str = None) -> str:
    """Colorize text using default formatter"""
    return get_default_formatter().colorize(
        text,
        Color[color.upper()] if isinstance(color, str) else color,
        Color[f'BG_{bg_color.upper()}'] if bg_color else None,
        Color[style.upper()] if style else None
    )


def spinner(message: str = "", style: str = "simple"):
    """Create spinner using default formatter"""
    return get_default_formatter().create_spinner(message, style)


# Export all symbols
__all__ = [
    # Main classes
    'EnhancedFormatter',
    'Spinner',
    'TerminalFormatter',  # Legacy compatibility
    'Theme',             # Legacy compatibility
    
    # Enums and data classes
    'Color',
    'HeaderStyle', 
    'TableStyle',
    'BoxChars',
    'TerminalCapabilities',
    
    # Quick functions
    'quick_header',
    'quick_table',
    'quick_panel',
    'quick_progress',
    'get_formatter',
    'get_default_formatter',
    
    # Convenience functions
    'header',
    'table',
    'panel',
    'progress_bar',
    'colorize',
    'spinner',
    
    # Metadata
    '__version__',
    '__author__',
    '__description__'
]