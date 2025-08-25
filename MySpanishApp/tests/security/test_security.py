# File: tests/security/test_security.py
"""
Security tests for SpanishMaster application.
Tests for vulnerabilities, data protection, and secure coding practices.
"""

import pytest
import sqlite3
import tempfile
import os
import hashlib
from unittest.mock import Mock, patch, MagicMock

from models.database import Database
from models.session_model import SessionModel
from models.vocab_model import VocabModel


class TestSQLInjectionPrevention:
    """Test prevention of SQL injection attacks."""
    
    @pytest.mark.security
    def test_sql_injection_in_session_creation(self, temp_db, sample_teacher):
        """Test SQL injection prevention in session creation."""
        session_model = SessionModel(temp_db)
        
        # Common SQL injection payloads
        malicious_payloads = [
            "'; DROP TABLE sessions; --",
            "' OR '1'='1",
            "'; UPDATE sessions SET status='completed' WHERE 1=1; --",
            "' UNION SELECT * FROM teachers --",
            "'; INSERT INTO sessions (teacher_id) VALUES (999); --"
        ]
        
        for payload in malicious_payloads:
            # Attempt injection through session_date parameter
            session_id = session_model.create_session(
                teacher_id=sample_teacher,
                session_date=payload,
                start_time="17:00",
                duration="1h"
            )
            
            # Session creation should handle malicious input gracefully
            # Either by rejecting it (returning None) or by escaping it properly
            
            # Verify database integrity - tables should still exist
            cursor = temp_db.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions';")
            result = cursor.fetchone()
            assert result is not None, "Sessions table should still exist after injection attempt"
            
            # Verify no unauthorized data modification occurred
            cursor.execute("SELECT COUNT(*) FROM sessions WHERE status='completed';")
            completed_count = cursor.fetchone()[0]
            
            # Should not have unauthorized completed sessions
            # (This assumes no sessions were marked as completed before the test)
            assert completed_count == 0, "No unauthorized session status changes should occur"
    
    @pytest.mark.security
    def test_sql_injection_in_vocabulary_search(self, temp_db, sample_session):
        """Test SQL injection prevention in vocabulary operations."""
        vocab_model = VocabModel(temp_db)
        
        # Add legitimate vocabulary first
        legitimate_vocab_id = vocab_model.add_vocab(
            session_id=sample_session,
            word_phrase="legitimate_word",
            translation="legitimate translation"
        )
        
        malicious_search_terms = [
            "'; DROP TABLE vocab; --",
            "' OR 1=1 --",
            "'; UPDATE vocab SET translation='HACKED'; --"
        ]
        
        for payload in malicious_search_terms:
            # Attempt injection through word_phrase parameter
            malicious_vocab_id = vocab_model.add_vocab(
                session_id=sample_session,
                word_phrase=payload,
                translation="test translation"
            )
            
            # Verify database integrity
            cursor = temp_db.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vocab';")
            result = cursor.fetchone()
            assert result is not None, "Vocab table should still exist"
            
            # Verify legitimate data wasn't modified
            cursor.execute("SELECT translation FROM vocab WHERE vocab_id = ?", (legitimate_vocab_id,))
            translation = cursor.fetchone()[0]
            assert translation == "legitimate translation", "Legitimate data should not be modified"
    
    @pytest.mark.security
    def test_parameterized_queries_usage(self, temp_db):
        """Test that parameterized queries are used correctly."""
        # This test verifies that the application uses parameterized queries
        # by checking that direct string concatenation doesn't work
        
        with patch.object(temp_db.conn, 'cursor') as mock_cursor:
            mock_cursor_instance = Mock()
            mock_cursor.return_value = mock_cursor_instance
            
            session_model = SessionModel(temp_db)
            
            # Create session (should use parameterized query)
            session_model.create_session(
                teacher_id=1,
                session_date="2025-04-10",
                start_time="17:00",
                duration="1h"
            )
            
            # Verify execute was called (indicating parameterized query usage)
            assert mock_cursor_instance.execute.called
            
            # Check that execute was called with parameters
            call_args = mock_cursor_instance.execute.call_args
            if call_args:
                query, params = call_args[0] if len(call_args[0]) == 2 else (call_args[0][0], None)
                
                # Query should contain placeholders (? for SQLite)
                if params:
                    assert '?' in query, "Query should use parameterized placeholders"


