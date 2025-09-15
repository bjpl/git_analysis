"""
Data models for the curriculum management CLI.

This package contains all data models for the curriculum management system:
- BaseModel: Common functionality for all models
- User: Learner profiles and authentication
- Content: Different content types and materials
- Curriculum: Hierarchical curriculum structure
- Progress: User progress tracking
"""

from .base import BaseModel
from .user import User, UserProfile, LearningPreferences
from .content import Content, ContentType, ContentMetadata
from .curriculum import Curriculum, Course, Module, Lesson
from .progress import Progress, CompletionStatus, ProgressMetrics

__all__ = [
    'BaseModel',
    'User', 'UserProfile', 'LearningPreferences',
    'Content', 'ContentType', 'ContentMetadata',
    'Curriculum', 'Course', 'Module', 'Lesson',
    'Progress', 'CompletionStatus', 'ProgressMetrics'
]