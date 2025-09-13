#!/usr/bin/env python3
"""
Progress Management - Handles user progress tracking and persistence
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict


@dataclass
class UserProgress:
    """User progress data model"""
    user: str = "learner"
    level: str = "foundation"
    completed: List[str] = field(default_factory=list)
    current_lesson: Optional[str] = None
    score: int = 0
    scores: Dict[str, int] = field(default_factory=dict)
    achievements: List[str] = field(default_factory=list)
    last_accessed: Optional[str] = None
    total_time: int = 0  # in minutes
    preferences: Dict[str, Any] = field(default_factory=lambda: {
        "learning_path": "visual",
        "difficulty": "beginner",
        "notifications": True
    })
    
    def mark_lesson_complete(self, lesson_id: str, points: int = 10):
        """Mark a lesson as complete"""
        if lesson_id not in self.completed:
            self.completed.append(lesson_id)
            self.score += points
            self.scores[lesson_id] = points
            
            # Clear current lesson if it was this one
            if self.current_lesson == lesson_id:
                self.current_lesson = None
    
    def set_current_lesson(self, lesson_id: str):
        """Set the current lesson being studied"""
        self.current_lesson = lesson_id
        self.last_accessed = datetime.now().isoformat()
    
    def get_completion_percentage(self, total_lessons: int) -> float:
        """Calculate completion percentage"""
        if total_lessons == 0:
            return 0.0
        return (len(self.completed) / total_lessons) * 100
    
    def add_achievement(self, achievement: str):
        """Add an achievement"""
        if achievement not in self.achievements:
            self.achievements.append(achievement)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['last_accessed'] = self.last_accessed or datetime.now().isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProgress':
        """Create from dictionary"""
        return cls(
            user=data.get('user', 'learner'),
            level=data.get('level', 'foundation'),
            completed=data.get('completed', []),
            current_lesson=data.get('current_lesson'),
            score=data.get('score', 0),
            scores=data.get('scores', {}),
            achievements=data.get('achievements', []),
            last_accessed=data.get('last_accessed'),
            total_time=data.get('total_time', 0),
            preferences=data.get('preferences', {
                "learning_path": "visual",
                "difficulty": "beginner",
                "notifications": True
            })
        )


class ProgressManager:
    """Manages user progress persistence and operations"""
    
    def __init__(self, progress_file: Optional[Path] = None):
        """Initialize progress manager
        
        Args:
            progress_file: Path to progress JSON file
        """
        self.progress_file = progress_file or Path("progress.json")
        self.progress = self._load_progress()
    
    def _load_progress(self) -> UserProgress:
        """Load progress from file"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    return UserProgress.from_dict(data)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load progress file: {e}")
                return UserProgress()
        return UserProgress()
    
    def save(self):
        """Save progress to file"""
        self.progress.last_accessed = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress.to_dict(), f, indent=2)
    
    def reset(self):
        """Reset all progress"""
        self.progress = UserProgress()
        self.save()
    
    def mark_lesson_complete(self, lesson_id: str, points: int = 10):
        """Mark a lesson as complete and save"""
        self.progress.mark_lesson_complete(lesson_id, points)
        self.save()
    
    def set_current_lesson(self, lesson_id: str):
        """Set current lesson and save"""
        self.progress.set_current_lesson(lesson_id)
        self.save()
    
    def update_preference(self, key: str, value: Any):
        """Update a user preference"""
        self.progress.preferences[key] = value
        self.save()
    
    def add_study_time(self, minutes: int):
        """Add study time to total"""
        self.progress.total_time += minutes
        self.save()
    
    def get_module_progress(self, module_lessons: List[str]) -> Dict[str, Any]:
        """Get progress for a specific module
        
        Args:
            module_lessons: List of lesson IDs in the module
            
        Returns:
            Dictionary with completion stats
        """
        completed = sum(1 for lid in module_lessons if lid in self.progress.completed)
        total = len(module_lessons)
        percentage = (completed / total * 100) if total > 0 else 0
        
        return {
            'completed': completed,
            'total': total,
            'percentage': percentage,
            'is_complete': completed == total
        }