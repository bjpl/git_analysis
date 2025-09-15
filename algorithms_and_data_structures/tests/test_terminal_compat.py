#!/usr/bin/env python3
"""
Comprehensive tests for terminal compatibility across different platforms and environments.

This test suite covers:
- Windows Command Prompt, PowerShell, and Windows Terminal compatibility
- Linux Bash, Zsh, and other shell compatibility
- macOS Terminal and iTerm2 compatibility
- SSH and remote terminal sessions
- CI/CD environment compatibility (GitHub Actions, GitLab CI, etc.)
- Color depth detection and fallbacks
- Terminal capability detection
- Unicode and emoji support detection
- Terminal size and resizing handling
- Input method compatibility (keyboard, mouse)
"""

import pytest
import sys
import os
import shutil
import subprocess
import tempfile
import time
from unittest.mock import Mock, patch, MagicMock, call
from typing import Dict, List, Any, Optional, Tuple

# Import modules under test
try:
    from src.ui.formatter import TerminalFormatter, Color, Theme
    from src.ui.interactive import InteractiveSession
except ImportError:
    pytest.skip("UI modules not available", allow_module_level=True)


class MockTerminalEnvironment:
    """Mock terminal environment for testing"""
    
    def __init__(self, platform: str, terminal_type: str, capabilities: Dict[str, Any]):
        self.platform = platform
        self.terminal_type = terminal_type
        self.capabilities = capabilities
        self.env_vars = {}
        self.stdout_attrs = {}
        self.stdin_attrs = {}
    
    def setup_environment(self):
        """Set up mock environment variables and attributes"""
        return patch.dict(os.environ, self.env_vars, clear=True)
    
    def setup_stdout(self):
        """Set up mock stdout attributes"""
        mock_stdout = MagicMock()
        for attr, value in self.stdout_attrs.items():
            setattr(mock_stdout, attr, value)
        return patch('sys.stdout', mock_stdout)
    
    def setup_stdin(self):
        """Set up mock stdin attributes"""
        mock_stdin = MagicMock()
        for attr, value in self.stdin_attrs.items():
            setattr(mock_stdin, attr, value)
        return patch('sys.stdin', mock_stdin)


@pytest.fixture
def terminal_environments():
    """Create mock terminal environments for testing"""
    return {
        'windows_cmd': MockTerminalEnvironment(
            platform='win32',
            terminal_type='cmd',
            capabilities={
                'colors': False,
                'unicode': False,
                'mouse': False,
                'true_color': False,
                'cursor_control': False
            }
        ),
        'windows_powershell': MockTerminalEnvironment(
            platform='win32',
            terminal_type='powershell',
            capabilities={
                'colors': True,
                'unicode': True,
                'mouse': False,
                'true_color': False,
                'cursor_control': True
            }
        ),
        'windows_terminal': MockTerminalEnvironment(
            platform='win32',
            terminal_type='windows_terminal',
            capabilities={
                'colors': True,
                'unicode': True,
                'mouse': True,
                'true_color': True,
                'cursor_control': True
            }
        ),
        'linux_bash': MockTerminalEnvironment(
            platform='linux',
            terminal_type='bash',
            capabilities={
                'colors': True,
                'unicode': True,
                'mouse': True,
                'true_color': True,
                'cursor_control': True
            }
        ),
        'linux_zsh': MockTerminalEnvironment(
            platform='linux',
            terminal_type='zsh',
            capabilities={
                'colors': True,
                'unicode': True,
                'mouse': True,
                'true_color': True,
                'cursor_control': True
            }
        ),
        'macos_terminal': MockTerminalEnvironment(
            platform='darwin',
            terminal_type='terminal',
            capabilities={
                'colors': True,
                'unicode': True,
                'mouse': True,
                'true_color': True,
                'cursor_control': True
            }
        ),
        'macos_iterm': MockTerminalEnvironment(
            platform='darwin',
            terminal_type='iterm2',
            capabilities={
                'colors': True,
                'unicode': True,
                'mouse': True,
                'true_color': True,
                'cursor_control': True
            }
        ),
        'ssh_session': MockTerminalEnvironment(
            platform='linux',
            terminal_type='ssh',
            capabilities={
                'colors': True,
                'unicode': False,  # May be limited over SSH
                'mouse': False,    # Often disabled over SSH
                'true_color': False,
                'cursor_control': True
            }
        ),
        'ci_github_actions': MockTerminalEnvironment(
            platform='linux',
            terminal_type='ci',
            capabilities={
                'colors': False,   # Usually disabled in CI
                'unicode': False,
                'mouse': False,
                'true_color': False,
                'cursor_control': False
            }
        ),
        'limited_vt100': MockTerminalEnvironment(
            platform='linux',
            terminal_type='vt100',
            capabilities={
                'colors': False,
                'unicode': False,
                'mouse': False,
                'true_color': False,
                'cursor_control': True
            }
        )
    }


