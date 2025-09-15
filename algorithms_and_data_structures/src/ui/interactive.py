#!/usr/bin/env python3
"""
Interactive Learning Session - Rich UI with Note-taking and Progress Tracking

This module provides a comprehensive interactive learning environment with:
- Beautiful ASCII art and color formatting
- Real-time note-taking during lessons
- Post-lesson review options
- Progress tracking and visualization
- Interactive quizzes and challenges
- Session summaries and exports
"""

import os
import sys
import json
import time
import asyncio
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    # Try to use the enhanced formatter first
    from .formatter.enhanced_formatter import EnhancedFormatter, Color, HeaderStyle
    from .formatter import TerminalFormatter, Theme
    USE_ENHANCED = True
except ImportError:
    # Fallback to original formatter
    from .formatter import TerminalFormatter, Theme, Color
    USE_ENHANCED = False

# Import content processor for proper text rendering
try:
    from ..utils.content_processor import ContentProcessor
    CONTENT_PROCESSOR_AVAILABLE = True
except ImportError:
    CONTENT_PROCESSOR_AVAILABLE = False

# Import new components
try:
    from .components import (
        COMPONENTS_AVAILABLE, GradientText, GradientPreset, 
        InputPrompt, MenuSelector, ask_text, ask_choice, ask_confirm,
        LoadingAnimation, SpinnerStyle, sparkline
    )
except ImportError:
    COMPONENTS_AVAILABLE = False


class LearningMode(Enum):
    """Learning mode options"""
    LESSON = "lesson"
    PRACTICE = "practice"
    QUIZ = "quiz"
    REVIEW = "review"
    NOTES = "notes"


@dataclass
class LessonNote:
    """Individual note taken during a lesson"""
    timestamp: str
    topic: str
    content: str
    tags: List[str] = field(default_factory=list)
    importance: int = 1  # 1-5 scale


@dataclass
class SessionProgress:
    """Track session progress"""
    lessons_completed: int = 0
    concepts_learned: List[str] = field(default_factory=list)
    notes_taken: int = 0
    quiz_score: float = 0.0
    time_spent_minutes: float = 0.0
    achievements: List[str] = field(default_factory=list)


