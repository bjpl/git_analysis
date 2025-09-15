#!/usr/bin/env python3
"""
Comprehensive tests for new UI components and interactive features.

This test suite covers:
- Interactive session management
- Note-taking functionality
- Progress tracking and visualization
- Menu navigation and user input
- Session state management
- Export and import functionality
- Achievement system
- Real-time UI updates
"""

import pytest
import asyncio
import json
import tempfile
import time
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock, call
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Import modules under test
try:
    from src.ui.interactive import (
        InteractiveSession, LearningMode, LessonNote, SessionProgress
    )
    from src.ui.formatter import TerminalFormatter, Color, Theme
except ImportError:
    pytest.skip("UI interactive modules not available", allow_module_level=True)


class TestInteractiveSessionCore:
    """Test core interactive session functionality"""
    
    @pytest.fixture
    def mock_cli_engine(self):
        """Mock CLI engine with curriculum"""
        engine = Mock()
        engine.curriculum = Mock()
        engine.curriculum.topics = {
            "Arrays": {"difficulty": "easy", "duration": 30},
            "Linked Lists": {"difficulty": "medium", "duration": 45},
            "Trees": {"difficulty": "hard", "duration": 60},
            "Graphs": {"difficulty": "hard", "duration": 90},
            "Dynamic Programming": {"difficulty": "expert", "duration": 120}
        }
        return engine
    
    @pytest.fixture
    def session(self, mock_cli_engine, tmp_path):
        """Create interactive session for testing"""
        with patch('pathlib.Path.mkdir'):
            session = InteractiveSession(cli_engine=mock_cli_engine)
            session.notes_dir = tmp_path / "notes"
            session.progress_file = tmp_path / "progress.json"
            session.notes_dir.mkdir(exist_ok=True)
        return session
    
    @pytest.fixture
    def sample_notes(self):
        """Sample notes for testing"""
        return [
            LessonNote(
                timestamp="2024-01-15T10:30:00",
                topic="Arrays",
                content="Arrays are contiguous memory locations",
                tags=["basics", "memory"],
                importance=4
            ),
            LessonNote(
                timestamp="2024-01-15T10:35:00",
                topic="Arrays",
                content="Time complexity for access is O(1)",
                tags=["complexity", "performance"],
                importance=5
            ),
            LessonNote(
                timestamp="2024-01-15T11:00:00",
                topic="Linked Lists",
                content="Dynamic size allocation",
                tags=["memory", "dynamic"],
                importance=3
            )
        ]
    
    def test_session_initialization(self, session):
        """Test session initialization"""
        assert session.mode == LearningMode.LESSON
        assert isinstance(session.progress, SessionProgress)
        assert len(session.notes) == 0
        assert session.current_topic == ""
        assert isinstance(session.session_start, datetime)
    
    def test_theme_configuration(self, session):
        """Test theme configuration"""
        if hasattr(session, 'theme'):
            assert isinstance(session.theme, Theme)
            assert session.formatter.theme == session.theme
    
    @pytest.mark.asyncio
    async def test_welcome_screen_display(self, session):
        """Test welcome screen display"""
        with patch('builtins.input', return_value=''), \
             patch('builtins.print') as mock_print, \
             patch.object(session, 'clear_screen'):
            
            await session.show_welcome()
            
            # Should have printed welcome content
            assert mock_print.called
            # Check for key welcome elements
            printed_content = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "ALGORITHMS PROFESSOR" in printed_content or "Welcome" in printed_content
    
    @pytest.mark.asyncio
    async def test_main_menu_display(self, session):
        """Test main menu display and navigation"""
        with patch('builtins.input', return_value='1'), \
             patch('builtins.print') as mock_print, \
             patch.object(session, 'clear_screen'):
            
            choice = await session.show_main_menu()
            
            assert choice == '1'
            assert mock_print.called
            
            # Check menu options are displayed
            printed_content = ' '.join(str(call) for call in mock_print.call_args_list)
            expected_options = ["Learning Session", "Practice", "Quiz", "Notes", "Progress"]
            # At least some menu options should be present
            assert any(option in printed_content for option in expected_options)


