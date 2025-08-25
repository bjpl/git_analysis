"""
Tests for configuration management functionality.
"""
import pytest
from unittest.mock import Mock, patch, mock_open
import tempfile
import os
from pathlib import Path

# Import the module to test
try:
    from config_manager import ConfigManager, ensure_api_keys_configured
except ImportError:
    pytest.skip("config_manager not available", allow_module_level=True)


class TestConfigManager:
    """Test ConfigManager class functionality."""
    
    def test_should_initialize_with_default_values(self, temp_data_dir):
        """Test that ConfigManager initializes with default values."""
        config_path = temp_data_dir / "config.ini"
        config_manager = ConfigManager(str(config_path))
        
        assert config_manager.config_file == str(config_path)
        assert config_manager.config is not None
    
    def test_should_load_existing_config_file(self, sample_config_file):
        """Test loading an existing configuration file."""
        config_manager = ConfigManager(str(sample_config_file))
        
        api_keys = config_manager.get_api_keys()
        assert api_keys['unsplash'] == 'test_unsplash_key'
        assert api_keys['openai'] == 'test_openai_key'
    
    def test_should_create_config_file_if_not_exists(self, temp_data_dir):
        """Test creating a new configuration file."""
        config_path = temp_data_dir / "new_config.ini"
        config_manager = ConfigManager(str(config_path))
        
        # Set some values
        config_manager.set_api_key('unsplash', 'new_unsplash_key')
        config_manager.set_api_key('openai', 'new_openai_key')
        
        # Check file was created
        assert config_path.exists()
    
    @patch('builtins.input')
    def test_should_prompt_for_missing_api_keys(self, mock_input, temp_data_dir):
        """Test prompting for missing API keys."""
        mock_input.side_effect = ['user_unsplash_key', 'user_openai_key']
        config_path = temp_data_dir / "config.ini"
        
        config_manager = ConfigManager(str(config_path))
        
        # This should trigger the prompts
        api_keys = config_manager.get_api_keys()
        
        # Check that input was called
        assert mock_input.call_count >= 2
    
    def test_should_get_data_paths(self, temp_data_dir):
        """Test getting data file paths."""
        config_path = temp_data_dir / "config.ini"
        config_manager = ConfigManager(str(config_path))
        
        paths = config_manager.get_paths()
        
        assert 'session_log' in paths
        assert 'vocabulary_csv' in paths
        assert 'data_dir' in paths
        assert paths['data_dir'].endswith('data')
    
    def test_should_get_default_settings(self, temp_data_dir):
        """Test getting default settings."""
        config_path = temp_data_dir / "config.ini"
        config_manager = ConfigManager(str(config_path))
        
        settings = config_manager.get_settings()
        
        assert 'gpt_model' in settings
        assert settings['gpt_model'] in ['gpt-4o-mini', 'gpt-4o', 'gpt-4']
    
    def test_should_validate_api_keys(self, sample_config_file):
        """Test API key validation."""
        config_manager = ConfigManager(str(sample_config_file))
        
        # Should not raise exception with valid keys
        api_keys = config_manager.get_api_keys()
        assert len(api_keys['unsplash']) > 0
        assert len(api_keys['openai']) > 0
    
    def test_should_handle_missing_config_sections(self, temp_data_dir):
        """Test handling missing configuration sections gracefully."""
        config_path = temp_data_dir / "incomplete_config.ini"
        config_path.write_text("[API_KEYS]\nunsplash_access_key = test_key")
        
        config_manager = ConfigManager(str(config_path))
        
        # Should not crash when getting settings
        settings = config_manager.get_settings()
        assert isinstance(settings, dict)


class TestEnsureAPIKeysConfigured:
    """Test the ensure_api_keys_configured function."""
    
    @patch('config_manager.ConfigManager')
    def test_should_return_config_manager_when_keys_exist(self, mock_config_class):
        """Test returning ConfigManager when API keys exist."""
        mock_config = Mock()
        mock_config.get_api_keys.return_value = {
            'unsplash': 'test_key',
            'openai': 'test_key'
        }
        mock_config_class.return_value = mock_config
        
        result = ensure_api_keys_configured(None)
        
        assert result == mock_config
    
    @patch('config_manager.ConfigManager')
    @patch('tkinter.messagebox.askokcancel')
    def test_should_handle_user_cancellation(self, mock_askokcancel, mock_config_class):
        """Test handling when user cancels API key setup."""
        mock_askokcancel.return_value = False
        mock_config = Mock()
        mock_config.get_api_keys.side_effect = Exception("No API keys")
        mock_config_class.return_value = mock_config
        
        result = ensure_api_keys_configured(None)
        
        assert result is None
    
    def test_should_create_data_directory(self, temp_data_dir):
        """Test that data directory is created."""
        config_path = temp_data_dir / "config.ini"
        config_manager = ConfigManager(str(config_path))
        
        paths = config_manager.get_paths()
        data_dir = Path(paths['data_dir'])
        
        # The directory should be created when paths are accessed
        assert data_dir.exists() or not data_dir.parent.exists()  # Either exists or parent doesn't exist


@pytest.mark.integration
class TestConfigManagerIntegration:
    """Integration tests for ConfigManager."""
    
    def test_full_config_workflow(self, temp_data_dir):
        """Test full configuration workflow."""
        config_path = temp_data_dir / "config.ini"
        
        # Create config manager
        config_manager = ConfigManager(str(config_path))
        
        # Set API keys
        config_manager.set_api_key('unsplash', 'integration_unsplash_key')
        config_manager.set_api_key('openai', 'integration_openai_key')
        
        # Get API keys
        api_keys = config_manager.get_api_keys()
        
        assert api_keys['unsplash'] == 'integration_unsplash_key'
        assert api_keys['openai'] == 'integration_openai_key'
        
        # Get paths
        paths = config_manager.get_paths()
        assert all(isinstance(path, str) for path in paths.values())
        
        # Get settings
        settings = config_manager.get_settings()
        assert 'gpt_model' in settings
    
    def test_config_persistence(self, temp_data_dir):
        """Test that configuration persists across instances."""
        config_path = temp_data_dir / "config.ini"
        
        # First instance
        config_manager1 = ConfigManager(str(config_path))
        config_manager1.set_api_key('unsplash', 'persistent_key')
        
        # Second instance
        config_manager2 = ConfigManager(str(config_path))
        api_keys = config_manager2.get_api_keys()
        
        assert api_keys['unsplash'] == 'persistent_key'