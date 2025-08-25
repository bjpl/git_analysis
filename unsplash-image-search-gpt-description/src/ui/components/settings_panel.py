"""
Modern settings panel with organized categories and Material Design styling.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Any, Callable, Optional, List
import json
from pathlib import Path

from ..styles import StyleManager, Easing


class SettingSection(tk.Frame):
    """Individual settings section with category grouping."""
    
    def __init__(self, parent: tk.Widget, title: str, 
                 style_manager: StyleManager = None):
        super().__init__(parent)
        
        self.style_manager = style_manager
        self.title = title
        self.settings_widgets = {}
        
        self._create_section()
        
        if self.style_manager:
            self.style_manager.register_widget(self, classes=['frame', 'settings-section'])
    
    def _create_section(self):
        """Create section header and content area."""
        # Section header
        header_frame = tk.Frame(self)
        header_frame.pack(fill='x', pady=(0, 10))
        
        if self.style_manager:
            header_frame.configure(bg=self.style_manager.theme.colors.background)
            
            title_label = self.style_manager.create_label(
                header_frame, self.title, heading=3
            )
        else:
            title_label = tk.Label(
                header_frame, text=self.title,
                font=('Segoe UI', 12, 'bold')
            )
        
        title_label.pack(side='left')
        
        # Separator line
        separator = tk.Frame(
            header_frame, 
            height=1,
            bg=self.style_manager.theme.colors.outline_variant if self.style_manager else "#e0e0e0"
        )
        separator.pack(side='bottom', fill='x', pady=(5, 0))
        
        # Content area
        self.content_frame = tk.Frame(self)
        self.content_frame.pack(fill='both', expand=True, padx=10)
    
    def add_toggle_setting(self, key: str, label: str, description: str = "",
                          default_value: bool = False, callback: Callable = None):
        """Add toggle (checkbox) setting."""
        setting_frame = tk.Frame(self.content_frame)
        setting_frame.pack(fill='x', pady=5)
        
        # Toggle variable
        var = tk.BooleanVar(value=default_value)
        
        # Checkbox
        checkbox = tk.Checkbutton(
            setting_frame,
            variable=var,
            font=('Segoe UI', 10),
            text=label,
            command=lambda: callback(key, var.get()) if callback else None
        )
        
        if self.style_manager:
            checkbox.configure(
                bg=self.style_manager.theme.colors.background,
                fg=self.style_manager.theme.colors.on_background,
                activebackground=self.style_manager.theme.colors.surface_variant,
                selectcolor=self.style_manager.theme.colors.surface
            )
        
        checkbox.pack(anchor='w')
        
        # Description
        if description:
            desc_label = tk.Label(
                setting_frame,
                text=description,
                font=('Segoe UI', 9),
                wraplength=400,
                justify='left'
            )
            
            if self.style_manager:
                desc_label.configure(
                    bg=self.style_manager.theme.colors.background,
                    fg=self.style_manager.theme.colors.outline
                )
            
            desc_label.pack(anchor='w', padx=(25, 0), pady=(2, 0))
        
        self.settings_widgets[key] = {'widget': checkbox, 'var': var, 'type': 'toggle'}
        return var
    
    def add_choice_setting(self, key: str, label: str, choices: List[str],
                          default_value: str = None, description: str = "",
                          callback: Callable = None):
        """Add dropdown choice setting."""
        setting_frame = tk.Frame(self.content_frame)
        setting_frame.pack(fill='x', pady=5)
        
        # Label
        label_widget = tk.Label(
            setting_frame,
            text=label,
            font=('Segoe UI', 10, 'bold')
        )
        
        if self.style_manager:
            label_widget.configure(
                bg=self.style_manager.theme.colors.background,
                fg=self.style_manager.theme.colors.on_background
            )
        
        label_widget.pack(anchor='w')
        
        # Choice frame
        choice_frame = tk.Frame(setting_frame)
        choice_frame.pack(fill='x', padx=(20, 0), pady=(5, 0))
        
        # Combobox
        var = tk.StringVar(value=default_value or choices[0] if choices else "")
        
        combobox = ttk.Combobox(
            choice_frame,
            textvariable=var,
            values=choices,
            state='readonly',
            width=20
        )
        combobox.pack(side='left')
        
        # Bind change event
        if callback:
            combobox.bind('<<ComboboxSelected>>', 
                         lambda e: callback(key, var.get()))
        
        # Description
        if description:
            desc_label = tk.Label(
                setting_frame,
                text=description,
                font=('Segoe UI', 9),
                wraplength=400,
                justify='left'
            )
            
            if self.style_manager:
                desc_label.configure(
                    bg=self.style_manager.theme.colors.background,
                    fg=self.style_manager.theme.colors.outline
                )
            
            desc_label.pack(anchor='w', padx=(20, 0), pady=(2, 0))
        
        self.settings_widgets[key] = {'widget': combobox, 'var': var, 'type': 'choice'}
        return var
    
    def add_text_setting(self, key: str, label: str, default_value: str = "",
                        description: str = "", callback: Callable = None,
                        password: bool = False):
        """Add text input setting."""
        setting_frame = tk.Frame(self.content_frame)
        setting_frame.pack(fill='x', pady=5)
        
        # Label
        label_widget = tk.Label(
            setting_frame,
            text=label,
            font=('Segoe UI', 10, 'bold')
        )
        
        if self.style_manager:
            label_widget.configure(
                bg=self.style_manager.theme.colors.background,
                fg=self.style_manager.theme.colors.on_background
            )
        
        label_widget.pack(anchor='w')
        
        # Entry frame
        entry_frame = tk.Frame(setting_frame)
        entry_frame.pack(fill='x', padx=(20, 0), pady=(5, 0))
        
        # Entry
        var = tk.StringVar(value=default_value)
        
        if self.style_manager:
            entry = self.style_manager.create_entry(entry_frame, textvariable=var)
        else:
            entry = tk.Entry(entry_frame, textvariable=var)
        
        if password:
            entry.configure(show="*")
        
        entry.pack(fill='x')
        
        # Bind change event
        if callback:
            var.trace('w', lambda *args: callback(key, var.get()))
        
        # Description
        if description:
            desc_label = tk.Label(
                setting_frame,
                text=description,
                font=('Segoe UI', 9),
                wraplength=400,
                justify='left'
            )
            
            if self.style_manager:
                desc_label.configure(
                    bg=self.style_manager.theme.colors.background,
                    fg=self.style_manager.theme.colors.outline
                )
            
            desc_label.pack(anchor='w', padx=(20, 0), pady=(2, 0))
        
        self.settings_widgets[key] = {'widget': entry, 'var': var, 'type': 'text'}
        return var
    
    def add_file_setting(self, key: str, label: str, default_value: str = "",
                        description: str = "", callback: Callable = None,
                        file_types: List[tuple] = None):
        """Add file selection setting."""
        setting_frame = tk.Frame(self.content_frame)
        setting_frame.pack(fill='x', pady=5)
        
        # Label
        label_widget = tk.Label(
            setting_frame,
            text=label,
            font=('Segoe UI', 10, 'bold')
        )
        
        if self.style_manager:
            label_widget.configure(
                bg=self.style_manager.theme.colors.background,
                fg=self.style_manager.theme.colors.on_background
            )
        
        label_widget.pack(anchor='w')
        
        # File frame
        file_frame = tk.Frame(setting_frame)
        file_frame.pack(fill='x', padx=(20, 0), pady=(5, 0))
        
        # Path entry
        var = tk.StringVar(value=default_value)
        
        if self.style_manager:
            entry = self.style_manager.create_entry(file_frame, textvariable=var)
        else:
            entry = tk.Entry(file_frame, textvariable=var)
        
        entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # Browse button
        def browse_file():
            file_types = file_types or [("All files", "*.*")]
            filename = filedialog.askopenfilename(filetypes=file_types)
            if filename:
                var.set(filename)
                if callback:
                    callback(key, filename)
        
        if self.style_manager:
            browse_btn = self.style_manager.create_button(
                file_frame, "Browse", variant='secondary'
            )
        else:
            browse_btn = tk.Button(file_frame, text="Browse")
        
        browse_btn.configure(command=browse_file)
        browse_btn.pack(side='right')
        
        # Description
        if description:
            desc_label = tk.Label(
                setting_frame,
                text=description,
                font=('Segoe UI', 9),
                wraplength=400,
                justify='left'
            )
            
            if self.style_manager:
                desc_label.configure(
                    bg=self.style_manager.theme.colors.background,
                    fg=self.style_manager.theme.colors.outline
                )
            
            desc_label.pack(anchor='w', padx=(20, 0), pady=(2, 0))
        
        self.settings_widgets[key] = {'widget': entry, 'var': var, 'type': 'file'}
        return var
    
    def add_action_setting(self, key: str, label: str, button_text: str,
                          description: str = "", callback: Callable = None,
                          button_variant: str = 'secondary'):
        """Add action button setting."""
        setting_frame = tk.Frame(self.content_frame)
        setting_frame.pack(fill='x', pady=5)
        
        # Label and description in left column
        text_frame = tk.Frame(setting_frame)
        text_frame.pack(side='left', fill='both', expand=True)
        
        label_widget = tk.Label(
            text_frame,
            text=label,
            font=('Segoe UI', 10, 'bold'),
            anchor='w'
        )
        
        if self.style_manager:
            label_widget.configure(
                bg=self.style_manager.theme.colors.background,
                fg=self.style_manager.theme.colors.on_background
            )
        
        label_widget.pack(anchor='w')
        
        if description:
            desc_label = tk.Label(
                text_frame,
                text=description,
                font=('Segoe UI', 9),
                wraplength=300,
                justify='left',
                anchor='w'
            )
            
            if self.style_manager:
                desc_label.configure(
                    bg=self.style_manager.theme.colors.background,
                    fg=self.style_manager.theme.colors.outline
                )
            
            desc_label.pack(anchor='w', pady=(2, 0))
        
        # Button in right column
        if self.style_manager:
            button = self.style_manager.create_button(
                setting_frame, button_text, variant=button_variant
            )
        else:
            button = tk.Button(setting_frame, text=button_text)
        
        button.configure(command=lambda: callback(key) if callback else None)
        button.pack(side='right', padx=(10, 0))
        
        self.settings_widgets[key] = {'widget': button, 'var': None, 'type': 'action'}
        return button
    
    def get_setting_value(self, key: str):
        """Get current value of a setting."""
        if key in self.settings_widgets:
            setting = self.settings_widgets[key]
            if setting['var']:
                return setting['var'].get()
        return None
    
    def set_setting_value(self, key: str, value: Any):
        """Set value of a setting."""
        if key in self.settings_widgets:
            setting = self.settings_widgets[key]
            if setting['var']:
                setting['var'].set(value)


class SettingsPanel(tk.Frame):
    """Main settings panel with organized categories."""
    
    def __init__(self, parent: tk.Widget, style_manager: StyleManager,
                 config_manager: Any = None, on_setting_change: Callable = None):
        super().__init__(parent)
        
        self.style_manager = style_manager
        self.config_manager = config_manager
        self.on_setting_change = on_setting_change
        
        # Settings sections
        self.sections: Dict[str, SettingSection] = {}
        self.settings_data: Dict[str, Any] = {}
        
        self._create_panel()
        self._create_sections()
        self._load_settings()
        
        # Register with style manager
        self.style_manager.register_widget(self, classes=['frame', 'settings-panel'])
    
    def _create_panel(self):
        """Create main panel structure."""
        # Header
        header = tk.Frame(self)
        header.pack(fill='x', padx=20, pady=10)
        
        title_label = self.style_manager.create_label(
            header, "Settings", heading=1
        )
        title_label.pack(side='left')
        
        # Action buttons
        button_frame = tk.Frame(header)
        button_frame.pack(side='right')
        
        self.reset_btn = self.style_manager.create_button(
            button_frame, "Reset to Defaults", variant='text'
        )
        self.reset_btn.configure(command=self._reset_to_defaults)
        self.reset_btn.pack(side='left', padx=(0, 10))
        
        self.save_btn = self.style_manager.create_button(
            button_frame, "Save Settings", variant='primary'
        )
        self.save_btn.configure(command=self._save_settings)
        self.save_btn.pack(side='right')
        
        # Separator
        separator = ttk.Separator(self, orient='horizontal')
        separator.pack(fill='x', padx=20, pady=5)
        
        # Scrollable content
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Apply theme to canvas
        if self.style_manager:
            canvas.configure(bg=self.style_manager.theme.colors.background)
            self.scrollable_frame.configure(bg=self.style_manager.theme.colors.background)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def _create_sections(self):
        """Create settings sections."""
        # General Settings
        general_section = SettingSection(
            self.scrollable_frame, "General", self.style_manager
        )
        general_section.pack(fill='x', padx=20, pady=10)
        self.sections['general'] = general_section
        
        # Theme Settings
        theme_section = SettingSection(
            self.scrollable_frame, "Appearance", self.style_manager
        )
        theme_section.pack(fill='x', padx=20, pady=10)
        self.sections['theme'] = theme_section
        
        # API Settings
        api_section = SettingSection(
            self.scrollable_frame, "API Configuration", self.style_manager
        )
        api_section.pack(fill='x', padx=20, pady=10)
        self.sections['api'] = api_section
        
        # Learning Settings
        learning_section = SettingSection(
            self.scrollable_frame, "Learning & Vocabulary", self.style_manager
        )
        learning_section.pack(fill='x', padx=20, pady=10)
        self.sections['learning'] = learning_section
        
        # Privacy & Data
        privacy_section = SettingSection(
            self.scrollable_frame, "Privacy & Data", self.style_manager
        )
        privacy_section.pack(fill='x', padx=20, pady=10)
        self.sections['privacy'] = privacy_section
        
        # Advanced Settings
        advanced_section = SettingSection(
            self.scrollable_frame, "Advanced", self.style_manager
        )
        advanced_section.pack(fill='x', padx=20, pady=10)
        self.sections['advanced'] = advanced_section
        
        self._populate_sections()
    
    def _populate_sections(self):
        """Populate sections with settings."""
        # General Settings
        general = self.sections['general']
        
        general.add_toggle_setting(
            'auto_save', 'Auto-save vocabulary',
            'Automatically save vocabulary entries as they are created',
            True, self._on_setting_change
        )
        
        general.add_toggle_setting(
            'show_tooltips', 'Show tooltips',
            'Display helpful tooltips when hovering over elements',
            True, self._on_setting_change
        )
        
        general.add_choice_setting(
            'language', 'Interface Language',
            ['English', 'Spanish', 'French', 'German'],
            'English', 'Choose your preferred interface language',
            self._on_setting_change
        )
        
        general.add_choice_setting(
            'startup_behavior', 'On Startup',
            ['Show empty search', 'Restore last session', 'Show onboarding'],
            'Show empty search', 'What to display when the application starts',
            self._on_setting_change
        )
        
        # Theme Settings
        theme = self.sections['theme']
        
        theme.add_choice_setting(
            'theme_mode', 'Theme Mode',
            ['Light', 'Dark', 'System'],
            'Light', 'Choose your preferred color theme',
            self._on_setting_change
        )
        
        theme.add_choice_setting(
            'accent_color', 'Accent Color',
            ['Blue', 'Green', 'Purple', 'Orange', 'Red'],
            'Blue', 'Primary color for buttons and highlights',
            self._on_setting_change
        )
        
        theme.add_toggle_setting(
            'animations_enabled', 'Enable Animations',
            'Smooth transitions and micro-interactions',
            True, self._on_setting_change
        )
        
        theme.add_choice_setting(
            'font_size', 'Font Size',
            ['Small', 'Medium', 'Large', 'Extra Large'],
            'Medium', 'Adjust text size for better readability',
            self._on_setting_change
        )
        
        # API Settings
        api = self.sections['api']
        
        api.add_text_setting(
            'unsplash_api_key', 'Unsplash API Key',
            '', 'Your Unsplash API key for image search',
            self._on_setting_change, password=True
        )
        
        api.add_text_setting(
            'openai_api_key', 'OpenAI API Key',
            '', 'Your OpenAI API key for GPT descriptions',
            self._on_setting_change, password=True
        )
        
        api.add_choice_setting(
            'gpt_model', 'GPT Model',
            ['gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'],
            'gpt-4-turbo', 'Choose the GPT model for descriptions',
            self._on_setting_change
        )
        
        api.add_text_setting(
            'api_timeout', 'API Timeout (seconds)',
            '30', 'Maximum time to wait for API responses',
            self._on_setting_change
        )
        
        # Learning Settings
        learning = self.sections['learning']
        
        learning.add_choice_setting(
            'daily_goal', 'Daily Learning Goal',
            ['5 words', '10 words', '15 words', '20 words', '25 words'],
            '10 words', 'Target number of new vocabulary words per day',
            self._on_setting_change
        )
        
        learning.add_toggle_setting(
            'show_context', 'Show Context in Vocabulary',
            'Include image context when saving vocabulary',
            True, self._on_setting_change
        )
        
        learning.add_toggle_setting(
            'duplicate_detection', 'Prevent Duplicate Words',
            'Skip words that have already been learned',
            True, self._on_setting_change
        )
        
        learning.add_choice_setting(
            'export_format', 'Default Export Format',
            ['Anki', 'CSV', 'Plain Text', 'JSON'],
            'Anki', 'Preferred format when exporting vocabulary',
            self._on_setting_change
        )
        
        # Privacy & Data
        privacy = self.sections['privacy']
        
        privacy.add_file_setting(
            'data_directory', 'Data Directory',
            '', 'Where to store vocabulary and session data',
            self._on_setting_change
        )
        
        privacy.add_toggle_setting(
            'analytics_enabled', 'Usage Analytics',
            'Help improve the app by sharing anonymous usage data',
            False, self._on_setting_change
        )
        
        privacy.add_toggle_setting(
            'crash_reporting', 'Crash Reporting',
            'Automatically send crash reports to help fix bugs',
            True, self._on_setting_change
        )
        
        privacy.add_action_setting(
            'clear_data', 'Clear All Data',
            'Clear Data', 'Remove all vocabulary and session data',
            self._on_action_setting, 'text'
        )
        
        privacy.add_action_setting(
            'export_data', 'Export All Data',
            'Export', 'Create backup of all your data',
            self._on_action_setting, 'secondary'
        )
        
        # Advanced Settings
        advanced = self.sections['advanced']
        
        advanced.add_toggle_setting(
            'debug_mode', 'Debug Mode',
            'Enable detailed logging and debug information',
            False, self._on_setting_change
        )
        
        advanced.add_text_setting(
            'cache_size', 'Cache Size (MB)',
            '100', 'Maximum size for image and data cache',
            self._on_setting_change
        )
        
        advanced.add_choice_setting(
            'log_level', 'Log Level',
            ['ERROR', 'WARNING', 'INFO', 'DEBUG'],
            'INFO', 'Amount of detail in application logs',
            self._on_setting_change
        )
        
        advanced.add_action_setting(
            'reset_settings', 'Reset All Settings',
            'Reset', 'Restore all settings to default values',
            self._on_action_setting, 'text'
        )
    
    def _on_setting_change(self, key: str, value: Any):
        """Handle setting value change."""
        self.settings_data[key] = value
        
        # Apply immediate changes
        if key == 'theme_mode':
            self._apply_theme_change(value)
        elif key == 'accent_color':
            self._apply_accent_color_change(value)
        elif key == 'animations_enabled':
            self._apply_animation_setting(value)
        
        # Notify callback
        if self.on_setting_change:
            self.on_setting_change(key, value)
    
    def _on_action_setting(self, key: str):
        """Handle action setting activation."""
        if key == 'clear_data':
            self._clear_all_data()
        elif key == 'export_data':
            self._export_all_data()
        elif key == 'reset_settings':
            self._reset_to_defaults()
    
    def _apply_theme_change(self, theme_mode: str):
        """Apply theme mode change."""
        if self.style_manager:
            theme_name = theme_mode.lower()
            if theme_name == 'system':
                # For now, default to light
                theme_name = 'light'
            
            from ..styles.material_theme import MaterialTheme
            new_theme = MaterialTheme(theme_name)
            self.style_manager.set_theme(new_theme)
    
    def _apply_accent_color_change(self, color_name: str):
        """Apply accent color change."""
        if self.style_manager:
            from ..styles.material_theme import MaterialTheme, MaterialVariant
            
            color_map = {
                'Blue': MaterialVariant.PRIMARY,
                'Green': MaterialVariant.SUCCESS,
                'Purple': MaterialVariant.TERTIARY,
                'Orange': MaterialVariant.WARNING,
                'Red': MaterialVariant.ERROR
            }
            
            if color_name in color_map:
                variant = color_map[color_name]
                new_theme = self.style_manager.theme.create_variant(variant)
                self.style_manager.set_theme(new_theme)
    
    def _apply_animation_setting(self, enabled: bool):
        """Apply animation setting."""
        # This would disable/enable animations in the animation manager
        if hasattr(self.style_manager, 'animation_manager'):
            if not enabled:
                self.style_manager.animation_manager.stop_all_animations()
    
    def _clear_all_data(self):
        """Clear all application data."""
        result = messagebox.askyesno(
            "Clear All Data",
            "This will permanently delete all vocabulary, sessions, and cached data. Are you sure?",
            icon='warning'
        )
        
        if result:
            try:
                # Clear data through config manager
                if self.config_manager and hasattr(self.config_manager, 'clear_all_data'):
                    self.config_manager.clear_all_data()
                
                messagebox.showinfo("Success", "All data has been cleared.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear data: {e}")
    
    def _export_all_data(self):
        """Export all application data."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Export Data"
            )
            
            if filename:
                export_data = {
                    'settings': self.settings_data,
                    'export_date': str(datetime.now()),
                    'version': '2.0'
                }
                
                # Add vocabulary data if available
                if self.config_manager:
                    # This would be implemented based on your config manager
                    pass
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Data exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {e}")
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        result = messagebox.askyesno(
            "Reset Settings",
            "This will restore all settings to their default values. Continue?",
            icon='question'
        )
        
        if result:
            # Clear current settings
            self.settings_data.clear()
            
            # Reset all widgets to defaults
            for section in self.sections.values():
                for key, setting in section.settings_widgets.items():
                    if setting['type'] == 'toggle':
                        setting['var'].set(False)
                    elif setting['type'] in ['choice', 'text']:
                        setting['var'].set('')
            
            # Apply default theme
            if self.style_manager:
                from ..styles.material_theme import MaterialTheme
                default_theme = MaterialTheme('light')
                self.style_manager.set_theme(default_theme)
            
            messagebox.showinfo("Success", "Settings have been reset to defaults.")
    
    def _save_settings(self):
        """Save all settings."""
        try:
            if self.config_manager and hasattr(self.config_manager, 'save_settings'):
                self.config_manager.save_settings(self.settings_data)
            
            # Show success animation
            self.style_manager.animate_widget(
                self.save_btn, 'pulse', scale=1.05, duration=0.2
            )
            
            # Temporarily change button text
            original_text = self.save_btn.cget('text')
            self.save_btn.configure(text='Saved!')
            self.after(1500, lambda: self.save_btn.configure(text=original_text))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def _load_settings(self):
        """Load existing settings."""
        try:
            if self.config_manager and hasattr(self.config_manager, 'load_settings'):
                loaded_settings = self.config_manager.load_settings()
                
                for key, value in loaded_settings.items():
                    self.settings_data[key] = value
                    
                    # Update UI widgets
                    for section in self.sections.values():
                        if key in section.settings_widgets:
                            setting = section.settings_widgets[key]
                            if setting['var']:
                                setting['var'].set(value)
                            break
                            
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def get_setting(self, key: str) -> Any:
        """Get current setting value."""
        return self.settings_data.get(key)
    
    def set_setting(self, key: str, value: Any):
        """Set setting value programmatically."""
        self.settings_data[key] = value
        
        # Update UI if widget exists
        for section in self.sections.values():
            if key in section.settings_widgets:
                setting = section.settings_widgets[key]
                if setting['var']:
                    setting['var'].set(value)
                break
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all current settings."""
        return self.settings_data.copy()
    
    def apply_settings(self, settings: Dict[str, Any]):
        """Apply multiple settings at once."""
        for key, value in settings.items():
            self.set_setting(key, value)
        
        # Trigger save
        self._save_settings()