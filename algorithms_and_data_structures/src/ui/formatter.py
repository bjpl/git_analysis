#!/usr/bin/env python3
"""
Terminal Formatter - Beautiful terminal formatting with colors

This module now imports from the unified formatter for consistency.
All formatting functionality is centralized in unified_formatter.py
"""

import sys
import os
from typing import Optional, List, Dict, Any, Union, Tuple, Callable
from enum import Enum
from dataclasses import dataclass
import shutil
import time
import threading
import asyncio
import random
import re

# Import everything from unified formatter
try:
    from .unified_formatter import (
        UnifiedFormatter, Color, Theme,
        formatter, success, error, warning, info, header,
        create_box, progress_bar, clear_screen
    )
    UNIFIED_AVAILABLE = True
except ImportError:
    UNIFIED_AVAILABLE = False
# Terminal utilities are now handled by unified formatter
# Keep imports for backward compatibility
try:
    from ..utils.terminal_utils import terminal_utils, get_terminal_width, create_safe_box, wrap_text_safe, calculate_display_width
except ImportError:
    # Provide fallback implementations
    def get_terminal_width():
        return shutil.get_terminal_size((80, 24)).columns
    
    def create_safe_box(content, title=None, width=None):
        if UNIFIED_AVAILABLE:
            return formatter.create_box(content, title, width)
        return '\n'.join(content)
    
    def wrap_text_safe(text, width=None):
        if UNIFIED_AVAILABLE:
            return formatter.wrap_text(text, width)
        return text
    
    def calculate_display_width(text):
        if UNIFIED_AVAILABLE:
            return len(formatter.strip_ansi(text))
        return len(text)
    
    terminal_utils = None
try:
    import msvcrt
except ImportError:
    msvcrt = None

# Import our new components
try:
    from .components.gradient import GradientText, GradientPreset, GradientDirection
    from .components.animations import LoadingAnimation, SpinnerStyle, AnimationSpeed
    from .components.charts import progress_bar as chart_progress_bar, sparkline
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False


# Re-export Color enum from unified formatter if not available
if not UNIFIED_AVAILABLE:
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


