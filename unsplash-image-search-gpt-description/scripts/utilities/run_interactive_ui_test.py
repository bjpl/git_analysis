#!/usr/bin/env python3
"""
Interactive UI Test Runner for Visual Verification

This script launches the application in test mode to visually verify:
1. Main window renders correctly with all widgets
2. API configuration modal displays properly
3. Application works with and without API keys
4. UI remains responsive and functional

Usage:
    python run_interactive_ui_test.py [--with-keys] [--without-keys] [--modal-only]

Options:
    --with-keys     Test with mock API keys
    --without-keys  Test without API keys (degraded mode)
    --modal-only    Show only the API configuration modal
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock, patch
import argparse
import time
import threading

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class InteractiveUITest:
    """Interactive UI test runner with visual verification."""
    
    def __init__(self):
        self.temp_config_dir = None
        self.test_results = []
        
    def setup_test_environment(self):
        """Set up test environment."""
        self.temp_config_dir = tempfile.mkdtemp(prefix="interactive_ui_test_")
        print(f"Test environment: {self.temp_config_dir}")
    
    def cleanup_test_environment(self):
        """Clean up test environment."""
        if self.temp_config_dir and Path(self.temp_config_dir).exists():
            shutil.rmtree(self.temp_config_dir)
            print("Test environment cleaned up")
    
    def test_main_window_with_keys(self):
        """Test main window with valid API keys."""
        print("\\n=== Testing Main Window with API Keys ===")
        
        try:
            with patch('config_manager.ConfigManager') as mock_config_class:
                mock_config = Mock()
                mock_config.get_api_keys.return_value = {
                    'unsplash': 'test-unsplash-key-1234567890123456789012345678901234567890',
                    'openai': 'sk-testopenaikey1234567890123456789012345678901234567890',
                    'gpt_model': 'gpt-4o-mini'
                }
                mock_config.get_paths.return_value = {
                    'data_dir': Path(self.temp_config_dir),
                    'log_file': Path(self.temp_config_dir) / 'session_log.json',
                    'vocabulary_file': Path(self.temp_config_dir) / 'vocabulary.csv'
                }
                mock_config.validate_api_keys.return_value = True
                mock_config.config = Mock()
                mock_config.config.get.return_value = '100'
                mock_config.config.set = Mock()
                mock_config.config.write = Mock()
                mock_config_class.return_value = mock_config
                
                with patch('main.ensure_api_keys_configured', return_value=mock_config):
                    from main import ImageSearchApp
                    
                    print("Creating main application window...")
                    app = ImageSearchApp()
                    
                    # Display test instructions
                    self.show_test_instructions(app, "Main Window with API Keys")
                    
                    # Run the app
                    app.mainloop()
                    
        except Exception as e:
            print(f"Error testing main window with keys: {e}")
            import traceback
            traceback.print_exc()
    
    def test_main_window_without_keys(self):
        """Test main window without API keys (degraded mode)."""
        print("\\n=== Testing Main Window without API Keys ===")
        
        try:
            with patch('config_manager.ConfigManager') as mock_config_class:
                mock_config = Mock()
                mock_config.get_api_keys.return_value = {
                    'unsplash': '',
                    'openai': '',
                    'gpt_model': 'gpt-4o-mini'
                }
                mock_config.get_paths.return_value = {
                    'data_dir': Path(self.temp_config_dir),
                    'log_file': Path(self.temp_config_dir) / 'session_log.json',
                    'vocabulary_file': Path(self.temp_config_dir) / 'vocabulary.csv'
                }
                mock_config.validate_api_keys.return_value = False
                mock_config.config = Mock()
                mock_config.config.get.return_value = '100'
                mock_config.config.set = Mock()
                mock_config.config.write = Mock()
                mock_config_class.return_value = mock_config
                
                # Mock ensure function to return None (user cancelled setup)
                with patch('main.ensure_api_keys_configured', return_value=None):
                    from main import ImageSearchApp
                    
                    print("Creating main application window without API keys...")
                    app = ImageSearchApp()
                    
                    # Display test instructions
                    self.show_test_instructions(app, "Main Window without API Keys (Degraded Mode)")
                    
                    # Run the app
                    app.mainloop()
                    
        except Exception as e:
            print(f"Error testing main window without keys: {e}")
            import traceback
            traceback.print_exc()
    
    def test_api_configuration_modal(self):
        """Test API configuration modal."""
        print("\\n=== Testing API Configuration Modal ===")
        
        try:
            # Create root window
            root = tk.Tk()
            root.title("Test Parent Window")
            root.geometry("400x200")
            
            # Add instructions to root window
            instruction_frame = ttk.Frame(root, padding="20")
            instruction_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(
                instruction_frame,
                text="API Configuration Modal Test",
                font=('TkDefaultFont', 14, 'bold')
            ).pack(pady=(0, 10))
            
            ttk.Label(
                instruction_frame,
                text="Click the button below to open the API configuration modal.\\n"
                      "Test that:\\n"
                      "• Modal opens properly\\n"
                      "• Form validation works\\n"
                      "• Modal doesn't block this parent window\\n"
                      "• Modal can be cancelled or submitted",
                wraplength=350
            ).pack(pady=(0, 20))
            
            def show_modal():
                with patch('config_manager.ConfigManager') as mock_config_class:
                    mock_config = Mock()
                    mock_config.get_api_keys.return_value = {
                        'unsplash': '',
                        'openai': '',
                        'gpt_model': 'gpt-4o-mini'
                    }
                    mock_config.validate_api_keys.return_value = False
                    mock_config.save_api_keys = Mock()
                    mock_config.config_file = Path(self.temp_config_dir) / 'config.ini'
                    mock_config_class.return_value = mock_config
                    
                    from config_manager import SetupWizard
                    
                    modal = SetupWizard(root, mock_config)
                    
                    # Show result after modal closes
                    def on_modal_close():
                        result = "User completed setup" if modal.result else "User cancelled setup"
                        messagebox.showinfo("Modal Result", f"Modal closed. Result: {result}")
                    
                    root.after(100, lambda: root.wait_window(modal))
                    root.after(200, on_modal_close)
            
            ttk.Button(
                instruction_frame,
                text="Open API Configuration Modal",
                command=show_modal
            ).pack()
            
            ttk.Button(
                instruction_frame,
                text="Close Test",
                command=root.destroy
            ).pack(pady=(10, 0))
            
            # Run the root window
            root.mainloop()
            
        except Exception as e:
            print(f"Error testing API modal: {e}")
            import traceback
            traceback.print_exc()
    
    def show_test_instructions(self, app, test_name):
        """Show test instructions in a separate window."""
        instructions_window = tk.Toplevel(app)
        instructions_window.title(f"Test Instructions: {test_name}")
        instructions_window.geometry("500x400")
        instructions_window.attributes('-topmost', True)
        
        frame = ttk.Frame(instructions_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        title = ttk.Label(
            frame,
            text=f"UI Test: {test_name}",
            font=('TkDefaultFont', 14, 'bold')
        )
        title.pack(pady=(0, 20))
        
        instructions_text = f\"\"\"Please verify the following:

MAIN WINDOW CHECKS:
✓ Window displays correctly with proper size (1100x800)
✓ All widgets are visible and properly arranged:
  • Search entry field and button
  • "Another Image" and "New Search" buttons
  • Theme toggle and Export buttons
  • Image preview area (left side)
  • Text areas for notes and description (right side)
  • Extracted phrases and vocabulary sections (bottom right)
  • Status bar and statistics at bottom

FUNCTIONALITY CHECKS:
✓ Enter text in search field
✓ Click buttons to verify they respond
✓ Check theme toggle works (light/dark switch)
✓ Verify menus and tooltips appear
✓ Test keyboard shortcuts (Ctrl+T for theme, etc.)

API KEYS STATUS:
{f"✓ With API keys: Search should work" if "with API Keys" in test_name else "⚠ Without API keys: App runs in limited mode"}

Close this instruction window, then test the main application.
Click the main window's close button when done testing.
\"\"\"
        
        instructions_label = ttk.Label(
            frame,
            text=instructions_text,
            wraplength=450,
            justify=tk.LEFT
        )
        instructions_label.pack(pady=(0, 20))
        
        ttk.Button(
            frame,
            text="Got it! Start Testing",
            command=instructions_window.destroy
        ).pack()


def main():
    """Main function to run interactive UI tests."""
    parser = argparse.ArgumentParser(description="Interactive UI Test Runner")
    parser.add_argument('--with-keys', action='store_true', 
                       help='Test with mock API keys')
    parser.add_argument('--without-keys', action='store_true',
                       help='Test without API keys (degraded mode)')
    parser.add_argument('--modal-only', action='store_true',
                       help='Show only the API configuration modal')
    
    args = parser.parse_args()
    
    # If no specific test is requested, run all
    if not any([args.with_keys, args.without_keys, args.modal_only]):
        args.with_keys = True
        args.without_keys = True
        args.modal_only = True
    
    print("=" * 80)
    print("INTERACTIVE UI TEST RUNNER")
    print("=" * 80)
    print("This will open windows for visual verification of UI rendering.")
    print("Follow the instructions in each window to verify functionality.")
    print("-" * 80)
    
    test_runner = InteractiveUITest()
    test_runner.setup_test_environment()
    
    try:
        if args.modal_only:
            input("\\nPress Enter to test the API Configuration Modal...")
            test_runner.test_api_configuration_modal()
        
        if args.without_keys:
            input("\\nPress Enter to test the Main Window WITHOUT API keys...")
            test_runner.test_main_window_without_keys()
        
        if args.with_keys:
            input("\\nPress Enter to test the Main Window WITH API keys...")
            test_runner.test_main_window_with_keys()
    
    finally:
        test_runner.cleanup_test_environment()
    
    print("\\n" + "=" * 80)
    print("Interactive testing complete!")
    print("If all windows displayed correctly and functions worked,")
    print("the UI rendering is working properly.")
    print("=" * 80)


if __name__ == "__main__":
    main()