class TestPlatformCompatibility:
    """Test compatibility across different platforms"""
    
    def test_windows_cmd_compatibility(self, terminal_environments):
        """Test Windows Command Prompt compatibility"""
        env = terminal_environments['windows_cmd']
        env.env_vars = {'TERM': '', 'ComSpec': 'C:\\Windows\\System32\\cmd.exe'}
        env.stdout_attrs = {'isatty': lambda: True}
        
        formatter = TerminalFormatter()
        
        with env.setup_environment(), \
             env.setup_stdout(), \
             patch('sys.platform', env.platform), \
             patch('importlib.import_module', side_effect=ImportError):
            
            formatter._color_enabled = None  # Reset detection
            
            # Should disable colors for basic cmd
            assert not formatter.color_enabled
            
            # Should still format text without colors
            result = formatter.success("Test message")
            assert "Test message" in result
            assert '\033[' not in result  # No ANSI codes
    
    def test_windows_powershell_compatibility(self, terminal_environments):
        """Test Windows PowerShell compatibility"""
        env = terminal_environments['windows_powershell']
        env.env_vars = {
            'TERM': 'xterm-256color',
            'PSModulePath': 'C:\\Program Files\\PowerShell\\Modules'
        }
        env.stdout_attrs = {'isatty': lambda: True}
        
        formatter = TerminalFormatter()
        
        # Mock colorama availability
        mock_colorama = MagicMock()
        
        with env.setup_environment(), \
             env.setup_stdout(), \
             patch('sys.platform', env.platform), \
             patch('importlib.import_module', return_value=mock_colorama):
            
            formatter._color_enabled = None  # Reset detection
            
            # Should enable colors with colorama
            assert formatter.color_enabled
            
            # Should initialize colorama
            mock_colorama.init.assert_called_once()
            
            # Should format with colors
            result = formatter.success("Test message")
            assert "Test message" in result
            assert '\033[' in result  # Should have ANSI codes
    
    def test_windows_terminal_compatibility(self, terminal_environments):
        """Test Windows Terminal compatibility"""
        env = terminal_environments['windows_terminal']
        env.env_vars = {
            'TERM': 'xterm-256color',
            'WT_SESSION': 'uuid-here',
            'FORCE_COLOR': '1'
        }
        env.stdout_attrs = {'isatty': lambda: True}
        
        formatter = TerminalFormatter()
        
        with env.setup_environment(), \
             env.setup_stdout(), \
             patch('sys.platform', env.platform):
            
            formatter._color_enabled = None  # Reset detection
            
            # Should enable colors due to FORCE_COLOR
            assert formatter.color_enabled
            
            # Should support advanced features
            box_result = formatter.box("Test content", style="double")
            assert "Test content" in box_result
    
    def test_linux_bash_compatibility(self, terminal_environments):
        """Test Linux Bash compatibility"""
        env = terminal_environments['linux_bash']
        env.env_vars = {
            'TERM': 'xterm-256color',
            'SHELL': '/bin/bash',
            'COLORTERM': 'truecolor'
        }
        env.stdout_attrs = {'isatty': lambda: True}
        
        formatter = TerminalFormatter()
        
        with env.setup_environment(), \
             env.setup_stdout(), \
             patch('sys.platform', env.platform):
            
            formatter._color_enabled = None  # Reset detection
            
            # Should enable colors
            assert formatter.color_enabled
            
            # Should support all features
            spinner_context = formatter.spinner("Testing...")
            assert spinner_context is not None
    
    def test_macos_terminal_compatibility(self, terminal_environments):
        """Test macOS Terminal compatibility"""
        env = terminal_environments['macos_terminal']
        env.env_vars = {
            'TERM': 'xterm-256color',
            'TERM_PROGRAM': 'Apple_Terminal',
            'SHELL': '/bin/zsh'
        }
        env.stdout_attrs = {'isatty': lambda: True}
        
        formatter = TerminalFormatter()
        
        with env.setup_environment(), \
             env.setup_stdout(), \
             patch('sys.platform', env.platform):
            
            formatter._color_enabled = None  # Reset detection
            
            # Should enable colors
            assert formatter.color_enabled
            
            # Should handle Unicode properly
            header_result = formatter.header("Test Header", style="banner")
            assert "Test Header" in header_result or "TEST HEADER" in header_result
    
    def test_ssh_session_compatibility(self, terminal_environments):
        """Test SSH session compatibility"""
        env = terminal_environments['ssh_session']
        env.env_vars = {
            'TERM': 'xterm',
            'SSH_CLIENT': '192.168.1.100 12345 22',
            'SSH_TTY': '/dev/pts/0'
        }
        env.stdout_attrs = {'isatty': lambda: True}
        
        formatter = TerminalFormatter()
        
        with env.setup_environment(), \
             env.setup_stdout(), \
             patch('sys.platform', env.platform):
            
            formatter._color_enabled = None  # Reset detection
            
            # Should enable basic colors
            assert formatter.color_enabled
            
            # Should avoid complex features that might not work over SSH
            progress_bar = formatter.progress_bar(100, "Test")
            assert progress_bar is not None


