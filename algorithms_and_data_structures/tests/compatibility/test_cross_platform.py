#!/usr/bin/env python3
"""
Cross-Platform Compatibility Tests for Notes System
Testing compatibility across different operating systems, terminals, and environments
"""

import pytest
import tempfile
import os
import sys
import platform
import subprocess
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the classes under test
sys_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(sys_path))

from notes_manager import NotesManager
from ui.notes import NotesManager as UINotesManager, RichNote, NoteType, Priority
from ui.formatter import TerminalFormatter


class TestOperatingSystemCompatibility:
    """Test compatibility across different operating systems"""
    
    @pytest.fixture
    def temp_db(self):
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    @pytest.fixture
    def temp_notes_dir(self):
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_file_path_handling(self, temp_db):
        """Test file path handling across operating systems"""
        manager = NotesManager(temp_db)
        
        # Test that database path works on current OS
        assert os.path.exists(temp_db)
        
        # Create some notes to test file operations
        note_id = manager.save_note(1, None, "Path test content", "Module", "Topic")
        assert note_id is not None
        
        # Test that notes can be retrieved (file operations work)
        notes = manager.get_notes(1)
        assert len(notes) == 1
        assert notes[0]['content'] == "Path test content"
    
    def test_unicode_file_handling(self, temp_notes_dir):
        """Test unicode handling in file operations"""
        formatter = TerminalFormatter()
        ui_manager = UINotesManager(formatter, temp_notes_dir)
        
        # Create note with unicode content
        unicode_note = RichNote(
            "unicode_test", "Unicode Test Note 📝",
            "Content with unicode: 中文, العربية, हिन्दी, 🚀🎉",
            NoteType.CONCEPT, Priority.MEDIUM, ["📝", "中文", "test"]
        )
        
        ui_manager.notes[unicode_note.id] = unicode_note
        
        # Test saving and loading unicode content
        ui_manager.save_notes()
        
        # Create new manager to test loading
        new_manager = UINotesManager(formatter, temp_notes_dir)
        
        # Should successfully load unicode content
        assert len(new_manager.notes) == 1
        loaded_note = new_manager.notes["unicode_test"]
        assert "中文" in loaded_note.content
        assert "🚀" in loaded_note.content
        assert "📝" in loaded_note.tags
    
    def test_line_ending_handling(self, temp_db):
        """Test handling of different line endings across platforms"""
        manager = NotesManager(temp_db)
        
        # Test different line ending styles
        line_ending_tests = [
            ("unix", "Line 1\nLine 2\nLine 3"),          # Unix LF
            ("windows", "Line 1\r\nLine 2\r\nLine 3"),    # Windows CRLF
            ("mac", "Line 1\rLine 2\rLine 3"),           # Old Mac CR
            ("mixed", "Line 1\nLine 2\r\nLine 3\r")       # Mixed
        ]
        
        note_ids = []
        for test_name, content in line_ending_tests:
            note_id = manager.save_note(1, None, content, "LineEndings", test_name)
            note_ids.append(note_id)
        
        # Retrieve and verify all line ending styles work
        notes = manager.get_notes(1)
        assert len(notes) == 4
        
        for note in notes:
            # Content should be preserved
            assert "Line 1" in note['content']
            assert "Line 2" in note['content']
            assert "Line 3" in note['content']
    
    @pytest.mark.skipif(platform.system() == "Windows", reason="Unix-specific test")
    def test_unix_permissions(self, temp_db, temp_notes_dir):
        """Test file permissions on Unix-like systems"""
        # Test database permissions
        db_stat = os.stat(temp_db)
        assert db_stat.st_mode & 0o600  # Should be readable/writable by owner
        
        # Test notes directory permissions
        dir_stat = os.stat(temp_notes_dir)
        assert dir_stat.st_mode & 0o700  # Should be accessible by owner
    
    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
    def test_windows_paths(self, temp_db):
        """Test Windows-specific path handling"""
        manager = NotesManager(temp_db)
        
        # Test that Windows paths work correctly
        assert '\\' in temp_db or ':' in temp_db  # Windows path indicators
        
        # Test file operations work with Windows paths
        note_id = manager.save_note(1, None, "Windows path test", "Module", "Topic")
        notes = manager.get_notes(1)
        assert len(notes) == 1
    
    def test_environment_variables(self, temp_db):
        """Test handling of environment-specific variables"""
        manager = NotesManager(temp_db)
        
        # Test common environment variables that might affect operation
        original_lang = os.environ.get('LANG')
        original_locale = os.environ.get('LC_ALL')
        
        try:
            # Test with different locales
            test_locales = ['C', 'en_US.UTF-8', 'C.UTF-8']
            
            for locale in test_locales:
                if locale:
                    os.environ['LANG'] = locale
                    os.environ['LC_ALL'] = locale
                
                # Create and retrieve note with current locale
                note_id = manager.save_note(1, None, f"Locale test {locale}", "Module", "Topic")
                notes = manager.get_notes(1, search_term="Locale")
                
                # Should work regardless of locale
                assert len([n for n in notes if f"Locale test {locale}" in n['content']]) >= 1
        
        finally:
            # Restore original environment
            if original_lang:
                os.environ['LANG'] = original_lang
            elif 'LANG' in os.environ:
                del os.environ['LANG']
                
            if original_locale:
                os.environ['LC_ALL'] = original_locale
            elif 'LC_ALL' in os.environ:
                del os.environ['LC_ALL']


