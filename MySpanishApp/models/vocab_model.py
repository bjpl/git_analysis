# File: models/vocab_model.py
import sqlite3
from datetime import datetime
from utils.logger import get_logger
from .database import Database

logger = get_logger(__name__)

class VocabModel:
    """
    Provides CRUD operations for the 'vocab' table 
    and the associated 'vocab_regionalisms'.
    """

    def __init__(self, db: Database):
        self.db = db

    def add_vocab(self, session_id, word_phrase, translation="", context_notes="", regionalisms=None):
        """
        Insert a new vocab record, plus any associated regionalisms.
        """
        if not session_id or not word_phrase:
            logger.error("Missing required fields: session_id, word_phrase")
            return None
            
        # Check if session exists
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT 1 FROM sessions WHERE session_id = ?", (session_id,))
        if not cursor.fetchone():
            logger.error(f"Session {session_id} does not exist")
            return None
            
        if regionalisms is None:
            regionalisms = []

        try:
            cursor = self.db.conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Insert into vocab
            sql_vocab = """
                INSERT INTO vocab 
                (session_id, word_phrase, translation, context_notes, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(sql_vocab, (session_id, word_phrase, translation, context_notes, timestamp))
            vocab_id = cursor.lastrowid

            # Insert regionalisms
            sql_reg = """
                INSERT INTO vocab_regionalisms (vocab_id, country_name)
                VALUES (?, ?)
            """
            for country in regionalisms:
                cursor.execute(sql_reg, (vocab_id, country))

            self.db.conn.commit()
            logger.info(f"Added vocab '{word_phrase}' with ID={vocab_id}, {len(regionalisms)} regionalisms.")
            return vocab_id
        except sqlite3.Error as e:
            logger.error(f"Error adding vocab: {e}")
            return None

    def get_vocab_for_session(self, session_id):
        """
        Fetch all vocab entries for a given session, 
        including associated regionalisms.
        """
        try:
            cursor = self.db.conn.cursor()
            sql_vocab = """
                SELECT v.*,
                       GROUP_CONCAT(r.country_name, ',') as countries
                FROM vocab v
                LEFT JOIN vocab_regionalisms r
                ON v.vocab_id = r.vocab_id
                WHERE v.session_id = ?
                GROUP BY v.vocab_id
                ORDER BY v.vocab_id
            """
            cursor.execute(sql_vocab, (session_id,))
            rows = cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            logger.error(f"Error fetching vocab for session {session_id}: {e}")
            return []

    def delete_vocab(self, vocab_id):
        """
        Delete vocab row + associated regionalisms.
        """
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("DELETE FROM vocab_regionalisms WHERE vocab_id = ?", (vocab_id,))
            cursor.execute("DELETE FROM vocab WHERE vocab_id = ?", (vocab_id,))
            self.db.conn.commit()
            logger.info(f"Deleted vocab ID={vocab_id}")
            return cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"Error deleting vocab: {e}")
            return 0