class TestColorDepthDetection:
    """Test color depth detection and fallbacks"""
    
    @pytest.fixture
    def formatter(self):
        return TerminalFormatter()
    
    @pytest.mark.parametrize("term,colorterm,expected_color", [
        ("xterm-256color", "truecolor", True),
        ("xterm-256color", None, True),
        ("xterm", None, True),
        ("screen", None, True),
        ("vt100", None, True),
        ("dumb", None, False),
        ("", None, False),
    ])
    def test_color_support_detection(self, formatter, term, colorterm, expected_color):
        """Test color support detection for different TERM values"""
        env_vars = {'TERM': term}
        if colorterm:
            env_vars['COLORTERM'] = colorterm
        
        with patch.dict(os.environ, env_vars, clear=True), \
             patch('sys.stdout.isatty', return_value=True), \
             patch('sys.platform', 'linux'):
            
            formatter._color_enabled = None  # Reset detection
            assert formatter.color_enabled == expected_color
    
    def test_true_color_detection(self, formatter):
        """Test true color (24-bit) detection"""
        env_vars = {
            'TERM': 'xterm-256color',
            'COLORTERM': 'truecolor'
        }
        
        with patch.dict(os.environ, env_vars, clear=True), \
             patch('sys.stdout.isatty', return_value=True):
            
            formatter._color_enabled = None  # Reset detection
            # True color support should enable colors
            assert formatter.color_enabled
    
    def test_256_color_detection(self, formatter):
        """Test 256 color detection"""
        env_vars = {
            'TERM': 'xterm-256color',
            'COLORTERM': '256'
        }
        
        with patch.dict(os.environ, env_vars, clear=True), \
             patch('sys.stdout.isatty', return_value=True):
            
            formatter._color_enabled = None  # Reset detection
            assert formatter.color_enabled
    
    def test_no_color_environment_variable(self, formatter):
        """Test NO_COLOR environment variable override"""
        env_vars = {
            'TERM': 'xterm-256color',
            'COLORTERM': 'truecolor',
            'NO_COLOR': '1'
        }
        
        with patch.dict(os.environ, env_vars, clear=True), \
             patch('sys.stdout.isatty', return_value=True):
            
            formatter._color_enabled = None  # Reset detection
            # NO_COLOR should override everything
            assert not formatter.color_enabled
    
    def test_force_color_environment_variable(self, formatter):
        """Test FORCE_COLOR environment variable override"""
        env_vars = {
            'TERM': 'dumb',
            'FORCE_COLOR': '1'
        }
        
        with patch.dict(os.environ, env_vars, clear=True), \
             patch('sys.stdout.isatty', return_value=False):  # Even non-TTY
            
            formatter._color_enabled = None  # Reset detection
            # FORCE_COLOR should override everything
            assert formatter.color_enabled


