"""
Theme Manager for the Unsplash Image Search Application
Provides light and dark theme support with customizable color schemes.
"""

import tkinter as tk
from tkinter import ttk
import json
from pathlib import Path
from typing import Dict, Any, Callable, Optional


class ThemeColors:
    """Theme color definitions"""
    
    LIGHT_THEME = {
        'bg': '#ffffff',
        'fg': '#000000',
        'select_bg': '#0078d4',
        'select_fg': '#ffffff',
        'frame_bg': '#f0f0f0',
        'entry_bg': '#ffffff',
        'entry_fg': '#000000',
        'button_bg': '#e1e1e1',
        'button_fg': '#000000',
        'button_active_bg': '#d0d0d0',
        'disabled_fg': '#888888',
        'border': '#cccccc',
        'error': '#d13438',
        'success': '#107c10',
        'warning': '#ff8c00',
        'info': '#0078d4',
        'text_bg': '#ffffff',
        'text_fg': '#000000',
        'status_bg': '#f5f5f5',
        'tooltip_bg': '#ffffdd',
        'tooltip_fg': '#000000',
        'scrollbar_bg': '#e0e0e0',
        'scrollbar_thumb': '#c0c0c0',
        'progress_bg': '#e0e0e0',
        'progress_fg': '#0078d4'
    }
    
    DARK_THEME = {
        'bg': '#2d2d2d',
        'fg': '#ffffff',
        'select_bg': '#0078d4',
        'select_fg': '#ffffff',
        'frame_bg': '#3d3d3d',
        'entry_bg': '#404040',
        'entry_fg': '#ffffff',
        'button_bg': '#505050',
        'button_fg': '#ffffff',
        'button_active_bg': '#606060',
        'disabled_fg': '#888888',
        'border': '#555555',
        'error': '#f85149',
        'success': '#56d364',
        'warning': '#ffa500',
        'info': '#4fc3f7',
        'text_bg': '#2d2d2d',
        'text_fg': '#ffffff',
        'status_bg': '#3d3d3d',
        'tooltip_bg': '#4d4d4d',
        'tooltip_fg': '#ffffff',
        'scrollbar_bg': '#404040',
        'scrollbar_thumb': '#606060',
        'progress_bg': '#404040',
        'progress_fg': '#4fc3f7'
    }


