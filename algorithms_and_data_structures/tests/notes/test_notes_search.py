#!/usr/bin/env python3
"""
Unit Tests for Notes Search Functionality
Testing search algorithms, indexing, and performance
"""

import pytest
import tempfile
import os
import time
from pathlib import Path
from unittest.mock import Mock, patch

# Import the classes under test
sys_path = Path(__file__).parent.parent.parent / "src"
import sys
sys.path.insert(0, str(sys_path))

from notes_manager import NotesManager
from ui.notes import NotesManager as UINotesManager, RichNote, NoteType, Priority
from ui.formatter import TerminalFormatter


class TestNotesSearch:
    """Test suite for notes search functionality"""
    
    @pytest.fixture
    def temp_db(self):
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    @pytest.fixture
    def notes_manager(self, temp_db):
        return NotesManager(temp_db)
    
    @pytest.fixture
    def sample_notes_data(self):
        """Sample notes data for search testing"""
        return [
            {
                'user_id': 1, 'lesson_id': 101, 'content': 'Binary search algorithm implementation',
                'module': 'Algorithms', 'topic': 'Binary Search', 'tags': ['algorithm', 'search', 'O(log n)']
            },
            {
                'user_id': 1, 'lesson_id': 102, 'content': 'Linear search is simpler but less efficient',
                'module': 'Algorithms', 'topic': 'Linear Search', 'tags': ['algorithm', 'search', 'O(n)']
            },
            {
                'user_id': 1, 'lesson_id': 201, 'content': 'Arrays are contiguous memory structures',
                'module': 'Data Structures', 'topic': 'Arrays', 'tags': ['array', 'memory', 'basic']
            },
            {
                'user_id': 1, 'lesson_id': 202, 'content': 'Linked lists provide dynamic memory allocation',
                'module': 'Data Structures', 'topic': 'Linked Lists', 'tags': ['linked-list', 'memory', 'dynamic']
            },
            {
                'user_id': 1, 'lesson_id': 301, 'content': 'Quick sort performance analysis and optimization',
                'module': 'Sorting', 'topic': 'Quick Sort', 'tags': ['sorting', 'performance', 'divide-conquer']
            },
            {
                'user_id': 1, 'lesson_id': 302, 'content': 'Merge sort is stable and predictable',
                'module': 'Sorting', 'topic': 'Merge Sort', 'tags': ['sorting', 'stable', 'O(n log n)']
            },
            {
                'user_id': 2, 'lesson_id': 101, 'content': 'Different user binary search notes',
                'module': 'Algorithms', 'topic': 'Binary Search', 'tags': ['algorithm', 'user2']
            }
        ]
    
    @pytest.fixture
    def populated_notes_manager(self, notes_manager, sample_notes_data):
        """Notes manager populated with test data"""
        for note_data in sample_notes_data:
            notes_manager.save_note(
                note_data['user_id'], note_data['lesson_id'], note_data['content'],
                note_data['module'], note_data['topic'], note_data['tags']
            )
        return notes_manager
    
    def test_search_by_content_exact_match(self, populated_notes_manager):
        """Test exact content matching"""
        results = populated_notes_manager.get_notes(1, search_term="Binary search algorithm")
        
        assert len(results) == 1
        assert "Binary search algorithm implementation" in results[0]['content']
    
    def test_search_by_content_partial_match(self, populated_notes_manager):
        """Test partial content matching"""
        results = populated_notes_manager.get_notes(1, search_term="search")
        
        # Should match both binary and linear search notes
        assert len(results) == 2
        contents = [note['content'] for note in results]
        assert any("Binary search" in content for content in contents)
        assert any("Linear search" in content for content in contents)
    
    def test_search_case_insensitive(self, populated_notes_manager):
        """Test case-insensitive search"""
        # Test various case combinations
        test_cases = ["BINARY", "binary", "Binary", "bInArY"]
        
        for search_term in test_cases:
            results = populated_notes_manager.get_notes(1, search_term=search_term)
            assert len(results) == 1
            assert "Binary search" in results[0]['content']
    
    def test_search_by_tags(self, populated_notes_manager):
        """Test searching by tags"""
        results = populated_notes_manager.get_notes(1, search_term="algorithm")
        
        # Should match notes tagged with 'algorithm'
        assert len(results) == 2
        for note in results:
            assert 'algorithm' in note['tags']
    
    def test_search_by_topic(self, populated_notes_manager):
        """Test searching by topic"""
        results = populated_notes_manager.get_notes(1, search_term="Quick Sort")
        
        assert len(results) == 1
        assert results[0]['topic'] == "Quick Sort"
    
    def test_search_by_module_filter(self, populated_notes_manager):
        """Test filtering by module"""
        results = populated_notes_manager.get_notes(1, module_name="Algorithms")
        
        assert len(results) == 2
        for note in results:
            assert note['module_name'] == "Algorithms"
    
    def test_search_by_lesson_filter(self, populated_notes_manager):
        """Test filtering by lesson ID"""
        results = populated_notes_manager.get_notes(1, lesson_id=201)
        
        assert len(results) == 1
        assert results[0]['lesson_id'] == 201
        assert "Arrays" in results[0]['content']
    
    def test_search_multiple_filters(self, populated_notes_manager):
        """Test combining multiple search filters"""
        results = populated_notes_manager.get_notes(
            1, module_name="Sorting", search_term="performance"
        )
        
        assert len(results) == 1
        assert results[0]['module_name'] == "Sorting"
        assert "performance" in results[0]['content']
    
    def test_search_no_results(self, populated_notes_manager):
        """Test search with no matching results"""
        results = populated_notes_manager.get_notes(1, search_term="nonexistent")
        
        assert len(results) == 0
        assert isinstance(results, list)
    
    def test_search_user_isolation(self, populated_notes_manager):
        """Test that search results are isolated by user"""
        # Search user 1's notes
        user1_results = populated_notes_manager.get_notes(1, search_term="binary")
        
        # Search user 2's notes  
        user2_results = populated_notes_manager.get_notes(2, search_term="binary")
        
        assert len(user1_results) == 1
        assert len(user2_results) == 1
        assert user1_results[0]['user_id'] == 1
        assert user2_results[0]['user_id'] == 2
        assert user1_results[0]['content'] != user2_results[0]['content']
    
    def test_search_special_characters(self, populated_notes_manager):
        """Test search with special characters"""
        # Add note with special characters
        populated_notes_manager.save_note(
            1, None, "C++ algorithm with O(n^2) complexity", 
            "Languages", "C++", ["c++", "complexity"]
        )
        
        # Search for special characters
        results = populated_notes_manager.get_notes(1, search_term="C++")
        assert len(results) == 1
        
        results = populated_notes_manager.get_notes(1, search_term="O(n^2)")
        assert len(results) == 1
    
    def test_search_unicode_content(self, populated_notes_manager):
        """Test search with unicode characters"""
        # Add note with unicode content
        unicode_content = "Algorithm notes in 中文 and العربية"
        populated_notes_manager.save_note(
            1, None, unicode_content, "Unicode", "International", ["中文"]
        )
        
        # Search for unicode text
        results = populated_notes_manager.get_notes(1, search_term="中文")
        assert len(results) == 1
        assert "中文" in results[0]['content']
    
    def test_search_performance_large_dataset(self, notes_manager):
        """Test search performance with large number of notes"""
        # Create large dataset
        num_notes = 1000
        start_time = time.time()
        
        for i in range(num_notes):
            content = f"Note {i} about algorithms and data structures performance"
            notes_manager.save_note(
                1, None, content, f"Module{i%10}", f"Topic{i}", 
                [f"tag{i%5}", "performance"]
            )
        
        creation_time = time.time() - start_time
        
        # Test search performance
        search_start = time.time()
        results = notes_manager.get_notes(1, search_term="performance")
        search_time = time.time() - search_start
        
        # Verify results
        assert len(results) == num_notes
        
        # Performance assertions (these may need adjustment based on system)
        assert search_time < 1.0  # Search should complete in under 1 second
        print(f"Created {num_notes} notes in {creation_time:.2f}s")
        print(f"Searched {num_notes} notes in {search_time:.4f}s")
    
    def test_search_result_ordering(self, populated_notes_manager):
        """Test that search results are properly ordered"""
        # Add notes with timestamps
        import time
        
        populated_notes_manager.save_note(1, None, "First search result", "M", "T")
        time.sleep(0.1)
        populated_notes_manager.save_note(1, None, "Second search result", "M", "T")
        time.sleep(0.1)
        populated_notes_manager.save_note(1, None, "Third search result", "M", "T")
        
        results = populated_notes_manager.get_notes(1, search_term="search result")
        
        # Should be ordered by creation time (newest first)
        assert len(results) == 3
        assert results[0]['content'] == "Third search result"
        assert results[1]['content'] == "Second search result"
        assert results[2]['content'] == "First search result"
    
    def test_search_empty_database(self, notes_manager):
        """Test search on empty database"""
        results = notes_manager.get_notes(1, search_term="anything")
        
        assert len(results) == 0
        assert isinstance(results, list)
    
    def test_search_sql_injection_protection(self, populated_notes_manager):
        """Test protection against SQL injection in search"""
        # Attempt various SQL injection patterns
        injection_attempts = [
            "'; DROP TABLE notes; --",
            "' OR '1'='1",
            "'; UPDATE notes SET content='hacked'; --",
            "' UNION SELECT * FROM notes --"
        ]
        
        for injection in injection_attempts:
            results = populated_notes_manager.get_notes(1, search_term=injection)
            
            # Should return empty results (no matches) without causing error
            assert isinstance(results, list)
            
            # Verify database integrity by checking normal search still works
            normal_results = populated_notes_manager.get_notes(1, search_term="search")
            assert len(normal_results) > 0


