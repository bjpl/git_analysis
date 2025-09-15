"""
Abstract Storage Backend and Implementations

Provides pluggable storage backends for different persistence needs:
- JSONBackend: Simple file-based storage for development
- SQLiteBackend: Local database with SQL capabilities  
- PostgreSQLBackend: Production-ready database with advanced features
"""

import json
import sqlite3
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Iterator
from pathlib import Path
from datetime import datetime, timedelta
import threading
from contextlib import contextmanager
import time

try:
    import psycopg2
    import psycopg2.pool
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

from .exceptions import StorageError, ConnectionError, QueryError
from .cache import LRUCache


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize storage backend.
        
        Args:
            config: Backend configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.cache = LRUCache(config.get('cache_size', 100))
        self.is_initialized = False
        
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the storage backend."""
        pass
    
    @abstractmethod 
    def close(self) -> None:
        """Close connections and cleanup resources."""
        pass
    
    @abstractmethod
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a value by key."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Dict[str, Any]) -> None:
        """Store a value with the given key."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a value by key. Returns True if key existed."""
        pass
    
    @abstractmethod
    def list_keys(self, prefix: str = "") -> List[str]:
        """List all keys, optionally filtered by prefix."""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if a key exists."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all data."""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get backend statistics."""
        pass
    
    @abstractmethod
    def export_data(self) -> Dict[str, Any]:
        """Export all data for backup purposes."""
        pass
    
    @abstractmethod
    def import_data(self, data: Dict[str, Any]) -> None:
        """Import data from backup."""
        pass
    
    @contextmanager
    def transaction(self):
        """Context manager for transactions."""
        # Default implementation - subclasses should override for real transactions
        try:
            yield self
        except Exception:
            # In base class, we can't rollback, so just re-raise
            raise
    
    def batch_get(self, keys: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """Get multiple values in a batch operation."""
        result = {}
        for key in keys:
            result[key] = self.get(key)
        return result
    
    def batch_set(self, items: Dict[str, Dict[str, Any]]) -> None:
        """Set multiple key-value pairs in a batch operation."""
        for key, value in items.items():
            self.set(key, value)
    
    def batch_delete(self, keys: List[str]) -> Dict[str, bool]:
        """Delete multiple keys in a batch operation.""" 
        result = {}
        for key in keys:
            result[key] = self.delete(key)
        return result


class JSONBackend(StorageBackend):
    """Simple JSON file-based storage backend."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.file_path = Path(config.get('connection_string', 'data/storage.json'))
        self.data: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self.auto_save = config.get('auto_save', True)
        self.backup_count = config.get('backup_count', 3)
        
    def initialize(self) -> None:
        """Initialize JSON storage backend."""
        try:
            # Ensure directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing data
            if self.file_path.exists():
                with open(self.file_path, 'r') as f:
                    self.data = json.load(f)
            else:
                self.data = {}
                self._save()
            
            self.is_initialized = True
            self.logger.info(f"JSON backend initialized: {self.file_path}")
            
        except Exception as e:
            raise StorageError(f"Failed to initialize JSON backend: {str(e)}")
    
    def close(self) -> None:
        """Close JSON backend and save data."""
        if self.is_initialized:
            self._save()
            self.is_initialized = False
            self.logger.info("JSON backend closed")
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve value by key."""
        # Check cache first
        cached = self.cache.get(key)
        if cached is not None:
            return cached
            
        with self._lock:
            value = self.data.get(key)
            if value is not None:
                self.cache.put(key, value)
            return value
    
    def set(self, key: str, value: Dict[str, Any]) -> None:
        """Store value with key."""
        with self._lock:
            self.data[key] = value
            self.cache.put(key, value)
            
            if self.auto_save:
                self._save()
    
    def delete(self, key: str) -> bool:
        """Delete key."""
        with self._lock:
            existed = key in self.data
            if existed:
                del self.data[key]
                self.cache.delete(key)
                
                if self.auto_save:
                    self._save()
                    
            return existed
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List all keys with optional prefix filter."""
        with self._lock:
            if prefix:
                return [k for k in self.data.keys() if k.startswith(prefix)]
            return list(self.data.keys())
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        with self._lock:
            return key in self.data
    
    def clear(self) -> None:
        """Clear all data."""
        with self._lock:
            self.data.clear()
            self.cache.clear()
            
            if self.auto_save:
                self._save()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get backend statistics."""
        return {
            'type': 'json',
            'file_path': str(self.file_path),
            'file_size': self.file_path.stat().st_size if self.file_path.exists() else 0,
            'key_count': len(self.data),
            'cache_size': len(self.cache),
            'cache_hit_rate': self.cache.hit_rate,
            'is_initialized': self.is_initialized
        }
    
    def export_data(self) -> Dict[str, Any]:
        """Export all data."""
        with self._lock:
            return dict(self.data)
    
    def import_data(self, data: Dict[str, Any]) -> None:
        """Import data."""
        with self._lock:
            self.data = dict(data)
            self.cache.clear()
            
            if self.auto_save:
                self._save()
    
    def _save(self) -> None:
        """Save data to file with backup rotation."""
        try:
            # Create backup if file exists
            if self.file_path.exists() and self.backup_count > 0:
                self._rotate_backups()
            
            # Write to temporary file first, then rename (atomic operation)
            temp_path = self.file_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
            
            temp_path.replace(self.file_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save JSON data: {str(e)}")
            raise StorageError(f"Failed to save data: {str(e)}")
    
    def _rotate_backups(self) -> None:
        """Rotate backup files."""
        for i in range(self.backup_count - 1, 0, -1):
            old_backup = self.file_path.with_suffix(f'.bak{i}')
            new_backup = self.file_path.with_suffix(f'.bak{i + 1}')
            
            if old_backup.exists():
                if new_backup.exists():
                    new_backup.unlink()
                old_backup.rename(new_backup)
        
        # Create first backup
        backup_path = self.file_path.with_suffix('.bak1')
        if backup_path.exists():
            backup_path.unlink()
        self.file_path.rename(backup_path)


class SQLiteBackend(StorageBackend):
    """SQLite database storage backend."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.db_path = Path(config.get('connection_string', 'data/storage.db'))
        self.connection: Optional[sqlite3.Connection] = None
        self._lock = threading.RLock()
        self.timeout = config.get('timeout', 30)
        
    def initialize(self) -> None:
        """Initialize SQLite backend."""
        try:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            self.connection = sqlite3.connect(
                str(self.db_path),
                timeout=self.timeout,
                check_same_thread=False
            )
            
            # Enable WAL mode for better concurrency
            self.connection.execute("PRAGMA journal_mode=WAL")
            self.connection.execute("PRAGMA synchronous=NORMAL")
            self.connection.execute("PRAGMA cache_size=10000")
            self.connection.execute("PRAGMA temp_store=MEMORY")
            
            # Create tables
            self._create_tables()
            
            self.is_initialized = True
            self.logger.info(f"SQLite backend initialized: {self.db_path}")
            
        except Exception as e:
            raise StorageError(f"Failed to initialize SQLite backend: {str(e)}")
    
    def close(self) -> None:
        """Close SQLite connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.is_initialized = False
            self.logger.info("SQLite backend closed")
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve value by key."""
        # Check cache first
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        
        try:
            with self._lock:
                cursor = self.connection.execute(
                    "SELECT value FROM storage WHERE key = ?", (key,)
                )
                row = cursor.fetchone()
                
                if row:
                    value = json.loads(row[0])
                    self.cache.put(key, value)
                    return value
                    
                return None
                
        except Exception as e:
            raise QueryError(f"Failed to get key '{key}': {str(e)}")
    
    def set(self, key: str, value: Dict[str, Any]) -> None:
        """Store value with key."""
        try:
            with self._lock:
                self.connection.execute(
                    "INSERT OR REPLACE INTO storage (key, value, created_at, updated_at) VALUES (?, ?, ?, ?)",
                    (key, json.dumps(value, default=str), datetime.now(), datetime.now())
                )
                self.connection.commit()
                self.cache.put(key, value)
                
        except Exception as e:
            raise QueryError(f"Failed to set key '{key}': {str(e)}")
    
    def delete(self, key: str) -> bool:
        """Delete key."""
        try:
            with self._lock:
                cursor = self.connection.execute("DELETE FROM storage WHERE key = ?", (key,))
                self.connection.commit()
                self.cache.delete(key)
                return cursor.rowcount > 0
                
        except Exception as e:
            raise QueryError(f"Failed to delete key '{key}': {str(e)}")
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List keys with optional prefix filter."""
        try:
            with self._lock:
                if prefix:
                    cursor = self.connection.execute(
                        "SELECT key FROM storage WHERE key LIKE ?", (f"{prefix}%",)
                    )
                else:
                    cursor = self.connection.execute("SELECT key FROM storage")
                
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            raise QueryError(f"Failed to list keys: {str(e)}")
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            with self._lock:
                cursor = self.connection.execute(
                    "SELECT 1 FROM storage WHERE key = ? LIMIT 1", (key,)
                )
                return cursor.fetchone() is not None
                
        except Exception as e:
            raise QueryError(f"Failed to check key existence: {str(e)}")
    
    def clear(self) -> None:
        """Clear all data."""
        try:
            with self._lock:
                self.connection.execute("DELETE FROM storage")
                self.connection.commit()
                self.cache.clear()
                
        except Exception as e:
            raise QueryError(f"Failed to clear data: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get backend statistics."""
        try:
            with self._lock:
                # Get database size
                cursor = self.connection.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                db_size = cursor.fetchone()[0]
                
                # Get record count
                cursor = self.connection.execute("SELECT COUNT(*) FROM storage")
                key_count = cursor.fetchone()[0]
                
                return {
                    'type': 'sqlite',
                    'db_path': str(self.db_path),
                    'db_size': db_size,
                    'key_count': key_count,
                    'cache_size': len(self.cache),
                    'cache_hit_rate': self.cache.hit_rate,
                    'is_initialized': self.is_initialized
                }
                
        except Exception as e:
            return {'error': str(e), 'type': 'sqlite'}
    
    def export_data(self) -> Dict[str, Any]:
        """Export all data."""
        try:
            with self._lock:
                cursor = self.connection.execute("SELECT key, value FROM storage")
                return {row[0]: json.loads(row[1]) for row in cursor.fetchall()}
                
        except Exception as e:
            raise QueryError(f"Failed to export data: {str(e)}")
    
    def import_data(self, data: Dict[str, Any]) -> None:
        """Import data."""
        try:
            with self._lock:
                # Clear existing data
                self.connection.execute("DELETE FROM storage")
                
                # Insert new data
                for key, value in data.items():
                    self.connection.execute(
                        "INSERT INTO storage (key, value, created_at, updated_at) VALUES (?, ?, ?, ?)",
                        (key, json.dumps(value, default=str), datetime.now(), datetime.now())
                    )
                
                self.connection.commit()
                self.cache.clear()
                
        except Exception as e:
            raise QueryError(f"Failed to import data: {str(e)}")
    
    @contextmanager
    def transaction(self):
        """SQLite transaction context manager."""
        try:
            with self._lock:
                self.connection.execute("BEGIN")
                yield self
                self.connection.execute("COMMIT")
        except Exception:
            self.connection.execute("ROLLBACK")
            raise
    
    def _create_tables(self) -> None:
        """Create database tables."""
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS storage (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_storage_updated_at ON storage(updated_at);
            
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.connection.commit()


class PostgreSQLBackend(StorageBackend):
    """PostgreSQL database storage backend."""
    
    def __init__(self, config: Dict[str, Any]):
        if not POSTGRESQL_AVAILABLE:
            raise StorageError("PostgreSQL support requires psycopg2: pip install psycopg2-binary")
            
        super().__init__(config)
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 5432)
        self.database = config.get('database', 'cli_app')
        self.username = config.get('username', 'postgres')
        self.password = config.get('password', '')
        self.pool_size = config.get('pool_size', 10)
        self.timeout = config.get('timeout', 30)
        
        self.connection_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        
    def initialize(self) -> None:
        """Initialize PostgreSQL backend."""
        try:
            # Create connection pool
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=self.pool_size,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password,
                connect_timeout=self.timeout
            )
            
            # Test connection and create tables
            with self._get_connection() as conn:
                self._create_tables(conn)
            
            self.is_initialized = True
            self.logger.info(f"PostgreSQL backend initialized: {self.host}:{self.port}/{self.database}")
            
        except Exception as e:
            raise StorageError(f"Failed to initialize PostgreSQL backend: {str(e)}")
    
    def close(self) -> None:
        """Close PostgreSQL connections."""
        if self.connection_pool:
            self.connection_pool.closeall()
            self.connection_pool = None
            self.is_initialized = False
            self.logger.info("PostgreSQL backend closed")
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve value by key."""
        # Check cache first
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT value FROM storage WHERE key = %s", (key,))
                    row = cursor.fetchone()
                    
                    if row:
                        value = json.loads(row[0])
                        self.cache.put(key, value)
                        return value
                    
                    return None
                    
        except Exception as e:
            raise QueryError(f"Failed to get key '{key}': {str(e)}")
    
    def set(self, key: str, value: Dict[str, Any]) -> None:
        """Store value with key."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO storage (key, value, created_at, updated_at) 
                        VALUES (%s, %s, NOW(), NOW())
                        ON CONFLICT (key) DO UPDATE SET 
                        value = EXCLUDED.value, updated_at = NOW()
                        """,
                        (key, json.dumps(value, default=str))
                    )
                    conn.commit()
                    self.cache.put(key, value)
                    
        except Exception as e:
            raise QueryError(f"Failed to set key '{key}': {str(e)}")
    
    def delete(self, key: str) -> bool:
        """Delete key."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM storage WHERE key = %s", (key,))
                    conn.commit()
                    self.cache.delete(key)
                    return cursor.rowcount > 0
                    
        except Exception as e:
            raise QueryError(f"Failed to delete key '{key}': {str(e)}")
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List keys with optional prefix filter."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    if prefix:
                        cursor.execute("SELECT key FROM storage WHERE key LIKE %s", (f"{prefix}%",))
                    else:
                        cursor.execute("SELECT key FROM storage")
                    
                    return [row[0] for row in cursor.fetchall()]
                    
        except Exception as e:
            raise QueryError(f"Failed to list keys: {str(e)}")
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM storage WHERE key = %s LIMIT 1", (key,))
                    return cursor.fetchone() is not None
                    
        except Exception as e:
            raise QueryError(f"Failed to check key existence: {str(e)}")
    
    def clear(self) -> None:
        """Clear all data."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM storage")
                    conn.commit()
                    self.cache.clear()
                    
        except Exception as e:
            raise QueryError(f"Failed to clear data: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get backend statistics."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get table size
                    cursor.execute("SELECT pg_total_relation_size('storage')")
                    table_size = cursor.fetchone()[0]
                    
                    # Get record count
                    cursor.execute("SELECT COUNT(*) FROM storage")
                    key_count = cursor.fetchone()[0]
                    
                    return {
                        'type': 'postgresql',
                        'host': self.host,
                        'database': self.database,
                        'table_size': table_size,
                        'key_count': key_count,
                        'cache_size': len(self.cache),
                        'cache_hit_rate': self.cache.hit_rate,
                        'pool_size': self.pool_size,
                        'is_initialized': self.is_initialized
                    }
                    
        except Exception as e:
            return {'error': str(e), 'type': 'postgresql'}
    
    def export_data(self) -> Dict[str, Any]:
        """Export all data."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT key, value FROM storage")
                    return {row[0]: json.loads(row[1]) for row in cursor.fetchall()}
                    
        except Exception as e:
            raise QueryError(f"Failed to export data: {str(e)}")
    
    def import_data(self, data: Dict[str, Any]) -> None:
        """Import data."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Clear existing data
                    cursor.execute("DELETE FROM storage")
                    
                    # Insert new data in batch
                    if data:
                        values = [
                            (key, json.dumps(value, default=str))
                            for key, value in data.items()
                        ]
                        cursor.executemany(
                            "INSERT INTO storage (key, value, created_at, updated_at) VALUES (%s, %s, NOW(), NOW())",
                            values
                        )
                    
                    conn.commit()
                    self.cache.clear()
                    
        except Exception as e:
            raise QueryError(f"Failed to import data: {str(e)}")
    
    @contextmanager 
    def transaction(self):
        """PostgreSQL transaction context manager."""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            conn.autocommit = False
            yield conn
            conn.commit()
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.autocommit = True
                self.connection_pool.putconn(conn)
    
    @contextmanager
    def _get_connection(self):
        """Get connection from pool."""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            yield conn
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    def _create_tables(self, conn) -> None:
        """Create database tables."""
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS storage (
                    key TEXT PRIMARY KEY,
                    value JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
                
                CREATE INDEX IF NOT EXISTS idx_storage_updated_at ON storage(updated_at);
                CREATE INDEX IF NOT EXISTS idx_storage_value_gin ON storage USING gin(value);
                
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            conn.commit()