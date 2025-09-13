"""
Simple Progress Tracker
Follows standard conventions without overengineering
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class SessionData:
    """Simple session tracking"""
    date: str  # ISO date format YYYY-MM-DD
    duration_minutes: int
    topics: List[str]
    completion_rate: float = 0.0  # 0.0 to 1.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass  
class TopicProgress:
    """Track progress on a single topic"""
    id: str
    name: str
    score: Optional[int] = None  # 0-100 scale
    progress: float = 0.0  # 0.0 to 1.0
    started_at: Optional[str] = None  # ISO 8601
    completed_at: Optional[str] = None  # ISO 8601
    
    def is_complete(self) -> bool:
        return self.completed_at is not None
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class QuizScore:
    """Simple quiz score tracking"""
    quiz_id: str
    score: int  # 0-100
    max_score: int = 100
    date: str = None  # ISO date
    
    def __post_init__(self):
        if self.date is None:
            self.date = datetime.now().strftime("%Y-%m-%d")
    
    def percentage(self) -> float:
        return (self.score / self.max_score) * 100 if self.max_score > 0 else 0
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ProgressTracker:
    """
    Simple progress tracker following standard conventions:
    - ISO 8601 dates/times
    - 0-100 scoring scale
    - 0.0-1.0 progress/completion rates
    - Simple JSON persistence
    """
    
    def __init__(self, progress_file: str = "progress.json"):
        self.progress_file = Path(progress_file)
        self.data = self._load_progress()
    
    def _load_progress(self) -> Dict:
        """Load progress from JSON file"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._default_progress()
        return self._default_progress()
    
    def _default_progress(self) -> Dict:
        """Create default progress structure"""
        now = datetime.now().isoformat() + 'Z'
        return {
            "user_id": "user",
            "created": now,
            "last_updated": now,
            "sessions": [],
            "topics_completed": [],
            "topics_in_progress": [],
            "quiz_scores": [],
            "stats": {
                "total_time_minutes": 0,
                "average_score": 0,
                "topics_completed": 0,
                "topics_started": 0,
                "current_streak_days": 0,
                "longest_streak_days": 0
            },
            "preferences": {
                "difficulty": "beginner",
                "preferred_language": "python",
                "show_hints": True,
                "email_reminders": False
            },
            "next_recommended": []
        }
    
    def save(self) -> None:
        """Save progress to JSON file"""
        self.data["last_updated"] = datetime.now().isoformat() + 'Z'
        self._update_stats()
        
        with open(self.progress_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def add_session(self, duration_minutes: int, topics: List[str]) -> None:
        """Add a learning session"""
        session = SessionData(
            date=datetime.now().strftime("%Y-%m-%d"),
            duration_minutes=duration_minutes,
            topics=topics,
            completion_rate=self._calculate_session_completion(topics)
        )
        
        self.data["sessions"].append(session.to_dict())
        self._update_streak()
        self.save()
    
    def complete_topic(self, topic_id: str, topic_name: str, score: int) -> None:
        """Mark a topic as completed with score (0-100)"""
        # Remove from in-progress if exists
        self.data["topics_in_progress"] = [
            t for t in self.data["topics_in_progress"] 
            if t["id"] != topic_id
        ]
        
        # Add to completed
        topic = TopicProgress(
            id=topic_id,
            name=topic_name,
            score=min(100, max(0, score)),  # Clamp to 0-100
            completed_at=datetime.now().isoformat() + 'Z'
        )
        
        # Check if already completed (update score if better)
        existing = next((t for t in self.data["topics_completed"] 
                        if t["id"] == topic_id), None)
        if existing:
            if score > existing.get("score", 0):
                existing["score"] = score
                existing["completed_at"] = topic.completed_at
        else:
            self.data["topics_completed"].append(topic.to_dict())
        
        self.save()
    
    def start_topic(self, topic_id: str, topic_name: str) -> None:
        """Start working on a topic"""
        # Check if already in progress or completed
        if any(t["id"] == topic_id for t in self.data["topics_in_progress"]):
            return
        if any(t["id"] == topic_id for t in self.data["topics_completed"]):
            return
        
        topic = TopicProgress(
            id=topic_id,
            name=topic_name,
            progress=0.0,
            started_at=datetime.now().isoformat() + 'Z'
        )
        
        self.data["topics_in_progress"].append(topic.to_dict())
        self.save()
    
    def update_topic_progress(self, topic_id: str, progress: float) -> None:
        """Update progress on a topic (0.0 to 1.0)"""
        progress = min(1.0, max(0.0, progress))  # Clamp to 0.0-1.0
        
        for topic in self.data["topics_in_progress"]:
            if topic["id"] == topic_id:
                topic["progress"] = progress
                break
        
        self.save()
    
    def add_quiz_score(self, quiz_id: str, score: int, max_score: int = 100) -> None:
        """Add a quiz score (0-100 scale)"""
        quiz = QuizScore(
            quiz_id=quiz_id,
            score=min(max_score, max(0, score)),
            max_score=max_score
        )
        
        self.data["quiz_scores"].append(quiz.to_dict())
        self.save()
    
    def _calculate_session_completion(self, topics: List[str]) -> float:
        """Calculate session completion rate based on topics"""
        if not topics:
            return 0.0
        
        completed = sum(1 for t in topics 
                       if any(tc["id"] == t for tc in self.data["topics_completed"]))
        return completed / len(topics)
    
    def _update_streak(self) -> None:
        """Update learning streak tracking"""
        today = datetime.now().strftime("%Y-%m-%d")
        sessions = self.data["sessions"]
        
        if not sessions:
            self.data["stats"]["current_streak_days"] = 1
            self.data["stats"]["longest_streak_days"] = 1
            return
        
        # Get unique session dates
        session_dates = sorted(set(s["date"] for s in sessions))
        
        # Calculate current streak
        current_streak = 1
        if session_dates and session_dates[-1] == today:
            # Count consecutive days backwards from today
            for i in range(len(session_dates) - 1, 0, -1):
                date1 = datetime.strptime(session_dates[i], "%Y-%m-%d")
                date2 = datetime.strptime(session_dates[i-1], "%Y-%m-%d")
                if (date1 - date2).days == 1:
                    current_streak += 1
                else:
                    break
        
        self.data["stats"]["current_streak_days"] = current_streak
        self.data["stats"]["longest_streak_days"] = max(
            current_streak, 
            self.data["stats"].get("longest_streak_days", 1)
        )
    
    def _update_stats(self) -> None:
        """Update aggregate statistics"""
        stats = self.data["stats"]
        
        # Total time
        stats["total_time_minutes"] = sum(
            s.get("duration_minutes", 0) for s in self.data["sessions"]
        )
        
        # Topic counts
        stats["topics_completed"] = len(self.data["topics_completed"])
        stats["topics_started"] = (
            len(self.data["topics_completed"]) + 
            len(self.data["topics_in_progress"])
        )
        
        # Average score
        all_scores = []
        all_scores.extend(t.get("score", 0) for t in self.data["topics_completed"] if "score" in t)
        all_scores.extend(q.get("score", 0) for q in self.data["quiz_scores"])
        
        if all_scores:
            stats["average_score"] = round(sum(all_scores) / len(all_scores))
        else:
            stats["average_score"] = 0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of progress"""
        self._update_stats()
        
        return {
            "user": self.data.get("user_id", "user"),
            "total_time_hours": round(self.data["stats"]["total_time_minutes"] / 60, 1),
            "topics_completed": self.data["stats"]["topics_completed"],
            "average_score": self.data["stats"]["average_score"],
            "current_streak": self.data["stats"]["current_streak_days"],
            "last_session": self.data["sessions"][-1]["date"] if self.data["sessions"] else None,
            "in_progress": [t["name"] for t in self.data["topics_in_progress"]],
            "next_recommended": self.data.get("next_recommended", [])
        }
    
    def get_recent_activity(self, days: int = 7) -> List[Dict]:
        """Get activity from the last N days"""
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        recent_sessions = [
            s for s in self.data["sessions"] 
            if s.get("date", "") >= cutoff_date
        ]
        
        return recent_sessions


# Example usage
if __name__ == "__main__":
    tracker = ProgressTracker()
    
    # Start a learning session
    tracker.add_session(duration_minutes=45, topics=["arrays", "linked-lists"])
    
    # Start a topic
    tracker.start_topic("arrays", "Arrays and Dynamic Arrays")
    
    # Update progress
    tracker.update_topic_progress("arrays", 0.5)
    
    # Complete a topic
    tracker.complete_topic("arrays", "Arrays and Dynamic Arrays", score=85)
    
    # Add quiz score
    tracker.add_quiz_score("arrays-quiz-1", score=90)
    
    # Get summary
    print(json.dumps(tracker.get_summary(), indent=2))