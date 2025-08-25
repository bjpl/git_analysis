"""Advanced session management with auto-save, history, and cloud sync preparation."""

import json
import sqlite3
import gzip
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time
import pickle
from contextlib import contextmanager


class SessionStatus(Enum):
    """Session status types."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CRASHED = "crashed"
    IMPORTED = "imported"


class AutoSaveFrequency(Enum):
    """Auto-save frequency options."""
    DISABLED = 0
    EVERY_ACTION = 1  # Save after every action
    EVERY_30_SECONDS = 30
    EVERY_MINUTE = 60
    EVERY_5_MINUTES = 300
    EVERY_15_MINUTES = 900


@dataclass
class SessionAction:
    """Individual action within a session."""
    id: str
    timestamp: str
    action_type: str  # 'search', 'image_view', 'vocabulary_add', 'description_generate', etc.
    data: Dict[str, Any]
    user_input: str = ""
    result: str = ""
    duration_ms: int = 0
    error: Optional[str] = None


@dataclass
class SessionState:
    """Complete state of a session."""
    search_query: str = ""
    current_image_url: str = ""
    current_image_metadata: Dict[str, Any] = None
    user_notes: str = ""
    generated_description: str = ""
    extracted_phrases: Dict[str, List[str]] = None
    target_phrases: List[str] = None
    ui_state: Dict[str, Any] = None
    settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.current_image_metadata is None:
            self.current_image_metadata = {}
        if self.extracted_phrases is None:
            self.extracted_phrases = {}
        if self.target_phrases is None:
            self.target_phrases = []
        if self.ui_state is None:
            self.ui_state = {}
        if self.settings is None:
            self.settings = {}


@dataclass
class Session:
    """Complete session information."""
    id: str
    name: str
    start_time: str
    end_time: Optional[str]
    status: SessionStatus
    actions: List[SessionAction]
    final_state: SessionState
    statistics: Dict[str, Any]
    tags: List[str] = None
    notes: str = ""
    auto_save_enabled: bool = True
    last_save_time: str = ""
    size_bytes: int = 0
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class SessionManager:
    """Advanced session management with auto-save and recovery features."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.db_path = data_dir / "sessions.db"
        self.sessions_dir = data_dir / "sessions"
        self.backups_dir = data_dir / "backups" 
        self.temp_dir = data_dir / "temp"
        
        # Create directories
        for directory in [self.sessions_dir, self.backups_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Auto-save settings
        self.auto_save_frequency = AutoSaveFrequency.EVERY_MINUTE
        self.max_auto_saves = 10  # Keep last 10 auto-saves
        self.compression_enabled = True
        
        # Current session tracking
        self.current_session: Optional[Session] = None
        self.current_session_id: Optional[str] = None
        self.auto_save_thread: Optional[threading.Thread] = None
        self.auto_save_running = False
        self.session_lock = threading.Lock()
        
        # Callbacks for session events
        self.session_callbacks: Dict[str, List[Callable]] = {
            'session_started': [],
            'session_ended': [],
            'session_saved': [],
            'action_recorded': [],
            'state_changed': []
        }
        
        self._init_database()
        self._recover_crashed_sessions()
    
    def _init_database(self):
        """Initialize the sessions database."""
        with sqlite3.connect(self.db_path) as conn:
            # Sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    status TEXT NOT NULL,
                    statistics TEXT,
                    tags TEXT,
                    notes TEXT,
                    auto_save_enabled BOOLEAN DEFAULT TRUE,
                    last_save_time TEXT,
                    size_bytes INTEGER DEFAULT 0,
                    file_path TEXT
                )
            """)
            
            # Session actions table (for quick queries)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_actions (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    duration_ms INTEGER DEFAULT 0,
                    has_error BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
                )
            """)
            
            # Auto-save history table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS auto_saves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    save_time TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    size_bytes INTEGER DEFAULT 0,
                    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
                )
            """)
            
            # Session recovery table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_recovery (
                    session_id TEXT PRIMARY KEY,
                    recovery_data TEXT NOT NULL,
                    crash_time TEXT NOT NULL,
                    recovered BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.commit()
    
    def start_session(self, name: Optional[str] = None, 
                     auto_save: bool = True) -> str:
        """Start a new session."""
        import uuid
        
        # End current session if exists
        if self.current_session_id:
            self.end_session()
        
        # Create new session
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        if not name:
            name = f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        session = Session(
            id=session_id,
            name=name,
            start_time=now,
            end_time=None,
            status=SessionStatus.ACTIVE,
            actions=[],
            final_state=SessionState(),
            statistics={},
            auto_save_enabled=auto_save,
            last_save_time=now
        )
        
        with self.session_lock:
            self.current_session = session
            self.current_session_id = session_id
        
        # Save initial session
        self._save_session_to_db(session)
        self._save_session_to_file(session)
        
        # Start auto-save if enabled
        if auto_save and self.auto_save_frequency != AutoSaveFrequency.DISABLED:
            self._start_auto_save_thread()
        
        # Notify callbacks
        self._trigger_callbacks('session_started', session)
        
        return session_id
    
    def end_session(self, notes: str = "") -> Optional[Session]:
        """End the current session."""
        if not self.current_session:
            return None
        
        with self.session_lock:
            session = self.current_session
            session.end_time = datetime.now().isoformat()
            session.status = SessionStatus.COMPLETED
            session.notes = notes
            
            # Calculate final statistics
            session.statistics = self._calculate_session_statistics(session)
            
            # Stop auto-save
            self._stop_auto_save_thread()
            
            # Final save
            self._save_session_to_db(session)
            self._save_session_to_file(session)
            
            # Cleanup
            self.current_session = None
            self.current_session_id = None
        
        # Notify callbacks
        self._trigger_callbacks('session_ended', session)
        
        return session
    
    def record_action(self, action_type: str, data: Dict[str, Any],
                     user_input: str = "", result: str = "",
                     duration_ms: int = 0, error: Optional[str] = None):
        """Record an action in the current session."""
        if not self.current_session:
            return
        
        import uuid
        action_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        action = SessionAction(
            id=action_id,
            timestamp=now,
            action_type=action_type,
            data=data.copy(),
            user_input=user_input,
            result=result,
            duration_ms=duration_ms,
            error=error
        )
        
        with self.session_lock:
            self.current_session.actions.append(action)
            
            # Save action to database for quick access
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO session_actions 
                    (id, session_id, timestamp, action_type, duration_ms, has_error)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    action_id, self.current_session_id, now, action_type,
                    duration_ms, error is not None
                ))
        
        # Auto-save if configured
        if (self.auto_save_frequency == AutoSaveFrequency.EVERY_ACTION and 
            self.current_session.auto_save_enabled):
            self._auto_save_session()
        
        # Notify callbacks
        self._trigger_callbacks('action_recorded', action)
    
    def update_session_state(self, **kwargs):
        """Update the current session state."""
        if not self.current_session:
            return
        
        with self.session_lock:
            state = self.current_session.final_state
            
            for key, value in kwargs.items():
                if hasattr(state, key):
                    setattr(state, key, value)
        
        # Notify callbacks
        self._trigger_callbacks('state_changed', self.current_session.final_state)
    
    def pause_session(self):
        """Pause the current session."""
        if not self.current_session:
            return
        
        with self.session_lock:
            self.current_session.status = SessionStatus.PAUSED
            self._stop_auto_save_thread()
        
        self._save_session_to_db(self.current_session)
    
    def resume_session(self):
        """Resume a paused session."""
        if not self.current_session:
            return
        
        with self.session_lock:
            self.current_session.status = SessionStatus.ACTIVE
            
            if (self.current_session.auto_save_enabled and 
                self.auto_save_frequency != AutoSaveFrequency.DISABLED):
                self._start_auto_save_thread()
    
    def get_session(self, session_id: str, load_actions: bool = True) -> Optional[Session]:
        """Get a session by ID."""
        # Check if it's the current session
        if self.current_session and self.current_session.id == session_id:
            return self.current_session
        
        # Load from file
        session_file = self.sessions_dir / f"{session_id}.json"
        compressed_file = self.sessions_dir / f"{session_id}.json.gz"
        
        data = None
        
        # Try compressed file first
        if compressed_file.exists():
            try:
                with gzip.open(compressed_file, 'rt', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Error loading compressed session: {e}")
        
        # Try uncompressed file
        if not data and session_file.exists():
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Error loading session: {e}")
                return None
        
        if not data:
            return None
        
        # Reconstruct session object
        session = Session(
            id=data['id'],
            name=data['name'],
            start_time=data['start_time'],
            end_time=data.get('end_time'),
            status=SessionStatus(data['status']),
            actions=[],
            final_state=SessionState(**data.get('final_state', {})),
            statistics=data.get('statistics', {}),
            tags=data.get('tags', []),
            notes=data.get('notes', ''),
            auto_save_enabled=data.get('auto_save_enabled', True),
            last_save_time=data.get('last_save_time', ''),
            size_bytes=data.get('size_bytes', 0)
        )
        
        # Load actions if requested
        if load_actions:
            for action_data in data.get('actions', []):
                action = SessionAction(
                    id=action_data['id'],
                    timestamp=action_data['timestamp'],
                    action_type=action_data['action_type'],
                    data=action_data.get('data', {}),
                    user_input=action_data.get('user_input', ''),
                    result=action_data.get('result', ''),
                    duration_ms=action_data.get('duration_ms', 0),
                    error=action_data.get('error')
                )
                session.actions.append(action)
        
        return session
    
    def list_sessions(self, limit: int = 50, status: Optional[SessionStatus] = None,
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> List[Session]:
        """List sessions with optional filtering."""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM sessions WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status.value)
            
            if start_date:
                query += " AND start_time >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                query += " AND start_time <= ?"
                params.append(end_date.isoformat())
            
            query += " ORDER BY start_time DESC LIMIT ?"
            params.append(limit)
            
            rows = conn.execute(query, params).fetchall()
            
            sessions = []
            for row in rows:
                # Load basic session info without actions for performance
                session = Session(
                    id=row[0],
                    name=row[1],
                    start_time=row[2],
                    end_time=row[3],
                    status=SessionStatus(row[4]),
                    actions=[],  # Don't load actions for list view
                    final_state=SessionState(),  # Placeholder
                    statistics=json.loads(row[5]) if row[5] else {},
                    tags=json.loads(row[6]) if row[6] else [],
                    notes=row[7] or '',
                    auto_save_enabled=bool(row[8]),
                    last_save_time=row[9] or '',
                    size_bytes=row[10] or 0
                )
                sessions.append(session)
            
            return sessions
    
    def search_sessions(self, query: str, limit: int = 20) -> List[Session]:
        """Search sessions by name, notes, or tags."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT * FROM sessions 
                WHERE name LIKE ? OR notes LIKE ? OR tags LIKE ?
                ORDER BY start_time DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", limit)).fetchall()
            
            sessions = []
            for row in rows:
                session = Session(
                    id=row[0],
                    name=row[1],
                    start_time=row[2],
                    end_time=row[3],
                    status=SessionStatus(row[4]),
                    actions=[],
                    final_state=SessionState(),
                    statistics=json.loads(row[5]) if row[5] else {},
                    tags=json.loads(row[6]) if row[6] else [],
                    notes=row[7] or '',
                    auto_save_enabled=bool(row[8]),
                    last_save_time=row[9] or '',
                    size_bytes=row[10] or 0
                )
                sessions.append(session)
            
            return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its data."""
        try:
            # Remove from database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM sessions WHERE id = ?", (session_id,)
                )
                
                if cursor.rowcount == 0:
                    return False
            
            # Remove files
            session_file = self.sessions_dir / f"{session_id}.json"
            compressed_file = self.sessions_dir / f"{session_id}.json.gz"
            
            for file_path in [session_file, compressed_file]:
                if file_path.exists():
                    file_path.unlink()
            
            # Remove auto-saves
            self._cleanup_auto_saves(session_id)
            
            return True
            
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    def export_session(self, session_id: str, format_type: str = 'json',
                      include_actions: bool = True) -> str:
        """Export session in specified format."""
        session = self.get_session(session_id, load_actions=include_actions)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if format_type == 'json':
            export_data = {
                'session': asdict(session),
                'export_timestamp': datetime.now().isoformat(),
                'format_version': '1.0'
            }
            return json.dumps(export_data, indent=2)
        
        elif format_type == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Session info
            writer.writerow(['Session Export'])
            writer.writerow(['Name', session.name])
            writer.writerow(['Start Time', session.start_time])
            writer.writerow(['End Time', session.end_time or 'Not ended'])
            writer.writerow(['Status', session.status.value])
            writer.writerow([])
            
            # Actions
            if include_actions:
                writer.writerow(['Actions'])
                writer.writerow(['Timestamp', 'Type', 'User Input', 'Result', 'Duration (ms)', 'Error'])
                
                for action in session.actions:
                    writer.writerow([
                        action.timestamp,
                        action.action_type,
                        action.user_input,
                        action.result[:100] if action.result else '',  # Truncate long results
                        action.duration_ms,
                        action.error or ''
                    ])
            
            return output.getvalue()
        
        return json.dumps(asdict(session), indent=2)
    
    def import_session(self, data: str, format_type: str = 'json') -> str:
        """Import session from external data."""
        if format_type == 'json':
            import_data = json.loads(data)
            session_data = import_data.get('session', import_data)
            
            # Generate new ID to avoid conflicts
            import uuid
            new_session_id = str(uuid.uuid4())
            session_data['id'] = new_session_id
            session_data['status'] = SessionStatus.IMPORTED.value
            
            # Create session object
            session = Session(**session_data)
            
            # Save to database and file
            self._save_session_to_db(session)
            self._save_session_to_file(session)
            
            return new_session_id
        
        raise ValueError(f"Unsupported import format: {format_type}")
    
    def get_session_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get session statistics for the specified period."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            # Basic session stats
            session_stats = conn.execute("""
                SELECT COUNT(*) as total_sessions,
                       COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
                       COUNT(CASE WHEN status = 'active' THEN 1 END) as active_sessions,
                       COUNT(CASE WHEN status = 'crashed' THEN 1 END) as crashed_sessions,
                       AVG(
                           CASE WHEN end_time IS NOT NULL THEN
                               (julianday(end_time) - julianday(start_time)) * 24 * 60
                           END
                       ) as avg_duration_minutes
                FROM sessions 
                WHERE start_time >= ? AND start_time <= ?
            """, (start_date.isoformat(), end_date.isoformat())).fetchone()
            
            # Action type breakdown
            action_stats = conn.execute("""
                SELECT sa.action_type, COUNT(*) as count,
                       AVG(sa.duration_ms) as avg_duration_ms
                FROM session_actions sa
                JOIN sessions s ON sa.session_id = s.id
                WHERE s.start_time >= ? AND s.start_time <= ?
                GROUP BY sa.action_type
                ORDER BY count DESC
            """, (start_date.isoformat(), end_date.isoformat())).fetchall()
            
            # Daily session counts
            daily_stats = conn.execute("""
                SELECT DATE(start_time) as date,
                       COUNT(*) as sessions
                FROM sessions 
                WHERE start_time >= ? AND start_time <= ?
                GROUP BY DATE(start_time)
                ORDER BY date
            """, (start_date.isoformat(), end_date.isoformat())).fetchall()
            
            return {
                'period_days': days,
                'total_sessions': session_stats[0] or 0,
                'completed_sessions': session_stats[1] or 0,
                'active_sessions': session_stats[2] or 0,
                'crashed_sessions': session_stats[3] or 0,
                'avg_duration_minutes': session_stats[4] or 0,
                'action_breakdown': [{
                    'action_type': row[0],
                    'count': row[1],
                    'avg_duration_ms': row[2]
                } for row in action_stats],
                'daily_sessions': [{
                    'date': row[0],
                    'sessions': row[1]
                } for row in daily_stats]
            }
    
    def register_callback(self, event_type: str, callback: Callable):
        """Register a callback for session events."""
        if event_type in self.session_callbacks:
            self.session_callbacks[event_type].append(callback)
    
    def set_auto_save_frequency(self, frequency: AutoSaveFrequency):
        """Set auto-save frequency."""
        self.auto_save_frequency = frequency
        
        # Restart auto-save thread if session is active
        if self.current_session and self.current_session.auto_save_enabled:
            self._stop_auto_save_thread()
            if frequency != AutoSaveFrequency.DISABLED:
                self._start_auto_save_thread()
    
    def create_backup(self, session_id: str) -> Path:
        """Create a backup of a session."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{session_id}_backup_{timestamp}.json.gz"
        backup_path = self.backups_dir / backup_filename
        
        # Export and compress
        export_data = self.export_session(session_id, 'json', include_actions=True)
        
        with gzip.open(backup_path, 'wt', encoding='utf-8') as f:
            f.write(export_data)
        
        return backup_path
    
    def _save_session_to_db(self, session: Session):
        """Save session metadata to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO sessions 
                (id, name, start_time, end_time, status, statistics, tags, 
                 notes, auto_save_enabled, last_save_time, size_bytes, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.id, session.name, session.start_time, session.end_time,
                session.status.value, json.dumps(session.statistics),
                json.dumps(session.tags), session.notes, session.auto_save_enabled,
                session.last_save_time, session.size_bytes,
                str(self.sessions_dir / f"{session.id}.json")
            ))
    
    def _save_session_to_file(self, session: Session):
        """Save complete session data to file."""
        session_data = asdict(session)
        json_data = json.dumps(session_data, indent=2)
        
        # Calculate size
        session.size_bytes = len(json_data.encode('utf-8'))
        session.last_save_time = datetime.now().isoformat()
        
        if self.compression_enabled:
            # Save compressed
            file_path = self.sessions_dir / f"{session.id}.json.gz"
            with gzip.open(file_path, 'wt', encoding='utf-8') as f:
                f.write(json_data)
        else:
            # Save uncompressed
            file_path = self.sessions_dir / f"{session.id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_data)
        
        # Notify callbacks
        self._trigger_callbacks('session_saved', session)
    
    def _start_auto_save_thread(self):
        """Start the auto-save background thread."""
        if self.auto_save_thread and self.auto_save_thread.is_alive():
            return
        
        self.auto_save_running = True
        self.auto_save_thread = threading.Thread(
            target=self._auto_save_worker,
            daemon=True
        )
        self.auto_save_thread.start()
    
    def _stop_auto_save_thread(self):
        """Stop the auto-save background thread."""
        self.auto_save_running = False
        if self.auto_save_thread:
            self.auto_save_thread.join(timeout=1.0)
    
    def _auto_save_worker(self):
        """Auto-save worker thread."""
        while self.auto_save_running:
            try:
                time.sleep(self.auto_save_frequency.value)
                
                if self.current_session and self.current_session.auto_save_enabled:
                    self._auto_save_session()
                    
            except Exception as e:
                print(f"Auto-save error: {e}")
    
    def _auto_save_session(self):
        """Perform an auto-save of the current session."""
        if not self.current_session:
            return
        
        with self.session_lock:
            # Create auto-save file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            auto_save_path = self.temp_dir / f"{self.current_session.id}_autosave_{timestamp}.json.gz"
            
            # Save session data
            session_data = asdict(self.current_session)
            json_data = json.dumps(session_data, indent=2)
            
            with gzip.open(auto_save_path, 'wt', encoding='utf-8') as f:
                f.write(json_data)
            
            # Record auto-save
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO auto_saves 
                    (session_id, save_time, file_path, size_bytes)
                    VALUES (?, ?, ?, ?)
                """, (
                    self.current_session.id,
                    datetime.now().isoformat(),
                    str(auto_save_path),
                    len(json_data.encode('utf-8'))
                ))
            
            # Cleanup old auto-saves
            self._cleanup_auto_saves(self.current_session.id)
    
    def _cleanup_auto_saves(self, session_id: str):
        """Remove old auto-save files, keeping only the most recent ones."""
        with sqlite3.connect(self.db_path) as conn:
            # Get auto-saves for this session, ordered by time
            rows = conn.execute("""
                SELECT id, file_path FROM auto_saves
                WHERE session_id = ?
                ORDER BY save_time DESC
            """, (session_id,)).fetchall()
            
            # Remove excess auto-saves
            if len(rows) > self.max_auto_saves:
                for row in rows[self.max_auto_saves:]:
                    auto_save_id, file_path = row
                    
                    # Remove file
                    try:
                        Path(file_path).unlink(missing_ok=True)
                    except Exception:
                        pass
                    
                    # Remove from database
                    conn.execute(
                        "DELETE FROM auto_saves WHERE id = ?", 
                        (auto_save_id,)
                    )
    
    def _recover_crashed_sessions(self):
        """Recover sessions that were interrupted."""
        with sqlite3.connect(self.db_path) as conn:
            # Find active sessions that might have crashed
            crashed_sessions = conn.execute("""
                SELECT id FROM sessions 
                WHERE status = 'active'
            """).fetchall()
            
            for (session_id,) in crashed_sessions:
                # Mark as crashed
                conn.execute(
                    "UPDATE sessions SET status = 'crashed' WHERE id = ?",
                    (session_id,)
                )
                
                # Store recovery data
                recovery_data = {
                    'session_id': session_id,
                    'crash_detected_at': datetime.now().isoformat(),
                    'auto_saves_available': self._get_auto_saves_count(session_id)
                }
                
                conn.execute("""
                    INSERT OR REPLACE INTO session_recovery 
                    (session_id, recovery_data, crash_time, recovered)
                    VALUES (?, ?, ?, FALSE)
                """, (
                    session_id,
                    json.dumps(recovery_data),
                    datetime.now().isoformat()
                ))
    
    def _get_auto_saves_count(self, session_id: str) -> int:
        """Get count of available auto-saves for a session."""
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM auto_saves WHERE session_id = ?",
                (session_id,)
            ).fetchone()[0]
            return count
    
    def _calculate_session_statistics(self, session: Session) -> Dict[str, Any]:
        """Calculate comprehensive statistics for a session."""
        if not session.actions:
            return {}
        
        # Duration
        start_time = datetime.fromisoformat(session.start_time)
        end_time = datetime.fromisoformat(session.end_time) if session.end_time else datetime.now()
        duration_minutes = (end_time - start_time).total_seconds() / 60
        
        # Action statistics
        action_counts = {}
        total_duration_ms = 0
        error_count = 0
        
        for action in session.actions:
            action_type = action.action_type
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
            total_duration_ms += action.duration_ms
            if action.error:
                error_count += 1
        
        return {
            'duration_minutes': duration_minutes,
            'total_actions': len(session.actions),
            'action_breakdown': action_counts,
            'avg_action_duration_ms': total_duration_ms / len(session.actions) if session.actions else 0,
            'error_count': error_count,
            'error_rate': error_count / len(session.actions) if session.actions else 0,
            'vocabulary_learned': len(session.final_state.target_phrases),
            'images_viewed': action_counts.get('image_view', 0),
            'searches_performed': action_counts.get('search', 0),
            'descriptions_generated': action_counts.get('description_generate', 0)
        }
    
    def _trigger_callbacks(self, event_type: str, data: Any):
        """Trigger registered callbacks for an event."""
        for callback in self.session_callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                print(f"Callback error for {event_type}: {e}")
    
    @contextmanager
    def session_context(self, name: str = None, auto_save: bool = True):
        """Context manager for automatic session management."""
        session_id = self.start_session(name, auto_save)
        try:
            yield session_id
        except Exception as e:
            # Record the error
            self.record_action('error', {'error': str(e)}, error=str(e))
            raise
        finally:
            self.end_session()