# Re-export Theme from unified formatter if not available
if not UNIFIED_AVAILABLE:
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
    """Terminal formatter that wraps UnifiedFormatter for backward compatibility"""
    
    def __init__(self, theme: Optional[Theme] = None, color_enabled: Optional[bool] = None):
        """Initialize terminal formatter
        
        Args:
            theme: Color theme to use
            color_enabled: Override color support detection
        """
        # Use unified formatter if available
        if UNIFIED_AVAILABLE:
            self._formatter = UnifiedFormatter(theme)
            if color_enabled is False:
                UnifiedFormatter.disable_colors()
            elif color_enabled is True:
                UnifiedFormatter.enable_colors()
        else:
            self._formatter = None
            
        self.theme = theme or Theme()
        self._color_enabled = color_enabled
        self.width = self._get_terminal_width()
        
        # Animation state
        self._spinner_active = False
        self._spinner_thread: Optional[threading.Thread] = None
        
        # Progress bar state
        self._progress_bars: Dict[str, Dict[str, Any]] = {}
        
        # Typing animation state
        self._typing_speed = 0.03  # Default typing speed
        self._typing_pause = 0.5   # Pause at sentence breaks
        
        # Initialize enhanced components if available
        if COMPONENTS_AVAILABLE:
            try:
                self.gradient = GradientText(color_enabled=self.color_enabled)
                self.animations = LoadingAnimation(color_enabled=self.color_enabled)
            except:
                self.gradient = None
                self.animations = None
        else:
            self.gradient = None
            self.animations = None
    
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
        """Get terminal width using safe utilities
        
        Returns:
            Terminal width in characters
        """
        return get_terminal_width()
    
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
    
    def success(self, message: str, icon: str = "[OK]") -> str:
        """Format success message
        
        Args:
            message: Success message
            icon: Success icon
            
        Returns:
            Formatted success message
        """
        formatted = f"{icon} {message}"
        colored = self._colorize(formatted, self.theme.success, Color.BOLD)
        return colored
    
    def error(self, message: str, icon: str = "[ERROR]") -> str:
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
    
    def warning(self, message: str, icon: str = "[WARN]") -> str:
        """Format warning message
        
        Args:
            message: Warning message
            icon: Warning icon
            
        Returns:
            Formatted warning message
        """
        formatted = f"{icon} {message}"
        colored = self._colorize(formatted, self.theme.warning, Color.BOLD)
        return colored
    
    def info(self, message: str, icon: str = "[INFO]") -> str:
        """Format info message
        
        Args:
            message: Info message
            icon: Info icon
            
        Returns:
            Formatted info message
        """
        formatted = f"{icon} {message}"
        colored = self._colorize(formatted, self.theme.info)
        return colored
    
    def debug(self, message: str, icon: str = "[DEBUG]") -> str:
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
    
    def gradient_text(self, text: str, preset: str = "rainbow") -> str:
        """Apply gradient effect to text
        
        Args:
            text: Text to apply gradient to
            preset: Gradient preset name
            
        Returns:
            Gradient text or plain text if gradients not available
        """
        if not COMPONENTS_AVAILABLE or not self.gradient:
            return text
        
        preset_map = {
            "fire": GradientPreset.FIRE,
            "ocean": GradientPreset.OCEAN,
            "sunset": GradientPreset.SUNSET,
            "forest": GradientPreset.FOREST,
            "purple": GradientPreset.PURPLE,
            "rainbow": GradientPreset.RAINBOW,
            "cyberpunk": GradientPreset.CYBERPUNK,
            "galaxy": GradientPreset.GALAXY
        }
        
        gradient_preset = preset_map.get(preset, GradientPreset.RAINBOW)
        return self.gradient.gradient_text(text, gradient_preset)
    
    def rainbow_text(self, text: str) -> str:
        """Apply rainbow gradient to text"""
        if not COMPONENTS_AVAILABLE or not self.gradient:
            return text
        return self.gradient.rainbow_text(text)
    
    def fire_text(self, text: str) -> str:
        """Apply fire gradient to text"""
        if not COMPONENTS_AVAILABLE or not self.gradient:
            return text
        return self.gradient.fire_text(text)
    
    def ocean_text(self, text: str) -> str:
        """Apply ocean gradient to text"""
        if not COMPONENTS_AVAILABLE or not self.gradient:
            return text
        return self.gradient.ocean_text(text)
    
    def cyberpunk_text(self, text: str) -> str:
        """Apply cyberpunk gradient to text"""
        if not COMPONENTS_AVAILABLE or not self.gradient:
            return text
        return self.gradient.cyberpunk_text(text)
    
    def header(self, title: str, level: int = 1, style: str = "default",
                subtitle: Optional[str] = None, gradient: Optional[str] = None) -> str:
        """Format enhanced header text with multiple styles
        
        Args:
            title: Header title
            level: Header level (1-3)
            style: Header style ('default', 'banner', 'centered', 'boxed')
            subtitle: Optional subtitle text
            gradient: Optional gradient preset for title
            
        Returns:
            Formatted header
        """
        
        # Apply gradient to title if requested
        if gradient and COMPONENTS_AVAILABLE and self.gradient:
            title = self.gradient_text(title, gradient)
        if style == "banner":
            # ASCII banner style
            width = min(80, self.width)
            border_char = "█" if level == 1 else "▓" if level == 2 else "░"
            
            lines = []
            lines.append(border_char * width)
            
            # Center title
            title_line = title.upper().center(width - 4)
            lines.append(f"{border_char} {title_line} {border_char}")
            
            if subtitle:
                subtitle_line = subtitle.center(width - 4)
                lines.append(f"{border_char} {subtitle_line} {border_char}")
            
            lines.append(border_char * width)
            
            formatted = "\n".join(lines)
            colored = self._colorize(formatted, self.theme.primary, Color.BOLD)
            
        elif style == "centered":
            # Centered with decorations
            width = min(80, self.width)
            
            if level == 1:
                decoration = "◆◇◆"
                border = "═" * ((width - len(title) - 8) // 2)
                formatted = f"\n{border} {decoration} {title.upper()} {decoration} {border}\n"
            elif level == 2:
                decoration = "●"
                border = "─" * ((width - len(title) - 6) // 2)
                formatted = f"\n{border} {decoration} {title} {decoration} {border}\n"
            else:
                formatted = f"\n{title.center(width)}\n"
            
            if subtitle:
                formatted += f"{subtitle.center(width)}\n"
            
            colored = self._colorize(formatted, self.theme.secondary, Color.BOLD)
            
        elif style == "boxed":
            # Boxed header
            content = title
            if subtitle:
                content += f"\n{subtitle}"
            
            return self.box(content, style="double" if level == 1 else "single",
                          align="center", padding=2)
            
        else:  # default
            if level == 1:
                # Large header with double border - use simple ASCII
                width = min(len(title) + 8, self.width)
                top_border = "+" + "=" * (width - 2) + "+"
                title_line = f"| {title.upper().center(width - 4)} |"
                
                lines = [top_border, title_line]
                
                if subtitle:
                    subtitle_line = f"| {subtitle.center(width - 4)} |"
                    lines.append(subtitle_line)
                
                bottom_border = "+" + "=" * (width - 2) + "+"
                lines.append(bottom_border)
                
                formatted = "\n" + "\n".join(lines) + "\n"
                colored = self._colorize(formatted, self.theme.primary, Color.BOLD)
                
            elif level == 2:
                # Medium header with single border - use simple ASCII
                formatted = f"\n+-- {title} --+\n"
                if subtitle:
                    formatted += f"  {subtitle}\n"
                formatted += "+" + "-" * (len(title) + 4) + "+\n"
                colored = self._colorize(formatted, self.theme.secondary, Color.BOLD)
                
            else:
                # Small header with arrow - use simple ASCII
                formatted = f"\n> {title}"
                if subtitle:
                    formatted += f"\n  {subtitle}"
                formatted += "\n"
                colored = self._colorize(formatted, self.theme.text, Color.BOLD)
        
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
        
        lines.append(" | ".join(header_parts))
        
        # Separator
        sep_parts = ["-" * widths[header] for header in headers]
        separator = "-+-".join(sep_parts)
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
            
            lines.append(" | ".join(row_parts))
        
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
           style: str = "single", padding: int = 2, width: Optional[int] = None,
           align: str = "left", color: Optional[Color] = None) -> str:
        """Draw an enhanced box around content with safe formatting
        
        Args:
            content: Content to box
            title: Optional box title
            style: Box style (ignored for safety, uses ASCII)
            padding: Internal padding for content (used by safe box)
            width: Fixed width for the box (auto-calculated if None)
            align: Text alignment (handled by safe box)
            color: Box border color (uses theme primary if None)
            
        Returns:
            Boxed content string
        """
        # Use safe box creation that handles all edge cases
        safe_box = create_safe_box(content, title, width)
        
        # Apply color if specified
        border_color = color or self.theme.primary
        colored_box = self._colorize(safe_box, border_color)
        
        print(colored_box)
        return colored_box
    
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
            # Ornate frame with decorations - use ASCII
            top = "+" + "=" * (frame_width - 2) + "+"
            framed_lines.append(self._colorize(top, Color.BRIGHT_MAGENTA))
            
            # Add margin lines
            for _ in range(margin):
                margin_line = "|" + " " * (frame_width - 2) + "|"
                framed_lines.append(self._colorize(margin_line, Color.BRIGHT_MAGENTA))
            
            # Content lines
            for line in lines:
                padded = line.center(max_width)
                full_line = "| " + " " * margin + padded + " " * margin + " |"
                framed_lines.append(self._colorize(full_line, Color.BRIGHT_MAGENTA))
            
            # Bottom margin
            for _ in range(margin):
                margin_line = "|" + " " * (frame_width - 2) + "|"
                framed_lines.append(self._colorize(margin_line, Color.BRIGHT_MAGENTA))
            
            bottom = "+" + "=" * (frame_width - 2) + "+"
            framed_lines.append(self._colorize(bottom, Color.BRIGHT_MAGENTA))
            
        elif style == "minimal":
            # Minimal frame
            for line in lines:
                framed_line = f"  {line}  "
                framed_lines.append(self._colorize(framed_line, self.theme.text))
            
        else:  # simple
            # Simple frame
            border = "+" + "-" * (frame_width - 2) + "+"
            framed_lines.append(self._colorize(border, self.theme.muted))
            
            for line in lines:
                padded = line.center(max_width)
                full_line = "|" + " " * margin + padded + " " * margin + "|"
                framed_lines.append(full_line)
            
            framed_lines.append(self._colorize(border, self.theme.muted))
        
        result = "\n".join(framed_lines)
        print(result)
        return result
    
    def panel(self, sections: List[Tuple[str, str]], title: Optional[str] = None) -> str:
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
        lines.append(self._colorize(title_line, self.theme.primary, Color.BOLD))
        
        # Process sections
        for i, (header, content) in enumerate(sections):
            # Section header
            if header:
                header_line = f"| {header}"
                header_line = header_line.ljust(panel_width - 1) + "|"
                lines.append(self._colorize(header_line, self.theme.secondary, Color.BOLD))
                
                # Divider under header
                divider = "+" + "-" * (panel_width - 2) + "+"
                lines.append(self._colorize(divider, self.theme.muted))
            
            # Content lines
            content_lines = content.split('\n')
            for line in content_lines:
                # Wrap long lines
                if len(line) > panel_width - 4:
                    wrapped = self._wrap_text(line, panel_width - 4)
                    for wrap_line in wrapped:
                        content_line = f"| {wrap_line.ljust(panel_width - 3)}|"
                        lines.append(content_line)
                else:
                    content_line = f"| {line.ljust(panel_width - 3)}|"
                    lines.append(content_line)
            
            # Add section separator if not last section
            if i < len(sections) - 1:
                separator = "+" + "-" * (panel_width - 2) + "+"
                lines.append(self._colorize(separator, self.theme.muted))
        
        # Panel bottom
        bottom_line = "+" + "=" * (panel_width - 2) + "+"
        lines.append(self._colorize(bottom_line, self.theme.primary, Color.BOLD))
        
        panel_str = "\n".join(lines)
        print(panel_str)
        return panel_str
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to specified width using safe utilities
        
        Args:
            text: Text to wrap
            width: Maximum line width
            
        Returns:
            List of wrapped lines
        """
        return wrap_text_safe(text, width)
    
    def rule(self, title: Optional[str] = None, char: str = "─", style: str = "single") -> str:
        """Draw an enhanced horizontal rule with various styles
        
        Args:
            title: Optional title in the middle of the rule
            char: Character to use for the rule
            style: Rule style ('single', 'double', 'thick', 'dotted', 'gradient')
            
        Returns:
            Formatted rule string
        """
        # Select rule characters based on style - use ASCII for Windows
        if style == "double":
            char = "="
            left_cap = "["
            right_cap = "]"
        elif style == "thick":
            char = "="
            left_cap = "["
            right_cap = "]"
        elif style == "dotted":
            char = "."
            left_cap = "["
            right_cap = "]"
        elif style == "gradient":
            # Create a gradient effect with ASCII
            gradient_chars = "...==="
            char = gradient_chars
            left_cap = "<"
            right_cap = ">"
        else:
            char = "-"
            left_cap = "["
            right_cap = "]"
        
        rule_width = min(self.width, 80)  # Cap at 80 chars for readability
        
        if title:
            # Format title with spacing
            formatted_title = f" {title} "
            title_len = len(formatted_title)
            
            if style == "gradient":
                # Special gradient rule with ASCII
                left_gradient = "...==="
                right_gradient = "===..."
                padding = (rule_width - title_len - 2) // 2
                
                rule_line = left_gradient * (padding // 6) + formatted_title + right_gradient * (padding // 6)
            else:
                padding = (rule_width - title_len - 4) // 2
                remaining = rule_width - title_len - 4 - padding
                
                rule_line = left_cap + char * padding + formatted_title + char * remaining + right_cap
            
            colored_rule = self._colorize(rule_line, self.theme.secondary, Color.BOLD)
        else:
            if style == "gradient":
                # Full gradient with ASCII
                rule_line = "...===" * (rule_width // 6)
            else:
                rule_line = char * rule_width
            
            colored_rule = self._colorize(rule_line, self.theme.muted)
        
        print(colored_rule)
        return colored_rule
    
    def enhanced_spinner(self, message: str = "Loading...", 
                        style: str = "dots") -> 'EnhancedSpinnerContext':
        """Create enhanced spinner with more styles
        
        Args:
            message: Spinner message
            style: Spinner style name
            
        Returns:
            Enhanced spinner context manager
        """
        if not COMPONENTS_AVAILABLE:
            return SpinnerContext(self, message, "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏")
        
        style_map = {
            "dots": SpinnerStyle.DOTS,
            "dots2": SpinnerStyle.DOTS2,
            "circles": SpinnerStyle.CIRCLES,
            "arrows": SpinnerStyle.ARROWS,
            "bars": SpinnerStyle.BARS,
            "blocks": SpinnerStyle.BLOCKS,
            "bounce": SpinnerStyle.BOUNCE,
            "clock": SpinnerStyle.CLOCK,
            "moon": SpinnerStyle.MOON,
            "earth": SpinnerStyle.EARTH,
            "ascii_dots": SpinnerStyle.ASCII_DOTS,
            "ascii_bars": SpinnerStyle.ASCII_BARS,
            "ascii_arrows": SpinnerStyle.ASCII_ARROWS
        }
        
        spinner_style = style_map.get(style, SpinnerStyle.DOTS)
        animation = LoadingAnimation(spinner_style, color_enabled=self.color_enabled)
        return EnhancedSpinnerContext(animation, message)
    
    def syntax_highlight(self, code: str, language: str = "python") -> str:
        """Apply basic syntax highlighting to code
        
        Args:
            code: Code to highlight
            language: Programming language
            
        Returns:
            Syntax highlighted code
        """
        if not self.color_enabled:
            return code
        
        # Basic syntax highlighting patterns
        if language.lower() == "python":
            # Keywords
            keywords = r'\b(def|class|if|else|elif|for|while|try|except|import|from|return|pass|break|continue|with|as|in|not|and|or|is|None|True|False)\b'
            code = re.sub(keywords, r'\033[94m\1\033[0m', code)
            
            # Strings
            code = re.sub(r'(["\'])([^"\']*)\1', r'\033[92m\1\2\1\033[0m', code)
            
            # Comments
            code = re.sub(r'(#.*)', r'\033[90m\1\033[0m', code)
            
            # Numbers
            code = re.sub(r'\b(\d+)\b', r'\033[93m\1\033[0m', code)
        
        elif language.lower() == "javascript":
            # Keywords
            keywords = r'\b(function|var|let|const|if|else|for|while|try|catch|return|class|extends|import|export|from|default|async|await|true|false|null|undefined)\b'
            code = re.sub(keywords, r'\033[94m\1\033[0m', code)
            
            # Strings
            code = re.sub(r'(["\'])([^"\']*)\1', r'\033[92m\1\2\1\033[0m', code)
            
            # Comments
            code = re.sub(r'(//.*)', r'\033[90m\1\033[0m', code)
            
            # Numbers
            code = re.sub(r'\b(\d+)\b', r'\033[93m\1\033[0m', code)
        
        return code
    
    def difficulty_badge(self, difficulty: str) -> str:
        """Create a color-coded difficulty badge
        
        Args:
            difficulty: Difficulty level
            
        Returns:
            Colored difficulty badge
        """
        difficulty_lower = difficulty.lower()
        
        if difficulty_lower in ['easy', 'beginner', 'basic']:
            return self._colorize(f"[{difficulty.upper()}]", Color.BRIGHT_GREEN, Color.BOLD)
        elif difficulty_lower in ['medium', 'intermediate', 'normal']:
            return self._colorize(f"[{difficulty.upper()}]", Color.BRIGHT_YELLOW, Color.BOLD)
        elif difficulty_lower in ['hard', 'advanced', 'expert']:
            return self._colorize(f"[{difficulty.upper()}]", Color.BRIGHT_RED, Color.BOLD)
        elif difficulty_lower in ['extreme', 'master', 'nightmare']:
            return self._colorize(f"[{difficulty.upper()}]", Color.BRIGHT_MAGENTA, Color.BOLD)
        else:
            return self._colorize(f"[{difficulty.upper()}]", Color.WHITE, Color.BOLD)
    
    def progress_with_eta(self, current: int, total: int, description: str = "",
                         start_time: Optional[float] = None) -> str:
        """Create progress bar with ETA calculation
        
        Args:
            current: Current progress
            total: Total items
            description: Progress description
            start_time: Start time for ETA calculation
            
        Returns:
            Progress bar with ETA
        """
        if total <= 0:
            return description
        
        progress = current / total
        bar_length = 30
        filled_length = int(bar_length * progress)
        
        # Create bar
        if self.color_enabled:
            filled = self._colorize("█" * filled_length, Color.BRIGHT_GREEN)
            empty = self._colorize("░" * (bar_length - filled_length), Color.BRIGHT_BLACK)
        else:
            filled = "#" * filled_length
            empty = "-" * (bar_length - filled_length)
        
        bar = filled + empty
        
        # Calculate ETA
        eta_str = ""
        if start_time and current > 0:
            elapsed = time.time() - start_time
            rate = current / elapsed
            if rate > 0:
                eta_seconds = (total - current) / rate
                if eta_seconds < 60:
                    eta_str = f" ETA: {eta_seconds:.0f}s"
                elif eta_seconds < 3600:
                    eta_str = f" ETA: {eta_seconds/60:.0f}m"
                else:
                    eta_str = f" ETA: {eta_seconds/3600:.1f}h"
        
        # Format percentage
        percentage = f"{progress * 100:6.1f}%"
        if self.color_enabled:
            percentage = self._colorize(percentage, Color.BRIGHT_CYAN, Color.BOLD)
        
        return f"{description} [{bar}] {percentage} ({current}/{total}){eta_str}"
    
    def sparkline_chart(self, data: List[float], width: int = 20) -> str:
        """Create a compact sparkline chart
        
        Args:
            data: Data points
            width: Chart width
            
        Returns:
            Sparkline chart
        """
        if not COMPONENTS_AVAILABLE or not data:
            return "No data"
        
        spark = sparkline(data)
        return spark.render()
    
    def status_indicator(self, status: str, message: str = "") -> str:
        """Create a status indicator with color coding
        
        Args:
            status: Status type
            message: Optional status message
            
        Returns:
            Colored status indicator
        """
        status_lower = status.lower()
        
        if status_lower in ['success', 'ok', 'pass', 'complete', 'done']:
            icon = "✓" if self._supports_unicode() else "[OK]"
            colored = self._colorize(f"{icon} {status.upper()}", Color.BRIGHT_GREEN, Color.BOLD)
        elif status_lower in ['error', 'fail', 'failed', 'crash']:
            icon = "✗" if self._supports_unicode() else "[ERR]"
            colored = self._colorize(f"{icon} {status.upper()}", Color.BRIGHT_RED, Color.BOLD)
        elif status_lower in ['warning', 'warn', 'caution']:
            icon = "⚠" if self._supports_unicode() else "[WRN]"
            colored = self._colorize(f"{icon} {status.upper()}", Color.BRIGHT_YELLOW, Color.BOLD)
        elif status_lower in ['info', 'note', 'tip']:
            icon = "ℹ" if self._supports_unicode() else "[INF]"
            colored = self._colorize(f"{icon} {status.upper()}", Color.BRIGHT_BLUE, Color.BOLD)
        elif status_lower in ['pending', 'wait', 'loading']:
            icon = "⟳" if self._supports_unicode() else "[...]"
            colored = self._colorize(f"{icon} {status.upper()}", Color.BRIGHT_CYAN, Color.BOLD)
        else:
            icon = "●" if self._supports_unicode() else "[*]"
            colored = self._colorize(f"{icon} {status.upper()}", Color.WHITE, Color.BOLD)
        
        if message:
            return f"{colored} {message}"
        return colored
    
    def _supports_unicode(self) -> bool:
        """Check if terminal supports Unicode characters"""
        try:
            test_chars = "✓✗⚠ℹ⟳"
            for char in test_chars:
                char.encode(sys.stdout.encoding or 'utf-8')
            return True
        except (UnicodeEncodeError, LookupError):
            return False


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


class AnimatedProgressBar:
    """Animated progress bar with visual effects"""
    
    def __init__(self, formatter: TerminalFormatter, total: int, 
                 description: str, style: str = "blocks"):
        self.formatter = formatter
        self.total = total
        self.description = description
        self.style = style
        self.current = 0
        self.bar_length = 40
        self.animation_frame = 0
    
    async def update(self, amount: int = 1):
        """Update progress bar with animation
        
        Args:
            amount: Amount to increment progress
        """
        self.current = min(self.current + amount, self.total)
        await self._render_animated()
    
    async def _render_animated(self):
        """Render the animated progress bar"""
        if not self.formatter.color_enabled:
            # Simple text progress for non-color terminals
            percent = (self.current / self.total) * 100
            print(f"\r{self.description}: {self.current}/{self.total} ({percent:.1f}%)", 
                  end="", flush=True)
            return
        
        # Calculate progress
        percent = self.current / self.total if self.total > 0 else 0
        filled_length = int(self.bar_length * percent)
        
        # Create animated progress bar based on style
        if self.style == "blocks":
            filled = "█" * filled_length
            empty = "░" * (self.bar_length - filled_length)
        elif self.style == "dots":
            filled = "●" * filled_length
            empty = "○" * (self.bar_length - filled_length)
        elif self.style == "arrows":
            filled = "►" * filled_length
            empty = "─" * (self.bar_length - filled_length)
        elif self.style == "pulse":
            # Pulsing animation
            pulse_chars = ["◐", "◓", "◑", "◒"]
            pulse_char = pulse_chars[self.animation_frame % len(pulse_chars)]
            filled = "█" * max(0, filled_length - 1) + (pulse_char if filled_length > 0 else "")
            empty = "░" * (self.bar_length - filled_length)
            self.animation_frame += 1
        else:
            filled = "#" * filled_length
            empty = "-" * (self.bar_length - filled_length)
        
        # Color the progress bar
        bar_colored = (self.formatter._colorize(filled, self.formatter.theme.success) +
                      self.formatter._colorize(empty, self.formatter.theme.muted))
        
        # Format percentage with color gradient
        percent_val = percent * 100
        if percent_val >= 80:
            percent_color = Color.BRIGHT_GREEN
        elif percent_val >= 50:
            percent_color = Color.BRIGHT_YELLOW
        else:
            percent_color = Color.BRIGHT_RED
        
        percent_str = f"{percent_val:6.1f}%"
        percent_colored = self.formatter._colorize(percent_str, percent_color, Color.BOLD)
        
        # Complete line
        line = f"\r{self.description} [{bar_colored}] {percent_colored} ({self.current}/{self.total})"
        print(line, end="", flush=True)
        
        # Brief animation delay for pulse effect
        if self.style == "pulse":
            await asyncio.sleep(0.1)
        
        # Print newline when complete
        if self.current >= self.total:
            print()


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
        
        # Create progress bar using ASCII
        bar = "#" * filled_length + "-" * (self.bar_length - filled_length)
        bar_colored = (self.formatter._colorize("#" * filled_length, 
                                               self.formatter.theme.success) +
                      self.formatter._colorize("-" * (self.bar_length - filled_length), 
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

    async def type_text(self, text: str, speed: Optional[float] = None, 
                       pause_on_punctuation: bool = True, 
                       cursor_char: str = "▌") -> str:
        """Display text with typing animation effect
        
        Args:
            text: Text to type out
            speed: Typing speed in seconds per character
            pause_on_punctuation: Whether to pause on sentence breaks
            cursor_char: Character to use as cursor
            
        Returns:
            The complete text
        """
        if not self.color_enabled:
            print(text)
            return text
        
        typing_speed = speed or self._typing_speed
        displayed_text = ""
        
        try:
            # Enable cursor hiding if possible
            if hasattr(sys.stdout, 'write'):
                sys.stdout.write('\033[?25l')  # Hide cursor
                sys.stdout.flush()
            
            for i, char in enumerate(text):
                displayed_text += char
                
                # Display current text with animated cursor
                cursor_color = self._colorize(cursor_char, Color.BRIGHT_YELLOW, Color.BLINK)
                line = f"\r{displayed_text}{cursor_color}"
                sys.stdout.write(line)
                sys.stdout.flush()
                
                # Variable speed based on character
                if char in '.!?':
                    await asyncio.sleep(self._typing_pause if pause_on_punctuation else typing_speed)
                elif char in ',;:':
                    await asyncio.sleep(typing_speed * 2)
                elif char == ' ':
                    await asyncio.sleep(typing_speed * 0.5)
                else:
                    await asyncio.sleep(typing_speed)
            
            # Clear cursor and show final text
            sys.stdout.write(f"\r{displayed_text}")
            sys.stdout.flush()
            
        finally:
            # Re-enable cursor
            if hasattr(sys.stdout, 'write'):
                sys.stdout.write('\033[?25h')  # Show cursor
                sys.stdout.flush()
        
        print()  # New line
        return text
    
    def get_key_input(self) -> str:
        """Get single key input (cross-platform)
        
        Returns:
            Key pressed as string
        """
        if os.name == 'nt':
            # Windows implementation
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\xe0':  # Arrow key prefix
                    key = msvcrt.getch()
                    if key == b'H':  # Up arrow
                        return 'UP'
                    elif key == b'P':  # Down arrow
                        return 'DOWN'
                    elif key == b'K':  # Left arrow
                        return 'LEFT'
                    elif key == b'M':  # Right arrow
                        return 'RIGHT'
                elif key == b'\r':  # Enter
                    return 'ENTER'
                elif key == b'\x1b':  # Escape
                    return 'ESCAPE'
                else:
                    return key.decode('utf-8', errors='ignore')
        else:
            # Unix/Linux implementation
            import termios
            import tty
            
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                key = sys.stdin.read(1)
                if key == '\x1b':  # Escape sequence
                    key += sys.stdin.read(2)
                    if key == '\x1b[A':
                        return 'UP'
                    elif key == '\x1b[B':
                        return 'DOWN'
                    elif key == '\x1b[C':
                        return 'RIGHT'
                    elif key == '\x1b[D':
                        return 'LEFT'
                elif key == '\r' or key == '\n':
                    return 'ENTER'
                elif key == '\x1b':
                    return 'ESCAPE'
                else:
                    return key
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
        return ''
    
    async def animated_progress_bar(self, total: int, description: str = "",
                                  style: str = "blocks") -> 'AnimatedProgressBar':
        """Create an animated progress bar with visual effects
        
        Args:
            total: Total number of items
            description: Progress description
            style: Animation style ('blocks', 'dots', 'arrows', 'pulse')
            
        Returns:
            Animated progress bar instance
        """
        return AnimatedProgressBar(self, total, description, style)
    
    def create_menu(self, title: str, options: List[Tuple[str, str, str]], 
                   selected_index: int = 0, show_numbers: bool = True) -> str:
        """Create a navigable menu with arrow key support
        
        Args:
            title: Menu title
            options: List of (key, icon, description) tuples
            selected_index: Currently selected option index
            show_numbers: Whether to show number shortcuts
            
        Returns:
            Formatted menu string
        """
        lines = []
        
        # Title
        lines.append(self._colorize(f"\n{title}", self.theme.primary, Color.BOLD))
        lines.append(self._colorize("═" * len(title), self.theme.primary))
        lines.append("")
        
        # Options
        for i, (key, icon, desc) in enumerate(options):
            if i == selected_index:
                # Highlighted option
                prefix = "► "
                option_text = f"{prefix}{icon} {desc}"
                if show_numbers:
                    option_text = f"[{key}] {option_text}"
                lines.append(self._colorize(option_text, Color.BRIGHT_YELLOW, Color.BOLD))
            else:
                # Normal option
                prefix = "  "
                option_text = f"{prefix}{icon} {desc}"
                if show_numbers:
                    option_text = f"[{key}] {option_text}"
                lines.append(self._colorize(option_text, self.theme.text))
        
        lines.append("")
        lines.append(self._colorize("Use ↑↓ arrows to navigate, Enter to select, or type number", 
                                   self.theme.muted))
        
        return "\n".join(lines)
    
    def transition_effect(self, effect_type: str = "fade") -> None:
        """Display transition effect between screens
        
        Args:
            effect_type: Type of transition ('fade', 'slide', 'wipe')
        """
        if not self.color_enabled:
            return
        
        if effect_type == "fade":
            # Fade effect using transparency simulation
            chars = ["█", "▓", "▒", "░", " "]
            for char in chars:
                print(f"\r{char * self.width}", end="")
                time.sleep(0.1)
        
        elif effect_type == "slide":
            # Slide effect
            for i in range(self.width):
                line = " " * i + "█" * (self.width - i)
                print(f"\r{line}", end="")
                time.sleep(0.02)
        
        elif effect_type == "wipe":
            # Wipe effect
            for i in range(10):
                pattern = "▌" * (i + 1)
                print(f"\r{pattern.center(self.width)}", end="")
                time.sleep(0.1)
        
        # Clear the line
        print(f"\r{' ' * self.width}\r", end="")


class EnhancedSpinnerContext:
    """Enhanced spinner context manager with more animation options"""
    
    def __init__(self, animation, message: str):
        self.animation = animation
        self.message = message
        self.spinner_context = None
    
    def __enter__(self):
        if COMPONENTS_AVAILABLE:
            self.spinner_context = self.animation.spinner(self.message)
            return self.spinner_context.__enter__()
        else:
            # Fallback to basic spinner
            print(f"{self.message}...")
            return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.spinner_context:
            return self.spinner_context.__exit__(exc_type, exc_val, exc_tb)
        else:
            print("Done!")


# Export Formatter class for backward compatibility
Formatter = TerminalFormatter

# If unified formatter is available, use it directly
if UNIFIED_AVAILABLE:
    from .unified_formatter import Formatter as UnifiedFormatterClass
    # Override with unified formatter for better compatibility
    Formatter = UnifiedFormatterClass

