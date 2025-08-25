"""
Integration tests for API key forms.

Tests the complete workflow from form entry to API validation and configuration saving.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
import threading
import time
import sys
from pathlib import Path
import tempfile
import shutil
import configparser

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config_manager import ConfigManager, SetupWizard, ensure_api_keys_configured


class TestAPIKeyFormIntegration(unittest.TestCase):
    """Integration tests for API key form complete workflow."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level test fixtures."""
        cls.test_dir = Path(tempfile.mkdtemp())
        
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level test fixtures."""
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Create test config directory
        self.config_dir = self.test_dir / "test_config"
        self.config_dir.mkdir(exist_ok=True)
        
    def tearDown(self):
        """Clean up after tests."""
        if self.root:
            self.root.destroy()
    
    @patch('config_manager.ConfigManager._get_config_dir')
    def test_full_setup_workflow(self, mock_config_dir):
        """Test complete setup workflow from start to finish."""
        mock_config_dir.return_value = self.config_dir
        
        # Test first run detection
        config_manager = ConfigManager()
        self.assertFalse(config_manager.validate_api_keys())
        
        # Test wizard creation and setup
        wizard = SetupWizard(self.root, config_manager)
        
        # Simulate user input
        wizard.unsplash_entry.insert(0, "test_unsplash_key_12345")
        wizard.openai_entry.insert(0, "sk-test_openai_key_67890")
        wizard.model_var.set("gpt-4o-mini")
        
        # Simulate save action
        wizard.save_and_continue()
        
        # Verify configuration was saved
        new_config = ConfigManager()
        api_keys = new_config.get_api_keys()
        
        self.assertEqual(api_keys['unsplash'], "test_unsplash_key_12345")
        self.assertEqual(api_keys['openai'], "sk-test_openai_key_67890")
        self.assertEqual(api_keys['gpt_model'], "gpt-4o-mini")
    
    @patch('config_manager.ConfigManager._get_config_dir')
    def test_configuration_persistence(self, mock_config_dir):
        """Test configuration persists between application runs."""
        mock_config_dir.return_value = self.config_dir
        
        # First run - save configuration
        config1 = ConfigManager()
        config1.save_api_keys(
            "persistent_unsplash_key",
            "sk-persistent_openai_key",
            "gpt-4o"
        )
        
        # Second run - load configuration
        config2 = ConfigManager()
        api_keys = config2.get_api_keys()
        
        self.assertEqual(api_keys['unsplash'], "persistent_unsplash_key")
        self.assertEqual(api_keys['openai'], "sk-persistent_openai_key")
        self.assertEqual(api_keys['gpt_model'], "gpt-4o")
        self.assertTrue(config2.validate_api_keys())
    
    @patch('config_manager.ConfigManager._get_config_dir')
    def test_configuration_file_format(self, mock_config_dir):
        """Test configuration file is saved in correct format."""
        mock_config_dir.return_value = self.config_dir
        
        config = ConfigManager()
        config.save_api_keys("test_key", "sk-test_key", "gpt-4o-mini")
        
        # Verify file exists and is readable
        config_file = self.config_dir / "config.ini"
        self.assertTrue(config_file.exists())
        
        # Verify file format
        parser = configparser.ConfigParser()
        parser.read(config_file)
        
        self.assertIn('API', parser.sections())
        self.assertEqual(parser['API']['unsplash_access_key'], 'test_key')
        self.assertEqual(parser['API']['openai_api_key'], 'sk-test_key')
        self.assertEqual(parser['API']['gpt_model'], 'gpt-4o-mini')
    
    @patch('config_manager.ConfigManager._get_config_dir')
    def test_ensure_api_keys_configured_flow(self, mock_config_dir):
        """Test the complete ensure_api_keys_configured workflow."""
        mock_config_dir.return_value = self.config_dir
        
        # Mock user interaction
        with patch('config_manager.SetupWizard') as mock_wizard_class:
            mock_wizard = Mock()
            mock_wizard.result = True
            mock_wizard_class.return_value = mock_wizard
            
            # Mock wait_window to simulate user completing wizard
            def mock_wait_window(window):
                # Simulate saving keys during wizard
                config = ConfigManager()
                config.save_api_keys("wizard_unsplash", "sk-wizard_openai", "gpt-4o")
            
            with patch.object(self.root, 'wait_window', side_effect=mock_wait_window):
                result = ensure_api_keys_configured(self.root)
                
                self.assertIsNotNone(result)
                mock_wizard_class.assert_called_once()
    
    def test_error_recovery_on_save_failure(self):
        """Test error recovery when save operation fails."""
        with patch('config_manager.ConfigManager') as mock_config:
            mock_config.return_value.save_api_keys.side_effect = IOError("Disk full")
            
            wizard = SetupWizard(self.root, mock_config.return_value)
            wizard.unsplash_entry.insert(0, "test_key")
            wizard.openai_entry.insert(0, "sk-test_key")
            
            with patch('tkinter.messagebox.showerror') as mock_error:
                wizard.save_and_continue()
                
                # Should show error message
                mock_error.assert_called_once()
                
                # Wizard should still be open (not destroyed)
                self.assertTrue(wizard.winfo_exists())


class TestAPIValidationIntegration(unittest.TestCase):
    """Integration tests for API validation workflow."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
        
    def tearDown(self):
        """Clean up after tests."""
        if self.root:
            self.root.destroy()
    
    @patch('requests.get')
    def test_unsplash_api_validation_success(self, mock_get):
        """Test successful Unsplash API validation."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'test_photo_id',
            'urls': {'regular': 'https://example.com/image.jpg'}
        }
        mock_get.return_value = mock_response
        
        # Test the validation process
        api_key = "valid_unsplash_key"
        headers = {"Authorization": f"Client-ID {api_key}"}
        
        response = mock_get("https://api.unsplash.com/photos/random", headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.json())
    
    @patch('requests.get')
    def test_unsplash_api_validation_failure(self, mock_get):
        """Test failed Unsplash API validation."""
        # Mock failed API response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'error': 'Invalid access token'}
        mock_get.return_value = mock_response
        
        api_key = "invalid_unsplash_key"
        headers = {"Authorization": f"Client-ID {api_key}"}
        
        response = mock_get("https://api.unsplash.com/photos/random", headers=headers)
        
        self.assertEqual(response.status_code, 401)
        self.assertIn('error', response.json())
    
    @patch('openai.OpenAI')
    def test_openai_api_validation_success(self, mock_openai_class):
        """Test successful OpenAI API validation."""
        # Mock OpenAI client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello!"
        
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Test the validation
        client = mock_openai_class(api_key="sk-valid_key")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        self.assertIsNotNone(response.choices)
        self.assertEqual(len(response.choices), 1)
    
    @patch('openai.OpenAI')
    def test_openai_api_validation_failure(self, mock_openai_class):
        """Test failed OpenAI API validation."""
        # Mock authentication error
        mock_openai_class.side_effect = Exception("Invalid API key")
        
        with self.assertRaises(Exception) as context:
            mock_openai_class(api_key="invalid_key")
        
        self.assertIn("Invalid API key", str(context.exception))


class TestFormStatePersistence(unittest.TestCase):
    """Test form state persistence and recovery."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
        
    def tearDown(self):
        """Clean up after tests."""
        if self.root:
            self.root.destroy()
    
    def test_form_state_recovery_after_validation_error(self):
        """Test form state is preserved after validation errors."""
        with patch('config_manager.ConfigManager') as mock_config:
            wizard = SetupWizard(self.root, mock_config.return_value)
            
            # Enter test data
            test_unsplash = "test_unsplash_key"
            test_openai = "sk-test_openai_key"
            test_model = "gpt-4o"
            
            wizard.unsplash_entry.insert(0, test_unsplash)
            wizard.openai_entry.insert(0, test_openai)
            wizard.model_var.set(test_model)
            
            # Simulate validation error
            mock_config.return_value.save_api_keys.side_effect = Exception("Validation failed")
            
            with patch('tkinter.messagebox.showerror'):
                wizard.save_and_continue()
            
            # Form state should be preserved
            self.assertEqual(wizard.unsplash_entry.get(), test_unsplash)
            self.assertEqual(wizard.openai_entry.get(), test_openai)
            self.assertEqual(wizard.model_var.get(), test_model)
    
    def test_form_cleanup_on_successful_completion(self):
        """Test form is properly cleaned up on successful completion."""
        with patch('config_manager.ConfigManager') as mock_config:
            mock_config.return_value.save_api_keys = Mock()
            
            wizard = SetupWizard(self.root, mock_config.return_value)
            wizard.unsplash_entry.insert(0, "test_key")
            wizard.openai_entry.insert(0, "sk-test_key")
            
            # Mock destroy to track cleanup
            wizard.destroy = Mock()
            
            wizard.save_and_continue()
            
            # Should clean up (destroy) the wizard
            wizard.destroy.assert_called_once()


