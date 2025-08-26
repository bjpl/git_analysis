"""
Enhanced session tracking for quiz attempts, learning analytics, and image search history.
Tracks quiz performance, vocabulary studied, accuracy metrics, and image search variety.
Implements image rotation logic to ensure different images across sessions.
"""

import csv
import json
import os
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class QuizAttempt:
    """Individual quiz attempt record."""
    
    def __init__(self, word: str, correct: bool, response_time: float = 0.0):
        self.timestamp = datetime.now()
        self.word = word
        self.correct = correct
        self.response_time = response_time
    
    def to_csv_row(self) -> List[str]:
        """Convert to CSV row format."""
        return [
            self.timestamp.isoformat(),
            self.word,
            str(self.correct).lower(),
            str(self.response_time)
        ]
    
    @classmethod
    def from_csv_row(cls, row: List[str]) -> 'QuizAttempt':
        """Create from CSV row."""
        attempt = cls(row[1], row[2].lower() == 'true')
        attempt.timestamp = datetime.fromisoformat(row[0])
        if len(row) > 3:
            try:
                attempt.response_time = float(row[3])
            except ValueError:
                attempt.response_time = 0.0
        return attempt


class ImageSearchRecord:
    """Record of an image search and displayed images."""
    
    def __init__(self, query: str, page: int = 1, image_id: str = None, 
                 image_url: str = None, timestamp: datetime = None):
        self.query = query.lower().strip()
        self.page = page
        self.image_id = image_id
        self.image_url = image_url
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'query': self.query,
            'page': self.page,
            'image_id': self.image_id,
            'image_url': self.image_url,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ImageSearchRecord':
        """Create from dictionary."""
        timestamp = datetime.fromisoformat(data['timestamp']) if data.get('timestamp') else datetime.now()
        return cls(
            query=data['query'],
            page=data.get('page', 1),
            image_id=data.get('image_id'),
            image_url=data.get('image_url'),
            timestamp=timestamp
        )


