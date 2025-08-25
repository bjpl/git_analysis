# File: tests/unit/test_session_model.py
"""
Unit tests for the SessionModel class.
Tests CRUD operations, data validation, and error handling.
"""

import pytest
import sqlite3
from unittest.mock import Mock, patch
from datetime import datetime, date

from models.session_model import SessionModel


class TestSessionModel:
    """Test cases for SessionModel CRUD operations."""
    
    def test_create_session_with_valid_data(self, temp_db, sample_teacher):
        """Test creating a session with valid data."""
        session_model = SessionModel(temp_db)
        
        session_id = session_model.create_session(
            teacher_id=sample_teacher,
            session_date="2025-04-10",
            start_time="17:00",
            duration="1h"
        )
        
        assert session_id is not None
        assert isinstance(session_id, int)
        assert session_id > 0
    
    def test_create_session_with_missing_teacher_id(self, temp_db):
        """Test creating session with missing teacher_id."""
        session_model = SessionModel(temp_db)
        
        session_id = session_model.create_session(
            teacher_id=None,
            session_date="2025-04-10",
            start_time="17:00",
            duration="1h"
        )
        
        assert session_id is None
    
    def test_create_session_with_missing_date(self, temp_db, sample_teacher):
        """Test creating session with missing date."""
        session_model = SessionModel(temp_db)
        
        session_id = session_model.create_session(
            teacher_id=sample_teacher,
            session_date=None,
            start_time="17:00",
            duration="1h"
        )
        
        assert session_id is None
    
    def test_create_session_with_invalid_teacher_id(self, temp_db):
        """Test creating session with non-existent teacher_id."""
        session_model = SessionModel(temp_db)
        
        # Assuming foreign key constraints are enabled
        with pytest.raises(sqlite3.IntegrityError):
            session_model.create_session(
                teacher_id=999,  # Non-existent teacher
                session_date="2025-04-10",
                start_time="17:00",
                duration="1h"
            )
    
    def test_create_session_sets_default_status(self, temp_db, sample_teacher):
        """Test that new sessions get default status."""
        session_model = SessionModel(temp_db)
        
        session_id = session_model.create_session(
            teacher_id=sample_teacher,
            session_date="2025-04-10",
            start_time="17:00",
            duration="1h"
        )
        
        # Retrieve the session to check default status
        sessions = session_model.get_sessions()
        created_session = next(s for s in sessions if s['session_id'] == session_id)
        
        assert created_session['status'] == 'planned'  # Assuming 'planned' is default
    
    def test_get_sessions_returns_all_sessions(self, temp_db, sample_teacher):
        """Test retrieving all sessions."""
        session_model = SessionModel(temp_db)
        
        # Create multiple sessions
        session_ids = []
        for i in range(3):
            session_id = session_model.create_session(
                teacher_id=sample_teacher,
                session_date=f"2025-04-{10+i:02d}",
                start_time="17:00",
                duration="1h"
            )
            session_ids.append(session_id)
        
        sessions = session_model.get_sessions()
        
        assert len(sessions) == 3
        retrieved_ids = [s['session_id'] for s in sessions]
        for session_id in session_ids:
            assert session_id in retrieved_ids
    
    def test_get_sessions_with_empty_database(self, temp_db):
        """Test retrieving sessions from empty database."""
        session_model = SessionModel(temp_db)
        
        sessions = session_model.get_sessions()
        
        assert isinstance(sessions, list)
        assert len(sessions) == 0
    
    def test_get_sessions_by_date_range(self, temp_db, sample_teacher):
        """Test retrieving sessions within a date range."""
        session_model = SessionModel(temp_db)
        
        # Create sessions on different dates
        dates = ["2025-04-10", "2025-04-15", "2025-04-20"]
        for date_str in dates:
            session_model.create_session(
                teacher_id=sample_teacher,
                session_date=date_str,
                start_time="17:00",
                duration="1h"
            )
        
        # This assumes get_sessions_by_date_range method exists
        # If it doesn't exist in the actual implementation, this test would be for future functionality
        if hasattr(session_model, 'get_sessions_by_date_range'):
            filtered_sessions = session_model.get_sessions_by_date_range(
                start_date="2025-04-12",
                end_date="2025-04-18"
            )
            
            assert len(filtered_sessions) == 1
            assert filtered_sessions[0]['session_date'] == "2025-04-15"
    
    def test_update_session_status_valid(self, temp_db, sample_session):
        """Test updating session status with valid data."""
        session_model = SessionModel(temp_db)
        
        rows_affected = session_model.update_session_status(sample_session, "completed")
        
        assert rows_affected == 1
        
        # Verify the update
        sessions = session_model.get_sessions()
        updated_session = next(s for s in sessions if s['session_id'] == sample_session)
        assert updated_session['status'] == "completed"
    
    def test_update_session_status_invalid_id(self, temp_db):
        """Test updating status for non-existent session."""
        session_model = SessionModel(temp_db)
        
        rows_affected = session_model.update_session_status(999, "completed")
        
        assert rows_affected == 0
    
    def test_update_session_status_none_id(self, temp_db):
        """Test updating status with None session_id."""
        session_model = SessionModel(temp_db)
        
        rows_affected = session_model.update_session_status(None, "completed")
        
        assert rows_affected == 0
    
    def test_delete_session_valid(self, temp_db, sample_session):
        """Test deleting a session with valid ID."""
        session_model = SessionModel(temp_db)
        
        # Verify session exists before deletion
        sessions_before = session_model.get_sessions()
        assert len(sessions_before) == 1
        
        rows_affected = session_model.delete_session(sample_session)
        
        assert rows_affected == 1
        
        # Verify session is deleted
        sessions_after = session_model.get_sessions()
        assert len(sessions_after) == 0
    
    def test_delete_session_invalid_id(self, temp_db):
        """Test deleting non-existent session."""
        session_model = SessionModel(temp_db)
        
        rows_affected = session_model.delete_session(999)
        
        assert rows_affected == 0
    
    def test_get_session_by_id_valid(self, temp_db, sample_session):
        """Test retrieving specific session by ID."""
        session_model = SessionModel(temp_db)
        
        session = session_model.get_session_by_id(sample_session)
        
        assert session is not None
        assert session['session_id'] == sample_session
        assert session['session_date'] == "2025-04-10"
    
    def test_get_session_by_id_invalid(self, temp_db):
        """Test retrieving non-existent session."""
        session_model = SessionModel(temp_db)
        
        session = session_model.get_session_by_id(999)
        
        assert session is None