class ThemeManager:
    """Manages application themes and styling"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.current_theme = 'light'
        self.theme_callbacks = []
        self.style = None
        self.root_window = None
        
        # Load theme preference
        self._load_theme_preference()
        
    def _load_theme_preference(self):
        """Load saved theme preference from config"""
        try:
            if hasattr(self.config_manager, 'config'):
                self.current_theme = self.config_manager.config.get(
                    'UI', 'theme', fallback='light'
                )
        except:
            self.current_theme = 'light'
    
    def _save_theme_preference(self):
        """Save theme preference to config"""
        try:
            if hasattr(self.config_manager, 'config'):
                if 'UI' not in self.config_manager.config:
                    self.config_manager.config.add_section('UI')
                self.config_manager.config.set('UI', 'theme', self.current_theme)
                
                # Save to file
                with open(self.config_manager.config_file, 'w') as f:
                    self.config_manager.config.write(f)
        except Exception as e:
            print(f"Error saving theme preference: {e}")
    
    def initialize(self, root_window: tk.Tk):
        """Initialize theme manager with root window"""
        self.root_window = root_window
        self.style = ttk.Style(root_window)
        self.apply_theme(self.current_theme)
    
    def get_colors(self, theme_name: str = None) -> Dict[str, str]:
        """Get color scheme for specified theme"""
        if theme_name is None:
            theme_name = self.current_theme
            
        if theme_name == 'dark':
            return ThemeColors.DARK_THEME.copy()
        else:
            return ThemeColors.LIGHT_THEME.copy()
    
    def apply_theme(self, theme_name: str):
        """Apply theme to the application"""
        if theme_name not in ['light', 'dark']:
            theme_name = 'light'
            
        self.current_theme = theme_name
        colors = self.get_colors(theme_name)
        
        if self.style is not None:
            self._configure_ttk_styles(colors)
        
        if self.root_window is not None:
            self._configure_tk_widgets(colors)
        
        # Save preference
        self._save_theme_preference()
        
        # Notify registered callbacks
        self._notify_theme_change(theme_name, colors)
    
    def _configure_ttk_styles(self, colors: Dict[str, str]):
        """Configure TTK widget styles"""
        style = self.style
        
        # Configure main theme
        if self.current_theme == 'dark':
            style.theme_use('clam')  # Good base for dark themes
        else:
            style.theme_use('clam')
        
        # Frame styles
        style.configure('TFrame', 
            background=colors['frame_bg'],
            borderwidth=0
        )
        
        style.configure('TLabelFrame', 
            background=colors['frame_bg'],
            foreground=colors['fg'],
            borderwidth=1,
            relief='solid',
            bordercolor=colors['border']
        )
        
        style.configure('TLabelFrame.Label',
            background=colors['frame_bg'],
            foreground=colors['fg']
        )
        
        # Button styles
        style.configure('TButton',
            background=colors['button_bg'],
            foreground=colors['button_fg'],
            borderwidth=1,
            relief='solid',
            bordercolor=colors['border'],
            focuscolor='none'
        )
        
        style.map('TButton',
            background=[
                ('active', colors['button_active_bg']),
                ('pressed', colors['select_bg']),
                ('disabled', colors['frame_bg'])
            ],
            foreground=[
                ('disabled', colors['disabled_fg'])
            ],
            bordercolor=[
                ('active', colors['select_bg']),
                ('focus', colors['select_bg'])
            ]
        )
        
        # Entry styles
        style.configure('TEntry',
            background=colors['entry_bg'],
            foreground=colors['entry_fg'],
            borderwidth=1,
            relief='solid',
            bordercolor=colors['border'],
            insertcolor=colors['fg'],
            selectbackground=colors['select_bg'],
            selectforeground=colors['select_fg']
        )
        
        style.map('TEntry',
            bordercolor=[
                ('focus', colors['select_bg']),
                ('active', colors['select_bg'])
            ]
        )
        
        # Label styles
        style.configure('TLabel',
            background=colors['frame_bg'],
            foreground=colors['fg']
        )
        
        # Combobox styles
        style.configure('TCombobox',
            background=colors['entry_bg'],
            foreground=colors['entry_fg'],
            borderwidth=1,
            relief='solid',
            bordercolor=colors['border'],
            selectbackground=colors['select_bg'],
            selectforeground=colors['select_fg']
        )
        
        # Progressbar styles
        style.configure('TProgressbar',
            background=colors['progress_fg'],
            troughcolor=colors['progress_bg'],
            borderwidth=0,
            relief='flat'
        )
        
        # Separator styles
        style.configure('TSeparator',
            background=colors['border']
        )
        
        # Scrollbar styles
        style.configure('TScrollbar',
            background=colors['scrollbar_bg'],
            troughcolor=colors['scrollbar_bg'],
            borderwidth=0,
            relief='flat'
        )
        
        style.map('TScrollbar',
            background=[
                ('active', colors['scrollbar_thumb']),
                ('pressed', colors['select_bg'])
            ]
        )
    
    def _configure_tk_widgets(self, colors: Dict[str, str]):
        """Configure standard Tk widget colors"""
        if self.root_window is None:
            return
            
        # Configure root window
        self.root_window.configure(
            bg=colors['bg'],
            highlightcolor=colors['select_bg'],
            highlightbackground=colors['border']
        )
        
        # Set default options for all Tk widgets
        self.root_window.option_add('*Background', colors['bg'])
        self.root_window.option_add('*Foreground', colors['fg'])
        self.root_window.option_add('*selectBackground', colors['select_bg'])
        self.root_window.option_add('*selectForeground', colors['select_fg'])
        self.root_window.option_add('*insertBackground', colors['fg'])
        self.root_window.option_add('*highlightColor', colors['select_bg'])
        self.root_window.option_add('*highlightBackground', colors['border'])
        
        # Text widget specific
        self.root_window.option_add('*Text*Background', colors['text_bg'])
        self.root_window.option_add('*Text*Foreground', colors['text_fg'])
        self.root_window.option_add('*Text*selectBackground', colors['select_bg'])
        self.root_window.option_add('*Text*selectForeground', colors['select_fg'])
        
        # Listbox specific
        self.root_window.option_add('*Listbox*Background', colors['entry_bg'])
        self.root_window.option_add('*Listbox*Foreground', colors['entry_fg'])
        self.root_window.option_add('*Listbox*selectBackground', colors['select_bg'])
        self.root_window.option_add('*Listbox*selectForeground', colors['select_fg'])
        
        # Canvas specific
        self.root_window.option_add('*Canvas*Background', colors['bg'])
        self.root_window.option_add('*Canvas*highlightBackground', colors['border'])
    
    def configure_widget(self, widget, widget_type: str = None):
        """Configure a specific widget with current theme"""
        colors = self.get_colors()
        
        if widget_type is None:
            widget_type = widget.winfo_class()
        
        try:
            if widget_type in ['Text', 'ScrolledText']:
                widget.configure(
                    bg=colors['text_bg'],
                    fg=colors['text_fg'],
                    selectbackground=colors['select_bg'],
                    selectforeground=colors['select_fg'],
                    insertbackground=colors['fg'],
                    highlightcolor=colors['select_bg'],
                    highlightbackground=colors['border']
                )
            elif widget_type == 'Listbox':
                widget.configure(
                    bg=colors['entry_bg'],
                    fg=colors['entry_fg'],
                    selectbackground=colors['select_bg'],
                    selectforeground=colors['select_fg'],
                    highlightcolor=colors['select_bg'],
                    highlightbackground=colors['border']
                )
            elif widget_type == 'Canvas':
                widget.configure(
                    bg=colors['bg'],
                    highlightbackground=colors['border'],
                    highlightcolor=colors['select_bg']
                )
            elif widget_type in ['Button', 'Label', 'Frame']:
                # For standard Tk widgets
                if hasattr(widget, 'configure'):
                    if widget_type == 'Button':
                        widget.configure(
                            bg=colors['button_bg'],
                            fg=colors['button_fg'],
                            activebackground=colors['button_active_bg'],
                            activeforeground=colors['button_fg'],
                            highlightbackground=colors['border'],
                            highlightcolor=colors['select_bg']
                        )
                    else:
                        widget.configure(
                            bg=colors['frame_bg'],
                            fg=colors['fg']
                        )
        except Exception as e:
            print(f"Error configuring widget {widget_type}: {e}")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        new_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme(new_theme)
    
    def register_theme_callback(self, callback: Callable[[str, Dict[str, str]], None]):
        """Register a callback to be called when theme changes"""
        self.theme_callbacks.append(callback)
    
    def _notify_theme_change(self, theme_name: str, colors: Dict[str, str]):
        """Notify all registered callbacks of theme change"""
        for callback in self.theme_callbacks:
            try:
                callback(theme_name, colors)
            except Exception as e:
                print(f"Error in theme callback: {e}")
    
    def create_themed_tooltip(self, widget, text: str):
        """Create a themed tooltip for a widget"""
        return ThemedTooltip(widget, text, self)


class ThemedTooltip:
    """Themed tooltip that follows current theme colors"""
    
    def __init__(self, widget, text: str, theme_manager: ThemeManager):
        self.widget = widget
        self.text = text
        self.theme_manager = theme_manager
        self.tooltip_window = None
        
        # Bind events
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Motion>", self.on_motion)
    
    def on_enter(self, event=None):
        """Show tooltip on mouse enter"""
        self.show_tooltip()
    
    def on_leave(self, event=None):
        """Hide tooltip on mouse leave"""
        self.hide_tooltip()
    
    def on_motion(self, event=None):
        """Update tooltip position on mouse motion"""
        if self.tooltip_window:
            self.position_tooltip(event)
    
    def show_tooltip(self):
        """Show the tooltip"""
        if self.tooltip_window or not self.text:
            return
        
        colors = self.theme_manager.get_colors()
        
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.configure(bg=colors['tooltip_bg'])
        
        # Create label
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background=colors['tooltip_bg'],
            foreground=colors['tooltip_fg'],
            relief=tk.SOLID,
            borderwidth=1,
            font=("TkDefaultFont", 9),
            padx=4,
            pady=2
        )
        label.pack()
        
        # Position tooltip
        self.position_tooltip()
    
    def position_tooltip(self, event=None):
        """Position the tooltip near the cursor"""
        if not self.tooltip_window:
            return
            
        # Get cursor position
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        
        # Ensure tooltip stays on screen
        screen_width = self.widget.winfo_screenwidth()
        screen_height = self.widget.winfo_screenheight()
        
        # Update tooltip geometry
        self.tooltip_window.update_idletasks()
        tooltip_width = self.tooltip_window.winfo_width()
        tooltip_height = self.tooltip_window.winfo_height()
        
        if x + tooltip_width > screen_width:
            x = screen_width - tooltip_width - 10
        if y + tooltip_height > screen_height:
            y = y - tooltip_height - 30
        
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
    
    def hide_tooltip(self):
        """Hide the tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
    
    def update_text(self, new_text: str):
        """Update tooltip text"""
        self.text = new_text
        if self.tooltip_window:
            self.hide_tooltip()
            self.show_tooltip()


