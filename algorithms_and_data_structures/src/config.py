#!/usr/bin/env python3
"""
Configuration System - Settings and preferences management

This module provides:
- Configuration loading from files and environment
- Settings validation and defaults
- User preferences management
- Environment-specific configurations
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class OutputFormat(Enum):
    """Output format options"""
    TABLE = "table"
    JSON = "json"
    YAML = "yaml"
    CSV = "csv"
    PLAIN = "plain"


@dataclass
class UISettings:
    """User interface settings"""
    color_enabled: bool = True
    interactive_mode: bool = False
    pager_enabled: bool = True
    progress_bars: bool = True
    animations: bool = True
    theme: str = "default"
    output_format: OutputFormat = OutputFormat.TABLE
    

@dataclass
class DatabaseSettings:
    """Database configuration"""
    url: Optional[str] = None
    host: str = "localhost"
    port: int = 5432
    database: str = "curriculum"
    username: Optional[str] = None
    password: Optional[str] = None
    pool_size: int = 10
    timeout: int = 30
    ssl_enabled: bool = False
    

@dataclass
class APISettings:
    """API configuration"""
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    timeout: int = 30
    retries: int = 3
    rate_limit: int = 100
    

@dataclass
class LoggingSettings:
    """Logging configuration"""
    level: LogLevel = LogLevel.INFO
    file_enabled: bool = False
    file_path: Optional[str] = None
    max_file_size: str = "10MB"
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    

@dataclass
class PluginSettings:
    """Plugin system configuration"""
    enabled: bool = True
    auto_load: bool = True
    plugin_dirs: list = field(default_factory=lambda: ["~/.curriculum-cli/plugins", "./plugins"])
    disabled_plugins: list = field(default_factory=list)
    

@dataclass
class SecuritySettings:
    """Security configuration"""
    encryption_enabled: bool = True
    key_file: Optional[str] = None
    session_timeout: int = 3600
    max_login_attempts: int = 3
    

class CLIConfig:
    """Main configuration class"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """Initialize configuration
        
        Args:
            config_file: Path to configuration file
        """
        # Default settings
        self.ui = UISettings()
        self.database = DatabaseSettings()
        self.api = APISettings()
        self.logging = LoggingSettings()
        self.plugins = PluginSettings()
        self.security = SecuritySettings()
        
        # Custom settings
        self.custom: Dict[str, Any] = {}
        
        # Configuration file paths
        self.config_file = config_file or self._find_config_file()
        self.user_config_dir = Path.home() / ".curriculum-cli"
        self.system_config_dir = Path("/etc/curriculum-cli")
        
        # Load configuration
        self._load_defaults()
        self._load_environment_variables()
        if self.config_file and self.config_file.exists():
            self.load_from_file(self.config_file)
    
    def _find_config_file(self) -> Optional[Path]:
        """Find configuration file in standard locations
        
        Returns:
            Path to config file or None if not found
        """
        search_paths = [
            Path.cwd() / "curriculum-cli.yml",
            Path.cwd() / "curriculum-cli.yaml",
            Path.cwd() / "curriculum-cli.json",
            Path.home() / ".curriculum-cli" / "config.yml",
            Path.home() / ".curriculum-cli" / "config.yaml",
            Path.home() / ".curriculum-cli" / "config.json",
            Path("/etc/curriculum-cli/config.yml"),
            Path("/etc/curriculum-cli/config.yaml"),
            Path("/etc/curriculum-cli/config.json"),
        ]
        
        for path in search_paths:
            if path.exists():
                return path
        
        return None
    
    def _load_defaults(self):
        """Load default configuration values"""
        # Set up default logging path
        self.logging.file_path = str(self.user_config_dir / "logs" / "cli.log")
        
        # Ensure config directory exists
        self.user_config_dir.mkdir(parents=True, exist_ok=True)
        (self.user_config_dir / "logs").mkdir(exist_ok=True)
        (self.user_config_dir / "plugins").mkdir(exist_ok=True)
    
    def _load_environment_variables(self):
        """Load configuration from environment variables"""
        env_mappings = {
            'CLI_COLOR': ('ui.color_enabled', bool),
            'CLI_INTERACTIVE': ('ui.interactive_mode', bool),
            'CLI_THEME': ('ui.theme', str),
            'CLI_OUTPUT_FORMAT': ('ui.output_format', OutputFormat),
            'CLI_LOG_LEVEL': ('logging.level', LogLevel),
            'CLI_LOG_FILE': ('logging.file_path', str),
            'CLI_DB_URL': ('database.url', str),
            'CLI_DB_HOST': ('database.host', str),
            'CLI_DB_PORT': ('database.port', int),
            'CLI_DB_NAME': ('database.database', str),
            'CLI_DB_USER': ('database.username', str),
            'CLI_DB_PASSWORD': ('database.password', str),
            'CLI_API_URL': ('api.base_url', str),
            'CLI_API_KEY': ('api.api_key', str),
            'CLI_API_TIMEOUT': ('api.timeout', int),
            'CLI_PLUGINS_ENABLED': ('plugins.enabled', bool),
            'CLI_PLUGINS_AUTO_LOAD': ('plugins.auto_load', bool),
        }
        
        for env_var, (config_path, config_type) in env_mappings.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                try:
                    if config_type == bool:
                        value = value.lower() in ('true', '1', 'yes', 'on')
                    elif config_type == int:
                        value = int(value)
                    elif issubclass(config_type, Enum):
                        value = config_type(value)
                    
                    self._set_nested_value(config_path, value)
                except (ValueError, TypeError) as e:
                    print(f"Warning: Invalid value for {env_var}: {e}")
    
    def _set_nested_value(self, path: str, value: Any):
        """Set a nested configuration value
        
        Args:
            path: Dot-separated path (e.g., 'ui.color_enabled')
            value: Value to set
        """
        parts = path.split('.')
        obj = self
        
        for part in parts[:-1]:
            obj = getattr(obj, part)
        
        setattr(obj, parts[-1], value)
    
    def load_from_file(self, config_file: Path):
        """Load configuration from file
        
        Args:
            config_file: Path to configuration file
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file format is invalid
        """
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        suffix = config_file.suffix.lower()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if suffix in ['.yml', '.yaml']:
                    data = yaml.safe_load(f)
                elif suffix == '.json':
                    data = json.load(f)
                else:
                    raise ValueError(f"Unsupported configuration file format: {suffix}")
            
            self._merge_config_data(data or {})
            
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid configuration file format: {e}")
    
    def _merge_config_data(self, data: Dict[str, Any]):
        """Merge configuration data into current settings
        
        Args:
            data: Configuration data to merge
        """
        for section_name, section_data in data.items():
            if hasattr(self, section_name) and isinstance(section_data, dict):
                section = getattr(self, section_name)
                for key, value in section_data.items():
                    if hasattr(section, key):
                        # Handle enum conversions
                        field_type = type(getattr(section, key))
                        if issubclass(field_type, Enum):
                            try:
                                value = field_type(value)
                            except ValueError:
                                continue
                        setattr(section, key, value)
            elif section_name == 'custom':
                self.custom.update(section_data)
    
    def save_to_file(self, config_file: Optional[Path] = None, format: str = 'yaml'):
        """Save configuration to file
        
        Args:
            config_file: Path to save configuration (defaults to current config file)
            format: File format ('yaml', 'json')
        """
        if config_file is None:
            config_file = self.config_file or (self.user_config_dir / "config.yml")
        
        config_data = self.to_dict()
        
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            if format.lower() in ['yml', 'yaml']:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            elif format.lower() == 'json':
                json.dump(config_data, f, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported format: {format}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary
        
        Returns:
            Configuration as dictionary
        """
        return {
            'ui': asdict(self.ui),
            'database': asdict(self.database),
            'api': asdict(self.api),
            'logging': asdict(self.logging),
            'plugins': asdict(self.plugins),
            'security': asdict(self.security),
            'custom': self.custom
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key
        
        Args:
            key: Dot-separated configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        try:
            parts = key.split('.')
            obj = self
            
            for part in parts:
                if hasattr(obj, part):
                    obj = getattr(obj, part)
                elif isinstance(obj, dict) and part in obj:
                    obj = obj[part]
                else:
                    return default
            
            return obj
        except (AttributeError, KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value by dot-separated key
        
        Args:
            key: Dot-separated configuration key
            value: Value to set
        """
        self._set_nested_value(key, value)
    
    def validate(self) -> list:
        """Validate configuration settings
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Validate database settings
        if self.database.url:
            # Basic URL validation
            if not self.database.url.startswith(('postgresql://', 'mysql://', 'sqlite://')):
                errors.append("Invalid database URL format")
        
        # Validate API settings
        if self.api.base_url and not self.api.base_url.startswith(('http://', 'https://')):
            errors.append("API base URL must start with http:// or https://")
        
        # Validate logging settings
        if self.logging.file_path:
            log_dir = Path(self.logging.file_path).parent
            if not log_dir.exists():
                try:
                    log_dir.mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    errors.append(f"Cannot create log directory: {e}")
        
        # Validate plugin directories
        for plugin_dir in self.plugins.plugin_dirs:
            path = Path(plugin_dir).expanduser()
            if not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    errors.append(f"Cannot create plugin directory {plugin_dir}: {e}")
        
        return errors
    
    def create_sample_config(self) -> str:
        """Create a sample configuration file content
        
        Returns:
            Sample configuration as YAML string
        """
        sample_data = {
            'ui': {
                'color_enabled': True,
                'interactive_mode': False,
                'theme': 'default',
                'output_format': 'table',
                'progress_bars': True,
                'animations': True
            },
            'database': {
                'host': 'localhost',
                'port': 5432,
                'database': 'curriculum',
                'pool_size': 10,
                'timeout': 30
            },
            'api': {
                'timeout': 30,
                'retries': 3,
                'rate_limit': 100
            },
            'logging': {
                'level': 'info',
                'file_enabled': True,
                'max_file_size': '10MB',
                'backup_count': 5
            },
            'plugins': {
                'enabled': True,
                'auto_load': True,
                'plugin_dirs': ['~/.curriculum-cli/plugins', './plugins']
            },
            'security': {
                'encryption_enabled': True,
                'session_timeout': 3600,
                'max_login_attempts': 3
            }
        }
        
        return yaml.dump(sample_data, default_flow_style=False, indent=2)
# Add alias for backward compatibility
Config = CLIConfig
