"""
Secure Setup Wizard

Enhanced first-run setup wizard with real-time API key validation,
security indicators, and user-friendly error handling.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
import logging
from typing import Optional, Dict, Any, Callable
from pathlib import Path

from .key_validator import APIKeyValidator, ValidationStatus, ValidationResult
from .secure_config_manager import SecureConfigManager

logger = logging.getLogger(__name__)

class SecureSetupWizard(tk.Toplevel):
    """Enhanced setup wizard with real-time validation and security features."""
    
    def __init__(self, parent: tk.Tk, config_manager: SecureConfigManager, 
                 on_success: Optional[Callable] = None):
        """
        Initialize the secure setup wizard.
        
        Args:
            parent: Parent window
            config_manager: Secure configuration manager instance
            on_success: Optional callback function called on successful setup
        """
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.validator = APIKeyValidator()
        self.on_success = on_success
        self.setup_complete = False
        
        # Validation state
        self.validation_results = {'unsplash': None, 'openai': None}
        self.validation_in_progress = {'unsplash': False, 'openai': False}
        
        self._setup_window()
        self._create_widgets()
        self._setup_bindings()
        
        # Load existing configuration if available
        self._load_existing_config()
        
        # Center window
        self._center_window()
    
    def _setup_window(self):
        """Configure window properties."""
        self.title("Secure API Configuration")
        self.geometry("700x600")
        self.resizable(False, False)
        
        # Make modal
        self.transient(self.master)
        self.grab_set()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Configure style
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
    
    def _create_widgets(self):
        """Create and layout all widgets."""
        # Main container
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self._create_header(main_frame)
        
        # Security notice
        self._create_security_notice(main_frame)
        
        # API Keys section
        self._create_api_keys_section(main_frame)
        
        # Model selection
        self._create_model_section(main_frame)
        
        # Validation status
        self._create_validation_section(main_frame)
        
        # Action buttons
        self._create_action_buttons(main_frame)
        
        # Progress bar
        self._create_progress_bar(main_frame)
    
    def _create_header(self, parent):
        """Create header section."""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="🔐 Secure API Configuration",
            font=('TkDefaultFont', 16, 'bold')
        )
        title_label.pack(anchor=tk.W)
        
        # Subtitle
        subtitle_label = ttk.Label(
            header_frame,
            text="Configure your API keys securely. Keys are encrypted and stored locally.",
            font=('TkDefaultFont', 10)
        )
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
    
    def _create_security_notice(self, parent):
        """Create security notice section."""
        notice_frame = ttk.LabelFrame(parent, text="🛡️ Security Information", padding="15")
        notice_frame.pack(fill=tk.X, pady=(0, 20))
        
        security_text = (
            "✓ API keys are encrypted using Windows DPAPI (or secure fallback)\n"
            "✓ Keys are stored in your user profile directory only\n"
            "✓ No keys are embedded in the application executable\n"
            "✓ Real-time validation ensures keys work before saving\n"
            "✓ Automatic backup and recovery features included"
        )
        
        security_label = ttk.Label(
            notice_frame,
            text=security_text,
            justify=tk.LEFT,
            wraplength=650
        )
        security_label.pack(anchor=tk.W)
    
    def _create_api_keys_section(self, parent):
        """Create API keys input section."""
        keys_frame = ttk.LabelFrame(parent, text="API Keys", padding="15")
        keys_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Configure grid
        keys_frame.columnconfigure(1, weight=1)
        
        # Unsplash API Key
        row = 0
        ttk.Label(keys_frame, text="Unsplash Access Key:", font=('TkDefaultFont', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.unsplash_entry = ttk.Entry(keys_frame, width=50, show="*")
        self.unsplash_entry.grid(row=row, column=1, pady=(0, 5), padx=(10, 0), sticky="ew")
        
        # Unsplash status indicator
        self.unsplash_status = ttk.Label(keys_frame, text="", foreground="gray")
        self.unsplash_status.grid(row=row, column=2, padx=(10, 0))
        
        # Unsplash help
        row += 1
        unsplash_help = ttk.Label(
            keys_frame,
            text="Get your key from: https://unsplash.com/developers (free, 50 requests/hour)",
            foreground="blue",
            cursor="hand2",
            font=('TkDefaultFont', 9)
        )
        unsplash_help.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 15))
        unsplash_help.bind("<Button-1>", lambda e: self._open_url("https://unsplash.com/developers"))
        
        # Show/Hide button for Unsplash key
        self.unsplash_show_btn = ttk.Button(
            keys_frame, text="👁", width=3,
            command=lambda: self._toggle_key_visibility(self.unsplash_entry, self.unsplash_show_btn)
        )
        self.unsplash_show_btn.grid(row=row-1, column=3, padx=(5, 0))
        
        # OpenAI API Key
        row += 1
        ttk.Label(keys_frame, text="OpenAI API Key:", font=('TkDefaultFont', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.openai_entry = ttk.Entry(keys_frame, width=50, show="*")
        self.openai_entry.grid(row=row, column=1, pady=(0, 5), padx=(10, 0), sticky="ew")
        
        # OpenAI status indicator
        self.openai_status = ttk.Label(keys_frame, text="", foreground="gray")
        self.openai_status.grid(row=row, column=2, padx=(10, 0))
        
        # OpenAI help
        row += 1
        openai_help = ttk.Label(
            keys_frame,
            text="Get your key from: https://platform.openai.com/api-keys (requires billing setup)",
            foreground="blue",
            cursor="hand2",
            font=('TkDefaultFont', 9)
        )
        openai_help.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 15))
        openai_help.bind("<Button-1>", lambda e: self._open_url("https://platform.openai.com/api-keys"))
        
        # Show/Hide button for OpenAI key
        self.openai_show_btn = ttk.Button(
            keys_frame, text="👁", width=3,
            command=lambda: self._toggle_key_visibility(self.openai_entry, self.openai_show_btn)
        )
        self.openai_show_btn.grid(row=row-1, column=3, padx=(5, 0))
        
        # Validation buttons
        row += 1
        validation_frame = ttk.Frame(keys_frame)
        validation_frame.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        
        self.validate_unsplash_btn = ttk.Button(
            validation_frame, text="Validate Unsplash Key",
            command=self._validate_unsplash_key
        )
        self.validate_unsplash_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.validate_openai_btn = ttk.Button(
            validation_frame, text="Validate OpenAI Key",
            command=self._validate_openai_key
        )
        self.validate_openai_btn.pack(side=tk.LEFT)
        
        self.validate_all_btn = ttk.Button(
            validation_frame, text="Validate All Keys",
            command=self._validate_all_keys,
            style="Accent.TButton"
        )
        self.validate_all_btn.pack(side=tk.RIGHT)
    
    def _create_model_section(self, parent):
        """Create GPT model selection section."""
        model_frame = ttk.LabelFrame(parent, text="GPT Model Selection", padding="15")
        model_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Model selection
        ttk.Label(model_frame, text="GPT Model:", font=('TkDefaultFont', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.model_var = tk.StringVar(value="gpt-4o-mini")
        model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
            state="readonly",
            width=20
        )
        model_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Model information
        model_info = ttk.Label(
            model_frame,
            text="gpt-4o-mini recommended (best value, ~$0.001 per description)",
            foreground="green",
            font=('TkDefaultFont', 9)
        )
        model_info.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
    
    def _create_validation_section(self, parent):
        """Create validation status section."""
        validation_frame = ttk.LabelFrame(parent, text="Validation Status", padding="15")
        validation_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Status text
        self.validation_status_text = tk.Text(
            validation_frame,
            height=6,
            width=70,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=('Consolas', 9)
        )
        self.validation_status_text.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(validation_frame, orient="vertical", command=self.validation_status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.validation_status_text.config(yscrollcommand=scrollbar.set)
        
        # Initial message
        self._update_validation_status("Ready to validate API keys. Enter your keys above and click validate.")
    
    def _create_action_buttons(self, parent):
        """Create action buttons section."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Left side buttons (help)
        left_frame = ttk.Frame(button_frame)
        left_frame.pack(side=tk.LEFT)
        
        help_btn = ttk.Button(left_frame, text="Help", command=self._show_help)
        help_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        tips_btn = ttk.Button(left_frame, text="Get API Keys", command=self._show_api_tips)
        tips_btn.pack(side=tk.LEFT)
        
        # Right side buttons (actions)
        right_frame = ttk.Frame(button_frame)
        right_frame.pack(side=tk.RIGHT)
        
        self.cancel_btn = ttk.Button(right_frame, text="Cancel", command=self._on_cancel)
        self.cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.save_btn = ttk.Button(
            right_frame, text="Save Configuration",
            command=self._save_configuration,
            style="Accent.TButton"
        )
        self.save_btn.pack(side=tk.RIGHT)
        self.save_btn.config(state=tk.DISABLED)  # Initially disabled
    
    def _create_progress_bar(self, parent):
        """Create progress bar for validation operations."""
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(
            parent,
            mode='indeterminate',
            variable=self.progress_var
        )
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        self.progress_bar.pack_forget()  # Initially hidden
    
    def _setup_bindings(self):
        """Setup event bindings."""
        # Real-time validation on key entry
        self.unsplash_entry.bind('<KeyRelease>', self._on_key_changed)
        self.openai_entry.bind('<KeyRelease>', self._on_key_changed)
        
        # Enter key validation
        self.unsplash_entry.bind('<Return>', lambda e: self._validate_unsplash_key())
        self.openai_entry.bind('<Return>', lambda e: self._validate_openai_key())
        
        # Model selection callback
        self.model_var.trace('w', self._on_model_changed)
    
    def _toggle_key_visibility(self, entry: ttk.Entry, button: ttk.Button):
        """Toggle visibility of API key in entry field."""
        current_show = entry.cget('show')
        if current_show == '*':
            entry.config(show='')
            button.config(text='🙈')
        else:
            entry.config(show='*')
            button.config(text='👁')
    
    def _open_url(self, url: str):
        """Open URL in default browser."""
        import webbrowser
        try:
            webbrowser.open(url)
        except Exception as e:
            logger.error(f"Failed to open URL {url}: {e}")
            messagebox.showerror("Error", f"Could not open URL: {url}")
    
    def _on_key_changed(self, event=None):
        """Handle key entry changes."""
        # Reset validation status for changed keys
        self.validation_results = {'unsplash': None, 'openai': None}
        self._update_save_button_state()
        
        # Clear status indicators
        self.unsplash_status.config(text="")
        self.openai_status.config(text="")
    
    def _on_model_changed(self, *args):
        """Handle model selection changes."""
        # If OpenAI key is validated, re-validate with new model
        if (self.validation_results['openai'] and 
            self.validation_results['openai'].is_valid):
            self._validate_openai_key()
    
    def _validate_unsplash_key(self):
        """Validate Unsplash API key."""
        key = self.unsplash_entry.get().strip()
        if not key:
            self._update_validation_status("❌ Unsplash key is empty")
            return
        
        if self.validation_in_progress['unsplash']:
            return
        
        self._update_validation_status("🔄 Validating Unsplash API key...")
        self.unsplash_status.config(text="⏳", foreground="orange")
        self.validate_unsplash_btn.config(state=tk.DISABLED)
        self.validation_in_progress['unsplash'] = True
        
        # Run validation in thread
        def validate():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.validator.validate_unsplash_key(key))
                loop.close()
                
                # Update UI in main thread
                self.after(0, lambda: self._on_unsplash_validation_complete(result))
            except Exception as e:
                error_result = ValidationResult(
                    status=ValidationStatus.UNKNOWN_ERROR,
                    message=f"Validation error: {str(e)}"
                )
                self.after(0, lambda: self._on_unsplash_validation_complete(error_result))
        
        threading.Thread(target=validate, daemon=True).start()
    
    def _validate_openai_key(self):
        """Validate OpenAI API key."""
        key = self.openai_entry.get().strip()
        model = self.model_var.get()
        
        if not key:
            self._update_validation_status("❌ OpenAI key is empty")
            return
        
        if self.validation_in_progress['openai']:
            return
        
        self._update_validation_status(f"🔄 Validating OpenAI API key with model {model}...")
        self.openai_status.config(text="⏳", foreground="orange")
        self.validate_openai_btn.config(state=tk.DISABLED)
        self.validation_in_progress['openai'] = True
        
        # Run validation in thread
        def validate():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.validator.validate_openai_key(key, model))
                loop.close()
                
                # Update UI in main thread
                self.after(0, lambda: self._on_openai_validation_complete(result))
            except Exception as e:
                error_result = ValidationResult(
                    status=ValidationStatus.UNKNOWN_ERROR,
                    message=f"Validation error: {str(e)}"
                )
                self.after(0, lambda: self._on_openai_validation_complete(error_result))
        
        threading.Thread(target=validate, daemon=True).start()
    
    def _validate_all_keys(self):
        """Validate all API keys concurrently."""
        unsplash_key = self.unsplash_entry.get().strip()
        openai_key = self.openai_entry.get().strip()
        model = self.model_var.get()
        
        if not unsplash_key or not openai_key:
            self._update_validation_status("❌ Both API keys must be entered")
            return
        
        self._update_validation_status("🔄 Validating all API keys...")
        self._show_progress()
        
        # Disable all validation buttons
        self.validate_unsplash_btn.config(state=tk.DISABLED)
        self.validate_openai_btn.config(state=tk.DISABLED)
        self.validate_all_btn.config(state=tk.DISABLED)
        
        # Update status indicators
        self.unsplash_status.config(text="⏳", foreground="orange")
        self.openai_status.config(text="⏳", foreground="orange")
        
        # Run validation in thread
        def validate():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(
                    self.validator.validate_all_keys(unsplash_key, openai_key, model)
                )
                loop.close()
                
                # Update UI in main thread
                self.after(0, lambda: self._on_all_validation_complete(results))
            except Exception as e:
                error_results = {
                    'unsplash': ValidationResult(
                        status=ValidationStatus.UNKNOWN_ERROR,
                        message=f"Validation error: {str(e)}"
                    ),
                    'openai': ValidationResult(
                        status=ValidationStatus.UNKNOWN_ERROR,
                        message=f"Validation error: {str(e)}"
                    )
                }
                self.after(0, lambda: self._on_all_validation_complete(error_results))
        
        threading.Thread(target=validate, daemon=True).start()
    
    def _on_unsplash_validation_complete(self, result: ValidationResult):
        """Handle Unsplash validation completion."""
        self.validation_results['unsplash'] = result
        self.validation_in_progress['unsplash'] = False
        self.validate_unsplash_btn.config(state=tk.NORMAL)
        
        if result.is_valid:
            self.unsplash_status.config(text="✅", foreground="green")
            self._update_validation_status(f"✅ Unsplash: {result.message}")
        else:
            self.unsplash_status.config(text="❌", foreground="red")
            self._update_validation_status(f"❌ Unsplash: {result.message}")
        
        self._update_save_button_state()
    
    def _on_openai_validation_complete(self, result: ValidationResult):
        """Handle OpenAI validation completion."""
        self.validation_results['openai'] = result
        self.validation_in_progress['openai'] = False
        self.validate_openai_btn.config(state=tk.NORMAL)
        
        if result.is_valid:
            self.openai_status.config(text="✅", foreground="green")
            self._update_validation_status(f"✅ OpenAI: {result.message}")
        else:
            self.openai_status.config(text="❌", foreground="red")
            self._update_validation_status(f"❌ OpenAI: {result.message}")
        
        self._update_save_button_state()
    
    def _on_all_validation_complete(self, results: Dict[str, ValidationResult]):
        """Handle completion of all validations."""
        self._hide_progress()
        
        # Update individual results
        self._on_unsplash_validation_complete(results['unsplash'])
        self._on_openai_validation_complete(results['openai'])
        
        # Enable validation buttons
        self.validate_all_btn.config(state=tk.NORMAL)
        
        # Summary message
        if all(result.is_valid for result in results.values()):
            self._update_validation_status("🎉 All API keys validated successfully! Ready to save configuration.")
        else:
            failed_services = [service for service, result in results.items() if not result.is_valid]
            self._update_validation_status(f"❌ Validation failed for: {', '.join(failed_services)}")
    
    def _update_validation_status(self, message: str):
        """Update validation status text."""
        self.validation_status_text.config(state=tk.NORMAL)
        self.validation_status_text.insert(tk.END, f"{message}\n")
        self.validation_status_text.see(tk.END)
        self.validation_status_text.config(state=tk.DISABLED)
    
    def _update_save_button_state(self):
        """Update save button state based on validation results."""
        all_valid = (
            self.validation_results['unsplash'] and 
            self.validation_results['openai'] and
            self.validation_results['unsplash'].is_valid and 
            self.validation_results['openai'].is_valid
        )
        
        if all_valid:
            self.save_btn.config(state=tk.NORMAL)
        else:
            self.save_btn.config(state=tk.DISABLED)
    
    def _show_progress(self):
        """Show progress bar."""
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        self.progress_bar.start(10)
    
    def _hide_progress(self):
        """Hide progress bar."""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
    
    def _save_configuration(self):
        """Save the validated configuration."""
        if not all(result.is_valid for result in self.validation_results.values() if result):
            messagebox.showerror("Error", "Please validate all API keys before saving.")
            return
        
        try:
            self._show_progress()
            self.save_btn.config(state=tk.DISABLED)
            
            api_keys = {
                'unsplash_access_key': self.unsplash_entry.get().strip(),
                'openai_api_key': self.openai_entry.get().strip(),
                'gpt_model': self.model_var.get()
            }
            
            # Save configuration in thread to avoid blocking UI
            def save():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    success = loop.run_until_complete(
                        self.config_manager.save_configuration(
                            api_keys=api_keys,
                            validate_keys=False  # Already validated
                        )
                    )
                    loop.close()
                    
                    self.after(0, lambda: self._on_save_complete(success))
                except Exception as e:
                    logger.error(f"Save configuration error: {e}")
                    self.after(0, lambda: self._on_save_complete(False, str(e)))
            
            threading.Thread(target=save, daemon=True).start()
            
        except Exception as e:
            self._hide_progress()
            self.save_btn.config(state=tk.NORMAL)
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def _on_save_complete(self, success: bool, error_msg: str = ""):
        """Handle save completion."""
        self._hide_progress()
        self.save_btn.config(state=tk.NORMAL)
        
        if success:
            self.setup_complete = True
            messagebox.showinfo("Success", 
                "Configuration saved successfully!\n\n"
                "Your API keys are securely encrypted and stored in your user profile.\n"
                "The application is now ready to use."
            )
            
            if self.on_success:
                self.on_success()
            
            self.destroy()
        else:
            error_message = f"Failed to save configuration."
            if error_msg:
                error_message += f"\n\nError: {error_msg}"
            messagebox.showerror("Save Failed", error_message)
    
    def _load_existing_config(self):
        """Load existing configuration if available."""
        try:
            if not self.config_manager.is_first_run():
                api_keys = self.config_manager.get_api_keys()
                if api_keys['unsplash']:
                    self.unsplash_entry.insert(0, api_keys['unsplash'])
                if api_keys['openai']:
                    self.openai_entry.insert(0, api_keys['openai'])
                if api_keys['gpt_model']:
                    self.model_var.set(api_keys['gpt_model'])
                
                self._update_validation_status("Loaded existing configuration. Please re-validate keys to continue.")
        except Exception as e:
            logger.error(f"Error loading existing config: {e}")
    
    def _show_help(self):
        """Show help dialog."""
        help_text = """
SECURE API CONFIGURATION HELP

This wizard helps you configure API keys securely:

🔐 SECURITY FEATURES:
• Keys are encrypted using Windows DPAPI
• No keys are stored in the application
• Keys are saved in your user profile only
• Automatic backup and recovery

🔑 API KEYS NEEDED:
• Unsplash: For image search (free tier: 50 requests/hour)
• OpenAI: For AI descriptions (requires billing setup)

✅ VALIDATION:
• Keys are tested before saving
• Real-time feedback on key validity
• Model compatibility checking

💡 TIPS:
• Use the "Get API Keys" button for registration links
• Start with gpt-4o-mini for cost efficiency
• Validation requires internet connection
        """
        
        messagebox.showinfo("Help", help_text.strip())
    
    def _show_api_tips(self):
        """Show API key acquisition tips."""
        tips_window = tk.Toplevel(self)
        tips_window.title("How to Get API Keys")
        tips_window.geometry("600x400")
        tips_window.transient(self)
        
        notebook = ttk.Notebook(tips_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Unsplash tab
        unsplash_frame = ttk.Frame(notebook)
        notebook.add(unsplash_frame, text="Unsplash API")
        
        unsplash_text = tk.Text(unsplash_frame, wrap=tk.WORD, padx=10, pady=10)
        unsplash_text.pack(fill=tk.BOTH, expand=True)
        unsplash_text.insert(tk.END, self.validator.get_validation_tips('unsplash'))
        unsplash_text.config(state=tk.DISABLED)
        
        # OpenAI tab
        openai_frame = ttk.Frame(notebook)
        notebook.add(openai_frame, text="OpenAI API")
        
        openai_text = tk.Text(openai_frame, wrap=tk.WORD, padx=10, pady=10)
        openai_text.pack(fill=tk.BOTH, expand=True)
        openai_text.insert(tk.END, self.validator.get_validation_tips('openai'))
        openai_text.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(tips_window, text="Close", command=tips_window.destroy).pack(pady=10)
    
    def _center_window(self):
        """Center the window on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _on_cancel(self):
        """Handle cancel button click."""
        if self.setup_complete:
            self.destroy()
            return
        
        result = messagebox.askyesno(
            "Cancel Setup",
            "Are you sure you want to cancel the setup?\n\n"
            "The application requires API keys to function properly.",
            parent=self
        )
        
        if result:
            self.destroy()
    
    def _on_close(self):
        """Handle window close event."""
        self._on_cancel()


def ensure_secure_configuration(parent_window: Optional[tk.Tk] = None) -> Optional[SecureConfigManager]:
    """
    Ensure API keys are configured securely, show setup wizard if needed.
    
    Args:
        parent_window: Parent window for the setup wizard
        
    Returns:
        Configured SecureConfigManager or None if setup was cancelled
    """
    config_manager = SecureConfigManager()
    
    if not config_manager.validate_api_keys():
        if parent_window is None:
            root = tk.Tk()
            root.withdraw()
            parent = root
            cleanup_root = True
        else:
            parent = parent_window
            cleanup_root = False
        
        wizard = SecureSetupWizard(parent, config_manager)
        parent.wait_window(wizard)
        
        if cleanup_root:
            root.destroy()
        
        if not wizard.setup_complete:
            return None
        
        # Reload configuration after setup
        config_manager = SecureConfigManager()
    
    return config_manager