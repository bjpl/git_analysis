#!/usr/bin/env python3
"""
Comprehensive tests for UI formatter enhancements with cross-platform compatibility.

This test suite covers:
- Color gradient rendering across different terminals
- Cross-platform terminal compatibility (Windows, Linux, macOS)
- Color support detection and fallbacks
- Terminal width and capability detection
- Animation and styling features
- Error handling for limited terminals
"""

import pytest
import sys
import os
import io
import time
import asyncio
import threading
from unittest.mock import Mock, patch, MagicMock, call
from typing import Dict, List, Any, Optional

# Import modules under test
try:
    from src.ui.formatter import (
        TerminalFormatter, Color, Theme, SpinnerContext,
        ProgressBar, AnimatedProgressBar
    )
except ImportError:
    pytest.skip("UI formatter modules not available", allow_module_level=True)


class TestTerminalCompatibility:
    """Test cross-platform terminal compatibility"""
    
    @pytest.fixture
    def formatter(self):
        """Create formatter instance for testing"""
        return TerminalFormatter()
    
    @pytest.fixture
    def mock_terminal_environments(self):
        """Mock different terminal environments"""
        return {
            'windows_cmd': {
                'platform': 'win32',
                'TERM': '',
                'NO_COLOR': None,
                'FORCE_COLOR': None,
                'isatty': True,
                'colorama_available': False
            },
            'windows_powershell': {
                'platform': 'win32',
                'TERM': 'xterm-256color',
                'NO_COLOR': None,
                'FORCE_COLOR': None,
                'isatty': True,
                'colorama_available': True
            },
            'windows_terminal': {
                'platform': 'win32',
                'TERM': 'xterm-256color',
                'NO_COLOR': None,
                'FORCE_COLOR': '1',
                'isatty': True,
                'colorama_available': True
            },
            'linux_bash': {
                'platform': 'linux',
                'TERM': 'xterm-256color',
                'NO_COLOR': None,
                'FORCE_COLOR': None,
                'isatty': True,
                'colorama_available': False
            },
            'macos_terminal': {
                'platform': 'darwin',
                'TERM': 'xterm-256color',
                'NO_COLOR': None,
                'FORCE_COLOR': None,
                'isatty': True,
                'colorama_available': False
            },
            'ci_environment': {
                'platform': 'linux',
                'TERM': 'dumb',
                'NO_COLOR': '1',
                'FORCE_COLOR': None,
                'isatty': False,
                'colorama_available': False
            },
            'limited_terminal': {
                'platform': 'linux',
                'TERM': 'vt100',
                'NO_COLOR': None,
                'FORCE_COLOR': None,
                'isatty': True,
                'colorama_available': False
            }
        }
    
    def test_color_detection_windows_cmd(self, formatter, mock_terminal_environments):
        """Test color detection in Windows Command Prompt"""
        env = mock_terminal_environments['windows_cmd']
        
        with patch('sys.platform', env['platform']), \
             patch('sys.stdout.isatty', return_value=env['isatty']), \
             patch.dict(os.environ, {'TERM': env['TERM']}, clear=True), \
             patch('importlib.import_module', side_effect=ImportError):
            
            formatter._color_enabled = None  # Reset detection
            assert not formatter.color_enabled
    
    def test_color_detection_windows_powershell(self, formatter, mock_terminal_environments):
        """Test color detection in Windows PowerShell"""
        env = mock_terminal_environments['windows_powershell']
        
        mock_colorama = MagicMock()
        
        with patch('sys.platform', env['platform']), \
             patch('sys.stdout.isatty', return_value=env['isatty']), \
             patch.dict(os.environ, {'TERM': env['TERM']}, clear=True), \
             patch('importlib.import_module', return_value=mock_colorama):
            
            formatter._color_enabled = None  # Reset detection
            assert formatter.color_enabled
    
    def test_color_detection_windows_terminal(self, formatter, mock_terminal_environments):
        """Test color detection in Windows Terminal"""
        env = mock_terminal_environments['windows_terminal']
        
        with patch('sys.platform', env['platform']), \
             patch('sys.stdout.isatty', return_value=env['isatty']), \
             patch.dict(os.environ, {
                'TERM': env['TERM'], 
                'FORCE_COLOR': env['FORCE_COLOR']
            }, clear=True):
            
            formatter._color_enabled = None  # Reset detection
            assert formatter.color_enabled
    
    def test_color_detection_linux_bash(self, formatter, mock_terminal_environments):
        """Test color detection in Linux Bash"""
        env = mock_terminal_environments['linux_bash']
        
        with patch('sys.platform', env['platform']), \
             patch('sys.stdout.isatty', return_value=env['isatty']), \
             patch.dict(os.environ, {'TERM': env['TERM']}, clear=True):
            
            formatter._color_enabled = None  # Reset detection
            assert formatter.color_enabled
    
    def test_color_detection_macos_terminal(self, formatter, mock_terminal_environments):
        """Test color detection in macOS Terminal"""
        env = mock_terminal_environments['macos_terminal']
        
        with patch('sys.platform', env['platform']), \
             patch('sys.stdout.isatty', return_value=env['isatty']), \
             patch.dict(os.environ, {'TERM': env['TERM']}, clear=True):
            
            formatter._color_enabled = None  # Reset detection
            assert formatter.color_enabled
    
    def test_color_detection_ci_environment(self, formatter, mock_terminal_environments):
        """Test color detection in CI environment (should disable colors)"""
        env = mock_terminal_environments['ci_environment']
        
        with patch('sys.platform', env['platform']), \
             patch('sys.stdout.isatty', return_value=env['isatty']), \
             patch.dict(os.environ, {
                'TERM': env['TERM'],
                'NO_COLOR': env['NO_COLOR']
            }, clear=True):
            
            formatter._color_enabled = None  # Reset detection
            assert not formatter.color_enabled
    
    def test_color_detection_limited_terminal(self, formatter, mock_terminal_environments):
        """Test color detection in limited terminal"""
        env = mock_terminal_environments['limited_terminal']
        
        with patch('sys.platform', env['platform']), \
             patch('sys.stdout.isatty', return_value=env['isatty']), \
             patch.dict(os.environ, {'TERM': env['TERM']}, clear=True):
            
            formatter._color_enabled = None  # Reset detection
            # Should still enable colors for vt100
            assert formatter.color_enabled
    
    @pytest.mark.parametrize("width,expected", [
        (80, 80),
        (120, 120),
        (40, 40),
        (None, 80)  # Default fallback
    ])
    def test_terminal_width_detection(self, formatter, width, expected):
        """Test terminal width detection with various scenarios"""
        if width is None:
            with patch('shutil.get_terminal_size', side_effect=OSError):
                detected_width = formatter._get_terminal_width()
        else:
            mock_size = MagicMock()
            mock_size.columns = width
            with patch('shutil.get_terminal_size', return_value=mock_size):
                detected_width = formatter._get_terminal_width()
        
        assert detected_width == expected
    
    def test_colorama_initialization_on_windows(self, formatter):
        """Test that colorama is properly initialized on Windows"""
        mock_colorama = MagicMock()
        
        with patch('sys.platform', 'win32'), \
             patch('sys.stdout.isatty', return_value=True), \
             patch('importlib.import_module', return_value=mock_colorama):
            
            formatter._color_enabled = None  # Reset detection
            _ = formatter.color_enabled  # Trigger detection
            
            # Colorama should be imported and initialized
            mock_colorama.init.assert_called_once()


