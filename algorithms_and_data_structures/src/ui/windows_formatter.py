#!/usr/bin/env python3
"""
Windows-Optimized Terminal Formatter - Beautiful terminal formatting for Windows
"""

import sys
import os
from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass
import shutil
# Handle relative imports when running as script
try:
    from ..utils.terminal_utils import terminal_utils, get_terminal_width, create_safe_box, wrap_text_safe
except ImportError:
    # If running as script, try absolute import
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from utils.terminal_utils import terminal_utils, get_terminal_width, create_safe_box, wrap_text_safe
# Note: ProgressBar not available in current formatter
# Creating basic ProgressBar class for compatibility

class ProgressBar:
    """Basic progress bar class for compatibility"""
    def __init__(self, formatter=None, total=100, description="Progress", bar_id=None):
        self.formatter = formatter
        self.total = total
        self.description = description
        self.bar_id = bar_id
        self.current = 0
    
    def update(self, amount=1):
        """Update progress"""
        self.current = min(self.current + amount, self.total)
    
    def set_progress(self, value):
        """Set absolute progress value"""
        self.current = min(value, self.total)
    
    def finish(self):
        """Complete the progress bar"""
        self.current = self.total


class WindowsColor(Enum):
    """Windows-safe ANSI color codes"""
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
    UNDERLINE = "\033[4m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


@dataclass
class ModernTheme:
    """Modern color theme optimized for readability"""
    primary: WindowsColor = WindowsColor.BRIGHT_CYAN
    secondary: WindowsColor = WindowsColor.BRIGHT_BLUE
    success: WindowsColor = WindowsColor.BRIGHT_GREEN
    warning: WindowsColor = WindowsColor.BRIGHT_YELLOW
    error: WindowsColor = WindowsColor.BRIGHT_RED
    info: WindowsColor = WindowsColor.CYAN
    muted: WindowsColor = WindowsColor.BRIGHT_BLACK
    text: WindowsColor = WindowsColor.WHITE
    highlight: WindowsColor = WindowsColor.BRIGHT_MAGENTA
    code: WindowsColor = WindowsColor.BRIGHT_WHITE
    comment: WindowsColor = WindowsColor.GREEN
    accent: WindowsColor = WindowsColor.BRIGHT_MAGENTA  # Added accent color for UI elements


