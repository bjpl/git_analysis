"""
Enhanced Terminal Formatter Module
Windows-safe terminal formatting with rich visual features
"""

import os
import sys
import time
import threading
from typing import Dict, List, Optional, Union, Tuple, Any
from enum import Enum
from dataclasses import dataclass
import re


class Color(Enum):
    """ANSI color codes with Windows PowerShell compatibility"""
    # Standard colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Styles
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    STRIKETHROUGH = '\033[9m'


class BoxChars:
    """Windows-safe ASCII box drawing characters"""
    # Simple box chars (always safe)
    HORIZONTAL = '-'
    VERTICAL = '|'
    TOP_LEFT = '+'
    TOP_RIGHT = '+'
    BOTTOM_LEFT = '+'
    BOTTOM_RIGHT = '+'
    CROSS = '+'
    T_UP = '+'
    T_DOWN = '+'
    T_LEFT = '+'
    T_RIGHT = '+'
    
    # Double line chars using equals
    DOUBLE_HORIZONTAL = '='
    DOUBLE_VERTICAL = '||'
    
    @classmethod
    def get_safe_chars(cls) -> Dict[str, str]:
        """Get dictionary of safe box drawing characters"""
        return {
            'horizontal': cls.HORIZONTAL,
            'vertical': cls.VERTICAL,
            'top_left': cls.TOP_LEFT,
            'top_right': cls.TOP_RIGHT,
            'bottom_left': cls.BOTTOM_LEFT,
            'bottom_right': cls.BOTTOM_RIGHT,
            'cross': cls.CROSS,
            't_up': cls.T_UP,
            't_down': cls.T_DOWN,
            't_left': cls.T_LEFT,
            't_right': cls.T_RIGHT,
            'double_horizontal': cls.DOUBLE_HORIZONTAL,
            'double_vertical': cls.DOUBLE_VERTICAL
        }


@dataclass
class TerminalCapabilities:
    """Terminal capability detection"""
    supports_color: bool = False
    supports_256_color: bool = False
    supports_true_color: bool = False
    width: int = 80
    height: int = 24
    is_powershell: bool = False
    is_windows: bool = False


class HeaderStyle(Enum):
    """Header display styles"""
    BANNER = "banner"
    CENTERED = "centered"
    BOXED = "boxed"
    UNDERLINED = "underlined"
    GRADIENT = "gradient"


class TableStyle(Enum):
    """Table formatting styles"""
    SIMPLE = "simple"
    GRID = "grid"
    FANCY_GRID = "fancy_grid"
    MINIMAL = "minimal"


