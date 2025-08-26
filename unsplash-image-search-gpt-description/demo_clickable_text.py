"""
Simple demo of the ClickableText component.
This demonstrates the functionality without complex imports.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import sys
import os
from pathlib import Path
import re
import csv
from datetime import datetime

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


class SimpleVocabularyManager:
    """Simplified vocabulary manager for demo."""
    
    def __init__(self):
        self.vocab_file = Path("demo_vocabulary.csv")
        self.vocabulary_cache = set()
        self._initialize_csv()
        self._load_cache()
    
    def _initialize_csv(self):
        if not self.vocab_file.exists():
            with open(self.vocab_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Spanish', 'English', 'Date', 'Context'])
    
    def _load_cache(self):
        try:
            with open(self.vocab_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'Spanish' in row and row['Spanish']:
                        self.vocabulary_cache.add(row['Spanish'])
        except:
            pass
    
    def add_word(self, spanish, english, context=""):
        if spanish in self.vocabulary_cache:
            return False
        
        try:
            with open(self.vocab_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([spanish, english, datetime.now().strftime("%Y-%m-%d %H:%M"), context])
            self.vocabulary_cache.add(spanish)
            return True
        except:
            return False
    
    def is_duplicate(self, word):
        return word in self.vocabulary_cache
    
    def get_count(self):
        return len(self.vocabulary_cache)


class SimpleClickableText(scrolledtext.ScrolledText):
    """Simplified clickable text widget for demo."""
    
    def __init__(self, parent, vocab_manager=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.vocab_manager = vocab_manager
        self.is_clickable = True
        self.popup_window = None
        
        # Configure tags
        self.tag_configure("clickable", underline=False, foreground="blue")
        self.tag_configure("highlight", background="yellow", relief="raised")
        
        # Bind events
        self.tag_bind("clickable", "<Button-1>", self._on_word_click)
        self.tag_bind("clickable", "<Enter>", lambda e: self.configure(cursor="hand2"))
        self.tag_bind("clickable", "<Leave>", lambda e: self.configure(cursor=""))
        
        self.bind("<<Modified>>", self._on_text_modified)
        
    def _on_text_modified(self, event):
        if self.is_clickable and self.edit_modified():
            self.after_idle(self._make_clickable)
            self.edit_modified(False)
    
    def _make_clickable(self):
        content = self.get("1.0", tk.END)
        self.tag_remove("clickable", "1.0", tk.END)
        
        # Simple Spanish word pattern
        word_pattern = r'\b[a-zA-ZáéíóúñüÁÉÍÓÚÑÜ]{3,}\b'
        
        for match in re.finditer(word_pattern, content):
            word = match.group()
            if self._is_spanish_word(word):
                start_pos = self._pos_to_index(match.start())
                end_pos = self._pos_to_index(match.end())
                self.tag_add("clickable", start_pos, end_pos)
    
    def _is_spanish_word(self, word):
        # Skip common words
        skip_words = {'el', 'la', 'los', 'las', 'un', 'una', 'de', 'del', 'en', 'con', 'por', 'para', 'que', 'como', 'muy', 'más', 'son', 'está', 'hay', 'the', 'and', 'is', 'are'}
        if word.lower() in skip_words:
            return False
        
        # Check if already in vocabulary
        if self.vocab_manager and self.vocab_manager.is_duplicate(word):
            return False
        
        # Spanish character check or reasonable length
        spanish_chars = set('áéíóúñüÁÉÍÓÚÑÜ')
        return any(char in spanish_chars for char in word) or len(word) >= 4
    
    def _pos_to_index(self, pos):
        lines = self.get("1.0", tk.END).split('\n')
        current_pos = 0
        for line_num, line in enumerate(lines, 1):
            if current_pos + len(line) >= pos:
                char_pos = pos - current_pos
                return f"{line_num}.{char_pos}"
            current_pos += len(line) + 1
        return "end"
    
    def _on_word_click(self, event):
        if not self.is_clickable:
            return
        
        index = self.index(f"@{event.x},{event.y}")
        word = self._get_word_at_index(index)
        if not word:
            return
        
        # Highlight word
        word_start, word_end = self._get_word_bounds(index)
        self._highlight_word(word_start, word_end)
        
        # Process the word
        self._process_word(word, word_start, word_end)
    
    def _get_word_at_index(self, index):
        try:
            char = self.get(index)
            if not char.isalpha():
                return None
            word_start, word_end = self._get_word_bounds(index)
            return self.get(word_start, word_end).strip()
        except:
            return None
    
    def _get_word_bounds(self, index):
        # Find word boundaries
        word_start = index
        while True:
            prev_index = self.index(f"{word_start} -1c")
            if prev_index == word_start:
                break
            prev_char = self.get(prev_index)
            if not (prev_char.isalpha() or prev_char in 'áéíóúñüÁÉÍÓÚÑÜ'):
                break
            word_start = prev_index
        
        word_end = index
        while True:
            next_index = self.index(f"{word_end} +1c")
            if next_index == word_end:
                break
            try:
                next_char = self.get(word_end)
                if not (next_char.isalpha() or next_char in 'áéíóúñüÁÉÍÓÚÑÜ'):
                    break
                word_end = next_index
            except:
                break
        
        return word_start, word_end
    
    def _highlight_word(self, start, end):
        self.tag_remove("highlight", "1.0", tk.END)
        self.tag_add("highlight", start, end)
        self.after(1500, lambda: self.tag_remove("highlight", "1.0", tk.END))
    
    def _process_word(self, word, start, end):
        # Simple mock translation
        translations = {
            'playa': 'beach',
            'agua': 'water', 
            'hermosa': 'beautiful',
            'cristalina': 'crystal clear',
            'arena': 'sand',
            'palmeras': 'palm trees',
            'cielo': 'sky',
            'nubes': 'clouds',
            'olas': 'waves',
            'tropical': 'tropical',
            'turistas': 'tourists',
            'temperatura': 'temperature',
            'paraíso': 'paradise',
            'experiencia': 'experience',
            'natural': 'natural',
            'tranquilo': 'peaceful',
            'relajante': 'relaxing',
            'perfecta': 'perfect',
            'belleza': 'beauty'
        }
        
        translation = translations.get(word.lower(), f"[Translation of '{word}']")
        
        # Get context
        context = self._get_context(start, end)
        
        if self.vocab_manager:
            success = self.vocab_manager.add_word(word, translation, context)
            if success:
                self._show_popup(f"Added: '{word}' = '{translation}'", "success")
            else:
                self._show_popup(f"'{word}' already in vocabulary", "warning")
        else:
            self._show_popup(f"Clicked: '{word}' = '{translation}'", "info")
    
    def _get_context(self, start, end, words_around=3):
        try:
            full_text = self.get("1.0", tk.END).strip()
            word_pos = len(self.get("1.0", start))
            words = full_text.split()
            
            # Find word index
            current_pos = 0
            word_index = -1
            for i, w in enumerate(words):
                if current_pos <= word_pos < current_pos + len(w):
                    word_index = i
                    break
                current_pos += len(w) + 1
            
            if word_index >= 0:
                start_ctx = max(0, word_index - words_around)
                end_ctx = min(len(words), word_index + words_around + 1)
                return " ".join(words[start_ctx:end_ctx])[:80]
            return ""
        except:
            return ""
    
    def _show_popup(self, message, type="info"):
        if self.popup_window:
            self.popup_window.destroy()
        
        self.popup_window = tk.Toplevel(self)
        self.popup_window.title("Word Processed")
        self.popup_window.geometry("300x100")
        self.popup_window.resizable(False, False)
        self.popup_window.transient(self.winfo_toplevel())
        
        # Center popup
        self.popup_window.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - 300) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 100) // 2
        self.popup_window.geometry(f"+{x}+{y}")
        
        # Content
        frame = tk.Frame(self.popup_window, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        colors = {"success": "green", "warning": "orange", "info": "blue"}
        color = colors.get(type, "blue")
        
        label = tk.Label(frame, text=message, wraplength=250, fg=color)
        label.pack(pady=(0, 10))
        
        tk.Button(frame, text="Close", command=self.popup_window.destroy).pack()
        
        # Auto-close
        self.popup_window.after(2500, self.popup_window.destroy)
    
    def set_clickable(self, clickable):
        self.is_clickable = clickable
        if clickable:
            self._make_clickable()
        else:
            self.tag_remove("clickable", "1.0", tk.END)


class ClickableTextDemo:
    """Demo application."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ClickableText Demo")
        self.root.geometry("700x600")
        
        self.vocab_manager = SimpleVocabularyManager()
        self.create_ui()
        self.load_sample_text()
    
    def create_ui(self):
        # Title
        title_label = tk.Label(self.root, text="ClickableText Component Demo", 
                              font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(self.root, 
                               text="Click on Spanish words below to translate and add to vocabulary",
                               font=('Arial', 10), fg='gray')
        instructions.pack(pady=(0, 10))
        
        # Controls
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=(0, 10))
        
        tk.Button(control_frame, text="Load New Text", command=self.load_sample_text).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(control_frame, text="Toggle Clickable", command=self.toggle_clickable).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(control_frame, text="Show Vocabulary", command=self.show_vocabulary).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(control_frame, text="Clear Text", command=self.clear_text).pack(side=tk.LEFT)
        
        # Text area
        text_frame = tk.LabelFrame(self.root, text="Clickable Spanish Text", padx=10, pady=10)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.text_widget = SimpleClickableText(text_frame, vocab_manager=self.vocab_manager,
                                              wrap=tk.WORD, font=('TkDefaultFont', 12))
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Status
        self.status_label = tk.Label(self.root, text="Ready - Click on Spanish words to translate them",
                                    relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=5, pady=5)
    
    def load_sample_text(self):
        texts = [
            """Esta imagen muestra una playa tropical hermosa con agua cristalina y arena blanca. 
Las palmeras proporcionan sombra natural para los turistas que visitan este paraíso. 
El cielo está despejado con algunas nubes blancas que flotan tranquilamente.""",
            
            """La ciudad nocturna cobra vida con luces brillantes en todos los rascacielos. 
Las calles están llenas de personas que caminan por las aceras iluminadas. 
Los restaurantes permanecen abiertos hasta muy tarde en la noche.""",
            
            """En las montañas, el paisaje es espectacular durante todas las estaciones del año. 
Los senderos permiten a los excursionistas explorar la naturaleza salvaje. 
La temperatura fresca hace que la experiencia sea muy agradable."""
        ]
        
        import random
        selected_text = random.choice(texts)
        
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, selected_text)
        self.status_label.config(text="New text loaded - try clicking on Spanish words")
    
    def toggle_clickable(self):
        current = self.text_widget.is_clickable
        self.text_widget.set_clickable(not current)
        status = "enabled" if not current else "disabled"
        self.status_label.config(text=f"Clickable functionality {status}")
    
    def show_vocabulary(self):
        count = self.vocab_manager.get_count()
        self.status_label.config(text=f"Vocabulary entries: {count}")
        
        if count > 0:
            # Show recent entries
            try:
                with open(self.vocab_manager.vocab_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader)  # Skip header
                    entries = list(reader)
                    
                if entries:
                    recent = entries[-5:]  # Last 5 entries
                    messagebox.showinfo("Recent Vocabulary", 
                                       "\n".join([f"'{row[0]}' = '{row[1]}'" for row in recent]))
            except:
                messagebox.showinfo("Vocabulary", f"You have {count} vocabulary entries")
    
    def clear_text(self):
        self.text_widget.delete("1.0", tk.END)
        self.status_label.config(text="Text cleared")
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    print("Starting ClickableText Demo...")
    print("This demo shows the basic functionality of the clickable text component.")
    print("Click on Spanish words to translate them and add to vocabulary.")
    print("Vocabulary is saved to demo_vocabulary.csv")
    
    try:
        demo = ClickableTextDemo()
        demo.run()
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()