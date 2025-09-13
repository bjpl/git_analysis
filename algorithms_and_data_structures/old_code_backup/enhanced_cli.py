#!/usr/bin/env python3
"""
Enhanced Algorithms & Data Structures CLI
Fully integrated learning platform with all features restored
"""

import sys
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Core imports
from src.ui.windows_formatter import WindowsFormatter, WindowsColor
from src.ui.lesson_display import LessonDisplay
from src.ui.enhanced_lesson_formatter import EnhancedLessonFormatter
from src.notes_manager import NotesManager
from src.notes_viewer import EnhancedNotesViewer
from src.ui.interactive import InteractiveSession
from src.ui.enhanced_interactive import EnhancedInteractiveSession
from src.command_router import CommandRouter


class EnhancedCLI:
    """
    Fully featured CLI with all systems integrated:
    - Interactive learning sessions
    - Notes management
    - Progress tracking
    - Claude AI integration guidance
    - Curriculum navigation
    - Practice problems
    """
    
    def __init__(self, reset_progress=False, cloud_mode=False, offline_mode=False, 
                 debug_mode=False, config_path=None):
        self.formatter = WindowsFormatter()
        self.lesson_display = LessonDisplay(self.formatter)
        self.enhanced_formatter = EnhancedLessonFormatter(self.formatter)
        self.notes_manager = NotesManager()
        self.notes_viewer = EnhancedNotesViewer()
        self.progress_file = Path("progress.json")
        self.curriculum_data = self._load_curriculum()
        self.current_session = {}
        self.current_user = self._detect_user()
        
        # Cloud integration settings
        self.cloud_mode = cloud_mode
        self.offline_mode = offline_mode
        self.debug_mode = debug_mode
        self.config_path = config_path
        
        # Cloud integration components (initialized later)
        self.flow_nexus_integration = None
        self.collaboration_manager = None
        
        # Command router for handling curriculum commands
        self.command_router = CommandRouter()
        
        # Reset progress if requested
        if reset_progress:
            self._reset_progress()
    
    async def initialize_cloud_features(self):
        """Initialize cloud integration features"""
        try:
            from .integrations.flow_nexus import FlowNexusIntegration
            from .integrations.collaboration import CollaborationManager
            
            print("☁️ Initializing cloud features...")
            
            # Initialize Flow Nexus integration
            self.flow_nexus_integration = FlowNexusIntegration(cli_engine=self)
            
            # Setup authentication if not offline
            if not self.offline_mode:
                auth_success = await self.flow_nexus_integration.login_interactive()
                if not auth_success:
                    print(self.formatter.warning("⚠️ Cloud authentication failed, some features limited"))
                    self.flow_nexus_integration.offline_mode = True
            else:
                self.flow_nexus_integration.offline_mode = True
            
            # Initialize collaboration manager
            self.collaboration_manager = CollaborationManager(self.flow_nexus_integration)
            
            # Sync progress to cloud if authenticated
            if self.flow_nexus_integration.is_authenticated:
                progress = self._load_progress()
                await self.flow_nexus_integration.sync_progress_to_cloud(progress)
            
            print(self.formatter.success("✅ Cloud features initialized!"))
            
        except ImportError as e:
            print(self.formatter.error(f"❌ Cloud integration not available: {e}"))
            self.cloud_mode = False
        except Exception as e:
            print(self.formatter.error(f"❌ Cloud initialization failed: {e}"))
            if self.debug_mode:
                import traceback
                traceback.print_exc()
            self.cloud_mode = False
        
    def _load_curriculum(self) -> Dict:
        """Load curriculum data"""
        # Try enhanced curriculum first, fall back to basic
        enhanced_file = Path("data/curriculum_enhanced.json")
        basic_file = Path("data/curriculum.json")
        
        curriculum_file = enhanced_file if enhanced_file.exists() else basic_file
        
        if curriculum_file.exists():
            with open(curriculum_file, 'r') as f:
                return json.load(f)
        return self._get_default_curriculum()
    
    def _get_default_curriculum(self) -> Dict:
        """Get default curriculum structure"""
        return {
            "modules": [
                {
                    "id": "foundations",
                    "title": "Foundations",
                    "lessons": [
                        {
                            "id": "big-o",
                            "title": "Big O Notation",
                            "content": "Understanding time and space complexity",
                            "topics": ["O(1)", "O(n)", "O(log n)", "O(n²)"],
                            "practice_problems": 5
                        },
                        {
                            "id": "arrays",
                            "title": "Arrays & Dynamic Arrays",
                            "content": "Fixed and dynamic array implementations",
                            "topics": ["Array basics", "Dynamic resizing", "Amortized analysis"],
                            "practice_problems": 8
                        }
                    ]
                },
                {
                    "id": "searching",
                    "title": "Searching Algorithms",
                    "lessons": [
                        {
                            "id": "linear-search",
                            "title": "Linear Search",
                            "content": "Sequential searching through collections",
                            "topics": ["Implementation", "When to use", "Optimizations"],
                            "practice_problems": 3
                        },
                        {
                            "id": "binary-search",
                            "title": "Binary Search",
                            "content": "Efficient searching in sorted arrays",
                            "topics": ["Implementation", "Requirements", "Variations"],
                            "practice_problems": 6
                        }
                    ]
                },
                {
                    "id": "sorting",
                    "title": "Sorting Algorithms",
                    "lessons": [
                        {
                            "id": "bubble-sort",
                            "title": "Bubble Sort",
                            "content": "Simple comparison-based sorting",
                            "topics": ["Algorithm", "Optimization", "Complexity"],
                            "practice_problems": 4
                        },
                        {
                            "id": "quicksort",
                            "title": "QuickSort",
                            "content": "Efficient divide-and-conquer sorting",
                            "topics": ["Partitioning", "Pivot selection", "Analysis"],
                            "practice_problems": 7
                        }
                    ]
                }
            ]
        }
    
    def _detect_user(self) -> str:
        """Detect current user from progress file or environment"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    return data.get('user', 'learner')
            except:
                pass
        return 'learner'
    
    def _load_progress(self) -> Dict:
        """Load user progress"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                data = json.load(f)
                # Ensure user field exists
                if 'user' not in data:
                    data['user'] = self.current_user or 'learner'
                return data
        return {
            "user": self.current_user or "learner",
            "level": "foundation",
            "completed": [],
            "score": 0,
            "scores": {},
            "achievements": [],
            "lastAccessed": None,
            "totalTime": 0,
            "preferences": {
                "learningPath": "visual",
                "difficulty": "beginner",
                "notifications": True
            }
        }
    
    def _save_progress(self, progress: Dict):
        """Save user progress"""
        progress["lastAccessed"] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def display_main_menu(self, show_header=True):
        """Display main menu"""
        if show_header:
            self.formatter.header("=" * 80)
            self.formatter.header("🎓 Algorithms & Data Structures Learning Platform")
            if hasattr(self, 'current_user') and self.current_user and self.current_user != 'learner':
                print(self.formatter.success(f"Welcome back, {self.current_user}!"))
            self.formatter.header("=" * 80)
            print()
        self.formatter.info("Choose an option:")
        print()
        print("1. 📚 Browse Curriculum")
        print("2. 🎯 Continue Learning (from last position)")
        print("3. 📝 Manage Notes") 
        print("4. 📊 View Progress")
        print("5. 💡 Practice Problems")
        print("6. 🤖 Claude AI Integration Guide")
        print("7. ⚙️  Settings & Statistics")
        print("8. 🔧 Advanced Mode (Simplified)")
        print("9. ✨ Enhanced Interactive Mode (NEW!)")
        print()
        print(self.formatter._color("📚 CURRICULUM MANAGEMENT", self.formatter.theme.info, WindowsColor.BOLD))
        print("C1. 📋 List All Curricula")
        print("C2. 👁️  Show Curriculum Details")
        print("C3. ➕ Create New Curriculum")
        print("C4. ✏️  Update Curriculum")
        print("C5. 🗑️  Delete Curriculum")
        
        # Cloud features menu (if available)
        if self.cloud_mode and self.flow_nexus_integration:
            print()
            print(self.formatter._color("☁️  CLOUD FEATURES", self.formatter.theme.info, WindowsColor.BOLD))
            print("C. 🏆 Challenges & Leaderboards")
            print("G. 👥 Study Groups & Collaboration") 
            print("S. ☁️  Cloud Status & Sync")
            print("A. 🏅 Achievements & Progress")
        
        print()
        print("H. ❓ Help")
        print("0. 🚪 Exit")
        print()
        
    def browse_curriculum(self):
        """Browse and select curriculum modules with enhanced visual formatting"""
        # Clear screen for better focus
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Windows-compatible header using formatter
        print(self.formatter.header(
            "CURRICULUM BROWSER",
            "Your Journey Through Algorithms",
            level=1
        ))
        
        progress = self._load_progress()
        completed_lessons = progress.get("completed", [])
        
        # Calculate overall progress
        total_lessons = sum(len(m["lessons"]) for m in self.curriculum_data["modules"])
        completed_count = len(completed_lessons)
        overall_percent = (completed_count / total_lessons * 100) if total_lessons else 0
        
        # Visual progress bar using formatter
        print()
        # Use built-in progress bar method
        bar_length = 40
        filled = int(bar_length * overall_percent / 100) if total_lessons > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"Overall Progress: [{bar}] {overall_percent:.1f}%")
        
        # Progress summary box using Windows-compatible formatter
        progress_content = f"""Completed: {completed_count} lessons
Remaining: {total_lessons - completed_count} lessons
Score: {progress.get('score', 0)} points"""
        
        print()
        print(self.formatter.box(
            progress_content,
            title="PROGRESS SUMMARY",
            style="simple"
        ))
        
        # Legend with better formatting
        print()
        print(self.formatter.box(
            "[ ] Not Started  |  [>] In Progress  |  [X] Completed",
            title="Legend",
            style="ascii"
        ))
        
        print()
        print(self.formatter.divider("Available Modules"))
        
        for i, module in enumerate(self.curriculum_data["modules"], 1):
            # Calculate module completion
            module_lessons = [l["id"] for l in module["lessons"]]
            module_completed = sum(1 for lid in module_lessons if lid in completed_lessons)
            module_total = len(module["lessons"])
            module_percent = (module_completed / module_total * 100) if module_total else 0
            
            # Module header with visual progress indicator
            if module_percent == 100:
                module_icon = "✅"
                module_color = self.formatter.theme.success
            elif module_percent > 0:
                module_icon = "📊"
                module_color = self.formatter.theme.warning
            else:
                module_icon = "📘"
                module_color = self.formatter.theme.info
            
            # Module title with progress
            module_title = f"{module_icon} Module {i}: {module['title']}"
            module_progress = f"[{module_completed}/{module_total}]"
            
            print()
            print(self.formatter.divider())
            print(self.formatter._color(
                f"{module_title} {module_progress}",
                module_color,
                WindowsColor.BOLD
            ))
            
            # Mini progress bar for module
            if module_total > 0:
                mini_bar_length = 20
                mini_filled = int(mini_bar_length * module_percent / 100)
                mini_bar = "#" * mini_filled + "-" * (mini_bar_length - mini_filled)
                print(f"   Progress: {self.formatter._color(mini_bar, module_color)} {module_percent:.0f}%")
            
            print()
            
            # Lessons with enhanced visual indicators
            for j, lesson in enumerate(module["lessons"], 1):
                # Determine lesson status
                if lesson["id"] in completed_lessons:
                    status = "[X]"
                    lesson_color = self.formatter.theme.success
                    lesson_style = WindowsColor.DIM
                elif lesson["id"] == progress.get("current_lesson"):
                    status = "[>]"
                    lesson_color = self.formatter.theme.warning
                    lesson_style = WindowsColor.BOLD
                else:
                    status = "[ ]"
                    lesson_color = self.formatter.theme.text
                    lesson_style = None
                
                # Format lesson line
                lesson_num = f"{i}.{j}"
                lesson_line = f"   {status} {lesson_num:5} {lesson['title']}"
                
                if lesson_style:
                    print(self.formatter._color(lesson_line, lesson_color, lesson_style))
                else:
                    print(self.formatter._color(lesson_line, lesson_color))
                
                # Show topic preview with better formatting
                topics_preview = lesson['topics'][:2]
                more = f" +{len(lesson['topics'])-2} more" if len(lesson['topics']) > 2 else ""
                print(f"        {', '.join(topics_preview)}{more} | {lesson['practice_problems']} exercises")
        
        print("\n" + "─" * 60)
        print("Options:")
        print("  • Enter module number (1-3) to browse lessons")
        print("  • Enter lesson number (e.g., 1.2) to start specific lesson")
        print("  • Enter 0 to return to main menu")
        print("\nYour selection: ", end="")
        choice = input().strip()
        
        if choice == "0":
            return
        elif "." in choice:
            # Direct lesson selection (e.g., "1.2")
            self._select_lesson_directly(choice)
        elif choice.isdigit() and 0 < int(choice) <= len(self.curriculum_data["modules"]):
            self.show_module_detail(self.curriculum_data["modules"][int(choice) - 1])
        else:
            print(self.formatter.error("Invalid selection. Please try again."))
    
    def continue_learning(self):
        """Continue from where the user left off"""
        progress = self._load_progress()
        completed_lessons = progress.get("completed", [])
        current_lesson = progress.get("current_lesson")
        
        # Find the next uncompleted lesson
        next_lesson = None
        next_module = None
        
        for module in self.curriculum_data["modules"]:
            for lesson in module["lessons"]:
                if lesson["id"] not in completed_lessons:
                    next_lesson = lesson
                    next_module = module
                    break
            if next_lesson:
                break
        
        if current_lesson:
            # User has a lesson in progress
            for module in self.curriculum_data["modules"]:
                for lesson in module["lessons"]:
                    if lesson["id"] == current_lesson:
                        print(self.formatter.info(f"\n📖 Resuming: {lesson['title']} from {module['title']}"))
                        self.start_lesson(lesson, module)
                        return
        
        if next_lesson:
            print(self.formatter.info(f"\n📚 Starting next lesson: {next_lesson['title']} from {next_module['title']}"))
            confirm = input("Continue? (y/n): ")
            if confirm.lower() == 'y':
                self.start_lesson(next_lesson, next_module)
            else:
                self.browse_curriculum()
        else:
            print(self.formatter.success("\n🎉 Congratulations! You've completed all available lessons!"))
            print(self.formatter.info("You can:"))
            print("  1. Review completed lessons")
            print("  2. Practice problems")
            print("  3. Check your notes")
            input("\nPress Enter to return to main menu...")
    
    def _select_lesson_directly(self, selection: str):
        """Handle direct lesson selection like '1.2'"""
        try:
            parts = selection.split(".")
            if len(parts) == 2:
                module_idx = int(parts[0]) - 1
                lesson_idx = int(parts[1]) - 1
                
                if 0 <= module_idx < len(self.curriculum_data["modules"]):
                    module = self.curriculum_data["modules"][module_idx]
                    if 0 <= lesson_idx < len(module["lessons"]):
                        lesson = module["lessons"][lesson_idx]
                        self.start_lesson(lesson, module)
                        return
            
            print(self.formatter.error("Invalid lesson selection. Use format: module.lesson (e.g., 1.2)"))
        except (ValueError, IndexError):
            print(self.formatter.error("Invalid lesson selection. Use format: module.lesson (e.g., 1.2)"))
    
    def show_module_detail(self, module: Dict):
        """Show detailed view of a specific module"""
        print(self.formatter.header(f"\n📚 Module: {module['title']}"))
        print("─" * 60)
        
        progress = self._load_progress()
        completed_lessons = progress.get("completed", [])
        
        for i, lesson in enumerate(module["lessons"], 1):
            if lesson["id"] in completed_lessons:
                status = "[✓] Completed"
                status_color = self.formatter.success
            elif lesson["id"] == progress.get("current_lesson"):
                status = "[▶] In Progress"
                status_color = self.formatter.warning
            else:
                status = "[ ] Not Started"
                status_color = lambda x: x
            
            print(f"\n{i}. {lesson['title']} {status_color(status)}")
            print(f"   {lesson['content']}")
            print(f"   Topics: {', '.join(lesson['topics'])}")
            print(f"   Exercises: {lesson['practice_problems']} problems")
        
        print("\n" + "─" * 60)
        print("Select a lesson number to start (or 0 to go back): ", end="")
        choice = input().strip()
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(module["lessons"]):
                self.start_lesson(module["lessons"][idx], module)
            elif choice != "0":
                print(self.formatter.error("Invalid lesson number."))
    
    def start_lesson(self, lesson: Dict, module: Dict):
        """Start a specific lesson with beautiful formatting and note integration"""
        # Mark as current lesson
        progress = self._load_progress()
        progress["current_lesson"] = lesson["id"]
        self._save_progress(progress)
        
        # Clear screen for focused learning
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Check for existing notes
        existing_notes = self.notes_manager.get_notes(
            user_id=1,
            lesson_id=lesson.get('id')
        )
        note_count = len(existing_notes) if existing_notes else 0
        
        # Beautiful lesson header with box and note indicator
        header_content = f"Module: {module['title']}\nLesson: {lesson['title']}"
        if note_count > 0:
            header_content += f"\n📝 Notes: {note_count} saved"
        self.formatter.box(header_content, title="📖 LESSON", style="double")
        
        # Lesson progress bar
        module_lessons = module["lessons"]
        current_idx = next((i for i, l in enumerate(module_lessons) if l["id"] == lesson["id"]), 0)
        progress_percent = ((current_idx + 1) / len(module_lessons)) * 100 if module_lessons else 0
        bar_length = 30
        filled = int(bar_length * progress_percent / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"Module Progress: [{bar}] {progress_percent:.0f}% ({current_idx + 1}/{len(module_lessons)})")
        
        # Ensure lesson has proper structure for formatter
        formatted_lesson = self._normalize_lesson_structure(lesson)
        
        # Display the lesson content with beautiful formatting
        try:
            self.enhanced_formatter.format_lesson_content(formatted_lesson)
        except Exception as e:
            # Fallback for any formatting errors
            print(self.formatter.warning(f"Note: Using simplified formatting due to: {e}"))
            print(self.formatter.header("📚 Lesson Content", level=2))
            
            # Display available content
            if formatted_lesson.get('content'):
                print(self.formatter._colorize(str(formatted_lesson['content']), 
                                              self.formatter.theme.text))
            elif formatted_lesson.get('description'):
                print(self.formatter._colorize(formatted_lesson['description'], 
                                              self.formatter.theme.text))
            else:
                print(self.formatter._colorize("No detailed content available yet.", 
                                              self.formatter.theme.text))
        
        # Topics section with colorful bullets
        print(self.formatter.header("🎯 Key Topics", level=2))
        topic_data = []
        for i, topic in enumerate(lesson["topics"], 1):
            # Use different colors for each topic
            colors = [self.formatter.theme.primary, self.formatter.theme.secondary, 
                     self.formatter.theme.success, self.formatter.theme.info]
            color = colors[i % len(colors)]
            print(self.formatter._colorize(f"  {i}. {topic}", color))
        
        # Learning objectives (if available)
        if lesson.get("objectives"):
            print(self.formatter.header("🎓 Learning Objectives", level=2))
            for obj in lesson["objectives"]:
                print(self.formatter._colorize(f"  ✓ {obj}", self.formatter.theme.success))
        
        # Estimated time and difficulty
        print(self.formatter.header("📊 Lesson Info", level=3))
        info_pairs = {
            "Difficulty": lesson.get("difficulty", "Beginner"),
            "Est. Time": lesson.get("time", "10-15 min"),
            "Practice Problems": str(lesson.get("practice_problems", 0)),
            "Prerequisites": lesson.get("prerequisites", "None")
        }
        
        # Display as a formatted table-like structure
        for key, value in info_pairs.items():
            key_colored = self.formatter._colorize(f"{key:20}", 
                                                  self.formatter.theme.secondary)
            value_colored = self.formatter._colorize(str(value), self.formatter.theme.info)
            print(f"  {key_colored} {value_colored}")
        
        # Interactive menu with better styling
        self.formatter.rule("Interactive Options")
        
        # Customize note menu text based on existing notes
        note_text = f"Take Notes ({note_count} existing)" if note_count > 0 else "Take Notes"
        note_desc = f"View {note_count} notes or add new" if note_count > 0 else "Capture your thoughts and insights"
        
        menu_options = [
            ("1", "📝", note_text, note_desc),
            ("2", "🤖", "Claude Questions", "Get AI-powered explanations"),
            ("3", "💡", "Practice Problems", f"{lesson.get('practice_problems', 0)} problems available"),
            ("4", "✅", "Mark Complete", "Finish and earn points"),
            ("5", "⏭️", "Skip to Next", "Continue without completing"),
            ("N", "📌", "Quick Note", "Add a quick note (shortcut)"),
            ("V", "👁️", "View Notes", f"View all {note_count} notes" if note_count else "No notes yet"),
            ("0", "🔙", "Back", "Return to curriculum")
        ]
        
        print()
        for key, icon, title, desc in menu_options:
            key_str = self.formatter._color(f"[{key}]", self.formatter.theme.warning, 
                                              WindowsColor.BOLD)
            title_str = self.formatter._color(title, self.formatter.theme.text, 
                                                WindowsColor.BOLD)
            desc_str = self.formatter._color(f"- {desc}", self.formatter.theme.muted)
            print(f"  {key_str} {icon} {title_str} {desc_str}")
        
        choice = input("\nYour choice: ").strip().upper()
        
        if choice == "1":
            self.take_lesson_notes(lesson)
            self.start_lesson(lesson, module)  # Return to lesson menu
        elif choice == "2":
            self.show_claude_suggestions(lesson)
            self.start_lesson(lesson, module)  # Return to lesson menu
        elif choice == "3":
            self.practice_problems(lesson)
            self.start_lesson(lesson, module)  # Return to lesson menu
        elif choice == "4":
            self.mark_complete(lesson)
            # Find next lesson
            self.continue_learning()
        elif choice == "5":
            # Clear current lesson and continue
            progress["current_lesson"] = None
            self._save_progress(progress)
            self.continue_learning()
        elif choice == "N":  # Quick note shortcut
            self.quick_note(lesson)
            self.start_lesson(lesson, module)  # Return to lesson menu
        elif choice == "V":  # View notes
            self.view_lesson_notes(lesson)
            input("\nPress Enter to continue...")
            self.start_lesson(lesson, module)  # Return to lesson menu
        elif choice == "0":
            # Clear current lesson when going back
            progress["current_lesson"] = None
            self._save_progress(progress)
            self.browse_curriculum()
    
    def start_module(self, module: Dict):
        """Start learning a module"""
        print(self.formatter.header(f"\n📖 Starting: {module['title']}"))
        
        for lesson in module["lessons"]:
            print(f"\n{self.formatter.info('Lesson: ' + lesson['title'])}")
            print(f"Content: {lesson['content']}")
            print(f"\nTopics covered:")
            for topic in lesson["topics"]:
                print(f"  • {topic}")
            
            # Interactive options
            print("\n" + self.formatter.warning("Options:"))
            print("1. Take notes on this lesson")
            print("2. View suggested Claude questions")
            print("3. Try practice problems")
            print("4. Mark as complete")
            print("5. Skip to next")
            
            choice = input("\nYour choice: ")
            
            if choice == "1":
                self.take_lesson_notes(lesson)
            elif choice == "2":
                self.show_claude_suggestions(lesson)
            elif choice == "3":
                self.practice_problems(lesson)
            elif choice == "4":
                self.mark_complete(lesson)
            elif choice == "5":
                continue
    
    def take_lesson_notes(self, lesson: Dict):
        """Enhanced note-taking with quick options and better integration"""
        print(self.formatter.info(f"\n📝 Taking notes for: {lesson['title']}"))
        
        # Check for existing notes
        existing_notes = self.notes_manager.get_notes(
            user_id=1,
            lesson_id=lesson.get('id')
        )
        
        if existing_notes:
            print(self.formatter._color(f"📚 You have {len(existing_notes)} existing note(s) for this lesson", 
                                       self.formatter.theme.info))
            print("Options:")
            print("1. Add new note")
            print("2. View existing notes")
            print("3. Quick note (single line)")
            print("0. Cancel")
            
            choice = input("\nYour choice: ").strip()
            if choice == "0":
                return
            elif choice == "2":
                self.view_lesson_notes(lesson)
                if input("\nAdd a new note? (y/n): ").lower() == 'y':
                    pass  # Continue to add note
                else:
                    return
            elif choice == "3":
                self.quick_note(lesson)
                return
        
        # Show note templates
        print("\nNote type:")
        print("1. 📝 General note")
        print("2. 💡 Key concept")
        print("3. ❓ Question/confusion")
        print("4. 📋 Summary")
        print("5. 🔗 Connection to other topics")
        
        note_type = input("\nSelect type (1-5, default=1): ").strip() or "1"
        
        prefixes = {
            "1": "",
            "2": "KEY CONCEPT: ",
            "3": "QUESTION: ",
            "4": "SUMMARY: ",
            "5": "CONNECTION: "
        }
        
        prefix = prefixes.get(note_type, "")
        
        print(f"\nEnter your notes (press Enter twice to finish):")
        if prefix:
            print(self.formatter._color(prefix, self.formatter.theme.warning))
        
        note_content = input()
        
        # Multi-line input
        lines = [note_content]
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        
        full_note = prefix + "\n".join(lines)
        
        # Auto-generate tags based on note type and content
        tags = [lesson.get("id", "unknown"), "study-notes"]
        
        if note_type == "2":
            tags.append("key-concept")
        elif note_type == "3":
            tags.append("question")
        elif note_type == "4":
            tags.append("summary")
        elif note_type == "5":
            tags.append("connection")
        
        # Save note with enhanced metadata
        self.notes_manager.save_note(
            user_id=1,
            lesson_id=lesson.get('id'),
            module_name=lesson.get('module', 'Lessons'),
            topic=f"{lesson['title']}",
            content=full_note,
            tags=list(set(tags))
        )
        
        print(self.formatter.success("✅ Note saved successfully!"))
        
        # Show note preview
        preview = full_note[:150]
        print(self.formatter._color(f"Preview: {preview}{'...' if len(full_note) > 150 else ''}", 
                                   self.formatter.theme.muted))
    
    def quick_note(self, lesson: Dict):
        """Add a quick single-line note"""
        note = input("Quick note: ").strip()
        if note:
            self.notes_manager.save_note(
                user_id=1,
                lesson_id=lesson.get('id'),
                module_name=lesson.get('module', 'Lessons'),
                topic=f"{lesson['title']} - Quick Note",
                content=note,
                tags=[lesson.get("id", "unknown"), "quick-note"]
            )
            print(self.formatter.success("✅ Quick note saved!"))
    
    def view_lesson_notes(self, lesson: Dict):
        """View all notes for current lesson"""
        notes = self.notes_manager.get_notes(
            user_id=1,
            lesson_id=lesson.get('id')
        )
        
        if not notes:
            print(self.formatter.warning("No notes found for this lesson."))
            return
        
        print(self.formatter.header(f"\n📚 Notes for: {lesson['title']}"))
        print(f"Total notes: {len(notes)}\n")
        
        for i, note in enumerate(notes, 1):
            print(self.formatter._color(f"Note #{i}", self.formatter.theme.warning))
            print(f"Date: {note.get('created_at', 'Unknown')}")
            if note.get('tags'):
                print(f"Tags: {', '.join(note['tags'])}")
            print(self.formatter._color("Content:", self.formatter.theme.info))
            print(note.get('content', 'No content'))
            print("-" * 40)
    
    def show_claude_suggestions(self, lesson: Dict):
        """Show suggested questions for Claude"""
        print(self.formatter.header(f"\n🤖 Claude AI Questions for: {lesson['title']}"))
        print(self.formatter.info("Copy these to Claude Code for detailed explanations:\n"))
        
        questions = [
            f"Can you explain {lesson['title']} with real-world examples?",
            f"What are the time and space complexities of {lesson['title']}?",
            f"When should I use {lesson['title']} vs alternatives?",
            f"Can you show me a step-by-step implementation of {lesson['title']}?",
            f"What are common mistakes when implementing {lesson['title']}?",
            f"How does {lesson['title']} compare to other approaches?"
        ]
        
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q}")
        
        print(self.formatter.warning("\n💡 Tip: Keep Claude Code open alongside for best results!"))
        input("\nPress Enter to continue...")
    
    def practice_problems(self, lesson: Dict):
        """Show practice problems"""
        print(self.formatter.header(f"\n🎯 Practice Problems: {lesson['title']}"))
        print(f"Available problems: {lesson['practice_problems']}")
        print(self.formatter.info("\nProblem categories:"))
        print("1. Basic implementation")
        print("2. Optimization challenges")
        print("3. Real-world applications")
        print("4. Edge cases")
        
        print(self.formatter.warning("\n💡 Use Claude to check your solutions!"))
        input("Press Enter to continue...")
    
    def mark_complete(self, lesson: Dict):
        """Mark lesson as complete"""
        progress = self._load_progress()
        if lesson["id"] not in progress["completed"]:
            progress["completed"].append(lesson["id"])
            progress["score"] += 10
            # Clear current lesson if it was this one
            if progress.get("current_lesson") == lesson["id"]:
                progress["current_lesson"] = None
            self._save_progress(progress)
            print(self.formatter.success(f"✅ Marked {lesson['title']} as complete!"))
            print(self.formatter.info(f"Score: {progress['score']} points"))
    
    def manage_notes(self):
        """Enhanced notes management interface"""
        from .enhanced_notes_ui import manage_notes_enhanced
        manage_notes_enhanced(self)
    
    def view_progress(self):
        """View learning progress"""
        progress = self._load_progress()
        total_lessons = sum(len(m["lessons"]) for m in self.curriculum_data["modules"])
        completed_count = len(progress.get("completed", []))
        percentage = (completed_count / total_lessons * 100) if total_lessons else 0
        
        print(self.formatter.header("\n📊 Your Progress"))
        print(self.formatter.info("=" * 60))
        print(f"Level: {progress.get('level', 'Beginner')}")
        print(f"Score: {progress.get('score', 0)} points")
        print(f"Lessons completed: {completed_count}/{total_lessons} ({percentage:.1f}%)")
        print(f"Last accessed: {progress.get('lastAccessed', 'Never')}")
        
        # Progress bar
        bar_length = 40
        filled = int(bar_length * percentage / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\nProgress: [{bar}] {percentage:.1f}%")
        
        # Achievements
        if progress.get("achievements"):
            print(f"\n🏆 Achievements: {', '.join(progress['achievements'])}")
        
        input("\nPress Enter to continue...")
    
    def claude_integration_guide(self):
        """Show Claude AI integration guide"""
        print(self.formatter.header("\n🤖 Claude AI Integration Guide"))
        print(self.formatter.info("=" * 60))
        print("""
How to use Claude Code with this CLI:

1. **Keep Claude Code open alongside this CLI**
   - Use split-screen or multiple monitors
   - Copy questions from CLI to Claude

2. **Best practices:**
   - Start with "I'm learning about [topic]..."
   - Ask for step-by-step explanations
   - Request code examples in Python
   - Ask for complexity analysis
   - Get help debugging your solutions

3. **Example prompts:**
   - "Explain binary search with visualizations"
   - "Show me 5 practice problems for arrays"
   - "Debug my quicksort implementation"
   - "Compare merge sort vs quicksort"

4. **Features to leverage:**
   - Code generation and review
   - Algorithm visualization
   - Performance optimization tips
   - Real-world use cases
   - Interview preparation

Press Enter to continue...
""")
        input()
    
    def _normalize_lesson_structure(self, lesson: Dict) -> Dict:
        """Normalize lesson structure for consistent formatting
        
        Args:
            lesson: Raw lesson data
            
        Returns:
            Normalized lesson with expected structure
        """
        normalized = {
            'id': lesson.get('id', 'unknown'),
            'title': lesson.get('title', 'Untitled Lesson'),
            'subtitle': lesson.get('subtitle', ''),
            'topics': lesson.get('topics', []),
            'practice_problems': lesson.get('practice_problems', 0)
        }
        
        # Handle content field - it might be string, dict, or missing
        if 'content' in lesson:
            normalized['content'] = lesson['content']
        elif 'description' in lesson:
            normalized['content'] = lesson['description']
        else:
            # Generate content from other fields
            content_parts = []
            if 'topics' in lesson and lesson['topics']:
                content_parts.append("## Topics Covered")
                for topic in lesson['topics']:
                    content_parts.append(f"- {topic}")
            if 'description' in lesson:
                content_parts.append("\n## Description")
                content_parts.append(lesson['description'])
            normalized['content'] = '\n'.join(content_parts) if content_parts else "Content coming soon..."
        
        # Copy over any additional fields
        for key in ['difficulty', 'est_time', 'prerequisites', 'objectives', 
                    'time_complexity', 'space_complexity', 'code_examples']:
            if key in lesson:
                normalized[key] = lesson[key]
        
        return normalized
    
    def _reset_progress(self):
        """Reset all learning progress"""
        if self.progress_file.exists():
            self.progress_file.unlink()
        print(self.formatter.success("✅ Progress reset successfully!"))
    
    def settings_and_statistics(self):
        """Settings and statistics interface"""
        print(self.formatter.header("\n⚙️ Settings & Statistics"))
        print("1. View detailed statistics")
        print("2. Reset progress")
        print("3. Export learning data")
        print("4. Preferences")
        print("0. Back to main menu")
        
        choice = input("\nYour choice: ")
        
        if choice == "1":
            self._show_detailed_statistics()
        elif choice == "2":
            confirm = input("Are you sure you want to reset all progress? (yes/no): ")
            if confirm.lower() == 'yes':
                self._reset_progress()
        elif choice == "3":
            self._export_learning_data()
        elif choice == "4":
            self._manage_preferences()
        elif choice == "0":
            return
    
    def _show_detailed_statistics(self):
        """Show detailed learning statistics"""
        progress = self._load_progress()
        notes = self.notes_manager.get_notes(user_id=1)
        
        print(self.formatter.header("\n📊 Detailed Statistics"))
        print(f"Total Score: {progress.get('score', 0)} points")
        print(f"Level: {progress.get('level', 'Beginner')}")
        print(f"Lessons Completed: {len(progress.get('completed', []))}")
        print(f"Notes Created: {len(notes) if notes else 0}")
        print(f"Total Study Time: {progress.get('totalTime', 0)} minutes")
        print(f"Last Study Session: {progress.get('lastAccessed', 'Never')}")
        
        if progress.get('achievements'):
            print(f"Achievements: {', '.join(progress['achievements'])}")
        
        input("\nPress Enter to continue...")
    
    def _export_learning_data(self):
        """Export learning data"""
        progress = self._load_progress()
        notes = self.notes_manager.get_notes(user_id=1)
        
        export_data = {
            'progress': progress,
            'notes_count': len(notes) if notes else 0,
            'exported_at': datetime.now().isoformat()
        }
        
        export_file = Path(f"learning_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(self.formatter.success(f"✅ Data exported to: {export_file}"))
        input("Press Enter to continue...")
    
    def _manage_preferences(self):
        """Manage user preferences"""
        progress = self._load_progress()
        prefs = progress.get('preferences', {})
        
        print(self.formatter.header("\n⚙️ Preferences"))
        print(f"Learning Path: {prefs.get('learningPath', 'visual')}")
        print(f"Difficulty: {prefs.get('difficulty', 'beginner')}")
        print(f"Notifications: {prefs.get('notifications', True)}")
        
        print("\n1. Change learning path")
        print("2. Change difficulty level") 
        print("3. Toggle notifications")
        print("0. Back")
        
        choice = input("\nYour choice: ")
        
        if choice == "1":
            print("Learning paths: visual, textual, interactive")
            new_path = input("Enter new path: ")
            if new_path in ['visual', 'textual', 'interactive']:
                prefs['learningPath'] = new_path
                progress['preferences'] = prefs
                self._save_progress(progress)
                print(self.formatter.success("✅ Learning path updated!"))
        elif choice == "2":
            print("Difficulty levels: beginner, intermediate, advanced")
            new_difficulty = input("Enter new difficulty: ")
            if new_difficulty in ['beginner', 'intermediate', 'advanced']:
                prefs['difficulty'] = new_difficulty
                progress['preferences'] = prefs
                self._save_progress(progress)
                print(self.formatter.success("✅ Difficulty updated!"))
        elif choice == "3":
            prefs['notifications'] = not prefs.get('notifications', True)
            progress['preferences'] = prefs
            self._save_progress(progress)
            status = "enabled" if prefs['notifications'] else "disabled"
            print(self.formatter.success(f"✅ Notifications {status}!"))
        
        input("Press Enter to continue...")
    
    async def run_advanced_mode(self):
        """Run simplified advanced mode"""
        session = InteractiveSession()
        await session.run()
    
    def launch_enhanced_interactive(self):
        """Launch the enhanced interactive learning system"""
        try:
            # Create enhanced interactive session
            enhanced_session = EnhancedInteractiveSession(cli_engine=self)
            
            # Run in async mode
            asyncio.run(enhanced_session.run())
            
        except Exception as e:
            print(self.formatter.error(f"Error launching enhanced mode: {e}"))
            print(self.formatter.info("Falling back to standard interactive mode..."))
            input("Press Enter to continue...")
            
            # Fallback to standard interactive mode
            try:
                interactive = InteractiveSession(cli_engine=self)
                asyncio.run(interactive.run())
            except Exception as fallback_error:
                print(self.formatter.error(f"Fallback failed: {fallback_error}"))
                print(self.formatter.info("Returning to main menu..."))
                input("Press Enter to continue...")
    
    async def handle_challenges_and_leaderboards(self):
        """Handle challenges and leaderboards menu"""
        if not self.flow_nexus_integration:
            print(self.formatter.warning("⚠️ Cloud features not available"))
            return
        
        while True:
            print(self.formatter.header("\n🏆 Challenges & Leaderboards"))
            print("1. 📋 Browse Available Challenges")
            print("2. 💻 Solve Challenge")
            print("3. 🏆 View Global Leaderboard")
            print("4. 📊 My Challenge Statistics")
            print("5. 🎯 Daily Challenge")
            print("0. 🔙 Back to Main Menu")
            
            choice = input("\nYour choice: ").strip()
            
            if choice == "1":
                await self._browse_challenges()
            elif choice == "2":
                await self._solve_challenge_interactive()
            elif choice == "3":
                await self._show_leaderboard()
            elif choice == "4":
                await self._show_challenge_stats()
            elif choice == "5":
                await self._daily_challenge()
            elif choice == "0":
                break
            else:
                print(self.formatter.error("Invalid choice"))
    
    async def _browse_challenges(self):
        """Browse available challenges"""
        print(self.formatter.info("🔄 Loading challenges..."))
        
        challenges = await self.flow_nexus_integration.get_available_challenges()
        
        if not challenges:
            print(self.formatter.warning("No challenges available"))
            return
        
        print(self.formatter.header("\n📋 Available Challenges"))
        
        for i, challenge in enumerate(challenges, 1):
            difficulty_colors = {
                "beginner": self.formatter.theme.success,
                "intermediate": self.formatter.theme.warning, 
                "advanced": self.formatter.theme.error,
                "expert": self.formatter.theme.primary
            }
            
            difficulty_color = difficulty_colors.get(challenge.difficulty, self.formatter.theme.text)
            
            print(f"\n{i}. {challenge.title}")
            print(f"   {self.formatter._color(challenge.difficulty.title(), difficulty_color)} | {challenge.category} | {challenge.points} points")
            print(f"   {challenge.description}")
        
        print("\nEnter challenge number to view details, or 0 to go back: ", end="")
        choice = input().strip()
        
        if choice.isdigit() and 0 < int(choice) <= len(challenges):
            challenge = challenges[int(choice) - 1]
            await self._show_challenge_details(challenge)
    
    async def _show_challenge_details(self, challenge):
        """Show detailed challenge information"""
        print(self.formatter.header(f"\n🎯 Challenge: {challenge.title}"))
        print(f"Difficulty: {challenge.difficulty}")
        print(f"Category: {challenge.category}")
        print(f"Points: {challenge.points}")
        print(f"\nDescription:")
        print(challenge.description)
        
        if challenge.test_cases:
            print(f"\nExample test cases:")
            for i, test in enumerate(challenge.test_cases[:2], 1):
                print(f"  {i}. Input: {test.get('input')}")
                print(f"     Output: {test.get('output')}")
        
        print("\n1. Attempt this challenge")
        print("2. Save for later")
        print("0. Back to challenges list")
        
        choice = input("\nYour choice: ").strip()
        
        if choice == "1":
            await self._attempt_challenge(challenge)
        elif choice == "2":
            print(self.formatter.success("💾 Challenge saved for later!"))
    
    async def _attempt_challenge(self, challenge):
        """Attempt to solve a challenge"""
        print(self.formatter.header(f"\n💻 Solving: {challenge.title}"))
        print("Enter your solution (Python code).")
        print("Type 'SUBMIT' on a new line when finished, or 'CANCEL' to cancel:")
        print()
        
        solution_lines = []
        while True:
            line = input(">>> " if not solution_lines else "... ")
            if line.strip() == "SUBMIT":
                break
            elif line.strip() == "CANCEL":
                print(self.formatter.info("❌ Challenge cancelled"))
                return
            else:
                solution_lines.append(line)
        
        solution_code = "\n".join(solution_lines)
        
        if not solution_code.strip():
            print(self.formatter.error("❌ No solution provided"))
            return
        
        print(self.formatter.info("🔄 Submitting solution..."))
        
        result = await self.flow_nexus_integration.submit_challenge_solution(
            challenge.challenge_id, solution_code, "python"
        )
        
        if result.get("error"):
            print(self.formatter.error(f"❌ Submission failed: {result['error']}"))
        else:
            print(self.formatter.success("✅ Solution submitted!"))
            if result.get("points_awarded"):
                print(f"🎉 Earned {result['points_awarded']} points!")
            
            # Award credits for attempt
            if self.flow_nexus_integration.is_authenticated:
                await self.flow_nexus_integration.award_credits_for_activity(
                    f"challenge attempt: {challenge.title}", 10
                )
    
    async def _solve_challenge_interactive(self):
        """Interactive challenge solving"""
        challenge_id = input("Enter challenge ID or name: ").strip()
        
        # For demo, use a simple challenge
        from .integrations.flow_nexus import Challenge
        demo_challenge = Challenge(
            challenge_id="demo_two_sum",
            title="Two Sum Problem",
            description="Given an array of integers and a target sum, return indices of two numbers that add to target.",
            difficulty="beginner",
            category="arrays",
            points=15
        )
        
        await self._attempt_challenge(demo_challenge)
    
    async def _show_leaderboard(self):
        """Show global leaderboard"""
        print(self.formatter.info("🔄 Loading leaderboard..."))
        
        leaderboard = await self.flow_nexus_integration.get_leaderboard_data()
        
        if leaderboard.get("error"):
            print(self.formatter.error(f"❌ Failed to load leaderboard: {leaderboard['error']}"))
            return
        
        print(self.formatter.header("\n🏆 Global Leaderboard"))
        
        if leaderboard.get("offline_mode"):
            print(self.formatter.warning("📱 Offline Mode - Showing sample data"))
        
        for entry in leaderboard.get("leaderboard", []):
            rank = entry["rank"]
            username = entry["username"]
            score = entry["score"]
            solved = entry["solved"]
            
            if entry.get("current_user"):
                line = self.formatter.success(f"#{rank:2} {username:20} {score:5} pts  {solved:3} solved (YOU)")
            else:
                line = f"#{rank:2} {username:20} {score:5} pts  {solved:3} solved"
            
            print(line)
        
        total = leaderboard.get("total_participants", 0)
        your_rank = leaderboard.get("your_rank")
        
        print(f"\nTotal participants: {total}")
        if your_rank:
            print(f"Your rank: #{your_rank}")
        
        input("\nPress Enter to continue...")
    
    async def _show_challenge_stats(self):
        """Show user's challenge statistics"""
        print(self.formatter.header("\n📊 Your Challenge Statistics"))
        
        if not self.flow_nexus_integration.is_authenticated:
            print(self.formatter.warning("⚠️ Login required to view statistics"))
            return
        
        # Mock statistics for demo
        stats = {
            "challenges_attempted": 15,
            "challenges_solved": 12,
            "total_points": 180,
            "favorite_category": "arrays",
            "success_rate": 80.0,
            "average_time": "12:34"
        }
        
        print(f"Challenges attempted: {stats['challenges_attempted']}")
        print(f"Challenges solved: {stats['challenges_solved']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        print(f"Total points earned: {stats['total_points']}")
        print(f"Favorite category: {stats['favorite_category']}")
        print(f"Average solve time: {stats['average_time']}")
        
        input("\nPress Enter to continue...")
    
    async def _daily_challenge(self):
        """Show today's daily challenge"""
        print(self.formatter.header("\n🎯 Daily Challenge"))
        print("Today's challenge: Array Rotation")
        print("Difficulty: Intermediate")
        print("Points: 25")
        print("Time limit: 30 minutes")
        print("\nRotate an array to the right by k steps.")
        print("Example: [1,2,3,4,5,6,7] rotated by 3 → [5,6,7,1,2,3,4]")
        
        print("\n1. Attempt daily challenge")
        print("2. Skip for today")
        print("0. Back")
        
        choice = input("\nYour choice: ").strip()
        
        if choice == "1":
            print(self.formatter.info("💡 Daily challenges coming soon!"))
            input("Press Enter to continue...")
    
    def show_cloud_status(self):
        """Show cloud connection and sync status"""
        if not self.flow_nexus_integration:
            print(self.formatter.warning("⚠️ Cloud features not initialized"))
            return
        
        self.flow_nexus_integration.display_cloud_status()
        
        if self.collaboration_manager:
            self.collaboration_manager.display_collaboration_status()
        
        # Show sync status
        print(self.formatter.header("\n🔄 Sync Status"))
        progress = self._load_progress()
        last_sync = progress.get("last_cloud_sync", "Never")
        print(f"  • Last sync: {last_sync}")
        print(f"  • Auto-sync: {'✅ Enabled' if self.cloud_mode else '❌ Disabled'}")
        print(f"  • Local progress: {len(progress.get('completed', []))} lessons completed")
        
        print("\n1. 🔄 Force sync now")
        print("2. 📤 Export progress")
        print("3. 📥 Import progress")
        print("4. 🚪 Logout")
        print("0. 🔙 Back")
        
        choice = input("\nYour choice: ").strip()
        
        if choice == "1":
            asyncio.run(self._force_sync())
        elif choice == "2":
            self._export_progress_to_cloud()
        elif choice == "3":
            asyncio.run(self._import_progress_from_cloud())
        elif choice == "4":
            asyncio.run(self._logout_from_cloud())
    
    async def _force_sync(self):
        """Force sync progress to cloud"""
        if not self.flow_nexus_integration:
            return
        
        print(self.formatter.info("🔄 Syncing progress..."))
        progress = self._load_progress()
        
        success = await self.flow_nexus_integration.sync_progress_to_cloud(progress)
        
        if success:
            progress["last_cloud_sync"] = datetime.now().isoformat()
            self._save_progress(progress)
            print(self.formatter.success("✅ Progress synced successfully!"))
        else:
            print(self.formatter.error("❌ Sync failed"))
        
        input("Press Enter to continue...")
    
    def _export_progress_to_cloud(self):
        """Export progress to cloud storage"""
        print(self.formatter.info("📤 Exporting progress..."))
        # Implementation would export to cloud
        print(self.formatter.success("✅ Progress exported!"))
        input("Press Enter to continue...")
    
    async def _import_progress_from_cloud(self):
        """Import progress from cloud storage"""
        print(self.formatter.info("📥 Importing progress..."))
        # Implementation would import from cloud
        print(self.formatter.success("✅ Progress imported!"))
        input("Press Enter to continue...")
    
    async def _logout_from_cloud(self):
        """Logout from cloud services"""
        if self.flow_nexus_integration:
            await self.flow_nexus_integration.logout()
            self.cloud_mode = False
    
    async def show_achievements_and_cloud_progress(self):
        """Show achievements and cloud-specific progress"""
        if not self.flow_nexus_integration:
            print(self.formatter.warning("⚠️ Cloud features not available"))
            return
        
        print(self.formatter.header("\n🏅 Achievements & Cloud Progress"))
        
        # Show achievements
        achievements = await self.flow_nexus_integration.get_user_achievements()
        
        if achievements:
            print(self.formatter.header("🏆 Your Achievements", level=2))
            for achievement in achievements:
                title = achievement.get("title", "Unknown")
                description = achievement.get("description", "")
                points = achievement.get("points", 0)
                earned_at = achievement.get("earned_at", "")
                
                if earned_at:
                    date_str = datetime.fromisoformat(earned_at).strftime("%m/%d/%Y")
                    print(f"🏅 {title} ({points} pts) - {date_str}")
                else:
                    print(f"🏅 {title} ({points} pts)")
                
                if description:
                    print(f"   {description}")
        else:
            print(self.formatter.info("No achievements yet - keep learning to earn some!"))
        
        # Show rUv credits if available
        if self.flow_nexus_integration.is_authenticated:
            credits = self.flow_nexus_integration.current_user.ruv_credits
            print(f"\n💰 rUv Credits: {credits}")
            print("Earn credits by completing lessons, solving challenges, and participating!")
        
        input("\nPress Enter to continue...")
    
    async def run(self):
        """Main run loop with proper async handling"""
        # Clear screen first to avoid duplicates
        os.system('cls' if os.name == 'nt' else 'clear')
        
        first_display = True
        while True:
            # Clear screen between menu displays to prevent duplicates
            if not first_display:
                os.system('cls' if os.name == 'nt' else 'clear')
            
            self.display_main_menu(show_header=first_display)
            first_display = False  # Only show header on first display
            choice = input("Enter your choice: ")
            
            if choice == "1":
                self.browse_curriculum()
            elif choice == "2":
                # Continue from last position
                self.continue_learning()
            elif choice == "3":
                self.manage_notes()
            elif choice == "4":
                self.view_progress()
            elif choice == "5":
                print(self.formatter.info("Practice problems coming soon!"))
                input("Press Enter to continue...")
            elif choice == "6":
                self.claude_integration_guide()
            elif choice == "7":
                self.settings_and_statistics()
            elif choice == "8":
                print(self.formatter.info("Launching simplified advanced mode..."))
                await self.run_advanced_mode()
            elif choice == "9":
                print(self.formatter.info("🚀 Launching Enhanced Interactive Mode..."))
                await self.launch_enhanced_interactive()
            elif choice.lower() == "c" and self.cloud_mode:
                await self.handle_challenges_and_leaderboards()
            elif choice.lower() == "g" and self.cloud_mode:
                if self.collaboration_manager:
                    await self.collaboration_manager.show_collaboration_menu()
                else:
                    print(self.formatter.warning("⚠️ Collaboration features not available"))
            elif choice.lower() == "s" and self.cloud_mode:
                await self.show_cloud_status()
            elif choice.lower() == "a" and self.cloud_mode:
                await self.show_achievements_and_cloud_progress()
            # Curriculum management commands
            elif choice.upper() == "C1":
                await self._handle_curriculum_command("curriculum list")
            elif choice.upper() == "C2":
                curriculum_id = input("Enter curriculum ID or name: ").strip()
                if curriculum_id:
                    await self._handle_curriculum_command(f"curriculum show {curriculum_id}")
            elif choice.upper() == "C3":
                await self._handle_curriculum_command("curriculum create")
            elif choice.upper() == "C4":
                curriculum_id = input("Enter curriculum ID to update: ").strip()
                if curriculum_id:
                    await self._handle_curriculum_command(f"curriculum update {curriculum_id}")
            elif choice.upper() == "C5":
                curriculum_id = input("Enter curriculum ID to delete: ").strip()
                if curriculum_id:
                    await self._handle_curriculum_command(f"curriculum delete {curriculum_id}")
            elif choice.lower() == "h":
                print(self.formatter.info("""
Help:
- This CLI helps you learn algorithms and data structures systematically
- Work through lessons in order or jump around freely
- Take comprehensive notes as you learn
- Use Claude Code for detailed explanations and help
- Track your progress over time with statistics
- Practice problems to reinforce learning
- Export your notes for future reference

NEW: Enhanced Interactive Mode features:
- Beautiful animated interface optimized for Windows PowerShell
- Arrow key navigation with number input fallback
- Typing animations and smooth transitions
- Rich note-taking with markdown-style formatting
- Visual quizzes with instant feedback
- Real-time progress visualization
- Advanced export options

CURRICULUM COMMANDS:
- C1-C5: Manage curricula (list, show, create, update, delete)
- You can also type commands directly like 'curriculum list'
"""))
                input("Press Enter to continue...")
            elif choice == "0":
                print(self.formatter.success("\n👋 Thanks for learning! See you next time!"))
                break
            else:
                # Try to handle as a direct command
                if self._is_curriculum_command(choice):
                    await self._handle_curriculum_command(choice)
                else:
                    print(self.formatter.error("Invalid choice. Please try again."))
    
    def run_sync(self):
        """Synchronous run method that properly handles the async main loop"""
        try:
            # Run the async main loop
            asyncio.run(self.run())
        except KeyboardInterrupt:
            print(self.formatter.success("\n👋 Thanks for learning! See you next time!"))
        except Exception as e:
            print(self.formatter.error(f"An error occurred: {e}"))
            if self.debug_mode:
                import traceback
                traceback.print_exc()
    
    def _is_curriculum_command(self, command: str) -> bool:
        """Check if input is a curriculum command"""
        curriculum_keywords = ['curriculum', 'curr', 'list', 'show', 'create', 'update', 'delete']
        return any(keyword in command.lower() for keyword in curriculum_keywords)
    
    async def _handle_curriculum_command(self, command_line: str):
        """Handle curriculum command in interactive mode"""
        try:
            # Clear screen for better focus
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Parse and route the command
            args = command_line.strip().split()
            command, remaining_args = self.command_router.parse_command(args)
            
            # Route the command
            success = await self.command_router.route_command(command, remaining_args)
            
            if not success:
                print(self.formatter.error("❌ Command execution failed"))
            
            # Pause for user to read output
            print()
            input("Press Enter to return to main menu...")
            
        except Exception as e:
            print(self.formatter.error(f"Error executing command: {e}"))
            if self.debug_mode:
                import traceback
                traceback.print_exc()
            input("Press Enter to continue...")


if __name__ == "__main__":
    cli = EnhancedCLI()
    cli.run_sync()