class EnhancedFormatter:
    """Enhanced terminal formatter with Windows PowerShell compatibility"""
    
    def __init__(self):
        self.capabilities = self._detect_capabilities()
        self.box_chars = BoxChars.get_safe_chars()
        self._spinner_active = False
        self._spinner_thread = None
        
    def _detect_capabilities(self) -> TerminalCapabilities:
        """Detect terminal capabilities"""
        caps = TerminalCapabilities()
        
        # Detect Windows
        caps.is_windows = os.name == 'nt'
        
        # Detect PowerShell
        caps.is_powershell = (
            caps.is_windows and 
            'POWERSHELL' in os.environ.get('PSModulePath', '').upper()
        ) or 'pwsh' in sys.argv[0].lower()
        
        # Terminal size
        try:
            size = os.get_terminal_size()
            caps.width = size.columns
            caps.height = size.lines
        except (OSError, AttributeError):
            caps.width = 80
            caps.height = 24
        
        # Color support detection
        if caps.is_windows:
            # Windows 10+ supports ANSI colors
            caps.supports_color = True
            caps.supports_256_color = False  # Conservative for PowerShell
            caps.supports_true_color = False
        else:
            # Unix-like systems
            term = os.environ.get('TERM', '')
            colorterm = os.environ.get('COLORTERM', '')
            
            caps.supports_color = (
                term not in ('', 'dumb') and
                hasattr(sys.stdout, 'isatty') and
                sys.stdout.isatty()
            )
            
            caps.supports_256_color = (
                caps.supports_color and
                ('256' in term or 'color' in term)
            )
            
            caps.supports_true_color = (
                caps.supports_256_color and
                colorterm in ('truecolor', '24bit')
            )
        
        return caps
    
    def colorize(self, text: str, color: Union[Color, str], 
                 bg_color: Optional[Union[Color, str]] = None,
                 style: Optional[Union[Color, str]] = None) -> str:
        """Apply color and style to text with fallback"""
        if not self.capabilities.supports_color:
            return text
        
        # Convert string colors to Color enum
        if isinstance(color, str):
            try:
                color = Color[color.upper()]
            except KeyError:
                return text
        
        result = color.value + text
        
        if bg_color:
            if isinstance(bg_color, str):
                try:
                    bg_color = Color[f'BG_{bg_color.upper()}']
                    result = bg_color.value + result
                except KeyError:
                    pass
        
        if style:
            if isinstance(style, str):
                try:
                    style = Color[style.upper()]
                    result = style.value + result
                except KeyError:
                    pass
        
        result += Color.RESET.value
        return result
    
    def gradient_text(self, text: str, colors: List[Color], 
                     horizontal: bool = True) -> str:
        """Create gradient text effect"""
        if not self.capabilities.supports_color or len(colors) < 2:
            return text
        
        if not text.strip():
            return text
        
        result = ""
        text_len = len(text)
        color_count = len(colors)
        
        if horizontal:
            # Horizontal gradient
            for i, char in enumerate(text):
                # Calculate which color segment this character falls into
                progress = i / max(1, text_len - 1)
                color_index = min(int(progress * (color_count - 1)), color_count - 2)
                
                color = colors[color_index]
                result += self.colorize(char, color)
        else:
            # For vertical gradient, just use the first color
            result = self.colorize(text, colors[0])
        
        return result
    
    def create_header(self, title: str, style: HeaderStyle = HeaderStyle.BANNER,
                     width: Optional[int] = None, color: Color = Color.BRIGHT_CYAN) -> str:
        """Create professional headers with multiple styles"""
        if width is None:
            width = min(self.capabilities.width, 80)
        
        title = title.strip()
        
        if style == HeaderStyle.BANNER:
            return self._create_banner_header(title, width, color)
        elif style == HeaderStyle.CENTERED:
            return self._create_centered_header(title, width, color)
        elif style == HeaderStyle.BOXED:
            return self._create_boxed_header(title, width, color)
        elif style == HeaderStyle.UNDERLINED:
            return self._create_underlined_header(title, width, color)
        elif style == HeaderStyle.GRADIENT:
            return self._create_gradient_header(title, width)
        else:
            return title
    
    def _create_banner_header(self, title: str, width: int, color: Color) -> str:
        """Create banner-style header"""
        lines = []
        
        # Top border
        top_line = self.box_chars['double_horizontal'] * width
        lines.append(self.colorize(top_line, color))
        
        # Title line
        padding = (width - len(title) - 2) // 2
        title_line = (
            self.box_chars['double_vertical'] +
            ' ' * padding +
            title +
            ' ' * (width - len(title) - padding - 2) +
            self.box_chars['double_vertical']
        )
        lines.append(self.colorize(title_line, color, style=Color.BOLD))
        
        # Bottom border
        bottom_line = self.box_chars['double_horizontal'] * width
        lines.append(self.colorize(bottom_line, color))
        
        return '\n'.join(lines)
    
    def _create_centered_header(self, title: str, width: int, color: Color) -> str:
        """Create centered header"""
        padding = (width - len(title)) // 2
        centered = ' ' * padding + title
        return self.colorize(centered, color, style=Color.BOLD)
    
    def _create_boxed_header(self, title: str, width: int, color: Color) -> str:
        """Create boxed header"""
        lines = []
        box_width = min(len(title) + 4, width)
        
        # Top border
        top = (
            self.box_chars['top_left'] +
            self.box_chars['horizontal'] * (box_width - 2) +
            self.box_chars['top_right']
        )
        lines.append(self.colorize(top, color))
        
        # Title line
        title_padding = (box_width - len(title) - 2) // 2
        title_line = (
            self.box_chars['vertical'] +
            ' ' * title_padding +
            title +
            ' ' * (box_width - len(title) - title_padding - 2) +
            self.box_chars['vertical']
        )
        lines.append(self.colorize(title_line, color, style=Color.BOLD))
        
        # Bottom border
        bottom = (
            self.box_chars['bottom_left'] +
            self.box_chars['horizontal'] * (box_width - 2) +
            self.box_chars['bottom_right']
        )
        lines.append(self.colorize(bottom, color))
        
        return '\n'.join(lines)
    
    def _create_underlined_header(self, title: str, width: int, color: Color) -> str:
        """Create underlined header"""
        lines = []
        lines.append(self.colorize(title, color, style=Color.BOLD))
        underline = self.box_chars['horizontal'] * len(title)
        lines.append(self.colorize(underline, color))
        return '\n'.join(lines)
    
    def _create_gradient_header(self, title: str, width: int) -> str:
        """Create gradient header"""
        gradient_colors = [
            Color.BRIGHT_BLUE,
            Color.BRIGHT_CYAN,
            Color.BRIGHT_GREEN,
            Color.BRIGHT_YELLOW,
            Color.BRIGHT_RED,
            Color.BRIGHT_MAGENTA
        ]
        return self.gradient_text(title, gradient_colors)
    
    def create_progress_bar(self, progress: float, width: int = 50,
                           color: Color = Color.BRIGHT_GREEN,
                           bg_color: Color = Color.BRIGHT_BLACK,
                           show_percentage: bool = True) -> str:
        """Create PowerShell-optimized progress bar"""
        progress = max(0.0, min(1.0, progress))
        filled_width = int(progress * width)
        
        # Use simple characters for better PowerShell compatibility
        filled_char = '#'
        empty_char = '-'
        
        filled = filled_char * filled_width
        empty = empty_char * (width - filled_width)
        
        bar = (
            '[' +
            self.colorize(filled, color) +
            self.colorize(empty, bg_color) +
            ']'
        )
        
        if show_percentage:
            percentage = f' {progress:.1%}'
            bar += self.colorize(percentage, Color.BRIGHT_WHITE)
        
        return bar
    
    def create_spinner(self, message: str = "", style: str = "dots") -> 'Spinner':
        """Create animated spinner optimized for PowerShell"""
        return Spinner(self, message, style)
    
    def create_table(self, data: List[List[str]], headers: Optional[List[str]] = None,
                    style: TableStyle = TableStyle.GRID,
                    alternating_colors: bool = True) -> str:
        """Create formatted table with alternating row colors"""
        if not data:
            return ""
        
        # Calculate column widths
        all_rows = [headers] + data if headers else data
        col_widths = []
        for col_idx in range(len(all_rows[0])):
            max_width = max(len(str(row[col_idx])) for row in all_rows if col_idx < len(row))
            col_widths.append(max_width)
        
        lines = []
        
        if style == TableStyle.GRID:
            lines.extend(self._create_grid_table(data, headers, col_widths, alternating_colors))
        elif style == TableStyle.SIMPLE:
            lines.extend(self._create_simple_table(data, headers, col_widths, alternating_colors))
        elif style == TableStyle.FANCY_GRID:
            lines.extend(self._create_fancy_grid_table(data, headers, col_widths, alternating_colors))
        elif style == TableStyle.MINIMAL:
            lines.extend(self._create_minimal_table(data, headers, col_widths, alternating_colors))
        
        return '\n'.join(lines)
    
    def _create_grid_table(self, data: List[List[str]], headers: Optional[List[str]],
                          col_widths: List[int], alternating_colors: bool) -> List[str]:
        """Create grid-style table"""
        lines = []
        
        # Top border
        top_border = self._create_table_border(col_widths, 'top')
        lines.append(self.colorize(top_border, Color.BRIGHT_BLACK))
        
        # Headers
        if headers:
            header_row = self._create_table_row(headers, col_widths, Color.BRIGHT_YELLOW, Color.BOLD)
            lines.append(header_row)
            
            # Header separator
            sep_border = self._create_table_border(col_widths, 'middle')
            lines.append(self.colorize(sep_border, Color.BRIGHT_BLACK))
        
        # Data rows
        for i, row in enumerate(data):
            if alternating_colors:
                color = Color.BRIGHT_WHITE if i % 2 == 0 else Color.WHITE
            else:
                color = Color.BRIGHT_WHITE
            
            row_line = self._create_table_row(row, col_widths, color)
            lines.append(row_line)
        
        # Bottom border
        bottom_border = self._create_table_border(col_widths, 'bottom')
        lines.append(self.colorize(bottom_border, Color.BRIGHT_BLACK))
        
        return lines
    
    def _create_simple_table(self, data: List[List[str]], headers: Optional[List[str]],
                            col_widths: List[int], alternating_colors: bool) -> List[str]:
        """Create simple table without borders"""
        lines = []
        
        # Headers
        if headers:
            header_row = '  '.join(
                self.colorize(str(headers[i]).ljust(col_widths[i]), Color.BRIGHT_YELLOW, style=Color.BOLD)
                for i in range(len(headers))
            )
            lines.append(header_row)
            
            # Header underline
            underline = '  '.join(
                self.colorize('-' * col_widths[i], Color.BRIGHT_BLACK)
                for i in range(len(headers))
            )
            lines.append(underline)
        
        # Data rows
        for i, row in enumerate(data):
            if alternating_colors:
                color = Color.BRIGHT_WHITE if i % 2 == 0 else Color.WHITE
            else:
                color = Color.BRIGHT_WHITE
            
            row_line = '  '.join(
                self.colorize(str(row[j]).ljust(col_widths[j]), color) if j < len(row) else ' ' * col_widths[j]
                for j in range(len(col_widths))
            )
            lines.append(row_line)
        
        return lines
    
    def _create_fancy_grid_table(self, data: List[List[str]], headers: Optional[List[str]],
                                col_widths: List[int], alternating_colors: bool) -> List[str]:
        """Create fancy grid table with double borders"""
        lines = []
        
        # Top border with double lines
        top_border = self._create_table_border(col_widths, 'top', double=True)
        lines.append(self.colorize(top_border, Color.BRIGHT_CYAN))
        
        # Headers
        if headers:
            header_row = self._create_table_row(headers, col_widths, Color.BRIGHT_CYAN, Color.BOLD, double_border=True)
            lines.append(header_row)
            
            # Header separator with double lines
            sep_border = self._create_table_border(col_widths, 'middle', double=True)
            lines.append(self.colorize(sep_border, Color.BRIGHT_CYAN))
        
        # Data rows
        for i, row in enumerate(data):
            if alternating_colors:
                color = Color.BRIGHT_WHITE if i % 2 == 0 else Color.WHITE
            else:
                color = Color.BRIGHT_WHITE
            
            row_line = self._create_table_row(row, col_widths, color, double_border=True)
            lines.append(row_line)
        
        # Bottom border with double lines
        bottom_border = self._create_table_border(col_widths, 'bottom', double=True)
        lines.append(self.colorize(bottom_border, Color.BRIGHT_CYAN))
        
        return lines
    
    def _create_minimal_table(self, data: List[List[str]], headers: Optional[List[str]],
                             col_widths: List[int], alternating_colors: bool) -> List[str]:
        """Create minimal table with only essential formatting"""
        lines = []
        
        # Headers
        if headers:
            header_row = ' | '.join(
                self.colorize(str(headers[i]).ljust(col_widths[i]), Color.BRIGHT_YELLOW, style=Color.BOLD)
                for i in range(len(headers))
            )
            lines.append(header_row)
        
        # Data rows
        for i, row in enumerate(data):
            if alternating_colors:
                color = Color.BRIGHT_WHITE if i % 2 == 0 else Color.WHITE
            else:
                color = Color.BRIGHT_WHITE
            
            row_line = ' | '.join(
                self.colorize(str(row[j]).ljust(col_widths[j]), color) if j < len(row) else ' ' * col_widths[j]
                for j in range(len(col_widths))
            )
            lines.append(row_line)
        
        return lines
    
    def _create_table_border(self, col_widths: List[int], position: str, double: bool = False) -> str:
        """Create table border line"""
        h_char = self.box_chars['double_horizontal'] if double else self.box_chars['horizontal']
        
        if position == 'top':
            left_char = self.box_chars['top_left']
            right_char = self.box_chars['top_right']
            junction_char = self.box_chars['t_down']
        elif position == 'bottom':
            left_char = self.box_chars['bottom_left']
            right_char = self.box_chars['bottom_right']
            junction_char = self.box_chars['t_up']
        else:  # middle
            left_char = self.box_chars['t_right']
            right_char = self.box_chars['t_left']
            junction_char = self.box_chars['cross']
        
        segments = [h_char * (width + 2) for width in col_widths]
        return left_char + junction_char.join(segments) + right_char
    
    def _create_table_row(self, row_data: List[str], col_widths: List[int],
                         color: Color, style: Optional[Color] = None,
                         double_border: bool = False) -> str:
        """Create formatted table row"""
        v_char = self.box_chars['double_vertical'] if double_border else self.box_chars['vertical']
        
        cells = []
        for i, width in enumerate(col_widths):
            cell_data = str(row_data[i]) if i < len(row_data) else ""
            padded_cell = f" {cell_data.ljust(width)} "
            colored_cell = self.colorize(padded_cell, color, style=style)
            cells.append(colored_cell)
        
        border_color = Color.BRIGHT_CYAN if double_border else Color.BRIGHT_BLACK
        v_colored = self.colorize(v_char, border_color)
        
        return v_colored + v_colored.join(cells) + v_colored
    
    def create_panel(self, title: str, content: str, width: Optional[int] = None,
                    color: Color = Color.BRIGHT_BLUE, padding: int = 1) -> str:
        """Create panel with title and content"""
        if width is None:
            width = min(self.capabilities.width - 4, 76)
        
        content_width = width - 4  # Account for borders and padding
        lines = []
        
        # Top border with title
        title_line = f" {title} "
        title_padding = max(0, content_width - len(title_line))
        top_border = (
            self.box_chars['top_left'] +
            title_line +
            self.box_chars['horizontal'] * title_padding +
            self.box_chars['top_right']
        )
        lines.append(self.colorize(top_border, color, style=Color.BOLD))
        
        # Content lines
        content_lines = content.split('\n')
        for line in content_lines:
            # Add padding lines if requested
            if padding > 0:
                for _ in range(padding):
                    empty_line = (
                        self.colorize(self.box_chars['vertical'], color) +
                        ' ' * content_width +
                        self.colorize(self.box_chars['vertical'], color)
                    )
                    lines.append(empty_line)
                    padding = 0  # Only add padding once at the beginning
            
            # Wrap long lines
            while line:
                chunk = line[:content_width-2]
                line = line[content_width-2:]
                
                padded_chunk = f" {chunk.ljust(content_width-2)} "
                content_line = (
                    self.colorize(self.box_chars['vertical'], color) +
                    padded_chunk +
                    self.colorize(self.box_chars['vertical'], color)
                )
                lines.append(content_line)
        
        # Add bottom padding
        if padding > 0:
            empty_line = (
                self.colorize(self.box_chars['vertical'], color) +
                ' ' * content_width +
                self.colorize(self.box_chars['vertical'], color)
            )
            lines.append(empty_line)
        
        # Bottom border
        bottom_border = (
            self.box_chars['bottom_left'] +
            self.box_chars['horizontal'] * content_width +
            self.box_chars['bottom_right']
        )
        lines.append(self.colorize(bottom_border, color))
        
        return '\n'.join(lines)
    
    def create_multi_panel(self, panels: List[Dict[str, Any]], 
                          arrangement: str = "vertical") -> str:
        """Create multiple panels arranged vertically or horizontally"""
        if not panels:
            return ""
        
        if arrangement == "vertical":
            return '\n\n'.join(
                self.create_panel(
                    panel.get('title', 'Panel'),
                    panel.get('content', ''),
                    panel.get('width'),
                    panel.get('color', Color.BRIGHT_BLUE),
                    panel.get('padding', 1)
                )
                for panel in panels
            )
        else:
            # Horizontal arrangement is more complex - simplified version
            return self.create_multi_panel(panels, "vertical")
    
    def clear_line(self) -> str:
        """Clear current line (PowerShell compatible)"""
        return '\r' + ' ' * self.capabilities.width + '\r'
    
    def move_cursor_up(self, lines: int = 1) -> str:
        """Move cursor up (limited PowerShell support)"""
        if self.capabilities.is_powershell:
            return ''  # PowerShell handles this differently
        return f'\033[{lines}A'
    
    def print_formatted(self, *args, **kwargs):
        """Print with automatic formatting detection"""
        output = ' '.join(str(arg) for arg in args)
        print(output, **kwargs)


