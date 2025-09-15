"""
Database Manager - Handles database connections, migrations, and lifecycle management.
"""

import os
import logging
import json
from typing import Dict, Any, Optional, List, Type
from pathlib import Path
from datetime import datetime
import hashlib

from .storage_backend import StorageBackend, JSONBackend, SQLiteBackend, PostgreSQLBackend
from .exceptions import DatabaseError, MigrationError, ConfigurationError


class DatabaseManager:
    """
    Manages database connections, migrations, and configuration for multiple storage backends.
    """
    
    SUPPORTED_BACKENDS = {
        'json': JSONBackend,
        'sqlite': SQLiteBackend,  
        'postgresql': PostgreSQLBackend
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the database manager.
        
        Args:
            config: Database configuration dictionary
        """
        self.config = config
        self.backend_type = config.get('backend', 'sqlite').lower()
        self.connection_string = config.get('connection_string', '')
        self.migrations_path = Path(config.get('migrations_path', 'src/persistence/migrations'))
        self.logger = logging.getLogger(__name__)
        
        # Initialize backend
        self.backend: Optional[StorageBackend] = None
        self._schema_version = None
        self._migration_lock = False
        
        # Ensure migrations directory exists
        self.migrations_path.mkdir(parents=True, exist_ok=True)
        
    def initialize(self) -> None:
        """Initialize the database backend and run migrations."""
        try:
            # Create backend instance
            backend_class = self.SUPPORTED_BACKENDS.get(self.backend_type)
            if not backend_class:
                raise ConfigurationError(f"Unsupported backend: {self.backend_type}")
                
            self.backend = backend_class(self.config)
            
            # Initialize backend
            self.backend.initialize()
            
            # Run migrations
            self.run_migrations()
            
            self.logger.info(f"Database initialized with {self.backend_type} backend")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {str(e)}")
            raise DatabaseError(f"Database initialization failed: {str(e)}")
    
    def get_backend(self) -> StorageBackend:
        """Get the active storage backend."""
        if not self.backend:
            raise DatabaseError("Database not initialized. Call initialize() first.")
        return self.backend
    
    def close(self) -> None:
        """Close database connections and cleanup resources."""
        if self.backend:
            self.backend.close()
            self.logger.info("Database connections closed")
    
    def run_migrations(self) -> None:
        """Run pending database migrations."""
        if self._migration_lock:
            self.logger.warning("Migration already in progress, skipping")
            return
            
        try:
            self._migration_lock = True
            
            # Get current schema version
            current_version = self._get_schema_version()
            
            # Get available migrations
            migrations = self._get_available_migrations()
            
            # Filter migrations that need to be applied
            pending_migrations = [
                m for m in migrations 
                if m['version'] > current_version
            ]
            
            if not pending_migrations:
                self.logger.info("No pending migrations")
                return
                
            self.logger.info(f"Running {len(pending_migrations)} pending migrations")
            
            # Apply each migration in order
            for migration in sorted(pending_migrations, key=lambda x: x['version']):
                self._apply_migration(migration)
                
        except Exception as e:
            self.logger.error(f"Migration failed: {str(e)}")
            raise MigrationError(f"Migration failed: {str(e)}")
        finally:
            self._migration_lock = False
    
    def create_migration(self, name: str, description: str = "") -> Path:
        """
        Create a new migration file.
        
        Args:
            name: Migration name
            description: Migration description
            
        Returns:
            Path to the created migration file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.py"
        migration_file = self.migrations_path / filename
        
        template = f'''"""
Migration: {name}
Description: {description}
Created: {datetime.now().isoformat()}
"""

from typing import Dict, Any
from ..storage_backend import StorageBackend


def up(backend: StorageBackend, config: Dict[str, Any]) -> None:
    """Apply the migration."""
    # TODO: Implement migration logic
    pass


def down(backend: StorageBackend, config: Dict[str, Any]) -> None:
    """Rollback the migration.""" 
    # TODO: Implement rollback logic
    pass


# Migration metadata
VERSION = {int(timestamp)}
DESCRIPTION = "{description}"
DEPENDENCIES = []  # List of migration versions this depends on
'''
        
        with open(migration_file, 'w') as f:
            f.write(template)
            
        self.logger.info(f"Created migration: {migration_file}")
        return migration_file
    
    def backup_database(self, backup_path: Optional[Path] = None) -> Path:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Optional backup file path
            
        Returns:
            Path to the backup file
        """
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = Path(f"backup_{self.backend_type}_{timestamp}.json")
            
        try:
            backup_data = {
                'backend_type': self.backend_type,
                'schema_version': self._get_schema_version(),
                'created_at': datetime.now().isoformat(),
                'data': self.backend.export_data() if self.backend else {}
            }
            
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
                
            self.logger.info(f"Database backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Backup failed: {str(e)}")
            raise DatabaseError(f"Backup failed: {str(e)}")
    
    def restore_database(self, backup_path: Path, force: bool = False) -> None:
        """
        Restore database from backup.
        
        Args:
            backup_path: Path to backup file
            force: Force restore even if schema versions don't match
        """
        try:
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
                
            # Validate backup format
            required_fields = ['backend_type', 'schema_version', 'data']
            for field in required_fields:
                if field not in backup_data:
                    raise DatabaseError(f"Invalid backup format: missing {field}")
            
            # Check backend compatibility
            if backup_data['backend_type'] != self.backend_type and not force:
                raise DatabaseError(
                    f"Backend mismatch: backup is {backup_data['backend_type']}, "
                    f"current is {self.backend_type}. Use force=True to override."
                )
            
            # Check schema version compatibility  
            backup_version = backup_data['schema_version']
            current_version = self._get_schema_version()
            
            if backup_version != current_version and not force:
                raise DatabaseError(
                    f"Schema version mismatch: backup is {backup_version}, "
                    f"current is {current_version}. Use force=True to override."
                )
            
            # Restore data
            if self.backend:
                self.backend.import_data(backup_data['data'])
                
            self.logger.info(f"Database restored from: {backup_path}")
            
        except Exception as e:
            self.logger.error(f"Restore failed: {str(e)}")
            raise DatabaseError(f"Restore failed: {str(e)}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get database health status and metrics."""
        try:
            status = {
                'backend_type': self.backend_type,
                'initialized': self.backend is not None,
                'schema_version': self._get_schema_version(),
                'timestamp': datetime.now().isoformat()
            }
            
            if self.backend:
                status.update(self.backend.get_stats())
                
            return status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                'backend_type': self.backend_type,
                'initialized': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_schema_version(self) -> int:
        """Get current database schema version."""
        if self._schema_version is not None:
            return self._schema_version
            
        try:
            if not self.backend:
                return 0
                
            # Try to get version from backend
            version_data = self.backend.get('_schema_version')
            if version_data and 'version' in version_data:
                self._schema_version = int(version_data['version'])
            else:
                self._schema_version = 0
                
            return self._schema_version
            
        except Exception:
            # If we can't get version, assume it's 0 (initial state)
            self._schema_version = 0
            return 0
    
    def _set_schema_version(self, version: int) -> None:
        """Set the current schema version."""
        try:
            if self.backend:
                self.backend.set('_schema_version', {'version': version})
                self._schema_version = version
                
        except Exception as e:
            raise MigrationError(f"Failed to set schema version: {str(e)}")
    
    def _get_available_migrations(self) -> List[Dict[str, Any]]:
        """Get list of available migration files."""
        migrations = []
        
        for migration_file in self.migrations_path.glob("*.py"):
            if migration_file.name.startswith("__"):
                continue
                
            try:
                # Extract timestamp from filename
                timestamp_str = migration_file.stem.split('_')[0]
                version = int(timestamp_str)
                
                migrations.append({
                    'version': version,
                    'name': migration_file.stem,
                    'file': migration_file,
                    'hash': self._get_file_hash(migration_file)
                })
                
            except (ValueError, IndexError) as e:
                self.logger.warning(f"Invalid migration filename: {migration_file} - {e}")
                continue
                
        return migrations
    
    def _apply_migration(self, migration: Dict[str, Any]) -> None:
        """Apply a single migration."""
        migration_file = migration['file']
        
        try:
            self.logger.info(f"Applying migration: {migration['name']}")
            
            # Import migration module
            spec = __import__(f"importlib.util")
            spec = spec.util.spec_from_file_location(migration['name'], migration_file)
            module = spec.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Execute migration
            if hasattr(module, 'up'):
                module.up(self.backend, self.config)
            else:
                raise MigrationError(f"Migration {migration['name']} missing 'up' function")
            
            # Update schema version
            self._set_schema_version(migration['version'])
            
            # Record migration in history
            self._record_migration(migration)
            
            self.logger.info(f"Migration {migration['name']} applied successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to apply migration {migration['name']}: {str(e)}")
            raise MigrationError(f"Migration {migration['name']} failed: {str(e)}")
    
    def _record_migration(self, migration: Dict[str, Any]) -> None:
        """Record migration in migration history."""
        try:
            if not self.backend:
                return
                
            history_key = '_migration_history'
            history = self.backend.get(history_key) or {'migrations': []}
            
            migration_record = {
                'version': migration['version'],
                'name': migration['name'], 
                'hash': migration['hash'],
                'applied_at': datetime.now().isoformat()
            }
            
            history['migrations'].append(migration_record)
            self.backend.set(history_key, history)
            
        except Exception as e:
            self.logger.warning(f"Failed to record migration history: {str(e)}")
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()


class DatabaseConfig:
    """Helper class for database configuration management."""
    
    @staticmethod
    def from_env() -> Dict[str, Any]:
        """Load database configuration from environment variables."""
        return {
            'backend': os.getenv('DB_BACKEND', 'sqlite'),
            'connection_string': os.getenv('DB_CONNECTION_STRING', ''),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'cli_app'),
            'username': os.getenv('DB_USER', ''),
            'password': os.getenv('DB_PASSWORD', ''),
            'migrations_path': os.getenv('DB_MIGRATIONS_PATH', 'src/persistence/migrations'),
            'cache_size': int(os.getenv('DB_CACHE_SIZE', '100')),
            'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),
            'timeout': int(os.getenv('DB_TIMEOUT', '30'))
        }
    
    @staticmethod
    def from_file(config_path: Path) -> Dict[str, Any]:
        """Load database configuration from JSON file."""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def get_default() -> Dict[str, Any]:
        """Get default database configuration."""
        return {
            'backend': 'sqlite',
            'connection_string': 'data/app.db',
            'migrations_path': 'src/persistence/migrations',
            'cache_size': 100,
            'pool_size': 5,
            'timeout': 30,
            'backup_retention': 7  # days
        }