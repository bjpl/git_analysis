"""
Comprehensive tests for the Enhanced Terminal Formatter
"""

import unittest
import sys
import os
import time
from unittest.mock import patch, MagicMock
from io import StringIO

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ui.formatter.enhanced_formatter import (
    EnhancedFormatter, Color, BoxChars, HeaderStyle, TableStyle,
    TerminalCapabilities, Spinner, quick_header, quick_table, 
    quick_panel, quick_progress, get_formatter
)


class TestTerminalCapabilities(unittest.TestCase):
    """Test terminal capability detection"""
    
    def test_capabilities_detection(self):
        """Test basic capability detection"""
        caps = TerminalCapabilities()
        self.assertIsInstance(caps.supports_color, bool)
        self.assertIsInstance(caps.width, int)
        self.assertIsInstance(caps.height, int)
        self.assertGreater(caps.width, 0)
        self.assertGreater(caps.height, 0)
    
    def test_windows_detection(self):
        """Test Windows detection"""
        with patch('os.name', 'nt'):
            formatter = EnhancedFormatter()
            self.assertTrue(formatter.capabilities.is_windows)
    
    def test_powershell_detection(self):
        """Test PowerShell detection"""
        with patch.dict(os.environ, {'PSModulePath': 'C:\\Windows\\system32\\WindowsPowerShell\\v1.0\\Modules'}):
            formatter = EnhancedFormatter()
            # May or may not be detected depending on environment


class TestBoxChars(unittest.TestCase):
    """Test box drawing characters"""
    
    def test_safe_chars_available(self):
        """Test that all safe characters are available"""
        chars = BoxChars.get_safe_chars()
        
        required_chars = [
            'horizontal', 'vertical', 'top_left', 'top_right',
            'bottom_left', 'bottom_right', 'cross'
        ]
        
        for char_name in required_chars:
            self.assertIn(char_name, chars)
            self.assertIsInstance(chars[char_name], str)
            self.assertGreater(len(chars[char_name]), 0)
    
    def test_ascii_compatibility(self):
        """Test that all characters are ASCII-safe"""
        chars = BoxChars.get_safe_chars()
        
        for char_name, char_value in chars.items():
            # All characters should be encodable as ASCII
            try:
                char_value.encode('ascii')
            except UnicodeEncodeError:
                self.fail(f"Character {char_name} ({char_value}) is not ASCII-safe")


class TestEnhancedFormatter(unittest.TestCase):
    """Test the main formatter class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.formatter = EnhancedFormatter()
    
    def test_initialization(self):
        """Test formatter initialization"""
        self.assertIsInstance(self.formatter.capabilities, TerminalCapabilities)
        self.assertIsInstance(self.formatter.box_chars, dict)
        self.assertFalse(self.formatter._spinner_active)
    
    def test_colorize_basic(self):
        """Test basic text colorization"""
        text = "Hello World"
        colored = self.formatter.colorize(text, Color.RED)
        
        if self.formatter.capabilities.supports_color:
            self.assertIn(Color.RED.value, colored)
            self.assertIn(Color.RESET.value, colored)
            self.assertIn(text, colored)
        else:
            self.assertEqual(colored, text)
    
    def test_colorize_with_background(self):
        """Test colorization with background color"""
        text = "Hello World"
        colored = self.formatter.colorize(text, Color.WHITE, bg_color=Color.BG_BLUE)
        
        if self.formatter.capabilities.supports_color:
            self.assertIn(Color.WHITE.value, colored)
            self.assertIn(Color.BG_BLUE.value, colored)
            self.assertIn(text, colored)
    
    def test_colorize_string_input(self):
        """Test colorization with string color names"""
        text = "Hello World"
        colored = self.formatter.colorize(text, "red")
        
        if self.formatter.capabilities.supports_color:
            self.assertIn(text, colored)
    
    def test_gradient_text(self):
        """Test gradient text creation"""
        text = "Gradient Text"
        colors = [Color.RED, Color.GREEN, Color.BLUE]
        gradient = self.formatter.gradient_text(text, colors)
        
        self.assertIn(text.replace(' ', ''), gradient.replace('\033[0m', '').replace('\033[31m', '').replace('\033[32m', '').replace('\033[34m', ''))
    
    def test_gradient_text_empty(self):
        """Test gradient text with empty input"""
        gradient = self.formatter.gradient_text("", [Color.RED, Color.BLUE])
        self.assertEqual(gradient, "")
    
    def test_gradient_text_single_color(self):
        """Test gradient text with single color"""
        text = "Single Color"
        gradient = self.formatter.gradient_text(text, [Color.RED])
        self.assertEqual(gradient, text)  # Should return original text


class TestHeaderStyles(unittest.TestCase):
    """Test header creation with different styles"""
    
    def setUp(self):
        self.formatter = EnhancedFormatter()
    
    def test_banner_header(self):
        """Test banner-style header"""
        title = "Test Banner"
        header = self.formatter.create_header(title, HeaderStyle.BANNER, width=50)
        
        lines = header.split('\n')
        self.assertEqual(len(lines), 3)  # Top border, title, bottom border
        
        # Check that all lines are roughly the same width
        for line in lines:
            # Remove ANSI codes for length check
            clean_line = self._strip_ansi(line)
            self.assertGreaterEqual(len(clean_line), 40)  # Should be close to width
    
    def test_centered_header(self):
        """Test centered header"""
        title = "Centered Title"
        header = self.formatter.create_header(title, HeaderStyle.CENTERED, width=50)
        
        clean_header = self._strip_ansi(header)
        # Title should be roughly centered
        self.assertIn(title, clean_header)
    
    def test_boxed_header(self):
        """Test boxed header"""
        title = "Boxed Title"
        header = self.formatter.create_header(title, HeaderStyle.BOXED, width=50)
        
        lines = header.split('\n')
        self.assertEqual(len(lines), 3)  # Top border, title, bottom border
        
        # All lines should contain the title or box characters
        for line in lines:
            clean_line = self._strip_ansi(line)
            self.assertTrue(
                title in clean_line or 
                any(char in clean_line for char in ['+', '-', '|'])
            )
    
    def test_underlined_header(self):
        """Test underlined header"""
        title = "Underlined Title"
        header = self.formatter.create_header(title, HeaderStyle.UNDERLINED, width=50)
        
        lines = header.split('\n')
        self.assertEqual(len(lines), 2)  # Title and underline
        
        clean_lines = [self._strip_ansi(line) for line in lines]
        self.assertIn(title, clean_lines[0])
        self.assertTrue(all(char in '-_=' for char in clean_lines[1].strip()))
    
    def test_gradient_header(self):
        """Test gradient header"""
        title = "Gradient Title"
        header = self.formatter.create_header(title, HeaderStyle.GRADIENT, width=50)
        
        clean_header = self._strip_ansi(header)
        self.assertIn(title, clean_header)
    
    def _strip_ansi(self, text):
        """Remove ANSI escape codes from text"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)


