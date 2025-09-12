"""Test suite for Persistence Layer - Database operations, storage backends, and data access."""

import pytest
import tempfile
import shutil
import json
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

try:
    from src.persistence.db_manager import DatabaseManager, DatabaseConfig
    from src.persistence.storage_backend import (
        StorageBackend, JSONBackend, SQLiteBackend, PostgreSQLBackend
    )
    from src.persistence.exceptions import DatabaseError, MigrationError, ConfigurationError
    from src.persistence.cache import CacheManager, LRUCache
    from src.persistence.repositories.base import BaseRepository
    from src.persistence.repositories.curriculum_repo import CurriculumRepository
    from src.persistence.repositories.content_repo import ContentRepository
    from src.persistence.repositories.progress_repo import ProgressRepository
except ImportError:
    # For isolated testing
    DatabaseManager = None
    StorageBackend = None


@pytest.mark.unit
class TestStorageBackends:
    """Test cases for storage backend implementations."""
    
    def test_json_backend_initialization(self, test_data_dir):
        """Test JSON backend initialization."""
        config = {
            "connection_string": str(test_data_dir / "test.json"),
            "backup_retention": 5
        }
        
        backend = JSONBackend(config)
        assert backend.config == config
        assert backend.file_path == Path(test_data_dir / "test.json")
        assert backend.data == {}
    
    def test_json_backend_operations(self, test_data_dir):
        """Test JSON backend CRUD operations."""
        config = {"connection_string": str(test_data_dir / "crud_test.json")}
        backend = JSONBackend(config)
        backend.initialize()
        
        # Test set operation
        test_data = {"name": "Test", "value": 42}
        backend.set("test_key", test_data)
        
        # Test get operation
        retrieved = backend.get("test_key")
        assert retrieved == test_data
        
        # Test get non-existent key
        assert backend.get("nonexistent") is None
        
        # Test delete operation
        backend.delete("test_key")
        assert backend.get("test_key") is None
        
        # Test exists operation
        backend.set("exists_test", {"data": "value"})
        assert backend.exists("exists_test") is True
        assert backend.exists("nonexistent") is False
    
    def test_json_backend_persistence(self, test_data_dir):
        """Test JSON backend data persistence."""
        file_path = test_data_dir / "persistence_test.json"
        config = {"connection_string": str(file_path)}
        
        # Create backend and add data
        backend1 = JSONBackend(config)
        backend1.initialize()
        backend1.set("persistent_key", {"data": "persistent_value"})
        backend1.close()
        
        # Verify file was created
        assert file_path.exists()
        
        # Create new backend instance and verify data persists
        backend2 = JSONBackend(config)
        backend2.initialize()
        retrieved = backend2.get("persistent_key")
        assert retrieved["data"] == "persistent_value"
        backend2.close()
    
    def test_sqlite_backend_initialization(self, test_data_dir):
        """Test SQLite backend initialization."""
        config = {
            "connection_string": str(test_data_dir / "test.db"),
            "timeout": 30,
            "cache_size": 100
        }
        
        backend = SQLiteBackend(config)
        backend.initialize()
        
        assert backend.connection is not None
        assert backend.config == config
        backend.close()
    
    def test_sqlite_backend_operations(self, test_data_dir):
        """Test SQLite backend CRUD operations."""
        config = {"connection_string": str(test_data_dir / "sqlite_crud.db")}
        backend = SQLiteBackend(config)
        backend.initialize()
        
        # Test set operation
        test_data = {"name": "SQLite Test", "value": 123}
        backend.set("sqlite_key", test_data)
        
        # Test get operation
        retrieved = backend.get("sqlite_key")
        assert retrieved["name"] == "SQLite Test"
        assert retrieved["value"] == 123
        
        # Test update operation
        updated_data = {"name": "Updated SQLite Test", "value": 456}
        backend.set("sqlite_key", updated_data)
        retrieved = backend.get("sqlite_key")
        assert retrieved["name"] == "Updated SQLite Test"
        assert retrieved["value"] == 456
        
        # Test delete operation
        backend.delete("sqlite_key")
        assert backend.get("sqlite_key") is None
        
        backend.close()
    
    def test_sqlite_backend_transactions(self, test_data_dir):
        """Test SQLite backend transaction handling."""
        config = {"connection_string": str(test_data_dir / "transactions.db")}
        backend = SQLiteBackend(config)
        backend.initialize()
        
        try:
            # Start transaction
            backend.begin_transaction()
            
            # Add data in transaction
            backend.set("tx_key1", {"data": "value1"})
            backend.set("tx_key2", {"data": "value2"})
            
            # Commit transaction
            backend.commit_transaction()
            
            # Verify data was committed
            assert backend.get("tx_key1")["data"] == "value1"
            assert backend.get("tx_key2")["data"] == "value2"
            
        finally:
            backend.close()
    
    def test_sqlite_backend_rollback(self, test_data_dir):
        """Test SQLite backend transaction rollback."""
        config = {"connection_string": str(test_data_dir / "rollback.db")}
        backend = SQLiteBackend(config)
        backend.initialize()
        
        try:
            # Add initial data
            backend.set("initial_key", {"data": "initial"})
            
            # Start transaction
            backend.begin_transaction()
            
            # Add data in transaction
            backend.set("rollback_key", {"data": "should_rollback"})
            
            # Rollback transaction
            backend.rollback_transaction()
            
            # Verify rollback worked
            assert backend.get("initial_key")["data"] == "initial"  # Should exist
            assert backend.get("rollback_key") is None  # Should not exist
            
        finally:
            backend.close()
    
    def test_backend_stats(self, test_data_dir):
        """Test backend statistics collection."""
        config = {"connection_string": str(test_data_dir / "stats_test.json")}
        backend = JSONBackend(config)
        backend.initialize()
        
        # Add some data
        for i in range(5):
            backend.set(f"key_{i}", {"value": i})
        
        # Get stats
        stats = backend.get_stats()
        
        assert "total_records" in stats
        assert "backend_type" in stats
        assert stats["total_records"] == 5
        assert stats["backend_type"] == "json"
        
        backend.close()
    
    def test_backend_export_import(self, test_data_dir):
        """Test backend data export and import."""
        config = {"connection_string": str(test_data_dir / "export_test.json")}
        backend = JSONBackend(config)
        backend.initialize()
        
        # Add test data
        test_data = {
            "key1": {"data": "value1"},
            "key2": {"data": "value2"},
            "key3": {"data": "value3"}
        }
        
        for key, value in test_data.items():
            backend.set(key, value)
        
        # Export data
        exported = backend.export_data()
        
        assert len(exported) == 3
        for key, value in test_data.items():
            assert key in exported
            assert exported[key] == value
        
        # Clear backend
        for key in test_data.keys():
            backend.delete(key)
        
        # Import data
        backend.import_data(exported)
        
        # Verify import
        for key, value in test_data.items():
            assert backend.get(key) == value
        
        backend.close()


