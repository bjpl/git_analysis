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

# Import theme manager
sys.path.append(str(Path(__file__).parent / 'src'))
from src.ui.theme_manager import ThemeManager, ThemedTooltip, ThemedMessageBox

# ─── CONFIGURATION ─────────────────────────────────────────────
# Configuration is now handled by ConfigManager
# API keys are loaded from environment variables or config.ini


class ImageSearchApp(tk.Tk):
    """
    Aplicación Tkinter que:
      - Busca imágenes en Unsplash (con paginación)
      - Muestra una vista previa de la imagen (izquierda)
      - Acepta notas del usuario y muestra una descripción generada por GPT (derecha)
      - Usa un modelo de GPT con capacidad de visión para generar descripciones en español
      - Extrae palabras/frases clave (sustantivos con artículos, verbos, adjetivos, adverbios, frases) en orden alfabético
      - Muestra esas frases como botones clicables
      - Al hacer clic en una frase, se traduce del español al inglés (EE.UU.) y se registra en un archivo CSV
      - Registra todo en un archivo de sesión y permite "Otra Imagen" y "Nueva Búsqueda"
    """

    def __init__(self):
        super().__init__()
        
        # Initialize configuration (but don't block UI creation)
        self.config_manager = ensure_api_keys_configured(self)
        if not self.config_manager:
            # User cancelled setup - create default config instead of exiting
            from config_manager import ConfigManager
            self.config_manager = ConfigManager()
            # Continue with UI creation even without API keys
            
        # MOVED: Defer heavy initialization until after UI is created
        # Performance optimization will be initialized after create_widgets()
        self.performance_optimizer = None
        
        # Initialize theme manager
        self.theme_manager = ThemeManager(self.config_manager)
        # MOVED: Defer theme initialization until after widgets exist
        # self.theme_manager.initialize(self)  # Will be called after create_widgets()
        
        # Theme change callback
        self.theme_manager.register_theme_callback(self.on_theme_change)
        
        # Load API keys and paths
        api_keys = self.config_manager.get_api_keys()
        paths = self.config_manager.get_paths()
        
        self.UNSPLASH_ACCESS_KEY = api_keys['unsplash']
        self.OPENAI_API_KEY = api_keys['openai']
        self.GPT_MODEL = api_keys['gpt_model']
        
        # Initialize OpenAI client with new SDK
        self.openai_client = OpenAI(api_key=self.OPENAI_API_KEY)
        
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
        
        self.title("Búsqueda de Imágenes en Unsplash & Descripción GPT")
        self.geometry("1100x800")
        self.resizable(True, True)

        self.log_entries = []
        self.extracted_phrases = {}
        self.target_phrases = []
        self.used_image_urls = set()
        self.vocabulary_cache = set()  # Cache to prevent duplicates
        self.image_cache = {}  # Simple cache for downloaded images

        # Estado de paginación
        self.current_query = ""
        self.current_page = 0
        self.current_results = []
        self.current_index = 0
        self.current_image_url = None
        
        # Collection limits and search state
        self.max_images_per_search = int(self.config_manager.config.get('Search', 'max_images_per_search', fallback='30'))
        self.images_collected_count = 0
        self.search_cancelled = False
        self.search_state = 'idle'  # idle, searching, paused, cancelled

        self.load_used_image_urls_from_log()
        self.load_vocabulary_cache()

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Initialize UI state
        self.zoom_level = float(self.config_manager.config.get('UI', 'zoom_level', fallback='100'))
        self.loading_animation_id = None
        
        self.create_widgets()
        
        # NOW initialize theme after widgets exist
        self.theme_manager.initialize(self)
        
        # NOW initialize performance optimization after UI is ready
        self._initialize_performance_optimization()
        
        self.setup_keyboard_shortcuts()
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        
        # Show API status in title
        self.update_title_with_status()
        
        # Load last search if exists
        self.load_last_search()
        
        # Initialize stats
        self.update_stats()

    def _initialize_performance_optimization(self):
        """Initialize performance optimization components."""
        try:
            # Only initialize if API keys are available
            if not hasattr(self, 'UNSPLASH_ACCESS_KEY') or not self.UNSPLASH_ACCESS_KEY:
                print("Skipping performance optimization - API keys not configured")
                self.performance_optimizer = None
                self.optimized_collector = None
                self.unsplash_service = None
                return
                
            from src.performance_optimization import PerformanceOptimizer
            from src.optimized_image_collection import OptimizedImageCollector
            from src.services.unsplash_service import UnsplashService
            
            # Initialize Unsplash service
            self.unsplash_service = UnsplashService(self.UNSPLASH_ACCESS_KEY)
            
            # Initialize performance optimizer - but defer starting to avoid blocking
            self.performance_optimizer = PerformanceOptimizer(self, str(self.DATA_DIR))
            # Start optimization after a delay to let UI finish rendering
            self.after(1000, lambda: self._start_performance_monitoring())
            
            # Initialize optimized image collector
            self.optimized_collector = OptimizedImageCollector(self, self.unsplash_service)
            self.optimized_collector.initialize_optimization()
            
            print("Performance optimization system initialized successfully")
        except ImportError as e:
            print(f"Performance optimization not available: {e}")
            self.performance_optimizer = None
            self.optimized_collector = None
            self.unsplash_service = None
        except Exception as e:
            print(f"Error initializing performance optimization: {e}")
            self.performance_optimizer = None
            self.optimized_collector = None
            self.unsplash_service = None
            import traceback
            traceback.print_exc()
    
    def _start_performance_monitoring(self):
        """Start performance monitoring after UI is ready"""
        try:
            if self.performance_optimizer:
                self.performance_optimizer.start_optimization()
                print("Performance monitoring started")
        except Exception as e:
            print(f"Error starting performance monitoring: {e}")

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for the application."""
        # Ctrl+N: New search
        self.bind('<Control-n>', lambda e: self.change_search())
        # Ctrl+G: Generate description
        self.bind('<Control-g>', lambda e: self.generate_description())
        # Ctrl+E: Export vocabulary
        self.bind('<Control-e>', lambda e: self.export_vocabulary())
        # Ctrl+T: Toggle theme
        self.bind('<Control-t>', lambda e: self.toggle_theme())
        # Ctrl+Q: Quit application
        self.bind('<Control-q>', lambda e: self.on_exit())
        # F1: Help/About dialog
        self.bind('<F1>', lambda e: self.show_help_dialog())
        # Ctrl+Plus/Minus: Zoom
        self.bind('<Control-plus>', lambda e: self.adjust_zoom(10))
        self.bind('<Control-equal>', lambda e: self.adjust_zoom(10))  # For US keyboards
        self.bind('<Control-minus>', lambda e: self.adjust_zoom(-10))
        self.bind('<Control-0>', lambda e: self.reset_zoom())
        # Ctrl+P: Show performance dashboard
        self.bind('<Control-p>', lambda e: self.show_performance_dashboard())
        
        # Make widgets focusable for keyboard navigation
        self.focus_set()
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.theme_manager.toggle_theme()
        self.update_status(f"Switched to {self.theme_manager.current_theme} theme")
    
    def adjust_zoom(self, delta):
        """Adjust image zoom level."""
        self.zoom_level = max(50, min(200, self.zoom_level + delta))
        self.save_zoom_preference()
        if hasattr(self, 'current_pil_image'):
            self.refresh_image_display()
        self.update_status(f"Zoom: {self.zoom_level}%")
    
    def reset_zoom(self):
        """Reset zoom to 100%."""
        self.zoom_level = 100
        self.save_zoom_preference()
        if hasattr(self, 'current_pil_image'):
            self.refresh_image_display()
        self.update_status("Zoom reset to 100%")
    
    def save_zoom_preference(self):
        """Save zoom level to config."""
        try:
            if hasattr(self.config_manager, 'config'):
                self.config_manager.config.set('UI', 'zoom_level', str(self.zoom_level))
                with open(self.config_manager.config_file, 'w') as f:
                    self.config_manager.config.write(f)
        except Exception as e:
            print(f"Error saving zoom preference: {e}")
    
    def on_theme_change(self, theme_name, colors):
        """Handle theme change events."""
        # Update any custom widgets that need theme updates
        try:
            # Update text widgets
            if hasattr(self, 'note_text'):
                self.theme_manager.configure_widget(self.note_text, 'Text')
            if hasattr(self, 'description_text'):
                self.theme_manager.configure_widget(self.description_text, 'Text')
            if hasattr(self, 'target_listbox'):
                self.theme_manager.configure_widget(self.target_listbox, 'Listbox')
            if hasattr(self, 'extracted_canvas'):
                self.theme_manager.configure_widget(self.extracted_canvas, 'Canvas')
            
            # Update custom buttons in extracted phrases
            if hasattr(self, 'extracted_inner_frame'):
                for widget in self.extracted_inner_frame.winfo_children():
                    if isinstance(widget, tk.Frame):
                        for btn in widget.winfo_children():
                            if isinstance(btn, tk.Button):
                                btn.configure(
                                    bg=colors['frame_bg'],
                                    fg=colors['info'],
                                    activebackground=colors['button_active_bg'],
                                    highlightbackground=colors['border']
                                )
        except Exception as e:
            print(f"Error updating theme: {e}")
    
    def show_help_dialog(self):
        """Show help/about dialog."""
        help_text = """
