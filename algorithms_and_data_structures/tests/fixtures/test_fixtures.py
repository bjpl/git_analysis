#!/usr/bin/env python3
"""
Test Fixtures and Mocking Utilities for Notes System
Reusable test data, mocks, and utility functions
"""

import pytest
import tempfile
import os
import json
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from typing import List, Dict, Any, Optional

# Import the classes under test
sys_path = Path(__file__).parent.parent.parent / "src"
import sys
sys.path.insert(0, str(sys_path))

from notes_manager import NotesManager
from ui.notes import NotesManager as UINotesManager, RichNote, NoteType, Priority
from ui.formatter import TerminalFormatter


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest.fixture
def temp_db():
    """Create temporary database file for testing"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def temp_notes_dir():
    """Create temporary notes directory for UI testing"""
    import tempfile
    import shutil
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def populated_db(temp_db):
    """Database populated with comprehensive test data"""
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        
        # Create all necessary tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY,
                title TEXT,
                module_name TEXT,
                content TEXT,
                difficulty TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress (
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
        
        # Insert test users
        cursor.execute("INSERT INTO users (id, name, email) VALUES (1, 'Test User 1', 'user1@test.com')")
        cursor.execute("INSERT INTO users (id, name, email) VALUES (2, 'Test User 2', 'user2@test.com')")
        cursor.execute("INSERT INTO users (id, name, email) VALUES (3, 'Test User 3', 'user3@test.com')")
        
        # Insert test lessons
        lessons_data = [
            (101, 'Arrays: Introduction', 'Data Structures', 'Array basics...', 'Beginner'),
            (102, 'Arrays: Operations', 'Data Structures', 'Array operations...', 'Beginner'),
            (201, 'Binary Search: Algorithm', 'Algorithms', 'Binary search...', 'Intermediate'),
            (202, 'Linear Search: Implementation', 'Algorithms', 'Linear search...', 'Beginner'),
            (301, 'Quick Sort: Divide & Conquer', 'Sorting', 'Quick sort...', 'Advanced'),
            (302, 'Merge Sort: Stable Sorting', 'Sorting', 'Merge sort...', 'Intermediate'),
            (401, 'Binary Trees: Structure', 'Trees', 'Binary trees...', 'Intermediate'),
            (402, 'BST: Search Operations', 'Trees', 'Binary search trees...', 'Advanced')
        ]
        
        cursor.executemany("""
            INSERT INTO lessons (id, title, module_name, content, difficulty)
            VALUES (?, ?, ?, ?, ?)
        """, lessons_data)
        
        # Insert test progress data
        progress_data = [
            (1, 101, 1, 95, 1800, 'Completed arrays intro'),
            (1, 102, 1, 88, 1500, None),
            (1, 201, 0, 0, 900, 'Working on binary search'),
            (2, 101, 1, 92, 2100, 'Arrays completed'),
            (2, 201, 1, 85, 2400, None),
            (3, 301, 0, 0, 300, 'Just started sorting')
        ]
        
        cursor.executemany("""
            INSERT INTO progress (user_id, lesson_id, completed, score, time_spent, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, progress_data)
        
        conn.commit()
    
    return temp_db


# =============================================================================
# Notes Manager Fixtures
# =============================================================================

@pytest.fixture
def notes_manager(temp_db):
    """Basic NotesManager instance"""
    return NotesManager(temp_db)