class TestNoteTakingFunctionality:
    """Test note-taking functionality"""
    
    @pytest.fixture
    def session(self, tmp_path):
        with patch('pathlib.Path.mkdir'):
            session = InteractiveSession()
            session.notes_dir = tmp_path / "notes"
            session.progress_file = tmp_path / "progress.json"
            session.notes_dir.mkdir(exist_ok=True)
        return session
    
    @pytest.mark.asyncio
    async def test_take_note_basic(self, session):
        """Test basic note-taking functionality"""
        topic = "Arrays"
        note_content = "Test note content"
        
        with patch('builtins.input', side_effect=[note_content, 'basics,memory', '4']), \
             patch('builtins.print'):
            
            initial_count = len(session.notes)
            await session.take_note(topic)
            
            assert len(session.notes) == initial_count + 1
            note = session.notes[-1]
            assert note.topic == topic
            assert note.content == note_content
            assert note.tags == ['basics', 'memory']
            assert note.importance == 4
    
    @pytest.mark.asyncio
    async def test_take_note_with_defaults(self, session):
        """Test note-taking with default values"""
        topic = "Trees"
        note_content = "Binary trees have at most two children"
        
        with patch('builtins.input', side_effect=[note_content, '', '']), \
             patch('builtins.print'):
            
            await session.take_note(topic)
            
            note = session.notes[-1]
            assert note.content == note_content
            assert note.tags == []
            assert note.importance == 3  # Default importance
    
    @pytest.mark.asyncio
    async def test_take_note_importance_validation(self, session):
        """Test note importance validation"""
        topic = "Graphs"
        note_content = "Graph traversal algorithms"
        
        # Test invalid importance gets clamped
        with patch('builtins.input', side_effect=[note_content, '', '10']), \
             patch('builtins.print'):
            
            await session.take_note(topic)
            
            note = session.notes[-1]
            assert note.importance == 5  # Should be clamped to max
        
        # Test negative importance gets clamped
        with patch('builtins.input', side_effect=[note_content, '', '-1']), \
             patch('builtins.print'):
            
            await session.take_note(topic)
            
            note = session.notes[-1]
            assert note.importance == 1  # Should be clamped to min
    
    @pytest.mark.asyncio
    async def test_take_note_invalid_importance(self, session):
        """Test note-taking with invalid importance input"""
        topic = "Dynamic Programming"
        note_content = "Memoization technique"
        
        with patch('builtins.input', side_effect=[note_content, '', 'invalid']), \
             patch('builtins.print'):
            
            await session.take_note(topic)
            
            note = session.notes[-1]
            assert note.importance == 3  # Should default to 3
    
    @pytest.mark.asyncio
    async def test_review_notes_empty(self, session):
        """Test reviewing notes when none exist"""
        with patch('builtins.input', return_value=''), \
             patch('builtins.print') as mock_print, \
             patch.object(session, 'clear_screen'):
            
            await session.review_notes()
            
            # Should display "no notes" message
            printed_content = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "No notes" in printed_content
    
    @pytest.mark.asyncio
    async def test_review_notes_with_content(self, session, sample_notes):
        """Test reviewing notes with content"""
        session.notes = sample_notes.copy()
        
        with patch('builtins.input', return_value='b'), \
             patch('builtins.print') as mock_print, \
             patch.object(session, 'clear_screen'):
            
            await session.review_notes()
            
            # Should display notes
            printed_content = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Arrays" in printed_content
            assert "contiguous memory" in printed_content
    
    @pytest.mark.asyncio
    async def test_review_notes_topic_filter(self, session, sample_notes):
        """Test reviewing notes with topic filter"""
        session.notes = sample_notes.copy()
        
        with patch('builtins.input', return_value='b'), \
             patch('builtins.print') as mock_print, \
             patch.object(session, 'clear_screen'):
            
            await session.review_notes(topic_filter="Arrays")
            
            # Should only show Arrays notes
            printed_content = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Arrays" in printed_content
            assert "Linked Lists" not in printed_content
    
    @pytest.mark.asyncio
    async def test_delete_note(self, session, sample_notes):
        """Test deleting a note"""
        session.notes = sample_notes.copy()
        initial_count = len(session.notes)
        
        with patch('builtins.input', side_effect=['d', '1']), \
             patch('builtins.print'), \
             patch.object(session, 'clear_screen'):
            
            await session.review_notes()
            
            # Should have one less note
            assert len(session.notes) == initial_count - 1
    
    @pytest.mark.asyncio
    async def test_delete_note_invalid_number(self, session, sample_notes):
        """Test deleting a note with invalid number"""
        session.notes = sample_notes.copy()
        initial_count = len(session.notes)
        
        with patch('builtins.input', side_effect=['d', 'invalid']), \
             patch('builtins.print'), \
             patch.object(session, 'clear_screen'):
            
            await session.review_notes()
            
            # Should not delete any notes
            assert len(session.notes) == initial_count