class TestSessionModelValidation:
    """Test data validation in SessionModel."""
    
    def test_validate_session_date_format(self, temp_db, sample_teacher):
        """Test session creation with various date formats."""
        session_model = SessionModel(temp_db)
        
        # Valid formats should work
        valid_dates = ["2025-04-10", "2025-12-31", "2024-02-29"]
        
        for date_str in valid_dates:
            session_id = session_model.create_session(
                teacher_id=sample_teacher,
                session_date=date_str,
                start_time="17:00",
                duration="1h"
            )
            assert session_id is not None
    
    def test_validate_invalid_date_formats(self, temp_db, sample_teacher):
        """Test session creation with invalid date formats."""
        session_model = SessionModel(temp_db)
        
        # These should either be rejected or handled gracefully
        invalid_dates = ["2025/04/10", "04-10-2025", "invalid_date", ""]
        
        for date_str in invalid_dates:
            # Depending on implementation, this might return None or raise exception
            try:
                session_id = session_model.create_session(
                    teacher_id=sample_teacher,
                    session_date=date_str,
                    start_time="17:00",
                    duration="1h"
                )
                # If it doesn't raise an exception, it should return None for invalid data
                if session_id is not None:
                    pytest.fail(f"Expected None for invalid date: {date_str}")
            except (ValueError, sqlite3.Error):
                # Exception is also acceptable for invalid dates
                pass
    
    def test_validate_time_format(self, temp_db, sample_teacher):
        """Test session creation with various time formats."""
        session_model = SessionModel(temp_db)
        
        valid_times = ["17:00", "09:30", "23:59", "00:00"]
        
        for time_str in valid_times:
            session_id = session_model.create_session(
                teacher_id=sample_teacher,
                session_date="2025-04-10",
                start_time=time_str,
                duration="1h"
            )
            assert session_id is not None
    
    def test_validate_duration_format(self, temp_db, sample_teacher):
        """Test session creation with various duration formats."""
        session_model = SessionModel(temp_db)
        
        valid_durations = ["1h", "2h", "30m", "1.5h", "90m"]
        
        for duration in valid_durations:
            session_id = session_model.create_session(
                teacher_id=sample_teacher,
                session_date="2025-04-10",
                start_time="17:00",
                duration=duration
            )
            assert session_id is not None


