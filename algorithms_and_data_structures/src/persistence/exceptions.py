"""
Persistence Layer Exceptions

Custom exception classes for the persistence layer.
"""


class PersistenceError(Exception):
    """Base exception for persistence layer errors."""
    pass


class DatabaseError(PersistenceError):
    """Database-related errors."""
    pass


class StorageError(PersistenceError):
    """Storage backend errors."""
    pass


class ConnectionError(StorageError):
    """Database connection errors.""" 
    pass


class QueryError(StorageError):
    """Query execution errors."""
    pass


class MigrationError(DatabaseError):
    """Migration-related errors."""
    pass


class ConfigurationError(PersistenceError):
    """Configuration-related errors."""
    pass


class ValidationError(PersistenceError):
    """Data validation errors."""
    pass


class CacheError(PersistenceError):
    """Cache-related errors."""
    pass


class RepositoryError(PersistenceError):
    """Repository operation errors."""
    pass


class TransactionError(PersistenceError):
    """Transaction-related errors."""
    pass