"""
Enhanced Search Panel with cancellation controls and progress tracking.
Provides robust UI controls for image search operations with timeout and cancellation support.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Optional, Callable, Dict, Any
from datetime import datetime

from .loading_states import ProgressIndicator, LoadingOverlay
from ...services.controlled_image_service import ControlledImageService, CancellationError


class EnhancedSearchPanel(ttk.Frame):
    """Enhanced search panel with robust cancellation and progress controls."""
    
    def __init__(self, parent, controlled_service: ControlledImageService, 
                 style_manager=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.controlled_service = controlled_service
        self.style_manager = style_manager
        
        # Operation tracking
        self.current_operation: Optional[str] = None
        self.operation_thread: Optional[threading.Thread] = None
        self.is_loading = False
        self.start_time: Optional[datetime] = None
        
        # Callbacks
        self.on_image_loaded: Optional[Callable] = None
        self.on_search_complete: Optional[Callable] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
        
        self._create_widgets()
        self._setup_bindings()
    
    def _create_widgets(self):
        """Create enhanced search control widgets."""
        # Main container
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search input section
        search_frame = ttk.LabelFrame(main_frame, text="Image Search", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Query input
        query_frame = ttk.Frame(search_frame)
        query_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(query_frame, text="Search Query:").pack(anchor=tk.W)
        
        entry_frame = ttk.Frame(query_frame)
        entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.query_entry = ttk.Entry(entry_frame, font=('Segoe UI', 11))
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.search_button = ttk.Button(
            entry_frame, 
            text="🔍 Search", 
            command=self._start_search,
            style='Accent.TButton'
        )
        self.search_button.pack(side=tk.RIGHT)
        
        # Control buttons
        button_frame = ttk.Frame(search_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.next_button = ttk.Button(
            button_frame,
            text="➡️ Next Image",
            command=self._get_next_image,
            state='disabled'
        )
        self.next_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_button = ttk.Button(
            button_frame,
            text="❌ Cancel",
            command=self._cancel_operation,
            state='disabled'
        )
        self.cancel_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(
            button_frame,
            text="⏹️ Stop Search",
            command=self._stop_search,
            state='disabled'
        )
        self.stop_button.pack(side=tk.LEFT)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Progress indicator with cancel support
        self.progress_indicator = ProgressIndicator(
            progress_frame,
            style_manager=self.style_manager,
            show_cancel=True,
            on_cancel=self._cancel_operation,
            timeout_seconds=60
        )
        self.progress_indicator.pack(fill=tk.X, pady=(0, 10))
        self.progress_indicator.pack_forget()  # Hidden initially
        
        # Status and statistics
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(
            stats_frame, 
            text="Ready to search",
            font=('Segoe UI', 10)
        )
        self.status_label.pack(anchor=tk.W)
        
        self.stats_label = ttk.Label(
            stats_frame,
            text="Images: 0 | Time: 0s",
            font=('Segoe UI', 9),
            foreground='gray'
        )
        self.stats_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Advanced options (collapsible)
        self.advanced_frame = ttk.LabelFrame(main_frame, text="⚙️ Advanced Options", padding="10")
        self.advanced_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Timeout settings
        timeout_frame = ttk.Frame(self.advanced_frame)
        timeout_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(timeout_frame, text="Operation Timeout:").pack(side=tk.LEFT)
        
        self.timeout_var = tk.IntVar(value=60)
        timeout_spin = ttk.Spinbox(
            timeout_frame,
            from_=10,
            to=300,
            textvariable=self.timeout_var,
            width=10
        )
        timeout_spin.pack(side=tk.LEFT, padx=(10, 5))
        
        ttk.Label(timeout_frame, text="seconds").pack(side=tk.LEFT)
        
        # Auto-continue option
        self.auto_continue_var = tk.BooleanVar(value=False)
        auto_check = ttk.Checkbutton(
            self.advanced_frame,
            text="Auto-continue to next image on success",
            variable=self.auto_continue_var
        )
        auto_check.pack(anchor=tk.W, pady=(5, 0))
        
        # Initially collapse advanced options
        self.advanced_frame.pack_forget()
        
        # Toggle for advanced options
        self.advanced_toggle = ttk.Button(
            main_frame,
            text="▼ Show Advanced Options",
            command=self._toggle_advanced
        )
        self.advanced_toggle.pack(pady=(5, 0))
        
        self.advanced_visible = False
    
    def _setup_bindings(self):
        """Setup keyboard shortcuts and event bindings."""
        self.query_entry.bind('<Return>', lambda e: self._start_search())
        self.query_entry.bind('<Escape>', lambda e: self._cancel_operation())
        
        # Focus management
        self.query_entry.focus_set()
    
    def _toggle_advanced(self):
        """Toggle advanced options visibility."""
        if self.advanced_visible:
            self.advanced_frame.pack_forget()
            self.advanced_toggle.configure(text="▼ Show Advanced Options")
            self.advanced_visible = False
        else:
            self.advanced_frame.pack(fill=tk.X, pady=(0, 10), before=self.advanced_toggle)
            self.advanced_toggle.configure(text="▲ Hide Advanced Options")
            self.advanced_visible = True
    
    def _start_search(self):
        """Start a new image search operation."""
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter a search query.")
            return
        
        if self.is_loading:
            messagebox.showwarning("Warning", "An operation is already in progress.")
            return
        
        self._begin_operation("search", f"Starting search for '{query}'")
        
        # Start search in thread
        self.operation_thread = threading.Thread(
            target=self._thread_search,
            args=(query,),
            daemon=True,
            name=f"search-{query}"
        )
        self.operation_thread.start()
    
    def _get_next_image(self):
        """Get the next image from current search."""
        if not self.controlled_service.current_session:
            messagebox.showerror("Error", "No active search session. Please start a new search.")
            return
        
        if self.is_loading:
            messagebox.showwarning("Warning", "An operation is already in progress.")
            return
        
        self._begin_operation("next_image", "Loading next image")
        
        # Get next image in thread
        self.operation_thread = threading.Thread(
            target=self._thread_get_next,
            daemon=True,
            name="get-next-image"
        )
        self.operation_thread.start()
    
    def _cancel_operation(self):
        """Cancel the current operation."""
        if not self.is_loading:
            return
        
        self.status_label.configure(text="Cancelling operation...")
        
        # Cancel the service operation
        if self.controlled_service.is_operation_active():
            self.controlled_service.cancel_current_operation()
        
        # Cancel the thread (best effort)
        if self.operation_thread and self.operation_thread.is_alive():
            # Thread will check cancellation status
            pass
        
        self._end_operation("Operation cancelled by user")
    
    def _stop_search(self):
        """Stop the current search session."""
        if self.controlled_service.current_session:
            self.controlled_service.stop_current_search()
            self.status_label.configure(text="Search session stopped")
            
            # Show session summary
            stats = self.controlled_service.get_session_stats()
            summary = f"""Search Session Summary:
