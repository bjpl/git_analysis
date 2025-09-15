"""
Configuration Manager - Centralized configuration handling
Manages application settings from files, environment variables, and defaults.
"""

import json
import os
import toml
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import timedelta

from utils.logging_config import get_logger


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    path: str = "data/adaptive_learning.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class LearningConfig:
    """Learning system configuration settings."""
    default_difficulty: str = "intermediate"
    max_concurrent_topics: int = 3
    session_timeout_minutes: int = 60
    auto_save_interval_seconds: int = 30
    recommendation_count: int = 5
    quiz_question_count: int = 10
    practice_problem_count: int = 10
    adaptive_threshold: float = 0.7
    mastery_threshold: float = 0.85


@dataclass
class UIConfig:
    """User interface configuration settings."""
    theme: str = "default"
    color_scheme: str = "auto"  # auto, dark, light
    animation_speed: str = "normal"  # slow, normal, fast
    show_progress_bars: bool = True
    show_hints: bool = True
    auto_complete: bool = True
    terminal_width: Optional[int] = None


@dataclass
class MLConfig:
    """Machine learning configuration settings."""
    enable_ml_features: bool = True
    model_cache_dir: str = "models"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    similarity_threshold: float = 0.6
    recommendation_model: str = "collaborative_filtering"
    update_frequency_hours: int = 24


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    log_dir: str = "logs"
    max_file_size_mb: int = 10
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True
    enable_rich: bool = True