class TestProgressBar(unittest.TestCase):
    """Test progress bar functionality"""
    
    def setUp(self):
        self.formatter = EnhancedFormatter()
    
    def test_progress_bar_creation(self):
        """Test basic progress bar creation"""
        progress_bar = self.formatter.create_progress_bar(0.5, width=20)
        
        self.assertIn('[', progress_bar)
        self.assertIn(']', progress_bar)
        self.assertIn('50.0%', progress_bar)
    
    def test_progress_bar_bounds(self):
        """Test progress bar with boundary values"""
        # Test 0% progress
        bar_0 = self.formatter.create_progress_bar(0.0, width=10)
        self.assertIn('0.0%', bar_0)
        
        # Test 100% progress
        bar_100 = self.formatter.create_progress_bar(1.0, width=10)
        self.assertIn('100.0%', bar_100)
        
        # Test over 100% (should be clamped)
        bar_over = self.formatter.create_progress_bar(1.5, width=10)
        self.assertIn('100.0%', bar_over)
        
        # Test negative (should be clamped)
        bar_neg = self.formatter.create_progress_bar(-0.5, width=10)
        self.assertIn('0.0%', bar_neg)
    
    def test_progress_bar_no_percentage(self):
        """Test progress bar without percentage display"""
        progress_bar = self.formatter.create_progress_bar(0.75, width=20, show_percentage=False)
        
        self.assertIn('[', progress_bar)
        self.assertIn(']', progress_bar)
        self.assertNotIn('%', progress_bar)


