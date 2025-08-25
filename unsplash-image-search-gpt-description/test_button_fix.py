#!/usr/bin/env python3
"""Test script to verify the button fix in SetupWizard."""

import tkinter as tk
from config_manager import ConfigManager, SetupWizard
import tempfile
import os

def test_setup_wizard():
    """Test the SetupWizard with button visibility fix."""
    
    # Create a temporary directory for config
    temp_dir = tempfile.mkdtemp()
    config_path = os.path.join(temp_dir, "test_config.ini")
    
    # Create main window (hidden)
    root = tk.Tk()
    root.withdraw()
    
    # Create config manager and setup wizard
    config_manager = ConfigManager(config_path)
    wizard = SetupWizard(root, config_manager)
    
    # Check if buttons exist and are visible
    print("Testing button visibility...")
    print(f"Submit button exists: {hasattr(wizard, 'submit_button')}")
    print(f"Cancel button exists: {hasattr(wizard, 'cancel_button')}")
    
    if hasattr(wizard, 'submit_button'):
        print(f"Submit button text: {wizard.submit_button['text']}")
        print(f"Submit button state: {wizard.submit_button['state']}")
        print(f"Submit button visible: {wizard.submit_button.winfo_viewable()}")
        
    if hasattr(wizard, 'cancel_button'):
        print(f"Cancel button text: {wizard.cancel_button['text']}")
        print(f"Cancel button state: {wizard.cancel_button['state']}")
        print(f"Cancel button visible: {wizard.cancel_button.winfo_viewable()}")
    
    # Test with valid keys to see if button enables
    wizard.unsplash_entry.insert(0, "test-unsplash-key-1234567890abcdefghijklmnopqrstuvwxyz")
    wizard.openai_entry.insert(0, "sk-test-openai-key-1234567890abcdefghijklmnopqrstuvwxyz")
    wizard._validate_form()
    
    print(f"\nAfter entering valid keys:")
    print(f"Submit button state: {wizard.submit_button['state']}")
    
    # Keep window open for visual inspection
    print("\n✅ Setup wizard is now open. Check if you can see the buttons at the bottom.")
    print("The submit button should be green when enabled.")
    print("Close the window when done.")
    
    root.mainloop()

if __name__ == "__main__":
    test_setup_wizard()