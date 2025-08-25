"""
Initialization Order Fix for main.py

This module provides a solution to the initialization order issue where API configuration
blocks UI creation with wait_window(). The fix implements:

1. Deferred API configuration until after UI creation
2. Loading screen displayed first
3. Graceful handling of missing API keys without blocking

Usage:
    Replace the problematic initialization code in main.py __init__ method
    with the fixed version provided in this module.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from pathlib import Path


class LoadingScreen:
    """Loading screen that shows during app initialization."""
    
    def __init__(self, parent=None):
        self.root = parent or tk.Tk()
        self.window = None
        self.progress_var = None
        self.status_var = None
        self.is_parent_root = parent is None
        
    def show(self, title="Loading Application"):
        """Show loading screen with progress bar."""
        if self.is_parent_root:
            # If we created the root, configure it
            self.root.withdraw()  # Hide the main window initially
            
        self.window = tk.Toplevel(self.root) if not self.is_parent_root else tk.Toplevel()
        self.window.title(title)
        self.window.geometry("400x150")
        self.window.resizable(False, False)
        
        # Center the loading window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - 200
        y = (self.window.winfo_screenheight() // 2) - 75
        self.window.geometry(f"+{x}+{y}")
        
        # Remove window decorations for loading screen effect
        self.window.overrideredirect(True)
        
        # Create loading content
        main_frame = tk.Frame(self.window, bg='#f0f0f0', padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # App title
        title_label = tk.Label(
            main_frame,
            text="Unsplash Image Search & GPT Description",
            font=('TkDefaultFont', 12, 'bold'),
            bg='#f0f0f0'
        )
        title_label.pack(pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Initializing application...")
        status_label = tk.Label(
            main_frame,
            textvariable=self.status_var,
            bg='#f0f0f0',
            fg='#666666'
        )
        status_label.pack(pady=(0, 15))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            main_frame,
            mode='determinate',
            variable=self.progress_var,
            maximum=100
        )
        progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Version info
        version_label = tk.Label(
            main_frame,
            text="Version 2.0 - Enhanced UI",
            font=('TkDefaultFont', 8),
            bg='#f0f0f0',
            fg='#999999'
        )
        version_label.pack()
        
        self.window.update()
        return self.window
        
    def update_progress(self, percentage, status=""):
        """Update loading progress."""
        if self.window and self.progress_var:
            self.progress_var.set(percentage)
            if status and self.status_var:
                self.status_var.set(status)
            self.window.update()
    
    def hide(self):
        """Hide loading screen."""
        if self.window:
            self.window.destroy()
            self.window = None
        if self.is_parent_root:
            self.root.deiconify()  # Show main window


class DeferredAPIConfiguration:
    """Handles API configuration after UI creation."""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.config_manager = None
        self.api_keys_configured = False
        self.loading_screen = None
    
    def show_api_setup_dialog(self):
        """Show API setup dialog without blocking."""
        dialog = tk.Toplevel(self.app)
        dialog.title("API Configuration Required")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self.app)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 200
        dialog.geometry(f"+{x}+{y}")
        
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="API Configuration Required",
            font=('TkDefaultFont', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Explanation
        explanation = """This application requires API keys to function properly:

• Unsplash API Key - For searching and downloading images
• OpenAI API Key - For generating image descriptions

You can either:
1. Configure API keys now (recommended)
2. Continue without API keys (limited functionality)

