"""
Fixed version of the Unsplash Image Search application with proper UI initialization.

Key fixes:
1. Initialize window and show loading screen first
2. Create all widgets before any blocking operations  
3. Handle API configuration asynchronously after UI is ready
4. Gracefully handle missing API keys without blocking
5. Use proper event loop management

The main window always renders even if API keys are missing.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from PIL import Image, ImageTk
from io import BytesIO
import threading
import os
import sys
import json
import re
import csv
import time
from pathlib import Path
from datetime import datetime
import traceback

# Import config manager with error handling
try:
    from config_manager import ConfigManager
except ImportError as e:
    print(f"Warning: Could not import config_manager: {e}")
    # Create minimal ConfigManager for fallback
    class ConfigManager:
        def __init__(self):
            self.config_dir = Path('.')
            self.data_dir = Path('./data')
            self.data_dir.mkdir(exist_ok=True)
        def get_api_keys(self):
            return {'unsplash': '', 'openai': '', 'gpt_model': 'gpt-4o-mini'}
        def get_paths(self):
            return {
                'data_dir': self.data_dir,
                'log_file': self.data_dir / 'session_log.json',
                'vocabulary_file': self.data_dir / 'vocabulary.csv'
            }
        def validate_api_keys(self):
            return False

# Import new components for enhanced functionality
try:
    from src.ui.components.clickable_text import ClickableText
    from src.ui.dialogs.settings_menu import show_settings_dialog
    from src.models.vocabulary import VocabularyManager
    from src.ui.components.style_selector import StyleSelectorPanel
    from src.features.description_styles import get_style_manager
    from src.features.session_tracker import SessionTracker
except ImportError as e:
    print(f"Warning: Could not import enhanced components: {e}")
    # Create fallback classes
    class ClickableText(scrolledtext.ScrolledText):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.update_context = lambda *args: None
            self.set_clickable = lambda x: None
    
    def show_settings_dialog(parent, config_manager):
        messagebox.showinfo("Settings", "Settings dialog not available.")
    
    class VocabularyManager:
        def __init__(self, *args):
            pass
        def is_duplicate(self, word):
            return False
    
    class StyleSelectorPanel(ttk.Frame):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.get_selected_style = lambda: None
            self.get_selected_vocabulary_level = lambda: None
    
    def get_style_manager():
        return None
    
    class SessionTracker:
        def __init__(self, *args):
            pass

# Import OpenAI with error handling
try:
    from openai import OpenAI
except ImportError:
    print("Warning: OpenAI module not available")
    OpenAI = None


class LoadingScreen(tk.Toplevel):
    """Loading screen shown during application initialization."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Loading...")
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Remove window decorations and center
        self.overrideredirect(True)
        self.configure(bg='#f0f0f0')
        
        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 200
        y = (self.winfo_screenheight() // 2) - 100
        self.geometry(f"+{x}+{y}")
        
        # Loading content
        self.create_loading_content()
        
        # Make it stay on top
        self.lift()
        self.focus_force()
        
    def create_loading_content(self):
        """Create loading screen content."""
        # Main frame
        main_frame = tk.Frame(self, bg='#f0f0f0', relief=tk.RAISED, bd=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # App title
        title_label = tk.Label(
            main_frame,
            text="Unsplash Image Search & GPT Description",
            font=('Arial', 14, 'bold'),
            bg='#f0f0f0',
            fg='#333'
        )
        title_label.pack(pady=(20, 10))
        
        # Loading animation
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=300
        )
        self.progress.pack(pady=10)
        self.progress.start(10)
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="Loading...",
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#666'
        )
        self.status_label.pack(pady=(10, 20))
        
    def update_status(self, message):
        """Update loading status message."""
        self.status_label.config(text=message)
        self.update_idletasks()

