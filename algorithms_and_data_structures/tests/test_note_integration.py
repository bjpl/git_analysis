#!/usr/bin/env python3
"""
Test script for validating note-taking integration with lesson viewer
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.enhanced_cli import EnhancedCLI
from src.notes_manager import NotesManager
from unittest.mock import Mock, patch, MagicMock
import unittest


class TestNoteIntegration(unittest.TestCase):
    """Test note-taking integration with lesson viewer"""
    
    def setUp(self):
        """Set up test environment"""
        self.cli = EnhancedCLI()
        self.test_lesson = {
            'id': 'test-lesson-1',
            'title': 'Test Lesson',
            'content': 'This is test content',
            'topics': ['topic1', 'topic2'],
            'module': 'Test Module',
            'practice_problems': 5,
            'difficulty': 'Medium',
            'duration': '15 mins'
        }
        self.test_module = {
            'title': 'Test Module',
            'lessons': [self.test_lesson]
        }
    
    def test_quick_note_method_exists(self):
        """Test that quick_note method exists"""
        self.assertTrue(hasattr(self.cli, 'quick_note'))
        self.assertTrue(callable(getattr(self.cli, 'quick_note')))
    
    def test_view_lesson_notes_method_exists(self):
        """Test that view_lesson_notes method exists"""
        self.assertTrue(hasattr(self.cli, 'view_lesson_notes'))
        self.assertTrue(callable(getattr(self.cli, 'view_lesson_notes')))
    
    @patch('builtins.input')
    @patch('src.enhanced_cli.NotesManager.save_note')
    def test_quick_note_saves(self, mock_save, mock_input):
        """Test that quick note saves correctly"""
        mock_input.return_value = "This is a quick note"
        
        self.cli.quick_note(self.test_lesson)
        
        # Verify save_note was called
        mock_save.assert_called_once()
        args = mock_save.call_args[1]
        
        # Check the saved note content
        self.assertEqual(args['content'], "This is a quick note")
        self.assertEqual(args['lesson_id'], 'test-lesson-1')
        self.assertIn('quick-note', args['tags'])
    
    @patch('src.enhanced_cli.NotesManager.get_notes')
    def test_view_lesson_notes_displays(self, mock_get_notes):
        """Test that view_lesson_notes displays notes correctly"""
        # Mock existing notes
        mock_get_notes.return_value = [
            {
                'content': 'Test note 1',
                'created_at': '2024-01-15',
                'tags': ['test', 'note']
            },
            {
                'content': 'Test note 2',
                'created_at': '2024-01-16',
                'tags': ['another', 'note']
            }
        ]
        
        # Capture output
        with patch('builtins.print') as mock_print:
            self.cli.view_lesson_notes(self.test_lesson)
            
            # Verify notes are displayed
            print_calls = [str(call) for call in mock_print.call_args_list]
            output = ' '.join(print_calls)
            
            self.assertIn('Test note 1', output)
            self.assertIn('Test note 2', output)
            self.assertIn('Total notes: 2', output)
    
    @patch('builtins.input')
    @patch('src.enhanced_cli.NotesManager.get_notes')
    @patch('src.enhanced_cli.NotesManager.save_note')
    def test_enhanced_note_taking_flow(self, mock_save, mock_get_notes, mock_input):
        """Test the enhanced note-taking flow with templates"""
        # Simulate no existing notes
        mock_get_notes.return_value = []
        
        # Simulate user choosing key concept note
        mock_input.side_effect = ['2', 'Binary Search is O(log n)', '']
        
        self.cli.take_lesson_notes(self.test_lesson)
        
        # Verify save was called with correct prefix
        mock_save.assert_called_once()
        args = mock_save.call_args[1]
        
        self.assertIn('KEY CONCEPT:', args['content'])
        self.assertIn('Binary Search is O(log n)', args['content'])
        self.assertIn('key-concept', args['tags'])
    
    @patch('builtins.input')
    @patch('src.enhanced_cli.NotesManager.get_notes')
    def test_existing_notes_prompt(self, mock_get_notes, mock_input):
        """Test that existing notes trigger the right prompts"""
        # Mock existing notes
        mock_get_notes.return_value = [
            {'content': 'Existing note', 'created_at': '2024-01-15'}
        ]
        
        # User chooses to view existing notes then cancels
        mock_input.side_effect = ['2', 'n']
        
        with patch('builtins.print') as mock_print:
            self.cli.take_lesson_notes(self.test_lesson)
            
            # Verify the existing notes message was shown
            print_calls = [str(call) for call in mock_print.call_args_list]
            output = ' '.join(print_calls)
            
            self.assertIn('1 existing note', output)
            self.assertIn('View existing notes', output)
    
    def test_note_count_in_lesson_display(self):
        """Test that note count is shown in lesson display"""
        with patch('src.enhanced_cli.NotesManager.get_notes') as mock_get_notes:
            # Mock 3 existing notes
            mock_get_notes.return_value = [
                {'content': 'Note 1'},
                {'content': 'Note 2'},
                {'content': 'Note 3'}
            ]
            
            with patch('builtins.print') as mock_print:
                with patch('builtins.input', return_value='0'):  # Exit immediately
                    with patch('os.system'):  # Mock clear screen
                        try:
                            self.cli.start_lesson(self.test_lesson, self.test_module)
                        except:
                            pass  # Ignore navigation errors
                        
                        # Check that note count is displayed
                        print_calls = [str(call) for call in mock_print.call_args_list]
                        output = ' '.join(print_calls)
                        
                        # The lesson header should show note count
                        self.assertIn('Notes: 3', output)


def run_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 Running Note Integration Tests")
    print("="*60 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestNoteIntegration)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("✅ All tests passed successfully!")
    else:
        print(f"❌ Tests failed: {len(result.failures)} failures, {len(result.errors)} errors")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)