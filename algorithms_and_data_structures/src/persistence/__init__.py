"""
Persistence Layer for CLI Application

This package provides a robust data persistence layer with support for multiple
storage backends, repository patterns, and advanced features like caching,
migrations, and backup/restore functionality.
"""

from .db_manager import DatabaseManager
from .storage_backend import StorageBackend, JSONBackend, SQLiteBackend, PostgreSQLBackend
from .repositories.base import BaseRepository
from .repositories.curriculum_repo import CurriculumRepository
from .repositories.content_repo import ContentRepository  
from .repositories.progress_repo import ProgressRepository

__all__ = [
    'DatabaseManager',
    'StorageBackend',
    'JSONBackend', 
    'SQLiteBackend',
    'PostgreSQLBackend',
    'BaseRepository',
    'CurriculumRepository',
    'ContentRepository',
    'ProgressRepository'
]

__version__ = "1.0.0"