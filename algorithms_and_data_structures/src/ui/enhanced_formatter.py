#!/usr/bin/env python3
"""
Enhanced Terminal Formatter - Beautiful CLI with Advanced Features
All the gorgeous formatting features for a stunning terminal experience
"""

import sys
import os
import time
import math
import random
import shutil
import threading
import asyncio
from typing import Optional, List, Dict, Any, Tuple, Callable
from enum import Enum
from dataclasses import dataclass
import re
import itertools

# Handle relative imports when running as script
try:
    from ..utils.terminal_utils import terminal_utils, get_terminal_width, create_safe_box, wrap_text_safe
except ImportError:
    # If running as script, try absolute import
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from utils.terminal_utils import terminal_utils, get_terminal_width, create_safe_box, wrap_text_safe

# Try to import Windows-specific modules
try:
    import msvcrt
    import ctypes
    from ctypes import wintypes
    WINDOWS = True
except ImportError:
    WINDOWS = False
    msvcrt = None

# Try to import colorama for Windows color support
try:
    import colorama
    colorama.init(autoreset=True)
    COLORAMA = True
except ImportError:
    COLORAMA = False


class Color(Enum):
    """Enhanced ANSI color codes with 256-color support"""
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
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # Styles
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    STRIKETHROUGH = "\033[9m"
    
    # 256 color palette methods
    @staticmethod
    def rgb(r: int, g: int, b: int) -> str:
        """Create 24-bit true color escape code"""
        return f"\033[38;2;{r};{g};{b}m"
    
    @staticmethod
    def bg_rgb(r: int, g: int, b: int) -> str:
        """Create 24-bit true color background escape code"""
        return f"\033[48;2;{r};{g};{b}m"


class GradientPreset(Enum):
    """Beautiful gradient presets"""
    RAINBOW = "rainbow"
    FIRE = "fire"
    OCEAN = "ocean"
    SUNSET = "sunset"
    FOREST = "forest"
    PURPLE = "purple"
    CYBERPUNK = "cyberpunk"
    GALAXY = "galaxy"
    MATRIX = "matrix"
    GOLD = "gold"
    ICE = "ice"
    NEON = "neon"


@dataclass
class GradientColor:
    """RGB color for gradients"""
    r: int
    g: int
    b: int
    
    def interpolate(self, other: 'GradientColor', t: float) -> 'GradientColor':
        """Interpolate between two colors"""
        return GradientColor(
            int(self.r + (other.r - self.r) * t),
            int(self.g + (other.g - self.g) * t),
            int(self.b + (other.b - self.b) * t)
        )


