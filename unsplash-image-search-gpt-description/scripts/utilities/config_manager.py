"""
Configuration manager for API keys and settings.
Handles both .env files (development) and config.ini (production/exe).
"""

import os
import sys
import configparser
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import json


class ConfigManager:
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.ini"
        self.data_dir = self.config_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to load from environment first (.env file)
        self._load_env_file()
        
        # Then load or create config.ini
        self.config = self._load_or_create_config()
    
    def _get_config_dir(self):
        """Get configuration directory based on whether running as exe or script."""
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            return Path(os.path.dirname(sys.executable))
        else:
            # Running as script
            return Path(os.path.dirname(os.path.abspath(__file__)))
    
    def _load_env_file(self):
        """Load .env file if it exists (for development)."""
        env_file = self.config_dir / ".env"
        if env_file.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
            except ImportError:
                pass  # dotenv not installed, skip
    
    def _load_or_create_config(self):
        """Load existing config or create new one."""
        config = configparser.ConfigParser()
        
        if self.config_file.exists():
            config.read(self.config_file)
        else:
            # Create default config
            config['API'] = {
                'unsplash_access_key': '',
                'openai_api_key': '',
                'gpt_model': 'gpt-4o-mini'
            }
            config['Paths'] = {
                'data_dir': str(self.data_dir),
                'log_file': str(self.data_dir / 'session_log.json'),
                'vocabulary_file': str(self.data_dir / 'vocabulary.csv')
            }
            config['UI'] = {
                'window_width': '1100',
                'window_height': '800',
                'font_size': '12',
                'theme': 'light',
                'zoom_level': '100'
            }
            config['Search'] = {
                'max_images_per_search': '30',
                'show_progress_counter': 'true',
                'enable_search_limits': 'true'
            }
        
        return config
    
    def get_api_keys(self):
        """Get API keys from environment or config file."""
        unsplash_key = os.getenv('UNSPLASH_ACCESS_KEY') or self.config.get('API', 'unsplash_access_key', fallback='')
        openai_key = os.getenv('OPENAI_API_KEY') or self.config.get('API', 'openai_api_key', fallback='')
        gpt_model = os.getenv('GPT_MODEL') or self.config.get('API', 'gpt_model', fallback='gpt-4o-mini')
        
        return {
            'unsplash': unsplash_key,
            'openai': openai_key,
            'gpt_model': gpt_model
        }
    
    def save_api_keys(self, unsplash_key, openai_key, gpt_model='gpt-4o-mini'):
        """Save API keys to config file."""
        self.config['API']['unsplash_access_key'] = unsplash_key
        self.config['API']['openai_api_key'] = openai_key
        self.config['API']['gpt_model'] = gpt_model
        
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get_paths(self):
        """Get application paths."""
        return {
            'data_dir': Path(self.config.get('Paths', 'data_dir', fallback=str(self.data_dir))),
            'log_file': Path(self.config.get('Paths', 'log_file', fallback=str(self.data_dir / 'session_log.json'))),
            'vocabulary_file': Path(self.config.get('Paths', 'vocabulary_file', fallback=str(self.data_dir / 'vocabulary.csv')))
        }
    
    def validate_api_keys(self):
        """Check if API keys are configured."""
        keys = self.get_api_keys()
        return bool(keys['unsplash'] and keys['openai'])