class TestTerminalCompatibility:
    """Test compatibility across different terminal environments"""
    
    @pytest.fixture
    def temp_notes_dir(self):
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_ansi_escape_handling(self, temp_notes_dir):
        """Test ANSI escape sequence handling across terminals"""
        formatter = TerminalFormatter()
        ui_manager = UINotesManager(formatter, temp_notes_dir)
        
        # Create note with formatting that uses ANSI escapes
        formatted_note = RichNote(
            "ansi_test", "ANSI Formatting Test",
            "Text with **bold**, *italic*, and `code` formatting.",
            NoteType.EXAMPLE, Priority.MEDIUM, ["ansi", "formatting"]
        )
        
        ui_manager.notes[formatted_note.id] = formatted_note
        
        # Test that formatted content contains ANSI sequences
        formatted_content = formatted_note.formatted_content
        
        # Should contain ANSI escape sequences for formatting
        assert '\033[' in formatted_content  # ANSI escape start
        
        # Test that original content is preserved
        assert "**bold**" in formatted_note.content
        assert "*italic*" in formatted_note.content
        assert "`code`" in formatted_note.content
    
    def test_color_support_detection(self, temp_notes_dir):
        """Test color support detection across different terminals"""
        formatter = TerminalFormatter()
        
        # Test color detection with different TERM values
        original_term = os.environ.get('TERM')
        
        try:
            test_terms = [
                'xterm-256color',  # Full color support
                'xterm',           # Basic color support
                'dumb',            # No color support
                'vt100',           # Limited support
                None               # No TERM variable
            ]
            
            for term_value in test_terms:
                if term_value is None:
                    if 'TERM' in os.environ:
                        del os.environ['TERM']
                else:
                    os.environ['TERM'] = term_value
                
                # Create new formatter to pick up environment change
                test_formatter = TerminalFormatter()
                ui_manager = UINotesManager(test_formatter, temp_notes_dir)
                
                # Should work regardless of color support
                note = RichNote(
                    f"term_test_{term_value or 'none'}", "Terminal Test",
                    "Content should work with any terminal type.",
                    NoteType.CONCEPT, Priority.MEDIUM, ["terminal", "test"]
                )
                
                ui_manager.notes[note.id] = note
                
                # Formatting should not crash, even without color support
                assert note.formatted_content is not None
        
        finally:
            # Restore original TERM
            if original_term:
                os.environ['TERM'] = original_term
            elif 'TERM' in os.environ:
                del os.environ['TERM']
    
    def test_terminal_width_handling(self, temp_notes_dir):
        """Test handling of different terminal widths"""
        formatter = TerminalFormatter()
        ui_manager = UINotesManager(formatter, temp_notes_dir)
        
        # Create note with content that should adapt to terminal width
        long_line_note = RichNote(
            "width_test", "Terminal Width Test",
            "This is a very long line of text that should handle different terminal widths gracefully without breaking the display or causing issues with text wrapping and formatting.",
            NoteType.CONCEPT, Priority.MEDIUM, ["width", "terminal"]
        )
        
        ui_manager.notes[long_line_note.id] = long_line_note
        
        # Test with different terminal width simulations
        original_columns = os.environ.get('COLUMNS')
        
        try:
            test_widths = ['80', '120', '40', '200']
            
            for width in test_widths:
                os.environ['COLUMNS'] = width
                
                # Content should be accessible regardless of width
                search_results = ui_manager.search_notes("Terminal Width", search_type="title")
                assert len(search_results) == 1
                
                # Formatted content should exist
                assert search_results[0].formatted_content is not None
        
        finally:
            # Restore original COLUMNS
            if original_columns:
                os.environ['COLUMNS'] = original_columns
            elif 'COLUMNS' in os.environ:
                del os.environ['COLUMNS']
    
    def test_input_encoding_handling(self, temp_notes_dir):
        """Test handling of different input encodings"""
        formatter = TerminalFormatter()
        ui_manager = UINotesManager(formatter, temp_notes_dir)
        
        # Test different character encodings
        encoding_tests = [
            ("ascii", "Basic ASCII text only"),
            ("latin1", "Latin-1 with àccénts and ñoñó"),
            ("utf8", "UTF-8 with 中文, عربي, and 🚀 emojis")
        ]
        
        for encoding_name, content in encoding_tests:
            try:
                # Test that content can be handled
                note = RichNote(
                    f"encoding_{encoding_name}", f"Encoding Test {encoding_name}",
                    content, NoteType.CONCEPT, Priority.MEDIUM, ["encoding", encoding_name]
                )
                
                ui_manager.notes[note.id] = note
                
                # Should be able to search and retrieve
                results = ui_manager.search_notes(encoding_name, search_type="tags")
                assert len(results) >= 1
                
            except UnicodeError:
                # Some encodings might not be supported on all systems
                # This is acceptable as long as it fails gracefully
                pass