class BeautifulFormatter:
    """The ultimate beautiful CLI formatter with all features"""
    
    # Gradient color definitions
    GRADIENTS = {
        GradientPreset.RAINBOW: [
            GradientColor(255, 0, 0),      # Red
            GradientColor(255, 127, 0),    # Orange
            GradientColor(255, 255, 0),    # Yellow
            GradientColor(0, 255, 0),      # Green
            GradientColor(0, 0, 255),      # Blue
            GradientColor(75, 0, 130),     # Indigo
            GradientColor(148, 0, 211)     # Violet
        ],
        GradientPreset.FIRE: [
            GradientColor(255, 0, 0),      # Red
            GradientColor(255, 69, 0),     # Orange-red
            GradientColor(255, 140, 0),    # Dark orange
            GradientColor(255, 215, 0),    # Gold
            GradientColor(255, 255, 224)   # Light yellow
        ],
        GradientPreset.OCEAN: [
            GradientColor(0, 119, 190),    # Deep blue
            GradientColor(0, 180, 216),    # Ocean blue
            GradientColor(144, 224, 239),  # Light blue
            GradientColor(202, 240, 248),  # Pale blue
            GradientColor(255, 255, 255)   # White (foam)
        ],
        GradientPreset.CYBERPUNK: [
            GradientColor(255, 0, 255),    # Magenta
            GradientColor(0, 255, 255),    # Cyan
            GradientColor(255, 0, 128),    # Hot pink
            GradientColor(128, 0, 255),    # Purple
            GradientColor(0, 128, 255)     # Sky blue
        ],
        GradientPreset.GALAXY: [
            GradientColor(25, 25, 112),    # Midnight blue
            GradientColor(138, 43, 226),   # Blue violet
            GradientColor(75, 0, 130),     # Indigo
            GradientColor(123, 104, 238),  # Medium slate blue
            GradientColor(230, 230, 250)   # Lavender
        ],
        GradientPreset.SUNSET: [
            GradientColor(255, 94, 77),    # Sunset orange
            GradientColor(255, 154, 0),    # Orange
            GradientColor(237, 117, 57),   # Burnt orange
            GradientColor(95, 39, 205),    # Purple
            GradientColor(25, 25, 112)     # Midnight blue
        ],
        GradientPreset.FOREST: [
            GradientColor(34, 139, 34),    # Forest green
            GradientColor(0, 128, 0),      # Green
            GradientColor(154, 205, 50),   # Yellow green
            GradientColor(107, 142, 35),   # Olive drab
            GradientColor(85, 107, 47)     # Dark olive green
        ],
        GradientPreset.MATRIX: [
            GradientColor(0, 255, 0),      # Bright green
            GradientColor(0, 128, 0),      # Green
            GradientColor(0, 64, 0),       # Dark green
            GradientColor(0, 32, 0),       # Very dark green
            GradientColor(0, 0, 0)         # Black
        ],
        GradientPreset.NEON: [
            GradientColor(255, 0, 255),    # Magenta
            GradientColor(255, 255, 0),    # Yellow
            GradientColor(0, 255, 255),    # Cyan
            GradientColor(255, 0, 0),      # Red
            GradientColor(0, 255, 0)       # Green
        ]
    }
    
    # Spinner styles
    SPINNERS = {
        "dots": "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏",
        "dots2": "⣾⣽⣻⢿⡿⣟⣯⣷",
        "dots3": "⠋⠙⠚⠞⠖⠦⠴⠲⠳⠓",
        "circles": "◐◓◑◒",
        "arrows": "←↖↑↗→↘↓↙",
        "bars": "▁▂▃▄▅▆▇█▇▆▅▄▃▂▁",
        "blocks": "▖▘▝▗",
        "bounce": "⠁⠂⠄⠂",
        "clock": "🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛",
        "moon": "🌑🌒🌓🌔🌕🌖🌗🌘",
        "earth": "🌍🌎🌏",
        "stars": "✶✸✹✺✹✸",
        "hearts": "💛💙💜💚❤️",
        "weather": "☀️🌤⛅️🌥☁️🌦🌧⛈🌩🌨",
        "ascii_dots": "...oooOOOooo...",
        "ascii_bars": "-\\|/",
        "ascii_arrows": "^>v<"
    }
    
    # ASCII art fonts (simplified)
    ASCII_FONTS = {
        "standard": {
            'A': ["  ╔═╗  ", "  ╠═╣  ", "  ╩ ╩  "],
            'L': ["  ╦   ", "  ║   ", "  ╩═╝ "],
            'G': ["  ╔═╗ ", "  ║ ╦ ", "  ╚═╝ "],
            'O': ["  ╔═╗ ", "  ║ ║ ", "  ╚═╝ "],
            'R': ["  ╦═╗ ", "  ╠╦╝ ", "  ╩╚═ "],
            'I': ["  ╦ ", "  ║ ", "  ╩ "],
            'T': ["  ╔╦╗ ", "   ║  ", "   ╩  "],
            'H': ["  ╦ ╦ ", "  ╠═╣ ", "  ╩ ╩ "],
            'M': ["  ╔╦╗ ", "  ║║║ ", "  ╩ ╩ "],
            'S': ["  ╔═╗ ", "  ╚═╗ ", "  ╚═╝ "],
        }
    }
    
    def __init__(self, color_enabled: Optional[bool] = None):
        """Initialize the beautiful formatter"""
        self._color_enabled = color_enabled
        self.width = self._get_terminal_width()
        self._spinner_active = False
        self._spinner_thread: Optional[threading.Thread] = None
        
        # Enable Windows terminal colors if needed
        if WINDOWS and self.color_enabled:
            self._enable_windows_ansi()
    
    def _enable_windows_ansi(self):
        """Enable ANSI escape sequences on Windows"""
        if WINDOWS:
            try:
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass
    
    @property
    def color_enabled(self) -> bool:
        """Check if color output is enabled"""
        if self._color_enabled is not None:
            return self._color_enabled
        
        # Auto-detect color support
        if not sys.stdout.isatty():
            return False
        
        if os.environ.get('NO_COLOR'):
            return False
        
        if os.environ.get('FORCE_COLOR'):
            return True
        
        # Windows color support
        if sys.platform == 'win32':
            return COLORAMA or self._check_windows_terminal()
        
        return True
    
    def _check_windows_terminal(self) -> bool:
        """Check if Windows Terminal or compatible terminal"""
        term = os.environ.get('TERM_PROGRAM', '')
        wt = os.environ.get('WT_SESSION', '')
        return bool(wt) or 'windowsterminal' in term.lower()
    
    def _get_terminal_width(self) -> int:
        """Get terminal width"""
        try:
            return shutil.get_terminal_size().columns
        except:
            return 80
    
    def gradient_text(self, text: str, preset: GradientPreset = GradientPreset.RAINBOW) -> str:
        """Apply beautiful gradient effect to text"""
        if not self.color_enabled or preset not in self.GRADIENTS:
            return text
        
        colors = self.GRADIENTS[preset]
        result = []
        text_len = len(text)
        
        for i, char in enumerate(text):
            if char.isspace():
                result.append(char)
                continue
            
            # Calculate position in gradient
            progress = i / max(text_len - 1, 1)
            color_idx = progress * (len(colors) - 1)
            
            # Interpolate between colors
            idx1 = int(color_idx)
            idx2 = min(idx1 + 1, len(colors) - 1)
            t = color_idx - idx1
            
            color = colors[idx1].interpolate(colors[idx2], t)
            result.append(f"{Color.rgb(color.r, color.g, color.b)}{char}{Color.RESET.value}")
        
        return ''.join(result)
    
    def ascii_art_banner(self, text: str, font: str = "standard") -> str:
        """Create ASCII art banner"""
        if font not in self.ASCII_FONTS:
            return text
        
        font_data = self.ASCII_FONTS[font]
        lines = ["", "", ""]
        
        for char in text.upper():
            if char in font_data:
                char_lines = font_data[char]
                for i in range(3):
                    lines[i] += char_lines[i]
            elif char == ' ':
                for i in range(3):
                    lines[i] += "   "
        
        return "\n".join(lines)
    
    def animated_spinner(self, message: str, style: str = "dots") -> 'SpinnerContext':
        """Create animated spinner context"""
        spinner_chars = self.SPINNERS.get(style, self.SPINNERS["dots"])
        return SpinnerContext(self, message, spinner_chars)
    
    def progress_bar_animated(self, current: int, total: int, 
                            description: str = "", style: str = "blocks") -> str:
        """Create animated progress bar with multiple styles"""
        if total <= 0:
            return description
        
        progress = current / total
        bar_length = 40
        filled_length = int(bar_length * progress)
        
        # Select style
        if style == "blocks":
            filled_char = "█"
            empty_char = "░"
            edge_chars = ["▏", "▎", "▍", "▌", "▋", "▊", "▉"]
            
            # Add partial block at the edge
            remainder = (bar_length * progress) - filled_length
            edge_idx = int(remainder * len(edge_chars))
            edge_char = edge_chars[min(edge_idx, len(edge_chars)-1)] if filled_length < bar_length else ""
            
            bar = filled_char * filled_length + edge_char + empty_char * (bar_length - filled_length - len(edge_char))
        
        elif style == "arrows":
            bar = "=" * filled_length + ">" + "-" * (bar_length - filled_length - 1) if filled_length < bar_length else "=" * bar_length
        
        elif style == "dots":
            bar = "●" * filled_length + "○" * (bar_length - filled_length)
        
        elif style == "stars":
            bar = "★" * filled_length + "☆" * (bar_length - filled_length)
        
        else:  # ascii
            bar = "#" * filled_length + "-" * (bar_length - filled_length)
        
        # Color the bar
        if self.color_enabled:
            if progress < 0.33:
                color = Color.BRIGHT_RED
            elif progress < 0.66:
                color = Color.BRIGHT_YELLOW
            else:
                color = Color.BRIGHT_GREEN
            
            bar = f"{color.value}{bar}{Color.RESET.value}"
        
        # Format percentage
        percentage = f"{progress * 100:6.1f}%"
        
        # Calculate ETA
        return f"{description} [{bar}] {percentage} ({current}/{total})"
    
    def syntax_highlight(self, code: str, language: str = "python") -> str:
        """Enhanced syntax highlighting for multiple languages"""
        if not self.color_enabled:
            return code
        
        highlighted = code
        
        if language.lower() in ["python", "py"]:
            # Python keywords
            keywords = r'\b(def|class|if|else|elif|for|while|try|except|finally|with|as|import|from|return|yield|lambda|pass|break|continue|global|nonlocal|assert|del|raise|in|not|and|or|is|None|True|False|async|await)\b'
            highlighted = re.sub(keywords, f'{Color.BRIGHT_BLUE.value}\\1{Color.RESET.value}', highlighted)
            
            # Built-in functions
            builtins = r'\b(print|len|range|int|str|float|list|dict|set|tuple|bool|type|isinstance|hasattr|getattr|setattr|abs|all|any|bin|chr|dir|enumerate|eval|exec|filter|format|hex|id|input|map|max|min|oct|ord|pow|repr|round|sorted|sum|zip)\b'
            highlighted = re.sub(builtins, f'{Color.BRIGHT_CYAN.value}\\1{Color.RESET.value}', highlighted)
            
            # Strings
            highlighted = re.sub(r'(["\'])((?:\\.|(?!\1).)*?)\1', 
                               f'{Color.BRIGHT_GREEN.value}\\1\\2\\1{Color.RESET.value}', highlighted)
            
            # Comments
            highlighted = re.sub(r'(#.*?)$', f'{Color.BRIGHT_BLACK.value}\\1{Color.RESET.value}', 
                               highlighted, flags=re.MULTILINE)
            
            # Numbers
            highlighted = re.sub(r'\b(\d+\.?\d*)\b', f'{Color.BRIGHT_YELLOW.value}\\1{Color.RESET.value}', highlighted)
            
            # Decorators
            highlighted = re.sub(r'(@\w+)', f'{Color.BRIGHT_MAGENTA.value}\\1{Color.RESET.value}', highlighted)
        
        elif language.lower() in ["javascript", "js", "typescript", "ts"]:
            # JavaScript keywords
            keywords = r'\b(function|var|let|const|if|else|for|while|do|switch|case|break|continue|return|try|catch|finally|throw|typeof|instanceof|new|this|class|extends|static|async|await|import|export|from|default|null|undefined|true|false)\b'
            highlighted = re.sub(keywords, f'{Color.BRIGHT_BLUE.value}\\1{Color.RESET.value}', highlighted)
            
            # Strings
            highlighted = re.sub(r'(["\'])((?:\\.|(?!\1).)*?)\1', 
                               f'{Color.BRIGHT_GREEN.value}\\1\\2\\1{Color.RESET.value}', highlighted)
            
            # Template literals
            highlighted = re.sub(r'(`)((?:\\.|(?!\1).)*?)\1', 
                               f'{Color.BRIGHT_GREEN.value}\\1\\2\\1{Color.RESET.value}', highlighted)
            
            # Comments
            highlighted = re.sub(r'(//.*?)$', f'{Color.BRIGHT_BLACK.value}\\1{Color.RESET.value}', 
                               highlighted, flags=re.MULTILINE)
            highlighted = re.sub(r'(/\*.*?\*/)', f'{Color.BRIGHT_BLACK.value}\\1{Color.RESET.value}', 
                               highlighted, flags=re.DOTALL)
            
            # Numbers
            highlighted = re.sub(r'\b(\d+\.?\d*)\b', f'{Color.BRIGHT_YELLOW.value}\\1{Color.RESET.value}', highlighted)
        
        elif language.lower() in ["java"]:
            # Java keywords
            keywords = r'\b(public|private|protected|static|final|abstract|synchronized|volatile|transient|native|strictfp|class|interface|extends|implements|enum|if|else|for|while|do|switch|case|break|continue|return|try|catch|finally|throw|throws|new|this|super|instanceof|boolean|byte|char|short|int|long|float|double|void|true|false|null|package|import)\b'
            highlighted = re.sub(keywords, f'{Color.BRIGHT_BLUE.value}\\1{Color.RESET.value}', highlighted)
            
            # Annotations
            highlighted = re.sub(r'(@\w+)', f'{Color.BRIGHT_MAGENTA.value}\\1{Color.RESET.value}', highlighted)
            
            # Strings
            highlighted = re.sub(r'(["\'])((?:\\.|(?!\1).)*?)\1', 
                               f'{Color.BRIGHT_GREEN.value}\\1\\2\\1{Color.RESET.value}', highlighted)
            
            # Comments
            highlighted = re.sub(r'(//.*?)$', f'{Color.BRIGHT_BLACK.value}\\1{Color.RESET.value}', 
                               highlighted, flags=re.MULTILINE)
            highlighted = re.sub(r'(/\*.*?\*/)', f'{Color.BRIGHT_BLACK.value}\\1{Color.RESET.value}', 
                               highlighted, flags=re.DOTALL)
            
            # Numbers
            highlighted = re.sub(r'\b(\d+\.?\d*[fFlLdD]?)\b', f'{Color.BRIGHT_YELLOW.value}\\1{Color.RESET.value}', highlighted)
        
        return highlighted
    
    def comparison_table(self, data: List[Dict[str, Any]], title: str = "Comparison") -> str:
        """Create beautiful comparison table"""
        if not data:
            return "No data to display"
        
        # Calculate column widths
        headers = list(data[0].keys())
        widths = {h: len(str(h)) for h in headers}
        
        for row in data:
            for header in headers:
                widths[header] = max(widths[header], len(str(row.get(header, ''))))
        
        # Add padding
        for header in headers:
            widths[header] += 2
        
        # Build table
        lines = []
        
        # Title
        total_width = sum(widths.values()) + len(headers) * 3 - 1
        title_line = f"╔{'═' * (total_width - 2)}╗"
        lines.append(self._colorize(title_line, Color.BRIGHT_CYAN))
        
        title_text = f"║ {title.center(total_width - 4)} ║"
        lines.append(self._colorize(title_text, Color.BRIGHT_CYAN, Color.BOLD))
        
        # Header separator
        sep_parts = []
        for i, header in enumerate(headers):
            if i == 0:
                sep_parts.append("╠" + "═" * widths[header])
            else:
                sep_parts.append("╦" + "═" * widths[header])
        sep_parts.append("╣")
        lines.append(self._colorize("".join(sep_parts), Color.BRIGHT_CYAN))
        
        # Headers with safe characters
        header_parts = []
        for header in headers:
            safe_width = min(widths[header], 20)
            header_text = str(header).center(safe_width)
            header_parts.append(self._colorize(header_text, Color.BRIGHT_YELLOW, Color.BOLD))
        lines.append("|" + "|".join(header_parts) + "|")
        
        # Header bottom separator
        sep_parts = []
        for i, header in enumerate(headers):
            if i == 0:
                sep_parts.append("╠" + "═" * widths[header])
            else:
                sep_parts.append("╬" + "═" * widths[header])
        sep_parts.append("╣")
        lines.append(self._colorize("".join(sep_parts), Color.BRIGHT_CYAN))
        
        # Data rows
        for i, row in enumerate(data):
            row_parts = []
            for header in headers:
                value = str(row.get(header, ''))
                cell_text = f" {value} ".ljust(widths[header])
                
                # Alternate row colors
                if i % 2 == 0:
                    row_parts.append(self._colorize(cell_text, Color.WHITE))
                else:
                    row_parts.append(self._colorize(cell_text, Color.BRIGHT_BLACK))
            
            lines.append("|" + "|".join(row_parts) + "|")
        
        # Bottom border
        bottom_parts = []
        for i, header in enumerate(headers):
            if i == 0:
                bottom_parts.append("╚" + "═" * widths[header])
            else:
                bottom_parts.append("╩" + "═" * widths[header])
        bottom_parts.append("╝")
        lines.append(self._colorize("".join(bottom_parts), Color.BRIGHT_CYAN))
        
        return "\n".join(lines)
    
    def typing_effect(self, text: str, delay: float = 0.03) -> None:
        """Display text with typing effect"""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()
    
    def transition_effect(self, style: str = "fade") -> None:
        """Show transition between screens"""
        if not self.color_enabled:
            return
        
        width = self.width
        
        if style == "fade":
            # Fade effect with gradient
            for i in range(5):
                brightness = 255 - (i * 50)
                color = Color.rgb(brightness, brightness, brightness)
                print(f"\r{color}{'█' * width}{Color.RESET.value}", end="")
                time.sleep(0.1)
            print(f"\r{' ' * width}\r", end="")
        
        elif style == "wipe":
            # Wipe effect from left to right
            for i in range(width):
                line = "█" * i + " " * (width - i)
                print(f"\r{Color.BRIGHT_CYAN.value}{line}{Color.RESET.value}", end="")
                time.sleep(0.01)
            print(f"\r{' ' * width}\r", end="")
        
        elif style == "matrix":
            # Matrix-style rain effect
            for _ in range(10):
                line = ''.join(random.choice(' █░▒▓') for _ in range(width))
                print(f"\r{Color.BRIGHT_GREEN.value}{line}{Color.RESET.value}", end="")
                time.sleep(0.05)
            print(f"\r{' ' * width}\r", end="")
    
    def sparkline(self, data: List[float], width: int = 20) -> str:
        """Create sparkline chart"""
        if not data:
            return ""
        
        # Normalize data
        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val if max_val != min_val else 1
        
        # Sparkline characters
        sparks = " ▁▂▃▄▅▆▇█"
        
        # Scale data points to fit width
        if len(data) > width:
            # Sample data points
            step = len(data) / width
            sampled = [data[int(i * step)] for i in range(width)]
        else:
            sampled = data
        
        # Convert to sparkline
        result = []
        for value in sampled:
            normalized = (value - min_val) / range_val
            spark_idx = int(normalized * (len(sparks) - 1))
            result.append(sparks[spark_idx])
        
        sparkline = ''.join(result)
        
        if self.color_enabled:
            # Color based on trend
            if len(data) > 1 and data[-1] > data[0]:
                color = Color.BRIGHT_GREEN
            elif len(data) > 1 and data[-1] < data[0]:
                color = Color.BRIGHT_RED
            else:
                color = Color.BRIGHT_YELLOW
            
            sparkline = f"{color.value}{sparkline}{Color.RESET.value}"
        
        return sparkline
    
    def status_icon(self, status: str) -> str:
        """Get colored status icon"""
        icons = {
            "success": ("✓", Color.BRIGHT_GREEN),
            "error": ("✗", Color.BRIGHT_RED),
            "warning": ("⚠", Color.BRIGHT_YELLOW),
            "info": ("ℹ", Color.BRIGHT_BLUE),
            "loading": ("⟳", Color.BRIGHT_CYAN),
            "star": ("★", Color.BRIGHT_YELLOW),
            "heart": ("♥", Color.BRIGHT_RED),
            "fire": ("🔥", Color.BRIGHT_RED),
            "rocket": ("🚀", Color.BRIGHT_CYAN),
            "trophy": ("🏆", Color.BRIGHT_YELLOW)
        }
        
        # Fallback for Windows without Unicode
        ascii_icons = {
            "success": ("[OK]", Color.BRIGHT_GREEN),
            "error": ("[ERR]", Color.BRIGHT_RED),
            "warning": ("[!]", Color.BRIGHT_YELLOW),
            "info": ("[i]", Color.BRIGHT_BLUE),
            "loading": ("[...]", Color.BRIGHT_CYAN),
            "star": ("[*]", Color.BRIGHT_YELLOW),
            "heart": ("[<3]", Color.BRIGHT_RED),
            "fire": ("[HOT]", Color.BRIGHT_RED),
            "rocket": ("[=>]", Color.BRIGHT_CYAN),
            "trophy": ("[#1]", Color.BRIGHT_YELLOW)
        }
        
        # Check Unicode support
        try:
            "✓".encode(sys.stdout.encoding or 'utf-8')
            icon_set = icons
        except:
            icon_set = ascii_icons
        
        icon, color = icon_set.get(status.lower(), ("●", Color.WHITE))
        
        if self.color_enabled:
            return f"{color.value}{icon}{Color.RESET.value}"
        return icon
    
    def menu_interactive(self, title: str, options: List[Tuple[str, str]], 
                        selected: int = 0) -> str:
        """Create interactive menu display"""
        lines = []
        
        # Title with gradient
        title_gradient = self.gradient_text(title, GradientPreset.CYBERPUNK)
        lines.append(f"\n{title_gradient}")
        lines.append(self._colorize("═" * len(title), Color.BRIGHT_CYAN))
        lines.append("")
        
        # Menu options
        for i, (key, desc) in enumerate(options):
            if i == selected:
                # Highlighted option
                prefix = self.status_icon("star") + " "
                option = f"{prefix}[{key}] {desc}"
                lines.append(self._colorize(option, Color.BRIGHT_YELLOW, Color.BOLD))
            else:
                prefix = "  "
                option = f"{prefix}[{key}] {desc}"
                lines.append(self._colorize(option, Color.WHITE))
        
        lines.append("")
        lines.append(self._colorize("Use ↑↓ arrows to navigate, Enter to select", 
                                   Color.BRIGHT_BLACK))
        
        return "\n".join(lines)
    
    def _colorize(self, text: str, color: Color, style: Optional[Color] = None) -> str:
        """Apply color and style to text"""
        if not self.color_enabled:
            return text
        
        result = color.value
        if style:
            result += style.value
        result += text + Color.RESET.value
        
        return result
    
    def clear_screen(self) -> None:
        """Clear terminal screen"""
        if sys.platform == 'win32':
            os.system('cls')
        else:
            os.system('clear')
    
    def box_fancy(self, content: str, title: str = "", style: str = "double") -> str:
        """Create fancy box with various styles"""
        lines = content.split('\n')
        max_width = max(len(line) for line in lines) if lines else 0
        
        # Box styles
        styles = {
            "single": "┌─┐│└┘",
            "double": "╔═╗║╚╝",
            "rounded": "╭─╮│╰╯",
            "heavy": "┏━┓┃┗┛",
            "ascii": "+-+||++"
        }
        
        chars = styles.get(style, styles["single"])
        tl, h, tr, v, bl, br = chars
        
        # Build box
        box_lines = []
        
        # Top border with title
        if title:
            title_text = f" {title} "
            padding = (max_width - len(title)) // 2
            top = tl + h * padding + title_text + h * (max_width - len(title) - padding) + tr
        else:
            top = tl + h * (max_width + 2) + tr
        
        box_lines.append(self._colorize(top, Color.BRIGHT_CYAN))
        
        # Content lines
        for line in lines:
            padded = line.ljust(max_width)
            content_line = f"{self._colorize(v, Color.BRIGHT_CYAN)} {padded} {self._colorize(v, Color.BRIGHT_CYAN)}"
            box_lines.append(content_line)
        
        # Bottom border
        bottom = bl + h * (max_width + 2) + br
        box_lines.append(self._colorize(bottom, Color.BRIGHT_CYAN))
        
        return "\n".join(box_lines)