API keys will be stored securely in config.ini file."""
        
        explanation_label = tk.Label(
            main_frame,
            text=explanation,
            justify=tk.LEFT,
            wraplength=450
        )
        explanation_label.pack(pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        def configure_apis():
            dialog.destroy()
            self._configure_apis_now()
        
        def continue_without():
            dialog.destroy()
            self._continue_without_apis()
        
        def exit_app():
            dialog.destroy()
            self.app.quit()
        
        tk.Button(
            button_frame,
            text="Configure APIs",
            command=configure_apis,
            bg='#4CAF50',
            fg='white',
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            button_frame,
            text="Continue Without APIs",
            command=continue_without,
            bg='#FFC107',
            fg='black',
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            button_frame,
            text="Exit",
            command=exit_app,
            bg='#F44336',
            fg='white',
            padx=20,
            pady=5
        ).pack(side=tk.RIGHT)
        
        return dialog
    
    def _configure_apis_now(self):
        """Configure APIs using the config manager."""
        try:
            from config_manager import ConfigManager, ensure_api_keys_configured
            
            # Show loading
            self.loading_screen = LoadingScreen(self.app)
            loading_window = self.loading_screen.show("Configuring APIs")
            self.loading_screen.update_progress(20, "Loading configuration...")
            
            # Initialize config manager
            self.config_manager = ConfigManager()
            self.loading_screen.update_progress(40, "Checking API keys...")
            
            # Check if keys already exist
            api_keys = self.config_manager.get_api_keys()
            if all([api_keys.get('unsplash'), api_keys.get('openai')]):
                # Keys already exist
                self.loading_screen.update_progress(100, "API keys found!")
                time.sleep(0.5)
                self.loading_screen.hide()
                self._apply_api_configuration(self.config_manager)
                return
            
            self.loading_screen.update_progress(60, "Opening configuration dialog...")
            time.sleep(0.2)
            self.loading_screen.hide()
            
            # Use ensure_api_keys_configured but don't block main thread
            result_config = ensure_api_keys_configured(self.app)
            
            if result_config:
                self.config_manager = result_config
                self._apply_api_configuration(result_config)
            else:
                self._show_config_cancelled_message()
                
        except Exception as e:
            if self.loading_screen:
                self.loading_screen.hide()
            messagebox.showerror("Configuration Error", 
                               f"Error configuring APIs:\n{str(e)}\n\nContinuing with limited functionality.")
            self._continue_without_apis()
    
    def _continue_without_apis(self):
        """Continue without API configuration."""
        from config_manager import ConfigManager
        
        self.loading_screen = LoadingScreen(self.app)
        loading_window = self.loading_screen.show("Initializing App")
        self.loading_screen.update_progress(50, "Setting up default configuration...")
        
        # Create default config manager
        self.config_manager = ConfigManager()
        time.sleep(0.3)
        
        self.loading_screen.update_progress(100, "Ready!")
        time.sleep(0.2)
        self.loading_screen.hide()
        
        # Apply configuration
        self._apply_api_configuration(self.config_manager, limited_mode=True)
        
        # Show info about limited functionality
        self.app.after(500, self._show_limited_mode_info)
    
    def _apply_api_configuration(self, config_manager, limited_mode=False):
        """Apply API configuration to the app."""
        self.app.config_manager = config_manager
        self.api_keys_configured = not limited_mode
        
        # Load API keys and paths
        api_keys = config_manager.get_api_keys()
        paths = config_manager.get_paths()
        
        self.app.UNSPLASH_ACCESS_KEY = api_keys.get('unsplash', '')
        self.app.OPENAI_API_KEY = api_keys.get('openai', '')
        self.app.GPT_MODEL = api_keys.get('gpt_model', 'gpt-4o-mini')
        
        # Initialize OpenAI client if key exists
        if self.app.OPENAI_API_KEY:
            from openai import OpenAI
            self.app.openai_client = OpenAI(api_key=self.app.OPENAI_API_KEY)
        else:
            self.app.openai_client = None
        
        # Set up paths
        self.app.DATA_DIR = paths['data_dir']
        self.app.LOG_FILENAME = paths['log_file']
        self.app.CSV_TARGET_WORDS = paths['vocabulary_file']
        
        # Ensure data directory exists
        self.app.DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialize CSV with headers if it doesn't exist
        if not self.app.CSV_TARGET_WORDS.exists():
            import csv
            with open(self.app.CSV_TARGET_WORDS, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
        
        # Update UI title with status
        self.app.update_title_with_status()
        
        # Initialize performance optimization after API setup
        self.app.after(500, self._initialize_performance_systems)
        
        if limited_mode:
            # Disable API-dependent features
            self._disable_api_features()
    
    def _initialize_performance_systems(self):
        """Initialize performance systems after API configuration."""
        try:
            self.app._initialize_performance_optimization()
        except Exception as e:
            print(f"Warning: Could not initialize performance systems: {e}")
    
    def _disable_api_features(self):
        """Disable features that require API keys."""
        # Disable search and generation buttons
        if hasattr(self.app, 'search_button'):
            self.app.search_button.config(state=tk.DISABLED)
        if hasattr(self.app, 'generate_desc_button'):
            self.app.generate_desc_button.config(state=tk.DISABLED)
        
        # Update status
        self.app.update_status("Limited mode - API keys not configured")
        
    def _show_config_cancelled_message(self):
        """Show message when user cancels API configuration."""
        messagebox.showinfo(
            "Configuration Cancelled",
            "API configuration was cancelled.\n\nYou can configure APIs later from the settings menu.\n\nRunning in limited mode."
        )
        self._continue_without_apis()
    
    def _show_limited_mode_info(self):
        """Show information about limited mode."""
        info_text = """Running in Limited Mode

Some features are not available without API keys:

Disabled Features:
• Image search (requires Unsplash API key)
• AI description generation (requires OpenAI API key)
• Vocabulary extraction

Available Features:
• Theme switching
• Export existing vocabulary
• View help and documentation