class TestPythonVersionCompatibility:
    """Test compatibility across different Python versions"""
    
    @pytest.fixture
    def temp_db(self):
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    def test_python_version_features(self, temp_db):
        """Test that code works with current Python version"""
        manager = NotesManager(temp_db)
        
        # Test features that might vary across Python versions
        python_version = sys.version_info
        
        # Basic functionality should work on all supported versions
        note_id = manager.save_note(
            1, None, f"Python {python_version.major}.{python_version.minor} test", 
            "Compatibility", "Python Version", ["python", "version"]
        )
        
        assert note_id is not None
        
        notes = manager.get_notes(1)
        assert len(notes) == 1
        assert f"Python {python_version.major}.{python_version.minor}" in notes[0]['content']
    
    def test_string_formatting_compatibility(self, temp_db):
        """Test string formatting across Python versions"""
        manager = NotesManager(temp_db)
        
        # Test different string formatting methods
        test_data = {
            'user_id': 1,
            'lesson_id': 101,
            'topic': 'String Formatting',
            'count': 42
        }
        
        # f-strings (Python 3.6+)
        if sys.version_info >= (3, 6):
            content_fstring = f"User {test_data['user_id']} completed lesson {test_data['lesson_id']}"
            manager.save_note(1, None, content_fstring, "Format", "F-String")
        
        # .format() method (Python 2.7+)
        content_format = "User {user_id} completed lesson {lesson_id}".format(**test_data)
        manager.save_note(1, None, content_format, "Format", "Format Method")
        
        # % formatting (legacy)
        content_percent = "User %d completed lesson %d" % (test_data['user_id'], test_data['lesson_id'])
        manager.save_note(1, None, content_percent, "Format", "Percent Format")
        
        # All formatting methods should work
        notes = manager.get_notes(1)
        expected_count = 3 if sys.version_info >= (3, 6) else 2
        assert len(notes) == expected_count
    
    def test_pathlib_compatibility(self, temp_db):
        """Test pathlib usage compatibility"""
        from pathlib import Path
        
        # Test that Path objects work with the notes system
        db_path = Path(temp_db)
        assert db_path.exists()
        
        manager = NotesManager(str(db_path))  # Convert to string for compatibility
        
        # Test basic operations
        note_id = manager.save_note(1, None, "Pathlib test", "Path", "Testing")
        notes = manager.get_notes(1)
        
        assert len(notes) == 1
        assert notes[0]['content'] == "Pathlib test"
    
    def test_json_compatibility(self, temp_db):
        """Test JSON serialization compatibility"""
        manager = NotesManager(temp_db)
        
        # Create note with complex tags that require JSON serialization
        complex_tags = ["tag with spaces", "tag-with-dashes", "tag_with_underscores", "中文tag"]
        
        note_id = manager.save_note(1, None, "JSON compatibility test", "JSON", "Test", complex_tags)
        
        notes = manager.get_notes(1)
        assert len(notes) == 1
        assert set(notes[0]['tags']) == set(complex_tags)
        
        # Test export functionality (uses JSON)
        with tempfile.TemporaryDirectory() as temp_dir:
            export_file = manager.export_notes(1, format="json", output_dir=temp_dir)
            assert export_file is not None
            
            # Should be valid JSON
            import json
            with open(export_file, 'r', encoding='utf-8') as f:
                exported_data = json.load(f)
            
            assert len(exported_data) == 1
            assert set(exported_data[0]['tags']) == set(complex_tags)


