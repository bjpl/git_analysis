"""
Controlled Search Panel - UI components for managing image search with limits
Provides user controls for stopping, continuing, and monitoring image collection.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Dict, Any
from datetime import datetime
import threading

from ..theme_manager import ThemeManager
from ...services.controlled_image_service import ImageCollectionLimits, SearchSession


class LimitsConfigDialog:
    """Dialog for configuring image collection limits."""
    
    def __init__(self, parent, current_limits: ImageCollectionLimits, theme_manager: ThemeManager):
        self.parent = parent
        self.current_limits = current_limits
        self.theme_manager = theme_manager
        self.result = None
        self.dialog = None
        
    def show_dialog(self) -> Optional[ImageCollectionLimits]:
        """Show the configuration dialog and return new limits if saved."""
        self.create_dialog()
        self.parent.wait_window(self.dialog)
        return self.result
    
    def create_dialog(self):
        """Create the limits configuration dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Collection Limits Settings")
        self.dialog.geometry("500x450")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Apply theme
        colors = self.theme_manager.get_colors()
        self.dialog.configure(bg=colors['bg'])
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 250
        y = (self.dialog.winfo_screenheight() // 2) - 225
        self.dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Collection Limits Configuration",
            font=('TkDefaultFont', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Limits", padding="15")
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Max images per session
        row = 0
        ttk.Label(settings_frame, text="Maximum images per session:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.max_images_var = tk.IntVar(value=self.current_limits.max_images_per_session)
        max_images_spin = ttk.Spinbox(
            settings_frame, 
            from_=5, 
            to=200, 
            textvariable=self.max_images_var,
            width=10
        )
        max_images_spin.grid(row=row, column=1, padx=10, pady=5, sticky=tk.W)
        ttk.Label(settings_frame, text="(5-200 images)", foreground="gray").grid(row=row, column=2, sticky=tk.W)
        
        # Warning threshold
        row += 1
        ttk.Label(settings_frame, text="Warning threshold:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.warn_threshold_var = tk.IntVar(value=self.current_limits.warn_threshold)
        warn_spin = ttk.Spinbox(
            settings_frame,
            from_=5,
            to=100,
            textvariable=self.warn_threshold_var,
            width=10
        )
        warn_spin.grid(row=row, column=1, padx=10, pady=5, sticky=tk.W)
        ttk.Label(settings_frame, text="(show warning after N images)", foreground="gray").grid(row=row, column=2, sticky=tk.W)
        
        # Batch size
        row += 1
        ttk.Label(settings_frame, text="Images loaded per batch:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.batch_size_var = tk.IntVar(value=self.current_limits.batch_size)
        batch_spin = ttk.Spinbox(
            settings_frame,
            from_=1,
            to=15,
            textvariable=self.batch_size_var,
            width=10
        )
        batch_spin.grid(row=row, column=1, padx=10, pady=5, sticky=tk.W)
        ttk.Label(settings_frame, text="(1-15 images)", foreground="gray").grid(row=row, column=2, sticky=tk.W)
        
        # Confirmation interval
        row += 1
        ttk.Label(settings_frame, text="Confirmation interval:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.confirmation_var = tk.IntVar(value=self.current_limits.confirmation_interval)
        confirmation_spin = ttk.Spinbox(
            settings_frame,
            from_=10,
            to=50,
            textvariable=self.confirmation_var,
            width=10
        )
        confirmation_spin.grid(row=row, column=1, padx=10, pady=5, sticky=tk.W)
        ttk.Label(settings_frame, text="(ask user every N images)", foreground="gray").grid(row=row, column=2, sticky=tk.W)
        
        # Max pages
        row += 1
        ttk.Label(settings_frame, text="Maximum API pages:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.max_pages_var = tk.IntVar(value=self.current_limits.max_pages_per_session)
        pages_spin = ttk.Spinbox(
            settings_frame,
            from_=5,
            to=25,
            textvariable=self.max_pages_var,
            width=10
        )
        pages_spin.grid(row=row, column=1, padx=10, pady=5, sticky=tk.W)
        ttk.Label(settings_frame, text="(5-25 pages)", foreground="gray").grid(row=row, column=2, sticky=tk.W)
        
        # Preset buttons
        presets_frame = ttk.Frame(settings_frame)
        presets_frame.grid(row=row+1, column=0, columnspan=3, pady=(20, 0), sticky=tk.EW)
        
        ttk.Label(presets_frame, text="Presets:", font=('TkDefaultFont', 9, 'bold')).pack(side=tk.LEFT)
        
        ttk.Button(presets_frame, text="Conservative (25)", command=self.preset_conservative, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(presets_frame, text="Balanced (50)", command=self.preset_balanced, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(presets_frame, text="Extended (100)", command=self.preset_extended, width=15).pack(side=tk.LEFT, padx=5)
        
        # Info frame
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        info_text = """These limits help prevent:
• Excessive API usage (Unsplash has 50 calls/hour limit)
• Memory issues from too many cached images
• Unintended infinite scrolling
• Long processing times

Current API quota usage will be shown in the status bar."""
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Save Settings", command=self.save_settings).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_defaults).pack(side=tk.LEFT)
        
        # Bind escape key
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def preset_conservative(self):
        """Apply conservative preset."""
        self.max_images_var.set(25)
        self.warn_threshold_var.set(15)
        self.batch_size_var.set(3)
        self.confirmation_var.set(15)
        self.max_pages_var.set(8)
    
    def preset_balanced(self):
        """Apply balanced preset (default)."""
        self.max_images_var.set(50)
        self.warn_threshold_var.set(30)
        self.batch_size_var.set(5)
        self.confirmation_var.set(20)
        self.max_pages_var.set(12)
    
    def preset_extended(self):
        """Apply extended preset."""
        self.max_images_var.set(100)
        self.warn_threshold_var.set(60)
        self.batch_size_var.set(8)
        self.confirmation_var.set(25)
        self.max_pages_var.set(20)
    
    def reset_defaults(self):
        """Reset to default values."""
        self.preset_balanced()
    
    def save_settings(self):
        """Save the current settings."""
        try:
            # Validate settings
            max_images = self.max_images_var.get()
            warn_threshold = self.warn_threshold_var.get()
            batch_size = self.batch_size_var.get()
            confirmation_interval = self.confirmation_var.get()
            max_pages = self.max_pages_var.get()
            
            # Basic validation
            if warn_threshold >= max_images:
                messagebox.showerror("Invalid Settings", "Warning threshold must be less than maximum images.")
                return
            
            if confirmation_interval > max_images:
                messagebox.showerror("Invalid Settings", "Confirmation interval cannot be larger than maximum images.")
                return
            
            # Create new limits object
            self.result = ImageCollectionLimits(
                max_images_per_session=max_images,
                max_pages_per_session=max_pages,
                warn_threshold=warn_threshold,
                batch_size=batch_size,
                confirmation_interval=confirmation_interval
            )
            
            self.dialog.destroy()
            
        except tk.TclError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values.")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving settings: {e}")
    
    def cancel(self):
        """Cancel without saving."""
        self.result = None
        self.dialog.destroy()


class ControlledSearchPanel:
    """Enhanced search panel with collection limits and user controls."""
    
    def __init__(self, parent_frame, theme_manager: ThemeManager):
        self.parent_frame = parent_frame
        self.theme_manager = theme_manager
        
        # Current state
        self.current_limits = ImageCollectionLimits()
        self.current_session: Optional[SearchSession] = None
        
        # Callbacks
        self.on_search_callback: Optional[Callable] = None
        self.on_load_more_callback: Optional[Callable] = None
        self.on_stop_callback: Optional[Callable] = None
        self.get_stats_callback: Optional[Callable] = None
        
        # UI components
        self.widgets = {}
        
        self.create_widgets()
        self.update_ui_state()
    
    def create_widgets(self):
        """Create the enhanced search panel widgets."""
        # Main search frame
        search_frame = ttk.Frame(self.parent_frame, padding="5")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search input row
        input_row = ttk.Frame(search_frame)
        input_row.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(input_row, text="Search Unsplash:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.widgets['search_entry'] = ttk.Entry(input_row, width=40)
        self.widgets['search_entry'].pack(side=tk.LEFT, padx=(0, 5))
        self.widgets['search_entry'].bind('<Return>', self.on_search_enter)
        
        self.widgets['search_btn'] = ttk.Button(
            input_row, 
            text="🔍 Search", 
            command=self.start_search,
            width=12
        )
        self.widgets['search_btn'].pack(side=tk.LEFT, padx=(0, 5))
        
        # Progress bar
        self.widgets['progress'] = ttk.Progressbar(
            input_row,
            mode='indeterminate'
        )
        self.widgets['progress'].pack(side=tk.LEFT, padx=(0, 5))
        self.widgets['progress'].pack_forget()  # Hidden initially
        
        # Control buttons row
        control_row = ttk.Frame(search_frame)
        control_row.pack(fill=tk.X, pady=(5, 0))\n        
        # Load More button (replaces automatic pagination)
        self.widgets['load_more_btn'] = ttk.Button(
            control_row,
            text="📥 Load More Images (5)",
            command=self.load_more_images,
            state='disabled'
        )
        self.widgets['load_more_btn'].pack(side=tk.LEFT, padx=(0, 5))
        
        # Stop button
        self.widgets['stop_btn'] = ttk.Button(
            control_row,
            text="⏹️ Stop",
            command=self.stop_search,
            state='disabled'
        )
        self.widgets['stop_btn'].pack(side=tk.LEFT, padx=(0, 5))
        
        # New Search button
        self.widgets['new_search_btn'] = ttk.Button(
            control_row,
            text="🔄 New Search",
            command=self.new_search
        )
        self.widgets['new_search_btn'].pack(side=tk.LEFT, padx=(0, 10))
        
        # Settings button
        self.widgets['settings_btn'] = ttk.Button(
            control_row,
            text="⚙️ Limits",
            command=self.show_settings
        )
        self.widgets['settings_btn'].pack(side=tk.RIGHT)
        
        # Export button
        self.widgets['export_btn'] = ttk.Button(
            control_row,
            text="📤 Export",
            command=self.export_vocabulary
        )
        self.widgets['export_btn'].pack(side=tk.RIGHT, padx=(0, 5))
        
        # Status and progress display
        status_frame = ttk.Frame(self.parent_frame)
        status_frame.pack(fill=tk.X, pady=(5, 10))
        
        # Progress text
        self.widgets['progress_label'] = ttk.Label(
            status_frame,
            text="Ready to search",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.widgets['progress_label'].pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Stats label
        self.widgets['stats_label'] = ttk.Label(
            status_frame,
            text="API: 0/45 | Cache: 0MB",
            relief=tk.SUNKEN,
            anchor=tk.E
        )
        self.widgets['stats_label'].pack(side=tk.RIGHT, padx=(5, 0))
        
        # Add tooltips
        self.add_tooltips()
    
    def add_tooltips(self):
        """Add helpful tooltips to widgets."""
        tooltips = {
            'search_btn': "Start new image search (Enter)",
            'load_more_btn': "Load next batch of images (user controlled)",
            'stop_btn': "Stop current search session",
            'new_search_btn': "Start completely new search",
            'settings_btn': "Configure collection limits and behavior",
            'export_btn': "Export vocabulary to various formats"
        }
        
        for widget_name, tooltip_text in tooltips.items():
            if widget_name in self.widgets:
                self.theme_manager.create_themed_tooltip(self.widgets[widget_name], tooltip_text)
    
    def on_search_enter(self, event):
        """Handle Enter key in search box."""
        self.start_search()
    
    def start_search(self):
        """Start a new search with current limits."""
        query = self.widgets['search_entry'].get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter a search query.")
            return
        
        # Create new session
        self.current_session = SearchSession(query, self.current_limits)
        
        # Call search callback
        if self.on_search_callback:
            self.on_search_callback(query, self.current_limits)
        
        self.update_ui_state()
        self.update_progress_display()
    
    def load_more_images(self):
        """Load more images in current session."""
        if not self.current_session:
            return
        
        if self.on_load_more_callback:
            # Show progress
            self.widgets['progress'].pack(side=tk.LEFT, padx=(0, 5))
            self.widgets['progress'].start(10)
            self.widgets['load_more_btn'].configure(state='disabled')
            
            # Call callback in thread to avoid blocking UI
            threading.Thread(
                target=self._load_more_thread,
                daemon=True
            ).start()
    
    def _load_more_thread(self):
        """Thread function for loading more images."""
        try:
            if self.on_load_more_callback:
                self.on_load_more_callback()
        finally:
            # Update UI in main thread
            self.parent_frame.after(0, self._load_more_complete)
    
    def _load_more_complete(self):
        """Complete load more operation."""
        self.widgets['progress'].stop()
        self.widgets['progress'].pack_forget()
        self.update_ui_state()
        self.update_progress_display()
    
    def stop_search(self):
        """Stop current search session."""
        if self.current_session:
            self.current_session.is_stopped = True
        
        if self.on_stop_callback:
            self.on_stop_callback()
        
        self.update_ui_state()
        self.update_progress_display()
    
    def new_search(self):
        """Start a completely new search."""
        # Clear current session
        self.current_session = None
        self.widgets['search_entry'].delete(0, tk.END)
        self.widgets['search_entry'].focus_set()
        
        self.update_ui_state()
        self.update_progress_display()
    
    def show_settings(self):
        """Show limits configuration dialog."""
        dialog = LimitsConfigDialog(self.parent_frame, self.current_limits, self.theme_manager)
        new_limits = dialog.show_dialog()
        
        if new_limits:
            self.current_limits = new_limits
            self.update_ui_state()
            messagebox.showinfo("Settings Saved", "New limits have been applied and will be used for future searches.")
    
    def export_vocabulary(self):
        """Trigger vocabulary export."""
        # This would typically call a callback to the main app
        pass
    
    def update_ui_state(self):
        """Update UI state based on current session and limits."""
        has_session = self.current_session is not None
        session_active = has_session and not (self.current_session.is_stopped if self.current_session else True)
        can_load_more = False
        
        if self.current_session:
            can_load_more = self.current_session.can_load_more_images()
            
            # Update load more button text
            remaining = self.current_session.get_remaining_images()
            batch_size = min(self.current_limits.batch_size, remaining)
            self.widgets['load_more_btn'].configure(
                text=f"📥 Load More Images ({batch_size})"
            )
        
        # Update button states
        self.widgets['search_btn'].configure(state='normal')
        self.widgets['load_more_btn'].configure(
            state='normal' if (session_active and can_load_more) else 'disabled'
        )
        self.widgets['stop_btn'].configure(
            state='normal' if session_active else 'disabled'
        )
        
        # Update progress display
        self.update_progress_display()
    
    def update_progress_display(self):
        """Update progress and stats display."""
        if self.current_session:
            progress_text = f"Search: '{self.current_session.query}' - {self.current_session.get_progress_text()}"
            
            # Add status indicators
            if self.current_session.is_stopped:
                progress_text += " [STOPPED]"
            elif not self.current_session.can_load_more_images():
                progress_text += " [LIMIT REACHED]"
        else:
            progress_text = "Ready to search"
        
        self.widgets['progress_label'].configure(text=progress_text)
        
        # Update stats
        self.update_stats_display()
    
    def update_stats_display(self):
        """Update statistics display."""
        if self.get_stats_callback:
            try:
                stats = self.get_stats_callback()
                if stats and stats.get('status') != 'no_session':
                    rate_stats = stats.get('rate_limit_stats', {})
                    cache_stats = stats.get('cache_stats', {})
                    
                    api_text = f"{rate_stats.get('api_calls_made', 0)}/45"
                    cache_text = f"{cache_stats.get('size_mb', 0):.1f}MB"
                    
                    stats_text = f"API: {api_text} | Cache: {cache_text}"
                else:
                    stats_text = "API: 0/45 | Cache: 0MB"
            except Exception:
                stats_text = "API: 0/45 | Cache: 0MB"
        else:
            stats_text = "API: 0/45 | Cache: 0MB"
        
        self.widgets['stats_label'].configure(text=stats_text)
    
    def set_callbacks(self, 
                     on_search: Optional[Callable] = None,
                     on_load_more: Optional[Callable] = None,
                     on_stop: Optional[Callable] = None,
                     get_stats: Optional[Callable] = None):
        """Set callback functions for panel actions."""
        self.on_search_callback = on_search
        self.on_load_more_callback = on_load_more
        self.on_stop_callback = on_stop
        self.get_stats_callback = get_stats
    
    def update_session(self, session: Optional[SearchSession]):
        """Update current session reference."""
        self.current_session = session
        self.update_ui_state()
    
    def get_current_limits(self) -> ImageCollectionLimits:
        """Get current collection limits."""
        return self.current_limits
    
    def show_progress_animation(self, show: bool = True):
        """Show or hide progress animation."""
        if show:
            self.widgets['progress'].pack(side=tk.LEFT, padx=(0, 5))
            self.widgets['progress'].start(10)
        else:
            self.widgets['progress'].stop()
            self.widgets['progress'].pack_forget()