class SearchVarietyManager:
    """Manages image search variety to prevent repetitive results."""
    
    def __init__(self, max_history: int = 50, session_memory_hours: int = 24):
        self.max_history = max_history
        self.session_memory_hours = session_memory_hours
        self.search_history: List[ImageSearchRecord] = []
        self.query_page_map: Dict[str, int] = {}  # Track current page per query
        self.shown_images: Dict[str, Set[str]] = {}  # Track shown image IDs per query
        self.time_seed = int(time.time())
        
        # Clean up old records on initialization
        self._cleanup_old_records()
    
    def _cleanup_old_records(self):
        """Remove records older than session_memory_hours."""
        cutoff_time = datetime.now() - timedelta(hours=self.session_memory_hours)
        self.search_history = [record for record in self.search_history 
                              if record.timestamp > cutoff_time]
        
        # Update page map and shown images based on remaining records
        self.query_page_map.clear()
        self.shown_images.clear()
        
        for record in self.search_history:
            query = record.query
            if query not in self.query_page_map:
                self.query_page_map[query] = 1
                self.shown_images[query] = set()
            
            if record.page > self.query_page_map[query]:
                self.query_page_map[query] = record.page
            
            if record.image_id:
                self.shown_images[query].add(record.image_id)
    
    def get_search_parameters(self, query: str, force_new: bool = False) -> Tuple[int, int]:
        """Get page number and random offset for search to ensure variety.
        
        Returns:
            Tuple[int, int]: (page_number, random_offset)
        """
        query = query.lower().strip()
        
        # Clean up old records
        self._cleanup_old_records()
        
        if force_new or query not in self.query_page_map:
            # For new queries or forced refresh, start with a random page
            base_seed = hash(query + str(self.time_seed)) % 1000
            page = max(1, (base_seed % 5) + 1)  # Random page 1-5
            random_offset = base_seed % 10  # Random offset 0-9
            self.query_page_map[query] = page
            self.shown_images[query] = set()
        else:
            # For repeated queries, use different strategy
            last_page = self.query_page_map[query]
            shown_count = len(self.shown_images.get(query, set()))
            
            if shown_count < 10:  # Less than one page shown
                # Stay on current page but use different offset
                page = last_page
                random_offset = (shown_count + hash(str(time.time())) % 10) % 10
            else:
                # Move to next page
                page = last_page + 1
                random_offset = hash(str(time.time())) % 10
                self.query_page_map[query] = page
        
        return page, random_offset
    
    def record_shown_image(self, query: str, image_id: str, image_url: str, page: int):
        """Record that an image was shown for a query."""
        query = query.lower().strip()
        
        # Add to shown images set
        if query not in self.shown_images:
            self.shown_images[query] = set()
        self.shown_images[query].add(image_id)
        
        # Create search record
        record = ImageSearchRecord(
            query=query,
            page=page,
            image_id=image_id,
            image_url=image_url
        )
        
        # Add to history and maintain size limit
        self.search_history.append(record)
        if len(self.search_history) > self.max_history:
            self.search_history = self.search_history[-self.max_history:]
    
    def has_seen_image(self, query: str, image_id: str) -> bool:
        """Check if an image has been shown for this query recently."""
        query = query.lower().strip()
        return image_id in self.shown_images.get(query, set())
    
    def get_query_stats(self, query: str) -> Dict:
        """Get statistics for a specific query."""
        query = query.lower().strip()
        shown_count = len(self.shown_images.get(query, set()))
        current_page = self.query_page_map.get(query, 1)
        
        recent_searches = sum(1 for record in self.search_history 
                             if record.query == query and 
                             record.timestamp > datetime.now() - timedelta(hours=1))
        
        return {
            'query': query,
            'images_shown': shown_count,
            'current_page': current_page,
            'recent_searches': recent_searches,
            'last_search': max([record.timestamp for record in self.search_history 
                               if record.query == query], default=None)
        }
    
    def reset_query_history(self, query: str):
        """Reset history for a specific query."""
        query = query.lower().strip()
        if query in self.query_page_map:
            del self.query_page_map[query]
        if query in self.shown_images:
            del self.shown_images[query]
        
        # Remove records for this query
        self.search_history = [record for record in self.search_history 
                              if record.query != query]
    
    def shuffle_search(self, query: str) -> Tuple[int, int]:
        """Get completely randomized search parameters for shuffling."""
        query = query.lower().strip()
        
        # Generate new random parameters based on current time
        time_seed = int(time.time() * 1000) % 10000  # More granular seed
        page = max(1, (time_seed % 10) + 1)  # Random page 1-10
        random_offset = time_seed % 20  # Random offset 0-19
        
        # Update tracking
        self.query_page_map[query] = page
        if query not in self.shown_images:
            self.shown_images[query] = set()
        
        return page, random_offset
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'search_history': [record.to_dict() for record in self.search_history],
            'query_page_map': self.query_page_map,
            'shown_images': {k: list(v) for k, v in self.shown_images.items()},
            'time_seed': self.time_seed,
            'last_cleanup': datetime.now().isoformat()
        }
    
    def from_dict(self, data: Dict):
        """Load from dictionary."""
        self.search_history = [ImageSearchRecord.from_dict(record) 
                              for record in data.get('search_history', [])]
        self.query_page_map = data.get('query_page_map', {})
        self.shown_images = {k: set(v) for k, v in data.get('shown_images', {}).items()}
        self.time_seed = data.get('time_seed', int(time.time()))
        
        # Clean up old records after loading
        self._cleanup_old_records()


