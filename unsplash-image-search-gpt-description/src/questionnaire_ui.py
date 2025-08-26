#!/usr/bin/env python3
"""
Tkinter-based Questionnaire UI
Simplified version extracted from PyQt6 image-questionnaire-gpt project

Features:
1. Question/Answer dialog system
2. Progress tracking with visual feedback  
3. Session management
4. Settings configuration
5. Results display
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from typing import Dict, List, Optional, Callable, Any
import threading
import time
from datetime import datetime

# Import our core functionality
from questionnaire_core import (
    SessionManager, QuestionnaireSettings, ProgressTracker,
    QuestionResponse, QuestionnaireSession, sanitize_filename
)


class SettingsDialog:
    """Settings configuration dialog"""
    
    def __init__(self, parent, current_settings: QuestionnaireSettings):
        self.parent = parent
        self.settings = current_settings
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Questionnaire Settings")
        self.dialog.geometry("500x400")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_dialog()
        
        self.create_widgets()
    
    def center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (500 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
    
    def create_widgets(self):
        """Create settings dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Session Directory
        ttk.Label(main_frame, text="Session Directory:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.session_dir_var = tk.StringVar(value=self.settings.get("session_directory", "sessions"))
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        dir_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(dir_frame, textvariable=self.session_dir_var).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).grid(row=0, column=1)
        row += 1
        
        # Auto Save
        ttk.Label(main_frame, text="Auto Save:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.auto_save_var = tk.BooleanVar(value=self.settings.get("auto_save", True))
        ttk.Checkbutton(main_frame, variable=self.auto_save_var).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Show Progress
        ttk.Label(main_frame, text="Show Progress:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.show_progress_var = tk.BooleanVar(value=self.settings.get("show_progress", True))
        ttk.Checkbutton(main_frame, variable=self.show_progress_var).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Processing Timeout
        ttk.Label(main_frame, text="Processing Timeout (ms):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.timeout_var = tk.StringVar(value=str(self.settings.get("processing_timeout_ms", 30000)))
        ttk.Entry(main_frame, textvariable=self.timeout_var).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Enable Timestamps
        ttk.Label(main_frame, text="Enable Timestamps:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.timestamps_var = tk.BooleanVar(value=self.settings.get("enable_timestamps", True))
        ttk.Checkbutton(main_frame, variable=self.timestamps_var).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Max Sessions to Keep
        ttk.Label(main_frame, text="Max Sessions to Keep:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.max_sessions_var = tk.StringVar(value=str(self.settings.get("max_sessions_to_keep", 100)))
        ttk.Entry(main_frame, textvariable=self.max_sessions_var).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_defaults).pack(side=tk.LEFT, padx=5)
    
    def browse_directory(self):
        """Browse for session directory"""
        directory = filedialog.askdirectory(
            title="Select Session Directory",
            initialdir=self.session_dir_var.get()
        )
        if directory:
            self.session_dir_var.set(directory)
    
    def ok_clicked(self):
        """Handle OK button click"""
        try:
            # Validate inputs
            timeout_ms = int(self.timeout_var.get())
            max_sessions = int(self.max_sessions_var.get())
            
            # Update settings
            new_settings = {
                "session_directory": self.session_dir_var.get(),
                "auto_save": self.auto_save_var.get(),
                "show_progress": self.show_progress_var.get(),
                "processing_timeout_ms": timeout_ms,
                "enable_timestamps": self.timestamps_var.get(),
                "max_sessions_to_keep": max_sessions
            }
            
            self.result = new_settings
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please check your numeric inputs: {e}")
    
    def cancel_clicked(self):
        """Handle Cancel button click"""
        self.result = None
        self.dialog.destroy()
    
    def reset_defaults(self):
        """Reset all settings to defaults"""
        defaults = QuestionnaireSettings().default_settings
        self.session_dir_var.set(defaults["session_directory"])
        self.auto_save_var.set(defaults["auto_save"])
        self.show_progress_var.set(defaults["show_progress"])
        self.timeout_var.set(str(defaults["processing_timeout_ms"]))
        self.timestamps_var.set(defaults["enable_timestamps"])
        self.max_sessions_var.set(str(defaults["max_sessions_to_keep"]))


class QuestionDialog:
    """Dialog for displaying a question and getting user response"""
    
    def __init__(self, parent, question_text: str, question_id: int = 0, 
                 default_answer: str = "", multiline: bool = True):
        self.parent = parent
        self.question_text = question_text
        self.question_id = question_id
        self.result = None
        self.start_time = time.time()
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Question {question_id + 1}")
        self.dialog.geometry("600x400")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_dialog()
        
        self.create_widgets(default_answer, multiline)
        
        # Focus on answer field
        if multiline:
            self.answer_text.focus_set()
        else:
            self.answer_entry.focus_set()
    
    def center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (600 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (400 // 2)
        self.dialog.geometry(f"600x400+{x}+{y}")
    
    def create_widgets(self, default_answer: str, multiline: bool):
        """Create question dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Question text
        question_frame = ttk.LabelFrame(main_frame, text="Question", padding="5")
        question_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        question_frame.columnconfigure(0, weight=1)
        
        question_display = scrolledtext.ScrolledText(
            question_frame, height=4, wrap=tk.WORD, state=tk.DISABLED
        )
        question_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Insert question text
        question_display.config(state=tk.NORMAL)
        question_display.insert(tk.END, self.question_text)
        question_display.config(state=tk.DISABLED)
        
        # Answer frame
        answer_frame = ttk.LabelFrame(main_frame, text="Your Answer", padding="5")
        answer_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        answer_frame.columnconfigure(0, weight=1)
        answer_frame.rowconfigure(0, weight=1)
        
        if multiline:
            self.answer_text = scrolledtext.ScrolledText(
                answer_frame, wrap=tk.WORD
            )
            self.answer_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            self.answer_text.insert(tk.END, default_answer)
            self.answer_entry = None
        else:
            self.answer_entry = ttk.Entry(answer_frame)
            self.answer_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
            self.answer_entry.insert(0, default_answer)
            self.answer_text = None
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(button_frame, text="Submit Answer", command=self.submit_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Skip", command=self.skip_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key for single-line answers
        if not multiline:
            self.answer_entry.bind('<Return>', lambda e: self.submit_clicked())
    
    def submit_clicked(self):
        """Handle submit button click"""
        if self.answer_text:
            answer = self.answer_text.get(1.0, tk.END).strip()
        else:
            answer = self.answer_entry.get().strip()
        
        processing_time = int((time.time() - self.start_time) * 1000)
        
        self.result = {
            'answer': answer,
            'processing_time_ms': processing_time,
            'skipped': False
        }
        self.dialog.destroy()
    
    def skip_clicked(self):
        """Handle skip button click"""
        processing_time = int((time.time() - self.start_time) * 1000)
        
        self.result = {
            'answer': '[SKIPPED]',
            'processing_time_ms': processing_time,
            'skipped': True
        }
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle cancel button click"""
        self.result = None
        self.dialog.destroy()


class QuestionnaireMainWindow:
    """Main questionnaire application window"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Questionnaire System")
        self.root.geometry("800x600")
        
        # Initialize core components
        self.settings = QuestionnaireSettings()
        self.session_manager = SessionManager(self.settings.get("session_directory"))
        self.progress_tracker = ProgressTracker()
        
        # State variables
        self.current_questions = []
        self.current_session_id = None
        self.is_running = False
        
        # Create UI
        self.create_widgets()
        self.setup_progress_tracking()
        
        # Update UI state
        self.update_ui_state()
    
    def create_widgets(self):
        """Create main window widgets"""
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Top section - Controls
        controls_frame = ttk.LabelFrame(main_container, text="Questionnaire Controls", padding="5")
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        controls_frame.columnconfigure(1, weight=1)
        
        # Settings button
        ttk.Button(controls_frame, text="Settings", command=self.open_settings).grid(row=0, column=0, padx=(0, 5))
        
        # Questions file selection
        ttk.Label(controls_frame, text="Questions:").grid(row=0, column=1, sticky=tk.W, padx=(10, 5))
        self.questions_file_var = tk.StringVar()
        ttk.Entry(controls_frame, textvariable=self.questions_file_var, state="readonly").grid(row=0, column=2, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(controls_frame, text="Load Questions", command=self.load_questions).grid(row=0, column=3, padx=(0, 5))
        
        # Start/Stop buttons
        self.start_button = ttk.Button(controls_frame, text="Start Questionnaire", command=self.start_questionnaire)
        self.start_button.grid(row=0, column=4, padx=(10, 5))
        
        self.stop_button = ttk.Button(controls_frame, text="Stop", command=self.stop_questionnaire, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_container, text="Progress", padding="5")
        progress_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Progress labels
        self.progress_label = ttk.Label(progress_frame, text="Ready")
        self.progress_label.grid(row=1, column=0)
        
        # Results section
        results_frame = ttk.LabelFrame(main_container, text="Session Results", padding="5")
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Results display
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, wrap=tk.WORD)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        
        # Results buttons
        results_buttons = ttk.Frame(results_frame)
        results_buttons.grid(row=1, column=0, sticky=tk.E)
        
        ttk.Button(results_buttons, text="Clear Results", command=self.clear_results).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(results_buttons, text="Export Results", command=self.export_results).pack(side=tk.LEFT)
    
    def setup_progress_tracking(self):
        """Setup progress tracking callbacks"""
        def update_progress(current, total):
            if total > 0:
                percentage = (current / total) * 100
                self.progress_var.set(percentage)
                
                # Update label
                self.progress_label.config(text=f"Question {current} of {total} ({percentage:.1f}%)")
                
                # Estimate time remaining
                remaining_time = self.progress_tracker.get_estimated_time_remaining()
                if remaining_time:
                    mins, secs = divmod(int(remaining_time), 60)
                    time_str = f" - Est. {mins}m {secs}s remaining" if mins > 0 else f" - Est. {secs}s remaining"
                    current_text = self.progress_label.cget("text")
                    self.progress_label.config(text=current_text + time_str)
            else:
                self.progress_var.set(0)
                self.progress_label.config(text="Ready")
        
        self.progress_tracker.add_progress_callback(update_progress)
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.root, self.settings)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.settings.update(dialog.result)
            # Reinitialize session manager with new directory
            self.session_manager = SessionManager(self.settings.get("session_directory"))
            messagebox.showinfo("Settings", "Settings updated successfully!")
    
    def load_questions(self):
        """Load questions from a text file"""
        file_path = filedialog.askopenfilename(
            title="Select Questions File",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                # Split by double newlines or numbered questions
                questions = []
                if '\n\n' in content:
                    questions = [q.strip() for q in content.split('\n\n') if q.strip()]
                else:
                    # Try to split by numbered questions (1., 2., etc.)
                    import re
                    parts = re.split(r'\n\s*\d+\.\s*', content)
                    questions = [q.strip() for q in parts if q.strip()]
                
                if not questions:
                    # Fallback: each line is a question
                    questions = [line.strip() for line in content.split('\n') if line.strip()]
                
                self.current_questions = questions
                self.questions_file_var.set(os.path.basename(file_path))
                
                self.results_text.insert(tk.END, f"Loaded {len(questions)} questions from {file_path}\n\n")
                self.results_text.see(tk.END)
                
                self.update_ui_state()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load questions: {e}")
    
    def start_questionnaire(self):
        """Start the questionnaire session"""
        if not self.current_questions:
            messagebox.showwarning("No Questions", "Please load questions first.")
            return
        
        self.is_running = True
        self.update_ui_state()
        
        # Start session
        self.current_session_id = self.session_manager.start_session(len(self.current_questions))
        self.progress_tracker.set_total_questions(len(self.current_questions))
        
        self.results_text.insert(tk.END, f"Started questionnaire session: {self.current_session_id}\n")
        self.results_text.insert(tk.END, f"Total questions: {len(self.current_questions)}\n\n")
        self.results_text.see(tk.END)
        
        # Start asking questions in a separate thread
        threading.Thread(target=self.run_questionnaire, daemon=True).start()
    
    def stop_questionnaire(self):
        """Stop the questionnaire session"""
        self.is_running = False
        
        if self.current_session_id:
            csv_path = self.session_manager.end_session()
            if csv_path:
                self.results_text.insert(tk.END, f"Session stopped and saved to: {csv_path}\n\n")
            else:
                self.results_text.insert(tk.END, "Session stopped.\n\n")
            self.results_text.see(tk.END)
        
        self.progress_tracker.reset()
        self.update_ui_state()
    
    def run_questionnaire(self):
        """Run the questionnaire in background thread"""
        for i, question in enumerate(self.current_questions):
            if not self.is_running:
                break
            
            # Show question dialog on main thread
            result = self.show_question_dialog(question, i)
            
            if result is None:  # Cancelled
                break
            
            # Add response to session
            self.session_manager.add_response(
                question_id=i,
                question_text=question,
                answer=result['answer'],
                processing_time_ms=result['processing_time_ms'],
                additional_data={'skipped': result['skipped']}
            )
            
            # Update results display
            self.root.after(0, self.update_results_display, i + 1, question, result)
            
            # Update progress
            self.progress_tracker.advance_question()
        
        # Complete the session
        if self.is_running:
            self.root.after(0, self.complete_questionnaire)
    
    def show_question_dialog(self, question: str, question_id: int):
        """Show question dialog and wait for result"""
        result = {'dialog_result': None}
        
        def show_dialog():
            dialog = QuestionDialog(self.root, question, question_id)
            self.root.wait_window(dialog.dialog)
            result['dialog_result'] = dialog.result
        
        # Run dialog on main thread
        self.root.after(0, show_dialog)
        
        # Wait for dialog to complete
        while result['dialog_result'] is None and self.is_running:
            time.sleep(0.1)
        
        return result['dialog_result']
    
    def update_results_display(self, question_num: int, question: str, result: dict):
        """Update results display with new response"""
        status = "[SKIPPED]" if result['skipped'] else "[ANSWERED]"
        time_str = f"({result['processing_time_ms']/1000:.1f}s)"
        
        self.results_text.insert(tk.END, f"Q{question_num}: {status} {time_str}\n")
        self.results_text.insert(tk.END, f"Question: {question[:100]}{'...' if len(question) > 100 else ''}\n")
        if not result['skipped']:
            answer_preview = result['answer'][:200] + ('...' if len(result['answer']) > 200 else '')
            self.results_text.insert(tk.END, f"Answer: {answer_preview}\n")
        self.results_text.insert(tk.END, "\n")
        self.results_text.see(tk.END)
    
    def complete_questionnaire(self):
        """Complete the questionnaire session"""
        self.is_running = False
        
        if self.current_session_id:
            csv_path = self.session_manager.end_session()
            if csv_path:
                self.results_text.insert(tk.END, f"Questionnaire completed! Results saved to:\n{csv_path}\n\n")
            else:
                self.results_text.insert(tk.END, "Questionnaire completed!\n\n")
            self.results_text.see(tk.END)
        
        self.update_ui_state()
        messagebox.showinfo("Complete", "Questionnaire session completed successfully!")
    
    def clear_results(self):
        """Clear the results display"""
        self.results_text.delete(1.0, tk.END)
    
    def export_results(self):
        """Export current session results"""
        if not self.current_session_id and not self.session_manager.current_session:
            messagebox.showinfo("No Session", "No active session to export.")
            return
        
        try:
            # Force save current session
            if self.session_manager.current_session:
                csv_path = self.session_manager.save_session_to_csv()
                messagebox.showinfo("Export Complete", f"Results exported to:\n{csv_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results: {e}")
    
    def update_ui_state(self):
        """Update UI state based on current status"""
        has_questions = bool(self.current_questions)
        
        if self.is_running:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.start_button.config(state=tk.NORMAL if has_questions else tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = QuestionnaireMainWindow(root)
    
    # Handle window close
    def on_closing():
        if app.is_running:
            if messagebox.askokcancel("Quit", "Questionnaire is running. Do you want to stop and quit?"):
                app.stop_questionnaire()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")


if __name__ == "__main__":
    main()