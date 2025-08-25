"""Advanced search panel with filters and history."""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from PIL import Image, ImageTk
from tkinter import filedialog
import threading

from ...features.advanced_search import AdvancedSearchManager, SearchFilter, SearchEntry


class AdvancedSearchPanel(ttk.Frame):
    """Advanced search panel with filters, history, and reverse search."""
    
    def __init__(self, parent, data_dir: Path, unsplash_api_key: str, 
                 search_callback: Optional[Callable] = None):
        super().__init__(parent)
        
        self.data_dir = data_dir
        self.unsplash_api_key = unsplash_api_key
        self.search_callback = search_callback
        
        # Initialize search manager
        self.search_manager = AdvancedSearchManager(data_dir)
        
        # State variables
        self.current_filters = SearchFilter()
        self.search_history = []
        self.saved_searches = []
        self.autocomplete_var = tk.StringVar()
        self.language_var = tk.StringVar(value='en')
        
        # UI setup
        self.setup_ui()
        self.load_search_data()
    
    def setup_ui(self):
        """Setup the UI components."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Search input section
        search_frame = ttk.LabelFrame(main_frame, text="Search Query", padding=5)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Search entry with autocomplete
        entry_frame = ttk.Frame(search_frame)
        entry_frame.pack(fill=tk.X)
        
        self.search_entry = ttk.Combobox(
            entry_frame, 
            textvariable=self.autocomplete_var,
            width=40
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind('<KeyRelease>', self.on_search_entry_change)
        self.search_entry.bind('<Return>', self.perform_search)
        
        # Language selection
        ttk.Label(entry_frame, text="Language:").pack(side=tk.RIGHT, padx=(10, 5))
        language_combo = ttk.Combobox(
            entry_frame,
            textvariable=self.language_var,
            values=list(self.search_manager.supported_languages.values()),
            width=10,
            state="readonly"
        )
        language_combo.pack(side=tk.RIGHT)
        
        # Search buttons
        button_frame = ttk.Frame(search_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(
            button_frame, 
            text="Search", 
            command=self.perform_search
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            button_frame, 
            text="Save Search", 
            command=self.save_current_search
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Button(
            button_frame, 
            text="Reverse Search", 
            command=self.reverse_image_search
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Clear button
        ttk.Button(
            button_frame, 
            text="Clear", 
            command=self.clear_search
        ).pack(side=tk.RIGHT)
        
        # Create notebook for different sections
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Filters tab
        self.create_filters_tab()
        
        # History tab  
        self.create_history_tab()
        
        # Saved searches tab
        self.create_saved_searches_tab()
        
        # Trending tab
        self.create_trending_tab()
    
    def create_filters_tab(self):
        """Create the filters tab."""
        filters_frame = ttk.Frame(self.notebook)
        self.notebook.add(filters_frame, text="Filters")
        
        # Scrollable frame
        canvas = tk.Canvas(filters_frame)
        scrollbar = ttk.Scrollbar(filters_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Filter controls
        row = 0
        
        # Color filter
        color_frame = ttk.LabelFrame(scrollable_frame, text="Color", padding=5)
        color_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        scrollable_frame.columnconfigure(0, weight=1)
        
        self.color_var = tk.StringVar()
        colors = [
            ('Any', ''),
            ('Black & White', 'black_and_white'),
            ('Black', 'black'),
            ('White', 'white'),
            ('Yellow', 'yellow'),
            ('Orange', 'orange'),
            ('Red', 'red'),
            ('Purple', 'purple'),
            ('Magenta', 'magenta'),
            ('Green', 'green'),
            ('Teal', 'teal'),
            ('Blue', 'blue')
        ]
        
        color_combo = ttk.Combobox(
            color_frame,
            textvariable=self.color_var,
            values=[color[0] for color in colors],
            state="readonly",
            width=20
        )
        color_combo.pack(fill=tk.X)
        color_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        self.color_mapping = {color[0]: color[1] for color in colors}
        
        row += 1
        
        # Orientation filter
        orientation_frame = ttk.LabelFrame(scrollable_frame, text="Orientation", padding=5)
        orientation_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        
        self.orientation_var = tk.StringVar()
        orientations = [('Any', ''), ('Landscape', 'landscape'), ('Portrait', 'portrait'), ('Square', 'squarish')]
        
        orientation_combo = ttk.Combobox(
            orientation_frame,
            textvariable=self.orientation_var,
            values=[orient[0] for orient in orientations],
            state="readonly",
            width=20
        )
        orientation_combo.pack(fill=tk.X)
        orientation_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        self.orientation_mapping = {orient[0]: orient[1] for orient in orientations}
        
        row += 1
        
        # Category filter
        category_frame = ttk.LabelFrame(scrollable_frame, text="Category", padding=5)
        category_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        
        self.category_var = tk.StringVar()
        categories = [
            ('Any', ''),
            ('Backgrounds', 'backgrounds'),
            ('Fashion', 'fashion'),
            ('Nature', 'nature'),
            ('Science', 'science'),
            ('Education', 'education'),
            ('People', 'people'),
            ('Places', 'places'),
            ('Animals', 'animals'),
            ('Food', 'food'),
            ('Sports', 'sports'),
            ('Travel', 'travel'),
            ('Buildings', 'buildings'),
            ('Business', 'business')
        ]
        
        category_combo = ttk.Combobox(
            category_frame,
            textvariable=self.category_var,
            values=[cat[0] for cat in categories],
            state="readonly",
            width=20
        )
        category_combo.pack(fill=tk.X)
        category_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        self.category_mapping = {cat[0]: cat[1] for cat in categories}
        
        row += 1
        
        # Size filters
        size_frame = ttk.LabelFrame(scrollable_frame, text="Minimum Size", padding=5)
        size_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        
        size_inner = ttk.Frame(size_frame)
        size_inner.pack(fill=tk.X)
        
        ttk.Label(size_inner, text="Width:").grid(row=0, column=0, sticky="w")
        self.min_width_var = tk.StringVar()
        ttk.Entry(size_inner, textvariable=self.min_width_var, width=10).grid(row=0, column=1, padx=(5, 10))
        
        ttk.Label(size_inner, text="Height:").grid(row=0, column=2, sticky="w")
        self.min_height_var = tk.StringVar()
        ttk.Entry(size_inner, textvariable=self.min_height_var, width=10).grid(row=0, column=3, padx=(5, 0))
        
        row += 1
        
        # Photographer filter
        photographer_frame = ttk.LabelFrame(scrollable_frame, text="Photographer", padding=5)
        photographer_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        
        self.photographer_var = tk.StringVar()
        ttk.Entry(photographer_frame, textvariable=self.photographer_var).pack(fill=tk.X)
        
        row += 1
        
        # Featured toggle
        featured_frame = ttk.LabelFrame(scrollable_frame, text="Options", padding=5)
        featured_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        
        self.featured_var = tk.BooleanVar()
        ttk.Checkbutton(
            featured_frame, 
            text="Featured images only", 
            variable=self.featured_var,
            command=self.on_filter_change
        ).pack(anchor="w")
        
        self.safe_search_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            featured_frame, 
            text="Safe search", 
            variable=self.safe_search_var,
            command=self.on_filter_change
        ).pack(anchor="w")
        
        row += 1
        
        # Reset filters button
        ttk.Button(
            scrollable_frame, 
            text="Reset Filters", 
            command=self.reset_filters
        ).grid(row=row, column=0, pady=10)
    
    def create_history_tab(self):
        """Create the search history tab."""
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="History")
        
        # History controls
        controls_frame = ttk.Frame(history_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            controls_frame, 
            text="Refresh", 
            command=self.load_search_history
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            controls_frame, 
            text="Clear History", 
            command=self.clear_search_history
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Button(
            controls_frame, 
            text="Export", 
            command=self.export_search_history
        ).pack(side=tk.RIGHT)
        
        # History list
        history_list_frame = ttk.Frame(history_frame)
        history_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Treeview for history
        columns = ('query', 'date', 'results', 'language')
        self.history_tree = ttk.Treeview(
            history_list_frame, 
            columns=columns, 
            show='tree headings',
            height=10
        )
        
        # Configure columns
        self.history_tree.heading('#0', text='#')
        self.history_tree.column('#0', width=50, minwidth=30)
        
        self.history_tree.heading('query', text='Search Query')
        self.history_tree.column('query', width=200, minwidth=150)
        
        self.history_tree.heading('date', text='Date')
        self.history_tree.column('date', width=120, minwidth=100)
        
        self.history_tree.heading('results', text='Results')
        self.history_tree.column('results', width=80, minwidth=60)
        
        self.history_tree.heading('language', text='Language')
        self.history_tree.column('language', width=80, minwidth=60)
        
        # Scrollbars
        h_scroll = ttk.Scrollbar(history_list_frame, orient=tk.HORIZONTAL, command=self.history_tree.xview)
        v_scroll = ttk.Scrollbar(history_list_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        
        self.history_tree.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        # Pack treeview and scrollbars
        self.history_tree.grid(row=0, column=0, sticky='nsew')
        h_scroll.grid(row=1, column=0, sticky='ew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        
        history_list_frame.grid_rowconfigure(0, weight=1)
        history_list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click to repeat search
        self.history_tree.bind('<Double-1>', self.repeat_search_from_history)
        
        # Context menu for history
        self.history_context_menu = tk.Menu(self, tearoff=0)
        self.history_context_menu.add_command(label="Repeat Search", command=self.repeat_selected_search)
        self.history_context_menu.add_command(label="Save Search", command=self.save_selected_search)
        self.history_context_menu.add_separator()
        self.history_context_menu.add_command(label="Delete", command=self.delete_selected_history)
        
        self.history_tree.bind('<Button-3>', self.show_history_context_menu)
    
    def create_saved_searches_tab(self):
        """Create the saved searches tab."""
        saved_frame = ttk.Frame(self.notebook)
        self.notebook.add(saved_frame, text="Saved")
        
        # Saved searches controls
        controls_frame = ttk.Frame(saved_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            controls_frame, 
            text="Refresh", 
            command=self.load_saved_searches
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            controls_frame, 
            text="Import", 
            command=self.import_saved_searches
        ).pack(side=tk.RIGHT)
        
        ttk.Button(
            controls_frame, 
            text="Export", 
            command=self.export_saved_searches
        ).pack(side=tk.RIGHT, padx=(0, 5))
        
        # Saved searches list
        saved_list_frame = ttk.Frame(saved_frame)
        saved_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Treeview for saved searches
        columns = ('name', 'query', 'created', 'used_count')
        self.saved_tree = ttk.Treeview(
            saved_list_frame, 
            columns=columns, 
            show='tree headings',
            height=10
        )
        
        # Configure columns
        self.saved_tree.heading('#0', text='#')
        self.saved_tree.column('#0', width=30, minwidth=30)
        
        self.saved_tree.heading('name', text='Name')
        self.saved_tree.column('name', width=150, minwidth=100)
        
        self.saved_tree.heading('query', text='Query')
        self.saved_tree.column('query', width=200, minwidth=150)
        
        self.saved_tree.heading('created', text='Created')
        self.saved_tree.column('created', width=100, minwidth=80)
        
        self.saved_tree.heading('used_count', text='Uses')
        self.saved_tree.column('used_count', width=60, minwidth=50)
        
        # Scrollbars for saved searches
        h_scroll_saved = ttk.Scrollbar(saved_list_frame, orient=tk.HORIZONTAL, command=self.saved_tree.xview)
        v_scroll_saved = ttk.Scrollbar(saved_list_frame, orient=tk.VERTICAL, command=self.saved_tree.yview)
        
        self.saved_tree.configure(xscrollcommand=h_scroll_saved.set, yscrollcommand=v_scroll_saved.set)
        
        # Pack saved searches treeview
        self.saved_tree.grid(row=0, column=0, sticky='nsew')
        h_scroll_saved.grid(row=1, column=0, sticky='ew')
        v_scroll_saved.grid(row=0, column=1, sticky='ns')
        
        saved_list_frame.grid_rowconfigure(0, weight=1)
        saved_list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.saved_tree.bind('<Double-1>', self.use_saved_search)
        
        # Context menu for saved searches
        self.saved_context_menu = tk.Menu(self, tearoff=0)
        self.saved_context_menu.add_command(label="Use Search", command=self.use_selected_saved_search)
        self.saved_context_menu.add_command(label="Edit", command=self.edit_selected_saved_search)
        self.saved_context_menu.add_separator()
        self.saved_context_menu.add_command(label="Delete", command=self.delete_selected_saved_search)
        
        self.saved_tree.bind('<Button-3>', self.show_saved_context_menu)
    
    def create_trending_tab(self):
        """Create the trending searches tab."""
        trending_frame = ttk.Frame(self.notebook)
        self.notebook.add(trending_frame, text="Trending")
        
        # Trending controls
        controls_frame = ttk.Frame(trending_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Time period:").pack(side=tk.LEFT)
        
        self.trending_period_var = tk.StringVar(value='7')
        period_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.trending_period_var,
            values=['1', '7', '30', '90'],
            width=5,
            state="readonly"
        )
        period_combo.pack(side=tk.LEFT, padx=(5, 0))
        period_combo.bind('<<ComboboxSelected>>', lambda e: self.load_trending_searches())
        
        ttk.Label(controls_frame, text="days").pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Button(
            controls_frame, 
            text="Refresh", 
            command=self.load_trending_searches
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Trending list
        trending_list_frame = ttk.Frame(trending_frame)
        trending_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        columns = ('query', 'count', 'avg_results', 'latest')
        self.trending_tree = ttk.Treeview(
            trending_list_frame, 
            columns=columns, 
            show='tree headings',
            height=10
        )
        
        # Configure trending columns
        self.trending_tree.heading('#0', text='Rank')
        self.trending_tree.column('#0', width=50, minwidth=40)
        
        self.trending_tree.heading('query', text='Search Query')
        self.trending_tree.column('query', width=200, minwidth=150)
        
        self.trending_tree.heading('count', text='Searches')
        self.trending_tree.column('count', width=80, minwidth=60)
        
        self.trending_tree.heading('avg_results', text='Avg Results')
        self.trending_tree.column('avg_results', width=80, minwidth=60)
        
        self.trending_tree.heading('latest', text='Last Search')
        self.trending_tree.column('latest', width=120, minwidth=100)
        
        # Scrollbars for trending
        h_scroll_trending = ttk.Scrollbar(trending_list_frame, orient=tk.HORIZONTAL, command=self.trending_tree.xview)
        v_scroll_trending = ttk.Scrollbar(trending_list_frame, orient=tk.VERTICAL, command=self.trending_tree.yview)
        
        self.trending_tree.configure(xscrollcommand=h_scroll_trending.set, yscrollcommand=v_scroll_trending.set)
        
        # Pack trending treeview
        self.trending_tree.grid(row=0, column=0, sticky='nsew')
        h_scroll_trending.grid(row=1, column=0, sticky='ew')
        v_scroll_trending.grid(row=0, column=1, sticky='ns')
        
        trending_list_frame.grid_rowconfigure(0, weight=1)
        trending_list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click to use trending search
        self.trending_tree.bind('<Double-1>', self.use_trending_search)
    
    def on_search_entry_change(self, event=None):
        """Handle search entry changes for autocomplete."""
        current_text = self.autocomplete_var.get()
        if len(current_text) >= 2:
            # Get autocomplete suggestions
            suggestions = self.search_manager.get_autocomplete_suggestions(current_text, 10)
            self.search_entry['values'] = suggestions
    
    def on_filter_change(self, event=None):
        """Handle filter changes."""
        self.update_current_filters()
    
    def update_current_filters(self):
        """Update current filters from UI."""
        self.current_filters = SearchFilter(
            color=self.color_mapping.get(self.color_var.get()),
            orientation=self.orientation_mapping.get(self.orientation_var.get()),
            category=self.category_mapping.get(self.category_var.get()),
            featured=self.featured_var.get(),
            photographer=self.photographer_var.get().strip() or None,
            min_width=int(self.min_width_var.get()) if self.min_width_var.get().isdigit() else None,
            min_height=int(self.min_height_var.get()) if self.min_height_var.get().isdigit() else None,
            safe_search=self.safe_search_var.get()
        )
    
    def perform_search(self, event=None):
        """Perform search with current filters."""
        query = self.autocomplete_var.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query.")
            return
        
        self.update_current_filters()
        
        # Get selected language code
        lang_name = self.language_var.get()
        lang_code = 'en'  # Default
        for code, name in self.search_manager.supported_languages.items():
            if name == lang_name:
                lang_code = code
                break
        
        # Translate query if needed
        if lang_code != 'en':
            translated_query = self.search_manager.translate_query(query, lang_code)
        else:
            translated_query = query
        
        # Add to search history
        self.search_manager.add_search_history(
            translated_query, 
            self.current_filters, 
            0,  # Will be updated with actual results
            lang_code
        )
        
        # Call search callback if provided
        if self.search_callback:
            self.search_callback({
                'query': translated_query,
                'original_query': query,
                'filters': self.current_filters,
                'language': lang_code
            })
        
        # Refresh history
        self.load_search_history()
    
    def reverse_image_search(self):
        """Perform reverse image search."""
        # Open file dialog to select image
        file_path = filedialog.askopenfilename(
            title="Select Image for Reverse Search",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Read image data
                with open(file_path, 'rb') as f:
                    image_data = f.read()
                
                # Show loading dialog
                loading_dialog = tk.Toplevel(self)
                loading_dialog.title("Reverse Search")
                loading_dialog.geometry("300x100")
                loading_dialog.transient(self)
                loading_dialog.grab_set()
                
                ttk.Label(loading_dialog, text="Analyzing image...").pack(expand=True)
                progress_bar = ttk.Progressbar(loading_dialog, mode='indeterminate')
                progress_bar.pack(pady=10, padx=20, fill=tk.X)
                progress_bar.start()
                
                # Perform reverse search in thread
                def reverse_search_thread():
                    try:
                        results = self.search_manager.reverse_image_search(
                            image_data, 
                            self.unsplash_api_key
                        )
                        
                        # Close loading dialog
                        loading_dialog.destroy()
                        
                        if results:
                            self.show_reverse_search_results(results)
                        else:
                            messagebox.showinfo("No Results", "No similar images found.")
                    
                    except Exception as e:
                        loading_dialog.destroy()
                        messagebox.showerror("Error", f"Reverse search failed: {str(e)}")
                
                threading.Thread(target=reverse_search_thread, daemon=True).start()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def show_reverse_search_results(self, results: List[Dict[str, Any]]):
        """Show reverse search results in a new window."""
        results_window = tk.Toplevel(self)
        results_window.title("Reverse Search Results")
        results_window.geometry("800x600")
        
        # Results list
        results_frame = ttk.Frame(results_window)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('similarity', 'description', 'photographer', 'tags')
        results_tree = ttk.Treeview(
            results_frame, 
            columns=columns, 
            show='tree headings'
        )
        
        # Configure columns
        results_tree.heading('#0', text='#')
        results_tree.column('#0', width=30)
        
        results_tree.heading('similarity', text='Similarity')
        results_tree.column('similarity', width=80)
        
        results_tree.heading('description', text='Description')
        results_tree.column('description', width=300)
        
        results_tree.heading('photographer', text='Photographer')
        results_tree.column('photographer', width=120)
        
        results_tree.heading('tags', text='Tags')
        results_tree.column('tags', width=200)
        
        # Add results
        for i, result in enumerate(results, 1):
            similarity = f"{result.get('similarity_score', 0):.1%}"
            description = result.get('description', result.get('alt_description', 'No description'))
            photographer = result.get('photographer', 'Unknown')
            tags = ', '.join(result.get('tags', []))
            
            results_tree.insert('', 'end', text=str(i), values=(similarity, description, photographer, tags))
        
        # Scrollbars
        v_scroll_results = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=results_tree.yview)
        results_tree.configure(yscrollcommand=v_scroll_results.set)
        
        results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll_results.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Use selected result button
        ttk.Button(
            results_window, 
            text="Use Selected Result", 
            command=lambda: self.use_reverse_search_result(results_tree, results, results_window)
        ).pack(pady=5)
    
    def use_reverse_search_result(self, tree, results, window):
        """Use selected reverse search result."""
        selection = tree.selection()
        if selection:
            item_index = int(tree.item(selection[0])['text']) - 1
            result = results[item_index]
            
            # Extract search terms from result
            description = result.get('description', result.get('alt_description', ''))
            tags = result.get('tags', [])
            
            # Create search query from tags and description
            search_terms = []
            if tags:
                search_terms.extend(tags[:3])  # Use first 3 tags
            
            if description and len(search_terms) < 3:
                # Extract keywords from description
                words = description.lower().split()
                keywords = [word for word in words if len(word) > 3]
                search_terms.extend(keywords[:3-len(search_terms)])
            
            query = ' '.join(search_terms[:3])
            
            if query:
                self.autocomplete_var.set(query)
                window.destroy()
                messagebox.showinfo("Search Query Set", f"Search query set to: {query}")
            else:
                messagebox.showwarning("Warning", "Could not generate search query from selected result.")
        else:
            messagebox.showwarning("Warning", "Please select a result to use.")
    
    def save_current_search(self):
        """Save current search configuration."""
        query = self.autocomplete_var.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query first.")
            return
        
        # Show save dialog
        save_dialog = tk.Toplevel(self)
        save_dialog.title("Save Search")
        save_dialog.geometry("400x250")
        save_dialog.transient(self)
        save_dialog.grab_set()
        
        # Center dialog
        save_dialog.update_idletasks()
        x = (save_dialog.winfo_screenwidth() // 2) - 200
        y = (save_dialog.winfo_screenheight() // 2) - 125
        save_dialog.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(save_dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Search Name:").pack(anchor="w")
        name_var = tk.StringVar(value=query)
        name_entry = ttk.Entry(frame, textvariable=name_var, width=40)
        name_entry.pack(fill=tk.X, pady=(2, 10))
        name_entry.focus()
        
        ttk.Label(frame, text="Tags (comma-separated):").pack(anchor="w")
        tags_var = tk.StringVar()
        ttk.Entry(frame, textvariable=tags_var, width=40).pack(fill=tk.X, pady=(2, 10))
        
        ttk.Label(frame, text="Notes:").pack(anchor="w")
        notes_text = tk.Text(frame, height=4, width=40)
        notes_text.pack(fill=tk.BOTH, expand=True, pady=(2, 10))
        
        def save_search():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Warning", "Please enter a name for the search.")
                return
            
            self.update_current_filters()
            tags = [tag.strip() for tag in tags_var.get().split(',') if tag.strip()]
            notes = notes_text.get('1.0', tk.END).strip()
            
            success = self.search_manager.save_search(
                name, query, self.current_filters, tags, notes
            )
            
            if success:
                save_dialog.destroy()
                self.load_saved_searches()
                messagebox.showinfo("Success", "Search saved successfully!")
            else:
                messagebox.showerror("Error", "Search name already exists. Please choose a different name.")
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Save", command=save_search).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Cancel", command=save_dialog.destroy).pack(side=tk.RIGHT, padx=(0, 5))
    
    def clear_search(self):
        """Clear search fields and filters."""
        self.autocomplete_var.set("")
        self.reset_filters()
    
    def reset_filters(self):
        """Reset all filters to default values."""
        self.color_var.set("Any")
        self.orientation_var.set("Any")
        self.category_var.set("Any")
        self.photographer_var.set("")
        self.min_width_var.set("")
        self.min_height_var.set("")
        self.featured_var.set(False)
        self.safe_search_var.set(True)
        self.update_current_filters()
    
    def load_search_data(self):
        """Load all search-related data."""
        self.load_search_history()
        self.load_saved_searches()
        self.load_trending_searches()
    
    def load_search_history(self):
        """Load search history into the tree view."""
        try:
            self.search_history = self.search_manager.get_search_history(50)
            
            # Clear existing items
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            # Add history items
            for i, entry in enumerate(self.search_history, 1):
                date_str = datetime.fromisoformat(entry.timestamp).strftime("%m/%d %H:%M")
                self.history_tree.insert(
                    '', 'end', 
                    text=str(i),
                    values=(entry.query, date_str, entry.results_count, 'Multi' if entry.filters else 'En')
                )
        
        except Exception as e:
            print(f"Error loading search history: {e}")
    
    def load_saved_searches(self):
        """Load saved searches into the tree view."""
        try:
            self.saved_searches = self.search_manager.get_saved_searches()
            
            # Clear existing items
            for item in self.saved_tree.get_children():
                self.saved_tree.delete(item)
            
            # Add saved searches
            for i, search in enumerate(self.saved_searches, 1):
                created_date = datetime.fromisoformat(search['created_at']).strftime("%m/%d/%y")
                self.saved_tree.insert(
                    '', 'end',
                    text=str(i),
                    values=(search['name'], search['query'], created_date, search['use_count'])
                )
        
        except Exception as e:
            print(f"Error loading saved searches: {e}")
    
    def load_trending_searches(self):
        """Load trending searches."""
        try:
            days = int(self.trending_period_var.get())
            trending = self.search_manager.get_trending_searches(days, 20)
            
            # Clear existing items
            for item in self.trending_tree.get_children():
                self.trending_tree.delete(item)
            
            # Add trending searches
            for i, trend in enumerate(trending, 1):
                latest_date = datetime.fromisoformat(trend['latest_search']).strftime("%m/%d %H:%M")
                self.trending_tree.insert(
                    '', 'end',
                    text=str(i),
                    values=(trend['query'], trend['search_count'], trend['avg_results'], latest_date)
                )
        
        except Exception as e:
            print(f"Error loading trending searches: {e}")
    
    # Event handlers for context menus and tree interactions
    def show_history_context_menu(self, event):
        """Show context menu for history tree."""
        item = self.history_tree.identify_row(event.y)
        if item:
            self.history_tree.selection_set(item)
            self.history_context_menu.post(event.x_root, event.y_root)
    
    def show_saved_context_menu(self, event):
        """Show context menu for saved searches tree."""
        item = self.saved_tree.identify_row(event.y)
        if item:
            self.saved_tree.selection_set(item)
            self.saved_context_menu.post(event.x_root, event.y_root)
    
    def repeat_search_from_history(self, event):
        """Repeat search from history on double-click."""
        self.repeat_selected_search()
    
    def repeat_selected_search(self):
        """Repeat selected search from history."""
        selection = self.history_tree.selection()
        if selection:
            item_index = int(self.history_tree.item(selection[0])['text']) - 1
            if 0 <= item_index < len(self.search_history):
                entry = self.search_history[item_index]
                self.autocomplete_var.set(entry.query)
                # Could also restore filters if needed
                messagebox.showinfo("Search Repeated", f"Search query set to: {entry.query}")
    
    def save_selected_search(self):
        """Save selected search from history."""
        selection = self.history_tree.selection()
        if selection:
            item_index = int(self.history_tree.item(selection[0])['text']) - 1
            if 0 <= item_index < len(self.search_history):
                entry = self.search_history[item_index]
                self.autocomplete_var.set(entry.query)
                self.save_current_search()
    
    def delete_selected_history(self):
        """Delete selected history entry."""
        # Implementation would require adding delete method to search_manager
        messagebox.showinfo("Info", "History deletion not implemented yet.")
    
    def use_saved_search(self, event):
        """Use saved search on double-click."""
        self.use_selected_saved_search()
    
    def use_selected_saved_search(self):
        """Use selected saved search."""
        selection = self.saved_tree.selection()
        if selection:
            item_index = int(self.saved_tree.item(selection[0])['text']) - 1
            if 0 <= item_index < len(self.saved_searches):
                search = self.saved_searches[item_index]
                result = self.search_manager.use_saved_search(search['name'])
                if result:
                    query, filters = result
                    self.autocomplete_var.set(query)
                    # Restore filters - implementation would set filter UI values
                    messagebox.showinfo("Search Loaded", f"Loaded search: {search['name']}")
                    self.load_saved_searches()  # Refresh to show updated use count
    
    def edit_selected_saved_search(self):
        """Edit selected saved search."""
        messagebox.showinfo("Info", "Edit saved search not implemented yet.")
    
    def delete_selected_saved_search(self):
        """Delete selected saved search."""
        selection = self.saved_tree.selection()
        if selection:
            item_index = int(self.saved_tree.item(selection[0])['text']) - 1
            if 0 <= item_index < len(self.saved_searches):
                search = self.saved_searches[item_index]
                if messagebox.askyesno("Confirm Delete", f"Delete saved search '{search['name']}'?"):
                    success = self.search_manager.delete_saved_search(search['name'])
                    if success:
                        self.load_saved_searches()
                        messagebox.showinfo("Success", "Saved search deleted.")
                    else:
                        messagebox.showerror("Error", "Failed to delete saved search.")
    
    def use_trending_search(self, event):
        """Use trending search on double-click."""
        selection = self.trending_tree.selection()
        if selection:
            query = self.trending_tree.item(selection[0])['values'][0]
            self.autocomplete_var.set(query)
            messagebox.showinfo("Search Set", f"Search query set to: {query}")
    
    def clear_search_history(self):
        """Clear search history."""
        if messagebox.askyesno("Confirm Clear", "Clear all search history?"):
            count = self.search_manager.clear_history()
            self.load_search_history()
            messagebox.showinfo("Success", f"Cleared {count} history entries.")
    
    def export_search_history(self):
        """Export search history to file."""
        file_path = filedialog.asksaveasfilename(
            title="Export Search History",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                format_type = 'json' if file_path.endswith('.json') else 'csv'
                data = self.search_manager.export_search_history(format_type)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(data)
                
                messagebox.showinfo("Success", f"Search history exported to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def import_saved_searches(self):
        """Import saved searches from file."""
        file_path = filedialog.askopenfilename(
            title="Import Saved Searches",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = f.read()
                
                success = self.search_manager.import_search_history(data, 'json')
                if success:
                    self.load_saved_searches()
                    messagebox.showinfo("Success", "Saved searches imported successfully!")
                else:
                    messagebox.showerror("Error", "Import failed. Please check the file format.")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Import failed: {str(e)}")
    
    def export_saved_searches(self):
        """Export saved searches to file."""
        file_path = filedialog.asksaveasfilename(
            title="Export Saved Searches",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                searches = self.search_manager.get_saved_searches()
                export_data = {
                    'saved_searches': searches,
                    'export_timestamp': datetime.now().isoformat()
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2)
                
                messagebox.showinfo("Success", f"Saved searches exported to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")