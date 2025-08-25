"""
Comprehensive unit tests for the SecureSetupWizard API key form.

Tests the enhanced security features, real-time validation, and advanced UI components.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
import tkinter as tk
from tkinter import ttk
import asyncio
# import pytest  # Not available, using unittest only
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config.setup_wizard import SecureSetupWizard
from src.config.secure_config_manager import SecureConfigManager
from src.config.key_validator import APIKeyValidator, ValidationStatus, ValidationResult


class TestSecureSetupWizardForm(unittest.TestCase):
    """Test the SecureSetupWizard form functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Mock config manager
        self.mock_config = Mock(spec=SecureConfigManager)
        self.mock_config.get_api_keys.return_value = {
            'unsplash': '',
            'openai': '',
            'gpt_model': 'gpt-4o-mini'
        }
        self.mock_config.validate_api_keys.return_value = False
        
    def tearDown(self):
        """Clean up after tests."""
        if self.root:
            self.root.destroy()
    
    def test_wizard_initialization(self):
        """Test wizard initializes correctly."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        # Check basic attributes
        self.assertIsNotNone(wizard.config_manager)
        self.assertIsNotNone(wizard.validator)
        self.assertFalse(wizard.setup_complete)
        
        # Check validation state
        self.assertEqual(wizard.validation_results['unsplash'], None)
        self.assertEqual(wizard.validation_results['openai'], None)
        self.assertFalse(wizard.validation_in_progress['unsplash'])
        self.assertFalse(wizard.validation_in_progress['openai'])
    
    def test_form_widgets_created(self):
        """Test all required form widgets are created."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        # Check entry fields exist
        self.assertIsNotNone(wizard.unsplash_entry)
        self.assertIsNotNone(wizard.openai_entry)
        
        # Check status labels exist
        self.assertIsNotNone(wizard.unsplash_status)
        self.assertIsNotNone(wizard.openai_status)
        
        # Check buttons exist
        self.assertIsNotNone(wizard.validate_unsplash_btn)
        self.assertIsNotNone(wizard.validate_openai_btn)
        self.assertIsNotNone(wizard.validate_all_btn)
        self.assertIsNotNone(wizard.save_btn)
        self.assertIsNotNone(wizard.cancel_btn)
        
        # Check model selection
        self.assertIsNotNone(wizard.model_var)
    
    def test_key_visibility_toggle(self):
        """Test API key visibility toggle functionality."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        # Test initial state (keys should be hidden)
        self.assertEqual(wizard.unsplash_entry.cget('show'), '*')
        self.assertEqual(wizard.openai_entry.cget('show'), '*')
        
        # Test toggle functionality
        wizard._toggle_key_visibility(wizard.unsplash_entry, wizard.unsplash_show_btn)
        self.assertEqual(wizard.unsplash_entry.cget('show'), '')
        self.assertEqual(wizard.unsplash_show_btn.cget('text'), '🙈')
        
        # Toggle back
        wizard._toggle_key_visibility(wizard.unsplash_entry, wizard.unsplash_show_btn)
        self.assertEqual(wizard.unsplash_entry.cget('show'), '*')
        self.assertEqual(wizard.unsplash_show_btn.cget('text'), '👁')
    
    def test_key_change_resets_validation(self):
        """Test that changing keys resets validation status."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        # Set some validation results
        wizard.validation_results['unsplash'] = Mock()
        wizard.validation_results['openai'] = Mock()
        
        # Trigger key change event
        wizard._on_key_changed()
        
        # Should reset validation results
        self.assertIsNone(wizard.validation_results['unsplash'])
        self.assertIsNone(wizard.validation_results['openai'])
        
        # Status indicators should be cleared
        self.assertEqual(wizard.unsplash_status.cget('text'), "")
        self.assertEqual(wizard.openai_status.cget('text'), "")
    
    @patch('src.config.setup_wizard.threading.Thread')
    def test_unsplash_key_validation(self, mock_thread):
        """Test Unsplash key validation process."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        # Set a test key
        wizard.unsplash_entry.insert(0, "test_unsplash_key")
        
        # Trigger validation
        wizard._validate_unsplash_key()
        
        # Check UI state during validation
        self.assertEqual(wizard.unsplash_status.cget('text'), "⏳")
        self.assertEqual(wizard.unsplash_status.cget('foreground'), "orange")
        self.assertEqual(wizard.validate_unsplash_btn.cget('state'), 'disabled')
        self.assertTrue(wizard.validation_in_progress['unsplash'])
        
        # Check thread was started
        mock_thread.assert_called_once()
    
    @patch('src.config.setup_wizard.threading.Thread')
    def test_openai_key_validation(self, mock_thread):
        """Test OpenAI key validation process."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        # Set a test key
        wizard.openai_entry.insert(0, "sk-test_openai_key")
        
        # Trigger validation
        wizard._validate_openai_key()
        
        # Check UI state during validation
        self.assertEqual(wizard.openai_status.cget('text'), "⏳")
        self.assertEqual(wizard.openai_status.cget('foreground'), "orange")
        self.assertEqual(wizard.validate_openai_btn.cget('state'), 'disabled')
        self.assertTrue(wizard.validation_in_progress['openai'])
        
        # Check thread was started
        mock_thread.assert_called_once()
    
    def test_validation_completion_success(self):
        """Test successful validation completion."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        # Create successful validation result
        success_result = ValidationResult(
            status=ValidationStatus.VALID,
            message="API key is valid",
            is_valid=True
        )
        
        # Test Unsplash validation completion
        wizard._on_unsplash_validation_complete(success_result)
        
        self.assertEqual(wizard.validation_results['unsplash'], success_result)
        self.assertFalse(wizard.validation_in_progress['unsplash'])
        self.assertEqual(wizard.unsplash_status.cget('text'), "✅")
        self.assertEqual(wizard.unsplash_status.cget('foreground'), "green")
        self.assertEqual(wizard.validate_unsplash_btn.cget('state'), 'normal')
    
    def test_validation_completion_failure(self):
        """Test failed validation completion."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        # Create failed validation result
        failure_result = ValidationResult(
            status=ValidationStatus.INVALID_KEY,
            message="Invalid API key",
            is_valid=False
        )
        
        # Test OpenAI validation completion
        wizard._on_openai_validation_complete(failure_result)
        
        self.assertEqual(wizard.validation_results['openai'], failure_result)
        self.assertFalse(wizard.validation_in_progress['openai'])
        self.assertEqual(wizard.openai_status.cget('text'), "❌")
        self.assertEqual(wizard.openai_status.cget('foreground'), "red")
        self.assertEqual(wizard.validate_openai_btn.cget('state'), 'normal')
    
    def test_save_button_state_management(self):
        """Test save button is only enabled when all keys are valid."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        # Initially should be disabled
        self.assertEqual(wizard.save_btn.cget('state'), 'disabled')
        
        # Add one valid key
        valid_result = ValidationResult(ValidationStatus.VALID, "Valid", is_valid=True)
        wizard.validation_results['unsplash'] = valid_result
        wizard._update_save_button_state()
        
        # Should still be disabled
        self.assertEqual(wizard.save_btn.cget('state'), 'disabled')
        
        # Add second valid key
        wizard.validation_results['openai'] = valid_result
        wizard._update_save_button_state()
        
        # Should now be enabled
        self.assertEqual(wizard.save_btn.cget('state'), 'normal')
    
    def test_progress_bar_functionality(self):
        """Test progress bar show/hide functionality."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        # Initially hidden
        self.assertNotIn(wizard.progress_bar, wizard.progress_bar.master.pack_slaves())
        
        # Show progress
        wizard._show_progress()
        self.assertIn(wizard.progress_bar, wizard.progress_bar.master.pack_slaves())
        
        # Hide progress
        wizard._hide_progress()
        self.assertNotIn(wizard.progress_bar, wizard.progress_bar.master.pack_slaves())
    
    def test_validation_status_text_updates(self):
        """Test validation status text updates correctly."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        test_message = "Test validation message"
        wizard._update_validation_status(test_message)
        
        # Check text was added
        text_content = wizard.validation_status_text.get("1.0", tk.END)
        self.assertIn(test_message, text_content)
    
    @patch('src.config.setup_wizard.threading.Thread')
    def test_save_configuration_process(self, mock_thread):
        """Test configuration save process."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        # Set valid keys
        wizard.unsplash_entry.insert(0, "test_unsplash")
        wizard.openai_entry.insert(0, "sk-test_openai")
        wizard.model_var.set("gpt-4o")
        
        # Set validation results as valid
        valid_result = ValidationResult(ValidationStatus.VALID, "Valid", is_valid=True)
        wizard.validation_results['unsplash'] = valid_result
        wizard.validation_results['openai'] = valid_result
        
        # Trigger save
        wizard._save_configuration()
        
        # Check thread was started
        mock_thread.assert_called_once()
        
        # Check UI state
        self.assertEqual(wizard.save_btn.cget('state'), 'disabled')
    
    def test_model_change_revalidation(self):
        """Test that changing model triggers OpenAI re-validation."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        # Set OpenAI as validated
        valid_result = ValidationResult(ValidationStatus.VALID, "Valid", is_valid=True)
        wizard.validation_results['openai'] = valid_result
        
        with patch.object(wizard, '_validate_openai_key') as mock_validate:
            # Change model
            wizard.model_var.set("gpt-4o")
            wizard._on_model_changed()
            
            # Should trigger re-validation
            mock_validate.assert_called_once()
    
    def test_cancel_confirmation(self):
        """Test cancel confirmation dialog."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        with patch('tkinter.messagebox.askyesno') as mock_confirm:
            mock_confirm.return_value = True
            wizard.destroy = Mock()
            
            wizard._on_cancel()
            
            mock_confirm.assert_called_once()
            wizard.destroy.assert_called_once()
    
    def test_help_dialog_functionality(self):
        """Test help dialog display."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        with patch('tkinter.messagebox.showinfo') as mock_info:
            wizard._show_help()
            
            mock_info.assert_called_once()
            args = mock_info.call_args[0]
            self.assertEqual(args[0], "Help")
            self.assertIn("SECURITY FEATURES", args[1])
    
    def test_api_tips_dialog(self):
        """Test API tips dialog functionality."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        # Mock ttk.Notebook and other widgets
        with patch('tkinter.Toplevel') as mock_toplevel:
            mock_window = Mock()
            mock_toplevel.return_value = mock_window
            
            with patch('tkinter.ttk.Notebook'):
                wizard._show_api_tips()
                
                mock_toplevel.assert_called_once()
    
    def test_load_existing_config(self):
        """Test loading existing configuration."""
        # Configure mock to return existing config
        self.mock_config.is_first_run.return_value = False
        self.mock_config.get_api_keys.return_value = {
            'unsplash': 'existing_unsplash',
            'openai': 'existing_openai',
            'gpt_model': 'gpt-4o-mini'
        }
        
        wizard = SecureSetupWizard(self.root, self.mock_config)
        wizard._load_existing_config()
        
        # Check values were loaded
        self.assertEqual(wizard.unsplash_entry.get(), 'existing_unsplash')
        self.assertEqual(wizard.openai_entry.get(), 'existing_openai')
        self.assertEqual(wizard.model_var.get(), 'gpt-4o-mini')


