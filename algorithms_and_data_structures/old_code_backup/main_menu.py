#!/usr/bin/env python3
"""
Main Menu System - Beautiful navigation with arrow keys
Integrates all components: lessons, notes, progress tracking
"""

import sys
import os
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import navigation system
from src.ui.navigation import NavigationController, MenuItem, NavigationMode
from src.ui.windows_formatter import WindowsFormatter, WindowsColor
from src.ui.enhanced_lesson_formatter import EnhancedLessonFormatter
from src.flow_nexus_teacher import AlgorithmTeacher
from src.notes_manager import NotesManager
from src.notes_viewer import EnhancedNotesViewer


class MainMenuSystem:
    """Main menu system with arrow key navigation and beautiful formatting"""
    
    def __init__(self):
        """Initialize the main menu system"""
        self.formatter = WindowsFormatter()
        self.nav_controller = NavigationController(self.formatter)
        self.enhanced_formatter = EnhancedLessonFormatter(self.formatter)
        self.teacher = AlgorithmTeacher()
        self.notes_manager = NotesManager()
        self.notes_viewer = EnhancedNotesViewer()
        
        # Load progress and curriculum
        self.progress_file = Path("progress.json")
        self.progress = self._load_progress()
        self.curriculum = self._load_curriculum()
        
        # Menu state
        self.current_menu = "main"
        self.current_lesson = None
        self.current_module = None
    
    def _load_progress(self) -> Dict:
        """Load user progress"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {
            "user": "learner",
            "level": "foundation",
            "completed": [],
            "score": 0,
            "lastAccessed": None,
            "totalTime": 0,
            "current_lesson": None
        }
    
    def _save_progress(self):
        """Save user progress"""
        self.progress["lastAccessed"] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def _load_curriculum(self) -> Dict:
        """Load curriculum data"""
        curriculum_file = Path("data/curriculum_enhanced.json")
        if not curriculum_file.exists():
            curriculum_file = Path("data/curriculum.json")
        
        if curriculum_file.exists():
            with open(curriculum_file, 'r') as f:
                return json.load(f)
        
        # Default curriculum structure
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
                        },
                        {
                            "id": "mergesort",
                            "title": "MergeSort",
                            "content": "Stable divide-and-conquer sorting",
                            "topics": ["Merging", "Recursion", "Stability"],
                            "practice_problems": 6
                        }
                    ]
                },
                {
                    "id": "data-structures",
                    "title": "Data Structures",
                    "lessons": [
                        {
                            "id": "linked-lists",
                            "title": "Linked Lists",
                            "content": "Dynamic linear data structures",
                            "topics": ["Singly linked", "Doubly linked", "Circular"],
                            "practice_problems": 10
                        },
                        {
                            "id": "stacks-queues",
                            "title": "Stacks & Queues",
                            "content": "LIFO and FIFO data structures",
                            "topics": ["Stack operations", "Queue operations", "Applications"],
                            "practice_problems": 8
                        },
                        {
                            "id": "trees",
                            "title": "Trees & Binary Trees",
                            "content": "Hierarchical data structures",
                            "topics": ["Tree traversal", "BST", "Balanced trees"],
                            "practice_problems": 12
                        }
                    ]
                },
                {
                    "id": "graphs",
                    "title": "Graph Algorithms",
                    "lessons": [
                        {
                            "id": "graph-basics",
                            "title": "Graph Fundamentals",
                            "content": "Introduction to graph theory",
                            "topics": ["Representations", "Directed vs Undirected", "Weighted graphs"],
                            "practice_problems": 7
                        },
                        {
                            "id": "dfs-bfs",
                            "title": "DFS & BFS",
                            "content": "Graph traversal algorithms",
                            "topics": ["Depth-first search", "Breadth-first search", "Applications"],
                            "practice_problems": 9
                        },
                        {
                            "id": "shortest-path",
                            "title": "Shortest Path Algorithms",
                            "content": "Finding optimal paths in graphs",
                            "topics": ["Dijkstra's", "Bellman-Ford", "Floyd-Warshall"],
                            "practice_problems": 8
                        }
                    ]
                },
                {
                    "id": "dynamic-programming",
                    "title": "Dynamic Programming",
                    "lessons": [
                        {
                            "id": "dp-intro",
                            "title": "DP Introduction",
                            "content": "Understanding dynamic programming",
                            "topics": ["Memoization", "Tabulation", "Optimal substructure"],
                            "practice_problems": 6
                        },
                        {
                            "id": "classic-dp",
                            "title": "Classic DP Problems",
                            "content": "Common dynamic programming patterns",
                            "topics": ["Fibonacci", "Knapsack", "LCS", "Edit distance"],
                            "practice_problems": 10
                        }
                    ]
                }
            ]
        }
    
    def _normalize_lesson_for_display(self, lesson: Dict, module: Dict) -> Dict:
        """Normalize lesson data for enhanced formatter
        
        Args:
            lesson: Raw lesson data
            module: Parent module data
            
        Returns:
            Normalized lesson structure
        """
        normalized = {
            'id': lesson.get('id', 'unknown'),
            'title': lesson.get('title', 'Untitled Lesson'),
            'subtitle': f"Module: {module.get('title', 'Unknown Module')}",
            'topics': lesson.get('topics', []),
            'practice_problems': lesson.get('practice_problems', 0)
        }
        
        # Handle content - ensure it's a string
        content = lesson.get('content', '')
        if isinstance(content, dict):
            # Convert dict to formatted string
            content_parts = []
            for key, value in content.items():
                if key not in ['title', 'subtitle', 'id']:
                    content_parts.append(f"## {key.replace('_', ' ').title()}")
                    if isinstance(value, list):
                        for item in value:
                            content_parts.append(f"- {item}")
                    else:
                        content_parts.append(str(value))
            normalized['content'] = '\n\n'.join(content_parts)
        elif isinstance(content, list):
            # Convert list to formatted string
            normalized['content'] = '\n\n'.join(str(item) for item in content)
        else:
            # Use as-is or default
            normalized['content'] = str(content) if content else self._generate_default_content(lesson)
        
        # Add any additional fields
        for key in ['difficulty', 'est_time', 'prerequisites', 'objectives', 
                    'time_complexity', 'space_complexity', 'code_examples']:
            if key in lesson:
                normalized[key] = lesson[key]
        
        # Ensure topics is always a list
        if not isinstance(normalized['topics'], list):
            normalized['topics'] = [str(normalized['topics'])] if normalized['topics'] else []
        
        # Add key_topics for formatter compatibility
        normalized['key_topics'] = normalized['topics']
        
        return normalized
    
    def _generate_default_content(self, lesson: Dict) -> str:
        """Generate default content from lesson structure
        
        Args:
            lesson: Lesson data
            
        Returns:
            Generated content string
        """
        parts = []
        
        if lesson.get('description'):
            parts.append(lesson['description'])
        
        if lesson.get('topics'):
            parts.append("\n## Topics Covered")
            for topic in lesson['topics']:
                parts.append(f"- {topic}")
        
        if lesson.get('objectives'):
            parts.append("\n## Learning Objectives")
            for obj in lesson['objectives']:
                parts.append(f"- {obj}")
        
        if not parts:
            parts.append("This lesson content is being prepared. Check back soon!")
        
        return '\n'.join(parts)
    
    async def run(self):
        """Main run loop"""
        while True:
            if self.current_menu == "main":
                result = await self.show_main_menu()
                if result == "quit":
                    break
            elif self.current_menu == "lessons":
                result = await self.show_lessons_menu()
                if result == "back":
                    self.current_menu = "main"
            elif self.current_menu == "notes":
                result = await self.show_notes_menu()
                if result == "back":
                    self.current_menu = "main"
            elif self.current_menu == "progress":
                await self.show_progress()
                self.current_menu = "main"
            elif self.current_menu == "search":
                await self.show_search()
                self.current_menu = "main"
    
    async def show_main_menu(self) -> str:
        """Show the main menu with arrow key navigation"""
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Calculate progress stats
        total_lessons = sum(len(m["lessons"]) for m in self.curriculum["modules"])
        completed_count = len(self.progress.get("completed", []))
        progress_percent = (completed_count / total_lessons * 100) if total_lessons else 0
        
        # Create main menu items
        menu_items = [
            MenuItem(
                key="1",
                icon="📚",
                title="Browse Lessons",
                description=f"Explore {len(self.curriculum['modules'])} modules with {total_lessons} lessons",
                color=self.formatter.theme.primary
            ),
            MenuItem(
                key="2",
                icon="🎯",
                title="Continue Learning",
                description=f"Resume from: {self.progress.get('current_lesson', 'Start fresh')}",
                color=self.formatter.theme.success
            ),
            MenuItem(
                key="3",
                icon="📝",
                title="My Notes",
                description="View and manage your study notes",
                color=self.formatter.theme.info
            ),
            MenuItem(
                key="4",
                icon="📊",
                title="Progress & Stats",
                description=f"You're {progress_percent:.0f}% complete!",
                color=self.formatter.theme.warning
            ),
            MenuItem(
                key="5",
                icon="🔍",
                title="Search",
                description="Find lessons, notes, and topics",
                color=self.formatter.theme.secondary
            ),
            MenuItem(
                key="6",
                icon="💡",
                title="Practice Problems",
                description="Test your knowledge with exercises",
                color=self.formatter.theme.accent
            ),
            MenuItem(
                key="7",
                icon="🤖",
                title="Claude AI Guide",
                description="Learn how to use Claude for help",
                color=self.formatter.theme.primary
            ),
            MenuItem(
                key="8",
                icon="⚙️",
                title="Settings",
                description="Customize your learning experience",
                color=self.formatter.theme.muted
            ),
            MenuItem(
                key="Q",
                icon="🚪",
                title="Exit",
                description="Save progress and quit",
                color=self.formatter.theme.error
            )
        ]
        
        # Show menu with navigation
        selected_index, action = await self.nav_controller.show_menu(
            "🎓 Algorithm Learning Platform - Main Menu",
            menu_items,
            selected_index=0,
            mode=NavigationMode.HYBRID
        )
        
        # Handle selection
        if action == "1":
            self.current_menu = "lessons"
        elif action == "2":
            await self.continue_learning()
        elif action == "3":
            self.current_menu = "notes"
        elif action == "4":
            self.current_menu = "progress"
        elif action == "5":
            self.current_menu = "search"
        elif action == "6":
            await self.show_practice_problems()
        elif action == "7":
            await self.show_claude_guide()
        elif action == "8":
            await self.show_settings()
        elif action in ["Q", "quit"]:
            self._save_progress()
            print(self.formatter.success("\n👋 Thanks for learning! See you next time!"))
            return "quit"
        
        return "continue"
    
    async def show_lessons_menu(self) -> str:
        """Show lessons browser with modules and lessons"""
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Create menu items for modules
        menu_items = []
        completed_lessons = self.progress.get("completed", [])
        
        for module in self.curriculum["modules"]:
            # Calculate module completion
            module_lessons = [l["id"] for l in module["lessons"]]
            module_completed = sum(1 for lid in module_lessons if lid in completed_lessons)
            module_total = len(module["lessons"])
            module_percent = (module_completed / module_total * 100) if module_total else 0
            
            # Determine icon and color based on completion
            if module_percent == 100:
                icon = "✅"
                color = self.formatter.theme.success
            elif module_percent > 0:
                icon = "📊"
                color = self.formatter.theme.warning
            else:
                icon = "📘"
                color = self.formatter.theme.info
            
            menu_items.append(MenuItem(
                key=module["id"],
                icon=icon,
                title=module["title"],
                description=f"{module_completed}/{module_total} lessons completed ({module_percent:.0f}%)",
                color=color
            ))
        
        # Add back option
        menu_items.append(MenuItem(
            key="B",
            icon="🔙",
            title="Back to Main Menu",
            description="Return to the main menu",
            color=self.formatter.theme.muted
        ))
        
        # Show menu
        selected_index, action = await self.nav_controller.show_menu(
            "📚 Browse Lessons - Select a Module",
            menu_items,
            mode=NavigationMode.HYBRID
        )
        
        # Handle selection
        if action == "B" or action == "quit":
            return "back"
        else:
            # Find selected module
            for module in self.curriculum["modules"]:
                if module["id"] == action:
                    await self.show_module_lessons(module)
                    break
        
        return "continue"
    
    async def show_module_lessons(self, module: Dict):
        """Show lessons within a module"""
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Create menu items for lessons
        menu_items = []
        completed_lessons = self.progress.get("completed", [])
        
        for lesson in module["lessons"]:
            # Determine status
            if lesson["id"] in completed_lessons:
                icon = "✅"
                color = self.formatter.theme.success
                status = "Completed"
            elif lesson["id"] == self.progress.get("current_lesson"):
                icon = "▶️"
                color = self.formatter.theme.warning
                status = "In Progress"
            else:
                icon = "📖"
                color = self.formatter.theme.text
                status = "Not Started"
            
            # Create description with topics
            topics_preview = ", ".join(lesson["topics"][:2])
            if len(lesson["topics"]) > 2:
                topics_preview += f" +{len(lesson['topics'])-2} more"
            
            description = f"{status} | Topics: {topics_preview} | {lesson['practice_problems']} exercises"
            
            menu_items.append(MenuItem(
                key=lesson["id"],
                icon=icon,
                title=lesson["title"],
                description=description,
                color=color
            ))
        
        # Add back option
        menu_items.append(MenuItem(
            key="B",
            icon="🔙",
            title="Back to Modules",
            description="Return to module selection",
            color=self.formatter.theme.muted
        ))
        
        # Show menu
        selected_index, action = await self.nav_controller.show_menu(
            f"📚 {module['title']} - Select a Lesson",
            menu_items,
            mode=NavigationMode.HYBRID
        )
        
        # Handle selection
        if action == "B" or action == "quit":
            return
        else:
            # Find selected lesson
            for lesson in module["lessons"]:
                if lesson["id"] == action:
                    await self.start_lesson(lesson, module)
                    break
    
    async def start_lesson(self, lesson: Dict, module: Dict):
        """Start a lesson with beautiful formatting"""
        # Update progress
        self.progress["current_lesson"] = lesson["id"]
        self._save_progress()
        
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Use the AlgorithmTeacher to display lesson content
        if lesson["id"] == "big-o":
            self.teacher.teach_big_o_notation()
        else:
            # Normalize lesson structure for consistent formatting
            normalized_lesson = self._normalize_lesson_for_display(lesson, module)
            
            # Use enhanced formatter for beautiful consistent display
            try:
                self.enhanced_formatter.format_lesson_content(normalized_lesson)
            except Exception as e:
                # Fallback to simple display if enhanced formatting fails
                print(self.formatter.warning(f"Note: Using simplified display"))
                print(self.formatter.header(f"📖 {lesson['title']}", level=1))
                
                # Safe content display
                content_str = str(lesson.get("content", "Content coming soon..."))
                print(self.formatter.box(content_str, title="Overview", style="rounded"))
                
                # Display topics
                if lesson.get("topics"):
                    print(self.formatter.header("🎯 Key Topics", level=2))
                    for i, topic in enumerate(lesson["topics"], 1):
                        print(f"  {i}. {topic}")
                
                # Display practice problems info
                if lesson.get("practice_problems"):
                    print(self.formatter.header(f"💡 Practice Problems: {lesson['practice_problems']} available", level=3))
        
        # Lesson menu
        menu_items = [
            MenuItem("1", "📝", "Take Notes", "Capture your thoughts on this lesson"),
            MenuItem("2", "✅", "Mark Complete", "Finish this lesson and earn points"),
            MenuItem("3", "💡", "Practice", f"Try {lesson['practice_problems']} problems"),
            MenuItem("4", "🤖", "Ask Claude", "Get AI help with this topic"),
            MenuItem("B", "🔙", "Back", "Return to lesson list")
        ]
        
        selected_index, action = await self.nav_controller.show_menu(
            "What would you like to do?",
            menu_items,
            mode=NavigationMode.HYBRID
        )
        
        if action == "1":
            await self.take_lesson_notes(lesson)
        elif action == "2":
            self.mark_lesson_complete(lesson)
        elif action == "3":
            await self.show_practice_problems()
        elif action == "4":
            await self.show_claude_guide()
    
    async def take_lesson_notes(self, lesson: Dict):
        """Take notes for a lesson"""
        print(self.formatter.info(f"\n📝 Taking notes for: {lesson['title']}"))
        print("Enter your notes (press Enter twice to finish):")
        
        lines = []
        while True:
            line = input()
            if not line and lines and not lines[-1]:
                break
            lines.append(line)
        
        note_content = "\n".join(lines[:-1])  # Remove last empty line
        
        if note_content.strip():
            # Save note
            self.notes_manager.save_note(
                user_id=1,
                lesson_id=lesson["id"],
                module_name="Lessons",
                topic=lesson["title"],
                content=note_content,
                tags=[lesson["id"], "study-notes"]
            )
            print(self.formatter.success("✅ Note saved successfully!"))
        else:
            print(self.formatter.warning("No note content to save."))
        
        input("\nPress Enter to continue...")
    
    def mark_lesson_complete(self, lesson: Dict):
        """Mark a lesson as complete"""
        if lesson["id"] not in self.progress["completed"]:
            self.progress["completed"].append(lesson["id"])
            self.progress["score"] = self.progress.get("score", 0) + 10
            
            # Clear current lesson if it was this one
            if self.progress.get("current_lesson") == lesson["id"]:
                self.progress["current_lesson"] = None
            
            self._save_progress()
            print(self.formatter.success(f"\n✅ Marked '{lesson['title']}' as complete!"))
            print(self.formatter.info(f"Score: {self.progress['score']} points"))
        else:
            print(self.formatter.warning(f"\n'{lesson['title']}' is already completed."))
        
        input("\nPress Enter to continue...")
    
    async def continue_learning(self):
        """Continue from the last lesson or find next lesson"""
        current_lesson_id = self.progress.get("current_lesson")
        completed_lessons = self.progress.get("completed", [])
        
        # Find current or next lesson
        next_lesson = None
        next_module = None
        
        for module in self.curriculum["modules"]:
            for lesson in module["lessons"]:
                if current_lesson_id and lesson["id"] == current_lesson_id:
                    # Resume current lesson
                    await self.start_lesson(lesson, module)
                    return
                elif lesson["id"] not in completed_lessons and not next_lesson:
                    # Found next uncompleted lesson
                    next_lesson = lesson
                    next_module = module
        
        if next_lesson:
            print(self.formatter.info(f"\n📚 Starting next lesson: {next_lesson['title']}"))
            input("Press Enter to continue...")
            await self.start_lesson(next_lesson, next_module)
        else:
            print(self.formatter.success("\n🎉 Congratulations! You've completed all lessons!"))
            input("Press Enter to return to main menu...")
    
    async def show_notes_menu(self) -> str:
        """Show notes management menu"""
        # Use the existing notes viewer
        self.notes_viewer.view_all_notes()
        return "back"
    
    async def show_progress(self):
        """Show detailed progress and statistics"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        total_lessons = sum(len(m["lessons"]) for m in self.curriculum["modules"])
        completed_count = len(self.progress.get("completed", []))
        percentage = (completed_count / total_lessons * 100) if total_lessons else 0
        
        print(self.formatter.header("📊 Your Learning Progress", level=1))
        
        # Progress bar
        bar_length = 40
        filled = int(bar_length * percentage / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\nOverall Progress: [{bar}] {percentage:.1f}%")
        
        # Statistics
        stats_content = f"""
User: {self.progress.get('user', 'Learner')}
Level: {self.progress.get('level', 'Beginner')}
Score: {self.progress.get('score', 0)} points
Lessons Completed: {completed_count}/{total_lessons}
Last Accessed: {self.progress.get('lastAccessed', 'Never')}
Total Study Time: {self.progress.get('totalTime', 0)} minutes
"""
        print(self.formatter.box(stats_content, title="Statistics", style="rounded"))
        
        # Module breakdown
        print(self.formatter.header("Module Progress", level=2))
        for module in self.curriculum["modules"]:
            module_lessons = [l["id"] for l in module["lessons"]]
            module_completed = sum(1 for lid in module_lessons if lid in self.progress.get("completed", []))
            module_total = len(module["lessons"])
            module_percent = (module_completed / module_total * 100) if module_total else 0
            
            # Mini progress bar
            mini_bar_length = 20
            mini_filled = int(mini_bar_length * module_percent / 100)
            mini_bar = "▓" * mini_filled + "░" * (mini_bar_length - mini_filled)
            
            status_icon = "✅" if module_percent == 100 else "📊" if module_percent > 0 else "📘"
            print(f"  {status_icon} {module['title']:20} [{mini_bar}] {module_percent:.0f}%")
        
        input("\nPress Enter to continue...")
    
    async def show_search(self):
        """Show search interface"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(self.formatter.header("🔍 Search", level=1))
        print("Search for lessons, topics, or notes")
        print("\nEnter search term (or press Enter to cancel): ", end="")
        
        search_term = input().strip()
        
        if not search_term:
            return
        
        # Search results
        results = []
        
        # Search in lessons
        for module in self.curriculum["modules"]:
            for lesson in module["lessons"]:
                if (search_term.lower() in lesson["title"].lower() or
                    search_term.lower() in lesson["content"].lower() or
                    any(search_term.lower() in topic.lower() for topic in lesson["topics"])):
                    results.append({
                        "type": "lesson",
                        "module": module["title"],
                        "title": lesson["title"],
                        "content": lesson["content"]
                    })
        
        # Display results
        if results:
            print(self.formatter.success(f"\n✅ Found {len(results)} results:"))
            for i, result in enumerate(results, 1):
                if result["type"] == "lesson":
                    print(f"\n{i}. 📖 Lesson: {result['title']}")
                    print(f"   Module: {result['module']}")
                    print(f"   {result['content']}")
        else:
            print(self.formatter.warning(f"\n❌ No results found for '{search_term}'"))
        
        input("\nPress Enter to continue...")
    
    async def show_practice_problems(self):
        """Show practice problems interface"""
        print(self.formatter.info("\n💡 Practice problems coming soon!"))
        print("This feature will include:")
        print("  • Algorithm implementation challenges")
        print("  • Time/space complexity analysis")
        print("  • Real-world problem solving")
        print("  • Interactive coding exercises")
        input("\nPress Enter to continue...")
    
    async def show_claude_guide(self):
        """Show Claude AI integration guide"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        guide_content = """
How to use Claude with your learning:

1. **Ask for explanations**
   "Explain binary search with examples"
   "Why is quicksort O(n log n) on average?"

2. **Request implementations**
   "Show me how to implement a linked list in Python"
   "Write a recursive solution for fibonacci"

3. **Debug your code**
   "Why doesn't my merge sort work?"
   "Help me optimize this algorithm"

4. **Practice problems**
   "Give me 5 array manipulation problems"
   "Create a coding challenge for graphs"

5. **Interview preparation**
   "Common sorting algorithm questions"
   "Explain time complexity tradeoffs"

Tips:
• Be specific with your questions
• Ask for step-by-step explanations
• Request multiple approaches
• Ask about edge cases
• Get help with optimization
"""
        
        print(self.formatter.header("🤖 Claude AI Learning Guide", level=1))
        print(self.formatter.box(guide_content, title="How to Learn with Claude", style="rounded"))
        
        input("\nPress Enter to continue...")
    
    async def show_settings(self):
        """Show settings menu"""
        print(self.formatter.info("\n⚙️ Settings"))
        print("1. Reset progress")
        print("2. Change color theme")
        print("3. Export data")
        print("4. Import data")
        
        choice = input("\nEnter choice (or press Enter to cancel): ").strip()
        
        if choice == "1":
            confirm = input("Are you sure you want to reset all progress? (yes/no): ")
            if confirm.lower() == "yes":
                self.progress = {
                    "user": "learner",
                    "level": "foundation",
                    "completed": [],
                    "score": 0,
                    "lastAccessed": None,
                    "totalTime": 0,
                    "current_lesson": None
                }
                self._save_progress()
                print(self.formatter.success("✅ Progress reset successfully!"))
        
        input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    menu_system = MainMenuSystem()
    
    # Show welcome message
    print(menu_system.formatter.header("🎓 Welcome to Algorithm Learning Platform!", level=1))
    print(menu_system.formatter.info("Master algorithms and data structures with interactive learning"))
    print(menu_system.formatter.success("Now with arrow key navigation! Use ↑↓ or number keys."))
    input("\nPress Enter to start...")
    
    # Run the menu system
    try:
        asyncio.run(menu_system.run())
    except KeyboardInterrupt:
        print(menu_system.formatter.success("\n\n👋 Thanks for learning! See you next time!"))
    except Exception as e:
        print(menu_system.formatter.error(f"\nError: {e}"))
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()