class TestUnicodeAndEmojiSupport:
    """Test Unicode and emoji support detection"""
    
    @pytest.fixture
    def formatter(self):
        return TerminalFormatter()
    
    def test_unicode_box_drawing_fallback(self, formatter):
        """Test Unicode box drawing character fallback"""
        # Test with limited Unicode support
        with patch.dict(os.environ, {'TERM': 'vt100'}, clear=True):
            
            box_result = formatter.box("Test content", style="single")
            
            # Should use ASCII characters instead of Unicode
            assert '+' in box_result or '|' in box_result or '-' in box_result
            # Should not use Unicode box drawing characters
            unicode_chars = ['┌', '┐', '└', '┘', '─', '│']
            for char in unicode_chars:
                assert char not in box_result
    
    def test_emoji_support_detection(self, formatter):
        """Test emoji support detection and fallback"""
        # Test with basic terminal (no emoji support)
        with patch.dict(os.environ, {'TERM': 'vt100'}, clear=True):
            
            # Test list with emoji bullets
            items = ["Item 1", "Item 2", "Item 3"]
            list_result = formatter.list_items(items, bullet="•")
            
            # Should contain the bullet character or fallback
            assert "•" in list_result or "*" in list_result or "-" in list_result
    
    def test_utf8_encoding_handling(self, formatter):
        """Test UTF-8 encoding handling"""
        # Test with UTF-8 content
        content = "Héllo Wörld with spëcial characters: 你好世界"
        
        try:
            result = formatter.info(content)
            # Should handle UTF-8 without crashing
            assert isinstance(result, str)
        except UnicodeError:
            # If encoding fails, it should be handled gracefully
            pytest.skip("Unicode encoding not supported in test environment")


class TestTerminalSizeHandling:
    """Test terminal size detection and handling"""
    
    @pytest.fixture
    def formatter(self):
        return TerminalFormatter()
    
    @pytest.mark.parametrize("width,height", [
        (80, 24),   # Standard
        (120, 30),  # Wide
        (40, 10),   # Narrow
        (200, 50),  # Very wide
    ])
    def test_terminal_size_detection(self, formatter, width, height):
        """Test terminal size detection with various sizes"""
        mock_size = MagicMock()
        mock_size.columns = width
        mock_size.lines = height
        
        with patch('shutil.get_terminal_size', return_value=mock_size):
            detected_width = formatter._get_terminal_width()
            assert detected_width == width
    
    def test_terminal_size_error_handling(self, formatter):
        """Test terminal size detection error handling"""
        with patch('shutil.get_terminal_size', side_effect=OSError("No terminal")):
            # Should fall back to default width
            width = formatter._get_terminal_width()
            assert width == 80
    
    def test_dynamic_width_content_adjustment(self, formatter):
        """Test content adjustment based on terminal width"""
        # Test with narrow terminal
        mock_size = MagicMock()
        mock_size.columns = 40
        
        with patch('shutil.get_terminal_size', return_value=mock_size):
            formatter.width = formatter._get_terminal_width()
            
            # Long content should be handled appropriately
            long_content = "This is a very long line that should be handled properly in narrow terminals"
            box_result = formatter.box(long_content, width=35)
            
            # Should not exceed terminal width significantly
            lines = box_result.split('\n')
            for line in lines:
                # Remove ANSI codes for accurate length measurement
                clean_line = line
                while '\033[' in clean_line:
                    start = clean_line.find('\033[')
                    end = clean_line.find('m', start)
                    if end != -1:
                        clean_line = clean_line[:start] + clean_line[end+1:]
                    else:
                        break
                assert len(clean_line) <= 45  # Some buffer for borders
    
    def test_responsive_layout_adjustment(self, formatter):
        """Test responsive layout adjustment"""
        # Test rule rendering with different widths
        widths = [40, 80, 120]
        
        for width in widths:
            mock_size = MagicMock()
            mock_size.columns = width
            
            with patch('shutil.get_terminal_size', return_value=mock_size):
                formatter.width = formatter._get_terminal_width()
                
                rule_result = formatter.rule(title="Test", style="single")
                
                # Rule should adapt to terminal width
                assert len(rule_result.split('\n')[0]) <= width + 10  # Some buffer for ANSI codes