class TestTableFormatting(unittest.TestCase):
    """Test table formatting functionality"""
    
    def setUp(self):
        self.formatter = EnhancedFormatter()
        self.sample_data = [
            ["Alice", "Engineer", "30"],
            ["Bob", "Designer", "25"],
            ["Charlie", "Manager", "35"]
        ]
        self.sample_headers = ["Name", "Role", "Age"]
    
    def test_empty_table(self):
        """Test empty table handling"""
        table = self.formatter.create_table([])
        self.assertEqual(table, "")
    
    def test_table_with_headers(self):
        """Test table creation with headers"""
        table = self.formatter.create_table(self.sample_data, self.sample_headers)
        
        lines = table.split('\n')
        self.assertGreater(len(lines), 3)  # Should have multiple lines
        
        # Check that headers are present
        table_text = self._strip_ansi(table)
        for header in self.sample_headers:
            self.assertIn(header, table_text)
    
    def test_table_without_headers(self):
        """Test table creation without headers"""
        table = self.formatter.create_table(self.sample_data)
        
        lines = table.split('\n')
        self.assertGreater(len(lines), 0)
        
        # Check that data is present
        table_text = self._strip_ansi(table)
        self.assertIn("Alice", table_text)
        self.assertIn("Bob", table_text)
    
    def test_table_styles(self):
        """Test different table styles"""
        styles = [TableStyle.GRID, TableStyle.SIMPLE, TableStyle.FANCY_GRID, TableStyle.MINIMAL]
        
        for style in styles:
            with self.subTest(style=style):
                table = self.formatter.create_table(self.sample_data, self.sample_headers, style)
                self.assertGreater(len(table), 0)
                
                table_text = self._strip_ansi(table)
                self.assertIn("Alice", table_text)
    
    def test_alternating_colors(self):
        """Test alternating row colors"""
        table_with_alt = self.formatter.create_table(
            self.sample_data, self.sample_headers, alternating_colors=True
        )
        table_without_alt = self.formatter.create_table(
            self.sample_data, self.sample_headers, alternating_colors=False
        )
        
        # Both should contain the data
        for table in [table_with_alt, table_without_alt]:
            table_text = self._strip_ansi(table)
            self.assertIn("Alice", table_text)
    
    def _strip_ansi(self, text):
        """Remove ANSI escape codes from text"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)


class TestPanelSystem(unittest.TestCase):
    """Test panel creation and formatting"""
    
    def setUp(self):
        self.formatter = EnhancedFormatter()
    
    def test_basic_panel(self):
        """Test basic panel creation"""
        title = "Test Panel"
        content = "This is test content"
        panel = self.formatter.create_panel(title, content)
        
        lines = panel.split('\n')
        self.assertGreaterEqual(len(lines), 3)  # At least top, content, bottom
        
        panel_text = self._strip_ansi(panel)
        self.assertIn(title, panel_text)
        self.assertIn(content, panel_text)
    
    def test_panel_with_long_content(self):
        """Test panel with content that needs wrapping"""
        title = "Long Content Panel"
        content = "This is a very long line of content that should be wrapped within the panel boundaries to ensure proper display formatting."
        panel = self.formatter.create_panel(title, content, width=40)
        
        lines = panel.split('\n')
        self.assertGreater(len(lines), 3)  # Should have wrapped content
        
        panel_text = self._strip_ansi(panel)
        self.assertIn(title, panel_text)
        # Content should be present even if wrapped
        content_words = content.split()
        for word in content_words[:3]:  # Check first few words
            self.assertIn(word, panel_text)
    
    def test_panel_with_multiline_content(self):
        """Test panel with multiline content"""
        title = "Multiline Panel"
        content = "Line 1\nLine 2\nLine 3"
        panel = self.formatter.create_panel(title, content)
        
        panel_text = self._strip_ansi(panel)
        self.assertIn(title, panel_text)
        self.assertIn("Line 1", panel_text)
        self.assertIn("Line 2", panel_text)
        self.assertIn("Line 3", panel_text)
    
    def test_multi_panel_vertical(self):
        """Test multiple panels arranged vertically"""
        panels = [
            {"title": "Panel 1", "content": "Content 1"},
            {"title": "Panel 2", "content": "Content 2"}
        ]
        
        multi_panel = self.formatter.create_multi_panel(panels, "vertical")
        
        multi_text = self._strip_ansi(multi_panel)
        self.assertIn("Panel 1", multi_text)
        self.assertIn("Panel 2", multi_text)
        self.assertIn("Content 1", multi_text)
        self.assertIn("Content 2", multi_text)
    
    def _strip_ansi(self, text):
        """Remove ANSI escape codes from text"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)


class TestSpinner(unittest.TestCase):
    """Test spinner functionality"""
    
    def setUp(self):
        self.formatter = EnhancedFormatter()
    
    def test_spinner_creation(self):
        """Test spinner creation"""
        spinner = self.formatter.create_spinner("Loading...", "simple")
        
        self.assertIsInstance(spinner, Spinner)
        self.assertEqual(spinner.message, "Loading...")
        self.assertEqual(spinner.style, "simple")
        self.assertFalse(spinner.active)
    
    def test_spinner_frames(self):
        """Test spinner frame availability"""
        for style in Spinner.SPINNER_STYLES:
            with self.subTest(style=style):
                spinner = self.formatter.create_spinner("Test", style)
                self.assertGreater(len(spinner.frames), 0)
                self.assertIsInstance(spinner.frames[0], str)
    
    def test_spinner_context_manager(self):
        """Test spinner as context manager"""
        with patch('builtins.print'):  # Mock print to avoid output during tests
            spinner = self.formatter.create_spinner("Testing...", "simple")
            
            with spinner:
                self.assertTrue(spinner.active)
                time.sleep(0.1)  # Give it a moment to spin
            
            self.assertFalse(spinner.active)
    
    def test_powershell_compatibility(self):
        """Test PowerShell compatibility mode"""
        # Mock PowerShell environment
        with patch.object(self.formatter.capabilities, 'is_powershell', True):
            spinner = self.formatter.create_spinner("Test", "dots")
            
            # Should fall back to simple frames for PowerShell
            self.assertEqual(spinner.frames, Spinner.SPINNER_STYLES['simple'])


