# File: tests/unit/test_database.py
"""
Unit tests for the Database class.
Tests connection handling, initialization, and basic operations.
"""

import pytest
import sqlite3
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock

from models.database import Database


class TestDatabase:
    """Test cases for Database class functionality."""
    
    def test_database_initialization_with_default_path(self, mock_logger):
        """Test database initialization with default path."""
        with patch('models.database.sqlite3.connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value = mock_conn
            
            db = Database()
            
            assert db.conn == mock_conn
            mock_connect.assert_called_once()
            mock_conn.__setattr__.assert_called_with('row_factory', sqlite3.Row)
    
    def test_database_initialization_with_custom_path(self, mock_logger):
        """Test database initialization with custom path."""
        custom_path = "/custom/path/test.db"
        
        with patch('models.database.sqlite3.connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value = mock_conn
            
            db = Database(custom_path)
            
            assert db.db_path == custom_path
            assert db.conn == mock_conn
            mock_connect.assert_called_once_with(custom_path)
    
    def test_database_connection_failure(self, mock_logger):
        """Test handling of database connection failures."""
        with patch('models.database.sqlite3.connect') as mock_connect:
            mock_connect.side_effect = sqlite3.Error("Connection failed")
            
            with pytest.raises(sqlite3.Error):
                Database()
    
    def test_database_init_db_creates_all_tables(self, temp_db):
        """Test that init_db creates all required tables."""
        cursor = temp_db.conn.cursor()
        
        # Check that all tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'teachers', 'sessions', 'vocab', 'vocab_regionalisms',
            'grammar', 'challenges', 'comfort'
        ]
        
        for table in expected_tables:
            assert table in tables, f"Table {table} was not created"
    
    def test_database_init_db_enables_foreign_keys(self, temp_db):
        """Test that foreign keys are enabled."""
        cursor = temp_db.conn.cursor()
        cursor.execute("PRAGMA foreign_keys;")
        result = cursor.fetchone()
        
        # Foreign keys should be enabled (1)
        assert result[0] == 1
    
    def test_database_init_db_handles_errors(self, mock_logger):
        """Test error handling during database initialization."""
        with patch('models.database.sqlite3.connect') as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = sqlite3.Error("Table creation failed")
            mock_connect.return_value = mock_conn
            
            db = Database()
            db.init_db()
            
            # Should handle the error gracefully
            mock_logger.error.assert_called()
    
    def test_database_close_connection(self, mock_logger):
        """Test closing database connection."""
        with patch('models.database.sqlite3.connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value = mock_conn
            
            db = Database()
            db.close()
            
            mock_conn.close.assert_called_once()
    
    def test_database_close_when_no_connection(self, mock_logger):
        """Test closing when no connection exists."""
        with patch('models.database.sqlite3.connect') as mock_connect:
            mock_connect.return_value = None
            
            db = Database()
            db.conn = None
            
            # Should not raise an error
            db.close()
    
    def test_teachers_table_structure(self, temp_db):
        """Test the structure of the teachers table."""
        cursor = temp_db.conn.cursor()
        cursor.execute("PRAGMA table_info(teachers);")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_columns = {
            'teacher_id': 'INTEGER',
            'name': 'TEXT',
            'region': 'TEXT',
            'notes': 'TEXT'
        }
        
        for col_name, col_type in expected_columns.items():
            assert col_name in columns
            assert col_type in columns[col_name]
    
    def test_sessions_table_structure(self, temp_db):
        """Test the structure of the sessions table."""
        cursor = temp_db.conn.cursor()
        cursor.execute("PRAGMA table_info(sessions);")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_columns = {
            'session_id': 'INTEGER',
            'teacher_id': 'INTEGER',
            'session_date': 'TEXT',
            'start_time': 'TEXT',
            'duration': 'TEXT',
            'status': 'TEXT',
            'timestamp': 'TEXT'
        }
        
        for col_name, col_type in expected_columns.items():
            assert col_name in columns
            assert col_type in columns[col_name]
    
    def test_vocab_table_structure(self, temp_db):
        """Test the structure of the vocab table."""
        cursor = temp_db.conn.cursor()
        cursor.execute("PRAGMA table_info(vocab);")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_columns = {
            'vocab_id': 'INTEGER',
            'session_id': 'INTEGER',
            'word_phrase': 'TEXT',
            'translation': 'TEXT',
            'context_notes': 'TEXT',
            'timestamp': 'TEXT'
        }
        
        for col_name, col_type in expected_columns.items():
            assert col_name in columns
            assert col_type in columns[col_name]
    
    def test_foreign_key_constraints(self, temp_db):
        """Test that foreign key constraints are properly defined."""
        cursor = temp_db.conn.cursor()
        
        # Test sessions table foreign key
        cursor.execute("PRAGMA foreign_key_list(sessions);")
        fk_info = cursor.fetchall()
        assert len(fk_info) > 0
        assert any(fk[2] == 'teachers' for fk in fk_info)
        
        # Test vocab table foreign key
        cursor.execute("PRAGMA foreign_key_list(vocab);")
        fk_info = cursor.fetchall()
        assert len(fk_info) > 0
        assert any(fk[2] == 'sessions' for fk in fk_info)
    
    def test_database_context_manager_behavior(self):
        """Test database connection as context manager (if implemented)."""
        # This test would be relevant if Database class implements __enter__ and __exit__
        pass
    
    @pytest.mark.performance
    def test_database_connection_performance(self, performance_timer):
        """Test database connection performance."""
        performance_timer.start()
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            db = Database(tmp_path)
            db.init_db()
            connection_time = performance_timer.stop()
            
            # Connection and initialization should be fast (< 1 second)
            assert connection_time < 1.0
            
            db.close()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_multiple_database_instances(self):
        """Test creating multiple database instances."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp1, \
             tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp2:
            
            try:
                db1 = Database(tmp1.name)
                db1.init_db()
                
                db2 = Database(tmp2.name)
                db2.init_db()
                
                # Both should be separate instances
                assert db1.conn != db2.conn
                assert db1.db_path != db2.db_path
                
                db1.close()
                db2.close()
            finally:
                for path in [tmp1.name, tmp2.name]:
                    if os.path.exists(path):
                        os.unlink(path)


class TestDatabaseEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_database_with_invalid_path_permissions(self):
        """Test database creation with invalid path permissions."""
        invalid_path = "/root/cannot_write_here.db"
        
        with pytest.raises((sqlite3.Error, PermissionError, OSError)):
            Database(invalid_path)
    
    def test_database_init_with_existing_tables(self, temp_db):
        """Test initializing database when tables already exist."""
        # Call init_db twice - should not raise errors
        temp_db.init_db()  # Called again
        
        # Verify tables still exist and are functional
        cursor = temp_db.conn.cursor()
        cursor.execute("INSERT INTO teachers (name) VALUES ('Test Teacher');")
        temp_db.conn.commit()
        
        cursor.execute("SELECT name FROM teachers WHERE name = 'Test Teacher';")
        result = cursor.fetchone()
        assert result is not None
    
    def test_database_operations_after_close(self, temp_db):
        """Test that operations fail gracefully after closing connection."""
        temp_db.close()
        
        with pytest.raises((sqlite3.Error, AttributeError)):
            cursor = temp_db.conn.cursor()
            cursor.execute("SELECT 1;")
    
    def test_concurrent_database_access(self, temp_db):
        """Test concurrent access to the same database file."""
        import threading
        import time
        
        results = []
        errors = []
        
        def database_operation(db_path, operation_id):
            try:
                db = Database(db_path)
                cursor = db.conn.cursor()
                
                # Perform some operations
                cursor.execute("INSERT INTO teachers (name) VALUES (?);", (f"Teacher {operation_id}",))
                db.conn.commit()
                
                cursor.execute("SELECT COUNT(*) FROM teachers;")
                count = cursor.fetchone()[0]
                results.append((operation_id, count))
                
                db.close()
            except Exception as e:
                errors.append((operation_id, str(e)))
        
        # Create multiple threads accessing the same database
        threads = []
        for i in range(3):
            thread = threading.Thread(target=database_operation, args=(temp_db.db_path, i))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results - should have some successful operations
        assert len(results) > 0
        # Some errors are acceptable due to SQLite locking behavior
        print(f"Results: {results}, Errors: {errors}")


# Integration with pytest markers
pytestmark = pytest.mark.unit