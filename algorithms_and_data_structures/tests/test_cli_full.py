#!/usr/bin/env python3
"""
Comprehensive test suite for the Algorithms & Data Structures CLI
Tests all major functionality without requiring user input
"""

import sys
import os
from pathlib import Path
import json
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Initialize colorama before imports
import colorama
colorama.init(autoreset=False, convert=True, strip=False)

# Import modules to test
from src.ui.windows_formatter import WindowsFormatter, WindowsColor
from src.ui.lesson_display import LessonDisplay
from src.notes_manager import NotesManager
from src.cli import CurriculumCLI


class TestWindowsFormatter(unittest.TestCase):
    """Test the Windows formatter functionality"""
    
    def setUp(self):
        self.formatter = WindowsFormatter()
    
    def test_initialization(self):
        """Test formatter initializes correctly"""
        self.assertIsNotNone(self.formatter)
        self.assertIsInstance(self.formatter.colors_enabled, bool)
        self.assertIn(self.formatter.box_style, ['simple', 'ascii'])
    
    def test_color_methods(self):
        """Test color formatting methods"""
        success_msg = self.formatter.success("Test")
        self.assertIn("Test", success_msg)
        
        error_msg = self.formatter.error("Error")
        self.assertIn("Error", error_msg)
        
        warning_msg = self.formatter.warning("Warning")
        self.assertIn("Warning", warning_msg)
        
        info_msg = self.formatter.info("Info")
        self.assertIn("Info", info_msg)
    
    def test_box_creation(self):
        """Test box drawing"""
        box = self.formatter.box("Test content", title="Test")
        self.assertIn("Test content", box)
        self.assertIn("Test", box)
    
    def test_header_creation(self):
        """Test header formatting"""
        header = self.formatter.header("Main Title", "Subtitle")
        self.assertIn("Main Title", header)
        self.assertIn("Subtitle", header)
    
    def test_divider(self):
        """Test divider creation"""
        divider = self.formatter.divider("Section")
        self.assertIn("Section", divider)
        self.assertTrue(len(divider) > 10)
    
    def test_progress_bar(self):
        """Test progress bar creation"""
        # Test 0%
        bar = self.formatter.progress_bar(0, 100, "Test")
        self.assertIsNotNone(bar)
        
        # Test 50%
        bar = self.formatter.progress_bar(50, 100, "Test")
        self.assertIsNotNone(bar)
        
        # Test 100%
        bar = self.formatter.progress_bar(100, 100, "Test")
        self.assertIsNotNone(bar)


class TestEnhancedCLI(unittest.TestCase):
    """Test the Enhanced CLI functionality"""
    
    def setUp(self):
        """Set up test CLI instance"""
        self.cli = CurriculumCLI()
    
    def test_initialization(self):
        """Test CLI initializes correctly"""
        self.assertIsNotNone(self.cli)
        self.assertIsNotNone(self.cli.formatter)
        self.assertIsNotNone(self.cli.lesson_display)
        self.assertIsNotNone(self.cli.notes_manager)
    
    def test_curriculum_loading(self):
        """Test curriculum data loads"""
        curriculum = self.cli.curriculum_data
        self.assertIsNotNone(curriculum)
        self.assertIn("modules", curriculum)
        self.assertIsInstance(curriculum["modules"], list)
        self.assertTrue(len(curriculum["modules"]) > 0)
    
    def test_progress_management(self):
        """Test progress loading and saving"""
        # Load progress
        progress = self.cli._load_progress()
        self.assertIsInstance(progress, dict)
        
        # Test progress structure
        self.assertIn("completed", progress)
        self.assertIn("current_module", progress)
        self.assertIn("current_lesson", progress)
        self.assertIn("score", progress)
    
    def test_user_detection(self):
        """Test user detection"""
        user = self.cli._detect_user()
        self.assertIsNotNone(user)
        self.assertIsInstance(user, str)
        self.assertTrue(len(user) > 0)
    
    @patch('builtins.input', return_value='0')
    def test_menu_display(self, mock_input):
        """Test main menu displays without errors"""
        # This should not raise any exceptions
        try:
            self.cli.display_main_menu(show_header=True)
            result = True
        except Exception as e:
            result = False
        
        self.assertTrue(result)


class TestNotesManager(unittest.TestCase):
    """Test the notes management functionality"""
    
    def setUp(self):
        self.notes_manager = NotesManager()
    
    def test_initialization(self):
        """Test notes manager initializes"""
        self.assertIsNotNone(self.notes_manager)
        self.assertIsNotNone(self.notes_manager.notes_dir)
    
    def test_notes_operations(self):
        """Test basic notes operations"""
        # Test getting notes for a lesson
        notes = self.notes_manager.get_notes("test-lesson")
        self.assertIsInstance(notes, str)
        
        # Test listing all notes
        all_notes = self.notes_manager.list_all_notes()
        self.assertIsInstance(all_notes, list)


class TestLessonDisplay(unittest.TestCase):
    """Test lesson display functionality"""
    
    def setUp(self):
        formatter = WindowsFormatter()
        self.lesson_display = LessonDisplay(formatter)
    
    def test_initialization(self):
        """Test lesson display initializes"""
        self.assertIsNotNone(self.lesson_display)
        self.assertIsNotNone(self.lesson_display.formatter)
    
    def test_format_content(self):
        """Test content formatting"""
        test_content = {
            "title": "Test Lesson",
            "content": "This is test content",
            "examples": ["Example 1", "Example 2"],
            "key_points": ["Point 1", "Point 2"]
        }
        
        # Format the content
        formatted = self.lesson_display.format_lesson_content(test_content)
        self.assertIsNotNone(formatted)
        self.assertIn("Test Lesson", formatted)
        self.assertIn("test content", formatted)


def run_tests():
    """Run all tests and return results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWindowsFormatter))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedCLI))
    suite.addTests(loader.loadTestsFromTestCase(TestNotesManager))
    suite.addTests(loader.loadTestsFromTestCase(TestLessonDisplay))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFailed tests:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\nTests with errors:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("🧪 Running Comprehensive CLI Test Suite")
    print("="*60)
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed! The CLI is working correctly.")
    else:
        print("\n❌ Some tests failed. Please review the output above.")
    
    sys.exit(0 if success else 1)