class TestProgressTracking:
    """Test progress tracking and visualization"""
    
    @pytest.fixture
    def session(self, tmp_path):
        with patch('pathlib.Path.mkdir'):
            session = InteractiveSession()
            session.notes_dir = tmp_path / "notes"
            session.progress_file = tmp_path / "progress.json"
            session.notes_dir.mkdir(exist_ok=True)
        return session
    
    def test_progress_initialization(self, session):
        """Test progress object initialization"""
        progress = session.progress
        assert progress.lessons_completed == 0
        assert progress.concepts_learned == []
        assert progress.notes_taken == 0
        assert progress.quiz_score == 0.0
        assert progress.time_spent_minutes == 0.0
        assert progress.achievements == []
    
    def test_calculate_progress_empty(self, session):
        """Test progress calculation with no progress"""
        progress = session.calculate_progress()
        assert progress >= 0
        assert progress <= 100
    
    def test_calculate_progress_with_data(self, session, sample_notes):
        """Test progress calculation with some data"""
        session.notes = sample_notes.copy()
        session.progress.notes_taken = len(sample_notes)
        session.progress.lessons_completed = 2
        session.progress.quiz_score = 85.0
        session.progress.time_spent_minutes = 60
        
        progress = session.calculate_progress()
        assert progress > 0
        assert progress <= 100
    
    @pytest.mark.asyncio
    async def test_view_progress_display(self, session, sample_notes):
        """Test progress display"""
        session.notes = sample_notes.copy()
        session.progress.notes_taken = len(sample_notes)
        session.progress.lessons_completed = 2
        session.progress.concepts_learned = ["Arrays", "Linked Lists"]
        
        with patch('builtins.input', return_value=''), \
             patch('builtins.print') as mock_print, \
             patch.object(session, 'clear_screen'):
            
            await session.view_progress()
            
            # Should display progress information
            printed_content = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Progress" in printed_content
            assert "Lessons Completed" in printed_content
            assert "Notes Taken" in printed_content
    
    def test_check_achievements_note_taker(self, session):
        """Test note taker achievement"""
        session.progress.notes_taken = 10
        
        with patch('builtins.print'):
            session.check_achievements()
        
        assert "Note Taker" in session.progress.achievements
    
    def test_check_achievements_dedicated_learner(self, session):
        """Test dedicated learner achievement"""
        session.progress.lessons_completed = 5
        
        with patch('builtins.print'):
            session.check_achievements()
        
        assert "Dedicated Learner" in session.progress.achievements
    
    def test_check_achievements_quiz_master(self, session):
        """Test quiz master achievement"""
        session.progress.quiz_score = 95.0
        
        with patch('builtins.print'):
            session.check_achievements()
        
        assert "Quiz Master" in session.progress.achievements
    
    def test_check_achievements_no_duplicates(self, session):
        """Test achievements are not duplicated"""
        session.progress.notes_taken = 15
        session.progress.achievements = ["Note Taker"]  # Already has it
        
        with patch('builtins.print'):
            session.check_achievements()
        
        # Should only have one instance
        achievement_count = session.progress.achievements.count("Note Taker")
        assert achievement_count == 1


