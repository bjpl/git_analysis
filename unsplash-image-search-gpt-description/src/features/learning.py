"""Spaced repetition learning system with flashcards and progress tracking."""

import json
import sqlite3
import random
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum


class DifficultyLevel(Enum):
    """Difficulty levels for learning items."""
    VERY_EASY = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    VERY_HARD = 5


class ReviewResult(Enum):
    """Results of review sessions."""
    AGAIN = "again"  # < 60% correct
    HARD = "hard"    # 60-79% correct
    GOOD = "good"    # 80-95% correct
    EASY = "easy"    # > 95% correct


class StudyMode(Enum):
    """Different study modes available."""
    FLASHCARDS = "flashcards"
    MULTIPLE_CHOICE = "multiple_choice"
    TYPING = "typing"
    LISTENING = "listening"
    MIXED = "mixed"


@dataclass
class LearningCard:
    """Individual learning card with spaced repetition data."""
    id: str
    front: str
    back: str
    category: str
    difficulty: DifficultyLevel
    interval: int  # Days until next review
    repetitions: int
    easiness_factor: float  # SM-2 algorithm factor
    last_reviewed: str
    next_review: str
    success_rate: float
    review_count: int
    creation_date: str
    tags: List[str] = None
    notes: str = ""
    audio_front: Optional[str] = None
    audio_back: Optional[str] = None
    image_url: Optional[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class StudySession:
    """Study session data."""
    id: str
    start_time: str
    end_time: Optional[str]
    cards_studied: int
    correct_answers: int
    study_mode: StudyMode
    duration_minutes: int
    categories: List[str]
    performance_data: Dict[str, Any]


@dataclass
class Achievement:
    """Achievement/badge for motivation."""
    id: str
    name: str
    description: str
    icon: str
    earned_date: str
    points: int
    category: str


class LearningSystem:
    """Spaced repetition learning system with achievements and progress tracking."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.db_path = data_dir / "learning.db"
        
        # SM-2 algorithm constants
        self.INITIAL_INTERVAL = 1
        self.INITIAL_REPETITIONS = 0
        self.INITIAL_EASINESS = 2.5
        self.MIN_EASINESS = 1.3
        
        self._init_database()
        self._init_achievements()
    
    def _init_database(self):
        """Initialize the learning database."""
        with sqlite3.connect(self.db_path) as conn:
            # Learning cards table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_cards (
                    id TEXT PRIMARY KEY,
                    front TEXT NOT NULL,
                    back TEXT NOT NULL,
                    category TEXT NOT NULL,
                    difficulty INTEGER NOT NULL,
                    interval INTEGER NOT NULL,
                    repetitions INTEGER NOT NULL,
                    easiness_factor REAL NOT NULL,
                    last_reviewed TEXT,
                    next_review TEXT NOT NULL,
                    success_rate REAL DEFAULT 0.0,
                    review_count INTEGER DEFAULT 0,
                    creation_date TEXT NOT NULL,
                    tags TEXT,
                    notes TEXT,
                    audio_front TEXT,
                    audio_back TEXT,
                    image_url TEXT
                )
            """)
            
            # Study sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS study_sessions (
                    id TEXT PRIMARY KEY,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    cards_studied INTEGER DEFAULT 0,
                    correct_answers INTEGER DEFAULT 0,
                    study_mode TEXT NOT NULL,
                    duration_minutes INTEGER DEFAULT 0,
                    categories TEXT,
                    performance_data TEXT
                )
            """)
            
            # Review history table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS review_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    review_date TEXT NOT NULL,
                    result TEXT NOT NULL,
                    response_time_ms INTEGER,
                    previous_interval INTEGER,
                    new_interval INTEGER,
                    FOREIGN KEY (card_id) REFERENCES learning_cards (id) ON DELETE CASCADE,
                    FOREIGN KEY (session_id) REFERENCES study_sessions (id) ON DELETE CASCADE
                )
            """)
            
            # Achievements table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS achievements (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    icon TEXT NOT NULL,
                    earned_date TEXT,
                    points INTEGER NOT NULL,
                    category TEXT NOT NULL
                )
            """)
            
            # User statistics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_stats (
                    stat_name TEXT PRIMARY KEY,
                    stat_value TEXT NOT NULL,
                    last_updated TEXT NOT NULL
                )
            """)
            
            conn.commit()
    
    def _init_achievements(self):
        """Initialize achievement definitions."""
        achievements = [
            {
                'id': 'first_card',
                'name': 'First Steps',
                'description': 'Create your first learning card',
                'icon': '🎯',
                'points': 10,
                'category': 'milestone'
            },
            {
                'id': 'daily_streak_7',
                'name': 'Week Warrior',
                'description': 'Study for 7 consecutive days',
                'icon': '🔥',
                'points': 50,
                'category': 'streak'
            },
            {
                'id': 'daily_streak_30',
                'name': 'Monthly Master',
                'description': 'Study for 30 consecutive days',
                'icon': '🏆',
                'points': 200,
                'category': 'streak'
            },
            {
                'id': 'perfect_session',
                'name': 'Perfectionist',
                'description': 'Complete a session with 100% accuracy',
                'icon': '💯',
                'points': 25,
                'category': 'performance'
            },
            {
                'id': 'speed_demon',
                'name': 'Speed Demon',
                'description': 'Answer 50 cards in under 5 minutes',
                'icon': '⚡',
                'points': 30,
                'category': 'performance'
            },
            {
                'id': 'vocabulary_100',
                'name': 'Vocabulary Scholar',
                'description': 'Learn 100 vocabulary words',
                'icon': '📚',
                'points': 100,
                'category': 'milestone'
            },
            {
                'id': 'review_master',
                'name': 'Review Master',
                'description': 'Complete 1000 reviews',
                'icon': '🎓',
                'points': 150,
                'category': 'milestone'
            }
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            for achievement in achievements:
                conn.execute("""
                    INSERT OR IGNORE INTO achievements 
                    (id, name, description, icon, points, category)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    achievement['id'],
                    achievement['name'],
                    achievement['description'],
                    achievement['icon'],
                    achievement['points'],
                    achievement['category']
                ))
    
    def create_card(self, front: str, back: str, category: str,
                   difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
                   tags: List[str] = None, notes: str = "",
                   image_url: Optional[str] = None) -> str:
        """Create a new learning card."""
        import uuid
        card_id = str(uuid.uuid4())
        now = datetime.now()
        
        card = LearningCard(
            id=card_id,
            front=front,
            back=back,
            category=category,
            difficulty=difficulty,
            interval=self.INITIAL_INTERVAL,
            repetitions=self.INITIAL_REPETITIONS,
            easiness_factor=self.INITIAL_EASINESS,
            last_reviewed="",
            next_review=now.isoformat(),
            success_rate=0.0,
            review_count=0,
            creation_date=now.isoformat(),
            tags=tags or [],
            notes=notes,
            image_url=image_url
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO learning_cards (
                    id, front, back, category, difficulty, interval, repetitions,
                    easiness_factor, last_reviewed, next_review, success_rate,
                    review_count, creation_date, tags, notes, image_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                card.id, card.front, card.back, card.category, card.difficulty.value,
                card.interval, card.repetitions, card.easiness_factor,
                card.last_reviewed, card.next_review, card.success_rate,
                card.review_count, card.creation_date, json.dumps(card.tags),
                card.notes, card.image_url
            ))
        
        # Check for first card achievement
        self._check_achievement('first_card')
        
        return card_id
    
    def get_due_cards(self, limit: int = 20, category: Optional[str] = None) -> List[LearningCard]:
        """Get cards that are due for review."""
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            if category:
                rows = conn.execute("""
                    SELECT * FROM learning_cards 
                    WHERE next_review <= ? AND category = ?
                    ORDER BY next_review ASC
                    LIMIT ?
                """, (now, category, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM learning_cards 
                    WHERE next_review <= ?
                    ORDER BY next_review ASC
                    LIMIT ?
                """, (now, limit)).fetchall()
            
            return [self._row_to_card(row) for row in rows]
    
    def get_new_cards(self, limit: int = 10, category: Optional[str] = None) -> List[LearningCard]:
        """Get new cards that haven't been reviewed yet."""
        with sqlite3.connect(self.db_path) as conn:
            if category:
                rows = conn.execute("""
                    SELECT * FROM learning_cards 
                    WHERE repetitions = 0 AND category = ?
                    ORDER BY creation_date ASC
                    LIMIT ?
                """, (category, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM learning_cards 
                    WHERE repetitions = 0
                    ORDER BY creation_date ASC
                    LIMIT ?
                """, (limit,)).fetchall()
            
            return [self._row_to_card(row) for row in rows]
    
    def start_study_session(self, study_mode: StudyMode, 
                           categories: List[str] = None) -> str:
        """Start a new study session."""
        import uuid
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO study_sessions 
                (id, start_time, study_mode, categories, performance_data)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id, now, study_mode.value, 
                json.dumps(categories or []), json.dumps({})
            ))
        
        return session_id
    
    def review_card(self, card_id: str, session_id: str, 
                   result: ReviewResult, response_time_ms: int = 0) -> LearningCard:
        """Review a card and update its scheduling using SM-2 algorithm."""
        card = self.get_card(card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")
        
        now = datetime.now()
        previous_interval = card.interval
        
        # Update success rate
        correct = result in [ReviewResult.GOOD, ReviewResult.EASY]
        card.review_count += 1
        card.success_rate = (
            (card.success_rate * (card.review_count - 1) + (1 if correct else 0)) 
            / card.review_count
        )
        
        # SM-2 Algorithm
        if result == ReviewResult.AGAIN:
            card.repetitions = 0
            card.interval = 1
        else:
            if card.repetitions == 0:
                card.interval = 1
            elif card.repetitions == 1:
                card.interval = 6
            else:
                card.interval = math.ceil(card.interval * card.easiness_factor)
            
            card.repetitions += 1
            
            # Update easiness factor
            quality = {
                ReviewResult.EASY: 5,
                ReviewResult.GOOD: 4,
                ReviewResult.HARD: 3,
                ReviewResult.AGAIN: 0
            }[result]
            
            card.easiness_factor = card.easiness_factor + (
                0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
            )
            
            if card.easiness_factor < self.MIN_EASINESS:
                card.easiness_factor = self.MIN_EASINESS
        
        # Set next review date
        card.next_review = (now + timedelta(days=card.interval)).isoformat()
        card.last_reviewed = now.isoformat()
        
        # Update database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE learning_cards SET
                    interval = ?, repetitions = ?, easiness_factor = ?,
                    last_reviewed = ?, next_review = ?, success_rate = ?,
                    review_count = ?
                WHERE id = ?
            """, (
                card.interval, card.repetitions, card.easiness_factor,
                card.last_reviewed, card.next_review, card.success_rate,
                card.review_count, card.id
            ))
            
            # Log review history
            conn.execute("""
                INSERT INTO review_history 
                (card_id, session_id, review_date, result, response_time_ms,
                 previous_interval, new_interval)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                card.id, session_id, now.isoformat(), result.value,
                response_time_ms, previous_interval, card.interval
            ))
        
        # Check for achievements
        if correct:
            self._check_performance_achievements(session_id)
        
        return card
    
    def end_study_session(self, session_id: str) -> StudySession:
        """End a study session and calculate statistics."""
        now = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            # Get session data
            session_row = conn.execute("""
                SELECT start_time, study_mode, categories FROM study_sessions
                WHERE id = ?
            """, (session_id,)).fetchone()
            
            if not session_row:
                raise ValueError(f"Session {session_id} not found")
            
            start_time = datetime.fromisoformat(session_row[0])
            duration_minutes = int((now - start_time).total_seconds() / 60)
            
            # Get review statistics
            stats = conn.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN result IN ('good', 'easy') THEN 1 ELSE 0 END) as correct
                FROM review_history WHERE session_id = ?
            """, (session_id,)).fetchone()
            
            cards_studied = stats[0] or 0
            correct_answers = stats[1] or 0
            
            # Calculate performance data
            performance_data = {
                'accuracy': correct_answers / cards_studied if cards_studied > 0 else 0,
                'cards_per_minute': cards_studied / duration_minutes if duration_minutes > 0 else 0,
                'streak': self._calculate_current_streak()
            }
            
            # Update session
            conn.execute("""
                UPDATE study_sessions SET
                    end_time = ?, cards_studied = ?, correct_answers = ?,
                    duration_minutes = ?, performance_data = ?
                WHERE id = ?
            """, (
                now.isoformat(), cards_studied, correct_answers,
                duration_minutes, json.dumps(performance_data), session_id
            ))
        
        # Check for session-based achievements
        if performance_data['accuracy'] == 1.0 and cards_studied > 0:
            self._check_achievement('perfect_session')
        
        if cards_studied >= 50 and duration_minutes <= 5:
            self._check_achievement('speed_demon')
        
        self._check_streak_achievements()
        self._check_milestone_achievements()
        
        return StudySession(
            id=session_id,
            start_time=session_row[0],
            end_time=now.isoformat(),
            cards_studied=cards_studied,
            correct_answers=correct_answers,
            study_mode=StudyMode(session_row[1]),
            duration_minutes=duration_minutes,
            categories=json.loads(session_row[2]) if session_row[2] else [],
            performance_data=performance_data
        )
    
    def get_card(self, card_id: str) -> Optional[LearningCard]:
        """Get a specific card by ID."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM learning_cards WHERE id = ?", 
                (card_id,)
            ).fetchone()
            
            return self._row_to_card(row) if row else None
    
    def get_study_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get study statistics for the specified period."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            # Session stats
            session_stats = conn.execute("""
                SELECT COUNT(*) as sessions,
                       SUM(cards_studied) as total_cards,
                       SUM(correct_answers) as correct_cards,
                       AVG(duration_minutes) as avg_duration,
                       SUM(duration_minutes) as total_minutes
                FROM study_sessions 
                WHERE start_time >= ? AND start_time <= ?
            """, (start_date.isoformat(), end_date.isoformat())).fetchone()
            
            # Daily breakdown
            daily_stats = conn.execute("""
                SELECT DATE(start_time) as date,
                       COUNT(*) as sessions,
                       SUM(cards_studied) as cards,
                       SUM(correct_answers) as correct
                FROM study_sessions 
                WHERE start_time >= ? AND start_time <= ?
                GROUP BY DATE(start_time)
                ORDER BY date
            """, (start_date.isoformat(), end_date.isoformat())).fetchall()
            
            # Category performance
            category_stats = conn.execute("""
                SELECT lc.category,
                       COUNT(*) as reviews,
                       AVG(CASE WHEN rh.result IN ('good', 'easy') THEN 1.0 ELSE 0.0 END) as accuracy
                FROM review_history rh
                JOIN learning_cards lc ON rh.card_id = lc.id
                WHERE rh.review_date >= ? AND rh.review_date <= ?
                GROUP BY lc.category
            """, (start_date.isoformat(), end_date.isoformat())).fetchall()
            
            # Streak information
            current_streak = self._calculate_current_streak()
            longest_streak = self._calculate_longest_streak()
            
            return {
                'period_days': days,
                'sessions': session_stats[0] or 0,
                'total_cards_studied': session_stats[1] or 0,
                'correct_answers': session_stats[2] or 0,
                'accuracy': (session_stats[2] / session_stats[1]) if session_stats[1] else 0,
                'avg_session_duration': session_stats[3] or 0,
                'total_study_time': session_stats[4] or 0,
                'daily_breakdown': [{
                    'date': row[0],
                    'sessions': row[1],
                    'cards': row[2],
                    'correct': row[3]
                } for row in daily_stats],
                'category_performance': [{
                    'category': row[0],
                    'reviews': row[1],
                    'accuracy': row[2]
                } for row in category_stats],
                'current_streak': current_streak,
                'longest_streak': longest_streak
            }
    
    def get_achievements(self, earned_only: bool = False) -> List[Achievement]:
        """Get all achievements, optionally filtered to earned only."""
        with sqlite3.connect(self.db_path) as conn:
            if earned_only:
                rows = conn.execute("""
                    SELECT id, name, description, icon, earned_date, points, category
                    FROM achievements 
                    WHERE earned_date IS NOT NULL
                    ORDER BY earned_date DESC
                """).fetchall()
            else:
                rows = conn.execute("""
                    SELECT id, name, description, icon, earned_date, points, category
                    FROM achievements 
                    ORDER BY category, points
                """).fetchall()
            
            achievements = []
            for row in rows:
                achievements.append(Achievement(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    icon=row[3],
                    earned_date=row[4] or "",
                    points=row[5],
                    category=row[6]
                ))
            
            return achievements
    
    def generate_practice_session(self, target_count: int = 20,
                                 include_new: bool = True,
                                 include_due: bool = True,
                                 categories: List[str] = None) -> List[LearningCard]:
        """Generate a balanced practice session."""
        cards = []
        
        if include_due:
            due_cards = self.get_due_cards(limit=target_count, category=categories[0] if categories else None)
            cards.extend(due_cards)
        
        if include_new and len(cards) < target_count:
            remaining = target_count - len(cards)
            new_cards = self.get_new_cards(limit=remaining, category=categories[0] if categories else None)
            cards.extend(new_cards)
        
        # Shuffle for variety
        random.shuffle(cards)
        
        return cards[:target_count]
    
    def export_cards(self, category: Optional[str] = None, 
                    format_type: str = 'json') -> str:
        """Export learning cards in specified format."""
        with sqlite3.connect(self.db_path) as conn:
            if category:
                rows = conn.execute(
                    "SELECT * FROM learning_cards WHERE category = ?", 
                    (category,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM learning_cards").fetchall()
            
            cards = [self._row_to_card(row) for row in rows]
            
            if format_type == 'json':
                export_data = {
                    'cards': [asdict(card) for card in cards],
                    'export_date': datetime.now().isoformat(),
                    'total_cards': len(cards)
                }
                return json.dumps(export_data, indent=2)
            
            elif format_type == 'anki':
                # Anki import format
                output = []
                for card in cards:
                    # Front[tab]Back[tab]Tags
                    output.append(f"{card.front}\t{card.back}\t{' '.join(card.tags)}")
                return '\n'.join(output)
            
            return json.dumps([asdict(card) for card in cards], indent=2)
    
    def _row_to_card(self, row) -> LearningCard:
        """Convert database row to LearningCard object."""
        return LearningCard(
            id=row[0],
            front=row[1],
            back=row[2],
            category=row[3],
            difficulty=DifficultyLevel(row[4]),
            interval=row[5],
            repetitions=row[6],
            easiness_factor=row[7],
            last_reviewed=row[8] or "",
            next_review=row[9],
            success_rate=row[10],
            review_count=row[11],
            creation_date=row[12],
            tags=json.loads(row[13]) if row[13] else [],
            notes=row[14] or "",
            audio_front=row[15],
            audio_back=row[16],
            image_url=row[17]
        )
    
    def _check_achievement(self, achievement_id: str) -> bool:
        """Check and award achievement if criteria met."""
        with sqlite3.connect(self.db_path) as conn:
            # Check if already earned
            earned = conn.execute(
                "SELECT earned_date FROM achievements WHERE id = ?",
                (achievement_id,)
            ).fetchone()
            
            if earned and earned[0]:
                return False  # Already earned
            
            # Award achievement
            conn.execute(
                "UPDATE achievements SET earned_date = ? WHERE id = ?",
                (datetime.now().isoformat(), achievement_id)
            )
            
            return True
    
    def _check_streak_achievements(self):
        """Check streak-based achievements."""
        streak = self._calculate_current_streak()
        
        if streak >= 7:
            self._check_achievement('daily_streak_7')
        if streak >= 30:
            self._check_achievement('daily_streak_30')
    
    def _check_milestone_achievements(self):
        """Check milestone achievements."""
        with sqlite3.connect(self.db_path) as conn:
            # Check vocabulary count
            vocab_count = conn.execute(
                "SELECT COUNT(*) FROM learning_cards WHERE category LIKE '%vocabulary%'"
            ).fetchone()[0]
            
            if vocab_count >= 100:
                self._check_achievement('vocabulary_100')
            
            # Check total reviews
            total_reviews = conn.execute(
                "SELECT COUNT(*) FROM review_history"
            ).fetchone()[0]
            
            if total_reviews >= 1000:
                self._check_achievement('review_master')
    
    def _check_performance_achievements(self, session_id: str):
        """Check performance-based achievements."""
        # Implementation would check various performance criteria
        pass
    
    def _calculate_current_streak(self) -> int:
        """Calculate current daily study streak."""
        with sqlite3.connect(self.db_path) as conn:
            # Get study dates in descending order
            dates = conn.execute("""
                SELECT DISTINCT DATE(start_time) as study_date
                FROM study_sessions
                WHERE cards_studied > 0
                ORDER BY study_date DESC
            """).fetchall()
            
            if not dates:
                return 0
            
            streak = 0
            today = datetime.now().date()
            
            for i, (date_str,) in enumerate(dates):
                date = datetime.fromisoformat(date_str).date()
                expected_date = today - timedelta(days=i)
                
                if date == expected_date:
                    streak += 1
                else:
                    break
            
            return streak
    
    def _calculate_longest_streak(self) -> int:
        """Calculate longest study streak ever achieved."""
        with sqlite3.connect(self.db_path) as conn:
            dates = conn.execute("""
                SELECT DISTINCT DATE(start_time) as study_date
                FROM study_sessions
                WHERE cards_studied > 0
                ORDER BY study_date ASC
            """).fetchall()
            
            if not dates:
                return 0
            
            max_streak = 0
            current_streak = 1
            
            for i in range(1, len(dates)):
                prev_date = datetime.fromisoformat(dates[i-1][0]).date()
                curr_date = datetime.fromisoformat(dates[i][0]).date()
                
                if (curr_date - prev_date).days == 1:
                    current_streak += 1
                else:
                    max_streak = max(max_streak, current_streak)
                    current_streak = 1
            
            return max(max_streak, current_streak)