class SessionStats:
    """Enhanced session statistics container with image search tracking."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.words_studied = set()
        self.quiz_attempts: List[QuizAttempt] = []
        self.session_duration = 0.0
        self.images_viewed = 0
        self.unique_searches = set()
        self.search_variety_manager = SearchVarietyManager()
    
    def add_word_studied(self, word: str):
        """Add a word to the studied set."""
        self.words_studied.add(word)
    
    def add_image_viewed(self, query: str, image_id: str = None, image_url: str = None):
        """Track an image view for analytics."""
        self.images_viewed += 1
        if query:
            self.unique_searches.add(query.lower().strip())
            if image_id and image_url:
                # Get current page from variety manager
                current_page = self.search_variety_manager.query_page_map.get(query.lower().strip(), 1)
                self.search_variety_manager.record_shown_image(query, image_id, image_url, current_page)
    
    def add_quiz_attempt(self, attempt: QuizAttempt):
        """Add a quiz attempt."""
        self.quiz_attempts.append(attempt)
        self.add_word_studied(attempt.word)
    
    def calculate_accuracy(self) -> float:
        """Calculate accuracy percentage."""
        if not self.quiz_attempts:
            return 0.0
        
        correct_count = sum(1 for attempt in self.quiz_attempts if attempt.correct)
        return (correct_count / len(self.quiz_attempts)) * 100
    
    def get_total_attempts(self) -> int:
        """Get total number of quiz attempts."""
        return len(self.quiz_attempts)
    
    def get_words_studied_count(self) -> int:
        """Get number of unique words studied."""
        return len(self.words_studied)
    
    def calculate_session_duration(self) -> float:
        """Calculate session duration in minutes."""
        if self.quiz_attempts:
            last_attempt = max(self.quiz_attempts, key=lambda x: x.timestamp)
            duration = (last_attempt.timestamp - self.start_time).total_seconds()
            return duration / 60.0
        return 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for CSV export."""
        return {
            'session_date': self.start_time.strftime('%Y-%m-%d'),
            'session_time': self.start_time.strftime('%H:%M:%S'),
            'words_studied': self.get_words_studied_count(),
            'total_attempts': self.get_total_attempts(),
            'correct_attempts': sum(1 for a in self.quiz_attempts if a.correct),
            'accuracy_percentage': round(self.calculate_accuracy(), 2),
            'session_duration_minutes': round(self.calculate_session_duration(), 2),
            'images_viewed': self.images_viewed,
            'unique_searches': len(self.unique_searches)
        }