class TestLessonMode:
    """Test lesson mode functionality"""
    
    @pytest.fixture
    def session(self, mock_cli_engine, tmp_path):
        with patch('pathlib.Path.mkdir'):
            session = InteractiveSession(cli_engine=mock_cli_engine)
            session.notes_dir = tmp_path / "notes"
            session.progress_file = tmp_path / "progress.json"
            session.notes_dir.mkdir(exist_ok=True)
        return session
    
    @pytest.mark.asyncio
    async def test_start_lesson_mode_topic_selection(self, session):
        """Test lesson mode topic selection"""
        with patch('builtins.input', return_value='1'), \
             patch('builtins.print'), \
             patch.object(session, 'clear_screen'), \
             patch.object(session, 'run_lesson_with_notes') as mock_lesson:
            
            await session.start_lesson_mode()
            
            # Should have called run_lesson_with_notes with first topic
            topics = list(session.cli_engine.curriculum.topics.keys())
            mock_lesson.assert_called_once_with(topics[0])
    
    @pytest.mark.asyncio
    async def test_start_lesson_mode_invalid_selection(self, session):
        """Test lesson mode with invalid topic selection"""
        with patch('builtins.input', return_value='invalid'), \
             patch('builtins.print') as mock_print, \
             patch.object(session, 'clear_screen'):
            
            await session.start_lesson_mode()
            
            # Should display warning about invalid selection
            printed_content = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Invalid" in printed_content
    
    @pytest.mark.asyncio
    async def test_run_lesson_with_notes_navigation(self, session):
        """Test lesson navigation and note-taking"""
        topic = "Arrays"
        
        # Simulate user continuing through lesson and taking a note
        with patch('builtins.input', side_effect=['c', 'n', 'c', 'c', 'q']), \
             patch('builtins.print'), \
             patch.object(session, 'take_note') as mock_take_note, \
             patch.object(session, 'post_lesson_review') as mock_review:
            
            await session.run_lesson_with_notes(topic)
            
            # Should have taken a note
            mock_take_note.assert_called_once_with(topic)
            # Should have called post-lesson review
            mock_review.assert_called_once_with(topic)
    
    @pytest.mark.asyncio
    async def test_post_lesson_review_options(self, session, sample_notes):
        """Test post-lesson review options"""
        topic = "Arrays"
        session.notes = sample_notes.copy()
        
        # Test review notes option
        with patch('builtins.input', return_value='1'), \
             patch('builtins.print'), \
             patch.object(session, 'clear_screen'), \
             patch.object(session, 'review_notes') as mock_review:
            
            await session.post_lesson_review(topic)
            
            mock_review.assert_called_once_with(topic_filter=topic)
            
            # Should update progress
            assert topic in session.progress.concepts_learned
            assert session.progress.lessons_completed > 0


class TestQuizMode:
    """Test quiz mode functionality"""
    
    @pytest.fixture
    def session(self, tmp_path):
        with patch('pathlib.Path.mkdir'):
            session = InteractiveSession()
            session.notes_dir = tmp_path / "notes"
            session.progress_file = tmp_path / "progress.json"
            session.notes_dir.mkdir(exist_ok=True)
        return session
    
    @pytest.mark.asyncio
    async def test_quiz_mode_correct_answers(self, session):
        """Test quiz mode with correct answers"""
        # Answer correctly (option 2 for both questions in the hardcoded quiz)
        with patch('builtins.input', side_effect=['2', '2']), \
             patch('builtins.print') as mock_print, \
             patch.object(session, 'clear_screen'):
            
            await session.quiz_mode()
            
            # Should have 100% score
            assert session.progress.quiz_score == 100.0
            
            # Should display success messages
            printed_content = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Correct" in printed_content
    
    @pytest.mark.asyncio
    async def test_quiz_mode_incorrect_answers(self, session):
        """Test quiz mode with incorrect answers"""
        # Answer incorrectly
        with patch('builtins.input', side_effect=['1', '1']), \
             patch('builtins.print') as mock_print, \
             patch.object(session, 'clear_screen'):
            
            await session.quiz_mode()
            
            # Should have 0% score
            assert session.progress.quiz_score == 0.0
            
            # Should display incorrect messages
            printed_content = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Incorrect" in printed_content
    
    @pytest.mark.asyncio
    async def test_quiz_mode_invalid_answers(self, session):
        """Test quiz mode with invalid answers"""
        # Answer with invalid input
        with patch('builtins.input', side_effect=['invalid', '5']), \
             patch('builtins.print') as mock_print, \
             patch.object(session, 'clear_screen'):
            
            await session.quiz_mode()
            
            # Should handle invalid answers gracefully
            printed_content = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Invalid" in printed_content


