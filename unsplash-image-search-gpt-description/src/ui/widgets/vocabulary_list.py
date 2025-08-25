"""
Vocabulary list widget for displaying extracted phrases and target words.
"""

import tkinter as tk
from tkinter import ttk


class VocabularyList(ttk.LabelFrame):
    """Widget for displaying target vocabulary with large, readable font."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="Frases Objetivo", padding="10", **kwargs)
        
        self.target_listbox = tk.Listbox(self)
        self.target_listbox.configure(font=("TkDefaultFont", 14))
        self.target_listbox.pack(fill=tk.BOTH, expand=True)
        
        self.target_phrases = []
    
    def add_phrase(self, phrase):
        """Add a phrase to the vocabulary list."""
        if phrase not in self.target_phrases:
            self.target_phrases.append(phrase)
            self.update_display()
    
    def remove_phrase(self, phrase):
        """Remove a phrase from the vocabulary list."""
        if phrase in self.target_phrases:
            self.target_phrases.remove(phrase)
            self.update_display()
    
    def clear_phrases(self):
        """Clear all phrases from the vocabulary list."""
        self.target_phrases.clear()
        self.update_display()
    
    def update_display(self):
        """Update the listbox display."""
        self.target_listbox.delete(0, tk.END)
        for phrase in self.target_phrases:
            self.target_listbox.insert(tk.END, phrase)
    
    def get_phrases(self):
        """Get all target phrases."""
        return self.target_phrases.copy()


class ExtractedPhrases(ttk.LabelFrame):
    """Widget for displaying extracted phrases organized by category."""
    
    def __init__(self, parent, on_phrase_click=None, **kwargs):
        super().__init__(parent, text="Frases Extraídas", padding="10", **kwargs)
        self.on_phrase_click = on_phrase_click
        
        # Create canvas for scrollable content
        self.canvas = tk.Canvas(self)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        v_scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=v_scroll.set)
        
        # Inner frame for content
        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Initial placeholder
        self.placeholder = ttk.Label(self.inner_frame, text="No hay frases extraídas todavía.")
        self.placeholder.pack(anchor="w", padx=2, pady=2)
        
        self.extracted_phrases = {}
    
    def display_phrases(self, phrase_groups):
        """Display extracted phrases organized by category."""
        self.extracted_phrases = phrase_groups
        
        # Clear existing widgets
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        
        if not phrase_groups or all(not phrases for phrases in phrase_groups.values()):
            placeholder = ttk.Label(self.inner_frame, text="No se pudieron extraer frases.")
            placeholder.pack(anchor="w", padx=2, pady=2)
            return
        
        # Function to sort phrases ignoring articles
        def sort_ignoring_articles(phrase):
            words = phrase.lower().split()
            if words and words[0] in ["el", "la", "los", "las"]:
                return " ".join(words[1:])
            return phrase.lower()
        
        max_columns = 3
        
        for category, phrases in phrase_groups.items():
            if phrases:
                # Sort using the auxiliary function
                sorted_phrases = sorted(phrases, key=sort_ignoring_articles)
                
                cat_label = ttk.Label(
                    self.inner_frame,
                    text=f"{category}:",
                    font=('TkDefaultFont', 10, 'bold')
                )
                cat_label.pack(anchor="w", padx=2, pady=(5, 0))
                
                btn_frame = ttk.Frame(self.inner_frame)
                btn_frame.pack(fill="x", padx=5)
                
                col = 0
                row = 0
                for phrase in sorted_phrases:
                    btn = tk.Button(
                        btn_frame, 
                        text=phrase, 
                        relief=tk.FLAT, 
                        fg="blue", 
                        cursor="hand2",
                        command=lambda p=phrase: self._on_phrase_clicked(p)
                    )
                    btn.grid(row=row, column=col, padx=2, pady=2, sticky="w")
                    col += 1
                    if col >= max_columns:
                        col = 0
                        row += 1
    
    def _on_phrase_clicked(self, phrase):
        """Handle phrase button click."""
        if self.on_phrase_click:
            self.on_phrase_click(phrase)
    
    def clear_phrases(self):
        """Clear all extracted phrases."""
        self.extracted_phrases = {}
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        
        self.placeholder = ttk.Label(self.inner_frame, text="No hay frases extraídas todavía.")
        self.placeholder.pack(anchor="w", padx=2, pady=2)