class SpinnerContext:
    """Context manager for spinner animation"""
    
    def __init__(self, formatter: BeautifulFormatter, message: str, spinner_chars: str):
        self.formatter = formatter
        self.message = message
        self.spinner_chars = spinner_chars
        self.active = False
        self.thread: Optional[threading.Thread] = None
    
    def __enter__(self):
        self.active = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.active = False
        if self.thread:
            self.thread.join(timeout=0.5)
        # Clear spinner line
        print(f"\r{' ' * (len(self.message) + 10)}\r", end="")
    
    def _animate(self):
        """Animate the spinner"""
        i = 0
        while self.active:
            char = self.spinner_chars[i % len(self.spinner_chars)]
            
            if self.formatter.color_enabled:
                # Rainbow effect for spinner
                colors = [Color.BRIGHT_RED, Color.BRIGHT_YELLOW, Color.BRIGHT_GREEN, 
                         Color.BRIGHT_CYAN, Color.BRIGHT_BLUE, Color.BRIGHT_MAGENTA]
                color = colors[i % len(colors)]
                spinner = f"{color.value}{char}{Color.RESET.value}"
            else:
                spinner = char
            
            print(f"\r{spinner} {self.message}", end="", flush=True)
            time.sleep(0.1)
            i += 1


# Convenience functions
def demo_beautiful_cli():
    """Demo all the beautiful CLI features"""
    formatter = BeautifulFormatter()
    
    # Clear screen
    formatter.clear_screen()
    
    # ASCII art banner with gradient
    print(formatter.gradient_text(
        formatter.ascii_art_banner("ALGORITHMS"), 
        GradientPreset.CYBERPUNK
    ))
    
    print("\n" + formatter.gradient_text("Welcome to the Beautiful CLI Experience!", 
                                         GradientPreset.RAINBOW))
    
    # Fancy box
    print("\n" + formatter.box_fancy(
        "This CLI has all the beautiful features:\n"
        "• Gradient text effects\n"
        "• ASCII art banners\n"
        "• Animated spinners\n"
        "• Syntax highlighting\n"
        "• And much more!",
        title="✨ Features ✨",
        style="double"
    ))
    
    # Progress bar demo
    print("\n" + formatter.progress_bar_animated(75, 100, "Loading modules", "blocks"))
    
    # Sparkline demo
    data = [3, 7, 2, 9, 4, 5, 8, 1, 6, 3, 7, 9]
    print("\nPerformance: " + formatter.sparkline(data))
    
    # Status icons
    print("\n" + formatter.status_icon("success") + " Ready to learn!")
    print(formatter.status_icon("fire") + " Hot streak: 5 days!")
    print(formatter.status_icon("trophy") + " Achievement unlocked!")
    
    # Comparison table
    algorithms = [
        {"Algorithm": "Bubble Sort", "Time": "O(n²)", "Space": "O(1)", "Stable": "Yes"},
        {"Algorithm": "Quick Sort", "Time": "O(n log n)", "Space": "O(log n)", "Stable": "No"},
        {"Algorithm": "Merge Sort", "Time": "O(n log n)", "Space": "O(n)", "Stable": "Yes"},
    ]
    print("\n" + formatter.comparison_table(algorithms, "Sorting Algorithms"))
    
    # Syntax highlighting
    code = """def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)"""
    
    print("\n" + formatter.box_fancy(
        formatter.syntax_highlight(code, "python"),
        title="Python Code",
        style="rounded"
    ))
    
    print("\n" + formatter.gradient_text("Enjoy your beautiful CLI experience! 🚀", 
                                         GradientPreset.SUNSET))


if __name__ == "__main__":
    # Run demo
    demo_beautiful_cli()