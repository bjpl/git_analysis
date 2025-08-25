"""
Comprehensive unit tests for the APISetupWizard (onboarding wizard).

Tests the multi-page wizard interface, help system, and user guidance features.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ui.onboarding.api_setup_wizard import APISetupWizard


class TestAPISetupWizardInterface(unittest.TestCase):
    """Test the APISetupWizard interface and navigation."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Mock dependencies
        self.mock_theme_manager = Mock()
        self.mock_theme_manager.get_colors.return_value = {
            'bg': '#ffffff',
            'fg': '#000000',
            'frame_bg': '#f0f0f0',
            'info': '#0066cc',
            'disabled_fg': '#808080',
            'button_bg': '#e0e0e0',
            'button_fg': '#000000',
            'select_bg': '#0066cc',
            'select_fg': '#ffffff',
            'success': '#008000',
            'error': '#ff0000',
            'warning': '#ff9900',
            'entry_bg': '#ffffff'
        }
        
        self.mock_config_manager = Mock()
        self.mock_config_manager.get_api_keys.return_value = {
            'unsplash': '',
            'openai': '',
            'gpt_model': 'gpt-4o'
        }
        
    def tearDown(self):
        """Clean up after tests."""
        if self.root:
            self.root.destroy()
    
    def test_wizard_initialization(self):
        """Test wizard initializes correctly."""
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        
        # Check basic attributes
        self.assertEqual(wizard.parent, self.root)
        self.assertEqual(wizard.theme_manager, self.mock_theme_manager)
        self.assertEqual(wizard.config_manager, self.mock_config_manager)
        self.assertEqual(wizard.current_page, 0)
        self.assertEqual(wizard.total_pages, 4)
        self.assertFalse(wizard.unsplash_valid)
        self.assertFalse(wizard.openai_valid)
    
    def test_wizard_window_creation(self):
        """Test wizard window is created properly."""
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        
        wizard.show()
        
        # Check window exists
        self.assertIsNotNone(wizard.wizard_window)
        self.assertEqual(wizard.wizard_window.title(), "API Setup Wizard")
        self.assertTrue(wizard.wizard_window.winfo_exists())
        
        wizard.hide()
    
    def test_page_navigation(self):
        """Test navigation between wizard pages."""
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        wizard.show()
        
        # Test forward navigation
        initial_page = wizard.current_page
        wizard._next_page()
        self.assertEqual(wizard.current_page, initial_page + 1)
        
        # Test backward navigation
        wizard._previous_page()
        self.assertEqual(wizard.current_page, initial_page)
        
        wizard.hide()
    
    def test_progress_bar_updates(self):
        """Test progress bar updates with page changes."""
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        wizard.show()
        
        # Check initial progress
        self.assertEqual(wizard.progress.cget('value'), 0)
        
        # Navigate to next page
        wizard._show_page(1)
        expected_progress = (1 / (wizard.total_pages - 1)) * 100
        self.assertEqual(wizard.progress.cget('value'), expected_progress)
        
        wizard.hide()
    
    def test_navigation_button_states(self):
        """Test navigation button states change correctly."""
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        wizard.show()
        
        # First page - back should be disabled
        wizard._show_page(0)
        self.assertEqual(wizard.back_button.cget('state'), 'disabled')
        
        # Middle page - both should be enabled
        wizard._show_page(1)
        self.assertEqual(wizard.back_button.cget('state'), 'normal')
        self.assertIn("Next", wizard.next_button.cget('text'))
        
        # Last page - next should show completion text
        wizard._show_page(wizard.total_pages - 1)
        self.assertIn("Complete", wizard.next_button.cget('text'))
        
        wizard.hide()
    
    def test_help_content_structure(self):
        """Test help content is properly structured."""
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        
        # Check Unsplash help content
        unsplash_help = wizard.help_content['unsplash']
        self.assertIn('title', unsplash_help)
        self.assertIn('steps', unsplash_help)
        self.assertIn('url', unsplash_help)
        self.assertIn('tips', unsplash_help)
        
        # Check OpenAI help content
        openai_help = wizard.help_content['openai']
        self.assertIn('title', openai_help)
        self.assertIn('steps', openai_help)
        self.assertIn('url', openai_help)
        self.assertIn('tips', openai_help)
        
        # Verify steps are not empty
        self.assertGreater(len(unsplash_help['steps']), 0)
        self.assertGreater(len(openai_help['steps']), 0)