@pytest.fixture
def populated_notes_manager(populated_db):
    """NotesManager with populated database"""
    manager = NotesManager(populated_db)
    
    # Add test notes
    test_notes = [
        (1, 101, "Arrays store elements in contiguous memory", "Data Structures", "Arrays - Memory", ["memory", "contiguous", "basic"]),
        (1, 102, "Array indexing provides O(1) access", "Data Structures", "Arrays - Performance", ["indexing", "O(1)", "performance"]),
        (1, 201, "Binary search requires sorted data", "Algorithms", "Binary Search - Requirements", ["binary-search", "sorted", "requirement"]),
        (1, 202, "Linear search works on unsorted data", "Algorithms", "Linear Search - Flexibility", ["linear-search", "unsorted", "simple"]),
        (2, 101, "Different perspective on arrays", "Data Structures", "Arrays - Alternative View", ["arrays", "perspective"]),
        (2, 201, "Binary search implementation in Python", "Algorithms", "Binary Search - Python", ["python", "implementation", "code"]),
        (3, 301, "Quick sort partitioning strategy", "Sorting", "Quick Sort - Strategy", ["quicksort", "partitioning", "strategy"])
    ]
    
    for user_id, lesson_id, content, module, topic, tags in test_notes:
        manager.save_note(user_id, lesson_id, content, module, topic, tags)
    
    # Mark some as favorites
    notes = manager.get_notes(1)
    if notes:
        manager.toggle_favorite(notes[0]['id'])
        if len(notes) > 2:
            manager.toggle_favorite(notes[2]['id'])
    
    return manager


@pytest.fixture
def ui_notes_manager(temp_notes_dir):
    """UI NotesManager instance"""
    formatter = TerminalFormatter()
    return UINotesManager(formatter, temp_notes_dir)


@pytest.fixture
def populated_ui_notes_manager(temp_notes_dir):
    """UI NotesManager with sample rich notes"""
    formatter = TerminalFormatter()
    manager = UINotesManager(formatter, temp_notes_dir)
    
    # Create sample rich notes
    sample_notes = [
        {
            'id': 'concept_arrays',
            'title': 'Array Data Structure Concept',
            'content': '**Arrays** are fundamental data structures that store elements in *contiguous memory*.\n\n# Key Properties:\n- Fixed size\n- O(1) random access\n- Cache-friendly\n\n```python\narr = [1, 2, 3, 4, 5]\nprint(arr[2])  # O(1) access\n```',
            'type': NoteType.CONCEPT,
            'priority': Priority.HIGH,
            'tags': ['arrays', 'data-structure', 'memory'],
            'topic': 'Data Structures'
        },
        {
            'id': 'example_binary_search',
            'title': 'Binary Search Implementation',
            'content': 'Python implementation of **binary search** algorithm:\n\n```python\ndef binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    \n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    \n    return -1\n```\n\n*Time Complexity*: O(log n)',
            'type': NoteType.EXAMPLE,
            'priority': Priority.MEDIUM,
            'tags': ['binary-search', 'algorithm', 'python', 'O(log n)'],
            'topic': 'Search Algorithms'
        },
        {
            'id': 'question_sorting',
            'title': 'Sorting Algorithm Question',
            'content': 'Which sorting algorithm should I use for **large datasets**?\n\n*Research needed:*\n- Quick sort vs Merge sort\n- In-place vs stable sorting\n- Worst-case performance\n\n**Follow up**: Test with different data patterns',
            'type': NoteType.QUESTION,
            'priority': Priority.HIGH,
            'tags': ['sorting', 'performance', 'research', 'comparison'],
            'topic': 'Sorting Algorithms'
        },
        {
            'id': 'insight_complexity',
            'title': 'Time Complexity Insight',
            'content': '💡 **Key insight**: *Preprocessing* can often improve query performance!\n\nExamples:\n- Sort array → Enable binary search\n- Build hash table → O(1) lookups\n- Create index → Faster database queries\n\nTradeoff: **Space vs Time**',
            'type': NoteType.INSIGHT,
            'priority': Priority.CRITICAL,
            'tags': ['complexity', 'preprocessing', 'optimization', 'tradeoffs'],
            'topic': 'Algorithm Analysis'
        },
        {
            'id': 'todo_practice',
            'title': 'Practice Problems Todo',
            'content': '☐ Complete 5 binary search problems\n☐ Implement quick sort from scratch\n☐ Solve tree traversal challenges\n☑ Review Big O notation\n\n**Priority**: Focus on search algorithms first',
            'type': NoteType.TODO,
            'priority': Priority.MEDIUM,
            'tags': ['practice', 'problems', 'todo', 'algorithms'],
            'topic': 'Study Plan'
        },
        {
            'id': 'reference_resources',
            'title': 'Algorithm Learning Resources',
            'content': '**Books:**\n- Introduction to Algorithms (CLRS)\n- Algorithm Design Manual (Skiena)\n\n**Online:**\n- [LeetCode](https://leetcode.com)\n- [HackerRank](https://hackerrank.com)\n- [Visualgo](https://visualgo.net)\n\n**YouTube Channels:**\n- MIT OpenCourseWare\n- Abdul Bari',
            'type': NoteType.REFERENCE,
            'priority': Priority.LOW,
            'tags': ['resources', 'books', 'online', 'references'],
            'topic': 'Learning Resources'
        }
    ]
    
    for note_data in sample_notes:
        note = RichNote(
            note_data['id'], note_data['title'], note_data['content'],
            note_data['type'], note_data['priority'], note_data['tags']
        )
        note.topic = note_data['topic']
        
        manager.notes[note.id] = note
        manager._update_indices(note)
    
    return manager


