"""
Vocabulary Quiz Widget - A simple Tkinter quiz component for Spanish vocabulary.

Features:
- Shows Spanish phrases from extracted vocabulary
- Presents 4 multiple choice English translations  
- Provides instant feedback (correct/incorrect)
- Tracks score throughout session
- Integrates with main app's vocabulary list
- Theme-aware styling
"""

import tkinter as tk
from tkinter import ttk
import random
from typing import List, Dict, Callable, Optional, Tuple
from pathlib import Path
import csv


class VocabularyQuizWidget(ttk.LabelFrame):
    """
    A lightweight vocabulary quiz widget that tests Spanish-to-English translation.
    Integrates with the main application's vocabulary system and theme manager.
    """
    
    def __init__(self, parent, vocabulary_manager=None, theme_manager=None, **kwargs):
        """
        Initialize the vocabulary quiz widget.
        
        Args:
            parent: Parent widget
            vocabulary_manager: VocabularyManager instance for accessing vocabulary
            theme_manager: ThemeManager instance for styling
            **kwargs: Additional arguments passed to LabelFrame
        """
        super().__init__(parent, text="📚 Vocabulary Quiz", padding="10", **kwargs)
        
        self.vocabulary_manager = vocabulary_manager
        self.theme_manager = theme_manager
        
        # Quiz state
        self.current_question = None
        self.correct_answer = None
        self.quiz_items = []
        self.current_score = 0
        self.questions_answered = 0
        self.last_answer_correct = None
        
        # UI components
        self.question_label = None
        self.answer_buttons = []
        self.feedback_label = None
        self.score_label = None
        self.next_button = None
        self.start_button = None
        
        self._create_ui()
        self._apply_theme()
    
    def _create_ui(self):
        """Create the quiz user interface."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Score display
        score_frame = ttk.Frame(main_frame)
        score_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.score_label = ttk.Label(
            score_frame,
            text="Score: 0/0 (0%)",
            font=("TkDefaultFont", 10, "bold")
        )
        self.score_label.pack(side=tk.RIGHT)
        
        # Question display
        question_frame = ttk.LabelFrame(main_frame, text="Question", padding="15")
        question_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.question_label = tk.Label(
            question_frame,
            text="Click 'Start Quiz' to begin",
            font=("TkDefaultFont", 14, "bold"),
            wraplength=350,
            justify=tk.CENTER,
            bg="white",
            fg="black",
            pady=10
        )
        self.question_label.pack(fill=tk.X)
        
        # Answer buttons frame
        answers_frame = ttk.LabelFrame(main_frame, text="Choose the English translation:", padding="10")
        answers_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create 4 answer buttons in a 2x2 grid
        buttons_grid = ttk.Frame(answers_frame)
        buttons_grid.pack(fill=tk.X)
        
        for i in range(4):
            btn = tk.Button(
                buttons_grid,
                text=f"Answer {i+1}",
                font=("TkDefaultFont", 10),
                width=20,
                height=2,
                command=lambda idx=i: self._on_answer_selected(idx),
                state=tk.DISABLED,
                relief=tk.RAISED,
                bd=2
            )
            row = i // 2
            col = i % 2
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            self.answer_buttons.append(btn)
        
        # Configure grid weights for even spacing
        buttons_grid.columnconfigure(0, weight=1)
        buttons_grid.columnconfigure(1, weight=1)
        
        # Feedback display
        feedback_frame = ttk.Frame(main_frame)
        feedback_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.feedback_label = tk.Label(
            feedback_frame,
            text="",
            font=("TkDefaultFont", 10, "bold"),
            wraplength=350,
            justify=tk.CENTER,
            pady=5
        )
        self.feedback_label.pack(fill=tk.X)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X)
        
        self.start_button = ttk.Button(
            control_frame,
            text="🎯 Start Quiz",
            command=self._start_quiz
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.next_button = ttk.Button(
            control_frame,
            text="➡️ Next Question",
            command=self._next_question,
            state=tk.DISABLED
        )
        self.next_button.pack(side=tk.LEFT, padx=(0, 10))
        
        restart_button = ttk.Button(
            control_frame,
            text="🔄 Restart",
            command=self._restart_quiz
        )
        restart_button.pack(side=tk.LEFT)
    
    def _apply_theme(self):
        """Apply current theme colors to the widget."""
        if not self.theme_manager:
            return
        
        try:
            colors = self.theme_manager.get_colors()
            
            # Configure question label
            if self.question_label:
                self.question_label.configure(
                    bg=colors.get('text_bg', 'white'),
                    fg=colors.get('text_fg', 'black')
                )
            
            # Configure feedback label
            if self.feedback_label:
                self.feedback_label.configure(
                    bg=colors.get('frame_bg', '#f0f0f0'),
                    fg=colors.get('fg', 'black')
                )
            
            # Configure answer buttons
            for btn in self.answer_buttons:
                btn.configure(
                    bg=colors.get('button_bg', '#e1e1e1'),
                    fg=colors.get('button_fg', 'black'),
                    activebackground=colors.get('button_active_bg', '#d0d0d0'),
                    highlightbackground=colors.get('border', '#cccccc')
                )
        
        except Exception as e:
            print(f"Error applying theme to vocabulary quiz: {e}")
    
    def _load_vocabulary_items(self) -> List[Tuple[str, str]]:
        """Load vocabulary items from the vocabulary manager."""
        vocab_items = []
        
        if not self.vocabulary_manager:
            # Return some sample data for demonstration
            return [
                ("la casa", "the house"),
                ("el perro", "the dog"),
                ("la comida", "the food"),
                ("el agua", "the water"),
                ("la escuela", "the school")
            ]
        
        try:
            entries = self.vocabulary_manager.get_all_entries()
            for entry in entries:
                if entry.spanish and entry.english:
                    vocab_items.append((entry.spanish.strip(), entry.english.strip()))
        
        except Exception as e:
            print(f"Error loading vocabulary items: {e}")
        
        return vocab_items
    
    def _generate_question(self) -> Optional[Dict]:
        """Generate a new quiz question with multiple choice answers."""
        if len(self.quiz_items) < 4:
            return None
        
        # Select a random correct answer
        correct_item = random.choice(self.quiz_items)
        spanish_word, correct_english = correct_item
        
        # Generate 3 incorrect options from other vocabulary items
        other_items = [item for item in self.quiz_items if item != correct_item]
        incorrect_options = random.sample(other_items, min(3, len(other_items)))
        
        # If we don't have enough vocabulary items, add some generic wrong answers
        while len(incorrect_options) < 3:
            generic_answers = [
                "the car", "the book", "the tree", "the computer", "the phone",
                "the window", "the door", "the chair", "the table", "the person",
                "to eat", "to drink", "to sleep", "to walk", "to read",
                "big", "small", "good", "bad", "beautiful"
            ]
            wrong_answer = random.choice(generic_answers)
            if wrong_answer != correct_english and wrong_answer not in [item[1] for item in incorrect_options]:
                incorrect_options.append(("", wrong_answer))
                break
        
        # Create answer options list
        all_options = [correct_english] + [item[1] for item in incorrect_options[:3]]
        random.shuffle(all_options)
        
        return {
            'spanish': spanish_word,
            'correct_answer': correct_english,
            'options': all_options,
            'correct_index': all_options.index(correct_english)
        }
    
    def _start_quiz(self):
        """Start or restart the quiz."""
        self.quiz_items = self._load_vocabulary_items()
        
        if len(self.quiz_items) < 4:
            self._show_feedback("❌ Need at least 4 vocabulary items to start quiz!", "error")
            return
        
        self.current_score = 0
        self.questions_answered = 0
        self._update_score_display()
        
        self.start_button.configure(state=tk.DISABLED)
        self._enable_answer_buttons()
        
        self._next_question()
    
    def _next_question(self):
        """Load the next quiz question."""
        question_data = self._generate_question()
        
        if not question_data:
            self._show_feedback("❌ Unable to generate question", "error")
            return
        
        self.current_question = question_data
        self.correct_answer = question_data['correct_index']
        
        # Update UI
        self.question_label.configure(text=f"What does '{question_data['spanish']}' mean?")
        
        for i, option in enumerate(question_data['options']):
            self.answer_buttons[i].configure(
                text=option,
                state=tk.NORMAL,
                relief=tk.RAISED
            )
        
        self.feedback_label.configure(text="")
        self.next_button.configure(state=tk.DISABLED)
        self._apply_theme()  # Reapply theme to reset button colors
    
    def _on_answer_selected(self, button_index: int):
        """Handle when user selects an answer."""
        self.questions_answered += 1
        is_correct = button_index == self.correct_answer
        
        if is_correct:
            self.current_score += 1
            self.last_answer_correct = True
            feedback_text = "✅ Correct! Well done!"
            feedback_color = "success"
            
            # Highlight correct button in green
            self.answer_buttons[button_index].configure(
                bg="lightgreen",
                relief=tk.SUNKEN
            )
        else:
            self.last_answer_correct = False
            feedback_text = f"❌ Incorrect. The correct answer is: {self.current_question['correct_answer']}"
            feedback_color = "error"
            
            # Highlight incorrect button in red, correct in green
            self.answer_buttons[button_index].configure(
                bg="lightcoral",
                relief=tk.SUNKEN
            )
            self.answer_buttons[self.correct_answer].configure(
                bg="lightgreen",
                relief=tk.SUNKEN
            )
        
        # Disable all answer buttons
        self._disable_answer_buttons()
        
        # Show feedback and update score
        self._show_feedback(feedback_text, feedback_color)
        self._update_score_display()
        
        # Enable next button
        self.next_button.configure(state=tk.NORMAL)
    
    def _show_feedback(self, message: str, msg_type: str = "info"):
        """Display feedback message with appropriate styling."""
        if not self.theme_manager:
            color = "black"
        else:
            colors = self.theme_manager.get_colors()
            color_map = {
                "success": colors.get('success', 'green'),
                "error": colors.get('error', 'red'),
                "warning": colors.get('warning', 'orange'),
                "info": colors.get('info', 'blue')
            }
            color = color_map.get(msg_type, colors.get('fg', 'black'))
        
        self.feedback_label.configure(text=message, fg=color)
    
    def _update_score_display(self):
        """Update the score display."""
        if self.questions_answered > 0:
            percentage = int((self.current_score / self.questions_answered) * 100)
            score_text = f"Score: {self.current_score}/{self.questions_answered} ({percentage}%)"
        else:
            score_text = "Score: 0/0 (0%)"
        
        self.score_label.configure(text=score_text)
    
    def _enable_answer_buttons(self):
        """Enable all answer buttons."""
        for btn in self.answer_buttons:
            btn.configure(state=tk.NORMAL)
    
    def _disable_answer_buttons(self):
        """Disable all answer buttons."""
        for btn in self.answer_buttons:
            btn.configure(state=tk.DISABLED)
    
    def _restart_quiz(self):
        """Restart the quiz from the beginning."""
        self.current_score = 0
        self.questions_answered = 0
        self.current_question = None
        self.correct_answer = None
        
        self.question_label.configure(text="Click 'Start Quiz' to begin")
        self.feedback_label.configure(text="")
        
        for btn in self.answer_buttons:
            btn.configure(
                text=f"Answer {self.answer_buttons.index(btn) + 1}",
                state=tk.DISABLED,
                relief=tk.RAISED
            )
        
        self.start_button.configure(state=tk.NORMAL)
        self.next_button.configure(state=tk.DISABLED)
        
        self._update_score_display()
        self._apply_theme()
    
    def get_statistics(self) -> Dict[str, int]:
        """Get current quiz statistics."""
        return {
            'questions_answered': self.questions_answered,
            'correct_answers': self.current_score,
            'incorrect_answers': self.questions_answered - self.current_score,
            'accuracy_percentage': int((self.current_score / max(1, self.questions_answered)) * 100)
        }
    
    def set_vocabulary_manager(self, vocabulary_manager):
        """Set or update the vocabulary manager."""
        self.vocabulary_manager = vocabulary_manager
        # If quiz is not active, reset it
        if self.start_button['state'] == 'normal':
            self._restart_quiz()
    
    def set_theme_manager(self, theme_manager):
        """Set or update the theme manager and apply theme."""
        self.theme_manager = theme_manager
        self._apply_theme()


# Example usage and integration helper
class VocabularyQuizIntegration:
    """Helper class for integrating the quiz widget with the main application."""
    
    @staticmethod
    def create_quiz_window(parent, vocabulary_manager=None, theme_manager=None):
        """Create a standalone quiz window."""
        quiz_window = tk.Toplevel(parent)
        quiz_window.title("Vocabulary Quiz")
        quiz_window.geometry("500x600")
        quiz_window.resizable(True, True)
        
        # Apply theme to window if theme manager available
        if theme_manager:
            colors = theme_manager.get_colors()
            quiz_window.configure(bg=colors.get('bg', 'white'))
        
        # Create main frame
        main_frame = ttk.Frame(quiz_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add instructions
        instructions = ttk.Label(
            main_frame,
            text="Test your Spanish vocabulary knowledge!\n"
                 "Read the Spanish phrase and choose the correct English translation.",
            font=("TkDefaultFont", 10),
            justify=tk.CENTER
        )
        instructions.pack(pady=(0, 10))
        
        # Create quiz widget
        quiz_widget = VocabularyQuizWidget(
            main_frame,
            vocabulary_manager=vocabulary_manager,
            theme_manager=theme_manager
        )
        quiz_widget.pack(fill=tk.BOTH, expand=True)
        
        # Add close button
        close_frame = ttk.Frame(main_frame)
        close_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            close_frame,
            text="Close Quiz",
            command=quiz_window.destroy
        ).pack(side=tk.RIGHT)
        
        return quiz_window, quiz_widget
    
    @staticmethod
    def add_to_main_app(main_app_window, vocabulary_manager=None, theme_manager=None):
        """Add quiz functionality to the main application."""
        def open_quiz():
            VocabularyQuizIntegration.create_quiz_window(
                main_app_window, vocabulary_manager, theme_manager
            )
        
        # This would typically be called from the main app to add a quiz button
        return open_quiz


if __name__ == "__main__":
    # Demo/test the widget
    root = tk.Tk()
    root.title("Vocabulary Quiz Demo")
    root.geometry("600x700")
    
    # Create demo quiz
    quiz = VocabularyQuizWidget(root)
    quiz.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    root.mainloop()