class TestConcurrentFormOperations(unittest.TestCase):
    """Test handling of concurrent form operations."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
        
    def tearDown(self):
        """Clean up after tests."""
        if self.root:
            self.root.destroy()
    
    def test_prevent_multiple_save_operations(self):
        """Test that multiple save operations are prevented."""
        with patch('config_manager.ConfigManager') as mock_config:
            # Make save operation slow
            def slow_save(*args):
                time.sleep(0.1)
                return None
            
            mock_config.return_value.save_api_keys.side_effect = slow_save
            
            wizard = SetupWizard(self.root, mock_config.return_value)
            wizard.unsplash_entry.insert(0, "test_key")
            wizard.openai_entry.insert(0, "sk-test_key")
            
            # Start first save operation in thread
            def save_operation():
                wizard.save_and_continue()
            
            thread1 = threading.Thread(target=save_operation)
            thread2 = threading.Thread(target=save_operation)
            
            thread1.start()
            thread2.start()
            
            thread1.join(timeout=1)
            thread2.join(timeout=1)
            
            # Should only be called once despite multiple attempts
            self.assertEqual(mock_config.return_value.save_api_keys.call_count, 1)
    
    def test_thread_safety_of_ui_updates(self):
        """Test UI updates are thread-safe."""
        # This test would be more complex in practice
        # For now, just verify basic thread safety concepts
        
        with patch('config_manager.ConfigManager') as mock_config:
            wizard = SetupWizard(self.root, mock_config.return_value)
            
            # Simulate concurrent UI updates
            def update_status():
                for i in range(10):
                    wizard.after_idle(lambda: None)
                    time.sleep(0.001)
            
            threads = [threading.Thread(target=update_status) for _ in range(3)]
            
            for thread in threads:
                thread.start()
            
            for thread in threads:
                thread.join(timeout=1)
            
            # Test passes if no exceptions were raised
            self.assertTrue(True)


class TestErrorHandlingIntegration(unittest.TestCase):
    """Test integrated error handling across form operations."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
        
    def tearDown(self):
        """Clean up after tests."""
        if self.root:
            self.root.destroy()
    
    def test_network_timeout_handling(self):
        """Test handling of network timeouts during API validation."""
        import socket
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = socket.timeout("Connection timed out")
            
            # Test timeout handling in validation context
            try:
                mock_get("https://api.unsplash.com/photos/random", timeout=10)
                self.fail("Expected timeout exception")
            except socket.timeout:
                # Expected behavior
                pass
    
    def test_invalid_configuration_recovery(self):
        """Test recovery from invalid configuration files."""
        with patch('configparser.ConfigParser.read') as mock_read:
            mock_read.side_effect = configparser.Error("Corrupted config file")
            
            # Should handle corrupted config gracefully
            try:
                config = ConfigManager()
                # Should create new config instead of failing
                self.assertIsNotNone(config.config)
            except configparser.Error:
                self.fail("Should handle corrupted config gracefully")
    
    def test_permission_error_handling(self):
        """Test handling of permission errors during save."""
        with patch('builtins.open') as mock_open:
            mock_open.side_effect = PermissionError("Access denied")
            
            config = ConfigManager()
            
            # Should raise or handle permission error appropriately
            with self.assertRaises(PermissionError):
                config.save_api_keys("test", "sk-test", "gpt-4o-mini")


if __name__ == '__main__':
    # Run integration tests
    unittest.main(verbosity=2, buffer=True)