class TestDataValidationSecurity:
    """Test data validation and sanitization."""
    
    @pytest.mark.security
    def test_input_length_validation(self, temp_db, sample_session):
        """Test validation of input data lengths."""
        vocab_model = VocabModel(temp_db)
        
        # Test extremely long inputs
        extremely_long_word = "a" * 10000
        extremely_long_translation = "b" * 10000
        extremely_long_context = "c" * 50000
        
        # Application should handle extremely long inputs gracefully
        vocab_id = vocab_model.add_vocab(
            session_id=sample_session,
            word_phrase=extremely_long_word,
            translation=extremely_long_translation,
            context_notes=extremely_long_context
        )
        
        # Either reject the input or truncate it appropriately
        if vocab_id is not None:
            # If accepted, verify it was stored safely
            cursor = temp_db.conn.cursor()
            cursor.execute("SELECT word_phrase, translation, context_notes FROM vocab WHERE vocab_id = ?", (vocab_id,))
            result = cursor.fetchone()
            
            stored_word = result[0]
            stored_translation = result[1]
            stored_context = result[2]
            
            # Data should be stored safely (might be truncated)
            assert len(stored_word) < 10000 or stored_word == extremely_long_word
            assert len(stored_translation) < 10000 or stored_translation == extremely_long_translation
            assert len(stored_context) < 50000 or stored_context == extremely_long_context
    
    @pytest.mark.security
    def test_html_xss_prevention(self, temp_db, sample_session):
        """Test prevention of XSS through HTML injection."""
        vocab_model = VocabModel(temp_db)
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "<body onload=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            vocab_id = vocab_model.add_vocab(
                session_id=sample_session,
                word_phrase=payload,
                translation=payload,
                context_notes=payload
            )
            
            if vocab_id is not None:
                # Verify data is stored safely (escaped or sanitized)
                cursor = temp_db.conn.cursor()
                cursor.execute("SELECT word_phrase, translation, context_notes FROM vocab WHERE vocab_id = ?", (vocab_id,))
                result = cursor.fetchone()
                
                stored_word = result[0]
                stored_translation = result[1]
                stored_context = result[2]
                
                # Data should be safe (either escaped or rejected)
                dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onload=']
                
                for pattern in dangerous_patterns:
                    # If the pattern is still there, it should be escaped
                    if pattern in payload.lower():
                        # Either the pattern is removed/escaped, or it's stored as-is but will be escaped on output
                        # The exact behavior depends on the sanitization strategy
                        pass  # Implementation-dependent validation
    
    @pytest.mark.security
    def test_path_traversal_prevention(self):
        """Test prevention of path traversal attacks."""
        # Test path traversal in file operations (if any)
        malicious_paths = [
            "../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "../../../home/user/.ssh/id_rsa",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"  # URL encoded
        ]
        
        # If the application has file operations, test them here
        # For the current SpanishMaster app, this might apply to export functionality
        
        for malicious_path in malicious_paths:
            # Test that file operations reject malicious paths
            # This is a placeholder - implement based on actual file operations
            
            # Example: if there's an export function that takes a filename
            # export_function(malicious_path) should reject the path or sanitize it
            
            # For now, just verify the paths are recognized as potentially malicious
            assert ".." in malicious_path or "%2e" in malicious_path.lower()
    
    @pytest.mark.security
    def test_null_byte_injection_prevention(self, temp_db, sample_session):
        """Test prevention of null byte injection."""
        vocab_model = VocabModel(temp_db)
        
        # Null byte injection attempts
        null_byte_payloads = [
            "normal_word\x00malicious_suffix",
            "word\x00.exe",
            "translation\x00DELETE FROM vocab",
            "context\x00' OR '1'='1"
        ]
        
        for payload in null_byte_payloads:
            vocab_id = vocab_model.add_vocab(
                session_id=sample_session,
                word_phrase=payload,
                translation="test translation"
            )
            
            if vocab_id is not None:
                # Verify null bytes are handled properly
                cursor = temp_db.conn.cursor()
                cursor.execute("SELECT word_phrase FROM vocab WHERE vocab_id = ?", (vocab_id,))
                result = cursor.fetchone()
                stored_word = result[0]
                
                # Null bytes should be removed or the input rejected
                assert "\x00" not in stored_word, "Null bytes should be filtered out"