class InteractiveSession:
    """Rich interactive learning session with full UI capabilities"""
    
    def __init__(self, cli_engine=None):
        """Initialize interactive session with all features"""
        if USE_ENHANCED:
            self.enhanced_formatter = EnhancedFormatter()
            self.formatter = TerminalFormatter()  # Keep for compatibility
        else:
            self.formatter = TerminalFormatter()
            self.enhanced_formatter = None
            
        self.cli_engine = cli_engine
        self.notes: List[LessonNote] = []
        self.progress = SessionProgress()
        self.session_start = datetime.now()
        self.current_topic = ""
        self.mode = LearningMode.LESSON
        
        # Paths for data persistence
        self.notes_dir = Path("notes")
        self.progress_file = Path("progress.json")
        self.notes_dir.mkdir(exist_ok=True)
        
        # UI customization
        if USE_ENHANCED:
            # Enhanced formatter doesn't use Theme class, colors are built-in
            pass
        else:
            self.theme = Theme(
                primary=Color.BRIGHT_CYAN,
                secondary=Color.BRIGHT_MAGENTA,
                success=Color.BRIGHT_GREEN,
                warning=Color.BRIGHT_YELLOW,
                error=Color.BRIGHT_RED,
                info=Color.BRIGHT_BLUE,
                muted=Color.BRIGHT_BLACK,
                text=Color.WHITE
            )
            self.formatter.theme = self.theme
        
        # Initialize enhanced components
        if COMPONENTS_AVAILABLE:
            self.input_prompt = InputPrompt(color_enabled=self.formatter.color_enabled)
            self.gradient = GradientText(color_enabled=self.formatter.color_enabled)
        else:
            self.input_prompt = None
            self.gradient = None
        
        # Command history for navigation
        self.command_history: List[str] = []
        self.current_menu_index = 0
    
    async def run(self):
        """Main interactive session loop"""
        await self.show_welcome()
        
        while True:
            try:
                choice = await self.show_main_menu()
                
                if choice == "1":
                    await self.start_lesson_mode()
                elif choice == "2":
                    await self.practice_mode()
                elif choice == "3":
                    await self.quiz_mode()
                elif choice == "4":
                    await self.review_notes()
                elif choice == "5":
                    await self.view_progress()
                elif choice == "6":
                    await self.export_session()
                elif choice.lower() in ["q", "quit", "exit"]:
                    await self.end_session()
                    break
                else:
                    print(self.formatter.warning("Invalid choice. Please try again."))
                    await asyncio.sleep(1)  # Brief pause before showing menu again
                    
            except KeyboardInterrupt:
                print("\n" + self.formatter.info("Session interrupted. Saving progress..."))
                await self.save_progress()
                break
            except EOFError:
                # Handle EOF gracefully (e.g., when input is piped)
                print("\n" + self.formatter.info("No input detected. Exiting session..."))
                await self.save_progress()
                break
            except Exception as e:
                print(self.formatter.error(f"An error occurred: {e}"))
                # Only continue if it's not a critical error
                if "EOF" in str(e):
                    break
                await asyncio.sleep(1)  # Brief pause before retrying
    
    async def show_welcome(self):
        """Display beautiful welcome screen with ASCII art"""
        self.clear_screen()
        
        # Enhanced ASCII Art Banner with proper formatting
        title = "ALGORITHMS PROFESSOR"
        subtitle = "Interactive Learning Environment"
        
        # Apply gradient to title if components available
        if COMPONENTS_AVAILABLE and self.gradient:
            title = self.gradient.gradient_text(title, GradientPreset.CYBERPUNK)
        
        # Use the new header with banner style
        print(self.formatter.header(title, level=1, style="banner", subtitle=subtitle))
        
        # Add a decorative frame below using ASCII characters
        welcome_frame = """
        +================================================================+
        |                  Welcome to Your Journey!                     |
        |                                                                |
        |         Where Complex Concepts Become Crystal Clear           |
        +================================================================+
        """
        print(self.formatter._colorize(welcome_frame, Color.BRIGHT_CYAN))
        
        # Welcome message with animation
        welcome_msg = "Welcome to your personalized algorithms learning journey!"
        subtitle = "Where complex concepts become crystal clear"
        
        print(self.formatter._colorize(welcome_msg.center(73), Color.BRIGHT_YELLOW))
        print(self.formatter._colorize(subtitle.center(73), Color.BRIGHT_MAGENTA))
        
        # Feature highlights
        print("\n" + self.formatter.header("✨ Session Features", level=2))
        
        features = [
            "📚 Interactive lessons with real-world examples",
            "📝 Real-time note-taking system",
            "🎯 Practice problems and challenges",
            "🧠 Adaptive quizzes to test understanding",
            "📊 Visual progress tracking",
            "💾 Session summaries and exports",
            "🏆 Achievement system"
        ]
        
        for feature in features:
            print(self.formatter._colorize(f"  {feature}", Color.BRIGHT_GREEN))
            await asyncio.sleep(0.1)  # Animated appearance
        
        print("\n" + self.formatter.rule(char="="))
        input(self.formatter._colorize("\nPress Enter to begin your learning journey...", 
                                       Color.BRIGHT_YELLOW))
    
    async def show_main_menu(self) -> str:
        """Display the main interactive menu"""
        self.clear_screen()
        
        # Enhanced header with session info using new panel system
        session_time = (datetime.now() - self.session_start).seconds // 60
        
        # Create session stats section
        stats_content = f"""Session Time: {session_time:3d} min    Notes Taken: {len(self.notes):3d}    Progress: {self.calculate_progress():3.0f}%"""
        
        # Use the new panel feature
        sections = [
            ("📊 Current Session Statistics", stats_content),
        ]
        
        self.formatter.panel(sections, title="MAIN LEARNING MENU")
        
        # Add a decorative rule
        self.formatter.rule(style="gradient")
        
        # Enhanced menu with better formatting and frames
        print(self.formatter._colorize("\n📋 Choose Your Learning Path:", Color.BRIGHT_CYAN, Color.BOLD))
        
        options = [
            ("1", "📚", "Start Learning Session", "Begin a new algorithm lesson"),
            ("2", "💪", "Practice Mode", "Solve practice problems"),
            ("3", "🧠", "Take a Quiz", "Test your understanding"),
            ("4", "📝", "Review Notes", "View and manage your notes"),
            ("5", "📊", "View Progress", "Check your learning statistics"),
            ("6", "💾", "Export Session", "Save your work"),
            ("Q", "🚪", "Exit", "End session and save progress")
        ]
        
        # Create a formatted menu with better visual hierarchy
        for key, icon, title, desc in options:
            # Create a mini-box for each option
            option_box = f"""
    ╭─[{key}]─────────────────────────────────────────────────────╮
    | {icon}  {title:<30} |
    |     {desc:<40} |
    ╰────────────────────────────────────────────────────────────╯"""
            
            if key == "Q":
                print(self.formatter._colorize(option_box, Color.BRIGHT_RED))
            else:
                print(self.formatter._colorize(option_box, Color.BRIGHT_GREEN))
        
        print("\n" + self.formatter.rule(char="=", style="double"))
        
        # Input prompt with color
        choice = input(self.formatter._colorize("\n➤ Enter your choice: ", 
                                               Color.BRIGHT_GREEN, Color.BOLD))
        
        return choice.strip()
    
    async def start_lesson_mode(self):
        """Interactive lesson mode with note-taking"""
        self.mode = LearningMode.LESSON
        self.clear_screen()
        
        print(self.formatter.header("📚 LESSON MODE", level=1))
        
        # Show available topics
        if self.cli_engine and hasattr(self.cli_engine, 'curriculum'):
            topics = list(self.cli_engine.curriculum.topics.keys())
            
            print(self.formatter._colorize("\nAvailable Topics:", Color.BRIGHT_CYAN, Color.BOLD))
            for i, topic in enumerate(topics[:10], 1):
                print(f"  {self.formatter._colorize(f'{i}.', Color.BRIGHT_YELLOW)} {topic}")
            
            choice = input(self.formatter._colorize("\nSelect topic (1-10): ", Color.BRIGHT_GREEN))
            
            try:
                topic_idx = int(choice) - 1
                if 0 <= topic_idx < len(topics):
                    self.current_topic = topics[topic_idx]
                    await self.run_lesson_with_notes(self.current_topic)
            except (ValueError, IndexError):
                print(self.formatter.warning("Invalid selection"))
    
    async def run_lesson_with_notes(self, topic: str):
        """Run a lesson with note-taking capability"""
        # Use banner style header for the lesson
        print(self.formatter.header(f"📖 {topic}", level=2, style="banner"))
        
        # Get actual curriculum content if available
        if self.cli_engine and hasattr(self.cli_engine, 'curriculum'):
            topic_data = self.cli_engine.curriculum.topics.get(topic, {})
            lesson_content = topic_data.get('content', [])
            
            # If no content, use default examples
            if not lesson_content:
                lesson_content = self._get_default_lesson_content(topic)
        else:
            lesson_content = self._get_default_lesson_content(topic)
        
        # Display lesson introduction with professor style
        intro_box = self.formatter.box(
            "Welcome to this interactive lesson! I'll guide you through each concept step by step.\n\n"
            "🎯 Press 'n' to take notes\n"
            "➡️ Press Enter to continue\n"
            "🚪 Press 'q' to finish",
            title="✨ Let's Begin Your Learning Journey",
            style="double",
            padding=2,
            color=self.formatter.theme.primary if hasattr(self.formatter, 'theme') else None
        )
        print(intro_box)
        
        for i, content in enumerate(lesson_content):
            # Display content with enhanced formatting
            self.display_formatted_content(content, i + 1, len(lesson_content))
            
            # Allow note-taking with enhanced formatting
            self.display_lesson_controls()
            
            action = input("➤ ").lower()
            
            if action == 'n':
                await self.take_note(topic)
            elif action == 'q':
                break
        
        # Post-lesson options
        await self.post_lesson_review(topic)
    
    def _get_default_lesson_content(self, topic: str) -> List[str]:
        """Get default lesson content with professor-style explanations"""
        # Check if we're dealing with Big O complexity topic
        if "big o" in topic.lower() or "complexity" in topic.lower():
            if CONTENT_PROCESSOR_AVAILABLE:
                big_o_content = ContentProcessor.format_big_o_content()
                return [
                    f"{big_o_content['sections'][0]['header']}\n\n{big_o_content['sections'][0]['content']}",
                    f"{big_o_content['sections'][1]['header']}\n\n{big_o_content['sections'][1]['content']}",
                    f"{big_o_content['sections'][2]['header']}\n\n{big_o_content['sections'][2]['content']}",
                    f"{big_o_content['sections'][3]['header']}\n\n{big_o_content['sections'][3]['content']}",
                    f"🎓 Key Takeaway:\n\n{big_o_content['key_takeaway']}"
                ]
        
        # Default content for other topics
        return [
            f"🌟 Why {topic} Matters:\n\n"
            "In your daily life, you already use this concept when organizing your tasks. "
            "Think about how you prioritize your to-do list - that's an algorithm! "
            "Today, we'll see how computers use similar thinking to solve problems efficiently.",
            
            f"🎯 Real-World Analogy:\n\n"
            f"Imagine you're organizing books in a library. You could randomly place them on shelves, "
            "but finding a specific book would take forever! Instead, libraries use classification systems "
            f"(like the Dewey Decimal System) - that's exactly what we're learning with {topic}.",
            
            f"💡 The Key Insight:\n\n"
            f"The brilliant thing about {topic} is that it transforms a complex problem into something manageable. "
            "Instead of checking every possibility (which could take years), we use clever shortcuts "
            "that get us the answer in seconds. It's like having a map instead of wandering randomly!",
            
            f"🔍 Let's Try It Together:\n\n"
            "Here's a concrete example you can relate to: Suppose you're looking for a friend's phone number "
            "in your contacts. You don't read every single name from A to Z - you jump to approximately where "
            f"their name should be. That's the same principle behind {topic}!",
            
            f"🏆 What You've Learned:\n\n"
            f"You now understand that {topic} is not just abstract computer science - it's a practical tool "
            "that makes impossible problems solvable. You can apply this thinking to optimize anything from "
            "your daily routines to complex business processes. Well done!"
        ]
    
    async def take_note(self, topic: str):
        """Take a note during the lesson"""
        # Display note-taking interface with enhanced formatting
        self.formatter.box(
            content=f"📝 Creating Note for Topic: {topic}",
            title="✍️ Note Taking Mode",
            style="single",
            padding=2,
            color=Color.BRIGHT_YELLOW
        )
        
        note_content = input(self.formatter._colorize("Your note: ", Color.BRIGHT_GREEN))
        
        if note_content:
            # Get tags
            tags_input = input(self.formatter._colorize("Tags (comma-separated, optional): ", 
                                                       Color.BRIGHT_BLUE))
            tags = [tag.strip() for tag in tags_input.split(',')] if tags_input else []
            
            # Get importance
            importance_input = input(self.formatter._colorize("Importance (1-5, default 3): ", 
                                                             Color.BRIGHT_MAGENTA))
            try:
                importance = int(importance_input) if importance_input else 3
                importance = max(1, min(5, importance))
            except ValueError:
                importance = 3
            
            # Create and save note
            note = LessonNote(
                timestamp=datetime.now().isoformat(),
                topic=topic,
                content=note_content,
                tags=tags,
                importance=importance
            )
            
            self.notes.append(note)
            
            # Visual confirmation
            stars = "⭐" * importance
            print(self.formatter.success(f"Note saved! {stars}"))
            
            self.progress.notes_taken += 1
    
    async def post_lesson_review(self, topic: str):
        """Post-lesson review options"""
        self.clear_screen()
        
        print(self.formatter.header("✅ Lesson Complete!", level=1))
        
        # Enhanced lesson summary with better formatting
        notes_count = len([n for n in self.notes if n.topic == topic])
        summary_content = f"""Topic Completed: {topic}

Notes Captured: {notes_count}
Estimated Duration: ~5 minutes
Understanding Level: Good"""
        
        print(self.formatter.box(
            summary_content,
            title="✅ Lesson Summary",
            style="double",
            padding=3,
            align="left",
            color=Color.BRIGHT_GREEN
        ))
        
        # Post-lesson options
        print(self.formatter._colorize("\n📋 What would you like to do next?", 
                                       Color.BRIGHT_CYAN, Color.BOLD))
        
        options = [
            "1. Review your notes",
            "2. Try a practice problem",
            "3. Take a quick quiz",
            "4. Export lesson summary",
            "5. Continue to next topic",
            "6. Return to main menu"
        ]
        
        for option in options:
            print(self.formatter._colorize(f"  {option}", Color.WHITE))
        
        choice = input(self.formatter._colorize("\n➤ Choice: ", Color.BRIGHT_GREEN))
        
        if choice == "1":
            await self.review_notes(topic_filter=topic)
        elif choice == "2":
            await self.practice_mode(topic)
        elif choice == "3":
            await self.quiz_mode(topic)
        elif choice == "4":
            await self.export_lesson_summary(topic)
        
        # Update progress
        if topic not in self.progress.concepts_learned:
            self.progress.concepts_learned.append(topic)
            self.progress.lessons_completed += 1
    
    async def practice_mode(self, topic: Optional[str] = None):
        """Practice problem solving mode"""
        self.mode = LearningMode.PRACTICE
        
        try:
            # Clear screen with error handling
            self.clear_screen()
            
            print(self.formatter.header("💪 PRACTICE MODE", level=1))
            
            # Enhanced practice problem presentation
            problem_content = """Given an array of integers, find two numbers that add
up to a specific target sum.

Example:
  Input:  nums = [2, 7, 11, 15], target = 9
  Output: [0, 1] (because nums[0] + nums[1] = 9)

Constraints:
  • Each input has exactly one solution
  • You may not use the same element twice
  • Return indices of the two numbers"""
            
            print(self.formatter.box(
                problem_content,
                title="💡 Practice Problem: Two Sum",
                style="heavy",
                padding=2,
                width=70,
                align="left",
                color=Color.BRIGHT_CYAN
            ))
            
            # Hints system
            print(self.formatter._colorize("\n💡 Need help? Type 'hint' for guidance", 
                                           Color.BRIGHT_YELLOW))
            
            # Use a more robust input prompt
            print(self.formatter._colorize("\n➤ Press Enter when ready to see the solution...", 
                                           Color.BRIGHT_GREEN))
            sys.stdin.readline()
        except Exception as e:
            print(self.formatter.error(f"Error in practice mode: {e}"))
        
        # Show solution with explanation
        await self.show_practice_solution()
    
    async def show_practice_solution(self):
        """Show practice problem solution with explanation"""
        print(self.formatter.header("Solution", level=2))
        
        # Step-by-step solution
        steps = [
            ("Approach 1: Brute Force", "Check every pair of numbers", "O(n²)"),
            ("Approach 2: Hash Map", "Use a dictionary to store complements", "O(n)"),
            ("Optimal Solution", "Single pass with hash map", "O(n) time, O(n) space")
        ]
        
        for i, (title, desc, complexity) in enumerate(steps, 1):
            step_content = f"{desc}\n\nComplexity: {complexity}"
            self.formatter.box(
                content=step_content,
                title=f"🔍 Step {i}: {title}",
                style="single",
                padding=2,
                color=Color.BRIGHT_GREEN
            )
        
        # Code solution
        code = """
def two_sum(nums, target):
    seen = {}  # Hash map to store values
    
    for i, num in enumerate(nums):
        complement = target - num
        
        if complement in seen:
            return [seen[complement], i]
        
        seen[num] = i  # Store index
    
    return []  # No solution found
        """
        
        # Enhanced code display with syntax highlighting
        highlighted_code = self.formatter.syntax_highlight(code.strip(), "python")
        self.formatter.box(
            highlighted_code, 
            title="🐍 Python Solution", 
            style="double",
            padding=2,
            width=70,
            align="left",
            color=Color.BRIGHT_GREEN
        )
    
    async def quiz_mode(self, topic: Optional[str] = None):
        """Interactive quiz mode"""
        self.mode = LearningMode.QUIZ
        self.clear_screen()
        
        print(self.formatter.header("🧠 QUIZ MODE", level=1))
        
        questions = [
            {
                "question": "What is the time complexity of binary search?",
                "options": ["O(n)", "O(log n)", "O(n²)", "O(1)"],
                "correct": 1,
                "explanation": "Binary search divides the search space in half with each step"
            },
            {
                "question": "Which data structure uses LIFO principle?",
                "options": ["Queue", "Stack", "Array", "Tree"],
                "correct": 1,
                "explanation": "Stack follows Last In, First Out (LIFO) principle"
            }
        ]
        
        score = 0
        total = len(questions)
        
        for i, q in enumerate(questions, 1):
            # Enhanced quiz question display
            question_content = f"{q['question']}\n\n" + "\n".join([
                f"  {j+1}. {option}" for j, option in enumerate(q['options'])
            ])
            
            self.formatter.box(
                content=question_content,
                title=f"🤔 Question {i} of {total}",
                style="double",
                padding=2,
                color=Color.BRIGHT_CYAN
            )
            
            answer = input(self.formatter._colorize("\nYour answer (1-4): ", Color.BRIGHT_GREEN))
            
            try:
                answer_idx = int(answer) - 1
                if answer_idx == q['correct']:
                    print(self.formatter.success("Correct! "))
                    score += 1
                else:
                    print(self.formatter.error(f"Incorrect. {q['explanation']}"))
            except (ValueError, IndexError):
                print(self.formatter.warning("Invalid answer"))
        
        # Quiz results
        percentage = (score / total) * 100
        self.progress.quiz_score = percentage
        
        print(self.formatter.box(
            f"Score: {score}/{total} ({percentage:.0f}%)\n"
            f"Great job!" if percentage >= 70 else "Keep practicing!",
            title="Quiz Results",
            style="double"
        ))
    
    async def review_notes(self, topic_filter: Optional[str] = None):
        """Review and manage notes"""
        self.mode = LearningMode.NOTES
        self.clear_screen()
        
        print(self.formatter.header("📝 YOUR NOTES", level=1))
        
        # Filter notes if topic specified
        notes_to_show = self.notes
        if topic_filter:
            notes_to_show = [n for n in self.notes if n.topic == topic_filter]
        
        if not notes_to_show:
            print(self.formatter.info("No notes yet. Take notes during lessons!"))
            input("\nPress Enter to continue...")
            return
        
        # Display notes beautifully
        for i, note in enumerate(notes_to_show, 1):
            stars = "⭐" * note.importance
            timestamp = datetime.fromisoformat(note.timestamp).strftime("%H:%M")
            
            # Enhanced note display with better formatting
            note_content = f"""Note #{i} - {timestamp} {stars}

{note.content[:100]}{'...' if len(note.content) > 100 else ''}

Tags: {', '.join(note.tags) if note.tags else 'None'}"""
            
            # Use different box styles based on importance
            box_style = "double" if note.importance >= 4 else "rounded" if note.importance >= 3 else "single"
            
            note_box = self.formatter.box(
                note_content,
                title=note.topic,
                style=box_style,
                padding=2,
                width=65,
                align="left",
                color=Color.BRIGHT_YELLOW if note.importance >= 4 else Color.WHITE
            )
            
            # Box is already colored by the formatter
            print(note_box)
        
        # Note management options
        print(self.formatter._colorize("\nOptions: [e]xport notes, [d]elete note, [b]ack", 
                                       Color.BRIGHT_BLACK))
        
        action = input("➤ ").lower()
        
        if action == 'e':
            await self.export_notes()
        elif action == 'd':
            note_num = input("Note number to delete: ")
            try:
                idx = int(note_num) - 1
                if 0 <= idx < len(notes_to_show):
                    self.notes.remove(notes_to_show[idx])
                    print(self.formatter.success("Note deleted"))
            except (ValueError, IndexError):
                print(self.formatter.warning("Invalid note number"))
    
    async def view_progress(self):
        """View detailed progress and statistics"""
        self.clear_screen()
        
        print(self.formatter.header("📊 YOUR PROGRESS", level=1))
        
        # Calculate statistics
        session_time = (datetime.now() - self.session_start).seconds / 60
        self.progress.time_spent_minutes = session_time
        
        # Progress visualization
        overall_progress = self.calculate_progress()
        
        # Enhanced progress visualization with frame
        bar_length = 50
        filled = int(bar_length * overall_progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        progress_display = f"""
Progress Overview:

[{bar}] {overall_progress:.0f}%

{'▪' * filled}{' ' * (bar_length - filled)}"""
        
        print(self.formatter.frame(progress_display, style="ornate", margin=2))
        
        # Statistics table
        stats = [
            ("📚 Lessons Completed", str(self.progress.lessons_completed)),
            ("📝 Notes Taken", str(self.progress.notes_taken)),
            ("🧠 Quiz Average", f"{self.progress.quiz_score:.0f}%"),
            ("⏱️ Time Invested", f"{session_time:.0f} minutes"),
            ("🎯 Concepts Learned", str(len(self.progress.concepts_learned))),
            ("🏆 Achievements", str(len(self.progress.achievements)))
        ]
        
        for label, value in stats:
            label_colored = self.formatter._colorize(label, Color.BRIGHT_CYAN)
            value_colored = self.formatter._colorize(value, Color.BRIGHT_YELLOW, Color.BOLD)
            print(f"  {label_colored}: {value_colored}")
        
        # Achievement badges
        if self.progress.achievements:
            print(self.formatter.header("🏆 Achievements", level=2))
            for achievement in self.progress.achievements:
                print(f"  ✨ {achievement}")
        
        # Learning streak
        print(self.formatter.header("🔥 Learning Insights", level=2))
        
        if self.progress.notes_taken >= 10:
            print(self.formatter._colorize("  📝 Note-taking Master - 10+ notes!", Color.BRIGHT_GREEN))
        
        if self.progress.quiz_score >= 80:
            print(self.formatter._colorize("  🧠 Quiz Champion - 80%+ average!", Color.BRIGHT_GREEN))
        
        if session_time >= 30:
            print(self.formatter._colorize("  ⏰ Dedicated Learner - 30+ minutes!", Color.BRIGHT_GREEN))
        
        input("\nPress Enter to continue...")
    
    async def export_session(self):
        """Export session data"""
        self.clear_screen()
        
        print(self.formatter.header("💾 EXPORT SESSION", level=1))
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export options
        print(self.formatter._colorize("Export Options:", Color.BRIGHT_CYAN, Color.BOLD))
        print("  1. Export notes to markdown")
        print("  2. Export progress report")
        print("  3. Export full session data")
        print("  4. Cancel")
        
        choice = input(self.formatter._colorize("\n➤ Choice: ", Color.BRIGHT_GREEN))
        
        if choice == "1":
            await self.export_notes()
        elif choice == "2":
            await self.export_progress_report()
        elif choice == "3":
            await self.export_full_session()
    
    async def export_notes(self):
        """Export notes to markdown file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.notes_dir / f"notes_{timestamp}.md"
        
        with open(filename, 'w') as f:
            f.write("# Learning Notes\n\n")
            f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")
            
            # Group notes by topic
            topics = {}
            for note in self.notes:
                if note.topic not in topics:
                    topics[note.topic] = []
                topics[note.topic].append(note)
            
            for topic, topic_notes in topics.items():
                f.write(f"## {topic}\n\n")
                for note in topic_notes:
                    stars = "⭐" * note.importance
                    f.write(f"### {stars} {datetime.fromisoformat(note.timestamp).strftime('%H:%M')}\n")
                    f.write(f"{note.content}\n")
                    if note.tags:
                        f.write(f"*Tags: {', '.join(note.tags)}*\n")
                    f.write("\n")
        
        print(self.formatter.success(f"Notes exported to {filename}"))
        input("\nPress Enter to continue...")
    
    async def export_progress_report(self):
        """Export progress report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = Path(f"progress_report_{timestamp}.md")
        
        with open(filename, 'w') as f:
            f.write("# Learning Progress Report\n\n")
            f.write(f"*Session Date: {datetime.now().strftime('%Y-%m-%d')}*\n\n")
            
            f.write("## Statistics\n\n")
            f.write(f"- **Lessons Completed:** {self.progress.lessons_completed}\n")
            f.write(f"- **Notes Taken:** {self.progress.notes_taken}\n")
            f.write(f"- **Quiz Score:** {self.progress.quiz_score:.0f}%\n")
            f.write(f"- **Time Spent:** {self.progress.time_spent_minutes:.0f} minutes\n")
            f.write(f"- **Concepts Learned:** {len(self.progress.concepts_learned)}\n\n")
            
            if self.progress.concepts_learned:
                f.write("## Topics Covered\n\n")
                for concept in self.progress.concepts_learned:
                    f.write(f"- {concept}\n")
            
            if self.progress.achievements:
                f.write("\n## Achievements\n\n")
                for achievement in self.progress.achievements:
                    f.write(f"- 🏆 {achievement}\n")
        
        print(self.formatter.success(f"Progress report exported to {filename}"))
        input("\nPress Enter to continue...")
    
    async def export_full_session(self):
        """Export complete session data as JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = Path(f"session_{timestamp}.json")
        
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "duration_minutes": self.progress.time_spent_minutes,
            "progress": asdict(self.progress),
            "notes": [asdict(note) for note in self.notes]
        }
        
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        print(self.formatter.success(f"Session data exported to {filename}"))
        input("\nPress Enter to continue...")
    
    async def export_lesson_summary(self, topic: str):
        """Export summary for a specific lesson"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = Path(f"lesson_{topic.replace(' ', '_')}_{timestamp}.md")
        
        topic_notes = [n for n in self.notes if n.topic == topic]
        
        with open(filename, 'w') as f:
            f.write(f"# Lesson Summary: {topic}\n\n")
            f.write(f"*Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")
            
            f.write("## Key Takeaways\n\n")
            for note in topic_notes:
                if note.importance >= 4:
                    f.write(f"- {note.content}\n")
            
            f.write("\n## All Notes\n\n")
            for note in topic_notes:
                f.write(f"- {note.content}\n")
                if note.tags:
                    f.write(f"  *Tags: {', '.join(note.tags)}*\n")
        
        print(self.formatter.success(f"Lesson summary exported to {filename}"))
    
    def calculate_progress(self) -> float:
        """Calculate overall progress percentage"""
        factors = []
        
        # Lessons progress (assuming 20 total topics)
        if self.cli_engine and hasattr(self.cli_engine, 'curriculum'):
            total_topics = len(self.cli_engine.curriculum.topics)
            lesson_progress = (self.progress.lessons_completed / total_topics) * 100
            factors.append(lesson_progress)
        
        # Notes progress (assuming 50 notes is good coverage)
        notes_progress = min((self.progress.notes_taken / 50) * 100, 100)
        factors.append(notes_progress)
        
        # Quiz performance
        if self.progress.quiz_score > 0:
            factors.append(self.progress.quiz_score)
        
        # Time investment (assuming 120 minutes is good)
        time_progress = min((self.progress.time_spent_minutes / 120) * 100, 100)
        factors.append(time_progress)
        
        return sum(factors) / len(factors) if factors else 0
    
    async def save_progress(self):
        """Save progress to file"""
        progress_data = asdict(self.progress)
        
        # Load existing progress if it exists
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                existing = json.load(f)
                
                # Merge progress
                progress_data['lessons_completed'] += existing.get('lessons_completed', 0)
                progress_data['notes_taken'] += existing.get('notes_taken', 0)
                
                # Combine concept lists
                existing_concepts = existing.get('concepts_learned', [])
                for concept in existing_concepts:
                    if concept not in progress_data['concepts_learned']:
                        progress_data['concepts_learned'].append(concept)
        
        # Save updated progress
        with open(self.progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)
        
        print(self.formatter.success("Progress saved!"))
    
    async def end_session(self):
        """End the session with summary"""
        self.clear_screen()
        
        # Save progress
        await self.save_progress()
        
        # Session summary
        print(self.formatter.header("👋 SESSION COMPLETE", level=1))
        
        session_time = (datetime.now() - self.session_start).seconds / 60
        
        # Enhanced session summary with panels
        session_stats = f"""Duration: {session_time:6.0f} minutes
Lessons Completed: {self.progress.lessons_completed:3d}
Notes Taken: {self.progress.notes_taken:3d}
Overall Progress: {self.calculate_progress():5.1f}%"""
        
        achievements_text = "\n".join(self.progress.achievements[:3]) if self.progress.achievements else "Keep learning to unlock achievements!"
        
        sections = [
            ("📊 Session Statistics", session_stats),
            ("🏆 Recent Achievements", achievements_text)
        ]
        
        self.formatter.panel(sections, title="SESSION COMPLETE")
        
        # Motivational message
        if session_time >= 30:
            print(self.formatter._colorize("\n🌟 Excellent dedication! You're making great progress!", 
                                          Color.BRIGHT_YELLOW, Color.BOLD))
        elif session_time >= 15:
            print(self.formatter._colorize("\n👍 Good session! Keep up the momentum!", 
                                          Color.BRIGHT_GREEN, Color.BOLD))
        else:
            print(self.formatter._colorize("\n💪 Every step counts! See you next time!", 
                                          Color.BRIGHT_BLUE, Color.BOLD))
        
        # Check for new achievements
        self.check_achievements()
        
        print(self.formatter._colorize("\nThank you for learning with us today!", 
                                       Color.BRIGHT_MAGENTA))
        print(self.formatter.rule(title="Thank You", char="=", style="double"))
    
    def display_formatted_content(self, content: str, current_step: int, total_steps: int):
        """Display lesson content with enhanced formatting"""
        # Process content to remove escape sequences and format properly
        if CONTENT_PROCESSOR_AVAILABLE:
            processed_content = ContentProcessor.format_lesson_content(content)
        else:
            # Fallback: basic cleaning if processor not available
            processed_content = content.replace('\\n', '\n').replace('\\t', '    ')
        
        # Create a beautiful content box with step indicator
        step_indicator = f"Step {current_step} of {total_steps}"
        
        # Display the processed content properly
        print(f"\n{self.formatter._colorize('─' * 70, Color.BRIGHT_CYAN)}")
        print(self.formatter._colorize(f"📚 {step_indicator}", Color.BRIGHT_YELLOW, Color.BOLD))
        print(self.formatter._colorize('─' * 70, Color.BRIGHT_CYAN))
        print()
        
        # Display the cleaned content without box to avoid formatting issues
        print(processed_content)
        
        # Add progress visualization
        print()
        progress_percent = (current_step / total_steps) * 100
        bar_length = 50
        filled = int(bar_length * current_step / total_steps)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"Progress: [{bar}] {progress_percent:.0f}%")
        print(self.formatter._colorize('─' * 70, Color.BRIGHT_CYAN))
    
    def display_lesson_controls(self):
        """Display lesson navigation controls with enhanced formatting"""
        controls_content = (
            "📝 [n] Take a note about this concept\n"
            "▶️  [c] Continue to next step\n" 
            "🚪 [q] Finish this lesson"
        )
        
        self.formatter.box(
            content=controls_content,
            title="⚡ Quick Actions",
            style="single",
            padding=1,
            align="left", 
            color=Color.BRIGHT_YELLOW
        )

    def check_achievements(self):
        """Check and award achievements"""
        new_achievements = []
        
        if self.progress.notes_taken >= 10 and "Note Taker" not in self.progress.achievements:
            self.progress.achievements.append("Note Taker")
            new_achievements.append("Note Taker - Took 10+ notes!")
        
        if self.progress.lessons_completed >= 5 and "Dedicated Learner" not in self.progress.achievements:
            self.progress.achievements.append("Dedicated Learner")
            new_achievements.append("Dedicated Learner - Completed 5+ lessons!")
        
        if self.progress.quiz_score >= 90 and "Quiz Master" not in self.progress.achievements:
            self.progress.achievements.append("Quiz Master")
            new_achievements.append("Quiz Master - Scored 90%+ on quiz!")
        
        if new_achievements:
            print(self.formatter.header("🏆 NEW ACHIEVEMENTS UNLOCKED!", level=2))
            for achievement in new_achievements:
                print(self.formatter._colorize(f"  ✨ {achievement}", Color.BRIGHT_YELLOW))
            print()
    
    def clear_screen(self):
        """Clear the terminal screen safely"""
        try:
            # Try to use ANSI escape codes first (works in most modern terminals)
            print('\033[2J\033[H', end='')
            sys.stdout.flush()
        except Exception:
            # Fallback to system command if ANSI codes don't work
            try:
                os.system('cls' if os.name == 'nt' else 'clear')
            except Exception:
                # Last resort: print newlines
                print('\n' * 50)
    
    def show_transition(self, effect: str = "fade"):
        """Show smooth transition between screens
        
        Args:
            effect: Transition effect type
        """
        if self.formatter.color_enabled and hasattr(self.formatter, 'transition_effect'):
            self.formatter.transition_effect(effect)
    
    def fuzzy_search(self, query: str, options: List[str], threshold: float = 0.6) -> List[str]:
        """Fuzzy search through options
        
        Args:
            query: Search query
            options: List of options to search
            threshold: Similarity threshold
            
        Returns:
            List of matching options
        """
        if not query.strip():
            return options
        
        # Simple substring matching as fallback
        query_lower = query.lower()
        matches = [opt for opt in options if query_lower in opt.lower()]
        
        # If we have difflib available, use fuzzy matching
        try:
            import difflib
            fuzzy_matches = difflib.get_close_matches(query, options, n=10, cutoff=threshold)
            # Combine and deduplicate
            all_matches = list(dict.fromkeys(matches + fuzzy_matches))
            return all_matches[:10]  # Limit results
        except ImportError:
            return matches[:10]
    
    async def enhanced_input(self, prompt: str, suggestions: List[str] = None) -> str:
        """Enhanced input with autocomplete suggestions
        
        Args:
            prompt: Input prompt
            suggestions: List of autocomplete suggestions
            
        Returns:
            User input
        """
        if COMPONENTS_AVAILABLE and self.input_prompt and suggestions:
            return self.input_prompt.autocomplete_input(prompt, suggestions)
        else:
            return input(f"{prompt}: ")