#!/usr/bin/env python3
"""
Claude Learning Session - Interactive Q&A with your curriculum
Run this directly in Claude Code for an interactive learning experience!
"""

import sqlite3
import json
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
import os

# Import the curriculum data
from curriculum_cli_enhanced import FULL_CURRICULUM_WITH_QUESTIONS, Database

@dataclass
class LearningSession:
    """A learning session with Claude"""
    username: str
    current_lesson: dict
    db: Database
    notes: list
    
class ClaudeLearningSession:
    """Interactive learning session powered by Claude"""
    
    def __init__(self, username="bjpl"):
        self.username = username
        self.db = Database("curriculum.db")
        self.user = self.db.get_or_create_user(username)
        self.current_lesson = None
        self.session_notes = []
        
    def get_all_lessons(self):
        """Get all lessons from curriculum"""
        all_lessons = []
        for course_key, course_data in FULL_CURRICULUM_WITH_QUESTIONS.items():
            if 'modules' in course_data:
                for module in course_data['modules']:
                    for lesson in module.get('lessons', []):
                        lesson['course'] = course_key
                        lesson['module'] = module.get('title', '')
                        all_lessons.append(lesson)
        return all_lessons
    
    def show_progress(self):
        """Show user's progress"""
        progress = self.db.get_user_progress(self.user.id)
        
        print("\n" + "="*60)
        print(f"📊 Progress for {self.username}")
        print("="*60)
        
        all_lessons = self.get_all_lessons()
        completed = 0
        
        for lesson in all_lessons:
            if lesson['id'] in progress and progress[lesson['id']]['completed']:
                completed += 1
                score = progress[lesson['id']].get('quiz_score', 0)
                print(f"✅ {lesson['title']} - Score: {score:.0f}%")
            else:
                print(f"⬜ {lesson['title']} - Not completed")
        
        print(f"\nTotal Progress: {completed}/{len(all_lessons)} lessons ({completed/len(all_lessons)*100:.1f}%)")
        return progress
    
    def load_lesson(self, lesson_id=None):
        """Load a specific lesson or the next one"""
        if lesson_id:
            # Find specific lesson
            for lesson in self.get_all_lessons():
                if lesson['id'] == lesson_id:
                    self.current_lesson = lesson
                    return lesson
        else:
            # Get next incomplete lesson
            progress = self.db.get_user_progress(self.user.id)
            for lesson in self.get_all_lessons():
                if lesson['id'] not in progress or not progress[lesson['id']]['completed']:
                    self.current_lesson = lesson
                    return lesson
        
        return None
    
    def display_lesson(self):
        """Display current lesson content"""
        if not self.current_lesson:
            print("No lesson loaded! Use load_lesson() first.")
            return
        
        lesson = self.current_lesson
        
        print("\n" + "="*80)
        print(f"📚 LESSON: {lesson['title']}")
        print("="*80)
        
        if 'difficulty' in lesson:
            print(f"Difficulty: {lesson['difficulty'].upper()}")
        if 'time' in lesson:
            print(f"Estimated Time: {lesson['time']} minutes")
        
        print("\n" + "-"*40)
        print("CONTENT:")
        print("-"*40)
        print(lesson.get('content', 'No content available'))
        
        if 'code' in lesson and lesson['code']:
            print("\n" + "-"*40)
            print("CODE EXAMPLE:")
            print("-"*40)
            print(lesson['code'])
        
        print("\n" + "="*80)
        print("You can now ask me questions about this lesson!")
        print("I'll provide detailed explanations based on the content.")
        print("="*80)
    
    def ask_claude(self, question):
        """Ask Claude a question about the current lesson"""
        if not self.current_lesson:
            return "Please load a lesson first with load_lesson()"
        
        # This is where I (Claude) provide intelligent answers!
        print(f"\n🤖 Claude: Let me answer your question about {self.current_lesson['title']}...")
        
        # Save the question
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.session_notes.append(f"[{timestamp}] Q: {question}")
        
        # I'll provide the answer based on the lesson content
        # The actual answer will come from me (Claude) in real-time!
        
        return "Claude will provide answer here based on lesson content"
    
    def save_note(self, note):
        """Save a note about the current lesson"""
        if not self.current_lesson:
            return "Please load a lesson first"
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.session_notes.append(f"[{timestamp}] Note: {note}")
        print("✅ Note saved!")
    
    def save_session(self):
        """Save all notes and Q&A to database"""
        if not self.current_lesson or not self.session_notes:
            print("Nothing to save")
            return
        
        notes_text = "\n".join(self.session_notes)
        self.db.save_progress(
            user_id=self.user.id,
            lesson_id=self.current_lesson['id'],
            completed=True,
            time_spent=30,  # You can adjust this
            quiz_score=None,  # Set this if you take the quiz
            notes=notes_text
        )
        print(f"✅ Saved {len(self.session_notes)} notes to database!")
        self.session_notes = []
    
    def interactive_menu(self):
        """Simple interactive menu for Claude Code"""
        print("\n" + "="*60)
        print("🎓 CLAUDE LEARNING SESSION")
        print("="*60)
        print(f"Welcome, {self.username}!")
        print("\nCommands you can use:")
        print("  session.show_progress()     - See your progress")
        print("  session.load_lesson()       - Load next lesson")
        print("  session.load_lesson('id')   - Load specific lesson")
        print("  session.display_lesson()    - Show current lesson")
        print("  session.ask_claude('...')   - Ask me a question")
        print("  session.save_note('...')    - Save a note")
        print("  session.save_session()      - Save all notes to DB")
        print("  session.list_lessons()      - Show all lessons")
        print("\n💡 TIP: After loading a lesson, ask me anything about it!")
        print("="*60)
    
    def list_lessons(self):
        """List all available lessons"""
        print("\n📚 AVAILABLE LESSONS:")
        print("="*60)
        for i, lesson in enumerate(self.get_all_lessons(), 1):
            print(f"{i}. [{lesson['id']}] {lesson['title']}")
            print(f"   Module: {lesson.get('module', 'N/A')}")
            print(f"   Difficulty: {lesson.get('difficulty', 'N/A')}")
        print("="*60)

# Create a session instance
print("🚀 Initializing Claude Learning Session...")
session = ClaudeLearningSession("bjpl")
session.interactive_menu()

print("\n✅ Session ready! Try these commands:")
print(">>> session.show_progress()")
print(">>> session.load_lesson()")
print(">>> session.display_lesson()")
print(">>> session.ask_claude('Why is this important?')")

# You can now interact with the session object directly!