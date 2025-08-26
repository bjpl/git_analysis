"""
Test suite for the Settings Dialog functionality.
Tests configuration management, UI components, and data persistence.
"""

import unittest
import tkinter as tk
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from config_manager import ConfigManager
    from src.ui.dialogs.settings_menu import SettingsDialog, show_settings_dialog
except ImportError as e:
    print(f"Import error: {e}")
    print("Ensure you're running tests from the project root directory")
    sys.exit(1)


class TestSettingsDialog(unittest.TestCase):
    """Test suite for Settings Dialog functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test config
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Create test config manager with temporary directory
        self.config_manager = ConfigManager()
        self.config_manager.config_dir = self.test_dir
        self.config_manager.config_file = self.test_dir / "config.ini"
        self.config_manager.data_dir = self.test_dir / "data"
        self.config_manager.data_dir.mkdir(exist_ok=True)
        
        # Initialize test config with default values
        self.config_manager.config.read_dict({
            'API': {
                'unsplash_access_key': 'test_unsplash_key',
                'openai_api_key': 'sk-test_openai_key',
                'gpt_model': 'gpt-4o-mini'
            },
            'GPT': {
                'temperature': '0.7',
                'max_tokens': '500'
            },
            'Learning': {
                'description_style': 'Simple',
                'vocabulary_level': 'Beginner',
                'enable_learning': 'true'
            },
            'UI': {
                'theme': 'light',
                'font_size': '12',
                'opacity': '1.0'
            }
        })
        
        # Save initial config
        with open(self.config_manager.config_file, 'w') as f:
            self.config_manager.config.write(f)
        
        # Create root window for testing (hidden)
        self.root = tk.Tk()
        self.root.withdraw()  # Hide test window
    
    def tearDown(self):
        """Clean up test environment."""
        try:
            if self.root:
                self.root.destroy()
        except:
            pass
        
        # Clean up temporary directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_config_manager_initialization(self):
        """Test ConfigManager initialization with test data."""
        # Test API keys loading
        api_keys = self.config_manager.get_api_keys()
        self.assertEqual(api_keys['unsplash'], 'test_unsplash_key')
        self.assertEqual(api_keys['openai'], 'sk-test_openai_key')
        self.assertEqual(api_keys['gpt_model'], 'gpt-4o-mini')
        
        # Test config sections exist
        self.assertTrue(self.config_manager.config.has_section('API'))
        self.assertTrue(self.config_manager.config.has_section('GPT'))
        self.assertTrue(self.config_manager.config.has_section('Learning'))
        self.assertTrue(self.config_manager.config.has_section('UI'))
    
    def test_settings_dialog_creation(self):
        """Test that Settings Dialog can be created without errors."""
        try:
            dialog = SettingsDialog(self.root, self.config_manager)
            self.assertIsInstance(dialog, SettingsDialog)
            
            # Test that dialog has required attributes
            self.assertTrue(hasattr(dialog, 'notebook'))
            self.assertTrue(hasattr(dialog, 'unsplash_key_var'))
            self.assertTrue(hasattr(dialog, 'openai_key_var'))
            self.assertTrue(hasattr(dialog, 'gpt_model_var'))
            self.assertTrue(hasattr(dialog, 'temperature_var'))
            self.assertTrue(hasattr(dialog, 'max_tokens_var'))
            
            dialog.destroy()
            
        except Exception as e:
            self.fail(f"Settings Dialog creation failed: {e}")
    
    def test_variable_initialization(self):
        """Test that UI variables are properly initialized."""
        dialog = SettingsDialog(self.root, self.config_manager)
        
        # Test API variables
        self.assertEqual(dialog.unsplash_key_var.get(), 'test_unsplash_key')
        self.assertEqual(dialog.openai_key_var.get(), 'sk-test_openai_key')
        self.assertEqual(dialog.gpt_model_var.get(), 'gpt-4o-mini')
        
        # Test GPT variables
        self.assertEqual(dialog.temperature_var.get(), 0.7)
        self.assertEqual(dialog.max_tokens_var.get(), 500)
        
        # Test Learning variables
        self.assertEqual(dialog.description_style_var.get(), 'Simple')
        self.assertEqual(dialog.vocabulary_level_var.get(), 'Beginner')
        self.assertEqual(dialog.enable_learning_var.get(), True)
        
        # Test UI variables
        self.assertEqual(dialog.theme_var.get(), 'light')
        self.assertEqual(dialog.font_size_var.get(), 12)
        self.assertEqual(dialog.window_opacity_var.get(), 1.0)
        
        dialog.destroy()
    
    def test_api_key_saving(self):
        """Test API key saving functionality."""
        dialog = SettingsDialog(self.root, self.config_manager)
        
        # Change API keys
        dialog.unsplash_key_var.set('new_unsplash_key')
        dialog.openai_key_var.set('sk-new_openai_key')
        dialog.gpt_model_var.set('gpt-4o')
        
        # Trigger save
        dialog._save_api_keys()
        
        # Verify keys are saved
        api_keys = self.config_manager.get_api_keys()
        self.assertEqual(api_keys['unsplash'], 'new_unsplash_key')
        self.assertEqual(api_keys['openai'], 'sk-new_openai_key')
        self.assertEqual(api_keys['gpt_model'], 'gpt-4o')
        
        dialog.destroy()
    
    def test_gpt_settings_saving(self):
        """Test GPT settings saving functionality."""
        dialog = SettingsDialog(self.root, self.config_manager)
        
        # Change GPT settings
        dialog.temperature_var.set(1.2)
        dialog.max_tokens_var.set(800)
        
        # Trigger save
        dialog._save_gpt_settings()
        
        # Verify settings are saved
        config = self.config_manager.config
        self.assertEqual(config.getfloat('GPT', 'temperature'), 1.2)
        self.assertEqual(config.getint('GPT', 'max_tokens'), 800)
        
        dialog.destroy()
    
    def test_learning_settings_saving(self):
        """Test learning settings saving functionality."""
        dialog = SettingsDialog(self.root, self.config_manager)
        
        # Change learning settings
        dialog.description_style_var.set('Detailed')
        dialog.vocabulary_level_var.set('Advanced')
        dialog.enable_learning_var.set(False)
        
        # Trigger save
        dialog._save_learning_settings()
        
        # Verify settings are saved
        config = self.config_manager.config
        self.assertEqual(config.get('Learning', 'description_style'), 'Detailed')
        self.assertEqual(config.get('Learning', 'vocabulary_level'), 'Advanced')
        self.assertEqual(config.getboolean('Learning', 'enable_learning'), False)
        
        dialog.destroy()
    
    def test_appearance_settings_saving(self):
        """Test appearance settings saving functionality."""
        dialog = SettingsDialog(self.root, self.config_manager)
        
        # Change appearance settings
        dialog.theme_var.set('dark')
        dialog.font_size_var.set(16)
        dialog.window_opacity_var.set(0.8)
        
        # Trigger save
        dialog._save_appearance_settings()
        
        # Verify settings are saved
        config = self.config_manager.config
        self.assertEqual(config.get('UI', 'theme'), 'dark')
        self.assertEqual(config.getint('UI', 'font_size'), 16)
        self.assertEqual(config.getfloat('UI', 'opacity'), 0.8)
        
        dialog.destroy()
    
    def test_config_backup_restore(self):
        """Test configuration backup and restore functionality."""
        dialog = SettingsDialog(self.root, self.config_manager)
        
        # Get original backup
        original_backup = dialog.original_config
        
        # Verify backup contains expected data
        self.assertIn('API', original_backup)
        self.assertIn('GPT', original_backup)
        self.assertEqual(original_backup['API']['gpt_model'], 'gpt-4o-mini')
        
        # Change some settings
        dialog.gpt_model_var.set('gpt-4o')
        dialog._save_api_keys()
        
        # Restore from backup
        dialog._restore_config()
        
        # Verify restoration worked
        api_keys = self.config_manager.get_api_keys()
        self.assertEqual(api_keys['gpt_model'], 'gpt-4o-mini')
        
        dialog.destroy()
    
    def test_show_settings_dialog_function(self):
        """Test the show_settings_dialog convenience function."""
        try:
            dialog = show_settings_dialog(self.root, self.config_manager)
            self.assertIsInstance(dialog, SettingsDialog)
            dialog.destroy()
        except Exception as e:
            self.fail(f"show_settings_dialog function failed: {e}")
    
    def test_validation_methods(self):
        """Test key validation methods."""
        dialog = SettingsDialog(self.root, self.config_manager)
        
        # Test Unsplash key validation
        self.assertFalse(dialog._validate_unsplash_key(''))  # Empty
        self.assertFalse(dialog._validate_unsplash_key('short'))  # Too short
        self.assertFalse(dialog._validate_unsplash_key('key with spaces'))  # Spaces
        self.assertTrue(dialog._validate_unsplash_key('a' * 43))  # Valid length
        
        # Test OpenAI key validation
        self.assertFalse(dialog._validate_openai_key(''))  # Empty
        self.assertFalse(dialog._validate_openai_key('invalid'))  # Wrong prefix
        self.assertFalse(dialog._validate_openai_key('sk-short'))  # Too short
        self.assertFalse(dialog._validate_openai_key('sk-key with spaces'))  # Spaces
        self.assertTrue(dialog._validate_openai_key('sk-' + 'a' * 40))  # Valid
        
        dialog.destroy()
    
    def test_ui_update_methods(self):
        """Test UI update methods."""
        dialog = SettingsDialog(self.root, self.config_manager)
        
        # Test temperature label update
        dialog.temperature_var.set(1.5)
        dialog._update_temperature_label()
        self.assertEqual(dialog.temp_label.cget('text'), '1.5')
        
        # Test font size label update
        dialog.font_size_var.set(18)
        dialog._update_font_size_label()
        self.assertEqual(dialog.font_size_label.cget('text'), '18')
        
        # Test opacity label update
        dialog.window_opacity_var.set(0.75)
        dialog._update_opacity_label()
        self.assertEqual(dialog.opacity_label.cget('text'), '75%')
        
        dialog.destroy()


class TestSettingsDialogIntegration(unittest.TestCase):
    """Test integration scenarios for Settings Dialog."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Create temporary config
        self.test_dir = Path(tempfile.mkdtemp())
        self.config_manager = ConfigManager()
        self.config_manager.config_dir = self.test_dir
        self.config_manager.config_file = self.test_dir / "config.ini"
    
    def tearDown(self):
        """Clean up integration test environment."""
        try:
            if self.root:
                self.root.destroy()
        except:
            pass
        
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_multiple_dialog_instances(self):
        """Test that multiple dialog instances can be created and destroyed."""
        dialogs = []
        
        try:
            # Create multiple dialogs
            for i in range(3):
                dialog = SettingsDialog(self.root, self.config_manager)
                dialogs.append(dialog)
            
            # Verify all were created
            self.assertEqual(len(dialogs), 3)
            
            # Clean up
            for dialog in dialogs:
                dialog.destroy()
                
        except Exception as e:
            self.fail(f"Multiple dialog creation failed: {e}")
    
    def test_config_persistence_across_dialogs(self):
        """Test that configuration changes persist across dialog instances."""
        # First dialog - change settings
        dialog1 = SettingsDialog(self.root, self.config_manager)
        dialog1.gpt_model_var.set('gpt-4o')
        dialog1._save_api_keys()
        dialog1.destroy()
        
        # Second dialog - verify changes persisted
        dialog2 = SettingsDialog(self.root, self.config_manager)
        self.assertEqual(dialog2.gpt_model_var.get(), 'gpt-4o')
        dialog2.destroy()


def run_tests():
    """Run all settings dialog tests."""
    # Create test loader
    loader = unittest.TestLoader()
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestSettingsDialog))
    suite.addTests(loader.loadTestsFromTestCase(TestSettingsDialogIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running Settings Dialog Tests...")
    print("=" * 50)
    
    success = run_tests()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed!")
    
    sys.exit(0 if success else 1)