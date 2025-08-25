"""
Accessibility settings panel for the Unsplash Image Search application.
Provides comprehensive accessibility configuration options.
"""

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from typing import Dict, Any, Optional, Callable
import json
from pathlib import Path


class AccessibilityPanel:
    """
    Comprehensive accessibility settings panel.
    Allows users to configure all accessibility features.
    """
    
    def __init__(self, parent: tk.Widget, accessibility_manager):
        self.parent = parent
        self.accessibility_manager = accessibility_manager
        self.window = None
        self.settings = accessibility_manager.settings.copy()
        
        # UI variables
        self.font_scale_var = tk.DoubleVar(value=self.settings.get('font_scale', 1.0))
        self.high_contrast_var = tk.BooleanVar(value=self.settings.get('high_contrast', False))
        self.sound_enabled_var = tk.BooleanVar(value=self.settings.get('sound_enabled', False))
        self.focus_indicators_var = tk.BooleanVar(value=self.settings.get('focus_indicators', True))
        self.keyboard_nav_var = tk.BooleanVar(value=self.settings.get('keyboard_navigation', True))
        self.screen_reader_var = tk.BooleanVar(value=self.settings.get('screen_reader_enabled', True))
        self.reduced_motion_var = tk.BooleanVar(value=self.settings.get('reduced_motion', False))
        
        self.color_blind_mode_var = tk.StringVar(value=self.settings.get('color_blind_mode', 'None'))
        self.announcement_verbosity_var = tk.StringVar(value=self.settings.get('announcement_verbosity', 'normal'))
        
        # Shortcuts variables
        self.custom_shortcuts = self.settings.get('custom_shortcuts', {}).copy()
    
    def show(self):
        """Show the accessibility settings panel."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_set()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("Accessibility Settings")
        self.window.geometry("700x800")
        self.window.resizable(True, True)
        self.window.transient(self.parent)
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - 350
        y = (self.window.winfo_screenheight() // 2) - 400
        self.window.geometry(f"+{x}+{y}")
        
        # Make window accessible
        if hasattr(self.accessibility_manager, 'make_accessible'):
            self.accessibility_manager.make_accessible(
                self.window,
                name="Accessibility Settings",
                role="dialog",
                description="Configure accessibility features for the application"
            )
        
        self._create_ui()
        
        # Bind close event
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Focus first control
        self.window.after(100, self._set_initial_focus)
    
    def _create_ui(self):
        """Create the settings UI."""
        # Main container with scrolling
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self._create_display_tab(notebook)
        self._create_navigation_tab(notebook)
        self._create_audio_tab(notebook)
        self._create_shortcuts_tab(notebook)
        self._create_advanced_tab(notebook)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Buttons
        ttk.Button(
            button_frame,
            text="Apply",
            command=self._apply_settings
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="OK",
            command=self._ok_clicked
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._cancel_clicked
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Reset to Defaults",
            command=self._reset_defaults
        ).pack(side=tk.LEFT)
    
    def _create_display_tab(self, notebook):
        """Create display accessibility settings tab."""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Display")
        
        # Font scaling section
        font_frame = ttk.LabelFrame(frame, text="Font Size", padding="10")
        font_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(font_frame, text="Font Scale:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        font_scale_frame = ttk.Frame(font_frame)
        font_scale_frame.grid(row=1, column=0, sticky=tk.W+tk.E, pady=5)
        font_frame.columnconfigure(0, weight=1)
        
        # Font scale slider
        self.font_scale_slider = tk.Scale(
            font_scale_frame,
            from_=0.5,
            to=2.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.font_scale_var,
            command=self._on_font_scale_change
        )
        self.font_scale_slider.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        # Font scale label
        self.font_scale_label = ttk.Label(font_scale_frame, text="100%")
        self.font_scale_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Font scale buttons
        font_btn_frame = ttk.Frame(font_frame)
        font_btn_frame.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        ttk.Button(font_btn_frame, text="50%", command=lambda: self._set_font_scale(0.5)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(font_btn_frame, text="75%", command=lambda: self._set_font_scale(0.75)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(font_btn_frame, text="100%", command=lambda: self._set_font_scale(1.0)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(font_btn_frame, text="125%", command=lambda: self._set_font_scale(1.25)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(font_btn_frame, text="150%", command=lambda: self._set_font_scale(1.5)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(font_btn_frame, text="200%", command=lambda: self._set_font_scale(2.0)).pack(side=tk.LEFT, padx=(0, 5))
        
        # High contrast section
        contrast_frame = ttk.LabelFrame(frame, text="High Contrast", padding="10")
        contrast_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(
            contrast_frame,
            text="Enable high contrast mode",
            variable=self.high_contrast_var,
            command=self._on_high_contrast_change
        ).pack(anchor=tk.W)
        
        # High contrast theme selection
        self.hc_theme_frame = ttk.Frame(contrast_frame)
        self.hc_theme_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(self.hc_theme_frame, text="High Contrast Theme:").pack(anchor=tk.W)
        
        self.hc_theme_var = tk.StringVar(value="high_contrast_dark")
        hc_themes = [
            ("Dark theme (white on black)", "high_contrast_dark"),
            ("Light theme (black on white)", "high_contrast_light"),
            ("Yellow on black", "yellow_on_black"),
            ("White on black", "white_on_black")
        ]
        
        for text, value in hc_themes:
            ttk.Radiobutton(
                self.hc_theme_frame,
                text=text,
                variable=self.hc_theme_var,
                value=value
            ).pack(anchor=tk.W, padx=(20, 0))
        
        # Color blind section
        colorblind_frame = ttk.LabelFrame(frame, text="Color Blind Accessibility", padding="10")
        colorblind_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(colorblind_frame, text="Color blind mode:").pack(anchor=tk.W)
        
        cb_modes = [
            ("None (use normal colors)", "None"),
            ("Deuteranopia (green-blind)", "deuteranopia"),
            ("Protanopia (red-blind)", "protanopia"),
            ("Tritanopia (blue-blind)", "tritanopia")
        ]
        
        for text, value in cb_modes:
            ttk.Radiobutton(
                colorblind_frame,
                text=text,
                variable=self.color_blind_mode_var,
                value=value
            ).pack(anchor=tk.W)
        
        # Motion settings
        motion_frame = ttk.LabelFrame(frame, text="Motion & Animation", padding="10")
        motion_frame.pack(fill=tk.X)
        
        ttk.Checkbutton(
            motion_frame,
            text="Reduce motion and animations",
            variable=self.reduced_motion_var
        ).pack(anchor=tk.W)
        
        ttk.Label(
            motion_frame,
            text="Reduces animated transitions and effects for users sensitive to motion.",
            font=("Arial", 8),
            foreground="gray"
        ).pack(anchor=tk.W, padx=(20, 0))
        
        # Update initial states
        self._on_font_scale_change()
        self._on_high_contrast_change()
    
    def _create_navigation_tab(self, notebook):
        """Create navigation accessibility settings tab."""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Navigation")
        
        # Keyboard navigation
        kb_frame = ttk.LabelFrame(frame, text="Keyboard Navigation", padding="10")
        kb_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(
            kb_frame,
            text="Enable keyboard navigation",
            variable=self.keyboard_nav_var
        ).pack(anchor=tk.W)
        
        ttk.Label(
            kb_frame,
            text="Allows navigation using Tab, Arrow keys, Enter, and Space.",
            font=("Arial", 8),
            foreground="gray"
        ).pack(anchor=tk.W, padx=(20, 0))
        
        # Focus indicators
        focus_frame = ttk.LabelFrame(frame, text="Focus Indicators", padding="10")
        focus_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(
            focus_frame,
            text="Show focus indicators",
            variable=self.focus_indicators_var
        ).pack(anchor=tk.W)
        
        ttk.Label(
            focus_frame,
            text="Highlights the currently focused element with a visible border.",
            font=("Arial", 8),
            foreground="gray"
        ).pack(anchor=tk.W, padx=(20, 0))
        
        # Focus ring customization
        ring_frame = ttk.Frame(focus_frame)
        ring_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(ring_frame, text="Focus ring width:").grid(row=0, column=0, sticky=tk.W)
        self.focus_width_var = tk.IntVar(value=3)
        ttk.Scale(
            ring_frame,
            from_=1,
            to=5,
            variable=self.focus_width_var,
            orient=tk.HORIZONTAL
        ).grid(row=0, column=1, sticky=tk.W+tk.E, padx=(10, 0))
        ring_frame.columnconfigure(1, weight=1)
        
        ttk.Label(ring_frame, text="Focus ring color:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.focus_color_var = tk.StringVar(value="#0078D4")
        color_frame = ttk.Frame(ring_frame)
        color_frame.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        self.color_preview = tk.Label(
            color_frame,
            text="  ",
            bg=self.focus_color_var.get(),
            relief="solid",
            borderwidth=1
        )
        self.color_preview.pack(side=tk.LEFT)
        
        ttk.Button(
            color_frame,
            text="Choose Color",
            command=self._choose_focus_color
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Tab order management
        tab_order_frame = ttk.LabelFrame(frame, text="Tab Order", padding="10")
        tab_order_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            tab_order_frame,
            text="Current tab order (first to last):"
        ).pack(anchor=tk.W)
        
        # Tab order listbox
        listbox_frame = ttk.Frame(tab_order_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self.tab_order_listbox = tk.Listbox(listbox_frame, height=8)
        self.tab_order_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.tab_order_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tab_order_listbox.config(yscrollcommand=scrollbar.set)
        
        # Tab order buttons
        tab_btn_frame = ttk.Frame(tab_order_frame)
        tab_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(tab_btn_frame, text="Move Up", command=self._move_tab_up).pack(side=tk.LEFT)
        ttk.Button(tab_btn_frame, text="Move Down", command=self._move_tab_down).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(tab_btn_frame, text="Refresh", command=self._refresh_tab_order).pack(side=tk.RIGHT)
        
        # Load current tab order
        self._refresh_tab_order()
    
    def _create_audio_tab(self, notebook):
        """Create audio accessibility settings tab."""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Audio")
        
        # Sound cues section
        sound_frame = ttk.LabelFrame(frame, text="Sound Cues", padding="10")
        sound_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(
            sound_frame,
            text="Enable sound cues",
            variable=self.sound_enabled_var,
            command=self._test_sound
        ).pack(anchor=tk.W)
        
        ttk.Label(
            sound_frame,
            text="Plays audio feedback for actions and notifications.",
            font=("Arial", 8),
            foreground="gray"
        ).pack(anchor=tk.W, padx=(20, 0))
        
        ttk.Button(
            sound_frame,
            text="Test Sound",
            command=self._test_sound
        ).pack(anchor=tk.W, pady=(10, 0))
        
        # Screen reader section
        sr_frame = ttk.LabelFrame(frame, text="Screen Reader", padding="10")
        sr_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(
            sr_frame,
            text="Enable screen reader support",
            variable=self.screen_reader_var
        ).pack(anchor=tk.W)
        
        ttk.Label(
            sr_frame,
            text="Provides text-to-speech announcements and screen reader integration.",
            font=("Arial", 8),
            foreground="gray"
        ).pack(anchor=tk.W, padx=(20, 0))
        
        # Announcement verbosity
        ttk.Label(sr_frame, text="Announcement level:").pack(anchor=tk.W, pady=(10, 0))
        
        verbosity_levels = [
            ("Quiet (minimal announcements)", "quiet"),
            ("Normal (standard announcements)", "normal"),
            ("Verbose (detailed announcements)", "verbose")
        ]
        
        for text, value in verbosity_levels:
            ttk.Radiobutton(
                sr_frame,
                text=text,
                variable=self.announcement_verbosity_var,
                value=value
            ).pack(anchor=tk.W, padx=(20, 0))
        
        # TTS testing
        tts_frame = ttk.LabelFrame(frame, text="Text-to-Speech Test", padding="10")
        tts_frame.pack(fill=tk.X)
        
        self.test_text_var = tk.StringVar(value="This is a test of the text-to-speech system.")
        ttk.Entry(
            tts_frame,
            textvariable=self.test_text_var,
            width=50
        ).pack(fill=tk.X, pady=(0, 10))
        
        tts_btn_frame = ttk.Frame(tts_frame)
        tts_btn_frame.pack(fill=tk.X)
        
        ttk.Button(
            tts_btn_frame,
            text="Test Speech",
            command=self._test_speech
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            tts_btn_frame,
            text="Stop Speech",
            command=self._stop_speech
        ).pack(side=tk.LEFT, padx=(5, 0))
    
    def _create_shortcuts_tab(self, notebook):
        """Create keyboard shortcuts customization tab."""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Shortcuts")
        
        # Shortcuts explanation
        ttk.Label(
            frame,
            text="Customize keyboard shortcuts for accessibility features:",
            font=("Arial", 10, "bold")
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Shortcuts frame
        shortcuts_frame = ttk.LabelFrame(frame, text="Accessibility Shortcuts", padding="10")
        shortcuts_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for shortcuts
        columns = ('Action', 'Shortcut', 'Description')
        self.shortcuts_tree = ttk.Treeview(shortcuts_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.shortcuts_tree.heading(col, text=col)
            if col == 'Action':
                self.shortcuts_tree.column(col, width=200)
            elif col == 'Shortcut':
                self.shortcuts_tree.column(col, width=150)
            else:
                self.shortcuts_tree.column(col, width=300)
        
        self.shortcuts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for treeview
        shortcuts_scroll = ttk.Scrollbar(shortcuts_frame, orient="vertical", command=self.shortcuts_tree.yview)
        shortcuts_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.shortcuts_tree.config(yscrollcommand=shortcuts_scroll.set)
        
        # Populate shortcuts
        self._populate_shortcuts()
        
        # Shortcut buttons
        shortcut_btn_frame = ttk.Frame(frame)
        shortcut_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            shortcut_btn_frame,
            text="Edit Shortcut",
            command=self._edit_shortcut
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            shortcut_btn_frame,
            text="Reset to Default",
            command=self._reset_shortcut
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Button(
            shortcut_btn_frame,
            text="Reset All",
            command=self._reset_all_shortcuts
        ).pack(side=tk.RIGHT)
    
    def _create_advanced_tab(self, notebook):
        """Create advanced accessibility settings tab."""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Advanced")
        
        # System integration
        system_frame = ttk.LabelFrame(frame, text="System Integration", padding="10")
        system_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Detect system settings
        ttk.Button(
            system_frame,
            text="Detect System Accessibility Settings",
            command=self._detect_system_settings
        ).pack(anchor=tk.W)
        
        ttk.Label(
            system_frame,
            text="Automatically configure based on Windows accessibility settings.",
            font=("Arial", 8),
            foreground="gray"
        ).pack(anchor=tk.W, padx=(20, 0))
        
        # Export/Import settings
        io_frame = ttk.LabelFrame(frame, text="Settings Management", padding="10")
        io_frame.pack(fill=tk.X, pady=(0, 10))
        
        io_btn_frame = ttk.Frame(io_frame)
        io_btn_frame.pack(anchor=tk.W)
        
        ttk.Button(
            io_btn_frame,
            text="Export Settings",
            command=self._export_settings
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            io_btn_frame,
            text="Import Settings",
            command=self._import_settings
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Diagnostics
        diag_frame = ttk.LabelFrame(frame, text="Diagnostics", padding="10")
        diag_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(
            diag_frame,
            text="Run Accessibility Check",
            command=self._run_accessibility_check
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Diagnostics text area
        self.diag_text = tk.Text(diag_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.diag_text.pack(fill=tk.BOTH, expand=True)
        
        diag_scroll = ttk.Scrollbar(diag_frame, orient="vertical", command=self.diag_text.yview)
        diag_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.diag_text.config(yscrollcommand=diag_scroll.set)
    
    def _on_font_scale_change(self, value=None):
        """Handle font scale slider change."""
        scale = self.font_scale_var.get()
        percentage = int(scale * 100)
        self.font_scale_label.config(text=f"{percentage}%")
    
    def _set_font_scale(self, scale: float):
        """Set font scale to specific value."""
        self.font_scale_var.set(scale)
        self._on_font_scale_change()
    
    def _on_high_contrast_change(self):
        """Handle high contrast checkbox change."""
        enabled = self.high_contrast_var.get()
        # Enable/disable theme selection
        for widget in self.hc_theme_frame.winfo_children():
            if isinstance(widget, (ttk.Radiobutton, ttk.Label)):
                if enabled:
                    widget.configure(state='normal')
                else:
                    widget.configure(state='disabled')
    
    def _choose_focus_color(self):
        """Open color chooser for focus ring color."""
        color = colorchooser.askcolor(
            color=self.focus_color_var.get(),
            title="Choose Focus Ring Color"
        )[1]
        
        if color:
            self.focus_color_var.set(color)
            self.color_preview.config(bg=color)
    
    def _refresh_tab_order(self):
        """Refresh the tab order display."""
        self.tab_order_listbox.delete(0, tk.END)
        
        if hasattr(self.accessibility_manager, 'focus_manager'):
            focus_order = self.accessibility_manager.focus_manager.get_focus_order()
            for i, widget_name in enumerate(focus_order):
                self.tab_order_listbox.insert(tk.END, f"{i+1}. {widget_name}")
    
    def _move_tab_up(self):
        """Move selected tab order item up."""
        selection = self.tab_order_listbox.curselection()
        if selection and selection[0] > 0:
            # Implementation would modify focus manager tab order
            messagebox.showinfo("Info", "Tab order modification not yet implemented")
    
    def _move_tab_down(self):
        """Move selected tab order item down."""
        selection = self.tab_order_listbox.curselection()
        if selection and selection[0] < self.tab_order_listbox.size() - 1:
            # Implementation would modify focus manager tab order
            messagebox.showinfo("Info", "Tab order modification not yet implemented")
    
    def _test_sound(self):
        """Test sound cues."""
        if self.sound_enabled_var.get():
            try:
                # Test sound through accessibility manager
                if hasattr(self.accessibility_manager, 'sound_manager'):
                    self.accessibility_manager.sound_manager.play_notification()
                else:
                    messagebox.showinfo("Sound Test", "Sound cues would play here")
            except Exception as e:
                messagebox.showerror("Sound Error", f"Sound test failed: {e}")
        else:
            messagebox.showinfo("Sound Disabled", "Enable sound cues to test")
    
    def _test_speech(self):
        """Test text-to-speech."""
        text = self.test_text_var.get()
        if text and self.screen_reader_var.get():
            try:
                self.accessibility_manager.announce(text, "assertive")
            except Exception as e:
                messagebox.showerror("Speech Error", f"Speech test failed: {e}")
        else:
            messagebox.showinfo("Speech Test", "Enter text and enable screen reader to test")
    
    def _stop_speech(self):
        """Stop current speech."""
        try:
            if hasattr(self.accessibility_manager, 'screen_reader'):
                self.accessibility_manager.screen_reader.stop_speech()
        except Exception as e:
            print(f"Stop speech error: {e}")
    
    def _populate_shortcuts(self):
        """Populate the shortcuts treeview."""
        # Default shortcuts
        default_shortcuts = {
            'toggle_high_contrast': {
                'action': 'Toggle High Contrast',
                'shortcut': 'Ctrl+Alt+H',
                'description': 'Switch between high contrast and normal themes'
            },
            'increase_font': {
                'action': 'Increase Font Size',
                'shortcut': 'Ctrl+Plus',
                'description': 'Increase font size by 10%'
            },
            'decrease_font': {
                'action': 'Decrease Font Size',
                'shortcut': 'Ctrl+Minus',
                'description': 'Decrease font size by 10%'
            },
            'reset_font': {
                'action': 'Reset Font Size',
                'shortcut': 'Ctrl+0',
                'description': 'Reset font size to 100%'
            },
            'accessibility_help': {
                'action': 'Accessibility Help',
                'shortcut': 'Ctrl+Alt+A',
                'description': 'Show accessibility help dialog'
            },
            'read_current': {
                'action': 'Read Current Widget',
                'shortcut': 'Ctrl+Alt+R',
                'description': 'Read information about focused widget'
            },
            'accessibility_settings': {
                'action': 'Accessibility Settings',
                'shortcut': 'Ctrl+Alt+S',
                'description': 'Open accessibility settings panel'
            }
        }
        
        # Clear existing items
        for item in self.shortcuts_tree.get_children():
            self.shortcuts_tree.delete(item)
        
        # Populate with shortcuts
        for key, shortcut_info in default_shortcuts.items():
            # Use custom shortcut if defined
            shortcut = self.custom_shortcuts.get(key, shortcut_info['shortcut'])
            
            self.shortcuts_tree.insert('', tk.END, values=(
                shortcut_info['action'],
                shortcut,
                shortcut_info['description']
            ))
    
    def _edit_shortcut(self):
        """Edit selected shortcut."""
        selection = self.shortcuts_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a shortcut to edit")
            return
        
        # Implementation would open shortcut editor dialog
        messagebox.showinfo("Edit Shortcut", "Shortcut editing not yet implemented")
    
    def _reset_shortcut(self):
        """Reset selected shortcut to default."""
        selection = self.shortcuts_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a shortcut to reset")
            return
        
        # Implementation would reset specific shortcut
        messagebox.showinfo("Reset Shortcut", "Shortcut reset not yet implemented")
    
    def _reset_all_shortcuts(self):
        """Reset all shortcuts to defaults."""
        if messagebox.askyesno("Reset All Shortcuts", "Reset all shortcuts to default values?"):
            self.custom_shortcuts.clear()
            self._populate_shortcuts()
    
    def _detect_system_settings(self):
        """Detect and apply system accessibility settings."""
        try:
            import platform
            system = platform.system()
            
            detected_settings = {}
            
            if system == "Windows":
                # Windows accessibility detection
                detected_settings = self._detect_windows_settings()
            elif system == "Darwin":
                # macOS accessibility detection
                detected_settings = self._detect_macos_settings()
            elif system == "Linux":
                # Linux accessibility detection
                detected_settings = self._detect_linux_settings()
            
            if detected_settings:
                # Apply detected settings
                for key, value in detected_settings.items():
                    if hasattr(self, f"{key}_var"):
                        getattr(self, f"{key}_var").set(value)
                
                messagebox.showinfo(
                    "System Settings Detected",
                    f"Applied {len(detected_settings)} accessibility settings from system"
                )
            else:
                messagebox.showinfo(
                    "No Settings Detected",
                    "No system accessibility settings detected or supported on this platform"
                )
        
        except Exception as e:
            messagebox.showerror("Detection Error", f"Failed to detect system settings: {e}")
    
    def _detect_windows_settings(self) -> Dict[str, Any]:
        """Detect Windows accessibility settings."""
        settings = {}
        try:
            import winreg
            
            # Check for high contrast
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Control Panel\Accessibility\HighContrast") as key:
                flags = winreg.QueryValueEx(key, "Flags")[0]
                if flags & 1:  # HCF_HIGHCONTRASTON
                    settings['high_contrast'] = True
        except:
            pass
        
        return settings
    
    def _detect_macos_settings(self) -> Dict[str, Any]:
        """Detect macOS accessibility settings."""
        settings = {}
        try:
            import subprocess
            
            # Check for increased contrast
            result = subprocess.run(
                ['defaults', 'read', 'com.apple.universalaccess', 'increaseContrast'],
                capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip() == '1':
                settings['high_contrast'] = True
        except:
            pass
        
        return settings
    
    def _detect_linux_settings(self) -> Dict[str, Any]:
        """Detect Linux accessibility settings."""
        settings = {}
        # Linux accessibility detection would go here
        # This is more complex due to variety of desktop environments
        return settings
    
    def _export_settings(self):
        """Export current accessibility settings to file."""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            title="Export Accessibility Settings",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Gather current settings
                export_data = {
                    'font_scale': self.font_scale_var.get(),
                    'high_contrast': self.high_contrast_var.get(),
                    'color_blind_mode': self.color_blind_mode_var.get(),
                    'sound_enabled': self.sound_enabled_var.get(),
                    'focus_indicators': self.focus_indicators_var.get(),
                    'keyboard_navigation': self.keyboard_nav_var.get(),
                    'screen_reader_enabled': self.screen_reader_var.get(),
                    'reduced_motion': self.reduced_motion_var.get(),
                    'announcement_verbosity': self.announcement_verbosity_var.get(),
                    'custom_shortcuts': self.custom_shortcuts,
                    'focus_ring_width': self.focus_width_var.get(),
                    'focus_ring_color': self.focus_color_var.get(),
                    'export_version': '1.0',
                    'export_timestamp': str(datetime.now())
                }
                
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                messagebox.showinfo("Export Successful", f"Settings exported to {filename}")
            
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export settings: {e}")
    
    def _import_settings(self):
        """Import accessibility settings from file."""
        from tkinter import filedialog
        
        filename = filedialog.askopenfilename(
            title="Import Accessibility Settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    import_data = json.load(f)
                
                # Apply imported settings
                if 'font_scale' in import_data:
                    self.font_scale_var.set(import_data['font_scale'])
                if 'high_contrast' in import_data:
                    self.high_contrast_var.set(import_data['high_contrast'])
                if 'color_blind_mode' in import_data:
                    self.color_blind_mode_var.set(import_data['color_blind_mode'])
                if 'sound_enabled' in import_data:
                    self.sound_enabled_var.set(import_data['sound_enabled'])
                if 'focus_indicators' in import_data:
                    self.focus_indicators_var.set(import_data['focus_indicators'])
                if 'keyboard_navigation' in import_data:
                    self.keyboard_nav_var.set(import_data['keyboard_navigation'])
                if 'screen_reader_enabled' in import_data:
                    self.screen_reader_var.set(import_data['screen_reader_enabled'])
                if 'reduced_motion' in import_data:
                    self.reduced_motion_var.set(import_data['reduced_motion'])
                if 'announcement_verbosity' in import_data:
                    self.announcement_verbosity_var.set(import_data['announcement_verbosity'])
                if 'custom_shortcuts' in import_data:
                    self.custom_shortcuts.update(import_data['custom_shortcuts'])
                    self._populate_shortcuts()
                
                messagebox.showinfo("Import Successful", "Settings imported successfully")
            
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import settings: {e}")
    
    def _run_accessibility_check(self):
        """Run comprehensive accessibility diagnostics."""
        self.diag_text.config(state=tk.NORMAL)
        self.diag_text.delete(1.0, tk.END)
        
        # Run diagnostics
        diagnostics = []
        
        # Check screen reader availability
        try:
            from ..accessibility.screen_reader import ScreenReaderSupport
            sr = ScreenReaderSupport()
            if sr.is_available():
                diagnostics.append("✓ Screen reader support available")
                if sr.screen_reader_detected:
                    diagnostics.append("✓ System screen reader detected")
                else:
                    diagnostics.append("⚠ No system screen reader detected")
                if sr.tts_available:
                    diagnostics.append("✓ Text-to-speech available")
                else:
                    diagnostics.append("✗ Text-to-speech not available")
            else:
                diagnostics.append("✗ Screen reader support not available")
        except Exception as e:
            diagnostics.append(f"✗ Screen reader check failed: {e}")
        
        # Check focus manager
        if hasattr(self.accessibility_manager, 'focus_manager'):
            fm = self.accessibility_manager.focus_manager
            issues = fm.validate_tab_order()
            if not issues:
                diagnostics.append("✓ Focus management working correctly")
            else:
                diagnostics.append(f"⚠ Focus issues found: {len(issues)}")
                for issue in issues[:3]:  # Show first 3 issues
                    diagnostics.append(f"  - {issue}")
        else:
            diagnostics.append("✗ Focus manager not initialized")
        
        # Check color accessibility
        try:
            from ..accessibility.themes import AccessibilityThemeManager
            theme_mgr = AccessibilityThemeManager()
            colors = theme_mgr.get_current_colors()
            
            # Test common color combinations
            fg_bg_ratio = theme_mgr.test_color_accessibility(colors['fg'], colors['bg'])
            if fg_bg_ratio['wcag_aa_compliant']:
                diagnostics.append("✓ Text colors meet WCAG AA standards")
            else:
                diagnostics.append(f"✗ Text contrast ratio: {fg_bg_ratio['contrast_ratio']} (needs 4.5+)")
            
        except Exception as e:
            diagnostics.append(f"⚠ Color accessibility check failed: {e}")
        
        # Check system integration
        import platform
        system = platform.system()
        diagnostics.append(f"ℹ Running on {system} {platform.release()}")
        
        # Display results
        result_text = "ACCESSIBILITY DIAGNOSTICS\n" + "="*50 + "\n\n"
        result_text += "\n".join(diagnostics)
        result_text += "\n\n" + "="*50
        result_text += "\nDiagnostics completed. ✓=Good, ⚠=Warning, ✗=Issue, ℹ=Info"
        
        self.diag_text.insert(tk.END, result_text)
        self.diag_text.config(state=tk.DISABLED)
    
    def _apply_settings(self):
        """Apply current settings."""
        # Update settings dictionary
        self.settings.update({
            'font_scale': self.font_scale_var.get(),
            'high_contrast': self.high_contrast_var.get(),
            'color_blind_mode': self.color_blind_mode_var.get() if self.color_blind_mode_var.get() != 'None' else None,
            'sound_enabled': self.sound_enabled_var.get(),
            'focus_indicators': self.focus_indicators_var.get(),
            'keyboard_navigation': self.keyboard_nav_var.get(),
            'screen_reader_enabled': self.screen_reader_var.get(),
            'reduced_motion': self.reduced_motion_var.get(),
            'announcement_verbosity': self.announcement_verbosity_var.get(),
            'custom_shortcuts': self.custom_shortcuts
        })
        
        # Apply through accessibility manager
        self.accessibility_manager.settings.update(self.settings)
        
        # Apply font scaling
        if hasattr(self.accessibility_manager, 'set_font_scale'):
            self.accessibility_manager.set_font_scale(self.font_scale_var.get())
        
        # Apply high contrast
        if hasattr(self.accessibility_manager, 'toggle_high_contrast'):
            current_hc = self.accessibility_manager.settings.get('high_contrast', False)
            desired_hc = self.high_contrast_var.get()
            if current_hc != desired_hc:
                self.accessibility_manager.toggle_high_contrast()
        
        # Apply color blind mode
        if hasattr(self.accessibility_manager, 'set_color_blind_mode'):
            cb_mode = self.color_blind_mode_var.get() if self.color_blind_mode_var.get() != 'None' else None
            self.accessibility_manager.set_color_blind_mode(cb_mode)
        
        # Apply sound settings
        if hasattr(self.accessibility_manager, 'toggle_sound_cues'):
            current_sound = self.accessibility_manager.settings.get('sound_enabled', False)
            desired_sound = self.sound_enabled_var.get()
            if current_sound != desired_sound:
                self.accessibility_manager.toggle_sound_cues()
        
        # Save settings
        self.accessibility_manager.save_settings()
        
        messagebox.showinfo("Settings Applied", "Accessibility settings have been applied")
    
    def _ok_clicked(self):
        """Handle OK button click."""
        self._apply_settings()
        self._on_close()
    
    def _cancel_clicked(self):
        """Handle Cancel button click."""
        self._on_close()
    
    def _reset_defaults(self):
        """Reset all settings to defaults."""
        if messagebox.askyesno("Reset to Defaults", "Reset all accessibility settings to default values?"):
            # Reset all variables to defaults
            self.font_scale_var.set(1.0)
            self.high_contrast_var.set(False)
            self.sound_enabled_var.set(False)
            self.focus_indicators_var.set(True)
            self.keyboard_nav_var.set(True)
            self.screen_reader_var.set(True)
            self.reduced_motion_var.set(False)
            self.color_blind_mode_var.set('None')
            self.announcement_verbosity_var.set('normal')
            self.custom_shortcuts.clear()
            
            # Update UI
            self._on_font_scale_change()
            self._on_high_contrast_change()
            self._populate_shortcuts()
    
    def _set_initial_focus(self):
        """Set initial focus to first control."""
        # Focus the font scale slider as the first interactive element
        if hasattr(self, 'font_scale_slider'):
            self.font_scale_slider.focus_set()
    
    def _on_close(self):
        """Handle window close event."""
        if self.window:
            self.window.destroy()
            self.window = None