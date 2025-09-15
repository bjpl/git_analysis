#!/usr/bin/env python3
"""
Unit Tests for Notes CRUD Operations
Testing all Create, Read, Update, Delete operations for the notes system
"""

import pytest
import sqlite3
import json
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the classes under test
sys_path = Path(__file__).parent.parent.parent / "src"
import sys
sys.path.insert(0, str(sys_path))

from notes_manager import NotesManager
from ui.notes import NotesManager as UINotesManager, RichNote, NoteType, Priority
from ui.formatter import TerminalFormatter


class TestNotesManagerCRUD:
    """Test suite for NotesManager CRUD operations"""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        os.unlink(path)
    
    @pytest.fixture
    def notes_manager(self, temp_db):
        """Create a NotesManager instance for testing"""
        return NotesManager(temp_db)
    
    @pytest.fixture
    def sample_user_id(self):
        """Sample user ID for testing"""
        return 1
    
    @pytest.fixture
    def sample_lesson_id(self):
        """Sample lesson ID for testing"""
        return 101
    
    def test_init_database(self, notes_manager):
        """Test database initialization creates required tables"""
        with sqlite3.connect(notes_manager.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if notes table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='notes'
            """)
            assert cursor.fetchone() is not None
            
            # Check table structure
            cursor.execute("PRAGMA table_info(notes)")
            columns = {col[1] for col in cursor.fetchall()}
            expected_columns = {
                'id', 'user_id', 'lesson_id', 'module_name', 
                'topic', 'content', 'tags', 'created_at', 
                'updated_at', 'is_favorite'
            }
            assert columns.issuperset(expected_columns)
    
    def test_save_note_success(self, notes_manager, sample_user_id, sample_lesson_id):
        """Test successful note creation"""
        content = "This is a test note about algorithms"
        module_name = "Algorithms"
        topic = "Big O Notation"
        tags = ["performance", "complexity"]
        
        note_id = notes_manager.save_note(
            sample_user_id, sample_lesson_id, content, 
            module_name, topic, tags
        )
        
        assert note_id is not None
        assert isinstance(note_id, int)
        assert note_id > 0
    
    def test_save_note_without_lesson(self, notes_manager, sample_user_id):
        """Test saving note without associated lesson"""
        content = "General note without lesson"
        module_name = "General"
        topic = "Random thoughts"
        
        note_id = notes_manager.save_note(
            sample_user_id, None, content, module_name, topic
        )
        
        assert note_id is not None
        assert note_id > 0
    
    def test_save_note_empty_content_fails(self, notes_manager, sample_user_id):
        """Test that empty content should fail or be handled gracefully"""
        with pytest.raises((ValueError, sqlite3.IntegrityError)):
            notes_manager.save_note(sample_user_id, None, "", "Module", "Topic")
    
    def test_get_notes_by_user(self, notes_manager, sample_user_id, sample_lesson_id):
        """Test retrieving notes by user ID"""
        # Create test notes
        note1_id = notes_manager.save_note(
            sample_user_id, sample_lesson_id, "First note", 
            "Module1", "Topic1", ["tag1"]
        )
        note2_id = notes_manager.save_note(
            sample_user_id, sample_lesson_id + 1, "Second note", 
            "Module2", "Topic2", ["tag2"]
        )
        
        # Retrieve notes
        notes = notes_manager.get_notes(sample_user_id)
        
        assert len(notes) == 2
        assert all(note['user_id'] == sample_user_id for note in notes)
        assert any(note['content'] == "First note" for note in notes)
        assert any(note['content'] == "Second note" for note in notes)
    
    def test_get_notes_by_lesson(self, notes_manager, sample_user_id, sample_lesson_id):
        """Test retrieving notes by lesson ID"""
        # Create notes for different lessons
        notes_manager.save_note(sample_user_id, sample_lesson_id, 
                              "Lesson 101 note", "Module", "Topic")
        notes_manager.save_note(sample_user_id, sample_lesson_id + 1, 
                              "Lesson 102 note", "Module", "Topic")
        
        # Get notes for specific lesson
        lesson_notes = notes_manager.get_notes(sample_user_id, lesson_id=sample_lesson_id)
        
        assert len(lesson_notes) == 1
        assert lesson_notes[0]['lesson_id'] == sample_lesson_id
        assert lesson_notes[0]['content'] == "Lesson 101 note"
    
    def test_get_notes_by_module(self, notes_manager, sample_user_id):
        """Test retrieving notes by module name"""
        # Create notes in different modules
        notes_manager.save_note(sample_user_id, None, "Arrays note", 
                              "Arrays", "Basic operations")
        notes_manager.save_note(sample_user_id, None, "Trees note", 
                              "Trees", "Binary trees")
        
        # Get notes for Arrays module
        arrays_notes = notes_manager.get_notes(sample_user_id, module_name="Arrays")
        
        assert len(arrays_notes) == 1
        assert arrays_notes[0]['module_name'] == "Arrays"
        assert arrays_notes[0]['content'] == "Arrays note"
    
    def test_search_notes_content(self, notes_manager, sample_user_id):
        """Test searching notes by content"""
        notes_manager.save_note(sample_user_id, None, 
                              "Quick sort algorithm implementation", 
                              "Sorting", "Quick Sort")
        notes_manager.save_note(sample_user_id, None, 
                              "Merge sort is stable", 
                              "Sorting", "Merge Sort")
        
        # Search for 'sort'
        search_results = notes_manager.get_notes(sample_user_id, search_term="sort")
        
        assert len(search_results) == 2
        assert all("sort" in note['content'].lower() for note in search_results)
    
    def test_search_notes_tags(self, notes_manager, sample_user_id):
        """Test searching notes by tags"""
        notes_manager.save_note(sample_user_id, None, "Algorithm note", 
                              "Algorithms", "Topic", ["performance", "O(n)"])
        notes_manager.save_note(sample_user_id, None, "Data structure note", 
                              "DataStructures", "Topic", ["memory", "efficiency"])
        
        # Search by tag
        performance_notes = notes_manager.get_notes(sample_user_id, search_term="performance")
        
        assert len(performance_notes) == 1
        assert "performance" in performance_notes[0]['tags']
    
    def test_update_note_success(self, notes_manager, sample_user_id):
        """Test successful note update"""
        # Create note
        note_id = notes_manager.save_note(sample_user_id, None, 
                                        "Original content", "Module", "Topic")
        
        # Update note
        updated_content = "Updated content with more details"
        new_tags = ["updated", "detailed"]
        success = notes_manager.update_note(note_id, updated_content, new_tags)
        
        assert success is True
        
        # Verify update
        notes = notes_manager.get_notes(sample_user_id)
        updated_note = next(note for note in notes if note['id'] == note_id)
        assert updated_note['content'] == updated_content
        assert set(updated_note['tags']) == set(new_tags)
    
    def test_update_nonexistent_note(self, notes_manager):
        """Test updating non-existent note returns False"""
        success = notes_manager.update_note(99999, "New content")
        assert success is False
    
    def test_delete_note_success(self, notes_manager, sample_user_id):
        """Test successful note deletion"""
        # Create note
        note_id = notes_manager.save_note(sample_user_id, None, 
                                        "Note to delete", "Module", "Topic")
        
        # Verify note exists
        notes_before = notes_manager.get_notes(sample_user_id)
        assert len(notes_before) == 1
        
        # Delete note
        success = notes_manager.delete_note(note_id)
        assert success is True
        
        # Verify note is gone
        notes_after = notes_manager.get_notes(sample_user_id)
        assert len(notes_after) == 0
    
    def test_delete_nonexistent_note(self, notes_manager):
        """Test deleting non-existent note returns False"""
        success = notes_manager.delete_note(99999)
        assert success is False
    
    def test_toggle_favorite_success(self, notes_manager, sample_user_id):
        """Test toggling favorite status"""
        # Create note
        note_id = notes_manager.save_note(sample_user_id, None, 
                                        "Favorite note", "Module", "Topic")
        
        # Initially not favorite
        notes = notes_manager.get_notes(sample_user_id)
        assert notes[0]['is_favorite'] == 0
        
        # Toggle to favorite
        success = notes_manager.toggle_favorite(note_id)
        assert success is True
        
        # Verify favorite status
        notes = notes_manager.get_notes(sample_user_id)
        assert notes[0]['is_favorite'] == 1
        
        # Toggle back
        notes_manager.toggle_favorite(note_id)
        notes = notes_manager.get_notes(sample_user_id)
        assert notes[0]['is_favorite'] == 0
    
    def test_notes_ordering(self, notes_manager, sample_user_id):
        """Test that notes are ordered by creation time (newest first)"""
        import time
        
        # Create notes with small delay to ensure different timestamps
        first_id = notes_manager.save_note(sample_user_id, None, "First note", "M", "T")
        time.sleep(0.1)
        second_id = notes_manager.save_note(sample_user_id, None, "Second note", "M", "T")
        time.sleep(0.1)
        third_id = notes_manager.save_note(sample_user_id, None, "Third note", "M", "T")
        
        notes = notes_manager.get_notes(sample_user_id)
        
        # Should be in reverse chronological order (newest first)
        assert notes[0]['content'] == "Third note"
        assert notes[1]['content'] == "Second note" 
        assert notes[2]['content'] == "First note"
    
    def test_tags_json_serialization(self, notes_manager, sample_user_id):
        """Test that tags are properly serialized/deserialized"""
        tags = ["algorithm", "performance", "O(log n)", "binary-search"]
        
        note_id = notes_manager.save_note(sample_user_id, None, 
                                        "Binary search note", "Algorithms", 
                                        "Binary Search", tags)
        
        notes = notes_manager.get_notes(sample_user_id)
        retrieved_note = notes[0]
        
        assert isinstance(retrieved_note['tags'], list)
        assert set(retrieved_note['tags']) == set(tags)
    
    def test_empty_tags_handling(self, notes_manager, sample_user_id):
        """Test handling of empty or None tags"""
        # Test with None tags
        note1_id = notes_manager.save_note(sample_user_id, None, 
                                         "Note with no tags", "Module", "Topic", None)
        
        # Test with empty list
        note2_id = notes_manager.save_note(sample_user_id, None, 
                                         "Note with empty tags", "Module", "Topic", [])
        
        notes = notes_manager.get_notes(sample_user_id)
        
        for note in notes:
            assert isinstance(note['tags'], list)
            assert len(note['tags']) == 0


class TestNotesValidation:
    """Test data validation and edge cases"""
    
    @pytest.fixture
    def temp_db(self):
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        os.unlink(path)
    
    @pytest.fixture
    def notes_manager(self, temp_db):
        return NotesManager(temp_db)
    
    def test_long_content_handling(self, notes_manager):
        """Test handling of very long note content"""
        long_content = "A" * 10000  # 10KB content
        
        note_id = notes_manager.save_note(1, None, long_content, "Module", "Topic")
        assert note_id is not None
        
        notes = notes_manager.get_notes(1)
        assert len(notes[0]['content']) == 10000
    
    def test_special_characters_content(self, notes_manager):
        """Test handling of special characters and unicode"""
        special_content = "Test with émojis 🚀 and special chars: @#$%^&*(){}[]|\\:;\"'<>,.?/~`"
        
        note_id = notes_manager.save_note(1, None, special_content, "Module", "Topic")
        
        notes = notes_manager.get_notes(1)
        assert notes[0]['content'] == special_content
    
    def test_sql_injection_protection(self, notes_manager):
        """Test protection against SQL injection attacks"""
        malicious_content = "'; DROP TABLE notes; --"
        
        # Should not cause database corruption
        note_id = notes_manager.save_note(1, None, malicious_content, "Module", "Topic")
        assert note_id is not None
        
        # Table should still exist and function
        notes = notes_manager.get_notes(1)
        assert len(notes) == 1
        assert notes[0]['content'] == malicious_content
    
    def test_invalid_user_id_handling(self, notes_manager):
        """Test handling of invalid user IDs"""
        # Negative user ID
        with pytest.raises((ValueError, sqlite3.IntegrityError)):
            notes_manager.save_note(-1, None, "Content", "Module", "Topic")
        
        # Zero user ID 
        with pytest.raises((ValueError, sqlite3.IntegrityError)):
            notes_manager.save_note(0, None, "Content", "Module", "Topic")
    
    def test_null_content_handling(self, notes_manager):
        """Test handling of null/None content"""
        with pytest.raises((ValueError, sqlite3.IntegrityError)):
            notes_manager.save_note(1, None, None, "Module", "Topic")
    
    def test_whitespace_only_content(self, notes_manager):
        """Test handling of whitespace-only content"""
        whitespace_content = "   \t\n   "
        
        # Should either reject or trim whitespace
        try:
            note_id = notes_manager.save_note(1, None, whitespace_content, "Module", "Topic")
            notes = notes_manager.get_notes(1)
            # If accepted, should be trimmed or preserved as-is
            assert notes[0]['content'] in [whitespace_content, whitespace_content.strip()]
        except (ValueError, sqlite3.IntegrityError):
            # Rejection is also acceptable behavior
            pass


class TestNotesStatistics:
    """Test notes statistics functionality"""
    
    @pytest.fixture
    def temp_db(self):
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        os.unlink(path)
    
    @pytest.fixture
    def notes_manager(self, temp_db):
        return NotesManager(temp_db)
    
    @pytest.fixture
    def setup_sample_notes(self, notes_manager):
        """Create sample notes for statistics testing"""
        user_id = 1
        
        # Create notes in different modules with different tags
        notes_manager.save_note(user_id, 1, "Arrays basics", "Arrays", 
                              "Introduction", ["basic", "data-structure"])
        notes_manager.save_note(user_id, 2, "Sorting algorithms", "Sorting", 
                              "Quick Sort", ["algorithm", "performance"])
        notes_manager.save_note(user_id, 3, "Binary trees", "Trees", 
                              "BST", ["tree", "recursive"])
        notes_manager.save_note(user_id, None, "General note", "General", 
                              "Misc", ["general"])
        
        # Mark one as favorite
        notes = notes_manager.get_notes(user_id)
        notes_manager.toggle_favorite(notes[0]['id'])
        
        return user_id
    
    def test_get_statistics_structure(self, notes_manager, setup_sample_notes):
        """Test that statistics return proper structure"""
        user_id = setup_sample_notes
        stats = notes_manager.get_statistics(user_id)
        
        # Check required keys
        required_keys = ['total_notes', 'by_module', 'recent_notes', 'favorites']
        for key in required_keys:
            assert key in stats
    
    def test_total_notes_count(self, notes_manager, setup_sample_notes):
        """Test total notes count in statistics"""
        user_id = setup_sample_notes
        stats = notes_manager.get_statistics(user_id)
        
        assert stats['total_notes'] == 4
    
    def test_notes_by_module_grouping(self, notes_manager, setup_sample_notes):
        """Test notes grouping by module"""
        user_id = setup_sample_notes
        stats = notes_manager.get_statistics(user_id)
        
        expected_modules = {'Arrays': 1, 'Sorting': 1, 'Trees': 1, 'General': 1}
        assert stats['by_module'] == expected_modules
    
    def test_favorites_count(self, notes_manager, setup_sample_notes):
        """Test favorites count in statistics"""
        user_id = setup_sample_notes
        stats = notes_manager.get_statistics(user_id)
        
        assert stats['favorites'] == 1
    
    def test_recent_notes_count(self, notes_manager, setup_sample_notes):
        """Test recent notes count (within 7 days)"""
        user_id = setup_sample_notes
        stats = notes_manager.get_statistics(user_id)
        
        # All test notes should be recent (just created)
        assert stats['recent_notes'] == 4
    
    def test_empty_statistics(self, notes_manager):
        """Test statistics for user with no notes"""
        stats = notes_manager.get_statistics(999)  # Non-existent user
        
        assert stats['total_notes'] == 0
        assert stats['by_module'] == {}
        assert stats['recent_notes'] == 0
        assert stats['favorites'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
