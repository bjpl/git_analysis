#!/usr/bin/env python3
"""
Unified CLI Formatting System
Ensures beautiful, consistent formatting across all CLI modules
Based on the elegant patterns from algo_teach.py
"""

from typing import Optional, Any, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
import os

# Rich terminal formatting
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.text import Text
    from rich.columns import Columns
    from rich.align import Align
    from rich.padding import Padding
    from rich import box
    from rich.style import Style
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.tree import Tree
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Fallback to colorama
try:
    from colorama import init, Fore, Back, Style as ColoramaStyle
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


class BoxStyle(Enum):
    """Standardized box styles for different contexts"""
    HEADER = "DOUBLE_EDGE"  # Main headers and titles
    CONTENT = "ROUNDED"      # Regular content panels
    EMPHASIS = "HEAVY_HEAD"  # Important information
    MINIMAL = "MINIMAL"      # Subtle borders
    CODE = "ROUNDED"         # Code blocks


@dataclass
class ColorPalette:
    """Unified color palette for consistent theming"""
    # Primary colors (gradient flow)
    primary_1 = "bold magenta"      # Headers, main titles
    primary_2 = "bright_blue"       # Borders, accents
    primary_3 = "cyan"              # Subtitles, secondary info
    
    # Semantic colors
    success = "bold green"          # Success messages
    warning = "bold yellow"         # Warnings, highlights
    error = "bold red"             # Errors, critical info
    info = "italic cyan"           # Information, tips
    
    # Content colors
    text_primary = "white"         # Main text
    text_secondary = "bright_white" # Secondary text
    text_muted = "dim white"       # Muted text
    
    # Special effects
    gradient_start = "magenta"
    gradient_mid = "cyan"
    gradient_end = "yellow"
    
    # Code syntax
    code_bg = "default"
    code_theme = "monokai"


@dataclass
class Spacing:
    """Consistent spacing and padding values"""
    panel_padding: Tuple[int, int] = (1, 2)  # (vertical, horizontal)
    section_gap: int = 1                      # Lines between sections
    indent: int = 2                           # Standard indentation
    table_width: Optional[int] = None        # Auto-width tables


