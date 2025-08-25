"""
Core accessibility manager and ARIA-like attributes for Tkinter.
Provides the foundation for making Tkinter applications accessible.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable, List
import json
from pathlib import Path
import platform


class AccessibilityWidget:
    """
    Wrapper class that adds ARIA-like attributes to Tkinter widgets.
    Provides screen reader support and accessibility metadata.
    """
    
    def __init__(self, widget: tk.Widget):
        self.widget = widget
        self._aria_attributes = {}
        self._accessible_name = ""
        self._accessible_description = ""
        self._accessible_role = ""
        self._tab_index = None
        
        # Initialize accessibility attributes
        self._setup_accessibility()
    
    def _setup_accessibility(self):
        """Initialize basic accessibility features."""
        # Add accessibility data to widget
        if not hasattr(self.widget, '_accessibility'):
            self.widget._accessibility = self
    
    def set_accessible_name(self, name: str):
        """Set the accessible name (equivalent to aria-label)."""
        self._accessible_name = name
        self._aria_attributes['label'] = name
        
        # Add to widget for screen reader access
        if hasattr(self.widget, 'config'):
            try:
                # Try to set tooltip as backup
                self._create_accessible_tooltip()
            except:
                pass
    
    def set_accessible_description(self, description: str):
        """Set the accessible description (equivalent to aria-describedby)."""
        self._accessible_description = description
        self._aria_attributes['describedby'] = description
    
    def set_role(self, role: str):
        """Set the widget role (equivalent to ARIA role)."""
        self._accessible_role = role
        self._aria_attributes['role'] = role
    
    def set_state(self, state: str, value: Any):
        """Set widget state (equivalent to aria-* states)."""
        self._aria_attributes[f"aria-{state}"] = value
        
        # Update visual state if applicable
        if state == "expanded" and hasattr(self.widget, 'state'):
            visual_state = "expanded" if value else "collapsed"
            try:
                self.widget.state([visual_state])
            except:
                pass
    
    def set_property(self, prop: str, value: Any):
        """Set widget property (equivalent to aria-* properties)."""
        self._aria_attributes[f"aria-{prop}"] = value
    
    def get_accessibility_info(self) -> Dict[str, Any]:
        """Get all accessibility information for this widget."""
        return {
            'name': self._accessible_name,
            'description': self._accessible_description,
            'role': self._accessible_role,
            'attributes': self._aria_attributes.copy(),
            'widget_class': self.widget.__class__.__name__,
            'tab_index': self._tab_index
        }
    
    def set_tab_index(self, index: int):
        """Set tab order index."""
        self._tab_index = index
    
    def _create_accessible_tooltip(self):
        """Create tooltip for accessibility information."""
        tooltip_text = self._accessible_name
        if self._accessible_description:
            tooltip_text += f" - {self._accessible_description}"
        
        if tooltip_text and not hasattr(self.widget, '_tooltip'):
            self.widget._tooltip = AccessibleTooltip(self.widget, tooltip_text)
    
    def announce(self, message: str, priority: str = "polite"):
        """Announce message to screen readers."""
        from .screen_reader import ScreenReaderSupport
        ScreenReaderSupport.announce(message, priority)


class AccessibleTooltip:
    """Accessible tooltip that provides additional context."""
    
    def __init__(self, widget: tk.Widget, text: str):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.delay = 1000  # 1 second delay
        self.timer_id = None
        
        # Bind events
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<KeyPress>", self.on_keypress)
    
    def on_enter(self, event=None):
        """Show tooltip after delay."""
        if self.timer_id:
            self.widget.after_cancel(self.timer_id)
        self.timer_id = self.widget.after(self.delay, self.show_tooltip)
    
    def on_leave(self, event=None):
        """Hide tooltip and cancel timer."""
        if self.timer_id:
            self.widget.after_cancel(self.timer_id)
            self.timer_id = None
        self.hide_tooltip()
    
    def on_keypress(self, event=None):
        """Show tooltip on F1 key for keyboard users."""
        if event and event.keysym == "F1":
            self.show_tooltip()
            return "break"
    
    def show_tooltip(self):
        """Display the tooltip."""
        if self.tooltip_window:
            return
        
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.configure(bg="#ffffdd", bd=1, relief="solid")
        
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            bg="#ffffdd",
            fg="#000000",
            font=("Arial", 9),
            justify="left",
            wraplength=300,
            padx=4,
            pady=2
        )
        label.pack()
        
        self.tooltip_window.geometry(f"+{x}+{y}")
        
        # Auto-hide after 5 seconds for screen reader users
        self.tooltip_window.after(5000, self.hide_tooltip)
    
    def hide_tooltip(self):
        """Hide the tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class AccessibilityManager:
    """
    Main accessibility manager for Tkinter applications.
    Coordinates all accessibility features and settings.
    """
    
    def __init__(self, root_window: tk.Tk):
        self.root = root_window
        self.settings = self._load_settings()
        self.accessible_widgets = {}
        self.focus_manager = None
        self.screen_reader = None
        self.keyboard_nav = None
        self.sound_manager = None
        
        # Initialize subsystems
        self._initialize_subsystems()
        
        # Apply initial settings
        self._apply_settings()
        
        # Setup global event handlers
        self._setup_global_handlers()
    
    def _initialize_subsystems(self):
        """Initialize accessibility subsystems."""
        try:
            from .focus_manager import FocusManager
            self.focus_manager = FocusManager(self.root)
        except ImportError:
            print("Focus manager not available")
        
        try:
            from .screen_reader import ScreenReaderSupport
            self.screen_reader = ScreenReaderSupport()
        except ImportError:
            print("Screen reader support not available")
        
        try:
            from .keyboard_nav import KeyboardNavigation
            self.keyboard_nav = KeyboardNavigation(self.root, self.settings)
        except ImportError:
            print("Keyboard navigation not available")
        
        try:
            from .sound_cues import SoundManager
            if self.settings.get('sound_enabled', False):
                self.sound_manager = SoundManager()
        except ImportError:
            print("Sound manager not available")
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load accessibility settings from file."""
        settings_file = Path.home() / ".accessibility_settings.json"
        default_settings = {
            'font_scale': 1.0,
            'high_contrast': False,
            'color_blind_mode': None,
            'sound_enabled': False,
            'focus_indicators': True,
            'keyboard_navigation': True,
            'screen_reader_enabled': True,
            'reduced_motion': False,
            'custom_shortcuts': {},
            'announcement_verbosity': 'normal'  # quiet, normal, verbose
        }
        
        try:
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    default_settings.update(loaded_settings)
        except Exception as e:
            print(f"Error loading accessibility settings: {e}")
        
        return default_settings
    
    def save_settings(self):
        """Save current accessibility settings."""
        settings_file = Path.home() / ".accessibility_settings.json"
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving accessibility settings: {e}")
    
    def _apply_settings(self):
        """Apply current accessibility settings."""
        # Apply font scaling
        self._apply_font_scaling()
        
        # Apply high contrast if enabled
        if self.settings.get('high_contrast'):
            self._apply_high_contrast()
        
        # Apply color blind mode
        if self.settings.get('color_blind_mode'):
            self._apply_color_blind_mode()
    
    def _apply_font_scaling(self):
        """Apply font scaling to all text."""
        scale = self.settings.get('font_scale', 1.0)
        if scale != 1.0:
            # Update default fonts
            import tkinter.font as tkFont
            default_font = tkFont.nametofont("TkDefaultFont")
            text_font = tkFont.nametofont("TkTextFont")
            
            new_size = int(default_font['size'] * scale)
            default_font.configure(size=new_size)
            text_font.configure(size=new_size)
    
    def _apply_high_contrast(self):
        """Apply high contrast theme."""
        try:
            from .themes import HighContrastThemes
            theme = HighContrastThemes()
            colors = theme.get_high_contrast_colors()
            
            # Apply to root and configure defaults
            self.root.configure(bg=colors['bg'])
            self.root.option_add('*Background', colors['bg'])
            self.root.option_add('*Foreground', colors['fg'])
            self.root.option_add('*selectBackground', colors['select_bg'])
            self.root.option_add('*selectForeground', colors['select_fg'])
        except ImportError:
            print("High contrast themes not available")
    
    def _apply_color_blind_mode(self):
        """Apply color blind friendly mode."""
        try:
            from .themes import ColorBlindThemes
            theme = ColorBlindThemes()
            mode = self.settings.get('color_blind_mode')
            colors = theme.get_color_blind_colors(mode)
            
            # Apply color blind friendly colors
            self.root.option_add('*Background', colors['bg'])
            self.root.option_add('*Foreground', colors['fg'])
        except ImportError:
            print("Color blind themes not available")
    
    def _setup_global_handlers(self):
        """Setup global keyboard and event handlers."""
        # Global accessibility shortcuts
        self.root.bind('<Control-Alt-a>', self._show_accessibility_help)
        self.root.bind('<Control-Alt-s>', self._show_accessibility_settings)
        self.root.bind('<Control-Alt-h>', self._toggle_high_contrast)
        
        # Screen reader shortcuts
        self.root.bind('<Control-Alt-r>', self._read_current_widget)
        self.root.bind('<Control-Alt-n>', self._read_next_widget)
        self.root.bind('<Control-Alt-p>', self._read_previous_widget)
    
    def make_accessible(self, widget: tk.Widget, **kwargs) -> AccessibilityWidget:
        """
        Make a widget accessible by wrapping it with accessibility features.
        
        Args:
            widget: The Tkinter widget to make accessible
            **kwargs: Accessibility attributes (name, description, role, etc.)
        
        Returns:
            AccessibilityWidget wrapper
        """
        acc_widget = AccessibilityWidget(widget)
        
        # Apply provided attributes
        if 'name' in kwargs:
            acc_widget.set_accessible_name(kwargs['name'])
        if 'description' in kwargs:
            acc_widget.set_accessible_description(kwargs['description'])
        if 'role' in kwargs:
            acc_widget.set_role(kwargs['role'])
        
        # Store reference
        widget_id = id(widget)
        self.accessible_widgets[widget_id] = acc_widget
        
        # Setup focus handling
        if self.focus_manager and self.settings.get('focus_indicators', True):
            self.focus_manager.add_widget(widget)
        
        # Add keyboard navigation
        if self.keyboard_nav and self.settings.get('keyboard_navigation', True):
            self.keyboard_nav.add_widget(widget)
        
        return acc_widget
    
    def announce(self, message: str, priority: str = "polite"):
        """Announce message to screen readers."""
        if self.screen_reader and self.settings.get('screen_reader_enabled', True):
            self.screen_reader.announce(message, priority)
        
        # Also play sound cue if enabled
        if self.sound_manager and self.settings.get('sound_enabled', False):
            self.sound_manager.play_notification()
    
    def set_font_scale(self, scale: float):
        """Set font scaling factor (0.5 to 2.0)."""
        scale = max(0.5, min(2.0, scale))
        self.settings['font_scale'] = scale
        self._apply_font_scaling()
        self.save_settings()
        self.announce(f"Font size set to {int(scale * 100)}%")
    
    def toggle_high_contrast(self):
        """Toggle high contrast mode."""
        self.settings['high_contrast'] = not self.settings.get('high_contrast', False)
        
        if self.settings['high_contrast']:
            self._apply_high_contrast()
            self.announce("High contrast mode enabled")
        else:
            # Reset to normal colors (would need theme manager integration)
            self.announce("High contrast mode disabled")
        
        self.save_settings()
    
    def set_color_blind_mode(self, mode: Optional[str]):
        """Set color blind friendly mode."""
        valid_modes = [None, 'deuteranopia', 'protanopia', 'tritanopia']
        if mode not in valid_modes:
            return
        
        self.settings['color_blind_mode'] = mode
        if mode:
            self._apply_color_blind_mode()
            self.announce(f"Color blind mode set to {mode}")
        else:
            self.announce("Color blind mode disabled")
        
        self.save_settings()
    
    def toggle_sound_cues(self):
        """Toggle sound cues."""
        self.settings['sound_enabled'] = not self.settings.get('sound_enabled', False)
        
        if self.settings['sound_enabled']:
            try:
                from .sound_cues import SoundManager
                self.sound_manager = SoundManager()
                self.announce("Sound cues enabled")
            except ImportError:
                self.settings['sound_enabled'] = False
                self.announce("Sound cues not available")
        else:
            self.sound_manager = None
            self.announce("Sound cues disabled")
        
        self.save_settings()
    
    def get_widget_info(self, widget: tk.Widget) -> Dict[str, Any]:
        """Get accessibility information for a widget."""
        widget_id = id(widget)
        if widget_id in self.accessible_widgets:
            return self.accessible_widgets[widget_id].get_accessibility_info()
        
        # Return basic info for non-wrapped widgets
        return {
            'widget_class': widget.__class__.__name__,
            'name': getattr(widget, 'text', ''),
            'state': str(getattr(widget, 'state', 'unknown'))
        }
    
    # Event handler methods
    def _show_accessibility_help(self, event=None):
        """Show accessibility help dialog."""
        help_text = """
