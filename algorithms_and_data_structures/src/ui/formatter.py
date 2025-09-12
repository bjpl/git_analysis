#!/usr/bin/env python3
"""
Terminal Formatter - Beautiful terminal formatting with colors

This module provides:
- Rich text formatting and colors
- Progress indicators and animations
- Table and list formatting
- Cross-platform terminal support
- Theme system
"""

import sys
import os
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from dataclasses import dataclass
import shutil
import time
import threading


class Color(Enum):
    """ANSI color codes"""
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
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # Reset
    RESET = "\033[0m"
    
    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    STRIKETHROUGH = "\033[9m"


@dataclass
class Theme:
    """Terminal theme configuration"""
    primary: Color = Color.BLUE
    secondary: Color = Color.CYAN
    success: Color = Color.GREEN
    warning: Color = Color.YELLOW
    error: Color = Color.RED
    info: Color = Color.BRIGHT_BLUE
    muted: Color = Color.BRIGHT_BLACK
    text: Color = Color.WHITE
    

class TerminalFormatter:
    """Terminal formatter with colors and styling"""
    
    def __init__(self, theme: Optional[Theme] = None, color_enabled: Optional[bool] = None):
        """Initialize terminal formatter
        
        Args:
            theme: Color theme to use
            color_enabled: Override color support detection
        """
        self.theme = theme or Theme()
        self._color_enabled = color_enabled
        self.width = self._get_terminal_width()
        
        # Animation state
        self._spinner_active = False
        self._spinner_thread: Optional[threading.Thread] = None
        
        # Progress bar state
        self._progress_bars: Dict[str, Dict[str, Any]] = {}
    
    @property
    def color_enabled(self) -> bool:
        """Check if color output is enabled"""
        if self._color_enabled is not None:
            return self._color_enabled
        
        # Auto-detect color support
        if not sys.stdout.isatty():
            return False
        
        # Check environment variables
        if os.environ.get('NO_COLOR'):
            return False
        
        if os.environ.get('FORCE_COLOR'):
            return True
        
        # Check terminal capabilities
        term = os.environ.get('TERM', '')
        if 'color' in term or term in ['xterm', 'xterm-256color', 'screen']:
            return True
        
        # Windows color support
        if sys.platform == 'win32':
            try:
                import colorama
                colorama.init()
                return True
            except ImportError:
                return False
        
        return True
    
    def disable_color(self):
        """Disable color output"""
        self._color_enabled = False
    
    def enable_color(self):
        """Enable color output"""
        self._color_enabled = True
    
    def _get_terminal_width(self) -> int:
        """Get terminal width
        
        Returns:
            Terminal width in characters
        """
        try:
            return shutil.get_terminal_size().columns
        except (AttributeError, OSError):
            return 80
    
    def _colorize(self, text: str, color: Color, style: Optional[Color] = None) -> str:
        """Apply color and style to text
        
        Args:
            text: Text to colorize
            color: Color to apply
            style: Optional style to apply
            
        Returns:
            Colored text or plain text if colors disabled
        """
        if not self.color_enabled:
            return text
        
        result = color.value
        if style:
            result += style.value
        result += text + Color.RESET.value
        
        return result
    
    def success(self, message: str, icon: str = "✅") -> str:
        """Format success message
        
        Args:
            message: Success message
            icon: Success icon
            
        Returns:
            Formatted success message
        """
        formatted = f"{icon} {message}"
        colored = self._colorize(formatted, self.theme.success, Color.BOLD)
        print(colored)
        return colored
    
    def error(self, message: str, icon: str = "❌") -> str:
        """Format error message
        
        Args:
            message: Error message
            icon: Error icon
            
        Returns:
            Formatted error message
        """
        formatted = f"{icon} {message}"
        colored = self._colorize(formatted, self.theme.error, Color.BOLD)
        print(colored, file=sys.stderr)
        return colored
    
    def warning(self, message: str, icon: str = "⚠️") -> str:
        """Format warning message
        
        Args:
            message: Warning message
            icon: Warning icon
            
        Returns:
            Formatted warning message
        """
        formatted = f"{icon} {message}"
        colored = self._colorize(formatted, self.theme.warning, Color.BOLD)
        print(colored)
        return colored
    
    def info(self, message: str, icon: str = "ℹ️") -> str:
        """Format info message
        
        Args:
            message: Info message
            icon: Info icon
            
        Returns:
            Formatted info message
        """
        formatted = f"{icon} {message}"
        colored = self._colorize(formatted, self.theme.info)
        print(colored)
        return colored
    
    def debug(self, message: str, icon: str = "🔍") -> str:
        """Format debug message
        
        Args:
            message: Debug message
            icon: Debug icon
            
        Returns:
            Formatted debug message
        """
        formatted = f"{icon} {message}"
        colored = self._colorize(formatted, self.theme.muted)
        print(colored)
        return colored
    
    def header(self, title: str, level: int = 1) -> str:
        """Format header text
        
        Args:
            title: Header title
            level: Header level (1-3)
            
        Returns:
            Formatted header
        """
        if level == 1:
            # Large header with border
            border = "═" * min(len(title) + 4, self.width)
            formatted = f"\n{border}\n  {title.upper()}  \n{border}\n"
            colored = self._colorize(formatted, self.theme.primary, Color.BOLD)
        elif level == 2:
            # Medium header with underline
            underline = "─" * len(title)
            formatted = f"\n{title}\n{underline}\n"
            colored = self._colorize(formatted, self.theme.secondary, Color.BOLD)
        else:
            # Small header
            formatted = f"\n▶ {title}\n"
            colored = self._colorize(formatted, self.theme.text, Color.BOLD)
        
        print(colored)
        return colored
    
    def table(self, data: List[Dict[str, Any]], headers: Optional[List[str]] = None) -> str:
        """Format data as a table
        
        Args:
            data: List of data dictionaries
            headers: Optional list of headers (uses data keys if None)
            
        Returns:
            Formatted table string
        """
        if not data:
            return self._colorize("No data to display", self.theme.muted)
        
        if headers is None:
            headers = list(data[0].keys())
        
        # Calculate column widths
        widths = {}
        for header in headers:
            widths[header] = len(str(header))
        
        for row in data:
            for header in headers:
                value = str(row.get(header, ''))
                widths[header] = max(widths[header], len(value))
        
        lines = []
        
        # Header row
        header_parts = []
        for header in headers:
            header_text = str(header).ljust(widths[header])
            header_parts.append(self._colorize(header_text, self.theme.primary, Color.BOLD))
        
        lines.append(" │ ".join(header_parts))
        
        # Separator
        sep_parts = ["─" * widths[header] for header in headers]
        separator = "─┼─".join(sep_parts)
        lines.append(self._colorize(separator, self.theme.muted))
        
        # Data rows
        for i, row in enumerate(data):
            row_parts = []
            for header in headers:
                value = str(row.get(header, ''))
                cell_text = value.ljust(widths[header])
                
                # Alternate row colors
                color = self.theme.text if i % 2 == 0 else self.theme.muted
                row_parts.append(self._colorize(cell_text, color))
            
            lines.append(" │ ".join(row_parts))
        
        table_str = "\n".join(lines)
        print(table_str)
        return table_str
    
    def list_items(self, items: List[str], bullet: str = "•") -> str:
        """Format list of items
        
        Args:
            items: List of items
            bullet: Bullet character
            
        Returns:
            Formatted list string
        """
        lines = []
        for item in items:
            bullet_colored = self._colorize(bullet, self.theme.primary)
            item_colored = self._colorize(str(item), self.theme.text)
            lines.append(f"  {bullet_colored} {item_colored}")
        
        list_str = "\n".join(lines)
        print(list_str)
        return list_str
    
    def key_value_pairs(self, pairs: Dict[str, Any], indent: int = 0) -> str:
        """Format key-value pairs
        
        Args:
            pairs: Dictionary of key-value pairs
            indent: Indentation level
            
        Returns:
            Formatted key-value string
        """
        lines = []
        prefix = "  " * indent
        
        for key, value in pairs.items():
            key_colored = self._colorize(f"{key}:", self.theme.secondary, Color.BOLD)
            value_colored = self._colorize(str(value), self.theme.text)
            lines.append(f"{prefix}{key_colored} {value_colored}")
        
        kv_str = "\n".join(lines)
        print(kv_str)
        return kv_str
    
    def spinner(self, message: str, spinner_chars: str = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏") -> 'SpinnerContext':
        """Create a spinner context manager
        
        Args:
            message: Message to display with spinner
            spinner_chars: Characters for spinner animation
            
        Returns:
            Spinner context manager
        """
        return SpinnerContext(self, message, spinner_chars)
    
    def progress_bar(self, total: int, description: str = "", 
                    bar_id: Optional[str] = None) -> 'ProgressBar':
        """Create a progress bar
        
        Args:
            total: Total number of items
            description: Progress description
            bar_id: Unique ID for the progress bar
            
        Returns:
            Progress bar instance
        """
        if bar_id is None:
            bar_id = f"progress_{len(self._progress_bars)}"
        
        progress_bar = ProgressBar(self, total, description, bar_id)
        self._progress_bars[bar_id] = {
            'bar': progress_bar,
            'current': 0,
            'total': total,
            'description': description
        }
        
        return progress_bar
    
    def box(self, content: str, title: Optional[str] = None, 
           style: str = "single") -> str:
        """Draw a box around content
        
        Args:
            content: Content to box
            title: Optional box title
            style: Box style ('single', 'double', 'rounded')
            
        Returns:
            Boxed content string
        """
        lines = content.split('\n')
        max_width = max(len(line) for line in lines) if lines else 0
        
        if title:
            max_width = max(max_width, len(title) + 2)
        
        # Box characters by style
        if style == "double":
            chars = {'tl': '╔', 'tr': '╗', 'bl': '╚', 'br': '╝', 
                    'h': '═', 'v': '║'}
        elif style == "rounded":
            chars = {'tl': '╭', 'tr': '╮', 'bl': '╰', 'br': '╯', 
                    'h': '─', 'v': '│'}
        else:  # single
            chars = {'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘', 
                    'h': '─', 'v': '│'}
        
        # Build box
        box_lines = []
        
        # Top border
        if title:
            title_len = len(title)
            padding = (max_width - title_len) // 2
            remaining = max_width - title_len - padding
            
            top_line = (chars['tl'] + chars['h'] * padding + 
                       title + chars['h'] * remaining + chars['tr'])
            box_lines.append(self._colorize(top_line, self.theme.primary))
        else:
            top_line = chars['tl'] + chars['h'] * max_width + chars['tr']
            box_lines.append(self._colorize(top_line, self.theme.primary))
        
        # Content lines
        for line in lines:
            padded_line = line.ljust(max_width)
            border_left = self._colorize(chars['v'], self.theme.primary)
            border_right = self._colorize(chars['v'], self.theme.primary)
            content_line = f"{border_left}{padded_line}{border_right}"
            box_lines.append(content_line)
        
        # Bottom border
        bottom_line = chars['bl'] + chars['h'] * max_width + chars['br']
        box_lines.append(self._colorize(bottom_line, self.theme.primary))
        
        boxed_str = "\n".join(box_lines)
        print(boxed_str)
        return boxed_str
    
    def rule(self, title: Optional[str] = None, char: str = "─") -> str:
        """Draw a horizontal rule
        
        Args:
            title: Optional title in the middle of the rule
            char: Character to use for the rule
            
        Returns:
            Formatted rule string
        """
        if title:
            title_len = len(title)
            padding = (self.width - title_len - 2) // 2
            remaining = self.width - title_len - 2 - padding
            
            rule_line = (char * padding + f" {title} " + char * remaining)
        else:
            rule_line = char * self.width
        
        colored_rule = self._colorize(rule_line, self.theme.muted)
        print(colored_rule)
        return colored_rule


class SpinnerContext:
    """Context manager for spinner animation"""
    
    def __init__(self, formatter: TerminalFormatter, message: str, 
                 spinner_chars: str):
        self.formatter = formatter
        self.message = message
        self.spinner_chars = spinner_chars
        self.active = False
        self.thread: Optional[threading.Thread] = None
    
    def __enter__(self):
        if not self.formatter.color_enabled:
            self.formatter.info(self.message)
            return self
        
        self.active = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.active = False
        if self.thread:
            self.thread.join(timeout=0.1)
        
        # Clear the line
        if self.formatter.color_enabled:
            print("\r" + " " * (len(self.message) + 10) + "\r", end="")
    
    def _animate(self):
        """Animate the spinner"""
        i = 0
        while self.active:
            char = self.spinner_chars[i % len(self.spinner_chars)]
            spinner_colored = self.formatter._colorize(
                char, self.formatter.theme.primary
            )
            message_colored = self.formatter._colorize(
                self.message, self.formatter.theme.text
            )
            
            print(f"\r{spinner_colored} {message_colored}", end="", flush=True)
            time.sleep(0.1)
            i += 1


class ProgressBar:
    """Progress bar for long-running operations"""
    
    def __init__(self, formatter: TerminalFormatter, total: int, 
                 description: str, bar_id: str):
        self.formatter = formatter
        self.total = total
        self.description = description
        self.bar_id = bar_id
        self.current = 0
        self.bar_length = 40
    
    def update(self, amount: int = 1):
        """Update progress bar
        
        Args:
            amount: Amount to increment progress
        """
        self.current = min(self.current + amount, self.total)
        self._render()
    
    def set_progress(self, current: int):
        """Set absolute progress
        
        Args:
            current: Current progress value
        """
        self.current = min(max(current, 0), self.total)
        self._render()
    
    def _render(self):
        """Render the progress bar"""
        if not self.formatter.color_enabled:
            # Simple text progress for non-color terminals
            percent = (self.current / self.total) * 100
            print(f"\r{self.description}: {self.current}/{self.total} ({percent:.1f}%)", 
                  end="", flush=True)
            return
        
        # Calculate progress
        percent = self.current / self.total if self.total > 0 else 0
        filled_length = int(self.bar_length * percent)
        
        # Create progress bar
        bar = "█" * filled_length + "░" * (self.bar_length - filled_length)
        bar_colored = (self.formatter._colorize("█" * filled_length, 
                                               self.formatter.theme.success) +
                      self.formatter._colorize("░" * (self.bar_length - filled_length), 
                                              self.formatter.theme.muted))
        
        # Format percentage
        percent_str = f"{percent * 100:6.1f}%"
        percent_colored = self.formatter._colorize(percent_str, 
                                                  self.formatter.theme.text, 
                                                  Color.BOLD)
        
        # Format progress text
        progress_text = f"{self.current}/{self.total}"
        progress_colored = self.formatter._colorize(progress_text, 
                                                   self.formatter.theme.muted)
        
        # Description
        desc_colored = self.formatter._colorize(self.description, 
                                               self.formatter.theme.text)
        
        # Complete line
        line = f"\r{desc_colored} [{bar_colored}] {percent_colored} {progress_colored}"
        print(line, end="", flush=True)
        
        # Print newline when complete
        if self.current >= self.total:
            print()
    
    def finish(self):
        """Mark progress bar as finished"""
        self.current = self.total
        self._render()
        
        # Remove from formatter's tracking
        if self.bar_id in self.formatter._progress_bars:
            del self.formatter._progress_bars[self.bar_id]
