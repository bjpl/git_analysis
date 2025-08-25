"""
FAQ System with expandable questions and answers
Quick access to frequently asked questions organized by category
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any


class FAQSystem:
    """FAQ system with searchable, categorized questions and answers"""
    
    def __init__(self, parent: tk.Tk, theme_manager, help_topics):
        self.parent = parent
        self.theme_manager = theme_manager
        self.help_topics = help_topics
        self.faq_window = None
        
        # FAQ data
        self.faqs = self._create_faq_data()
    
    def _create_faq_data(self):
        """Create FAQ data structure"""
        return {
            "Getting Started": [
                {
                    "question": "How do I get started with the app?",
                    "answer": "First, set up your API keys (Unsplash + OpenAI), then search for an image, generate a description, and click vocabulary words to build your learning list."
                },
                {
                    "question": "Do I need to pay for API keys?",
                    "answer": "Both services offer free tiers. Unsplash provides 50 requests/hour free, and OpenAI has pay-per-use pricing (very affordable for learning)."
                }
            ],
            "Technical Issues": [
                {
                    "question": "Why aren't my API keys working?",
                    "answer": "Double-check that keys are copied correctly with no extra spaces. For OpenAI, ensure billing is set up in your account."
                },
                {
                    "question": "The app is running slowly. What can I do?",
                    "answer": "Try restarting the app, check your internet connection, or add the app to your antivirus exclusions."
                }
            ],
            "Learning & Features": [
                {
                    "question": "How does the vocabulary extraction work?",
                    "answer": "The AI analyzes Spanish descriptions and automatically identifies useful vocabulary, organizing it by type (nouns, verbs, adjectives, phrases)."
                },
                {
                    "question": "Can I export my vocabulary to study apps?",
                    "answer": "Yes! Export to Anki (tab-delimited), CSV, plain text, or JSON formats. Perfect for spaced repetition learning."
                }
            ]
        }
    
    def show(self):
        """Show FAQ window"""
        if self.faq_window:
            self.faq_window.lift()
            return
        
        self._create_faq_window()
    
    def _create_faq_window(self):
        """Create FAQ interface"""
        colors = self.theme_manager.get_colors()
        
        self.faq_window = tk.Toplevel(self.parent)
        self.faq_window.title("Frequently Asked Questions")
        self.faq_window.geometry("700x600")
        self.faq_window.configure(bg=colors['bg'])
        
        # Header
        header_label = tk.Label(
            self.faq_window,
            text="❓ Frequently Asked Questions",
            font=('TkDefaultFont', 16, 'bold'),
            bg=colors['bg'],
            fg=colors['info']
        )
        header_label.pack(pady=20)
        
        # Create scrollable content with FAQ items
        # Implementation would create expandable FAQ items
        # For brevity, showing structure only
        
        tk.Label(
            self.faq_window,
            text="FAQ content would be implemented here with expandable sections",
            bg=colors['bg'],
            fg=colors['fg']
        ).pack(pady=50)
    
    def hide(self):
        """Hide FAQ window"""
        if self.faq_window:
            self.faq_window.destroy()
            self.faq_window = None