class TestColorGradientRendering:
    """Test color gradient rendering functionality"""
    
    @pytest.fixture
    def formatter(self):
        return TerminalFormatter()
    
    def test_gradient_rule_rendering(self, formatter):
        """Test gradient rule rendering"""
        with patch.object(formatter, 'color_enabled', True):
            gradient_rule = formatter.rule(title="Test", style="gradient")
            
            # Should contain gradient pattern
            assert "..." in gradient_rule or "===" in gradient_rule
            assert "Test" in gradient_rule
    
    def test_gradient_rule_fallback(self, formatter):
        """Test gradient rule fallback for no-color terminals"""
        with patch.object(formatter, 'color_enabled', False):
            gradient_rule = formatter.rule(title="Test", style="gradient")
            
            # Should not contain ANSI codes
            assert '\033[' not in gradient_rule
            assert "Test" in gradient_rule
    
    def test_box_drawing_ascii_compatibility(self, formatter):
        """Test that box drawing uses ASCII characters for compatibility"""
        content = "Test content"
        
        # Test different box styles
        styles = ['single', 'double', 'rounded', 'heavy', 'ascii']
        
        for style in styles:
            box = formatter.box(content, style=style)
            
            # Should use ASCII-compatible characters
            assert '+' in box or '#' in box  # Corner characters
            assert '-' in box or '=' in box  # Horizontal lines
            assert '|' in box or '#' in box  # Vertical lines
            
            # Should not use Unicode box drawing characters
            unicode_chars = ['┌', '┐', '└', '┘', '─', '│', '╭', '╮', '╯', '╰']
            for char in unicode_chars:
                assert char not in box
    
    def test_frame_ascii_compatibility(self, formatter):
        """Test that frames use ASCII characters"""
        content = "Test content"
        
        styles = ['simple', 'ornate', 'minimal']
        
        for style in styles:
            frame = formatter.frame(content, style=style)
            
            # Should use ASCII-compatible characters
            if style == 'ornate':
                assert '+' in frame and '=' in frame and '|' in frame
            elif style == 'simple':
                assert '+' in frame and '-' in frame and '|' in frame


