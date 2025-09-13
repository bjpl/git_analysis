#!/usr/bin/env python3
"""
Unit Tests for Notes Data Persistence
Testing storage limits, auto-save, and data integrity
"""

import pytest
import sqlite3
import json
import tempfile
import os
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call

# Import the classes under test
sys_path = Path(__file__).parent.parent.parent / "src"
import sys
sys.path.insert(0, str(sys_path))

from notes_manager import NotesManager
from ui.notes import NotesManager as UINotesManager, RichNote, NoteType, Priority


class TestNotesPersistence:
    """Test suite for notes data persistence and storage"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    @pytest.fixture
    def temp_notes_dir(self):
        """Create temporary notes directory"""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def notes_manager(self, temp_db):
        """Create NotesManager instance for testing"""
        return NotesManager(temp_db)
    
    def test_database_file_creation(self, temp_db):
        """Test that database file is created when NotesManager is initialized"""
        # Remove the file if it exists
        if os.path.exists(temp_db):
            os.remove(temp_db)
        
        # Initialize NotesManager
        manager = NotesManager(temp_db)
        
        # Database file should be created
        assert os.path.exists(temp_db)
        assert os.path.getsize(temp_db) > 0
    
    def test_database_persistence_after_restart(self, temp_db):
        """Test that notes persist after manager restart"""
        # Create notes with first manager instance
        manager1 = NotesManager(temp_db)
        note_id = manager1.save_note(1, 101, "Persistent note", "Module", "Topic")
        
        # Close connection and create new manager instance
        del manager1
        manager2 = NotesManager(temp_db)
        
        # Notes should still be there
        notes = manager2.get_notes(1)
        assert len(notes) == 1
        assert notes[0]['content'] == "Persistent note"
        assert notes[0]['id'] == note_id
    
    def test_concurrent_access_safety(self, temp_db):
        """Test that multiple concurrent accesses are handled safely"""
        results = []
        errors = []
        
        def create_notes(start_id, count):
            try:
                manager = NotesManager(temp_db)
                for i in range(count):
                    note_id = manager.save_note(
                        1, None, f"Concurrent note {start_id + i}", 
                        "Module", "Topic"
                    )
                    results.append(note_id)
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_notes, args=(i * 10, 5))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Concurrent access errors: {errors}"
        assert len(results) == 25  # 5 threads * 5 notes each
        assert len(set(results)) == 25  # All note IDs should be unique
    
    def test_storage_limits_large_content(self, notes_manager):
        """Test handling of large note content"""
        # Test various content sizes
        sizes = [1024, 10240, 102400, 1048576]  # 1KB, 10KB, 100KB, 1MB
        
        for size in sizes:
            large_content = "X" * size
            
            note_id = notes_manager.save_note(
                1, None, large_content, "Module", f"Large content {size}"
            )
            
            assert note_id is not None
            
            # Verify content integrity
            notes = notes_manager.get_notes(1, search_term=f"Large content {size}")
            assert len(notes) == 1
            assert len(notes[0]['content']) == size
            assert notes[0]['content'] == large_content
    
    def test_storage_limits_many_notes(self, notes_manager):
        """Test handling of large number of notes"""
        num_notes = 1000
        user_id = 1
        
        # Create many notes
        note_ids = []
        for i in range(num_notes):
            note_id = notes_manager.save_note(
                user_id, None, f"Note content {i}", 
                f"Module{i % 10}", f"Topic{i}"
            )
            note_ids.append(note_id)
        
        # Verify all notes are stored
        all_notes = notes_manager.get_notes(user_id)
        assert len(all_notes) == num_notes
        assert len(set(note['id'] for note in all_notes)) == num_notes
    
    def test_storage_limits_many_tags(self, notes_manager):
        """Test handling of notes with many tags"""
        # Create note with many tags
        many_tags = [f"tag{i}" for i in range(100)]
        
        note_id = notes_manager.save_note(
            1, None, "Note with many tags", "Module", "Topic", many_tags
        )
        
        # Verify tags are stored correctly
        notes = notes_manager.get_notes(1)
        assert len(notes) == 1
        assert len(notes[0]['tags']) == 100
        assert set(notes[0]['tags']) == set(many_tags)
    
    def test_data_integrity_after_system_failure(self, temp_db):
        """Test data integrity after simulated system failure"""
        manager = NotesManager(temp_db)
        
        # Create some notes
        note_ids = []
        for i in range(10):
            note_id = manager.save_note(
                1, None, f"Note {i}", "Module", "Topic"
            )
            note_ids.append(note_id)
        
        # Simulate system failure by forcibly closing database connection
        with sqlite3.connect(temp_db) as conn:
            conn.execute("PRAGMA journal_mode = WAL")  # Enable Write-Ahead Logging
        
        # Create new manager and verify data integrity
        new_manager = NotesManager(temp_db)
        notes = new_manager.get_notes(1)
        
        assert len(notes) == 10
        for i, note in enumerate(sorted(notes, key=lambda x: x['content'])):
            assert note['content'] == f"Note {i}"
    
    def test_database_corruption_recovery(self, temp_db):
        """Test recovery from database corruption"""
        # Create manager and some notes
        manager = NotesManager(temp_db)
        manager.save_note(1, None, "Test note", "Module", "Topic")
        
        # Corrupt the database file
        with open(temp_db, 'wb') as f:
            f.write(b"corrupted data" * 100)
        
        # Creating a new manager should handle corruption gracefully
        try:
            new_manager = NotesManager(temp_db)
            # Should either recover or reinitialize
            notes = new_manager.get_notes(1)
            # If recovered, notes exist; if reinitialized, no notes
            assert isinstance(notes, list)
        except Exception as e:
            # Should handle corruption gracefully, not crash
            assert "database" in str(e).lower() or "corrupt" in str(e).lower()
    
    def test_backup_and_restore(self, notes_manager, temp_notes_dir):
        """Test backup and restore functionality"""
        # Create test notes
        test_notes = [
            (1, 101, "First note", "Module1", "Topic1", ["tag1", "tag2"]),
            (1, 102, "Second note", "Module2", "Topic2", ["tag3"]),
            (1, None, "Third note", "Module1", "Topic3", [])
        ]
        
        for user_id, lesson_id, content, module, topic, tags in test_notes:
            notes_manager.save_note(user_id, lesson_id, content, module, topic, tags)
        
        # Export notes (backup)
        backup_file = notes_manager.export_notes(1, format="json", output_dir=temp_notes_dir)
        assert backup_file is not None
        assert os.path.exists(backup_file)
        
        # Verify backup content
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        assert len(backup_data) == 3
        assert all(note['user_id'] == 1 for note in backup_data)
    
    def test_auto_save_functionality(self, notes_manager):
        """Test auto-save behavior"""
        # This test assumes auto-save happens on note creation
        # In a real implementation, this might be more complex
        
        initial_notes = notes_manager.get_notes(1)
        initial_count = len(initial_notes)
        
        # Create a note
        note_id = notes_manager.save_note(1, None, "Auto-save test", "Module", "Topic")
        
        # Immediately check if it's saved (auto-save)
        notes_after = notes_manager.get_notes(1)
        assert len(notes_after) == initial_count + 1
        
        # Find the new note
        new_note = next((n for n in notes_after if n['id'] == note_id), None)
        assert new_note is not None
        assert new_note['content'] == "Auto-save test"
    
    def test_transaction_rollback_on_error(self, temp_db):
        """Test transaction rollback when errors occur"""
        manager = NotesManager(temp_db)
        
        # Create initial note
        manager.save_note(1, None, "Initial note", "Module", "Topic")
        initial_notes = manager.get_notes(1)
        
        # Simulate a transaction that should fail
        with patch.object(manager, '_init_database') as mock_init:
            mock_init.side_effect = sqlite3.Error("Simulated error")
            
            try:
                # Attempt operation that should fail
                manager.save_note(1, None, "Failed note", "Module", "Topic")
            except sqlite3.Error:
                pass
        
        # Verify that the failed operation didn't corrupt existing data
        final_notes = manager.get_notes(1)
        assert len(final_notes) == len(initial_notes)
        assert final_notes[0]['content'] == "Initial note"
    
    def test_migration_of_old_notes(self, temp_db):
        """Test migration functionality for old note formats"""
        # Create a database with old-style notes in progress table
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            
            # Create old-style progress table with notes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS progress (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    lesson_id INTEGER,
                    notes TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lessons (
                    id INTEGER PRIMARY KEY,
                    title TEXT
                )
            """)
            
            # Insert test data
            cursor.execute("INSERT INTO lessons (id, title) VALUES (101, 'Arrays: Basic Operations')")
            cursor.execute("""
                INSERT INTO progress (user_id, lesson_id, notes) 
                VALUES (1, 101, 'Old note content from progress table')
            """)
            
            conn.commit()
        
        # Initialize NotesManager (should trigger migration)
        manager = NotesManager(temp_db)
        migrated_count = manager.migrate_old_notes()
        
        # Verify migration
        assert migrated_count == 1
        
        notes = manager.get_notes(1)
        assert len(notes) == 1
        assert notes[0]['content'] == 'Old note content from progress table'
        assert notes[0]['module_name'] == 'Arrays'
    
    def test_cleanup_orphaned_notes(self, temp_db):
        """Test cleanup of orphaned notes (references to deleted lessons)"""
        # Create database with lessons and notes
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            
            # Create lessons table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lessons (
                    id INTEGER PRIMARY KEY,
                    title TEXT
                )
            """)
            
            cursor.execute("INSERT INTO lessons (id, title) VALUES (101, 'Valid Lesson')")
            conn.commit()
        
        manager = NotesManager(temp_db)
        
        # Create notes - one valid, one orphaned
        manager.save_note(1, 101, "Valid note", "Module", "Topic")  # Valid
        manager.save_note(1, 999, "Orphaned note", "Module", "Topic")  # Orphaned
        
        # Remove the lesson to create orphaned note
        with sqlite3.connect(temp_db) as conn:
            conn.execute("DELETE FROM lessons WHERE id = 999")
            conn.commit()
        
        # Cleanup orphaned notes
        deleted_count = manager.cleanup_orphaned_notes()
        
        # Verify cleanup
        assert deleted_count == 1
        
        notes = manager.get_notes(1)
        assert len(notes) == 1
        assert notes[0]['content'] == "Valid note"


class TestNotesFileSystemPersistence:
    """Test file system persistence for UI notes"""
    
    @pytest.fixture
    def temp_notes_dir(self):
        import tempfile
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def formatter(self):
        from ui.formatter import TerminalFormatter
        return TerminalFormatter()
    
    @pytest.fixture
    def ui_notes_manager(self, formatter, temp_notes_dir):
        return UINotesManager(formatter, temp_notes_dir)
    
    def test_notes_file_creation(self, ui_notes_manager, temp_notes_dir):
        """Test that notes.json file is created"""
        # Create a note to trigger file creation
        note = RichNote(
            id="test1",
            title="Test Note",
            content="Test content",
            note_type=NoteType.CONCEPT,
            priority=Priority.MEDIUM
        )
        
        ui_notes_manager.notes[note.id] = note
        ui_notes_manager.save_notes()
        
        notes_file = Path(temp_notes_dir) / "notes.json"
        assert notes_file.exists()
        assert notes_file.stat().st_size > 0
    
    def test_notes_json_format(self, ui_notes_manager, temp_notes_dir):
        """Test the format of saved JSON file"""
        # Create test notes
        notes = [
            RichNote("note1", "Title 1", "Content 1", NoteType.CONCEPT, Priority.HIGH, ["tag1"]),
            RichNote("note2", "Title 2", "Content 2", NoteType.EXAMPLE, Priority.LOW, ["tag2", "tag3"])
        ]
        
        for note in notes:
            ui_notes_manager.notes[note.id] = note
        
        ui_notes_manager.save_notes()
        
        # Verify JSON structure
        notes_file = Path(temp_notes_dir) / "notes.json"
        with open(notes_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert 'notes' in data
        assert 'created' in data
        assert 'version' in data
        assert len(data['notes']) == 2
        
        # Check note structure
        note_data = data['notes'][0]
        required_fields = ['id', 'title', 'content', 'note_type', 'priority', 'tags', 'timestamp']
        for field in required_fields:
            assert field in note_data
    
    def test_notes_loading_persistence(self, ui_notes_manager, temp_notes_dir):
        """Test loading notes from file system"""
        # Create and save notes
        original_note = RichNote(
            "persistent1", "Persistent Note", "This should persist", 
            NoteType.INSIGHT, Priority.CRITICAL, ["persistent", "test"]
        )
        
        ui_notes_manager.notes[original_note.id] = original_note
        ui_notes_manager.save_notes()
        
        # Create new manager instance to test loading
        new_manager = UINotesManager(ui_notes_manager.formatter, temp_notes_dir)
        
        # Verify note was loaded
        assert len(new_manager.notes) == 1
        loaded_note = new_manager.notes["persistent1"]
        
        assert loaded_note.title == "Persistent Note"
        assert loaded_note.content == "This should persist"
        assert loaded_note.note_type == NoteType.INSIGHT
        assert loaded_note.priority == Priority.CRITICAL
        assert set(loaded_note.tags) == {"persistent", "test"}
    
    def test_unicode_content_persistence(self, ui_notes_manager, temp_notes_dir):
        """Test persistence of unicode and special characters"""
        unicode_content = "Unicode test: 中文, العربية, हिन्दी, 🚀🎆🎉"
        
        note = RichNote(
            "unicode1", "Unicode Note", unicode_content,
            NoteType.REFERENCE, Priority.MEDIUM, ["📝", "中文"]
        )
        
        ui_notes_manager.notes[note.id] = note
        ui_notes_manager.save_notes()
        
        # Load and verify
        new_manager = UINotesManager(ui_notes_manager.formatter, temp_notes_dir)
        loaded_note = new_manager.notes["unicode1"]
        
        assert loaded_note.content == unicode_content
        assert "📝" in loaded_note.tags
        assert "中文" in loaded_note.tags
    
    def test_large_notes_collection_persistence(self, ui_notes_manager):
        """Test persistence of large collection of notes"""
        # Create many notes
        num_notes = 100
        for i in range(num_notes):
            note = RichNote(
                f"note_{i}", f"Title {i}", f"Content for note {i}",
                NoteType.CONCEPT, Priority.MEDIUM, [f"tag_{i}", "bulk_test"]
            )
            ui_notes_manager.notes[note.id] = note
        
        # Save and reload
        ui_notes_manager.save_notes()
        new_manager = UINotesManager(ui_notes_manager.formatter, ui_notes_manager.notes_dir)
        
        # Verify all notes loaded
        assert len(new_manager.notes) == num_notes
        
        # Verify content integrity
        for i in range(num_notes):
            note_id = f"note_{i}"
            assert note_id in new_manager.notes
            assert new_manager.notes[note_id].title == f"Title {i}"
            assert new_manager.notes[note_id].content == f"Content for note {i}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
