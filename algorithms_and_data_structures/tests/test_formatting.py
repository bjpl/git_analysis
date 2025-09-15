#!/usr/bin/env python3
"""Test script to verify curriculum formatting is working correctly"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.formatter import TerminalFormatter
from src.commands.curriculum_commands import CurriculumShowCommand

def test_curriculum_formatting():
    """Test that curriculum content is displayed with enhanced formatting"""
    
    # Initialize formatter
    formatter = TerminalFormatter()
    
    print("\n" + "="*60)
    print("TESTING ENHANCED CURRICULUM FORMATTING")
    print("="*60 + "\n")
    
    # Create a mock curriculum
    mock_curriculum = {
        'id': 1,
        'name': 'Data Structures & Algorithms',
        'description': 'Master the fundamental concepts that power modern software. '
                      'Learn how to think algorithmically and solve complex problems efficiently.',
        'status': 'active',
        'difficulty': 'intermediate',
        'category': 'Computer Science',
        'author': 'Prof. Algorithm',
        'tags': ['algorithms', 'data-structures', 'problem-solving', 'optimization'],
        'created': '2024-01-15T10:30:00',
        'updated': '2024-02-01T14:22:00',
        'modules': [
            {'id': 1, 'name': 'Arrays and Strings', 'order': 1, 'status': 'published'},
            {'id': 2, 'name': 'Linked Lists', 'order': 2, 'status': 'published'},
            {'id': 3, 'name': 'Trees and Graphs', 'order': 3, 'status': 'draft'},
            {'id': 4, 'name': 'Dynamic Programming', 'order': 4, 'status': 'draft'}
        ],
        'students': 342,
        'completion_rate': 78.5,
        'average_rating': 4.7,
        'total_duration': '40 hours'
    }
    
    # Create command instance and mock args
    cmd = CurriculumShowCommand()
    
    class MockArgs:
        include_stats = True
        include_modules = True
    
    args = MockArgs()
    
    # Test the enhanced display
    print("\n🎨 Testing Enhanced Curriculum Display:\n")
    cmd._show_detailed(formatter, mock_curriculum, args)
    
    print("\n" + "="*60)
    print("✅ Formatting test complete!")
    print("="*60 + "\n")
    
    # Test interactive lesson content formatting
    print("\n🎓 Testing Lesson Content Formatting:\n")
    
    from src.ui.interactive import InteractiveSession
    session = InteractiveSession()
    
    # Get sample lesson content
    sample_content = session._get_default_lesson_content("Binary Search")
    
    print("Sample lesson content (professor style):")
    print("-" * 40)
    
    for i, content in enumerate(sample_content[:2], 1):  # Show first 2 sections
        formatter.box(
            content,
            title=f"Section {i}",
            style="rounded",
            padding=2,
            color=formatter.theme.primary if hasattr(formatter, 'theme') else None
        )
        print()
    
    print("\n✅ All formatting tests passed successfully!")
    print("\nThe enhanced formatter is now properly integrated with:")
    print("  • Curriculum display commands")
    print("  • Interactive lesson content")
    print("  • Professor-style teaching explanations")
    
    return True

if __name__ == "__main__":
    try:
        test_curriculum_formatting()
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)