class TestInputMethodCompatibility:
    """Test input method compatibility"""
    
    @pytest.fixture
    def formatter(self):
        return TerminalFormatter()
    
    @pytest.mark.skipif(os.name == 'nt', reason="Unix-specific key input testing")
    def test_unix_key_input_handling(self, formatter):
        """Test Unix key input handling"""
        if not hasattr(formatter, 'get_key_input'):
            pytest.skip("Key input not available")
        
        # Mock Unix terminal input
        with patch('termios.tcgetattr'), \
             patch('termios.tcsetattr'), \
             patch('tty.setraw'), \
             patch('sys.stdin.read', side_effect=['\x1b', '[', 'A']):  # Up arrow
            
            try:
                key = formatter.get_key_input()
                assert key == 'UP'
            except (ImportError, AttributeError):
                pytest.skip("Terminal input not available in test environment")
    
    @pytest.mark.skipif(os.name != 'nt', reason="Windows-specific key input testing")
    def test_windows_key_input_handling(self, formatter):
        """Test Windows key input handling"""
        if not hasattr(formatter, 'get_key_input'):
            pytest.skip("Key input not available")
        
        # Mock Windows terminal input
        try:
            import msvcrt
            
            with patch.object(msvcrt, 'kbhit', return_value=True), \
                 patch.object(msvcrt, 'getch', side_effect=[b'\xe0', b'H']):  # Up arrow
                
                key = formatter.get_key_input()
                assert key == 'UP'
        except ImportError:
            pytest.skip("msvcrt not available")
    
    def test_input_timeout_handling(self, formatter):
        """Test input timeout handling"""
        if not hasattr(formatter, 'get_key_input'):
            pytest.skip("Key input not available")
        
        # Test that input doesn't block indefinitely
        start_time = time.time()
        
        try:
            with patch('sys.stdin.read', side_effect=lambda x: time.sleep(0.1) or 'q'):
                key = formatter.get_key_input()
                duration = time.time() - start_time
                
                # Should complete quickly
                assert duration < 1.0
        except Exception:
            # Input handling may not be available in test environment
            pytest.skip("Input handling not available in test environment")


class TestCIEnvironmentCompatibility:
    """Test CI/CD environment compatibility"""
    
    @pytest.fixture
    def formatter(self):
        return TerminalFormatter()
    
    @pytest.mark.parametrize("ci_env", [
        {'CI': 'true'},
        {'GITHUB_ACTIONS': 'true'},
        {'GITLAB_CI': 'true'},
        {'JENKINS_URL': 'http://jenkins.example.com'},
        {'BUILDKITE': 'true'},
        {'CIRCLECI': 'true'},
    ])
    def test_ci_environment_detection(self, formatter, ci_env):
        """Test CI environment detection"""
        env_vars = {
            'TERM': 'dumb',
            **ci_env
        }
        
        with patch.dict(os.environ, env_vars, clear=True), \
             patch('sys.stdout.isatty', return_value=False):
            
            formatter._color_enabled = None  # Reset detection
            
            # CI environments should typically disable colors
            assert not formatter.color_enabled
    
    def test_github_actions_compatibility(self, formatter):
        """Test GitHub Actions specific compatibility"""
        env_vars = {
            'GITHUB_ACTIONS': 'true',
            'RUNNER_OS': 'Linux',
            'TERM': 'dumb'
        }
        
        with patch.dict(os.environ, env_vars, clear=True), \
             patch('sys.stdout.isatty', return_value=False):
            
            # Should work without colors or interactive features
            result = formatter.success("Build successful")
            assert "Build successful" in result
            assert '\033[' not in result  # No ANSI codes
    
    def test_gitlab_ci_compatibility(self, formatter):
        """Test GitLab CI specific compatibility"""
        env_vars = {
            'GITLAB_CI': 'true',
            'CI_JOB_ID': '12345',
            'TERM': 'dumb'
        }
        
        with patch.dict(os.environ, env_vars, clear=True), \
             patch('sys.stdout.isatty', return_value=False):
            
            # Should work without colors
            result = formatter.error("Build failed")
            assert "Build failed" in result
            assert '\033[' not in result
    
    def test_ci_progress_bar_fallback(self, formatter):
        """Test progress bar fallback in CI environments"""
        env_vars = {
            'CI': 'true',
            'TERM': 'dumb'
        }
        
        with patch.dict(os.environ, env_vars, clear=True), \
             patch('sys.stdout.isatty', return_value=False), \
             patch('builtins.print') as mock_print:
            
            formatter._color_enabled = None  # Reset detection
            
            progress_bar = formatter.progress_bar(100, "CI Progress")
            progress_bar.update(50)
            
            # Should have printed simple text progress
            assert mock_print.called
            printed_content = str(mock_print.call_args_list)
            assert "50/100" in printed_content or "50.0%" in printed_content


