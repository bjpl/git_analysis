#!/usr/bin/env python3
"""
Test script for questionnaire core functionality
Demonstrates session management, logging, and progress tracking without GUI
"""

import os
import sys
import time
from datetime import datetime

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from questionnaire_core import (
    SessionManager, QuestionnaireSettings, ProgressTracker,
    cleanup_old_sessions
)


def test_session_management():
    """Test session creation, response logging, and CSV export"""
    print("Testing Session Management...")
    
    # Create session manager
    session_mgr = SessionManager("test_sessions")
    
    # Start a session
    session_id = session_mgr.start_session(5)
    print(f"Started session: {session_id}")
    
    # Simulate answering questions
    questions = [
        "What is your name?",
        "What is your favorite color?",
        "Describe your ideal vacation.",
        "What motivates you?",
        "What are your goals?"
    ]
    
    answers = [
        "Alice Johnson",
        "Blue - it reminds me of the ocean",
        "A quiet cabin in the mountains with good books",
        "Making a positive impact on others",
        "To learn something new every day"
    ]
    
    for i, (question, answer) in enumerate(zip(questions, answers)):
        # Simulate processing time
        start_time = time.time()
        time.sleep(0.1)  # Simulate thinking time
        processing_time = int((time.time() - start_time) * 1000)
        
        session_mgr.add_response(
            question_id=i,
            question_text=question,
            answer=answer,
            processing_time_ms=processing_time,
            additional_data={"confidence": 0.9}
        )
        print(f"Added response {i + 1}/5")
    
    # End session and get CSV path
    csv_path = session_mgr.end_session()
    print(f"Session saved to: {csv_path}")
    
    # Verify file exists and has content
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"CSV file size: {len(content)} characters")
            print("First few lines of CSV:")
            for i, line in enumerate(content.split('\n')[:10]):
                print(f"  {i+1}: {line}")
    
    return csv_path


def test_settings_management():
    """Test settings loading, modification, and saving"""
    print("\nTesting Settings Management...")
    
    # Create settings with custom file
    settings = QuestionnaireSettings("test_settings.json")
    
    print("Default settings:")
    for key, value in settings.settings.items():
        print(f"  {key}: {value}")
    
    # Modify some settings
    settings.set("processing_timeout_ms", 45000)
    settings.set("max_sessions_to_keep", 50)
    settings.update({
        "show_progress": False,
        "enable_timestamps": True
    })
    
    print("\nModified settings:")
    print(f"  processing_timeout_ms: {settings.get('processing_timeout_ms')}")
    print(f"  max_sessions_to_keep: {settings.get('max_sessions_to_keep')}")
    print(f"  show_progress: {settings.get('show_progress')}")
    
    # Verify settings file was created
    if os.path.exists("test_settings.json"):
        print("Settings file created successfully")
        
        # Load settings again to verify persistence
        settings2 = QuestionnaireSettings("test_settings.json")
        assert settings2.get('processing_timeout_ms') == 45000
        print("Settings persistence verified")


def test_progress_tracking():
    """Test progress tracking functionality"""
    print("\nTesting Progress Tracking...")
    
    tracker = ProgressTracker()
    
    # Test callback mechanism
    progress_updates = []
    
    def progress_callback(current, total):
        progress_updates.append((current, total))
        percentage = (current / total) * 100 if total > 0 else 0
        print(f"Progress: {current}/{total} ({percentage:.1f}%)")
    
    tracker.add_progress_callback(progress_callback)
    
    # Simulate progress through 10 questions
    tracker.set_total_questions(10)
    
    for i in range(10):
        time.sleep(0.05)  # Simulate processing time
        tracker.advance_question()
        
        if i == 5:  # Halfway through
            remaining = tracker.get_estimated_time_remaining()
            if remaining:
                print(f"  Estimated time remaining: {remaining:.2f} seconds")
    
    print(f"Final progress: {tracker.get_progress_percentage():.1f}%")
    print(f"Total progress updates: {len(progress_updates)}")
    
    # Test reset
    tracker.reset()
    assert tracker.get_progress_percentage() == 0.0
    print("Progress reset verified")


def test_error_handling():
    """Test error handling scenarios"""
    print("\nTesting Error Handling...")
    
    session_mgr = SessionManager("test_sessions")
    
    # Try to add response without starting session
    try:
        session_mgr.add_response(0, "Test question", "Test answer")
        print("ERROR: Should have raised exception")
    except ValueError as e:
        print(f"✓ Correctly caught error: {e}")
    
    # Try to end session without starting one
    result = session_mgr.end_session()
    if result is None:
        print("✓ Correctly handled ending non-existent session")
    
    # Test settings with invalid file path
    try:
        settings = QuestionnaireSettings("/invalid/path/settings.json")
        print("✓ Settings gracefully handled invalid path")
    except Exception as e:
        print(f"Settings error handling: {e}")


def test_cleanup_functionality():
    """Test session cleanup functionality"""
    print("\nTesting Cleanup Functionality...")
    
    # Create multiple session files
    test_dir = "test_cleanup_sessions"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create some fake session files with different timestamps
    for i in range(15):
        filename = f"session_2025082{i:02d}_120000_2025082{i:02d}_120100.csv"
        filepath = os.path.join(test_dir, filename)
        with open(filepath, 'w') as f:
            f.write(f"Test session {i}")
    
    print(f"Created {len(os.listdir(test_dir))} test session files")
    
    # Run cleanup with limit of 10
    cleanup_old_sessions(test_dir, max_sessions=10)
    
    remaining_files = len(os.listdir(test_dir))
    print(f"Files remaining after cleanup: {remaining_files}")
    
    if remaining_files <= 10:
        print("✓ Cleanup function working correctly")
    else:
        print("⚠ Cleanup may not have worked as expected")
    
    # Clean up test directory
    import shutil
    shutil.rmtree(test_dir)


def main():
    """Run all tests"""
    print("=" * 60)
    print("Questionnaire Core Functionality Test")
    print("=" * 60)
    
    try:
        # Run all tests
        csv_path = test_session_management()
        test_settings_management()
        test_progress_tracking()
        test_error_handling()
        test_cleanup_functionality()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print(f"Sample session data saved to: {csv_path}")
        print("=" * 60)
        
        # Clean up test files
        test_files = [
            "test_settings.json",
        ]
        
        for test_file in test_files:
            if os.path.exists(test_file):
                os.remove(test_file)
                print(f"Cleaned up: {test_file}")
                
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()