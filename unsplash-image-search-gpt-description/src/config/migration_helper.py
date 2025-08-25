"""
Configuration Migration Helper

Helps users migrate from the old config_manager.py system to the new
secure configuration system while preserving their API keys and settings.
"""

import os
import json
import configparser
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

from .secure_config_manager import SecureConfigManager

logger = logging.getLogger(__name__)

class ConfigMigrationHelper:
    """Handles migration from legacy configuration to secure configuration."""
    
    def __init__(self, secure_manager: SecureConfigManager):
        """
        Initialize migration helper.
        
        Args:
            secure_manager: Instance of SecureConfigManager
        """
        self.secure_manager = secure_manager
        self.app_root = self._find_app_root()
    
    def _find_app_root(self) -> Path:
        """Find the application root directory."""
        # Try to find the directory containing the main application
        current = Path.cwd()
        
        # Look for main.py or config_manager.py in current or parent directories
        for path in [current] + list(current.parents):
            if (path / "main.py").exists() or (path / "config_manager.py").exists():
                return path
        
        # Fallback to current directory
        return current
    
    def find_legacy_config(self) -> Dict[str, Path]:
        """
        Find legacy configuration files.
        
        Returns:
            Dictionary with paths to found legacy config files
        """
        found_files = {}
        
        # Look for config.ini files
        config_ini_locations = [
            self.app_root / "config.ini",
            self.app_root / "data" / "config.ini",
            Path.home() / "AppData" / "Local" / "UnsplashImageSearch" / "config.ini",
        ]
        
        for location in config_ini_locations:
            if location.exists():
                found_files['config_ini'] = location
                break
        
        # Look for .env files
        env_locations = [
            self.app_root / ".env",
            self.app_root / ".env.local",
        ]
        
        for location in env_locations:
            if location.exists():
                found_files['env_file'] = location
                break
        
        # Look for session log files that might contain API usage
        log_locations = [
            self.app_root / "session_log.json",
            self.app_root / "data" / "session_log.json",
        ]
        
        for location in log_locations:
            if location.exists():
                found_files['session_log'] = location
                break
        
        return found_files
    
    def extract_legacy_config(self, config_files: Dict[str, Path]) -> Optional[Dict[str, str]]:
        """
        Extract API keys and settings from legacy configuration files.
        
        Args:
            config_files: Dictionary of legacy config file paths
            
        Returns:
            Dictionary with extracted configuration or None if nothing found
        """
        extracted = {
            'unsplash_access_key': '',
            'openai_api_key': '',
            'gpt_model': 'gpt-4o-mini'
        }
        
        # Try config.ini first
        if 'config_ini' in config_files:
            try:
                config_data = self._extract_from_ini(config_files['config_ini'])
                if config_data:
                    extracted.update(config_data)
                    logger.info(f"Extracted configuration from {config_files['config_ini']}")
            except Exception as e:
                logger.error(f"Error reading config.ini: {e}")
        
        # Try .env file
        if 'env_file' in config_files:
            try:
                env_data = self._extract_from_env(config_files['env_file'])
                if env_data:
                    # .env takes precedence over config.ini
                    for key, value in env_data.items():
                        if value:  # Only override if env has a value
                            extracted[key] = value
                    logger.info(f"Extracted configuration from {config_files['env_file']}")
            except Exception as e:
                logger.error(f"Error reading .env file: {e}")
        
        # Check environment variables as final fallback
        env_vars = {
            'unsplash_access_key': os.getenv('UNSPLASH_ACCESS_KEY', ''),
            'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
            'gpt_model': os.getenv('GPT_MODEL', 'gpt-4o-mini')
        }
        
        for key, value in env_vars.items():
            if value and not extracted.get(key):
                extracted[key] = value
        
        # Return None if no keys were found
        if not (extracted['unsplash_access_key'] or extracted['openai_api_key']):
            return None
        
        return extracted
    
    def _extract_from_ini(self, ini_path: Path) -> Optional[Dict[str, str]]:
        """Extract configuration from INI file."""
        try:
            config = configparser.ConfigParser()
            config.read(ini_path, encoding='utf-8')
            
            if 'API' in config:
                api_section = config['API']
                return {
                    'unsplash_access_key': api_section.get('unsplash_access_key', ''),
                    'openai_api_key': api_section.get('openai_api_key', ''),
                    'gpt_model': api_section.get('gpt_model', 'gpt-4o-mini')
                }
        except Exception as e:
            logger.error(f"Error parsing INI file {ini_path}: {e}")
            
        return None
    
    def _extract_from_env(self, env_path: Path) -> Optional[Dict[str, str]]:
        """Extract configuration from .env file."""
        try:
            env_vars = {}
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        env_vars[key] = value
            
            return {
                'unsplash_access_key': env_vars.get('UNSPLASH_ACCESS_KEY', ''),
                'openai_api_key': env_vars.get('OPENAI_API_KEY', ''),
                'gpt_model': env_vars.get('GPT_MODEL', 'gpt-4o-mini')
            }
        except Exception as e:
            logger.error(f"Error parsing .env file {env_path}: {e}")
            
        return None
    
    def create_migration_backup(self, config_files: Dict[str, Path]) -> Path:
        """
        Create a backup of legacy configuration files.
        
        Args:
            config_files: Dictionary of legacy config file paths
            
        Returns:
            Path to backup directory
        """
        import shutil
        from datetime import datetime
        
        # Create backup directory
        backup_dir = self.secure_manager.config_dir / "migration_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy legacy files to backup
        for file_type, file_path in config_files.items():
            try:
                backup_path = backup_dir / f"{file_type}_{file_path.name}"
                shutil.copy2(file_path, backup_path)
                logger.info(f"Backed up {file_path} to {backup_path}")
            except Exception as e:
                logger.error(f"Failed to backup {file_path}: {e}")
        
        # Create migration info file
        migration_info = {
            "migration_date": datetime.now().isoformat(),
            "original_files": {file_type: str(path) for file_type, path in config_files.items()},
            "backup_location": str(backup_dir),
            "migration_successful": False  # Will be updated after successful migration
        }
        
        with open(backup_dir / "migration_info.json", 'w', encoding='utf-8') as f:
            json.dump(migration_info, f, indent=2)
        
        return backup_dir
    
    async def perform_migration(self, extracted_config: Dict[str, str], 
                               backup_dir: Path, validate_keys: bool = True) -> bool:
        """
        Perform the migration to secure configuration.
        
        Args:
            extracted_config: Configuration extracted from legacy files
            backup_dir: Path to migration backup directory
            validate_keys: Whether to validate API keys during migration
            
        Returns:
            True if migration was successful
        """
        try:
            # Save configuration using secure manager
            success = await self.secure_manager.save_configuration(
                api_keys=extracted_config,
                validate_keys=validate_keys
            )
            
            if success:
                # Update migration info
                migration_info_path = backup_dir / "migration_info.json"
                if migration_info_path.exists():
                    with open(migration_info_path, 'r', encoding='utf-8') as f:
                        migration_info = json.load(f)
                    
                    migration_info["migration_successful"] = True
                    migration_info["secure_config_location"] = str(self.secure_manager.config_file)
                    
                    with open(migration_info_path, 'w', encoding='utf-8') as f:
                        json.dump(migration_info, f, indent=2)
                
                logger.info("Migration completed successfully")
                return True
            else:
                logger.error("Failed to save secure configuration during migration")
                return False
                
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def cleanup_legacy_files(self, config_files: Dict[str, Path], 
                           backup_created: bool = True) -> bool:
        """
        Clean up legacy configuration files after successful migration.
        
        Args:
            config_files: Dictionary of legacy config file paths
            backup_created: Whether backups were created
            
        Returns:
            True if cleanup was successful
        """
        if not backup_created:
            logger.warning("No backup was created, skipping cleanup of legacy files")
            return False
        
        cleaned_files = []
        failed_cleanups = []
        
        for file_type, file_path in config_files.items():
            try:
                # Only delete config.ini files, leave .env files as they might be used for development
                if file_type == 'config_ini':
                    file_path.unlink()
                    cleaned_files.append(str(file_path))
                    logger.info(f"Removed legacy file: {file_path}")
            except Exception as e:
                failed_cleanups.append((str(file_path), str(e)))
                logger.error(f"Failed to remove {file_path}: {e}")
        
        if cleaned_files:
            logger.info(f"Cleaned up legacy files: {', '.join(cleaned_files)}")
        
        if failed_cleanups:
            logger.warning(f"Failed to clean up some files: {failed_cleanups}")
        
        return len(failed_cleanups) == 0
    
    def get_migration_summary(self) -> Tuple[bool, Dict[str, str]]:
        """
        Get a summary of what would be migrated.
        
        Returns:
            Tuple of (migration_needed, summary_info)
        """
        summary = {
            'migration_needed': 'No',
            'legacy_files_found': 'None',
            'api_keys_found': 'None',
            'recommendation': 'No action needed'
        }
        
        # Check if secure config already exists
        if not self.secure_manager.is_first_run():
            summary['recommendation'] = 'Secure configuration already exists'
            return False, summary
        
        # Find legacy files
        legacy_files = self.find_legacy_config()
        if not legacy_files:
            summary['recommendation'] = 'No legacy configuration found, use setup wizard'
            return False, summary
        
        # Extract configuration
        extracted = self.extract_legacy_config(legacy_files)
        if not extracted:
            summary.update({
                'legacy_files_found': ', '.join(f"{k}: {v.name}" for k, v in legacy_files.items()),
                'recommendation': 'Legacy files found but no API keys detected'
            })
            return False, summary
        
        # Migration is needed
        key_status = []
        if extracted.get('unsplash_access_key'):
            key_status.append('Unsplash')
        if extracted.get('openai_api_key'):
            key_status.append('OpenAI')
        
        summary.update({
            'migration_needed': 'Yes',
            'legacy_files_found': ', '.join(f"{k}: {v.name}" for k, v in legacy_files.items()),
            'api_keys_found': ' + '.join(key_status),
            'recommendation': 'Migration recommended to secure configuration'
        })
        
        return True, summary