class TestPracticeMode:
    """Test practice mode functionality"""
    
    @pytest.fixture
    def session(self, tmp_path):
        with patch('pathlib.Path.mkdir'):
            session = InteractiveSession()
            session.notes_dir = tmp_path / "notes"
            session.progress_file = tmp_path / "progress.json"
            session.notes_dir.mkdir(exist_ok=True)
        return session
    
    @pytest.mark.asyncio
    async def test_practice_mode_display(self, session):
        """Test practice mode display"""
        with patch('builtins.print') as mock_print, \
             patch.object(session, 'clear_screen'), \
             patch.object(session, 'show_practice_solution') as mock_solution, \
             patch('sys.stdin.readline', return_value='\n'):
            
            await session.practice_mode()
            
            # Should display practice problem
            printed_content = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Practice" in printed_content or "Problem" in printed_content
            
            # Should show solution
            mock_solution.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_practice_mode_with_topic(self, session):
        """Test practice mode with specific topic"""
        topic = "Arrays"
        
        with patch('builtins.print'), \
             patch.object(session, 'clear_screen'), \
             patch.object(session, 'show_practice_solution'), \
             patch('sys.stdin.readline', return_value='\n'):
            
            await session.practice_mode(topic)
            
            # Should set mode correctly
            assert session.mode == LearningMode.PRACTICE
    
    @pytest.mark.asyncio
    async def test_practice_mode_error_handling(self, session):
        """Test practice mode error handling"""
        with patch.object(session, 'clear_screen', side_effect=Exception("Test error")), \
             patch('builtins.print') as mock_print:
            
            await session.practice_mode()
            
            # Should handle error gracefully
            printed_content = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Error" in printed_content
    
    @pytest.mark.asyncio
    async def test_show_practice_solution(self, session):
        """Test practice solution display"""
        with patch('builtins.print') as mock_print:
            
            await session.show_practice_solution()
            
            # Should display solution components
            printed_content = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Solution" in printed_content or "def two_sum" in printed_content


