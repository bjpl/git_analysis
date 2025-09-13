#!/usr/bin/env python3
"""
Unified Formatter - Centralized formatting solution for the CLI
This module provides a single, robust formatting interface that works across all platforms.
"""

import os
import sys
import shutil
from typing import Optional, List, Dict, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass
import re

# Platform detection
IS_WINDOWS = sys.platform == 'win32'

# Try to enable ANSI colors on Windows
if IS_WINDOWS:
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        pass

class Color(Enum):
    """ANSI color codes with fallback support"""
    # Basic colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Styles
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    
    @property
    def value(self):
        """Return color code or empty string if colors disabled"""
        if not UnifiedFormatter.colors_enabled:
            return ""
        return self._value_


@dataclass
class Theme:
    """Color theme configuration"""
    primary: Color = Color.BLUE
    secondary: Color = Color.CYAN
    success: Color = Color.GREEN
    warning: Color = Color.YELLOW
    error: Color = Color.RED
    info: Color = Color.BRIGHT_BLUE
    header: Color = Color.BRIGHT_CYAN
    accent: Color = Color.MAGENTA


class UnifiedFormatter:
    """
    Unified formatting class that provides all formatting methods.
    This is the single source of truth for all formatting in the application.
    """
    
    # Class-level configuration
    colors_enabled = True
    unicode_enabled = not IS_WINDOWS  # Disable unicode on Windows by default
    
    def __init__(self, theme: Optional[Theme] = None):
        """Initialize formatter with optional theme"""
        self.theme = theme or Theme()
        self.terminal_width = shutil.get_terminal_size((80, 24)).columns
        
    @classmethod
    def disable_colors(cls):
        """Disable all color output"""
        cls.colors_enabled = False
    
    @classmethod
    def enable_colors(cls):
        """Enable color output"""
        cls.colors_enabled = True
    
    @classmethod
    def set_unicode(cls, enabled: bool):
        """Enable or disable unicode characters"""
        cls.unicode_enabled = enabled
    
    def color(self, text: str, color: Color) -> str:
        """Apply color to text"""
        if not self.colors_enabled:
            return text
        return f"{color.value}{text}{Color.RESET.value}"
    
    def bold(self, text: str) -> str:
        """Make text bold"""
        return self.color(text, Color.BOLD)
    
    def success(self, text: str) -> str:
        """Format success message"""
        return self.color(text, self.theme.success)
    
    def error(self, text: str) -> str:
        """Format error message"""
        return self.color(text, self.theme.error)
    
    def warning(self, text: str) -> str:
        """Format warning message"""
        return self.color(text, self.theme.warning)
    
    def info(self, text: str) -> str:
        """Format info message"""
        return self.color(text, self.theme.info)
    
    def header(self, text: str, style: str = "default") -> str:
        """Format header text"""
        text = self.color(text, self.theme.header)
        if style == "box":
            return self.create_box(text)
        elif style == "banner":
            return self.create_banner(text)
        return self.bold(text)
    
    def create_box(self, content: Union[str, List[str]], 
                   title: Optional[str] = None,
                   width: Optional[int] = None) -> str:
        """Create a box around content"""
        if isinstance(content, str):
            content = content.split('\n')
        
        # Use safe box characters for Windows
        if IS_WINDOWS or not self.unicode_enabled:
            h_line = '-'
            v_line = '|'
            tl_corner = '+'
            tr_corner = '+'
            bl_corner = '+'
            br_corner = '+'
        else:
            h_line = '─'
            v_line = '│'
            tl_corner = '┌'
            tr_corner = '┐'
            bl_corner = '└'
            br_corner = '┘'
        
        # Calculate box width
        max_content_width = max(len(self.strip_ansi(line)) for line in content) if content else 0
        if title:
            max_content_width = max(max_content_width, len(title) + 4)
        
        box_width = width or min(max_content_width + 4, self.terminal_width - 2)
        inner_width = box_width - 2
        
        # Build box
        lines = []
        
        # Top border
        if title:
            title_line = f" {title} "
            padding = box_width - len(title_line) - 2
            left_pad = padding // 2
            right_pad = padding - left_pad
            lines.append(f"{tl_corner}{h_line * left_pad}{title_line}{h_line * right_pad}{tr_corner}")
        else:
            lines.append(f"{tl_corner}{h_line * (box_width - 2)}{tr_corner}")
        
        # Content
        for line in content:
            clean_line = self.strip_ansi(line)
            padding = inner_width - len(clean_line)
            lines.append(f"{v_line} {line}{' ' * padding} {v_line}")
        
        # Bottom border
        lines.append(f"{bl_corner}{h_line * (box_width - 2)}{br_corner}")
        
        return '\n'.join(lines)
    
    def create_banner(self, text: str, char: str = "=") -> str:
        """Create a banner with text"""
        width = min(self.terminal_width, 80)
        padding = (width - len(text) - 2) // 2
        banner = f"{char * width}\n"
        banner += f"{char}{' ' * padding}{text}{' ' * (width - padding - len(text) - 2)}{char}\n"
        banner += char * width
        return banner
    
    def create_table(self, headers: List[str], rows: List[List[str]], 
                    show_index: bool = False) -> str:
        """Create a formatted table"""
        if show_index:
            headers = ['#'] + headers
            rows = [[str(i+1)] + row for i, row in enumerate(rows)]
        
        # Calculate column widths
        col_widths = []
        for i in range(len(headers)):
            max_width = len(headers[i])
            for row in rows:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))
            col_widths.append(max_width)
        
        # Use safe table characters
        if IS_WINDOWS or not self.unicode_enabled:
            h_sep = '-'
            v_sep = '|'
            cross = '+'
        else:
            h_sep = '─'
            v_sep = '│'
            cross = '┼'
        
        # Build table
        lines = []
        
        # Header
        header_line = v_sep
        for i, header in enumerate(headers):
            header_line += f" {header:<{col_widths[i]}} {v_sep}"
        lines.append(header_line)
        
        # Separator
        sep_line = cross
        for width in col_widths:
            sep_line += h_sep * (width + 2) + cross
        lines.append(sep_line)
        
        # Rows
        for row in rows:
            row_line = v_sep
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    row_line += f" {str(cell):<{col_widths[i]}} {v_sep}"
            lines.append(row_line)
        
        return '\n'.join(lines)
    
    def progress_bar(self, current: int, total: int, 
                    width: int = 40, show_percentage: bool = True) -> str:
        """Create a progress bar"""
        if total == 0:
            progress = 0
        else:
            progress = min(1.0, current / total)
        
        filled = int(width * progress)
        empty = width - filled
        
        # Use safe characters
        if IS_WINDOWS or not self.unicode_enabled:
            bar = f"[{'#' * filled}{'-' * empty}]"
        else:
            bar = f"[{'█' * filled}{'░' * empty}]"
        
        if show_percentage:
            bar += f" {progress*100:.1f}%"
        
        return bar
    
    def format_list(self, items: List[str], style: str = "bullet") -> str:
        """Format a list of items"""
        if style == "bullet":
            marker = "•" if self.unicode_enabled else "*"
        elif style == "number":
            return '\n'.join(f"{i+1}. {item}" for i, item in enumerate(items))
        elif style == "arrow":
            marker = "→" if self.unicode_enabled else "->"
        else:
            marker = "-"
        
        return '\n'.join(f"  {marker} {item}" for item in items)
    
    def wrap_text(self, text: str, width: Optional[int] = None, 
                 indent: int = 0) -> str:
        """Wrap text to specified width"""
        width = width or self.terminal_width - indent - 2
        
        lines = []
        for paragraph in text.split('\n'):
            if not paragraph:
                lines.append('')
                continue
                
            words = paragraph.split()
            current_line = []
            current_length = 0
            
            for word in words:
                word_length = len(self.strip_ansi(word))
                if current_length + word_length + len(current_line) > width:
                    if current_line:
                        lines.append(' ' * indent + ' '.join(current_line))
                        current_line = [word]
                        current_length = word_length
                    else:
                        # Word is too long, add it anyway
                        lines.append(' ' * indent + word)
                        current_line = []
                        current_length = 0
                else:
                    current_line.append(word)
                    current_length += word_length
            
            if current_line:
                lines.append(' ' * indent + ' '.join(current_line))
        
        return '\n'.join(lines)
    
    def strip_ansi(self, text: str) -> str:
        """Remove ANSI escape codes from text"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def clear_screen(self):
        """Clear the terminal screen"""
        if IS_WINDOWS:
            os.system('cls')
        else:
            os.system('clear')
    
    def print_formatted(self, text: str, end: str = '\n'):
        """Print formatted text with proper encoding"""
        try:
            print(text, end=end)
        except UnicodeEncodeError:
            # Fallback for terminals that don't support unicode
            safe_text = text.encode('ascii', 'replace').decode('ascii')
            print(safe_text, end=end)


# Create a global instance for easy access
formatter = UnifiedFormatter()

# Convenience functions that use the global formatter
def success(text: str) -> str:
    """Format success message"""
    return formatter.success(text)

def error(text: str) -> str:
    """Format error message"""
    return formatter.error(text)

def warning(text: str) -> str:
    """Format warning message"""
    return formatter.warning(text)

def info(text: str) -> str:
    """Format info message"""
    return formatter.info(text)

def header(text: str, style: str = "default") -> str:
    """Format header"""
    return formatter.header(text, style)

def create_box(content: Union[str, List[str]], title: Optional[str] = None) -> str:
    """Create a box around content"""
    return formatter.create_box(content, title)

def progress_bar(current: int, total: int) -> str:
    """Create a progress bar"""
    return formatter.progress_bar(current, total)

def clear_screen():
    """Clear the terminal screen"""
    formatter.clear_screen()


# For backward compatibility, provide Formatter class alias
class Formatter:
    """Backward compatibility alias for UnifiedFormatter"""
    def __init__(self, *args, **kwargs):
        self._formatter = UnifiedFormatter(*args, **kwargs)
    
    def __getattr__(self, name):
        return getattr(self._formatter, name)


# Also provide TerminalFormatter for compatibility
TerminalFormatter = UnifiedFormatter