Query: {stats.get('query', 'N/A')}
Images Loaded: {stats.get('images_loaded', 0)}
Pages Fetched: {stats.get('pages_fetched', 0)}
Status: {stats.get('status', 'unknown')}"""
            
            messagebox.showinfo("Session Stopped", summary)
        
        self._end_operation("Search session stopped")
    
    def _begin_operation(self, operation_type: str, status_message: str):
        """Begin a new operation with UI updates."""
        self.current_operation = operation_type
        self.is_loading = True
        self.start_time = datetime.now()
        
        # Update UI
        self.search_button.configure(state='disabled')
        self.next_button.configure(state='disabled')
        self.cancel_button.configure(state='normal')
        self.stop_button.configure(state='normal')
        
        # Show progress
        self.progress_indicator.pack(fill=tk.X, pady=(0, 10))
        self.progress_indicator.start_loading(
            status_message,
            timeout_callback=self._handle_timeout
        )
        
        self.status_label.configure(text=status_message)
        self._update_stats()
    
    def _end_operation(self, final_message: str):
        """End current operation with UI cleanup."""
        self.current_operation = None
        self.is_loading = False
        self.operation_thread = None
        
        # Update UI
        self.search_button.configure(state='normal')
        self.cancel_button.configure(state='disabled')
        
        # Enable next button if we have an active session
        if (self.controlled_service.current_session and 
            self.controlled_service.can_load_more_images()):
            self.next_button.configure(state='normal')
            self.stop_button.configure(state='normal')
        else:
            self.next_button.configure(state='disabled')
            self.stop_button.configure(state='disabled')
        
        # Hide progress
        self.progress_indicator.stop_loading()
        self.progress_indicator.pack_forget()
        
        self.status_label.configure(text=final_message)
        self._update_stats()
    
    def _handle_timeout(self):
        """Handle operation timeout."""
        messagebox.showwarning(
            "Timeout", 
            f"Operation timed out after {self.timeout_var.get()} seconds."
        )
        self._cancel_operation()
    
    def _update_stats(self):
        """Update statistics display."""
        stats = self.controlled_service.get_session_stats()
        
        if self.start_time:
            elapsed = int((datetime.now() - self.start_time).total_seconds())
        else:
            elapsed = 0
        
        if stats.get('status') != 'no_session':
            images = stats.get('images_loaded', 0)
            api_calls = stats.get('rate_limit_stats', {}).get('api_calls_made', 0)
            cache_size = stats.get('cache_stats', {}).get('cached_images', 0)
            
            stats_text = f"Images: {images} | API Calls: {api_calls} | Cached: {cache_size} | Time: {elapsed}s"
        else:
            stats_text = f"No active session | Time: {elapsed}s"
        
        self.stats_label.configure(text=stats_text)
    
    def _thread_search(self, query: str):
        """Thread function for starting a new search."""
        try:
            # Start new search session
            success = self.controlled_service.start_new_search(query)
            if not success:
                raise Exception("Failed to start search session")
            
            # Get first image
            def progress_callback(message: str):
                self.after(0, lambda: self.progress_indicator.set_text(message))
            
            result = self.controlled_service.get_next_image_controlled(progress_callback)
            
            if result:
                photo_image, pil_image, url = result
                
                # Notify main thread of success
                self.after(0, lambda: self._handle_search_success(photo_image, pil_image, url, query))
                
                # Auto-continue if enabled
                if self.auto_continue_var.get():
                    self.after(2000, self._get_next_image)  # Auto-continue after 2s
            else:
                self.after(0, lambda: self._handle_search_failure("No images found or limit reached"))
        
        except CancellationError:
            self.after(0, lambda: self._end_operation("Search was cancelled"))
        except Exception as e:
            self.after(0, lambda: self._handle_search_failure(str(e)))
    
    def _thread_get_next(self):
        """Thread function for getting next image."""
        try:
            def progress_callback(message: str):
                self.after(0, lambda: self.progress_indicator.set_text(message))
            
            result = self.controlled_service.get_next_image_controlled(progress_callback)
            
            if result:
                photo_image, pil_image, url = result
                self.after(0, lambda: self._handle_image_success(photo_image, pil_image, url))
                
                # Auto-continue if enabled
                if self.auto_continue_var.get():
                    self.after(2000, self._get_next_image)  # Auto-continue after 2s
            else:
                self.after(0, lambda: self._handle_search_failure("No more images available"))
        
        except CancellationError:
            self.after(0, lambda: self._end_operation("Operation was cancelled"))
        except Exception as e:
            self.after(0, lambda: self._handle_search_failure(str(e)))
    
    def _handle_search_success(self, photo_image, pil_image, url, query):
        """Handle successful search completion."""
        self._end_operation(f"Search completed for '{query}'")
        
        if self.on_image_loaded:
            self.on_image_loaded(photo_image, pil_image, url)
        
        if self.on_search_complete:
            self.on_search_complete(query)
    
    def _handle_image_success(self, photo_image, pil_image, url):
        """Handle successful image loading."""
        self._end_operation("Image loaded successfully")
        
        if self.on_image_loaded:
            self.on_image_loaded(photo_image, pil_image, url)
    
    def _handle_search_failure(self, error_message: str):
        """Handle search/loading failure."""
        self._end_operation(f"Error: {error_message}")
        
        if self.on_error:
            self.on_error(Exception(error_message))
        else:
            messagebox.showerror("Error", error_message)
    
    def set_query(self, query: str):
        """Set the search query."""
        self.query_entry.delete(0, tk.END)
        self.query_entry.insert(0, query)
    
    def get_query(self) -> str:
        """Get the current search query."""
        return self.query_entry.get().strip()
    
    def set_callbacks(self, on_image_loaded: Callable = None, 
                     on_search_complete: Callable = None,
                     on_error: Callable = None):
        """Set callback functions for events."""
        self.on_image_loaded = on_image_loaded
        self.on_search_complete = on_search_complete
        self.on_error = on_error
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics."""
        return self.controlled_service.get_session_stats()
    
    def is_operation_running(self) -> bool:
        """Check if an operation is currently running."""
        return self.is_loading