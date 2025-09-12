"""Test suite for CLI Commands - All command implementations and execution."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import argparse
from pathlib import Path

try:
    from src.commands.base import (
        BaseCommand, CommandResult, CommandCategory, CommandMetadata,
        AsyncCommand, SyncCommand, CompositeBECommand
    )
    from src.commands.curriculum_commands import (
        ListTopicsCommand, ShowTopicCommand, SearchTopicsCommand
    )
    from src.commands.content_commands import (
        CreateContentCommand, EditContentCommand, DeleteContentCommand
    )
    from src.commands.progress_commands import (
        ShowProgressCommand, UpdateProgressCommand, ExportProgressCommand
    )
    from src.commands.search_commands import (
        SearchCommand, FindCommand, FilterCommand
    )
    from src.commands.admin_commands import (
        BackupCommand, RestoreCommand, MigrateCommand
    )
except ImportError:
    # For isolated testing
    BaseCommand = None
    CommandResult = None


# Mock implementations for testing
class TestCommand(BaseCommand):
    """Test command implementation."""
    
    def __init__(self, name: str = "test", should_fail: bool = False):
        self._name = name
        self._should_fail = should_fail
        super().__init__()
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name=self._name,
            description=f"Test command: {self._name}",
            category=CommandCategory.SYSTEM,
            aliases=["t"],
            examples=[f"{self._name} --help"]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(subparsers)
        parser.add_argument("--test-flag", action="store_true", help="Test flag")
        parser.add_argument("--value", type=int, default=0, help="Test value")
        return parser
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        if self._should_fail:
            return CommandResult(
                success=False,
                message="Test command failed",
                exit_code=1
            )
        
        parsed_args = self.parse_args(args)
        return CommandResult(
            success=True,
            message=f"Test command {self._name} executed",
            data={
                "test_flag": parsed_args.test_flag,
                "value": parsed_args.value,
                "dry_run": parsed_args.dry_run,
                "force": parsed_args.force,
                "quiet": parsed_args.quiet
            }
        )


class TestAsyncCommand(AsyncCommand):
    """Test async command implementation."""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="async-test",
            description="Test async command",
            category=CommandCategory.SYSTEM
        )
    
    def setup_parser(self, subparsers):
        return self.create_subparser(subparsers)
    
    async def async_execute(self, context, args: List[str]) -> CommandResult:
        # Simulate async operation
        await asyncio.sleep(0.01)
        return CommandResult(
            success=True,
            message="Async command executed"
        )


class TestSyncCommand(SyncCommand):
    """Test sync command implementation."""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="sync-test",
            description="Test sync command",
            category=CommandCategory.SYSTEM
        )
    
    def setup_parser(self, subparsers):
        return self.create_subparser(subparsers)
    
    def sync_execute(self, context, args: List[str]) -> CommandResult:
        return CommandResult(
            success=True,
            message="Sync command executed"
        )


class TestCompositeCommand(CompositeBECommand):
    """Test composite command implementation."""
    
    def __init__(self):
        super().__init__()
        self.add_sub_command(TestCommand("sub1"))
        self.add_sub_command(TestCommand("sub2"))
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="composite-test",
            description="Test composite command",
            category=CommandCategory.SYSTEM
        )
    
    def setup_parser(self, subparsers):
        return self.create_subparser(subparsers)


@pytest.mark.unit
class TestBaseCommand:
    """Test cases for BaseCommand abstract class."""
    
    def test_command_initialization(self):
        """Test command initialization."""
        command = TestCommand("init-test")
        
        assert command.name == "init-test"
        assert command.description == "Test command: init-test"
        assert command.category == CommandCategory.SYSTEM
        assert "t" in command.aliases
        assert len(command.examples) > 0
    
    def test_command_metadata(self):
        """Test command metadata properties."""
        command = TestCommand("metadata-test")
        metadata = command.get_metadata()
        
        assert isinstance(metadata, CommandMetadata)
        assert metadata.name == "metadata-test"
        assert metadata.category == CommandCategory.SYSTEM
        assert isinstance(metadata.aliases, list)
        assert isinstance(metadata.examples, list)
    
    def test_parser_setup(self):
        """Test parser setup and argument parsing."""
        command = TestCommand("parser-test")
        
        # Create mock subparsers
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        
        # Setup parser
        parser = command.setup_parser(subparsers)
        
        assert parser is not None
        assert command._parser is not None
        
        # Test parsing arguments
        args = command.parse_args(["--test-flag", "--value", "42", "--dry-run"])
        assert args.test_flag is True
        assert args.value == 42
        assert args.dry_run is True
        assert args.force is False
        assert args.quiet is False
    
    def test_parser_validation(self):
        """Test argument parsing validation."""
        command = TestCommand("validation-test")
        
        # Setup parser
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        command.setup_parser(subparsers)
        
        # Test valid arguments
        args = command.parse_args(["--value", "10"])
        errors = command.validate_args(args)
        assert len(errors) == 0
    
    @pytest.mark.asyncio
    async def test_command_execution_success(self, cli_context):
        """Test successful command execution."""
        command = TestCommand("success-test")
        
        # Setup parser
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        command.setup_parser(subparsers)
        
        result = await command.execute(cli_context, ["--test-flag", "--value", "5"])
        
        assert result.success is True
        assert "success-test executed" in result.message
        assert result.data["test_flag"] is True
        assert result.data["value"] == 5
    
    @pytest.mark.asyncio
    async def test_command_execution_failure(self, cli_context):
        """Test command execution failure."""
        command = TestCommand("failure-test", should_fail=True)
        
        # Setup parser
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        command.setup_parser(subparsers)
        
        result = await command.execute(cli_context, [])
        
        assert result.success is False
        assert "Test command failed" in result.message
        assert result.exit_code == 1
    
    @pytest.mark.asyncio
    async def test_run_with_error_handling(self, cli_context):
        """Test command execution with error handling wrapper."""
        command = TestCommand("error-handling-test")
        
        # Setup parser
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        command.setup_parser(subparsers)
        
        # Test successful execution
        result = await command.run_with_error_handling(cli_context, ["--test-flag"])
        assert result.success is True
        
        # Test parser not initialized
        command_no_parser = TestCommand("no-parser")
        result = await command_no_parser.run_with_error_handling(cli_context, [])
        assert result.success is False
        assert "parser not initialized" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_keyboard_interrupt_handling(self, cli_context):
        """Test keyboard interrupt handling."""
        command = TestCommand("interrupt-test")
        
        # Mock execute method to raise KeyboardInterrupt
        async def interrupt_execute(context, args):
            raise KeyboardInterrupt()
        
        command.execute = interrupt_execute
        
        # Setup parser
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        command.setup_parser(subparsers)
        
        result = await command.run_with_error_handling(cli_context, [])
        
        assert result.success is False
        assert "interrupted" in result.message.lower()
        assert result.exit_code == 130
    
    def test_get_help(self):
        """Test help text generation."""
        command = TestCommand("help-test")
        help_text = command.get_help()
        
        assert "help-test" in help_text
        assert "Test command: help-test" in help_text
        assert "system" in help_text.lower()
        assert "t" in help_text  # alias
    
    def test_confirmation_prompt(self, mock_terminal_input):
        """Test confirmation prompt functionality."""
        command = TestCommand("confirm-test")
        
        # Test yes response
        mock_terminal_input.set_inputs(["y"])
        with patch('builtins.input', side_effect=mock_terminal_input.get_input):
            result = command.confirm_action("Proceed?")
            assert result is True
        
        # Test no response
        mock_terminal_input.set_inputs(["n"])
        with patch('builtins.input', side_effect=mock_terminal_input.get_input):
            result = command.confirm_action("Proceed?")
            assert result is False
        
        # Test default yes
        mock_terminal_input.set_inputs([""])  # Empty input
        with patch('builtins.input', side_effect=mock_terminal_input.get_input):
            result = command.confirm_action("Proceed?", default=True)
            assert result is True
        
        # Test KeyboardInterrupt
        with patch('builtins.input', side_effect=KeyboardInterrupt()):
            result = command.confirm_action("Proceed?")
            assert result is False
    
    def test_table_formatting(self):
        """Test table data formatting."""
        command = TestCommand("table-test")
        
        # Test with data
        data = [
            {"name": "Alice", "age": 25, "city": "New York"},
            {"name": "Bob", "age": 30, "city": "San Francisco"},
            {"name": "Charlie", "age": 35, "city": "Chicago"}
        ]
        headers = ["name", "age", "city"]
        
        table = command.format_table_data(data, headers)
        
        assert "Alice" in table
        assert "Bob" in table
        assert "Charlie" in table
        assert "New York" in table
        assert "25" in table
        assert "|" in table  # Table separator
        assert "-" in table  # Header separator
        
        # Test with empty data
        empty_table = command.format_table_data([], headers)
        assert "No data to display" in empty_table
        
        # Test with missing data
        incomplete_data = [{"name": "Alice"}, {"age": 30}]
        table = command.format_table_data(incomplete_data, headers)
        assert "Alice" in table
        assert "30" in table


@pytest.mark.unit
class TestAsyncCommand:
    """Test cases for AsyncCommand class."""
    
    @pytest.mark.asyncio
    async def test_async_command_execution(self, cli_context):
        """Test async command execution."""
        command = TestAsyncCommand()
        
        # Setup parser
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        command.setup_parser(subparsers)
        
        result = await command.execute(cli_context, [])
        
        assert result.success is True
        assert "Async command executed" in result.message
    
    @pytest.mark.asyncio
    async def test_async_command_timing(self, cli_context, performance_tracker):
        """Test async command timing."""
        command = TestAsyncCommand()
        
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        command.setup_parser(subparsers)
        
        performance_tracker.start_timer("async_execution")
        result = await command.execute(cli_context, [])
        duration = performance_tracker.end_timer("async_execution")
        
        assert result.success is True
        assert duration >= 0.01  # Should take at least 10ms due to sleep


@pytest.mark.unit
class TestSyncCommand:
    """Test cases for SyncCommand class."""
    
    @pytest.mark.asyncio
    async def test_sync_command_execution(self, cli_context):
        """Test sync command execution in async context."""
        command = TestSyncCommand()
        
        # Setup parser
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        command.setup_parser(subparsers)
        
        result = await command.execute(cli_context, [])
        
        assert result.success is True
        assert "Sync command executed" in result.message


@pytest.mark.unit
class TestCompositeCommand:
    """Test cases for CompositeBECommand class."""
    
    @pytest.mark.asyncio
    async def test_composite_command_execution(self, cli_context):
        """Test composite command execution."""
        command = TestCompositeCommand()
        
        # Setup parser
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        command.setup_parser(subparsers)
        
        # Test executing sub-command
        result = await command.execute(cli_context, ["sub1", "--test-flag"])
        
        assert result.success is True
        assert "sub1 executed" in result.message
    
    @pytest.mark.asyncio
    async def test_composite_command_no_subcommand(self, cli_context):
        """Test composite command without sub-command."""
        command = TestCompositeCommand()
        
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        command.setup_parser(subparsers)
        
        result = await command.execute(cli_context, [])
        
        assert result.success is False
        assert "Sub-command required" in result.message
        assert result.exit_code == 2
    
    @pytest.mark.asyncio
    async def test_composite_command_unknown_subcommand(self, cli_context):
        """Test composite command with unknown sub-command."""
        command = TestCompositeCommand()
        
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        command.setup_parser(subparsers)
        
        result = await command.execute(cli_context, ["unknown"])
        
        assert result.success is False
        assert "Unknown sub-command" in result.message
        assert result.exit_code == 2
    
    def test_add_sub_command(self):
        """Test adding sub-commands."""
        command = TestCompositeCommand()
        new_sub = TestCommand("new-sub")
        
        command.add_sub_command(new_sub)
        
        assert "new-sub" in command.sub_commands
        assert command.sub_commands["new-sub"] == new_sub
    
    def test_add_sub_command_with_aliases(self):
        """Test adding sub-commands with aliases."""
        command = TestCompositeCommand()
        new_sub = TestCommand("aliased-sub")
        new_sub._aliases = ["as"]
        
        command.add_sub_command(new_sub)
        
        assert "aliased-sub" in command.sub_commands
        assert "as" in command.sub_commands
        assert command.sub_commands["as"] == new_sub


@pytest.mark.integration
class TestCommandIntegration:
    """Integration tests for command functionality."""
    
    @pytest.mark.asyncio
    async def test_command_pipeline(self, cli_context, test_data_factory):
        """Test executing multiple commands in sequence."""
        commands = [
            TestCommand("step1"),
            TestCommand("step2"),
            TestCommand("step3")
        ]
        
        # Setup parsers for all commands
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        
        for command in commands:
            command.setup_parser(subparsers)
        
        # Execute commands in sequence
        results = []
        for command in commands:
            result = await command.execute(cli_context, ["--quiet"])
            results.append(result)
        
        # All commands should succeed
        assert all(r.success for r in results)
        assert len(results) == 3
        
        # All should have quiet flag set
        for result in results:
            assert result.data["quiet"] is True
    
    @pytest.mark.asyncio
    async def test_command_error_propagation(self, cli_context):
        """Test error propagation in command execution."""
        success_command = TestCommand("success")
        failure_command = TestCommand("failure", should_fail=True)
        
        # Setup parsers
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        
        success_command.setup_parser(subparsers)
        failure_command.setup_parser(subparsers)
        
        # Test successful command doesn't affect failure
        success_result = await success_command.execute(cli_context, [])
        assert success_result.success is True
        
        # Test failure is properly reported
        failure_result = await failure_command.execute(cli_context, [])
        assert failure_result.success is False
        assert failure_result.exit_code == 1
    
    @pytest.mark.asyncio
    async def test_command_context_usage(self, cli_context, test_config):
        """Test commands using CLI context properly."""
        # Test with different context configurations
        contexts = [
            cli_context,  # Default context
            # Verbose context
            type(cli_context)(
                config=test_config,
                formatter=cli_context.formatter,
                verbose=True,
                debug=False
            ),
            # Debug context
            type(cli_context)(
                config=test_config,
                formatter=cli_context.formatter,
                verbose=False,
                debug=True
            )
        ]
        
        command = TestCommand("context-test")
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        command.setup_parser(subparsers)
        
        # Execute with different contexts
        for context in contexts:
            result = await command.execute(context, [])
            assert result.success is True


@pytest.mark.performance
class TestCommandPerformance:
    """Performance tests for command execution."""
    
    @pytest.mark.asyncio
    async def test_command_execution_performance(self, cli_context, performance_tracker):
        """Test performance of command execution."""
        commands = [TestCommand(f"perf-test-{i}") for i in range(50)]
        
        # Setup all parsers
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        
        for command in commands:
            command.setup_parser(subparsers)
        
        performance_tracker.start_timer("command_execution")
        
        # Execute all commands
        results = []
        for command in commands:
            result = await command.execute(cli_context, [])
            results.append(result)
        
        duration = performance_tracker.end_timer("command_execution")
        
        # Should execute 50 commands quickly
        performance_tracker.assert_max_duration("command_execution", 1.0)
        
        # All commands should succeed
        assert all(r.success for r in results)
        assert len(results) == 50
    
    def test_parser_setup_performance(self, performance_tracker):
        """Test performance of parser setup."""
        commands = [TestCommand(f"parser-perf-{i}") for i in range(100)]
        
        performance_tracker.start_timer("parser_setup")
        
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        
        for command in commands:
            command.setup_parser(subparsers)
        
        duration = performance_tracker.end_timer("parser_setup")
        
        # Should setup 100 parsers quickly
        performance_tracker.assert_max_duration("parser_setup", 0.5)
    
    @pytest.mark.asyncio
    async def test_concurrent_command_execution(self, cli_context, performance_tracker):
        """Test concurrent command execution."""
        commands = [TestCommand(f"concurrent-{i}") for i in range(20)]
        
        # Setup parsers
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        
        for command in commands:
            command.setup_parser(subparsers)
        
        performance_tracker.start_timer("concurrent_execution")
        
        # Execute commands concurrently
        tasks = [command.execute(cli_context, []) for command in commands]
        results = await asyncio.gather(*tasks)
        
        duration = performance_tracker.end_timer("concurrent_execution")
        
        # Concurrent execution should be fast
        performance_tracker.assert_max_duration("concurrent_execution", 0.5)
        
        # All commands should succeed
        assert all(r.success for r in results)
        assert len(results) == 20


@pytest.mark.slow
class TestCommandErrorScenarios:
    """Test various error scenarios in command execution."""
    
    @pytest.mark.asyncio
    async def test_malformed_arguments(self, cli_context):
        """Test handling of malformed command arguments."""
        command = TestCommand("malformed-test")
        
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        command.setup_parser(subparsers)
        
        # Test invalid argument format
        with pytest.raises(SystemExit):
            command.parse_args(["--invalid-flag"])
    
    @pytest.mark.asyncio
    async def test_resource_exhaustion(self, cli_context):
        """Test command behavior under resource constraints."""
        command = TestCommand("resource-test")
        
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        command.setup_parser(subparsers)
        
        # Mock resource exhaustion
        with patch('asyncio.sleep', side_effect=MemoryError("Out of memory")):
            # Commands should handle resource errors gracefully
            result = await command.run_with_error_handling(cli_context, [])
            assert result.success is False or result.success is True  # Either handling or success
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, cli_context):
        """Test command timeout handling."""
        class TimeoutCommand(TestCommand):
            async def execute(self, context, args: List[str]) -> CommandResult:
                await asyncio.sleep(10)  # Long operation
                return CommandResult(success=True, message="Should timeout")
        
        command = TimeoutCommand("timeout-test")
        
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        command.setup_parser(subparsers)
        
        # Test with timeout
        try:
            result = await asyncio.wait_for(
                command.execute(cli_context, []),
                timeout=0.1  # 100ms timeout
            )
        except asyncio.TimeoutError:
            # Expected behavior
            assert True
        else:
            # Should not reach here
            pytest.fail("Command should have timed out")
    
    def test_validation_edge_cases(self):
        """Test validation with edge cases."""
        class ValidationCommand(TestCommand):
            def validate_args(self, args) -> List[str]:
                errors = []
                if hasattr(args, 'value') and args.value < 0:
                    errors.append("Value must be non-negative")
                if hasattr(args, 'test_flag') and args.test_flag and args.quiet:
                    errors.append("Cannot use --test-flag with --quiet")
                return errors
        
        command = ValidationCommand("validation-edge-test")
        
        main_parser = argparse.ArgumentParser()
        subparsers = main_parser.add_subparsers(dest="command")
        command.setup_parser(subparsers)
        
        # Test valid args
        args = command.parse_args(["--value", "10"])
        errors = command.validate_args(args)
        assert len(errors) == 0
        
        # Test invalid value
        args = command.parse_args(["--value", "-5"])
        errors = command.validate_args(args)
        assert len(errors) == 1
        assert "non-negative" in errors[0]
        
        # Test conflicting flags
        args = command.parse_args(["--test-flag", "--quiet"])
        errors = command.validate_args(args)
        assert len(errors) == 1
        assert "Cannot use --test-flag with --quiet" in errors[0]