class SetupWizard(tk.Toplevel):
    """First-run setup wizard for API keys."""
    
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager
        self.title("Setup - API Configuration")
        self.geometry("600x500")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.result = False
        self.create_widgets()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Welcome! Let's set up your API keys",
            font=('TkDefaultFont', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = (
            "This application requires API keys from Unsplash and OpenAI.\n"
            "Your keys will be saved locally and never shared.\n\n"
            "Press Enter to submit or use the Submit button below."
        )
        ttk.Label(main_frame, text=instructions, wraplength=550).pack(pady=(0, 20))
        
        # API Keys Frame
        keys_frame = ttk.LabelFrame(main_frame, text="API Keys", padding="15")
        keys_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Unsplash API Key
        ttk.Label(keys_frame, text="Unsplash Access Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.unsplash_entry = ttk.Entry(keys_frame, width=50)
        self.unsplash_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        self.unsplash_entry.bind('<Return>', self._on_enter_key)
        self.unsplash_entry.bind('<KeyRelease>', self._on_key_release)
        
        # Validation label for Unsplash key
        self.unsplash_validation = ttk.Label(keys_frame, text="", foreground="red")
        self.unsplash_validation.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        unsplash_link = ttk.Label(
            keys_frame,
            text="Get key from: https://unsplash.com/developers",
            foreground="blue",
            cursor="hand2"
        )
        unsplash_link.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # OpenAI API Key
        ttk.Label(keys_frame, text="OpenAI API Key:").grid(row=3, column=0, sticky=tk.W, pady=(20, 5))
        self.openai_entry = ttk.Entry(keys_frame, width=50, show="*")
        self.openai_entry.grid(row=3, column=1, pady=(20, 5), padx=(10, 0))
        self.openai_entry.bind('<Return>', self._on_enter_key)
        self.openai_entry.bind('<KeyRelease>', self._on_key_release)
        
        # Validation label for OpenAI key
        self.openai_validation = ttk.Label(keys_frame, text="", foreground="red")
        self.openai_validation.grid(row=4, column=1, sticky=tk.W, padx=(10, 0))
        
        openai_link = ttk.Label(
            keys_frame,
            text="Get key from: https://platform.openai.com/api-keys",
            foreground="blue",
            cursor="hand2"
        )
        openai_link.grid(row=5, column=1, sticky=tk.W, padx=(10, 0))
        
        # GPT Model Selection with cost info
        ttk.Label(keys_frame, text="GPT Model:").grid(row=6, column=0, sticky=tk.W, pady=(20, 5))
        self.model_var = tk.StringVar(value="gpt-4o-mini")
        
        # Model options with cost estimates
        model_options = [
            "gpt-4o-mini ($0.001/desc)",
            "gpt-4o ($0.01/desc)",
            "gpt-4-turbo ($0.005/desc)"
        ]
        
        model_combo = ttk.Combobox(
            keys_frame,
            textvariable=self.model_var,
            values=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
            state="readonly",
            width=20
        )
        model_combo.grid(row=6, column=1, sticky=tk.W, pady=(20, 5), padx=(10, 0))
        model_combo.bind('<Return>', self._on_enter_key)
        
        # Cost hint
        cost_hint = ttk.Label(
            keys_frame,
            text="gpt-4o-mini recommended (best value)",
            foreground="gray"
        )
        cost_hint.grid(row=7, column=1, sticky=tk.W, padx=(10, 0))
        
        # Add separator before buttons
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(15, 0))
        
        # Buttons - ensure they are visible
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 10), expand=False)
        
        # Status label for validation feedback
        self.status_label = ttk.Label(button_frame, text="", foreground="gray")
        self.status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Submit button - use standard tk.Button for better visibility
        self.submit_button = tk.Button(
            button_frame,
            text="Save & Continue",
            command=self.save_and_continue,
            width=20,
            bg="#0084ff",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            bd=2,
            cursor="hand2"
        )
        self.submit_button.pack(side=tk.RIGHT, padx=(0, 10), pady=5)
        self.submit_button.configure(state='disabled')  # Initially disabled
        
        # Cancel button
        self.cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel,
            width=10,
            bg="#e0e0e0",
            fg="black",
            font=("Arial", 10),
            relief=tk.RAISED,
            bd=2,
            cursor="hand2"
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=(5, 5), pady=5)
        
        # Set initial focus
        self.unsplash_entry.focus_set()
        
        # Load existing keys if any
        keys = self.config_manager.get_api_keys()
        if keys['unsplash']:
            self.unsplash_entry.insert(0, keys['unsplash'])
        if keys['openai']:
            self.openai_entry.insert(0, keys['openai'])
        if keys['gpt_model']:
            self.model_var.set(keys['gpt_model'])
        
        # Validate initial state
        self._validate_form()
        
        # Bind Escape key to cancel
        self.bind('<Escape>', lambda e: self.cancel())
    
    def _on_enter_key(self, event):
        """Handle Enter key press to submit form."""
        if str(self.submit_button['state']) != 'disabled':
            self.save_and_continue()
        return 'break'
    
    def _on_key_release(self, event):
        """Handle key release to validate form in real-time."""
        self._validate_form()
    
    def _validate_form(self):
        """Validate form inputs and update UI accordingly."""
        unsplash_key = self.unsplash_entry.get().strip()
        openai_key = self.openai_entry.get().strip()
        
        # Reset validation messages
        self.unsplash_validation.config(text="")
        self.openai_validation.config(text="")
        
        # Validate Unsplash key
        unsplash_valid = self._validate_unsplash_key(unsplash_key)
        
        # Validate OpenAI key
        openai_valid = self._validate_openai_key(openai_key)
        
        # Enable/disable submit button with color change
        if unsplash_valid and openai_valid:
            self.submit_button.configure(state='normal', bg="#00aa00")
            self.status_label.config(text="✓ Ready to submit", foreground="green")
        else:
            self.submit_button.configure(state='disabled', bg="#808080")
            if not unsplash_key and not openai_key:
                self.status_label.config(text="Please enter your API keys", foreground="gray")
            else:
                self.status_label.config(text="Please fix validation errors", foreground="red")
    
    def _validate_unsplash_key(self, key):
        """Validate Unsplash API key format."""
        if not key:
            self.unsplash_validation.config(text="Unsplash key is required")
            return False
        elif len(key) < 20:
            self.unsplash_validation.config(text="Key appears too short (should be ~43 characters)")
            return False
        elif ' ' in key:
            self.unsplash_validation.config(text="Key should not contain spaces")
            return False
        else:
            self.unsplash_validation.config(text="✓ Valid format", foreground="green")
            return True
    
    def _validate_openai_key(self, key):
        """Validate OpenAI API key format."""
        if not key:
            self.openai_validation.config(text="OpenAI key is required")
            return False
        elif not key.startswith('sk-'):
            self.openai_validation.config(text="OpenAI keys should start with 'sk-'")
            return False
        elif len(key) < 40:
            self.openai_validation.config(text="Key appears too short")
            return False
        elif ' ' in key:
            self.openai_validation.config(text="Key should not contain spaces")
            return False
        else:
            self.openai_validation.config(text="✓ Valid format", foreground="green")
            return True
    
    def save_and_continue(self):
        """Save API keys with enhanced validation and user feedback."""
        unsplash_key = self.unsplash_entry.get().strip()
        openai_key = self.openai_entry.get().strip()
        gpt_model = self.model_var.get()
        
        # Final validation
        if not self._validate_unsplash_key(unsplash_key) or not self._validate_openai_key(openai_key):
            messagebox.showerror(
                "Validation Error",
                "Please fix the validation errors shown above.",
                parent=self
            )
            return
        
        # Show processing feedback
        self.submit_button.configure(state='disabled', text="Saving...")
        self.status_label.config(text="Saving configuration...", foreground="blue")
        self.update_idletasks()
        
        try:
            # Save keys
            self.config_manager.save_api_keys(unsplash_key, openai_key, gpt_model)
            
            # Success feedback
            self.status_label.config(text="✓ Configuration saved successfully!", foreground="green")
            self.update_idletasks()
            
            # Brief delay to show success message
            self.after(500, self._close_with_success)
            
        except Exception as e:
            # Error handling
            self.submit_button.configure(state='normal', text="✓ Submit & Continue")
            self.status_label.config(text="Error saving configuration", foreground="red")
            messagebox.showerror(
                "Save Error",
                f"Failed to save API keys:\n{str(e)}",
                parent=self
            )
    
    def _close_with_success(self):
        """Close dialog with success result."""
        self.result = True
        self.destroy()
    
    def cancel(self):
        self.result = False
        self.destroy()


def ensure_api_keys_configured(parent_window=None):
    """Ensure API keys are configured, show setup wizard if not."""
    config = ConfigManager()
    
    if not config.validate_api_keys():
        if parent_window is None:
            root = tk.Tk()
            root.withdraw()
            parent = root
        else:
            parent = parent_window
        
        wizard = SetupWizard(parent, config)
        parent.wait_window(wizard)
        
        if parent_window is None:
            root.destroy()
        
        if not wizard.result:
            return None
        
        # Reload config after wizard
        config = ConfigManager()
    
    return config