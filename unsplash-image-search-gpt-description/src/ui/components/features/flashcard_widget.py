"""Flashcard widget for spaced repetition learning."""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from PIL import Image, ImageTk
import threading
import time
from dataclasses import asdict

from ...features.learning import LearningSystem, LearningCard, ReviewResult, StudyMode, DifficultyLevel


class FlashcardWidget(ttk.Frame):
    """Interactive flashcard widget with spaced repetition."""
    
    def __init__(self, parent, data_dir: Path):
        super().__init__(parent)
        
        self.data_dir = data_dir
        
        # Initialize learning system
        self.learning_system = LearningSystem(data_dir)
        
        # State variables
        self.current_session_id = None
        self.current_cards = []
        self.current_card_index = 0
        self.current_card = None
        self.showing_answer = False
        self.session_stats = {
            'cards_studied': 0,
            'correct_answers': 0,
            'start_time': None
        }
        
        # Timer variables
        self.start_time = None
        self.timer_id = None
        
        # Setup UI
        self.setup_ui()
        self.load_study_data()
    
    def setup_ui(self):
        """Setup the flashcard UI."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Study mode selection
        mode_frame = ttk.LabelFrame(main_frame, text="Study Mode", padding=5)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.study_mode_var = tk.StringVar(value=StudyMode.FLASHCARDS.value)
        modes = [
            ("Flashcards", StudyMode.FLASHCARDS.value),
            ("Multiple Choice", StudyMode.MULTIPLE_CHOICE.value),
            ("Typing", StudyMode.TYPING.value),
            ("Mixed", StudyMode.MIXED.value)
        ]
        
        for i, (label, value) in enumerate(modes):
            ttk.Radiobutton(
                mode_frame, 
                text=label, 
                variable=self.study_mode_var, 
                value=value,
                command=self.on_study_mode_change
            ).grid(row=0, column=i, padx=5, sticky="w")
        
        # Study controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            controls_frame, 
            text="Start Session", 
            command=self.start_study_session
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            controls_frame, 
            text="End Session", 
            command=self.end_study_session,
            state=tk.DISABLED
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Session info
        self.session_info_label = ttk.Label(
            controls_frame, 
            text="No active session"
        )
        self.session_info_label.pack(side=tk.RIGHT)
        
        # Card display area
        card_frame = ttk.LabelFrame(main_frame, text="Flashcard", padding=10)
        card_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Card content
        self.card_content_frame = ttk.Frame(card_frame)
        self.card_content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Front/Back indicator
        self.card_side_label = ttk.Label(
            self.card_content_frame, 
            text="Front", 
            font=('TkDefaultFont', 10, 'bold')
        )
        self.card_side_label.pack(pady=(0, 10))
        
        # Card text
        self.card_text = tk.Text(
            self.card_content_frame,
            height=8,
            width=50,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=('TkDefaultFont', 12),
            relief=tk.FLAT,
            bg=self.cget('bg') or 'white'
        )
        self.card_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Card image (if available)
        self.card_image_label = ttk.Label(self.card_content_frame)
        # Initially hidden
        
        # Card navigation and review buttons
        nav_frame = ttk.Frame(self.card_content_frame)
        nav_frame.pack(fill=tk.X)
        
        # Show answer button (for flashcard mode)
        self.show_answer_btn = ttk.Button(
            nav_frame, 
            text="Show Answer", 
            command=self.show_answer,
            state=tk.DISABLED
        )
        self.show_answer_btn.pack(side=tk.LEFT)
        
        # Progress info
        self.progress_label = ttk.Label(
            nav_frame, 
            text="0/0"
        )
        self.progress_label.pack(side=tk.RIGHT)
        
        # Review buttons (initially hidden)
        self.review_frame = ttk.Frame(main_frame)
        # Will be packed when needed
        
        # Review difficulty buttons
        review_buttons = [
            ("Again", ReviewResult.AGAIN, "#ff4444"),
            ("Hard", ReviewResult.HARD, "#ff8800"),
            ("Good", ReviewResult.GOOD, "#44aa44"),
            ("Easy", ReviewResult.EASY, "#0088ff")
        ]
        
        for i, (text, result, color) in enumerate(review_buttons):
            btn = ttk.Button(
                self.review_frame,
                text=text,
                command=lambda r=result: self.review_card(r)
            )
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.review_frame.columnconfigure(i, weight=1)
        
        # Timer display
        self.timer_label = ttk.Label(
            main_frame, 
            text="00:00", 
            font=('TkDefaultFont', 10)
        )
        self.timer_label.pack(pady=(5, 0))
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(main_frame, text="Session Statistics", padding=5)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        # Statistics labels
        ttk.Label(stats_grid, text="Cards:").grid(row=0, column=0, sticky="w")
        self.cards_studied_label = ttk.Label(stats_grid, text="0")
        self.cards_studied_label.grid(row=0, column=1, sticky="w", padx=(5, 20))
        
        ttk.Label(stats_grid, text="Correct:").grid(row=0, column=2, sticky="w")
        self.correct_label = ttk.Label(stats_grid, text="0")
        self.correct_label.grid(row=0, column=3, sticky="w", padx=(5, 20))
        
        ttk.Label(stats_grid, text="Accuracy:").grid(row=0, column=4, sticky="w")
        self.accuracy_label = ttk.Label(stats_grid, text="0%")
        self.accuracy_label.grid(row=0, column=5, sticky="w", padx=(5, 0))
        
        # Configure grid weights
        for i in range(6):
            stats_grid.columnconfigure(i, weight=1)
    
    def load_study_data(self):
        """Load available study data."""
        try:
            # Load due cards count
            due_cards = self.learning_system.get_due_cards(limit=1)
            new_cards = self.learning_system.get_new_cards(limit=1)
            
            # Update UI with available cards info
            due_count = len(due_cards)
            new_count = len(new_cards)
            
            if due_count > 0 or new_count > 0:
                self.session_info_label.config(
                    text=f"Due: {due_count}, New: {new_count}"
                )
            else:
                self.session_info_label.config(text="No cards available")
                
        except Exception as e:
            print(f"Error loading study data: {e}")
    
    def on_study_mode_change(self):
        """Handle study mode change."""
        mode = StudyMode(self.study_mode_var.get())
        # Adjust UI based on study mode
        if mode == StudyMode.FLASHCARDS:
            self.show_answer_btn.config(text="Show Answer")
        elif mode == StudyMode.MULTIPLE_CHOICE:
            self.show_answer_btn.config(text="Show Choices")
        elif mode == StudyMode.TYPING:
            self.show_answer_btn.config(text="Check Answer")
    
    def start_study_session(self):
        """Start a new study session."""
        try:
            # Get study mode
            study_mode = StudyMode(self.study_mode_var.get())
            
            # Start session with learning system
            self.current_session_id = self.learning_system.start_study_session(
                study_mode=study_mode
            )
            
            # Generate practice cards
            self.current_cards = self.learning_system.generate_practice_session(
                target_count=20,
                include_new=True,
                include_due=True
            )
            
            if not self.current_cards:
                messagebox.showinfo(
                    "No Cards", 
                    "No cards available for study. Create some cards first!"
                )
                return
            
            # Initialize session
            self.current_card_index = 0
            self.showing_answer = False
            self.session_stats = {
                'cards_studied': 0,
                'correct_answers': 0,
                'start_time': datetime.now()
            }
            
            # Start timer
            self.start_timer()
            
            # Update UI
            self.update_session_controls(True)
            self.show_current_card()
            self.update_progress()
            self.update_statistics()
            
            messagebox.showinfo(
                "Session Started", 
                f"Starting study session with {len(self.current_cards)} cards"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start session: {str(e)}")
    
    def end_study_session(self):
        """End the current study session."""
        if not self.current_session_id:
            return
        
        try:
            # Stop timer
            self.stop_timer()
            
            # End session with learning system
            session = self.learning_system.end_study_session(self.current_session_id)
            
            # Show session summary
            if session:
                self.show_session_summary(session)
            
            # Reset state
            self.current_session_id = None
            self.current_cards = []
            self.current_card_index = 0
            self.current_card = None
            self.showing_answer = False
            
            # Update UI
            self.update_session_controls(False)
            self.clear_card_display()
            self.load_study_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to end session: {str(e)}")
    
    def show_current_card(self):
        """Display the current card."""
        if not self.current_cards or self.current_card_index >= len(self.current_cards):
            self.end_study_session()
            return
        
        self.current_card = self.current_cards[self.current_card_index]
        self.showing_answer = False
        
        # Start timing this card
        self.start_time = time.time()
        
        # Update card display
        self.card_side_label.config(text="Question")
        self.update_card_text(self.current_card.front)
        
        # Show image if available
        if self.current_card.image_url:
            self.load_card_image(self.current_card.image_url)
        else:
            self.card_image_label.pack_forget()
        
        # Update buttons
        self.show_answer_btn.config(state=tk.NORMAL)
        self.review_frame.pack_forget()
        
        # Update progress
        self.update_progress()
    
    def show_answer(self):
        """Show the answer for the current card."""
        if not self.current_card or self.showing_answer:
            return
        
        self.showing_answer = True
        
        # Update card display
        self.card_side_label.config(text="Answer")
        self.update_card_text(self.current_card.back)
        
        # Show review buttons
        self.show_answer_btn.config(state=tk.DISABLED)
        self.review_frame.pack(fill=tk.X, pady=(10, 0))
    
    def review_card(self, result: ReviewResult):
        """Review the current card with the given result."""
        if not self.current_card or not self.current_session_id:
            return
        
        try:
            # Calculate response time
            response_time_ms = int((time.time() - self.start_time) * 1000) if self.start_time else 0
            
            # Review card with learning system
            updated_card = self.learning_system.review_card(
                self.current_card.id,
                self.current_session_id,
                result,
                response_time_ms
            )
            
            # Update statistics
            self.session_stats['cards_studied'] += 1
            if result in [ReviewResult.GOOD, ReviewResult.EASY]:
                self.session_stats['correct_answers'] += 1
            
            self.update_statistics()
            
            # Move to next card
            self.current_card_index += 1
            self.show_current_card()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to review card: {str(e)}")
    
    def update_card_text(self, text: str):
        """Update the card text display."""
        self.card_text.config(state=tk.NORMAL)
        self.card_text.delete('1.0', tk.END)
        self.card_text.insert('1.0', text)
        self.card_text.config(state=tk.DISABLED)
    
    def load_card_image(self, image_url: str):
        """Load and display card image."""
        def load_image_thread():
            try:
                import requests
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                
                image = Image.open(BytesIO(response.content))
                # Resize to fit in card
                image.thumbnail((300, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                # Update UI in main thread
                self.after(0, lambda: self.display_card_image(photo))
                
            except Exception as e:
                print(f"Error loading card image: {e}")
        
        threading.Thread(target=load_image_thread, daemon=True).start()
    
    def display_card_image(self, photo):
        """Display the loaded card image."""
        self.card_image_label.config(image=photo)
        self.card_image_label.image = photo  # Keep reference
        self.card_image_label.pack(pady=(0, 10))
    
    def clear_card_display(self):
        """Clear the card display."""
        self.card_side_label.config(text="")
        self.update_card_text("No active session")
        self.card_image_label.pack_forget()
        self.progress_label.config(text="0/0")
    
    def update_progress(self):
        """Update progress display."""
        if self.current_cards:
            current = self.current_card_index + 1
            total = len(self.current_cards)
            self.progress_label.config(text=f"{current}/{total}")
        else:
            self.progress_label.config(text="0/0")
    
    def update_statistics(self):
        """Update session statistics display."""
        cards_studied = self.session_stats['cards_studied']
        correct = self.session_stats['correct_answers']
        accuracy = (correct / cards_studied * 100) if cards_studied > 0 else 0
        
        self.cards_studied_label.config(text=str(cards_studied))
        self.correct_label.config(text=str(correct))
        self.accuracy_label.config(text=f"{accuracy:.1f}%")
    
    def update_session_controls(self, session_active: bool):
        """Update session control buttons."""
        start_btn = None
        end_btn = None
        
        # Find buttons in controls frame
        for child in self.children.values():
            if isinstance(child, ttk.Frame):
                for grandchild in child.children.values():
                    if isinstance(grandchild, ttk.Frame):
                        for button in grandchild.children.values():
                            if isinstance(button, ttk.Button):
                                if "Start" in button.cget("text"):
                                    start_btn = button
                                elif "End" in button.cget("text"):
                                    end_btn = button
        
        if start_btn:
            start_btn.config(state=tk.DISABLED if session_active else tk.NORMAL)
        if end_btn:
            end_btn.config(state=tk.NORMAL if session_active else tk.DISABLED)
    
    def start_timer(self):
        """Start the session timer."""
        self.session_stats['start_time'] = datetime.now()
        self.update_timer()
    
    def stop_timer(self):
        """Stop the session timer."""
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
    
    def update_timer(self):
        """Update timer display."""
        if self.session_stats['start_time']:
            elapsed = datetime.now() - self.session_stats['start_time']
            minutes = int(elapsed.total_seconds() // 60)
            seconds = int(elapsed.total_seconds() % 60)
            self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
            
            # Schedule next update
            self.timer_id = self.after(1000, self.update_timer)
    
    def show_session_summary(self, session):
        """Show session completion summary."""
        summary_window = tk.Toplevel(self)
        summary_window.title("Session Complete")
        summary_window.geometry("400x300")
        summary_window.transient(self)
        summary_window.grab_set()
        
        # Center window
        summary_window.update_idletasks()
        x = (summary_window.winfo_screenwidth() // 2) - 200
        y = (summary_window.winfo_screenheight() // 2) - 150
        summary_window.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(summary_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            frame, 
            text="Study Session Complete!", 
            font=('TkDefaultFont', 14, 'bold')
        ).pack(pady=(0, 20))
        
        # Session statistics
        stats_frame = ttk.LabelFrame(frame, text="Session Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        stats = [
            ("Duration:", f"{session.duration_minutes:.1f} minutes"),
            ("Cards Studied:", str(session.cards_studied)),
            ("Correct Answers:", str(session.correct_answers)),
            ("Accuracy:", f"{session.performance_data.get('accuracy', 0):.1%}"),
            ("Cards/Minute:", f"{session.performance_data.get('cards_per_minute', 0):.1f}")
        ]
        
        for i, (label, value) in enumerate(stats):
            ttk.Label(stats_frame, text=label, font=('TkDefaultFont', 10, 'bold')).grid(
                row=i, column=0, sticky="w", pady=2
            )
            ttk.Label(stats_frame, text=value).grid(
                row=i, column=1, sticky="w", padx=(10, 0), pady=2
            )
        
        # Achievements (if any)
        # This would show any achievements earned during the session
        
        ttk.Button(
            frame, 
            text="Continue", 
            command=summary_window.destroy
        ).pack(pady=(20, 0))
    
    def create_card_from_vocabulary(self, spanish_word: str, english_translation: str, 
                                  context: str = "", image_url: str = None):
        """Create a new learning card from vocabulary."""
        try:
            card_id = self.learning_system.create_card(
                front=spanish_word,
                back=english_translation,
                category="vocabulary",
                difficulty=DifficultyLevel.MEDIUM,
                tags=["vocabulary", "spanish"],
                notes=context,
                image_url=image_url
            )
            
            # Reload study data
            self.load_study_data()
            
            return card_id
            
        except Exception as e:
            print(f"Error creating card: {e}")
            return None
    
    def get_learning_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get learning statistics for display."""
        try:
            return self.learning_system.get_study_statistics(days)
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def export_cards(self, format_type: str = 'json') -> str:
        """Export learning cards."""
        try:
            return self.learning_system.export_cards(format_type=format_type)
        except Exception as e:
            print(f"Error exporting cards: {e}")
            return ""