import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from PIL import Image, ImageTk
from io import BytesIO
import threading
from openai import OpenAI
import os
import sys
import json
import re
import csv
import time
from pathlib import Path
from datetime import datetime
from config_manager import ConfigManager, ensure_api_keys_configured
import traceback
import logging

# Import theme manager
sys.path.append(str(Path(__file__).parent.parent / 'src'))
try:
    from src.ui.theme_manager import ThemeManager, ThemedTooltip, ThemedMessageBox
except ImportError:
    print("Warning: Theme manager not available - using basic UI")
    ThemeManager = None
    ThemedTooltip = None
    ThemedMessageBox = None

# ─── CONFIGURATION ─────────────────────────────────────────────
# Configuration is now handled by ConfigManager
# API keys are loaded from environment variables or config.ini


class UIFixedImageSearchApp(tk.Tk):
    """
    Fixed version of the Image Search App that ensures proper UI initialization.
    
    This version:
    - Separates UI creation from API configuration
    - Provides detailed debug logging
    - Handles configuration errors gracefully
    - Ensures main window always displays properly
    - Fixes race conditions between dialogs and main window
    """

    def __init__(self):
        super().__init__()
        
        # Initialize debug logging first
        self._setup_debug_logging()
        self.debug_log("Starting application initialization")
        
        # Initialize basic window properties immediately
        self._init_basic_window_properties()
        
        # Initialize UI state variables
        self._init_ui_state_variables()
        
        # Create basic UI structure first (always create UI)
        self.debug_log("Creating basic UI structure")
        self._create_basic_ui()
        
        # Show window and ensure it's visible
        self._ensure_window_visible()
        
        # Handle configuration in background
        self.debug_log("Handling API configuration")
        self._handle_configuration_async()
        
        # Set up cleanup handlers
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        
        self.debug_log("Application initialization completed")

    def _setup_debug_logging(self):
        """Set up debug logging system for troubleshooting."""
        self.debug_messages = []
        self.debug_enabled = True
        self.max_debug_messages = 100
        
        # Create log directory
        log_dir = Path("debug_logs")
        log_dir.mkdir(exist_ok=True)
        
        # Set up file logging
        self.debug_log_file = log_dir / f"ui_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Set up logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.debug_log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Debug logging initialized")
    
    def debug_log(self, message):
        """Add debug message with timestamp."""
        if not self.debug_enabled:
            return
            
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        debug_msg = f"[{timestamp}] {message}"
        
        # Add to in-memory log
        self.debug_messages.append(debug_msg)
        if len(self.debug_messages) > self.max_debug_messages:
            self.debug_messages.pop(0)
        
        # Log to file
        self.logger.debug(message)
        
        # Print to console
        print(debug_msg)
    
    def _init_basic_window_properties(self):
        """Initialize basic window properties immediately."""
        self.debug_log("Initializing basic window properties")
        
        try:
            self.title("Unsplash Image Search & GPT Description - Initializing...")
            self.geometry("1100x800")
            self.resizable(True, True)
            
            # Set minimum size to prevent invisibility
            self.minsize(800, 600)
            
            # Center window on screen
            self.update_idletasks()
            x = (self.winfo_screenwidth() // 2) - 550
            y = (self.winfo_screenheight() // 2) - 400
            self.geometry(f"1100x800+{x}+{y}")
            
            # Force window to front
            self.lift()
            self.attributes('-topmost', True)
            self.after(100, lambda: self.attributes('-topmost', False))
            
            self.debug_log("Basic window properties initialized successfully")
            
        except Exception as e:
            self.debug_log(f"Error initializing window properties: {e}")
            # Continue anyway - don't let this stop UI creation
    
    def _init_ui_state_variables(self):
        """Initialize UI state variables."""
        self.debug_log("Initializing UI state variables")
        
        # Configuration state
        self.config_manager = None
        self.config_ready = False
        self.config_error = None
        
        # API configuration
        self.UNSPLASH_ACCESS_KEY = ""
        self.OPENAI_API_KEY = ""
        self.GPT_MODEL = "gpt-4o-mini"
        self.openai_client = None
        
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
        
        # Collection state
        self.max_images_per_search = 30
        self.images_collected_count = 0
        self.search_cancelled = False
        self.search_state = 'idle'
        
        # UI state
        self.zoom_level = 100
        self.loading_animation_id = None
        
        # Theme management
        self.theme_manager = None
        
        self.debug_log("UI state variables initialized")
    
    def _create_basic_ui(self):
        """Create basic UI structure that always works."""
        self.debug_log("Creating basic UI structure")
        
        try:
            # Create main container
            self.main_frame = ttk.Frame(self, padding="10")
            self.main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Create status area first
            self._create_status_area()
            
            # Create search area
            self._create_search_area()
            
            # Create content area
            self._create_content_area()
            
            # Show initial status
            self.update_status("Initializing application...")
            
            self.debug_log("Basic UI structure created successfully")
            
        except Exception as e:
            self.debug_log(f"Error creating basic UI: {e}")
            self._create_fallback_ui()
    
    def _create_fallback_ui(self):
        """Create minimal fallback UI if main UI creation fails."""
        self.debug_log("Creating fallback UI")
        
        try:
            # Clear any existing widgets
            for widget in self.winfo_children():
                widget.destroy()
            
            # Create simple error display
            error_frame = tk.Frame(self, bg='white')
            error_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            title_label = tk.Label(
                error_frame,
                text="Unsplash Image Search & GPT Description",
                font=('Arial', 16, 'bold'),
                bg='white'
            )
            title_label.pack(pady=20)
            
            status_label = tk.Label(
                error_frame,
                text="Application is starting up...\nPlease wait while we configure your settings.",
                font=('Arial', 12),
                bg='white',
                justify=tk.CENTER
            )
            status_label.pack(pady=20)
            
            # Store reference to status label for updates
            self.fallback_status_label = status_label
            
            self.debug_log("Fallback UI created successfully")
            
        except Exception as e:
            self.debug_log(f"Critical error: Could not create even fallback UI: {e}")
            # Last resort - just show the window with a basic label
            try:
                basic_label = tk.Label(self, text="Application Starting...", font=('Arial', 14))
                basic_label.pack(expand=True)
            except:
                pass  # If even this fails, at least the window will show
    
    def _create_status_area(self):
        """Create status and statistics area."""
        self.debug_log("Creating status area")
        
        # Status frame at top for visibility
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(
            status_frame, 
            text="Ready", 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            font=('TkDefaultFont', 10)
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Session stats
        self.stats_label = ttk.Label(
            status_frame, 
            text="Images: 0 | Words: 0 | Ready", 
            relief=tk.SUNKEN, 
            anchor=tk.E
        )
        self.stats_label.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.debug_log("Status area created")
    
    def _create_search_area(self):
        """Create search controls area."""
        self.debug_log("Creating search area")
        
        # Search frame
        search_frame = ttk.Frame(self.main_frame, padding="5")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search label and entry
        ttk.Label(search_frame, text="Search Unsplash:").grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.grid(row=0, column=1, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.search_image())
        
        # Search button
        self.search_button = ttk.Button(
            search_frame, 
            text="Search Images", 
            command=self.search_image
        )
        self.search_button.grid(row=0, column=2, padx=5)
        
        # Progress bar
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(
            search_frame, 
            mode='indeterminate',
            variable=self.progress_var
        )
        self.progress_bar.grid(row=0, column=3, padx=5, sticky="ew")
        self.progress_bar.grid_remove()  # Hidden by default
        
        # Control buttons row
        self.another_button = ttk.Button(
            search_frame, 
            text="Another Image", 
            command=self.another_image
        )
        self.another_button.grid(row=1, column=0, padx=5, pady=(5, 0), sticky=tk.W)
        
        self.newsearch_button = ttk.Button(
            search_frame, 
            text="New Search", 
            command=self.change_search
        )
        self.newsearch_button.grid(row=1, column=1, padx=5, pady=(5, 0), sticky=tk.W)
        
        # Generate description button
        self.generate_desc_button = ttk.Button(
            search_frame, 
            text="Generate Description", 
            command=self.generate_description
        )
        self.generate_desc_button.grid(row=1, column=2, padx=5, pady=(5, 0), sticky=tk.W)
        
        # Configuration button
        self.config_button = ttk.Button(
            search_frame,
            text="⚙️ Setup",
            command=self.show_configuration_dialog
        )
        self.config_button.grid(row=1, column=3, padx=5, pady=(5, 0), sticky=tk.W)
        
        self.debug_log("Search area created")
    
    def _create_content_area(self):
        """Create main content area."""
        self.debug_log("Creating content area")
        
        # Content frame
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Left side - Image preview
        image_frame = ttk.LabelFrame(content_frame, text="Image Preview", padding="10")
        image_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        image_frame.rowconfigure(0, weight=1)
        image_frame.columnconfigure(0, weight=1)
        
        # Image display
        self.image_canvas = tk.Canvas(image_frame, bg='white', relief=tk.SUNKEN, bd=1)
        self.image_canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars for image
        v_scrollbar_img = ttk.Scrollbar(image_frame, orient="vertical", command=self.image_canvas.yview)
        v_scrollbar_img.grid(row=0, column=1, sticky="ns")
        h_scrollbar_img = ttk.Scrollbar(image_frame, orient="horizontal", command=self.image_canvas.xview)
        h_scrollbar_img.grid(row=1, column=0, sticky="ew")
        
        self.image_canvas.configure(
            yscrollcommand=v_scrollbar_img.set,
            xscrollcommand=h_scrollbar_img.set
        )
        
        # Image label inside canvas
        self.image_label = tk.Label(
            self.image_canvas, 
            text="No image loaded\n\nSearch for images to begin",
            font=('Arial', 12),
            fg='gray',
            bg='white'
        )
        self.image_canvas_window = self.image_canvas.create_window(0, 0, anchor="nw", window=self.image_label)
        
        # Right side - Text areas
        self.text_area_frame = ttk.Frame(content_frame)
        self.text_area_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.text_area_frame.rowconfigure(0, weight=1)
        self.text_area_frame.rowconfigure(1, weight=1)
        self.text_area_frame.rowconfigure(2, weight=1)
        self.text_area_frame.columnconfigure(0, weight=1)
        
        # Notes area
        notes_frame = ttk.LabelFrame(self.text_area_frame, text="Your Notes", padding="10")
        notes_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        notes_frame.rowconfigure(0, weight=1)
        notes_frame.columnconfigure(0, weight=1)
        
        self.note_text = scrolledtext.ScrolledText(notes_frame, wrap=tk.WORD, height=6)
        self.note_text.grid(row=0, column=0, sticky="nsew")
        
        # Description area
        desc_frame = ttk.LabelFrame(self.text_area_frame, text="GPT Description", padding="10")
        desc_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 5))
        desc_frame.rowconfigure(0, weight=1)
        desc_frame.columnconfigure(0, weight=1)
        
        self.description_text = scrolledtext.ScrolledText(
            desc_frame, 
            wrap=tk.WORD, 
            state=tk.DISABLED,
            height=6,
            font=('TkDefaultFont', 11)
        )
        self.description_text.grid(row=0, column=0, sticky="nsew")
        
        # Vocabulary area
        vocab_frame = ttk.LabelFrame(self.text_area_frame, text="Vocabulary", padding="10")
        vocab_frame.grid(row=2, column=0, sticky="nsew")
        vocab_frame.rowconfigure(0, weight=1)
        vocab_frame.columnconfigure(0, weight=1)
        
        self.target_listbox = tk.Listbox(vocab_frame, height=8)
        self.target_listbox.grid(row=0, column=0, sticky="nsew")
        
        # Vocabulary scrollbar
        vocab_scroll = ttk.Scrollbar(vocab_frame, orient="vertical", command=self.target_listbox.yview)
        vocab_scroll.grid(row=0, column=1, sticky="ns")
        self.target_listbox.configure(yscrollcommand=vocab_scroll.set)
        
        self.debug_log("Content area created")
    
    def _ensure_window_visible(self):
        """Ensure the main window is visible and has focus."""
        self.debug_log("Ensuring window visibility")
        
        try:
            # Update the display
            self.update_idletasks()
            
            # Make sure window is visible
            self.deiconify()
            
            # Force window to front
            self.lift()
            self.focus_force()
            
            # Brief topmost to ensure visibility
            self.attributes('-topmost', True)
            self.after(200, lambda: self.attributes('-topmost', False))
            
            self.debug_log("Window visibility ensured")
            
        except Exception as e:
            self.debug_log(f"Error ensuring window visibility: {e}")
    
    def _handle_configuration_async(self):
        """Handle API configuration asynchronously to avoid blocking UI."""
        self.debug_log("Starting async configuration handling")
        
        # Start configuration in background thread
        thread = threading.Thread(target=self._configure_apis, daemon=True)
        thread.start()
        
        # Also start checking for configuration completion
        self.after(100, self._check_configuration_status)
    
    def _configure_apis(self):
        """Configure APIs in background thread."""
        self.debug_log("Configuring APIs in background")
        
        try:
            # Initialize configuration manager
            self.config_manager = ensure_api_keys_configured(None)  # No parent to avoid blocking
            
            if self.config_manager:
                self.debug_log("Configuration successful")
                self.config_ready = True
                
                # Load API keys
                api_keys = self.config_manager.get_api_keys()
                self.UNSPLASH_ACCESS_KEY = api_keys['unsplash']
                self.OPENAI_API_KEY = api_keys['openai']
                self.GPT_MODEL = api_keys['gpt_model']
                
                # Initialize OpenAI client
                if self.OPENAI_API_KEY:
                    self.openai_client = OpenAI(api_key=self.OPENAI_API_KEY)
                
                # Initialize paths and other components
                self._initialize_data_components()
                
            else:
                self.debug_log("Configuration was cancelled by user")
                self.config_error = "Configuration cancelled"
                
        except Exception as e:
            self.debug_log(f"Configuration error: {e}")
            self.config_error = str(e)
            traceback.print_exc()
    
    def _initialize_data_components(self):
        """Initialize data directories and files."""
        self.debug_log("Initializing data components")
        
        try:
            if not self.config_manager:
                return
                
            # Set up paths
            paths = self.config_manager.get_paths()
            self.DATA_DIR = paths['data_dir']
            self.LOG_FILENAME = paths['log_file']
            self.CSV_TARGET_WORDS = paths['vocabulary_file']
            
            # Ensure data directory exists
            self.DATA_DIR.mkdir(parents=True, exist_ok=True)
            
            # Initialize CSV file
            if not self.CSV_TARGET_WORDS.exists():
                with open(self.CSV_TARGET_WORDS, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
            
            # Load cached data
            self.load_used_image_urls_from_log()
            self.load_vocabulary_cache()
            
            self.debug_log("Data components initialized")
            
        except Exception as e:
            self.debug_log(f"Error initializing data components: {e}")
    
    def _check_configuration_status(self):
        """Check configuration status and update UI accordingly."""
        if self.config_ready:
            self.debug_log("Configuration ready - updating UI")
            self._on_configuration_ready()
        elif self.config_error:
            self.debug_log(f"Configuration error detected: {self.config_error}")
            self._on_configuration_error()
        else:
            # Still configuring, check again soon
            self.after(100, self._check_configuration_status)
    
    def _on_configuration_ready(self):
        """Handle successful configuration."""
        self.debug_log("Configuration ready - updating UI")
        
        # Update window title
        self.title(f"Unsplash & GPT Tool - Model: {self.GPT_MODEL} - Ready")
        
        # Update status
        self.update_status("Ready - API keys configured successfully")
        
        # Enable all buttons
        self._enable_ui_controls()
        
        # Initialize theme manager if available
        self._initialize_theme_manager()
        
        # Update stats
        self.update_stats()
        
        self.debug_log("UI updated for ready state")
    
    def _on_configuration_error(self):
        """Handle configuration errors."""
        self.debug_log("Handling configuration error")
        
        # Update title to show error state
        self.title("Unsplash & GPT Tool - Configuration Required")
        
        # Update status
        self.update_status(f"Configuration needed - Click Setup to configure API keys")
        
        # Disable API-dependent buttons but keep UI functional
        self._disable_api_buttons()
        
        self.debug_log("UI updated for error state")
    
    def _enable_ui_controls(self):
        """Enable all UI controls."""
        try:
            self.search_button.config(state=tk.NORMAL)
            self.another_button.config(state=tk.NORMAL)
            self.newsearch_button.config(state=tk.NORMAL)
            self.generate_desc_button.config(state=tk.NORMAL)
        except Exception as e:
            self.debug_log(f"Error enabling controls: {e}")
    
    def _disable_api_buttons(self):
        """Disable buttons that require API access."""
        try:
            self.search_button.config(state=tk.DISABLED)
            self.generate_desc_button.config(state=tk.DISABLED)
            # Keep other buttons enabled for basic functionality
        except Exception as e:
            self.debug_log(f"Error disabling API buttons: {e}")
    
    def _initialize_theme_manager(self):
        """Initialize theme manager if available."""
        if ThemeManager and self.config_manager:
            try:
                self.theme_manager = ThemeManager(self.config_manager)
                self.theme_manager.initialize(self)
                self.debug_log("Theme manager initialized")
            except Exception as e:
                self.debug_log(f"Could not initialize theme manager: {e}")
    
    # ─── UI EVENT HANDLERS ─────────────────────────────
    
    def update_status(self, message):
        """Update status label safely."""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.config(text=message)
            elif hasattr(self, 'fallback_status_label'):
                self.fallback_status_label.config(text=message)
            
            self.update_idletasks()
            
        except Exception as e:
            self.debug_log(f"Error updating status: {e}")
    
    def update_stats(self):
        """Update session statistics display."""
        try:
            if hasattr(self, 'stats_label'):
                image_count = len(self.used_image_urls)
                word_count = len(self.vocabulary_cache) + len(self.target_phrases)
                progress_text = f"{self.images_collected_count}/{self.max_images_per_search}"
                self.stats_label.config(text=f"Images: {image_count} | Words: {word_count} | Progress: {progress_text}")
                self.update_idletasks()
        except Exception as e:
            self.debug_log(f"Error updating stats: {e}")
    
    def show_configuration_dialog(self):
        """Show API configuration dialog."""
        self.debug_log("Showing configuration dialog")
        
        try:
            # Create a new config manager for the dialog
            from config_manager import SetupWizard, ConfigManager
            
            config_manager = ConfigManager()
            wizard = SetupWizard(self, config_manager)
            self.wait_window(wizard)
            
            if wizard.result:
                self.debug_log("User completed configuration")
                # Reload configuration
                self.config_manager = config_manager
                self.config_ready = True
                self.config_error = None
                self._on_configuration_ready()
            else:
                self.debug_log("User cancelled configuration")
                
        except Exception as e:
            self.debug_log(f"Error showing configuration dialog: {e}")
            messagebox.showerror(
                "Configuration Error",
                f"Could not open configuration dialog:\n{e}"
            )
    
    # ─── SEARCH FUNCTIONALITY ─────────────────────────────
    
    def search_image(self):
        """Search for images on Unsplash."""
        self.debug_log("Search image requested")
        
        if not self.config_ready or not self.UNSPLASH_ACCESS_KEY:
            self.show_api_not_configured_message()
            return
        
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter a search query.")
            return
        
        self.debug_log(f"Starting search for: {query}")
        self.update_status(f"Searching for '{query}'...")
        
        # Start search in background
        thread = threading.Thread(target=self._perform_search, args=(query,), daemon=True)
        thread.start()
    
    def _perform_search(self, query):
        """Perform search in background thread."""
        try:
            self.debug_log(f"Performing search for: {query}")
            
            # Make API call to Unsplash
            headers = {"Authorization": f"Client-ID {self.UNSPLASH_ACCESS_KEY}"}
            url = f"https://api.unsplash.com/search/photos?query={query}&page=1&per_page=10"
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            if results:
                self.debug_log(f"Found {len(results)} images")
                # Load first image
                first_image = results[0]
                self._load_image(first_image["urls"]["regular"])
            else:
                self.after(0, lambda: self.update_status(f"No images found for '{query}'"))
                
        except Exception as e:
            self.debug_log(f"Search error: {e}")
            self.after(0, lambda: self.update_status(f"Search error: {e}"))
    
    def _load_image(self, image_url):
        """Load image from URL."""
        try:
            self.debug_log(f"Loading image: {image_url[:50]}...")
            
            response = requests.get(image_url, timeout=15)
            response.raise_for_status()
            
            image = Image.open(BytesIO(response.content))
            # Resize for display
            image.thumbnail((400, 400))
            photo = ImageTk.PhotoImage(image)
            
            # Update UI in main thread
            self.after(0, lambda: self._display_image(photo, image_url))
            
        except Exception as e:
            self.debug_log(f"Error loading image: {e}")
            self.after(0, lambda: self.update_status(f"Error loading image: {e}"))
    
    def _display_image(self, photo, image_url):
        """Display image in UI."""
        self.debug_log("Displaying image")
        
        try:
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo  # Keep reference
            self.current_image_url = image_url
            
            # Update canvas scroll region
            self.image_canvas.update_idletasks()
            self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all"))
            
            self.update_status("Image loaded successfully")
            
        except Exception as e:
            self.debug_log(f"Error displaying image: {e}")
    
    def another_image(self):
        """Get another image from current search."""
        self.update_status("Getting another image...")
        # Implementation would go here
    
    def change_search(self):
        """Start a new search."""
        self.search_entry.delete(0, tk.END)
        self.image_label.config(
            image="", 
            text="No image loaded\n\nSearch for images to begin",
            compound=tk.CENTER
        )
        self.image_label.image = None
        self.current_image_url = None
        self.update_status("Ready for new search")
    
    # ─── GPT FUNCTIONALITY ─────────────────────────────
    
    def generate_description(self):
        """Generate description using GPT."""
        self.debug_log("Generate description requested")
        
        if not self.config_ready or not self.openai_client:
            self.show_api_not_configured_message()
            return
        
        if not self.current_image_url:
            messagebox.showerror("Error", "No image loaded. Please search for an image first.")
            return
        
        user_note = self.note_text.get("1.0", tk.END).strip()
        
        self.debug_log("Starting GPT description generation")
        self.update_status("Analyzing image with GPT...")
        
        # Start generation in background
        thread = threading.Thread(
            target=self._generate_description_background, 
            args=(user_note,), 
            daemon=True
        )
        thread.start()
    
    def _generate_description_background(self, user_note):
        """Generate description in background thread."""
        try:
            self.debug_log("Generating description with GPT")
            
            # Prepare prompt
            text_prompt = """Analyze the image and describe it in Latin American Spanish.
            
IMPORTANT: Describe ONLY what you see in this specific image:
- What objects, people, or animals appear?
- What are the predominant colors?
- What is happening in the scene?
- Where does it seem to be located (interior/exterior)?
- What details stand out?

Write 1-2 descriptive and natural paragraphs."""
            
            if user_note:
                text_prompt += f"\n\nAdditional user context: {user_note}"
            
            # Make GPT API call
            response = self.openai_client.chat.completions.create(
                model=self.GPT_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": text_prompt},
                            {"type": "image_url", "image_url": {"url": self.current_image_url, "detail": "high"}}
                        ]
                    }
                ],
                max_tokens=600,
                temperature=0.7,
            )
            
            description = response.choices[0].message.content.strip()
            self.debug_log(f"Generated description: {description[:50]}...")
            
            # Update UI in main thread
            self.after(0, lambda: self._display_description(description))
            
        except Exception as e:
            self.debug_log(f"GPT error: {e}")
            self.after(0, lambda: self.update_status(f"GPT error: {e}"))
    
    def _display_description(self, description):
        """Display generated description."""
        try:
            self.description_text.config(state=tk.NORMAL)
            self.description_text.delete("1.0", tk.END)
            self.description_text.insert(tk.END, description)
            self.description_text.config(state=tk.DISABLED)
            
            self.update_status("Description generated successfully")
            
        except Exception as e:
            self.debug_log(f"Error displaying description: {e}")
    
    # ─── UTILITY METHODS ─────────────────────────────
    
    def show_api_not_configured_message(self):
        """Show message when APIs are not configured."""
        messagebox.showwarning(
            "API Not Configured",
            "API keys are not configured. Please click the Setup button to configure your Unsplash and OpenAI API keys."
        )
    
    def load_used_image_urls_from_log(self):
        """Load used image URLs from session log."""
        try:
            if hasattr(self, 'LOG_FILENAME') and self.LOG_FILENAME.exists():
                with open(self.LOG_FILENAME, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for session in data.get('sessions', []):
                        for entry in session.get('entries', []):
                            url = entry.get('image_url', '')
                            if url:
                                self.used_image_urls.add(url.split('?')[0])
                self.debug_log(f"Loaded {len(self.used_image_urls)} used image URLs")
        except Exception as e:
            self.debug_log(f"Error loading used image URLs: {e}")
    
    def load_vocabulary_cache(self):
        """Load vocabulary cache to prevent duplicates."""
        try:
            if hasattr(self, 'CSV_TARGET_WORDS') and self.CSV_TARGET_WORDS.exists():
                with open(self.CSV_TARGET_WORDS, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'Spanish' in row:
                            self.vocabulary_cache.add(row['Spanish'])
                self.debug_log(f"Loaded {len(self.vocabulary_cache)} vocabulary words")
        except Exception as e:
            self.debug_log(f"Error loading vocabulary cache: {e}")
    
    def show_debug_info(self):
        """Show debug information dialog."""
        debug_window = tk.Toplevel(self)
        debug_window.title("Debug Information")
        debug_window.geometry("800x600")
        
        # Debug text area
        debug_text = scrolledtext.ScrolledText(debug_window, wrap=tk.WORD)
        debug_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add debug messages
        debug_info = "\n".join(self.debug_messages)
        debug_text.insert(tk.END, debug_info)
        debug_text.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = tk.Frame(debug_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            button_frame, 
            text="Save Debug Log", 
            command=lambda: self._save_debug_log(debug_info)
        ).pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="Close", command=debug_window.destroy).pack(side=tk.RIGHT)
    
    def _save_debug_log(self, debug_info):
        """Save debug log to file."""
        try:
            with open(self.debug_log_file, 'w', encoding='utf-8') as f:
                f.write(debug_info)
            messagebox.showinfo("Debug Log Saved", f"Debug log saved to:\n{self.debug_log_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save debug log:\n{e}")
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts."""
        try:
            # Basic shortcuts
            self.bind('<Control-n>', lambda e: self.change_search())
            self.bind('<Control-g>', lambda e: self.generate_description())
            self.bind('<Control-q>', lambda e: self.on_exit())
            self.bind('<F1>', lambda e: self.show_debug_info())
            
            self.debug_log("Keyboard shortcuts configured")
        except Exception as e:
            self.debug_log(f"Error setting up shortcuts: {e}")
    
    def on_exit(self):
        """Handle application exit."""
        self.debug_log("Application exit requested")
        
        try:
            # Save any session data if configured
            if self.config_ready and hasattr(self, 'log_entries') and self.log_entries:
                self._save_session_data()
            
            self.debug_log("Application shutdown complete")
            
        except Exception as e:
            self.debug_log(f"Error during shutdown: {e}")
        
        self.destroy()
    
    def _save_session_data(self):
        """Save session data before exit."""
        try:
            if not hasattr(self, 'LOG_FILENAME'):
                return
                
            # Load existing data
            if self.LOG_FILENAME.exists():
                with open(self.LOG_FILENAME, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {"sessions": []}
            
            # Add current session if we have entries
            if self.log_entries:
                session = {
                    "session_start": self.log_entries[0].get("timestamp", datetime.now().isoformat()),
                    "session_end": datetime.now().isoformat(),
                    "entries": self.log_entries,
                    "vocabulary_learned": len(self.target_phrases),
                    "target_phrases": self.target_phrases
                }
                data["sessions"].append(session)
                
                # Save to file
                with open(self.LOG_FILENAME, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
                self.debug_log("Session data saved")
                
        except Exception as e:
            self.debug_log(f"Error saving session data: {e}")


def main():
    """Main entry point with comprehensive error handling."""
    print("Starting Unsplash Image Search & GPT Description Tool...")
    
    try:
        # Create and run the application
        app = UIFixedImageSearchApp()
        
        # Setup keyboard shortcuts after UI is ready
        app.after(500, app.setup_keyboard_shortcuts)
        
        # Start the main loop
        print("Application UI created successfully - starting main loop")
        app.mainloop()
        
    except Exception as e:
        print(f"Critical application error: {e}")
        traceback.print_exc()
        
        # Show error dialog if possible
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Application Error",
                f"Failed to start application:\n\n{str(e)}\n\nPlease check the debug log for more information."
            )
            root.destroy()
        except:
            print("Could not show error dialog")


if __name__ == "__main__":
    main()
