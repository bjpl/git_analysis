#!/usr/bin/env python3
"""
Integration Tests for Notes System
Testing component interactions, lesson integration, and session persistence
"""

import pytest
import tempfile
import os
import json
import sqlite3
import time
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta

# Import the classes under test
sys_path = Path(__file__).parent.parent.parent / "src"
import sys
sys.path.insert(0, str(sys_path))

from notes_manager import NotesManager, integrate_with_cli
from ui.notes import NotesManager as UINotesManager, RichNote, NoteType, Priority, NoteEditor
from ui.formatter import TerminalFormatter


class MockCLI:
    """Mock CLI instance for testing integration"""
    def __init__(self):
        self.current_user_id = 1
        self.current_lesson_id = 101
        self.current_module = "Algorithms"
        self.commands = {}


class TestNotesLessonIntegration:
    """Test integration between notes and lesson system"""
    
    @pytest.fixture
    def temp_db(self):
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        # Initialize with lesson data
        with sqlite3.connect(path) as conn:
            cursor = conn.cursor()
            
            # Create lessons table
            cursor.execute("""
                CREATE TABLE lessons (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    module_name TEXT,
                    content TEXT,
                    difficulty TEXT
                )
            """)
            
            # Create users table
            cursor.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                )
            """)
            
            # Create progress table
            cursor.execute("""
                CREATE TABLE progress (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    lesson_id INTEGER,
                    completed BOOLEAN,
                    score INTEGER,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (lesson_id) REFERENCES lessons(id)
                )
            """)
            
            # Insert test data
            cursor.execute("INSERT INTO users (id, name) VALUES (1, 'Test User')")
            cursor.execute("""
                INSERT INTO lessons (id, title, module_name, content, difficulty)
                VALUES 
                    (101, 'Binary Search: Introduction', 'Algorithms', 'Binary search content...', 'Intermediate'),
                    (102, 'Linear Search: Basics', 'Algorithms', 'Linear search content...', 'Beginner'),
                    (201, 'Arrays: Fundamentals', 'Data Structures', 'Array content...', 'Beginner')
            """)
            
            cursor.execute("""
                INSERT INTO progress (user_id, lesson_id, completed, score, notes)
                VALUES 
                    (1, 101, 1, 95, 'Old progress note about binary search'),
                    (1, 102, 0, 0, NULL)
            """)
            
            conn.commit()
        
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    @pytest.fixture
    def notes_manager(self, temp_db):
        return NotesManager(temp_db)
    
    def test_note_creation_during_lesson(self, notes_manager):
        """Test creating notes while viewing a lesson"""
        lesson_id = 101
        user_id = 1
        
        # Simulate note creation during lesson
        note_id = notes_manager.save_note(
            user_id, lesson_id, 
            "Key insight: Binary search requires sorted array",
            "Algorithms", "Binary Search", ["requirement", "sorted"]
        )
        
        # Verify note is associated with lesson
        notes = notes_manager.get_notes(user_id, lesson_id=lesson_id)
        assert len(notes) == 1
        assert notes[0]['lesson_id'] == lesson_id
        assert "Binary search" in notes[0]['content']
    
    def test_notes_persistence_across_sessions(self, notes_manager):
        """Test that notes persist when user returns to lesson"""
        user_id = 1
        lesson_id = 101
        
        # Session 1: Create notes
        session1_note = notes_manager.save_note(
            user_id, lesson_id, "Session 1 insight", "Module", "Topic", ["session1"]
        )
        
        # Simulate session end - create new manager instance
        new_manager = NotesManager(notes_manager.db_path)
        
        # Session 2: Create more notes
        session2_note = new_manager.save_note(
            user_id, lesson_id, "Session 2 insight", "Module", "Topic", ["session2"]
        )
        
        # Verify both notes persist
        all_notes = new_manager.get_notes(user_id, lesson_id=lesson_id)
        assert len(all_notes) == 2
        
        contents = [note['content'] for note in all_notes]
        assert "Session 1 insight" in contents
        assert "Session 2 insight" in contents
    
    def test_notes_export_import_integration(self, notes_manager):
        """Test full export/import cycle"""
        user_id = 1
        
        # Create diverse notes
        test_notes = [
            (101, "Binary search complexity analysis", "Algorithms", "Analysis", ["complexity", "O(log n)"]),
            (102, "Linear search implementation", "Algorithms", "Implementation", ["simple", "O(n)"]),
            (201, "Array memory layout", "Data Structures", "Memory", ["contiguous", "memory"])
        ]
        
        for lesson_id, content, module, topic, tags in test_notes:
            notes_manager.save_note(user_id, lesson_id, content, module, topic, tags)
        
        # Export notes
        with tempfile.TemporaryDirectory() as temp_dir:
            export_file = notes_manager.export_notes(user_id, format="json", output_dir=temp_dir)
            assert export_file is not None
            assert os.path.exists(export_file)
            
            # Verify export content
            with open(export_file, 'r', encoding='utf-8') as f:
                exported_data = json.load(f)
            
            assert len(exported_data) == 3
            assert all(note['user_id'] == user_id for note in exported_data)
    
    def test_notes_migration_from_progress_table(self, notes_manager):
        """Test migration of old notes from progress table"""
        # Migration should happen during initialization
        migrated_count = notes_manager.migrate_old_notes()
        
        # Should migrate the existing progress note
        assert migrated_count == 1
        
        # Verify migrated note
        notes = notes_manager.get_notes(1)
        migrated_notes = [n for n in notes if "Old progress note" in n['content']]
        assert len(migrated_notes) == 1
        
        migrated_note = migrated_notes[0]
        assert migrated_note['lesson_id'] == 101
        assert migrated_note['module_name'] == "Binary Search"  # Extracted from lesson title
    
    def test_notes_cleanup_orphaned_references(self, temp_db):
        """Test cleanup of notes with invalid lesson references"""
        manager = NotesManager(temp_db)
        
        # Create notes with valid and invalid lesson references
        manager.save_note(1, 101, "Valid note", "Module", "Topic")  # Valid lesson
        manager.save_note(1, 999, "Orphaned note", "Module", "Topic")  # Invalid lesson
        
        # Cleanup should remove orphaned note
        deleted_count = manager.cleanup_orphaned_notes()
        assert deleted_count == 1
        
        # Only valid note should remain
        remaining_notes = manager.get_notes(1)
        assert len(remaining_notes) == 1
        assert remaining_notes[0]['content'] == "Valid note"
    
    def test_multi_user_lesson_notes_isolation(self, notes_manager):
        """Test that notes are isolated between users even for same lessons"""
        lesson_id = 101
        
        # Different users create notes for same lesson
        notes_manager.save_note(1, lesson_id, "User 1 notes", "Module", "Topic")
        notes_manager.save_note(2, lesson_id, "User 2 notes", "Module", "Topic")
        
        # Each user should only see their own notes
        user1_notes = notes_manager.get_notes(1, lesson_id=lesson_id)
        user2_notes = notes_manager.get_notes(2, lesson_id=lesson_id)
        
        assert len(user1_notes) == 1
        assert len(user2_notes) == 1
        assert user1_notes[0]['content'] == "User 1 notes"
        assert user2_notes[0]['content'] == "User 2 notes"


class TestNotesCLIIntegration:
    """Test integration between notes system and CLI"""
    
    @pytest.fixture
    def temp_db(self):
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    @pytest.fixture
    def mock_cli(self):
        return MockCLI()
    
    @pytest.fixture
    def integrated_cli(self, temp_db, mock_cli):
        """CLI with integrated notes commands"""
        # Create notes manager
        notes_manager = NotesManager(temp_db)
        
        # Integrate with CLI
        cli_commands = integrate_with_cli(mock_cli)
        mock_cli.commands.update(cli_commands)
        
        # Store manager for access in tests
        mock_cli.notes_manager = notes_manager
        
        return mock_cli
    
    def test_cli_note_commands_registration(self, integrated_cli):
        """Test that note commands are properly registered with CLI"""
        expected_commands = ['note', 'notes', 'note-export', 'note-stats', 'note-cleanup']
        
        for cmd in expected_commands:
            assert cmd in integrated_cli.commands
            assert callable(integrated_cli.commands[cmd])
    
    @patch('builtins.input')
    def test_cli_note_creation_interactive(self, mock_input, integrated_cli):
        """Test interactive note creation through CLI"""
        # Mock user input
        mock_input.side_effect = [
            "Test note content",  # Content
            "",                   # End content input
            "Test Topic",         # Topic
            "test, cli"           # Tags
        ]
        
        # Execute note creation command
        integrated_cli.commands['note']({})
        
        # Verify note was created
        notes = integrated_cli.notes_manager.get_notes(1)
        assert len(notes) == 1
        assert notes[0]['content'] == "Test note content"
        assert notes[0]['topic'] == "Test Topic"
        assert set(notes[0]['tags']) == {"test", "cli"}
    
    def test_cli_note_listing(self, integrated_cli):
        """Test listing notes through CLI"""
        # Create test notes
        integrated_cli.notes_manager.save_note(
            1, 101, "First CLI note", "Module1", "Topic1", ["cli", "test"]
        )
        integrated_cli.notes_manager.save_note(
            1, 102, "Second CLI note", "Module2", "Topic2", ["cli", "demo"]
        )
        
        # Test listing all notes
        with patch('src.notes_manager.console') as mock_console:
            integrated_cli.commands['notes']({})
            # Should display notes table
            assert mock_console.print.called
    
    def test_cli_note_export(self, integrated_cli):
        """Test note export through CLI"""
        # Create test note
        integrated_cli.notes_manager.save_note(
            1, None, "Export test note", "Module", "Topic", ["export"]
        )
        
        # Test export
        with patch('src.notes_manager.console') as mock_console:
            integrated_cli.commands['note-export']({'format': 'markdown'})
            # Should show success message
            mock_console.print.assert_called()
    
    def test_cli_note_statistics(self, integrated_cli):
        """Test note statistics display through CLI"""
        # Create test notes in different modules
        test_notes = [
            ("Note 1", "Module1", ["tag1"]),
            ("Note 2", "Module1", ["tag2"]),
            ("Note 3", "Module2", ["tag1"])
        ]
        
        for content, module, tags in test_notes:
            integrated_cli.notes_manager.save_note(1, None, content, module, "Topic", tags)
        
        # Mark one as favorite
        notes = integrated_cli.notes_manager.get_notes(1)
        integrated_cli.notes_manager.toggle_favorite(notes[0]['id'])
        
        # Test statistics display
        with patch('src.notes_manager.console') as mock_console:
            integrated_cli.commands['note-stats']({})
            # Should display statistics panel
            assert mock_console.print.called
    
    def test_cli_context_preservation(self, integrated_cli):
        """Test that CLI context is preserved in note operations"""
        # Set CLI context
        integrated_cli.current_user_id = 5
        integrated_cli.current_lesson_id = 205
        integrated_cli.current_module = "Advanced Algorithms"
        
        # Mock note creation
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = ["Context test", "", "Test", "context"]
            integrated_cli.commands['note']({})
        
        # Verify context was used
        notes = integrated_cli.notes_manager.get_notes(5)  # User ID 5
        assert len(notes) == 1
        assert notes[0]['user_id'] == 5
        assert notes[0]['lesson_id'] == 205
        assert notes[0]['module_name'] == "Advanced Algorithms"


class TestNotesUIIntegration:
    """Test integration of rich UI notes with other components"""
    
    @pytest.fixture
    def temp_notes_dir(self):
        import tempfile
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def formatter(self):
        return TerminalFormatter()
    
    @pytest.fixture
    def ui_notes_manager(self, formatter, temp_notes_dir):
        return UINotesManager(formatter, temp_notes_dir)
    
    @pytest.fixture
    def sample_notes(self, ui_notes_manager):
        """Create sample notes for testing"""
        notes = [
            RichNote(
                "integration1", "Integration Test Note",
                "This is a **test note** for integration testing\n- Point 1\n- Point 2",
                NoteType.CONCEPT, Priority.HIGH, ["integration", "test"]
            ),
            RichNote(
                "integration2", "Code Example Note",
                "```python\ndef example():\n    return 'test'\n```",
                NoteType.EXAMPLE, Priority.MEDIUM, ["code", "python"]
            )
        ]
        
        for note in notes:
            ui_notes_manager.notes[note.id] = note
            ui_notes_manager._update_indices(note)
        
        return notes
    
    def test_ui_notes_persistence_integration(self, ui_notes_manager, sample_notes):
        """Test UI notes persistence across manager instances"""
        # Save notes
        ui_notes_manager.save_notes()
        
        # Create new manager instance
        new_manager = UINotesManager(
            ui_notes_manager.formatter, 
            str(ui_notes_manager.notes_dir)
        )
        
        # Verify notes loaded
        assert len(new_manager.notes) == 2
        assert "integration1" in new_manager.notes
        assert "integration2" in new_manager.notes
        
        # Verify indices rebuilt
        assert "integration" in new_manager.tags_index
        assert "test" in new_manager.tags_index
    
    @pytest.mark.asyncio
    async def test_note_editor_integration(self, formatter):
        """Test note editor integration with notes manager"""
        editor = NoteEditor(formatter)
        
        # Mock user input for note creation
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = [
                "Test Editor Note",  # Title
                "editor, test"       # Tags
            ]
            
            # Mock navigation menu selections
            with patch('src.ui.navigation.NavigationController.show_menu') as mock_menu:
                mock_menu.side_effect = [
                    (None, "1"),  # Note type: Concept
                    (None, "3")   # Priority: High
                ]
                
                # Mock content input (editor)
                with patch('builtins.input') as mock_content:
                    mock_content.side_effect = [
                        "This is test content",
                        "/save"
                    ]
                    
                    note = await editor.create_new_note("Test Topic")
        
        # Verify note creation
        assert note is not None
        assert note.title == "Test Editor Note"
        assert note.content == "This is test content"
        assert note.note_type == NoteType.CONCEPT
        assert note.priority == Priority.HIGH
        assert "editor" in note.tags
    
    @pytest.mark.asyncio
    async def test_note_formatting_integration(self, ui_notes_manager, sample_notes):
        """Test rich formatting integration"""
        # Get note with formatting
        formatted_note = ui_notes_manager.notes["integration1"]
        
        # Check that formatted content was generated
        assert formatted_note.formatted_content
        assert formatted_note.formatted_content != formatted_note.content
        
        # Verify formatting applied (contains ANSI codes for bold)
        assert '\033[1m' in formatted_note.formatted_content  # Bold formatting
        assert '\033[92m' in formatted_note.formatted_content  # List formatting
    
    def test_search_integration_with_indices(self, ui_notes_manager, sample_notes):
        """Test search integration with tag and topic indices"""
        # Test tag-based search
        tag_results = ui_notes_manager.get_notes_by_tag("integration")
        assert len(tag_results) == 1
        assert tag_results[0].id == "integration1"
        
        # Test general search
        search_results = ui_notes_manager.search_notes("test", search_type="all")
        assert len(search_results) == 2  # Both notes contain "test"
    
    def test_statistics_integration(self, ui_notes_manager, sample_notes):
        """Test statistics integration with UI notes"""
        stats = ui_notes_manager.get_statistics()
        
        assert stats['total_notes'] == 2
        assert stats['notes_by_type']['concept'] == 1
        assert stats['notes_by_type']['example'] == 1
        assert stats['notes_by_priority']['HIGH'] == 1
        assert stats['notes_by_priority']['MEDIUM'] == 1
        assert stats['total_tags'] == 4  # integration, test, code, python


class TestNotesMultiTabSynchronization:
    """Test notes synchronization across multiple sessions/tabs"""
    
    @pytest.fixture
    def temp_db(self):
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    def test_concurrent_note_creation(self, temp_db):
        """Test concurrent note creation from multiple sessions"""
        # Create two manager instances (simulate two tabs)
        manager1 = NotesManager(temp_db)
        manager2 = NotesManager(temp_db)
        
        # Create notes from both sessions
        note1_id = manager1.save_note(1, None, "Session 1 note", "Module", "Topic")
        note2_id = manager2.save_note(1, None, "Session 2 note", "Module", "Topic")
        
        # Both managers should see all notes
        manager1_notes = manager1.get_notes(1)
        manager2_notes = manager2.get_notes(1)
        
        assert len(manager1_notes) == 2
        assert len(manager2_notes) == 2
        
        # Verify unique IDs
        all_ids = [note['id'] for note in manager1_notes]
        assert len(set(all_ids)) == 2
        assert note1_id in all_ids
        assert note2_id in all_ids
    
    def test_note_update_synchronization(self, temp_db):
        """Test note updates are visible across sessions"""
        manager1 = NotesManager(temp_db)
        manager2 = NotesManager(temp_db)
        
        # Create note in session 1
        note_id = manager1.save_note(1, None, "Original content", "Module", "Topic")
        
        # Update note in session 2
        manager2.update_note(note_id, "Updated content", ["updated"])
        
        # Session 1 should see the update
        updated_notes = manager1.get_notes(1)
        assert len(updated_notes) == 1
        assert updated_notes[0]['content'] == "Updated content"
        assert "updated" in updated_notes[0]['tags']
    
    def test_note_deletion_synchronization(self, temp_db):
        """Test note deletions are synchronized across sessions"""
        manager1 = NotesManager(temp_db)
        manager2 = NotesManager(temp_db)
        
        # Create notes in both sessions
        note1_id = manager1.save_note(1, None, "Note 1", "Module", "Topic")
        note2_id = manager2.save_note(1, None, "Note 2", "Module", "Topic")
        
        # Delete one note from session 1
        manager1.delete_note(note1_id)
        
        # Session 2 should only see the remaining note
        remaining_notes = manager2.get_notes(1)
        assert len(remaining_notes) == 1
        assert remaining_notes[0]['id'] == note2_id
        assert remaining_notes[0]['content'] == "Note 2"


class TestNotesPerformanceIntegration:
    """Test performance characteristics of integrated notes system"""
    
    @pytest.fixture
    def temp_db(self):
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    def test_bulk_operations_performance(self, temp_db):
        """Test performance of bulk note operations"""
        manager = NotesManager(temp_db)
        
        # Bulk creation
        start_time = time.time()
        note_ids = []
        
        for i in range(100):
            note_id = manager.save_note(
                1, None, f"Bulk note {i} content", 
                f"Module{i % 5}", f"Topic{i}", 
                [f"tag{i % 3}", "bulk"]
            )
            note_ids.append(note_id)
        
        creation_time = time.time() - start_time
        
        # Bulk retrieval
        start_time = time.time()
        all_notes = manager.get_notes(1)
        retrieval_time = time.time() - start_time
        
        # Bulk search
        start_time = time.time()
        search_results = manager.get_notes(1, search_term="bulk")
        search_time = time.time() - start_time
        
        # Performance assertions
        assert len(all_notes) == 100
        assert len(search_results) == 100
        assert creation_time < 5.0  # Should create 100 notes in under 5 seconds
        assert retrieval_time < 1.0  # Should retrieve in under 1 second
        assert search_time < 2.0     # Should search in under 2 seconds
        
        print(f"Created 100 notes in {creation_time:.2f}s")
        print(f"Retrieved 100 notes in {retrieval_time:.4f}s")
        print(f"Searched 100 notes in {search_time:.4f}s")
    
    def test_large_content_performance(self, temp_db):
        """Test performance with large note content"""
        manager = NotesManager(temp_db)
        
        # Create note with large content (1MB)
        large_content = "X" * (1024 * 1024)  # 1MB
        
        start_time = time.time()
        note_id = manager.save_note(1, None, large_content, "Module", "Topic")
        save_time = time.time() - start_time
        
        start_time = time.time()
        notes = manager.get_notes(1)
        load_time = time.time() - start_time
        
        # Verify content integrity and performance
        assert len(notes) == 1
        assert len(notes[0]['content']) == 1024 * 1024
        assert save_time < 2.0   # Should save 1MB in under 2 seconds
        assert load_time < 1.0   # Should load in under 1 second
        
        print(f"Saved 1MB note in {save_time:.4f}s")
        print(f"Loaded 1MB note in {load_time:.4f}s")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