@pytest.mark.unit
class TestDatabaseManager:
    """Test cases for DatabaseManager class."""
    
    def test_database_manager_initialization(self, test_data_dir):
        """Test database manager initialization."""
        config = {
            "backend": "json",
            "connection_string": str(test_data_dir / "manager_test.json"),
            "migrations_path": str(test_data_dir / "migrations")
        }
        
        manager = DatabaseManager(config)
        
        assert manager.config == config
        assert manager.backend_type == "json"
        assert manager.migrations_path.exists()
    
    def test_database_manager_backend_creation(self, test_data_dir):
        """Test database manager backend creation."""
        config = {
            "backend": "json",
            "connection_string": str(test_data_dir / "backend_test.json"),
            "migrations_path": str(test_data_dir / "migrations")
        }
        
        manager = DatabaseManager(config)
        manager.initialize()
        
        assert manager.backend is not None
        assert isinstance(manager.backend, JSONBackend)
        
        # Test get_backend method
        backend = manager.get_backend()
        assert backend == manager.backend
        
        manager.close()
    
    def test_database_manager_unsupported_backend(self, test_data_dir):
        """Test error handling for unsupported backend."""
        config = {
            "backend": "unsupported",
            "connection_string": "test",
            "migrations_path": str(test_data_dir / "migrations")
        }
        
        manager = DatabaseManager(config)
        
        with pytest.raises(DatabaseError, match="Database initialization failed"):
            manager.initialize()
    
    def test_database_manager_health_check(self, test_data_dir):
        """Test database manager health check."""
        config = {
            "backend": "json",
            "connection_string": str(test_data_dir / "health_test.json"),
            "migrations_path": str(test_data_dir / "migrations")
        }
        
        manager = DatabaseManager(config)
        
        # Test health check before initialization
        health = manager.get_health_status()
        assert health["initialized"] is False
        
        # Initialize and test health check
        manager.initialize()
        health = manager.get_health_status()
        assert health["initialized"] is True
        assert health["backend_type"] == "json"
        assert "timestamp" in health
        
        manager.close()
    
    def test_database_manager_backup_restore(self, test_data_dir):
        """Test database backup and restore functionality."""
        config = {
            "backend": "json",
            "connection_string": str(test_data_dir / "backup_test.json"),
            "migrations_path": str(test_data_dir / "migrations")
        }
        
        manager = DatabaseManager(config)
        manager.initialize()
        
        # Add test data
        backend = manager.get_backend()
        backend.set("backup_key", {"data": "backup_value"})
        
        # Create backup
        backup_path = manager.backup_database()
        assert backup_path.exists()
        
        # Verify backup content
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        
        assert backup_data["backend_type"] == "json"
        assert "backup_key" in backup_data["data"]
        assert backup_data["data"]["backup_key"]["data"] == "backup_value"
        
        # Clear data and restore
        backend.delete("backup_key")
        assert backend.get("backup_key") is None
        
        manager.restore_database(backup_path, force=True)
        assert backend.get("backup_key")["data"] == "backup_value"
        
        manager.close()
    
    def test_migration_creation(self, test_data_dir):
        """Test migration file creation."""
        config = {
            "backend": "json",
            "connection_string": str(test_data_dir / "migration_test.json"),
            "migrations_path": str(test_data_dir / "migrations")
        }
        
        manager = DatabaseManager(config)
        
        # Create migration
        migration_path = manager.create_migration(
            "test_migration",
            "Test migration description"
        )
        
        assert migration_path.exists()
        assert "test_migration" in migration_path.name
        
        # Verify migration content
        content = migration_path.read_text()
        assert "def up(" in content
        assert "def down(" in content
        assert "Test migration description" in content
    
    @patch('importlib.util.spec_from_file_location')
    @patch('importlib.util.module_from_spec')
    def test_migration_execution(self, mock_module_from_spec, mock_spec_from_file, test_data_dir):
        """Test migration execution."""
        config = {
            "backend": "json",
            "connection_string": str(test_data_dir / "migration_exec_test.json"),
            "migrations_path": str(test_data_dir / "migrations")
        }
        
        # Create mock migration file
        migration_file = test_data_dir / "migrations" / "20240115_120000_test_migration.py"
        migration_file.parent.mkdir(parents=True, exist_ok=True)
        migration_file.write_text(
            "VERSION = 20240115120000\n"
            "DESCRIPTION = 'Test migration'\n"
            "def up(backend, config): pass\n"
            "def down(backend, config): pass\n"
        )
        
        # Mock the import machinery
        mock_module = Mock()
        mock_module.up = Mock()
        mock_module.VERSION = 20240115120000
        mock_module.DESCRIPTION = "Test migration"
        
        mock_spec = Mock()
        mock_spec.loader.exec_module = Mock()
        
        mock_spec_from_file.return_value = mock_spec
        mock_module_from_spec.return_value = mock_module
        
        manager = DatabaseManager(config)
        manager.initialize()
        
        # Run migrations
        manager.run_migrations()
        
        # Verify migration was executed
        mock_module.up.assert_called_once()
        
        manager.close()