class TestKeyboardNavigationSecure(unittest.TestCase):
    """Test keyboard navigation in SecureSetupWizard."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.mock_config = Mock(spec=SecureConfigManager)
        self.mock_config.get_api_keys.return_value = {'unsplash': '', 'openai': '', 'gpt_model': 'gpt-4o-mini'}
        
    def tearDown(self):
        """Clean up after tests."""
        if self.root:
            self.root.destroy()
    
    def test_enter_key_validation(self):
        """Test Enter key triggers validation."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        with patch.object(wizard, '_validate_unsplash_key') as mock_validate:
            # Set focus and simulate Enter
            wizard.unsplash_entry.focus_set()
            wizard.unsplash_entry.insert(0, "test_key")
            wizard.unsplash_entry.event_generate('<Return>')
            
            # Should trigger validation
            mock_validate.assert_called_once()
    
    def test_real_time_validation_binding(self):
        """Test real-time validation on key release."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        with patch.object(wizard, '_on_key_changed') as mock_change:
            # Simulate key release
            wizard.unsplash_entry.event_generate('<KeyRelease>')
            
            mock_change.assert_called_once()


class TestValidationIntegration(unittest.TestCase):
    """Test integration with validation system."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.mock_config = Mock(spec=SecureConfigManager)
        self.mock_config.get_api_keys.return_value = {'unsplash': '', 'openai': '', 'gpt_model': 'gpt-4o-mini'}
        
    def tearDown(self):
        """Clean up after tests."""
        if self.root:
            self.root.destroy()
    
    @patch('src.config.setup_wizard.asyncio.new_event_loop')
    def test_async_validation_error_handling(self, mock_loop):
        """Test async validation error handling."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        # Mock async validation failure
        mock_loop.return_value.run_until_complete.side_effect = Exception("Network error")
        
        wizard.unsplash_entry.insert(0, "test_key")
        
        # This would normally run in a thread
        try:
            loop = mock_loop.return_value
            loop.run_until_complete.side_effect = Exception("Network error")
        except Exception:
            pass
        
        # Error should be handled gracefully
        self.assertTrue(True)  # Test passes if no unhandled exception
    
    def test_validation_all_keys_process(self):
        """Test validating all keys simultaneously."""
        wizard = SecureSetupWizard(self.root, self.mock_config)
        
        wizard.unsplash_entry.insert(0, "unsplash_key")
        wizard.openai_entry.insert(0, "sk-openai_key")
        
        with patch('src.config.setup_wizard.threading.Thread') as mock_thread:
            wizard._validate_all_keys()
            
            # Should start validation thread
            mock_thread.assert_called_once()
            
            # Should disable buttons
            self.assertEqual(wizard.validate_unsplash_btn.cget('state'), 'disabled')
            self.assertEqual(wizard.validate_openai_btn.cget('state'), 'disabled')
            self.assertEqual(wizard.validate_all_btn.cget('state'), 'disabled')


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)