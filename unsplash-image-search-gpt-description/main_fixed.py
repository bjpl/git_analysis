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
        self.api_keys_ready = False
        self.initialization_complete = False
        
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
        
        # UI state
        self.zoom_level = 100
        self.loading_animation_id = None
        
        # API clients (will be set up later)
        self.openai_client = None
        self.UNSPLASH_ACCESS_KEY = ""
        self.OPENAI_API_KEY = ""
        self.GPT_MODEL = "gpt-4o-mini"
        
        # Initialize UI immediately - this is critical
        self.create_basic_ui()
        
        # Start async initialization
        self.after(100, self.start_async_initialization)
    
    def create_basic_ui(self):
        """Create basic UI structure immediately."""
        self.loading_screen.update_status("Creating user interface...")
        
        try:
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
        
        self.description_text = scrolledtext.ScrolledText(
            desc_frame, 
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
        
    def setup_basic_shortcuts(self):
        """Set up basic keyboard shortcuts."""
        self.bind('<Control-q>', lambda e: self.on_exit())
        self.bind('<F1>', lambda e: self.show_help())
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
            prompt = """Analyze this image and describe it in Latin American Spanish.

IMPORTANT: Describe ONLY what you see in this specific image:
- What objects, people, or animals appear?
- What are the predominant colors?
- What is happening in the scene?
- Where does it seem to be located (indoor/outdoor)?
- What details stand out?

Write 1-2 descriptive and natural paragraphs."""
            
            if user_note:
                prompt += f"\n\nAdditional context from user: {user_note}"
            
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
        """Display generated description."""
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.insert(tk.END, text)
        self.description_text.config(state=tk.DISABLED)
        self.copy_desc_button.config(state=tk.NORMAL)
        self.update_status("Description generated successfully")
    
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
    
    def enable_buttons(self):
        """Enable buttons after operations."""
        if self.api_keys_ready:
            self.search_button.config(state=tk.NORMAL)
            self.another_button.config(state=tk.NORMAL)
            self.newsearch_button.config(state=tk.NORMAL)
            self.generate_button.config(state=tk.NORMAL)
    
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
    
    def show_help(self):
        """Show help dialog."""
        help_text = """
Unsplash Image Search & GPT Description Tool

FEATURES:
• Search and view Unsplash images
• AI-powered image descriptions in Spanish
• Vocabulary learning and extraction

KEYBOARD SHORTCUTS:
• Ctrl+Q - Quit application
• F1 - Show this help
• Escape - Cancel current operation

GETTING STARTED:
1. Configure your API keys (Unsplash + OpenAI)
2. Enter a search query and press Enter
3. Generate AI descriptions for learning

Developed with OpenAI GPT and Unsplash API
        """.strip()
        
        messagebox.showinfo("Help", help_text)
    
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