# =============================================================================
# Mock Objects
# =============================================================================

class MockCLI:
    """Mock CLI instance for testing integration"""
    def __init__(self):
        self.current_user_id = 1
        self.current_lesson_id = 101
        self.current_module = "Algorithms"
        self.commands = {}
        self.history = []
    
    def execute_command(self, command, args=None):
        """Mock command execution"""
        self.history.append((command, args))
        if command in self.commands:
            return self.commands[command](args or {})
        return f"Mock executed: {command}"


class MockFormatter:
    """Mock formatter for testing UI components"""
    def __init__(self):
        self.calls = []
    
    def header(self, text, level=1, style=None):
        self.calls.append(('header', text, level, style))
        return f"HEADER({level}): {text}"
    
    def box(self, content, title=None, style=None, color=None):
        self.calls.append(('box', content, title, style, color))
        return f"BOX: {title or 'untitled'}\n{content}"
    
    def success(self, message):
        self.calls.append(('success', message))
        return f"SUCCESS: {message}"
    
    def error(self, message):
        self.calls.append(('error', message))
        return f"ERROR: {message}"
    
    def warning(self, message):
        self.calls.append(('warning', message))
        return f"WARNING: {message}"
    
    def info(self, message):
        self.calls.append(('info', message))
        return f"INFO: {message}"
    
    def _colorize(self, text, color):
        return f"COLOR({color}): {text}"


class MockDatabase:
    """Mock database for testing without actual SQLite"""
    def __init__(self):
        self.tables = {}
        self.last_insert_id = 0
        self.executed_queries = []
    
    def execute(self, query, params=None):
        self.executed_queries.append((query, params or []))
        
        # Mock INSERT behavior
        if query.strip().upper().startswith('INSERT'):
            self.last_insert_id += 1
            return MockCursor(lastrowid=self.last_insert_id)
        
        # Mock SELECT behavior
        if query.strip().upper().startswith('SELECT'):
            return MockCursor(fetchall_result=self._mock_select_result(query, params))
        
        # Mock other operations
        return MockCursor()
    
    def _mock_select_result(self, query, params):
        """Generate mock results for SELECT queries"""
        if 'notes' in query.lower():
            return [
                (1, 1, 101, "Mock Module", "Mock Topic", "Mock content", 
                 '["mock", "test"]', '2025-01-01 12:00:00', '2025-01-01 12:00:00', 0)
            ]
        return []


class MockCursor:
    """Mock database cursor"""
    def __init__(self, fetchall_result=None, lastrowid=None, rowcount=1):
        self._fetchall_result = fetchall_result or []
        self.lastrowid = lastrowid
        self.rowcount = rowcount
        self.description = [
            ('id',), ('user_id',), ('lesson_id',), ('module_name',), 
            ('topic',), ('content',), ('tags',), ('created_at',), 
            ('updated_at',), ('is_favorite',)
        ]
    
    def fetchall(self):
        return self._fetchall_result
    
    def fetchone(self):
        if self._fetchall_result:
            return self._fetchall_result[0]
        return None


