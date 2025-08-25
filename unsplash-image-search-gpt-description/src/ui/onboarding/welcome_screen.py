"""
Welcome screen for first-time users
Shows app value proposition and gets user started
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
import webbrowser


class WelcomeScreen:
    """
    Welcome screen that introduces users to the application
    and explains its key features and benefits
    """
    
    def __init__(self, parent: tk.Tk, theme_manager, 
                 on_continue: Callable = None, on_skip: Callable = None):
        self.parent = parent
        self.theme_manager = theme_manager
        self.on_continue = on_continue
        self.on_skip = on_skip
        
        self.welcome_window = None
        self.current_page = 0
        self.total_pages = 3
        
        # Content for each page
        self.pages = [
            {
                "title": "Welcome to Unsplash Image Search & GPT",
                "icon": "🖼️",
                "content": [
                    "Transform your language learning with AI-powered image descriptions!",
                    "",
                    "✨ Search beautiful images from Unsplash",
                    "🤖 Get detailed AI descriptions in Spanish", 
                    "📚 Extract and learn vocabulary automatically",
                    "💾 Export to Anki for spaced repetition",
                    "",
                    "Perfect for visual learners who want to build vocabulary",
                    "through real-world images and contexts."
                ]
            },
            {
                "title": "How It Works",
                "icon": "⚡",
                "content": [
                    "Learning Spanish has never been easier:",
                    "",
                    "1️⃣ Search for any topic (food, travel, nature...)",
                    "2️⃣ Get AI-generated descriptions in Spanish",
                    "3️⃣ Click highlighted words to add to vocabulary",
                    "4️⃣ Export your word lists to study apps",
                    "",
                    "The AI analyzes each image and creates rich, contextual",
                    "descriptions that help you learn vocabulary naturally."
                ]
            },
            {
                "title": "Ready to Start?",
                "icon": "🚀",
                "content": [
                    "Let's get you set up in just a few minutes:",
                    "",
                    "🔑 Configure your API keys (we'll help!)",
                    "🎯 Take a quick tour of the interface", 
                    "🖼️ Try a sample image to see it in action",
                    "⚙️ Customize your learning preferences",
                    "",
                    "Don't worry - you can always change settings later.",
                    "We'll guide you through each step!"
                ]
            }
        ]
    
    def show(self):
        """Display the welcome screen"""
        if self.welcome_window:
            self.welcome_window.lift()
            return
        
        colors = self.theme_manager.get_colors()
        
        # Create main window
        self.welcome_window = tk.Toplevel(self.parent)
        self.welcome_window.title("Welcome - Unsplash Image Search & GPT")
        self.welcome_window.geometry("600x500")
        self.welcome_window.configure(bg=colors['bg'])
        self.welcome_window.resizable(False, False)
        self.welcome_window.transient(self.parent)
        self.welcome_window.grab_set()
        
        # Center window
        self.welcome_window.update_idletasks()
        x = (self.welcome_window.winfo_screenwidth() // 2) - 300
        y = (self.welcome_window.winfo_screenheight() // 2) - 250
        self.welcome_window.geometry(f"+{x}+{y}")
        
        # Prevent closing with X button
        self.welcome_window.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        self._create_widgets()
        self._show_page(0)
    
    def _create_widgets(self):
        """Create the welcome screen widgets"""
        colors = self.theme_manager.get_colors()
        
        # Main container
        main_frame = tk.Frame(self.welcome_window, bg=colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Header with logo/icon
        header_frame = tk.Frame(main_frame, bg=colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Icon
        self.icon_label = tk.Label(
            header_frame,
            text="🖼️",
            font=('TkDefaultFont', 48),
            bg=colors['bg'],
            fg=colors['info']
        )
        self.icon_label.pack()
        
        # Title
        self.title_label = tk.Label(
            header_frame,
            text="Welcome!",
            font=('TkDefaultFont', 20, 'bold'),
            bg=colors['bg'],
            fg=colors['fg']
        )
        self.title_label.pack(pady=(10, 0))
        
        # Content area
        self.content_frame = tk.Frame(main_frame, bg=colors['bg'])
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Content text
        self.content_text = tk.Text(
            self.content_frame,
            wrap=tk.WORD,
            font=('TkDefaultFont', 11),
            bg=colors['text_bg'],
            fg=colors['text_fg'],
            relief=tk.FLAT,
            state=tk.DISABLED,
            cursor="arrow",
            height=15,
            padx=20,
            pady=15
        )
        self.content_text.pack(fill=tk.BOTH, expand=True)
        
        # Progress indicator
        progress_frame = tk.Frame(main_frame, bg=colors['bg'])
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.progress_dots = []
        dots_container = tk.Frame(progress_frame, bg=colors['bg'])
        dots_container.pack()
        
        for i in range(self.total_pages):
            dot = tk.Label(
                dots_container,
                text="●",
                font=('TkDefaultFont', 16),
                bg=colors['bg'],
                fg=colors['border']
            )
            dot.pack(side=tk.LEFT, padx=3)
            self.progress_dots.append(dot)
        
        # Navigation buttons
        nav_frame = tk.Frame(main_frame, bg=colors['bg'])
        nav_frame.pack(fill=tk.X)
        
        # Skip button (always visible)
        self.skip_button = tk.Button(
            nav_frame,
            text="Skip Setup",
            command=self._on_skip,
            font=('TkDefaultFont', 10),
            bg=colors['button_bg'],
            fg=colors['disabled_fg'],
            activebackground=colors['button_active_bg'],
            relief=tk.FLAT,
            padx=20,
            cursor="hand2"
        )
        self.skip_button.pack(side=tk.LEFT)
        
        # Right side buttons
        right_buttons = tk.Frame(nav_frame, bg=colors['bg'])
        right_buttons.pack(side=tk.RIGHT)
        
        # Back button
        self.back_button = tk.Button(
            right_buttons,
            text="← Back",
            command=self._previous_page,
            font=('TkDefaultFont', 10),
            bg=colors['button_bg'],
            fg=colors['button_fg'],
            activebackground=colors['button_active_bg'],
            relief=tk.FLAT,
            padx=20,
            cursor="hand2"
        )
        self.back_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Next/Start button
        self.next_button = tk.Button(
            right_buttons,
            text="Next →",
            command=self._next_page,
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['select_bg'],
            fg=colors['select_fg'],
            activebackground=colors['button_active_bg'],
            relief=tk.FLAT,
            padx=20,
            cursor="hand2"
        )
        self.next_button.pack(side=tk.LEFT)
        
        # Add tooltips
        self.theme_manager.create_themed_tooltip(
            self.skip_button, 
            "Skip onboarding and go directly to the app"
        )
        
        # Help link
        help_frame = tk.Frame(main_frame, bg=colors['bg'])
        help_frame.pack(fill=tk.X, pady=(10, 0))
        
        help_link = tk.Label(
            help_frame,
            text="Need help? View documentation",
            font=('TkDefaultFont', 9, 'underline'),
            fg=colors['info'],
            bg=colors['bg'],
            cursor="hand2"
        )
        help_link.pack()
        help_link.bind("<Button-1>", self._open_help)
    
    def _show_page(self, page_index: int):
        """Display a specific page of the welcome screen"""
        if page_index < 0 or page_index >= len(self.pages):
            return
        
        self.current_page = page_index
        page = self.pages[page_index]
        colors = self.theme_manager.get_colors()
        
        # Update icon and title
        self.icon_label.config(text=page["icon"])
        self.title_label.config(text=page["title"])
        
        # Update content
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete('1.0', tk.END)
        
        content_text = "\\n".join(page["content"])
        self.content_text.insert('1.0', content_text)
        
        # Style the content
        self.content_text.tag_configure(
            "highlight",
            foreground=colors['info'],
            font=('TkDefaultFont', 11, 'bold')
        )
        
        # Highlight emojis and important text
        lines = content_text.split('\\n')
        for line_num, line in enumerate(lines):
            line_start = f"{line_num + 1}.0"
            if line.strip().startswith(('✨', '🤖', '📚', '💾', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '🔑', '🎯', '🖼️', '⚙️')):
                line_end = f"{line_num + 1}.end"
                self.content_text.tag_add("highlight", line_start, line_end)
        
        self.content_text.config(state=tk.DISABLED)
        
        # Update progress dots
        for i, dot in enumerate(self.progress_dots):
            if i == page_index:
                dot.config(fg=colors['select_bg'])
            elif i < page_index:
                dot.config(fg=colors['success'])
            else:
                dot.config(fg=colors['border'])
        
        # Update navigation buttons
        self.back_button.config(state=tk.NORMAL if page_index > 0 else tk.DISABLED)
        
        if page_index == len(self.pages) - 1:
            # Last page - show "Get Started" button
            self.next_button.config(
                text="Get Started! 🚀",
                bg=colors['success'],
                fg=colors['select_fg']
            )
            self.theme_manager.create_themed_tooltip(
                self.next_button,
                "Start the setup process"
            )
        else:
            self.next_button.config(
                text="Next →",
                bg=colors['select_bg'],
                fg=colors['select_fg']
            )
            self.theme_manager.create_themed_tooltip(
                self.next_button,
                "Continue to next page"
            )
    
    def _next_page(self):
        """Go to next page or start setup"""
        if self.current_page < len(self.pages) - 1:
            self._show_page(self.current_page + 1)
        else:
            # Last page - start setup
            self._on_start_setup()
    
    def _previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self._show_page(self.current_page - 1)
    
    def _on_start_setup(self):
        """Handle starting the setup process"""
        if self.on_continue:
            self.on_continue()
    
    def _on_skip(self):
        """Handle skipping the entire onboarding"""
        # Show confirmation dialog
        colors = self.theme_manager.get_colors()
        
        from ..theme_manager import ThemedMessageBox
        result = ThemedMessageBox.ask_yes_no(
            self.welcome_window,
            "Skip Onboarding?",
            "Are you sure you want to skip the setup process?\\n\\n" +
            "You can always access help and settings later from the menu.",
            self.theme_manager
        )
        
        if result and self.on_skip:
            self.on_skip()
    
    def _open_help(self, event=None):
        """Open help documentation"""
        # You could open local help or online documentation
        try:
            webbrowser.open("https://github.com/yourusername/unsplash-gpt-description")
        except:
            pass  # Ignore if browser fails to open
    
    def _on_window_close(self):
        """Handle window close button - treat as skip"""
        self._on_skip()
    
    def hide(self):
        """Hide the welcome screen"""
        if self.welcome_window:
            self.welcome_window.destroy()
            self.welcome_window = None
    
    def show_quick_tip(self, tip_text: str):
        """Show a quick tip overlay"""
        if not self.welcome_window:
            return
        
        colors = self.theme_manager.get_colors()
        
        # Create tip overlay
        tip_frame = tk.Frame(
            self.welcome_window,
            bg=colors['info'],
            relief=tk.RAISED,
            borderwidth=1
        )
        tip_frame.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        
        tip_label = tk.Label(
            tip_frame,
            text=f"💡 Tip: {tip_text}",
            bg=colors['info'],
            fg=colors['select_fg'],
            font=('TkDefaultFont', 9),
            padx=15,
            pady=5
        )
        tip_label.pack()
        
        # Auto-hide after 3 seconds
        self.welcome_window.after(3000, tip_frame.destroy)