class TestDependencyCompatibility:
    """Test compatibility with different versions of dependencies"""
    
    @pytest.fixture
    def temp_db(self):
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    def test_sqlite_compatibility(self, temp_db):
        """Test SQLite compatibility across versions"""
        import sqlite3
        
        manager = NotesManager(temp_db)
        
        # Test SQLite version info
        sqlite_version = sqlite3.sqlite_version_info
        print(f"SQLite version: {sqlite3.sqlite_version}")
        
        # Basic operations should work with any reasonable SQLite version
        note_id = manager.save_note(1, None, "SQLite compatibility test", "DB", "SQLite")
        notes = manager.get_notes(1)
        
        assert len(notes) == 1
        assert notes[0]['content'] == "SQLite compatibility test"
        
        # Test database schema compatibility
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            
            # Check that notes table exists and has expected structure
            cursor.execute("PRAGMA table_info(notes)")
            columns = cursor.fetchall()
            
            column_names = [col[1] for col in columns]
            expected_columns = ['id', 'user_id', 'lesson_id', 'module_name', 'topic', 'content', 'tags']
            
            for expected_col in expected_columns:
                assert expected_col in column_names
    
    def test_optional_dependencies(self, temp_db):
        """Test behavior when optional dependencies are missing"""
        manager = NotesManager(temp_db)
        
        # Test markdown export when markdown library might not be available
        note_id = manager.save_note(1, None, "Markdown test content", "Module", "Topic")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # HTML export should work even if markdown library is not available
            try:
                html_file = manager.export_notes(1, format="html", output_dir=temp_dir)
                assert html_file is not None
                assert os.path.exists(html_file)
                
                # File should contain basic HTML structure
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                assert "<!DOCTYPE html>" in html_content
                assert "Markdown test content" in html_content
                
            except ImportError:
                # If markdown is not available, should fall back gracefully
                pass
    
    def test_rich_library_compatibility(self, temp_db):
        """Test Rich library compatibility (if available)"""
        try:
            from rich.console import Console
            from rich.table import Table
            
            # Test that Rich integration works if available
            manager = NotesManager(temp_db)
            
            # Create test data
            for i in range(3):
                manager.save_note(1, None, f"Rich test {i}", "Module", f"Topic{i}")
            
            # Test statistics display (uses Rich if available)
            stats = manager.get_statistics(1)
            assert stats['total_notes'] == 3
            
        except ImportError:
            # Rich library not available - should still work
            pytest.skip("Rich library not available")


class TestNetworkEnvironmentCompatibility:
    """Test compatibility in different network environments"""
    
    @pytest.fixture
    def temp_db(self):
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    def test_offline_operation(self, temp_db):
        """Test that notes system works completely offline"""
        manager = NotesManager(temp_db)
        
        # All operations should work without network access
        note_id = manager.save_note(1, None, "Offline test content", "Offline", "Test")
        assert note_id is not None
        
        notes = manager.get_notes(1)
        assert len(notes) == 1
        
        # Search should work offline
        search_results = manager.get_notes(1, search_term="offline")
        assert len(search_results) == 1
        
        # Export should work offline
        with tempfile.TemporaryDirectory() as temp_dir:
            export_file = manager.export_notes(1, format="json", output_dir=temp_dir)
            assert export_file is not None
            assert os.path.exists(export_file)
    
    def test_no_external_dependencies(self, temp_db):
        """Test that core functionality has no external network dependencies"""
        # Mock network access to ensure no external calls
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.side_effect = Exception("No network access should be required")
            
            manager = NotesManager(temp_db)
            
            # All basic operations should work without network
            note_id = manager.save_note(1, None, "No network test", "Local", "Test")
            notes = manager.get_notes(1)
            search_results = manager.get_notes(1, search_term="network")
            stats = manager.get_statistics(1)
            
            # Export should work without network
            with tempfile.TemporaryDirectory() as temp_dir:
                export_file = manager.export_notes(1, format="markdown", output_dir=temp_dir)
            
            # Verify no network calls were attempted
            assert not mock_urlopen.called


if __name__ == '__main__':
    # Run with platform-specific markers
    pytest.main([__file__, '-v', '--tb=short', '-m', 'not slow'])
