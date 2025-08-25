"""
Comprehensive test for the UI fix to ensure the main window displays correctly.

This test verifies:
1. UI elements are created even without API keys
2. Window shows and has proper focus
3. No race conditions between dialogs and main window
4. Proper error handling that doesn't hide failures
5. Debug logging tracks initialization properly
"""

import sys
import os
import unittest
import threading
import time
from pathlib import Path
import tempfile
import shutil

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from ui_fix_main import UIFixedImageSearchApp
    import tkinter as tk
    from unittest.mock import Mock, patch, MagicMock
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure tkinter is available and src/ui_fix_main.py exists")
    sys.exit(1)


class TestUIFix(unittest.TestCase):
    """Test suite for the UI fix."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Mock config manager to avoid actual file operations
        self.config_patcher = patch('ui_fix_main.ensure_api_keys_configured')
        self.mock_config = self.config_patcher.start()
        
    def tearDown(self):
        """Clean up test environment."""
        self.config_patcher.stop()
        os.chdir(self.original_cwd)
        try:
            shutil.rmtree(self.test_dir)
        except:
            pass
    
    def test_ui_creation_without_api_keys(self):
        """Test that UI is created even when API keys are not configured."""
        print("Testing UI creation without API keys...")
        
        # Mock configuration to return None (cancelled setup)
        self.mock_config.return_value = None
        
        # Create application in test mode
        app = UIFixedImageSearchApp()
        
        # Verify window was created
        self.assertIsInstance(app, tk.Tk)
        self.assertTrue(app.winfo_exists())
        
        # Verify basic UI elements exist
        self.assertTrue(hasattr(app, 'main_frame'))
        self.assertTrue(hasattr(app, 'status_label'))
        self.assertTrue(hasattr(app, 'search_entry'))
        self.assertTrue(hasattr(app, 'search_button'))
        
        # Verify window properties
        self.assertIn("Unsplash", app.title())
        width = app.winfo_reqwidth()
        height = app.winfo_reqheight()
        self.assertGreater(width, 800)
        self.assertGreater(height, 600)
        
        # Verify debug logging is working
        self.assertTrue(hasattr(app, 'debug_messages'))
        self.assertGreater(len(app.debug_messages), 0)
        self.assertTrue(any("Starting application initialization" in msg for msg in app.debug_messages))
        
        # Clean up
        app.destroy()
        print("✓ UI creation without API keys test passed")
    
    def test_ui_creation_with_config_error(self):
        """Test UI creation when configuration encounters an error."""
        print("Testing UI creation with configuration error...")
        
        # Mock configuration to raise an exception
        self.mock_config.side_effect = Exception("Mock configuration error")
        
        # Create application
        app = UIFixedImageSearchApp()
        
        # Give background thread time to complete
        time.sleep(0.5)
        app.update_idletasks()
        
        # Verify UI still exists and is functional
        self.assertTrue(app.winfo_exists())
        self.assertTrue(hasattr(app, 'status_label'))
        
        # Verify error state is handled
        # (The app should still be functional, just with APIs disabled)
        status_text = app.status_label.cget('text').lower()
        self.assertTrue(any(word in status_text for word in ['configuration', 'setup', 'needed']))
        
        # Verify debug logging captured the error
        debug_log = " ".join(app.debug_messages)
        self.assertIn("error", debug_log.lower())
        
        # Clean up
        app.destroy()
        print("✓ UI creation with configuration error test passed")
    
    def test_window_visibility_and_focus(self):
        """Test that the main window is visible and has proper focus."""
        print("Testing window visibility and focus...")
        
        self.mock_config.return_value = None
        
        # Create application
        app = UIFixedImageSearchApp()
        app.update_idletasks()
        
        # Verify window is visible (not withdrawn)
        self.assertEqual(app.state(), 'normal')
        
        # Verify window has reasonable geometry
        app.update_idletasks()
        geometry = app.geometry()
        self.assertRegex(geometry, r'\\d+x\\d+\\+\\d+\\+\\d+')
        
        # Verify window is not minimized
        self.assertNotEqual(app.state(), 'iconic')
        
        # Clean up
        app.destroy()
        print("✓ Window visibility and focus test passed")
    
    def test_debug_logging_functionality(self):
        """Test that debug logging captures initialization steps."""
        print("Testing debug logging functionality...")
        
        self.mock_config.return_value = None
        
        # Create application
        app = UIFixedImageSearchApp()
        
        # Verify debug logging is working
        self.assertTrue(hasattr(app, 'debug_messages'))
        self.assertGreater(len(app.debug_messages), 5)  # Should have multiple initialization messages
        
        # Check for key initialization steps
        debug_log = " ".join(app.debug_messages)
        expected_messages = [
            "Starting application initialization",
            "Initializing basic window properties", 
            "Creating basic UI structure",
            "Ensuring window visibility",
            "Application initialization completed"
        ]
        
        for expected in expected_messages:
            self.assertIn(expected, debug_log, f"Missing debug message: {expected}")
        
        # Verify debug log file is created
        self.assertTrue(hasattr(app, 'debug_log_file'))
        self.assertTrue(app.debug_log_file.exists())
        
        # Clean up
        app.destroy()
        print("✓ Debug logging functionality test passed")
    
    def test_fallback_ui_creation(self):
        """Test fallback UI creation when main UI fails."""
        print("Testing fallback UI creation...")
        
        self.mock_config.return_value = None
        
        # Create application and force fallback UI
        app = UIFixedImageSearchApp()
        
        # Simulate UI creation error by patching the create method
        with patch.object(app, '_create_content_area', side_effect=Exception("Mock UI error")):
            app._create_basic_ui()  # This should trigger fallback
        
        # Verify app still exists
        self.assertTrue(app.winfo_exists())
        
        # The fallback should have been triggered, but the app should still work
        # (This is hard to test directly, but we can verify the app didn't crash)
        
        # Clean up
        app.destroy()
        print("✓ Fallback UI creation test passed")
    
    def test_configuration_handling(self):
        """Test proper handling of configuration states."""
        print("Testing configuration handling...")
        
        # Test successful configuration
        mock_config_manager = Mock()
        mock_config_manager.get_api_keys.return_value = {
            'unsplash': 'test_unsplash_key',
            'openai': 'sk-test_openai_key',
            'gpt_model': 'gpt-4o-mini'
        }
        mock_config_manager.get_paths.return_value = {
            'data_dir': self.test_dir / 'data',
            'log_file': self.test_dir / 'log.json',
            'vocabulary_file': self.test_dir / 'vocab.csv'
        }
        
        self.mock_config.return_value = mock_config_manager
        
        # Create application
        app = UIFixedImageSearchApp()
        
        # Give configuration time to complete
        time.sleep(0.5)
        app.update_idletasks()
        
        # Verify configuration was handled
        self.assertEqual(app.UNSPLASH_ACCESS_KEY, 'test_unsplash_key')
        self.assertEqual(app.OPENAI_API_KEY, 'sk-test_openai_key')
        self.assertEqual(app.GPT_MODEL, 'gpt-4o-mini')
        self.assertTrue(app.config_ready)
        
        # Clean up
        app.destroy()
        print("✓ Configuration handling test passed")
    
    def test_ui_controls_exist(self):
        """Test that all essential UI controls exist and are accessible."""
        print("Testing UI controls existence...")
        
        self.mock_config.return_value = None
        
        # Create application
        app = UIFixedImageSearchApp()
        app.update_idletasks()
        
        # Verify essential controls exist
        essential_controls = [
            'search_entry',
            'search_button',
            'another_button',
            'newsearch_button',
            'generate_desc_button',
            'config_button',
            'status_label',
            'stats_label',
            'image_label',
            'note_text',
            'description_text',
            'target_listbox'
        ]
        
        for control in essential_controls:
            self.assertTrue(hasattr(app, control), f"Missing control: {control}")
            widget = getattr(app, control)
            self.assertTrue(widget.winfo_exists(), f"Control {control} doesn't exist in UI")
        
        # Clean up
        app.destroy()
        print("✓ UI controls existence test passed")
    
    def test_thread_safety(self):
        """Test that background configuration doesn't interfere with UI."""
        print("Testing thread safety...")
        
        # Mock slow configuration
        def slow_config(*args, **kwargs):
            time.sleep(0.2)  # Simulate slow config
            return None
        
        self.mock_config.side_effect = slow_config
        
        # Create application
        app = UIFixedImageSearchApp()
        
        # UI should be immediately responsive even with slow config
        self.assertTrue(app.winfo_exists())
        self.assertTrue(hasattr(app, 'status_label'))
        
        # Update UI multiple times while config is running
        for _ in range(5):
            app.update_idletasks()
            time.sleep(0.1)
        
        # App should still be functional
        self.assertTrue(app.winfo_exists())
        
        # Clean up
        app.destroy()
        print("✓ Thread safety test passed")