class TestUINotesSearch:
    """Test suite for UI notes search functionality"""
    
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
    def sample_rich_notes(self, ui_notes_manager):
        """Create sample rich notes for testing"""
        notes = [
            RichNote(
                "note1", "Binary Search Implementation", 
                "Implementing **binary search** in Python\n```python\ndef binary_search(arr, target):\n    # Implementation\n```",
                NoteType.EXAMPLE, Priority.HIGH, ["algorithm", "python", "search"]
            ),
            RichNote(
                "note2", "Data Structure Concepts",
                "Understanding *arrays* and their properties\n- Random access\n- Fixed size",
                NoteType.CONCEPT, Priority.MEDIUM, ["data-structure", "array", "basics"]
            ),
            RichNote(
                "note3", "Performance Question",
                "Why is binary search **O(log n)**? Need to research more.",
                NoteType.QUESTION, Priority.HIGH, ["performance", "complexity", "research"]
            ),
            RichNote(
                "note4", "Optimization Insight",
                "Discovered that *preprocessing* can improve search performance significantly.",
                NoteType.INSIGHT, Priority.CRITICAL, ["optimization", "preprocessing", "performance"]
            )
        ]
        
        for note in notes:
            ui_notes_manager.notes[note.id] = note
            ui_notes_manager._update_indices(note)
        
        return notes
    
    def test_search_by_title(self, ui_notes_manager, sample_rich_notes):
        """Test searching by note title"""
        results = ui_notes_manager.search_notes("Binary", search_type="title")
        
        assert len(results) == 1
        assert results[0].title == "Binary Search Implementation"
    
    def test_search_by_content_formatted(self, ui_notes_manager, sample_rich_notes):
        """Test searching in formatted content"""
        results = ui_notes_manager.search_notes("python", search_type="content")
        
        assert len(results) == 1
        assert "Python" in results[0].content
    
    def test_search_by_tags_specific(self, ui_notes_manager, sample_rich_notes):
        """Test searching by specific tags"""
        results = ui_notes_manager.search_notes("performance", search_type="tags")
        
        assert len(results) == 2  # note3 and note4 have performance tag
        for note in results:
            assert "performance" in note.tags
    
    def test_search_all_fields(self, ui_notes_manager, sample_rich_notes):
        """Test searching across all fields"""
        results = ui_notes_manager.search_notes("array", search_type="all")
        
        # Should find note2 (has 'array' in content and tags)
        assert len(results) == 1
        assert results[0].id == "note2"
    
    def test_search_result_priority_ordering(self, ui_notes_manager, sample_rich_notes):
        """Test that search results are ordered by priority and recency"""
        results = ui_notes_manager.search_notes("performance", search_type="all")
        
        # Should be ordered by priority (higher first), then by timestamp
        assert len(results) == 2
        priorities = [note.priority.value for note in results]
        
        # Should be in descending priority order
        assert priorities == sorted(priorities, reverse=True)
    
    def test_search_by_note_type(self, ui_notes_manager, sample_rich_notes):
        """Test filtering by note type (not direct search but relevant)"""
        # Get all concept notes
        concept_notes = [note for note in ui_notes_manager.notes.values() 
                        if note.note_type == NoteType.CONCEPT]
        
        assert len(concept_notes) == 1
        assert concept_notes[0].title == "Data Structure Concepts"
    
    def test_search_by_topic_grouping(self, ui_notes_manager, sample_rich_notes):
        """Test searching within topic groups"""
        # Set topics for some notes
        ui_notes_manager.notes["note1"].topic = "algorithms"
        ui_notes_manager.notes["note3"].topic = "algorithms"
        ui_notes_manager._update_indices(ui_notes_manager.notes["note1"])
        ui_notes_manager._update_indices(ui_notes_manager.notes["note3"])
        
        topic_notes = ui_notes_manager.get_notes_by_topic("algorithms")
        
        assert len(topic_notes) == 2
        note_ids = {note.id for note in topic_notes}
        assert note_ids == {"note1", "note3"}
    
    def test_search_by_tag_grouping(self, ui_notes_manager, sample_rich_notes):
        """Test searching by tag groups"""
        performance_notes = ui_notes_manager.get_notes_by_tag("performance")
        
        assert len(performance_notes) == 2
        for note in performance_notes:
            assert "performance" in note.tags
    
    def test_search_empty_query(self, ui_notes_manager, sample_rich_notes):
        """Test search with empty query"""
        results = ui_notes_manager.search_notes("", search_type="all")
        
        # Empty search should return no results or all results depending on implementation
        assert isinstance(results, list)
    
    def test_search_whitespace_query(self, ui_notes_manager, sample_rich_notes):
        """Test search with whitespace-only query"""
        results = ui_notes_manager.search_notes("   ", search_type="all")
        
        # Whitespace-only search should return no results
        assert len(results) == 0
    
    def test_search_case_insensitive_ui(self, ui_notes_manager, sample_rich_notes):
        """Test case-insensitive search in UI notes"""
        test_cases = ["BINARY", "binary", "Binary", "bInArY"]
        
        for search_term in test_cases:
            results = ui_notes_manager.search_notes(search_term, search_type="all")
            assert len(results) == 1
            assert "Binary" in results[0].title
    
    def test_search_indices_update(self, ui_notes_manager):
        """Test that search indices are properly updated"""
        # Add a new note
        new_note = RichNote(
            "dynamic1", "Dynamic Note", "Dynamically added content",
            NoteType.TODO, Priority.LOW, ["dynamic", "test"]
        )
        
        ui_notes_manager.notes[new_note.id] = new_note
        ui_notes_manager._update_indices(new_note)
        
        # Search should find the new note
        results = ui_notes_manager.search_notes("dynamic", search_type="all")
        assert len(results) == 1
        assert results[0].id == "dynamic1"
        
        # Check indices are updated
        assert "dynamic" in ui_notes_manager.tags_index
        assert "dynamic1" in ui_notes_manager.tags_index["dynamic"]
    
    def test_search_performance_ui_notes(self, ui_notes_manager):
        """Test search performance with many UI notes"""
        # Create many notes
        num_notes = 500
        for i in range(num_notes):
            note = RichNote(
                f"perf_{i}", f"Performance Note {i}",
                f"Content about performance testing #{i} with **formatting**",
                NoteType.CONCEPT, Priority.MEDIUM, ["performance", f"test{i}"]
            )
            ui_notes_manager.notes[note.id] = note
            ui_notes_manager._update_indices(note)
        
        # Test search performance
        start_time = time.time()
        results = ui_notes_manager.search_notes("performance", search_type="all")
        search_time = time.time() - start_time
        
        # Verify results and performance
        assert len(results) == num_notes
        assert search_time < 0.5  # Should complete in under 0.5 seconds
        print(f"UI search of {num_notes} notes completed in {search_time:.4f}s")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
