# File: tests/conftest.py
"""
Pytest configuration file with shared fixtures and test setup.
Provides database fixtures, Qt application fixtures, and testing utilities.
"""

import os
import sys
import tempfile
import pytest
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch

# Add the parent directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.database import Database
from models.session_model import SessionModel
from models.vocab_model import VocabModel
from models.grammar_model import GrammarModel


@pytest.fixture(scope="session")
def qt_app():
    """Create a QApplication instance for testing Qt widgets."""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Set up test-specific settings
    app.setQuitOnLastWindowClosed(False)
    
    yield app
    
    # Clean up
    app.quit()


@pytest.fixture
def temp_db():
    """Create a temporary test database that gets cleaned up after each test."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        db = Database(tmp_path)
        db.init_db()
        yield db
    finally:
        if os.path.exists(tmp_path):
            db.close()
            os.unlink(tmp_path)


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for faster tests."""
    db = Database(":memory:")
    db.init_db()
    yield db
    db.close()


@pytest.fixture
def sample_teacher(temp_db):
    """Create a sample teacher for testing."""
    cursor = temp_db.conn.cursor()
    cursor.execute(
        "INSERT INTO teachers (name, region, notes) VALUES (?, ?, ?)",
        ("María García", "Mexico", "Experienced Spanish teacher")
    )
    temp_db.conn.commit()
    return cursor.lastrowid


@pytest.fixture
def sample_session(temp_db, sample_teacher):
    """Create a sample session for testing."""
    session_model = SessionModel(temp_db)
    session_id = session_model.create_session(
        teacher_id=sample_teacher,
        session_date="2025-04-10",
        start_time="17:00",
        duration="1h"
    )
    return session_id


@pytest.fixture
def sample_vocab_data():
    """Provide sample vocabulary data for testing."""
    return {
        "word_phrase": "faltar",
        "translation": "to be missing, to lack",
        "context_notes": "Used in expressions like 'me falta tiempo'",
        "regionalisms": ["Mexico", "Argentina", "Colombia"]
    }


@pytest.fixture
def sample_grammar_data():
    """Provide sample grammar data for testing."""
    return {
        "phrase_structure": "Subjunctive mood with doubt",
        "explanation": "Use subjunctive after expressions of doubt like 'dudo que'",
        "resource_link": "https://example.com/subjunctive-guide"
    }


@pytest.fixture
def mock_logger():
    """Mock logger for testing without actual log output."""
    with patch('utils.logger.get_logger') as mock:
        mock_logger_instance = Mock()
        mock.return_value = mock_logger_instance
        yield mock_logger_instance


@pytest.fixture
def test_data_factory():
    """Factory for creating test data with various scenarios."""
    class TestDataFactory:
        @staticmethod
        def create_session_data(**overrides):
            base_data = {
                "teacher_id": 1,
                "session_date": "2025-04-10",
                "start_time": "17:00",
                "duration": "1h",
                "status": "planned"
            }
            base_data.update(overrides)
            return base_data
        
        @staticmethod
        def create_vocab_data(**overrides):
            base_data = {
                "word_phrase": "estudiar",
                "translation": "to study",
                "context_notes": "Regular -ar verb",
                "regionalisms": ["Universal"]
            }
            base_data.update(overrides)
            return base_data
        
        @staticmethod
        def create_invalid_session_data():
            return {
                "teacher_id": None,
                "session_date": "",
                "start_time": "invalid_time",
                "duration": "",
                "status": "unknown_status"
            }
    
    return TestDataFactory()


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables and settings."""
    # Set test-specific environment variables
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    
    # Mock external dependencies that shouldn't run during tests
    with patch('requests.get'), \
         patch('requests.post'), \
         patch('webbrowser.open'):
        yield


@pytest.fixture
def database_with_sample_data(temp_db, sample_teacher):
    """Database pre-populated with sample data for integration tests."""
    session_model = SessionModel(temp_db)
    vocab_model = VocabModel(temp_db)
    grammar_model = GrammarModel(temp_db)
    
    # Create sessions
    session_ids = []
    for i in range(3):
        session_id = session_model.create_session(
            teacher_id=sample_teacher,
            session_date=f"2025-04-{10 + i:02d}",
            start_time="17:00",
            duration="1h"
        )
        session_ids.append(session_id)
    
    # Add vocabulary to sessions
    vocab_words = [
        ("hola", "hello"),
        ("adiós", "goodbye"),
        ("gracias", "thank you"),
        ("por favor", "please")
    ]
    
    for session_id in session_ids[:2]:  # Add vocab to first 2 sessions
        for word, translation in vocab_words:
            vocab_model.add_vocab(
                session_id=session_id,
                word_phrase=word,
                translation=translation
            )
    
    # Add grammar patterns
    grammar_patterns = [
        ("Ser vs Estar", "Ser for permanent states, Estar for temporary"),
        ("Por vs Para", "Por for cause/exchange, Para for purpose/destination")
    ]
    
    for session_id in session_ids[:1]:  # Add grammar to first session
        for pattern, explanation in grammar_patterns:
            grammar_model.add_grammar(
                session_id=session_id,
                phrase_structure=pattern,
                explanation=explanation
            )
    
    return {
        "database": temp_db,
        "session_ids": session_ids,
        "teacher_id": sample_teacher,
        "vocab_count": len(vocab_words) * 2,
        "grammar_count": len(grammar_patterns)
    }


# Performance testing fixtures
@pytest.fixture
def performance_timer():
    """Timer fixture for performance testing."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
            return self.elapsed_time
        
        @property
        def elapsed_time(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


# Markers for organizing tests
def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "slow: Slow-running tests")
    config.addinivalue_line("markers", "gui: Tests requiring GUI")


# Test collection customization
def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        elif "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
        
        # Mark GUI tests
        if any(gui_indicator in item.name.lower() 
               for gui_indicator in ["widget", "window", "gui", "ui"]):
            item.add_marker(pytest.mark.gui)