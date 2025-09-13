#!/usr/bin/env python3
"""
Curriculum Management - Core business logic for curriculum data
Handles loading, validation, and access to curriculum content
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field


@dataclass
class Lesson:
    """Represents a single lesson"""
    id: str
    title: str
    content: str
    topics: List[str] = field(default_factory=list)
    practice_problems: int = 0
    difficulty: str = "beginner"
    est_time: str = "10-15 min"
    prerequisites: List[str] = field(default_factory=list)
    objectives: List[str] = field(default_factory=list)
    code_examples: List[Dict] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Lesson':
        """Create Lesson from dictionary"""
        return cls(
            id=data.get('id', 'unknown'),
            title=data.get('title', 'Untitled'),
            content=data.get('content', ''),
            topics=data.get('topics', []),
            practice_problems=data.get('practice_problems', 0),
            difficulty=data.get('difficulty', 'beginner'),
            est_time=data.get('est_time', '10-15 min'),
            prerequisites=data.get('prerequisites', []),
            objectives=data.get('objectives', []),
            code_examples=data.get('code_examples', [])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for display"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'topics': self.topics,
            'practice_problems': self.practice_problems,
            'difficulty': self.difficulty,
            'est_time': self.est_time,
            'prerequisites': self.prerequisites,
            'objectives': self.objectives,
            'code_examples': self.code_examples
        }


@dataclass
class Module:
    """Represents a curriculum module"""
    id: str
    title: str
    lessons: List[Lesson]
    description: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Module':
        """Create Module from dictionary"""
        lessons = [Lesson.from_dict(l) for l in data.get('lessons', [])]
        return cls(
            id=data.get('id', 'unknown'),
            title=data.get('title', 'Untitled Module'),
            lessons=lessons,
            description=data.get('description', '')
        )
    
    def get_lesson(self, lesson_id: str) -> Optional[Lesson]:
        """Get a specific lesson by ID"""
        for lesson in self.lessons:
            if lesson.id == lesson_id:
                return lesson
        return None


class CurriculumManager:
    """Manages curriculum data and operations"""
    
    def __init__(self, curriculum_path: Optional[Path] = None):
        """Initialize curriculum manager
        
        Args:
            curriculum_path: Path to curriculum JSON file
        """
        self.curriculum_path = curriculum_path or self._find_curriculum_file()
        self.modules: List[Module] = []
        self._load_curriculum()
    
    def _find_curriculum_file(self) -> Path:
        """Find the curriculum file"""
        # Try enhanced curriculum first
        enhanced = Path("data/curriculum_enhanced.json")
        if enhanced.exists():
            return enhanced
        
        # Fall back to basic curriculum
        basic = Path("data/curriculum.json")
        if basic.exists():
            return basic
        
        # Return path even if doesn't exist (will use defaults)
        return Path("data/curriculum.json")
    
    def _load_curriculum(self):
        """Load curriculum from file"""
        if self.curriculum_path.exists():
            with open(self.curriculum_path, 'r') as f:
                data = json.load(f)
                self.modules = [Module.from_dict(m) for m in data.get('modules', [])]
        else:
            # Load default curriculum
            self.modules = self._get_default_modules()
    
    def _get_default_modules(self) -> List[Module]:
        """Get default curriculum modules"""
        return [
            Module(
                id="foundations",
                title="Foundations",
                lessons=[
                    Lesson(
                        id="big-o",
                        title="Big O Notation",
                        content="Understanding time and space complexity",
                        topics=["Time Complexity", "Space Complexity", "Growth Rates", "Complexity Analysis"],
                        practice_problems=8,
                        difficulty="beginner"
                    ),
                    Lesson(
                        id="arrays",
                        title="Arrays & Dynamic Arrays",
                        content="Fixed and dynamic array implementations",
                        topics=["Array basics", "Dynamic resizing", "Amortized analysis"],
                        practice_problems=10,
                        difficulty="beginner"
                    )
                ]
            ),
            Module(
                id="searching",
                title="Searching Algorithms",
                lessons=[
                    Lesson(
                        id="linear-search",
                        title="Linear Search",
                        content="Sequential searching through collections",
                        topics=["Implementation", "When to use", "Optimizations"],
                        practice_problems=5,
                        difficulty="beginner"
                    ),
                    Lesson(
                        id="binary-search",
                        title="Binary Search",
                        content="Efficient searching in sorted arrays",
                        topics=["Implementation", "Requirements", "Variations"],
                        practice_problems=8,
                        difficulty="intermediate"
                    )
                ]
            )
        ]
    
    def get_all_modules(self) -> List[Module]:
        """Get all curriculum modules"""
        return self.modules
    
    def get_module(self, module_id: str) -> Optional[Module]:
        """Get a specific module by ID"""
        for module in self.modules:
            if module.id == module_id:
                return module
        return None
    
    def get_lesson(self, lesson_id: str) -> Optional[Tuple[Lesson, Module]]:
        """Get a lesson and its parent module"""
        for module in self.modules:
            lesson = module.get_lesson(lesson_id)
            if lesson:
                return lesson, module
        return None
    
    def get_total_lessons(self) -> int:
        """Get total number of lessons"""
        return sum(len(module.lessons) for module in self.modules)
    
    def get_next_lesson(self, current_lesson_id: str, completed_ids: List[str]) -> Optional[Tuple[Lesson, Module]]:
        """Get the next uncompleted lesson
        
        Args:
            current_lesson_id: Current lesson ID (if any)
            completed_ids: List of completed lesson IDs
            
        Returns:
            Next lesson and module, or None if all completed
        """
        # First, try to find the lesson after the current one
        found_current = False
        
        for module in self.modules:
            for lesson in module.lessons:
                if found_current and lesson.id not in completed_ids:
                    return lesson, module
                if lesson.id == current_lesson_id:
                    found_current = True
        
        # If no current lesson or no next lesson found, find first uncompleted
        for module in self.modules:
            for lesson in module.lessons:
                if lesson.id not in completed_ids:
                    return lesson, module
        
        return None