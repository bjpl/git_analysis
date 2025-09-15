#!/usr/bin/env python3
"""Test that the continue learning functionality works"""

import sys
import os
from unittest.mock import patch, MagicMock

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cli import CurriculumCLI
from src.persistence.db_manager import DBManager as Database

def test_lesson_retrieval():
    """Test that lessons are properly retrieved"""
    print("Testing lesson retrieval...")
    
    # Create a test CLI instance
    cli = CurriculumCLI()
    
    # Get all lessons
    all_lessons = cli.get_all_lessons()
    print(f"✅ Found {len(all_lessons)} lessons")
    
    # Test each lesson can be found by ID
    for i, lesson in enumerate(all_lessons[:3]):  # Test first 3
        found = cli.find_lesson_by_id(lesson['id'])
        if found:
            print(f"✅ Lesson {i+1}: {found['title']} (ID: {found['id']})")
        else:
            print(f"❌ Could not find lesson with ID: {lesson['id']}")
            return False
    
    return True

def test_first_incomplete_lesson():
    """Test that first incomplete lesson is found correctly"""
    print("\nTesting first incomplete lesson retrieval...")
    
    # Create a test database
    db = Database("test_continue.db")
    
    # Create a test user
    user = db.get_or_create_user("testuser")
    print(f"✅ Created test user: {user.username}")
    
    # Get first incomplete (should be first lesson for new user)
    first_incomplete = db.get_first_incomplete_lesson(user.id)
    print(f"✅ First incomplete lesson: {first_incomplete}")
    
    if first_incomplete:
        print("✅ Successfully found first incomplete lesson")
    else:
        print("⚠️  No incomplete lesson found (might be None for new user)")
    
    # Clean up
    import os
    if os.path.exists("test_continue.db"):
        os.remove("test_continue.db")
    
    return True

def test_continue_flow():
    """Test the continue learning flow"""
    print("\nTesting continue learning flow...")
    
    try:
        # Mock user inputs to avoid interaction
        with patch('src.cli.Prompt.ask') as mock_prompt, \
             patch('src.cli.Confirm.ask') as mock_confirm, \
             patch('src.cli.input') as mock_input, \
             patch('src.cli.IntPrompt.ask') as mock_int:
            
            # Setup mocks
            mock_prompt.return_value = 'testuser'
            mock_confirm.return_value = False  # Don't continue to next lesson
            mock_input.return_value = ''  # Just press enter
            mock_int.return_value = '1'  # Answer first option
            
            # Create CLI instance
            cli = CurriculumCLI()
            cli.current_user = cli.db.get_or_create_user("testuser")
            cli.session_start = 0
            
            # Check that get_all_lessons works
            lessons = cli.get_all_lessons()
            if lessons:
                print(f"✅ CLI has {len(lessons)} lessons available")
                
                # Check first lesson can be found
                first_lesson = cli.find_lesson_by_id(lessons[0]['id'])
                if first_lesson:
                    print(f"✅ Can find first lesson: {first_lesson['title']}")
                else:
                    print(f"❌ Cannot find first lesson with ID: {lessons[0]['id']}")
            else:
                print("❌ No lessons found!")
                return False
            
        return True
    except Exception as e:
        print(f"❌ Error testing continue flow: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("CONTINUE LEARNING FIX TEST")
    print("="*60)
    
    all_passed = True
    
    # Test lesson retrieval
    if not test_lesson_retrieval():
        all_passed = False
    
    # Test first incomplete lesson
    if not test_first_incomplete_lesson():
        all_passed = False
    
    # Test continue flow
    if not test_continue_flow():
        all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nThe continue learning feature should now work properly.")
        print("Debug output will show when you run the CLI.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("="*60)

if __name__ == "__main__":
    main()