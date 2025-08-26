"""
Enhanced main application demo integrating all new features:
- Description style selector (academic/poetic/technical)
- Session-based image variety
- Improved vocabulary management
- UI patterns learned from image-questionnaire-gpt
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import new features
from src.features.description_styles import DescriptionStyleManager, DescriptionStyle, VocabularyLevel
from src.features.session_tracker import SessionTracker
from src.ui.components.style_selector import StyleSelectorPanel


class EnhancedImageSearchApp(tk.Tk):
    """
    Enhanced version of the Unsplash Image Search application with new features.
    """
    
    def __init__(self):
        super().__init__()
        
        self.title("Enhanced Unsplash Image Search - GPT Description Tool")
        self.geometry("1200x900")
        
        # Initialize managers
        self.style_manager = DescriptionStyleManager()
        self.session_tracker = SessionTracker(Path("./data"))
        self.preferences_file = Path("./data/preferences.json")
        
        # Load preferences
        self.load_preferences()
        
        # Create UI
        self.create_ui()
        
        # Set focus
        self.search_entry.focus_set()
    
    def create_ui(self):
        """Create the enhanced UI with all new features."""
        # Create menu bar
        self.create_menu()
        
        # Main container
        main_container = ttk.Frame(self, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Top section: Search and controls
        self.create_search_section(main_container)
        
        # Middle section: Style selector (NEW)
        self.create_style_section(main_container)
        
        # Bottom section: Content area
        self.create_content_section(main_container)
        
        # Status bar
        self.create_status_bar(main_container)
    
    def create_menu(self):
        """Create enhanced menu bar."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Search", command=self.new_search, accelerator="Ctrl+N")
        file_menu.add_command(label="Reset Session History", command=self.reset_session)
        file_menu.add_separator()
        file_menu.add_command(label="Export Session Stats", command=self.export_stats)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit, accelerator="Ctrl+Q")
        
        # Style menu (NEW)
        style_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Style", menu=style_menu)
        style_menu.add_command(label="Academic Style", command=lambda: self.set_style(DescriptionStyle.ACADEMIC))
        style_menu.add_command(label="Poetic Style", command=lambda: self.set_style(DescriptionStyle.POETIC))
        style_menu.add_command(label="Technical Style", command=lambda: self.set_style(DescriptionStyle.TECHNICAL))
        style_menu.add_separator()
        style_menu.add_command(label="Beginner Level", command=lambda: self.set_level(VocabularyLevel.BEGINNER))
        style_menu.add_command(label="Intermediate Level", command=lambda: self.set_level(VocabularyLevel.INTERMEDIATE))
        style_menu.add_command(label="Advanced Level", command=lambda: self.set_level(VocabularyLevel.ADVANCED))
        style_menu.add_command(label="Native Level", command=lambda: self.set_level(VocabularyLevel.NATIVE))
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Session Statistics", command=self.show_statistics)
        view_menu.add_command(label="Search History", command=self.show_history)
        
        # Bind shortcuts
        self.bind('<Control-n>', lambda e: self.new_search())
        self.bind('<Control-q>', lambda e: self.quit())
    
    def create_search_section(self, parent):
        """Create search controls section."""
        search_frame = ttk.LabelFrame(parent, text="🔍 Search Controls", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search row
        search_row = ttk.Frame(search_frame)
        search_row.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_row, text="Search Query:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_entry = ttk.Entry(search_row, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<Return>', self.perform_search)
        
        ttk.Button(search_row, text="Search", command=self.perform_search).pack(side=tk.LEFT, padx=5)
        
        # Session info label (NEW)
        self.session_info_label = ttk.Label(search_row, text="", foreground="blue")
        self.session_info_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Control buttons row
        button_row = ttk.Frame(search_frame)
        button_row.pack(fill=tk.X)
        
        ttk.Button(button_row, text="🔄 Shuffle (New Image)", 
                  command=self.shuffle_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_row, text="🆕 Fresh Search", 
                  command=self.fresh_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_row, text="📝 Generate Description", 
                  command=self.generate_description).pack(side=tk.LEFT, padx=5)
    
    def create_style_section(self, parent):
        """Create style selector section (NEW)."""
        # Use the StyleSelectorPanel component
        self.style_selector = StyleSelectorPanel(
            parent,
            self.style_manager,
            on_style_change=self.on_style_change
        )
        self.style_selector.pack(fill=tk.X, pady=(0, 10))
    
    def create_content_section(self, parent):
        """Create main content area."""
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Left: Image preview (placeholder)
        image_frame = ttk.LabelFrame(content_frame, text="📷 Image Preview", padding="10")
        image_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.image_label = ttk.Label(image_frame, text="[Image will appear here]", 
                                     relief=tk.SUNKEN, anchor=tk.CENTER)
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Right: Text areas
        text_frame = ttk.Frame(content_frame)
        text_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        text_frame.rowconfigure(0, weight=1)
        text_frame.rowconfigure(1, weight=1)
        text_frame.columnconfigure(0, weight=1)
        
        # Description area with style indicator
        desc_frame = ttk.LabelFrame(text_frame, text="✨ AI Description", padding="10")
        desc_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        desc_frame.rowconfigure(0, weight=1)
        desc_frame.columnconfigure(0, weight=1)
        
        # Style indicator label (NEW)
        self.style_indicator = ttk.Label(desc_frame, text="", font=('Arial', 9, 'italic'))
        self.style_indicator.grid(row=0, column=0, sticky="w")
        
        self.description_text = scrolledtext.ScrolledText(desc_frame, wrap=tk.WORD, height=10)
        self.description_text.grid(row=1, column=0, sticky="nsew")
        
        # Vocabulary area
        vocab_frame = ttk.LabelFrame(text_frame, text="📚 Extracted Vocabulary", padding="10")
        vocab_frame.grid(row=1, column=0, sticky="nsew")
        vocab_frame.rowconfigure(0, weight=1)
        vocab_frame.columnconfigure(0, weight=1)
        
        self.vocab_text = scrolledtext.ScrolledText(vocab_frame, wrap=tk.WORD, height=8)
        self.vocab_text.grid(row=0, column=0, sticky="nsew")
    
    def create_status_bar(self, parent):
        """Create status bar."""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.stats_label = ttk.Label(status_frame, text="", relief=tk.SUNKEN, anchor=tk.E)
        self.stats_label.pack(side=tk.RIGHT, padx=(5, 0))
    
    def perform_search(self, event=None):
        """Perform image search with variety management."""
        query = self.search_entry.get().strip()
        if not query:
            self.update_status("Please enter a search query")
            return
        
        # Get optimized search parameters from session tracker
        params = self.session_tracker.get_search_parameters(query)
        
        # Update session info display
        self.session_info_label.config(
            text=f"Page: {params['page']} | Strategy: {params['strategy']} | Shown: {params['shown_count']}"
        )
        
        # Simulate search (in real app, would call Unsplash API)
        self.update_status(f"Searching '{query}' with variety parameters: Page {params['page']}")
        
        # Record shown image (simulated)
        fake_image_url = f"https://unsplash.com/photos/{query}_{params['page']}_{params['shuffle_seed']}"
        self.session_tracker.record_shown_image(query, fake_image_url, params['page'])
        
        # Update display
        self.image_label.config(text=f"[Image: {query} - Page {params['page']}]")
        self.update_stats()
    
    def shuffle_image(self):
        """Get a different image for the same query."""
        query = self.search_entry.get().strip()
        if query:
            # Force new parameters by adding time component
            import time
            time.sleep(0.1)  # Small delay to ensure different timestamp
            self.perform_search()
    
    def fresh_search(self):
        """Reset history for current query and search again."""
        query = self.search_entry.get().strip()
        if query:
            self.session_tracker.reset_query_history(query)
            self.update_status(f"Reset history for '{query}'")
            self.perform_search()
    
    def generate_description(self):
        """Generate AI description with selected style."""
        query = self.search_entry.get().strip()
        if not query:
            self.update_status("No search query to generate description for")
            return
        
        # Get style-specific prompt
        prompt = self.style_manager.generate_prompt(
            base_context=f"Image search query: {query}",
            user_notes=""
        )
        
        # Update style indicator
        style_info = self.style_manager.get_style_info()
        self.style_indicator.config(
            text=f"Style: {style_info['display_name']}"
        )
        
        # Display sample description based on style
        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(tk.END, f"Generated with {style_info['display_name']}:\n\n")
        
        # Add example phrases
        for phrase in style_info['example_phrases']:
            self.description_text.insert(tk.END, f"{phrase}\n")
        
        # Extract vocabulary for style
        vocab = self.style_manager.extract_vocabulary_for_style("")
        self.vocab_text.delete(1.0, tk.END)
        for category, words in vocab.items():
            self.vocab_text.insert(tk.END, f"{category}:\n")
            self.vocab_text.insert(tk.END, f"  [Vocabulary would be extracted here]\n\n")
        
        self.update_status(f"Description generated using {style_info['style']} style")
    
    def on_style_change(self, style, level):
        """Handle style change from selector."""
        self.save_preferences()
        self.update_status(f"Style changed to: {style.value} - {level.value}")
        self.update_stats()
    
    def set_style(self, style):
        """Set description style from menu."""
        self.style_manager.set_style(style)
        self.style_selector.set_style(style, self.style_manager.current_level)
        self.save_preferences()
    
    def set_level(self, level):
        """Set vocabulary level from menu."""
        self.style_manager.set_style(self.style_manager.current_style, level)
        self.style_selector.set_style(self.style_manager.current_style, level)
        self.save_preferences()
    
    def new_search(self):
        """Clear and prepare for new search."""
        self.search_entry.delete(0, tk.END)
        self.image_label.config(text="[Image will appear here]")
        self.description_text.delete(1.0, tk.END)
        self.vocab_text.delete(1.0, tk.END)
        self.session_info_label.config(text="")
        self.style_indicator.config(text="")
        self.update_status("Ready for new search")
    
    def reset_session(self):
        """Reset all session history."""
        query = self.search_entry.get().strip()
        if query:
            self.session_tracker.reset_query_history(query)
            self.update_status(f"Reset session history for '{query}'")
        else:
            # Reset all history
            for query in list(self.session_tracker.search_history.keys()):
                self.session_tracker.reset_query_history(query)
            self.update_status("All session history cleared")
        self.update_stats()
    
    def show_statistics(self):
        """Show session statistics dialog."""
        stats = self.session_tracker.get_statistics()
        
        # Create stats window
        stats_window = tk.Toplevel(self)
        stats_window.title("Session Statistics")
        stats_window.geometry("500x400")
        
        # Display stats
        text = scrolledtext.ScrolledText(stats_window, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text.insert(tk.END, "📊 Session Statistics\n\n")
        text.insert(tk.END, f"Total Unique Searches: {stats['total_searches']}\n")
        text.insert(tk.END, f"Total Images Shown: {stats['total_images_shown']}\n")
        text.insert(tk.END, f"Data Size: {stats['data_size_mb']:.2f} MB\n\n")
        
        text.insert(tk.END, "🔍 Most Searched Terms:\n")
        for item in stats['most_searched']:
            text.insert(tk.END, f"  • {item['query']}: {item['images']} images\n")
        
        text.insert(tk.END, f"\n📝 Current Style: {self.style_manager.get_style_info()['display_name']}\n")
        
        text.config(state=tk.DISABLED)
    
    def show_history(self):
        """Show search history dialog."""
        # Create history window
        history_window = tk.Toplevel(self)
        history_window.title("Search History")
        history_window.geometry("600x400")
        
        # Display history
        text = scrolledtext.ScrolledText(history_window, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text.insert(tk.END, "📜 Search History\n\n")
        
        for query, session in self.session_tracker.search_history.items():
            text.insert(tk.END, f"Query: {query}\n")
            text.insert(tk.END, f"  Images shown: {len(session.images_shown)}\n")
            text.insert(tk.END, f"  Pages used: {session.page_numbers_used}\n\n")
        
        text.config(state=tk.DISABLED)
    
    def export_stats(self):
        """Export session statistics to file."""
        filepath = Path("./data/session_export.json")
        self.session_tracker.export_history(filepath)
        self.update_status(f"Statistics exported to {filepath}")
    
    def update_status(self, message):
        """Update status bar."""
        self.status_label.config(text=message)
    
    def update_stats(self):
        """Update statistics label."""
        stats = self.session_tracker.get_statistics()
        self.stats_label.config(
            text=f"Searches: {stats['total_searches']} | Images: {stats['total_images_shown']}"
        )
    
    def save_preferences(self):
        """Save user preferences."""
        self.preferences_file.parent.mkdir(parents=True, exist_ok=True)
        
        preferences = {
            "style": self.style_manager.current_style.value,
            "level": self.style_manager.current_level.value
        }
        
        with open(self.preferences_file, 'w') as f:
            json.dump(preferences, f, indent=2)
    
    def load_preferences(self):
        """Load user preferences."""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r') as f:
                    preferences = json.load(f)
                
                style = DescriptionStyle(preferences.get("style", "academic"))
                level = VocabularyLevel(preferences.get("level", "intermediate"))
                self.style_manager.set_style(style, level)
            except (json.JSONDecodeError, ValueError):
                pass


def main():
    """Run the enhanced demo application."""
    app = EnhancedImageSearchApp()
    app.mainloop()


if __name__ == "__main__":
    main()