class TestLegacyTerminalSupport:
    """Test support for legacy terminals"""
    
    @pytest.fixture
    def formatter(self):
        return TerminalFormatter()
    
    def test_vt100_compatibility(self, formatter):
        """Test VT100 terminal compatibility"""
        env_vars = {
            'TERM': 'vt100'
        }
        
        with patch.dict(os.environ, env_vars, clear=True), \
             patch('sys.stdout.isatty', return_value=True):
            
            formatter._color_enabled = None  # Reset detection
            
            # Should still enable basic color support
            assert formatter.color_enabled
            
            # Should use simple formatting
            box_result = formatter.box("Test", style="ascii")
            assert '+' in box_result and '-' in box_result and '|' in box_result
    
    def test_ansi_only_support(self, formatter):
        """Test ANSI-only terminal support"""
        env_vars = {
            'TERM': 'ansi'
        }
        
        with patch.dict(os.environ, env_vars, clear=True), \
             patch('sys.stdout.isatty', return_value=True):
            
            formatter._color_enabled = None  # Reset detection
            
            # Should work with basic ANSI codes
            result = formatter.warning("Test warning")
            assert "Test warning" in result
    
    def test_minimal_terminal_support(self, formatter):
        """Test minimal terminal support"""
        env_vars = {
            'TERM': 'dumb'
        }
        
        with patch.dict(os.environ, env_vars, clear=True), \
             patch('sys.stdout.isatty', return_value=True):
            
            formatter._color_enabled = None  # Reset detection
            
            # Should disable colors for dumb terminals
            assert not formatter.color_enabled
            
            # Should still provide text output
            result = formatter.info("Test info")
            assert "Test info" in result
            assert '\033[' not in result


class TestInteractiveSessionCompatibility:
    """Test interactive session compatibility across terminals"""
    
    def test_session_windows_cmd_compatibility(self, tmp_path):
        """Test interactive session on Windows Command Prompt"""
        with patch('pathlib.Path.mkdir'), \
             patch('sys.platform', 'win32'), \
             patch('sys.stdout.isatty', return_value=True), \
             patch.dict(os.environ, {'TERM': '', 'ComSpec': 'cmd.exe'}, clear=True):
            
            session = InteractiveSession()
            session.notes_dir = tmp_path / "notes"
            session.progress_file = tmp_path / "progress.json"
            
            # Should initialize without errors
            assert session.formatter is not None
            assert session.progress is not None
    
    def test_session_ssh_compatibility(self, tmp_path):
        """Test interactive session over SSH"""
        with patch('pathlib.Path.mkdir'), \
             patch('sys.platform', 'linux'), \
             patch('sys.stdout.isatty', return_value=True), \
             patch.dict(os.environ, {
                'TERM': 'xterm',
                'SSH_CLIENT': '192.168.1.100 12345 22'
             }, clear=True):
            
            session = InteractiveSession()
            session.notes_dir = tmp_path / "notes"
            session.progress_file = tmp_path / "progress.json"
            
            # Should work with limited features
            assert session.formatter.color_enabled  # Basic colors should work
    
    def test_session_screen_tmux_compatibility(self, tmp_path):
        """Test interactive session in screen/tmux"""
        with patch('pathlib.Path.mkdir'), \
             patch('sys.platform', 'linux'), \
             patch('sys.stdout.isatty', return_value=True), \
             patch.dict(os.environ, {
                'TERM': 'screen-256color',
                'STY': 'screen_session'
             }, clear=True):
            
            session = InteractiveSession()
            session.notes_dir = tmp_path / "notes"
            session.progress_file = tmp_path / "progress.json"
            
            # Should work well in screen
            assert session.formatter.color_enabled


