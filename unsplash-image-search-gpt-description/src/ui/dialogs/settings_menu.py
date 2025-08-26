"""
Settings dialog with tabbed interface for application configuration.
Provides tabs for API Keys, GPT Settings, Learning preferences, and Appearance.
All settings are saved immediately to config.ini on change.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import configparser
from pathlib import Path
import os
import sys


class SettingsDialog(tk.Toplevel):
    """
    Comprehensive settings dialog with tabbed interface.
    Features:
    - API Keys tab with show/hide toggles
    - GPT Settings with model selection and parameters
    - Learning preferences for description styles and vocabulary
    - Appearance settings for theme and font size
    """
    
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager
        self.parent = parent
        
        # Dialog setup
        self.title("Settings")
        self.geometry("700x600")
        self.resizable(True, True)
        self.minsize(600, 500)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Store original values for cancel functionality
        self.original_config = self._backup_config()
        
        # Initialize variables for UI binding
        self._init_variables()
        
        # Create the interface
        self._create_widgets()
        
        # Load current settings
        self._load_settings()
        
        # Center window
        self._center_window()
        
        # Bind events
        self._bind_events()
    
    def _init_variables(self):
        """Initialize Tkinter variables for UI elements."""
        # API Keys
        self.unsplash_key_var = tk.StringVar()
        self.openai_key_var = tk.StringVar()
        self.show_unsplash_var = tk.BooleanVar(value=False)
        self.show_openai_var = tk.BooleanVar(value=False)
        
        # GPT Settings
        self.gpt_model_var = tk.StringVar(value="gpt-4o-mini")
        self.temperature_var = tk.DoubleVar(value=0.7)
        self.max_tokens_var = tk.IntVar(value=500)
        
        # Learning Settings
        self.description_style_var = tk.StringVar(value="Simple")
        self.vocabulary_level_var = tk.StringVar(value="Beginner")
        self.enable_learning_var = tk.BooleanVar(value=True)
        
        # Appearance Settings
        self.theme_var = tk.StringVar(value="light")
        self.font_size_var = tk.IntVar(value=12)
        self.window_opacity_var = tk.DoubleVar(value=1.0)
    
    def _create_widgets(self):
        """Create the main UI with tabbed interface."""
        # Main container with padding
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Application Settings",
            font=('TkDefaultFont', 14, 'bold')
        )
        title_label.pack(pady=(0, 15))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create tabs
        self._create_api_keys_tab()
        self._create_gpt_settings_tab()
        self._create_learning_tab()
        self._create_appearance_tab()
        
        # Button frame
        self._create_buttons()
    
    def _create_api_keys_tab(self):
        """Create API Keys configuration tab."""
        tab_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(tab_frame, text="API Keys")
        
        # Instructions
        instructions = ttk.Label(
            tab_frame,
            text="Configure your API keys for Unsplash and OpenAI services.\n"
                 "Keys are stored securely and only used for API requests.",
            wraplength=600,
            justify=tk.LEFT
        )
        instructions.pack(anchor=tk.W, pady=(0, 20))
        
        # Unsplash API Key Section
        unsplash_frame = ttk.LabelFrame(tab_frame, text="Unsplash API", padding="10")
        unsplash_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(unsplash_frame, text="Access Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Key entry with show/hide functionality
        key_frame = ttk.Frame(unsplash_frame)
        key_frame.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0))
        key_frame.columnconfigure(0, weight=1)
        
        self.unsplash_entry = ttk.Entry(
            key_frame,
            textvariable=self.unsplash_key_var,
            show="*",
            width=50
        )
        self.unsplash_entry.grid(row=0, column=0, sticky=tk.EW)
        
        self.unsplash_toggle = ttk.Checkbutton(
            key_frame,
            text="Show",
            variable=self.show_unsplash_var,
            command=self._toggle_unsplash_visibility
        )
        self.unsplash_toggle.grid(row=0, column=1, padx=(5, 0))
        
        # Link to get API key
        unsplash_link = ttk.Label(
            unsplash_frame,
            text="Get your free API key at: https://unsplash.com/developers",
            foreground="blue",
            cursor="hand2"
        )
        unsplash_link.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        unsplash_link.bind("<Button-1>", lambda e: self._open_url("https://unsplash.com/developers"))
        
        # OpenAI API Key Section
        openai_frame = ttk.LabelFrame(tab_frame, text="OpenAI API", padding="10")
        openai_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(openai_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        openai_key_frame = ttk.Frame(openai_frame)
        openai_key_frame.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0))
        openai_key_frame.columnconfigure(0, weight=1)
        
        self.openai_entry = ttk.Entry(
            openai_key_frame,
            textvariable=self.openai_key_var,
            show="*",
            width=50
        )
        self.openai_entry.grid(row=0, column=0, sticky=tk.EW)
        
        self.openai_toggle = ttk.Checkbutton(
            openai_key_frame,
            text="Show",
            variable=self.show_openai_var,
            command=self._toggle_openai_visibility
        )
        self.openai_toggle.grid(row=0, column=1, padx=(5, 0))
        
        openai_link = ttk.Label(
            openai_frame,
            text="Get your API key at: https://platform.openai.com/api-keys",
            foreground="blue",
            cursor="hand2"
        )
        openai_link.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        openai_link.bind("<Button-1>", lambda e: self._open_url("https://platform.openai.com/api-keys"))
        
        # Configure column weights
        unsplash_frame.columnconfigure(1, weight=1)
        openai_frame.columnconfigure(1, weight=1)
        
        # Bind change events
        self.unsplash_key_var.trace_add('write', self._on_api_key_change)
        self.openai_key_var.trace_add('write', self._on_api_key_change)
    
    def _create_gpt_settings_tab(self):
        """Create GPT Settings configuration tab."""
        tab_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(tab_frame, text="GPT Settings")
        
        # Instructions
        instructions = ttk.Label(
            tab_frame,
            text="Configure GPT model parameters for generating image descriptions.",
            wraplength=600,
            justify=tk.LEFT
        )
        instructions.pack(anchor=tk.W, pady=(0, 20))
        
        # Model Selection
        model_frame = ttk.LabelFrame(tab_frame, text="Model Configuration", padding="10")
        model_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(model_frame, text="GPT Model:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        model_options = [
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-3.5-turbo"
        ]
        
        self.model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.gpt_model_var,
            values=model_options,
            state="readonly",
            width=20
        )
        self.model_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        self.model_combo.bind('<<ComboboxSelected>>', self._on_gpt_setting_change)
        
        # Cost information
        cost_info = ttk.Label(
            model_frame,
            text="gpt-4o-mini: Most economical (~$0.001/description)\n"
                 "gpt-4o: Balanced performance (~$0.01/description)\n"
                 "gpt-4-turbo: High quality (~$0.005/description)",
            foreground="gray",
            justify=tk.LEFT
        )
        cost_info.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # Parameters Section
        params_frame = ttk.LabelFrame(tab_frame, text="Generation Parameters", padding="10")
        params_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Temperature
        ttk.Label(params_frame, text="Temperature:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        temp_frame = ttk.Frame(params_frame)
        temp_frame.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0))
        temp_frame.columnconfigure(0, weight=1)
        
        self.temp_scale = ttk.Scale(
            temp_frame,
            from_=0.0,
            to=2.0,
            variable=self.temperature_var,
            orient=tk.HORIZONTAL,
            command=self._on_temperature_change
        )
        self.temp_scale.grid(row=0, column=0, sticky=tk.EW)
        
        self.temp_label = ttk.Label(temp_frame, text="0.7")
        self.temp_label.grid(row=0, column=1, padx=(5, 0))
        
        temp_help = ttk.Label(
            params_frame,
            text="Lower = more focused, Higher = more creative",
            foreground="gray",
            font=('TkDefaultFont', 8)
        )
        temp_help.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Max Tokens
        ttk.Label(params_frame, text="Max Tokens:").grid(row=2, column=0, sticky=tk.W, pady=(15, 5))
        
        tokens_frame = ttk.Frame(params_frame)
        tokens_frame.grid(row=2, column=1, sticky=tk.EW, padx=(10, 0))
        tokens_frame.columnconfigure(0, weight=1)
        
        self.tokens_spinbox = ttk.Spinbox(
            tokens_frame,
            from_=100,
            to=2000,
            textvariable=self.max_tokens_var,
            width=10,
            command=self._on_gpt_setting_change
        )
        self.tokens_spinbox.grid(row=0, column=0, sticky=tk.W)
        
        tokens_help = ttk.Label(
            params_frame,
            text="Maximum length of generated descriptions (100-2000)",
            foreground="gray",
            font=('TkDefaultFont', 8)
        )
        tokens_help.grid(row=3, column=1, sticky=tk.W, padx=(10, 0))
        
        # Configure column weights
        model_frame.columnconfigure(1, weight=1)
        params_frame.columnconfigure(1, weight=1)
        
        # Bind additional change events
        self.max_tokens_var.trace_add('write', self._on_gpt_setting_change)
    
    def _create_learning_tab(self):
        """Create Learning preferences tab."""
        tab_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(tab_frame, text="Learning")
        
        # Instructions
        instructions = ttk.Label(
            tab_frame,
            text="Customize how descriptions are generated to match your learning preferences.",
            wraplength=600,
            justify=tk.LEFT
        )
        instructions.pack(anchor=tk.W, pady=(0, 20))
        
        # Description Style
        style_frame = ttk.LabelFrame(tab_frame, text="Description Style", padding="10")
        style_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(style_frame, text="Style:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        style_options = ["Simple", "Detailed", "Poetic"]
        self.style_combo = ttk.Combobox(
            style_frame,
            textvariable=self.description_style_var,
            values=style_options,
            state="readonly",
            width=15
        )
        self.style_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        self.style_combo.bind('<<ComboboxSelected>>', self._on_learning_setting_change)
        
        # Style descriptions
        style_help = ttk.Label(
            style_frame,
            text="Simple: Basic descriptions with common vocabulary\n"
                 "Detailed: Comprehensive descriptions with varied vocabulary\n"
                 "Poetic: Creative, artistic descriptions with advanced language",
            foreground="gray",
            justify=tk.LEFT
        )
        style_help.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # Vocabulary Level
        vocab_frame = ttk.LabelFrame(tab_frame, text="Vocabulary Level", padding="10")
        vocab_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(vocab_frame, text="Level:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        vocab_options = ["Beginner", "Intermediate", "Advanced", "Native"]
        self.vocab_combo = ttk.Combobox(
            vocab_frame,
            textvariable=self.vocabulary_level_var,
            values=vocab_options,
            state="readonly",
            width=15
        )
        self.vocab_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        self.vocab_combo.bind('<<ComboboxSelected>>', self._on_learning_setting_change)
        
        vocab_help = ttk.Label(
            vocab_frame,
            text="Controls the complexity of vocabulary used in descriptions",
            foreground="gray",
            font=('TkDefaultFont', 8)
        )
        vocab_help.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # Learning Features
        features_frame = ttk.LabelFrame(tab_frame, text="Learning Features", padding="10")
        features_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.learning_checkbox = ttk.Checkbutton(
            features_frame,
            text="Enable adaptive learning (adjusts descriptions based on your feedback)",
            variable=self.enable_learning_var,
            command=self._on_learning_setting_change
        )
        self.learning_checkbox.pack(anchor=tk.W)
        
        # Configure column weights
        style_frame.columnconfigure(1, weight=1)
        vocab_frame.columnconfigure(1, weight=1)
    
    def _create_appearance_tab(self):
        """Create Appearance settings tab."""
        tab_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(tab_frame, text="Appearance")
        
        # Instructions
        instructions = ttk.Label(
            tab_frame,
            text="Customize the application's appearance and user interface.",
            wraplength=600,
            justify=tk.LEFT
        )
        instructions.pack(anchor=tk.W, pady=(0, 20))
        
        # Theme Settings
        theme_frame = ttk.LabelFrame(tab_frame, text="Theme", padding="10")
        theme_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(theme_frame, text="Color Theme:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Theme radio buttons
        theme_inner_frame = ttk.Frame(theme_frame)
        theme_inner_frame.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Radiobutton(
            theme_inner_frame,
            text="Light",
            variable=self.theme_var,
            value="light",
            command=self._on_appearance_change
        ).pack(side=tk.LEFT)
        
        ttk.Radiobutton(
            theme_inner_frame,
            text="Dark",
            variable=self.theme_var,
            value="dark",
            command=self._on_appearance_change
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Radiobutton(
            theme_inner_frame,
            text="Auto",
            variable=self.theme_var,
            value="auto",
            command=self._on_appearance_change
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Font Settings
        font_frame = ttk.LabelFrame(tab_frame, text="Font", padding="10")
        font_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(font_frame, text="Font Size:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        font_size_frame = ttk.Frame(font_frame)
        font_size_frame.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0))
        font_size_frame.columnconfigure(0, weight=1)
        
        self.font_scale = ttk.Scale(
            font_size_frame,
            from_=8,
            to=24,
            variable=self.font_size_var,
            orient=tk.HORIZONTAL,
            command=self._on_font_size_change
        )
        self.font_scale.grid(row=0, column=0, sticky=tk.EW)
        
        self.font_size_label = ttk.Label(font_size_frame, text="12")
        self.font_size_label.grid(row=0, column=1, padx=(5, 0))
        
        # Preview text
        self.preview_label = ttk.Label(
            font_frame,
            text="Preview: This is how text will appear in the application",
            font=('TkDefaultFont', 12)
        )
        self.preview_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        
        # Window Settings
        window_frame = ttk.LabelFrame(tab_frame, text="Window", padding="10")
        window_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(window_frame, text="Opacity:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        opacity_frame = ttk.Frame(window_frame)
        opacity_frame.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0))
        opacity_frame.columnconfigure(0, weight=1)
        
        self.opacity_scale = ttk.Scale(
            opacity_frame,
            from_=0.5,
            to=1.0,
            variable=self.window_opacity_var,
            orient=tk.HORIZONTAL,
            command=self._on_opacity_change
        )
        self.opacity_scale.grid(row=0, column=0, sticky=tk.EW)
        
        self.opacity_label = ttk.Label(opacity_frame, text="100%")
        self.opacity_label.grid(row=0, column=1, padx=(5, 0))
        
        # Configure column weights
        theme_frame.columnconfigure(1, weight=1)
        font_frame.columnconfigure(1, weight=1)
        window_frame.columnconfigure(1, weight=1)
    
    def _create_buttons(self):
        """Create dialog buttons."""
        button_frame = ttk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(button_frame, text="", foreground="green")
        self.status_label.pack(side=tk.LEFT)
        
        # Buttons
        ttk.Button(
            button_frame,
            text="Reset to Defaults",
            command=self._reset_defaults
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._cancel
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Apply",
            command=self._apply_settings
        ).pack(side=tk.RIGHT, padx=(5, 0))
    
    def _load_settings(self):
        """Load current settings from config manager."""
        try:
            # Load API keys
            api_keys = self.config_manager.get_api_keys()
            self.unsplash_key_var.set(api_keys.get('unsplash', ''))
            self.openai_key_var.set(api_keys.get('openai', ''))
            self.gpt_model_var.set(api_keys.get('gpt_model', 'gpt-4o-mini'))
            
            config = self.config_manager.config
            
            # Load GPT settings
            if config.has_section('GPT'):
                self.temperature_var.set(config.getfloat('GPT', 'temperature', fallback=0.7))
                self.max_tokens_var.set(config.getint('GPT', 'max_tokens', fallback=500))
            
            # Load learning settings
            if config.has_section('Learning'):
                self.description_style_var.set(config.get('Learning', 'description_style', fallback='Simple'))
                self.vocabulary_level_var.set(config.get('Learning', 'vocabulary_level', fallback='Beginner'))
                self.enable_learning_var.set(config.getboolean('Learning', 'enable_learning', fallback=True))
            
            # Load UI settings
            if config.has_section('UI'):
                self.theme_var.set(config.get('UI', 'theme', fallback='light'))
                self.font_size_var.set(config.getint('UI', 'font_size', fallback=12))
                self.window_opacity_var.set(config.getfloat('UI', 'opacity', fallback=1.0))
            
            # Update UI elements
            self._update_temperature_label()
            self._update_font_size_label()
            self._update_opacity_label()
            self._update_font_preview()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings: {e}")
    
    def _backup_config(self):
        """Create backup of current configuration for cancel functionality."""
        backup = {}
        config = self.config_manager.config
        
        for section_name in config.sections():
            backup[section_name] = {}
            for key, value in config[section_name].items():
                backup[section_name][key] = value
        
        return backup
    
    def _restore_config(self):
        """Restore configuration from backup."""
        config = self.config_manager.config
        
        # Clear current config
        for section in config.sections():
            config.remove_section(section)
        
        # Restore from backup
        for section_name, items in self.original_config.items():
            config.add_section(section_name)
            for key, value in items.items():
                config.set(section_name, key, value)
        
        self._save_config()
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_manager.config_file, 'w') as f:
                self.config_manager.config.write(f)
            self._show_status("Settings saved", "green")
        except Exception as e:
            self._show_status(f"Error saving: {e}", "red")
    
    def _show_status(self, message, color="black"):
        """Show status message."""
        self.status_label.config(text=message, foreground=color)
        # Clear status after 3 seconds
        self.after(3000, lambda: self.status_label.config(text=""))
    
    # Event Handlers
    def _on_api_key_change(self, *args):
        """Handle API key changes."""
        self._save_api_keys()
    
    def _on_gpt_setting_change(self, *args):
        """Handle GPT setting changes."""
        self._save_gpt_settings()
    
    def _on_learning_setting_change(self, *args):
        """Handle learning setting changes."""
        self._save_learning_settings()
    
    def _on_appearance_change(self, *args):
        """Handle appearance setting changes."""
        self._save_appearance_settings()
    
    def _on_temperature_change(self, value):
        """Handle temperature slider change."""
        self._update_temperature_label()
        self._save_gpt_settings()
    
    def _on_font_size_change(self, value):
        """Handle font size change."""
        self._update_font_size_label()
        self._update_font_preview()
        self._save_appearance_settings()
    
    def _on_opacity_change(self, value):
        """Handle opacity change."""
        self._update_opacity_label()
        self._apply_opacity()
        self._save_appearance_settings()
    
    # Save Methods
    def _save_api_keys(self):
        """Save API keys to config."""
        try:
            unsplash_key = self.unsplash_key_var.get().strip()
            openai_key = self.openai_key_var.get().strip()
            gpt_model = self.gpt_model_var.get()
            
            self.config_manager.save_api_keys(unsplash_key, openai_key, gpt_model)
            self._show_status("API keys saved")
        except Exception as e:
            self._show_status(f"Error saving API keys: {e}", "red")
    
    def _save_gpt_settings(self):
        """Save GPT settings to config."""
        try:
            config = self.config_manager.config
            
            if not config.has_section('GPT'):
                config.add_section('GPT')
            
            config.set('GPT', 'temperature', str(self.temperature_var.get()))
            config.set('GPT', 'max_tokens', str(self.max_tokens_var.get()))
            
            self._save_config()
        except Exception as e:
            self._show_status(f"Error saving GPT settings: {e}", "red")
    
    def _save_learning_settings(self):
        """Save learning settings to config."""
        try:
            config = self.config_manager.config
            
            if not config.has_section('Learning'):
                config.add_section('Learning')
            
            config.set('Learning', 'description_style', self.description_style_var.get())
            config.set('Learning', 'vocabulary_level', self.vocabulary_level_var.get())
            config.set('Learning', 'enable_learning', str(self.enable_learning_var.get()))
            
            self._save_config()
        except Exception as e:
            self._show_status(f"Error saving learning settings: {e}", "red")
    
    def _save_appearance_settings(self):
        """Save appearance settings to config."""
        try:
            config = self.config_manager.config
            
            if not config.has_section('UI'):
                config.add_section('UI')
            
            config.set('UI', 'theme', self.theme_var.get())
            config.set('UI', 'font_size', str(self.font_size_var.get()))
            config.set('UI', 'opacity', str(self.window_opacity_var.get()))
            
            self._save_config()
        except Exception as e:
            self._show_status(f"Error saving appearance settings: {e}", "red")
    
    # Utility Methods
    def _toggle_unsplash_visibility(self):
        """Toggle Unsplash key visibility."""
        if self.show_unsplash_var.get():
            self.unsplash_entry.config(show="")
        else:
            self.unsplash_entry.config(show="*")
    
    def _toggle_openai_visibility(self):
        """Toggle OpenAI key visibility."""
        if self.show_openai_var.get():
            self.openai_entry.config(show="")
        else:
            self.openai_entry.config(show="*")
    
    def _update_temperature_label(self):
        """Update temperature display label."""
        value = round(self.temperature_var.get(), 2)
        self.temp_label.config(text=str(value))
    
    def _update_font_size_label(self):
        """Update font size display label."""
        size = int(self.font_size_var.get())
        self.font_size_label.config(text=str(size))
    
    def _update_opacity_label(self):
        """Update opacity display label."""
        opacity = self.window_opacity_var.get()
        percentage = int(opacity * 100)
        self.opacity_label.config(text=f"{percentage}%")
    
    def _update_font_preview(self):
        """Update font preview with current size."""
        size = int(self.font_size_var.get())
        self.preview_label.config(font=('TkDefaultFont', size))
    
    def _apply_opacity(self):
        """Apply opacity to parent window."""
        try:
            if self.parent and hasattr(self.parent, 'wm_attributes'):
                opacity = self.window_opacity_var.get()
                self.parent.wm_attributes('-alpha', opacity)
        except Exception:
            pass  # Ignore if parent doesn't support transparency
    
    def _validate_unsplash_key(self, key):
        """Validate Unsplash API key format."""
        if not key:
            return False
        elif len(key) < 20:
            return False
        elif ' ' in key:
            return False
        else:
            return True
    
    def _validate_openai_key(self, key):
        """Validate OpenAI API key format."""
        if not key:
            return False
        elif not key.startswith('sk-'):
            return False
        elif len(key) < 40:
            return False
        elif ' ' in key:
            return False
        else:
            return True
    
    def _open_url(self, url):
        """Open URL in default browser."""
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            # Copy URL to clipboard as fallback
            self.clipboard_clear()
            self.clipboard_append(url)
            self._show_status("URL copied to clipboard")
    
    def _reset_defaults(self):
        """Reset all settings to default values."""
        result = messagebox.askyesno(
            "Reset Settings",
            "Are you sure you want to reset all settings to their default values?\n"
            "This will not affect your API keys.",
            parent=self
        )
        
        if result:
            # Reset to defaults (preserve API keys)
            api_keys = self.config_manager.get_api_keys()
            
            # Reset UI variables
            self.gpt_model_var.set("gpt-4o-mini")
            self.temperature_var.set(0.7)
            self.max_tokens_var.set(500)
            self.description_style_var.set("Simple")
            self.vocabulary_level_var.set("Beginner")
            self.enable_learning_var.set(True)
            self.theme_var.set("light")
            self.font_size_var.set(12)
            self.window_opacity_var.set(1.0)
            
            # Update displays
            self._update_temperature_label()
            self._update_font_size_label()
            self._update_opacity_label()
            self._update_font_preview()
            
            # Save changes
            self._save_gpt_settings()
            self._save_learning_settings()
            self._save_appearance_settings()
            
            self._show_status("Settings reset to defaults", "green")
    
    def _apply_settings(self):
        """Apply current settings."""
        self._save_api_keys()
        self._save_gpt_settings()
        self._save_learning_settings()
        self._save_appearance_settings()
        self._show_status("All settings applied", "green")
    
    def _cancel(self):
        """Cancel changes and close dialog."""
        # Ask for confirmation if there are changes
        result = messagebox.askyesno(
            "Cancel Changes",
            "Are you sure you want to cancel? Any unsaved changes will be lost.",
            parent=self
        )
        
        if result:
            self._restore_config()
            self.destroy()
    
    def _center_window(self):
        """Center the dialog on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _bind_events(self):
        """Bind keyboard events."""
        self.bind('<Escape>', lambda e: self._cancel())
        self.bind('<Control-s>', lambda e: self._apply_settings())
        self.bind('<F5>', lambda e: self._load_settings())


def show_settings_dialog(parent, config_manager):
    """
    Show the settings dialog.
    
    Args:
        parent: Parent window
        config_manager: ConfigManager instance
    
    Returns:
        SettingsDialog instance
    """
    dialog = SettingsDialog(parent, config_manager)
    return dialog


# Test/demo functionality
if __name__ == "__main__":
    # For testing purposes
    import sys
    import os
    
    # Add parent directory to path for imports
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    
    from config_manager import ConfigManager
    
    root = tk.Tk()
    root.title("Settings Dialog Test")
    root.geometry("400x200")
    
    # Initialize config manager
    config_manager = ConfigManager()
    
    # Create test button
    def open_settings():
        show_settings_dialog(root, config_manager)
    
    ttk.Button(
        root,
        text="Open Settings",
        command=open_settings
    ).pack(pady=50)
    
    root.mainloop()