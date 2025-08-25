"""
Main application window containing all UI components and business logic coordination.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from datetime import datetime

from .widgets.search_bar import SearchBar
from .widgets.image_viewer import ImageViewer
from .widgets.vocabulary_list import VocabularyList, ExtractedPhrases
from .components.enhanced_search_panel import EnhancedSearchPanel
from .components.loading_states import LoadingOverlay
from ..services.unsplash_service import UnsplashService, ApiCallRetryMixin, CancellationError
from ..services.controlled_image_service import ControlledImageService
from ..services.openai_service import OpenAIService
from ..services.translation_service import TranslationService
from ..models.session import SessionManager, SessionEntry
from ..models.vocabulary import VocabularyManager, VocabularyEntry
from ..models.image import ImageSearchState
from ..utils.cache import ImageCache
from ..utils.data_export import ExportDialog
from ..utils.file_manager import LastSearchManager


class MainWindow(tk.Tk):
    """Main application window with modular architecture."""
    
    def __init__(self, config_manager):
        super().__init__()
        
        # Configuration
        self.config_manager = config_manager
        self._load_configuration()
        
        # Initialize services
        self._initialize_services()
        
        # Initialize models and managers
        self._initialize_managers()
        
        # UI Setup
        self._setup_window()
        self._create_widgets()
        
        # Load previous state
        self._load_previous_state()
        
        # Setup event handlers
        self._setup_event_handlers()
    
    def _load_configuration(self):
        """Load configuration from config manager."""
        api_keys = self.config_manager.get_api_keys()
        paths = self.config_manager.get_paths()
        
        self.UNSPLASH_ACCESS_KEY = api_keys['unsplash']
        self.OPENAI_API_KEY = api_keys['openai']
        self.GPT_MODEL = api_keys['gpt_model']
        
        self.DATA_DIR = paths['data_dir']
        self.LOG_FILENAME = paths['log_file']
        self.CSV_TARGET_WORDS = paths['vocabulary_file']
        
        # Ensure data directory exists
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    def _initialize_services(self):
        """Initialize API services."""
        self.unsplash_service = UnsplashService(self.UNSPLASH_ACCESS_KEY)
        self.controlled_image_service = ControlledImageService(self.UNSPLASH_ACCESS_KEY, self)
        self.openai_service = OpenAIService(self.OPENAI_API_KEY, self.GPT_MODEL)
        self.translation_service = TranslationService(self.openai_service)
        
        # Loading overlay for blocking operations
        self.loading_overlay = None
    
    def _initialize_managers(self):
        """Initialize data managers and state."""
        self.session_manager = SessionManager(self.LOG_FILENAME)
        self.vocabulary_manager = VocabularyManager(self.CSV_TARGET_WORDS)
        self.last_search_manager = LastSearchManager(self.DATA_DIR)
        self.image_search_state = ImageSearchState()
        self.image_cache = ImageCache(max_size=10)
    
    def _setup_window(self):
        """Setup main window properties."""
        self.title(f"Unsplash & GPT Tool - Model: {self.GPT_MODEL}")
        self.geometry("1100x800")
        self.resizable(True, True)
        
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
    
    def _create_widgets(self):
        """Create and layout all UI widgets."""
        # Main container
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Enhanced search panel
        self.enhanced_search_panel = EnhancedSearchPanel(
            main_frame,
            self.controlled_image_service
        )
        self.enhanced_search_panel.pack(fill=tk.X, pady=(0, 10))
        
        # Setup search panel callbacks
        self.enhanced_search_panel.set_callbacks(
            on_image_loaded=self.handle_image_loaded,
            on_search_complete=self.handle_search_complete,
            on_error=self.handle_search_error
        )
        
        # Legacy search controls (kept for compatibility)
        self.search_bar = SearchBar(
            main_frame,
            on_search=self.search_image_legacy,
            on_another_image=self.another_image,
            on_new_search=self.change_search,
            on_export=self.export_vocabulary
        )
        # Hide legacy search bar by default
        # self.search_bar.pack(fill=tk.X)
        
        # Status bar
        self._create_status_bar(main_frame)
        
        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Left side: Image viewer
        self.image_viewer = ImageViewer(content_frame)
        self.image_viewer.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Right side: Text area
        self._create_text_area(content_frame)
    
    def _create_status_bar(self, parent):
        """Create status bar with statistics."""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.status_label = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.stats_label = ttk.Label(status_frame, text="Images: 0 | Words: 0", relief=tk.SUNKEN, anchor=tk.E)
        self.stats_label.pack(side=tk.RIGHT, padx=(5, 0))
    
    def _create_text_area(self, parent):
        """Create the right-side text area with notes, description, and vocabulary."""
        text_area_frame = ttk.Frame(parent)
        text_area_frame.grid(row=0, column=1, sticky="nsew")
        text_area_frame.rowconfigure(0, weight=1)  # Notes
        text_area_frame.rowconfigure(1, weight=1)  # Description
        text_area_frame.rowconfigure(2, weight=0)  # Vocabulary
        text_area_frame.columnconfigure(0, weight=1)
        
        # User notes
        notes_frame = ttk.LabelFrame(text_area_frame, text="Tus Notas / Descripción", padding="10")
        notes_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=(0, 5))
        notes_frame.rowconfigure(0, weight=1)
        notes_frame.columnconfigure(0, weight=1)
        
        self.note_text = scrolledtext.ScrolledText(notes_frame, wrap=tk.WORD)
        self.note_text.grid(row=0, column=0, sticky="nsew")
        
        # GPT description
        desc_frame = ttk.LabelFrame(text_area_frame, text="Descripción Generada por GPT", padding="10")
        desc_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
        desc_frame.rowconfigure(0, weight=1)
        desc_frame.columnconfigure(0, weight=1)
        
        self.description_text = scrolledtext.ScrolledText(desc_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.description_text.configure(font=("TkDefaultFont", 14))
        self.description_text.grid(row=0, column=0, sticky="nsew")
        
        # Description buttons
        desc_button_frame = ttk.Frame(desc_frame)
        desc_button_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        
        self.copy_desc_button = ttk.Button(
            desc_button_frame,
            text="📋 Copiar",
            command=self.copy_description,
            state=tk.DISABLED
        )
        self.copy_desc_button.pack(side=tk.RIGHT, padx=(0, 5))
        
        self.generate_desc_button = ttk.Button(
            desc_button_frame,
            text="Generar Descripción",
            command=self.generate_description
        )
        self.generate_desc_button.pack(side=tk.RIGHT)
        
        # Bottom frame for vocabulary
        bottom_frame = ttk.Frame(text_area_frame)
        bottom_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=(5, 5))
        bottom_frame.columnconfigure(0, weight=2)
        bottom_frame.columnconfigure(1, weight=1)
        
        # Extracted phrases
        self.extracted_phrases = ExtractedPhrases(bottom_frame, on_phrase_click=self.add_target_phrase)
        self.extracted_phrases.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Target vocabulary
        self.vocabulary_list = VocabularyList(bottom_frame)
        self.vocabulary_list.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
    
    def _load_previous_state(self):
        """Load previous application state."""
        # Load last search query
        last_query = self.last_search_manager.load_last_search()
        if last_query:
            self.search_bar.set_query(last_query)
            self.search_bar.select_all_query()
        
        # Update stats
        self.update_stats()
    
    def _setup_event_handlers(self):
        """Setup keyboard shortcuts and event handlers."""
        self.bind('<Control-g>', lambda e: self.generate_description())
    
    def update_status(self, message: str):
        """Update status bar message."""
        self.status_label.config(text=message)
        self.update_idletasks()
    
    def update_stats(self):
        """Update session statistics display."""
        stats = self.session_manager.get_session_stats()
        vocab_count = self.vocabulary_manager.get_vocabulary_count()
        self.stats_label.config(text=f"Images: {stats['images']} | Words: {vocab_count}")
        self.update_idletasks()
    
    def copy_description(self):
        """Copy the generated description to clipboard."""
        description = self.description_text.get("1.0", tk.END).strip()
        if description:
            self.clipboard_clear()
            self.clipboard_append(description)
            self.update_status("Descripción copiada al portapapeles")
    
    # Enhanced image search methods with cancellation support
    def handle_image_loaded(self, photo_image, pil_image, url):
        """Handle successful image loading from enhanced search panel."""
        try:
            # Display image
            self.image_viewer.display_image_from_pil(pil_image)
            
            # Create session entry
            entry = SessionEntry(
                self.enhanced_search_panel.get_query(),
                url
            )
            self.session_manager.current_session.add_entry(entry)
            
            # Clear previous content
            self._clear_text_areas()
            self.update_status("Image loaded successfully")
            self.update_stats()
            
        except Exception as e:
            self.handle_search_error(e)
    
    def handle_search_complete(self, query: str):
        """Handle search completion."""
        self.last_search_manager.save_last_search(query)
        self.update_status(f"Search completed for '{query}'")
    
    def handle_search_error(self, error: Exception):
        """Handle search errors with user-friendly messages."""
        error_msg = str(error)
        
        if isinstance(error, CancellationError):
            self.update_status("Operation was cancelled")
        elif "403" in error_msg or "invalid" in error_msg.lower():
            messagebox.showerror(
                "API Error", 
                "Unsplash API key may be invalid. Please check your configuration."
            )
        elif "rate" in error_msg.lower() or "429" in error_msg:
            messagebox.showerror(
                "Rate Limit", 
                "Unsplash rate limit reached. Please wait before trying again."
            )
        elif "timeout" in error_msg.lower():
            messagebox.showerror(
                "Timeout", 
                "Operation timed out. Please check your internet connection and try again."
            )
        else:
            messagebox.showerror("Error", f"Search failed: {error_msg}")
        
        self.update_status(f"Error: {error_msg}")
    
    def get_parent_window(self):
        """Return the parent window for dialogs."""
        return self
    
    # Legacy image search methods (kept for compatibility)
    def search_image_legacy(self, query: str):
        """Legacy search method - redirects to enhanced search."""
        self.enhanced_search_panel.set_query(query)
        self.enhanced_search_panel._start_search()
    
    def search_image(self, query: str):
        """Initiate a new image search (legacy method)."""
        if not query:
            messagebox.showerror("Error", "Por favor ingresa una consulta de búsqueda.")
            return
        
        # Show loading overlay for legacy operations
        self.show_loading_overlay(f"Searching for '{query}'...")
        
        self.last_search_manager.save_last_search(query)
        self.update_status(f"Buscando '{query}' en Unsplash...")
        self.search_bar.show_progress()
        self.search_bar.disable_buttons()
        
        threading.Thread(target=self._thread_search_images, args=(query,), daemon=True).start()
    
    def _thread_search_images(self, query: str):
        """Thread function for searching images."""
        try:
            results_data = ApiCallRetryMixin.api_call_with_retry(
                self.unsplash_service.search_photos, query=query, page=1
            )
            
            if not results_data.get("results"):
                self.after(0, lambda: messagebox.showinfo("Sin Resultados", f"No se encontraron imágenes para '{query}'."))
                return
            
            self.image_search_state.set_new_search(query, results_data)
            self._get_next_valid_image()
            
        except Exception as e:
            error_msg = self.unsplash_service.handle_rate_limit_error(e)
            self.after(0, lambda: messagebox.showerror("Error", error_msg))
        finally:
            self.after(0, self.search_bar.hide_progress)
            self.after(0, self.search_bar.enable_buttons)
    
    def another_image(self):
        """Get another image from current search."""
        if not self.image_search_state.current_query:
            messagebox.showerror("Error", "Por favor ingresa una consulta antes.")
            return
        
        self.update_status("Buscando otra imagen...")
        self.search_bar.show_progress()
        self.search_bar.disable_buttons()
        
        threading.Thread(target=self._thread_get_next_image, daemon=True).start()
    
    def _thread_get_next_image(self):
        """Thread function for getting next image."""
        try:
            self._get_next_valid_image()
        finally:
            self.after(0, self.search_bar.hide_progress)
            self.after(0, self.search_bar.enable_buttons)
    
    def _get_next_valid_image(self):
        """Get the next valid (unused) image from search results."""
        while True:
            # Check if we need more results
            if not self.image_search_state.has_more_images():
                # Try to get next page
                try:
                    self.image_search_state.increment_page()
                    results_data = ApiCallRetryMixin.api_call_with_retry(
                        self.unsplash_service.search_photos,
                        query=self.image_search_state.current_query,
                        page=self.image_search_state.current_page
                    )
                    
                    if not results_data.get("results"):
                        self.after(0, lambda: messagebox.showinfo(
                            "Sin más imágenes",
                            f"No se encontraron más imágenes nuevas para '{self.image_search_state.current_query}'."
                        ))
                        return
                    
                    self.image_search_state.add_page_results(results_data)
                
                except Exception as e:
                    error_msg = self.unsplash_service.handle_rate_limit_error(e)
                    self.after(0, lambda: messagebox.showerror("Error", error_msg))
                    return
            
            # Get next image
            image_result = self.image_search_state.get_next_image()
            if not image_result:
                continue
            
            # Check if already used
            if self.session_manager.is_url_used(image_result.regular_url):
                continue
            
            # Try to download and display
            try:
                # Check cache first
                image_data = self.image_cache.get_image(image_result.regular_url)
                if not image_data:
                    image_data = ApiCallRetryMixin.api_call_with_retry(
                        self.unsplash_service.download_image,
                        image_result.regular_url
                    )
                    self.image_cache.cache_image(image_result.regular_url, image_data)
                
                # Display image
                photo = self.image_viewer.display_image(image_data)
                if photo:
                    # Create session entry
                    entry = SessionEntry(
                        self.image_search_state.current_query,
                        image_result.regular_url
                    )
                    self.session_manager.current_session.add_entry(entry)
                    
                    # Clear previous content
                    self.after(0, self._clear_text_areas)
                    self.after(0, lambda: self.update_status("Imagen cargada."))
                    self.after(0, self.update_stats)
                    
                    return
                
            except Exception as e:
                print(f"Error downloading image: {e}")
                continue
    
    def _clear_text_areas(self):
        """Clear text areas for new image."""
        self.note_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.DISABLED)
        self.copy_desc_button.config(state=tk.DISABLED)
        self.extracted_phrases.clear_phrases()
    
    def change_search(self):
        """Clear everything for a new search."""
        self.search_bar.clear_query()
        self.image_viewer.clear_image()
        self._clear_text_areas()
        self.vocabulary_list.clear_phrases()
        self.image_search_state.clear_search()
        self.update_status("Lista para nueva búsqueda.")
    
    # Description generation methods
    def generate_description(self):
        """Generate GPT description for current image."""
        query = self.search_bar.get_query()
        user_note = self.note_text.get("1.0", tk.END).strip()
        
        if not query:
            messagebox.showerror("Error", "Por favor ingresa una consulta de búsqueda.")
            return
        
        if not self.image_viewer.has_image():
            messagebox.showerror("Error", "No hay imagen cargada. Por favor busca una imagen primero.")
            return
        
        self.update_status(f"Analizando imagen con {self.GPT_MODEL}...")
        self.search_bar.show_progress()
        self.search_bar.disable_buttons()
        
        threading.Thread(target=self._thread_generate_description, args=(query, user_note), daemon=True).start()
    
    def _thread_generate_description(self, query: str, user_note: str):
        """Thread function for generating description."""
        try:
            image_url = self.image_search_state.current_image_url
            if not image_url:
                self.after(0, lambda: messagebox.showerror("Error", "No se encontró la URL de la imagen."))
                return
            
            # Generate description
            description = ApiCallRetryMixin.api_call_with_retry(
                self.openai_service.generate_image_description,
                image_url, user_note
            )
            
            # Display description
            self.after(0, lambda: self._display_description(description))
            
            # Update session entry
            self.session_manager.current_session.update_entry_description(image_url, user_note, description)
            
            # Extract vocabulary
            threading.Thread(target=self._extract_vocabulary, args=(description,), daemon=True).start()
            
        except Exception as e:
            error_msg = self.openai_service.handle_api_error(e)
            self.after(0, lambda: messagebox.showerror("Error", error_msg))
        finally:
            self.after(0, self.search_bar.hide_progress)
            self.after(0, self.search_bar.enable_buttons)
    
    def _display_description(self, text: str):
        """Display generated description in text area."""
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.insert(tk.END, text)
        self.description_text.config(state=tk.DISABLED)
        self.copy_desc_button.config(state=tk.NORMAL)
        self.update_status("Descripción generada.")
    
    def _extract_vocabulary(self, description: str):
        """Extract vocabulary from description."""
        try:
            vocabulary_groups = ApiCallRetryMixin.api_call_with_retry(
                self.openai_service.extract_vocabulary,
                description
            )
            self.after(0, lambda: self.extracted_phrases.display_phrases(vocabulary_groups))
        except Exception as e:
            print(f"Error extracting vocabulary: {e}")
            self.after(0, lambda: self.extracted_phrases.display_phrases({}))
    
    # Vocabulary management methods
    def add_target_phrase(self, phrase: str):
        """Add phrase to target vocabulary list."""
        # Check for duplicates
        if self.vocabulary_manager.is_duplicate(phrase):
            self.update_status(f"'{phrase}' ya está en tu vocabulario")
            return
        
        # Check if already in current session
        current_phrases = self.vocabulary_list.get_phrases()
        if any(phrase == tp.split(" - ")[0] for tp in current_phrases):
            return
        
        self.update_status(f"Traduciendo '{phrase}'...")
        
        # Translate and add
        context = self.description_text.get("1.0", tk.END).strip()
        
        def translate_and_add():
            try:
                translation = ApiCallRetryMixin.api_call_with_retry(
                    self.translation_service.translate_phrase,
                    phrase, context
                )
                
                if translation:
                    # Create vocabulary entry
                    vocab_entry = VocabularyEntry(
                        phrase, 
                        translation,
                        self.image_search_state.current_query,
                        self.image_search_state.current_image_url,
                        context[:100]
                    )
                    
                    # Add to manager
                    if self.vocabulary_manager.add_vocabulary_entry(vocab_entry):
                        combined = f"{phrase} - {translation}"
                        self.after(0, lambda: self.vocabulary_list.add_phrase(combined))
                        self.after(0, lambda: self.update_status("Frase añadida al vocabulario"))
                        self.after(0, self.update_stats)
                    else:
                        self.after(0, lambda: self.update_status("Error al guardar vocabulario"))
                else:
                    self.after(0, lambda: self.update_status("Error en traducción"))
                    
            except Exception as e:
                print(f"Translation error: {e}")
                self.after(0, lambda: self.update_status("Error en traducción"))
        
        threading.Thread(target=translate_and_add, daemon=True).start()
    
    def export_vocabulary(self):
        """Show export vocabulary dialog."""
        export_dialog = ExportDialog(self, self.vocabulary_manager, self.DATA_DIR)
        export_dialog.show_export_dialog()
    
    def show_loading_overlay(self, message: str, show_cancel: bool = True):
        """Show loading overlay for blocking operations."""
        if not self.loading_overlay:
            self.loading_overlay = LoadingOverlay(
                self,
                text=message,
                show_progress=True,
                show_cancel=show_cancel,
                on_cancel=self._cancel_loading_overlay
            )
        else:
            self.loading_overlay.set_text(message)
        
        self.loading_overlay.show_loading()
    
    def hide_loading_overlay(self):
        """Hide loading overlay."""
        if self.loading_overlay:
            self.loading_overlay.hide_loading()
            self.loading_overlay = None
    
    def _cancel_loading_overlay(self):
        """Handle loading overlay cancellation."""
        # Cancel any active operations
        if self.controlled_image_service.is_operation_active():
            self.controlled_image_service.cancel_current_operation()
        
        # Cancel Unsplash service operations
        self.unsplash_service.cancel_all_requests()
        
        self.update_status("Operation cancelled by user")
        self.hide_loading_overlay()
    
    def on_exit(self):
        """Handle application exit with proper cleanup."""
        try:
            # Cancel any active operations
            if self.controlled_image_service.is_operation_active():
                self.controlled_image_service.cancel_current_operation()
            
            # Shutdown services
            self.unsplash_service.shutdown(wait=False)
            
            # Save data
            self.session_manager.save_session()
            
        except Exception as e:
            print(f"Error during shutdown: {e}")
        finally:
            self.destroy()


# Keep the main window class compatible with original interface
class ImageSearchApp(MainWindow):
    """Alias for backwards compatibility."""
    pass