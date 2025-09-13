#!/usr/bin/env python3
"""
Lesson Viewer - Dedicated component for displaying lesson content
Handles all lesson display without recursive menu loops
"""

import os
from typing import Dict, Any, Optional
from .windows_formatter import WindowsFormatter
from .enhanced_lesson_formatter import EnhancedLessonFormatter
from ..core.curriculum import Lesson, Module


class LessonViewer:
    """Handles lesson content display and interaction"""
    
    def __init__(self, formatter: Optional[WindowsFormatter] = None):
        """Initialize lesson viewer
        
        Args:
            formatter: Terminal formatter instance
        """
        self.formatter = formatter or WindowsFormatter()
        self.enhanced_formatter = EnhancedLessonFormatter(self.formatter)
    
    def display_lesson(self, lesson: Lesson, module: Module) -> str:
        """Display lesson content and return user action
        
        Args:
            lesson: Lesson to display
            module: Parent module
            
        Returns:
            User's selected action
        """
        # Clear screen for clean display
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Convert lesson to display format
        lesson_data = self._prepare_lesson_data(lesson, module)
        
        try:
            # Use enhanced formatter for beautiful display
            self.enhanced_formatter.format_lesson_content(lesson_data)
        except Exception as e:
            # Fallback to simple display
            self._simple_lesson_display(lesson, module)
        
        # Show interactive menu and get user choice
        return self._show_lesson_menu()
    
    def _prepare_lesson_data(self, lesson: Lesson, module: Module) -> Dict[str, Any]:
        """Prepare lesson data for enhanced formatter
        
        Args:
            lesson: Lesson object
            module: Parent module
            
        Returns:
            Formatted lesson dictionary
        """
        # Convert lesson to dict and add required fields
        data = lesson.to_dict()
        
        # Add module context
        data['subtitle'] = f"Module: {module.title}"
        
        # Ensure key_topics exists for formatter
        data['key_topics'] = data.get('topics', [])
        
        # Ensure content is properly formatted
        if not data.get('content'):
            data['content'] = self._generate_default_content(lesson)
        
        return data
    
    def _generate_default_content(self, lesson: Lesson) -> str:
        """Generate default content if none exists
        
        Args:
            lesson: Lesson object
            
        Returns:
            Generated content string
        """
        parts = []
        
        if lesson.topics:
            parts.append("## Topics Covered")
            for topic in lesson.topics:
                parts.append(f"- {topic}")
        
        if lesson.objectives:
            parts.append("\n## Learning Objectives")
            for obj in lesson.objectives:
                parts.append(f"- {obj}")
        
        if lesson.prerequisites:
            parts.append("\n## Prerequisites")
            for prereq in lesson.prerequisites:
                parts.append(f"- {prereq}")
        
        if not parts:
            parts.append("This lesson content is being prepared. Check back soon!")
        
        return '\n'.join(parts)
    
    def _simple_lesson_display(self, lesson: Lesson, module: Module):
        """Simple fallback display for lessons
        
        Args:
            lesson: Lesson to display
            module: Parent module
        """
        # Header
        print(self.formatter.header(f"📖 {lesson.title}", level=1))
        print(self.formatter.info(f"Module: {module.title}"))
        print()
        
        # Content
        if lesson.content:
            print(self.formatter.box(lesson.content, title="Overview", style="rounded"))
        
        # Topics
        if lesson.topics:
            print(self.formatter.header("🎯 Key Topics", level=2))
            for i, topic in enumerate(lesson.topics, 1):
                print(f"  {i}. {topic}")
            print()
        
        # Info
        print(self.formatter.header("📊 Lesson Info", level=3))
        print(f"  Difficulty: {lesson.difficulty}")
        print(f"  Est. Time: {lesson.est_time}")
        print(f"  Practice Problems: {lesson.practice_problems}")
        print()
    
    def _show_lesson_menu(self) -> str:
        """Show lesson interaction menu and get user choice
        
        Returns:
            User's selected action
        """
        print(self.formatter.divider())
        print("Your choice: ", end="", flush=True)
        
        choice = input().strip()
        return choice
    
    def show_claude_questions(self, lesson: Lesson):
        """Display suggested Claude questions without recursion
        
        Args:
            lesson: Current lesson
        """
        print()
        print(self.formatter.header("🤖 Suggested Questions for Claude", level=2))
        print(self.formatter.info("Copy these questions to Claude for detailed explanations:"))
        print()
        
        questions = self._generate_claude_questions(lesson)
        
        for i, question in enumerate(questions, 1):
            print(f"{i}. {question}")
        
        print()
        print(self.formatter.warning("💡 Tip: Keep Claude open alongside this CLI for best results!"))
        print()
        input("Press Enter to return to lesson menu...")
    
    def _generate_claude_questions(self, lesson: Lesson) -> list:
        """Generate relevant questions for Claude based on lesson
        
        Args:
            lesson: Current lesson
            
        Returns:
            List of suggested questions
        """
        questions = [
            f"Can you explain {lesson.title} with real-world examples?",
            f"What are the time and space complexities of concepts in {lesson.title}?",
            f"When should I use techniques from {lesson.title} vs alternatives?",
            f"Can you show me a step-by-step implementation of {lesson.title}?",
            f"What are common mistakes when learning {lesson.title}?",
            f"How does {lesson.title} compare to other approaches?"
        ]
        
        # Add topic-specific questions
        if lesson.topics:
            for topic in lesson.topics[:2]:  # First two topics
                questions.append(f"Can you deep dive into {topic}?")
        
        return questions[:8]  # Limit to 8 questions