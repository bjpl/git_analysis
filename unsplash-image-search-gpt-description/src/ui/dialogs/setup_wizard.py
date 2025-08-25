"""
Setup wizard dialog for configuring API keys.
This module extracts the setup wizard from config_manager.py for better separation of concerns.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class SetupWizard(tk.Toplevel):
    """First-run setup wizard for API keys."""
    
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager
        self.title("Setup - API Configuration")
        self.geometry("600x400")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.result = False
        self.create_widgets()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (400 // 2)
        self.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """Create the setup wizard UI."""
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
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Cancel button
        self.cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Submit button (enhanced)
        self.submit_button = ttk.Button(
            button_frame,
            text="✓ Submit & Continue",
            command=self.save_and_continue
        )
        self.submit_button.pack(side=tk.RIGHT)
        self.submit_button.configure(state='disabled')  # Initially disabled
        
        # Status label for validation feedback
        self.status_label = ttk.Label(button_frame, text="", foreground="gray")
        self.status_label.pack(side=tk.LEFT)
        
        # Load existing keys if any
        self._load_existing_keys()
        
        # Set initial focus and validate
        self.unsplash_entry.focus_set()
        self._validate_form()
        
        # Bind Escape key to cancel
        self.bind('<Escape>', lambda e: self.cancel())
    
    def _load_existing_keys(self):
        """Load existing API keys if available."""
        keys = self.config_manager.get_api_keys()
        if keys['unsplash']:
            self.unsplash_entry.insert(0, keys['unsplash'])
        if keys['openai']:
            self.openai_entry.insert(0, keys['openai'])
        if keys['gpt_model']:
            self.model_var.set(keys['gpt_model'])
    
    def _on_enter_key(self, event):
        """Handle Enter key press to submit form."""
        if self.submit_button['state'] == 'normal':
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
        
        # Enable/disable submit button
        if unsplash_valid and openai_valid:
            self.submit_button.configure(state='normal')
            self.status_label.config(text="✓ Ready to submit", foreground="green")
        else:
            self.submit_button.configure(state='disabled')
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
        """Cancel the setup wizard."""
        self.result = False
        self.destroy()


def ensure_api_keys_configured(parent_window=None):
    """Ensure API keys are configured, show setup wizard if not."""
    from config_manager import ConfigManager
    
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