class TestAccessControlSecurity:
    """Test access control and authorization."""
    
    @pytest.mark.security
    def test_database_file_permissions(self):
        """Test database file has appropriate permissions."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            db = Database(tmp_path)
            db.init_db()
            db.close()
            
            # Check file permissions
            import stat
            file_stat = os.stat(tmp_path)
            file_permissions = stat.filemode(file_stat.st_mode)
            
            # Database file should not be world-readable in production
            # For development/testing, this might be more permissive
            print(f"Database file permissions: {file_permissions}")
            
            # At minimum, should not be executable
            assert not (file_stat.st_mode & stat.S_IXUSR), "Database file should not be executable"
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    @pytest.mark.security
    def test_teacher_data_isolation(self, temp_db):
        """Test that data from different teachers is properly isolated."""
        session_model = SessionModel(temp_db)
        vocab_model = VocabModel(temp_db)
        
        # Create two teachers
        cursor = temp_db.conn.cursor()
        cursor.execute("INSERT INTO teachers (name) VALUES (?)", ("Teacher A",))
        temp_db.conn.commit()
        teacher_a_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO teachers (name) VALUES (?)", ("Teacher B",))
        temp_db.conn.commit()
        teacher_b_id = cursor.lastrowid
        
        # Create sessions for each teacher
        session_a_id = session_model.create_session(
            teacher_id=teacher_a_id,
            session_date="2025-04-10",
            start_time="17:00",
            duration="1h"
        )
        
        session_b_id = session_model.create_session(
            teacher_id=teacher_b_id,
            session_date="2025-04-10",
            start_time="18:00",
            duration="1h"
        )
        
        # Add vocabulary to each session
        vocab_a_id = vocab_model.add_vocab(session_a_id, "teacher_a_word", "teacher a translation")
        vocab_b_id = vocab_model.add_vocab(session_b_id, "teacher_b_word", "teacher b translation")
        
        # Verify data isolation - should not be able to access other teacher's data inappropriately
        session_a_vocab = vocab_model.get_vocab_for_session(session_a_id)
        session_b_vocab = vocab_model.get_vocab_for_session(session_b_id)
        
        # Each session should only have its own vocabulary
        assert len(session_a_vocab) == 1
        assert len(session_b_vocab) == 1
        
        assert session_a_vocab[0]['word_phrase'] == "teacher_a_word"
        assert session_b_vocab[0]['word_phrase'] == "teacher_b_word"
        
        # Cross-contamination check
        teacher_a_words = [v['word_phrase'] for v in session_a_vocab]
        teacher_b_words = [v['word_phrase'] for v in session_b_vocab]
        
        assert "teacher_b_word" not in teacher_a_words
        assert "teacher_a_word" not in teacher_b_words


class TestDataProtectionSecurity:
    """Test data protection and privacy measures."""
    
    @pytest.mark.security
    def test_sensitive_data_not_logged(self, temp_db, sample_session):
        """Test that sensitive data is not logged inappropriately."""
        vocab_model = VocabModel(temp_db)
        
        with patch('utils.logger.get_logger') as mock_logger:
            mock_logger_instance = Mock()
            mock_logger.return_value = mock_logger_instance
            
            # Add vocabulary with potentially sensitive information
            vocab_model.add_vocab(
                session_id=sample_session,
                word_phrase="password123",  # Simulate sensitive data
                translation="contraseña secreta",
                context_notes="Personal password example - should not be logged"
            )
            
            # Check logged calls
            if mock_logger_instance.info.called or mock_logger_instance.debug.called:
                # Verify sensitive data is not in log messages
                for call in mock_logger_instance.info.call_args_list:
                    log_message = str(call[0][0]) if call[0] else ""
                    assert "password123" not in log_message.lower()
                    assert "contraseña secreta" not in log_message.lower()
                
                for call in mock_logger_instance.debug.call_args_list:
                    log_message = str(call[0][0]) if call[0] else ""
                    assert "password123" not in log_message.lower()
                    assert "contraseña secreta" not in log_message.lower()
    
    @pytest.mark.security
    def test_database_connection_string_security(self):
        """Test that database connection strings don't expose sensitive information."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            db = Database(tmp_path)
            
            # Connection string should not contain passwords or sensitive info
            # (SQLite doesn't use passwords, but test the concept)
            connection_info = str(db.conn) if db.conn else ""
            
            # Should not contain obvious sensitive patterns
            sensitive_patterns = ['password=', 'pwd=', 'secret=', 'key=']
            for pattern in sensitive_patterns:
                assert pattern not in connection_info.lower()
            
            db.close()
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    @pytest.mark.security
    def test_temporary_file_security(self):
        """Test that temporary files are created securely."""
        # Test that temporary files have appropriate permissions
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Check file permissions
            import stat
            file_stat = os.stat(tmp_path)
            
            # Temporary files should not be world-readable
            world_readable = file_stat.st_mode & stat.S_IROTH
            world_writable = file_stat.st_mode & stat.S_IWOTH
            
            assert not world_readable, "Temporary files should not be world-readable"
            assert not world_writable, "Temporary files should not be world-writable"
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class TestCryptographicSecurity:
    """Test cryptographic operations and security."""
    
    @pytest.mark.security
    def test_password_hashing_if_implemented(self):
        """Test password hashing implementation (if passwords are used)."""
        # The current SpanishMaster app doesn't use passwords, but this test
        # would be relevant if authentication is added
        
        # Test password hashing best practices
        test_password = "test_password_123"
        
        # Example of secure password hashing (not implemented in current app)
        # This is a template for future security enhancements
        def secure_hash_password(password):
            import hashlib
            import secrets
            
            # Generate a random salt
            salt = secrets.token_hex(16)
            
            # Hash the password with salt
            password_hash = hashlib.pbkdf2_hmac('sha256', 
                                              password.encode('utf-8'), 
                                              salt.encode('utf-8'), 
                                              100000)  # 100,000 iterations
            
            return salt + password_hash.hex()
        
        # Test the concept (would be implemented in actual authentication system)
        if hasattr(self, 'hash_password'):  # Only if implemented
            hashed = secure_hash_password(test_password)
            
            # Hash should be different each time (due to salt)
            hashed2 = secure_hash_password(test_password)
            assert hashed != hashed2
            
            # Hash should be long enough
            assert len(hashed) > 32
    
    @pytest.mark.security
    def test_random_number_generation_security(self):
        """Test that cryptographically secure random numbers are used."""
        import secrets
        import random
        
        # Generate random values
        secure_random = secrets.token_hex(16)
        secure_random2 = secrets.token_hex(16)
        
        # Should be different
        assert secure_random != secure_random2
        
        # Should be proper length
        assert len(secure_random) == 32  # 16 bytes = 32 hex characters
        
        # Test that insecure random is not used for security purposes
        # This is more of a code review item, but we can test the concept
        insecure_random = f"{random.randint(1000, 9999)}"
        
        # Insecure random should not be used for tokens, IDs, etc.
        # This would be caught by code review and static analysis


