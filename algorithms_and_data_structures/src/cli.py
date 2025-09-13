#!/usr/bin/env python3
"""
Unified CLI - Clean, maintainable entry point for the learning platform
Eliminates recursion issues and provides proper state management
"""

import os
import sys
import asyncio
from pathlib import Path
from enum import Enum
from typing import Optional, Tuple

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Core imports
from src.core.curriculum import CurriculumManager, Lesson, Module
from src.core.progress import ProgressManager
from src.ui.windows_formatter import WindowsFormatter
from src.ui.lesson_viewer import LessonViewer
from src.notes_manager import NotesManager
from src.notes_viewer import EnhancedNotesViewer


class MenuState(Enum):
    """Application state enumeration"""
    MAIN_MENU = "main_menu"
    BROWSE_MODULES = "browse_modules"
    BROWSE_LESSONS = "browse_lessons"
    VIEW_LESSON = "view_lesson"
    NOTES = "notes"
    PROGRESS = "progress"
    SETTINGS = "settings"
    EXIT = "exit"


class UnifiedCLI:
    """Unified CLI with proper state management and no recursion"""
    
    def __init__(self):
        """Initialize the unified CLI"""
        # Core managers
        self.curriculum = CurriculumManager()
        self.progress = ProgressManager()
        
        # UI components
        self.formatter = WindowsFormatter()
        self.lesson_viewer = LessonViewer(self.formatter)
        self.notes_manager = NotesManager()
        self.notes_viewer = EnhancedNotesViewer()
        
        # State management
        self.state = MenuState.MAIN_MENU
        self.current_module: Optional[Module] = None
        self.current_lesson: Optional[Lesson] = None
        self.running = True
    
    def run(self):
        """Main run loop with proper state management"""
        # Welcome message
        self._show_welcome()
        
        # Main state machine loop
        while self.running:
            try:
                if self.state == MenuState.MAIN_MENU:
                    self._handle_main_menu()
                elif self.state == MenuState.BROWSE_MODULES:
                    self._handle_browse_modules()
                elif self.state == MenuState.BROWSE_LESSONS:
                    self._handle_browse_lessons()
                elif self.state == MenuState.VIEW_LESSON:
                    self._handle_view_lesson()
                elif self.state == MenuState.NOTES:
                    self._handle_notes()
                elif self.state == MenuState.PROGRESS:
                    self._handle_progress()
                elif self.state == MenuState.SETTINGS:
                    self._handle_settings()
                elif self.state == MenuState.EXIT:
                    self._handle_exit()
                    break
            except KeyboardInterrupt:
                print("\n")
                self.state = MenuState.EXIT
            except Exception as e:
                print(self.formatter.error(f"Error: {e}"))
                input("Press Enter to continue...")
                self.state = MenuState.MAIN_MENU
    
    def _show_welcome(self):
        """Display welcome message"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(self.formatter.header("=" * 80))
        print(self.formatter.header("🎓 Algorithms & Data Structures Learning Platform"))
        print(self.formatter.header("=" * 80))
        print()
        print(self.formatter.success(f"Welcome back, {self.progress.progress.user}!"))
        print(self.formatter.info("Master algorithms with structured learning"))
        print()
        input("Press Enter to start...")
    
    def _handle_main_menu(self):
        """Handle main menu display and selection"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Calculate stats
        total_lessons = self.curriculum.get_total_lessons()
        completed = len(self.progress.progress.completed)
        percentage = self.progress.progress.get_completion_percentage(total_lessons)
        
        # Display header
        print(self.formatter.header("🎓 Main Menu", level=1))
        print(f"Progress: {completed}/{total_lessons} lessons ({percentage:.1f}%)")
        print()
        
        # Menu options
        print("1. 📚 Browse Curriculum")
        print("2. 🎯 Continue Learning")
        print("3. 📝 Manage Notes")
        print("4. 📊 View Progress")
        print("5. 💡 Practice Problems")
        print("6. 🤖 Claude AI Guide")
        print("7. ⚙️  Settings")
        print("0. 🚪 Exit")
        print()
        
        choice = input("Your choice: ").strip()
        
        # Handle choice
        if choice == "1":
            self.state = MenuState.BROWSE_MODULES
        elif choice == "2":
            self._continue_learning()
        elif choice == "3":
            self.state = MenuState.NOTES
        elif choice == "4":
            self.state = MenuState.PROGRESS
        elif choice == "5":
            self._show_practice_problems()
        elif choice == "6":
            self._show_claude_guide()
        elif choice == "7":
            self.state = MenuState.SETTINGS
        elif choice == "0":
            self.state = MenuState.EXIT
        else:
            print(self.formatter.error("Invalid choice"))
            input("Press Enter to continue...")
    
    def _handle_browse_modules(self):
        """Handle module browsing"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(self.formatter.header("📚 Browse Modules", level=1))
        print()
        
        modules = self.curriculum.get_all_modules()
        
        # Display modules with progress
        for i, module in enumerate(modules, 1):
            lesson_ids = [l.id for l in module.lessons]
            progress_info = self.progress.get_module_progress(lesson_ids)
            
            # Status icon
            if progress_info['is_complete']:
                icon = "✅"
                color = self.formatter.theme.success
            elif progress_info['completed'] > 0:
                icon = "📊"
                color = self.formatter.theme.warning
            else:
                icon = "📘"
                color = self.formatter.theme.info
            
            # Display module
            module_text = f"{i}. {icon} {module.title}"
            progress_text = f"[{progress_info['completed']}/{progress_info['total']}]"
            
            print(self.formatter._color(f"{module_text:40} {progress_text}", color))
        
        print()
        print("Enter module number (0 to go back): ", end="")
        choice = input().strip()
        
        if choice == "0":
            self.state = MenuState.MAIN_MENU
        elif choice.isdigit() and 1 <= int(choice) <= len(modules):
            self.current_module = modules[int(choice) - 1]
            self.state = MenuState.BROWSE_LESSONS
        else:
            print(self.formatter.error("Invalid choice"))
            input("Press Enter to continue...")
    
    def _handle_browse_lessons(self):
        """Handle lesson browsing within a module"""
        if not self.current_module:
            self.state = MenuState.BROWSE_MODULES
            return
        
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(self.formatter.header(f"📚 {self.current_module.title} - Lessons", level=1))
        print()
        
        # Display lessons
        for i, lesson in enumerate(self.current_module.lessons, 1):
            # Status
            if lesson.id in self.progress.progress.completed:
                icon = "✅"
                status = "Completed"
                color = self.formatter.theme.success
            elif lesson.id == self.progress.progress.current_lesson:
                icon = "▶️"
                status = "In Progress"
                color = self.formatter.theme.warning
            else:
                icon = "📖"
                status = "Not Started"
                color = self.formatter.theme.text
            
            # Display lesson
            print(self.formatter._color(f"{i}. {icon} {lesson.title} - {status}", color))
            print(f"   Topics: {', '.join(lesson.topics[:3])}")
            print(f"   {lesson.practice_problems} practice problems | {lesson.est_time}")
            print()
        
        print("Enter lesson number (0 to go back): ", end="")
        choice = input().strip()
        
        if choice == "0":
            self.state = MenuState.BROWSE_MODULES
            self.current_module = None
        elif choice.isdigit() and 1 <= int(choice) <= len(self.current_module.lessons):
            self.current_lesson = self.current_module.lessons[int(choice) - 1]
            self.progress.set_current_lesson(self.current_lesson.id)
            self.state = MenuState.VIEW_LESSON
        else:
            print(self.formatter.error("Invalid choice"))
            input("Press Enter to continue...")
    
    def _handle_view_lesson(self):
        """Handle lesson viewing and interaction"""
        if not self.current_lesson or not self.current_module:
            self.state = MenuState.BROWSE_LESSONS
            return
        
        # Display lesson content
        choice = self.lesson_viewer.display_lesson(self.current_lesson, self.current_module)
        
        # Handle user choice
        if choice == "1":  # Take Notes
            self._take_lesson_notes()
        elif choice == "2":  # Claude Questions
            self.lesson_viewer.show_claude_questions(self.current_lesson)
        elif choice == "3":  # Practice Problems
            self._show_lesson_practice()
        elif choice == "4":  # Mark Complete
            self._mark_lesson_complete()
            self.state = MenuState.BROWSE_LESSONS
        elif choice == "5":  # Skip to Next
            self._skip_to_next()
        elif choice == "0":  # Back
            self.state = MenuState.BROWSE_LESSONS
        else:
            print(self.formatter.error("Invalid choice"))
            input("Press Enter to continue...")
    
    def _take_lesson_notes(self):
        """Take notes for current lesson"""
        if not self.current_lesson:
            return
        
        print()
        print(self.formatter.header("📝 Taking Notes", level=2))
        print("Enter your notes (press Enter twice to finish):")
        
        lines = []
        while True:
            line = input()
            if not line and lines and not lines[-1]:
                break
            lines.append(line)
        
        note_content = "\n".join(lines[:-1])  # Remove last empty line
        
        if note_content.strip():
            self.notes_manager.save_note(
                user_id=1,
                lesson_id=self.current_lesson.id,
                module_name=self.current_module.title,
                topic=self.current_lesson.title,
                content=note_content,
                tags=[self.current_lesson.id, "study-notes"]
            )
            print(self.formatter.success("✅ Note saved successfully!"))
        else:
            print(self.formatter.warning("No content to save"))
        
        input("Press Enter to continue...")
    
    def _mark_lesson_complete(self):
        """Mark current lesson as complete"""
        if not self.current_lesson:
            return
        
        self.progress.mark_lesson_complete(self.current_lesson.id, points=10)
        print()
        print(self.formatter.success(f"✅ Marked '{self.current_lesson.title}' as complete!"))
        print(self.formatter.info(f"Score: {self.progress.progress.score} points"))
        input("Press Enter to continue...")
        
        # Clear current lesson
        self.current_lesson = None
    
    def _skip_to_next(self):
        """Skip to next lesson"""
        next_lesson_data = self.curriculum.get_next_lesson(
            self.current_lesson.id if self.current_lesson else None,
            self.progress.progress.completed
        )
        
        if next_lesson_data:
            lesson, module = next_lesson_data
            self.current_lesson = lesson
            self.current_module = module
            self.progress.set_current_lesson(lesson.id)
            print(self.formatter.info(f"\n⏭️ Skipping to: {lesson.title}"))
            input("Press Enter to continue...")
        else:
            print(self.formatter.success("\n🎉 No more lessons available!"))
            input("Press Enter to return to menu...")
            self.state = MenuState.MAIN_MENU
    
    def _continue_learning(self):
        """Continue from last lesson or find next"""
        # Try to resume current lesson
        if self.progress.progress.current_lesson:
            lesson_data = self.curriculum.get_lesson(self.progress.progress.current_lesson)
            if lesson_data:
                self.current_lesson, self.current_module = lesson_data
                self.state = MenuState.VIEW_LESSON
                return
        
        # Find next uncompleted lesson
        next_lesson_data = self.curriculum.get_next_lesson(
            None,
            self.progress.progress.completed
        )
        
        if next_lesson_data:
            self.current_lesson, self.current_module = next_lesson_data
            self.progress.set_current_lesson(self.current_lesson.id)
            self.state = MenuState.VIEW_LESSON
        else:
            print(self.formatter.success("\n🎉 All lessons completed!"))
            input("Press Enter to continue...")
    
    def _handle_notes(self):
        """Handle notes management"""
        self.notes_viewer.view_all_notes()
        self.state = MenuState.MAIN_MENU
    
    def _handle_progress(self):
        """Handle progress display"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        total_lessons = self.curriculum.get_total_lessons()
        progress = self.progress.progress
        percentage = progress.get_completion_percentage(total_lessons)
        
        print(self.formatter.header("📊 Your Progress", level=1))
        print()
        
        # Progress bar
        bar_length = 40
        filled = int(bar_length * percentage / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"Overall: [{bar}] {percentage:.1f}%")
        print()
        
        # Stats
        print(f"User: {progress.user}")
        print(f"Level: {progress.level}")
        print(f"Score: {progress.score} points")
        print(f"Completed: {len(progress.completed)}/{total_lessons} lessons")
        print(f"Total Time: {progress.total_time} minutes")
        print(f"Last Accessed: {progress.last_accessed or 'Never'}")
        
        if progress.achievements:
            print(f"\n🏆 Achievements: {', '.join(progress.achievements)}")
        
        print()
        input("Press Enter to continue...")
        self.state = MenuState.MAIN_MENU
    
    def _handle_settings(self):
        """Handle settings menu"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(self.formatter.header("⚙️ Settings", level=1))
        print()
        print("1. Reset Progress")
        print("2. Change Difficulty")
        print("3. Export Data")
        print("0. Back")
        print()
        
        choice = input("Your choice: ").strip()
        
        if choice == "1":
            confirm = input("Reset all progress? (yes/no): ")
            if confirm.lower() == "yes":
                self.progress.reset()
                print(self.formatter.success("✅ Progress reset!"))
                input("Press Enter to continue...")
        elif choice == "2":
            print("Difficulty levels: beginner, intermediate, advanced")
            level = input("New difficulty: ").strip().lower()
            if level in ["beginner", "intermediate", "advanced"]:
                self.progress.update_preference("difficulty", level)
                print(self.formatter.success(f"✅ Difficulty set to {level}"))
                input("Press Enter to continue...")
        
        self.state = MenuState.MAIN_MENU
    
    def _show_practice_problems(self):
        """Show practice problems interface"""
        print()
        print(self.formatter.info("💡 Practice problems coming soon!"))
        print("This feature will include:")
        print("  • Algorithm challenges")
        print("  • Time/space complexity exercises")
        print("  • Real-world problems")
        input("\nPress Enter to continue...")
    
    def _show_lesson_practice(self):
        """Show practice for current lesson"""
        if not self.current_lesson:
            return
        
        print()
        print(self.formatter.header(f"💡 Practice: {self.current_lesson.title}", level=2))
        print(f"Available problems: {self.current_lesson.practice_problems}")
        print()
        print("Practice problems coming soon!")
        input("\nPress Enter to continue...")
    
    def _show_claude_guide(self):
        """Show Claude AI integration guide"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        guide = """
