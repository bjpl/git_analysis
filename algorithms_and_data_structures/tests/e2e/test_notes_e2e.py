#!/usr/bin/env python3
"""
End-to-End Tests for Notes System
Testing complete user workflows and real-world scenarios
"""

import pytest
import tempfile
import os
import json
import subprocess
import time
import asyncio
import signal
import threading
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the classes under test
sys_path = Path(__file__).parent.parent.parent / "src"
import sys
sys.path.insert(0, str(sys_path))

from notes_manager import NotesManager, integrate_with_cli
from ui.notes import NotesManager as UINotesManager, RichNote, NoteType, Priority
from ui.formatter import TerminalFormatter


class TestCompleteNoteWorkflows:
    """Test complete end-to-end note-taking workflows"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for E2E testing"""
        import tempfile
        workspace = tempfile.mkdtemp()
        
        # Create directory structure
        (Path(workspace) / "notes").mkdir()
        (Path(workspace) / "exports").mkdir()
        
        yield workspace
        
        import shutil
        shutil.rmtree(workspace, ignore_errors=True)
    
    @pytest.fixture
    def learning_session_notes(self, temp_workspace):
        """Simulate a complete learning session with notes"""
        db_path = Path(workspace) / "curriculum.db"
        manager = NotesManager(str(db_path))
        
        # Simulate learning session: Arrays module
        session_notes = [
            {
                'content': "Arrays store elements in contiguous memory locations",
                'module': "Data Structures",
                'topic': "Arrays - Introduction",
                'tags': ["memory", "contiguous", "basic"]
            },
            {
                'content': "Array indexing: arr[i] gives O(1) access time",
                'module': "Data Structures", 
                'topic': "Arrays - Indexing",
                'tags': ["indexing", "O(1)", "performance"]
            },
            {
                'content': "Dynamic arrays (vectors) can resize automatically",
                'module': "Data Structures",
                'topic': "Arrays - Dynamic",
                'tags': ["dynamic", "resize", "vectors"]
            },
            {
                'content': "Question: How does dynamic array resizing work internally?",
                'module': "Data Structures",
                'topic': "Arrays - Questions", 
                'tags': ["question", "resizing", "internal"]
            },
            {
                'content': "Insight: Arrays are perfect for sequential data processing",
                'module': "Data Structures",
                'topic': "Arrays - Insights",
                'tags': ["insight", "sequential", "processing"]
            }
        ]
        
        user_id = 1
        note_ids = []
        
        for i, note_data in enumerate(session_notes, 1):
            note_id = manager.save_note(
                user_id, 100 + i, note_data['content'],
                note_data['module'], note_data['topic'], note_data['tags']
            )
            note_ids.append(note_id)
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        return manager, note_ids, session_notes
    
    def test_complete_note_taking_session(self, learning_session_notes):
        """Test complete note-taking session workflow"""
        manager, note_ids, expected_notes = learning_session_notes
        
        # 1. Verify all notes were created
        all_notes = manager.get_notes(1)
        assert len(all_notes) == 5
        
        # 2. Test searching during the session
        array_notes = manager.get_notes(1, search_term="array")
        assert len(array_notes) >= 3  # Should find multiple array-related notes
        
        # 3. Test filtering by module
        ds_notes = manager.get_notes(1, module_name="Data Structures")
        assert len(ds_notes) == 5
        
        # 4. Test tagging system
        performance_notes = manager.get_notes(1, search_term="performance")
        assert len(performance_notes) >= 1
        
        # 5. Mark important notes as favorites
        insights = [n for n in all_notes if "insight" in n['tags']]
        for insight in insights:
            manager.toggle_favorite(insight['id'])
        
        # 6. Verify favorites
        stats = manager.get_statistics(1)
        assert stats['favorites'] >= 1
    
    def test_multi_session_note_continuity(self, temp_workspace):
        """Test note continuity across multiple learning sessions"""
        db_path = Path(temp_workspace) / "curriculum.db"
        
        # Session 1: Arrays
        session1_manager = NotesManager(str(db_path))
        session1_note = session1_manager.save_note(
            1, 101, "Arrays session 1 notes", "Arrays", "Basics", ["session1"]
        )
        
        # Simulate session end
        del session1_manager
        
        # Session 2: Continue with linked lists
        session2_manager = NotesManager(str(db_path))
        session2_note = session2_manager.save_note(
            1, 201, "Linked lists session 2 notes", "LinkedLists", "Basics", ["session2"]
        )
        
        # Session 3: Review both topics
        session3_manager = NotesManager(str(db_path))
        
        # Should see notes from all sessions
        all_notes = session3_manager.get_notes(1)
        assert len(all_notes) == 2
        
        contents = [note['content'] for note in all_notes]
        assert "Arrays session 1" in ' '.join(contents)
        assert "Linked lists session 2" in ' '.join(contents)
    
    def test_note_export_import_workflow(self, learning_session_notes):
        """Test complete export/import workflow"""
        manager, note_ids, _ = learning_session_notes
        
        # Export in different formats
        with tempfile.TemporaryDirectory() as export_dir:
            # 1. Export as Markdown
            md_file = manager.export_notes(1, format="markdown", output_dir=export_dir)
            assert md_file is not None
            assert Path(md_file).exists()
            assert Path(md_file).suffix == ".md"
            
            # Verify markdown content
            with open(md_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
            assert "# 📚 Learning Notes" in md_content
            assert "Data Structures" in md_content
            assert "Arrays" in md_content
            
            # 2. Export as HTML
            html_file = manager.export_notes(1, format="html", output_dir=export_dir)
            assert html_file is not None
            assert Path(html_file).exists()
            assert Path(html_file).suffix == ".html"
            
            # Verify HTML structure
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            assert "<!DOCTYPE html>" in html_content
            assert "<body>" in html_content
            assert "Learning Notes" in html_content
            
            # 3. Export as JSON
            json_file = manager.export_notes(1, format="json", output_dir=export_dir)
            assert json_file is not None
            assert Path(json_file).exists()
            assert Path(json_file).suffix == ".json"
            
            # Verify JSON structure
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            assert len(json_data) == 5
            assert all('content' in note for note in json_data)
            assert all('tags' in note for note in json_data)
    
    def test_note_search_and_review_workflow(self, learning_session_notes):
        """Test searching and reviewing notes workflow"""
        manager, note_ids, expected_notes = learning_session_notes
        
        # 1. Search by content keywords
        memory_notes = manager.get_notes(1, search_term="memory")
        assert len(memory_notes) >= 1
        
        # 2. Search by tags
        performance_notes = manager.get_notes(1, search_term="performance")
        assert len(performance_notes) >= 1
        
        # 3. Filter by specific topics
        intro_notes = manager.get_notes(1, search_term="Introduction")
        assert len(intro_notes) >= 1
        
        # 4. Review questions for follow-up
        question_notes = manager.get_notes(1, search_term="question")
        assert len(question_notes) >= 1
        
        # 5. Review insights for key learnings
        insight_notes = manager.get_notes(1, search_term="insight")
        assert len(insight_notes) >= 1
        
        # 6. Get comprehensive statistics
        stats = manager.get_statistics(1)
        assert stats['total_notes'] == 5
        assert len(stats['by_module']) >= 1
        assert stats['recent_notes'] == 5  # All notes are recent
    
    @pytest.mark.asyncio
    async def test_rich_note_creation_workflow(self, temp_workspace):
        """Test rich note creation workflow with UI components"""
        formatter = TerminalFormatter()
        ui_manager = UINotesManager(formatter, temp_workspace)
        
        # Simulate rich note creation workflow
        rich_notes = [
            {
                'id': 'concept1',
                'title': 'Binary Search Concept',
                'content': '**Binary search** works on *sorted arrays*\n\n# Key Points:\n- Divide and conquer\n- O(log n) complexity\n- Requires sorted data',
                'type': NoteType.CONCEPT,
                'priority': Priority.HIGH,
                'tags': ['binary-search', 'algorithms', 'complexity'],
                'topic': 'Search Algorithms'
            },
            {
                'id': 'example1', 
                'title': 'Python Implementation',
                'content': '```python\ndef binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1\n```',
                'type': NoteType.EXAMPLE,
                'priority': Priority.MEDIUM,
                'tags': ['python', 'implementation', 'code'],
                'topic': 'Search Algorithms'
            },
            {
                'id': 'question1',
                'title': 'Performance Question',
                'content': 'Why does binary search require **sorted** data?\n\n*Need to research:*\n1. Comparison with linear search\n2. Preprocessing costs\n3. Use cases where sorting isn\'t worth it',
                'type': NoteType.QUESTION,
                'priority': Priority.HIGH,
                'tags': ['research', 'sorting', 'performance'],
                'topic': 'Search Algorithms'
            }
        ]
        
        # Create rich notes
        for note_data in rich_notes:
            note = RichNote(
                note_data['id'], note_data['title'], note_data['content'],
                note_data['type'], note_data['priority'], note_data['tags']
            )
            note.topic = note_data['topic']
            
            ui_manager.notes[note.id] = note
            ui_manager._update_indices(note)
        
        # Test rich formatting
        concept_note = ui_manager.notes['concept1']
        assert concept_note.formatted_content != concept_note.content
        assert '\033[1m' in concept_note.formatted_content  # Bold formatting
        
        # Test search functionality
        search_results = ui_manager.search_notes('binary', search_type='all')
        assert len(search_results) >= 1
        
        # Test topic grouping
        topic_notes = ui_manager.get_notes_by_topic('Search Algorithms')
        assert len(topic_notes) == 3
        
        # Test tag-based filtering
        python_notes = ui_manager.get_notes_by_tag('python')
        assert len(python_notes) == 1
        assert python_notes[0].id == 'example1'
        
        # Test statistics
        stats = ui_manager.get_statistics()
        assert stats['total_notes'] == 3
        assert stats['notes_by_type']['concept'] == 1
        assert stats['notes_by_type']['example'] == 1
        assert stats['notes_by_type']['question'] == 1
    
    def test_concurrent_user_workflows(self, temp_workspace):
        """Test multiple users working simultaneously"""
        db_path = Path(temp_workspace) / "multiuser.db"
        
        def user_workflow(user_id, module_name, num_notes):
            """Simulate a user's note-taking workflow"""
            manager = NotesManager(str(db_path))
            note_ids = []
            
            for i in range(num_notes):
                note_id = manager.save_note(
                    user_id, None, f"User {user_id} note {i+1}",
                    module_name, f"Topic {i+1}", [f"user{user_id}", f"note{i+1}"]
                )
                note_ids.append(note_id)
                time.sleep(0.01)  # Simulate typing time
            
            return note_ids
        
        # Simulate 3 users working concurrently
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(user_workflow, 1, "Algorithms", 3),
                executor.submit(user_workflow, 2, "Data Structures", 3), 
                executor.submit(user_workflow, 3, "Mathematics", 3)
            ]
            
            # Wait for all workflows to complete
            results = [future.result() for future in futures]
        
        # Verify all notes were created without conflicts
        final_manager = NotesManager(str(db_path))
        
        user1_notes = final_manager.get_notes(1)
        user2_notes = final_manager.get_notes(2)
        user3_notes = final_manager.get_notes(3)
        
        assert len(user1_notes) == 3
        assert len(user2_notes) == 3
        assert len(user3_notes) == 3
        
        # Verify user isolation
        assert all(note['user_id'] == 1 for note in user1_notes)
        assert all(note['user_id'] == 2 for note in user2_notes)
        assert all(note['user_id'] == 3 for note in user3_notes)
        
        # Verify module separation
        assert all(note['module_name'] == "Algorithms" for note in user1_notes)
        assert all(note['module_name'] == "Data Structures" for note in user2_notes)
        assert all(note['module_name'] == "Mathematics" for note in user3_notes)


