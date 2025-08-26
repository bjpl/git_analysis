"""
Enhanced Vocabulary Management System
=====================================

A comprehensive vocabulary management system with advanced features including:
- Word frequency tracking and learning statistics
- Categorization by difficulty, theme, and custom tags
- Spaced repetition scheduling integration
- Import/export with multiple formats
- Session history and progress analytics
- User preference tracking and personalization
- Performance optimization with caching
- Data integrity and backup systems
"""

import json
import sqlite3
import csv
import hashlib
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
from collections import defaultdict, Counter
import math


class DifficultyLevel(Enum):
    """Word difficulty levels for learning optimization."""
    BEGINNER = 1      # Common, high-frequency words
    ELEMENTARY = 2    # Basic vocabulary
    INTERMEDIATE = 3  # Standard vocabulary
    ADVANCED = 4      # Complex or specialized terms
    EXPERT = 5        # Rare or technical vocabulary
    UNKNOWN = 0       # Not yet classified


class WordStatus(Enum):
    """Learning status of vocabulary words."""
    NEW = "new"                    # Just discovered/added
    LEARNING = "learning"          # Currently being studied
    REVIEWING = "reviewing"        # In spaced repetition cycle
    MASTERED = "mastered"          # Well-learned, long intervals
    SUSPENDED = "suspended"        # Temporarily removed from study
    ARCHIVED = "archived"          # Permanently stored, not active


class SourceType(Enum):
    """Sources where vocabulary was discovered."""
    IMAGE_DESCRIPTION = "image_description"
    MANUAL_ENTRY = "manual_entry"
    IMPORT_CSV = "import_csv"
    IMPORT_ANKI = "import_anki"
    WEB_LOOKUP = "web_lookup"
    CONVERSATION = "conversation"
    READING = "reading"


@dataclass
class WordFrequency:
    """Frequency tracking for vocabulary words."""
    word: str
    encounters: int = 0                    # Total times encountered
    study_sessions: int = 0                # Times studied/reviewed
    correct_responses: int = 0             # Correct quiz answers
    incorrect_responses: int = 0           # Incorrect quiz answers
    last_encountered: str = ""             # Last encounter timestamp
    last_studied: str = ""                 # Last study session
    response_times: List[int] = field(default_factory=list)  # Response times in ms
    difficulty_adjustments: int = 0        # Times difficulty was adjusted
    
    def calculate_accuracy(self) -> float:
        """Calculate response accuracy percentage."""
        total = self.correct_responses + self.incorrect_responses
        return (self.correct_responses / total * 100) if total > 0 else 0.0
    
    def get_average_response_time(self) -> float:
        """Get average response time in milliseconds."""
        return sum(self.response_times) / len(self.response_times) if self.response_times else 0.0


@dataclass
class WordContext:
    """Context information for where/how word was encountered."""
    context_text: str                      # Surrounding text
    source_url: str = ""                   # Image URL or source
    search_query: str = ""                 # Original search query
    session_id: str = ""                   # Session where discovered
    extraction_method: str = ""            # How it was extracted
    confidence_score: float = 0.0          # AI confidence in translation
    validated: bool = False                # Human validation status
    notes: str = ""                        # User-added notes


@dataclass
class SpacedRepetitionData:
    """Spaced repetition algorithm data."""
    interval: int = 1                      # Days until next review
    repetitions: int = 0                   # Number of successful reviews
    easiness_factor: float = 2.5           # SM-2 algorithm factor
    next_review_date: str = ""             # Scheduled review date
    quality_history: List[int] = field(default_factory=list)  # Quality ratings (0-5)
    streak: int = 0                        # Current correct streak
    longest_streak: int = 0                # Best streak achieved


