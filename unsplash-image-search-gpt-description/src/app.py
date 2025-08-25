"""
Main application entry point for the modular Unsplash Image Search application.
"""

import tkinter as tk
from tkinter import messagebox
import traceback

from .ui.main_window import MainWindow
from .ui.dialogs.setup_wizard import ensure_api_keys_configured


def main():
    """Main entry point for the application."""
    try:
        # Initialize configuration and show setup wizard if needed
        config_manager = ensure_api_keys_configured()
        
        if not config_manager:
            # User cancelled setup
            return
        
        # Create and run main application
        app = MainWindow(config_manager)
        app.mainloop()
        
    except Exception as e:
        # Show error in a message box if GUI fails to start
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Application Error",
            f"Failed to start application:\n\n{str(e)}\n\nPlease check your configuration and try again."
        )
        traceback.print_exc()
        root.destroy()


if __name__ == "__main__":
    main()