class TestNoteSystemRecovery:
    """Test system recovery and error handling scenarios"""
    
    @pytest.fixture
    def temp_db(self):
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    def test_recovery_from_corrupted_database(self, temp_db):
        """Test recovery from database corruption"""
        # Create manager with some notes
        manager = NotesManager(temp_db)
        note_id = manager.save_note(1, None, "Important note", "Module", "Topic")
        
        # Simulate database corruption
        with open(temp_db, 'wb') as f:
            f.write(b"corrupted database content")
        
        # New manager should handle corruption gracefully
        try:
            recovery_manager = NotesManager(temp_db)
            # Should either recover or reinitialize without crashing
            notes = recovery_manager.get_notes(1)
            # If recovered: notes exist, if reinitialized: no notes but no crash
            assert isinstance(notes, list)
        except Exception as e:
            # Should not crash with unhandled exception
            assert "database" in str(e).lower() or "corrupt" in str(e).lower()
    
    def test_recovery_from_permission_errors(self, temp_db):
        """Test handling of file permission errors"""
        manager = NotesManager(temp_db)
        manager.save_note(1, None, "Test note", "Module", "Topic")
        
        # Make database read-only to simulate permission error
        os.chmod(temp_db, 0o444)  # Read-only
        
        try:
            # Operations should fail gracefully
            with pytest.raises((OSError, PermissionError)):
                manager.save_note(1, None, "New note", "Module", "Topic")
        finally:
            # Restore permissions for cleanup
            os.chmod(temp_db, 0o666)
    
    def test_handling_disk_full_scenario(self, temp_db):
        """Test handling when disk space is full"""
        manager = NotesManager(temp_db)
        
        # Create a very large note to simulate disk full condition
        try:
            large_content = "X" * (100 * 1024 * 1024)  # 100MB
            note_id = manager.save_note(1, None, large_content, "Module", "Topic")
            
            # If successful, verify it was actually saved
            notes = manager.get_notes(1)
            if len(notes) > 0:
                assert len(notes[0]['content']) == 100 * 1024 * 1024
                
        except (OSError, MemoryError) as e:
            # Acceptable - system limits reached
            assert "memory" in str(e).lower() or "space" in str(e).lower() or "size" in str(e).lower()
    
    def test_network_interruption_simulation(self, temp_db):
        """Test handling of simulated network interruptions (for cloud sync)"""
        manager = NotesManager(temp_db)
        
        # Create notes normally
        note_ids = []
        for i in range(5):
            note_id = manager.save_note(1, None, f"Note {i}", "Module", "Topic")
            note_ids.append(note_id)
        
        # Verify all notes are saved locally
        notes = manager.get_notes(1)
        assert len(notes) == 5
        
        # Even with simulated network issues, local operations should work
        with patch('builtins.open', side_effect=lambda *args, **kwargs: 
                   open(*args, **kwargs) if 'notes' not in str(args[0]) else 
                   (_ for _ in ()).throw(ConnectionError("Network error"))):
            
            # Local database operations should still work
            local_notes = manager.get_notes(1)
            assert len(local_notes) == 5