Unsplash Image Search & GPT Description Tool

KEYBOARD SHORTCUTS:
• Ctrl+N - New search
• Ctrl+G - Generate description
• Ctrl+E - Export vocabulary
• Ctrl+T - Toggle theme (light/dark)
• Ctrl+Q - Quit application
• F1 - Show this help
• Ctrl+Plus/Minus - Zoom image
• Ctrl+0 - Reset zoom

FEATURES:
• Search and view Unsplash images
• AI-powered image descriptions
• Spanish vocabulary extraction
• Export to Anki, text, or CSV
• Dark/light theme support
• Image zoom functionality

CLICK:
• Blue words/phrases to add to vocabulary
• Export button for different formats
• Theme toggle in toolbar

Developed with OpenAI GPT and Unsplash API
Version 2.0 with Enhanced UI
        """.strip()
        
        # Create help dialog
        help_dialog = tk.Toplevel(self)
        help_dialog.title("Help & About")
        help_dialog.geometry("500x600")
        help_dialog.resizable(False, False)
        help_dialog.transient(self)
        help_dialog.grab_set()
        
        # Apply theme
        colors = self.theme_manager.get_colors()
        help_dialog.configure(bg=colors['bg'])
        
        # Center dialog
        help_dialog.update_idletasks()
        x = (help_dialog.winfo_screenwidth() // 2) - 250
        y = (help_dialog.winfo_screenheight() // 2) - 300
        help_dialog.geometry(f"+{x}+{y}")
        
        # Create text widget
        text_widget = tk.Text(
            help_dialog,
            wrap=tk.WORD,
            padx=20,
            pady=20,
            font=('TkDefaultFont', 10),
            state=tk.DISABLED
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Apply theme to text widget
        self.theme_manager.configure_widget(text_widget, 'Text')
        
        # Configure scrollbar for help text
        scrollbar = ttk.Scrollbar(help_dialog, orient="vertical", command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # Repack text widget
        text_widget.pack_forget()
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Insert help text
        text_widget.configure(state=tk.NORMAL)
        text_widget.insert(tk.END, help_text)
        text_widget.configure(state=tk.DISABLED)
        
        # Close button
        button_frame = tk.Frame(help_dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        close_btn = ttk.Button(
            button_frame,
            text="Close",
            command=help_dialog.destroy
        )
        close_btn.pack(side=tk.RIGHT)
    
    def update_title_with_status(self):
        """Update window title with API status."""
        model = self.GPT_MODEL
        theme = self.theme_manager.current_theme.title()
        self.title(f"Unsplash & GPT Tool - Model: {model} - Theme: {theme}")
    
    def load_last_search(self):
        """Load the last search query from previous session."""
        try:
            last_search_file = self.DATA_DIR / "last_search.txt"
            if last_search_file.exists():
                with open(last_search_file, 'r', encoding='utf-8') as f:
                    last_query = f.read().strip()
                    if last_query:
                        self.search_entry.insert(0, last_query)
                        self.search_entry.selection_range(0, tk.END)  # Select all text
        except:
            pass  # Ignore errors
    
    def save_last_search(self):
        """Save the current search query for next session."""
        try:
            if self.current_query:
                last_search_file = self.DATA_DIR / "last_search.txt"
                with open(last_search_file, 'w', encoding='utf-8') as f:
                    f.write(self.current_query)
        except:
            pass  # Ignore errors

    def canonicalize_url(self, url):
        """Retorna la URL base sin parámetros de consulta."""
        return url.split('?')[0] if url else ""

    def load_vocabulary_cache(self):
        """Load existing vocabulary to prevent duplicates."""
        if self.CSV_TARGET_WORDS.exists():
            try:
                with open(self.CSV_TARGET_WORDS, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'Spanish' in row:
                            self.vocabulary_cache.add(row['Spanish'])
            except Exception as e:
                # If file is corrupted or has old format, try to read as simple CSV
                try:
                    with open(self.CSV_TARGET_WORDS, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        next(reader, None)  # Skip header if exists
                        for row in reader:
                            if row and len(row) > 0:
                                self.vocabulary_cache.add(row[0])
                except Exception:
                    pass  # Start fresh if all fails

    def load_used_image_urls_from_log(self):
        """Carga URLs de imagen usadas desde el archivo de sesión JSON."""
        if self.LOG_FILENAME.exists():
            try:
                with open(self.LOG_FILENAME, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for session in data.get('sessions', []):
                        for entry in session.get('entries', []):
                            url = entry.get('image_url', '')
                            if url:
                                self.used_image_urls.add(self.canonicalize_url(url))
            except (json.JSONDecodeError, Exception):
                # If JSON is corrupted, try to read as text (backwards compatibility)
                try:
                    with open(self.LOG_FILENAME, "r", encoding="utf-8") as f:
                        for line in f:
                            if "URL de la Imagen" in line:
                                parts = line.split(":", 1)
                                if len(parts) == 2:
                                    url = parts[1].strip()
                                    if url:
                                        self.used_image_urls.add(self.canonicalize_url(url))
                except Exception:
                    pass

    def api_call_with_retry(self, func, *args, max_retries=3, **kwargs):
        """
        Execute an API call with exponential backoff retry logic.
        """
        last_exception = None
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                    self.update_status(f"API error, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                continue
            except Exception as e:
                last_exception = e
                if "rate_limit" in str(e).lower():
                    self.update_status("Rate limit reached. Please wait a moment...")
                    time.sleep(5)
                    continue
                break
        
        # If all retries failed
        raise last_exception

    def create_widgets(self):
        # Contenedor principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # CONTROLES DE BÚSQUEDA (arriba)
        search_frame = ttk.Frame(main_frame, padding="5")
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Consulta en Unsplash:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.grid(row=0, column=1, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.search_image())
        # Focus handling for accessibility
        self.search_entry.bind('<Tab>', self.focus_next_widget)
        self.search_entry.bind('<Shift-Tab>', self.focus_prev_widget)
        
        self.search_button = ttk.Button(search_frame, text="Buscar Imagen", command=self.search_image)
        self.search_button.grid(row=0, column=2, padx=5)
        # Add tooltip
        self.theme_manager.create_themed_tooltip(self.search_button, "Search for images on Unsplash (Enter)")
        
        # Progress bar for API calls
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(
            search_frame, 
            mode='indeterminate',
            variable=self.progress_var
        )
        self.progress_bar.grid(row=0, column=3, padx=5, sticky="ew")
        self.progress_bar.grid_remove()  # Hidden by default
        
        self.another_button = ttk.Button(search_frame, text="Otra Imagen", command=self.handle_another_image_click)
        self.another_button.grid(row=1, column=0, padx=5, pady=(5, 0), sticky=tk.W)
        self.theme_manager.create_themed_tooltip(self.another_button, "Get another image from current search")
        
        self.newsearch_button = ttk.Button(search_frame, text="Nueva Búsqueda", command=self.change_search_with_confirmation)
        self.newsearch_button.grid(row=1, column=1, padx=5, pady=(5, 0), sticky=tk.W)
        self.theme_manager.create_themed_tooltip(self.newsearch_button, "Start new search (Ctrl+N)")
        
        # Theme toggle button
        self.theme_button = ttk.Button(search_frame, text="🌓 Theme", command=self.toggle_theme)
        self.theme_button.grid(row=1, column=2, padx=5, pady=(5, 0), sticky=tk.W)
        self.theme_manager.create_themed_tooltip(self.theme_button, "Toggle light/dark theme (Ctrl+T)")
        
        # Export button
        self.export_button = ttk.Button(search_frame, text="📤 Export", command=self.export_vocabulary)
        self.export_button.grid(row=1, column=3, padx=5, pady=(5, 0), sticky=tk.W)
        self.theme_manager.create_themed_tooltip(self.export_button, "Export vocabulary (Ctrl+E)")
        
        # Performance dashboard button
        self.perf_button = ttk.Button(search_frame, text="⚡ Performance", command=self.show_performance_dashboard)
        self.perf_button.grid(row=2, column=0, padx=5, pady=(5, 0), sticky=tk.W)
        self.theme_manager.create_themed_tooltip(self.perf_button, "Show performance dashboard (Ctrl+P)")
        
        # Optimized collection button
        self.opt_collection_button = ttk.Button(search_frame, text="🚀 Optimized Search", command=self.start_optimized_collection)
        self.opt_collection_button.grid(row=2, column=1, padx=5, pady=(5, 0), sticky=tk.W)
        self.theme_manager.create_themed_tooltip(self.opt_collection_button, "Start optimized image collection")

        # BARRA DE ESTADO with statistics
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.status_label = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Session stats with collection progress
        self.stats_label = ttk.Label(status_frame, text="Images: 0 | Words: 0 | Progress: 0/30", relief=tk.SUNKEN, anchor=tk.E)
        self.stats_label.pack(side=tk.RIGHT, padx=(5, 0))

        # ÁREA DE CONTENIDO (Imagen a la izquierda, área de texto a la derecha)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # IZQUIERDA: Vista Previa de la Imagen with zoom controls
        image_frame = ttk.LabelFrame(content_frame, text="Vista Previa", padding="10")
        image_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        image_frame.rowconfigure(0, weight=1)
        image_frame.columnconfigure(0, weight=1)
        
        # Create scrollable canvas for image
        self.image_canvas = tk.Canvas(image_frame, bg='white')
        self.image_canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars for image canvas
        v_scrollbar_img = ttk.Scrollbar(image_frame, orient="vertical", command=self.image_canvas.yview)
        v_scrollbar_img.grid(row=0, column=1, sticky="ns")
        h_scrollbar_img = ttk.Scrollbar(image_frame, orient="horizontal", command=self.image_canvas.xview)
        h_scrollbar_img.grid(row=1, column=0, sticky="ew")
        
        self.image_canvas.configure(
            yscrollcommand=v_scrollbar_img.set,
            xscrollcommand=h_scrollbar_img.set
        )
        
        # Image label inside canvas
        self.image_label = tk.Label(self.image_canvas)
        self.image_canvas_window = self.image_canvas.create_window(0, 0, anchor="nw", window=self.image_label)
        
        # Zoom controls
        zoom_frame = ttk.Frame(image_frame)
        zoom_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        
        ttk.Label(zoom_frame, text="Zoom:").pack(side=tk.LEFT)
        
        zoom_out_btn = ttk.Button(zoom_frame, text="-", command=lambda: self.adjust_zoom(-10), width=3)
        zoom_out_btn.pack(side=tk.LEFT, padx=(5, 0))
        self.theme_manager.create_themed_tooltip(zoom_out_btn, "Zoom out (Ctrl+-)")
        
        self.zoom_label = ttk.Label(zoom_frame, text="100%")
        self.zoom_label.pack(side=tk.LEFT, padx=5)
        
        zoom_in_btn = ttk.Button(zoom_frame, text="+", command=lambda: self.adjust_zoom(10), width=3)
        zoom_in_btn.pack(side=tk.LEFT)
        self.theme_manager.create_themed_tooltip(zoom_in_btn, "Zoom in (Ctrl++)")
        
        reset_zoom_btn = ttk.Button(zoom_frame, text="Reset", command=self.reset_zoom)
        reset_zoom_btn.pack(side=tk.RIGHT)
        self.theme_manager.create_themed_tooltip(reset_zoom_btn, "Reset zoom to 100% (Ctrl+0)")
        
        # Bind mouse wheel for zooming
        self.image_canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.image_canvas.bind("<Button-4>", self.on_mouse_wheel)  # Linux
        self.image_canvas.bind("<Button-5>", self.on_mouse_wheel)  # Linux

        # DERECHA: Área de Texto (Notas, Descripción GPT, Sección Inferior)
        self.text_area_frame = ttk.Frame(content_frame)
        self.text_area_frame.grid(row=0, column=1, sticky="nsew")
        self.text_area_frame.rowconfigure(0, weight=1)  # Notas
        self.text_area_frame.rowconfigure(1, weight=1)  # Descripción GPT
        self.text_area_frame.rowconfigure(2, weight=0)  # Sección Inferior (Frases Extraídas y Frases Objetivo)
        self.text_area_frame.columnconfigure(0, weight=1)

        # 1) Notas del Usuario
        notes_frame = ttk.LabelFrame(self.text_area_frame, text="Tus Notas / Descripción", padding="10")
        notes_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=(0, 5))
        notes_frame.rowconfigure(0, weight=1)
        notes_frame.columnconfigure(0, weight=1)
        self.note_text = scrolledtext.ScrolledText(notes_frame, wrap=tk.WORD)
        self.note_text.grid(row=0, column=0, sticky="nsew")

        # 2) Descripción GPT
        desc_frame = ttk.LabelFrame(self.text_area_frame, text="Descripción Generada por GPT", padding="10")
        desc_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
        desc_frame.rowconfigure(0, weight=1)
        desc_frame.columnconfigure(0, weight=1)
        self.description_text = scrolledtext.ScrolledText(desc_frame, wrap=tk.WORD, state=tk.DISABLED)
        # Increase the font size for the description
        self.description_text.configure(font=("TkDefaultFont", 14))
        self.description_text.grid(row=0, column=0, sticky="nsew")
        
        # Button frame for description actions
        desc_button_frame = ttk.Frame(desc_frame)
        desc_button_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        
        self.generate_desc_button = ttk.Button(
            desc_button_frame, 
            text="Generar Descripción", 
            command=self.generate_description
        )
        self.generate_desc_button.pack(side=tk.RIGHT)
        self.theme_manager.create_themed_tooltip(self.generate_desc_button, "Generate AI description (Ctrl+G)")
        
        # Copy button for description
        self.copy_desc_button = ttk.Button(
            desc_button_frame,
            text="📋 Copiar",
            command=self.copy_description,
            state=tk.DISABLED
        )
        self.copy_desc_button.pack(side=tk.RIGHT, padx=(0, 5))
        self.theme_manager.create_themed_tooltip(self.copy_desc_button, "Copy description to clipboard")

        # 3) Sección Inferior: Frases Extraídas y Frases Objetivo
        bottom_frame = ttk.Frame(self.text_area_frame)
        bottom_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=(5, 5))
        bottom_frame.columnconfigure(0, weight=2)
        bottom_frame.columnconfigure(1, weight=1)

        # Frases Extraídas
        self.extracted_frame = ttk.LabelFrame(bottom_frame, text="Frases Extraídas", padding="10")
        self.extracted_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.extracted_canvas = tk.Canvas(self.extracted_frame)
        self.extracted_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll = ttk.Scrollbar(self.extracted_frame, orient="vertical", command=self.extracted_canvas.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.extracted_canvas.configure(yscrollcommand=v_scroll.set)
        self.extracted_inner_frame = ttk.Frame(self.extracted_canvas)
        self.extracted_canvas.create_window((0, 0), window=self.extracted_inner_frame, anchor="nw")
        self.extracted_inner_frame.bind("<Configure>", lambda e: self.extracted_canvas.configure(scrollregion=self.extracted_canvas.bbox("all")))
        self.extracted_placeholder = ttk.Label(self.extracted_inner_frame, text="No hay frases extraídas todavía.")
        self.extracted_placeholder.pack(anchor="w", padx=2, pady=2)

        # Frases Objetivo (Listbox)
        self.target_frame = ttk.LabelFrame(bottom_frame, text="Frases Objetivo", padding="10")
        self.target_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.target_listbox = tk.Listbox(self.target_frame)
        # Increase font size for target word list
        self.target_listbox.configure(font=("TkDefaultFont", 14))
        self.target_listbox.pack(fill=tk.BOTH, expand=True)

    def handle_another_image_click(self):
        """Handle Another Image button click - switches to Load More when needed."""
        if self.another_button.cget('text') == "Load More (30)":
            self.load_more_images()
        else:
            self.another_image()
    
    def show_progress(self, message="Loading..."):
        """Show progress bar during API calls with enhanced animation."""
        self.progress_bar.grid()
        if self.search_state == 'searching' and self.images_collected_count > 0:
            # Show determinate progress
            self.progress_bar.configure(mode='determinate')
            self.progress_var.set(self.images_collected_count)
        else:
            # Show indeterminate for initial search
            self.progress_bar.configure(mode='indeterminate')
            self.progress_bar.start(10)
        
        # Start loading animation in status
        self.start_loading_animation(message)
    
    def start_loading_animation(self, base_message):
        """Start animated loading text."""
        self.loading_dots = 0
        self.loading_base_message = base_message
        self.update_loading_animation()
    
    def update_loading_animation(self):
        """Update loading animation."""
        if hasattr(self, 'loading_base_message'):
            dots = '.' * (self.loading_dots % 4)
            self.update_status(f"{self.loading_base_message}{dots}")
            self.loading_dots += 1
            
            # Schedule next update
            self.loading_animation_id = self.after(500, self.update_loading_animation)
    
    def stop_loading_animation(self):
        """Stop loading animation."""
        if self.loading_animation_id:
            self.after_cancel(self.loading_animation_id)
            self.loading_animation_id = None
        if hasattr(self, 'loading_base_message'):
            del self.loading_base_message

    def hide_progress(self):
        """Hide progress bar after API calls."""
        self.progress_bar.stop()
        if self.search_state != 'searching' or self.search_cancelled:
            self.progress_bar.grid_remove()
        self.stop_loading_animation()

    def copy_description(self):
        """Copy the generated description to clipboard."""
        description = self.description_text.get("1.0", tk.END).strip()
        if description:
            self.clipboard_clear()
            self.clipboard_append(description)
            self.update_status("Description copied to clipboard")
    
    def show_enhanced_error(self, title, message, error_type="error"):
        """Show enhanced themed error dialog."""
        if error_type == "api":
            ThemedMessageBox.show_error(self, title, message, self.theme_manager)
        elif error_type == "warning":
            ThemedMessageBox.show_warning(self, title, message, self.theme_manager)
        else:
            ThemedMessageBox.show_error(self, title, message, self.theme_manager)

    def update_status(self, message):
        self.status_label.config(text=message)
        self.update_idletasks()  # Force UI update
    
    def update_stats(self):
        """Update session statistics display."""
        image_count = len(self.used_image_urls)
        word_count = len(self.vocabulary_cache) + len(self.target_phrases)
        progress_text = f"{self.images_collected_count}/{self.max_images_per_search}"
        self.stats_label.config(text=f"Images: {image_count} | Words: {word_count} | Progress: {progress_text}")
        self.update_idletasks()

    def disable_buttons(self):
        self.search_button.config(state=tk.DISABLED)
        self.another_button.config(state=tk.DISABLED)
        self.newsearch_button.config(state=tk.DISABLED)
        self.generate_desc_button.config(state=tk.DISABLED)
        if hasattr(self, 'theme_button'):
            self.theme_button.config(state=tk.DISABLED)
        if hasattr(self, 'export_button'):
            self.export_button.config(state=tk.DISABLED)
        # Keep stop button enabled during search
        if hasattr(self, 'stop_button') and self.search_state == 'searching':
            self.stop_button.config(state=tk.NORMAL)

    def enable_buttons(self):
        self.search_button.config(state=tk.NORMAL)
        self.another_button.config(state=tk.NORMAL)
        self.newsearch_button.config(state=tk.NORMAL)
        self.generate_desc_button.config(state=tk.NORMAL)
        if hasattr(self, 'theme_button'):
            self.theme_button.config(state=tk.NORMAL)
        if hasattr(self, 'export_button'):
            self.export_button.config(state=tk.NORMAL)

    # ─── LÓGICA DE BÚSQUEDA DE IMÁGENES Y PAGINACIÓN ─────────────────────────────
    def fetch_images_page(self, query, page):
        """Obtiene una página de resultados desde Unsplash para la consulta dada."""
        headers = {"Authorization": f"Client-ID {self.UNSPLASH_ACCESS_KEY}"}
        url = f"https://api.unsplash.com/search/photos?query={query}&page={page}&per_page=10"
        
        def make_request():
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        
        data = self.api_call_with_retry(make_request)
        return data.get("results", [])

    def get_next_image(self):
        """
        Retorna la siguiente imagen nueva para la consulta actual, evitando duplicados.
        Si se acaba la página actual, pasa a la siguiente.
        """
        while True:
            # Check collection limits first
            if self.images_collected_count >= self.max_images_per_search:
                self.show_collection_limit_reached()
                return None
            
            # Check if search was cancelled
            if self.search_cancelled:
                return None
            
            if self.current_index >= len(self.current_results):
                self.current_page += 1
                try:
                    new_results = self.fetch_images_page(self.current_query, self.current_page)
                except Exception as e:
                    error_msg = str(e)
                    if "403" in error_msg:
                        self.show_enhanced_error("API Error", "Unsplash API key may be invalid. Please check your configuration.", "api")
                    elif "rate" in error_msg.lower() or "429" in error_msg:
                        # Calculate time until reset (Unsplash resets hourly)
                        from datetime import datetime, timedelta
                        next_hour = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0)
                        minutes_left = int((next_hour - datetime.now()).seconds / 60)
                        self.show_enhanced_error("Rate Limit", f"Unsplash rate limit reached (50/hour).\n\nTry again in {minutes_left} minutes.", "warning")
                    else:
                        self.show_enhanced_error("Error", f"Error searching for images:\n{e}", "error")
                    return None

                if not new_results:
                    messagebox.showinfo("Sin más imágenes", f"No se encontraron más imágenes nuevas para '{self.current_query}'.")
                    return None

                self.current_results = new_results
                self.current_index = 0

            candidate = self.current_results[self.current_index]
            self.current_index += 1
            candidate_url = candidate["urls"]["regular"]
            canonical_url = self.canonicalize_url(candidate_url)
            if canonical_url not in self.used_image_urls:
                try:
                    # Check cache first
                    if canonical_url in self.image_cache:
                        img_data = self.image_cache[canonical_url]
                    else:
                        def download_image():
                            img_response = requests.get(candidate_url, timeout=15)
                            img_response.raise_for_status()
                            return img_response.content
                        
                        img_data = self.api_call_with_retry(download_image)
                        # Cache the image (keep last 10)
                        if len(self.image_cache) > 10:
                            # Remove oldest entry
                            self.image_cache.pop(next(iter(self.image_cache)))
                        self.image_cache[canonical_url] = img_data
                    
                    image = Image.open(BytesIO(img_data))
                    # Store original image
                    self.current_pil_image = image.copy()
                    
                    # Apply zoom
                    display_image = self.apply_zoom_to_image(image)
                    photo = ImageTk.PhotoImage(display_image)
                    
                    self.used_image_urls.add(canonical_url)
                    self.images_collected_count += 1  # Increment collection count
                    self.current_image_url = candidate_url
                    self.update_stats()  # Update image count
                    self.log_entries.append({
                        "timestamp": datetime.now().isoformat(),
                        "query": self.current_query,
                        "image_url": candidate_url,
                        "user_note": "",
                        "generated_description": ""
                    })
                    return photo, display_image
                except Exception as e:
                    print(f"Error downloading image: {e}")
                    continue

    def search_image(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Por favor ingresa una consulta de búsqueda.")
            return
        self.current_query = query
        self.current_page = 1
        self.current_index = 0
        self.images_collected_count = 0  # Reset collection count for new search
        self.search_cancelled = False  # Reset cancellation flag
        self.save_last_search()  # Remember this search
        
        self.show_progress(f"Searching '{query}' on Unsplash")
        self.disable_buttons()
        
        threading.Thread(target=self.thread_search_images, args=(query,), daemon=True).start()

    def thread_search_images(self, query):
        try:
            if self.search_cancelled:
                return
                
            self.current_results = self.fetch_images_page(query, self.current_page)
            
            if not self.current_results:
                self.after(0, lambda: messagebox.showinfo("Sin Resultados", f"No se encontraron imágenes para '{query}'."))
                self.after(0, self.hide_progress)
                self.after(0, self.enable_buttons)
                return
            
            if self.search_cancelled:
                return
                
            result = self.get_next_image()
            if result and not self.search_cancelled:
                photo, pil_img = result
                self.after(0, lambda: self.display_image(photo, pil_img))
        except Exception as e:
            if not self.search_cancelled:
                self.after(0, lambda: messagebox.showerror("Error", f"Error al buscar imágenes:\n{e}"))
        finally:
            if not self.search_cancelled:
                self.after(0, self.hide_progress)
            self.after(0, self.enable_buttons)

    def thread_get_next_image(self):
        try:
            if self.search_cancelled:
                return
                
            result = self.get_next_image()
            if result and not self.search_cancelled:
                photo, pil_img = result
                self.after(0, lambda: self.display_image(photo, pil_img))
        finally:
            if not self.search_cancelled:
                self.after(0, self.hide_progress)
            self.after(0, self.enable_buttons)

    def another_image(self):
        if not self.current_query:
            messagebox.showerror("Error", "Por favor ingresa una consulta antes.")
            return
        self.show_progress("Getting another image")
        self.disable_buttons()
        threading.Thread(target=self.thread_get_next_image, daemon=True).start()

    def display_image(self, photo, pil_image=None):
        self.image_label.config(image=photo)
        self.image_label.image = photo
        
        # Store PIL image for zoom functionality
        if pil_image:
            self.current_pil_image = pil_image
        
        # Update canvas scroll region
        self.image_canvas.update_idletasks()
        self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all"))
        
        # Center image in canvas
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()
        img_width = photo.width()
        img_height = photo.height()
        
        x = max(0, (canvas_width - img_width) // 2)
        y = max(0, (canvas_height - img_height) // 2)
        self.image_canvas.coords(self.image_canvas_window, x, y)
        
        self.note_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.DISABLED)
        self.copy_desc_button.config(state=tk.DISABLED)
        self.update_status("Image loaded successfully")
        self.enable_buttons()
        
        # Update zoom label
        if hasattr(self, 'zoom_label'):
            self.zoom_label.config(text=f"{self.zoom_level:.0f}%")
        
        # Configure canvas scrolling
        self.image_canvas.update_idletasks()
        self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all"))

    def apply_zoom_to_image(self, pil_image):
        """Apply current zoom level to PIL image."""
        if not pil_image:
            return None
            
        # Calculate new size based on zoom
        original_width, original_height = pil_image.size
        zoom_factor = self.zoom_level / 100.0
        
        # Limit maximum size to prevent memory issues
        max_width = 1200
        max_height = 1200
        
        new_width = int(original_width * zoom_factor)
        new_height = int(original_height * zoom_factor)
        
        # Apply maximum limits
        if new_width > max_width:
            ratio = max_width / new_width
            new_width = max_width
            new_height = int(new_height * ratio)
        
        if new_height > max_height:
            ratio = max_height / new_height
            new_height = max_height
            new_width = int(new_width * ratio)
        
        # Resize image
        return pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def refresh_image_display(self):
        """Refresh image display with current zoom level."""
        if hasattr(self, 'current_pil_image') and self.current_pil_image:
            display_image = self.apply_zoom_to_image(self.current_pil_image)
            if display_image:
                photo = ImageTk.PhotoImage(display_image)
                self.display_image(photo, display_image)
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel for zooming."""
        if event.state & 0x4:  # Ctrl key pressed
            if event.delta > 0 or event.num == 4:  # Zoom in
                self.adjust_zoom(10)
            else:  # Zoom out
                self.adjust_zoom(-10)
            return "break"
    
    def focus_next_widget(self, event):
        """Move focus to next widget."""
        event.widget.tk_focusNext().focus()
        return "break"
    
    def focus_prev_widget(self, event):
        """Move focus to previous widget."""
        event.widget.tk_focusPrev().focus()
        return "break"
    
    def change_search_with_confirmation(self):
        """Change search with confirmation if there's unsaved work."""
        if (hasattr(self, 'target_phrases') and self.target_phrases and 
            len(self.target_phrases) > 0):
            
            result = ThemedMessageBox.ask_yes_no(
                self, 
                "Confirm New Search", 
                f"You have {len(self.target_phrases)} vocabulary words in progress.\n\nStart new search anyway?",
                self.theme_manager
            )
            
            if not result:
                return
        
        self.change_search()
    
    def change_search(self):
        self.search_entry.delete(0, tk.END)
        # Clear image display
        self.image_label.config(image="")
        self.image_label.image = None
        if hasattr(self, 'current_pil_image'):
            del self.current_pil_image
        self.note_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.DISABLED)
        self.copy_desc_button.config(state=tk.DISABLED)
        self.update_status("Ready for new search")
        self.current_query = ""
        self.current_page = 0
        self.current_results = []
        self.current_index = 0
        self.current_image_url = None
        
        # Clear extracted phrases
        for widget in self.extracted_inner_frame.winfo_children():
            widget.destroy()
        self.extracted_placeholder = ttk.Label(self.extracted_inner_frame, text="No hay frases extraídas todavía.")
        self.extracted_placeholder.pack(anchor="w", padx=2, pady=2)

    # ─── LÓGICA DE DESCRIPCIÓN GPT ─────────────────────────────
    def generate_description(self):
        query = self.search_entry.get().strip()
        user_note = self.note_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showerror("Error", "Por favor ingresa una consulta de búsqueda.")
            return
        if not getattr(self.image_label, "image", None):
            messagebox.showerror("Error", "No hay imagen cargada. Por favor busca una imagen primero.")
            return

        self.show_progress(f"Analyzing image with {self.GPT_MODEL}")
        self.disable_buttons()
        threading.Thread(target=self.thread_generate_description, args=(query, user_note), daemon=True).start()

    def thread_generate_description(self, query, user_note):
        try:
            image_url = self.current_image_url
            if not image_url:
                self.after(0, lambda: messagebox.showerror("Error", "No se encontró la URL de la imagen."))
                return
            
            # Debug: Verify we have a valid Unsplash URL
            if not image_url.startswith('https://images.unsplash.com/'):
                print(f"Warning: Unexpected image URL format: {image_url}")
            
            print(f"Sending image to GPT-4 Vision: {image_url[:50]}...")

            # Better prompt that ensures GPT analyzes the actual image
            text_prompt = """Analiza la imagen que te estoy mostrando y descríbela en español latinoamericano.
            
IMPORTANTE: Describe SOLO lo que ves en esta imagen específica:
- ¿Qué objetos, personas o animales aparecen?
- ¿Cuáles son los colores predominantes?
- ¿Qué está sucediendo en la escena?
- ¿Dónde parece estar ubicada (interior/exterior)?
- ¿Qué detalles destacan?

Escribe 1-2 párrafos descriptivos y naturales."""
            
            if user_note:
                text_prompt += f"\n\nContexto adicional del usuario: {user_note}"

            # Use new OpenAI client syntax
            def make_gpt_call():
                response = self.openai_client.chat.completions.create(
                    model=self.GPT_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": text_prompt},
                                {"type": "image_url", "image_url": {"url": image_url, "detail": "high"}}
                            ]
                        }
                    ],
                    max_tokens=600,
                    temperature=0.7,
                )
                return response.choices[0].message.content.strip()
            
            generated_text = self.api_call_with_retry(make_gpt_call)
            self.after(0, lambda: self.display_description(generated_text))
            
            # Update log entry
            for entry in reversed(self.log_entries):
                if entry["image_url"] == image_url and entry["generated_description"] == "":
                    entry["user_note"] = user_note
                    entry["generated_description"] = generated_text
                    break
            
            # Extract phrases in background
            threading.Thread(target=self.extract_phrases_from_description, args=(generated_text,), daemon=True).start()
            
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower():
                self.after(0, lambda: self.show_enhanced_error("API Error", "OpenAI API key may be invalid. Please check your configuration.", "api"))
            elif "rate_limit" in error_msg.lower():
                self.after(0, lambda: self.show_enhanced_error("Rate Limit", "OpenAI rate limit reached. Please wait a moment.", "warning"))
            elif "insufficient_quota" in error_msg.lower():
                self.after(0, lambda: self.show_enhanced_error("Quota Error", "OpenAI API quota exceeded. Please check your account.", "error"))
            else:
                self.after(0, lambda: self.show_enhanced_error("Error", f"GPT API Error:\n{e}", "error"))
        finally:
            self.after(0, self.hide_progress)
            self.after(0, self.enable_buttons)

    def display_description(self, text):
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.insert(tk.END, text)
        self.description_text.config(state=tk.DISABLED)
        self.copy_desc_button.config(state=tk.NORMAL)
        self.update_status("Description generated successfully")
        self.enable_buttons()

    # ─── EXTRACCIÓN DE FRASES (GPT) ─────────────────────────────
    def extract_phrases_from_description(self, description):
        def remove_trailing_commas(json_str):
            return re.sub(r",\s*([\]\}])", r"\1", json_str)

        system_msg = (
            "You are a helpful assistant that returns only valid JSON. "
            "No disclaimers, no code fences, no extra text. If you have no data, return '{}'."
        )
        user_msg = f"""Del siguiente texto en español, extrae vocabulario útil para aprender el idioma.
        
TEXTO: {description}

Devuelve un JSON con estas categorías (pueden estar vacías si no hay ejemplos):
- "Sustantivos": incluye el artículo (el/la), máximo 10
- "Verbos": forma conjugada encontrada, máximo 10
- "Adjetivos": con concordancia de género si aplica, máximo 10
- "Adverbios": solo los más relevantes, máximo 5
- "Frases clave": expresiones de 2-4 palabras que sean útiles, máximo 10

Evita palabras muy comunes como: el, la, de, que, y, a, en, es, son
Solo devuelve el JSON, sin comentarios adicionales."""
        
        try:
            def make_extraction_call():
                response = self.openai_client.chat.completions.create(
                    model=self.GPT_MODEL,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg}
                    ],
                    max_tokens=600,
                    temperature=0.3,
                    response_format={"type": "json_object"}  # Force JSON response
                )
                return response.choices[0].message.content.strip()
            
            raw_str = self.api_call_with_retry(make_extraction_call)
            print("DEBUG GPT OUTPUT:\n", raw_str)
            
            # Parse JSON response
            groups = json.loads(raw_str)
            
            # Ensure all expected keys exist
            expected_keys = ['Sustantivos', 'Verbos', 'Adjetivos', 'Adverbios', 'Frases clave']
            for key in expected_keys:
                if key not in groups:
                    groups[key] = []
            
            self.after(0, lambda: self.display_extracted_phrases(groups))
            
        except json.JSONDecodeError as je:
            print(f"JSON decode error: {je}")
            # Try to recover with empty groups
            self.after(0, lambda: self.display_extracted_phrases({}))
        except Exception as e:
            print(f"Error extracting phrases: {e}")
            self.after(0, lambda: self.display_extracted_phrases({}))

    def display_extracted_phrases(self, groups):
        """
        Muestra las frases extraídas, agrupadas por categoría, con cada grupo ordenado alfabéticamente
        ignorando los artículos iniciales ("el", "la", "los", "las") al ordenar.
        """
        self.extracted_phrases = groups

        # Limpia los widgets anteriores
        for widget in self.extracted_inner_frame.winfo_children():
            widget.destroy()

        if not groups or all(not phrases for phrases in groups.values()):
            placeholder = ttk.Label(self.extracted_inner_frame, text="No se pudieron extraer frases.")
            placeholder.pack(anchor="w", padx=2, pady=2)
            return

        # Función auxiliar para ordenar ignorando artículos
        def sort_ignoring_articles(phrase):
            words = phrase.lower().split()
            if words and words[0] in ["el", "la", "los", "las"]:
                return " ".join(words[1:])
            return phrase.lower()

        max_columns = 3

        for category, phrases in groups.items():
            if phrases:
                # Ordena usando la función auxiliar
                sorted_phrases = sorted(phrases, key=sort_ignoring_articles)

                cat_label = ttk.Label(
                    self.extracted_inner_frame,
                    text=f"{category}:",
                    font=('TkDefaultFont', 10, 'bold')
                )
                cat_label.pack(anchor="w", padx=2, pady=(5, 0))

                btn_frame = ttk.Frame(self.extracted_inner_frame)
                btn_frame.pack(fill="x", padx=5)

                col = 0
                row = 0
                for phrase in sorted_phrases:
                    colors = self.theme_manager.get_colors()
                    btn = tk.Button(
                        btn_frame, text=phrase, relief=tk.FLAT, 
                        fg=colors['info'], cursor="hand2",
                        bg=colors['frame_bg'],
                        activebackground=colors['button_active_bg'],
                        command=lambda p=phrase: self.add_target_phrase(p)
                    )
                    # Add tooltip for phrase buttons
                    self.theme_manager.create_themed_tooltip(btn, f"Click to add '{phrase}' to vocabulary")
                    btn.grid(row=row, column=col, padx=2, pady=2, sticky="w")
                    col += 1
                    if col >= max_columns:
                        col = 0
                        row += 1

    # ─── TRADUCCIÓN Y ADICIÓN DE FRASES OBJETIVO ─────────────────────────────
    def translate_word(self, word, context=""):
        """
        Traduce la palabra (en español) al inglés de EE.UU., usando el contexto si se proporciona.
        """
        if context:
            prompt = (
                f"Translate the Latin American Spanish word '{word}' into US English "
                f"as used in the following sentence:\n\n{context}\n\nProvide only the translation."
            )
        else:
            prompt = f"Translate the Latin American Spanish word '{word}' into US English without additional text."
        
        try:
            def make_translation_call():
                response = self.openai_client.chat.completions.create(
                    model=self.GPT_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=20,
                    temperature=0.0,
                )
                return response.choices[0].message.content.strip()
            
            translation = self.api_call_with_retry(make_translation_call, max_retries=2)
            return translation
        except Exception as e:
            print(f"Error de traducción para '{word}': {e}")
            return ""

    def add_target_phrase(self, phrase):
        # Evita duplicados comparando la palabra base (antes del guión).
        if any(phrase == tp.split(" - ")[0] for tp in self.target_phrases):
            return
        
        # Check if already in vocabulary cache
        if phrase in self.vocabulary_cache:
            self.update_status(f"'{phrase}' is already in your vocabulary")
            return
        
        self.show_progress(f"Translating '{phrase}'")
        context = self.description_text.get("1.0", tk.END).strip()
        translation = self.translate_word(phrase, context)
        combined = f"{phrase} - {translation}" if translation else phrase
        self.target_phrases.append(combined)
        self.update_target_list_display()

        # Registra en CSV with additional metadata
        if translation:
            # Include search query and image URL for better context
            self.log_target_word_csv(phrase, translation, self.current_query, self.current_image_url, context[:100])
            self.vocabulary_cache.add(phrase)
        
        self.hide_progress()
        self.update_status("Phrase added to vocabulary")
        self.update_stats()  # Update word count

    def log_target_word_csv(self, spanish_phrase, english_translation, search_query, image_url, context=""):
        """Registra la palabra objetivo con contexto completo en CSV."""
        try:
            # Check if file exists and has headers
            file_exists = self.CSV_TARGET_WORDS.exists()
            
            with open(self.CSV_TARGET_WORDS, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                
                # Write headers if file is new or empty
                if not file_exists or os.path.getsize(self.CSV_TARGET_WORDS) == 0:
                    writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
                
                # Write the data with full context
                writer.writerow([
                    spanish_phrase,
                    english_translation,
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    search_query if search_query else "",
                    image_url[:100] if image_url else "",  # Truncate long URLs
                    context[:100] if context else ""
                ])
        except Exception as e:
            print(f"Error al escribir en el CSV: {e}")

    def update_target_list_display(self):
        self.target_listbox.delete(0, tk.END)
        for phrase in self.target_phrases:
            self.target_listbox.insert(tk.END, phrase)
    
    def export_vocabulary(self):
        """Export vocabulary in different formats."""
        if not self.CSV_TARGET_WORDS.exists() or os.path.getsize(self.CSV_TARGET_WORDS) == 0:
            messagebox.showinfo("No Data", "No vocabulary to export yet!")
            return
        
        # Create export dialog
        export_window = tk.Toplevel(self)
        export_window.title("Export Vocabulary")
        export_window.geometry("400x300")
        export_window.transient(self)
        export_window.grab_set()
        
        # Center window
        export_window.update_idletasks()
        x = (export_window.winfo_screenwidth() // 2) - 200
        y = (export_window.winfo_screenheight() // 2) - 150
        export_window.geometry(f"+{x}+{y}")
        
        # Export options
        frame = ttk.Frame(export_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Export Format:", font=('TkDefaultFont', 10, 'bold')).pack(pady=(0, 10))
        
        # Anki export
        def export_anki():
            try:
                anki_file = self.DATA_DIR / f"anki_export_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                with open(self.CSV_TARGET_WORDS, 'r', encoding='utf-8') as f_in:
                    reader = csv.DictReader(f_in)
                    with open(anki_file, 'w', encoding='utf-8') as f_out:
                        for row in reader:
                            if 'Spanish' in row and 'English' in row:
                                # Anki format: front[tab]back
                                spanish = row['Spanish']
                                english = row['English']
                                context = row.get('Context', '')[:50]
                                f_out.write(f"{spanish}\t{english} | {context}\n")
                
                messagebox.showinfo("Success", f"Exported to:\n{anki_file}\n\nImport this file into Anki using 'Import File'")
                export_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
        
        ttk.Button(frame, text="📚 Anki (Tab-delimited)", command=export_anki, width=30).pack(pady=5)
        
        # Simple text export
        def export_text():
            try:
                text_file = self.DATA_DIR / f"vocabulary_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                with open(self.CSV_TARGET_WORDS, 'r', encoding='utf-8') as f_in:
                    reader = csv.DictReader(f_in)
                    with open(text_file, 'w', encoding='utf-8') as f_out:
                        f_out.write("VOCABULARY LIST\n")
                        f_out.write("=" * 50 + "\n\n")
                        for row in reader:
                            if 'Spanish' in row and 'English' in row:
                                f_out.write(f"{row['Spanish']} = {row['English']}\n")
                                if row.get('Search Query'):
                                    f_out.write(f"  (from: {row['Search Query']})\n")
                                f_out.write("\n")
                
                messagebox.showinfo("Success", f"Exported to:\n{text_file}")
                export_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
        
        ttk.Button(frame, text="📝 Plain Text", command=export_text, width=30).pack(pady=5)
        
        # Open CSV directly
        def open_csv():
            try:
                if sys.platform == "win32":
                    os.startfile(self.CSV_TARGET_WORDS)
                elif sys.platform == "darwin":
                    os.system(f"open {self.CSV_TARGET_WORDS}")
                else:
                    os.system(f"xdg-open {self.CSV_TARGET_WORDS}")
                export_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
        
        ttk.Button(frame, text="📊 Open CSV in Excel", command=open_csv, width=30).pack(pady=5)
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=20)
        
        # Stats
        try:
            with open(self.CSV_TARGET_WORDS, 'r', encoding='utf-8') as f:
                word_count = sum(1 for line in csv.DictReader(f))
            ttk.Label(frame, text=f"Total vocabulary: {word_count} words").pack()
        except:
            pass
        
        ttk.Button(frame, text="Close", command=export_window.destroy).pack(pady=10)

    # ─── SALIDA Y REGISTRO ─────────────────────────────
    def save_session_to_json(self):
        """Save session data in JSON format for better structure."""
        try:
            # Load existing data or create new structure
            if self.LOG_FILENAME.exists():
                try:
                    with open(self.LOG_FILENAME, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except (json.JSONDecodeError, Exception):
                    data = {"sessions": []}
            else:
                data = {"sessions": []}
            
            # Add current session
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
                
        except Exception as e:
            print(f"Error saving session to JSON: {e}")
            # Fallback to text format
            self.save_session_to_text()

    def save_session_to_text(self):
        """Fallback text format for backwards compatibility."""
        try:
            with open(self.LOG_FILENAME.with_suffix('.txt'), "a", encoding="utf-8") as f:
                f.write("\n=== Informe de Sesión ===\n")
                f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                for i, entry in enumerate(self.log_entries, start=1):
                    f.write(f"\nEntrada {i}:\n")
                    f.write(f"  Consulta de la Búsqueda: {entry.get('query', '')}\n")
                    f.write(f"  URL de la Imagen     : {entry.get('image_url', '')}\n")
                    f.write(f"  Notas del Usuario    : {entry.get('user_note', '')}\n")
                    f.write(f"  Descripción Generada : {entry.get('generated_description', '')}\n")
                    f.write("-" * 40 + "\n")
                if self.target_phrases:
                    f.write("Target Phrases: " + ", ".join(self.target_phrases) + "\n")
        except Exception as e:
            messagebox.showerror("Error", f"Error al escribir el archivo de sesión:\n{e}")

    def reset_search_state(self):
        """Reset search state variables for new search."""
        self.images_collected_count = 0
        self.search_cancelled = False
        self.search_state = 'idle'
        self.progress_var.set(0)
        self.hide_progress()
        self.stop_button.grid_remove()
    
    def start_search_session(self):
        """Start a new search session with proper state management."""
        self.search_state = 'searching'
        self.search_cancelled = False
        self.images_collected_count = 0
        self.progress_var.set(0)
        self.progress_bar.configure(maximum=self.max_images_per_search)
        self.stop_button.grid()  # Show stop button
    
    def stop_search(self):
        """Stop the current search operation."""
        self.search_cancelled = True
        self.search_state = 'cancelled'
        self.hide_progress()
        self.stop_button.grid_remove()
        self.enable_buttons()
        self.update_status(f"Search stopped. Collected {self.images_collected_count} images.")
    
    def show_collection_limit_reached(self):
        """Show message when collection limit is reached."""
        self.search_state = 'completed'
        self.stop_button.grid_remove()
        self.hide_progress()
        
        # Change Another Image button to Load More
        if self.images_collected_count >= self.max_images_per_search:
            self.another_button.config(text="Load More (30)")
            self.theme_manager.create_themed_tooltip(self.another_button, "Load 30 more images from current search")
        
        self.update_status(f"Collection limit reached: {self.max_images_per_search} images. Click 'Load More' to continue.")
        messagebox.showinfo(
            "Collection Limit Reached", 
            f"Reached limit of {self.max_images_per_search} images for this search.\n\nClick 'Load More' to collect 30 more images, or start a new search."
        )
    
    def show_no_more_images(self):
        """Show message when no more images are available."""
        self.search_state = 'completed'
        self.stop_button.grid_remove()
        self.hide_progress()
        messagebox.showinfo("No More Images", f"No more new images found for '{self.current_query}'.")
    
    def update_search_progress(self):
        """Update search progress bar and status."""
        self.progress_var.set(self.images_collected_count)
        progress_text = f"Collected {self.images_collected_count}/{self.max_images_per_search} images"
        
        # Update status with progress
        if self.search_state == 'searching':
            self.update_status(f"Searching... {progress_text}")
        else:
            self.update_status(progress_text)
            
        # Show stop button during search
        if self.search_state == 'searching' and self.images_collected_count < self.max_images_per_search:
            self.stop_button.grid()
        else:
            self.stop_button.grid_remove()
    
    def load_more_images(self):
        """Load more images beyond the initial limit."""
        # Reset the limit for this session
        self.max_images_per_search += 30
        self.progress_bar.configure(maximum=self.max_images_per_search)
        
        # Reset button text
        self.another_button.config(text="Otra Imagen")
        self.theme_manager.create_themed_tooltip(self.another_button, "Get another image from current search")
        
        # Continue with another image
        self.another_image()
    
    def show_performance_dashboard(self):
        """Show performance monitoring dashboard."""
        if hasattr(self, 'optimized_collector') and self.optimized_collector:
            self.optimized_collector.show_performance_dashboard()
        else:
            messagebox.showinfo("Performance Dashboard", "Performance optimization not available in this session.")
            
    def start_optimized_collection(self):
        """Start optimized image collection."""
        if not hasattr(self, 'optimized_collector') or not self.optimized_collector:
            messagebox.showerror("Error", "Optimized collection not available.")
            return
            
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter a search query first.")
            return
            
        # Create collection dialog
        dialog = OptimizedCollectionDialog(self, self.optimized_collector, query)
        dialog.show()

    def on_exit(self):
        """Save session data before closing."""
        # Cleanup performance optimization
        if hasattr(self, 'performance_optimizer') and self.performance_optimizer:
            self.performance_optimizer.stop_optimization()
        if hasattr(self, 'optimized_collector') and self.optimized_collector:
            self.optimized_collector.shutdown_optimization()
            
        self.save_session_to_json()
        self.destroy()


class OptimizedCollectionDialog:
    """Dialog for optimized image collection configuration."""
    
    def __init__(self, parent, optimized_collector, query):
        self.parent = parent
        self.collector = optimized_collector
        self.query = query
        self.dialog = None
        
    def show(self):
        """Show the collection dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Optimized Image Collection")
        self.dialog.geometry("600x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 300
        y = (self.dialog.winfo_screenheight() // 2) - 250
        self.dialog.geometry(f"+{x}+{y}")
        
        self._create_dialog_content()
        
    def _create_dialog_content(self):
        """Create dialog content."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text=f"Optimized Collection for: '{self.query}'",
            font=('TkDefaultFont', 12, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Collection Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Max images
        images_frame = ttk.Frame(settings_frame)
        images_frame.pack(fill=tk.X, pady=5)
        ttk.Label(images_frame, text="Maximum Images:").pack(side=tk.LEFT)
        self.max_images_var = tk.StringVar(value="50")
        ttk.Entry(images_frame, textvariable=self.max_images_var, width=10).pack(side=tk.LEFT, padx=(5, 0))
        
        # Memory limit
        memory_frame = ttk.Frame(settings_frame)
        memory_frame.pack(fill=tk.X, pady=5)
        ttk.Label(memory_frame, text="Memory Limit (MB):").pack(side=tk.LEFT)
        self.memory_limit_var = tk.StringVar(value="600")
        ttk.Entry(memory_frame, textvariable=self.memory_limit_var, width=10).pack(side=tk.LEFT, padx=(5, 0))
        
        # Batch size
        batch_frame = ttk.Frame(settings_frame)
        batch_frame.pack(fill=tk.X, pady=5)
        ttk.Label(batch_frame, text="Batch Size:").pack(side=tk.LEFT)
        self.batch_size_var = tk.StringVar(value="10")
        ttk.Entry(batch_frame, textvariable=self.batch_size_var, width=10).pack(side=tk.LEFT, padx=(5, 0))
        
        # Progress frame
        self.progress_frame = ttk.LabelFrame(main_frame, text="Collection Progress", padding="10")
        self.progress_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Setup progress feedback
        self.collector.setup_progress_feedback(self.progress_frame)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT)
        
        start_button = ttk.Button(
            button_frame, 
            text="Start Collection", 
            command=self._start_collection
        )
        start_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        dashboard_button = ttk.Button(
            button_frame,
            text="Performance Dashboard",
            command=self._show_dashboard
        )
        dashboard_button.pack(side=tk.RIGHT)
        
    def _start_collection(self):
        """Start the optimized collection."""
        try:
            max_images = int(self.max_images_var.get())
            memory_limit = float(self.memory_limit_var.get())
            batch_size = int(self.batch_size_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric values")
            return
            
        # Configure collector
        self.collector.configure_collection(
            memory_threshold_mb=memory_limit,
            batch_size=batch_size
        )
        
        # Start collection in background
        threading.Thread(
            target=self._run_collection,
            args=(max_images,),
            daemon=True,
            name="OptimizedCollectionDialog"
        ).start()
        
    def _run_collection(self, max_images):
        """Run the collection."""
        try:
            collected_images = self.collector.collect_images_optimized(
                self.query, max_images
            )
            
            # Update parent app with results
            self.parent.after(0, lambda: self._collection_complete(collected_images))
            
        except Exception as e:
            self.parent.after(0, lambda: messagebox.showerror("Error", f"Collection failed: {e}"))
            
    def _collection_complete(self, images):
        """Handle collection completion."""
        messagebox.showinfo(
            "Collection Complete",
            f"Successfully collected {len(images)} optimized images!"
        )
        
        # Close dialog
        if self.dialog:
            self.dialog.destroy()
            
    def _show_dashboard(self):
        """Show performance dashboard."""
        self.collector.show_performance_dashboard()


def main():
    """Main entry point for the application."""
    try:
        app = ImageSearchApp()
        if app.config_manager:  # Only run if configuration was successful
            app.mainloop()
    except Exception as e:
        # Show error in a message box if GUI fails to start
        import traceback
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