class TestAnimationFeatures:
    """Test animation features and frame rates"""
    
    @pytest.fixture
    def formatter(self):
        return TerminalFormatter()
    
    @pytest.mark.asyncio
    async def test_animated_progress_bar_creation(self, formatter):
        """Test creation of animated progress bar"""
        progress_bar = await formatter.animated_progress_bar(100, "Test", "blocks")
        
        assert isinstance(progress_bar, AnimatedProgressBar)
        assert progress_bar.total == 100
        assert progress_bar.description == "Test"
        assert progress_bar.style == "blocks"
    
    @pytest.mark.asyncio
    async def test_animated_progress_bar_styles(self, formatter):
        """Test different animated progress bar styles"""
        styles = ['blocks', 'dots', 'arrows', 'pulse']
        
        for style in styles:
            progress_bar = await formatter.animated_progress_bar(10, f"Test {style}", style)
            
            # Test update
            with patch('builtins.print'):
                await progress_bar.update(5)
            
            assert progress_bar.current == 5
    
    @pytest.mark.asyncio
    async def test_progress_bar_animation_timing(self, formatter):
        """Test progress bar animation timing for pulse effect"""
        progress_bar = await formatter.animated_progress_bar(10, "Test", "pulse")
        
        start_time = time.time()
        
        with patch('builtins.print'), \
             patch('asyncio.sleep') as mock_sleep:
            await progress_bar.update(1)
        
        # Pulse effect should trigger sleep
        if progress_bar.style == "pulse":
            mock_sleep.assert_called_with(0.1)
    
    def test_spinner_animation_performance(self, formatter):
        """Test spinner animation performance"""
        with formatter.spinner("Testing...") as spinner:
            # Let it run briefly
            time.sleep(0.2)
            
            # Should not consume excessive CPU
            assert spinner.active
        
        # Should stop after context exit
        assert not spinner.active
    
    @pytest.mark.asyncio
    async def test_typing_animation_speed(self, formatter):
        """Test typing animation speed control"""
        if not hasattr(formatter, 'type_text'):
            pytest.skip("Typing animation not available in this formatter")
        
        text = "Hello World"
        start_time = time.time()
        
        with patch('sys.stdout.write'), \
             patch('sys.stdout.flush'):
            result = await formatter.type_text(text, speed=0.01)
        
        duration = time.time() - start_time
        
        # Should complete in reasonable time
        assert duration < 2.0  # Allow some overhead
        assert result == text
    
    def test_transition_effects_performance(self, formatter):
        """Test transition effects don't block too long"""
        effects = ['fade', 'slide', 'wipe']
        
        for effect in effects:
            start_time = time.time()
            
            with patch('builtins.print'), \
                 patch('time.sleep') as mock_sleep:
                formatter.transition_effect(effect)
            
            duration = time.time() - start_time
            
            # Should complete quickly (not counting mocked sleeps)
            assert duration < 0.1
            
            # Should have called sleep for animation
            assert mock_sleep.called