class ImageSearchApp(tk.Tk):
    """
    Fixed version of the Unsplash Image Search application.
    
    Key improvements:
    - Always shows main window first
    - Loads API configuration asynchronously
    - Gracefully handles missing API keys
    - Proper error handling without blocking UI
    """

    def __init__(self):
        super().__init__()
        
        # Set up basic window properties immediately
        self.title("Unsplash Image Search & GPT Description")
        self.geometry("1100x800")
        self.resizable(True, True)
        
        # Show loading screen immediately
        self.loading_screen = LoadingScreen(self)
        self.update_idletasks()
        
        # Initialize state variables early
        self.config_manager = None
        self.performance_optimizer = None
        self.theme_manager = None
        self.vocabulary_manager = None
        self.api_keys_ready = False
        self.initialization_complete = False
        self.style_manager = None
        self.session_tracker = None
        self.style_selector_panel = None
        
        # Application state
        self.log_entries = []
        self.extracted_phrases = {}
        self.target_phrases = []
        self.used_image_urls = set()
        self.vocabulary_cache = set()
        self.image_cache = {}
        
        # Search state
        self.current_query = ""
        self.current_page = 0
        self.current_results = []
        self.current_index = 0
        self.current_image_url = None
        self.max_images_per_search = 30
        self.images_collected_count = 0
        self.search_cancelled = False
        self.search_state = 'idle'
        
        # Quiz state
        self.current_quiz_phrases = []
        
        # UI state
        self.zoom_level = 100
        self.loading_animation_id = None
        
        # API clients (will be set up later)
        self.openai_client = None
        self.UNSPLASH_ACCESS_KEY = ""
        self.OPENAI_API_KEY = ""
        self.GPT_MODEL = "gpt-4o-mini"
        
        # Initialize UI immediately - this is critical
        self.create_menu_bar()
        self.create_basic_ui()
        
        # Start async initialization
        self.after(100, self.start_async_initialization)
    
    def create_basic_ui(self):
        """Create basic UI structure immediately."""
        self.loading_screen.update_status("Creating user interface...")
        
        try:
            # Create menu bar first
            self.create_menu_bar()
            
            # Create main container
            self.main_frame = ttk.Frame(self, padding="10")
            self.main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Create search controls
            self.create_search_controls()
            
            # Create status bar
            self.create_status_bar()
            
            # Create content area
            self.create_content_area()
            
            # Create initial empty widgets
            self.create_placeholder_widgets()
            
            # Set up basic keyboard shortcuts
            self.setup_basic_shortcuts()
            
            # Window close protocol
            self.protocol("WM_DELETE_WINDOW", self.on_exit)
            
            self.loading_screen.update_status("UI created successfully")
            
        except Exception as e:
            self.handle_initialization_error(f"Failed to create UI: {e}")
    
    def create_menu_bar(self):
        """Create menu bar with Settings menu."""
        try:
            # Create menu bar
            self.menubar = tk.Menu(self)
            self.config(menu=self.menubar)
            
            # File menu
            file_menu = tk.Menu(self.menubar, tearoff=0)
            self.menubar.add_cascade(label="File", menu=file_menu)
            file_menu.add_command(label="New Search", command=self.change_search, accelerator="Ctrl+N")
            file_menu.add_separator()
            file_menu.add_command(label="Exit", command=self.on_exit, accelerator="Ctrl+Q")
            
            # Tools menu
            tools_menu = tk.Menu(self.menubar, tearoff=0)
            self.menubar.add_cascade(label="Tools", menu=tools_menu)
            tools_menu.add_command(label="Generate Description", command=self.safe_generate_description, accelerator="F5")
            tools_menu.add_command(label="Vocabulary Quiz", command=self.open_vocabulary_quiz, accelerator="F6")
            
            # Settings menu
            settings_menu = tk.Menu(self.menubar, tearoff=0)
            self.menubar.add_cascade(label="Settings", menu=settings_menu)
            settings_menu.add_command(label="Preferences...", command=self.open_settings_dialog, accelerator="Ctrl+,")
            settings_menu.add_separator()
            settings_menu.add_command(label="API Configuration...", command=self.show_api_setup)
            
            # Help menu
            help_menu = tk.Menu(self.menubar, tearoff=0)
            self.menubar.add_cascade(label="Help", menu=help_menu)
            help_menu.add_command(label="Help", command=self.show_help, accelerator="F1")
            help_menu.add_separator()
            help_menu.add_command(label="About", command=self.show_about)
            
        except Exception as e:
            print(f"Error creating menu bar: {e}")
    
    def open_settings_dialog(self):
        """Open the settings dialog."""
        try:
            if hasattr(self, 'config_manager') and self.config_manager:
                show_settings_dialog(self, self.config_manager)
            else:
                messagebox.showwarning("Settings", "Configuration manager not available.")
        except Exception as e:
            messagebox.showerror("Settings Error", f"Failed to open settings: {e}")
    
    def show_about(self):
        """Show about dialog."""
        about_text = (
            "Unsplash Image Search & GPT Description Tool\n\n"
            "Version 1.0\n\n"
            "Features:\n"
            "• Search Unsplash images\n"
            "• AI-powered Spanish descriptions\n"
            "• Interactive vocabulary learning\n"
            "• Clickable text for translations\n\n"
            "Powered by OpenAI GPT and Unsplash API"
        )
        messagebox.showinfo("About", about_text)
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Search", command=self.new_search, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Export Vocabulary", command=self.export_vocabulary, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit, accelerator="Ctrl+Q")
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Settings", command=self.open_settings, accelerator="Ctrl+,")
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear Data", command=self.clear_data)
        
        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme, accelerator="Ctrl+T")
        view_menu.add_separator()
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Reset Zoom", command=self.reset_zoom, accelerator="Ctrl+0")
        
        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Quiz Me", command=self.open_vocabulary_quiz, accelerator="Ctrl+G", state=tk.DISABLED)
        tools_menu.add_separator()
        tools_menu.add_command(label="View Statistics", command=self.view_statistics)
        
        # Store menu references for later state management
        self.tools_menu = tools_menu
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about, accelerator="F1")
        
        # Bind keyboard shortcuts
        self.bind('<Control-n>', lambda e: self.new_search())
        self.bind('<Control-N>', lambda e: self.new_search())
        self.bind('<Control-e>', lambda e: self.export_vocabulary())
        self.bind('<Control-E>', lambda e: self.export_vocabulary())
        self.bind('<Control-comma>', lambda e: self.open_settings())
        self.bind('<Control-t>', lambda e: self.toggle_theme())
        self.bind('<Control-T>', lambda e: self.toggle_theme())
        self.bind('<Control-plus>', lambda e: self.zoom_in())
        self.bind('<Control-equal>', lambda e: self.zoom_in())  # For keyboards without separate + key
        self.bind('<Control-minus>', lambda e: self.zoom_out())
        self.bind('<Control-0>', lambda e: self.reset_zoom())
        self.bind('<Control-g>', lambda e: self.open_vocabulary_quiz())
        self.bind('<Control-G>', lambda e: self.open_vocabulary_quiz())
        self.bind('<F1>', lambda e: self.show_about())
    
    def create_search_controls(self):
        """Create search control widgets."""
        search_frame = ttk.Frame(self.main_frame, padding="5")
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Search Query:").grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.grid(row=0, column=1, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.safe_search_image())
        
        self.search_button = ttk.Button(
            search_frame, 
            text="Search Images", 
            command=self.safe_search_image,
            state=tk.DISABLED  # Disabled until API keys are ready
        )
        self.search_button.grid(row=0, column=2, padx=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            search_frame, 
            mode='indeterminate'
        )
        self.progress_bar.grid(row=0, column=3, padx=5, sticky="ew")
        self.progress_bar.grid_remove()
        
        # Second row buttons
        self.another_button = ttk.Button(
            search_frame, 
            text="Another Image", 
            command=self.safe_another_image,
            state=tk.DISABLED
        )
        self.another_button.grid(row=1, column=0, padx=5, pady=(5, 0), sticky=tk.W)
        
        self.newsearch_button = ttk.Button(
            search_frame, 
            text="New Search", 
            command=self.change_search,
            state=tk.DISABLED
        )
        self.newsearch_button.grid(row=1, column=1, padx=5, pady=(5, 0), sticky=tk.W)
        
        self.generate_button = ttk.Button(
            search_frame, 
            text="Generate Description", 
            command=self.safe_generate_description,
            state=tk.DISABLED
        )
        self.generate_button.grid(row=1, column=2, padx=5, pady=(5, 0), sticky=tk.W)
        
        self.quiz_button = ttk.Button(
            search_frame, 
            text="🎯 Quiz Me", 
            command=self.open_vocabulary_quiz,
            state=tk.DISABLED
        )
        self.quiz_button.grid(row=1, column=3, padx=5, pady=(5, 0), sticky=tk.W)
    
    def create_status_bar(self):
        """Create status bar."""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.status_label = ttk.Label(
            status_frame, 
            text="Initializing...", 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.stats_label = ttk.Label(
            status_frame, 
            text="API Status: Not Ready", 
            relief=tk.SUNKEN, 
            anchor=tk.E
        )
        self.stats_label.pack(side=tk.RIGHT, padx=(5, 0))
    
    def create_content_area(self):
        """Create main content area."""
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Left side: Image preview
        self.image_frame = ttk.LabelFrame(content_frame, text="Image Preview", padding="10")
        self.image_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.image_frame.rowconfigure(0, weight=1)
        self.image_frame.columnconfigure(0, weight=1)
        
        # Image canvas
        self.image_canvas = tk.Canvas(self.image_frame, bg='white', width=400, height=400)
        self.image_canvas.grid(row=0, column=0, sticky="nsew")
        
        # Image placeholder
        self.image_label = tk.Label(self.image_canvas, text="No image loaded", bg='white')
        self.image_canvas.create_window(200, 200, window=self.image_label)
        
        # Right side: Text areas
        self.text_area_frame = ttk.Frame(content_frame)
        self.text_area_frame.grid(row=0, column=1, sticky="nsew")
        self.text_area_frame.rowconfigure(0, weight=1)
        self.text_area_frame.rowconfigure(1, weight=1)
        self.text_area_frame.rowconfigure(2, weight=1)
        self.text_area_frame.columnconfigure(0, weight=1)
        
    def create_placeholder_widgets(self):
        """Create placeholder text widgets."""
        # Notes area
        notes_frame = ttk.LabelFrame(self.text_area_frame, text="Your Notes", padding="10")
        notes_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=(0, 5))
        notes_frame.rowconfigure(0, weight=1)
        notes_frame.columnconfigure(0, weight=1)
        
        self.note_text = scrolledtext.ScrolledText(notes_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.note_text.grid(row=0, column=0, sticky="nsew")
        
        # Description area
        desc_frame = ttk.LabelFrame(self.text_area_frame, text="AI Description", padding="10")
        desc_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
        desc_frame.rowconfigure(0, weight=1)
        desc_frame.columnconfigure(0, weight=1)
        
        # Use ClickableText for interactive Spanish vocabulary learning
        self.description_text = ClickableText(
            desc_frame,
            vocabulary_manager=getattr(self, 'vocabulary_manager', None),
            openai_service=None,  # Will be set later when API client is ready
            theme_manager=getattr(self, 'theme_manager', None),
            current_search_query="",
            current_image_url="",
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("TkDefaultFont", 12)
        )
        self.description_text.grid(row=0, column=0, sticky="nsew")
        
        # Copy button for description
        self.copy_desc_button = ttk.Button(
            desc_frame,
            text="📋 Copy",
            command=self.copy_description,
            state=tk.DISABLED
        )
        self.copy_desc_button.grid(row=1, column=0, sticky="e", pady=(5, 0))
        
        # Vocabulary area
        vocab_frame = ttk.LabelFrame(self.text_area_frame, text="Vocabulary", padding="10")
        vocab_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=(0, 5))
        vocab_frame.rowconfigure(0, weight=1)
        vocab_frame.columnconfigure(0, weight=1)
        
        self.vocab_text = scrolledtext.ScrolledText(vocab_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.vocab_text.grid(row=0, column=0, sticky="nsew")
    
    def create_style_selector_area(self):
        """Create style selector area."""
        if not hasattr(self, 'main_frame'):
            return
        
        # Style selector frame
        style_frame = ttk.LabelFrame(self.main_frame, text="Configuración de Estilo", padding="5")
        style_frame.pack(fill=tk.X, pady=(10, 5))
        
        # Create placeholder initially
        placeholder_label = ttk.Label(
            style_frame, 
            text="Selector de estilo se inicializará cuando la aplicación esté lista...",
            foreground='gray'
        )
        placeholder_label.pack(pady=10)
        
        # Store reference for later initialization
        self.style_frame = style_frame
        self.style_placeholder = placeholder_label
        
    def setup_basic_shortcuts(self):
        """Set up basic keyboard shortcuts."""
        self.bind('<Control-q>', lambda e: self.on_exit())
        self.bind('<Control-Q>', lambda e: self.on_exit())
        self.bind('<Control-n>', lambda e: self.change_search())
        self.bind('<Control-N>', lambda e: self.change_search())
        self.bind('<Control-comma>', lambda e: self.open_settings_dialog())
        self.bind('<F5>', lambda e: self.safe_generate_description())
        self.bind('<F6>', lambda e: self.open_vocabulary_quiz())
        self.bind('<Escape>', lambda e: self.cancel_operation())
    
    def start_async_initialization(self):
        """Start asynchronous initialization in background thread."""
        threading.Thread(
            target=self.async_initialization, 
            daemon=True,
            name="AsyncInitialization"
        ).start()
    
    def async_initialization(self):
        """Perform heavy initialization in background."""
        try:
            self.after(0, lambda: self.loading_screen.update_status("Loading configuration..."))
            
            # Initialize configuration manager
            self.config_manager = ConfigManager()
            
            # Initialize vocabulary manager
            paths = self.config_manager.get_paths()
            self.vocabulary_manager = VocabularyManager(paths['vocabulary_file'])
            
            # Initialize style manager
            self.style_manager = get_style_manager()
            
            # Initialize session tracker
            self.session_tracker = SessionTracker(paths['data_dir'])
            
            self.after(0, lambda: self.loading_screen.update_status("Setting up data directories..."))
            
            # Set up paths
            paths = self.config_manager.get_paths()
            self.DATA_DIR = paths['data_dir']
            self.LOG_FILENAME = paths['log_file']
            self.CSV_TARGET_WORDS = paths['vocabulary_file']
            
            # Ensure data directory exists
            self.DATA_DIR.mkdir(parents=True, exist_ok=True)
            
            self.after(0, lambda: self.loading_screen.update_status("Checking API configuration..."))
            
            # Check API keys
            api_keys = self.config_manager.get_api_keys()
            self.api_keys_ready = bool(api_keys['unsplash'] and api_keys['openai'])
            
            if self.api_keys_ready:
                self.after(0, lambda: self.loading_screen.update_status("Initializing API clients..."))
                self.setup_api_clients(api_keys)
            else:
                self.after(0, lambda: self.loading_screen.update_status("API keys not configured"))
            
            self.after(0, lambda: self.loading_screen.update_status("Loading application data..."))
            
            # Load application data
            self.load_application_data()
            
            self.after(0, lambda: self.loading_screen.update_status("Completing initialization..."))
            
            # Complete initialization
            self.after(0, self.complete_initialization)
            
        except Exception as e:
            self.after(0, lambda: self.handle_initialization_error(f"Initialization failed: {e}"))
    
    def setup_api_clients(self, api_keys):
        """Set up API clients if keys are available."""
        try:
            self.UNSPLASH_ACCESS_KEY = api_keys['unsplash']
            self.OPENAI_API_KEY = api_keys['openai']
            self.GPT_MODEL = api_keys['gpt_model']
            
            # Initialize OpenAI client
            if self.OPENAI_API_KEY and OpenAI:
                self.openai_client = OpenAI(api_key=self.OPENAI_API_KEY)
                
                # Update ClickableText with OpenAI service if it exists
                if hasattr(self, 'description_text') and hasattr(self.description_text, 'openai_service'):
                    # Create a simple OpenAI service wrapper
                    class OpenAIServiceWrapper:
                        def __init__(self, client, model):
                            self.client = client
                            self.model = model
                    
                    self.description_text.openai_service = OpenAIServiceWrapper(self.openai_client, self.GPT_MODEL)
                
        except Exception as e:
            print(f"Error setting up API clients: {e}")
            self.api_keys_ready = False
    
    def load_application_data(self):
        """Load existing application data."""
        try:
            # Initialize CSV if it doesn't exist
            if not self.CSV_TARGET_WORDS.exists():
                with open(self.CSV_TARGET_WORDS, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
            
            # Load vocabulary cache
            self.load_vocabulary_cache()
            
            # Load used image URLs
            self.load_used_image_urls_from_log()
            
        except Exception as e:
            print(f"Error loading application data: {e}")
    
    def complete_initialization(self):
        """Complete initialization and update UI."""
        try:
            # Hide loading screen
            if hasattr(self, 'loading_screen'):
                self.loading_screen.destroy()
            
            # Update UI based on API status
            if self.api_keys_ready:
                self.enable_api_dependent_features()
                self.update_status("Ready - API keys configured")
                self.stats_label.config(text=f"Model: {self.GPT_MODEL} | Ready")
            else:
                self.show_api_setup_needed()
                self.update_status("Ready - Click 'Setup API Keys' to configure")
                self.stats_label.config(text="API Status: Not Configured")
            
            # Enable basic features
            self.note_text.config(state=tk.NORMAL)
            
            # Update ClickableText with managers if available
            if hasattr(self, 'description_text') and hasattr(self, 'vocabulary_manager'):
                if hasattr(self.description_text, 'vocabulary_manager'):
                    self.description_text.vocabulary_manager = self.vocabulary_manager
            
            # Initialize style selector panel
            self.initialize_style_selector()
            
            # Set focus to search entry
            self.search_entry.focus_set()
            
            # Load last search if available
            self.load_last_search()
            
            self.initialization_complete = True
            
        except Exception as e:
            self.handle_initialization_error(f"Failed to complete initialization: {e}")
    
    def enable_api_dependent_features(self):
        """Enable features that require API keys."""
        self.search_button.config(state=tk.NORMAL)
        self.another_button.config(state=tk.NORMAL)
        self.newsearch_button.config(state=tk.NORMAL)
        self.generate_button.config(state=tk.NORMAL)
    
    def show_api_setup_needed(self):
        """Show UI indicating API setup is needed."""
        # Add setup button to main frame
        setup_button = ttk.Button(
            self.main_frame,
            text="🔑 Setup API Keys",
            command=self.show_api_setup
        )
        setup_button.pack(pady=10)
        
        # Show informational message in description area
        self.description_text.config(state=tk.NORMAL)
        self.description_text.insert(
            tk.END,
            "Welcome to Unsplash Image Search & GPT Description Tool!\n\n"
            "To get started, you'll need to configure your API keys:\n"
            "• Unsplash Access Key (for image search)\n"
            "• OpenAI API Key (for AI descriptions)\n\n"
            "Click 'Setup API Keys' to configure these settings."
        )
        self.description_text.config(state=tk.DISABLED)
    
    def show_api_setup(self):
        """Show API key setup dialog."""
        try:
            from config_manager import SetupWizard
            wizard = SetupWizard(self, self.config_manager)
            self.wait_window(wizard)
            
            if wizard.result:
                # Reload configuration and restart initialization
                self.restart_with_new_config()
                
        except Exception as e:
            messagebox.showerror("Setup Error", f"Failed to show setup wizard: {e}")
    
    def restart_with_new_config(self):
        """Restart app with new configuration."""
        messagebox.showinfo(
            "Configuration Updated",
            "API keys have been saved. Please restart the application to use the new configuration."
        )
        self.on_exit()
    
    def handle_initialization_error(self, error_message):
        """Handle initialization errors gracefully."""
        if hasattr(self, 'loading_screen'):
            self.loading_screen.destroy()
        
        self.update_status(f"Initialization error: {error_message}")
        
        # Show error in description area
        self.description_text.config(state=tk.NORMAL)
        self.description_text.insert(
            tk.END,
            f"Initialization Error:\n{error_message}\n\n"
            "The application may have limited functionality. "
            "Please check your configuration and restart."
        )
        self.description_text.config(state=tk.DISABLED)
        
        # Enable note text for user input
        self.note_text.config(state=tk.NORMAL)
        
        print(f"Initialization error: {error_message}")
        traceback.print_exc()
    
    def initialize_style_selector(self):
        """Initialize the style selector panel after full initialization."""
        try:
            if hasattr(self, 'style_frame') and hasattr(self, 'style_placeholder'):
                # Remove placeholder
                self.style_placeholder.destroy()
                
                # Create actual style selector if managers are available
                if self.style_manager and self.session_tracker:
                    self.style_selector_panel = StyleSelectorPanel(
                        self.style_frame,
                        session_tracker=self.session_tracker,
                        style_change_callback=self.on_style_change
                    )
                    self.style_selector_panel.pack(fill=tk.BOTH, expand=True)
                    
                    # Load style preferences
                    self.load_style_preferences()
                else:
                    # Show info message if managers not available
                    info_label = ttk.Label(
                        self.style_frame,
                        text="Selector de estilo no disponible (dependencias faltantes)",
                        foreground='orange'
                    )
                    info_label.pack(pady=10)
                    
        except Exception as e:
            print(f"Error initializing style selector: {e}")
            # Show error message in style frame
            if hasattr(self, 'style_frame'):
                error_label = ttk.Label(
                    self.style_frame,
                    text=f"Error al cargar selector de estilo: {e}",
                    foreground='red',
                    wraplength=400
                )
                error_label.pack(pady=10)
    
    def load_style_preferences(self):
        """Load and apply saved style preferences."""
        try:
            if self.session_tracker:
                preferences = self.session_tracker.load_style_preferences()
                
                # Apply to style manager
                if self.style_manager and preferences:
                    from src.features.description_styles import DescriptionStyle, VocabularyLevel
                    
                    # Set style
                    style_name = preferences.get('description_style', 'academic')
                    if style_name == 'academic':
                        self.style_manager.set_current_style(DescriptionStyle.ACADEMIC)
                    elif style_name == 'poetic':
                        self.style_manager.set_current_style(DescriptionStyle.POETIC)
                    elif style_name == 'technical':
                        self.style_manager.set_current_style(DescriptionStyle.TECHNICAL)
                    
                    # Set vocabulary level
                    vocab_level = preferences.get('vocabulary_level', 'intermediate')
                    if vocab_level == 'beginner':
                        self.style_manager.set_vocabulary_level(VocabularyLevel.BEGINNER)
                    elif vocab_level == 'intermediate':
                        self.style_manager.set_vocabulary_level(VocabularyLevel.INTERMEDIATE)
                    elif vocab_level == 'advanced':
                        self.style_manager.set_vocabulary_level(VocabularyLevel.ADVANCED)
                    elif vocab_level == 'native':
                        self.style_manager.set_vocabulary_level(VocabularyLevel.NATIVE)
                        
        except Exception as e:
            print(f"Error loading style preferences: {e}")
    
    def on_style_change(self, style, vocabulary_level):
        """Handle style change callback from style selector."""
        try:
            if self.session_tracker:
                # Save preferences
                preferences = {
                    'description_style': style.value if style else 'academic',
                    'vocabulary_level': vocabulary_level.value if vocabulary_level else 'intermediate'
                }
                self.session_tracker.save_style_preferences(preferences)
                
                # Update status
                style_display = style.value.title() if style else 'Academic'
                vocab_display = vocabulary_level.value.title() if vocabulary_level else 'Intermediate'
                self.update_status(f"Estilo actualizado: {style_display} - {vocab_display}")
                
        except Exception as e:
            print(f"Error handling style change: {e}")
            self.update_status("Error al guardar preferencias de estilo")
    
    def safe_search_image(self):
        """Safely handle search image request."""
        if not self.api_keys_ready:
            messagebox.showwarning("API Not Ready", "Please configure your API keys first.")
            return
        
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter a search query.")
            return
            
        self.search_image(query)
    
    def safe_another_image(self):
        """Safely handle another image request."""
        if not self.api_keys_ready:
            messagebox.showwarning("API Not Ready", "Please configure your API keys first.")
            return
            
        self.another_image()
    
    def safe_generate_description(self):
        """Safely handle generate description request."""
        if not self.api_keys_ready:
            messagebox.showwarning("API Not Ready", "Please configure your API keys first.")
            return
            
        self.generate_description()
    
    def search_image(self, query):
        """Search for images."""
        self.current_query = query
        self.current_page = 1
        self.current_index = 0
        self.images_collected_count = 0
        self.search_cancelled = False
        
        self.show_progress("Searching for images...")
        self.disable_buttons()
        
        threading.Thread(
            target=self.thread_search_images, 
            args=(query,), 
            daemon=True,
            name="ImageSearch"
        ).start()
    
    def thread_search_images(self, query):
        """Search for images in background thread."""
        try:
            headers = {"Authorization": f"Client-ID {self.UNSPLASH_ACCESS_KEY}"}
            url = f"https://api.unsplash.com/search/photos?query={query}&page={self.current_page}&per_page=10"
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            self.current_results = data.get("results", [])
            
            if not self.current_results:
                self.after(0, lambda: messagebox.showinfo("No Results", f"No images found for '{query}'."))
                return
            
            # Get first image
            result = self.get_next_image()
            if result:
                photo, pil_img = result
                self.after(0, lambda: self.display_image(photo, pil_img))
                
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Search Error", f"Failed to search images: {e}"))
        finally:
            self.after(0, self.hide_progress)
            self.after(0, self.enable_buttons)
    
    def get_next_image(self):
        """Get next image from current results."""
        if not self.current_results or self.current_index >= len(self.current_results):
            return None
            
        candidate = self.current_results[self.current_index]
        self.current_index += 1
        
        try:
            img_url = candidate["urls"]["regular"]
            img_response = requests.get(img_url, timeout=15)
            img_response.raise_for_status()
            
            image = Image.open(BytesIO(img_response.content))
            photo = ImageTk.PhotoImage(image)
            
            self.current_image_url = img_url
            self.used_image_urls.add(img_url)
            
            return photo, image
            
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    
    def another_image(self):
        """Get another image from current search."""
        if not self.current_query:
            messagebox.showerror("Error", "Please search for images first.")
            return
            
        self.show_progress("Loading another image...")
        self.disable_buttons()
        
        threading.Thread(
            target=self.thread_get_next_image, 
            daemon=True,
            name="GetNextImage"
        ).start()
    
    def thread_get_next_image(self):
        """Get next image in background thread."""
        try:
            result = self.get_next_image()
            if result:
                photo, pil_img = result
                self.after(0, lambda: self.display_image(photo, pil_img))
            else:
                self.after(0, lambda: messagebox.showinfo("No More Images", "No more images available."))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to load image: {e}"))
        finally:
            self.after(0, self.hide_progress)
            self.after(0, self.enable_buttons)
    
    def display_image(self, photo, pil_image=None):
        """Display image in UI."""
        self.image_label.config(image=photo, text="")
        self.image_label.image = photo
        
        if pil_image:
            self.current_pil_image = pil_image
        
        # Clear previous content
        self.note_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.DISABLED)
        
        self.update_status("Image loaded successfully")
    
    def generate_description(self):
        """Generate AI description for current image."""
        if not self.openai_client:
            messagebox.showerror("Error", "OpenAI client not initialized.")
            return
            
        if not hasattr(self, 'current_image_url') or not self.current_image_url:
            messagebox.showerror("Error", "No image loaded.")
            return
        
        user_note = self.note_text.get("1.0", tk.END).strip()
        
        self.show_progress("Generating AI description...")
        self.disable_buttons()
        
        threading.Thread(
            target=self.thread_generate_description,
            args=(user_note,),
            daemon=True,
            name="GenerateDescription"
        ).start()
    
    def thread_generate_description(self, user_note):
        """Generate description in background thread."""
        try:
            # Get current style and generate appropriate prompt
            if self.style_manager:
                # Use style manager to generate prompt
                focus_areas = []
                if user_note:
                    focus_areas = [user_note]
                
                prompt = self.style_manager.generate_description_prompt(
                    context=user_note,
                    focus_areas=focus_areas
                )
            else:
                # Fallback to basic prompt if style manager not available
                base_prompt = "Analiza esta imagen y descríbela en español latinoamericano.\n\n"
                
                style_instruction = (
                    "Usa vocabulario claro y natural. "
                    "Enfócate en describir lo que ves de manera directa."
                )
                
                vocab_instruction = "Usa vocabulario apropiado para estudiantes intermedios."
                
                content_guidelines = (
                    "DESCRIBE ÚNICAMENTE lo que observas en la imagen:\n"
                    "• Objetos, personas o animales que aparecen\n"
                    "• Colores predominantes\n"
                    "• Lo que está sucediendo en la escena\n"
                    "• Ubicación (interior/exterior)\n"
                    "• Detalles que destacan\n"
                )
                
                format_instruction = "Redacta 1-2 párrafos descriptivos y naturales."
                
                prompt = f"{base_prompt}\n{style_instruction}\n{vocab_instruction}\n\n{content_guidelines}\n\n{format_instruction}"
                
                if user_note:
                    prompt += f"\n\nContexto adicional del usuario: {user_note}"
            
            response = self.openai_client.chat.completions.create(
                model=self.GPT_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": self.current_image_url, "detail": "high"}}
                        ]
                    }
                ],
                max_tokens=600,
                temperature=0.7,
            )
            
            generated_text = response.choices[0].message.content.strip()
            self.after(0, lambda: self.display_description(generated_text))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Generation Error", f"Failed to generate description: {e}"))
        finally:
            self.after(0, self.hide_progress)
            self.after(0, self.enable_buttons)
    
    def display_description(self, text):
        """Display generated description with clickable text functionality."""
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        
        # Update context for clickable text functionality
        if hasattr(self.description_text, 'update_context'):
            self.description_text.update_context(
                search_query=getattr(self, 'current_query', ''),
                image_url=getattr(self, 'current_image_url', '')
            )
        
        # Insert the text and make it clickable
        self.description_text.insert(tk.END, text)
        
        # Enable clickable functionality if available
        if hasattr(self.description_text, 'set_clickable'):
            self.description_text.set_clickable(True)
        
        self.description_text.config(state=tk.DISABLED)
        self.copy_desc_button.config(state=tk.NORMAL)
        self.update_status("Description generated successfully - Click words to add to vocabulary")
        
        # Extract vocabulary for quiz
        self.extract_vocabulary_for_quiz(text)
        
        # Enable quiz button if we have extracted phrases
        if hasattr(self, 'current_quiz_phrases') and self.current_quiz_phrases:
            self.quiz_button.config(state=tk.NORMAL)
            # Also enable quiz menu item
            if hasattr(self, 'tools_menu'):
                self.tools_menu.entryconfig(0, state=tk.NORMAL)
    
    def change_search(self):
        """Start new search."""
        self.search_entry.delete(0, tk.END)
        self.image_label.config(image="", text="No image loaded")
        self.image_label.image = None
        
        self.note_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.DISABLED)
        self.copy_desc_button.config(state=tk.DISABLED)
        
        self.current_query = ""
        self.current_results = []
        self.current_index = 0
        self.current_image_url = None
        
        # Clear quiz data
        self.current_quiz_phrases = []
        self.quiz_button.config(state=tk.DISABLED)
        # Also disable quiz menu item
        if hasattr(self, 'tools_menu'):
            self.tools_menu.entryconfig(0, state=tk.DISABLED)
        
        self.update_status("Ready for new search")
    
    def copy_description(self):
        """Copy the generated description to clipboard."""
        description = self.description_text.get("1.0", tk.END).strip()
        if description:
            self.clipboard_clear()
            self.clipboard_append(description)
            self.update_status("Description copied to clipboard")
    
    def show_progress(self, message="Loading..."):
        """Show progress indicator."""
        self.progress_bar.grid()
        self.progress_bar.start(10)
        self.update_status(message)
    
    def hide_progress(self):
        """Hide progress indicator."""
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
    
    def disable_buttons(self):
        """Disable buttons during operations."""
        self.search_button.config(state=tk.DISABLED)
        self.another_button.config(state=tk.DISABLED)
        self.newsearch_button.config(state=tk.DISABLED)
        self.generate_button.config(state=tk.DISABLED)
        self.quiz_button.config(state=tk.DISABLED)
        # Also disable quiz menu item
        if hasattr(self, 'tools_menu'):
            self.tools_menu.entryconfig(0, state=tk.DISABLED)
    
    def enable_buttons(self):
        """Enable buttons after operations."""
        if self.api_keys_ready:
            self.search_button.config(state=tk.NORMAL)
            self.another_button.config(state=tk.NORMAL)
            self.newsearch_button.config(state=tk.NORMAL)
            self.generate_button.config(state=tk.NORMAL)
            # Only enable quiz if we have phrases
            if hasattr(self, 'current_quiz_phrases') and self.current_quiz_phrases:
                self.quiz_button.config(state=tk.NORMAL)
                # Also enable quiz menu item
                if hasattr(self, 'tools_menu'):
                    self.tools_menu.entryconfig(0, state=tk.NORMAL)
    
    def update_status(self, message):
        """Update status bar message."""
        self.status_label.config(text=message)
        self.update_idletasks()
    
    def load_vocabulary_cache(self):
        """Load existing vocabulary to prevent duplicates."""
        try:
            if self.CSV_TARGET_WORDS.exists():
                with open(self.CSV_TARGET_WORDS, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'Spanish' in row:
                            self.vocabulary_cache.add(row['Spanish'])
        except Exception as e:
            print(f"Error loading vocabulary cache: {e}")
    
    def load_used_image_urls_from_log(self):
        """Load used image URLs from log file."""
        try:
            if self.LOG_FILENAME.exists():
                with open(self.LOG_FILENAME, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for session in data.get('sessions', []):
                        for entry in session.get('entries', []):
                            url = entry.get('image_url', '')
                            if url:
                                self.used_image_urls.add(url)
        except Exception as e:
            print(f"Error loading used URLs: {e}")
    
    def load_last_search(self):
        """Load the last search query from previous session."""
        try:
            last_search_file = self.DATA_DIR / "last_search.txt"
            if last_search_file.exists():
                with open(last_search_file, 'r', encoding='utf-8') as f:
                    last_query = f.read().strip()
                    if last_query:
                        self.search_entry.insert(0, last_query)
        except Exception as e:
            print(f"Error loading last search: {e}")
    
    
    def cancel_operation(self):
        """Cancel current operation."""
        self.search_cancelled = True
        self.hide_progress()
        self.enable_buttons()
        self.update_status("Operation cancelled")
    
    def on_exit(self):
        """Handle application exit."""
        try:
            # Save current search
            if hasattr(self, 'current_query') and self.current_query:
                last_search_file = self.DATA_DIR / "last_search.txt"
                with open(last_search_file, 'w', encoding='utf-8') as f:
                    f.write(self.current_query)
        except:
            pass
        
        self.destroy()
    
    def extract_vocabulary_for_quiz(self, description):
        """Extract vocabulary from description for quiz."""
        if not self.openai_client:
            return
            
        try:
            # Use existing OpenAI service to extract vocabulary
            vocabulary = self.extract_vocabulary_simple(description)
            
            # Flatten vocabulary into quiz phrases
            self.current_quiz_phrases = []
            for category, words in vocabulary.items():
                if isinstance(words, list):
                    self.current_quiz_phrases.extend(words[:3])  # Max 3 per category
            
            # Update vocabulary display
            self.display_vocabulary(vocabulary)
            
        except Exception as e:
            print(f"Error extracting vocabulary for quiz: {e}")
            self.current_quiz_phrases = []
    
    def extract_vocabulary_simple(self, description):
        """Simple vocabulary extraction from description."""
        try:
            # Use style manager if available for context-aware vocabulary extraction
            if self.style_manager:
                user_msg = self.style_manager.get_vocabulary_extraction_prompt(description)
            else:
                # Fallback to basic extraction
                user_msg = f"""Del siguiente texto en español, extrae vocabulario útil para aprender el idioma.
                
TEXTO: {description}

Devuelve un JSON con estas categorías (pueden estar vacías si no hay ejemplos):
- "Sustantivos": incluye el artículo (el/la), máximo 5
- "Verbos": forma conjugada encontrada, máximo 5
- "Adjetivos": con concordancia de género si aplica, máximo 5
- "Frases clave": expresiones de 2-4 palabras que sean útiles, máximo 5

Evita palabras muy comunes como: el, la, de, que, y, a, en, es, son
Solo devuelve el JSON, sin comentarios adicionales."""
            
            system_msg = (
                "You are a helpful assistant that returns only valid JSON. "
                "No disclaimers, no code fences, no extra text. If you have no data, return '{}'."
            )
            
            response = self.openai_client.chat.completions.create(
                model=self.GPT_MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                max_tokens=400,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            raw_str = response.choices[0].message.content.strip()
            vocabulary = json.loads(raw_str)
            
            # Ensure expected keys exist
            expected_keys = ['Sustantivos', 'Verbos', 'Adjetivos', 'Frases clave']
            for key in expected_keys:
                if key not in vocabulary:
                    vocabulary[key] = []
            
            return vocabulary
            
        except Exception as e:
            print(f"Error extracting vocabulary: {e}")
            return {}
    
    def display_vocabulary(self, vocabulary):
        """Display extracted vocabulary in the vocabulary text area."""
        self.vocab_text.config(state=tk.NORMAL)
        self.vocab_text.delete("1.0", tk.END)
        
        for category, words in vocabulary.items():
            if words:
                self.vocab_text.insert(tk.END, f"{category}:\n")
                for word in words:
                    self.vocab_text.insert(tk.END, f"  • {word}\n")
                self.vocab_text.insert(tk.END, "\n")
        
        self.vocab_text.config(state=tk.DISABLED)
    
    def open_vocabulary_quiz(self):
        """Open vocabulary quiz dialog."""
        if not hasattr(self, 'current_quiz_phrases') or not self.current_quiz_phrases:
            messagebox.showwarning("No Vocabulary", "No vocabulary available for quiz. Generate a description first.")
            return
        
        quiz_dialog = VocabularyQuizDialog(self, self.current_quiz_phrases, self.openai_client, self.GPT_MODEL)
        self.wait_window(quiz_dialog)
        
        # Update session statistics if quiz was completed
        if hasattr(quiz_dialog, 'quiz_completed') and quiz_dialog.quiz_completed:
            self.update_session_stats(quiz_dialog.score, quiz_dialog.total_questions)
    
    def update_session_stats(self, score, total):
        """Update session statistics after quiz."""
        accuracy = (score / total) * 100 if total > 0 else 0
        message = f"Quiz completed! Score: {score}/{total} ({accuracy:.1f}%)"
        
        # Update status
        self.update_status(message)
        
        # Show summary
        summary_msg = f"Quiz Summary:\n\nScore: {score} out of {total}\nAccuracy: {accuracy:.1f}%"
        if accuracy >= 80:
            summary_msg += "\n\n¡Excelente! Great job! 🎉"
        elif accuracy >= 60:
            summary_msg += "\n\n¡Bien hecho! Good work! 👍"
        else:
            summary_msg += "\n\nKeep practicing! ¡Sigue practicando! 💪"
        
        messagebox.showinfo("Quiz Results", summary_msg)
    
    # Menu Methods
    def new_search(self):
        """Start a new search (File menu)."""
        self.change_search()
    
    def export_vocabulary(self):
        """Export vocabulary to a file (File menu)."""
        try:
            if not self.CSV_TARGET_WORDS.exists():
                messagebox.showinfo("No Data", "No vocabulary data to export.")
                return
            
            from tkinter import filedialog
            
            # Ask user where to save the file
            filename = filedialog.asksaveasfilename(
                title="Export Vocabulary",
                defaultextension=".csv",
                filetypes=[
                    ("CSV files", "*.csv"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )
            
            if filename:
                # Copy the vocabulary file to the selected location
                import shutil
                shutil.copy2(self.CSV_TARGET_WORDS, filename)
                messagebox.showinfo("Export Complete", f"Vocabulary exported to:\n{filename}")
                self.update_status(f"Vocabulary exported to {filename}")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export vocabulary:\n{e}")
    
    def open_settings(self):
        """Open settings dialog (Edit menu)."""
        try:
            if hasattr(self, 'config_manager') and self.config_manager:
                from config_manager import SetupWizard
                wizard = SetupWizard(self, self.config_manager)
                self.wait_window(wizard)
                
                if hasattr(wizard, 'result') and wizard.result:
                    messagebox.showinfo(
                        "Settings Updated",
                        "Settings have been updated. Please restart the application to apply changes."
                    )
            else:
                messagebox.showwarning(
                    "Settings Unavailable",
                    "Settings are not available. Please restart the application."
                )
        except ImportError:
            messagebox.showerror(
                "Settings Error",
                "Settings module is not available. Please check your installation."
            )
        except Exception as e:
            messagebox.showerror("Settings Error", f"Failed to open settings:\n{e}")
    
    def clear_data(self):
        """Clear application data (Edit menu)."""
        result = messagebox.askyesno(
            "Clear Data",
            "This will clear all vocabulary data and session history.\n\n"
            "This action cannot be undone. Are you sure?",
            icon='warning'
        )
        
        if result:
            try:
                # Clear vocabulary file
                if self.CSV_TARGET_WORDS.exists():
                    with open(self.CSV_TARGET_WORDS, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
                
                # Clear log file
                if hasattr(self, 'LOG_FILENAME') and self.LOG_FILENAME.exists():
                    self.LOG_FILENAME.unlink()
                
                # Clear application state
                self.vocabulary_cache.clear()
                self.log_entries.clear()
                self.extracted_phrases.clear()
                self.target_phrases.clear()
                self.used_image_urls.clear()
                self.current_quiz_phrases = []
                
                # Clear UI
                self.vocab_text.config(state=tk.NORMAL)
                self.vocab_text.delete("1.0", tk.END)
                self.vocab_text.config(state=tk.DISABLED)
                
                messagebox.showinfo("Data Cleared", "All application data has been cleared.")
                self.update_status("Application data cleared")
                
            except Exception as e:
                messagebox.showerror("Clear Error", f"Failed to clear data:\n{e}")
    
    def toggle_theme(self):
        """Toggle between light and dark themes (View menu)."""
        # For now, just show a placeholder message
        # In a full implementation, this would switch between light/dark themes
        messagebox.showinfo(
            "Theme Toggle",
            "Theme switching is not yet implemented.\n"
            "This feature would toggle between light and dark themes."
        )
    
    def zoom_in(self):
        """Increase font size/zoom level (View menu)."""
        if self.zoom_level < 200:
            self.zoom_level += 10
            self.apply_zoom()
            self.update_status(f"Zoom: {self.zoom_level}%")
    
    def zoom_out(self):
        """Decrease font size/zoom level (View menu)."""
        if self.zoom_level > 50:
            self.zoom_level -= 10
            self.apply_zoom()
            self.update_status(f"Zoom: {self.zoom_level}%")
    
    def reset_zoom(self):
        """Reset zoom to 100% (View menu)."""
        self.zoom_level = 100
        self.apply_zoom()
        self.update_status("Zoom reset to 100%")
    
    def apply_zoom(self):
        """Apply current zoom level to text widgets."""
        try:
            # Calculate font size based on zoom level
            base_font_size = 9
            current_font_size = int(base_font_size * (self.zoom_level / 100))
            
            # Apply to text widgets
            font_config = ("TkDefaultFont", current_font_size)
            
            if hasattr(self, 'note_text'):
                self.note_text.config(font=font_config)
            if hasattr(self, 'description_text'):
                self.description_text.config(font=font_config)
            if hasattr(self, 'vocab_text'):
                self.vocab_text.config(font=font_config)
                
        except Exception as e:
            print(f"Error applying zoom: {e}")
    
    def view_statistics(self):
        """View application statistics (Tools menu)."""
        try:
            # Count vocabulary entries
            vocab_count = 0
            if self.CSV_TARGET_WORDS.exists():
                with open(self.CSV_TARGET_WORDS, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    vocab_count = max(0, sum(1 for row in reader) - 1)  # Subtract header row
            
            # Count image searches
            search_count = len(self.used_image_urls)
            
            # Count current session phrases
            session_phrases = len(self.current_quiz_phrases) if hasattr(self, 'current_quiz_phrases') else 0
            
            stats_text = f"""Application Statistics:

Vocabulary Collected: {vocab_count} entries
Images Searched: {search_count} images
Current Session Phrases: {session_phrases} phrases

Zoom Level: {self.zoom_level}%
API Status: {"Connected" if self.api_keys_ready else "Not Configured"}
Model: {getattr(self, 'GPT_MODEL', 'Not Set')}

Data Directory: {getattr(self, 'DATA_DIR', 'Not Set')}"""
            
            messagebox.showinfo("Statistics", stats_text)
            
        except Exception as e:
            messagebox.showerror("Statistics Error", f"Failed to generate statistics:\n{e}")
    
    def show_shortcuts(self):
        """Show keyboard shortcuts (Help menu)."""
        shortcuts_text = """Keyboard Shortcuts:

FILE:
• Ctrl+N - New Search
• Ctrl+E - Export Vocabulary
• Ctrl+Q - Exit Application

EDIT:
• Ctrl+, - Open Settings
• (No shortcut) - Clear Data

VIEW:
• Ctrl+T - Toggle Theme
• Ctrl++ - Zoom In
• Ctrl+- - Zoom Out
• Ctrl+0 - Reset Zoom

TOOLS:
• Ctrl+G - Quiz Me
• (No shortcut) - View Statistics

GENERAL:
• F1 - About Dialog
• Escape - Cancel Operation
• Enter - Submit/Search (when in text fields)"""
        
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
    
    def show_about(self):
        """Show about dialog (Help menu)."""
        about_text = """Unsplash Image Search & GPT Description Tool

Version 2.0

A powerful application for searching Unsplash images and generating AI-powered descriptions in Spanish for language learning.

FEATURES:
• Search high-quality images from Unsplash
• Generate detailed Spanish descriptions using GPT
• Interactive vocabulary extraction and learning
• Built-in vocabulary quiz system
• Export vocabulary for external study

APIS USED:
• Unsplash API - for image search
• OpenAI GPT API - for AI descriptions

SHORTCUTS:
Press F1 or Help → Shortcuts for keyboard shortcuts

Developed with Python, Tkinter, and OpenAI"""
        
        messagebox.showinfo("About", about_text)


class VocabularyQuizDialog(tk.Toplevel):
    """Dialog for vocabulary quiz."""
    
    def __init__(self, parent, phrases, openai_client, model):
        super().__init__(parent)
        self.parent = parent
        self.phrases = phrases[:10]  # Limit to 10 questions
        self.openai_client = openai_client
        self.model = model
        
        self.current_question = 0
        self.score = 0
        self.total_questions = len(self.phrases)
        self.quiz_completed = False
        self.translations = {}
        
        self.setup_dialog()
        self.load_translations()
    
    def setup_dialog(self):
        """Set up the quiz dialog UI."""
        self.title("Vocabulary Quiz")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # Center on parent
        self.transient(self.parent)
        self.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Progress label
        self.progress_label = ttk.Label(
            main_frame, 
            text=f"Question 1 of {self.total_questions}",
            font=('Arial', 12, 'bold')
        )
        self.progress_label.pack(pady=(0, 20))
        
        # Question frame
        question_frame = ttk.LabelFrame(main_frame, text="Question", padding="15")
        question_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.question_label = ttk.Label(
            question_frame,
            text="Loading...",
            font=('Arial', 14),
            wraplength=400
        )
        self.question_label.pack()
        
        # Answer frame
        answer_frame = ttk.LabelFrame(main_frame, text="Your Answer", padding="15")
        answer_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.answer_var = tk.StringVar()
        self.answer_entry = ttk.Entry(
            answer_frame,
            textvariable=self.answer_var,
            font=('Arial', 12),
            width=40
        )
        self.answer_entry.pack()
        self.answer_entry.bind('<Return>', lambda e: self.check_answer())
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.submit_button = ttk.Button(
            buttons_frame,
            text="Submit Answer",
            command=self.check_answer
        )
        self.submit_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.skip_button = ttk.Button(
            buttons_frame,
            text="Skip",
            command=self.skip_question
        )
        self.skip_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            buttons_frame,
            text="Cancel",
            command=self.destroy
        ).pack(side=tk.RIGHT)
        
        # Result label (initially hidden)
        self.result_label = ttk.Label(
            main_frame,
            text="",
            font=('Arial', 11),
            foreground="green"
        )
        self.result_label.pack(pady=(10, 0))
        
        # Score label
        self.score_label = ttk.Label(
            main_frame,
            text=f"Score: {self.score}/{self.total_questions}",
            font=('Arial', 10)
        )
        self.score_label.pack(side=tk.BOTTOM, pady=(10, 0))
    
    def load_translations(self):
        """Load translations for all phrases."""
        self.progress_label.config(text="Loading translations...")
        self.update_idletasks()
        
        threading.Thread(
            target=self._load_translations_thread,
            daemon=True
        ).start()
    
    def _load_translations_thread(self):
        """Load translations in background thread."""
        try:
            for phrase in self.phrases:
                if phrase not in self.translations:
                    translation = self.translate_phrase(phrase)
                    self.translations[phrase] = translation
            
            # Start the quiz on the main thread
            self.after(0, self.start_quiz)
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to load translations: {e}"))
    
    def translate_phrase(self, phrase):
        """Translate a Spanish phrase to English."""
        try:
            prompt = f"Translate this Spanish phrase to English: '{phrase}'. Provide only the translation."
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.0
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error translating '{phrase}': {e}")
            return "[Translation Error]"
    
    def start_quiz(self):
        """Start the quiz with the first question."""
        if not self.phrases:
            messagebox.showwarning("No Questions", "No vocabulary available for quiz.")
            self.destroy()
            return
        
        self.show_question()
        self.answer_entry.focus_set()
    
    def show_question(self):
        """Show the current question."""
        if self.current_question >= len(self.phrases):
            self.finish_quiz()
            return
        
        phrase = self.phrases[self.current_question]
        self.progress_label.config(text=f"Question {self.current_question + 1} of {self.total_questions}")
        self.question_label.config(text=f"What does '{phrase}' mean in English?")
        self.answer_var.set("")
        self.result_label.config(text="")
        self.answer_entry.focus_set()
    
    def check_answer(self):
        """Check the user's answer."""
        if self.current_question >= len(self.phrases):
            return
        
        user_answer = self.answer_var.get().strip().lower()
        phrase = self.phrases[self.current_question]
        correct_answer = self.translations.get(phrase, "").lower()
        
        if not user_answer:
            messagebox.showwarning("Empty Answer", "Please enter an answer or click Skip.")
            return
        
        # Simple similarity check
        is_correct = self.is_answer_correct(user_answer, correct_answer)
        
        if is_correct:
            self.score += 1
            self.result_label.config(text="✓ Correct!", foreground="green")
        else:
            self.result_label.config(
                text=f"✗ Correct answer: {self.translations.get(phrase, 'Unknown')}",
                foreground="red"
            )
        
        self.score_label.config(text=f"Score: {self.score}/{self.total_questions}")
        
        # Disable input temporarily
        self.submit_button.config(state=tk.DISABLED)
        self.skip_button.config(text="Next")
        
        # Auto-advance after 2 seconds
        self.after(2000, self.next_question)
    
    def is_answer_correct(self, user_answer, correct_answer):
        """Check if the user's answer is correct (simple similarity)."""
        if not correct_answer:
            return False
        
        # Simple checks for correctness
        user_words = set(user_answer.split())
        correct_words = set(correct_answer.split())
        
        # Check for exact match
        if user_answer == correct_answer:
            return True
        
        # Check for significant word overlap
        common_words = user_words.intersection(correct_words)
        if len(common_words) >= min(2, len(correct_words)):
            return True
        
        # Check for key word presence
        for word in correct_words:
            if len(word) > 3 and word in user_answer:
                return True
        
        return False
    
    def skip_question(self):
        """Skip current question or move to next."""
        if self.skip_button.cget('text') == 'Next':
            self.next_question()
        else:
            phrase = self.phrases[self.current_question]
            self.result_label.config(
                text=f"Skipped. Answer: {self.translations.get(phrase, 'Unknown')}",
                foreground="orange"
            )
            self.after(1500, self.next_question)
    
    def next_question(self):
        """Move to the next question."""
        self.current_question += 1
        self.submit_button.config(state=tk.NORMAL)
        self.skip_button.config(text="Skip")
        self.show_question()
    
    def finish_quiz(self):
        """Finish the quiz and show results."""
        self.quiz_completed = True
        accuracy = (self.score / self.total_questions) * 100
        
        # Update UI to show completion
        self.progress_label.config(text="Quiz Complete!")
        self.question_label.config(text=f"Final Score: {self.score}/{self.total_questions} ({accuracy:.1f}%)")
        
        # Hide quiz controls
        self.answer_entry.pack_forget()
        self.submit_button.pack_forget()
        self.skip_button.pack_forget()
        
        # Show close button
        ttk.Button(
            self.result_label.master,
            text="Close",
            command=self.destroy
        ).pack(pady=10)
        
        # Auto-close after 5 seconds
        self.after(5000, self.destroy)


def main():
    """Main entry point for the fixed application."""
    try:
        # Create and run the application
        app = ImageSearchApp()
        app.mainloop()
        
    except Exception as e:
        # Show error dialog if the application fails to start
        error_root = tk.Tk()
        error_root.withdraw()  # Hide the root window
        
        error_message = (
            f"Application failed to start:\n\n{str(e)}\n\n"
            "Please check your Python installation and try again."
        )
        
        messagebox.showerror("Application Error", error_message)
        
        print(f"Application error: {e}")
        traceback.print_exc()
        
        error_root.destroy()


if __name__ == "__main__":
    main()