ACCESSIBILITY FEATURES:

Font Scaling:
- Ctrl+Plus: Increase font size
- Ctrl+Minus: Decrease font size
- Ctrl+0: Reset font size

Navigation:
- Tab/Shift+Tab: Navigate between elements
- Arrow keys: Navigate within lists/grids
- Enter/Space: Activate buttons/checkboxes
- Escape: Cancel/close dialogs

Screen Reader:
- Ctrl+Alt+R: Read current widget
- Ctrl+Alt+N: Read next widget
- Ctrl+Alt+P: Read previous widget

Accessibility Settings:
- Ctrl+Alt+S: Open accessibility settings
- Ctrl+Alt+H: Toggle high contrast
- F1 on any widget: Show help tooltip

All features can be customized in the accessibility settings panel.
        """.strip()
        
        self._show_info_dialog("Accessibility Help", help_text)
    
    def _show_accessibility_settings(self, event=None):
        """Show accessibility settings panel."""
        try:
            from ..components.accessibility_panel import AccessibilityPanel
            panel = AccessibilityPanel(self.root, self)
            panel.show()
        except ImportError:
            self.announce("Accessibility settings panel not available")
    
    def _toggle_high_contrast(self, event=None):
        """Toggle high contrast mode via keyboard shortcut."""
        self.toggle_high_contrast()
    
    def _read_current_widget(self, event=None):
        """Read information about the currently focused widget."""
        focused = self.root.focus_get()
        if focused:
            info = self.get_widget_info(focused)
            message = f"{info.get('name', info['widget_class'])}"
            if info.get('description'):
                message += f", {info['description']}"
            self.announce(message, "assertive")
    
    def _read_next_widget(self, event=None):
        """Move focus to and read next widget."""
        focused = self.root.focus_get()
        if focused:
            next_widget = focused.tk_focusNext()
            if next_widget:
                next_widget.focus_set()
                self._read_current_widget()
    
    def _read_previous_widget(self, event=None):
        """Move focus to and read previous widget."""
        focused = self.root.focus_get()
        if focused:
            prev_widget = focused.tk_focusPrev()
            if prev_widget:
                prev_widget.focus_set()
                self._read_current_widget()
    
    def _show_info_dialog(self, title: str, message: str):
        """Show accessible information dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Make dialog accessible
        acc_dialog = self.make_accessible(dialog, name=title, role="dialog")
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 300
        y = (dialog.winfo_screenheight() // 2) - 200
        dialog.geometry(f"+{x}+{y}")
        
        # Content
        text_frame = ttk.Frame(dialog, padding="20")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            padx=10,
            pady=10,
            state=tk.DISABLED
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Make text widget accessible
        acc_text = self.make_accessible(
            text_widget,
            name="Help content",
            role="document",
            description="Use arrow keys to scroll"
        )
        
        # Insert content
        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, message)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        button_frame = ttk.Frame(text_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        close_btn = ttk.Button(
            button_frame,
            text="Close",
            command=dialog.destroy
        )
        close_btn.pack(side=tk.RIGHT)
        
        # Make close button accessible
        acc_btn = self.make_accessible(
            close_btn,
            name="Close dialog",
            description="Press Enter to close this help dialog"
        )
        
        # Set focus and announce
        close_btn.focus_set()
        self.announce(f"{title} dialog opened. Press Tab to navigate.")
        
        # Escape key to close
        dialog.bind('<Escape>', lambda e: dialog.destroy())