@dataclass
class EnhancedVocabularyEntry:
    """Enhanced vocabulary entry with comprehensive tracking."""
    # Core word data
    id: str                                # Unique identifier
    spanish: str                          # Spanish word/phrase
    english: str                          # English translation
    phonetic: str = ""                    # Phonetic pronunciation
    part_of_speech: str = ""              # noun, verb, adjective, etc.
    
    # Learning data
    difficulty: DifficultyLevel = DifficultyLevel.UNKNOWN
    status: WordStatus = WordStatus.NEW
    frequency_data: WordFrequency = field(default_factory=WordFrequency)
    spaced_repetition: SpacedRepetitionData = field(default_factory=SpacedRepetitionData)
    
    # Context and source
    contexts: List[WordContext] = field(default_factory=list)
    source: SourceType = SourceType.MANUAL_ENTRY
    
    # Categorization
    themes: Set[str] = field(default_factory=set)  # beach, food, travel, etc.
    custom_tags: Set[str] = field(default_factory=set)  # User-defined tags
    categories: Set[str] = field(default_factory=set)  # Grammar categories
    
    # Metadata
    created_date: str = ""
    last_modified: str = ""
    created_by: str = "system"            # system, user, import, etc.
    
    # Related words
    synonyms: Set[str] = field(default_factory=set)
    antonyms: Set[str] = field(default_factory=set)
    related_words: Set[str] = field(default_factory=set)
    
    # Media
    audio_url: str = ""                   # Pronunciation audio
    image_urls: List[str] = field(default_factory=list)  # Associated images
    example_sentences: List[str] = field(default_factory=list)
    
    # User preferences
    priority: int = 3                     # 1-5 priority for study
    personal_notes: str = ""              # User's personal notes
    memory_aids: List[str] = field(default_factory=list)  # Mnemonics, etc.
    
    def __post_init__(self):
        """Initialize computed fields after creation."""
        if not self.id:
            self.id = self._generate_id()
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        if not self.frequency_data.word:
            self.frequency_data.word = self.spanish
        if not self.spaced_repetition.next_review_date:
            self.spaced_repetition.next_review_date = datetime.now().isoformat()
        self.last_modified = datetime.now().isoformat()
    
    def _generate_id(self) -> str:
        """Generate unique ID based on Spanish word."""
        content = f"{self.spanish}_{self.english}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def add_context(self, context: WordContext):
        """Add new context for this word."""
        self.contexts.append(context)
        self.last_modified = datetime.now().isoformat()
    
    def update_frequency(self, encountered: bool = False, studied: bool = False, 
                        correct: bool = None, response_time: int = 0):
        """Update frequency tracking data."""
        now = datetime.now().isoformat()
        
        if encountered:
            self.frequency_data.encounters += 1
            self.frequency_data.last_encountered = now
            
        if studied:
            self.frequency_data.study_sessions += 1
            self.frequency_data.last_studied = now
            
        if correct is not None:
            if correct:
                self.frequency_data.correct_responses += 1
            else:
                self.frequency_data.incorrect_responses += 1
                
        if response_time > 0:
            self.frequency_data.response_times.append(response_time)
            # Keep only last 50 response times to prevent memory bloat
            if len(self.frequency_data.response_times) > 50:
                self.frequency_data.response_times.pop(0)
        
        self.last_modified = now
    
    def get_learning_score(self) -> float:
        """Calculate overall learning score (0-100)."""
        # Base score from accuracy
        accuracy = self.frequency_data.calculate_accuracy()
        
        # Adjust for frequency of study
        study_factor = min(self.frequency_data.study_sessions / 10.0, 1.0)
        
        # Adjust for consistency (spaced repetition streak)
        consistency_factor = min(self.spaced_repetition.streak / 5.0, 1.0)
        
        # Combine factors
        score = (accuracy * 0.5 + study_factor * 25 + consistency_factor * 25)
        return min(score, 100.0)
    
    def is_due_for_review(self) -> bool:
        """Check if word is due for spaced repetition review."""
        if self.status not in [WordStatus.LEARNING, WordStatus.REVIEWING]:
            return False
        
        next_review = datetime.fromisoformat(self.spaced_repetition.next_review_date)
        return datetime.now() >= next_review
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert sets to lists for JSON serialization
        data['themes'] = list(self.themes)
        data['custom_tags'] = list(self.custom_tags)
        data['categories'] = list(self.categories)
        data['synonyms'] = list(self.synonyms)
        data['antonyms'] = list(self.antonyms)
        data['related_words'] = list(self.related_words)
        # Convert enums to values
        data['difficulty'] = self.difficulty.value
        data['status'] = self.status.value
        data['source'] = self.source.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancedVocabularyEntry':
        """Create instance from dictionary."""
        # Convert lists back to sets
        if 'themes' in data:
            data['themes'] = set(data['themes'])
        if 'custom_tags' in data:
            data['custom_tags'] = set(data['custom_tags'])
        if 'categories' in data:
            data['categories'] = set(data['categories'])
        if 'synonyms' in data:
            data['synonyms'] = set(data['synonyms'])
        if 'antonyms' in data:
            data['antonyms'] = set(data['antonyms'])
        if 'related_words' in data:
            data['related_words'] = set(data['related_words'])
        
        # Convert enum values back to enums
        if 'difficulty' in data:
            data['difficulty'] = DifficultyLevel(data['difficulty'])
        if 'status' in data:
            data['status'] = WordStatus(data['status'])
        if 'source' in data:
            data['source'] = SourceType(data['source'])
        
        # Handle nested dataclasses
        if 'frequency_data' in data and isinstance(data['frequency_data'], dict):
            data['frequency_data'] = WordFrequency(**data['frequency_data'])
        if 'spaced_repetition' in data and isinstance(data['spaced_repetition'], dict):
            data['spaced_repetition'] = SpacedRepetitionData(**data['spaced_repetition'])
        if 'contexts' in data:
            data['contexts'] = [
                WordContext(**ctx) if isinstance(ctx, dict) else ctx 
                for ctx in data['contexts']
            ]
        
        return cls(**data)


