"""
UI Fix for Blank Main Window Issue
====================================
This module fixes the issue where the main window shows blank while the API 
configuration modal is displayed. The problem occurs because ensure_api_keys_configured
blocks the main window before create_widgets() is called.

Solution: Defer API configuration until after UI is created.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time


def fix_initialization_order(app_class):
    """
    Decorator to fix the initialization order of the main application.
    Ensures UI is created before blocking modals are shown.
    """
    original_init = app_class.__init__
    
    def new_init(self):
        # Call parent init
        tk.Tk.__init__(self)
        
        # Set basic window properties first
        self.title("Loading Application...")
        self.geometry("1100x800")
        self.resizable(True, True)
        
        # Create a loading screen
        self.loading_frame = ttk.Frame(self)
        self.loading_frame.pack(fill=tk.BOTH, expand=True)
        
        loading_label = ttk.Label(
            self.loading_frame, 
            text="Initializing application...", 
            font=('TkDefaultFont', 16)
        )
        loading_label.pack(expand=True)
        
        progress = ttk.Progressbar(
            self.loading_frame, 
            mode='indeterminate',
            length=300
        )
        progress.pack(pady=20)
        progress.start(10)
        
        # Force UI update to show loading screen
        self.update_idletasks()
        self.update()
        
        # Schedule the rest of initialization after UI is visible
        self.after(100, lambda: complete_initialization(self, original_init))
    
    def complete_initialization(self, original_init):
        """Complete the initialization after UI is visible."""
        try:
            # Remove loading screen
            if hasattr(self, 'loading_frame'):
                self.loading_frame.destroy()
            
            # Call original init (but we need to skip tk.Tk.__init__)
            # This is a bit tricky - we'll need to extract the initialization code
            _run_deferred_init(self)
            
        except Exception as e:
            print(f"Error during initialization: {e}")
            import traceback
            traceback.print_exc()
    
    app_class.__init__ = new_init
    return app_class


def _run_deferred_init(self):
    """
    Run the deferred initialization with proper error handling.
    This extracts the initialization logic and runs it after UI is created.
    """
    from config_manager import ConfigManager
    from src.ui.theme_manager import ThemeManager
    from openai import OpenAI
    import csv
    from pathlib import Path
    
    try:
        # Create config manager without blocking
        self.config_manager = ConfigManager()
        
        # Initialize theme manager
        self.theme_manager = ThemeManager(self.config_manager)
        
        # Set default values for API keys if not configured
        api_keys = self.config_manager.get_api_keys()
        paths = self.config_manager.get_paths()
        
        self.UNSPLASH_ACCESS_KEY = api_keys.get('unsplash', '')
        self.OPENAI_API_KEY = api_keys.get('openai', '')
        self.GPT_MODEL = api_keys.get('gpt_model', 'gpt-4o-mini')
        
        # Initialize OpenAI client (will work with empty key)
        self.openai_client = OpenAI(api_key=self.OPENAI_API_KEY) if self.OPENAI_API_KEY else None
        
        # Set up paths
        self.DATA_DIR = paths['data_dir']
        self.LOG_FILENAME = paths['log_file']
        self.CSV_TARGET_WORDS = paths['vocabulary_file']
        
        # Ensure data directory exists
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialize CSV with headers if it doesn't exist
        if not self.CSV_TARGET_WORDS.exists():
            with open(self.CSV_TARGET_WORDS, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
        
        # Set title
        self.title("Búsqueda de Imágenes en Unsplash & Descripción GPT")
        
        # Initialize state variables
        self.log_entries = []
        self.extracted_phrases = {}
        self.target_phrases = []
        self.used_image_urls = set()
        self.vocabulary_cache = set()
        self.image_cache = {}
        
        # Pagination state
        self.current_query = ""
        self.current_page = 0
        self.current_results = []
        self.current_index = 0
        self.current_image_url = None
        
        # Collection limits and search state
        self.max_images_per_search = int(self.config_manager.config.get('Search', 'max_images_per_search', fallback='30'))
        self.images_collected_count = 0
        self.search_cancelled = False
        self.search_state = 'idle'
        
        # Load previous data
        self.load_used_image_urls_from_log()
        self.load_vocabulary_cache()
        
        # Style
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        # Initialize UI state
        self.zoom_level = float(self.config_manager.config.get('UI', 'zoom_level', fallback='100'))
        self.loading_animation_id = None
        
        # Create widgets
        self.create_widgets()
        
        # Initialize theme after widgets exist
        self.theme_manager.initialize(self)
        self.theme_manager.register_theme_callback(self.on_theme_change)
        
        # Initialize performance optimization after UI is ready
        self.performance_optimizer = None
        self.after(1000, lambda: self._initialize_performance_optimization())
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        
        # Update title with status
        self.update_title_with_status()
        
        # Load last search if exists
        self.load_last_search()
        
        # Update stats
        self.update_stats()
        
        # Show API configuration if needed (non-blocking)
        if not self.config_manager.validate_api_keys():
            self.after(500, self.show_api_configuration)
            
    except Exception as e:
        print(f"Error in deferred initialization: {e}")
        import traceback
        traceback.print_exc()
        
        # Show error dialog
        self.show_initialization_error(str(e))


def show_api_configuration(self):
    """Show API configuration dialog without blocking main window."""
    from config_manager import SetupWizard
    
    # Create the wizard as a toplevel window
    wizard = SetupWizard(self, self.config_manager)
    
    # Don't use wait_window - let it run independently
    # The main window is already rendered and functional
    
    def on_wizard_close():
        """Handle wizard closing."""
        if wizard.result:
            # Reload configuration
            api_keys = self.config_manager.get_api_keys()
            self.UNSPLASH_ACCESS_KEY = api_keys.get('unsplash', '')
            self.OPENAI_API_KEY = api_keys.get('openai', '')
            self.GPT_MODEL = api_keys.get('gpt_model', 'gpt-4o-mini')
            
            # Reinitialize OpenAI client
            if self.OPENAI_API_KEY:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.OPENAI_API_KEY)
            
            self.update_title_with_status()
            self.update_status("API keys configured successfully")
        else:
            self.update_status("Running without API keys - some features disabled")
    
    # Bind the close event
    wizard.protocol("WM_DELETE_WINDOW", lambda: [on_wizard_close(), wizard.destroy()])


def show_initialization_error(self, error_message):
    """Show initialization error dialog."""
    error_frame = ttk.Frame(self)
    error_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    ttk.Label(
        error_frame,
        text="Initialization Error",
        font=('TkDefaultFont', 16, 'bold')
    ).pack(pady=10)
    
    ttk.Label(
        error_frame,
        text=f"The application encountered an error during startup:\n\n{error_message}",
        wraplength=500
    ).pack(pady=10)
    
    ttk.Button(
        error_frame,
        text="Try Again",
        command=self.restart_application
    ).pack(pady=10)
    
    ttk.Button(
        error_frame,
        text="Exit",
        command=self.destroy
    ).pack()


def restart_application(self):
    """Restart the application."""
    import sys
    import os
    
    python = sys.executable
    os.execl(python, python, *sys.argv)


# Monkey-patch the show_api_configuration method
ImageSearchApp.show_api_configuration = show_api_configuration
ImageSearchApp.show_initialization_error = show_initialization_error  
ImageSearchApp.restart_application = restart_application