class Spinner:
    """Animated spinner optimized for PowerShell"""
    
    SPINNER_STYLES = {
        'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
        'simple': ['|', '/', '-', '\\'],
        'blocks': ['█', '▉', '▊', '▋', '▌', '▍', '▎', '▏', '▎', '▍', '▌', '▋', '▊', '▉'],
        'dots_simple': ['.', '..', '...', '....', '.....'],
        'arrows': ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
    }
    
    def __init__(self, formatter: EnhancedFormatter, message: str = "", 
                 style: str = "simple"):
        self.formatter = formatter
        self.message = message
        self.style = style
        self.frames = self.SPINNER_STYLES.get(style, self.SPINNER_STYLES['simple'])
        self.current_frame = 0
        self.active = False
        self.thread = None
        
        # Use simple style for PowerShell compatibility
        if formatter.capabilities.is_powershell:
            self.frames = self.SPINNER_STYLES['simple']
    
    def start(self):
        """Start spinning animation"""
        if self.active:
            return
        
        self.active = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop spinning animation"""
        self.active = False
        if self.thread:
            self.thread.join(timeout=0.1)
        
        # Clear the spinner line
        print(self.formatter.clear_line(), end='', flush=True)
    
    def _spin(self):
        """Internal spinning logic"""
        while self.active:
            frame = self.frames[self.current_frame]
            colored_frame = self.formatter.colorize(frame, Color.BRIGHT_YELLOW)
            
            output = f"\r{colored_frame} {self.message}"
            print(output, end='', flush=True)
            
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            time.sleep(0.1)
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


# Convenience functions for quick formatting
def quick_header(title: str, style: str = "banner", color: str = "bright_cyan") -> str:
    """Quick header creation"""
    formatter = EnhancedFormatter()
    header_style = HeaderStyle(style) if isinstance(style, str) else style
    color_enum = Color[color.upper()] if isinstance(color, str) else color
    return formatter.create_header(title, header_style, color=color_enum)


def quick_table(data: List[List[str]], headers: Optional[List[str]] = None,
               style: str = "grid") -> str:
    """Quick table creation"""
    formatter = EnhancedFormatter()
    table_style = TableStyle(style) if isinstance(style, str) else style
    return formatter.create_table(data, headers, table_style)


def quick_panel(title: str, content: str, color: str = "bright_blue") -> str:
    """Quick panel creation"""
    formatter = EnhancedFormatter()
    color_enum = Color[color.upper()] if isinstance(color, str) else color
    return formatter.create_panel(title, content, color=color_enum)


def quick_progress(progress: float, width: int = 50) -> str:
    """Quick progress bar"""
    formatter = EnhancedFormatter()
    return formatter.create_progress_bar(progress, width)


# Global formatter instance for convenience
_global_formatter = None

def get_formatter() -> EnhancedFormatter:
    """Get global formatter instance"""
    global _global_formatter
    if _global_formatter is None:
        _global_formatter = EnhancedFormatter()
    return _global_formatter