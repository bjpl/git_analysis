"""UI components for advanced features."""

from .advanced_search_panel import AdvancedSearchPanel
from .collection_browser import CollectionBrowser
from .learning_dashboard import LearningDashboard
from .session_browser import SessionBrowser
from .batch_processor import BatchProcessor
from .vocabulary_manager import VocabularyManager
from .search_history_widget import SearchHistoryWidget
from .flashcard_widget import FlashcardWidget

__all__ = [
    'AdvancedSearchPanel',
    'CollectionBrowser',
    'LearningDashboard',
    'SessionBrowser',
    'BatchProcessor',
    'VocabularyManager',
    'SearchHistoryWidget',
    'FlashcardWidget'
]