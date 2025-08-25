"""
Tutorial system for video and interactive tutorials
Provides structured learning content and progress tracking
"""

import tkinter as tk
from tkinter import ttk


class TutorialSystem:
    """Video and interactive tutorial system"""
    
    def __init__(self, parent: tk.Tk, theme_manager, on_tutorial_complete=None):
        self.parent = parent
        self.theme_manager = theme_manager
        self.on_tutorial_complete = on_tutorial_complete
        self.tutorial_window = None
    
    def show_tutorial(self, tutorial_id: str):
        """Show specific tutorial"""
        if self.tutorial_window:
            self.tutorial_window.lift()
            return
        
        self._create_tutorial_window(tutorial_id)
    
    def _create_tutorial_window(self, tutorial_id: str):
        """Create tutorial interface"""
        colors = self.theme_manager.get_colors()
        
        self.tutorial_window = tk.Toplevel(self.parent)
        self.tutorial_window.title(f"Tutorial: {tutorial_id}")
        self.tutorial_window.geometry("800x600")
        self.tutorial_window.configure(bg=colors['bg'])
        
        # Header
        header_label = tk.Label(
            self.tutorial_window,
            text="🎥 Video Tutorials",
            font=('TkDefaultFont', 16, 'bold'),
            bg=colors['bg'],
            fg=colors['info']
        )
        header_label.pack(pady=20)
        
        # Placeholder for tutorial content
        tk.Label(
            self.tutorial_window,
            text=f"Tutorial content for '{tutorial_id}' would be displayed here",
            bg=colors['bg'],
            fg=colors['fg']
        ).pack(pady=50)
    
    def hide(self):
        """Hide tutorial window"""
        if self.tutorial_window:
            self.tutorial_window.destroy()
            self.tutorial_window = None