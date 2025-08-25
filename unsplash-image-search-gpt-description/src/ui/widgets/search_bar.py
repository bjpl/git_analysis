"""
Search bar widget with controls and progress indication.
"""

import tkinter as tk
from tkinter import ttk


class SearchBar(ttk.Frame):
    """Search controls with query input, buttons, and progress indication."""
    
    def __init__(self, parent, on_search=None, on_another_image=None, 
                 on_new_search=None, on_export=None, **kwargs):
        super().__init__(parent, padding="5", **kwargs)
        
        # Callbacks
        self.on_search = on_search
        self.on_another_image = on_another_image
        self.on_new_search = on_new_search
        self.on_export = on_export
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create search control widgets."""
        # Search input row
        ttk.Label(self, text="Consulta en Unsplash:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.search_entry = ttk.Entry(self, width=40)
        self.search_entry.grid(row=0, column=1, padx=5)
        self.search_entry.bind('<Return>', lambda e: self._on_search())
        
        self.search_button = ttk.Button(self, text="Buscar Imagen", command=self._on_search)
        self.search_button.grid(row=0, column=2, padx=5)
        
        # Progress bar
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(
            self, 
            mode='indeterminate',
            variable=self.progress_var
        )
        self.progress_bar.grid(row=0, column=3, padx=5, sticky="ew")
        self.progress_bar.grid_remove()  # Hidden by default
        
        # Action buttons row
        self.another_button = ttk.Button(self, text="Otra Imagen", command=self._on_another_image)
        self.another_button.grid(row=1, column=0, padx=5, pady=(5, 0), sticky=tk.W)
        
        self.newsearch_button = ttk.Button(self, text="Nueva Búsqueda", command=self._on_new_search)
        self.newsearch_button.grid(row=1, column=1, padx=5, pady=(5, 0), sticky=tk.W)
        
        # Export button
        self.export_button = ttk.Button(self, text="📤 Export", command=self._on_export)
        self.export_button.grid(row=1, column=2, padx=5, pady=(5, 0), sticky=tk.W)
    
    def _on_search(self):
        """Handle search button click."""
        if self.on_search:
            query = self.get_query()
            if query:
                self.on_search(query)
    
    def _on_another_image(self):
        """Handle another image button click."""
        if self.on_another_image:
            self.on_another_image()
    
    def _on_new_search(self):
        """Handle new search button click."""
        if self.on_new_search:
            self.on_new_search()
    
    def _on_export(self):
        """Handle export button click."""
        if self.on_export:
            self.on_export()
    
    def get_query(self):
        """Get the current search query."""
        return self.search_entry.get().strip()
    
    def set_query(self, query):
        """Set the search query."""
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, query)
    
    def clear_query(self):
        """Clear the search query."""
        self.search_entry.delete(0, tk.END)
    
    def select_all_query(self):
        """Select all text in the search entry."""
        self.search_entry.selection_range(0, tk.END)
    
    def show_progress(self):
        """Show progress bar during operations."""
        self.progress_bar.grid()
        self.progress_bar.start(10)
    
    def hide_progress(self):
        """Hide progress bar after operations."""
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
    
    def disable_buttons(self):
        """Disable all buttons during operations."""
        self.search_button.config(state=tk.DISABLED)
        self.another_button.config(state=tk.DISABLED)
        self.newsearch_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.DISABLED)
    
    def enable_buttons(self):
        """Enable all buttons after operations."""
        self.search_button.config(state=tk.NORMAL)
        self.another_button.config(state=tk.NORMAL)
        self.newsearch_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.NORMAL)