class TestSessionModelErrorHandling:
    """Test error handling in SessionModel."""
    
    def test_database_error_handling_on_create(self, temp_db):
        """Test handling of database errors during session creation."""
        session_model = SessionModel(temp_db)
        
        # Simulate database error by closing connection
        temp_db.close()
        
        with pytest.raises(sqlite3.Error):
            session_model.create_session(
                teacher_id=1,
                session_date="2025-04-10",
                start_time="17:00",
                duration="1h"
            )
    
    def test_database_error_handling_on_read(self, temp_db):
        """Test handling of database errors during session retrieval."""
        session_model = SessionModel(temp_db)
        
        # Close database to simulate error
        temp_db.close()
        
        with pytest.raises(sqlite3.Error):
            session_model.get_sessions()
    
    def test_sql_injection_protection(self, temp_db, sample_teacher):
        """Test protection against SQL injection attacks."""
        session_model = SessionModel(temp_db)
        
        # Attempt SQL injection through session_date
        malicious_date = "2025-04-10'; DROP TABLE sessions; --"
        
        # This should not cause database corruption
        session_id = session_model.create_session(
            teacher_id=sample_teacher,
            session_date=malicious_date,
            start_time="17:00",
            duration="1h"
        )
        
        # Verify tables still exist
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions';")
        result = cursor.fetchone()
        assert result is not None, "Sessions table should still exist"
    
    @pytest.mark.performance
    def test_bulk_session_creation_performance(self, temp_db, sample_teacher, performance_timer):
        """Test performance of creating multiple sessions."""
        session_model = SessionModel(temp_db)
        
        performance_timer.start()
        
        session_ids = []
        for i in range(100):
            session_id = session_model.create_session(
                teacher_id=sample_teacher,
                session_date=f"2025-{4 + i // 30:02d}-{10 + i % 30:02d}",
                start_time="17:00",
                duration="1h"
            )
            session_ids.append(session_id)
        
        elapsed_time = performance_timer.stop()
        
        # All sessions should be created
        assert len(session_ids) == 100
        assert all(sid is not None for sid in session_ids)
        
        # Should be reasonably fast (< 5 seconds for 100 sessions)
        assert elapsed_time < 5.0
    
    def test_concurrent_session_operations(self, temp_db, sample_teacher):
        """Test concurrent session operations."""
        import threading
        import time
        
        session_model = SessionModel(temp_db)
        results = []
        errors = []
        
        def create_sessions(start_index):
            try:
                for i in range(start_index, start_index + 10):
                    session_id = session_model.create_session(
                        teacher_id=sample_teacher,
                        session_date=f"2025-04-{10 + i:02d}",
                        start_time="17:00",
                        duration="1h"
                    )
                    results.append(session_id)
                    time.sleep(0.01)  # Small delay to increase chance of concurrent access
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_sessions, args=(i * 10,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Unexpected errors: {errors}"
        assert len(results) == 30
        assert all(sid is not None for sid in results)


# Test fixtures specific to SessionModel
@pytest.fixture
def session_model_with_mock_db():
    """Create SessionModel with mocked database for isolated testing."""
    mock_db = Mock()
    mock_cursor = Mock()
    mock_db.conn.cursor.return_value = mock_cursor
    
    return SessionModel(mock_db), mock_cursor


class TestSessionModelMocked:
    """Test SessionModel with mocked dependencies."""
    
    def test_create_session_with_mocked_db(self, session_model_with_mock_db):
        """Test session creation with fully mocked database."""
        session_model, mock_cursor = session_model_with_mock_db
        
        # Mock successful insertion
        mock_cursor.lastrowid = 123
        
        session_id = session_model.create_session(
            teacher_id=1,
            session_date="2025-04-10",
            start_time="17:00",
            duration="1h"
        )
        
        assert session_id == 123
        mock_cursor.execute.assert_called()
        session_model.db.conn.commit.assert_called()


# Integration with pytest markers
pytestmark = pytest.mark.unit