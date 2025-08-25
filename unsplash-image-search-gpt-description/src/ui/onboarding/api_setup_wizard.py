"""
API Key Setup Wizard with comprehensive help and guidance
Helps users configure their API keys with videos, GIFs, and step-by-step instructions
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from typing import Callable, Optional, Dict, Any
import re
import requests
from pathlib import Path
import base64


class APISetupWizard:
    """
    Comprehensive wizard for setting up API keys with help content
    """
    
    def __init__(self, parent: tk.Tk, theme_manager, config_manager,
                 on_completion: Callable = None, on_skip: Callable = None):
        self.parent = parent
        self.theme_manager = theme_manager
        self.config_manager = config_manager
        self.on_completion = on_completion
        self.on_skip = on_skip
        
        self.wizard_window = None
        self.current_page = 0
        self.total_pages = 4
        
        # API key validation status
        self.unsplash_valid = False
        self.openai_valid = False
        
        # Form fields
        self.unsplash_entry = None
        self.openai_entry = None
        self.gpt_model_var = None
        
        # Help content
        self.help_content = {
            'unsplash': {
                'title': 'How to Get Your Unsplash API Key',
                'steps': [
                    '1. Go to https://unsplash.com/developers',
                    '2. Click "Create an Application"',
                    '3. Sign in or create an Unsplash account',
                    '4. Fill out the application form',
                    '5. Copy your "Access Key"',
                    '6. Paste it in the field below'
                ],
                'url': 'https://unsplash.com/developers',
                'docs_url': 'https://unsplash.com/documentation',
                'signup_url': 'https://unsplash.com/join',
                'tips': [
                    'Free tier provides 50 requests per hour',
                    'You only need the "Access Key", not the "Secret Key"',
                    'Keep your key private and never share it'
                ]
            },
            'openai': {
                'title': 'How to Get Your OpenAI API Key',
                'steps': [
                    '1. Go to https://platform.openai.com/api-keys',
                    '2. Sign in to your OpenAI account',
                    '3. Click "Create new secret key"',
                    '4. Name your key (e.g., "Spanish Learning App")',
                    '5. Copy the generated key immediately',
                    '6. Paste it in the field below'
                ],
                'url': 'https://platform.openai.com/api-keys',
                'docs_url': 'https://platform.openai.com/docs',
                'billing_url': 'https://platform.openai.com/account/billing',
                'tips': [
                    'GPT-4 Vision is recommended for image analysis',
                    'You need billing set up for API access',
                    'Keys start with "sk-" followed by random characters',
                    'Never share your API key with anyone'
                ]
            }
        }
    
    def show(self):
        """Display the API setup wizard"""
        if self.wizard_window:
            self.wizard_window.lift()
            return
        
        colors = self.theme_manager.get_colors()
        
        # Create wizard window with enhanced properties
        self.wizard_window = tk.Toplevel(self.parent)
        self.wizard_window.title("API Setup Wizard - Spanish Learning Tool")
        self.wizard_window.geometry("700x600")
        self.wizard_window.minsize(600, 500)  # Minimum size for usability
        self.wizard_window.configure(bg=colors['bg'])
        self.wizard_window.resizable(True, True)
        self.wizard_window.transient(self.parent)
        self.wizard_window.grab_set()
        
        # Enhanced window attributes
        try:
            # Set window icon if available
            if hasattr(self.parent, 'iconbitmap'):
                self.wizard_window.iconbitmap(self.parent.iconbitmap())
        except:
            pass
        
        # Center window
        self.wizard_window.update_idletasks()
        x = (self.wizard_window.winfo_screenwidth() // 2) - 350
        y = (self.wizard_window.winfo_screenheight() // 2) - 300
        self.wizard_window.geometry(f"+{x}+{y}")
        
        # Prevent closing with X button
        self.wizard_window.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        self._create_wizard_widgets()
        self._show_page(0)
    
    def _create_wizard_widgets(self):
        """Create the wizard interface"""
        colors = self.theme_manager.get_colors()
        
        # Main container with scrolling
        main_canvas = tk.Canvas(
            self.wizard_window,
            bg=colors['bg'],
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            self.wizard_window,
            orient="vertical",
            command=main_canvas.yview
        )
        self.scrollable_frame = tk.Frame(main_canvas, bg=colors['bg'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrolling components
        main_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Header
        self._create_header()
        
        # Content area (will be populated by pages)
        self.content_frame = tk.Frame(self.scrollable_frame, bg=colors['bg'])
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Progress bar
        self._create_progress_bar()
        
        # Navigation buttons
        self._create_navigation()
        
        # Enable mouse wheel scrolling
        self._bind_mousewheel()
        
        # Add keyboard shortcuts
        self._setup_keyboard_shortcuts()
        
        # Set initial focus
        self.wizard_window.after(100, self._set_initial_focus)
    
    def _create_header(self):
        """Create the wizard header"""
        colors = self.theme_manager.get_colors()
        
        header_frame = tk.Frame(self.scrollable_frame, bg=colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Icon
        icon_label = tk.Label(
            header_frame,
            text="🔑",
            font=('TkDefaultFont', 32),
            bg=colors['bg'],
            fg=colors['info']
        )
        icon_label.pack()
        
        # Title
        self.title_label = tk.Label(
            header_frame,
            text="API Key Setup",
            font=('TkDefaultFont', 18, 'bold'),
            bg=colors['bg'],
            fg=colors['fg']
        )
        self.title_label.pack(pady=(5, 0))
        
        # Subtitle
        self.subtitle_label = tk.Label(
            header_frame,
            text="Let's configure your API keys for the best experience",
            font=('TkDefaultFont', 10),
            bg=colors['bg'],
            fg=colors['disabled_fg']
        )
        self.subtitle_label.pack(pady=(5, 0))
    
    def _create_progress_bar(self):
        """Create progress indicator"""
        colors = self.theme_manager.get_colors()
        
        progress_frame = tk.Frame(self.scrollable_frame, bg=colors['bg'])
        progress_frame.pack(fill=tk.X, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400
        )
        self.progress.pack()
        
        # Progress text
        self.progress_text = tk.Label(
            progress_frame,
            text="Step 1 of 4",
            font=('TkDefaultFont', 9),
            bg=colors['bg'],
            fg=colors['disabled_fg']
        )
        self.progress_text.pack(pady=(5, 0))
    
    def _create_navigation(self):
        """Create navigation buttons"""
        colors = self.theme_manager.get_colors()
        
        nav_frame = tk.Frame(self.scrollable_frame, bg=colors['bg'])
        nav_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Skip button
        self.skip_button = tk.Button(
            nav_frame,
            text="Skip Setup",
            command=self._skip_setup,
            font=('TkDefaultFont', 10),
            bg=colors['button_bg'],
            fg=colors['disabled_fg'],
            relief=tk.FLAT,
            padx=20
        )
        self.skip_button.pack(side=tk.LEFT)
        
        # Right navigation
        right_nav = tk.Frame(nav_frame, bg=colors['bg'])
        right_nav.pack(side=tk.RIGHT)
        
        # Back button
        self.back_button = tk.Button(
            right_nav,
            text="← Back",
            command=self._previous_page,
            font=('TkDefaultFont', 10),
            bg=colors['button_bg'],
            fg=colors['button_fg'],
            relief=tk.FLAT,
            padx=20
        )
        self.back_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Next button
        self.next_button = tk.Button(
            right_nav,
            text="Next →",
            command=self._next_page,
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['select_bg'],
            fg=colors['select_fg'],
            relief=tk.FLAT,
            padx=20
        )
        self.next_button.pack(side=tk.LEFT)
    
    def _bind_mousewheel(self):
        """Enable mouse wheel scrolling with cross-platform support"""
        def _on_mousewheel(event):
            try:
                canvas = self.wizard_window.winfo_children()[0]  # main_canvas
                # Windows
                if event.delta:
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                # Linux
                elif event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")
            except:
                pass  # Ignore scrolling errors
        
        self.wizard_window.bind("<MouseWheel>", _on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # Linux mouse wheel support
        self.wizard_window.bind("<Button-4>", _on_mousewheel)
        self.wizard_window.bind("<Button-5>", _on_mousewheel)
        self.scrollable_frame.bind("<Button-4>", _on_mousewheel)
        self.scrollable_frame.bind("<Button-5>", _on_mousewheel)
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for accessibility"""
        # Global shortcuts
        self.wizard_window.bind('<Escape>', lambda e: self._skip_setup())
        self.wizard_window.bind('<F1>', lambda e: self._show_detailed_help('general'))
        self.wizard_window.bind('<Control-h>', lambda e: self._show_detailed_help('general'))
        self.wizard_window.bind('<Alt-F4>', lambda e: self._on_window_close())
        
        # Navigation shortcuts
        self.wizard_window.bind('<Control-Tab>', lambda e: self._focus_next_page())
        self.wizard_window.bind('<Control-Shift-Tab>', lambda e: self._focus_previous_page())
        
        # Page-specific shortcuts
        self.wizard_window.bind('<Control-n>', lambda e: self._next_page())
        self.wizard_window.bind('<Control-p>', lambda e: self._previous_page())
    
    def _set_initial_focus(self):
        """Set initial focus to appropriate element"""
        if self.current_page == 1 and self.unsplash_entry:
            self.unsplash_entry.focus()
        elif self.current_page == 2 and self.openai_entry:
            self.openai_entry.focus()
        else:
            self.next_button.focus()
    
    def _focus_next_page(self):
        """Focus navigation for next page"""
        if self.current_page < self.total_pages - 1:
            self._next_page()
    
    def _focus_previous_page(self):
        """Focus navigation for previous page"""
        if self.current_page > 0:
            self._previous_page()
    
    def _show_page(self, page_index: int):
        """Show a specific wizard page"""
        if page_index < 0 or page_index >= self.total_pages:
            return
        
        self.current_page = page_index
        
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Show appropriate page
        if page_index == 0:
            self._show_welcome_page()
        elif page_index == 1:
            self._show_unsplash_page()
        elif page_index == 2:
            self._show_openai_page()
        elif page_index == 3:
            self._show_completion_page()
        
        # Update progress
        progress = (page_index / (self.total_pages - 1)) * 100
        self.progress.configure(value=progress)
        self.progress_text.configure(text=f"Step {page_index + 1} of {self.total_pages}")
        
        # Update navigation
        self._update_navigation()
    
    def _show_welcome_page(self):
        """Show welcome/introduction page"""
        colors = self.theme_manager.get_colors()
        
        # Welcome content
        welcome_frame = tk.Frame(self.content_frame, bg=colors['bg'])
        welcome_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Introduction text
        intro_text = """Welcome to the API Setup Wizard!
        
To use this application, you'll need two API keys:

🖼️ Unsplash API Key
   • For searching and downloading images
   • Free tier: 50 requests per hour
   • Required for image search functionality

🤖 OpenAI API Key  
   • For AI image descriptions and translations
   • Supports GPT-4 Vision for best results
   • Pay-per-use pricing

Don't worry - we'll guide you through getting both keys step by step, with visual instructions and helpful tips!

Both services offer generous free tiers to get you started."""
        
        intro_label = tk.Label(
            welcome_frame,
            text=intro_text,
            font=('TkDefaultFont', 11),
            bg=colors['bg'],
            fg=colors['fg'],
            justify=tk.LEFT,
            wraplength=600
        )
        intro_label.pack(anchor=tk.W, pady=20)
        
        # Benefits section
        benefits_frame = tk.LabelFrame(
            welcome_frame,
            text="What You'll Get",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg']
        )
        benefits_frame.pack(fill=tk.X, pady=(20, 0))
        
        benefits = [
            "✅ Access to millions of high-quality images",
            "✅ AI-powered Spanish descriptions", 
            "✅ Automatic vocabulary extraction",
            "✅ Translation to English",
            "✅ Export to study apps like Anki"
        ]
        
        for benefit in benefits:
            benefit_label = tk.Label(
                benefits_frame,
                text=benefit,
                font=('TkDefaultFont', 10),
                bg=colors['frame_bg'],
                fg=colors['success'],
                anchor=tk.W
            )
            benefit_label.pack(fill=tk.X, padx=15, pady=3)
    
    def _show_unsplash_page(self):
        """Show Unsplash API key setup page"""
        colors = self.theme_manager.get_colors()
        
        page_frame = tk.Frame(self.content_frame, bg=colors['bg'])
        page_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Page title
        title = tk.Label(
            page_frame,
            text="Step 1: Unsplash API Key",
            font=('TkDefaultFont', 16, 'bold'),
            bg=colors['bg'],
            fg=colors['info']
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Help section
        self._create_help_section(page_frame, 'unsplash')
        
        # API Key input
        input_frame = tk.LabelFrame(
            page_frame,
            text="Enter Your Unsplash API Key",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg']
        )
        input_frame.pack(fill=tk.X, pady=20)
        
        # Entry field with enhanced labeling
        entry_frame = tk.Frame(input_frame, bg=colors['frame_bg'])
        entry_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Clear label with helper text
        label_frame = tk.Frame(entry_frame, bg=colors['frame_bg'])
        label_frame.pack(fill=tk.X, anchor=tk.W)
        
        tk.Label(
            label_frame,
            text="Access Key:",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(side=tk.LEFT)
        
        tk.Label(
            label_frame,
            text=" *Required - Starts with random characters",
            font=('TkDefaultFont', 9),
            bg=colors['frame_bg'],
            fg=colors['info']
        ).pack(side=tk.LEFT)
        
        # Entry with validation styling
        entry_container = tk.Frame(entry_frame, bg=colors['frame_bg'])
        entry_container.pack(fill=tk.X, pady=(5, 10))
        
        self.unsplash_entry = tk.Entry(
            entry_container,
            font=('TkDefaultFont', 10),
            width=50,
            show="*",  # Hide the key for security
            relief=tk.SOLID,
            borderwidth=1
        )
        self.unsplash_entry.pack(fill=tk.X)
        self.unsplash_entry.bind('<KeyRelease>', self._on_unsplash_key_change)
        self.unsplash_entry.bind('<FocusIn>', self._on_unsplash_focus_in)
        self.unsplash_entry.bind('<FocusOut>', self._on_unsplash_focus_out)
        
        # Helper text
        helper_text = tk.Label(
            entry_frame,
            text="💡 Tip: Your key should be around 30-40 characters long",
            font=('TkDefaultFont', 8),
            bg=colors['frame_bg'],
            fg=colors['disabled_fg']
        )
        helper_text.pack(anchor=tk.W, pady=(0, 5))
        
        # Show/Hide toggle
        show_var = tk.BooleanVar()
        show_check = tk.Checkbutton(
            entry_frame,
            text="Show API key",
            variable=show_var,
            command=lambda: self.unsplash_entry.config(
                show="" if show_var.get() else "*"
            ),
            bg=colors['frame_bg'],
            fg=colors['fg'],
            selectcolor=colors['entry_bg']
        )
        show_check.pack(anchor=tk.W)
        
        # Test button and status with improved UX
        test_frame = tk.Frame(entry_frame, bg=colors['frame_bg'])
        test_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.test_unsplash_button = tk.Button(
            test_frame,
            text="🔍 Test Connection",
            command=self._test_unsplash_key,
            font=('TkDefaultFont', 9, 'bold'),
            bg=colors['info'],
            fg=colors['select_fg'],
            relief=tk.FLAT,
            padx=15,
            cursor="hand2"
        )
        self.test_unsplash_button.pack(side=tk.LEFT)
        
        # Loading indicator (initially hidden)
        self.unsplash_loading = tk.Label(
            test_frame,
            text="⏳ Testing...",
            font=('TkDefaultFont', 9),
            bg=colors['frame_bg'],
            fg=colors['info']
        )
        
        self.unsplash_status_label = tk.Label(
            test_frame,
            text="Enter your key and click Test Connection",
            font=('TkDefaultFont', 9),
            bg=colors['frame_bg'],
            fg=colors['disabled_fg']
        )
        self.unsplash_status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Load existing key if available
        self._load_existing_unsplash_key()
        
        # Add keyboard accessibility
        self.unsplash_entry.bind('<Control-Return>', lambda e: self._test_unsplash_key())
        self.unsplash_entry.bind('<F5>', lambda e: self._test_unsplash_key())
    
    def _show_openai_page(self):
        """Show OpenAI API key setup page"""
        colors = self.theme_manager.get_colors()
        
        page_frame = tk.Frame(self.content_frame, bg=colors['bg'])
        page_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Page title
        title = tk.Label(
            page_frame,
            text="Step 2: OpenAI API Key",
            font=('TkDefaultFont', 16, 'bold'),
            bg=colors['bg'],
            fg=colors['info']
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Help section
        self._create_help_section(page_frame, 'openai')
        
        # API Key input
        input_frame = tk.LabelFrame(
            page_frame,
            text="Enter Your OpenAI API Key",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg']
        )
        input_frame.pack(fill=tk.X, pady=20)
        
        # Entry field with enhanced labeling
        entry_frame = tk.Frame(input_frame, bg=colors['frame_bg'])
        entry_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Clear label with helper text
        label_frame = tk.Frame(entry_frame, bg=colors['frame_bg'])
        label_frame.pack(fill=tk.X, anchor=tk.W)
        
        tk.Label(
            label_frame,
            text="Secret Key:",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(side=tk.LEFT)
        
        tk.Label(
            label_frame,
            text=" *Required - Must start with 'sk-'",
            font=('TkDefaultFont', 9),
            bg=colors['frame_bg'],
            fg=colors['info']
        ).pack(side=tk.LEFT)
        
        # Entry with validation styling
        entry_container = tk.Frame(entry_frame, bg=colors['frame_bg'])
        entry_container.pack(fill=tk.X, pady=(5, 10))
        
        self.openai_entry = tk.Entry(
            entry_container,
            font=('TkDefaultFont', 10),
            width=50,
            show="*",
            relief=tk.SOLID,
            borderwidth=1
        )
        self.openai_entry.pack(fill=tk.X)
        self.openai_entry.bind('<KeyRelease>', self._on_openai_key_change)
        self.openai_entry.bind('<FocusIn>', self._on_openai_focus_in)
        self.openai_entry.bind('<FocusOut>', self._on_openai_focus_out)
        
        # Helper text
        helper_text = tk.Label(
            entry_frame,
            text="💡 Tip: Billing must be enabled on your OpenAI account",
            font=('TkDefaultFont', 8),
            bg=colors['frame_bg'],
            fg=colors['disabled_fg']
        )
        helper_text.pack(anchor=tk.W, pady=(0, 5))
        
        # Show/Hide toggle
        show_var = tk.BooleanVar()
        show_check = tk.Checkbutton(
            entry_frame,
            text="Show API key",
            variable=show_var,
            command=lambda: self.openai_entry.config(
                show="" if show_var.get() else "*"
            ),
            bg=colors['frame_bg'],
            fg=colors['fg'],
            selectcolor=colors['entry_bg']
        )
        show_check.pack(anchor=tk.W)
        
        # Model selection
        model_frame = tk.Frame(entry_frame, bg=colors['frame_bg'])
        model_frame.pack(fill=tk.X, pady=(15, 0))
        
        tk.Label(
            model_frame,
            text="GPT Model:",
            font=('TkDefaultFont', 10),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(anchor=tk.W)
        
        self.gpt_model_var = tk.StringVar(value="gpt-4o")
        model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.gpt_model_var,
            values=["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
            state="readonly",
            width=20
        )
        model_combo.pack(anchor=tk.W, pady=(5, 0))
        
        # Model info
        model_info = tk.Label(
            model_frame,
            text="Recommended: GPT-4o for best image analysis",
            font=('TkDefaultFont', 9),
            bg=colors['frame_bg'],
            fg=colors['info']
        )
        model_info.pack(anchor=tk.W, pady=(5, 0))
        
        # Test button and status with improved UX
        test_frame = tk.Frame(entry_frame, bg=colors['frame_bg'])
        test_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.test_openai_button = tk.Button(
            test_frame,
            text="🔍 Test Connection",
            command=self._test_openai_key,
            font=('TkDefaultFont', 9, 'bold'),
            bg=colors['info'],
            fg=colors['select_fg'],
            relief=tk.FLAT,
            padx=15,
            cursor="hand2"
        )
        self.test_openai_button.pack(side=tk.LEFT)
        
        # Loading indicator (initially hidden)
        self.openai_loading = tk.Label(
            test_frame,
            text="⏳ Testing...",
            font=('TkDefaultFont', 9),
            bg=colors['frame_bg'],
            fg=colors['info']
        )
        
        self.openai_status_label = tk.Label(
            test_frame,
            text="Enter your key and click Test Connection",
            font=('TkDefaultFont', 9),
            bg=colors['frame_bg'],
            fg=colors['disabled_fg']
        )
        self.openai_status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Load existing key if available
        self._load_existing_openai_key()
        
        # Add keyboard accessibility
        self.openai_entry.bind('<Control-Return>', lambda e: self._test_openai_key())
        self.openai_entry.bind('<F5>', lambda e: self._test_openai_key())
    
    def _safe_open_url(self, url):
        """Safely open URL with error handling"""
        try:
            webbrowser.open(url)
        except Exception as e:
            colors = self.theme_manager.get_colors()
            messagebox.showerror(
                "Browser Error",
                f"Could not open browser.\n\nPlease manually visit:\n{url}\n\nError: {e}",
                parent=self.wizard_window
            )
    
    def _show_completion_page(self):
        """Show setup completion page"""
        colors = self.theme_manager.get_colors()
        
        page_frame = tk.Frame(self.content_frame, bg=colors['bg'])
        page_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Success icon
        success_icon = tk.Label(
            page_frame,
            text="🎉",
            font=('TkDefaultFont', 48),
            bg=colors['bg'],
            fg=colors['success']
        )
        success_icon.pack(pady=20)
        
        # Title
        title = tk.Label(
            page_frame,
            text="Setup Complete!",
            font=('TkDefaultFont', 18, 'bold'),
            bg=colors['bg'],
            fg=colors['success']
        )
        title.pack(pady=(0, 20))
        
        # Status summary
        status_frame = tk.Frame(page_frame, bg=colors['bg'])
        status_frame.pack(fill=tk.X, pady=20)
        
        # API status indicators
        unsplash_status = "✅ Configured" if self.unsplash_valid else "⚠️ Not tested"
        openai_status = "✅ Configured" if self.openai_valid else "⚠️ Not tested"
        
        status_text = f"""Configuration Summary:

Unsplash API: {unsplash_status}
OpenAI API: {openai_status}
GPT Model: {self.gpt_model_var.get() if self.gpt_model_var else 'gpt-4o'}

You're ready to start learning Spanish with AI-powered image descriptions!"""
        
        status_label = tk.Label(
            status_frame,
            text=status_text,
            font=('TkDefaultFont', 11),
            bg=colors['bg'],
            fg=colors['fg'],
            justify=tk.LEFT
        )
        status_label.pack(anchor=tk.W)
        
        # Next steps
        next_steps_frame = tk.LabelFrame(
            page_frame,
            text="What's Next?",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg']
        )
        next_steps_frame.pack(fill=tk.X, pady=(30, 0))
        
        steps = [
            "1️⃣ Take the interactive tour to learn the interface",
            "2️⃣ Try the sample walkthrough with a demo image",
            "3️⃣ Start searching for images on topics you want to learn",
            "4️⃣ Build your vocabulary and export to study apps"
        ]
        
        for step in steps:
            step_label = tk.Label(
                next_steps_frame,
                text=step,
                font=('TkDefaultFont', 10),
                bg=colors['frame_bg'],
                fg=colors['fg'],
                anchor=tk.W
            )
            step_label.pack(fill=tk.X, padx=15, pady=3)
    
    def _create_help_section(self, parent, api_type):
        """Create expandable help section for API setup"""
        colors = self.theme_manager.get_colors()
        help_info = self.help_content[api_type]
        
        # Help frame
        help_frame = tk.LabelFrame(
            parent,
            text=help_info['title'],
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['info']
        )
        help_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Quick access buttons
        button_frame = tk.Frame(help_frame, bg=colors['frame_bg'])
        button_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Open website button with enhanced UX
        website_btn = tk.Button(
            button_frame,
            text=f"🌐 Open {api_type.title()} Website",
            command=lambda: self._safe_open_url(help_info['url']),
            font=('TkDefaultFont', 9, 'bold'),
            bg=colors['select_bg'],
            fg=colors['select_fg'],
            relief=tk.FLAT,
            padx=15,
            cursor="hand2"
        )
        website_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Tooltip-like help text
        url_hint = tk.Label(
            button_frame,
            text=f"({help_info['url']})",
            font=('TkDefaultFont', 8),
            bg=colors['frame_bg'],
            fg=colors['disabled_fg']
        )
        url_hint.pack(side=tk.LEFT, padx=(5, 0))
        
        # Show steps button
        steps_btn = tk.Button(
            button_frame,
            text="Show Detailed Steps",
            command=lambda: self._show_detailed_help(api_type),
            font=('TkDefaultFont', 9),
            bg=colors['info'],
            fg=colors['select_fg'],
            relief=tk.FLAT,
            padx=15
        )
        steps_btn.pack(side=tk.LEFT)
        
        # Quick steps preview
        steps_frame = tk.Frame(help_frame, bg=colors['frame_bg'])
        steps_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        quick_steps = help_info['steps'][:3]  # Show first 3 steps
        for step in quick_steps:
            step_label = tk.Label(
                steps_frame,
                text=step,
                font=('TkDefaultFont', 9),
                bg=colors['frame_bg'],
                fg=colors['disabled_fg'],
                anchor=tk.W
            )
            step_label.pack(fill=tk.X)
        
        more_label = tk.Label(
            steps_frame,
            text="... click 'Show Detailed Steps' for complete instructions",
            font=('TkDefaultFont', 9, 'italic'),
            bg=colors['frame_bg'],
            fg=colors['info'],
            anchor=tk.W
        )
        more_label.pack(fill=tk.X, pady=(5, 0))
    
    def _show_detailed_help(self, api_type):
        """Show detailed help dialog"""
        if api_type == 'general':
            self._show_general_help()
            return
        colors = self.theme_manager.get_colors()
        help_info = self.help_content[api_type]
        
        # Create help dialog
        help_dialog = tk.Toplevel(self.wizard_window)
        help_dialog.title(f"{api_type.title()} API Setup Guide")
        help_dialog.geometry("500x600")
        help_dialog.configure(bg=colors['bg'])
        help_dialog.transient(self.wizard_window)
        help_dialog.grab_set()
        
        # Center dialog
        help_dialog.update_idletasks()
        x = (help_dialog.winfo_screenwidth() // 2) - 250
        y = (help_dialog.winfo_screenheight() // 2) - 300
        help_dialog.geometry(f"+{x}+{y}")
        
        # Scrollable content
        canvas = tk.Canvas(help_dialog, bg=colors['bg'])
        scrollbar = ttk.Scrollbar(help_dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Content
        title_label = tk.Label(
            scrollable_frame,
            text=help_info['title'],
            font=('TkDefaultFont', 14, 'bold'),
            bg=colors['bg'],
            fg=colors['info']
        )
        title_label.pack(pady=(0, 20))
        
        # Detailed steps
        steps_frame = tk.LabelFrame(
            scrollable_frame,
            text="Step-by-Step Instructions",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg']
        )
        steps_frame.pack(fill=tk.X, pady=(0, 20))
        
        for step in help_info['steps']:
            step_label = tk.Label(
                steps_frame,
                text=step,
                font=('TkDefaultFont', 10),
                bg=colors['frame_bg'],
                fg=colors['fg'],
                anchor=tk.W,
                wraplength=400
            )
            step_label.pack(fill=tk.X, padx=15, pady=2)
        
        # Tips section
        tips_frame = tk.LabelFrame(
            scrollable_frame,
            text="Important Tips",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['warning']
        )
        tips_frame.pack(fill=tk.X, pady=(0, 20))
        
        for tip in help_info['tips']:
            tip_label = tk.Label(
                tips_frame,
                text=f"💡 {tip}",
                font=('TkDefaultFont', 9),
                bg=colors['frame_bg'],
                fg=colors['fg'],
                anchor=tk.W,
                wraplength=400
            )
            tip_label.pack(fill=tk.X, padx=15, pady=2)
        
        # Close button
        close_btn = tk.Button(
            scrollable_frame,
            text="Close",
            command=help_dialog.destroy,
            font=('TkDefaultFont', 10),
            bg=colors['button_bg'],
            fg=colors['button_fg'],
            relief=tk.FLAT,
            padx=20
        )
        close_btn.pack(pady=20)
    
    def _show_general_help(self):
        """Show general help dialog"""
        help_text = '''🔑 API Setup Wizard Help

KEYBOARD SHORTCUTS:
• F1 or Ctrl+H: Show this help
• Escape: Skip setup
• Ctrl+Enter or F5: Test API key (when focused on entry)
• Ctrl+N: Next page
• Ctrl+P: Previous page
• Tab: Navigate between fields

API KEY REQUIREMENTS:
🖼️ Unsplash: Free developer account, Access Key
🤖 OpenAI: Account with billing enabled, Secret Key

SECURITY:
• Keys are stored locally and encrypted
• Never share your API keys
• You can change them anytime in Settings

TROUBLESHOoting:
• Test your keys before saving
• Check internet connection
• Verify keys are copied completely
• Ensure OpenAI billing is enabled

For more help, visit the documentation or contact support.'''
        
        messagebox.showinfo(
            "API Setup Help", 
            help_text,
            parent=self.wizard_window
        )
    
    def _load_existing_unsplash_key(self):
        """Load existing Unsplash key if available"""
        try:
            api_keys = self.config_manager.get_api_keys()
            if api_keys.get('unsplash'):
                self.unsplash_entry.insert(0, api_keys['unsplash'])
                self.unsplash_valid = True
                self.unsplash_status_label.config(
                    text="✅ Previously configured",
                    fg=self.theme_manager.get_colors()['success']
                )
        except:
            pass
    
    def _load_existing_openai_key(self):
        """Load existing OpenAI key if available"""
        try:
            api_keys = self.config_manager.get_api_keys()
            if api_keys.get('openai'):
                self.openai_entry.insert(0, api_keys['openai'])
                self.openai_valid = True
                self.openai_status_label.config(
                    text="✅ Previously configured",
                    fg=self.theme_manager.get_colors()['success']
                )
            if api_keys.get('gpt_model') and self.gpt_model_var:
                self.gpt_model_var.set(api_keys['gpt_model'])
        except:
            pass
    
    def _on_unsplash_key_change(self, event=None):
        """Handle Unsplash key input changes"""
        self.unsplash_valid = False
        key = self.unsplash_entry.get().strip()
        colors = self.theme_manager.get_colors()
        
        if not key:
            self.unsplash_status_label.config(text="Enter your key and click Test Connection", fg=colors['disabled_fg'])
        elif len(key) < 20:
            self.unsplash_status_label.config(text="⚠️ Key seems too short", fg=colors['warning'])
        else:
            self.unsplash_status_label.config(text="Ready to test - Click Test Connection", fg=colors['info'])
        
        self._validate_entry_styling(self.unsplash_entry, key)
    
    def _on_openai_key_change(self, event=None):
        """Handle OpenAI key input changes"""
        self.openai_valid = False
        key = self.openai_entry.get().strip()
        colors = self.theme_manager.get_colors()
        
        if not key:
            self.openai_status_label.config(text="Enter your key and click Test Connection", fg=colors['disabled_fg'])
        elif not key.startswith('sk-'):
            self.openai_status_label.config(text="⚠️ Key should start with 'sk-'", fg=colors['warning'])
        elif len(key) < 40:
            self.openai_status_label.config(text="⚠️ Key seems too short", fg=colors['warning'])
        else:
            self.openai_status_label.config(text="Ready to test - Click Test Connection", fg=colors['info'])
        
        self._validate_entry_styling(self.openai_entry, key)
    
    def _test_unsplash_key(self):
        """Test the Unsplash API key"""
        key = self.unsplash_entry.get().strip()
        if not key:
            self.unsplash_status_label.config(
                text="❌ Please enter a key",
                fg=self.theme_manager.get_colors()['error']
            )
            return
        
        colors = self.theme_manager.get_colors()
        # Show loading state
        self.unsplash_status_label.pack_forget()
        self.unsplash_loading.pack(side=tk.LEFT, padx=(10, 0))
        self.test_unsplash_button.config(state=tk.DISABLED, text="⏳ Testing...")
        self.wizard_window.update_idletasks()
        
        # Test in background thread
        import threading
        threading.Thread(target=self._do_unsplash_test, args=(key,), daemon=True).start()
    
    def _do_unsplash_test(self, key):
        """Perform actual Unsplash API test with enhanced error handling"""
        try:
            headers = {"Authorization": f"Client-ID {key}"}
            response = requests.get(
                "https://api.unsplash.com/photos/random",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.unsplash_valid = True
                self.wizard_window.after(0, lambda: self._update_unsplash_status(True, "✅ Connection successful!"))
            elif response.status_code == 401:
                message = "❌ Invalid API key - check your Access Key"
                self.wizard_window.after(0, lambda: self._update_unsplash_status(False, message))
            elif response.status_code == 403:
                message = "❌ API key lacks permissions - check application status"
                self.wizard_window.after(0, lambda: self._update_unsplash_status(False, message))
            elif response.status_code == 429:
                message = "❌ Rate limit exceeded - try again in a few minutes"
                self.wizard_window.after(0, lambda: self._update_unsplash_status(False, message))
            else:
                message = f"❌ API error (Status: {response.status_code}) - check your key"
                self.wizard_window.after(0, lambda: self._update_unsplash_status(False, message))
        except requests.exceptions.Timeout:
            message = "❌ Connection timeout - check your internet connection"
            self.wizard_window.after(0, lambda: self._update_unsplash_status(False, message))
        except requests.exceptions.ConnectionError:
            message = "❌ No internet connection - check your network"
            self.wizard_window.after(0, lambda: self._update_unsplash_status(False, message))
        except Exception as e:
            error_str = str(e)[:50] + "..." if len(str(e)) > 50 else str(e)
            message = f"❌ Unexpected error: {error_str}"
            self.wizard_window.after(0, lambda: self._update_unsplash_status(False, message))
    
    def _update_unsplash_status(self, valid, message):
        """Update Unsplash status in UI"""
        colors = self.theme_manager.get_colors()
        color = colors['success'] if valid else colors['error']
        
        # Hide loading, show status
        self.unsplash_loading.pack_forget()
        self.unsplash_status_label.config(text=message, fg=color)
        self.unsplash_status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Update button
        success_text = "✅ Test Connection" if valid else "🔍 Test Connection"
        self.test_unsplash_button.config(state=tk.NORMAL, text=success_text)
        
        # Update entry styling
        self._validate_entry_styling(self.unsplash_entry, self.unsplash_entry.get().strip(), valid)
    
    def _test_openai_key(self):
        """Test the OpenAI API key"""
        key = self.openai_entry.get().strip()
        if not key:
            self.openai_status_label.config(
                text="❌ Please enter a key",
                fg=self.theme_manager.get_colors()['error']
            )
            return
        
        colors = self.theme_manager.get_colors()
        # Show loading state
        self.openai_status_label.pack_forget()
        self.openai_loading.pack(side=tk.LEFT, padx=(10, 0))
        self.test_openai_button.config(state=tk.DISABLED, text="⏳ Testing...")
        self.wizard_window.update_idletasks()
        
        # Test in background thread
        import threading
        threading.Thread(target=self._do_openai_test, args=(key,), daemon=True).start()
    
    def _do_openai_test(self, key):
        """Perform actual OpenAI API test with enhanced error handling"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=key)
            
            # Simple test call with preferred model
            test_model = "gpt-3.5-turbo"  # Cheaper for testing
            response = client.chat.completions.create(
                model=test_model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1
            )
            
            if response.choices:
                self.openai_valid = True
                self.wizard_window.after(0, lambda: self._update_openai_status(True, "✅ Connection successful!"))
            else:
                self.wizard_window.after(0, lambda: self._update_openai_status(False, "❌ Unexpected API response"))
                
        except Exception as e:
            error_msg = str(e).lower()
            
            if "api_key" in error_msg or "authentication" in error_msg or "invalid" in error_msg:
                message = "❌ Invalid API key - check your Secret Key"
            elif "quota" in error_msg or "insufficient_quota" in error_msg:
                message = "❌ Quota exceeded - add billing or wait for reset"
            elif "billing" in error_msg or "payment" in error_msg:
                message = "❌ Billing not set up - enable billing in OpenAI dashboard"
            elif "rate_limit" in error_msg or "too_many" in error_msg:
                message = "❌ Rate limit hit - try again in a moment"
            elif "model" in error_msg and "does not exist" in error_msg:
                message = "❌ Model access issue - check your OpenAI plan"
            elif "connection" in error_msg or "timeout" in error_msg:
                message = "❌ Connection failed - check your internet"
            elif "openai" in error_msg and "not found" in error_msg:
                message = "❌ OpenAI library missing - installation issue"
            else:
                error_str = str(e)[:45] + "..." if len(str(e)) > 45 else str(e)
                message = f"❌ Error: {error_str}"
            
            self.wizard_window.after(0, lambda: self._update_openai_status(False, message))
    
    def _update_openai_status(self, valid, message):
        """Update OpenAI status in UI"""
        colors = self.theme_manager.get_colors()
        color = colors['success'] if valid else colors['error']
        
        # Hide loading, show status
        self.openai_loading.pack_forget()
        self.openai_status_label.config(text=message, fg=color)
        self.openai_status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Update button
        success_text = "✅ Test Connection" if valid else "🔍 Test Connection"
        self.test_openai_button.config(state=tk.NORMAL, text=success_text)
        
        # Update entry styling
        self._validate_entry_styling(self.openai_entry, self.openai_entry.get().strip(), valid)
    
    def _save_keys(self):
        """Save API keys to configuration"""
        try:
            # Get current keys
            unsplash_key = self.unsplash_entry.get().strip() if self.unsplash_entry else ""
            openai_key = self.openai_entry.get().strip() if self.openai_entry else ""
            gpt_model = self.gpt_model_var.get() if self.gpt_model_var else "gpt-4o"
            
            # Update configuration
            if unsplash_key:
                self.config_manager.set_api_key('unsplash', unsplash_key)
            if openai_key:
                self.config_manager.set_api_key('openai', openai_key)
                self.config_manager.set_api_key('gpt_model', gpt_model)
            
            return True
        except Exception as e:
            messagebox.showerror("Configuration Error", f"Failed to save API keys: {e}")
            return False
    
    def _next_page(self):
        """Go to next page"""
        if self.current_page == self.total_pages - 1:
            # Last page - complete setup
            self._complete_setup()
        else:
            self._show_page(self.current_page + 1)
    
    def _previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self._show_page(self.current_page - 1)
    
    def _skip_setup(self):
        """Skip the API setup"""
        result = messagebox.askyesno(
            "Skip Setup",
            "Are you sure you want to skip API setup?\\n\\n" +
            "The app won't work without valid API keys, but you can " +
            "configure them later in Settings.",
            parent=self.wizard_window
        )
        
        if result and self.on_skip:
            self.on_skip()
    
    def _complete_setup(self):
        """Complete the setup process"""
        if self._save_keys():
            if self.on_completion:
                self.on_completion()
    
    def _update_navigation(self):
        """Update navigation button states"""
        colors = self.theme_manager.get_colors()
        
        # Back button
        self.back_button.config(
            state=tk.NORMAL if self.current_page > 0 else tk.DISABLED
        )
        
        # Next button
        if self.current_page == self.total_pages - 1:
            self.next_button.config(text="Complete Setup ✓")
        else:
            self.next_button.config(text="Next →")
    
    def _on_window_close(self):
        """Handle window close - treat as skip"""
        self._skip_setup()
    
    def _validate_entry_styling(self, entry, value, is_valid=None):
        """Apply styling to entry based on validation state"""
        colors = self.theme_manager.get_colors()
        
        if is_valid is True:
            entry.config(bg=colors.get('success_bg', '#e8f5e8'), fg=colors['fg'])
        elif is_valid is False:
            entry.config(bg=colors.get('error_bg', '#ffe8e8'), fg=colors['fg'])
        elif value and len(value) > 10:
            entry.config(bg=colors.get('entry_bg', colors['bg']), fg=colors['info'])
        else:
            entry.config(bg=colors.get('entry_bg', colors['bg']), fg=colors['fg'])
    
    def _on_unsplash_focus_in(self, event=None):
        """Handle focus entering Unsplash entry"""
        colors = self.theme_manager.get_colors()
        self.unsplash_entry.config(highlightbackground=colors['select_bg'], highlightcolor=colors['select_bg'])
    
    def _on_unsplash_focus_out(self, event=None):
        """Handle focus leaving Unsplash entry"""
        colors = self.theme_manager.get_colors()
        self.unsplash_entry.config(highlightbackground=colors.get('border', '#ccc'))
    
    def _on_openai_focus_in(self, event=None):
        """Handle focus entering OpenAI entry"""
        colors = self.theme_manager.get_colors()
        self.openai_entry.config(highlightbackground=colors['select_bg'], highlightcolor=colors['select_bg'])
    
    def _on_openai_focus_out(self, event=None):
        """Handle focus leaving OpenAI entry"""
        colors = self.theme_manager.get_colors()
        self.openai_entry.config(highlightbackground=colors.get('border', '#ccc'))
    
    def _toggle_key_visibility(self, entry, var):
        """Toggle API key visibility with accessibility feedback"""
        show_key = var.get()
        entry.config(show="" if show_key else "*")
        
        # Audio feedback for accessibility
        try:
            self.wizard_window.bell()
        except:
            pass
    
    def hide(self):
        """Hide the wizard"""
        if self.wizard_window:
            self.wizard_window.destroy()
            self.wizard_window = None