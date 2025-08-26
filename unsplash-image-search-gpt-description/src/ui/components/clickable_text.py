"""
Clickable Text Component for Spanish vocabulary learning.

This component makes text clickable for word selection and translation.
When users click on Spanish words, they are automatically translated and added
to the vocabulary list with confirmation popup.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import re
import threading
from typing import Optional, Callable, Dict, Any
from pathlib import Path

try:
    from ..theme_manager import ThemeManager
except ImportError:
    ThemeManager = None

try:
    from ...models.vocabulary import VocabularyManager, VocabularyEntry
except ImportError:
    try:
        import sys
        sys.path.append(str(Path(__file__).parent.parent.parent))
        from models.vocabulary import VocabularyManager, VocabularyEntry
    except ImportError:
        VocabularyManager = None
        VocabularyEntry = None

try:
    from ...services.openai_service import OpenAIService
except ImportError:
    try:
        import sys
        sys.path.append(str(Path(__file__).parent.parent.parent))
        from services.openai_service import OpenAIService
    except ImportError:
        OpenAIService = None


class ClickableText(scrolledtext.ScrolledText):
    """
    A ScrolledText widget that makes Spanish words clickable for vocabulary learning.
    
    Features:
    - Click detection on individual words
    - Word highlighting with themes
    - Automatic translation via OpenAI
    - Vocabulary storage with context
    - Popup confirmation dialogs
    - Integration with existing theme system
    """
    
    def __init__(self, parent, vocabulary_manager = None,
                 openai_service = None, theme_manager = None,
                 current_search_query: str = "", current_image_url: str = "", **kwargs):
        """
        Initialize the clickable text widget.
        
        Args:
            parent: Parent widget
            vocabulary_manager: Manager for vocabulary storage
            openai_service: Service for translations
            theme_manager: Theme manager for styling
            current_search_query: Current search context
            current_image_url: Current image URL for context
            **kwargs: Additional ScrolledText arguments
        """
        super().__init__(parent, **kwargs)
        
        # Store references
        self.vocabulary_manager = vocabulary_manager
        self.openai_service = openai_service
        self.theme_manager = theme_manager
        self.current_search_query = current_search_query
        self.current_image_url = current_image_url
        
        # State tracking
        self.is_clickable = True
        self.click_callbacks: Dict[str, Callable] = {}
        self.popup_window: Optional[tk.Toplevel] = None
        self.highlight_tag = "word_highlight"
        self.click_tag = "clickable_word"
        
        # Setup the widget
        self._setup_tags()
        self._bind_events()
        
        # Apply theme if available
        if self.theme_manager:
            self.theme_manager.register_theme_callback(self._on_theme_changed)
            self._apply_current_theme()
    
    def _setup_tags(self):
        """Configure text tags for highlighting and interaction."""
        colors = self._get_theme_colors()
        
        # Highlight tag for temporary word highlighting
        self.tag_configure(self.highlight_tag, 
                          background=colors.get('select_bg', '#0078d4'),
                          foreground=colors.get('select_fg', '#ffffff'),
                          relief='raised',
                          borderwidth=1)
        
        # Clickable word tag
        self.tag_configure(self.click_tag,
                          underline=False,
                          foreground=colors.get('fg', '#000000'))
        
        # Add hover effect
        self.tag_bind(self.click_tag, '<Enter>', self._on_word_hover)
        self.tag_bind(self.click_tag, '<Leave>', self._on_word_leave)
        self.tag_bind(self.click_tag, '<Button-1>', self._on_word_click)
    
    def _bind_events(self):
        """Bind necessary events for interaction."""
        # Rebind text insertion to make new text clickable
        self.bind('<<Modified>>', self._on_text_modified)
        
        # Handle cursor changes for better UX
        self.bind('<Motion>', self._on_mouse_motion)
    
    def _get_theme_colors(self) -> Dict[str, str]:
        """Get current theme colors."""
        if self.theme_manager:
            return self.theme_manager.get_colors()
        else:
            # Default light theme colors
            return {
                'bg': '#ffffff',
                'fg': '#000000',
                'select_bg': '#0078d4',
                'select_fg': '#ffffff',
                'text_bg': '#ffffff',
                'text_fg': '#000000',
                'success': '#107c10',
                'warning': '#ff8c00',
                'error': '#d13438'
            }
    
    def _apply_current_theme(self):
        """Apply the current theme to the widget."""
        if self.theme_manager:
            self.theme_manager.configure_widget(self, 'ScrolledText')
            self._setup_tags()  # Reconfigure tags with new colors
    
    def _on_theme_changed(self, theme_name: str, colors: Dict[str, str]):
        """Handle theme change events."""
        self._setup_tags()  # Reconfigure tags with new colors
    
    def _on_text_modified(self, event):
        """Handle text modification to make new content clickable."""
        if self.is_clickable and self.edit_modified():
            self.after_idle(self._make_text_clickable)
            self.edit_modified(False)
    
    def _make_text_clickable(self):
        """Make Spanish words in the text clickable."""
        if not self.is_clickable:
            return
            
        # Get all text content
        content = self.get("1.0", tk.END)
        
        # Remove existing clickable tags
        self.tag_remove(self.click_tag, "1.0", tk.END)
        
        # Spanish word pattern (including accented characters)
        word_pattern = r'\b[a-zA-ZáéíóúñüÁÉÍÓÚÑÜ]+\b'
        
        # Find all Spanish words and make them clickable
        for match in re.finditer(word_pattern, content):
            word = match.group()
            start_pos = match.start()
            end_pos = match.end()
            
            # Skip very short words (articles, prepositions, etc.)
            if len(word) >= 3 and self._is_likely_spanish_word(word):
                # Convert to text widget indices
                start_index = self._pos_to_index(start_pos)
                end_index = self._pos_to_index(end_pos)
                
                # Apply clickable tag
                self.tag_add(self.click_tag, start_index, end_index)
    
    def _is_likely_spanish_word(self, word: str) -> bool:
        """
        Simple heuristic to identify likely Spanish words.
        This filters out very common words that aren't useful for learning.
        """
        # Common Spanish articles, prepositions, and conjunctions to skip
        skip_words = {
            'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
            'de', 'del', 'en', 'con', 'por', 'para', 'sin', 'sobre',
            'que', 'como', 'pero', 'sino', 'porque', 'cuando',
            'muy', 'más', 'menos', 'tan', 'tanto', 'toda', 'todo',
            'son', 'está', 'están', 'hay', 'fue', 'ser', 'era',
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'of', 'for', 'with', 'by', 'from', 'is', 'are', 'was'
        }
        
        # Convert to lowercase for checking
        word_lower = word.lower()
        
        # Skip if it's a common word
        if word_lower in skip_words:
            return False
            
        # Skip if already in vocabulary (optional - you might want to allow re-clicking)
        if self.vocabulary_manager and self.vocabulary_manager.is_duplicate(word):
            return False
            
        # If it contains Spanish characters, it's likely Spanish
        spanish_chars = set('áéíóúñüÁÉÍÓÚÑÜ')
        if any(char in spanish_chars for char in word):
            return True
            
        # If it's a reasonable length and doesn't look like English, include it
        if len(word) >= 4:
            return True
            
        return False
    
    def _pos_to_index(self, pos: int) -> str:
        """Convert character position to tkinter text index."""
        lines = self.get("1.0", tk.END).split('\n')
        current_pos = 0
        
        for line_num, line in enumerate(lines, 1):
            if current_pos + len(line) >= pos:
                char_pos = pos - current_pos
                return f"{line_num}.{char_pos}"
            current_pos += len(line) + 1  # +1 for newline
        
        return "end"
    
    def _on_word_hover(self, event):
        """Handle mouse hover over clickable word."""
        if self.is_clickable:
            self.configure(cursor="hand2")
    
    def _on_word_leave(self, event):
        """Handle mouse leave from clickable word."""
        self.configure(cursor="")
    
    def _on_mouse_motion(self, event):
        """Handle mouse motion to update cursor."""
        if not self.is_clickable:
            return
            
        # Get position under mouse
        index = self.index(f"@{event.x},{event.y}")
        
        # Check if mouse is over a clickable word
        tags = self.tag_names(index)
        if self.click_tag in tags:
            self.configure(cursor="hand2")
        else:
            self.configure(cursor="")
    
    def _on_word_click(self, event):
        """Handle click on a Spanish word."""
        if not self.is_clickable:
            return
            
        # Get the clicked position
        index = self.index(f"@{event.x},{event.y}")
        
        # Get the word at this position
        word = self._get_word_at_index(index)
        if not word:
            return
            
        # Highlight the word temporarily
        word_start, word_end = self._get_word_bounds(index)
        self._highlight_word(word_start, word_end)
        
        # Process the word (translate and add to vocabulary)
        self._process_clicked_word(word, word_start, word_end)
    
    def _get_word_at_index(self, index: str) -> Optional[str]:
        """Get the word at the given index."""
        try:
            # Get the character at the index
            char = self.get(index)
            if not char.isalpha():
                return None
                
            # Find word boundaries
            word_start, word_end = self._get_word_bounds(index)
            word = self.get(word_start, word_end)
            return word.strip()
        except:
            return None
    
    def _get_word_bounds(self, index: str) -> tuple:
        """Get the start and end indices of the word containing the given index."""
        # Move to beginning of word
        word_start = index
        while True:
            prev_char_index = self.index(f"{word_start} -1c")
            if prev_char_index == word_start:  # At beginning of text
                break
            prev_char = self.get(prev_char_index)
            if not (prev_char.isalpha() or prev_char in 'áéíóúñüÁÉÍÓÚÑÜ'):
                break
            word_start = prev_char_index
        
        # Move to end of word
        word_end = index
        while True:
            next_char_index = self.index(f"{word_end} +1c")
            if next_char_index == word_end:  # At end of text
                break
            try:
                next_char = self.get(word_end)
                if not (next_char.isalpha() or next_char in 'áéíóúñüÁÉÍÓÚÑÜ'):
                    break
                word_end = next_char_index
            except:
                break
        
        return word_start, word_end
    
    def _highlight_word(self, start_index: str, end_index: str):
        """Temporarily highlight a word."""
        # Remove any existing highlights
        self.tag_remove(self.highlight_tag, "1.0", tk.END)
        
        # Add highlight to the selected word
        self.tag_add(self.highlight_tag, start_index, end_index)
        
        # Remove highlight after a short delay
        self.after(2000, lambda: self.tag_remove(self.highlight_tag, "1.0", tk.END))
    
    def _process_clicked_word(self, word: str, start_index: str, end_index: str):
        """Process a clicked word - translate and add to vocabulary."""
        if not word or not self.openai_service or not self.vocabulary_manager:
            self._show_simple_popup(f"Clicked: {word}", "No translation service available.")
            return
        
        # Check if already in vocabulary
        if self.vocabulary_manager.is_duplicate(word):
            self._show_simple_popup(f"'{word}'", "Already in vocabulary!")
            return
        
        # Show loading popup
        self._show_loading_popup(f"Translating '{word}'...")
        
        # Translate in background thread
        threading.Thread(
            target=self._translate_and_add_word,
            args=(word, start_index, end_index),
            daemon=True,
            name="WordTranslation"
        ).start()
    
    def _translate_and_add_word(self, word: str, start_index: str, end_index: str):
        """Translate word and add to vocabulary (background thread)."""
        try:
            # Get translation
            translation = self._translate_word(word)
            
            # Get context from surrounding text
            context = self._get_word_context(start_index, end_index)
            
            # Create vocabulary entry
            if VocabularyEntry:
                vocab_entry = VocabularyEntry(
                    spanish=word,
                    english=translation,
                    search_query=self.current_search_query,
                    image_url=self.current_image_url,
                    context=context
                )
            else:
                # Create a simple dictionary if VocabularyEntry is not available
                vocab_entry = {
                    'spanish': word,
                    'english': translation,
                    'search_query': self.current_search_query,
                    'image_url': self.current_image_url,
                    'context': context
                }
            
            # Add to vocabulary
            success = self.vocabulary_manager.add_vocabulary_entry(vocab_entry)
            
            # Show result popup on main thread
            self.after(0, lambda: self._show_result_popup(word, translation, success))
            
        except Exception as e:
            # Show error popup on main thread
            self.after(0, lambda: self._show_error_popup(word, str(e)))
    
    def _translate_word(self, word: str) -> str:
        """Translate a Spanish word to English."""
        try:
            prompt = f"Translate this Spanish word to English, providing only the most common/appropriate translation: '{word}'"
            
            response = self.openai_service.client.chat.completions.create(
                model=self.openai_service.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.0
            )
            
            translation = response.choices[0].message.content.strip()
            
            # Clean up the response (remove quotes, extra text)
            translation = re.sub(r'^["\']|["\']$', '', translation)
            translation = translation.split('.')[0]  # Take first sentence
            translation = translation.split(',')[0]  # Take first part before comma
            
            return translation[:50]  # Limit length
            
        except Exception as e:
            print(f"Translation error: {e}")
            return "[Translation failed]"
    
    def _get_word_context(self, start_index: str, end_index: str, context_words: int = 5) -> str:
        """Get surrounding context for a word."""
        try:
            # Get the full text
            full_text = self.get("1.0", tk.END).strip()
            
            # Find the word position in the text
            word_start_pos = len(self.get("1.0", start_index))
            word_end_pos = len(self.get("1.0", end_index))
            
            # Split text into words
            words = full_text.split()
            
            # Find word index in the word list
            current_pos = 0
            word_index = -1
            for i, w in enumerate(words):
                if current_pos <= word_start_pos < current_pos + len(w):
                    word_index = i
                    break
                current_pos += len(w) + 1  # +1 for space
            
            if word_index >= 0:
                # Get context words before and after
                start_ctx = max(0, word_index - context_words)
                end_ctx = min(len(words), word_index + context_words + 1)
                context_words_list = words[start_ctx:end_ctx]
                return " ".join(context_words_list)[:100]  # Limit context length
            
            return ""
            
        except Exception as e:
            print(f"Context extraction error: {e}")
            return ""
    
    def _show_loading_popup(self, message: str):
        """Show loading popup."""
        self._close_popup()
        
        colors = self._get_theme_colors()
        
        self.popup_window = tk.Toplevel(self)
        self.popup_window.title("Processing...")
        self.popup_window.geometry("250x100")
        self.popup_window.configure(bg=colors.get('bg', '#ffffff'))
        self.popup_window.resizable(False, False)
        self.popup_window.transient(self.winfo_toplevel())
        
        # Center popup over the widget
        self._center_popup()
        
        # Loading content
        frame = tk.Frame(self.popup_window, bg=colors.get('bg', '#ffffff'), padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Progress bar
        progress = ttk.Progressbar(frame, mode='indeterminate')
        progress.pack(pady=(0, 10))
        progress.start(10)
        
        # Message
        label = tk.Label(
            frame, 
            text=message, 
            bg=colors.get('bg', '#ffffff'),
            fg=colors.get('fg', '#000000'),
            font=('TkDefaultFont', 9)
        )
        label.pack()
        
        # Auto-close after timeout
        self.popup_window.after(10000, self._close_popup)
    
    def _show_result_popup(self, word: str, translation: str, success: bool):
        """Show result popup with translation and success status."""
        self._close_popup()
        
        colors = self._get_theme_colors()
        
        self.popup_window = tk.Toplevel(self)
        self.popup_window.title("Word Added!" if success else "Already Exists")
        self.popup_window.geometry("300x150")
        self.popup_window.configure(bg=colors.get('bg', '#ffffff'))
        self.popup_window.resizable(False, False)
        self.popup_window.transient(self.winfo_toplevel())
        
        self._center_popup()
        
        # Main frame
        frame = tk.Frame(self.popup_window, bg=colors.get('bg', '#ffffff'), padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Status icon and message
        if success:
            status_color = colors.get('success', '#107c10')
            status_icon = "✓"
            status_text = "Added to vocabulary!"
        else:
            status_color = colors.get('warning', '#ff8c00')
            status_icon = "⚠"
            status_text = "Already in vocabulary"
        
        # Status header
        status_frame = tk.Frame(frame, bg=colors.get('bg', '#ffffff'))
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        icon_label = tk.Label(
            status_frame,
            text=status_icon,
            font=('TkDefaultFont', 16, 'bold'),
            fg=status_color,
            bg=colors.get('bg', '#ffffff')
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        status_label = tk.Label(
            status_frame,
            text=status_text,
            font=('TkDefaultFont', 10, 'bold'),
            fg=colors.get('fg', '#000000'),
            bg=colors.get('bg', '#ffffff')
        )
        status_label.pack(side=tk.LEFT)
        
        # Word and translation
        word_label = tk.Label(
            frame,
            text=f"'{word}' = '{translation}'",
            font=('TkDefaultFont', 11),
            fg=colors.get('fg', '#000000'),
            bg=colors.get('bg', '#ffffff'),
            wraplength=260
        )
        word_label.pack(pady=(0, 10))
        
        # Close button
        close_btn = tk.Button(
            frame,
            text="Close",
            command=self._close_popup,
            bg=colors.get('button_bg', '#e1e1e1'),
            fg=colors.get('button_fg', '#000000'),
            activebackground=colors.get('button_active_bg', '#d0d0d0'),
            relief=tk.FLAT,
            padx=20
        )
        close_btn.pack()
        
        # Auto-close after 3 seconds
        self.popup_window.after(3000, self._close_popup)
    
    def _show_error_popup(self, word: str, error: str):
        """Show error popup."""
        self._close_popup()
        
        colors = self._get_theme_colors()
        
        self.popup_window = tk.Toplevel(self)
        self.popup_window.title("Translation Error")
        self.popup_window.geometry("300x120")
        self.popup_window.configure(bg=colors.get('bg', '#ffffff'))
        self.popup_window.resizable(False, False)
        self.popup_window.transient(self.winfo_toplevel())
        
        self._center_popup()
        
        # Error content
        frame = tk.Frame(self.popup_window, bg=colors.get('bg', '#ffffff'), padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Error icon
        error_label = tk.Label(
            frame,
            text=f"✗ Failed to translate '{word}'",
            font=('TkDefaultFont', 10, 'bold'),
            fg=colors.get('error', '#d13438'),
            bg=colors.get('bg', '#ffffff')
        )
        error_label.pack(pady=(0, 5))
        
        # Error message
        msg_label = tk.Label(
            frame,
            text=error[:50] + "..." if len(error) > 50 else error,
            font=('TkDefaultFont', 9),
            fg=colors.get('fg', '#000000'),
            bg=colors.get('bg', '#ffffff'),
            wraplength=260
        )
        msg_label.pack(pady=(0, 10))
        
        # Close button
        close_btn = tk.Button(
            frame,
            text="Close",
            command=self._close_popup,
            bg=colors.get('button_bg', '#e1e1e1'),
            fg=colors.get('button_fg', '#000000'),
            relief=tk.FLAT,
            padx=20
        )
        close_btn.pack()
        
        # Auto-close after 3 seconds
        self.popup_window.after(3000, self._close_popup)
    
    def _show_simple_popup(self, title: str, message: str):
        """Show a simple informational popup."""
        self._close_popup()
        
        colors = self._get_theme_colors()
        
        self.popup_window = tk.Toplevel(self)
        self.popup_window.title("Info")
        self.popup_window.geometry("250x100")
        self.popup_window.configure(bg=colors.get('bg', '#ffffff'))
        self.popup_window.resizable(False, False)
        self.popup_window.transient(self.winfo_toplevel())
        
        self._center_popup()
        
        frame = tk.Frame(self.popup_window, bg=colors.get('bg', '#ffffff'), padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            frame,
            text=title,
            font=('TkDefaultFont', 10, 'bold'),
            fg=colors.get('fg', '#000000'),
            bg=colors.get('bg', '#ffffff')
        ).pack()
        
        tk.Label(
            frame,
            text=message,
            font=('TkDefaultFont', 9),
            fg=colors.get('fg', '#000000'),
            bg=colors.get('bg', '#ffffff')
        ).pack(pady=(5, 0))
        
        # Auto-close after 2 seconds
        self.popup_window.after(2000, self._close_popup)
    
    def _center_popup(self):
        """Center popup over the parent widget."""
        if not self.popup_window:
            return
            
        # Update popup to get actual size
        self.popup_window.update_idletasks()
        
        # Get popup size
        popup_width = self.popup_window.winfo_width()
        popup_height = self.popup_window.winfo_height()
        
        # Get parent widget position and size
        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()
        
        # Calculate centered position
        x = parent_x + (parent_width - popup_width) // 2
        y = parent_y + (parent_height - popup_height) // 2
        
        # Ensure popup stays on screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        x = max(10, min(x, screen_width - popup_width - 10))
        y = max(10, min(y, screen_height - popup_height - 10))
        
        self.popup_window.geometry(f"+{x}+{y}")
    
    def _close_popup(self):
        """Close the current popup window."""
        if self.popup_window:
            try:
                self.popup_window.destroy()
            except:
                pass
            self.popup_window = None
    
    # Public API methods
    
    def set_clickable(self, clickable: bool):
        """Enable or disable word clicking."""
        self.is_clickable = clickable
        if clickable:
            self._make_text_clickable()
        else:
            self.tag_remove(self.click_tag, "1.0", tk.END)
            self.configure(cursor="")
    
    def update_context(self, search_query: str = "", image_url: str = ""):
        """Update the context information for new vocabulary entries."""
        self.current_search_query = search_query
        self.current_image_url = image_url
    
    def insert(self, index, chars, *args):
        """Override insert to make new text clickable."""
        result = super().insert(index, chars, *args)
        if self.is_clickable:
            self.after_idle(self._make_text_clickable)
        return result
    
    def delete(self, index1, index2=None):
        """Override delete to clean up tags."""
        result = super().delete(index1, index2)
        if self.is_clickable:
            self.after_idle(self._make_text_clickable)
        return result
    
    def clear(self):
        """Clear all text and tags."""
        self.delete("1.0", tk.END)
        self._close_popup()
    
    def register_click_callback(self, event_type: str, callback: Callable):
        """Register callbacks for click events."""
        self.click_callbacks[event_type] = callback
    
    def destroy(self):
        """Clean up when destroying the widget."""
        self._close_popup()
        super().destroy()


# Example usage and integration helper
def integrate_with_existing_app():
    """
    Example of how to integrate ClickableText with existing application.
    Replace the existing ScrolledText widget in main.py.
    """
    example_code = '''
    # In main.py, replace the description_text ScrolledText widget:
    
    # OLD CODE:
    # self.description_text = scrolledtext.ScrolledText(
    #     desc_frame, 
    #     wrap=tk.WORD, 
    #     state=tk.DISABLED,
    #     font=("TkDefaultFont", 12)
    # )
    
    # NEW CODE:
    from src.ui.components.clickable_text import ClickableText
    
    self.description_text = ClickableText(
        desc_frame,
        vocabulary_manager=self.vocabulary_manager,  # You'll need to create this
        openai_service=self.openai_service,          # Already exists
        theme_manager=self.theme_manager,            # Already exists  
        wrap=tk.WORD,
        state=tk.DISABLED,
        font=("TkDefaultFont", 12)
    )
    
    # Update context when displaying new descriptions:
    def display_description(self, text):
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.update_context(
            search_query=self.current_query,
            image_url=self.current_image_url
        )
        self.description_text.insert(tk.END, text)
        self.description_text.config(state=tk.DISABLED)
        # Note: Clickable functionality works even when state=DISABLED for display
    '''
    
    return example_code


if __name__ == "__main__":
    # Simple test of the component
    import tkinter as tk
    
    root = tk.Tk()
    root.title("Clickable Text Test")
    root.geometry("500x400")
    
    # Create a simple test
    clickable_text = ClickableText(root, wrap=tk.WORD)
    clickable_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Add some sample Spanish text
    sample_text = """
    Esta es una imagen hermosa de una playa tropical. 
    Se puede ver el agua cristalina y la arena blanca. 
    Los árboles de coco proporcionan sombra natural.
    El cielo está despejado con algunas nubes blancas.
    """
    
    clickable_text.insert(tk.END, sample_text.strip())
    
    # Add instructions
    instructions = tk.Label(
        root, 
        text="Click on Spanish words to translate and add to vocabulary\n(Note: Translation requires API setup)",
        font=('TkDefaultFont', 9),
        fg='gray'
    )
    instructions.pack(pady=5)
    
    root.mainloop()