async def migrate_legacy_configuration(secure_manager: SecureConfigManager) -> Optional[bool]:
    """
    Automated migration helper function.
    
    Args:
        secure_manager: SecureConfigManager instance
        
    Returns:
        True if migration successful, False if failed, None if no migration needed
    """
    migration_helper = ConfigMigrationHelper(secure_manager)
    
    # Check if migration is needed
    migration_needed, summary = migration_helper.get_migration_summary()
    if not migration_needed:
        logger.info(f"Migration not needed: {summary['recommendation']}")
        return None
    
    logger.info(f"Legacy configuration detected: {summary['api_keys_found']} keys found")
    
    # Find and extract legacy configuration
    legacy_files = migration_helper.find_legacy_config()
    extracted_config = migration_helper.extract_legacy_config(legacy_files)
    
    if not extracted_config:
        logger.warning("No API keys found in legacy configuration")
        return False
    
    # Create backup
    backup_dir = migration_helper.create_migration_backup(legacy_files)
    logger.info(f"Created migration backup: {backup_dir}")
    
    # Perform migration
    success = await migration_helper.perform_migration(
        extracted_config, backup_dir, validate_keys=False  # Skip validation for migration
    )
    
    if success:
        # Clean up legacy files
        migration_helper.cleanup_legacy_files(legacy_files, backup_created=True)
        logger.info("Legacy configuration migrated successfully")
        return True
    else:
        logger.error("Migration failed")
        return False