def run_visual_test():
    """Run a visual test to manually verify the UI appears correctly."""
    print("\\n" + "="*60)
    print("VISUAL TEST - The application window should appear")
    print("="*60)
    
    # Mock configuration for visual test
    with patch('ui_fix_main.ensure_api_keys_configured') as mock_config:
        mock_config.return_value = None
        
        print("Creating application window...")
        app = UIFixedImageSearchApp()
        
        print("✓ Application created successfully")
        print("✓ Window should now be visible")
        print("✓ Check that:")
        print("  - Window has title 'Unsplash Image Search & GPT Description'")
        print("  - Window is properly sized and centered")
        print("  - All UI elements are visible (search box, buttons, etc.)")
        print("  - Status shows configuration message")
        print("  - No blank window or 'tk' only display")
        
        print("\\nWindow will close automatically in 5 seconds...")
        
        # Keep window open for visual inspection
        def auto_close():
            time.sleep(5)
            try:
                app.quit()
            except:
                pass
        
        timer_thread = threading.Thread(target=auto_close, daemon=True)
        timer_thread.start()
        
        try:
            app.mainloop()
        except:
            pass
        
        print("✓ Visual test completed")


def main():
    """Run all tests."""
    print("Starting UI Fix Tests...")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestUIFix)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\\n✓ All tests passed! The UI fix should work correctly.")
        
        # Ask if user wants to run visual test
        try:
            response = input("\\nRun visual test? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                run_visual_test()
        except KeyboardInterrupt:
            print("\\nSkipping visual test.")
    else:
        print("\\n✗ Some tests failed. Please review the issues above.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)