"""Advanced features module for Unsplash Image Search application.

This module contains enhanced functionality including:
- Advanced search capabilities
- Collection management
- Learning features
- Session management
- Batch operations
"""

from .advanced_search import AdvancedSearchManager
from .collections import CollectionManager
from .learning import LearningSystem
from .session_manager import SessionManager
from .batch_operations import BatchOperations

__all__ = [
    'AdvancedSearchManager',
    'CollectionManager', 
    'LearningSystem',
    'SessionManager',
    'BatchOperations'
]