class TestExportFunctionality:
    """Test export functionality"""
    
    @pytest.fixture
    def session(self, tmp_path):
        with patch('pathlib.Path.mkdir'):
            session = InteractiveSession()
            session.notes_dir = tmp_path / "notes"
            session.progress_file = tmp_path / "progress.json"
            session.notes_dir.mkdir(exist_ok=True)
        return session
    
    @pytest.mark.asyncio
    async def test_export_notes_markdown(self, session, sample_notes, tmp_path):
        """Test exporting notes to markdown"""
        session.notes = sample_notes.copy()
        session.notes_dir = tmp_path
        
        with patch('builtins.input', return_value=''), \
             patch('builtins.print'):
            
            await session.export_notes()
            
            # Should create markdown file
            md_files = list(tmp_path.glob("notes_*.md"))
            assert len(md_files) == 1
            
            # Check file content
            content = md_files[0].read_text()
            assert "# Learning Notes" in content
            assert "Arrays" in content
            assert "contiguous memory" in content
    
    @pytest.mark.asyncio
    async def test_export_progress_report(self, session, tmp_path):
        """Test exporting progress report"""
        session.progress.lessons_completed = 3
        session.progress.notes_taken = 5
        session.progress.quiz_score = 85.0
        session.progress.concepts_learned = ["Arrays", "Trees"]
        
        with patch('builtins.input', return_value=''), \
             patch('builtins.print'), \
             patch('pathlib.Path.cwd', return_value=tmp_path):
            
            await session.export_progress_report()
            
            # Should create progress report file
            report_files = list(tmp_path.glob("progress_report_*.md"))
            assert len(report_files) == 1
            
            # Check file content
            content = report_files[0].read_text()
            assert "# Learning Progress Report" in content
            assert "Lessons Completed:** 3" in content
            assert "Quiz Score:** 85%" in content
            assert "Arrays" in content
    
    @pytest.mark.asyncio
    async def test_export_full_session(self, session, sample_notes, tmp_path):
        """Test exporting full session data"""
        session.notes = sample_notes.copy()
        session.progress.lessons_completed = 2
        
        with patch('builtins.input', return_value=''), \
             patch('builtins.print'), \
             patch('pathlib.Path.cwd', return_value=tmp_path):
            
            await session.export_full_session()
            
            # Should create JSON file
            json_files = list(tmp_path.glob("session_*.json"))
            assert len(json_files) == 1
            
            # Check file content
            with open(json_files[0], 'r') as f:
                data = json.load(f)
            
            assert "timestamp" in data
            assert "progress" in data
            assert "notes" in data
            assert len(data["notes"]) == len(sample_notes)
    
    @pytest.mark.asyncio
    async def test_export_lesson_summary(self, session, sample_notes, tmp_path):
        """Test exporting lesson summary"""
        session.notes = sample_notes.copy()
        topic = "Arrays"
        
        with patch('builtins.print'), \
             patch('pathlib.Path.cwd', return_value=tmp_path):
            
            await session.export_lesson_summary(topic)
            
            # Should create lesson summary file
            summary_files = list(tmp_path.glob("lesson_Arrays_*.md"))
            assert len(summary_files) == 1
            
            # Check file content
            content = summary_files[0].read_text()
            assert f"# Lesson Summary: {topic}" in content
            assert "Key Takeaways" in content
            assert "contiguous memory" in content  # High importance note
    
    @pytest.mark.asyncio
    async def test_export_session_menu(self, session):
        """Test export session menu navigation"""
        # Test notes export option
        with patch('builtins.input', side_effect=['1']), \
             patch('builtins.print'), \
             patch.object(session, 'clear_screen'), \
             patch.object(session, 'export_notes') as mock_export_notes:
            
            await session.export_session()
            
            mock_export_notes.assert_called_once()
        
        # Test progress report option
        with patch('builtins.input', side_effect=['2']), \
             patch('builtins.print'), \
             patch.object(session, 'clear_screen'), \
             patch.object(session, 'export_progress_report') as mock_export_progress:
            
            await session.export_session()
            
            mock_export_progress.assert_called_once()
        
        # Test full session option
        with patch('builtins.input', side_effect=['3']), \
             patch('builtins.print'), \
             patch.object(session, 'clear_screen'), \
             patch.object(session, 'export_full_session') as mock_export_full:
            
            await session.export_session()
            
            mock_export_full.assert_called_once()


