"""
Database Layer with SQLite and FTS5
PATTERN: Repository pattern with async operations
WHY: Separation of concerns and testability
"""
import aiosqlite
import json
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import asynccontextmanager

class Database:
    def __init__(self, db_path: str = "learning_captures.db"):
        self.db_path = db_path
        self._initialized = False
    
    async def initialize(self):
        """
        CONCEPT: Lazy initialization with FTS5 virtual table
        WHY: Efficient full-text search without external dependencies
        """
        if self._initialized:
            return
            
        async with aiosqlite.connect(self.db_path) as db:
            # Main captures table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS captures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_text TEXT NOT NULL,
                    agent_text TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            # FTS5 virtual table for search
            await db.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS captures_fts 
                USING fts5(
                    session_id UNINDEXED,
                    user_text,
                    agent_text,
                    content=captures,
                    content_rowid=id
                )
            """)
            
            # Triggers to keep FTS index in sync
            await db.execute("""
                CREATE TRIGGER IF NOT EXISTS captures_ai 
                AFTER INSERT ON captures BEGIN
                    INSERT INTO captures_fts(rowid, session_id, user_text, agent_text)
                    VALUES (new.id, new.session_id, new.user_text, new.agent_text);
                END
            """)
            
            await db.execute("""
                CREATE TRIGGER IF NOT EXISTS captures_ad 
                AFTER DELETE ON captures BEGIN
                    DELETE FROM captures_fts WHERE rowid = old.id;
                END
            """)
            
            await db.execute("""
                CREATE TRIGGER IF NOT EXISTS captures_au 
                AFTER UPDATE ON captures BEGIN
                    UPDATE captures_fts 
                    SET user_text = new.user_text, agent_text = new.agent_text
                    WHERE rowid = new.id;
                END
            """)
            
            # Index for session queries
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_timestamp 
                ON captures(session_id, timestamp DESC)
            """)
            
            await db.commit()
        
        self._initialized = True
    
    @asynccontextmanager
    async def get_connection(self):
        """Connection pool manager"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            yield db
    
    async def save_exchange(
        self, 
        session_id: str, 
        user_text: str, 
        agent_text: str,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        PATTERN: Async write with automatic FTS indexing
        """
        async with self.get_connection() as db:
            cursor = await db.execute(
                """
                INSERT INTO captures (session_id, user_text, agent_text, metadata)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, user_text, agent_text, json.dumps(metadata or {}))
            )
            await db.commit()
            return cursor.lastrowid
    
    async def get_session_history(
        self, 
        session_id: str, 
        limit: int = 5
    ) -> List[Dict]:
        """
        CONCEPT: Efficient windowed retrieval
        WHY: Only fetch what's needed for context
        """
        async with self.get_connection() as db:
            cursor = await db.execute(
                """
                SELECT id, timestamp, user_text, agent_text, metadata
                FROM captures
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (session_id, limit)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in reversed(rows)]
    
    async def search_captures(
        self, 
        query: str, 
        limit: int = 20
    ) -> List[Dict]:
        """
        PATTERN: FTS5 search with BM25 ranking
        WHY: Better relevance than simple LIKE queries
        """
        async with self.get_connection() as db:
            cursor = await db.execute(
                """
                SELECT 
                    c.id, c.session_id, c.timestamp, 
                    c.user_text, c.agent_text,
                    snippet(captures_fts, 1, '<mark>', '</mark>', '...', 32) as user_snippet,
                    snippet(captures_fts, 2, '<mark>', '</mark>', '...', 32) as agent_snippet
                FROM captures c
                JOIN captures_fts ON c.id = captures_fts.rowid
                WHERE captures_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (query, limit)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_stats(self) -> Dict:
        """Database statistics for monitoring"""
        async with self.get_connection() as db:
            cursor = await db.execute("""
                SELECT 
                    COUNT(*) as total_captures,
                    COUNT(DISTINCT session_id) as unique_sessions,
                    MAX(timestamp) as last_capture
                FROM captures
            """)
            return dict(await cursor.fetchone())

# Global database instance
db = Database()