You can configure API keys anytime by going to Settings → Configure APIs"""

        messagebox.showinfo("Limited Mode", info_text)


def apply_init_order_fix():
    """
    Returns the fixed __init__ method content for the ImageSearchApp class.
    This should replace the existing __init__ method in main.py
    """
    
    fixed_init_code = '''
    def __init__(self):
        super().__init__()
        
        # Show loading screen first
        self.loading_screen = LoadingScreen(self)
        loading_window = self.loading_screen.show("Starting Unsplash App")
        
        # Initialize basic attributes first (no blocking operations)
        self.config_manager = None  # Will be set later
        self.performance_optimizer = None
        self.openai_client = None
        
        # Initialize basic app state
        self.log_entries = []
        self.extracted_phrases = {}
        self.target_phrases = []
        self.used_image_urls = set()
        self.vocabulary_cache = set()
        self.image_cache = {}
        
        # Estado de paginación
        self.current_query = ""
        self.current_page = 0
        self.current_results = []
        self.current_index = 0
        self.current_image_url = None
        
        # Collection limits and search state
        self.max_images_per_search = 30  # Default value
        self.images_collected_count = 0
        self.search_cancelled = False
        self.search_state = 'idle'
        
        self.loading_screen.update_progress(30, "Setting up window...")
        
        # Basic window configuration
        self.title("Búsqueda de Imágenes en Unsplash & Descripción GPT")
        self.geometry("1100x800")
        self.resizable(True, True)
        
        # Initialize UI state
        self.zoom_level = 100  # Default zoom level
        self.loading_animation_id = None
        
        self.loading_screen.update_progress(50, "Creating user interface...")
        
        # Create UI first (no API dependencies)
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        # Create all widgets
        self.create_widgets()
        
        self.loading_screen.update_progress(70, "Initializing theme system...")
        
        # Initialize theme manager with default config
        from config_manager import ConfigManager
        temp_config = ConfigManager()
        self.theme_manager = ThemeManager(temp_config)
        self.theme_manager.initialize(self)
        self.theme_manager.register_theme_callback(self.on_theme_change)
        
        self.loading_screen.update_progress(90, "Finalizing setup...")
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        
        # Hide loading screen
        self.loading_screen.update_progress(100, "Ready!")
        time.sleep(0.3)
        self.loading_screen.hide()
        
        # NOW handle API configuration in a non-blocking way
        self.deferred_api_config = DeferredAPIConfiguration(self)
        
        # Check if we need to configure APIs (after UI is ready)
        self.after(100, self._check_api_configuration)
    
    def _check_api_configuration(self):
        """Check and handle API configuration after UI is ready."""
        try:
            from config_manager import ConfigManager
            temp_config = ConfigManager()
            
            # Check if APIs are already configured
            api_keys = temp_config.get_api_keys()
            if api_keys.get('unsplash') and api_keys.get('openai'):
                # APIs already configured
                self.deferred_api_config._apply_api_configuration(temp_config)
                self.load_session_data()  # Load data after APIs are ready
            else:
                # Show API setup dialog
                self.after(500, self.deferred_api_config.show_api_setup_dialog)
                
        except Exception as e:
            print(f"Error checking API configuration: {e}")
            # Continue without APIs
            self.deferred_api_config._continue_without_apis()
            
    def load_session_data(self):
        """Load session data after API configuration is complete."""
        try:
            # Load previously used image URLs and vocabulary
            self.load_used_image_urls_from_log()
            self.load_vocabulary_cache()
            
            # Load last search if exists
            self.load_last_search()
            
            # Update stats
            self.update_stats()
            
            self.update_status("Application ready")
            
        except Exception as e:
            print(f"Warning: Could not load session data: {e}")
            self.update_status("Application ready (some data could not be loaded)")
    '''
    
    return fixed_init_code


def create_updated_main_py(original_file_path, output_file_path=None):
    """
    Create an updated version of main.py with the initialization order fix applied.
    
    Args:
        original_file_path: Path to the original main.py file
        output_file_path: Path where to save the fixed version (optional)
    
    Returns:
        str: Path to the created fixed file
    """
    import re
    
    if output_file_path is None:
        output_file_path = Path(original_file_path).parent / "main_fixed_init_order.py"
    
    # Read original file
    with open(original_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add the imports at the top
    imports_to_add = '''
# Import fix components
import time
from src.fixes.init_order_fix import LoadingScreen, DeferredAPIConfiguration
'''
    
    # Insert after existing imports (find the last import line)
    import_pattern = r'(from src\.ui\.theme_manager import.*?\n)'
    content = re.sub(import_pattern, r'\1' + imports_to_add, content)
    
    # Replace the __init__ method
    init_pattern = r'(    def __init__\(self\):.*?)(?=\n    def [a-zA-Z_])'
    fixed_init = apply_init_order_fix()
    
    content = re.sub(init_pattern, fixed_init, content, flags=re.DOTALL)
    
    # Write fixed version
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return str(output_file_path)


if __name__ == "__main__":
    # Example usage
    print("Initialization Order Fix Module")
    print("This module provides fixes for the main.py initialization order issue.")
    print("Key features:")
    print("- Deferred API configuration")
    print("- Loading screen during startup")
    print("- Graceful handling of missing API keys")
    print("- Non-blocking UI creation")