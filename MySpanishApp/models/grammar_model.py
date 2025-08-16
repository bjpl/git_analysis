# File: models/grammar_model.py
import sqlite3
from datetime import datetime
from utils.logger import get_logger
from .database import Database

logger = get_logger(__name__)

class GrammarModel:
    """
    Provides CRUD operations for the 'grammar' table.
    """
    def __init__(self, db: Database):
        self.db = db

    def add_grammar(self, session_id, phrase_structure, explanation="", resource_link=None):
        """
        Insert a new grammar record.
        """
        try:
            cursor = self.db.conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = """
                INSERT INTO grammar
                (session_id, phrase_structure, explanation, resource_link, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(sql, (session_id, phrase_structure, explanation, resource_link, timestamp))
            grammar_id = cursor.lastrowid
            self.db.conn.commit()
            logger.info(f"Added grammar ID={grammar_id} for session={session_id}.")
            return grammar_id
        except sqlite3.Error as e:
            logger.error(f"Error adding grammar: {e}")
            return None

    def get_grammar_for_session(self, session_id):
        """
        Fetch grammar entries for a specific session.
        """
        try:
            cursor = self.db.conn.cursor()
            sql = """
                SELECT * FROM grammar
                WHERE session_id = ?
                ORDER BY grammar_id
            """
            cursor.execute(sql, (session_id,))
            rows = cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            logger.error(f"Error fetching grammar for session {session_id}: {e}")
            return []

    def delete_grammar(self, grammar_id):
        """
        Remove a grammar record.
        """
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("DELETE FROM grammar WHERE grammar_id = ?", (grammar_id,))
            self.db.conn.commit()
            logger.info(f"Deleted grammar ID={grammar_id}")
            return cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"Error deleting grammar: {e}")
            return 0