class VocabularyAnalytics:
    """Analytics and reporting for vocabulary learning."""
    
    def __init__(self, vocabulary_entries: List[EnhancedVocabularyEntry]):
        self.entries = vocabulary_entries
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get comprehensive learning statistics."""
        if not self.entries:
            return {}
        
        # Basic counts
        total_words = len(self.entries)
        status_counts = Counter(entry.status.value for entry in self.entries)
        difficulty_counts = Counter(entry.difficulty.value for entry in self.entries)
        
        # Accuracy statistics
        accuracies = [entry.frequency_data.calculate_accuracy() for entry in self.entries]
        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
        
        # Learning scores
        scores = [entry.get_learning_score() for entry in self.entries]
        avg_learning_score = sum(scores) / len(scores) if scores else 0
        
        # Due for review
        due_count = sum(1 for entry in self.entries if entry.is_due_for_review())
        
        # Theme analysis
        theme_counts = Counter()
        for entry in self.entries:
            theme_counts.update(entry.themes)
        
        # Study frequency
        study_sessions = [entry.frequency_data.study_sessions for entry in self.entries]
        avg_study_sessions = sum(study_sessions) / len(study_sessions) if study_sessions else 0
        
        return {
            'total_words': total_words,
            'status_breakdown': dict(status_counts),
            'difficulty_breakdown': dict(difficulty_counts),
            'average_accuracy': round(avg_accuracy, 2),
            'average_learning_score': round(avg_learning_score, 2),
            'words_due_for_review': due_count,
            'top_themes': dict(theme_counts.most_common(10)),
            'average_study_sessions': round(avg_study_sessions, 2),
            'mastery_rate': round(status_counts.get('mastered', 0) / total_words * 100, 2)
        }
    
    def get_progress_over_time(self, days: int = 30) -> Dict[str, Any]:
        """Analyze learning progress over time."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Daily progress tracking
        daily_progress = defaultdict(lambda: {'words_added': 0, 'words_studied': 0, 'accuracy': []})
        
        for entry in self.entries:
            # Words added
            created = datetime.fromisoformat(entry.created_date)
            if start_date <= created <= end_date:
                date_key = created.date().isoformat()
                daily_progress[date_key]['words_added'] += 1
            
            # Study sessions
            if entry.frequency_data.last_studied:
                studied = datetime.fromisoformat(entry.frequency_data.last_studied)
                if start_date <= studied <= end_date:
                    date_key = studied.date().isoformat()
                    daily_progress[date_key]['words_studied'] += 1
                    daily_progress[date_key]['accuracy'].append(
                        entry.frequency_data.calculate_accuracy()
                    )
        
        # Process daily data
        processed_daily = {}
        for date, data in daily_progress.items():
            avg_accuracy = sum(data['accuracy']) / len(data['accuracy']) if data['accuracy'] else 0
            processed_daily[date] = {
                'words_added': data['words_added'],
                'words_studied': data['words_studied'],
                'average_accuracy': round(avg_accuracy, 2)
            }
        
        return {
            'period_days': days,
            'daily_breakdown': processed_daily,
            'total_new_words': sum(data['words_added'] for data in processed_daily.values()),
            'total_study_sessions': sum(data['words_studied'] for data in processed_daily.values())
        }
    
    def identify_challenging_words(self, threshold: float = 50.0) -> List[EnhancedVocabularyEntry]:
        """Identify words that are challenging to learn."""
        challenging = []
        
        for entry in self.entries:
            # Low accuracy or low learning score indicates challenge
            if (entry.frequency_data.calculate_accuracy() < threshold or
                entry.get_learning_score() < threshold):
                # But only if they've been studied enough to be meaningful
                if entry.frequency_data.study_sessions >= 3:
                    challenging.append(entry)
        
        # Sort by learning score (lowest first)
        challenging.sort(key=lambda x: x.get_learning_score())
        return challenging
    
    def recommend_study_words(self, count: int = 20) -> List[EnhancedVocabularyEntry]:
        """Recommend words for study based on various factors."""
        candidates = []
        
        for entry in self.entries:
            if entry.status in [WordStatus.NEW, WordStatus.LEARNING, WordStatus.REVIEWING]:
                # Calculate recommendation score
                score = 0
                
                # Prioritize due words
                if entry.is_due_for_review():
                    score += 50
                
                # Consider priority setting
                score += entry.priority * 10
                
                # Consider difficulty (appropriate challenge)
                if entry.difficulty in [DifficultyLevel.ELEMENTARY, DifficultyLevel.INTERMEDIATE]:
                    score += 20
                
                # Consider frequency of encounters (more encountered = more important)
                score += min(entry.frequency_data.encounters * 5, 25)
                
                # Penalize if studied too recently (unless due)
                if entry.frequency_data.last_studied:
                    last_study = datetime.fromisoformat(entry.frequency_data.last_studied)
                    hours_since = (datetime.now() - last_study).total_seconds() / 3600
                    if hours_since < 1:  # Studied in last hour
                        score -= 30
                
                candidates.append((entry, score))
        
        # Sort by recommendation score and return top candidates
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [entry for entry, score in candidates[:count]]