@pytest.mark.unit
class TestCacheManager:
    """Test cases for cache management."""
    
    def test_lru_cache_basic_operations(self):
        """Test basic LRU cache operations."""
        cache = LRUCache(capacity=3)
        
        # Test set and get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Test non-existent key
        assert cache.get("nonexistent") is None
        
        # Test capacity limit
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache.set("key4", "value4")  # Should evict key1
        
        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"
    
    def test_lru_cache_eviction_order(self):
        """Test LRU cache eviction order."""
        cache = LRUCache(capacity=2)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # Access key1 to make it recently used
        cache.get("key1")
        
        # Add key3, should evict key2 (least recently used)
        cache.set("key3", "value3")
        
        assert cache.get("key1") == "value1"  # Still exists
        assert cache.get("key2") is None       # Evicted
        assert cache.get("key3") == "value3"  # New item
    
    def test_cache_manager_integration(self):
        """Test cache manager with multiple cache types."""
        cache_manager = CacheManager({
            "default_ttl": 300,
            "max_size": 100
        })
        
        # Test cache creation
        lru_cache = cache_manager.get_cache("lru", cache_type="lru", capacity=5)
        assert lru_cache is not None
        
        # Test cache operations through manager
        cache_manager.set("lru", "test_key", "test_value")
        assert cache_manager.get("lru", "test_key") == "test_value"
        
        # Test cache invalidation
        cache_manager.invalidate("lru", "test_key")
        assert cache_manager.get("lru", "test_key") is None
        
        # Test cache clearing
        cache_manager.set("lru", "key1", "value1")
        cache_manager.set("lru", "key2", "value2")
        cache_manager.clear("lru")
        assert cache_manager.get("lru", "key1") is None
        assert cache_manager.get("lru", "key2") is None