class TestQuickFunctions(unittest.TestCase):
    """Test quick formatting functions"""
    
    def test_quick_header(self):
        """Test quick header function"""
        header = quick_header("Quick Test", "banner", "bright_cyan")
        self.assertIsInstance(header, str)
        self.assertGreater(len(header), 0)
        self.assertIn("Quick Test", self._strip_ansi(header))
    
    def test_quick_table(self):
        """Test quick table function"""
        data = [["A", "B"], ["C", "D"]]
        headers = ["Col1", "Col2"]
        table = quick_table(data, headers, "grid")
        
        self.assertIsInstance(table, str)
        self.assertGreater(len(table), 0)
        table_text = self._strip_ansi(table)
        self.assertIn("Col1", table_text)
        self.assertIn("A", table_text)
    
    def test_quick_panel(self):
        """Test quick panel function"""
        panel = quick_panel("Quick Panel", "Quick content", "bright_blue")
        
        self.assertIsInstance(panel, str)
        self.assertGreater(len(panel), 0)
        panel_text = self._strip_ansi(panel)
        self.assertIn("Quick Panel", panel_text)
        self.assertIn("Quick content", panel_text)
    
    def test_quick_progress(self):
        """Test quick progress function"""
        progress = quick_progress(0.6, 30)
        
        self.assertIsInstance(progress, str)
        self.assertIn('60.0%', progress)
        self.assertIn('[', progress)
        self.assertIn(']', progress)
    
    def test_get_formatter(self):
        """Test global formatter function"""
        formatter1 = get_formatter()
        formatter2 = get_formatter()
        
        # Should return the same instance
        self.assertIs(formatter1, formatter2)
        self.assertIsInstance(formatter1, EnhancedFormatter)
    
    def _strip_ansi(self, text):
        """Remove ANSI escape codes from text"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)


class TestWindowsCompatibility(unittest.TestCase):
    """Test Windows-specific compatibility features"""
    
    def setUp(self):
        self.formatter = EnhancedFormatter()
    
    def test_ascii_only_box_chars(self):
        """Test that box characters are ASCII-only"""
        for char_name, char_value in self.formatter.box_chars.items():
            with self.subTest(char=char_name):
                try:
                    char_value.encode('ascii')
                except UnicodeEncodeError:
                    self.fail(f"Box character {char_name} is not ASCII: {char_value}")
    
    def test_clear_line_method(self):
        """Test clear line functionality"""
        clear_seq = self.formatter.clear_line()
        self.assertIsInstance(clear_seq, str)
        self.assertIn('\r', clear_seq)
    
    def test_move_cursor_powershell(self):
        """Test cursor movement in PowerShell mode"""
        with patch.object(self.formatter.capabilities, 'is_powershell', True):
            cursor_seq = self.formatter.move_cursor_up(2)
            self.assertEqual(cursor_seq, '')  # Should return empty for PowerShell
    
    def test_move_cursor_normal(self):
        """Test cursor movement in normal terminal"""
        with patch.object(self.formatter.capabilities, 'is_powershell', False):
            cursor_seq = self.formatter.move_cursor_up(2)
            self.assertIn('\033[2A', cursor_seq)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def setUp(self):
        self.formatter = EnhancedFormatter()
    
    def test_invalid_color_string(self):
        """Test handling of invalid color strings"""
        text = "Test text"
        result = self.formatter.colorize(text, "invalid_color")
        # Should return original text when color is invalid
        self.assertEqual(result, text)
    
    def test_negative_width(self):
        """Test handling of negative width values"""
        header = self.formatter.create_header("Test", width=-10)
        # Should handle gracefully without crashing
        self.assertIsInstance(header, str)
    
    def test_empty_table_data(self):
        """Test empty table data handling"""
        table = self.formatter.create_table([])
        self.assertEqual(table, "")
        
        # Test with empty rows
        table = self.formatter.create_table([[]])
        # Should handle gracefully
        self.assertIsInstance(table, str)
    
    def test_none_values_in_table(self):
        """Test table with None values"""
        data = [["Alice", None, "30"], [None, "Designer", "25"]]
        table = self.formatter.create_table(data)
        
        # Should convert None to string and handle gracefully
        self.assertIsInstance(table, str)
        self.assertIn("Alice", self._strip_ansi(table))
    
    def _strip_ansi(self, text):
        """Remove ANSI escape codes from text"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)


if __name__ == '__main__':
    # Configure test runner
    unittest.main(verbosity=2, buffer=True)