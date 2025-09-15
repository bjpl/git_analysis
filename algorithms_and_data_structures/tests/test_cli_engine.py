"""Test suite for CLI Engine - Core command routing and parsing system."""

import pytest
import asyncio
import sys
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

try:
    from src.cli_engine import CLIEngine, CLIContext, main
    from src.config import CLIConfig
    from src.commands.base import BaseCommand, CommandResult, CommandCategory, CommandMetadata
    from src.ui.formatter import TerminalFormatter
    from src.core.exceptions import CLIError, CommandNotFoundError
except ImportError:
    # For isolated testing
    CLIEngine = None
    CLIContext = None


class MockCommand(BaseCommand):
    """Mock command for testing."""
    
    def __init__(self, name: str = "mock", aliases: List[str] = None):
        self._name = name
        self._aliases = aliases or []
        super().__init__()
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name=self._name,
            description=f"Mock command: {self._name}",
            category=CommandCategory.SYSTEM,
            aliases=self._aliases,
            examples=[f"{self._name} --help"]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(subparsers)
        parser.add_argument("--test", action="store_true", help="Test flag")
        return parser
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        return CommandResult(
            success=True,
            message=f"Mock command {self._name} executed",
            data={"command": self._name, "args": args}
        )


class FailingMockCommand(MockCommand):
    """Mock command that always fails."""
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        raise Exception("Mock command failure")


@pytest.mark.unit
class TestCLIEngine:
    """Test cases for CLIEngine class."""
    
    def test_cli_engine_initialization(self, test_config):
        """Test CLI engine initialization."""
        engine = CLIEngine(test_config)
        
        assert engine.config == test_config
        assert engine.formatter is not None
        assert engine.plugin_manager is not None
        assert isinstance(engine.commands, dict)
        assert isinstance(engine.aliases, dict)
        assert engine.context.config == test_config
    
    def test_cli_engine_default_config(self):
        """Test CLI engine with default configuration."""
        engine = CLIEngine()
        
        assert engine.config is not None
        assert engine.formatter is not None
        assert isinstance(engine.commands, dict)
    
    def test_register_command(self, test_config):
        """Test command registration."""
        engine = CLIEngine(test_config)
        mock_command = MockCommand("test", ["t", "tst"])
        
        engine.register_command(mock_command)
        
        assert "test" in engine.commands
        assert engine.commands["test"] == mock_command
        assert "t" in engine.aliases
        assert "tst" in engine.aliases
        assert engine.aliases["t"] == "test"
        assert engine.aliases["tst"] == "test"
    
    def test_get_command_by_name(self, test_config):
        """Test retrieving command by name."""
        engine = CLIEngine(test_config)
        mock_command = MockCommand("test")
        engine.register_command(mock_command)
        
        # Test direct name
        assert engine.get_command("test") == mock_command
        
        # Test non-existent command
        assert engine.get_command("nonexistent") is None
    
    def test_get_command_by_alias(self, test_config):
        """Test retrieving command by alias."""
        engine = CLIEngine(test_config)
        mock_command = MockCommand("test", ["t"])
        engine.register_command(mock_command)
        
        # Test alias
        assert engine.get_command("t") == mock_command
    
    def test_create_parser(self, test_config):
        """Test argument parser creation."""
        engine = CLIEngine(test_config)
        mock_command = MockCommand("test")
        engine.register_command(mock_command)
        
        parser = engine.create_parser()
        
        assert parser is not None
        assert parser.prog == "curriculum-cli"
        
        # Test parsing valid arguments
        args = parser.parse_args(["--verbose", "test", "--test"])
        assert args.verbose is True
        assert args.command == "test"
    
    def test_create_parser_global_options(self, test_config):
        """Test global options in argument parser."""
        engine = CLIEngine(test_config)
        parser = engine.create_parser()
        
        # Test all global options
        args = parser.parse_args([
            "--verbose",
            "--debug", 
            "--no-color",
            "--interactive"
        ])
        
        assert args.verbose is True
        assert args.debug is True
        assert args.no_color is True
        assert args.interactive is True
    
    @pytest.mark.asyncio
    async def test_execute_command_success(self, test_config):
        """Test successful command execution."""
        engine = CLIEngine(test_config)
        mock_command = MockCommand("test")
        engine.register_command(mock_command)
        
        result = await engine.execute_command("test", ["--test"])
        
        assert result.success is True
        assert "Mock command test executed" in result.message
        assert result.data["command"] == "test"
    
    @pytest.mark.asyncio
    async def test_execute_command_not_found(self, test_config):
        """Test command not found error."""
        engine = CLIEngine(test_config)
        
        with pytest.raises(CommandNotFoundError, match="Command 'nonexistent' not found"):
            await engine.execute_command("nonexistent", [])
    
    @pytest.mark.asyncio
    async def test_execute_command_failure(self, test_config):
        """Test command execution failure."""
        engine = CLIEngine(test_config)
        failing_command = FailingMockCommand("failing")
        engine.register_command(failing_command)
        
        result = await engine.execute_command("failing", [])
        
        assert result.success is False
        assert "Mock command failure" in result.message
        assert result.error is not None
    
    @pytest.mark.asyncio
    async def test_execute_command_failure_debug_mode(self, test_config):
        """Test command execution failure in debug mode."""
        engine = CLIEngine(test_config)
        engine.context.debug = True
        failing_command = FailingMockCommand("failing")
        engine.register_command(failing_command)
        
        with pytest.raises(Exception, match="Mock command failure"):
            await engine.execute_command("failing", [])
    
    def test_list_commands(self, test_config):
        """Test listing available commands."""
        engine = CLIEngine(test_config)
        mock_command1 = MockCommand("test1")
        mock_command2 = MockCommand("test2")
        
        engine.register_command(mock_command1)
        engine.register_command(mock_command2)
        
        commands = engine.list_commands()
        
        assert "test1" in commands
        assert "test2" in commands
        assert commands == sorted(commands)  # Should be sorted
    
    def test_get_command_help(self, test_config):
        """Test getting command help."""
        engine = CLIEngine(test_config)
        mock_command = MockCommand("test")
        engine.register_command(mock_command)
        
        help_text = engine.get_command_help("test")
        
        assert help_text is not None
        assert "Mock command: test" in help_text
    
    def test_get_command_help_not_found(self, test_config):
        """Test getting help for non-existent command."""
        engine = CLIEngine(test_config)
        
        help_text = engine.get_command_help("nonexistent")
        
        assert help_text is None