class WindowsFormatter:
    """Beautiful terminal formatter optimized for Windows"""
    
    def __init__(self):
        """Initialize the formatter with Windows-specific settings"""
        # Enable Windows ANSI support
        self.colors_enabled = True  # Default to true
        if sys.platform == 'win32':
            self.colors_enabled = self._enable_windows_ansi()
        
        self.box_style = 'simple' if self.colors_enabled else 'ascii'
        self.color_enabled = self.colors_enabled  # Alias for compatibility
        self.width = self._get_terminal_width()
        
        # Create a theme object for compatibility with enhanced_cli
        self.theme = type('Theme', (), {
            'primary': WindowsColor.BRIGHT_CYAN,
            'secondary': WindowsColor.BRIGHT_MAGENTA,
            'success': WindowsColor.BRIGHT_GREEN,
            'warning': WindowsColor.BRIGHT_YELLOW,
            'error': WindowsColor.BRIGHT_RED,
            'info': WindowsColor.BRIGHT_BLUE,
            'muted': WindowsColor.BRIGHT_BLACK,
            'text': WindowsColor.WHITE,
            'accent': WindowsColor.BRIGHT_MAGENTA,  # Added missing accent attribute
            'highlight': WindowsColor.BRIGHT_MAGENTA,  # Also add highlight for consistency
            'code': WindowsColor.BRIGHT_WHITE,  # Add code color
            'comment': WindowsColor.GREEN  # Add comment color
        })()
    
    # Windows-safe box drawing characters
    BOX_CHARS = {
        'ascii': {
            'top_left': '+', 'top_right': '+', 'bottom_left': '+', 'bottom_right': '+',
            'horizontal': '-', 'vertical': '|', 'cross': '+', 
            'tee_down': '+', 'tee_up': '+', 'tee_right': '+', 'tee_left': '+'
        },
        'simple': {
            'top_left': '+', 'top_right': '+', 'bottom_left': '+', 'bottom_right': '+',
            'horizontal': '=', 'vertical': '|', 'cross': '+',
            'tee_down': '=', 'tee_up': '=', 'tee_right': '|', 'tee_left': '|'
        },
        'double': {
            'top_left': '#', 'top_right': '#', 'bottom_left': '#', 'bottom_right': '#',
            'horizontal': '=', 'vertical': '#', 'cross': '#',
            'tee_down': '#', 'tee_up': '#', 'tee_right': '#', 'tee_left': '#'
        }
    }
    
    def _enable_windows_ansi(self):
        """Enable ANSI color support on Windows"""
        try:
            # Try to use colorama first with proper Windows settings
            import colorama
            colorama.init(autoreset=False, convert=True, strip=False)
            return True
        except ImportError:
            # Fallback to Windows API
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                # Enable ANSI escape sequences
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except:
                # If all else fails, disable colors
                return False
    
    def _get_terminal_width(self) -> int:
        """Get terminal width safely using terminal utilities"""
        return get_terminal_width()
    
    def _color(self, text: str, color: WindowsColor, style: Optional[WindowsColor] = None) -> str:
        """Apply color to text"""
        if not self.colors_enabled:
            return text
        
        result = color.value
        if style:
            result += style.value
        result += text + WindowsColor.RESET.value
        return result
    
    def _colorize(self, text: str, color, style=None) -> str:
        """Alias for _color to match the base formatter interface
        
        This method accepts color in various formats and converts to WindowsColor
        """
        # Convert color to WindowsColor if needed
        if not isinstance(color, WindowsColor):
            # Try to find matching WindowsColor by name or value
            if hasattr(WindowsColor, str(color).upper()):
                color = getattr(WindowsColor, str(color).upper())
            else:
                # Default to white if color not found
                color = WindowsColor.WHITE
        
        # Convert style if provided
        if style and not isinstance(style, WindowsColor):
            if hasattr(WindowsColor, str(style).upper()):
                style = getattr(WindowsColor, str(style).upper())
            else:
                style = None
        
        return self._color(text, color, style)
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if sys.platform == 'win32' else 'clear')
    
    def header(self, title: str, subtitle: Optional[str] = None, level: int = 1) -> str:
        """Create a beautiful header"""
        width = min(80, self.width)
        
        if level == 1:
            # Main header with decorative border
            border = "=" * width
            lines = [
                self._color(border, self.theme.primary, WindowsColor.BOLD),
                "",
                self._color(title.upper().center(width), self.theme.primary, WindowsColor.BOLD)
            ]
            
            if subtitle:
                lines.append(self._color(subtitle.center(width), self.theme.secondary))
            
            lines.extend([
                "",
                self._color(border, self.theme.primary, WindowsColor.BOLD)
            ])
            
        elif level == 2:
            # Section header
            decorator = ">>>"
            lines = [
                "",
                self._color(f"{decorator} {title} {decorator}", self.theme.secondary, WindowsColor.BOLD)
            ]
            if subtitle:
                lines.append(self._color(f"    {subtitle}", self.theme.muted))
            lines.append(self._color("-" * min(len(title) + 8, width), self.theme.muted))
            
        else:
            # Subsection header
            lines = [
                "",
                self._color(f"> {title}", self.theme.text, WindowsColor.BOLD)
            ]
            if subtitle:
                lines.append(self._color(f"  {subtitle}", self.theme.muted))
        
        return "\n".join(lines)
    
    def code_block(self, code: str, language: str = "python", title: Optional[str] = None) -> str:
        """Format a code block with syntax-like highlighting"""
        width = min(80, self.width - 4)
        lines = []
        
        # Header
        if title:
            header = f" {title} [{language}] "
            padding = (width - len(header)) // 2
            header_line = "+" + "-" * padding + header + "-" * (width - padding - len(header)) + "+"
            lines.append(self._color(header_line, self.theme.muted))
        else:
            lines.append(self._color("+" + "-" * width + "+", self.theme.muted))
        
        # Code lines with basic syntax highlighting
        code_lines = code.split('\n')
        for line in code_lines:
            # Simple keyword highlighting
            highlighted = line
            
            # Python keywords
            keywords = ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 
                       'return', 'import', 'from', 'as', 'try', 'except', 
                       'with', 'in', 'not', 'and', 'or', 'True', 'False', 'None']
            
            for keyword in keywords:
                if f' {keyword} ' in highlighted or highlighted.startswith(f'{keyword} '):
                    # Preserve the line but highlight keywords
                    parts = highlighted.split(keyword)
                    highlighted_keyword = self._color(keyword, self.theme.highlight, WindowsColor.BOLD)
                    highlighted = highlighted_keyword.join(parts)
            
            # Comments (simple detection)
            if '#' in line:
                comment_pos = line.find('#')
                code_part = line[:comment_pos]
                comment_part = line[comment_pos:]
                highlighted = code_part + self._color(comment_part, self.theme.comment)
            
            # String literals (very basic)
            if '"' in highlighted or "'" in highlighted:
                # Color strings in green
                pass  # Complex to do properly without breaking
            
            # Add line with border
            formatted_line = f"| {highlighted:<{width-2}} |"
            lines.append(formatted_line)
        
        # Footer
        lines.append(self._color("+" + "-" * width + "+", self.theme.muted))
        
        return "\n".join(lines)
    
    def box(self, content: str, title: Optional[str] = None, style: str = "ascii", 
            color: Optional[WindowsColor] = None) -> str:
        """Create a clean box around content using safe terminal utilities"""
        # Use the safe box creation from terminal utilities
        safe_box = create_safe_box(content, title)
        
        # Apply color if specified
        border_color = color or self.theme.primary
        return self._color(safe_box, border_color)
    
    def progress_bar(self, total: int, description: str = "", 
                    bar_id: Optional[str] = None) -> ProgressBar:
        """Create a progress bar that returns a ProgressBar instance
        
        Args:
            total: Total number of items
            description: Progress description
            bar_id: Unique ID for the progress bar
            
        Returns:
            Progress bar instance
        """
        # Create a ProgressBar instance that works with Windows formatter
        if bar_id is None:
            bar_id = f"progress_{id(self)}"
        
        # We need to create a custom ProgressBar that uses our Windows formatter
        progress_bar = WindowsProgressBar(self, total, description, bar_id)
        return progress_bar
    
    def render_progress_bar(self, current: int, total: int, label: str = "", width: int = 40) -> str:
        """Create a beautiful progress bar string with safe characters"""
        # Ensure both values are integers
        current = int(current) if isinstance(current, str) else current
        total = int(total) if isinstance(total, str) else total
        percent = current / total if total > 0 else 0
        
        # Adjust width to fit terminal
        safe_width = min(width, get_terminal_width() - 20)  # Leave space for text
        filled = int(safe_width * percent)
        
        # Use ASCII characters for maximum compatibility
        bar = "#" * filled + "-" * (safe_width - filled)
        
        # Color based on progress
        if percent < 0.33:
            bar_color = self.theme.error
        elif percent < 0.66:
            bar_color = self.theme.warning
        else:
            bar_color = self.theme.success
        
        # Format the bar
        bar_str = self._color(bar, bar_color)
        percent_str = f"{percent*100:5.1f}%"
        progress_str = f"{current}/{total}"
        
        if label:
            return f"{label}: [{bar_str}] {percent_str} ({progress_str})"
        else:
            return f"[{bar_str}] {percent_str} ({progress_str})"
    
    def list_items(self, items: List[str], style: str = "bullet") -> str:
        """Format a list of items beautifully"""
        lines = []
        
        if style == "numbered":
            for i, item in enumerate(items, 1):
                number = self._color(f"{i:2d}.", self.theme.primary, WindowsColor.BOLD)
                lines.append(f"  {number} {item}")
        elif style == "checkbox":
            for item in items:
                checkbox = self._color("[  ]", self.theme.muted)
                lines.append(f"  {checkbox} {item}")
        elif style == "arrow":
            for item in items:
                arrow = self._color("=>", self.theme.secondary, WindowsColor.BOLD)
                lines.append(f"  {arrow} {item}")
        else:  # bullet
            for item in items:
                bullet = self._color("*", self.theme.primary, WindowsColor.BOLD)
                lines.append(f"  {bullet} {item}")
        
        return "\n".join(lines)
    
    def table(self, headers: List[str], rows: List[List[str]], style: str = "simple") -> str:
        """Create a beautiful table"""
        # Calculate column widths
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(str(cell)))
        
        lines = []
        
        # Header row
        header_cells = []
        for i, header in enumerate(headers):
            header_text = str(header).center(widths[i])
            header_cells.append(self._color(header_text, self.theme.primary, WindowsColor.BOLD))
        lines.append(" | ".join(header_cells))
        
        # Separator
        sep = "-+-".join(["-" * w for w in widths])
        lines.append(self._color(sep, self.theme.muted))
        
        # Data rows
        for row_num, row in enumerate(rows):
            cells = []
            for i, cell in enumerate(row):
                if i < len(widths):
                    cell_text = str(cell).ljust(widths[i])
                    # Alternate row colors
                    if row_num % 2 == 0:
                        cells.append(cell_text)
                    else:
                        cells.append(self._color(cell_text, self.theme.muted))
            lines.append(" | ".join(cells))
        
        return "\n".join(lines)
    
    def success(self, message: str) -> str:
        """Format a success message"""
        icon = "[OK]"
        return self._color(f"{icon} {message}", self.theme.success, WindowsColor.BOLD)
    
    def error(self, message: str) -> str:
        """Format an error message"""
        icon = "[ERROR]"
        return self._color(f"{icon} {message}", self.theme.error, WindowsColor.BOLD)
    
    def warning(self, message: str) -> str:
        """Format a warning message"""
        icon = "[WARN]"
        return self._color(f"{icon} {message}", self.theme.warning, WindowsColor.BOLD)
    
    def info(self, message: str) -> str:
        """Format an info message"""
        icon = "[INFO]"
        return self._color(f"{icon} {message}", self.theme.info)
    
    def highlight(self, text: str, pattern: str) -> str:
        """Highlight pattern in text"""
        if pattern in text:
            parts = text.split(pattern)
            highlighted_pattern = self._color(pattern, self.theme.highlight, WindowsColor.BOLD)
            return highlighted_pattern.join(parts)
        return text
    
    def divider(self, title: Optional[str] = None, char: str = "-", width: Optional[int] = None) -> str:
        """Create a divider line"""
        if width is None:
            width = min(80, self.width)
        
        if title:
            title_text = f" {title} "
            padding = (width - len(title_text)) // 2
            line = char * padding + title_text + char * (width - padding - len(title_text))
            return self._color(line, self.theme.muted)
        else:
            return self._color(char * width, self.theme.muted)
    
    def rule(self, title: Optional[str] = None, char: str = "-", style: str = "single") -> str:
        """Create a horizontal rule with optional title (alias for divider for compatibility)
        
        Args:
            title: Optional title in the middle of the rule
            char: Character to use for the rule
            style: Rule style (ignored for Windows compatibility)
            
        Returns:
            Formatted rule string
        """
        # Map style to appropriate character
        if style == "double":
            char = "="
        elif style == "thick":
            char = "#"
        elif style == "dotted":
            char = "."
        elif style == "gradient":
            # Use a pattern for gradient effect
            char = "="
        else:
            char = "-"
        
        # Use the divider method with appropriate formatting
        width = min(80, self.width)
        
        if title:
            title_text = f" {title} "
            padding = (width - len(title_text)) // 2
            line = char * padding + title_text + char * (width - padding - len(title_text))
            colored_rule = self._color(line, self.theme.secondary, WindowsColor.BOLD)
        else:
            line = char * width
            colored_rule = self._color(line, self.theme.muted)
        
        print(colored_rule)
        return colored_rule
    
    def frame(self, content: str, style: str = "simple", margin: int = 1) -> str:
        """Create a decorative frame around content
        
        Args:
            content: Content to frame
            style: Frame style ('simple', 'ornate', 'minimal')
            margin: Margin around content
            
        Returns:
            Framed content string
        """
        lines = content.split('\n')
        max_width = max(len(line) for line in lines) if lines else 0
        frame_width = max_width + (margin * 2) + 4
        
        framed_lines = []
        
        if style == "ornate":
            # Ornate frame with ASCII decorations
            top = "+" + "=" * (frame_width - 2) + "+"
            framed_lines.append(self._color(top, WindowsColor.BRIGHT_MAGENTA))
            
            # Add margin lines
            for _ in range(margin):
                margin_line = "|" + " " * (frame_width - 2) + "|"
                framed_lines.append(self._color(margin_line, WindowsColor.BRIGHT_MAGENTA))
            
            # Content lines
            for line in lines:
                padded = line.center(max_width)
                full_line = "| " + " " * margin + padded + " " * margin + " |"
                framed_lines.append(self._color(full_line, WindowsColor.BRIGHT_MAGENTA))
            
            # Bottom margin
            for _ in range(margin):
                margin_line = "|" + " " * (frame_width - 2) + "|"
                framed_lines.append(self._color(margin_line, WindowsColor.BRIGHT_MAGENTA))
            
            bottom = "+" + "=" * (frame_width - 2) + "+"
            framed_lines.append(self._color(bottom, WindowsColor.BRIGHT_MAGENTA))
            
        elif style == "minimal":
            # Minimal frame
            for line in lines:
                framed_line = f"  {line}  "
                framed_lines.append(self._color(framed_line, self.theme.text))
            
        else:  # simple
            # Simple frame
            border = "+" + "-" * (frame_width - 2) + "+"
            framed_lines.append(self._color(border, self.theme.muted))
            
            for line in lines:
                padded = line.center(max_width)
                full_line = "|" + " " * margin + padded + " " * margin + "|"
                framed_lines.append(full_line)
            
            framed_lines.append(self._color(border, self.theme.muted))
        
        result = "\n".join(framed_lines)
        print(result)
        return result
    
    def panel(self, sections: List[tuple], title: Optional[str] = None) -> str:
        """Create a multi-section panel with dividers
        
        Args:
            sections: List of (header, content) tuples
            title: Optional panel title
            
        Returns:
            Panel string
        """
        panel_width = self.width - 4 if self.width > 80 else 76
        lines = []
        
        # Panel top
        if title:
            title_line = f"+===  {title} " + "=" * (panel_width - len(title) - 6) + "+"
        else:
            title_line = "+" + "=" * (panel_width - 2) + "+"
        lines.append(self._color(title_line, self.theme.primary, WindowsColor.BOLD))
        
        # Process sections
        for i, (header, content) in enumerate(sections):
            # Section header
            if header:
                header_line = f"| {header}"
                header_line = header_line.ljust(panel_width - 1) + "|"
                lines.append(self._color(header_line, self.theme.secondary, WindowsColor.BOLD))
                
                # Divider under header
                divider = "+" + "-" * (panel_width - 2) + "+"
                lines.append(self._color(divider, self.theme.muted))
            
            # Content lines
            content_lines = content.split('\n')
            for line in content_lines:
                # Wrap long lines
                if len(line) > panel_width - 4:
                    # Simple truncation for Windows
                    line = line[:panel_width - 7] + "..."
                content_line = f"| {line.ljust(panel_width - 3)}|"
                lines.append(content_line)
            
            # Add section separator if not last section
            if i < len(sections) - 1:
                separator = "+" + "-" * (panel_width - 2) + "+"
                lines.append(self._color(separator, self.theme.muted))
        
        # Panel bottom
        bottom_line = "+" + "=" * (panel_width - 2) + "+"
        lines.append(self._color(bottom_line, self.theme.primary, WindowsColor.BOLD))
        
        panel_str = "\n".join(lines)
        print(panel_str)
        return panel_str
    
    def transition_effect(self, effect_type: str = "fade") -> None:
        """Display transition effect between screens (simplified for Windows)
        
        Args:
            effect_type: Type of transition ('fade', 'slide', 'wipe')
        """
        import time
        
        if not self.colors_enabled:
            return
        
        # Simple transition effects using ASCII
        if effect_type == "fade":
            # Fade effect with ASCII characters
            chars = ["#", "=", "-", ".", " "]
            for char in chars:
                print(f"\r{char * min(self.width, 80)}", end="")
                time.sleep(0.05)
        
        elif effect_type == "slide":
            # Slide effect
            for i in range(min(self.width, 40)):
                line = " " * i + "#" * (min(self.width, 80) - i)
                print(f"\r{line}", end="")
                time.sleep(0.02)
        
        elif effect_type == "wipe":
            # Wipe effect
            for i in range(10):
                pattern = "|" * (i + 1)
                print(f"\r{pattern.center(min(self.width, 80))}", end="")
                time.sleep(0.05)
        
        # Clear the line
        print(f"\r{' ' * min(self.width, 80)}\r", end="")


