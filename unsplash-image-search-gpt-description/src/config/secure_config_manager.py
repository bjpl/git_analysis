"""
Secure Configuration Manager

Enterprise-grade secure configuration management for distributed executables.
Features:
- Never embeds API keys in executable
- Stores keys securely in user's AppData directory
- Uses Windows DPAPI encryption
- Supports environment variable fallbacks
- Validates keys before saving
- Zero hardcoded secrets
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any, Union
from datetime import datetime

from .encryption_manager import EncryptionManager, EncryptionError
from .key_validator import APIKeyValidator, ValidationResult

logger = logging.getLogger(__name__)

class SecureConfigManager:
    """
    Manages secure configuration storage with encryption and validation.
    
    Stores configuration in the user's AppData/Local directory on Windows,
    ~/.local/share on Linux, and ~/Library/Application Support on macOS.
    """
    
    CONFIG_FILE_NAME = "config.enc"
    BACKUP_FILE_NAME = "config_backup.enc"
    TEMPLATE_FILE_NAME = "config_template.json"
    
    def __init__(self, app_name: str = "UnsplashImageSearch"):
        """
        Initialize secure configuration manager.
        
        Args:
            app_name: Application name for config directory
        """
        self.app_name = app_name
        self.encryption_manager = EncryptionManager()
        self.validator = APIKeyValidator()
        
        # Determine secure config directory
        self.config_dir = self._get_secure_config_dir()
        self.config_file = self.config_dir / self.CONFIG_FILE_NAME
        self.backup_file = self.config_dir / self.BACKUP_FILE_NAME
        self.template_file = self.config_dir / self.TEMPLATE_FILE_NAME
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Set secure permissions on config directory (Windows/Unix)
        self._secure_config_directory()
        
        # Configuration cache
        self._config_cache = None
        self._cache_timestamp = None
        
        logger.info(f"Secure config manager initialized: {self.config_dir}")
    
    def _get_secure_config_dir(self) -> Path:
        """
        Get platform-specific secure configuration directory.
        
        Returns:
            Path to secure configuration directory
        """
        if sys.platform.startswith('win'):
            # Windows: Use AppData/Local
            app_data = os.environ.get('LOCALAPPDATA')
            if not app_data:
                app_data = os.path.expanduser('~\\AppData\\Local')
            return Path(app_data) / self.app_name
        
        elif sys.platform == 'darwin':
            # macOS: Use Application Support
            return Path.home() / 'Library' / 'Application Support' / self.app_name
        
        else:
            # Linux/Unix: Use XDG base directory specification
            xdg_config = os.environ.get('XDG_CONFIG_HOME')
            if xdg_config:
                return Path(xdg_config) / self.app_name
            return Path.home() / '.config' / self.app_name
    
    def _secure_config_directory(self):
        """Set secure permissions on the config directory."""
        try:
            if sys.platform.startswith('win'):
                # Windows: Use icacls to set permissions (owner full access only)
                import subprocess
                subprocess.run([
                    'icacls', str(self.config_dir), 
                    '/inheritance:r',  # Remove inherited permissions
                    '/grant:r', f'{os.environ.get("USERNAME", "User")}:F'  # Grant full access to user only
                ], check=False, capture_output=True)
            else:
                # Unix-like: Set 700 permissions (owner read/write/execute only)
                self.config_dir.chmod(0o700)
                if self.config_file.exists():
                    self.config_file.chmod(0o600)
        except Exception as e:
            logger.warning(f"Could not set secure permissions: {e}")
    
    def is_first_run(self) -> bool:
        """
        Check if this is the first run (no configuration exists).
        
        Returns:
            True if configuration doesn't exist
        """
        return not self.config_file.exists()
    
    def create_config_template(self) -> Path:
        """
        Create a configuration template file for distribution.
        
        Returns:
            Path to created template file
        """
        template = {
            "version": "1.0",
            "app_name": self.app_name,
            "created_at": datetime.now().isoformat(),
            "instructions": {
                "notice": "This is a template file. API keys should NEVER be stored here.",
                "setup": "Run the application to launch the secure setup wizard.",
                "keys_location": "API keys will be stored securely in your user profile."
            },
            "api_keys": {
                "unsplash_access_key": "PLACEHOLDER_UNSPLASH_KEY",
                "openai_api_key": "PLACEHOLDER_OPENAI_KEY",
                "gpt_model": "gpt-4o-mini"
            },
            "ui_settings": {
                "window_width": 1100,
                "window_height": 800,
                "font_size": 12,
                "theme": "light",
                "zoom_level": 100
            },
            "security": {
                "encryption_enabled": True,
                "backup_enabled": True,
                "key_validation_enabled": True
            }
        }
        
        with open(self.template_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Configuration template created: {self.template_file}")
        return self.template_file
    
    async def save_configuration(self, api_keys: Dict[str, str], 
                                ui_settings: Optional[Dict] = None,
                                validate_keys: bool = True) -> bool:
        """
        Save configuration with encryption and optional validation.
        
        Args:
            api_keys: Dictionary with 'unsplash_access_key', 'openai_api_key', 'gpt_model'
            ui_settings: Optional UI settings dictionary
            validate_keys: Whether to validate API keys before saving
            
        Returns:
            True if configuration was saved successfully
        """
        try:
            # Validate keys if requested
            if validate_keys:
                unsplash_key = api_keys.get('unsplash_access_key', '').strip()
                openai_key = api_keys.get('openai_api_key', '').strip()
                gpt_model = api_keys.get('gpt_model', 'gpt-4o-mini')
                
                if not unsplash_key or not openai_key:
                    logger.error("API keys cannot be empty")
                    return False
                
                # Validate keys
                validation_results = await self.validator.validate_all_keys(
                    unsplash_key, openai_key, gpt_model
                )
                
                # Check validation results
                for service, result in validation_results.items():
                    if not result.is_valid:
                        logger.error(f"{service.title()} API key validation failed: {result.message}")
                        return False
                
                logger.info("All API keys validated successfully")
            
            # Prepare configuration data
            config_data = {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "api_keys": {
                    "unsplash_access_key": api_keys.get('unsplash_access_key', '').strip(),
                    "openai_api_key": api_keys.get('openai_api_key', '').strip(),
                    "gpt_model": api_keys.get('gpt_model', 'gpt-4o-mini')
                },
                "ui_settings": ui_settings or {
                    "window_width": 1100,
                    "window_height": 800,
                    "font_size": 12,
                    "theme": "light",
                    "zoom_level": 100
                },
                "security": {
                    "encryption_method": "DPAPI" if self.encryption_manager.dpapi_available else "Base64",
                    "backup_enabled": True,
                    "last_backup": None
                }
            }
            
            # Create backup of existing config
            if self.config_file.exists():
                if not self._create_backup():
                    logger.warning("Failed to create backup of existing configuration")
            
            # Encrypt and save configuration
            encrypted_data = self.encryption_manager.encrypt_data(
                config_data, "Application Configuration"
            )
            
            # Save to file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "encrypted_config": encrypted_data,
                    "metadata": {
                        "version": "1.0",
                        "encryption_method": "DPAPI" if self.encryption_manager.dpapi_available else "Base64",
                        "created_at": datetime.now().isoformat()
                    }
                }, f, indent=2)
            
            # Set secure permissions
            if not sys.platform.startswith('win'):
                self.config_file.chmod(0o600)
            
            # Clear cache
            self._config_cache = None
            self._cache_timestamp = None
            
            logger.info("Configuration saved successfully with encryption")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def load_configuration(self) -> Optional[Dict[str, Any]]:
        """
        Load and decrypt configuration.
        
        Returns:
            Configuration dictionary or None if failed
        """
        try:
            if not self.config_file.exists():
                logger.info("No configuration file found")
                return None
            
            # Check cache
            file_mtime = self.config_file.stat().st_mtime
            if (self._config_cache and self._cache_timestamp and 
                self._cache_timestamp >= file_mtime):
                return self._config_cache
            
            # Load and decrypt configuration
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_wrapper = json.load(f)
            
            encrypted_data = config_wrapper.get("encrypted_config")
            if not encrypted_data:
                logger.error("Invalid configuration file format")
                return None
            
            # Decrypt configuration
            config_data = self.encryption_manager.decrypt_data(encrypted_data)
            
            # Cache the result
            self._config_cache = config_data
            self._cache_timestamp = file_mtime
            
            logger.info("Configuration loaded successfully")
            return config_data
            
        except EncryptionError as e:
            logger.error(f"Failed to decrypt configuration: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return None
    
    def get_api_keys(self) -> Dict[str, str]:
        """
        Get API keys with environment variable fallbacks.
        
        Returns:
            Dictionary with API keys
        """
        # Default values
        api_keys = {
            'unsplash': '',
            'openai': '',
            'gpt_model': 'gpt-4o-mini'
        }
        
        # Try environment variables first
        env_unsplash = os.getenv('UNSPLASH_ACCESS_KEY', '').strip()
        env_openai = os.getenv('OPENAI_API_KEY', '').strip()
        env_model = os.getenv('GPT_MODEL', '').strip()
        
        if env_unsplash and env_openai:
            logger.info("Using API keys from environment variables")
            api_keys.update({
                'unsplash': env_unsplash,
                'openai': env_openai,
                'gpt_model': env_model or 'gpt-4o-mini'
            })
            return api_keys
        
        # Try configuration file
        config = self.load_configuration()
        if config and 'api_keys' in config:
            config_keys = config['api_keys']
            api_keys.update({
                'unsplash': config_keys.get('unsplash_access_key', '').strip(),
                'openai': config_keys.get('openai_api_key', '').strip(),
                'gpt_model': config_keys.get('gpt_model', 'gpt-4o-mini')
            })
        
        return api_keys
    
    def get_ui_settings(self) -> Dict[str, Any]:
        """
        Get UI settings from configuration.
        
        Returns:
            Dictionary with UI settings
        """
        default_settings = {
            'window_width': 1100,
            'window_height': 800,
            'font_size': 12,
            'theme': 'light',
            'zoom_level': 100
        }
        
        config = self.load_configuration()
        if config and 'ui_settings' in config:
            settings = config['ui_settings']
            # Merge with defaults to handle missing keys
            default_settings.update(settings)
        
        return default_settings
    
    async def update_ui_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Update UI settings in configuration.
        
        Args:
            settings: Dictionary with UI settings to update
            
        Returns:
            True if settings were updated successfully
        """
        try:
            config = self.load_configuration()
            if not config:
                logger.error("No configuration found to update")
                return False
            
            # Update UI settings
            if 'ui_settings' not in config:
                config['ui_settings'] = {}
            
            config['ui_settings'].update(settings)
            config['last_updated'] = datetime.now().isoformat()
            
            # Save updated configuration
            api_keys = config.get('api_keys', {})
            return await self.save_configuration(api_keys, config['ui_settings'], validate_keys=False)
            
        except Exception as e:
            logger.error(f"Failed to update UI settings: {e}")
            return False
    
    def validate_api_keys(self) -> bool:
        """
        Check if valid API keys are configured.
        
        Returns:
            True if both API keys are present and non-empty
        """
        api_keys = self.get_api_keys()
        return bool(api_keys['unsplash'] and api_keys['openai'])
    
    def _create_backup(self) -> bool:
        """
        Create backup of current configuration.
        
        Returns:
            True if backup was created successfully
        """
        try:
            if not self.config_file.exists():
                return True
            
            # Copy current config to backup location
            import shutil
            shutil.copy2(self.config_file, self.backup_file)
            
            # Update backup timestamp in config
            config = self.load_configuration()
            if config:
                config['security']['last_backup'] = datetime.now().isoformat()
            
            logger.info("Configuration backup created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def restore_from_backup(self) -> bool:
        """
        Restore configuration from backup.
        
        Returns:
            True if restore was successful
        """
        try:
            if not self.backup_file.exists():
                logger.error("No backup file found")
                return False
            
            # Copy backup to current config
            import shutil
            shutil.copy2(self.backup_file, self.config_file)
            
            # Clear cache
            self._config_cache = None
            self._cache_timestamp = None
            
            logger.info("Configuration restored from backup")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False
    
    def delete_configuration(self) -> bool:
        """
        Securely delete configuration and backup files.
        
        Returns:
            True if deletion was successful
        """
        try:
            files_deleted = []
            
            if self.config_file.exists():
                self.config_file.unlink()
                files_deleted.append("config")
            
            if self.backup_file.exists():
                self.backup_file.unlink()
                files_deleted.append("backup")
            
            # Clear cache
            self._config_cache = None
            self._cache_timestamp = None
            
            if files_deleted:
                logger.info(f"Deleted configuration files: {', '.join(files_deleted)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete configuration: {e}")
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        Get information about the current configuration.
        
        Returns:
            Dictionary with configuration metadata
        """
        info = {
            'config_dir': str(self.config_dir),
            'config_file': str(self.config_file),
            'config_exists': self.config_file.exists(),
            'backup_exists': self.backup_file.exists(),
            'is_first_run': self.is_first_run(),
            'encryption_available': self.encryption_manager.dpapi_available,
            'has_valid_keys': self.validate_api_keys()
        }
        
        if self.config_file.exists():
            config = self.load_configuration()
            if config:
                info.update({
                    'config_version': config.get('version', 'unknown'),
                    'created_at': config.get('created_at', 'unknown'),
                    'last_updated': config.get('last_updated', 'unknown'),
                    'encryption_method': config.get('security', {}).get('encryption_method', 'unknown')
                })
        
        return info