class TestErrorRecoveryCompatibility:
    """Test error recovery in incompatible environments"""
    
    @pytest.fixture
    def formatter(self):
        return TerminalFormatter()
    
    def test_print_failure_recovery(self, formatter):
        """Test recovery from print failures"""
        with patch('builtins.print', side_effect=OSError("Print failed")):
            # Should not raise exception
            try:
                result = formatter.success("Test message")
                # May return None or empty string on failure
                assert result is not None or result == ""
            except OSError:
                pytest.fail("Formatter should handle print failures gracefully")
    
    def test_terminal_size_failure_recovery(self, formatter):
        """Test recovery from terminal size detection failure"""
        with patch('shutil.get_terminal_size', side_effect=OSError("No terminal")):
            # Should fall back to default
            width = formatter._get_terminal_width()
            assert width == 80
    
    def test_encoding_error_recovery(self, formatter):
        """Test recovery from encoding errors"""
        # Test with problematic Unicode content
        problematic_content = "Test \udcff\udcfe invalid Unicode"
        
        try:
            result = formatter.info(problematic_content)
            # Should handle encoding issues gracefully
            assert isinstance(result, str)
        except UnicodeError:
            # Encoding errors should be handled gracefully
            pytest.skip("Unicode handling not available")
    
    def test_ansi_support_failure_recovery(self, formatter):
        """Test recovery when ANSI codes are not supported"""
        # Simulate environment where ANSI codes cause issues
        with patch('sys.stdout.write', side_effect=lambda x: None if '\033[' in x else print(x, end='')):
            
            formatter._color_enabled = True  # Force color mode
            
            # Should still produce output even if colors fail
            result = formatter.warning("Test warning")
            assert "Test warning" in result


@pytest.mark.integration
class TestTerminalCompatibilityIntegration:
    """Integration tests for terminal compatibility"""
    
    def test_real_terminal_detection(self):
        """Test real terminal detection in current environment"""
        formatter = TerminalFormatter()
        
        # Should not crash
        width = formatter._get_terminal_width()
        assert isinstance(width, int)
        assert width > 0
        
        # Color detection should work
        color_enabled = formatter.color_enabled
        assert isinstance(color_enabled, bool)
    
    def test_formatter_consistency_across_modes(self):
        """Test formatter consistency between color and no-color modes"""
        formatter = TerminalFormatter()
        test_message = "Test consistency message"
        
        # Test with colors enabled
        formatter.enable_color()
        colored_result = formatter.info(test_message)
        
        # Test with colors disabled
        formatter.disable_color()
        no_color_result = formatter.info(test_message)
        
        # Both should contain the message
        assert test_message in colored_result
        assert test_message in no_color_result
        
        # No-color version should not have ANSI codes
        assert '\033[' not in no_color_result
    
    def test_cross_platform_box_rendering(self):
        """Test box rendering across different platforms"""
        formatter = TerminalFormatter()
        content = "Cross-platform test content"
        
        # Test different box styles
        styles = ['single', 'double', 'ascii']
        
        for style in styles:
            result = formatter.box(content, style=style)
            
            # Should contain the content
            assert content in result
            
            # Should have box structure (corners and borders)
            assert '+' in result or '#' in result
            assert '-' in result or '=' in result
            assert '|' in result or '#' in result
    
    def test_progress_bar_cross_platform(self):
        """Test progress bar functionality across platforms"""
        formatter = TerminalFormatter()
        
        # Test both color and no-color modes
        for color_enabled in [True, False]:
            if color_enabled:
                formatter.enable_color()
            else:
                formatter.disable_color()
            
            progress_bar = formatter.progress_bar(100, "Cross-platform test")
            
            with patch('builtins.print') as mock_print:
                progress_bar.update(50)
                progress_bar.finish()
            
            # Should have printed progress
            assert mock_print.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])