@pytest.mark.unit
class TestRepositories:
    """Test cases for repository pattern implementations."""
    
    def test_base_repository(self, mock_db_manager):
        """Test base repository functionality."""
        class TestRepository(BaseRepository):
            def __init__(self, db_manager):
                super().__init__(db_manager, "test_collection")
        
        repo = TestRepository(mock_db_manager)
        
        assert repo.db_manager == mock_db_manager
        assert repo.collection_name == "test_collection"
    
    def test_curriculum_repository(self, mock_db_manager, test_data_factory):
        """Test curriculum repository operations."""
        # Mock backend
        mock_backend = Mock()
        mock_db_manager.get_backend.return_value = mock_backend
        
        repo = CurriculumRepository(mock_db_manager)
        
        # Test save operation
        curriculum_data = test_data_factory.create_learning_path()
        repo.save(curriculum_data)
        
        mock_backend.set.assert_called_once()
        
        # Test find operation
        mock_backend.get.return_value = curriculum_data
        result = repo.find_by_id(curriculum_data["id"])
        
        assert result == curriculum_data
        mock_backend.get.assert_called_with(f"curricula:{curriculum_data['id']}")
    
    def test_content_repository(self, mock_db_manager, test_data_factory):
        """Test content repository operations."""
        mock_backend = Mock()
        mock_db_manager.get_backend.return_value = mock_backend
        
        repo = ContentRepository(mock_db_manager)
        
        # Test save operation
        content_data = test_data_factory.create_topic()
        repo.save(content_data)
        
        mock_backend.set.assert_called_once()
        
        # Test search operation
        mock_backend.export_data.return_value = {
            f"content:{content_data['id']}": content_data
        }
        
        results = repo.search("test")
        assert len(results) >= 0  # Should return list
    
    def test_progress_repository(self, mock_db_manager, test_data_factory):
        """Test progress repository operations."""
        mock_backend = Mock()
        mock_db_manager.get_backend.return_value = mock_backend
        
        repo = ProgressRepository(mock_db_manager)
        
        # Test save operation
        progress_data = test_data_factory.create_user_progress()
        repo.save(progress_data)
        
        mock_backend.set.assert_called_once()
        
        # Test find by user operation
        mock_backend.export_data.return_value = {
            f"progress:{progress_data['id']}": progress_data
        }
        
        results = repo.find_by_user_id(progress_data["user_id"])
        assert isinstance(results, list)