class ThemedMessageBox:
    """Themed message box dialogs"""
    
    @staticmethod
    def show_info(parent, title: str, message: str, theme_manager: ThemeManager):
        """Show themed info dialog"""
        return ThemedMessageBox._show_message(parent, title, message, 'info', theme_manager)
    
    @staticmethod
    def show_warning(parent, title: str, message: str, theme_manager: ThemeManager):
        """Show themed warning dialog"""
        return ThemedMessageBox._show_message(parent, title, message, 'warning', theme_manager)
    
    @staticmethod
    def show_error(parent, title: str, message: str, theme_manager: ThemeManager):
        """Show themed error dialog"""
        return ThemedMessageBox._show_message(parent, title, message, 'error', theme_manager)
    
    @staticmethod
    def ask_yes_no(parent, title: str, message: str, theme_manager: ThemeManager):
        """Show themed yes/no dialog"""
        return ThemedMessageBox._show_message(parent, title, message, 'question', theme_manager)
    
    @staticmethod
    def _show_message(parent, title: str, message: str, msg_type: str, theme_manager: ThemeManager):
        """Internal method to show themed message dialog"""
        colors = theme_manager.get_colors()
        
        # Create dialog window
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.configure(bg=colors['bg'])
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 100
        dialog.geometry(f"400x150+{x}+{y}")
        
        result = None
        
        # Main frame
        main_frame = tk.Frame(dialog, bg=colors['bg'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Icon and message
        icon_color = colors.get(msg_type, colors['info'])
        icon_text = {'info': 'ℹ', 'warning': '⚠', 'error': '✖', 'question': '?'}
        
        icon_label = tk.Label(
            main_frame,
            text=icon_text.get(msg_type, 'ℹ'),
            font=('TkDefaultFont', 24),
            fg=icon_color,
            bg=colors['bg']
        )
        icon_label.grid(row=0, column=0, padx=(0, 15), pady=(0, 20))
        
        msg_label = tk.Label(
            main_frame,
            text=message,
            font=('TkDefaultFont', 10),
            fg=colors['fg'],
            bg=colors['bg'],
            wraplength=300,
            justify=tk.LEFT
        )
        msg_label.grid(row=0, column=1, pady=(0, 20), sticky='w')
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=colors['bg'])
        button_frame.grid(row=1, column=0, columnspan=2, sticky='e')
        
        if msg_type == 'question':
            def on_yes():
                nonlocal result
                result = True
                dialog.destroy()
            
            def on_no():
                nonlocal result
                result = False
                dialog.destroy()
            
            no_btn = tk.Button(
                button_frame, text="No", command=on_no,
                bg=colors['button_bg'], fg=colors['button_fg'],
                activebackground=colors['button_active_bg'],
                relief=tk.FLAT, padx=20
            )
            no_btn.pack(side=tk.RIGHT, padx=(5, 0))
            
            yes_btn = tk.Button(
                button_frame, text="Yes", command=on_yes,
                bg=colors['select_bg'], fg=colors['select_fg'],
                activebackground=colors['button_active_bg'],
                relief=tk.FLAT, padx=20
            )
            yes_btn.pack(side=tk.RIGHT)
        else:
            def on_ok():
                nonlocal result
                result = True
                dialog.destroy()
            
            ok_btn = tk.Button(
                button_frame, text="OK", command=on_ok,
                bg=colors['button_bg'], fg=colors['button_fg'],
                activebackground=colors['button_active_bg'],
                relief=tk.FLAT, padx=20
            )
            ok_btn.pack(side=tk.RIGHT)
        
        # Wait for dialog to close
        dialog.wait_window()
        return result