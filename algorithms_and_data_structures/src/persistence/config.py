"""
Configuration Management for Persistence Layer

Centralized configuration handling for database connections and persistence settings.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from .exceptions import ConfigurationError


@dataclass
class DatabaseConfig:
    """Database configuration dataclass."""
    
    backend: str = "sqlite"
    connection_string: str = "data/app.db"
    host: str = "localhost"
    port: int = 5432
    database: str = "cli_app"
    username: str = ""
    password: str = ""
    migrations_path: str = "src/persistence/migrations"
    cache_size: int = 100
    pool_size: int = 10
    timeout: int = 30
    backup_retention: int = 7
    auto_migrate: bool = True
    
    # Advanced settings
    connection_pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo_sql: bool = False
    
    # Performance settings
    enable_query_cache: bool = True
    query_cache_size: int = 1000
    enable_connection_pooling: bool = True
    
    # Security settings
    ssl_mode: str = "prefer"
    ssl_cert: str = ""
    ssl_key: str = ""
    ssl_ca: str = ""
    
    # Backup settings
    backup_enabled: bool = True
    backup_schedule: str = "daily"  # daily, weekly, monthly
    backup_path: str = "backups"
    
    # Monitoring settings
    enable_metrics: bool = True
    metrics_interval: int = 60  # seconds
    slow_query_threshold: float = 1.0  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'backend': self.backend,
            'connection_string': self.connection_string,
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'username': self.username,
            'password': self.password,
            'migrations_path': self.migrations_path,
            'cache_size': self.cache_size,
            'pool_size': self.pool_size,
            'timeout': self.timeout,
            'backup_retention': self.backup_retention,
            'auto_migrate': self.auto_migrate,
            'connection_pool_size': self.connection_pool_size,
            'max_overflow': self.max_overflow,
            'pool_timeout': self.pool_timeout,
            'pool_recycle': self.pool_recycle,
            'echo_sql': self.echo_sql,
            'enable_query_cache': self.enable_query_cache,
            'query_cache_size': self.query_cache_size,
            'enable_connection_pooling': self.enable_connection_pooling,
            'ssl_mode': self.ssl_mode,
            'ssl_cert': self.ssl_cert,
            'ssl_key': self.ssl_key,
            'ssl_ca': self.ssl_ca,
            'backup_enabled': self.backup_enabled,
            'backup_schedule': self.backup_schedule,
            'backup_path': self.backup_path,
            'enable_metrics': self.enable_metrics,
            'metrics_interval': self.metrics_interval,
            'slow_query_threshold': self.slow_query_threshold
        }


class ConfigurationManager:
    """Manages persistence layer configuration."""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file
        self._config: Optional[DatabaseConfig] = None
        self._environment_mapping = {
            # Database settings
            'DB_BACKEND': 'backend',
            'DB_CONNECTION_STRING': 'connection_string',
            'DB_HOST': 'host',
            'DB_PORT': 'port',
            'DB_NAME': 'database',
            'DB_USER': 'username',
            'DB_PASSWORD': 'password',
            'DB_MIGRATIONS_PATH': 'migrations_path',
            'DB_CACHE_SIZE': 'cache_size',
            'DB_POOL_SIZE': 'pool_size',
            'DB_TIMEOUT': 'timeout',
            'DB_BACKUP_RETENTION': 'backup_retention',
            'DB_AUTO_MIGRATE': 'auto_migrate',
            
            # Connection pool settings
            'DB_POOL_SIZE': 'connection_pool_size',
            'DB_MAX_OVERFLOW': 'max_overflow',
            'DB_POOL_TIMEOUT': 'pool_timeout',
            'DB_POOL_RECYCLE': 'pool_recycle',
            'DB_ECHO_SQL': 'echo_sql',
            
            # Performance settings
            'DB_ENABLE_QUERY_CACHE': 'enable_query_cache',
            'DB_QUERY_CACHE_SIZE': 'query_cache_size',
            'DB_ENABLE_CONNECTION_POOLING': 'enable_connection_pooling',
            
            # Security settings
            'DB_SSL_MODE': 'ssl_mode',
            'DB_SSL_CERT': 'ssl_cert',
            'DB_SSL_KEY': 'ssl_key',
            'DB_SSL_CA': 'ssl_ca',
            
            # Backup settings
            'DB_BACKUP_ENABLED': 'backup_enabled',
            'DB_BACKUP_SCHEDULE': 'backup_schedule',
            'DB_BACKUP_PATH': 'backup_path',
            
            # Monitoring settings
            'DB_ENABLE_METRICS': 'enable_metrics',
            'DB_METRICS_INTERVAL': 'metrics_interval',
            'DB_SLOW_QUERY_THRESHOLD': 'slow_query_threshold'
        }
    
    def load_config(self) -> DatabaseConfig:
        """Load configuration from various sources."""
        if self._config:
            return self._config
        
        # Start with default configuration
        config_dict = DatabaseConfig().to_dict()
        
        # Override with file configuration if available
        if self.config_file and self.config_file.exists():
            file_config = self._load_from_file(self.config_file)
            config_dict.update(file_config)
        
        # Override with environment variables
        env_config = self._load_from_environment()
        config_dict.update(env_config)
        
        # Validate and create config object
        self._validate_config(config_dict)
        self._config = DatabaseConfig(**config_dict)
        
        return self._config
    
    def save_config(self, config: DatabaseConfig, file_path: Optional[Path] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save
            file_path: Optional file path (uses default if not provided)
        """
        if not file_path:
            if not self.config_file:
                raise ConfigurationError("No configuration file path specified")
            file_path = self.config_file
        
        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dict and remove sensitive data for file storage
            config_dict = config.to_dict()
            sensitive_fields = ['password']
            
            file_config = {k: v for k, v in config_dict.items() if k not in sensitive_fields}
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(file_config, f, indent=2)
                
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {str(e)}")
    
    def get_connection_url(self, config: Optional[DatabaseConfig] = None) -> str:
        """
        Generate database connection URL.
        
        Args:
            config: Optional configuration (uses loaded config if not provided)
            
        Returns:
            Database connection URL
        """
        if not config:
            config = self.load_config()
        
        if config.backend == 'postgresql':
            if config.connection_string:
                return config.connection_string
            
            url = f"postgresql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
            
            # Add SSL parameters if configured
            params = []
            if config.ssl_mode != 'prefer':
                params.append(f"sslmode={config.ssl_mode}")
            if config.ssl_cert:
                params.append(f"sslcert={config.ssl_cert}")
            if config.ssl_key:
                params.append(f"sslkey={config.ssl_key}")
            if config.ssl_ca:
                params.append(f"sslrootcert={config.ssl_ca}")
            
            if params:
                url += "?" + "&".join(params)
                
            return url
            
        elif config.backend == 'sqlite':
            return config.connection_string
            
        elif config.backend == 'json':
            return config.connection_string
            
        else:
            raise ConfigurationError(f"Unsupported backend: {config.backend}")
    
    def _load_from_file(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration file {file_path}: {str(e)}")
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        
        for env_var, config_key in self._environment_mapping.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Type conversion based on config key
                if config_key in ['port', 'cache_size', 'pool_size', 'timeout', 'backup_retention',
                                 'connection_pool_size', 'max_overflow', 'pool_timeout', 'pool_recycle',
                                 'query_cache_size', 'metrics_interval']:
                    config[config_key] = int(env_value)
                elif config_key in ['auto_migrate', 'echo_sql', 'enable_query_cache', 
                                   'enable_connection_pooling', 'backup_enabled', 'enable_metrics']:
                    config[config_key] = env_value.lower() in ('true', '1', 'yes', 'on')
                elif config_key in ['slow_query_threshold']:
                    config[config_key] = float(env_value)
                else:
                    config[config_key] = env_value
        
        return config
    
    def _validate_config(self, config_dict: Dict[str, Any]) -> None:
        """Validate configuration values."""
        backend = config_dict.get('backend', 'sqlite')
        
        # Validate backend
        valid_backends = ['sqlite', 'postgresql', 'json']
        if backend not in valid_backends:
            raise ConfigurationError(f"Invalid backend '{backend}'. Must be one of: {valid_backends}")
        
        # Validate required fields for PostgreSQL
        if backend == 'postgresql':
            required_fields = ['host', 'port', 'database']
            for field in required_fields:
                if not config_dict.get(field):
                    raise ConfigurationError(f"PostgreSQL backend requires '{field}' configuration")
        
        # Validate numeric values
        numeric_fields = {
            'port': (1, 65535),
            'cache_size': (1, 10000),
            'pool_size': (1, 100),
            'timeout': (1, 300),
            'backup_retention': (1, 365),
            'connection_pool_size': (1, 100),
            'max_overflow': (0, 100),
            'pool_timeout': (1, 300),
            'pool_recycle': (60, 86400),
            'query_cache_size': (1, 100000),
            'metrics_interval': (1, 3600),
        }
        
        for field, (min_val, max_val) in numeric_fields.items():
            value = config_dict.get(field)
            if value is not None and not (min_val <= value <= max_val):
                raise ConfigurationError(f"'{field}' must be between {min_val} and {max_val}")
        
        # Validate float values
        slow_threshold = config_dict.get('slow_query_threshold')
        if slow_threshold is not None and not (0.1 <= slow_threshold <= 60.0):
            raise ConfigurationError("'slow_query_threshold' must be between 0.1 and 60.0 seconds")
        
        # Validate SSL mode
        ssl_mode = config_dict.get('ssl_mode', 'prefer')
        valid_ssl_modes = ['disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full']
        if ssl_mode not in valid_ssl_modes:
            raise ConfigurationError(f"Invalid SSL mode '{ssl_mode}'. Must be one of: {valid_ssl_modes}")
        
        # Validate backup schedule
        backup_schedule = config_dict.get('backup_schedule', 'daily')
        valid_schedules = ['hourly', 'daily', 'weekly', 'monthly']
        if backup_schedule not in valid_schedules:
            raise ConfigurationError(f"Invalid backup schedule '{backup_schedule}'. Must be one of: {valid_schedules}")
    
    def get_environment_template(self) -> str:
        """Generate environment variable template."""
        template = "# Database Configuration Environment Variables\n\n"
        
        sections = {
            "Basic Database Settings": [
                ('DB_BACKEND', 'sqlite', 'Database backend (sqlite, postgresql, json)'),
                ('DB_CONNECTION_STRING', 'data/app.db', 'Connection string or file path'),
                ('DB_HOST', 'localhost', 'Database host (PostgreSQL)'),
                ('DB_PORT', '5432', 'Database port (PostgreSQL)'),
                ('DB_NAME', 'cli_app', 'Database name (PostgreSQL)'),
                ('DB_USER', '', 'Database username (PostgreSQL)'),
                ('DB_PASSWORD', '', 'Database password (PostgreSQL)'),
            ],
            "Performance Settings": [
                ('DB_CACHE_SIZE', '100', 'Cache size'),
                ('DB_POOL_SIZE', '10', 'Connection pool size'),
                ('DB_TIMEOUT', '30', 'Connection timeout (seconds)'),
                ('DB_ENABLE_QUERY_CACHE', 'true', 'Enable query caching'),
                ('DB_QUERY_CACHE_SIZE', '1000', 'Query cache size'),
            ],
            "Backup Settings": [
                ('DB_BACKUP_ENABLED', 'true', 'Enable automatic backups'),
                ('DB_BACKUP_SCHEDULE', 'daily', 'Backup schedule (hourly, daily, weekly, monthly)'),
                ('DB_BACKUP_PATH', 'backups', 'Backup directory path'),
                ('DB_BACKUP_RETENTION', '7', 'Backup retention days'),
            ],
            "Security Settings": [
                ('DB_SSL_MODE', 'prefer', 'SSL mode (disable, allow, prefer, require, verify-ca, verify-full)'),
                ('DB_SSL_CERT', '', 'SSL certificate file path'),
                ('DB_SSL_KEY', '', 'SSL key file path'),
                ('DB_SSL_CA', '', 'SSL CA certificate file path'),
            ],
            "Development Settings": [
                ('DB_AUTO_MIGRATE', 'true', 'Run migrations automatically'),
                ('DB_ECHO_SQL', 'false', 'Log SQL queries'),
                ('DB_ENABLE_METRICS', 'true', 'Enable performance metrics'),
                ('DB_SLOW_QUERY_THRESHOLD', '1.0', 'Slow query threshold (seconds)'),
            ]
        }
        
        for section, variables in sections.items():
            template += f"# {section}\n"
            for var, default, description in variables:
                template += f"# {description}\n"
                template += f"{var}={default}\n\n"
        
        return template


# Global configuration manager instance
config_manager = ConfigurationManager()


def get_default_config() -> DatabaseConfig:
    """Get default database configuration."""
    return DatabaseConfig()


def load_config_from_file(file_path: Path) -> DatabaseConfig:
    """Load configuration from specific file."""
    manager = ConfigurationManager(file_path)
    return manager.load_config()


def create_config_template(output_path: Path) -> None:
    """Create configuration file template."""
    config = get_default_config()
    manager = ConfigurationManager()
    manager.save_config(config, output_path)


def create_env_template(output_path: Path) -> None:
    """Create environment variables template file."""
    manager = ConfigurationManager()
    template = manager.get_environment_template()
    
    with open(output_path, 'w') as f:
        f.write(template)