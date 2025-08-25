"""
Enhanced Setup wizard dialog with comprehensive UX improvements.
Includes real-time validation, test connections, accessibility features, and clear guidance.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import threading
import requests
from typing import Callable, Optional


class EnhancedSetupWizard(tk.Toplevel):
    """Enhanced setup wizard with comprehensive UX improvements."""
    
    def __init__(self, parent, config_manager, theme_manager=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.theme_manager = theme_manager
        
        # Validation states
        self.unsplash_valid = False
        self.openai_valid = False
        self.testing_keys = False
        
        self._setup_window()
        self._create_widgets()
        self._load_existing_keys()
        self._setup_keyboard_navigation()
        
        # Center window
        self._center_window()
        
        self.result = False
    
    def _setup_window(self):
        """Configure main window properties."""
        self.title("API Configuration - Enhanced Setup")
        self.geometry("700x650")
        self.resizable(True, True)
        self.minsize(600, 500)
        
        # Make modal
        self.transient(self.master)
        self.grab_set()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)
    
    def _center_window(self):
        """Center the window on screen."""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.winfo_screenheight() // 2) - (650 // 2)
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create the enhanced setup wizard UI."""
        # Main container with scrolling
        self._create_main_container()
        
        # Header
        self._create_header()
        
        # Instructions
        self._create_instructions()
        
        # API Keys section
        self._create_api_keys_section()
        
        # Buttons
        self._create_buttons()
        
        # Status bar
        self._create_status_bar()
    
    def _create_main_container(self):
        """Create main scrollable container."""
        # Create canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack scrolling components
        self.canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        self.scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        self._bind_mousewheel()
    
    def _bind_mousewheel(self):
        """Enable mouse wheel scrolling."""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.bind("<MouseWheel>", _on_mousewheel)
        self.canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def _create_header(self):
        """Create wizard header."""
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Icon
        icon_label = tk.Label(
            header_frame,
            text="🔑",
            font=('TkDefaultFont', 32)
        )
        icon_label.pack()
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="API Configuration Setup",
            font=('TkDefaultFont', 18, 'bold')
        )
        title_label.pack(pady=(5, 0))
        
        # Subtitle
        subtitle_label = ttk.Label(
            header_frame,
            text="Configure your API keys for the best experience"
        )
        subtitle_label.pack(pady=(5, 0))
    
    def _create_instructions(self):
        """Create instructions section."""
        instructions_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="What You Need",
            padding="15"
        )
        instructions_frame.pack(fill=tk.X, pady=(0, 20))
        
        instructions_text = '''This application requires API keys from two services:

🖼️  Unsplash API - For searching high-quality images
    • Free tier: 50 requests per hour  
    • Required for image search functionality
    
🤖  OpenAI API - For AI-powered descriptions and translations  
    • Supports multiple GPT models
    • Pay-per-use pricing (very affordable for learning)

✅  Both services offer generous free tiers to get you started
🔒  Your keys are stored locally and never shared
📋  You can reconfigure these keys anytime in Settings'''
        
        instructions_label = ttk.Label(
            instructions_frame,
            text=instructions_text,
            justify=tk.LEFT,
            wraplength=600
        )
        instructions_label.pack(anchor=tk.W)
    
    def _create_api_keys_section(self):
        """Create API keys configuration section."""
        keys_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="API Keys Configuration",
            padding="15"
        )
        keys_frame.pack(fill=tk.X, pady=(0, 20))
        keys_frame.columnconfigure(0, weight=1)
        
        # Unsplash section
        self._create_unsplash_section(keys_frame)
        
        # Separator
        ttk.Separator(keys_frame, orient=tk.HORIZONTAL).grid(
            row=10, column=0, columnspan=2, sticky="ew", pady=20
        )
        
        # OpenAI section
        self._create_openai_section(keys_frame)
    
    def _create_unsplash_section(self, parent):
        """Create Unsplash API key section."""
        # Header
        unsplash_header = ttk.Label(
            parent,
            text="🖼️ Unsplash API Configuration",
            font=('TkDefaultFont', 12, 'bold')
        )
        unsplash_header.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Label with requirements
        label_frame = ttk.Frame(parent)
        label_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        label_frame.columnconfigure(1, weight=1)
        
        ttk.Label(
            label_frame,
            text="Access Key:",
            font=('TkDefaultFont', 10, 'bold')
        ).grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(
            label_frame,
            text="*Required - Should be 20+ characters",
            foreground="gray"
        ).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Entry with test button
        entry_frame = ttk.Frame(parent)
        entry_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        entry_frame.columnconfigure(0, weight=1)
        
        self.unsplash_entry = ttk.Entry(entry_frame, font=('TkDefaultFont', 10), show="*")
        self.unsplash_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.unsplash_entry.bind('<KeyRelease>', self._on_unsplash_change)
        self.unsplash_entry.bind('<Return>', lambda e: self._test_unsplash_key())
        self.unsplash_entry.bind('<FocusIn>', self._on_focus_in)
        self.unsplash_entry.bind('<FocusOut>', self._on_focus_out)
        
        self.test_unsplash_btn = ttk.Button(
            entry_frame,
            text="🔗 Test",
            command=self._test_unsplash_key,
            width=10
        )
        self.test_unsplash_btn.grid(row=0, column=1)
        
        # Controls frame
        controls_frame = ttk.Frame(parent)
        controls_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        controls_frame.columnconfigure(1, weight=1)
        
        # Show key checkbox
        self.unsplash_show_var = tk.BooleanVar()
        show_unsplash = ttk.Checkbutton(
            controls_frame,
            text="Show key",
            variable=self.unsplash_show_var,
            command=lambda: self.unsplash_entry.config(
                show="" if self.unsplash_show_var.get() else "*"
            )
        )
        show_unsplash.grid(row=0, column=0, sticky=tk.W)
        
        # Status
        self.unsplash_status = ttk.Label(
            controls_frame,
            text="Enter your key and click Test",
            foreground="gray"
        )
        self.unsplash_status.grid(row=0, column=1, sticky=tk.E)
        
        # Help text
        help_text = ttk.Label(
            parent,
            text="💡 Get your free API key at: https://unsplash.com/developers",
            foreground="blue",
            cursor="hand2"
        )
        help_text.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        help_text.bind("<Button-1>", lambda e: webbrowser.open("https://unsplash.com/developers"))
    
    def _create_openai_section(self, parent):
        """Create OpenAI API key section."""
        # Header
        openai_header = ttk.Label(
            parent,
            text="🤖 OpenAI API Configuration",
            font=('TkDefaultFont', 12, 'bold')
        )
        openai_header.grid(row=11, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Label with requirements
        label_frame = ttk.Frame(parent)
        label_frame.grid(row=12, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        label_frame.columnconfigure(1, weight=1)
        
        ttk.Label(
            label_frame,
            text="Secret Key:",
            font=('TkDefaultFont', 10, 'bold')
        ).grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(
            label_frame,
            text="*Required - Must start with 'sk-'",
            foreground="gray"
        ).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Entry with test button
        entry_frame = ttk.Frame(parent)
        entry_frame.grid(row=13, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        entry_frame.columnconfigure(0, weight=1)
        
        self.openai_entry = ttk.Entry(entry_frame, font=('TkDefaultFont', 10), show="*")
        self.openai_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.openai_entry.bind('<KeyRelease>', self._on_openai_change)
        self.openai_entry.bind('<Return>', lambda e: self._test_openai_key())
        self.openai_entry.bind('<FocusIn>', self._on_focus_in)
        self.openai_entry.bind('<FocusOut>', self._on_focus_out)
        
        self.test_openai_btn = ttk.Button(
            entry_frame,
            text="🔗 Test",
            command=self._test_openai_key,
            width=10
        )
        self.test_openai_btn.grid(row=0, column=1)
        
        # Controls frame
        controls_frame = ttk.Frame(parent)
        controls_frame.grid(row=14, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        controls_frame.columnconfigure(1, weight=1)
        
        # Show key checkbox
        self.openai_show_var = tk.BooleanVar()
        show_openai = ttk.Checkbutton(
            controls_frame,
            text="Show key",
            variable=self.openai_show_var,
            command=lambda: self.openai_entry.config(
                show="" if self.openai_show_var.get() else "*"
            )
        )
        show_openai.grid(row=0, column=0, sticky=tk.W)
        
        # Status
        self.openai_status = ttk.Label(
            controls_frame,
            text="Enter your key and click Test",
            foreground="gray"
        )
        self.openai_status.grid(row=0, column=1, sticky=tk.E)
        
        # Model selection
        model_frame = ttk.Frame(parent)
        model_frame.grid(row=15, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        model_frame.columnconfigure(1, weight=1)
        
        ttk.Label(
            model_frame,
            text="GPT Model:",
            font=('TkDefaultFont', 10, 'bold')
        ).grid(row=0, column=0, sticky=tk.W)
        
        self.model_var = tk.StringVar(value="gpt-4o-mini")
        model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
            state="readonly",
            width=20
        )
        model_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        model_combo.bind('<<ComboboxSelected>>', self._on_model_change)
        
        # Model info
        self.model_info = ttk.Label(
            parent,
            text="💰 Most affordable - great for learning Spanish",
            foreground="green"
        )
        self.model_info.grid(row=16, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Help text
        help_text = ttk.Label(
            parent,
            text="💡 Get your API key at: https://platform.openai.com/api-keys",
            foreground="blue",
            cursor="hand2"
        )
        help_text.grid(row=17, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        help_text.bind("<Button-1>", lambda e: webbrowser.open("https://platform.openai.com/api-keys"))
    
    def _create_buttons(self):
        """Create action buttons."""
        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.pack(fill=tk.X, pady=(20, 10))
        
        # Help button
        help_btn = ttk.Button(
            button_frame,
            text="❓ Need Help?",
            command=self._show_help
        )
        help_btn.pack(side=tk.LEFT)
        
        # Right side buttons
        right_frame = ttk.Frame(button_frame)
        right_frame.pack(side=tk.RIGHT)
        
        # Skip button
        skip_btn = ttk.Button(
            right_frame,
            text="Skip for Now",
            command=self._skip_setup
        )
        skip_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Save button
        self.save_btn = ttk.Button(
            right_frame,
            text="💾 Save & Continue",
            command=self.save_and_continue
        )
        self.save_btn.pack(side=tk.LEFT)
    
    def _create_status_bar(self):
        """Create status bar."""
        self.status_frame = ttk.Frame(self.scrollable_frame)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Overall status
        self.overall_status = ttk.Label(
            self.status_frame,
            text="🔧 Enter your API keys to get started",
            foreground="blue"
        )
        self.overall_status.pack(side=tk.LEFT)
        
        # Keyboard shortcut hint
        shortcut_hint = ttk.Label(
            self.status_frame,
            text="💡 Tab: Navigate • Enter: Test • Escape: Cancel",
            foreground="gray",
            font=('TkDefaultFont', 8)
        )
        shortcut_hint.pack(side=tk.RIGHT)
    
    def _setup_keyboard_navigation(self):
        """Setup keyboard shortcuts."""
        self.bind('<Escape>', lambda e: self._skip_setup())
        self.bind('<F1>', lambda e: self._show_help())
        
        # Tab order
        self.unsplash_entry.bind('<Tab>', self._focus_next)
        self.test_unsplash_btn.bind('<Tab>', self._focus_next)
        self.openai_entry.bind('<Tab>', self._focus_next)
        self.test_openai_btn.bind('<Tab>', self._focus_next)
    
    def _focus_next(self, event):
        """Handle tab key navigation."""
        event.widget.tk_focusNext().focus()
        return "break"
    
    def _on_focus_in(self, event):
        """Handle focus in events."""
        widget = event.widget
        widget.selection_range(0, tk.END)
    
    def _on_focus_out(self, event):
        """Handle focus out events."""
        pass
    
    def _on_unsplash_change(self, event=None):
        """Handle Unsplash key changes."""
        self.unsplash_valid = False
        key = self.unsplash_entry.get().strip()
        
        if not key:
            self.unsplash_status.config(text="Enter your key and click Test", foreground="gray")
        elif len(key) < 20:
            self.unsplash_status.config(text="⚠️ Key seems too short", foreground="orange")
        else:
            self.unsplash_status.config(text="Ready to test", foreground="blue")
        
        self._update_overall_status()
    
    def _on_openai_change(self, event=None):
        """Handle OpenAI key changes."""
        self.openai_valid = False
        key = self.openai_entry.get().strip()
        
        if not key:
            self.openai_status.config(text="Enter your key and click Test", foreground="gray")
        elif not key.startswith('sk-'):
            self.openai_status.config(text="⚠️ Should start with 'sk-'", foreground="orange")
        elif len(key) < 40:
            self.openai_status.config(text="⚠️ Key seems too short", foreground="orange")
        else:
            self.openai_status.config(text="Ready to test", foreground="blue")
        
        self._update_overall_status()
    
    def _on_model_change(self, event=None):
        """Handle model selection changes."""
        model = self.model_var.get()
        
        model_info = {
            "gpt-4o-mini": ("💰 Most affordable - great for learning", "green"),
            "gpt-4o": ("🚀 Best performance - higher cost", "blue"),
            "gpt-4-turbo": ("⚡ Fast and capable - moderate cost", "blue"),
            "gpt-3.5-turbo": ("🏃 Fast and cheap - basic capability", "green")
        }
        
        text, color = model_info.get(model, ("", "gray"))
        self.model_info.config(text=text, foreground=color)
    
    def _update_overall_status(self):
        """Update the overall status message."""
        if self.unsplash_valid and self.openai_valid:
            self.overall_status.config(
                text="✅ Ready to go! Click Save & Continue",
                foreground="green"
            )
            self.save_btn.config(text="✅ Save & Continue")
        elif self.testing_keys:
            self.overall_status.config(
                text="🔄 Testing connection...",
                foreground="blue"
            )
        elif self.unsplash_valid:
            self.overall_status.config(
                text="🔧 Unsplash ready, test OpenAI key",
                foreground="orange"
            )
        elif self.openai_valid:
            self.overall_status.config(
                text="🔧 OpenAI ready, test Unsplash key",
                foreground="orange"
            )
        else:
            self.overall_status.config(
                text="🔧 Enter your API keys to get started",
                foreground="blue"
            )
    
    def _test_unsplash_key(self):
        """Test Unsplash API key."""
        key = self.unsplash_entry.get().strip()
        if not key:
            self.unsplash_status.config(text="❌ Please enter a key", foreground="red")
            return
        
        self.testing_keys = True
        self._update_overall_status()
        self.unsplash_status.config(text="🔄 Testing connection...", foreground="blue")
        self.test_unsplash_btn.config(state="disabled", text="Testing...")
        
        # Test in background thread
        threading.Thread(target=self._do_unsplash_test, args=(key,), daemon=True).start()
    
    def _do_unsplash_test(self, key):
        """Perform Unsplash API test."""
        try:
            headers = {"Authorization": f"Client-ID {key}"}
            response = requests.get(
                "https://api.unsplash.com/photos/random",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.unsplash_valid = True
                message = "✅ Connection successful!"
                color = "green"
            else:
                message = f"❌ Invalid key (Status: {response.status_code})"
                color = "red"
                
        except Exception as e:
            message = f"❌ Connection failed: {str(e)[:30]}..."
            color = "red"
        
        # Update UI on main thread
        self.after(0, lambda: self._update_unsplash_test_result(message, color))
    
    def _update_unsplash_test_result(self, message, color):
        """Update Unsplash test result."""
        self.unsplash_status.config(text=message, foreground=color)
        self.test_unsplash_btn.config(state="normal", text="✅ Test" if self.unsplash_valid else "🔗 Test")
        self.testing_keys = False
        self._update_overall_status()
    
    def _test_openai_key(self):
        """Test OpenAI API key."""
        key = self.openai_entry.get().strip()
        if not key:
            self.openai_status.config(text="❌ Please enter a key", foreground="red")
            return
        
        self.testing_keys = True
        self._update_overall_status()
        self.openai_status.config(text="🔄 Testing connection...", foreground="blue")
        self.test_openai_btn.config(state="disabled", text="Testing...")
        
        # Test in background thread
        threading.Thread(target=self._do_openai_test, args=(key,), daemon=True).start()
    
    def _do_openai_test(self, key):
        """Perform OpenAI API test."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=key)
            
            # Simple test call
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            if response.choices:
                self.openai_valid = True
                message = "✅ Connection successful!"
                color = "green"
            else:
                message = "❌ Unexpected response"
                color = "red"
                
        except Exception as e:
            error_msg = str(e).lower()
            if "api_key" in error_msg or "authentication" in error_msg:
                message = "❌ Invalid API key"
            elif "quota" in error_msg or "billing" in error_msg:
                message = "❌ Quota exceeded or billing issue"
            else:
                message = f"❌ Error: {str(e)[:30]}..."
            color = "red"
        
        # Update UI on main thread
        self.after(0, lambda: self._update_openai_test_result(message, color))
    
    def _update_openai_test_result(self, message, color):
        """Update OpenAI test result."""
        self.openai_status.config(text=message, foreground=color)
        self.test_openai_btn.config(state="normal", text="✅ Test" if self.openai_valid else "🔗 Test")
        self.testing_keys = False
        self._update_overall_status()
    
    def _load_existing_keys(self):
        """Load existing API keys if available."""
        try:
            keys = self.config_manager.get_api_keys()
            if keys.get('unsplash'):
                self.unsplash_entry.insert(0, keys['unsplash'])
                self.unsplash_valid = True
                self.unsplash_status.config(text="✅ Previously configured", foreground="green")
            
            if keys.get('openai'):
                self.openai_entry.insert(0, keys['openai'])
                self.openai_valid = True
                self.openai_status.config(text="✅ Previously configured", foreground="green")
            
            if keys.get('gpt_model'):
                self.model_var.set(keys['gpt_model'])
            
            self._update_overall_status()
            
        except Exception:
            pass  # Keys not found, that's fine
    
    def _show_help(self):
        """Show help dialog."""
        help_text = '''🔑 API Key Setup Help

🖼️ UNSPLASH API KEY:
• Go to https://unsplash.com/developers
• Click "Create an Application"
• Fill out the form (personal use is fine)
• Copy your "Access Key" (NOT the Secret Key)
• Free tier: 50 requests per hour

🤖 OPENAI API KEY:
• Go to https://platform.openai.com/api-keys
• Sign in to your OpenAI account
• Click "Create new secret key"
• Copy the key immediately (starts with "sk-")
• You need billing enabled for API access

💰 COSTS:
• Unsplash: Free tier is generous
• OpenAI: Pay per use, very affordable for learning
  - gpt-4o-mini: ~$0.15 per 1M tokens (cheapest)
  - gpt-4o: ~$5 per 1M tokens (best quality)

🔒 SECURITY:
• Your keys are stored locally only
• Never share your API keys with anyone
• You can change them anytime in Settings

❓ NEED MORE HELP?
Check the documentation or contact support.'''
        
        messagebox.showinfo("API Key Setup Help", help_text, parent=self)
    
    def save_and_continue(self):
        """Validate and save API keys."""
        unsplash_key = self.unsplash_entry.get().strip()
        openai_key = self.openai_entry.get().strip()
        gpt_model = self.model_var.get()
        
        # Validation
        if not unsplash_key:
            messagebox.showerror(
                "Missing Unsplash Key",
                "Please enter your Unsplash API key.\n\nGet it from: https://unsplash.com/developers",
                parent=self
            )
            self.unsplash_entry.focus()
            return
        
        if not openai_key:
            messagebox.showerror(
                "Missing OpenAI Key", 
                "Please enter your OpenAI API key.\n\nGet it from: https://platform.openai.com/api-keys",
                parent=self
            )
            self.openai_entry.focus()
            return
        
        # Recommend testing if not done
        if not self.unsplash_valid or not self.openai_valid:
            result = messagebox.askyesno(
                "Keys Not Tested",
                "You haven't tested your API keys yet. They might not work.\n\n" +
                "Do you want to save them anyway?",
                parent=self
            )
            if not result:
                return
        
        try:
            # Save keys
            self.config_manager.save_api_keys(unsplash_key, openai_key, gpt_model)
            self.result = True
            messagebox.showinfo(
                "Setup Complete",
                "API keys saved successfully!\n\nYou're ready to start learning Spanish with AI-powered image descriptions.",
                parent=self
            )
            self.destroy()
            
        except Exception as e:
            messagebox.showerror(
                "Save Error",
                f"Failed to save API keys: {e}\n\nPlease try again.",
                parent=self
            )
    
    def _skip_setup(self):
        """Skip the setup wizard."""
        result = messagebox.askyesno(
            "Skip Setup",
            "Are you sure you want to skip API setup?\n\n" +
            "The app won't work without valid API keys, but you can " +
            "configure them later in Settings.",
            parent=self
        )
        
        if result:
            self.result = False
            self.destroy()
    
    def _on_window_close(self):
        """Handle window close event."""
        self._skip_setup()


def ensure_api_keys_configured_enhanced(parent_window=None, config_manager=None, theme_manager=None):
    """Ensure API keys are configured using enhanced wizard."""
    if config_manager is None:
        from ...config.secure_config_manager import SecureConfigManager
        config_manager = SecureConfigManager()
    
    if not config_manager.validate_api_keys():
        if parent_window is None:
            root = tk.Tk()
            root.withdraw()
            parent = root
        else:
            parent = parent_window
        
        wizard = EnhancedSetupWizard(parent, config_manager, theme_manager)
        parent.wait_window(wizard)
        
        if parent_window is None:
            root.destroy()
        
        if not wizard.result:
            return None
        
        # Reload config after wizard
        config_manager = SecureConfigManager() if config_manager is None else config_manager
    
    return config_manager