class TestSessionStateManagement:
    """Test session state management and persistence"""
    
    @pytest.fixture
    def session(self, tmp_path):
        with patch('pathlib.Path.mkdir'):
            session = InteractiveSession()
            session.notes_dir = tmp_path / "notes"
            session.progress_file = tmp_path / "progress.json"
            session.notes_dir.mkdir(exist_ok=True)
        return session
    
    @pytest.mark.asyncio
    async def test_save_progress_new_file(self, session, tmp_path):
        """Test saving progress to new file"""
        session.progress.lessons_completed = 3
        session.progress.notes_taken = 7
        session.progress.concepts_learned = ["Arrays", "Trees"]
        
        with patch('builtins.print'):
            await session.save_progress()
        
        # Should create progress file
        assert session.progress_file.exists()
        
        # Check file content
        with open(session.progress_file, 'r') as f:
            data = json.load(f)
        
        assert data["lessons_completed"] == 3
        assert data["notes_taken"] == 7
        assert "Arrays" in data["concepts_learned"]
    
    @pytest.mark.asyncio
    async def test_save_progress_merge_existing(self, session, tmp_path):
        """Test saving progress with existing file (merge)"""
        # Create existing progress file
        existing_data = {
            "lessons_completed": 2,
            "notes_taken": 5,
            "concepts_learned": ["Graphs"],
            "quiz_score": 0.0,
            "time_spent_minutes": 0.0,
            "achievements": []
        }
        
        with open(session.progress_file, 'w') as f:
            json.dump(existing_data, f)
        
        # Update session progress
        session.progress.lessons_completed = 1
        session.progress.notes_taken = 3
        session.progress.concepts_learned = ["Arrays"]
        
        with patch('builtins.print'):
            await session.save_progress()
        
        # Check merged content
        with open(session.progress_file, 'r') as f:
            data = json.load(f)
        
        assert data["lessons_completed"] == 3  # 2 + 1
        assert data["notes_taken"] == 8       # 5 + 3
        assert "Graphs" in data["concepts_learned"]
        assert "Arrays" in data["concepts_learned"]
    
    @pytest.mark.asyncio
    async def test_end_session_summary(self, session, sample_notes):
        """Test session end summary"""
        session.notes = sample_notes.copy()
        session.progress.lessons_completed = 2
        session.progress.notes_taken = len(sample_notes)
        
        with patch('builtins.print') as mock_print, \
             patch.object(session, 'clear_screen'), \
             patch.object(session, 'save_progress') as mock_save, \
             patch.object(session, 'check_achievements'):
            
            await session.end_session()
            
            # Should save progress
            mock_save.assert_called_once()
            
            # Should display session summary
            printed_content = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "SESSION COMPLETE" in printed_content
            assert "minutes" in printed_content
    
    def test_clear_screen_functionality(self, session):
        """Test clear screen functionality"""
        with patch('builtins.print') as mock_print, \
             patch('sys.stdout.flush') as mock_flush:
            
            session.clear_screen()
            
            # Should have called print and flush
            assert mock_print.called or mock_flush.called


class TestMainRunLoop:
    """Test main run loop and navigation"""
    
    @pytest.fixture
    def session(self, tmp_path):
        with patch('pathlib.Path.mkdir'):
            session = InteractiveSession()
            session.notes_dir = tmp_path / "notes"
            session.progress_file = tmp_path / "progress.json"
            session.notes_dir.mkdir(exist_ok=True)
        return session
    
    @pytest.mark.asyncio
    async def test_main_loop_quit(self, session):
        """Test main loop quit functionality"""
        with patch.object(session, 'show_welcome') as mock_welcome, \
             patch.object(session, 'show_main_menu', return_value='q'), \
             patch.object(session, 'end_session') as mock_end:
            
            await session.run()
            
            mock_welcome.assert_called_once()
            mock_end.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_main_loop_keyboard_interrupt(self, session):
        """Test main loop keyboard interrupt handling"""
        with patch.object(session, 'show_welcome'), \
             patch.object(session, 'show_main_menu', side_effect=KeyboardInterrupt), \
             patch.object(session, 'save_progress') as mock_save, \
             patch('builtins.print'):
            
            await session.run()
            
            # Should save progress on interrupt
            mock_save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_main_loop_eof_error(self, session):
        """Test main loop EOF error handling"""
        with patch.object(session, 'show_welcome'), \
             patch.object(session, 'show_main_menu', side_effect=EOFError), \
             patch.object(session, 'save_progress') as mock_save, \
             patch('builtins.print'):
            
            await session.run()
            
            # Should save progress on EOF
            mock_save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_main_loop_menu_navigation(self, session):
        """Test main loop menu navigation"""
        menu_choices = ['1', '2', '3', '4', '5', '6', 'q']
        
        with patch.object(session, 'show_welcome'), \
             patch.object(session, 'show_main_menu', side_effect=menu_choices), \
             patch.object(session, 'start_lesson_mode') as mock_lesson, \
             patch.object(session, 'practice_mode') as mock_practice, \
             patch.object(session, 'quiz_mode') as mock_quiz, \
             patch.object(session, 'review_notes') as mock_notes, \
             patch.object(session, 'view_progress') as mock_progress, \
             patch.object(session, 'export_session') as mock_export, \
             patch.object(session, 'end_session'):
            
            await session.run()
            
            # Should have called all menu functions
            mock_lesson.assert_called_once()
            mock_practice.assert_called_once()
            mock_quiz.assert_called_once()
            mock_notes.assert_called_once()
            mock_progress.assert_called_once()
            mock_export.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_main_loop_invalid_choice(self, session):
        """Test main loop with invalid menu choice"""
        with patch.object(session, 'show_welcome'), \
             patch.object(session, 'show_main_menu', side_effect=['invalid', 'q']), \
             patch.object(session, 'end_session'), \
             patch('builtins.print') as mock_print, \
             patch('asyncio.sleep') as mock_sleep:
            
            await session.run()
            
            # Should display invalid choice warning
            printed_content = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Invalid" in printed_content
            
            # Should have brief pause
            mock_sleep.assert_called()


