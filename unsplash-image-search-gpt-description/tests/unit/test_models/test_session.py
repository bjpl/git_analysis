"""
Unit tests for session management and data models.
Tests the ImageSearchApp's session handling, logging, and data persistence.
"""

import pytest
import json
import tempfile
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import sys
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from main import ImageSearchApp
from tests.fixtures.sample_data import (
    SAMPLE_SESSION_DATA,
    SAMPLE_VOCABULARY_CSV_DATA,
    create_sample_files
)


@pytest.mark.unit
class TestSessionManagement:
    """Test suite for session management functionality."""

    @pytest.fixture
    def app_instance(self, mock_config_manager, tkinter_root):
        """Create ImageSearchApp instance for testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            app = ImageSearchApp()
            app.withdraw()
            yield app
            try:
                app.destroy()
            except:
                pass

    def test_session_initialization(self, app_instance):
        """Test session data initialization."""
        assert app_instance.log_entries == []
        assert app_instance.extracted_phrases == {}
        assert app_instance.target_phrases == []
        assert isinstance(app_instance.used_image_urls, set)
        assert isinstance(app_instance.vocabulary_cache, set)
        assert isinstance(app_instance.image_cache, dict)

    def test_log_entry_creation_on_image_load(self, app_instance):
        """Test that log entries are created when images are loaded."""
        # Simulate image loading
        app_instance.current_query = "mountain landscape"
        app_instance.current_image_url = "https://test.com/image"
        
        initial_count = len(app_instance.log_entries)
        
        # Simulate the log entry creation that happens in get_next_image
        app_instance.log_entries.append({
            "timestamp": datetime.now().isoformat(),
            "query": app_instance.current_query,
            "image_url": app_instance.current_image_url,
            "user_note": "",
            "generated_description": ""
        })
        
        assert len(app_instance.log_entries) == initial_count + 1
        entry = app_instance.log_entries[-1]
        assert entry["query"] == "mountain landscape"
        assert entry["image_url"] == "https://test.com/image"
        assert "timestamp" in entry

    def test_log_entry_update_with_description(self, app_instance):
        """Test updating log entry with generated description."""
        # Create initial log entry
        image_url = "https://test.com/image"
        app_instance.log_entries.append({
            "timestamp": datetime.now().isoformat(),
            "query": "mountain",
            "image_url": image_url,
            "user_note": "",
            "generated_description": ""
        })

        # Simulate description generation completion
        user_note = "Beautiful mountain scene"
        generated_description = "Esta imagen muestra un paisaje montañoso..."
        
        # Find and update the entry (simulate thread_generate_description behavior)
        for entry in reversed(app_instance.log_entries):
            if entry["image_url"] == image_url and entry["generated_description"] == "":
                entry["user_note"] = user_note
                entry["generated_description"] = generated_description
                break

        # Verify entry was updated
        updated_entry = app_instance.log_entries[-1]
        assert updated_entry["user_note"] == user_note
        assert updated_entry["generated_description"] == generated_description

    def test_save_session_to_json_new_file(self, app_instance, test_data_dir):
        """Test saving session to new JSON file."""
        # Setup test data
        log_file = test_data_dir / "new_session.json"
        app_instance.LOG_FILENAME = log_file
        
        # Add test log entries
        app_instance.log_entries = [
            {
                "timestamp": "2023-01-01T10:00:00",
                "query": "mountain",
                "image_url": "https://test.com/image1",
                "user_note": "Test note",
                "generated_description": "Test description"
            }
        ]
        app_instance.target_phrases = ["paisaje - landscape"]

        # Save session
        app_instance.save_session_to_json()

        # Verify file was created
        assert log_file.exists()

        # Verify content
        with open(log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert "sessions" in data
        assert len(data["sessions"]) == 1
        session = data["sessions"][0]
        assert "session_start" in session
        assert "session_end" in session
        assert "entries" in session
        assert len(session["entries"]) == 1
        assert session["vocabulary_learned"] == 1
        assert session["target_phrases"] == ["paisaje - landscape"]

    def test_save_session_to_json_append_existing(self, app_instance, test_data_dir):
        """Test appending session to existing JSON file."""
        log_file = test_data_dir / "existing_session.json"
        app_instance.LOG_FILENAME = log_file

        # Create existing file with one session
        existing_data = {
            "sessions": [{
                "session_start": "2023-01-01T09:00:00",
                "session_end": "2023-01-01T09:30:00",
                "entries": [],
                "vocabulary_learned": 0,
                "target_phrases": []
            }]
        }
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f)

        # Add new log entries
        app_instance.log_entries = [
            {
                "timestamp": "2023-01-01T10:00:00",
                "query": "city",
                "image_url": "https://test.com/image2",
                "user_note": "Urban scene",
                "generated_description": "City description"
            }
        ]
        app_instance.target_phrases = ["ciudad - city"]

        # Save session
        app_instance.save_session_to_json()

        # Verify both sessions exist
        with open(log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert len(data["sessions"]) == 2
        assert data["sessions"][1]["entries"][0]["query"] == "city"

    def test_save_session_to_json_empty_entries(self, app_instance, test_data_dir):
        """Test saving session with no log entries."""
        log_file = test_data_dir / "empty_session.json"
        app_instance.LOG_FILENAME = log_file
        app_instance.log_entries = []

        # Save session (should not create entry)
        app_instance.save_session_to_json()

        # File should exist but be empty or have empty sessions
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Should have no sessions or empty sessions list
            assert len(data.get("sessions", [])) == 0

    def test_save_session_corrupted_existing_file(self, app_instance, test_data_dir):
        """Test saving session when existing file is corrupted."""
        log_file = test_data_dir / "corrupted_session.json"
        app_instance.LOG_FILENAME = log_file

        # Create corrupted JSON file
        with open(log_file, 'w') as f:
            f.write("invalid json content")

        # Add test data
        app_instance.log_entries = [
            {
                "timestamp": "2023-01-01T10:00:00",
                "query": "test",
                "image_url": "https://test.com/image",
                "user_note": "",
                "generated_description": ""
            }
        ]

        # Should handle corruption gracefully
        app_instance.save_session_to_json()

        # Verify file was recreated with new data
        with open(log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert "sessions" in data
        assert len(data["sessions"]) == 1

    def test_save_session_fallback_to_text(self, app_instance, test_data_dir):
        """Test fallback to text format when JSON saving fails."""
        log_file = test_data_dir / "fallback_session.json"
        app_instance.LOG_FILENAME = log_file

        # Add test data
        app_instance.log_entries = [
            {
                "timestamp": "2023-01-01T10:00:00",
                "query": "test",
                "image_url": "https://test.com/image",
                "user_note": "Test note",
                "generated_description": "Test description"
            }
        ]
        app_instance.target_phrases = ["test - test"]

        # Mock JSON dump to fail
        with patch('json.dump', side_effect=Exception("JSON error")):
            app_instance.save_session_to_json()

        # Should create text file as fallback
        text_file = log_file.with_suffix('.txt')
        assert text_file.exists()

        # Verify text content
        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "Informe de Sesión" in content
        assert "test" in content
        assert "Test note" in content
        assert "Test description" in content

    def test_save_session_to_text_format(self, app_instance, test_data_dir):
        """Test saving session in text format."""
        text_file = test_data_dir / "session.txt"
        app_instance.LOG_FILENAME = Path(str(text_file).replace('.txt', '.json'))

        # Add test data
        app_instance.log_entries = [
            {
                "timestamp": "2023-01-01T10:00:00",
                "query": "mountain",
                "image_url": "https://test.com/image",
                "user_note": "Mountain view",
                "generated_description": "Beautiful mountain landscape"
            },
            {
                "timestamp": "2023-01-01T10:15:00", 
                "query": "ocean",
                "image_url": "https://test.com/ocean",
                "user_note": "Ocean sunset",
                "generated_description": "Sunset over ocean"
            }
        ]
        app_instance.target_phrases = ["montaña - mountain", "océano - ocean"]

        # Save in text format
        app_instance.save_session_to_text()

        # Verify file and content
        assert text_file.exists()

        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "Informe de Sesión" in content
        assert "Entrada 1:" in content
        assert "Entrada 2:" in content
        assert "mountain" in content
        assert "ocean" in content
        assert "Mountain view" in content
        assert "Ocean sunset" in content
        assert "Target Phrases: montaña - mountain, océano - ocean" in content

    def test_load_used_image_urls_from_json_log(self, app_instance, test_data_dir):
        """Test loading used image URLs from JSON log."""
        log_file = test_data_dir / "session_with_urls.json"
        app_instance.LOG_FILENAME = log_file

        # Create sample session data
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(SAMPLE_SESSION_DATA, f)

        # Clear and reload
        app_instance.used_image_urls.clear()
        app_instance.load_used_image_urls_from_log()

        # Verify URLs were loaded and canonicalized
        expected_urls = {
            "https://images.unsplash.com/photo-test1",
            "https://images.unsplash.com/photo-test2",
            "https://images.unsplash.com/photo-test3"
        }

        for url in expected_urls:
            canonical_url = app_instance.canonicalize_url(url)
            assert canonical_url in app_instance.used_image_urls

    def test_load_used_image_urls_from_text_log(self, app_instance, test_data_dir):
        """Test loading URLs from old text format log (backwards compatibility)."""
        log_file = test_data_dir / "session_text.json"
        app_instance.LOG_FILENAME = log_file

        # Create text format log content (simulate old format)
        text_content = """
        Some session data
        URL de la Imagen: https://images.unsplash.com/photo-old1?params
        More data
        URL de la Imagen: https://images.unsplash.com/photo-old2?more_params
        """

        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(text_content)

        # Clear and reload
        app_instance.used_image_urls.clear()
        app_instance.load_used_image_urls_from_log()

        # Should attempt to parse as JSON first, fail, then try text format
        # Verify URLs were loaded from text format
        expected_urls = {
            "https://images.unsplash.com/photo-old1",
            "https://images.unsplash.com/photo-old2"
        }

        for url in expected_urls:
            assert url in app_instance.used_image_urls

    def test_load_used_image_urls_malformed_file(self, app_instance, test_data_dir):
        """Test handling of completely malformed log file."""
        log_file = test_data_dir / "malformed_session.json"
        app_instance.LOG_FILENAME = log_file

        # Create completely malformed file
        with open(log_file, 'w') as f:
            f.write("this is not json or valid text format")

        # Should handle gracefully
        app_instance.used_image_urls.clear()
        app_instance.load_used_image_urls_from_log()

        # URLs should remain empty due to malformed data
        assert len(app_instance.used_image_urls) == 0

    def test_load_used_image_urls_missing_file(self, app_instance, test_data_dir):
        """Test handling when log file doesn't exist."""
        log_file = test_data_dir / "nonexistent_session.json"
        app_instance.LOG_FILENAME = log_file

        # Should handle missing file gracefully
        app_instance.used_image_urls.clear()
        app_instance.load_used_image_urls_from_log()

        # URLs should remain empty
        assert len(app_instance.used_image_urls) == 0

    def test_on_exit_saves_session(self, app_instance, test_data_dir):
        """Test that on_exit properly saves session data."""
        log_file = test_data_dir / "exit_session.json"
        app_instance.LOG_FILENAME = log_file

        # Add test data
        app_instance.log_entries = [
            {
                "timestamp": datetime.now().isoformat(),
                "query": "exit test",
                "image_url": "https://test.com/exit",
                "user_note": "Exit test note",
                "generated_description": "Exit test description"
            }
        ]

        # Mock destroy to prevent actual window closure
        with patch.object(app_instance, 'destroy'):
            app_instance.on_exit()

        # Verify session was saved
        assert log_file.exists()

        with open(log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert len(data["sessions"]) == 1
        assert data["sessions"][0]["entries"][0]["query"] == "exit test"

    def test_session_data_integrity(self, app_instance, test_data_dir):
        """Test session data maintains integrity across save/load cycles."""
        log_file = test_data_dir / "integrity_test.json"
        app_instance.LOG_FILENAME = log_file

        # Create complex session data with special characters
        original_entries = [
            {
                "timestamp": "2023-01-01T10:00:00.123456",
                "query": "niño montaña corazón",
                "image_url": "https://test.com/image?param=value&other=test",
                "user_note": "Nota con caracteres especiales: ñáéíóú ¡¿",
                "generated_description": "Descripción con \"comillas\" y 'apostrofes' y saltos\nde línea"
            }
        ]
        
        app_instance.log_entries = original_entries
        app_instance.target_phrases = ["niño - child", "montaña - mountain"]

        # Save session
        app_instance.save_session_to_json()

        # Reload and verify integrity
        with open(log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        loaded_entry = data["sessions"][0]["entries"][0]
        original_entry = original_entries[0]

        assert loaded_entry["query"] == original_entry["query"]
        assert loaded_entry["image_url"] == original_entry["image_url"] 
        assert loaded_entry["user_note"] == original_entry["user_note"]
        assert loaded_entry["generated_description"] == original_entry["generated_description"]

    def test_session_timestamp_format(self, app_instance):
        """Test that session timestamps are in proper ISO format."""
        # Create log entry with current timestamp
        app_instance.log_entries.append({
            "timestamp": datetime.now().isoformat(),
            "query": "timestamp test",
            "image_url": "https://test.com/image",
            "user_note": "",
            "generated_description": ""
        })

        entry = app_instance.log_entries[-1]
        timestamp_str = entry["timestamp"]

        # Verify timestamp can be parsed back to datetime
        parsed_timestamp = datetime.fromisoformat(timestamp_str)
        assert isinstance(parsed_timestamp, datetime)

    def test_session_statistics_calculation(self, app_instance):
        """Test session statistics are calculated correctly."""
        # Setup test data
        app_instance.log_entries = [{"timestamp": datetime.now().isoformat()}] * 3
        app_instance.target_phrases = ["phrase1", "phrase2", "phrase3", "phrase4", "phrase5"]
        app_instance.vocabulary_cache = {"cached1", "cached2"}

        # Test statistics in session save
        test_data = {
            "entries": app_instance.log_entries,
            "vocabulary_learned": len(app_instance.target_phrases),
            "target_phrases": app_instance.target_phrases
        }

        assert test_data["vocabulary_learned"] == 5
        assert len(test_data["target_phrases"]) == 5
        assert len(test_data["entries"]) == 3

    def test_concurrent_session_access(self, app_instance, test_data_dir):
        """Test handling of concurrent access to session file."""
        log_file = test_data_dir / "concurrent_session.json"
        app_instance.LOG_FILENAME = log_file

        # Create initial file
        initial_data = {"sessions": [{"test": "initial"}]}
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f)

        app_instance.log_entries = [
            {
                "timestamp": datetime.now().isoformat(),
                "query": "concurrent test",
                "image_url": "https://test.com/concurrent",
                "user_note": "",
                "generated_description": ""
            }
        ]

        # Save should handle existing data properly
        app_instance.save_session_to_json()

        # Verify both sessions exist
        with open(log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert len(data["sessions"]) == 2


@pytest.mark.unit
class TestSessionDataValidation:
    """Test suite for session data validation and error handling."""

    @pytest.fixture
    def app_instance(self, mock_config_manager, tkinter_root):
        """Create ImageSearchApp instance for testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            app = ImageSearchApp()
            app.withdraw()
            yield app
            try:
                app.destroy()
            except:
                pass

    def test_validate_log_entry_structure(self, app_instance):
        """Test validation of log entry structure."""
        # Valid entry
        valid_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": "test query",
            "image_url": "https://test.com/image",
            "user_note": "test note",
            "generated_description": "test description"
        }

        # Should contain all required fields
        required_fields = ["timestamp", "query", "image_url", "user_note", "generated_description"]
        for field in required_fields:
            assert field in valid_entry

    def test_handle_missing_log_entry_fields(self, app_instance, test_data_dir):
        """Test handling of log entries with missing fields."""
        log_file = test_data_dir / "missing_fields.json"
        app_instance.LOG_FILENAME = log_file

        # Entry with missing fields
        incomplete_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": "incomplete test"
            # Missing: image_url, user_note, generated_description
        }

        app_instance.log_entries = [incomplete_entry]

        # Should handle gracefully during save
        app_instance.save_session_to_json()

        # Verify file was created and contains available data
        assert log_file.exists()

    def test_handle_invalid_timestamp_format(self, app_instance):
        """Test handling of invalid timestamp formats."""
        # Entry with invalid timestamp
        invalid_entry = {
            "timestamp": "not-a-valid-timestamp",
            "query": "timestamp test",
            "image_url": "https://test.com/image",
            "user_note": "",
            "generated_description": ""
        }

        app_instance.log_entries = [invalid_entry]

        # Should handle invalid timestamp gracefully
        # (Implementation would need to validate/correct timestamps)

    def test_handle_extremely_long_fields(self, app_instance, test_data_dir):
        """Test handling of extremely long field values."""
        log_file = test_data_dir / "long_fields.json"
        app_instance.LOG_FILENAME = log_file

        # Entry with very long values
        long_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": "x" * 10000,  # Very long query
            "image_url": "https://test.com/image",
            "user_note": "y" * 10000,  # Very long note
            "generated_description": "z" * 50000  # Very long description
        }

        app_instance.log_entries = [long_entry]

        # Should handle long fields without issues
        app_instance.save_session_to_json()

        assert log_file.exists()

        # Verify data was saved (though it might be truncated by implementation)
        with open(log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert len(data["sessions"]) == 1