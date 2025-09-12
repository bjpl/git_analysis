"""
Migration: initial_schema
Description: Create initial database schema and indexes
Created: 2025-09-11T22:58:00.000000
"""

from typing import Dict, Any
from ..storage_backend import StorageBackend, SQLiteBackend, PostgreSQLBackend


def up(backend: StorageBackend, config: Dict[str, Any]) -> None:
    """Apply the migration."""
    
    if isinstance(backend, SQLiteBackend):
        # SQLite-specific schema creation
        connection = backend.connection
        connection.executescript("""
            -- Enhanced storage table with metadata
            CREATE TABLE IF NOT EXISTS storage (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                entity_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                version INTEGER DEFAULT 1
            );
            
            -- Indexes for better performance
            CREATE INDEX IF NOT EXISTS idx_storage_entity_type ON storage(entity_type);
            CREATE INDEX IF NOT EXISTS idx_storage_created_at ON storage(created_at);
            CREATE INDEX IF NOT EXISTS idx_storage_updated_at ON storage(updated_at);
            
            -- Full-text search support for content
            CREATE VIRTUAL TABLE IF NOT EXISTS storage_fts USING fts5(
                key, 
                content,
                content='storage',
                content_rowid='rowid'
            );
            
            -- Triggers for FTS updates
            CREATE TRIGGER IF NOT EXISTS storage_fts_insert AFTER INSERT ON storage BEGIN
                INSERT INTO storage_fts(rowid, key, content) VALUES (new.rowid, new.key, new.value);
            END;
            
            CREATE TRIGGER IF NOT EXISTS storage_fts_delete AFTER DELETE ON storage BEGIN
                INSERT INTO storage_fts(storage_fts, rowid, key, content) VALUES('delete', old.rowid, old.key, old.value);
            END;
            
            CREATE TRIGGER IF NOT EXISTS storage_fts_update AFTER UPDATE ON storage BEGIN
                INSERT INTO storage_fts(storage_fts, rowid, key, content) VALUES('delete', old.rowid, old.key, old.value);
                INSERT INTO storage_fts(rowid, key, content) VALUES (new.rowid, new.key, new.value);
            END;
            
            -- Metadata table for schema versioning and system info
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- User sessions table for progress tracking
            CREATE TABLE IF NOT EXISTS user_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
            CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
            
            -- Analytics table for usage tracking
            CREATE TABLE IF NOT EXISTS analytics_events (
                id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                user_id TEXT,
                entity_type TEXT,
                entity_id TEXT,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_analytics_event_type ON analytics_events(event_type);
            CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics_events(user_id);
            CREATE INDEX IF NOT EXISTS idx_analytics_created_at ON analytics_events(created_at);
        """)
        
        connection.commit()
        
    elif isinstance(backend, PostgreSQLBackend):
        # PostgreSQL-specific schema creation
        with backend._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    -- Enhanced storage table with JSONB and advanced indexing
                    CREATE TABLE IF NOT EXISTS storage (
                        key TEXT PRIMARY KEY,
                        value JSONB NOT NULL,
                        entity_type TEXT,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW(),
                        version INTEGER DEFAULT 1
                    );
                    
                    -- Advanced indexes
                    CREATE INDEX IF NOT EXISTS idx_storage_entity_type ON storage(entity_type);
                    CREATE INDEX IF NOT EXISTS idx_storage_created_at ON storage(created_at);
                    CREATE INDEX IF NOT EXISTS idx_storage_updated_at ON storage(updated_at);
                    CREATE INDEX IF NOT EXISTS idx_storage_value_gin ON storage USING gin(value);
                    
                    -- Full-text search index
                    CREATE INDEX IF NOT EXISTS idx_storage_value_fts ON storage USING gin(to_tsvector('english', value));
                    
                    -- Partial indexes for common queries
                    CREATE INDEX IF NOT EXISTS idx_storage_curriculum ON storage(entity_type) WHERE entity_type = 'curriculum';
                    CREATE INDEX IF NOT EXISTS idx_storage_progress ON storage(entity_type) WHERE entity_type = 'user_progress';
                    
                    -- Metadata table
                    CREATE TABLE IF NOT EXISTS metadata (
                        key TEXT PRIMARY KEY,
                        value JSONB NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    );
                    
                    -- User sessions with JSON data
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        session_data JSONB NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        last_accessed_at TIMESTAMP DEFAULT NOW(),
                        expires_at TIMESTAMP
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
                    CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
                    CREATE INDEX IF NOT EXISTS idx_user_sessions_data ON user_sessions USING gin(session_data);
                    
                    -- Analytics with JSONB properties
                    CREATE TABLE IF NOT EXISTS analytics_events (
                        id TEXT PRIMARY KEY,
                        event_type TEXT NOT NULL,
                        user_id TEXT,
                        entity_type TEXT,
                        entity_id TEXT,
                        properties JSONB,
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_analytics_event_type ON analytics_events(event_type);
                    CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics_events(user_id);
                    CREATE INDEX IF NOT EXISTS idx_analytics_created_at ON analytics_events(created_at);
                    CREATE INDEX IF NOT EXISTS idx_analytics_properties ON analytics_events USING gin(properties);
                    
                    -- Performance optimization: Enable auto-vacuum
                    ALTER TABLE storage SET (autovacuum_enabled = true);
                    ALTER TABLE user_sessions SET (autovacuum_enabled = true);
                    ALTER TABLE analytics_events SET (autovacuum_enabled = true);
                """)
                
                conn.commit()


def down(backend: StorageBackend, config: Dict[str, Any]) -> None:
    """Rollback the migration."""
    
    if isinstance(backend, SQLiteBackend):
        connection = backend.connection
        connection.executescript("""
            -- Drop FTS triggers first
            DROP TRIGGER IF EXISTS storage_fts_insert;
            DROP TRIGGER IF EXISTS storage_fts_delete;
            DROP TRIGGER IF EXISTS storage_fts_update;
            
            -- Drop FTS table
            DROP TABLE IF EXISTS storage_fts;
            
            -- Drop other tables
            DROP TABLE IF EXISTS analytics_events;
            DROP TABLE IF EXISTS user_sessions;
            DROP TABLE IF EXISTS metadata;
            
            -- Reset storage table to basic structure
            CREATE TABLE storage_backup AS SELECT key, value, created_at, updated_at FROM storage;
            DROP TABLE storage;
            CREATE TABLE storage (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            INSERT INTO storage SELECT * FROM storage_backup;
            DROP TABLE storage_backup;
            
            CREATE INDEX idx_storage_updated_at ON storage(updated_at);
        """)
        
        connection.commit()
        
    elif isinstance(backend, PostgreSQLBackend):
        with backend._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    -- Drop additional tables
                    DROP TABLE IF EXISTS analytics_events;
                    DROP TABLE IF EXISTS user_sessions;
                    DROP TABLE IF EXISTS metadata;
                    
                    -- Reset storage table to basic structure
                    CREATE TABLE storage_backup AS SELECT key, value, created_at, updated_at FROM storage;
                    DROP TABLE storage;
                    CREATE TABLE storage (
                        key TEXT PRIMARY KEY,
                        value JSONB NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    );
                    INSERT INTO storage SELECT * FROM storage_backup;
                    DROP TABLE storage_backup;
                    
                    CREATE INDEX idx_storage_updated_at ON storage(updated_at);
                    CREATE INDEX idx_storage_value_gin ON storage USING gin(value);
                """)
                
                conn.commit()


# Migration metadata
VERSION = 20250911225800
DESCRIPTION = "Create initial database schema and indexes"
DEPENDENCIES = []  # List of migration versions this depends on