@pytest.mark.integration
class TestUIComponentsIntegration:
    """Integration tests for UI components"""
    
    @pytest.mark.asyncio
    async def test_complete_learning_session_flow(self, mock_cli_engine, tmp_path):
        """Test complete learning session flow"""
        with patch('pathlib.Path.mkdir'):
            session = InteractiveSession(cli_engine=mock_cli_engine)
            session.notes_dir = tmp_path / "notes"
            session.progress_file = tmp_path / "progress.json"
            session.notes_dir.mkdir(exist_ok=True)
        
        # Simulate a complete learning session
        with patch('builtins.input', side_effect=[
            '1',  # Start lesson
            '1',  # Select first topic
            'c',  # Continue lesson
            'n',  # Take note
            'Important concept',  # Note content
            'key,important',  # Tags
            '5',  # Importance
            'q',  # Quit lesson
            '6',  # Export session
            '3',  # Export full session
            'q'   # Quit
        ]), \
        patch('builtins.print'), \
        patch.object(session, 'clear_screen'), \
        patch('sys.stdin.readline', return_value='\n'):
            
            await session.run()
            
            # Should have taken notes
            assert len(session.notes) > 0
            
            # Should have updated progress
            assert session.progress.lessons_completed > 0
            assert session.progress.notes_taken > 0
            
            # Should have created export file
            json_files = list(tmp_path.glob("session_*.json"))
            assert len(json_files) == 1
    
    def test_data_class_serialization(self, sample_notes):
        """Test data class serialization for export"""
        note = sample_notes[0]
        
        # Test serialization
        note_dict = {
            'timestamp': note.timestamp,
            'topic': note.topic,
            'content': note.content,
            'tags': note.tags,
            'importance': note.importance
        }
        
        # Should be JSON serializable
        json_str = json.dumps(note_dict)
        assert json_str is not None
        
        # Should be deserializable
        restored_dict = json.loads(json_str)
        assert restored_dict['topic'] == note.topic
        assert restored_dict['content'] == note.content
    
    def test_session_progress_serialization(self):
        """Test session progress serialization"""
        progress = SessionProgress(
            lessons_completed=5,
            concepts_learned=["Arrays", "Trees"],
            notes_taken=10,
            quiz_score=85.5,
            time_spent_minutes=120.0,
            achievements=["Note Taker"]
        )
        
        # Test serialization using dataclass asdict
        from dataclasses import asdict
        progress_dict = asdict(progress)
        
        # Should be JSON serializable
        json_str = json.dumps(progress_dict)
        assert json_str is not None
        
        # Should contain all fields
        restored_dict = json.loads(json_str)
        assert restored_dict['lessons_completed'] == 5
        assert "Arrays" in restored_dict['concepts_learned']
        assert restored_dict['quiz_score'] == 85.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])