# =============================================================================
# Fixture Factories
# =============================================================================

def create_test_note_data(count=5, user_id=1, base_lesson_id=100):
    """Factory function to create test note data"""
    modules = ["Algorithms", "Data Structures", "Mathematics", "Programming"]
    topics = ["Introduction", "Implementation", "Analysis", "Optimization"]
    tag_sets = [
        ["basic", "intro"],
        ["intermediate", "implementation"],
        ["advanced", "analysis"],
        ["expert", "optimization"],
        ["general", "review"]
    ]
    
    notes = []
    for i in range(count):
        notes.append({
            'user_id': user_id,
            'lesson_id': base_lesson_id + i,
            'content': f"Test note {i+1} content with detailed information about the topic.",
            'module': modules[i % len(modules)],
            'topic': f"{topics[i % len(topics)]} {i+1}",
            'tags': tag_sets[i % len(tag_sets)]
        })
    
    return notes


def create_rich_notes_data(count=3):
    """Factory function to create rich note test data"""
    note_types = [NoteType.CONCEPT, NoteType.EXAMPLE, NoteType.QUESTION, NoteType.INSIGHT, NoteType.TODO, NoteType.REFERENCE]
    priorities = [Priority.LOW, Priority.MEDIUM, Priority.HIGH, Priority.CRITICAL, Priority.URGENT]
    
    contents = [
        "**Bold text** with *emphasis* and `code snippets`\n\n# Header\n- List item",
        "```python\ndef example():\n    return 'formatted code'\n```\n\nExample with code formatting.",
        "Question about **algorithms**: How do we optimize?\n\n*Research needed*:",
        "💡 Insight: Always consider the *time-space tradeoff* in algorithms.",
        "☐ Task 1\n☑ Completed task\n☐ Another task\n\n**Priority**: High",
        "Reference material:\n- Link 1\n- Link 2\n\n[External Resource](https://example.com)"
    ]
    
    notes = []
    for i in range(count):
        notes.append({
            'id': f"rich_note_{i}",
            'title': f"Rich Note {i+1}",
            'content': contents[i % len(contents)],
            'type': note_types[i % len(note_types)],
            'priority': priorities[i % len(priorities)],
            'tags': [f"rich{i}", "test", "formatted"],
            'topic': f"Test Topic {i+1}"
        })
    
    return notes


# =============================================================================
# Utility Functions
# =============================================================================

def assert_note_equality(note1, note2, ignore_fields=None):
    """Assert that two notes are equal, ignoring specified fields"""
    ignore_fields = ignore_fields or ['created_at', 'updated_at']
    
    for key in note1.keys():
        if key not in ignore_fields:
            assert note1[key] == note2[key], f"Field {key} differs: {note1[key]} != {note2[key]}"


def create_performance_dataset(manager, size=1000, user_id=1):
    """Create large dataset for performance testing"""
    modules = ["Module" + str(i) for i in range(10)]
    topics = ["Topic" + str(i) for i in range(20)]
    tags = ["tag" + str(i) for i in range(15)]
    
    note_ids = []
    for i in range(size):
        content = f"Performance test note {i} " + "content " * (i % 10 + 1)
        module = modules[i % len(modules)]
        topic = topics[i % len(topics)]
        note_tags = [tags[j % len(tags)] for j in range(i % 5 + 1)]
        
        note_id = manager.save_note(user_id, i % 100 + 100, content, module, topic, note_tags)
        note_ids.append(note_id)
    
    return note_ids


def measure_execution_time(func, *args, **kwargs):
    """Measure execution time of a function"""
    start_time = time.time()
    result = func(*args, **kwargs)
    execution_time = time.time() - start_time
    return result, execution_time