class ConfigManager:
    """
    Manages application configuration from multiple sources:
    1. Default values
    2. Configuration files (JSON, TOML, YAML)
    3. Environment variables
    4. Runtime overrides
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = get_logger(__name__)
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        
        # Load configuration in priority order
        self._load_default_config()
        self._load_file_config(config_path)
        self._load_environment_config()
        
        self.logger.info(f"Configuration loaded from: {self._get_config_sources()}")
    
    def _load_default_config(self):
        """Load default configuration values."""
        self.config = {
            'database': asdict(DatabaseConfig()),
            'learning': asdict(LearningConfig()),
            'ui': asdict(UIConfig()),
            'ml': asdict(MLConfig()),
            'logging': asdict(LoggingConfig()),
            
            # Additional default settings
            'app_name': 'Adaptive Learning System',
            'version': '1.0.0',
            'debug': False,
            'data_dir': 'data',
            'cache_dir': 'cache',
            'temp_dir': 'temp',
            'export_dir': 'exports',
            
            # Performance settings
            'performance': {
                'enable_caching': True,
                'cache_ttl_seconds': 1800,  # 30 minutes
                'max_cache_size_mb': 100,
                'enable_parallel_processing': True,
                'max_workers': 4,
            },
            
            # Security settings
            'security': {
                'enable_audit_logging': True,
                'password_min_length': 8,
                'session_timeout_minutes': 30,
                'max_login_attempts': 3,
                'lockout_duration_minutes': 15,
            },
            
            # Feature flags
            'features': {
                'enable_recommendations': True,
                'enable_analytics': True,
                'enable_export': True,
                'enable_social_features': False,
                'enable_gamification': True,
            },
            
            # Default user preferences
            'default_user_preferences': {
                'difficulty_preference': 'adaptive',
                'study_time_goal_minutes': 60,
                'daily_problem_goal': 5,
                'notification_enabled': True,
                'theme': 'dark',
                'language': 'en',
            }
        }
    
    def _load_file_config(self, config_path: Optional[str]):
        """Load configuration from file."""
        if not config_path:
            # Try default config file locations
            possible_paths = [
                'config.json',
                'config.toml', 
                'config.yaml',
                'config.yml',
                Path.home() / '.adaptive_learning' / 'config.json',
                Path('/etc/adaptive_learning/config.json'),
            ]
            
            for path in possible_paths:
                if Path(path).exists():
                    config_path = str(path)
                    break
        
        if not config_path:
            self.logger.info("No configuration file found, using defaults")
            return
        
        config_file = Path(config_path)
        if not config_file.exists():
            self.logger.warning(f"Configuration file not found: {config_path}")
            return
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix.lower() == '.json':
                    file_config = json.load(f)
                elif config_file.suffix.lower() == '.toml':
                    file_config = toml.load(f)
                elif config_file.suffix.lower() in ['.yaml', '.yml']:
                    file_config = yaml.safe_load(f)
                else:
                    self.logger.warning(f"Unsupported config file format: {config_file.suffix}")
                    return
            
            # Merge file config with defaults
            self._deep_merge(self.config, file_config)
            self.logger.info(f"Loaded configuration from: {config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load config file {config_path}: {str(e)}")
    
    def _load_environment_config(self):
        """Load configuration from environment variables."""
        env_prefix = 'ALS_'  # Adaptive Learning System prefix
        
        env_mapping = {
            # Database settings
            f'{env_prefix}DB_PATH': ('database', 'path'),
            f'{env_prefix}DB_ECHO': ('database', 'echo'),
            
            # Learning settings
            f'{env_prefix}DEFAULT_DIFFICULTY': ('learning', 'default_difficulty'),
            f'{env_prefix}SESSION_TIMEOUT': ('learning', 'session_timeout_minutes'),
            
            # UI settings
            f'{env_prefix}THEME': ('ui', 'theme'),
            f'{env_prefix}COLOR_SCHEME': ('ui', 'color_scheme'),
            
            # ML settings
            f'{env_prefix}ENABLE_ML': ('ml', 'enable_ml_features'),
            f'{env_prefix}MODEL_CACHE_DIR': ('ml', 'model_cache_dir'),
            
            # Logging settings
            f'{env_prefix}LOG_LEVEL': ('logging', 'level'),
            f'{env_prefix}LOG_DIR': ('logging', 'log_dir'),
            
            # General settings
            f'{env_prefix}DEBUG': ('debug',),
            f'{env_prefix}DATA_DIR': ('data_dir',),
        }
        
        for env_var, config_path in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string values to appropriate types
                value = self._convert_env_value(value)
                self._set_nested_config(config_path, value)
        
        self.logger.debug(f"Loaded environment variables with prefix: {env_prefix}")
    
    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Convert environment variable string to appropriate type."""
        # Boolean conversion
        if value.lower() in ('true', '1', 'yes', 'on'):
            return True
        elif value.lower() in ('false', '0', 'no', 'off'):
            return False
        
        # Numeric conversion
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _set_nested_config(self, path: tuple, value: Any):
        """Set nested configuration value."""
        config = self.config
        for key in path[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[path[-1]] = value
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]):
        """Deep merge two dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _get_config_sources(self) -> str:
        """Get string describing configuration sources."""
        sources = ["defaults"]
        
        if self.config_path and Path(self.config_path).exists():
            sources.append(f"file({self.config_path})")
        
        env_vars = [key for key in os.environ.keys() if key.startswith('ALS_')]
        if env_vars:
            sources.append(f"environment({len(env_vars)} vars)")
        
        return ", ".join(sources)
    
    def get_config(self) -> Dict[str, Any]:
        """Get complete configuration dictionary."""
        return self.config.copy()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key path.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'database.path')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """
        Set configuration value by key path.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.logger.debug(f"Set configuration: {key} = {value}")
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration as dataclass."""
        db_config = self.config.get('database', {})
        return DatabaseConfig(**db_config)
    
    def get_learning_config(self) -> LearningConfig:
        """Get learning configuration as dataclass."""
        learning_config = self.config.get('learning', {})
        return LearningConfig(**learning_config)
    
    def get_ui_config(self) -> UIConfig:
        """Get UI configuration as dataclass."""
        ui_config = self.config.get('ui', {})
        return UIConfig(**ui_config)
    
    def get_ml_config(self) -> MLConfig:
        """Get ML configuration as dataclass."""
        ml_config = self.config.get('ml', {})
        return MLConfig(**ml_config)
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration as dataclass."""
        logging_config = self.config.get('logging', {})
        return LoggingConfig(**logging_config)
    
    def save_config(self, output_path: Optional[str] = None, format: str = 'json'):
        """
        Save current configuration to file.
        
        Args:
            output_path: Output file path
            format: Output format ('json', 'toml', 'yaml')
        """
        if not output_path:
            output_path = f"config.{format}"
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                if format == 'json':
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                elif format == 'toml':
                    toml.dump(self.config, f)
                elif format in ['yaml', 'yml']:
                    yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
                else:
                    raise ValueError(f"Unsupported format: {format}")
            
            self.logger.info(f"Configuration saved to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save config to {output_path}: {str(e)}")
            raise
    
    def validate_config(self) -> Dict[str, list]:
        """
        Validate configuration and return any issues found.
        
        Returns:
            Dictionary with validation issues by category
        """
        issues = {
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # Validate database configuration
        db_path = Path(self.get('database.path'))
        if not db_path.parent.exists():
            issues['warnings'].append(f"Database directory does not exist: {db_path.parent}")
        
        # Validate directories
        required_dirs = ['data_dir', 'cache_dir', 'temp_dir', 'export_dir']
        for dir_key in required_dirs:
            dir_path = Path(self.get(dir_key))
            if not dir_path.exists():
                issues['info'].append(f"Directory will be created: {dir_path}")
        
        # Validate logging configuration
        log_level = self.get('logging.level', '').upper()
        if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            issues['errors'].append(f"Invalid log level: {log_level}")
        
        # Validate ML configuration
        if self.get('ml.enable_ml_features'):
            model_cache_dir = Path(self.get('ml.model_cache_dir'))
            if not model_cache_dir.exists():
                issues['info'].append(f"ML model cache directory will be created: {model_cache_dir}")
        
        # Validate numeric ranges
        numeric_validations = [
            ('learning.max_concurrent_topics', 1, 10),
            ('learning.session_timeout_minutes', 5, 480),
            ('learning.adaptive_threshold', 0.0, 1.0),
            ('learning.mastery_threshold', 0.0, 1.0),
            ('performance.max_workers', 1, 32),
        ]
        
        for key, min_val, max_val in numeric_validations:
            value = self.get(key)
            if value is not None and not (min_val <= value <= max_val):
                issues['warnings'].append(f"Value {key}={value} outside recommended range [{min_val}, {max_val}]")
        
        return issues
    
    def create_directories(self):
        """Create all configured directories if they don't exist."""
        directories = [
            self.get('data_dir'),
            self.get('cache_dir'),
            self.get('temp_dir'),
            self.get('export_dir'),
            self.get('logging.log_dir'),
            self.get('ml.model_cache_dir'),
        ]
        
        for directory in directories:
            if directory:
                dir_path = Path(directory)
                dir_path.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Ensured directory exists: {dir_path}")
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"ConfigManager(sources: {self._get_config_sources()}, keys: {len(self.config)})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"ConfigManager(config_path={self.config_path}, config_keys={list(self.config.keys())})"