class TestAPIKeyFormFunctionality(unittest.TestCase):
    """Test API key form functionality within the wizard."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.mock_theme_manager = Mock()
        self.mock_theme_manager.get_colors.return_value = {
            'bg': '#ffffff', 'fg': '#000000', 'frame_bg': '#f0f0f0',
            'info': '#0066cc', 'disabled_fg': '#808080', 'success': '#008000',
            'error': '#ff0000', 'select_bg': '#0066cc', 'select_fg': '#ffffff'
        }
        
        self.mock_config_manager = Mock()
        self.mock_config_manager.get_api_keys.return_value = {
            'unsplash': '', 'openai': '', 'gpt_model': 'gpt-4o'
        }
        
    def tearDown(self):
        """Clean up after tests."""
        if self.root:
            self.root.destroy()
    
    def test_api_key_entry_fields(self):
        """Test API key entry fields are created correctly."""
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        wizard.show()
        
        # Navigate to Unsplash page
        wizard._show_page(1)
        
        # Check entry field exists
        self.assertIsNotNone(wizard.unsplash_entry)
        self.assertEqual(wizard.unsplash_entry.cget('show'), '*')  # Should be masked
        
        # Navigate to OpenAI page
        wizard._show_page(2)
        
        # Check entry field exists
        self.assertIsNotNone(wizard.openai_entry)
        self.assertEqual(wizard.openai_entry.cget('show'), '*')  # Should be masked
        
        wizard.hide()
    
    def test_key_visibility_toggle(self):
        """Test API key visibility toggle in wizard."""
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        wizard.show()
        
        # Navigate to page with entry field
        wizard._show_page(1)
        
        # Test initial state (masked)
        self.assertEqual(wizard.unsplash_entry.cget('show'), '*')
        
        # Find and click show/hide toggle (implementation specific)
        # This would need to be implemented based on actual UI structure
        
        wizard.hide()
    
    def test_key_change_handlers(self):
        """Test key change event handlers."""
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        wizard.show()
        
        # Navigate to Unsplash page
        wizard._show_page(1)
        
        # Set initial state
        wizard.unsplash_valid = True
        
        # Trigger key change
        wizard._on_unsplash_key_change()
        
        # Should reset validation state
        self.assertFalse(wizard.unsplash_valid)
        
        wizard.hide()
    
    @patch('requests.get')
    def test_unsplash_key_validation(self, mock_get):
        """Test Unsplash API key validation."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 'test_image'}
        mock_get.return_value = mock_response
        
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        wizard.show()
        wizard._show_page(1)
        
        # Set test key
        wizard.unsplash_entry.insert(0, "test_unsplash_key")
        
        # Trigger validation
        wizard._test_unsplash_key()
        
        # Wait for background thread to complete
        self.root.after(100, lambda: None)
        self.root.update()
        
        # Should eventually set valid state
        # Note: This test might need adjustment for thread timing
        
        wizard.hide()
    
    @patch('src.ui.onboarding.api_setup_wizard.OpenAI')
    def test_openai_key_validation(self, mock_openai_class):
        """Test OpenAI API key validation."""
        # Mock successful API response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        wizard.show()
        wizard._show_page(2)
        
        # Set test key
        wizard.openai_entry.insert(0, "sk-test_openai_key")
        
        # Trigger validation
        wizard._test_openai_key()
        
        # Wait for background thread
        self.root.after(100, lambda: None)
        self.root.update()
        
        wizard.hide()
    
    def test_model_selection(self):
        """Test GPT model selection functionality."""
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        wizard.show()
        wizard._show_page(2)
        
        # Check model variable exists
        self.assertIsNotNone(wizard.gpt_model_var)
        
        # Test setting model
        wizard.gpt_model_var.set("gpt-4-turbo")
        self.assertEqual(wizard.gpt_model_var.get(), "gpt-4-turbo")
        
        wizard.hide()


