#!/usr/bin/env python3
"""
Regression Tests for Notes System
Ensuring existing functionality continues to work after changes
"""

import pytest
import tempfile
import os
import sqlite3
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the classes under test
sys_path = Path(__file__).parent.parent.parent / "src"
import sys
sys.path.insert(0, str(sys_path))

from notes_manager import NotesManager
from ui.notes import NotesManager as UINotesManager, RichNote, NoteType, Priority
from ui.formatter import TerminalFormatter


class TestLegacyNotesCompatibility:
    """Ensure backward compatibility with existing notes data"""
    
    @pytest.fixture
    def legacy_db(self):
        """Create database with legacy note format"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        # Create legacy database structure
        with sqlite3.connect(path) as conn:
            cursor = conn.cursor()
            
            # Legacy progress table with notes column
            cursor.execute("""
                CREATE TABLE progress (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    lesson_id INTEGER,
                    notes TEXT,
                    completed BOOLEAN DEFAULT 0,
                    score INTEGER DEFAULT 0
                )
            """)
            
            # Legacy lessons table
            cursor.execute("""
                CREATE TABLE lessons (
                    id INTEGER PRIMARY KEY,
                    title TEXT
                )
            """)
            
            # Insert legacy data
            cursor.execute("INSERT INTO lessons (id, title) VALUES (1, 'Arrays: Introduction')")
            cursor.execute("INSERT INTO lessons (id, title) VALUES (2, 'Sorting: Quick Sort')")
            
            cursor.execute("""
                INSERT INTO progress (user_id, lesson_id, notes, completed, score)
                VALUES (1, 1, 'Legacy note about arrays\nMultiple lines\nWith formatting', 1, 95)
            """)
            
            cursor.execute("""
                INSERT INTO progress (user_id, lesson_id, notes, completed, score)
                VALUES (1, 2, 'Legacy sorting notes', 0, 0)
            """)
            
            conn.commit()
        
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    def test_legacy_notes_migration(self, legacy_db):
        """Test that legacy notes are properly migrated"""
        # Initialize notes manager (should trigger migration)
        manager = NotesManager(legacy_db)
        
        # Check migration occurred
        migrated_count = manager.migrate_old_notes()
        assert migrated_count >= 0  # May be 0 if already migrated
        
        # Verify legacy notes are accessible in new format
        notes = manager.get_notes(1)
        legacy_note_contents = [note['content'] for note in notes]
        
        assert any('Legacy note about arrays' in content for content in legacy_note_contents)
        assert any('Legacy sorting notes' in content for content in legacy_note_contents)
    
    def test_legacy_database_structure_compatibility(self, legacy_db):
        """Test that new notes system works with legacy database structure"""
        manager = NotesManager(legacy_db)
        
        # Should be able to create new notes alongside legacy data
        new_note_id = manager.save_note(
            1, None, "New format note", "Modern", "Topic", ["new", "format"]
        )
        
        assert new_note_id is not None
        
        # Should be able to retrieve both legacy and new notes
        all_notes = manager.get_notes(1)
        contents = [note['content'] for note in all_notes]
        
        assert any('Legacy note about arrays' in content for content in contents)
        assert any('New format note' in content for content in contents)
    
    def test_legacy_export_format_support(self, legacy_db):
        """Test that legacy notes can be exported in all formats"""
        manager = NotesManager(legacy_db)
        manager.migrate_old_notes()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Should export legacy notes without errors
            formats = ['json', 'markdown', 'html']
            
            for fmt in formats:
                export_file = manager.export_notes(1, format=fmt, output_dir=temp_dir)
                assert export_file is not None
                assert os.path.exists(export_file)
                
                # Verify content is present
                with open(export_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if fmt == 'json':
                        data = json.loads(content)
                        assert len(data) >= 2  # At least the legacy notes
                    else:
                        assert 'arrays' in content.lower() or 'sorting' in content.lower()


class TestExistingFeatureStability:
    """Ensure existing features continue to work as expected"""
    
    @pytest.fixture
    def stable_db(self):
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    @pytest.fixture
    def populated_manager(self, stable_db):
        """Create manager with stable test data"""
        manager = NotesManager(stable_db)
        
        # Create standard test dataset
        test_data = [
            (1, 101, "Binary search algorithm", "Algorithms", "Binary Search", ["algorithm", "search"]),
            (1, 102, "Linear search basics", "Algorithms", "Linear Search", ["algorithm", "basic"]),
            (1, 201, "Array data structure", "Data Structures", "Arrays", ["array", "structure"]),
            (2, 101, "Different user binary search", "Algorithms", "Binary Search", ["algorithm"])
        ]
        
        for user_id, lesson_id, content, module, topic, tags in test_data:
            manager.save_note(user_id, lesson_id, content, module, topic, tags)
        
        return manager
    
    def test_basic_crud_operations_stability(self, populated_manager):
        """Test that basic CRUD operations remain stable"""
        # CREATE - already done in fixture
        notes = populated_manager.get_notes(1)
        initial_count = len(notes)
        assert initial_count == 3
        
        # CREATE - add new note
        new_note_id = populated_manager.save_note(
            1, None, "New stability test note", "Test", "Stability", ["test"]
        )
        assert new_note_id is not None
        
        # READ - verify new note
        updated_notes = populated_manager.get_notes(1)
        assert len(updated_notes) == initial_count + 1
        
        new_note = next(note for note in updated_notes if note['id'] == new_note_id)
        assert new_note['content'] == "New stability test note"
        
        # UPDATE - modify existing note
        success = populated_manager.update_note(new_note_id, "Updated content", ["updated"])
        assert success is True
        
        updated_notes = populated_manager.get_notes(1)
        updated_note = next(note for note in updated_notes if note['id'] == new_note_id)
        assert updated_note['content'] == "Updated content"
        assert "updated" in updated_note['tags']
        
        # DELETE - remove note
        success = populated_manager.delete_note(new_note_id)
        assert success is True
        
        final_notes = populated_manager.get_notes(1)
        assert len(final_notes) == initial_count
    
    def test_search_functionality_stability(self, populated_manager):
        """Test that search functionality remains stable"""
        # Content search
        search_results = populated_manager.get_notes(1, search_term="search")
        assert len(search_results) == 2  # Binary and linear search
        
        # Tag search
        algorithm_notes = populated_manager.get_notes(1, search_term="algorithm")
        assert len(algorithm_notes) == 2
        
        # Module filter
        algo_notes = populated_manager.get_notes(1, module_name="Algorithms")
        assert len(algo_notes) == 2
        
        # Lesson filter
        lesson_notes = populated_manager.get_notes(1, lesson_id=101)
        assert len(lesson_notes) == 1
        assert "Binary search" in lesson_notes[0]['content']
        
        # Case insensitive search
        case_results = populated_manager.get_notes(1, search_term="BINARY")
        assert len(case_results) == 1
    
    def test_user_isolation_stability(self, populated_manager):
        """Test that user isolation continues to work"""
        user1_notes = populated_manager.get_notes(1)
        user2_notes = populated_manager.get_notes(2)
        
        assert len(user1_notes) == 3
        assert len(user2_notes) == 1
        
        # Verify no cross-contamination
        user1_contents = [note['content'] for note in user1_notes]
        user2_contents = [note['content'] for note in user2_notes]
        
        assert all(note['user_id'] == 1 for note in user1_notes)
        assert all(note['user_id'] == 2 for note in user2_notes)
        assert "Different user" not in ' '.join(user1_contents)
        assert "Different user" in ' '.join(user2_contents)
    
    def test_favorites_functionality_stability(self, populated_manager):
        """Test that favorites functionality remains stable"""
        notes = populated_manager.get_notes(1)
        first_note_id = notes[0]['id']
        
        # Initially not favorite
        assert notes[0]['is_favorite'] == 0
        
        # Toggle to favorite
        success = populated_manager.toggle_favorite(first_note_id)
        assert success is True
        
        # Verify favorite status
        updated_notes = populated_manager.get_notes(1)
        favorite_note = next(note for note in updated_notes if note['id'] == first_note_id)
        assert favorite_note['is_favorite'] == 1
        
        # Verify in statistics
        stats = populated_manager.get_statistics(1)
        assert stats['favorites'] == 1
        
        # Toggle back
        populated_manager.toggle_favorite(first_note_id)
        final_notes = populated_manager.get_notes(1)
        unfavorite_note = next(note for note in final_notes if note['id'] == first_note_id)
        assert unfavorite_note['is_favorite'] == 0
    
    def test_statistics_calculation_stability(self, populated_manager):
        """Test that statistics calculations remain accurate"""
        stats = populated_manager.get_statistics(1)
        
        # Verify basic counts
        assert stats['total_notes'] == 3
        assert stats['favorites'] == 0
        assert stats['recent_notes'] == 3  # All notes are recent
        
        # Verify module breakdown
        expected_modules = {'Algorithms': 2, 'Data Structures': 1}
        assert stats['by_module'] == expected_modules
    
    def test_export_functionality_stability(self, populated_manager):
        """Test that export functionality remains stable"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test all export formats
            formats = ['json', 'markdown', 'html']
            
            for fmt in formats:
                export_file = populated_manager.export_notes(1, format=fmt, output_dir=temp_dir)
                assert export_file is not None
                assert os.path.exists(export_file)
                
                # Verify file is not empty
                assert os.path.getsize(export_file) > 0
                
                # Verify contains expected content
                with open(export_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if fmt == 'json':
                    data = json.loads(content)
                    assert len(data) == 3
                    assert all('content' in item for item in data)
                else:
                    assert 'algorithm' in content.lower()
                    assert 'search' in content.lower()


class TestProgressTrackingRegression:
    """Test that progress tracking features continue to work"""
    
    @pytest.fixture
    def progress_db(self):
        """Create database with progress tracking setup"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        with sqlite3.connect(path) as conn:
            cursor = conn.cursor()
            
            # Create comprehensive schema
            cursor.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE lessons (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    module_name TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE progress (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    lesson_id INTEGER,
                    completed BOOLEAN DEFAULT 0,
                    score INTEGER DEFAULT 0,
                    time_spent INTEGER DEFAULT 0,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (lesson_id) REFERENCES lessons(id)
                )
            """)
            
            # Insert test data
            cursor.execute("INSERT INTO users (id, name) VALUES (1, 'Test User')")
            cursor.execute("""
                INSERT INTO lessons (id, title, module_name) VALUES 
                (101, 'Arrays: Basic Operations', 'Data Structures'),
                (102, 'Sorting: Quick Sort', 'Algorithms'),
                (103, 'Trees: Binary Search Trees', 'Data Structures')
            """)
            
            cursor.execute("""
                INSERT INTO progress (user_id, lesson_id, completed, score, time_spent) VALUES
                (1, 101, 1, 95, 1800),
                (1, 102, 0, 0, 600),
                (1, 103, 0, 0, 0)
            """)
            
            conn.commit()
        
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    def test_lesson_navigation_with_notes(self, progress_db):
        """Test that lesson navigation continues to work with notes"""
        manager = NotesManager(progress_db)
        
        # Add notes during "lesson viewing"
        current_lesson_id = 101
        note_id = manager.save_note(
            1, current_lesson_id, 
            "Notes while viewing Arrays lesson", 
            "Data Structures", "Arrays", ["arrays", "lesson"]
        )
        
        # Navigate to different lesson
        next_lesson_id = 102
        manager.save_note(
            1, next_lesson_id,
            "Notes while viewing Sorting lesson",
            "Algorithms", "Sorting", ["sorting", "lesson"]
        )
        
        # Should be able to retrieve notes by lesson
        arrays_notes = manager.get_notes(1, lesson_id=current_lesson_id)
        sorting_notes = manager.get_notes(1, lesson_id=next_lesson_id)
        
        assert len(arrays_notes) == 1
        assert len(sorting_notes) == 1
        assert "Arrays lesson" in arrays_notes[0]['content']
        assert "Sorting lesson" in sorting_notes[0]['content']
    
    def test_progress_persistence_with_notes(self, progress_db):
        """Test that progress data persists alongside notes"""
        manager = NotesManager(progress_db)
        
        # Add notes to lessons with existing progress
        manager.save_note(1, 101, "Additional arrays notes", "Data Structures", "Arrays")
        manager.save_note(1, 102, "Additional sorting notes", "Algorithms", "Sorting")
        
        # Verify original progress data is intact
        with sqlite3.connect(progress_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT lesson_id, completed, score, time_spent 
                FROM progress WHERE user_id = 1
                ORDER BY lesson_id
            """)
            progress_data = cursor.fetchall()
        
        # Verify progress data unchanged
        assert progress_data[0] == (101, 1, 95, 1800)  # Completed lesson
        assert progress_data[1] == (102, 0, 0, 600)    # In progress lesson
        assert progress_data[2] == (103, 0, 0, 0)      # Unstarted lesson
        
        # Verify notes were added
        notes = manager.get_notes(1)
        assert len(notes) == 2
    
    def test_quiz_scores_integration(self, progress_db):
        """Test that notes don't interfere with quiz scoring"""
        manager = NotesManager(progress_db)
        
        # Add notes about quiz preparation
        manager.save_note(
            1, 101, "Quiz prep notes: Remember array indexing starts at 0",
            "Data Structures", "Arrays - Quiz Prep", ["quiz", "prep"]
        )
        
        # Simulate quiz completion by updating progress
        with sqlite3.connect(progress_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE progress 
                SET completed = 1, score = 88 
                WHERE user_id = 1 AND lesson_id = 102
            """)
            conn.commit()
        
        # Add post-quiz reflection notes
        manager.save_note(
            1, 102, "Quiz reflection: Need to review time complexity",
            "Algorithms", "Sorting - Reflection", ["quiz", "reflection", "review"]
        )
        
        # Verify quiz scores are preserved
        with sqlite3.connect(progress_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT lesson_id, score 
                FROM progress 
                WHERE user_id = 1 AND completed = 1
                ORDER BY lesson_id
            """)
            scores = cursor.fetchall()
        
        assert (101, 95) in scores  # Original score
        assert (102, 88) in scores  # New score
        
        # Verify notes exist
        quiz_notes = manager.get_notes(1, search_term="quiz")
        assert len(quiz_notes) == 2


class TestUINotesRegression:
    """Test that UI notes features remain stable"""
    
    @pytest.fixture
    def temp_notes_dir(self):
        import tempfile
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def ui_manager(self, temp_notes_dir):
        formatter = TerminalFormatter()
        return UINotesManager(formatter, temp_notes_dir)
    
    def test_rich_formatting_stability(self, ui_manager):
        """Test that rich text formatting continues to work"""
        # Create note with various formatting
        formatted_note = RichNote(
            "format_test", "Formatting Test",
            "This note has **bold text**, *italic text*, and `code snippets`.\n\n" +
            "# Header\n" +
            "- List item 1\n" +
            "- List item 2\n" +
            "1. Numbered item\n" +
            "2. Another numbered item",
            NoteType.EXAMPLE, Priority.MEDIUM, ["formatting", "test"]
        )
        
        ui_manager.notes[formatted_note.id] = formatted_note
        
        # Verify formatting was applied
        assert formatted_note.formatted_content != formatted_note.content
        assert '\033[1m' in formatted_note.formatted_content  # Bold
        assert '\033[3m' in formatted_note.formatted_content  # Italic
        assert '\033[93m' in formatted_note.formatted_content  # Code or numbers
        assert '\033[92m' in formatted_note.formatted_content  # Lists
    
    def test_note_types_and_priorities_stability(self, ui_manager):
        """Test that note types and priorities work correctly"""
        # Create notes of different types and priorities
        test_notes = [
            RichNote("concept1", "Concept", "Content", NoteType.CONCEPT, Priority.HIGH),
            RichNote("example1", "Example", "Content", NoteType.EXAMPLE, Priority.MEDIUM),
            RichNote("question1", "Question", "Content", NoteType.QUESTION, Priority.URGENT),
            RichNote("insight1", "Insight", "Content", NoteType.INSIGHT, Priority.LOW),
            RichNote("todo1", "Todo", "Content", NoteType.TODO, Priority.CRITICAL),
            RichNote("ref1", "Reference", "Content", NoteType.REFERENCE, Priority.MEDIUM)
        ]
        
        for note in test_notes:
            ui_manager.notes[note.id] = note
        
        # Test statistics by type and priority
        stats = ui_manager.get_statistics()
        
        assert stats['total_notes'] == 6
        assert stats['notes_by_type']['concept'] == 1
        assert stats['notes_by_type']['example'] == 1
        assert stats['notes_by_type']['question'] == 1
        assert stats['notes_by_type']['insight'] == 1
        assert stats['notes_by_type']['todo'] == 1
        assert stats['notes_by_type']['reference'] == 1
        
        assert stats['notes_by_priority']['HIGH'] == 1
        assert stats['notes_by_priority']['MEDIUM'] == 2
        assert stats['notes_by_priority']['URGENT'] == 1
        assert stats['notes_by_priority']['LOW'] == 1
        assert stats['notes_by_priority']['CRITICAL'] == 1
    
    def test_search_and_indexing_stability(self, ui_manager):
        """Test that search and indexing continue to work"""
        # Create notes with tags and topics
        notes = [
            RichNote("search1", "Search Test 1", "Algorithm content", 
                    NoteType.CONCEPT, Priority.MEDIUM, ["algorithm", "search"]),
            RichNote("search2", "Search Test 2", "Data structure content",
                    NoteType.CONCEPT, Priority.MEDIUM, ["data-structure", "tree"]),
            RichNote("search3", "Search Test 3", "Performance analysis",
                    NoteType.INSIGHT, Priority.HIGH, ["performance", "analysis"])
        ]
        
        for note in notes:
            note.topic = "Search Testing"
            ui_manager.notes[note.id] = note
            ui_manager._update_indices(note)
        
        # Test various search methods
        title_results = ui_manager.search_notes("Search Test", search_type="title")
        assert len(title_results) == 3
        
        content_results = ui_manager.search_notes("algorithm", search_type="content")
        assert len(content_results) == 1
        
        tag_results = ui_manager.search_notes("performance", search_type="tags")
        assert len(tag_results) == 1
        
        all_results = ui_manager.search_notes("content", search_type="all")
        assert len(all_results) == 2  # "content" appears in two notes
        
        # Test topic and tag indexing
        topic_notes = ui_manager.get_notes_by_topic("Search Testing")
        assert len(topic_notes) == 3
        
        algorithm_notes = ui_manager.get_notes_by_tag("algorithm")
        assert len(algorithm_notes) == 1
    
    def test_persistence_stability(self, ui_manager):
        """Test that UI notes persistence continues to work"""
        # Create test notes
        original_notes = [
            RichNote("persist1", "Persistent Note 1", "Content 1",
                    NoteType.CONCEPT, Priority.HIGH, ["persist", "test"]),
            RichNote("persist2", "Persistent Note 2", "Content 2",
                    NoteType.EXAMPLE, Priority.MEDIUM, ["persist", "demo"])
        ]
        
        for note in original_notes:
            ui_manager.notes[note.id] = note
            ui_manager._update_indices(note)
        
        # Save to disk
        ui_manager.save_notes()
        
        # Create new manager instance
        new_manager = UINotesManager(ui_manager.formatter, str(ui_manager.notes_dir))
        
        # Verify notes were loaded
        assert len(new_manager.notes) == 2
        assert "persist1" in new_manager.notes
        assert "persist2" in new_manager.notes
        
        # Verify indices were rebuilt
        persist_notes = new_manager.get_notes_by_tag("persist")
        assert len(persist_notes) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