def create_mock_console():
    """Create mock console for testing output"""
    mock_console = Mock()
    mock_console.print = Mock()
    return mock_console


# =============================================================================
# Pytest Fixtures Registration
# =============================================================================

@pytest.fixture
def mock_cli():
    """Mock CLI instance"""
    return MockCLI()


@pytest.fixture
def mock_formatter():
    """Mock formatter instance"""
    return MockFormatter()


@pytest.fixture
def mock_database():
    """Mock database instance"""
    return MockDatabase()


@pytest.fixture
def mock_console():
    """Mock console for output testing"""
    return create_mock_console()


@pytest.fixture
def performance_notes_manager(temp_db):
    """NotesManager with performance test dataset"""
    manager = NotesManager(temp_db)
    create_performance_dataset(manager, size=100)  # Smaller size for faster tests
    return manager


@pytest.fixture
def sample_notes_data():
    """Sample notes data for testing"""
    return create_test_note_data(10)


@pytest.fixture
def sample_rich_notes_data():
    """Sample rich notes data for testing"""
    return create_rich_notes_data(6)


# =============================================================================
# Context Managers for Testing
# =============================================================================

class TemporaryNoteEnvironment:
    """Context manager for temporary note testing environment"""
    def __init__(self, with_ui=False, with_data=True):
        self.with_ui = with_ui
        self.with_data = with_data
        self.db_path = None
        self.notes_dir = None
        self.manager = None
        self.ui_manager = None
    
    def __enter__(self):
        # Create temporary database
        fd, self.db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        self.manager = NotesManager(self.db_path)
        
        if self.with_ui:
            import tempfile
            self.notes_dir = tempfile.mkdtemp()
            formatter = TerminalFormatter()
            self.ui_manager = UINotesManager(formatter, self.notes_dir)
        
        if self.with_data:
            self._populate_test_data()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup
        if self.db_path and os.path.exists(self.db_path):
            os.unlink(self.db_path)
        
        if self.notes_dir:
            import shutil
            shutil.rmtree(self.notes_dir, ignore_errors=True)
    
    def _populate_test_data(self):
        """Populate with test data"""
        test_notes = create_test_note_data(5)
        for note_data in test_notes:
            self.manager.save_note(**note_data)
        
        if self.ui_manager:
            rich_notes = create_rich_notes_data(3)
            for note_data in rich_notes:
                note = RichNote(
                    note_data['id'], note_data['title'], note_data['content'],
                    note_data['type'], note_data['priority'], note_data['tags']
                )
                note.topic = note_data['topic']
                self.ui_manager.notes[note.id] = note
                self.ui_manager._update_indices(note)


# =============================================================================
# Parameterized Test Data
# =============================================================================

# Database scenarios for parameterized tests
DATABASE_SCENARIOS = [
    pytest.param("empty", marks=pytest.mark.basic),
    pytest.param("small", marks=pytest.mark.basic),
    pytest.param("medium", marks=pytest.mark.extended),
    pytest.param("large", marks=pytest.mark.performance)
]

# Search test cases
SEARCH_TEST_CASES = [
    ("algorithm", "content", 2),
    ("Algorithm", "content", 2),  # Case insensitive
    ("ALGORITHM", "content", 2),  # Case insensitive
    ("nonexistent", "content", 0),
    ("tag1", "tags", 1),
    ("Introduction", "title", 1),
    ("test", "all", 5)
]

# Performance test parameters
PERFORMANCE_PARAMS = [
    pytest.param(10, marks=pytest.mark.basic),
    pytest.param(100, marks=pytest.mark.extended),
    pytest.param(1000, marks=pytest.mark.performance),
    pytest.param(5000, marks=pytest.mark.stress)
]


if __name__ == '__main__':
    # Demonstrate fixture usage
    with TemporaryNoteEnvironment(with_ui=True) as env:
        print(f"Created environment with {len(env.manager.get_notes(1))} notes")
        if env.ui_manager:
            print(f"UI manager has {len(env.ui_manager.notes)} rich notes")