class CLIFormatter:
    """
    Unified formatter for beautiful CLI output
    Ensures consistent styling across all modules
    """
    
    def __init__(self, force_color: bool = True):
        """Initialize formatter with consistent settings"""
        if force_color:
            os.environ["FORCE_COLOR"] = "1"
            os.environ["COLORTERM"] = "truecolor"
        
        self.console = Console() if RICH_AVAILABLE else None
        self.colors = ColorPalette()
        self.spacing = Spacing()
        self.emojis = {
            # Status indicators
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'rocket': '🚀',
            'sparkles': '✨',
            
            # Progress indicators
            'loading': '⏳',
            'complete': '🎉',
            'working': '⚡',
            
            # Educational
            'learn': '📚',
            'teach': '👨‍🏫',
            'practice': '💪',
            'quiz': '🎯',
            
            # Visual anchors
            'folder': '📁',
            'file': '📄',
            'code': '💻',
            'chart': '📊',
            'bulb': '💡',
            'fire': '🔥',
            'star': '⭐',
            'trophy': '🏆'
        }
    
    def display_header(self, title: str, subtitle: str = "", style: BoxStyle = BoxStyle.HEADER):
        """Display a beautiful header with consistent styling"""
        if RICH_AVAILABLE and self.console:
            # Create gradient-like header
            header_text = Text(title, style=self.colors.primary_1)
            
            if subtitle:
                subtitle_text = Text(subtitle, style=self.colors.info)
                content = Align.center(
                    Columns([header_text, subtitle_text], align="center", expand=True)
                )
            else:
                content = Align.center(header_text)
            
            # Select box style
            box_style = getattr(box, style.value, box.DOUBLE_EDGE)
            
            panel = Panel(
                content,
                box=box_style,
                border_style=self.colors.primary_2,
                padding=self.spacing.panel_padding,
                expand=True
            )
            
            self.console.print()
            self.console.print(panel)
            self.console.print()
            
        elif COLORAMA_AVAILABLE:
            self._colorama_header(title, subtitle)
        else:
            self._plain_header(title, subtitle)
    
    def display_panel(self, content: Any, title: str = "", style: BoxStyle = BoxStyle.CONTENT,
                     border_color: Optional[str] = None):
        """Display content in a beautiful panel"""
        if RICH_AVAILABLE and self.console:
            border_style = border_color or self.colors.primary_2
            box_style = getattr(box, style.value, box.ROUNDED)
            
            panel = Panel(
                content,
                title=title,
                box=box_style,
                border_style=border_style,
                padding=self.spacing.panel_padding,
                expand=False
            )
            
            self.console.print(panel)
            
        elif COLORAMA_AVAILABLE:
            self._colorama_panel(str(content), title)
        else:
            self._plain_panel(str(content), title)
    
    def display_table(self, title: str, columns: List[Dict[str, Any]], 
                     rows: List[List[Any]], style: BoxStyle = BoxStyle.CONTENT):
        """Display a beautiful formatted table"""
        if RICH_AVAILABLE and self.console:
            box_style = getattr(box, style.value, box.ROUNDED)
            
            table = Table(
                title=f"{self.emojis['chart']} {title}",
                box=box_style,
                border_style=self.colors.primary_2,
                header_style=self.colors.primary_1,
                title_style=self.colors.primary_3,
                show_lines=False,
                expand=False
            )
            
            # Add columns
            for col in columns:
                table.add_column(
                    col.get('name', ''),
                    style=col.get('style', self.colors.text_primary),
                    width=col.get('width', None),
                    justify=col.get('justify', 'left')
                )
            
            # Add rows
            for row in rows:
                table.add_row(*[str(cell) for cell in row])
            
            self.console.print(table)
            
        elif COLORAMA_AVAILABLE:
            self._colorama_table(title, columns, rows)
        else:
            self._plain_table(title, columns, rows)
    
    def display_code(self, code: str, title: str = "", language: str = "python"):
        """Display syntax-highlighted code with consistent styling"""
        if RICH_AVAILABLE and self.console:
            syntax = Syntax(
                code,
                language,
                theme=self.colors.code_theme,
                line_numbers=True,
                background_color=self.colors.code_bg
            )
            
            if title:
                panel_title = f"{self.emojis['code']} {title}"
            else:
                panel_title = ""
            
            code_panel = Panel(
                syntax,
                title=panel_title,
                box=getattr(box, BoxStyle.CODE.value),
                border_style=self.colors.primary_2,
                padding=self.spacing.panel_padding
            )
            
            self.console.print(code_panel)
            
        elif COLORAMA_AVAILABLE:
            self._colorama_code(code, title)
        else:
            self._plain_code(code, title)
    
    def display_progress(self, description: str, total: int = 100):
        """Create a beautiful progress bar"""
        if RICH_AVAILABLE:
            return Progress(
                SpinnerColumn(spinner_name="dots", style=self.colors.primary_1),
                TextColumn("[progress.description]{task.description}", style=self.colors.primary_3),
                BarColumn(style=self.colors.primary_2, complete_style=self.colors.success),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%", style=self.colors.warning),
                console=self.console
            )
        else:
            return None
    
    def display_tree(self, title: str, tree_data: Dict[str, Any]):
        """Display a beautiful tree structure"""
        if RICH_AVAILABLE and self.console:
            tree = Tree(
                f"{self.emojis['folder']} {title}",
                style=self.colors.primary_1,
                guide_style=self.colors.primary_2
            )
            
            def add_branches(node, data):
                for key, value in data.items():
                    if isinstance(value, dict):
                        branch = node.add(f"{self.emojis['folder']} {key}", style=self.colors.primary_3)
                        add_branches(branch, value)
                    else:
                        node.add(f"{self.emojis['file']} {key}: {value}", style=self.colors.text_primary)
            
            add_branches(tree, tree_data)
            
            panel = Panel(
                tree,
                box=box.ROUNDED,
                border_style=self.colors.primary_2,
                padding=self.spacing.panel_padding
            )
            
            self.console.print(panel)
            
        else:
            self._plain_tree(title, tree_data)
    
    def create_gradient_text(self, text: str) -> Text:
        """Create text with gradient effect"""
        if RICH_AVAILABLE:
            gradient = Text()
            colors = [self.colors.gradient_start, self.colors.gradient_mid, self.colors.gradient_end]
            
            for i, char in enumerate(text):
                color_idx = int(i / len(text) * len(colors))
                color_idx = min(color_idx, len(colors) - 1)
                gradient.append(char, style=colors[color_idx])
            
            return gradient
        return text
    
    def success(self, message: str):
        """Display success message with consistent styling"""
        if RICH_AVAILABLE and self.console:
            self.console.print(f"{self.emojis['success']} {message}", style=self.colors.success)
        elif COLORAMA_AVAILABLE:
            print(f"{Fore.GREEN}✅ {message}{ColoramaStyle.RESET_ALL}")
        else:
            print(f"✅ {message}")
    
    def error(self, message: str):
        """Display error message with consistent styling"""
        if RICH_AVAILABLE and self.console:
            self.console.print(f"{self.emojis['error']} {message}", style=self.colors.error)
        elif COLORAMA_AVAILABLE:
            print(f"{Fore.RED}❌ {message}{ColoramaStyle.RESET_ALL}")
        else:
            print(f"❌ {message}")
    
    def warning(self, message: str):
        """Display warning message with consistent styling"""
        if RICH_AVAILABLE and self.console:
            self.console.print(f"{self.emojis['warning']} {message}", style=self.colors.warning)
        elif COLORAMA_AVAILABLE:
            print(f"{Fore.YELLOW}⚠️ {message}{ColoramaStyle.RESET_ALL}")
        else:
            print(f"⚠️ {message}")
    
    def info(self, message: str):
        """Display info message with consistent styling"""
        if RICH_AVAILABLE and self.console:
            self.console.print(f"{self.emojis['info']} {message}", style=self.colors.info)
        elif COLORAMA_AVAILABLE:
            print(f"{Fore.CYAN}ℹ️ {message}{ColoramaStyle.RESET_ALL}")
        else:
            print(f"ℹ️ {message}")
    
    # Fallback methods for when Rich is not available
    def _colorama_header(self, title: str, subtitle: str):
        """Colorama fallback for headers"""
        width = 60
        print(f"\n{Fore.MAGENTA}{ColoramaStyle.BRIGHT}{'═'*width}")
        print(f"{Fore.CYAN}{ColoramaStyle.BRIGHT}{title.center(width)}")
        if subtitle:
            print(f"{Fore.YELLOW}{subtitle.center(width)}")
        print(f"{Fore.MAGENTA}{ColoramaStyle.BRIGHT}{'═'*width}{ColoramaStyle.RESET_ALL}\n")
    
    def _plain_header(self, title: str, subtitle: str):
        """Plain text fallback for headers"""
        width = 60
        print(f"\n{'='*width}")
        print(title.center(width))
        if subtitle:
            print(subtitle.center(width))
        print(f"{'='*width}\n")
    
    def _colorama_panel(self, content: str, title: str):
        """Colorama fallback for panels"""
        width = 60
        if title:
            print(f"\n{Fore.CYAN}┌─ {title} {'─'*(width-len(title)-4)}┐")
        else:
            print(f"\n{Fore.CYAN}┌{'─'*width}┐")
        
        for line in content.split('\n'):
            print(f"{Fore.CYAN}│ {Fore.WHITE}{line.ljust(width-2)} {Fore.CYAN}│")
        
        print(f"{Fore.CYAN}└{'─'*width}┘{ColoramaStyle.RESET_ALL}\n")
    
    def _plain_panel(self, content: str, title: str):
        """Plain text fallback for panels"""
        width = 60
        if title:
            print(f"\n+- {title} {'-'*(width-len(title)-4)}+")
        else:
            print(f"\n+{'-'*width}+")
        
        for line in content.split('\n'):
            print(f"| {line.ljust(width-2)} |")
        
        print(f"+{'-'*width}+\n")
    
    def _colorama_table(self, title: str, columns: List[Dict], rows: List[List]):
        """Colorama fallback for tables"""
        print(f"\n{Fore.CYAN}{ColoramaStyle.BRIGHT}{title}")
        print(f"{Fore.BLUE}{'─'*60}")
        
        # Headers
        header_row = " | ".join([col['name'] for col in columns])
        print(f"{Fore.MAGENTA}{header_row}")
        print(f"{Fore.BLUE}{'─'*60}")
        
        # Rows
        for row in rows:
            row_str = " | ".join([str(cell) for cell in row])
            print(f"{Fore.WHITE}{row_str}")
        
        print(f"{Fore.BLUE}{'─'*60}{ColoramaStyle.RESET_ALL}\n")
    
    def _plain_table(self, title: str, columns: List[Dict], rows: List[List]):
        """Plain text fallback for tables"""
        print(f"\n{title}")
        print("-" * 60)
        
        # Headers
        header_row = " | ".join([col['name'] for col in columns])
        print(header_row)
        print("-" * 60)
        
        # Rows
        for row in rows:
            row_str = " | ".join([str(cell) for cell in row])
            print(row_str)
        
        print("-" * 60)
        print()
    
    def _colorama_code(self, code: str, title: str):
        """Colorama fallback for code blocks"""
        if title:
            print(f"\n{Fore.YELLOW}### {title} ###")
        print(f"{Fore.GREEN}```python")
        print(f"{Fore.WHITE}{code}")
        print(f"{Fore.GREEN}```{ColoramaStyle.RESET_ALL}\n")
    
    def _plain_code(self, code: str, title: str):
        """Plain text fallback for code blocks"""
        if title:
            print(f"\n### {title} ###")
        print("```python")
        print(code)
        print("```\n")
    
    def _plain_tree(self, title: str, tree_data: Dict, indent: int = 0):
        """Plain text fallback for tree display"""
        if indent == 0:
            print(f"\n{title}")
            print("-" * 40)
        
        for key, value in tree_data.items():
            print("  " * indent + f"├─ {key}")
            if isinstance(value, dict):
                self._plain_tree("", value, indent + 1)
            else:
                print("  " * (indent + 1) + f"└─ {value}")
    
    def clear_screen(self):
        """Clear the terminal screen"""
        import platform
        os.system('cls' if platform.system() == 'Windows' else 'clear')
    
    def ascii_art_banner(self, text: str) -> str:
        """Create ASCII art banner (simple version)"""
        banner = f"""
    ╔═══════════════════════════════════════╗
    ║  {text.center(35)}  ║
    ╚═══════════════════════════════════════╝
        """
        return banner
    
    def gradient_text(self, text: str, preset=None) -> str:
        """Apply gradient colors to text (simplified for CLIFormatter)"""
        if COLORAMA_AVAILABLE:
            # Use colorama colors based on preset
            if preset and "ocean" in str(preset).lower():
                return f"{Fore.BLUE}{ColoramaStyle.BRIGHT}{text}{ColoramaStyle.RESET_ALL}"
            elif preset and "forest" in str(preset).lower():
                return f"{Fore.GREEN}{ColoramaStyle.BRIGHT}{text}{ColoramaStyle.RESET_ALL}"
            elif preset and "sunset" in str(preset).lower():
                return f"{Fore.YELLOW}{ColoramaStyle.BRIGHT}{text}{ColoramaStyle.RESET_ALL}"
            elif preset and "neon" in str(preset).lower():
                return f"{Fore.MAGENTA}{ColoramaStyle.BRIGHT}{text}{ColoramaStyle.RESET_ALL}"
            elif preset and "rainbow" in str(preset).lower():
                return f"{Fore.RED}{ColoramaStyle.BRIGHT}{text}{ColoramaStyle.RESET_ALL}"
            else:
                # Default cyberpunk style
                return f"{Fore.CYAN}{ColoramaStyle.BRIGHT}{text}{ColoramaStyle.RESET_ALL}"
        else:
            return text


# Singleton instance for easy import
formatter = CLIFormatter()

# Export commonly used functions
display_header = formatter.display_header
display_panel = formatter.display_panel
display_table = formatter.display_table
display_code = formatter.display_code
display_progress = formatter.display_progress
display_tree = formatter.display_tree
success = formatter.success
error = formatter.error
warning = formatter.warning
info = formatter.info