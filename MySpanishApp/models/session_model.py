# File: models/session_model.py
import sqlite3
from datetime import datetime
from utils.logger import get_logger
from .database import Database

logger = get_logger(__name__)

class SessionModel:
    """
    Provides CRUD operations for the 'sessions' table.
    """

    def __init__(self, db: Database):
        self.db = db

    def create_session(self, teacher_id, session_date, start_time, duration, status="planned"):
        """
        Insert a new session record.
        """
        if not teacher_id or not session_date or not start_time:
            logger.error("Missing required fields: teacher_id, session_date, start_time")
            return None
            
        try:
            cursor = self.db.conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = """
                INSERT INTO sessions
                (teacher_id, session_date, start_time, duration, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql, (teacher_id, session_date, start_time, duration, status, timestamp))
            self.db.conn.commit()
            session_id = cursor.lastrowid
            logger.info(f"Created new session with id={session_id}")
            return session_id
        except sqlite3.Error as e:
            logger.error(f"Error creating session: {e}")
            return None

    def get_sessions(self):
        """
        Retrieve all sessions (for demo purposes).
        """
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT * FROM sessions ORDER BY session_date ASC, start_time ASC")
            rows = cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            logger.error(f"Error fetching sessions: {e}")
            return []

    def update_session_status(self, session_id, new_status):
        """
        Update the status of a given session (e.g., from 'planned' to 'completed').
        """
        try:
            cursor = self.db.conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = """
                UPDATE sessions
                SET status = ?, timestamp = ?
                WHERE session_id = ?
            """
            cursor.execute(sql, (new_status, timestamp, session_id))
            self.db.conn.commit()
            logger.info(f"Updated session {session_id} to status={new_status}")
            return cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"Error updating session: {e}")
            return 0

    def delete_session(self, session_id):
        """
        Remove a session record.
        """
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            self.db.conn.commit()
            logger.info(f"Deleted session {session_id}")
            return cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"Error deleting session: {e}")
            return 0