class TestMenuNavigation:
    """Test menu navigation functionality"""
    
    @pytest.fixture
    def formatter(self):
        return TerminalFormatter()
    
    def test_menu_creation(self, formatter):
        """Test menu creation with proper formatting"""
        options = [
            ("1", "🏠", "Home", "Go to home"),
            ("2", "⚙️", "Settings", "Configure app"),
            ("q", "🚪", "Quit", "Exit application")
        ]
        
        menu = formatter.create_menu("Main Menu", options, selected_index=0)
        
        # Should contain all options
        for key, icon, title, desc in options:
            assert title in menu
            assert icon in menu
        
        # Should show selection indicator
        assert "►" in menu or ">" in menu
    
    def test_menu_selection_highlighting(self, formatter):
        """Test menu selection highlighting"""
        options = [("1", "📚", "Learn"), ("2", "🎯", "Practice")]
        
        # Test different selected indices
        menu_0 = formatter.create_menu("Test", options, selected_index=0)
        menu_1 = formatter.create_menu("Test", options, selected_index=1)
        
        # Different selections should produce different output
        assert menu_0 != menu_1
    
    def test_menu_with_numbers(self, formatter):
        """Test menu with number shortcuts"""
        options = [("1", "📚", "Learn")]
        
        menu_with_numbers = formatter.create_menu("Test", options, show_numbers=True)
        menu_without_numbers = formatter.create_menu("Test", options, show_numbers=False)
        
        assert "[1]" in menu_with_numbers
        assert "[1]" not in menu_without_numbers
    
    @pytest.mark.skipif(os.name == 'nt', reason="Key input testing not reliable on Windows in CI")
    def test_key_input_handling(self, formatter):
        """Test key input handling for navigation"""
        if not hasattr(formatter, 'get_key_input'):
            pytest.skip("Key input not available in this formatter")
        
        # Mock keyboard input
        with patch('sys.stdin.read', return_value='\x1b[A'):  # Up arrow
            key = formatter.get_key_input()
            assert key == 'UP'
        
        with patch('sys.stdin.read', return_value='\r'):  # Enter
            key = formatter.get_key_input()
            assert key == 'ENTER'


