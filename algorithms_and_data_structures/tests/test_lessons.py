#!/usr/bin/env python3
"""Test script to verify lesson count in enhanced CLI"""

import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the curriculum
from curriculum_cli_enhanced import FULL_CURRICULUM_WITH_QUESTIONS

def count_lessons():
    """Count total lessons and verify questions"""
    total_lessons = 0
    lessons_with_questions = 0
    lessons_without_questions = 0
    
    print("=" * 80)
    print("CURRICULUM ANALYSIS")
    print("=" * 80)
    
    for course_key, course_data in FULL_CURRICULUM_WITH_QUESTIONS.items():
        print(f"\n📚 {course_key.replace('_', ' ').title()}")
        
        course_lesson_count = 0
        
        # Check if lessons are directly in course_data
        if 'lessons' in course_data:
            course_lessons = course_data['lessons']
            for lesson in course_lessons:
                course_lesson_count += 1
                total_lessons += 1
                questions = lesson.get('comprehension_questions', [])
                
                if questions:
                    lessons_with_questions += 1
                    print(f"   ✓ {lesson['id']}: {lesson['title']} ({len(questions)} questions)")
                else:
                    lessons_without_questions += 1
                    print(f"   ✗ {lesson['id']}: {lesson['title']} (NO QUESTIONS)")
        
        # Or if they're nested in modules
        elif 'modules' in course_data:
            for module in course_data['modules']:
                module_title = module.get('title', 'Unknown Module')
                print(f"   📂 {module_title}")
                
                for lesson in module.get('lessons', []):
                    course_lesson_count += 1
                    total_lessons += 1
                    questions = lesson.get('comprehension_questions', [])
                    
                    if questions:
                        lessons_with_questions += 1
                        print(f"      ✓ {lesson['id']}: {lesson['title']} ({len(questions)} questions)")
                    else:
                        lessons_without_questions += 1
                        print(f"      ✗ {lesson['id']}: {lesson['title']} (NO QUESTIONS)")
        
        print(f"   Total lessons in course: {course_lesson_count}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Lessons: {total_lessons}")
    print(f"Lessons with comprehension questions: {lessons_with_questions}")
    print(f"Lessons without questions: {lessons_without_questions}")
    
    if lessons_with_questions == total_lessons:
        print("\n✅ SUCCESS: All lessons have comprehension questions!")
    else:
        print(f"\n⚠️  WARNING: {lessons_without_questions} lessons are missing questions")
    
    # Check question quality
    print("\n" + "=" * 80)
    print("QUESTION QUALITY CHECK")
    print("=" * 80)
    
    for course_key, course_data in FULL_CURRICULUM_WITH_QUESTIONS.items():
        # Check direct lessons
        if 'lessons' in course_data:
            for lesson in course_data['lessons']:
                questions = lesson.get('comprehension_questions', [])
                if questions:
                    print(f"\n{lesson['title']}:")
                    for i, q in enumerate(questions, 1):
                        difficulty = q.get('difficulty', 'unknown')
                        has_explanation = 'explanation' in q
                        print(f"  Q{i}: Difficulty={difficulty}, Has explanation={has_explanation}")
        
        # Check module lessons
        elif 'modules' in course_data:
            for module in course_data['modules']:
                for lesson in module.get('lessons', []):
                    questions = lesson.get('comprehension_questions', [])
                    if questions:
                        print(f"\n{lesson['title']}:")
                        for i, q in enumerate(questions, 1):
                            difficulty = q.get('difficulty', 'unknown')
                            has_explanation = 'explanation' in q
                            print(f"  Q{i}: Difficulty={difficulty}, Has explanation={has_explanation}")

if __name__ == "__main__":
    count_lessons()