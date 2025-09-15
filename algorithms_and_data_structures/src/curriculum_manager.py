#!/usr/bin/env python3
"""
Curriculum Manager
Centralized management for curriculum operations with beautiful display
"""

import json
import asyncio
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime

# Handle relative imports when running as script
try:
    from .ui.windows_formatter import WindowsFormatter, WindowsColor
except ImportError:
    # If running as script, try absolute import
    from ui.windows_formatter import WindowsFormatter, WindowsColor
# Handle relative imports when running as script
try:
    from .utils.terminal_utils import terminal_utils, get_terminal_width, create_safe_box, wrap_text_safe
except ImportError:
    # If running as script, try absolute import
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__)))
    from utils.terminal_utils import terminal_utils, get_terminal_width, create_safe_box, wrap_text_safe


class CurriculumManager:
    """Centralized curriculum management system"""
    
    def __init__(self):
        self.formatter = WindowsFormatter()
        self.data_dir = Path("data")
        self.curriculum_file = self.data_dir / "curriculum.json"
        self.enhanced_curriculum_file = self.data_dir / "curriculum_enhanced.json"
        self._ensure_data_directory()
        self.curriculum_data = self._load_curriculum_data()
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        self.data_dir.mkdir(exist_ok=True)
    
    def _load_curriculum_data(self) -> Dict[str, Any]:
        """Load curriculum data from files"""
        # Try enhanced curriculum first, fall back to basic
        for curriculum_file in [self.enhanced_curriculum_file, self.curriculum_file]:
            if curriculum_file.exists():
                try:
                    with open(curriculum_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Check if this is old format (modules only) and convert to new format
                        if 'curricula' not in data and 'modules' in data:
                            return self._convert_old_to_new_format(data)
                        return data
                except json.JSONDecodeError:
                    continue
        
        # Return default curriculum if no files exist
        return self._get_default_curriculum_data()
    
    def _convert_old_to_new_format(self, old_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert old curriculum format (modules only) to new format (with curricula)"""
        modules = old_data.get('modules', [])
        
        # Count lessons across all modules
        total_lessons = sum(len(m.get('lessons', [])) for m in modules)
        
        # Create a single main curriculum from the old modules
        main_curriculum = {
            "id": 1,
            "name": "Complete Algorithms & Data Structures",
            "description": "Master computer science fundamentals with hands-on learning",
            "status": "active",
            "difficulty": "intermediate", 
            "category": "Computer Science",
            "author": "Learning Platform",
            "tags": ["algorithms", "data-structures", "computer-science", "programming"],
            "created": "2024-01-01T00:00:00",
            "updated": datetime.now().isoformat(),
            "modules": len(modules),
            "lessons": total_lessons,
            "students": 150,
            "completion_rate": 85.5,
            "average_rating": 4.7,
            "total_duration": "40-60 hours"
        }
        
        # Create new format with curricula and modules
        new_data = {
            "metadata": {
                "title": "Algorithms & Data Structures Curriculum",
                "version": "2.0",
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
                "total_modules": len(modules),
                "estimated_hours": 120,
                "difficulty": "beginner-to-advanced"
            },
            "curricula": [main_curriculum],
            "modules": modules
        }
        
        return new_data
    
    def _get_default_curriculum_data(self) -> Dict[str, Any]:
        """Get default curriculum data structure"""
        return {
            "metadata": {
                "title": "Algorithms & Data Structures Curriculum",
                "version": "2.0",
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
                "total_modules": 3,
                "estimated_hours": 120,
                "difficulty": "beginner-to-advanced"
            },
            "curricula": [
                {
                    "id": 1,
                    "name": "Complete Algorithms & Data Structures",
                    "description": "Master computer science fundamentals with hands-on learning",
                    "status": "active",
                    "difficulty": "intermediate",
                    "category": "Computer Science",
                    "author": "Learning Platform",
                    "tags": ["algorithms", "data-structures", "computer-science", "programming"],
                    "created": "2024-01-01T00:00:00",
                    "updated": datetime.now().isoformat(),
                    "modules": 3,
                    "lessons": 8,
                    "students": 150,
                    "completion_rate": 85.5,
                    "average_rating": 4.7,
                    "total_duration": "40-60 hours"
                },
                {
                    "id": 2, 
                    "name": "Advanced Algorithm Techniques",
                    "description": "Deep dive into advanced algorithmic concepts and optimization",
                    "status": "active",
                    "difficulty": "advanced",
                    "category": "Computer Science",
                    "author": "Learning Platform",
                    "tags": ["advanced-algorithms", "optimization", "dynamic-programming", "graph-theory"],
                    "created": "2024-01-15T00:00:00",
                    "updated": datetime.now().isoformat(),
                    "modules": 4,
                    "lessons": 12,
                    "students": 75,
                    "completion_rate": 70.2,
                    "average_rating": 4.9,
                    "total_duration": "60-80 hours"
                },
                {
                    "id": 3,
                    "name": "Data Structures Foundations",
                    "description": "Essential data structures every programmer should know",
                    "status": "active",
                    "difficulty": "beginner",
                    "category": "Computer Science", 
                    "author": "Learning Platform",
                    "tags": ["data-structures", "arrays", "linked-lists", "trees", "hash-tables"],
                    "created": "2024-02-01T00:00:00",
                    "updated": datetime.now().isoformat(),
                    "modules": 5,
                    "lessons": 15,
                    "students": 200,
                    "completion_rate": 92.3,
                    "average_rating": 4.5,
                    "total_duration": "30-45 hours"
                }
            ],
            "modules": [
                {
                    "id": "foundations",
                    "curriculum_id": 1,
                    "title": "Foundations",
                    "description": "Essential concepts and complexity analysis",
                    "order": 1,
                    "lessons": [
                        {
                            "id": "big-o",
                            "title": "Big O Notation & Complexity Analysis",
                            "content": "Understanding algorithmic complexity and performance analysis",
                            "description": "Learn to analyze and compare algorithm efficiency",
                            "topics": ["O(1) Constant Time", "O(n) Linear Time", "O(log n) Logarithmic", "O(n²) Quadratic", "Space Complexity"],
                            "objectives": [
                                "Understand time and space complexity concepts",
                                "Analyze algorithms using Big O notation",
                                "Compare algorithm efficiency",
                                "Identify optimization opportunities"
                            ],
                            "difficulty": "Beginner",
                            "time": "15-20 min",
                            "practice_problems": 5,
                            "prerequisites": "Basic programming knowledge"
                        },
                        {
                            "id": "arrays",
                            "title": "Arrays & Dynamic Arrays",
                            "content": "Understanding fixed and dynamic array data structures",
                            "description": "Master array operations and dynamic resizing",
                            "topics": ["Array Basics", "Dynamic Resizing", "Amortized Analysis", "Memory Layout", "Cache Performance"],
                            "objectives": [
                                "Implement array operations efficiently",
                                "Understand dynamic array growth strategies",
                                "Analyze amortized time complexity",
                                "Optimize memory usage patterns"
                            ],
                            "difficulty": "Beginner",
                            "time": "20-25 min",
                            "practice_problems": 8,
                            "prerequisites": "Big O notation"
                        }
                    ]
                },
                {
                    "id": "searching",
                    "curriculum_id": 1,
                    "title": "Searching Algorithms",
                    "description": "Efficient techniques for finding elements in collections",
                    "order": 2,
                    "lessons": [
                        {
                            "id": "linear-search",
                            "title": "Linear Search",
                            "content": "Sequential searching through collections",
                            "description": "Basic search algorithm with O(n) complexity",
                            "topics": ["Sequential Access", "Best/Worst Cases", "Optimizations", "Use Cases"],
                            "objectives": [
                                "Implement linear search algorithm",
                                "Understand when to use linear search",
                                "Optimize search performance",
                                "Handle edge cases properly"
                            ],
                            "difficulty": "Beginner",
                            "time": "10-15 min",
                            "practice_problems": 3,
                            "prerequisites": "Arrays"
                        },
                        {
                            "id": "binary-search",
                            "title": "Binary Search",
                            "content": "Efficient O(log n) searching in sorted arrays",
                            "description": "Divide-and-conquer approach for sorted collections",
                            "topics": ["Divide & Conquer", "Loop Implementation", "Recursive Implementation", "Boundary Conditions", "Variations"],
                            "objectives": [
                                "Master binary search implementation",
                                "Handle boundary conditions correctly",
                                "Apply binary search to various problems",
                                "Understand logarithmic complexity benefits"
                            ],
                            "difficulty": "Intermediate", 
                            "time": "25-30 min",
                            "practice_problems": 6,
                            "prerequisites": "Linear search, Sorted arrays"
                        }
                    ]
                },
                {
                    "id": "sorting",
                    "curriculum_id": 1,
                    "title": "Sorting Algorithms",
                    "description": "Algorithms for ordering data efficiently",
                    "order": 3,
                    "lessons": [
                        {
                            "id": "bubble-sort",
                            "title": "Bubble Sort",
                            "content": "Simple comparison-based sorting algorithm",
                            "description": "Educational sorting algorithm with O(n²) complexity",
                            "topics": ["Comparison Sorting", "Swapping Elements", "Optimization Techniques", "Stability"],
                            "objectives": [
                                "Understand basic sorting principles",
                                "Implement bubble sort algorithm",
                                "Analyze quadratic time complexity",
                                "Recognize when simpler algorithms suffice"
                            ],
                            "difficulty": "Beginner",
                            "time": "15-20 min",
                            "practice_problems": 4,
                            "prerequisites": "Arrays, Big O notation"
                        },
                        {
                            "id": "quicksort",
                            "title": "QuickSort",
                            "content": "Efficient divide-and-conquer sorting algorithm",
                            "description": "High-performance sorting with average O(n log n) complexity",
                            "topics": ["Partitioning", "Pivot Selection", "Recursive Structure", "Worst-Case Analysis", "Optimizations"],
                            "objectives": [
                                "Master quicksort implementation",
                                "Understand partitioning strategies",
                                "Choose optimal pivot selection methods",
                                "Optimize for real-world performance"
                            ],
                            "difficulty": "Intermediate",
                            "time": "35-40 min", 
                            "practice_problems": 7,
                            "prerequisites": "Recursion, Bubble sort"
                        }
                    ]
                }
            ]
        }
    
    def display_curriculum_banner(self):
        """Display beautiful curriculum banner with safe terminal sizing"""
        banner_content = """🎓 ALGORITHMS & DATA STRUCTURES CURRICULUM SYSTEM 🎓

📚 Master Computer Science Fundamentals
⚡ Interactive Learning & Practice Problems  
🤖 AI-Powered Explanations & Guidance
📊 Progress Tracking & Analytics"""
        
        # Use safe box creation that respects terminal width
        banner = create_safe_box(banner_content, width=get_terminal_width())
        print(self.formatter._color(banner, self.formatter.theme.primary))
    
    def display_curriculum_list(self, curricula: List[Dict], format_type: str = "table"):
        """Display curriculum list with beautiful formatting"""
        if format_type == "json":
            print(json.dumps(curricula, indent=2, default=str))
            return
        
        if not curricula:
            self.formatter.warning("📚 No curricula found matching the criteria")
            return
        
        # Beautiful header
        self.display_curriculum_banner()
        
        # Summary statistics
        total_curricula = len(curricula)
        total_students = sum(c.get('students', 0) for c in curricula)
        avg_rating = sum(c.get('average_rating', 0) for c in curricula) / total_curricula if curricula else 0
        
        summary_content = f"""📊 CURRICULUM OVERVIEW

📚 Total Curricula: {total_curricula}
👥 Total Students: {total_students:,}
⭐ Average Rating: {avg_rating:.1f}/5.0
🔥 Active Programs: {len([c for c in curricula if c.get('status') == 'active'])}"""
        
        # Use safe box creation
        summary_box = create_safe_box(summary_content)
        colored_box = self.formatter._color(summary_box, self.formatter.theme.info)
        print("\n" + colored_box)
        
        # Display curricula with enhanced formatting
        term_width = get_terminal_width()
        divider = terminal_utils.create_horizontal_rule("AVAILABLE CURRICULA", width=term_width)
        print("\n" + self.formatter._color(divider, self.formatter.theme.primary, WindowsColor.BOLD))
        
        for i, curriculum in enumerate(curricula, 1):
            self._display_curriculum_card(curriculum, i)
    
    def _display_curriculum_card(self, curriculum: Dict, index: int):
        """Display a single curriculum as a beautiful card"""
        # Status indicators
        status_icons = {
            "active": "🟢",
            "draft": "🟡", 
            "archived": "🔴",
            "published": "🟢"
        }
        
        difficulty_colors = {
            "beginner": self.formatter.theme.success,
            "intermediate": self.formatter.theme.warning,
            "advanced": self.formatter.theme.error,
            "expert": self.formatter.theme.primary
        }
        
        status = curriculum.get('status', 'draft')
        difficulty = curriculum.get('difficulty', 'beginner')
        
        status_icon = status_icons.get(status, "🔘")
        difficulty_color = difficulty_colors.get(difficulty, self.formatter.theme.text)
        
        # Card header
        title = f"#{curriculum['id']} {curriculum['name']}"
        print(f"\n{self.formatter._color(title, self.formatter.theme.primary, WindowsColor.BOLD)}")
        
        # Status and difficulty line
        status_line = f"{status_icon} {status.upper()}  |  "
        difficulty_text = f"🎯 {difficulty.title()}"
        print(f"  {status_line}{self.formatter._color(difficulty_text, difficulty_color)}")
        
        # Description with safe wrapping
        desc = curriculum.get('description', 'No description available')
        wrapped_lines = wrap_text_safe(desc, get_terminal_width() - 6)
        for i, line in enumerate(wrapped_lines):
            prefix = "  📝 " if i == 0 else "     "
            print(f"{prefix}{line}")
        
        # Metadata
        metadata_items = [
            ("Category", curriculum.get('category', 'N/A')),
            ("Author", curriculum.get('author', 'Unknown')),
            ("Modules", str(curriculum.get('modules', 0))),
            ("Lessons", str(curriculum.get('lessons', 0)))
        ]
        
        meta_line = "  📊 "
        for i, (key, value) in enumerate(metadata_items):
            if i > 0:
                meta_line += " | "
            meta_line += f"{key}: {self.formatter._color(value, self.formatter.theme.secondary)}"
        print(meta_line)
        
        # Statistics (if available)
        if curriculum.get('students'):
            stats_items = [
                ("👥", f"{curriculum.get('students', 0):,} students"),
                ("✅", f"{curriculum.get('completion_rate', 0):.1f}% completion"),
                ("⭐", f"{curriculum.get('average_rating', 0):.1f}/5.0 rating"),
                ("⏱️", curriculum.get('total_duration', 'Time varies'))
            ]
            
            stats_line = "  "
            for icon, stat in stats_items:
                stats_line += f"{icon} {stat}  "
            print(stats_line)
        
        # Tags
        if curriculum.get('tags'):
            tags_line = "  🏷️  "
            tags = curriculum['tags'][:5]  # Limit to first 5 tags
            for tag in tags:
                tags_line += f"#{tag} "
            if len(curriculum['tags']) > 5:
                tags_line += f"+{len(curriculum['tags']) - 5} more"
            print(self.formatter._color(tags_line, self.formatter.theme.muted))
        
        # Separator with safe width
        separator_width = min(76, get_terminal_width() - 4)
        print("  " + self.formatter._color("-" * separator_width, self.formatter.theme.muted))
    
    def _wrap_text(self, text: str, max_width: int) -> str:
        """Wrap text to specified width using safe terminal utilities"""
        return terminal_utils.truncate_text(text, max_width)
    
    def display_curriculum_details(self, curriculum: Dict, include_modules: bool = False, include_stats: bool = False):
        """Display detailed curriculum information"""
        self.display_curriculum_banner()
        
        # Main curriculum header
        title = curriculum['name']
        subtitle = f"{curriculum['category']} | {curriculum['difficulty'].title()} Level"
        
        header_content = f"""🎓 {title}
{subtitle}"""
        header_box = create_safe_box(header_content, title="CURRICULUM DETAILS")
        print("\n" + header_box)
        
        # Description section with safe box
        if curriculum.get('description'):
            desc_content = curriculum['description']
            desc_box = create_safe_box(desc_content, title="📚 WHAT YOU'LL LEARN")
            print("\n" + desc_box)
        
        # Basic information panel
        basic_info = [
            ("Status", curriculum.get('status', 'Unknown').upper()),
            ("Author", curriculum.get('author', 'Unknown')),
            ("Created", curriculum.get('created', 'Unknown')),
            ("Last Updated", curriculum.get('updated', 'Unknown')),
            ("Total Modules", str(curriculum.get('modules', 0))),
            ("Total Lessons", str(curriculum.get('lessons', 0)))
        ]
        
        print("\n📊 CURRICULUM OVERVIEW")
        for key, value in basic_info:
            key_colored = self.formatter._color(f"{key:15}", self.formatter.theme.secondary)
            value_colored = self.formatter._color(value, self.formatter.theme.info)
            print(f"  {key_colored} {value_colored}")
        
        # Tags section with safe box
        if curriculum.get('tags'):
            tags_text = " • ".join([f"#{tag}" for tag in curriculum['tags']])
            tags_box = create_safe_box(tags_text, title="🏷️ TOPICS COVERED")
            print("\n" + tags_box)
        
        # Statistics section (if requested and available)
        if include_stats and curriculum.get('students'):
            stats = [
                ("👥 Students Enrolled", f"{curriculum.get('students', 0):,}"),
                ("✅ Completion Rate", f"{curriculum.get('completion_rate', 0):.1f}%"),
                ("⭐ Average Rating", f"{curriculum.get('average_rating', 0):.1f}/5.0"),
                ("⏱️ Total Duration", curriculum.get('total_duration', 'Not specified'))
            ]
            
            print("\n📈 PERFORMANCE METRICS")
            for icon_label, value in stats:
                print(f"  {icon_label:<25} {self.formatter._color(value, self.formatter.theme.success)}")
        
        # Modules section (if requested)
        if include_modules:
            modules = self._get_curriculum_modules(curriculum['id'])
            if modules:
                print("\n" + self.formatter._color("📚 CURRICULUM MODULES", self.formatter.theme.primary, WindowsColor.BOLD))
                
                for i, module in enumerate(modules, 1):
                    module_title = f"{i}. {module['title']}"
                    print(f"\n  {self.formatter._color(module_title, self.formatter.theme.info, WindowsColor.BOLD)}")
                    print(f"     {module.get('description', 'No description available')}")
                    
                    lessons = module.get('lessons', [])
                    if lessons:
                        print(f"     📝 Lessons: {len(lessons)}")
                        for lesson in lessons[:3]:  # Show first 3 lessons
                            print(f"       • {lesson['title']}")
                        if len(lessons) > 3:
                            print(f"       • +{len(lessons) - 3} more lessons...")
    
    def _get_curriculum_modules(self, curriculum_id: int) -> List[Dict]:
        """Get modules for a specific curriculum"""
        modules = self.curriculum_data.get('modules', [])
        return [m for m in modules if m.get('curriculum_id') == curriculum_id]
    
    def get_curricula(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Get curricula with optional filtering"""
        curricula = self.curriculum_data.get('curricula', [])
        
        if not filters:
            return curricula
        
        filtered = curricula
        
        # Apply filters
        if filters.get('status'):
            filtered = [c for c in filtered if c.get('status') == filters['status']]
        
        if filters.get('difficulty'):
            filtered = [c for c in filtered if c.get('difficulty') == filters['difficulty']]
        
        if filters.get('category'):
            category_filter = filters['category'].lower()
            filtered = [c for c in filtered if category_filter in c.get('category', '').lower()]
        
        if filters.get('author'):
            author_filter = filters['author'].lower()
            filtered = [c for c in filtered if author_filter in c.get('author', '').lower()]
        
        if filters.get('tags'):
            for tag in filters['tags']:
                filtered = [c for c in filtered if tag in c.get('tags', [])]
        
        if filters.get('search'):
            search_term = filters['search'].lower()
            filtered = [c for c in filtered 
                       if search_term in c.get('name', '').lower() or 
                          search_term in c.get('description', '').lower()]
        
        return filtered
    
    def find_curriculum_by_id(self, curriculum_id: int) -> Optional[Dict]:
        """Find curriculum by ID"""
        curricula = self.curriculum_data.get('curricula', [])
        for curriculum in curricula:
            if curriculum.get('id') == curriculum_id:
                return curriculum
        return None
    
    def find_curriculum_by_name(self, name: str) -> Optional[Dict]:
        """Find curriculum by name (partial match)"""
        curricula = self.curriculum_data.get('curricula', [])
        name_lower = name.lower()
        for curriculum in curricula:
            if name_lower in curriculum.get('name', '').lower():
                return curriculum
        return None
    
    def get_curriculum_statistics(self) -> Dict[str, Any]:
        """Get overall curriculum statistics"""
        curricula = self.curriculum_data.get('curricula', [])
        modules = self.curriculum_data.get('modules', [])
        
        total_lessons = sum(len(m.get('lessons', [])) for m in modules)
        total_students = sum(c.get('students', 0) for c in curricula)
        
        stats = {
            'total_curricula': len(curricula),
            'total_modules': len(modules),
            'total_lessons': total_lessons,
            'total_students': total_students,
            'active_curricula': len([c for c in curricula if c.get('status') == 'active']),
            'average_rating': sum(c.get('average_rating', 0) for c in curricula) / len(curricula) if curricula else 0,
            'completion_rates': [c.get('completion_rate', 0) for c in curricula if c.get('completion_rate')]
        }
        
        return stats
    
    def save_curriculum_data(self):
        """Save curriculum data to file"""
        with open(self.enhanced_curriculum_file, 'w', encoding='utf-8') as f:
            json.dump(self.curriculum_data, f, indent=2, ensure_ascii=False)