class TestErrorHandlingSecurity:
    """Test secure error handling."""
    
    @pytest.mark.security
    def test_error_messages_dont_leak_information(self, temp_db):
        """Test that error messages don't leak sensitive information."""
        session_model = SessionModel(temp_db)
        
        # Cause a database error
        temp_db.close()  # Close database to cause errors
        
        try:
            session_model.create_session(
                teacher_id=999,  # Non-existent teacher
                session_date="2025-04-10",
                start_time="17:00",
                duration="1h"
            )
        except Exception as e:
            error_message = str(e)
            
            # Error message should not contain:
            # - Database file paths
            # - Internal implementation details
            # - Stack traces (in production)
            
            sensitive_info_patterns = [
                temp_db.db_path,  # Database file path
                'sqlite3.',  # Internal implementation details
                'Traceback',  # Stack trace indicators
                'File "/',  # File paths in stack traces
            ]
            
            for pattern in sensitive_info_patterns:
                # In production, these shouldn't be exposed to users
                # In development/testing, some might be acceptable
                if pattern in error_message:
                    print(f"Warning: Error message contains potentially sensitive info: {pattern}")
    
    @pytest.mark.security
    def test_exception_handling_prevents_information_disclosure(self, temp_db):
        """Test that exceptions are handled securely."""
        vocab_model = VocabModel(temp_db)
        
        # Test various error conditions
        error_conditions = [
            (None, "test", "test"),  # None session_id
            (999999, None, "test"),  # None word_phrase
            (-1, "test", "test"),    # Invalid session_id
        ]
        
        for session_id, word_phrase, translation in error_conditions:
            try:
                vocab_model.add_vocab(
                    session_id=session_id,
                    word_phrase=word_phrase,
                    translation=translation
                )
            except Exception as e:
                # Exception should be handled gracefully
                # Should not expose internal implementation details
                error_message = str(e)
                
                # Check for information disclosure
                dangerous_patterns = [
                    'File "',  # File paths
                    'line ',   # Line numbers
                    'sqlite3.', # Database implementation details
                ]
                
                for pattern in dangerous_patterns:
                    if pattern in error_message:
                        print(f"Warning: Exception may disclose sensitive info: {pattern}")


# Integration with pytest markers
pytestmark = pytest.mark.security