class EnhancedSessionTracker:
    """Enhanced session tracking class with CSV persistence and image search variety management."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
        
        # File paths
        self.attempts_file = self.data_dir / "quiz_attempts.csv"
        self.sessions_file = self.data_dir / "session_stats.csv"
        self.image_history_file = self.data_dir / "image_search_history.json"
        
        # Current session
        self.current_session = SessionStats()
        
        # Load image search variety manager data
        self._load_image_history()
        
        # Initialize files
        self._initialize_files()
    
    def _load_image_history(self):
        """Load image search history from JSON file."""
        if self.image_history_file.exists():
            try:
                with open(self.image_history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_session.search_variety_manager.from_dict(data)
            except Exception as e:
                print(f"Warning: Could not load image history: {e}")
                # Start fresh if file is corrupted
                self.current_session.search_variety_manager = SearchVarietyManager()
    
    def _save_image_history(self):
        """Save image search history to JSON file."""
        try:
            data = self.current_session.search_variety_manager.to_dict()
            with open(self.image_history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save image history: {e}")
    
    def _initialize_files(self):
        """Initialize CSV files with headers if they don't exist."""
        # Quiz attempts file
        if not self.attempts_file.exists():
            with open(self.attempts_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'word', 'correct', 'response_time'])
        
        # Session stats file
        if not self.sessions_file.exists():
            with open(self.sessions_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'session_date', 'session_time', 'words_studied', 
                    'total_attempts', 'correct_attempts', 'accuracy_percentage',
                    'session_duration_minutes', 'images_viewed', 'unique_searches'
                ])
    
    def get_search_parameters(self, query: str, force_new: bool = False) -> Tuple[int, int]:
        """Get optimized search parameters for image variety."""
        return self.current_session.search_variety_manager.get_search_parameters(query, force_new)
    
    def shuffle_search(self, query: str) -> Tuple[int, int]:
        """Get randomized search parameters for shuffling."""
        return self.current_session.search_variety_manager.shuffle_search(query)
    
    def record_image_shown(self, query: str, image_id: str, image_url: str, page: int = 1):
        """Record that an image was displayed."""
        self.current_session.add_image_viewed(query, image_id, image_url)
        self.current_session.search_variety_manager.record_shown_image(query, image_id, image_url, page)
        self._save_image_history()
    
    def has_seen_image(self, query: str, image_id: str) -> bool:
        """Check if image has been shown recently."""
        return self.current_session.search_variety_manager.has_seen_image(query, image_id)
    
    def get_query_stats(self, query: str) -> Dict:
        """Get statistics for a query."""
        return self.current_session.search_variety_manager.get_query_stats(query)
    
    def reset_query_history(self, query: str):
        """Reset search history for a query."""
        self.current_session.search_variety_manager.reset_query_history(query)
        self._save_image_history()
    
    def log_quiz_attempt(self, word: str, correct: bool, response_time: float = 0.0):
        """Log a quiz attempt."""
        attempt = QuizAttempt(word, correct, response_time)
        self.current_session.add_quiz_attempt(attempt)
        
        # Save to CSV
        try:
            with open(self.attempts_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(attempt.to_csv_row())
        except Exception as e:
            print(f"Error logging quiz attempt: {e}")
    
    def add_studied_word(self, word: str):
        """Add a word to the current session's studied words."""
        self.current_session.add_word_studied(word)
    
    def get_current_accuracy(self) -> float:
        """Get current session accuracy percentage."""
        return self.current_session.calculate_accuracy()
    
    def get_session_stats(self) -> Dict:
        """Get current session statistics."""
        stats = self.current_session.to_dict()
        stats['current_session'] = True
        return stats
    
    def save_session(self):
        """Save current session stats to CSV."""
        if (self.current_session.get_total_attempts() == 0 and 
            self.current_session.images_viewed == 0):
            return  # Don't save empty sessions
        
        try:
            session_data = self.current_session.to_dict()
            
            with open(self.sessions_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    session_data['session_date'],
                    session_data['session_time'],
                    session_data['words_studied'],
                    session_data['total_attempts'],
                    session_data['correct_attempts'],
                    session_data['accuracy_percentage'],
                    session_data['session_duration_minutes'],
                    session_data['images_viewed'],
                    session_data['unique_searches']
                ])
            
            print(f"Session saved: {session_data['total_attempts']} attempts, "
                  f"{session_data['accuracy_percentage']}% accuracy, "
                  f"{session_data['images_viewed']} images viewed")
            
        except Exception as e:
            print(f"Error saving session: {e}")
    
    def load_previous_session_stats(self, days_back: int = 7) -> List[Dict]:
        """Load previous session statistics."""
        stats = []
        
        if not self.sessions_file.exists():
            return stats
        
        try:
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Get cutoff date
                cutoff_date = datetime.now().date()
                cutoff_date -= timedelta(days=days_back)
                
                for row in reader:
                    try:
                        session_date = datetime.strptime(row['session_date'], '%Y-%m-%d').date()
                        if session_date >= cutoff_date:
                            # Convert numeric fields
                            row['words_studied'] = int(row['words_studied'])
                            row['total_attempts'] = int(row['total_attempts'])
                            row['correct_attempts'] = int(row['correct_attempts'])
                            row['accuracy_percentage'] = float(row['accuracy_percentage'])
                            row['session_duration_minutes'] = float(row['session_duration_minutes'])
                            
                            # Handle new fields that might not exist in older records
                            row['images_viewed'] = int(row.get('images_viewed', 0))
                            row['unique_searches'] = int(row.get('unique_searches', 0))
                            
                            stats.append(row)
                    except (ValueError, KeyError):
                        continue  # Skip invalid rows
                        
        except Exception as e:
            print(f"Error loading previous sessions: {e}")
        
        return stats
    
    def get_overall_stats(self) -> Dict:
        """Calculate overall statistics from all sessions."""
        previous_stats = self.load_previous_session_stats(days_back=30)  # Last 30 days
        
        if not previous_stats:
            return {
                'total_sessions': 0,
                'total_words_studied': 0,
                'total_attempts': 0,
                'overall_accuracy': 0.0,
                'average_session_duration': 0.0,
                'total_images_viewed': 0,
                'total_unique_searches': 0
            }
        
        total_sessions = len(previous_stats)
        total_words = sum(session['words_studied'] for session in previous_stats)
        total_attempts = sum(session['total_attempts'] for session in previous_stats)
        total_correct = sum(session['correct_attempts'] for session in previous_stats)
        total_duration = sum(session['session_duration_minutes'] for session in previous_stats)
        total_images = sum(session['images_viewed'] for session in previous_stats)
        total_searches = sum(session['unique_searches'] for session in previous_stats)
        
        overall_accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0.0
        avg_duration = total_duration / total_sessions if total_sessions > 0 else 0.0
        
        return {
            'total_sessions': total_sessions,
            'total_words_studied': total_words,
            'total_attempts': total_attempts,
            'overall_accuracy': round(overall_accuracy, 2),
            'average_session_duration': round(avg_duration, 2),
            'total_images_viewed': total_images,
            'total_unique_searches': total_searches
        }
    
    def reset_session(self):
        """Reset current session (start new session)."""
        if (self.current_session.get_total_attempts() > 0 or 
            self.current_session.images_viewed > 0):
            self.save_session()
        
        # Preserve search variety manager across sessions
        variety_manager = self.current_session.search_variety_manager
        self.current_session = SessionStats()
        self.current_session.search_variety_manager = variety_manager
    
    def export_attempts_for_analysis(self, output_file: Optional[Path] = None) -> Path:
        """Export all quiz attempts for external analysis."""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.data_dir / f"quiz_attempts_export_{timestamp}.csv"
        
        try:
            # Copy the attempts file with additional calculated fields
            with open(self.attempts_file, 'r', encoding='utf-8') as input_f:
                with open(output_file, 'w', newline='', encoding='utf-8') as output_f:
                    reader = csv.reader(input_f)
                    writer = csv.writer(output_f)
                    
                    # Write enhanced header
                    header = next(reader)
                    header.extend(['date', 'time', 'day_of_week'])
                    writer.writerow(header)
                    
                    # Write data with additional fields
                    for row in reader:
                        if len(row) >= 4:
                            try:
                                timestamp = datetime.fromisoformat(row[0])
                                row.extend([
                                    timestamp.strftime('%Y-%m-%d'),
                                    timestamp.strftime('%H:%M:%S'),
                                    timestamp.strftime('%A')
                                ])
                            except ValueError:
                                # Handle invalid timestamps
                                row.extend(['', '', ''])
                            writer.writerow(row)
            
            return output_file
            
        except Exception as e:
            print(f"Error exporting attempts: {e}")
            return self.attempts_file  # Return original file as fallback


# Convenience functions for easy integration
def create_enhanced_session_tracker(data_dir: Path = None) -> EnhancedSessionTracker:
    """Create an enhanced session tracker with default data directory."""
    if data_dir is None:
        data_dir = Path('./data/sessions')
    return EnhancedSessionTracker(data_dir)


def get_image_search_parameters(tracker: EnhancedSessionTracker, query: str, 
                               shuffle: bool = False) -> Dict[str, any]:
    """Get search parameters for image API call."""
    if shuffle:
        page, offset = tracker.shuffle_search(query)
    else:
        page, offset = tracker.get_search_parameters(query)
    
    return {
        'page': page,
        'per_page': 10,
        'order_by': 'relevant',  # Can randomize this too
        'orientation': 'all',
        'content_filter': 'high',
        'query_offset': offset  # Custom parameter for skipping results
    }