class TestProgressBarUpdates:
    """Test progress bar update functionality"""
    
    @pytest.fixture
    def formatter(self):
        return TerminalFormatter()
    
    def test_progress_bar_creation(self, formatter):
        """Test progress bar creation"""
        progress_bar = formatter.progress_bar(100, "Test Progress")
        
        assert isinstance(progress_bar, ProgressBar)
        assert progress_bar.total == 100
        assert progress_bar.description == "Test Progress"
        assert progress_bar.current == 0
    
    def test_progress_bar_updates(self, formatter):
        """Test progress bar update functionality"""
        progress_bar = formatter.progress_bar(100, "Test")
        
        with patch('builtins.print'):
            # Test increment
            progress_bar.update(25)
            assert progress_bar.current == 25
            
            # Test another increment
            progress_bar.update(25)
            assert progress_bar.current == 50
            
            # Test setting absolute value
            progress_bar.set_progress(75)
            assert progress_bar.current == 75
    
    def test_progress_bar_overflow_protection(self, formatter):
        """Test progress bar overflow protection"""
        progress_bar = formatter.progress_bar(100, "Test")
        
        with patch('builtins.print'):
            # Test overflow protection
            progress_bar.update(150)
            assert progress_bar.current == 100  # Should not exceed total
            
            # Test negative protection
            progress_bar.set_progress(-10)
            assert progress_bar.current == 0  # Should not go below 0
    
    def test_progress_bar_completion(self, formatter):
        """Test progress bar completion behavior"""
        progress_bar = formatter.progress_bar(100, "Test")
        
        with patch('builtins.print') as mock_print:
            progress_bar.update(100)
            progress_bar.finish()
            
            # Should have printed newline on completion
            assert any('\n' in str(call) for call in mock_print.call_args_list)
        
        # Should be removed from tracking
        assert progress_bar.bar_id not in formatter._progress_bars
    
    def test_multiple_progress_bars(self, formatter):
        """Test multiple progress bars tracking"""
        bar1 = formatter.progress_bar(100, "Task 1", "bar1")
        bar2 = formatter.progress_bar(50, "Task 2", "bar2")
        
        assert "bar1" in formatter._progress_bars
        assert "bar2" in formatter._progress_bars
        
        with patch('builtins.print'):
            bar1.update(50)
            bar2.update(25)
        
        assert formatter._progress_bars["bar1"]["current"] == 50
        assert formatter._progress_bars["bar2"]["current"] == 25


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.fixture
    def formatter(self):
        return TerminalFormatter()
    
    def test_color_detection_error_handling(self, formatter):
        """Test error handling in color detection"""
        with patch('sys.stdout.isatty', side_effect=Exception("Test error")):
            formatter._color_enabled = None  # Reset detection
            
            # Should handle error gracefully and return default
            color_enabled = formatter.color_enabled
            assert isinstance(color_enabled, bool)
    
    def test_terminal_width_error_handling(self, formatter):
        """Test error handling in terminal width detection"""
        with patch('shutil.get_terminal_size', side_effect=OSError("No terminal")):
            width = formatter._get_terminal_width()
            assert width == 80  # Should fall back to default
    
    def test_spinner_thread_safety(self, formatter):
        """Test spinner thread safety and cleanup"""
        spinner = formatter.spinner("Test")
        
        # Test multiple enters/exits
        with spinner:
            assert spinner.active
        
        assert not spinner.active
        
        # Test rapid start/stop
        for _ in range(5):
            with spinner:
                time.sleep(0.01)
            assert not spinner.active
    
    def test_print_error_handling(self, formatter):
        """Test error handling when print fails"""
        with patch('builtins.print', side_effect=OSError("Print failed")):
            # Should not raise exception
            try:
                formatter.success("Test message")
                formatter.error("Test error")
                formatter.warning("Test warning")
                formatter.info("Test info")
            except OSError:
                pytest.fail("Formatter should handle print errors gracefully")
    
    def test_box_text_overflow_handling(self, formatter):
        """Test box text overflow handling"""
        long_content = "x" * 200  # Very long content
        
        box = formatter.box(long_content, width=50)
        
        # Should handle overflow gracefully
        lines = box.split('\n')
        for line in lines:
            # Remove ANSI codes for length check
            clean_line = line
            while '\033[' in clean_line:
                start = clean_line.find('\033[')
                end = clean_line.find('m', start)
                if end != -1:
                    clean_line = clean_line[:start] + clean_line[end+1:]
                else:
                    break
            
            # Should not exceed reasonable width
            assert len(clean_line) <= 60  # Some padding for borders


class TestFallbackModes:
    """Test fallback modes for limited terminals"""
    
    @pytest.fixture
    def formatter_no_color(self):
        formatter = TerminalFormatter()
        formatter.disable_color()
        return formatter
    
    def test_text_only_messages(self, formatter_no_color):
        """Test text-only message formatting"""
        success_msg = formatter_no_color.success("Test success")
        error_msg = formatter_no_color.error("Test error")
        warning_msg = formatter_no_color.warning("Test warning")
        info_msg = formatter_no_color.info("Test info")
        
        # Should not contain ANSI codes
        for msg in [success_msg, error_msg, warning_msg, info_msg]:
            assert '\033[' not in msg
            assert "Test" in msg
    
    def test_ascii_box_fallback(self, formatter_no_color):
        """Test ASCII box drawing fallback"""
        box = formatter_no_color.box("Test content", style="double")
        
        # Should use ASCII characters only
        assert '+' in box
        assert '=' in box or '-' in box
        assert '|' in box
        assert '\033[' not in box  # No color codes
    
    def test_simple_progress_fallback(self, formatter_no_color):
        """Test simple progress fallback"""
        progress_bar = formatter_no_color.progress_bar(100, "Test")
        
        with patch('builtins.print') as mock_print:
            progress_bar.update(50)
        
        # Should have printed simple text progress
        printed_text = str(mock_print.call_args_list)
        assert "50/100" in printed_text
        assert "50.0%" in printed_text
    
    def test_spinner_fallback(self, formatter_no_color):
        """Test spinner fallback for no-color terminals"""
        with patch('builtins.print') as mock_print:
            with formatter_no_color.spinner("Testing..."):
                time.sleep(0.1)
        
        # Should have printed info message instead of spinner
        mock_print.assert_called()
    
    def test_header_fallback(self, formatter_no_color):
        """Test header fallback formatting"""
        header = formatter_no_color.header("Test Header", level=1, style="banner")
        
        # Should not contain color codes
        assert '\033[' not in header
        # Should still contain the title
        assert "TEST HEADER" in header or "Test Header" in header
    
    def test_table_fallback(self, formatter_no_color):
        """Test table formatting fallback"""
        data = [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25}
        ]
        
        with patch('builtins.print') as mock_print:
            formatter_no_color.table(data)
        
        # Should have printed table without colors
        printed_calls = [str(call) for call in mock_print.call_args_list]
        table_output = ''.join(printed_calls)
        
        assert "John" in table_output
        assert "Jane" in table_output
        assert '\033[' not in table_output