# Example usage and test
class WindowsProgressBar(ProgressBar):
    """Windows-optimized progress bar that extends the base ProgressBar"""
    
    def __init__(self, formatter, total: int, description: str, bar_id: str):
        """Initialize the Windows progress bar"""
        # Store the Windows formatter reference
        self.windows_formatter = formatter
        # Initialize with a dummy formatter since we'll override the render method
        super().__init__(formatter, total, description, bar_id)
    
    def _render(self):
        """Render the progress bar using Windows-safe characters"""
        if not hasattr(self.windows_formatter, 'color_enabled'):
            # Fallback to simple text progress
            percent = (self.current / self.total) * 100 if self.total > 0 else 0
            print(f"\r{self.description}: {self.current}/{self.total} ({percent:.1f}%)", 
                  end="", flush=True)
            return
        
        # Use the Windows formatter's render method
        percent = self.current / self.total if self.total > 0 else 0
        filled_length = int(40 * percent)
        
        # Use Windows-safe characters
        bar = "█" * filled_length + "░" * (40 - filled_length)
        
        # Color based on progress
        if percent < 0.33:
            bar_color = WindowsColor.RED
        elif percent < 0.66:
            bar_color = WindowsColor.YELLOW
        else:
            bar_color = WindowsColor.GREEN
        
        # Format the progress line
        percent_str = f"{percent*100:.1f}%"
        progress_line = f"{self.description}: {self.windows_formatter._color(bar, bar_color)} {percent_str}"
        
        # Print with carriage return for updating
        print(f"\r{progress_line}", end="", flush=True)
    
    def finish(self):
        """Complete the progress bar"""
        self.set_progress(self.total)
        print()  # New line after completion


if __name__ == "__main__":
    formatter = WindowsFormatter()
    
    # Clear screen for fresh start
    formatter.clear_screen()
    
    # Show examples
    print(formatter.header("Algorithm Learning System", "Beautiful Terminal Interface", level=1))
    print()
    
    print(formatter.header("Features", level=2))
    print(formatter.list_items([
        "Clean, readable output",
        "Windows-optimized characters",
        "Beautiful color schemes",
        "No broken Unicode boxes"
    ], style="arrow"))
    print()
    
    # Code example
    code = """def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1"""
    
    print(formatter.code_block(code, "python", "Binary Search Example"))
    print()
    
    # Progress bar
    print(formatter.render_progress_bar(7, 10, "Learning Progress"))
    print()
    
    # Table
    headers = ["Algorithm", "Time Complexity", "Space"]
    rows = [
        ["Binary Search", "O(log n)", "O(1)"],
        ["Linear Search", "O(n)", "O(1)"],
        ["Quick Sort", "O(n log n)", "O(log n)"]
    ]
    print(formatter.table(headers, rows))