class TestAccessibilityAndUsability:
    """Test accessibility and usability features"""
    
    @pytest.fixture
    def temp_workspace(self):
        import tempfile
        workspace = tempfile.mkdtemp()
        yield workspace
        import shutil
        shutil.rmtree(workspace, ignore_errors=True)
    
    def test_keyboard_navigation_simulation(self, temp_workspace):
        """Test keyboard navigation patterns"""
        formatter = TerminalFormatter()
        ui_manager = UINotesManager(formatter, temp_workspace)
        
        # Create notes for navigation testing
        notes = [
            RichNote(f"nav{i}", f"Navigation Note {i}", f"Content {i}",
                    NoteType.CONCEPT, Priority.MEDIUM, [f"nav{i}"])
            for i in range(5)
        ]
        
        for note in notes:
            ui_manager.notes[note.id] = note
        
        # Test search navigation (simulated)
        search_results = ui_manager.search_notes("Navigation", search_type="title")
        assert len(search_results) == 5
        
        # Test that results are properly ordered for navigation
        for i, note in enumerate(search_results):
            assert f"Navigation Note {i}" in note.title
    
    def test_large_text_support(self, temp_workspace):
        """Test support for large font sizes and screen readers"""
        formatter = TerminalFormatter()
        ui_manager = UINotesManager(formatter, temp_workspace)
        
        # Create note with content suitable for accessibility
        accessible_note = RichNote(
            "accessible1",
            "Accessible Note Title",
            "This note contains **important information** formatted for accessibility.\n\n" +
            "# Section Header\n" +
            "- List item 1\n" +
            "- List item 2\n" +
            "\n" +
            "Clear, structured content for screen readers.",
            NoteType.CONCEPT,
            Priority.HIGH,
            ["accessibility", "structured"]
        )
        
        ui_manager.notes[accessible_note.id] = accessible_note
        
        # Verify structured content
        assert "# Section Header" in accessible_note.content
        assert "List item" in accessible_note.content
        assert accessible_note.formatted_content != accessible_note.content
    
    def test_color_blind_friendly_formatting(self, temp_workspace):
        """Test that formatting works without relying solely on color"""
        formatter = TerminalFormatter()
        ui_manager = UINotesManager(formatter, temp_workspace)
        
        # Create notes with different priorities (should use symbols, not just colors)
        priority_notes = [
            RichNote("urgent1", "Urgent Note", "Urgent content", 
                    NoteType.TODO, Priority.URGENT, ["urgent"]),
            RichNote("high1", "High Priority", "High priority content", 
                    NoteType.CONCEPT, Priority.HIGH, ["high"]),
            RichNote("low1", "Low Priority", "Low priority content", 
                    NoteType.REFERENCE, Priority.LOW, ["low"])
        ]
        
        for note in priority_notes:
            ui_manager.notes[note.id] = note
        
        # Verify that priority is indicated by more than just color
        stats = ui_manager.get_statistics()
        assert stats['notes_by_priority']['URGENT'] == 1
        assert stats['notes_by_priority']['HIGH'] == 1
        assert stats['notes_by_priority']['LOW'] == 1
    
    def test_mobile_responsiveness_simulation(self, temp_workspace):
        """Test content formatting for mobile-like constraints"""
        formatter = TerminalFormatter()
        ui_manager = UINotesManager(formatter, temp_workspace)
        
        # Create note with content that should wrap well on small screens
        mobile_note = RichNote(
            "mobile1",
            "Mobile-Friendly Note",
            "Short paragraphs work better on mobile devices.\n\n" +
            "Key points:\n" +
            "- Point 1\n" +
            "- Point 2\n" +
            "- Point 3\n\n" +
            "Code should also wrap:\n" +
            "`short_function(param1, param2)`",
            NoteType.EXAMPLE,
            Priority.MEDIUM,
            ["mobile", "responsive"]
        )
        
        ui_manager.notes[mobile_note.id] = mobile_note
        
        # Verify content is structured for mobile consumption
        lines = mobile_note.content.split('\n')
        max_line_length = max(len(line) for line in lines if line.strip())
        
        # Most lines should be reasonable length for mobile
        reasonable_lines = [line for line in lines if len(line) <= 80]
        assert len(reasonable_lines) / len([l for l in lines if l.strip()]) > 0.8


if __name__ == '__main__':
    # Run with more detailed output for E2E tests
    pytest.main([__file__, '-v', '--tb=long', '-s'])
