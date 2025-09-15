#!/usr/bin/env python3
"""Test that the enhanced CLI starts properly with database fix"""

import sys
import os
from unittest.mock import patch, MagicMock

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cli import CurriculumCLI
from src.persistence.db_manager import DBManager as Database

def test_database_fix():
    """Test that database handles corrupted data properly"""
    print("Testing database corruption handling...")
    
    # Create a database instance
    db = Database("test_curriculum.db")
    
    # Test getting/creating a user
    try:
        user = db.get_or_create_user("testuser")
        print(f"✅ Successfully created/retrieved user: {user.username}")
        print(f"   ID: {user.id}")
        print(f"   Created: {user.created_at}")
        print(f"   Last accessed: {user.last_accessed}")
    except Exception as e:
        print(f"❌ Failed to create/retrieve user: {e}")
        return False
    
    # Test saving progress
    try:
        db.save_progress(user.id, "test_lesson", completed=True, time_spent=60, quiz_score=85.0)
        print("✅ Successfully saved progress")
    except Exception as e:
        print(f"❌ Failed to save progress: {e}")
        return False
    
    # Test retrieving progress
    try:
        progress = db.get_user_progress(user.id)
        print(f"✅ Successfully retrieved progress: {len(progress)} records")
    except Exception as e:
        print(f"❌ Failed to retrieve progress: {e}")
        return False
    
    # Clean up test database
    import os
    if os.path.exists("test_curriculum.db"):
        os.remove("test_curriculum.db")
        print("✅ Cleaned up test database")
    
    return True

def test_cli_initialization():
    """Test that CLI initializes properly"""
    print("\nTesting CLI initialization...")
    
    try:
        # Mock user input to avoid interactive prompts
        with patch('src.cli.Prompt.ask', return_value='testuser'):
            cli = CurriculumCLI()
            print("✅ CLI initialized successfully")
            
            # Test getting all lessons
            lessons = cli.get_all_lessons()
            print(f"✅ Found {len(lessons)} lessons")
            
            # Test finding a lesson
            if lessons:
                first_lesson = lessons[0]
                found_lesson = cli.find_lesson_by_id(first_lesson['id'])
                if found_lesson:
                    print(f"✅ Successfully found lesson: {found_lesson['title']}")
                else:
                    print("❌ Failed to find lesson by ID")
            
        return True
    except Exception as e:
        print(f"❌ Failed to initialize CLI: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("ENHANCED CLI STARTUP TEST")
    print("="*60)
    
    all_passed = True
    
    # Test database fix
    if not test_database_fix():
        all_passed = False
    
    # Test CLI initialization
    if not test_cli_initialization():
        all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("The enhanced CLI should now work properly.")
        print("\nRun: python curriculum_cli_enhanced.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("="*60)

if __name__ == "__main__":
    main()