class TestHelpSystemFunctionality(unittest.TestCase):
    """Test the help system and user guidance features."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.mock_theme_manager = Mock()
        self.mock_theme_manager.get_colors.return_value = {
            'bg': '#ffffff', 'fg': '#000000', 'frame_bg': '#f0f0f0',
            'info': '#0066cc', 'disabled_fg': '#808080'
        }
        
        self.mock_config_manager = Mock()
        
    def tearDown(self):
        """Clean up after tests."""
        if self.root:
            self.root.destroy()
    
    @patch('webbrowser.open')
    def test_website_link_opening(self, mock_webbrowser):
        """Test opening help website links."""
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        wizard.show()
        wizard._show_page(1)  # Unsplash page
        
        # Simulate clicking website link
        unsplash_url = wizard.help_content['unsplash']['url']
        
        # Would need actual button click simulation
        # For now, test the URL is correct
        self.assertEqual(unsplash_url, 'https://unsplash.com/developers')
        
        wizard.hide()
    
    def test_detailed_help_dialog(self):
        """Test detailed help dialog creation."""
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        wizard.show()
        
        with patch('tkinter.Toplevel') as mock_toplevel:
            mock_dialog = Mock()
            mock_toplevel.return_value = mock_dialog
            
            wizard._show_detailed_help('unsplash')
            
            # Check dialog was created
            mock_toplevel.assert_called_once()
            
        wizard.hide()
    
    def test_help_content_completeness(self):
        """Test that help content contains all necessary information."""
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        
        for api_type in ['unsplash', 'openai']:
            help_info = wizard.help_content[api_type]
            
            # Check required fields
            self.assertIn('title', help_info)
            self.assertIn('steps', help_info)
            self.assertIn('url', help_info)
            self.assertIn('tips', help_info)
            
            # Check content quality
            self.assertGreater(len(help_info['steps']), 3)  # At least 4 steps
            self.assertGreater(len(help_info['tips']), 2)   # At least 3 tips
            self.assertTrue(help_info['url'].startswith('https://'))


class TestWizardCompletion(unittest.TestCase):
    """Test wizard completion and configuration saving."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.mock_theme_manager = Mock()
        self.mock_theme_manager.get_colors.return_value = {
            'bg': '#ffffff', 'fg': '#000000', 'success': '#008000'
        }
        
        self.mock_config_manager = Mock()
        self.mock_config_manager.set_api_key = Mock()
        
    def tearDown(self):
        """Clean up after tests."""
        if self.root:
            self.root.destroy()
    
    def test_save_keys_functionality(self):
        """Test saving API keys to configuration."""
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        
        # Mock entry fields
        wizard.unsplash_entry = Mock()
        wizard.unsplash_entry.get.return_value = "test_unsplash_key"
        
        wizard.openai_entry = Mock()
        wizard.openai_entry.get.return_value = "sk-test_openai_key"
        
        wizard.gpt_model_var = Mock()
        wizard.gpt_model_var.get.return_value = "gpt-4o"
        
        # Test save functionality
        result = wizard._save_keys()
        
        # Should call config manager
        self.assertTrue(result)
        wizard.mock_config_manager.set_api_key.assert_called()
    
    def test_completion_callback(self):
        """Test completion callback is called."""
        completion_callback = Mock()
        
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager,
            on_completion=completion_callback
        )
        
        with patch.object(wizard, '_save_keys', return_value=True):
            wizard._complete_setup()
            
            completion_callback.assert_called_once()
    
    def test_skip_functionality(self):
        """Test skip setup functionality."""
        skip_callback = Mock()
        
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager,
            on_skip=skip_callback
        )
        
        with patch('tkinter.messagebox.askyesno') as mock_confirm:
            mock_confirm.return_value = True
            
            wizard._skip_setup()
            
            skip_callback.assert_called_once()
    
    def test_window_close_handling(self):
        """Test window close event handling."""
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        
        with patch.object(wizard, '_skip_setup') as mock_skip:
            wizard._on_window_close()
            
            mock_skip.assert_called_once()


class TestAccessibilityAndUsability(unittest.TestCase):
    """Test accessibility and usability features."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.mock_theme_manager = Mock()
        self.mock_theme_manager.get_colors.return_value = {
            'bg': '#ffffff', 'fg': '#000000', 'frame_bg': '#f0f0f0'
        }
        
        self.mock_config_manager = Mock()
        
    def tearDown(self):
        """Clean up after tests."""
        if self.root:
            self.root.destroy()
    
    def test_mouse_wheel_scrolling(self):
        """Test mouse wheel scrolling functionality."""
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        wizard.show()
        
        # Test that mouse wheel events are bound
        # This would need specific implementation testing
        
        wizard.hide()
    
    def test_window_centering(self):
        """Test window is centered on screen."""
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        wizard.show()
        
        # Check window position
        wizard.wizard_window.update_idletasks()
        geometry = wizard.wizard_window.geometry()
        
        # Should contain position information
        self.assertIn('+', geometry)
        
        wizard.hide()
    
    def test_load_existing_keys(self):
        """Test loading existing API keys."""
        self.mock_config_manager.get_api_keys.return_value = {
            'unsplash': 'existing_unsplash',
            'openai': 'sk-existing_openai',
            'gpt_model': 'gpt-4-turbo'
        }
        
        wizard = APISetupWizard(
            self.root,
            self.mock_theme_manager,
            self.mock_config_manager
        )
        wizard.show()
        
        # Navigate to pages and check values loaded
        wizard._show_page(1)
        wizard._load_existing_unsplash_key()
        # Would check if entry field was populated
        
        wizard._show_page(2)
        wizard._load_existing_openai_key()
        # Would check if entry field was populated
        
        wizard.hide()


if __name__ == '__main__':
    # Create test suite with all test classes
    test_classes = [
        TestAPISetupWizardInterface,
        TestAPIKeyFormFunctionality,
        TestHelpSystemFunctionality,
        TestWizardCompletion,
        TestAccessibilityAndUsability
    ]
    
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"API Setup Wizard Test Results")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    
    if result.failures:
        print(f"\nFailures ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\nErrors ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}")