🤖 CLAUDE AI LEARNING GUIDE

How to use Claude with your learning:

1. ASK FOR EXPLANATIONS
   • "Explain binary search with examples"
   • "Why is quicksort O(n log n)?"

2. REQUEST IMPLEMENTATIONS
   • "Show me linked list in Python"
   • "Write recursive fibonacci"

3. DEBUG YOUR CODE
   • "Why doesn't my merge sort work?"
   • "Help optimize this algorithm"

4. PRACTICE PROBLEMS
   • "Give me 5 array problems"
   • "Create a graph challenge"

5. INTERVIEW PREP
   • "Common sorting questions"
   • "Explain complexity tradeoffs"

Tips:
• Be specific with questions
• Ask for step-by-step explanations
• Request multiple approaches
• Ask about edge cases
"""
        
        print(self.formatter.header("🤖 Claude AI Guide", level=1))
        print(self.formatter.box(guide, title="Learning with Claude", style="rounded"))
        input("\nPress Enter to continue...")
    
    def _handle_exit(self):
        """Handle exit and cleanup"""
        self.progress.save()
        print()
        print(self.formatter.success("👋 Thanks for learning! See you next time!"))
        print(f"You completed {len(self.progress.progress.completed)} lessons")
        print(f"Total score: {self.progress.progress.score} points")
        self.running = False


def main():
    """Main entry point"""
    cli = UnifiedCLI()
    cli.run()


if __name__ == "__main__":
    main()