#!/usr/bin/env python3
"""
Terminal Utilities - Comprehensive terminal width detection and box drawing
Fixes terminal box border alignment issues across different terminals and platforms.
"""

import sys
import os
import shutil
import unicodedata
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class BoxStyle(Enum):
    """Box drawing styles with reliable character sets"""
    ASCII = "ascii"
    SINGLE = "single" 
    DOUBLE = "double"
    ROUNDED = "rounded"
    HEAVY = "heavy"
    MINIMAL = "minimal"


@dataclass
class TerminalCapabilities:
    """Terminal capability detection results"""
    width: int
    height: int
    supports_unicode: bool
    supports_color: bool
    supports_256_color: bool
    supports_true_color: bool
    platform: str
    terminal_type: str
    safe_box_style: BoxStyle


class TerminalUtils:
    """Comprehensive terminal utilities for width detection and safe box drawing"""
    
    # Safe box drawing character sets
    BOX_CHARS = {
        BoxStyle.ASCII: {
            'top_left': '+', 'top_right': '+', 'bottom_left': '+', 'bottom_right': '+',
            'horizontal': '-', 'vertical': '|', 'cross': '+', 'tee_down': '+',
            'tee_up': '+', 'tee_right': '+', 'tee_left': '+', 'title_left': '[',
            'title_right': ']'
        },
        BoxStyle.SINGLE: {
            # Use ASCII fallback for maximum compatibility
            'top_left': '+', 'top_right': '+', 'bottom_left': '+', 'bottom_right': '+',
            'horizontal': '-', 'vertical': '|', 'cross': '+', 'tee_down': '+',
            'tee_up': '+', 'tee_right': '+', 'tee_left': '+', 'title_left': '[',
            'title_right': ']'
        },
        BoxStyle.DOUBLE: {
            'top_left': '#', 'top_right': '#', 'bottom_left': '#', 'bottom_right': '#',
            'horizontal': '=', 'vertical': '#', 'cross': '#', 'tee_down': '#',
            'tee_up': '#', 'tee_right': '#', 'tee_left': '#', 'title_left': '<',
            'title_right': '>'
        },
        BoxStyle.ROUNDED: {
            'top_left': '+', 'top_right': '+', 'bottom_left': '+', 'bottom_right': '+',
            'horizontal': '-', 'vertical': '|', 'cross': '+', 'tee_down': '+',
            'tee_up': '+', 'tee_right': '+', 'tee_left': '+', 'title_left': '(',
            'title_right': ')'
        },
        BoxStyle.HEAVY: {
            'top_left': '*', 'top_right': '*', 'bottom_left': '*', 'bottom_right': '*',
            'horizontal': '=', 'vertical': '*', 'cross': '*', 'tee_down': '*',
            'tee_up': '*', 'tee_right': '*', 'tee_left': '*', 'title_left': '<',
            'title_right': '>'
        },
        BoxStyle.MINIMAL: {
            'top_left': ' ', 'top_right': ' ', 'bottom_left': ' ', 'bottom_right': ' ',
            'horizontal': ' ', 'vertical': ' ', 'cross': ' ', 'tee_down': ' ',
            'tee_up': ' ', 'tee_right': ' ', 'tee_left': ' ', 'title_left': ' ',
            'title_right': ' '
        }
    }
    
    def __init__(self):
        """Initialize terminal utilities"""
        self.capabilities = self.detect_terminal_capabilities()
        self._width_cache = {}
        self._width_cache_time = 0
        
    def detect_terminal_capabilities(self) -> TerminalCapabilities:
        """Detect comprehensive terminal capabilities"""
        # Get dimensions
        width, height = self._get_terminal_size()
        
        # Detect platform
        platform = sys.platform
        
        # Detect terminal type
        terminal_type = self._detect_terminal_type()
        
        # Test Unicode support
        supports_unicode = self._test_unicode_support()
        
        # Test color support
        supports_color = self._test_color_support()
        supports_256_color = self._test_256_color_support()
        supports_true_color = self._test_true_color_support()
        
        # Determine safe box style
        safe_box_style = self._determine_safe_box_style(
            platform, terminal_type, supports_unicode
        )
        
        return TerminalCapabilities(
            width=width,
            height=height,
            supports_unicode=supports_unicode,
            supports_color=supports_color,
            supports_256_color=supports_256_color,
            supports_true_color=supports_true_color,
            platform=platform,
            terminal_type=terminal_type,
            safe_box_style=safe_box_style
        )
    
    def _get_terminal_size(self) -> Tuple[int, int]:
        """Get terminal size with multiple fallback methods"""
        # Method 1: shutil.get_terminal_size (most reliable)
        try:
            size = shutil.get_terminal_size()
            if size.columns > 0 and size.lines > 0:
                return size.columns, size.lines
        except (AttributeError, OSError, ValueError):
            pass
        
        # Method 2: os.get_terminal_size (Python 3.3+)
        try:
            size = os.get_terminal_size()
            if size.columns > 0 and size.lines > 0:
                return size.columns, size.lines
        except (AttributeError, OSError, ValueError):
            pass
        
        # Method 3: Environment variables
        try:
            cols = int(os.environ.get('COLUMNS', 0))
            lines = int(os.environ.get('LINES', 0))
            if cols > 0 and lines > 0:
                return cols, lines
        except (ValueError, TypeError):
            pass
        
        # Method 4: Windows-specific
        if sys.platform == 'win32':
            try:
                import ctypes
                from ctypes import wintypes
                
                # Get console screen buffer info
                STD_OUTPUT_HANDLE = -11
                h = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
                
                class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
                    _fields_ = [
                        ("dwSize", wintypes._COORD),
                        ("dwCursorPosition", wintypes._COORD),
                        ("wAttributes", wintypes.WORD),
                        ("srWindow", wintypes.SMALL_RECT),
                        ("dwMaximumWindowSize", wintypes._COORD)
                    ]
                
                csbi = CONSOLE_SCREEN_BUFFER_INFO()
                if ctypes.windll.kernel32.GetConsoleScreenBufferInfo(h, ctypes.byref(csbi)):
                    cols = csbi.srWindow.Right - csbi.srWindow.Left + 1
                    lines = csbi.srWindow.Bottom - csbi.srWindow.Top + 1
                    if cols > 0 and lines > 0:
                        return cols, lines
            except Exception:
                pass
        
        # Method 5: Unix-specific ioctl
        if hasattr(sys.stdin, 'fileno') and sys.platform != 'win32':
            try:
                import fcntl
                import termios
                import struct
                
                # Get window size using ioctl
                h, w, hp, wp = struct.unpack('HHHH',
                    fcntl.ioctl(sys.stdin.fileno(), termios.TIOCGWINSZ,
                    struct.pack('HHHH', 0, 0, 0, 0)))
                if w > 0 and h > 0:
                    return w, h
            except Exception:
                pass
        
        # Fallback to common defaults
        return 80, 24
    
    def _detect_terminal_type(self) -> str:
        """Detect terminal type from environment"""
        term = os.environ.get('TERM', '').lower()
        term_program = os.environ.get('TERM_PROGRAM', '').lower()
        wt_session = os.environ.get('WT_SESSION', '')
        
        # Windows Terminal
        if wt_session or 'windowsterminal' in term_program:
            return 'windows_terminal'
        
        # PowerShell
        if 'powershell' in term_program or sys.platform == 'win32':
            return 'powershell'
        
        # Common terminals
        terminals = {
            'xterm': 'xterm',
            'gnome': 'gnome_terminal',
            'konsole': 'konsole',
            'iterm': 'iterm',
            'vscode': 'vscode'
        }
        
        for key, value in terminals.items():
            if key in term or key in term_program:
                return value
        
        return 'unknown'
    
    def _test_unicode_support(self) -> bool:
        """Test if terminal supports Unicode characters safely"""
        try:
            # Test with common Unicode box characters
            test_chars = ['─', '│', '┌', '└', '┐', '┘', '╔', '╚', '╗', '╝']
            for char in test_chars:
                # Try to encode with terminal encoding
                if sys.stdout.encoding:
                    char.encode(sys.stdout.encoding)
                else:
                    char.encode('utf-8')
            return True
        except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
            return False
    
    def _test_color_support(self) -> bool:
        """Test basic ANSI color support"""
        # Check if we're in a TTY
        if not sys.stdout.isatty():
            return False
        
        # Check for NO_COLOR environment variable
        if os.environ.get('NO_COLOR'):
            return False
        
        # Check for FORCE_COLOR
        if os.environ.get('FORCE_COLOR'):
            return True
        
        # Check TERM variable
        term = os.environ.get('TERM', '').lower()
        color_terms = ['color', 'ansi', 'xterm', 'screen', 'tmux', 'rxvt']
        return any(ct in term for ct in color_terms)
    
    def _test_256_color_support(self) -> bool:
        """Test 256-color support"""
        term = os.environ.get('TERM', '').lower()
        return '256' in term or 'color' in term
    
    def _test_true_color_support(self) -> bool:
        """Test true color (24-bit) support"""
        colorterm = os.environ.get('COLORTERM', '').lower()
        return 'truecolor' in colorterm or '24bit' in colorterm
    
    def _determine_safe_box_style(self, platform: str, terminal: str, unicode_support: bool) -> BoxStyle:
        """Determine safest box drawing style for the terminal"""
        # Always use ASCII for maximum compatibility
        # This prevents Unicode width calculation issues
        if platform == 'win32':
            return BoxStyle.ASCII
        
        # For terminals known to have Unicode issues
        problem_terminals = ['powershell', 'cmd', 'unknown']
        if terminal in problem_terminals:
            return BoxStyle.ASCII
        
        # Even if Unicode is supported, use ASCII to avoid width issues
        return BoxStyle.ASCII
    
    def get_safe_width(self, margin: int = 2) -> int:
        """Get safe terminal width accounting for margins"""
        return max(20, self.capabilities.width - margin)
    
    def calculate_text_width(self, text: str) -> int:
        """Calculate display width of text accounting for Unicode"""
        width = 0
        for char in text:
            # Get Unicode character width
            eaw = unicodedata.east_asian_width(char)
            if eaw in ('F', 'W'):  # Full-width or Wide
                width += 2
            elif eaw in ('H', 'Na', 'N', 'A'):  # Half-width, Narrow, Ambiguous
                width += 1
            # Control characters (Mn, Me, Cc) have width 0
        return width
    
    def truncate_text(self, text: str, max_width: int, suffix: str = "...") -> str:
        """Truncate text to fit within max_width, accounting for Unicode"""
        if self.calculate_text_width(text) <= max_width:
            return text
        
        suffix_width = self.calculate_text_width(suffix)
        target_width = max_width - suffix_width
        
        result = ""
        current_width = 0
        
        for char in text:
            char_width = self.calculate_text_width(char)
            if current_width + char_width > target_width:
                break
            result += char
            current_width += char_width
        
        return result + suffix
    
    def wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to specified width, accounting for Unicode"""
        lines = []
        for line in text.split('\n'):
            if not line:
                lines.append('')
                continue
                
            words = line.split(' ')
            current_line = ""
            current_width = 0
            
            for word in words:
                word_width = self.calculate_text_width(word)
                space_width = 1 if current_line else 0
                
                if current_width + space_width + word_width <= width:
                    if current_line:
                        current_line += ' '
                        current_width += 1
                    current_line += word
                    current_width += word_width
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
                    current_width = word_width
            
            if current_line:
                lines.append(current_line)
        
        return lines
    
    def create_box(self, content: str, title: Optional[str] = None, 
                   width: Optional[int] = None, style: Optional[BoxStyle] = None,
                   padding: int = 1) -> str:
        """Create a properly aligned box with safe characters"""
        if style is None:
            style = self.capabilities.safe_box_style
        
        chars = self.BOX_CHARS[style]
        lines = content.split('\n')
        
        # Calculate dimensions
        if width is None:
            content_width = max(self.calculate_text_width(line) for line in lines) if lines else 0
            title_width = self.calculate_text_width(title) + 4 if title else 0
            width = max(content_width, title_width) + (padding * 2)
        
        # Ensure width fits in terminal
        max_width = self.get_safe_width()
        width = min(width, max_width)
        inner_width = width - 2  # Account for border characters
        content_width = inner_width - (padding * 2)
        
        result = []
        
        # Top border with optional title
        if title:
            title_display = self.truncate_text(title, content_width)
            title_with_brackets = f" {title_display} "
            title_width = self.calculate_text_width(title_with_brackets)
            
            # Center the title
            left_padding = (inner_width - title_width) // 2
            right_padding = inner_width - title_width - left_padding
            
            top_line = (chars['top_left'] + 
                       chars['horizontal'] * left_padding +
                       title_with_brackets +
                       chars['horizontal'] * right_padding +
                       chars['top_right'])
        else:
            top_line = (chars['top_left'] + 
                       chars['horizontal'] * inner_width +
                       chars['top_right'])
        
        result.append(top_line)
        
        # Top padding
        for _ in range(padding):
            padding_line = chars['vertical'] + ' ' * inner_width + chars['vertical']
            result.append(padding_line)
        
        # Content lines
        for line in lines:
            # Wrap line if too long
            wrapped_lines = self.wrap_text(line, content_width)
            for wrapped_line in wrapped_lines:
                # Pad line to exact width
                line_width = self.calculate_text_width(wrapped_line)
                right_padding = content_width - line_width
                
                content_line = (chars['vertical'] + 
                               ' ' * padding + 
                               wrapped_line + 
                               ' ' * right_padding + 
                               ' ' * padding + 
                               chars['vertical'])
                result.append(content_line)
        
        # Bottom padding
        for _ in range(padding):
            padding_line = chars['vertical'] + ' ' * inner_width + chars['vertical']
            result.append(padding_line)
        
        # Bottom border
        bottom_line = (chars['bottom_left'] + 
                      chars['horizontal'] * inner_width +
                      chars['bottom_right'])
        result.append(bottom_line)
        
        return '\n'.join(result)
    
    def create_horizontal_rule(self, title: Optional[str] = None, 
                             width: Optional[int] = None, 
                             char: str = '-') -> str:
        """Create a horizontal rule with optional title"""
        if width is None:
            width = self.get_safe_width()
        
        if title:
            title_display = f" {title} "
            title_width = self.calculate_text_width(title_display)
            
            if title_width < width:
                left_width = (width - title_width) // 2
                right_width = width - title_width - left_width
                return char * left_width + title_display + char * right_width
            else:
                # Title too long, truncate
                truncated_title = self.truncate_text(title, width - 4)
                return f" {truncated_title} "
        else:
            return char * width
    
    def refresh_capabilities(self) -> None:
        """Refresh terminal capabilities (call after window resize)"""
        self.capabilities = self.detect_terminal_capabilities()
        self._width_cache.clear()


# Global instance
terminal_utils = TerminalUtils()


def get_terminal_width(margin: int = 2) -> int:
    """Get safe terminal width with margin"""
    return terminal_utils.get_safe_width(margin)


def create_safe_box(content: str, title: Optional[str] = None, 
                    width: Optional[int] = None) -> str:
    """Create a safe box that works in all terminals"""
    return terminal_utils.create_box(content, title, width)


def calculate_display_width(text: str) -> int:
    """Calculate the display width of text"""
    return terminal_utils.calculate_text_width(text)


def wrap_text_safe(text: str, width: Optional[int] = None) -> List[str]:
    """Safely wrap text to terminal width"""
    if width is None:
        width = get_terminal_width() - 4
    return terminal_utils.wrap_text(text, width)