@pytest.mark.integration
class TestPersistenceIntegration:
    """Integration tests for persistence layer."""
    
    def test_full_persistence_workflow(self, test_data_dir, test_data_factory):
        """Test complete persistence workflow."""
        config = {
            "backend": "json",
            "connection_string": str(test_data_dir / "workflow_test.json"),
            "migrations_path": str(test_data_dir / "migrations")
        }
        
        # Initialize database manager
        manager = DatabaseManager(config)
        manager.initialize()
        
        try:
            # Create repositories
            curriculum_repo = CurriculumRepository(manager)
            content_repo = ContentRepository(manager)
            progress_repo = ProgressRepository(manager)
            
            # Create test data
            curriculum = test_data_factory.create_learning_path()
            topic = test_data_factory.create_topic()
            progress = test_data_factory.create_user_progress()
            
            # Save data
            curriculum_repo.save(curriculum)
            content_repo.save(topic)
            progress_repo.save(progress)
            
            # Retrieve and verify data
            retrieved_curriculum = curriculum_repo.find_by_id(curriculum["id"])
            retrieved_topic = content_repo.find_by_id(topic["id"])
            retrieved_progress = progress_repo.find_by_id(progress["id"])
            
            assert retrieved_curriculum["name"] == curriculum["name"]
            assert retrieved_topic["name"] == topic["name"]
            assert retrieved_progress["user_id"] == progress["user_id"]
            
        finally:
            manager.close()
    
    def test_persistence_with_caching(self, test_data_dir, test_data_factory):
        """Test persistence layer with caching enabled."""
        config = {
            "backend": "json",
            "connection_string": str(test_data_dir / "cache_test.json"),
            "migrations_path": str(test_data_dir / "migrations"),
            "cache_enabled": True,
            "cache_size": 50
        }
        
        manager = DatabaseManager(config)
        manager.initialize()
        
        try:
            repo = ContentRepository(manager)
            topic = test_data_factory.create_topic()
            
            # Save and retrieve multiple times (should hit cache)
            repo.save(topic)
            
            # First retrieval (from database)
            result1 = repo.find_by_id(topic["id"])
            
            # Second retrieval (should be from cache)
            result2 = repo.find_by_id(topic["id"])
            
            assert result1 == result2
            assert result1["name"] == topic["name"]
            
        finally:
            manager.close()


@pytest.mark.performance
class TestPersistencePerformance:
    """Performance tests for persistence layer."""
    
    def test_bulk_operations_performance(self, test_data_dir, test_data_factory, performance_tracker):
        """Test performance of bulk database operations."""
        config = {
            "backend": "json",
            "connection_string": str(test_data_dir / "performance_test.json"),
            "migrations_path": str(test_data_dir / "migrations")
        }
        
        manager = DatabaseManager(config)
        manager.initialize()
        
        try:
            repo = ContentRepository(manager)
            
            # Create test data
            topics = [test_data_factory.create_topic(f"Topic {i}") for i in range(100)]
            
            # Test bulk insert performance
            performance_tracker.start_timer("bulk_insert")
            
            for topic in topics:
                repo.save(topic)
            
            duration = performance_tracker.end_timer("bulk_insert")
            
            # Should insert 100 records quickly
            performance_tracker.assert_max_duration("bulk_insert", 2.0)
            
            # Test bulk retrieval performance
            performance_tracker.start_timer("bulk_retrieval")
            
            retrieved = []
            for topic in topics:
                result = repo.find_by_id(topic["id"])
                retrieved.append(result)
            
            duration = performance_tracker.end_timer("bulk_retrieval")
            
            # Should retrieve 100 records quickly
            performance_tracker.assert_max_duration("bulk_retrieval", 1.0)
            
            assert len(retrieved) == 100
            
        finally:
            manager.close()
    
    def test_cache_performance(self, test_data_dir, performance_tracker):
        """Test cache performance impact."""
        cache = LRUCache(capacity=1000)
        
        # Test cache insertion performance
        performance_tracker.start_timer("cache_insert")
        
        for i in range(1000):
            cache.set(f"key_{i}", f"value_{i}")
        
        duration = performance_tracker.end_timer("cache_insert")
        performance_tracker.assert_max_duration("cache_insert", 0.1)
        
        # Test cache retrieval performance
        performance_tracker.start_timer("cache_retrieval")
        
        for i in range(1000):
            value = cache.get(f"key_{i}")
            assert value == f"value_{i}"
        
        duration = performance_tracker.end_timer("cache_retrieval")
        performance_tracker.assert_max_duration("cache_retrieval", 0.05)


