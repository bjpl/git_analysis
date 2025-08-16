# File: models/database.py
import sqlite3
import os
from utils.logger import get_logger
from config import DB_FILE

logger = get_logger(__name__)

class Database:
    """
    Manages the SQLite connection and provides methods 
    for initializing or querying the database.
    """

    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self.conn = None
        self.connect()

    def connect(self):
        """Create a connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # So we can use row keys
            logger.info(f"Connected to SQLite DB at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to DB: {e}")
            raise

    def init_db(self):
        """
        Create tables if they don't already exist.
        For now, we'll include sessions, vocab, grammar, etc.
        Expand as needed later.
        """
        try:
            cursor = self.conn.cursor()

            # Create TEACHERS table (simple example)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    region TEXT,
                    notes TEXT
                );
            """)

            # Create SESSIONS table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_id INTEGER,
                    session_date TEXT,
                    start_time TEXT,
                    duration TEXT,    -- e.g., "1h" or "30m"
                    status TEXT,      -- planned, completed, etc.
                    timestamp TEXT,   -- could be creation or update time
                    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
                );
            """)

            # Create VOCAB table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vocab (
                    vocab_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    word_phrase TEXT NOT NULL,
                    translation TEXT,
                    context_notes TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                );
            """)

            # Create VOCAB_REGIONALISMS linking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vocab_regionalisms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vocab_id INTEGER,
                    country_name TEXT,
                    FOREIGN KEY (vocab_id) REFERENCES vocab(vocab_id)
                );
            """)

            # Create GRAMMAR table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS grammar (
                    grammar_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    phrase_structure TEXT,
                    explanation TEXT,
                    resource_link TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                );
            """)

            # Create CHALLENGES table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS challenges (
                    challenge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    description TEXT,
                    type TEXT,  -- expression or comprehension
                    timestamp TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                );
            """)

            # Create COMFORT table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comfort (
                    comfort_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    description TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                );
            """)

            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON")
            
            self.conn.commit()
            logger.info("Database tables created or already exist.")
        except sqlite3.Error as e:
            logger.error(f"DB init failed: {e}")

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")