class EnhancedVocabularyManager:
    """Advanced vocabulary manager with comprehensive features."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Database setup
        self.db_path = data_dir / "enhanced_vocabulary.db"
        self.backup_dir = data_dir / "vocabulary_backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # In-memory cache for performance
        self.vocabulary_cache: Dict[str, EnhancedVocabularyEntry] = {}
        self.word_index: Dict[str, str] = {}  # spanish_word -> entry_id
        self.theme_index: Dict[str, Set[str]] = defaultdict(set)  # theme -> entry_ids
        self.tag_index: Dict[str, Set[str]] = defaultdict(set)  # tag -> entry_ids
        
        # Thread safety
        self.cache_lock = threading.RLock()
        
        # Settings
        self.auto_backup_enabled = True
        self.compression_enabled = True
        self.max_backups = 10
        
        self._initialize_database()
        self._load_cache()
    
    def _initialize_database(self):
        """Initialize the SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            # Main vocabulary table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vocabulary_entries (
                    id TEXT PRIMARY KEY,
                    spanish TEXT NOT NULL,
                    english TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    created_date TEXT NOT NULL,
                    last_modified TEXT NOT NULL,
                    status TEXT NOT NULL,
                    difficulty INTEGER NOT NULL,
                    priority INTEGER DEFAULT 3,
                    learning_score REAL DEFAULT 0.0,
                    next_review_date TEXT,
                    search_index TEXT  -- For full-text search
                )
            """)
            
            # Frequency tracking table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS word_frequencies (
                    word_id TEXT PRIMARY KEY,
                    encounters INTEGER DEFAULT 0,
                    study_sessions INTEGER DEFAULT 0,
                    correct_responses INTEGER DEFAULT 0,
                    incorrect_responses INTEGER DEFAULT 0,
                    last_encountered TEXT,
                    last_studied TEXT,
                    FOREIGN KEY (word_id) REFERENCES vocabulary_entries (id) ON DELETE CASCADE
                )
            """)
            
            # Themes and tags table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS word_themes (
                    word_id TEXT NOT NULL,
                    theme TEXT NOT NULL,
                    PRIMARY KEY (word_id, theme),
                    FOREIGN KEY (word_id) REFERENCES vocabulary_entries (id) ON DELETE CASCADE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS word_tags (
                    word_id TEXT NOT NULL,
                    tag TEXT NOT NULL,
                    PRIMARY KEY (word_id, tag),
                    FOREIGN KEY (word_id) REFERENCES vocabulary_entries (id) ON DELETE CASCADE
                )
            """)
            
            # User preferences table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    pref_key TEXT PRIMARY KEY,
                    pref_value TEXT NOT NULL,
                    last_updated TEXT NOT NULL
                )
            """)
            
            # Study sessions log
            conn.execute("""
                CREATE TABLE IF NOT EXISTS study_sessions (
                    id TEXT PRIMARY KEY,
                    session_date TEXT NOT NULL,
                    words_studied INTEGER DEFAULT 0,
                    correct_answers INTEGER DEFAULT 0,
                    session_duration_minutes INTEGER DEFAULT 0,
                    session_data TEXT
                )
            """)
            
            # Create indices for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_spanish_word ON vocabulary_entries(spanish)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON vocabulary_entries(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_difficulty ON vocabulary_entries(difficulty)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_next_review ON vocabulary_entries(next_review_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_learning_score ON vocabulary_entries(learning_score)")
            
            conn.commit()
    
    def _load_cache(self):
        """Load vocabulary entries into memory cache."""
        with self.cache_lock:
            self.vocabulary_cache.clear()
            self.word_index.clear()
            self.theme_index.clear()
            self.tag_index.clear()
            
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute("""
                    SELECT id, spanish, data_json FROM vocabulary_entries
                """).fetchall()
                
                for row in rows:
                    entry_id, spanish, data_json = row
                    try:
                        data = json.loads(data_json)
                        entry = EnhancedVocabularyEntry.from_dict(data)
                        
                        self.vocabulary_cache[entry_id] = entry
                        self.word_index[spanish.lower()] = entry_id
                        
                        # Update indices
                        for theme in entry.themes:
                            self.theme_index[theme].add(entry_id)
                        for tag in entry.custom_tags:
                            self.tag_index[tag].add(entry_id)
                            
                    except Exception as e:
                        print(f"Error loading entry {entry_id}: {e}")
    
    def add_vocabulary_entry(self, entry: EnhancedVocabularyEntry) -> bool:
        """Add a new vocabulary entry."""
        with self.cache_lock:
            # Check for duplicates
            if entry.spanish.lower() in self.word_index:
                return False
            
            # Ensure entry has proper ID
            if not entry.id:
                entry.id = entry._generate_id()
            
            # Update search index
            search_terms = [
                entry.spanish, entry.english, entry.phonetic,
                entry.part_of_speech, entry.personal_notes
            ]
            search_index = " ".join(filter(None, search_terms)).lower()
            
            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO vocabulary_entries 
                    (id, spanish, english, data_json, created_date, last_modified, 
                     status, difficulty, priority, learning_score, next_review_date, search_index)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.id, entry.spanish, entry.english, json.dumps(entry.to_dict()),
                    entry.created_date, entry.last_modified, entry.status.value,
                    entry.difficulty.value, entry.priority, entry.get_learning_score(),
                    entry.spaced_repetition.next_review_date, search_index
                ))
                
                # Save themes and tags
                for theme in entry.themes:
                    conn.execute(
                        "INSERT OR IGNORE INTO word_themes (word_id, theme) VALUES (?, ?)",
                        (entry.id, theme)
                    )
                
                for tag in entry.custom_tags:
                    conn.execute(
                        "INSERT OR IGNORE INTO word_tags (word_id, tag) VALUES (?, ?)",
                        (entry.id, tag)
                    )
                
                conn.commit()
            
            # Update cache
            self.vocabulary_cache[entry.id] = entry
            self.word_index[entry.spanish.lower()] = entry.id
            
            for theme in entry.themes:
                self.theme_index[theme].add(entry.id)
            for tag in entry.custom_tags:
                self.tag_index[tag].add(entry.id)
            
            # Auto-backup if enabled
            if self.auto_backup_enabled:
                self._create_backup()
            
            return True
    
    def get_entry(self, entry_id: str) -> Optional[EnhancedVocabularyEntry]:
        """Get vocabulary entry by ID."""
        with self.cache_lock:
            return self.vocabulary_cache.get(entry_id)
    
    def get_entry_by_word(self, spanish_word: str) -> Optional[EnhancedVocabularyEntry]:
        """Get vocabulary entry by Spanish word."""
        with self.cache_lock:
            entry_id = self.word_index.get(spanish_word.lower())
            if entry_id:
                return self.vocabulary_cache.get(entry_id)
            return None
    
    def update_entry(self, entry: EnhancedVocabularyEntry) -> bool:
        """Update an existing vocabulary entry."""
        with self.cache_lock:
            if entry.id not in self.vocabulary_cache:
                return False
            
            entry.last_modified = datetime.now().isoformat()
            
            # Update search index
            search_terms = [
                entry.spanish, entry.english, entry.phonetic,
                entry.part_of_speech, entry.personal_notes
            ]
            search_index = " ".join(filter(None, search_terms)).lower()
            
            # Update database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE vocabulary_entries SET
                        spanish = ?, english = ?, data_json = ?, last_modified = ?,
                        status = ?, difficulty = ?, priority = ?, learning_score = ?,
                        next_review_date = ?, search_index = ?
                    WHERE id = ?
                """, (
                    entry.spanish, entry.english, json.dumps(entry.to_dict()),
                    entry.last_modified, entry.status.value, entry.difficulty.value,
                    entry.priority, entry.get_learning_score(),
                    entry.spaced_repetition.next_review_date, search_index, entry.id
                ))
                
                # Update themes and tags
                conn.execute("DELETE FROM word_themes WHERE word_id = ?", (entry.id,))
                conn.execute("DELETE FROM word_tags WHERE word_id = ?", (entry.id,))
                
                for theme in entry.themes:
                    conn.execute(
                        "INSERT INTO word_themes (word_id, theme) VALUES (?, ?)",
                        (entry.id, theme)
                    )
                
                for tag in entry.custom_tags:
                    conn.execute(
                        "INSERT INTO word_tags (word_id, tag) VALUES (?, ?)",
                        (entry.id, tag)
                    )
                
                conn.commit()
            
            # Update cache
            self.vocabulary_cache[entry.id] = entry
            
            # Update indices
            self._rebuild_indices()
            
            return True
    
    def search_entries(self, query: str, filters: Dict[str, Any] = None) -> List[EnhancedVocabularyEntry]:
        """Search vocabulary entries with optional filters."""
        with self.cache_lock:
            results = []
            query_lower = query.lower()
            
            for entry in self.vocabulary_cache.values():
                # Text search
                if query_lower in entry.spanish.lower() or query_lower in entry.english.lower():
                    match = True
                else:
                    match = False
                
                # Apply filters
                if filters and match:
                    if 'status' in filters and entry.status != filters['status']:
                        match = False
                    if 'difficulty' in filters and entry.difficulty != filters['difficulty']:
                        match = False
                    if 'theme' in filters and filters['theme'] not in entry.themes:
                        match = False
                    if 'tag' in filters and filters['tag'] not in entry.custom_tags:
                        match = False
                    if 'min_score' in filters and entry.get_learning_score() < filters['min_score']:
                        match = False
                    if 'due_only' in filters and filters['due_only'] and not entry.is_due_for_review():
                        match = False
                
                if match:
                    results.append(entry)
            
            # Sort results by relevance/learning score
            results.sort(key=lambda x: x.get_learning_score(), reverse=True)
            return results
    
    def get_entries_by_theme(self, theme: str) -> List[EnhancedVocabularyEntry]:
        """Get all entries for a specific theme."""
        with self.cache_lock:
            entry_ids = self.theme_index.get(theme, set())
            return [self.vocabulary_cache[entry_id] for entry_id in entry_ids 
                   if entry_id in self.vocabulary_cache]
    
    def get_due_for_review(self, limit: int = 20) -> List[EnhancedVocabularyEntry]:
        """Get words due for spaced repetition review."""
        with self.cache_lock:
            due_words = [entry for entry in self.vocabulary_cache.values() 
                        if entry.is_due_for_review()]
            
            # Sort by review date (most overdue first)
            due_words.sort(key=lambda x: x.spaced_repetition.next_review_date)
            return due_words[:limit]
    
    def get_analytics(self) -> VocabularyAnalytics:
        """Get analytics object for vocabulary analysis."""
        with self.cache_lock:
            return VocabularyAnalytics(list(self.vocabulary_cache.values()))
    
    def export_vocabulary(self, format_type: str = 'json', 
                         filters: Dict[str, Any] = None) -> str:
        """Export vocabulary in various formats."""
        entries = list(self.vocabulary_cache.values())
        
        # Apply filters if provided
        if filters:
            filtered_entries = []
            for entry in entries:
                match = True
                if 'status' in filters and entry.status != filters['status']:
                    match = False
                if 'theme' in filters and filters['theme'] not in entry.themes:
                    match = False
                if match:
                    filtered_entries.append(entry)
            entries = filtered_entries
        
        if format_type == 'json':
            export_data = {
                'vocabulary': [entry.to_dict() for entry in entries],
                'export_date': datetime.now().isoformat(),
                'total_entries': len(entries),
                'format_version': '2.0'
            }
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        
        elif format_type == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Headers
            writer.writerow([
                'ID', 'Spanish', 'English', 'Phonetic', 'Part of Speech',
                'Difficulty', 'Status', 'Priority', 'Learning Score',
                'Themes', 'Tags', 'Created Date', 'Study Sessions',
                'Accuracy', 'Notes'
            ])
            
            # Data
            for entry in entries:
                writer.writerow([
                    entry.id,
                    entry.spanish,
                    entry.english,
                    entry.phonetic,
                    entry.part_of_speech,
                    entry.difficulty.name,
                    entry.status.value,
                    entry.priority,
                    round(entry.get_learning_score(), 2),
                    ';'.join(entry.themes),
                    ';'.join(entry.custom_tags),
                    entry.created_date,
                    entry.frequency_data.study_sessions,
                    round(entry.frequency_data.calculate_accuracy(), 2),
                    entry.personal_notes
                ])
            
            return output.getvalue()
        
        elif format_type == 'anki':
            # Anki deck format
            output = []
            for entry in entries:
                themes_str = ' '.join(f"#{theme}" for theme in entry.themes)
                front = f"{entry.spanish}"
                back = f"{entry.english}"
                
                if entry.phonetic:
                    back += f"<br><i>[{entry.phonetic}]</i>"
                
                if entry.personal_notes:
                    back += f"<br><br><small>{entry.personal_notes}</small>"
                
                if themes_str:
                    back += f"<br><br>{themes_str}"
                
                output.append(f"{front}\t{back}")
            
            return '\n'.join(output)
        
        return json.dumps([entry.to_dict() for entry in entries], indent=2)
    
    def import_vocabulary(self, data: str, format_type: str = 'json',
                         merge_strategy: str = 'skip_duplicates') -> Dict[str, int]:
        """Import vocabulary from various formats."""
        stats = {'imported': 0, 'skipped': 0, 'updated': 0, 'errors': 0}
        
        try:
            if format_type == 'json':
                import_data = json.loads(data)
                
                if isinstance(import_data, dict) and 'vocabulary' in import_data:
                    entries_data = import_data['vocabulary']
                else:
                    entries_data = import_data
                
                for entry_data in entries_data:
                    try:
                        entry = EnhancedVocabularyEntry.from_dict(entry_data)
                        
                        existing = self.get_entry_by_word(entry.spanish)
                        
                        if existing:
                            if merge_strategy == 'skip_duplicates':
                                stats['skipped'] += 1
                            elif merge_strategy == 'update_existing':
                                # Merge data
                                existing.english = entry.english
                                existing.themes.update(entry.themes)
                                existing.custom_tags.update(entry.custom_tags)
                                self.update_entry(existing)
                                stats['updated'] += 1
                        else:
                            # Generate new ID to avoid conflicts
                            entry.id = entry._generate_id()
                            entry.source = SourceType.IMPORT_CSV
                            
                            if self.add_vocabulary_entry(entry):
                                stats['imported'] += 1
                            else:
                                stats['errors'] += 1
                    
                    except Exception as e:
                        print(f"Error importing entry: {e}")
                        stats['errors'] += 1
            
            elif format_type == 'csv':
                import csv
                from io import StringIO
                
                reader = csv.DictReader(StringIO(data))
                
                for row in reader:
                    try:
                        entry = EnhancedVocabularyEntry(
                            spanish=row.get('Spanish', ''),
                            english=row.get('English', ''),
                            phonetic=row.get('Phonetic', ''),
                            part_of_speech=row.get('Part of Speech', ''),
                            source=SourceType.IMPORT_CSV
                        )
                        
                        # Parse difficulty
                        if 'Difficulty' in row:
                            try:
                                entry.difficulty = DifficultyLevel[row['Difficulty'].upper()]
                            except (KeyError, ValueError):
                                pass
                        
                        # Parse themes and tags
                        if 'Themes' in row and row['Themes']:
                            entry.themes = set(row['Themes'].split(';'))
                        
                        if 'Tags' in row and row['Tags']:
                            entry.custom_tags = set(row['Tags'].split(';'))
                        
                        if 'Priority' in row and row['Priority']:
                            try:
                                entry.priority = int(row['Priority'])
                            except ValueError:
                                pass
                        
                        if 'Notes' in row:
                            entry.personal_notes = row['Notes']
                        
                        # Check for existing
                        existing = self.get_entry_by_word(entry.spanish)
                        
                        if existing:
                            if merge_strategy == 'skip_duplicates':
                                stats['skipped'] += 1
                            elif merge_strategy == 'update_existing':
                                existing.english = entry.english
                                existing.themes.update(entry.themes)
                                self.update_entry(existing)
                                stats['updated'] += 1
                        else:
                            if self.add_vocabulary_entry(entry):
                                stats['imported'] += 1
                            else:
                                stats['errors'] += 1
                    
                    except Exception as e:
                        print(f"Error importing CSV row: {e}")
                        stats['errors'] += 1
        
        except Exception as e:
            print(f"Import error: {e}")
            stats['errors'] += 1
        
        return stats
    
    def _rebuild_indices(self):
        """Rebuild theme and tag indices."""
        self.theme_index.clear()
        self.tag_index.clear()
        
        for entry_id, entry in self.vocabulary_cache.items():
            for theme in entry.themes:
                self.theme_index[theme].add(entry_id)
            for tag in entry.custom_tags:
                self.tag_index[tag].add(entry_id)
    
    def _create_backup(self) -> Path:
        """Create a backup of the vocabulary database."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"vocabulary_backup_{timestamp}.json.gz"
        backup_path = self.backup_dir / backup_filename
        
        # Export all data
        export_data = self.export_vocabulary('json')
        
        if self.compression_enabled:
            with gzip.open(backup_path, 'wt', encoding='utf-8') as f:
                f.write(export_data)
        else:
            backup_path = backup_path.with_suffix('.json')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(export_data)
        
        # Cleanup old backups
        self._cleanup_old_backups()
        
        return backup_path
    
    def _cleanup_old_backups(self):
        """Remove old backup files."""
        backup_files = list(self.backup_dir.glob("vocabulary_backup_*.json*"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove excess backups
        for backup_file in backup_files[self.max_backups:]:
            backup_file.unlink()
    
    def get_vocabulary_count(self) -> int:
        """Get total vocabulary count."""
        with self.cache_lock:
            return len(self.vocabulary_cache)
    
    def is_duplicate(self, spanish_word: str) -> bool:
        """Check if Spanish word already exists."""
        with self.cache_lock:
            return spanish_word.lower() in self.word_index
    
    def get_all_themes(self) -> List[str]:
        """Get all unique themes."""
        with self.cache_lock:
            return sorted(list(self.theme_index.keys()))
    
    def get_all_tags(self) -> List[str]:
        """Get all unique custom tags."""
        with self.cache_lock:
            return sorted(list(self.tag_index.keys()))
    
    def record_study_session(self, session_data: Dict[str, Any]):
        """Record a study session for analytics."""
        session_id = hashlib.md5(
            f"{datetime.now().isoformat()}_{session_data}".encode()
        ).hexdigest()[:12]
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO study_sessions 
                (id, session_date, words_studied, correct_answers, 
                 session_duration_minutes, session_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                datetime.now().isoformat(),
                session_data.get('words_studied', 0),
                session_data.get('correct_answers', 0),
                session_data.get('duration_minutes', 0),
                json.dumps(session_data)
            ))
            conn.commit()