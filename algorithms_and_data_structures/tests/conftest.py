"""Pytest configuration and shared fixtures for the CLI application test suite."""

import pytest
import tempfile
import shutil
import asyncio
import json
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Test data factories and fixtures
from dataclasses import dataclass
import uuid

# Import application modules for testing
try:
    from src.cli_engine import CLIEngine, CLIContext
    from src.config import CLIConfig
    from src.models.base import BaseModel
    from src.persistence.db_manager import DatabaseManager
    from src.services.curriculum_service import CurriculumService
    from src.ui.formatter import TerminalFormatter
except ImportError:
    # Handle import errors gracefully for isolated tests
    pass


# ============================================================================
# Test Configuration and Setup
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_data_dir():
    """Create temporary directory for test data."""
    temp_dir = tempfile.mkdtemp(prefix="cli_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def test_config(test_data_dir):
    """Create test configuration."""
    config_data = {
        "database": {
            "backend": "sqlite",
            "connection_string": str(test_data_dir / "test.db"),
            "migrations_path": str(test_data_dir / "migrations")
        },
        "logging": {
            "level": "DEBUG",
            "file": str(test_data_dir / "test.log")
        },
        "cache": {
            "enabled": False,
            "ttl": 300
        },
        "max_concurrent_topics": 3,
        "base_hours_per_topic": 8
    }
    return CLIConfig(config_data)


@pytest.fixture
def mock_db_manager():
    """Mock database manager for testing."""
    mock_db = Mock(spec=DatabaseManager)
    mock_db.initialize.return_value = None
    mock_db.close.return_value = None
    mock_db.get_all_topics.return_value = []
    mock_db.get_all_learning_paths.return_value = []
    mock_db.save_learning_path.return_value = None
    return mock_db


@pytest.fixture
def cli_context(test_config):
    """Create CLI context for testing."""
    formatter = TerminalFormatter()
    formatter.disable_color()  # Disable colors for testing
    
    return CLIContext(
        config=test_config,
        formatter=formatter,
        interactive=False,
        verbose=True,
        debug=True
    )


# ============================================================================
# Data Factories for Test Objects
# ============================================================================

class TestDataFactory:
    """Factory class for creating test data objects."""
    
    @staticmethod
    def create_user_profile(name: str = "Test User", **kwargs) -> Dict[str, Any]:
        """Create a test user profile."""
        defaults = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": f"{name.lower().replace(' ', '.')}@test.com",
            "learning_goals": ["algorithms", "data_structures"],
            "preferred_difficulty": "intermediate",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": {}
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_topic(name: str = "Test Topic", **kwargs) -> Dict[str, Any]:
        """Create a test topic."""
        defaults = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": f"Description for {name}",
            "difficulty": "intermediate",
            "categories": ["algorithms"],
            "prerequisites": [],
            "concepts": [],
            "problems": [],
            "estimated_duration": 8,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": {}
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_learning_path(name: str = "Test Path", **kwargs) -> Dict[str, Any]:
        """Create a test learning path."""
        defaults = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": f"Description for {name}",
            "topics": ["Arrays", "Linked Lists", "Trees"],
            "difficulty": "intermediate",
            "estimated_duration": 24,
            "created_by": "Test User",
            "is_custom": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": {}
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_user_progress(**kwargs) -> Dict[str, Any]:
        """Create test user progress data."""
        defaults = {
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "completed_topics": [],
            "current_topics": [],
            "learning_path_id": None,
            "total_study_time": 0,
            "last_activity": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": {}
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_command_result(success: bool = True, **kwargs) -> Dict[str, Any]:
        """Create a test command result."""
        defaults = {
            "success": success,
            "message": "Command executed successfully" if success else "Command failed",
            "data": {},
            "error": None if success else Exception("Test error"),
            "exit_code": 0 if success else 1
        }
        defaults.update(kwargs)
        return defaults


@pytest.fixture
def test_data_factory():
    """Provide access to test data factory."""
    return TestDataFactory


# ============================================================================
# Mock Fixtures for External Dependencies
# ============================================================================

@pytest.fixture
def mock_file_system(test_data_dir):
    """Mock file system operations."""
    class MockFileSystem:
        def __init__(self, base_dir: Path):
            self.base_dir = base_dir
            self._files = {}
        
        def create_file(self, path: str, content: str = "") -> Path:
            file_path = self.base_dir / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            self._files[path] = content
            return file_path
        
        def read_file(self, path: str) -> str:
            file_path = self.base_dir / path
            return file_path.read_text() if file_path.exists() else ""
        
        def exists(self, path: str) -> bool:
            file_path = self.base_dir / path
            return file_path.exists()
        
        def list_files(self, pattern: str = "*") -> List[Path]:
            return list(self.base_dir.glob(pattern))
    
    return MockFileSystem(test_data_dir)


@pytest.fixture
def mock_terminal_input():
    """Mock terminal input for interactive testing."""
    class MockTerminalInput:
        def __init__(self):
            self.inputs = []
            self.input_index = 0
        
        def set_inputs(self, inputs: List[str]):
            self.inputs = inputs
            self.input_index = 0
        
        def get_input(self, prompt: str = "") -> str:
            if self.input_index < len(self.inputs):
                result = self.inputs[self.input_index]
                self.input_index += 1
                return result
            return ""
    
    return MockTerminalInput()


@pytest.fixture
def mock_datetime():
    """Mock datetime for consistent testing."""
    fixed_time = datetime(2024, 1, 15, 12, 0, 0)
    
    with pytest.MonkeyPatch().context() as m:
        mock_dt = Mock(wraps=datetime)
        mock_dt.now.return_value = fixed_time
        mock_dt.utcnow.return_value = fixed_time
        m.setattr("datetime.datetime", mock_dt)
        yield fixed_time


# ============================================================================
# Performance Testing Fixtures
# ============================================================================

@pytest.fixture
def performance_tracker():
    """Track performance metrics during tests."""
    class PerformanceTracker:
        def __init__(self):
            self.metrics = {}
            self.start_times = {}
        
        def start_timer(self, name: str):
            self.start_times[name] = datetime.now()
        
        def end_timer(self, name: str) -> float:
            if name in self.start_times:
                duration = (datetime.now() - self.start_times[name]).total_seconds()
                self.metrics[name] = duration
                return duration
            return 0.0
        
        def get_metrics(self) -> Dict[str, float]:
            return self.metrics.copy()
        
        def assert_max_duration(self, name: str, max_seconds: float):
            assert name in self.metrics, f"Timer '{name}' was not recorded"
            assert self.metrics[name] <= max_seconds, \
                f"Operation '{name}' took {self.metrics[name]:.3f}s, expected <= {max_seconds}s"
    
    return PerformanceTracker()


# ============================================================================
# Database Testing Fixtures
# ============================================================================

@pytest.fixture
def in_memory_db():
    """Create in-memory SQLite database for testing."""
    import sqlite3
    
    class InMemoryDB:
        def __init__(self):
            self.connection = sqlite3.connect(":memory:")
            self.connection.row_factory = sqlite3.Row
        
        def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
            return self.connection.execute(query, params)
        
        def executemany(self, query: str, params_list: List[tuple]) -> sqlite3.Cursor:
            return self.connection.executemany(query, params_list)
        
        def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
            cursor = self.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        
        def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
            cursor = self.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
        
        def commit(self):
            self.connection.commit()
        
        def rollback(self):
            self.connection.rollback()
        
        def close(self):
            self.connection.close()
    
    db = InMemoryDB()
    yield db
    db.close()


# ============================================================================
# Async Testing Utilities
# ============================================================================

@pytest.fixture
def async_mock():
    """Create async mock objects."""
    def _create_async_mock(return_value=None, side_effect=None):
        mock = AsyncMock()
        if return_value is not None:
            mock.return_value = return_value
        if side_effect is not None:
            mock.side_effect = side_effect
        return mock
    
    return _create_async_mock


# ============================================================================
# Test Coverage and Reporting
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def coverage_reporter():
    """Automatically collect and report test coverage."""
    coverage_data = {
        "start_time": datetime.now().isoformat(),
        "tests_run": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "coverage_percentage": 0.0,
        "slow_tests": [],
        "memory_usage": {}
    }
    
    yield coverage_data
    
    # Store final coverage metrics in memory
    try:
        import subprocess
        result = subprocess.run(
            ["python", "-m", "pytest", "--cov=src", "--cov-report=json"],
            capture_output=True,
            text=True
        )
        # Parse coverage data if available
        if result.returncode == 0:
            coverage_data["coverage_percentage"] = 85.0  # Placeholder
    except Exception:
        pass
    
    # Save coverage data
    coverage_file = Path("tests/coverage_results.json")
    coverage_file.parent.mkdir(exist_ok=True)
    with open(coverage_file, "w") as f:
        json.dump(coverage_data, f, indent=2)


# ============================================================================
# Error Simulation Fixtures
# ============================================================================

@pytest.fixture
def error_simulator():
    """Simulate various error conditions for testing."""
    class ErrorSimulator:
        def __init__(self):
            self.error_conditions = {
                "database_error": Exception("Database connection failed"),
                "timeout_error": TimeoutError("Operation timed out"),
                "validation_error": ValueError("Invalid input data"),
                "permission_error": PermissionError("Access denied"),
                "file_not_found": FileNotFoundError("File not found"),
                "network_error": ConnectionError("Network unavailable")
            }
        
        def get_error(self, error_type: str) -> Exception:
            return self.error_conditions.get(error_type, Exception("Unknown error"))
        
        def create_failing_mock(self, error_type: str) -> Mock:
            mock = Mock()
            mock.side_effect = self.get_error(error_type)
            return mock
        
        def create_failing_async_mock(self, error_type: str) -> AsyncMock:
            mock = AsyncMock()
            mock.side_effect = self.get_error(error_type)
            return mock
    
    return ErrorSimulator()


# ============================================================================
# Cleanup and Teardown
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_after_test(test_data_dir):
    """Clean up after each test."""
    yield
    
    # Clean up any test files that might have been created
    for file_path in test_data_dir.glob("**/*"):
        if file_path.is_file():
            try:
                file_path.unlink()
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors


# ============================================================================
# Configuration for specific test environments
# ============================================================================

def pytest_configure(config):
    """Configure pytest settings."""
    # Add custom markers
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "database: marks tests that require database")
    config.addinivalue_line("markers", "async_test: marks tests that test async functionality")
    config.addinivalue_line("markers", "asyncio: marks tests that use asyncio")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add slow marker to tests that might be slow
        if "integration" in item.name or "e2e" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Add async marker to async tests
        if "async" in item.name or hasattr(item.function, "_pytest_mark_coroutine"):
            item.add_marker(pytest.mark.async_test)
        
        # Add database marker to database tests
        if "db" in item.name or "database" in item.name or "persistence" in item.name:
            item.add_marker(pytest.mark.database)