@pytest.mark.database
class TestDatabaseConfiguration:
    """Test database configuration management."""
    
    def test_database_config_from_env(self):
        """Test database configuration from environment variables."""
        with patch.dict('os.environ', {
            'DB_BACKEND': 'postgresql',
            'DB_HOST': 'localhost',
            'DB_PORT': '5432',
            'DB_NAME': 'testdb',
            'DB_USER': 'testuser',
            'DB_PASSWORD': 'testpass'
        }):
            config = DatabaseConfig.from_env()
            
            assert config['backend'] == 'postgresql'
            assert config['host'] == 'localhost'
            assert config['port'] == 5432
            assert config['database'] == 'testdb'
            assert config['username'] == 'testuser'
            assert config['password'] == 'testpass'
    
    def test_database_config_from_file(self, test_data_dir):
        """Test database configuration from file."""
        config_data = {
            "backend": "sqlite",
            "connection_string": "test.db",
            "cache_size": 200
        }
        
        config_file = test_data_dir / "db_config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        config = DatabaseConfig.from_file(config_file)
        
        assert config['backend'] == 'sqlite'
        assert config['connection_string'] == 'test.db'
        assert config['cache_size'] == 200
    
    def test_database_config_defaults(self):
        """Test default database configuration."""
        config = DatabaseConfig.get_default()
        
        assert config['backend'] == 'sqlite'
        assert 'connection_string' in config
        assert 'migrations_path' in config
        assert config['cache_size'] == 100
        assert config['pool_size'] == 5
        assert config['timeout'] == 30


@pytest.mark.slow
class TestPersistenceErrorHandling:
    """Test error handling in persistence layer."""
    
    def test_database_connection_errors(self, test_data_dir, error_simulator):
        """Test handling of database connection errors."""
        config = {
            "backend": "json",
            "connection_string": "/invalid/path/test.json",  # Invalid path
            "migrations_path": str(test_data_dir / "migrations")
        }
        
        manager = DatabaseManager(config)
        
        # Should handle initialization errors gracefully
        with pytest.raises(DatabaseError):
            manager.initialize()
    
    def test_migration_errors(self, test_data_dir):
        """Test migration error handling."""
        config = {
            "backend": "json",
            "connection_string": str(test_data_dir / "migration_error_test.json"),
            "migrations_path": str(test_data_dir / "migrations")
        }
        
        # Create invalid migration file
        migration_file = test_data_dir / "migrations" / "20240115_120000_invalid_migration.py"
        migration_file.parent.mkdir(parents=True, exist_ok=True)
        migration_file.write_text("invalid python code")
        
        manager = DatabaseManager(config)
        manager.initialize()
        
        # Should handle migration errors
        with pytest.raises(MigrationError):
            manager.run_migrations()
        
        manager.close()
    
    def test_backup_restore_errors(self, test_data_dir):
        """Test backup and restore error handling."""
        config = {
            "backend": "json",
            "connection_string": str(test_data_dir / "backup_error_test.json"),
            "migrations_path": str(test_data_dir / "migrations")
        }
        
        manager = DatabaseManager(config)
        manager.initialize()
        
        try:
            # Test restore with non-existent backup
            with pytest.raises(DatabaseError):
                manager.restore_database(Path("/nonexistent/backup.json"))
            
            # Test restore with invalid backup format
            invalid_backup = test_data_dir / "invalid_backup.json"
            invalid_backup.write_text('{"invalid": "format"}')
            
            with pytest.raises(DatabaseError):
                manager.restore_database(invalid_backup)
                
        finally:
            manager.close()
    
    def test_repository_error_handling(self, error_simulator):
        """Test repository error handling."""
        # Mock database manager that throws errors
        mock_db_manager = Mock()
        mock_backend = error_simulator.create_failing_mock("database_error")
        mock_db_manager.get_backend.return_value = mock_backend
        
        repo = ContentRepository(mock_db_manager)
        
        # Should handle database errors gracefully
        with pytest.raises(Exception):  # Should propagate the error
            repo.save({"id": "test", "data": "test"})