@pytest.mark.integration
class TestFormatterIntegration:
    """Integration tests for formatter with real terminal scenarios"""
    
    def test_formatter_with_redirected_output(self):
        """Test formatter behavior with redirected output"""
        formatter = TerminalFormatter()
        
        # Simulate redirected output
        with patch('sys.stdout.isatty', return_value=False):
            formatter._color_enabled = None  # Reset detection
            assert not formatter.color_enabled
    
    def test_formatter_memory_usage(self):
        """Test formatter doesn't leak memory with repeated use"""
        import gc
        
        formatter = TerminalFormatter()
        
        # Create many progress bars and clean them up
        for i in range(100):
            bar = formatter.progress_bar(100, f"Test {i}")
            with patch('builtins.print'):
                bar.update(100)
                bar.finish()
        
        # Force garbage collection
        gc.collect()
        
        # Should not have accumulated progress bars
        assert len(formatter._progress_bars) == 0
    
    def test_concurrent_spinner_usage(self):
        """Test concurrent spinner usage safety"""
        formatter = TerminalFormatter()
        
        def spinner_worker():
            with formatter.spinner("Worker"):
                time.sleep(0.1)
        
        # Start multiple spinners concurrently
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=spinner_worker)
            threads.append(thread)
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join(timeout=1.0)
        
        # All should complete without error
        for thread in threads:
            assert not thread.is_alive()


class TestPerformanceMetrics:
    """Test performance metrics for UI components"""
    
    @pytest.fixture
    def formatter(self):
        return TerminalFormatter()
    
    def test_color_application_performance(self, formatter):
        """Test color application performance"""
        large_text = "x" * 10000
        
        start_time = time.time()
        
        # Apply color to large text
        colored_text = formatter._colorize(large_text, Color.BRIGHT_GREEN)
        
        duration = time.time() - start_time
        
        # Should complete quickly
        assert duration < 0.1
        assert len(colored_text) > len(large_text)  # Should have color codes
    
    def test_box_rendering_performance(self, formatter):
        """Test box rendering performance"""
        large_content = "\n".join(["Line " + str(i) for i in range(1000)])
        
        start_time = time.time()
        
        with patch('builtins.print'):
            box = formatter.box(large_content, style="single", width=80)
        
        duration = time.time() - start_time
        
        # Should complete in reasonable time
        assert duration < 1.0
        assert "Line 1" in box
        assert "Line 999" in box
    
    def test_table_rendering_performance(self, formatter):
        """Test table rendering performance with large dataset"""
        # Create large dataset
        data = []
        for i in range(1000):
            data.append({
                "id": i,
                "name": f"Item {i}",
                "value": i * 2,
                "description": f"Description for item {i}"
            })
        
        start_time = time.time()
        
        with patch('builtins.print'):
            formatter.table(data)
        
        duration = time.time() - start_time
        
        # Should complete in reasonable time
        assert duration < 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])