@pytest.mark.unit
class TestCLIContext:
    """Test cases for CLIContext class."""
    
    def test_cli_context_creation(self, test_config):
        """Test CLI context creation."""
        formatter = TerminalFormatter()
        
        context = CLIContext(
            config=test_config,
            formatter=formatter,
            interactive=True,
            verbose=True,
            debug=False
        )
        
        assert context.config == test_config
        assert context.formatter == formatter
        assert context.interactive is True
        assert context.verbose is True
        assert context.debug is False
    
    def test_cli_context_defaults(self, test_config):
        """Test CLI context default values."""
        formatter = TerminalFormatter()
        
        context = CLIContext(
            config=test_config,
            formatter=formatter
        )
        
        assert context.interactive is False
        assert context.verbose is False
        assert context.debug is False


@pytest.mark.integration
class TestCLIEngineIntegration:
    """Integration tests for CLI engine."""
    
    @pytest.mark.asyncio
    async def test_run_single_command_success(self, test_config, capsys):
        """Test running a single command successfully."""
        engine = CLIEngine(test_config)
        mock_command = MockCommand("test")
        engine.register_command(mock_command)
        
        exit_code = await engine.run_single_command(["test"])
        
        assert exit_code == 0
        captured = capsys.readouterr()
        # Should have some output indicating success
    
    @pytest.mark.asyncio
    async def test_run_single_command_failure(self, test_config):
        """Test running a single command that fails."""
        engine = CLIEngine(test_config)
        failing_command = FailingMockCommand("failing")
        engine.register_command(failing_command)
        
        exit_code = await engine.run_single_command(["failing"])
        
        assert exit_code == 1
    
    @pytest.mark.asyncio
    async def test_run_single_command_help(self, test_config, capsys):
        """Test running command with help flag."""
        engine = CLIEngine(test_config)
        
        exit_code = await engine.run_single_command(["--help"])
        
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "curriculum-cli" in captured.out
    
    @pytest.mark.asyncio
    async def test_run_single_command_no_command(self, test_config, capsys):
        """Test running without specifying a command."""
        engine = CLIEngine(test_config)
        
        exit_code = await engine.run_single_command([])
        
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "curriculum-cli" in captured.out
    
    @pytest.mark.asyncio
    async def test_run_single_command_keyboard_interrupt(self, test_config):
        """Test handling keyboard interrupt."""
        engine = CLIEngine(test_config)
        
        # Mock command that raises KeyboardInterrupt
        mock_command = MockCommand("interrupt")
        original_execute = mock_command.execute
        
        async def interrupt_execute(context, args):
            raise KeyboardInterrupt()
        
        mock_command.execute = interrupt_execute
        engine.register_command(mock_command)
        
        exit_code = await engine.run_single_command(["interrupt"])
        
        assert exit_code == 130
    
    @pytest.mark.asyncio
    async def test_run_interactive_mode(self, test_config):
        """Test interactive mode initialization."""
        engine = CLIEngine(test_config)
        
        # Mock InteractiveSession
        with patch('src.cli_engine.InteractiveSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            await engine.run_interactive()
            
            assert engine.context.interactive is True
            mock_session_class.assert_called_once_with(engine)
            mock_session.run.assert_called_once()
    
    def test_load_built_in_commands(self, test_config):
        """Test loading built-in commands."""
        with patch('src.cli_engine.importlib.import_module') as mock_import:
            # Mock successful module import
            mock_module = Mock()
            mock_module.TestCommand = MockCommand
            mock_import.return_value = mock_module
            
            engine = CLIEngine(test_config)
            
            # Should have attempted to load built-in commands
            # This is tested indirectly through initialization
            assert engine.commands is not None
    
    def test_load_plugins(self, test_config):
        """Test plugin loading."""
        engine = CLIEngine(test_config)
        
        # Mock plugin manager
        mock_plugin = Mock()
        mock_plugin.commands = [MockCommand("plugin_cmd")]
        
        with patch.object(engine.plugin_manager, 'load_all_plugins') as mock_load:
            mock_load.return_value = [mock_plugin]
            engine._load_plugins()
            
            assert "plugin_cmd" in engine.commands


@pytest.mark.performance
class TestCLIEnginePerformance:
    """Performance tests for CLI engine."""
    
    def test_command_registration_performance(self, test_config, performance_tracker):
        """Test performance of command registration."""
        engine = CLIEngine(test_config)
        commands = [MockCommand(f"cmd{i}") for i in range(100)]
        
        performance_tracker.start_timer("command_registration")
        
        for command in commands:
            engine.register_command(command)
        
        duration = performance_tracker.end_timer("command_registration")
        
        # Should register 100 commands in under 1 second
        performance_tracker.assert_max_duration("command_registration", 1.0)
        assert len(engine.commands) == 100
    
    @pytest.mark.asyncio
    async def test_command_execution_performance(self, test_config, performance_tracker):
        """Test performance of command execution."""
        engine = CLIEngine(test_config)
        mock_command = MockCommand("fast")
        engine.register_command(mock_command)
        
        performance_tracker.start_timer("command_execution")
        
        # Execute command multiple times
        for _ in range(50):
            result = await engine.execute_command("fast", [])
            assert result.success
        
        duration = performance_tracker.end_timer("command_execution")
        
        # Should execute 50 commands in under 1 second
        performance_tracker.assert_max_duration("command_execution", 1.0)


@pytest.mark.asyncio
class TestMainFunction:
    """Test the main function."""
    
    async def test_main_function_success(self, test_config):
        """Test main function with successful execution."""
        with patch('src.cli_engine.CLIEngine') as mock_engine_class:
            mock_engine = AsyncMock()
            mock_engine.run_single_command.return_value = 0
            mock_engine_class.return_value = mock_engine
            
            with patch('sys.argv', ['cli', 'test']):
                with patch('sys.exit') as mock_exit:
                    await main()
                    mock_exit.assert_called_once_with(0)
    
    async def test_main_function_failure(self, test_config):
        """Test main function with failure."""
        with patch('src.cli_engine.CLIEngine') as mock_engine_class:
            mock_engine = AsyncMock()
            mock_engine.run_single_command.return_value = 1
            mock_engine_class.return_value = mock_engine
            
            with patch('sys.argv', ['cli', 'failing']):
                with patch('sys.exit') as mock_exit:
                    await main()
                    mock_exit.assert_called_once_with(1)


@pytest.mark.slow
class TestCLIEngineErrorHandling:
    """Test error handling in CLI engine."""
    
    @pytest.mark.asyncio
    async def test_cli_error_handling(self, test_config):
        """Test CLI error handling."""
        engine = CLIEngine(test_config)
        
        # Mock command that raises CLIError
        mock_command = MockCommand("error")
        
        async def error_execute(context, args):
            raise CLIError("Test CLI error")
        
        mock_command.execute = error_execute
        engine.register_command(mock_command)
        
        exit_code = await engine.run_single_command(["error"])
        
        assert exit_code == 1
    
    @pytest.mark.asyncio
    async def test_unexpected_error_handling(self, test_config):
        """Test unexpected error handling."""
        engine = CLIEngine(test_config)
        
        # Mock command that raises unexpected error
        mock_command = MockCommand("unexpected")
        
        async def unexpected_execute(context, args):
            raise RuntimeError("Unexpected error")
        
        mock_command.execute = unexpected_execute
        engine.register_command(mock_command)
        
        exit_code = await engine.run_single_command(["unexpected"])
        
        assert exit_code == 1
    
    @pytest.mark.asyncio
    async def test_configuration_loading(self, test_config, tmp_path):
        """Test configuration loading from file."""
        config_file = tmp_path / "test_config.json"
        config_file.write_text('{"test": "value"}')
        
        engine = CLIEngine(test_config)
        
        # Mock config loading
        with patch.object(engine.config, 'load_from_file') as mock_load:
            await engine.run_single_command(["--config", str(config_file)])
            mock_load.assert_called_once_with(config_file)
    
    def test_parser_error_handling(self, test_config):
        """Test parser error handling."""
        engine = CLIEngine(test_config)
        mock_command = MockCommand("test")
        engine.register_command(mock_command)
        
        # Test invalid argument
        parser = engine.create_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args(["--invalid-option"])
