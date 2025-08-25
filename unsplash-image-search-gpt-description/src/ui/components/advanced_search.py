"""
Advanced search bar component with filters, autocomplete, and modern Material Design styling.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable, Optional, Any
import json
from pathlib import Path

from ..styles import StyleManager, ComponentStyle, Easing


class SearchSuggestions:
    """Manages search suggestions and history."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.history_file = data_dir / "search_history.json"
        self.suggestions_file = data_dir / "search_suggestions.json"
        
        self.search_history: List[str] = []
        self.popular_searches: List[str] = []
        self.category_suggestions: Dict[str, List[str]] = {}
        
        self._load_data()
    
    def _load_data(self):
        """Load search history and suggestions from disk."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.search_history = data.get('history', [])
            
            if self.suggestions_file.exists():
                with open(self.suggestions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.popular_searches = data.get('popular', [])
                    self.category_suggestions = data.get('categories', {})
        except (json.JSONDecodeError, FileNotFoundError):
            self._create_default_suggestions()
    
    def _create_default_suggestions(self):
        """Create default search suggestions."""
        self.popular_searches = [
            "nature", "city", "food", "people", "animals", "architecture",
            "landscape", "technology", "art", "travel", "business", "education"
        ]
        
        self.category_suggestions = {
            "Nature": ["forest", "mountain", "ocean", "sunset", "flowers", "trees"],
            "City": ["skyline", "street", "buildings", "traffic", "urban", "downtown"],
            "Food": ["restaurant", "cooking", "ingredients", "dining", "kitchen", "meal"],
            "People": ["portrait", "family", "friends", "business", "children", "elderly"],
            "Animals": ["cats", "dogs", "wildlife", "birds", "pets", "zoo"],
            "Travel": ["vacation", "hotel", "airplane", "beach", "adventure", "tourism"]
        }
        
        self._save_suggestions()
    
    def add_to_history(self, query: str):
        """Add search query to history."""
        query = query.strip().lower()
        if query and query not in self.search_history:
            self.search_history.insert(0, query)
            # Keep only last 50 searches
            self.search_history = self.search_history[:50]
            self._save_history()
    
    def get_suggestions(self, partial_query: str, max_results: int = 10) -> List[str]:
        """Get search suggestions based on partial query."""
        partial_query = partial_query.lower().strip()
        if not partial_query:
            return self.search_history[:max_results]
        
        suggestions = []
        
        # Add matching history items
        for item in self.search_history:
            if partial_query in item and item not in suggestions:
                suggestions.append(item)
        
        # Add matching popular searches
        for item in self.popular_searches:
            if partial_query in item and item not in suggestions:
                suggestions.append(item)
        
        # Add matching category suggestions
        for category, items in self.category_suggestions.items():
            for item in items:
                if partial_query in item and item not in suggestions:
                    suggestions.append(item)
        
        return suggestions[:max_results]
    
    def _save_history(self):
        """Save search history to disk."""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump({'history': self.search_history}, f, indent=2)
        except Exception as e:
            print(f"Error saving search history: {e}")
    
    def _save_suggestions(self):
        """Save suggestions to disk."""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            with open(self.suggestions_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'popular': self.popular_searches,
                    'categories': self.category_suggestions
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving suggestions: {e}")


class AutoCompleteDropdown(tk.Toplevel):
    """Dropdown widget for autocomplete suggestions."""
    
    def __init__(self, parent: tk.Widget, suggestions: List[str], 
                 style_manager: StyleManager, on_select: Callable[[str], None]):
        super().__init__(parent)
        
        self.parent_widget = parent
        self.suggestions = suggestions
        self.style_manager = style_manager
        self.on_select = on_select
        self.selected_index = -1
        
        self._setup_window()
        self._create_widgets()
        self._position_window()
        
        # Bind events
        self.bind('<FocusOut>', self._on_focus_out)
        self.bind('<Escape>', lambda e: self.destroy())
    
    def _setup_window(self):
        """Setup dropdown window properties."""
        self.wm_overrideredirect(True)
        self.configure(bg=self.style_manager.theme.colors.surface)
        self.attributes('-topmost', True)
        
        # Add border
        self.configure(
            relief='solid',
            borderwidth=1,
            highlightbackground=self.style_manager.theme.colors.outline,
            highlightcolor=self.style_manager.theme.colors.outline,
            highlightthickness=1
        )
    
    def _create_widgets(self):
        """Create dropdown content."""
        # Create scrollable listbox
        frame = tk.Frame(self, bg=self.style_manager.theme.colors.surface)
        frame.pack(fill=tk.BOTH, expand=True)
        
        self.listbox = tk.Listbox(
            frame,
            height=min(8, len(self.suggestions)),
            font=('Segoe UI', 10),
            activestyle='none',
            borderwidth=0,
            highlightthickness=0
        )
        
        # Apply theme colors
        self.listbox.configure(
            bg=self.style_manager.theme.colors.surface,
            fg=self.style_manager.theme.colors.on_surface,
            selectbackground=self.style_manager.theme.colors.primary,
            selectforeground=self.style_manager.theme.colors.on_primary
        )
        
        # Add suggestions
        for suggestion in self.suggestions:
            self.listbox.insert(tk.END, suggestion)
        
        # Add scrollbar if needed
        if len(self.suggestions) > 8:
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.listbox.yview)
            self.listbox.configure(yscrollcommand=scrollbar.set)
            
            self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        else:
            self.listbox.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection events
        self.listbox.bind('<Button-1>', self._on_click)
        self.listbox.bind('<Return>', self._on_return)
        self.listbox.bind('<Double-Button-1>', self._on_double_click)
    
    def _position_window(self):
        """Position dropdown below parent widget."""
        parent_x = self.parent_widget.winfo_rootx()
        parent_y = self.parent_widget.winfo_rooty() + self.parent_widget.winfo_height()
        parent_width = self.parent_widget.winfo_width()
        
        # Update geometry to get correct size
        self.update_idletasks()
        
        dropdown_height = self.winfo_reqheight()
        screen_height = self.winfo_screenheight()
        
        # Adjust position if dropdown would go off screen
        if parent_y + dropdown_height > screen_height:
            parent_y = self.parent_widget.winfo_rooty() - dropdown_height
        
        self.geometry(f"{parent_width}x{dropdown_height}+{parent_x}+{parent_y}")
    
    def _on_click(self, event):
        """Handle listbox click."""
        selection = self.listbox.curselection()
        if selection:
            self.selected_index = selection[0]
            self._select_current()
    
    def _on_return(self, event):
        """Handle return key."""
        self._select_current()
    
    def _on_double_click(self, event):
        """Handle double click."""
        self._on_click(event)
    
    def _select_current(self):
        """Select current item and close dropdown."""
        if 0 <= self.selected_index < len(self.suggestions):
            selected_text = self.suggestions[self.selected_index]
            self.on_select(selected_text)
        self.destroy()
    
    def _on_focus_out(self, event):
        """Handle focus loss."""
        # Small delay to allow for clicks
        self.after(100, self._check_focus)
    
    def _check_focus(self):
        """Check if focus is still in dropdown."""
        try:
            focus_widget = self.focus_get()
            if focus_widget != self and focus_widget != self.listbox:
                self.destroy()
        except:
            self.destroy()
    
    def handle_key(self, event):
        """Handle keyboard navigation."""
        if event.keysym == 'Down':
            self.selected_index = min(self.selected_index + 1, len(self.suggestions) - 1)
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.selected_index)
            self.listbox.see(self.selected_index)
            return 'break'
        
        elif event.keysym == 'Up':
            self.selected_index = max(self.selected_index - 1, 0)
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.selected_index)
            self.listbox.see(self.selected_index)
            return 'break'
        
        elif event.keysym == 'Return':
            self._select_current()
            return 'break'
        
        elif event.keysym == 'Escape':
            self.destroy()
            return 'break'


class SearchFilter:
    """Individual search filter."""
    
    def __init__(self, name: str, display_name: str, options: List[str], 
                 default_value: str = None):
        self.name = name
        self.display_name = display_name
        self.options = options
        self.current_value = default_value or options[0] if options else None
    
    def set_value(self, value: str):
        """Set filter value."""
        if value in self.options:
            self.current_value = value
    
    def get_value(self) -> str:
        """Get current filter value."""
        return self.current_value
    
    def is_active(self) -> bool:
        """Check if filter has non-default value."""
        return self.current_value != (self.options[0] if self.options else None)


class FilterPanel(tk.Frame):
    """Panel for search filters."""
    
    def __init__(self, parent: tk.Widget, style_manager: StyleManager,
                 on_filter_change: Callable[[Dict[str, str]], None] = None):
        super().__init__(parent)
        
        self.style_manager = style_manager
        self.on_filter_change = on_filter_change
        self.filters: Dict[str, SearchFilter] = {}
        self.filter_widgets: Dict[str, ttk.Combobox] = {}
        
        self._setup_filters()
        self._create_widgets()
        
        # Register with style manager
        self.style_manager.register_widget(self, classes=['frame', 'filter-panel'])
    
    def _setup_filters(self):
        """Setup available filters."""
        self.filters = {
            'orientation': SearchFilter(
                'orientation', 'Orientation',
                ['Any', 'Landscape', 'Portrait', 'Square'],
                'Any'
            ),
            'category': SearchFilter(
                'category', 'Category', 
                ['Any', 'Nature', 'People', 'Architecture', 'Animals', 'Food', 'Travel'],
                'Any'
            ),
            'color': SearchFilter(
                'color', 'Color',
                ['Any', 'Black & White', 'Blue', 'Green', 'Red', 'Orange', 'Yellow', 'Purple'],
                'Any'
            ),
            'size': SearchFilter(
                'size', 'Size',
                ['Any', 'Small', 'Medium', 'Large'],
                'Any'
            )
        }
    
    def _create_widgets(self):
        """Create filter widgets."""
        # Title
        title_label = self.style_manager.create_label(
            self, "Filters", heading=3
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Filter controls
        for filter_name, filter_obj in self.filters.items():
            filter_frame = tk.Frame(self)
            filter_frame.pack(fill='x', pady=5)
            
            # Filter label
            label = self.style_manager.create_label(
                filter_frame, f"{filter_obj.display_name}:"
            )
            label.pack(side='left')
            
            # Filter combobox
            combobox = ttk.Combobox(
                filter_frame,
                values=filter_obj.options,
                state='readonly',
                width=12
            )
            combobox.set(filter_obj.current_value)
            combobox.pack(side='right')
            
            self.filter_widgets[filter_name] = combobox
            
            # Bind change event
            combobox.bind('<<ComboboxSelected>>', 
                         lambda e, fname=filter_name: self._on_filter_changed(fname))
        
        # Clear filters button
        clear_btn = self.style_manager.create_button(
            self, "Clear Filters", variant='text'
        )
        clear_btn.configure(command=self._clear_filters)
        clear_btn.pack(pady=(10, 0))
    
    def _on_filter_changed(self, filter_name: str):
        """Handle filter change."""
        combobox = self.filter_widgets[filter_name]
        new_value = combobox.get()
        
        self.filters[filter_name].set_value(new_value)
        
        if self.on_filter_change:
            self.on_filter_change(self.get_active_filters())
    
    def _clear_filters(self):
        """Clear all filters to default values."""
        for filter_name, filter_obj in self.filters.items():
            default_value = filter_obj.options[0] if filter_obj.options else None
            filter_obj.set_value(default_value)
            self.filter_widgets[filter_name].set(default_value)
        
        if self.on_filter_change:
            self.on_filter_change(self.get_active_filters())
    
    def get_active_filters(self) -> Dict[str, str]:
        """Get currently active filters."""
        active_filters = {}
        for filter_name, filter_obj in self.filters.items():
            if filter_obj.is_active():
                active_filters[filter_name] = filter_obj.get_value()
        return active_filters
    
    def set_filter(self, filter_name: str, value: str):
        """Set specific filter value."""
        if filter_name in self.filters:
            self.filters[filter_name].set_value(value)
            self.filter_widgets[filter_name].set(value)


class AdvancedSearchBar(tk.Frame):
    """Advanced search bar with autocomplete, filters, and modern styling."""
    
    def __init__(self, parent: tk.Widget, style_manager: StyleManager,
                 data_dir: Path, on_search: Callable[[str, Dict[str, str]], None] = None,
                 on_clear: Callable[[], None] = None):
        super().__init__(parent)
        
        self.style_manager = style_manager
        self.data_dir = data_dir
        self.on_search = on_search
        self.on_clear = on_clear
        
        # Components
        self.suggestions = SearchSuggestions(data_dir)
        self.current_dropdown: Optional[AutoCompleteDropdown] = None
        self.filters_visible = False
        
        # Variables
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_text_changed)
        
        self._create_widgets()
        self._setup_bindings()
        
        # Register with style manager
        self.style_manager.register_widget(self, classes=['frame', 'search-bar'])
    
    def _create_widgets(self):
        """Create search bar widgets."""
        # Main search container
        search_container = self.style_manager.create_frame(self, variant='card')
        search_container.pack(fill='x', padx=10, pady=5)
        
        # Search input row
        input_row = tk.Frame(search_container)
        input_row.pack(fill='x', padx=15, pady=15)
        
        # Search icon
        search_icon = self.style_manager.create_label(
            input_row, "🔍", font=('Segoe UI', 16)
        )
        search_icon.pack(side='left', padx=(0, 10))
        
        # Search entry
        self.search_entry = self.style_manager.create_entry(
            input_row, textvariable=self.search_var, font=('Segoe UI', 14)
        )
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        # Search button
        self.search_button = self.style_manager.create_button(
            input_row, "Search", variant='primary'
        )
        self.search_button.configure(command=self._perform_search)
        self.search_button.pack(side='right', padx=(5, 0))
        
        # Filter toggle button
        self.filter_button = self.style_manager.create_button(
            input_row, "⚙", variant='text'
        )
        self.filter_button.configure(command=self._toggle_filters)
        self.filter_button.pack(side='right')
        
        # Action buttons row
        action_row = tk.Frame(search_container)
        action_row.pack(fill='x', padx=15, pady=(0, 15))
        
        # Recent searches label
        recent_label = self.style_manager.create_label(
            action_row, "Recent:", font=('Segoe UI', 10)
        )
        recent_label.pack(side='left')
        
        # Quick search buttons
        self.quick_buttons_frame = tk.Frame(action_row)
        self.quick_buttons_frame.pack(side='left', padx=(10, 0))
        
        self._create_quick_search_buttons()
        
        # Clear button
        clear_button = self.style_manager.create_button(
            action_row, "Clear", variant='text'
        )
        clear_button.configure(command=self._clear_search)
        clear_button.pack(side='right')
        
        # Progress indicator (hidden by default)
        self.progress_frame = tk.Frame(search_container)
        self.progress_frame.pack(fill='x', padx=15, pady=(0, 10))
        self.progress_frame.pack_forget()  # Hidden by default
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='indeterminate',
            style='Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill='x')
        
        # Filter panel (hidden by default)
        self.filter_panel = FilterPanel(
            self, self.style_manager, self._on_filter_changed
        )
        # Initially hidden
    
    def _create_quick_search_buttons(self):
        """Create quick search buttons for recent searches."""
        # Clear existing buttons
        for widget in self.quick_buttons_frame.winfo_children():
            widget.destroy()
        
        # Add buttons for recent searches (max 5)
        recent_searches = self.suggestions.search_history[:5]
        for query in recent_searches:
            if query:
                btn = self.style_manager.create_button(
                    self.quick_buttons_frame, query[:15] + "..." if len(query) > 15 else query,
                    variant='text'
                )
                btn.configure(command=lambda q=query: self._quick_search(q))
                btn.pack(side='left', padx=2)
    
    def _setup_bindings(self):
        """Setup event bindings."""
        self.search_entry.bind('<Return>', lambda e: self._perform_search())
        self.search_entry.bind('<KeyPress>', self._on_key_press)
        self.search_entry.bind('<FocusOut>', self._on_focus_out)
        
        # Bind window clicks to close dropdown
        self.bind_all('<Button-1>', self._on_window_click)
    
    def _on_search_text_changed(self, *args):
        """Handle search text changes for autocomplete."""
        query = self.search_var.get()
        
        if len(query) >= 2:  # Show suggestions after 2 characters
            suggestions = self.suggestions.get_suggestions(query)
            if suggestions and query.lower() not in [s.lower() for s in suggestions]:
                self._show_autocomplete(suggestions)
            else:
                self._hide_autocomplete()
        else:
            self._hide_autocomplete()
    
    def _show_autocomplete(self, suggestions: List[str]):
        """Show autocomplete dropdown."""
        self._hide_autocomplete()  # Close any existing dropdown
        
        if suggestions:
            self.current_dropdown = AutoCompleteDropdown(
                self.search_entry, suggestions, self.style_manager, self._on_suggestion_selected
            )
            
            # Animate dropdown appearance
            self.style_manager.animate_widget(
                self.current_dropdown, 'fade_in', duration=0.2
            )
    
    def _hide_autocomplete(self):
        """Hide autocomplete dropdown."""
        if self.current_dropdown:
            try:
                self.current_dropdown.destroy()
            except:
                pass
            self.current_dropdown = None
    
    def _on_suggestion_selected(self, suggestion: str):
        """Handle autocomplete suggestion selection."""
        self.search_var.set(suggestion)
        self.search_entry.icursor(tk.END)
        self._hide_autocomplete()
        self.search_entry.focus_set()
    
    def _on_key_press(self, event):
        """Handle key press in search entry."""
        if self.current_dropdown and event.keysym in ['Down', 'Up', 'Return', 'Escape']:
            return self.current_dropdown.handle_key(event)
    
    def _on_focus_out(self, event):
        """Handle search entry focus out."""
        # Delay hiding to allow for dropdown interaction
        self.after(200, self._check_dropdown_focus)
    
    def _check_dropdown_focus(self):
        """Check if focus moved to dropdown."""
        if self.current_dropdown:
            try:
                focus_widget = self.focus_get()
                if focus_widget != self.current_dropdown.listbox:
                    self._hide_autocomplete()
            except:
                self._hide_autocomplete()
    
    def _on_window_click(self, event):
        """Handle clicks outside dropdown."""
        if self.current_dropdown:
            try:
                if event.widget not in [self.current_dropdown, self.current_dropdown.listbox]:
                    self._hide_autocomplete()
            except:
                self._hide_autocomplete()
    
    def _toggle_filters(self):
        """Toggle filter panel visibility."""
        if self.filters_visible:
            self._hide_filters()
        else:
            self._show_filters()
    
    def _show_filters(self):
        """Show filter panel."""
        self.filter_panel.pack(fill='x', padx=10, pady=(0, 10))
        self.filters_visible = True
        
        # Animate filter panel
        self.style_manager.animate_widget(
            self.filter_panel, 'slide_in', direction='up', duration=0.3
        )
        
        # Update filter button appearance
        self.filter_button.configure(relief='solid')
    
    def _hide_filters(self):
        """Hide filter panel."""
        def hide_after_animation():
            self.filter_panel.pack_forget()
            self.filters_visible = False
        
        # Animate out and then hide
        self.style_manager.animate_widget(
            self.filter_panel, 'slide_out', direction='up', 
            duration=0.3, complete_callback=hide_after_animation
        )
        
        # Update filter button appearance
        self.filter_button.configure(relief='flat')
    
    def _on_filter_changed(self, active_filters: Dict[str, str]):
        """Handle filter changes."""
        # Update filter button to show active state
        if active_filters:
            self.style_manager.add_class(self.filter_button, 'active')
        else:
            self.style_manager.remove_class(self.filter_button, 'active')
    
    def _perform_search(self):
        """Perform search with current query and filters."""
        query = self.search_var.get().strip()
        if not query:
            return
        
        # Add to search history
        self.suggestions.add_to_history(query)
        
        # Update quick search buttons
        self._create_quick_search_buttons()
        
        # Hide autocomplete
        self._hide_autocomplete()
        
        # Get active filters
        active_filters = self.filter_panel.get_active_filters()
        
        # Show loading state
        self.show_loading()
        
        # Call search callback
        if self.on_search:
            self.on_search(query, active_filters)
    
    def _quick_search(self, query: str):
        """Perform quick search with predefined query."""
        self.search_var.set(query)
        self._perform_search()
    
    def _clear_search(self):
        """Clear search and filters."""
        self.search_var.set('')
        self.filter_panel._clear_filters()
        self._hide_autocomplete()
        self.hide_loading()
        
        if self.on_clear:
            self.on_clear()
    
    def show_loading(self):
        """Show loading state."""
        self.progress_frame.pack(fill='x', padx=15, pady=(0, 10))
        self.progress_bar.start(10)
        
        # Disable search controls
        self.search_entry.configure(state='disabled')
        self.search_button.configure(state='disabled')
        self.filter_button.configure(state='disabled')
    
    def hide_loading(self):
        """Hide loading state."""
        self.progress_bar.stop()
        self.progress_frame.pack_forget()
        
        # Re-enable search controls
        self.search_entry.configure(state='normal')
        self.search_button.configure(state='normal')
        self.filter_button.configure(state='normal')
    
    def get_current_query(self) -> str:
        """Get current search query."""
        return self.search_var.get().strip()
    
    def set_query(self, query: str):
        """Set search query."""
        self.search_var.set(query)
    
    def get_active_filters(self) -> Dict[str, str]:
        """Get currently active filters."""
        return self.filter_panel.get_active_filters()
    
    def set_filter(self, filter_name: str, value: str):
        """Set specific filter value."""
        self.filter_panel.set_filter(filter_name, value)