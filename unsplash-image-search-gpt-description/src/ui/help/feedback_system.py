"""
Feedback and support system for collecting user input
Provides in-app feedback forms, bug reports, feature requests, and user satisfaction surveys
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, Dict, Any
import json
from datetime import datetime
from pathlib import Path
import webbrowser


class FeedbackSystem:
    """
    Comprehensive feedback system for collecting user input and support requests
    """
    
    def __init__(self, parent: tk.Tk, theme_manager, config_manager,
                 on_feedback_submit: Callable[[str], None] = None):
        self.parent = parent
        self.theme_manager = theme_manager
        self.config_manager = config_manager
        self.on_feedback_submit = on_feedback_submit
        
        self.feedback_window = None
        self.feedback_type = tk.StringVar(value="general")
        self.rating = tk.IntVar(value=5)
        
        # Feedback storage
        self.feedback_file = Path(config_manager.get_paths()['data_dir']) / "feedback.json"
    
    def show(self, feedback_type: str = "general"):
        """Show the feedback system"""
        if self.feedback_window:
            self.feedback_window.lift()
            return
        
        self.feedback_type.set(feedback_type)
        self._create_feedback_window()
    
    def show_bug_report(self):
        """Show bug report form"""
        self.show("bug")
    
    def show_feature_request(self):
        """Show feature request form"""
        self.show("feature")
    
    def show_satisfaction_survey(self):
        """Show satisfaction survey"""
        self.show("survey")
    
    def _create_feedback_window(self):
        """Create the main feedback window"""
        colors = self.theme_manager.get_colors()
        
        # Create window
        self.feedback_window = tk.Toplevel(self.parent)
        self.feedback_window.title("Feedback & Support")
        self.feedback_window.geometry("600x700")
        self.feedback_window.configure(bg=colors['bg'])
        self.feedback_window.resizable(True, True)
        self.feedback_window.transient(self.parent)
        self.feedback_window.grab_set()
        
        # Center window
        self.feedback_window.update_idletasks()
        x = (self.feedback_window.winfo_screenwidth() // 2) - 300
        y = (self.feedback_window.winfo_screenheight() // 2) - 350
        self.feedback_window.geometry(f"+{x}+{y}")
        
        # Create scrollable content
        self._create_scrollable_content()
        
        # Create form based on type
        self._create_feedback_form()
    
    def _create_scrollable_content(self):
        """Create scrollable content area"""
        colors = self.theme_manager.get_colors()
        
        # Main canvas for scrolling
        self.main_canvas = tk.Canvas(
            self.feedback_window,
            bg=colors['bg'],
            highlightthickness=0
        )
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            self.feedback_window,
            orient="vertical",
            command=self.main_canvas.yview
        )
        
        # Scrollable frame
        self.scrollable_frame = tk.Frame(self.main_canvas, bg=colors['bg'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack components
        self.main_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        self._bind_mousewheel()
    
    def _create_feedback_form(self):
        """Create the appropriate feedback form"""
        form_type = self.feedback_type.get()
        
        if form_type == "bug":
            self._create_bug_report_form()
        elif form_type == "feature":
            self._create_feature_request_form()
        elif form_type == "survey":
            self._create_satisfaction_survey()
        else:
            self._create_general_feedback_form()
    
    def _create_general_feedback_form(self):
        """Create general feedback form"""
        colors = self.theme_manager.get_colors()
        
        # Header
        self._create_header("💬 General Feedback", "Share your thoughts about the app")
        
        # Feedback type selection
        type_frame = self._create_section("Feedback Type")
        
        feedback_types = [
            ("general", "General feedback or comments"),
            ("bug", "Report a bug or problem"),
            ("feature", "Request a new feature"),
            ("survey", "Rate your experience")
        ]
        
        for value, text in feedback_types:
            radio = tk.Radiobutton(
                type_frame,
                text=text,
                variable=self.feedback_type,
                value=value,
                font=('TkDefaultFont', 10),
                bg=colors['frame_bg'],
                fg=colors['fg'],
                selectcolor=colors['entry_bg'],
                command=self._on_feedback_type_change
            )
            radio.pack(anchor=tk.W, pady=2)
        
        # Overall rating
        rating_frame = self._create_section("Overall Rating")
        
        tk.Label(
            rating_frame,
            text="How would you rate your experience with the app?",
            font=('TkDefaultFont', 10),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Star rating
        stars_frame = tk.Frame(rating_frame, bg=colors['frame_bg'])
        stars_frame.pack(anchor=tk.W)
        
        self.star_buttons = []
        for i in range(1, 6):
            star_btn = tk.Button(
                stars_frame,
                text="⭐",
                font=('TkDefaultFont', 16),
                bg=colors['frame_bg'],
                fg=colors['disabled_fg'],
                relief=tk.FLAT,
                command=lambda rating=i: self._set_rating(rating)
            )
            star_btn.pack(side=tk.LEFT, padx=2)
            self.star_buttons.append(star_btn)
        
        # Update initial rating display
        self._update_star_display()
        
        # Comments section
        self._create_comments_section()
        
        # Contact info
        self._create_contact_section()
        
        # Action buttons
        self._create_action_buttons()
    
    def _create_bug_report_form(self):
        """Create bug report form"""
        colors = self.theme_manager.get_colors()
        
        # Header
        self._create_header("🐛 Bug Report", "Help us fix issues by providing detailed information")
        
        # Bug description
        desc_frame = self._create_section("Describe the Problem")
        
        tk.Label(
            desc_frame,
            text="What went wrong? Please be as specific as possible:",
            font=('TkDefaultFont', 10),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(anchor=tk.W)
        
        self.bug_description = tk.Text(
            desc_frame,
            height=6,
            font=('TkDefaultFont', 10),
            bg=colors['text_bg'],
            fg=colors['text_fg'],
            wrap=tk.WORD
        )
        self.bug_description.pack(fill=tk.X, pady=(5, 0))
        
        # Steps to reproduce
        steps_frame = self._create_section("Steps to Reproduce")
        
        tk.Label(
            steps_frame,
            text="How can we reproduce this problem? (Step by step):",
            font=('TkDefaultFont', 10),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(anchor=tk.W)
        
        self.bug_steps = tk.Text(
            steps_frame,
            height=4,
            font=('TkDefaultFont', 10),
            bg=colors['text_bg'],
            fg=colors['text_fg'],
            wrap=tk.WORD
        )
        self.bug_steps.pack(fill=tk.X, pady=(5, 0))
        
        # Expected vs actual behavior
        behavior_frame = self._create_section("Expected vs Actual Behavior")
        
        tk.Label(
            behavior_frame,
            text="What did you expect to happen?",
            font=('TkDefaultFont', 10),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(anchor=tk.W)
        
        self.expected_behavior = tk.Text(
            behavior_frame,
            height=3,
            font=('TkDefaultFont', 10),
            bg=colors['text_bg'],
            fg=colors['text_fg'],
            wrap=tk.WORD
        )
        self.expected_behavior.pack(fill=tk.X, pady=(5, 10))
        
        tk.Label(
            behavior_frame,
            text="What actually happened?",
            font=('TkDefaultFont', 10),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(anchor=tk.W)
        
        self.actual_behavior = tk.Text(
            behavior_frame,
            height=3,
            font=('TkDefaultFont', 10),
            bg=colors['text_bg'],
            fg=colors['text_fg'],
            wrap=tk.WORD
        )
        self.actual_behavior.pack(fill=tk.X, pady=(5, 0))
        
        # System information
        self._create_system_info_section()
        
        # Severity
        severity_frame = self._create_section("Severity")
        
        self.severity = tk.StringVar(value="medium")
        severities = [
            ("low", "Low - Minor inconvenience"),
            ("medium", "Medium - Affects functionality"),
            ("high", "High - Prevents normal use"),
            ("critical", "Critical - App crashes or data loss")
        ]
        
        for value, text in severities:
            radio = tk.Radiobutton(
                severity_frame,
                text=text,
                variable=self.severity,
                value=value,
                font=('TkDefaultFont', 10),
                bg=colors['frame_bg'],
                fg=colors['fg'],
                selectcolor=colors['entry_bg']
            )
            radio.pack(anchor=tk.W, pady=2)
        
        # Contact info
        self._create_contact_section()
        
        # Action buttons
        self._create_action_buttons("Submit Bug Report")
    
    def _create_feature_request_form(self):
        """Create feature request form"""
        colors = self.theme_manager.get_colors()
        
        # Header
        self._create_header("💡 Feature Request", "Suggest improvements and new features")
        
        # Feature description
        desc_frame = self._create_section("Feature Description")
        
        tk.Label(
            desc_frame,
            text="What feature would you like to see added?",
            font=('TkDefaultFont', 10),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(anchor=tk.W)
        
        self.feature_description = tk.Text(
            desc_frame,
            height=5,
            font=('TkDefaultFont', 10),
            bg=colors['text_bg'],
            fg=colors['text_fg'],
            wrap=tk.WORD
        )
        self.feature_description.pack(fill=tk.X, pady=(5, 0))
        
        # Use case
        usecase_frame = self._create_section("Use Case")
        
        tk.Label(
            usecase_frame,
            text="How would this feature help you learn Spanish better?",
            font=('TkDefaultFont', 10),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(anchor=tk.W)
        
        self.feature_usecase = tk.Text(
            usecase_frame,
            height=4,
            font=('TkDefaultFont', 10),
            bg=colors['text_bg'],
            fg=colors['text_fg'],
            wrap=tk.WORD
        )
        self.feature_usecase.pack(fill=tk.X, pady=(5, 0))
        
        # Priority
        priority_frame = self._create_section("Priority")
        
        self.priority = tk.StringVar(value="medium")
        priorities = [
            ("low", "Nice to have"),
            ("medium", "Would be helpful"),
            ("high", "Really important"),
            ("critical", "Essential for my learning")
        ]
        
        for value, text in priorities:
            radio = tk.Radiobutton(
                priority_frame,
                text=text,
                variable=self.priority,
                value=value,
                font=('TkDefaultFont', 10),
                bg=colors['frame_bg'],
                fg=colors['fg'],
                selectcolor=colors['entry_bg']
            )
            radio.pack(anchor=tk.W, pady=2)
        
        # Similar features
        similar_frame = self._create_section("Similar Features")
        
        tk.Label(
            similar_frame,
            text="Have you seen this feature in other apps? (Optional)",
            font=('TkDefaultFont', 10),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(anchor=tk.W)
        
        self.similar_features = tk.Text(
            similar_frame,
            height=3,
            font=('TkDefaultFont', 10),
            bg=colors['text_bg'],
            fg=colors['text_fg'],
            wrap=tk.WORD
        )
        self.similar_features.pack(fill=tk.X, pady=(5, 0))
        
        # Contact info
        self._create_contact_section()
        
        # Action buttons
        self._create_action_buttons("Submit Feature Request")
    
    def _create_satisfaction_survey(self):
        """Create satisfaction survey"""
        colors = self.theme_manager.get_colors()
        
        # Header
        self._create_header("📊 User Satisfaction Survey", "Help us improve your learning experience")
        
        # Overall satisfaction
        overall_frame = self._create_section("Overall Satisfaction")
        
        tk.Label(
            overall_frame,
            text="How satisfied are you with the app overall?",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Star rating
        stars_frame = tk.Frame(overall_frame, bg=colors['frame_bg'])
        stars_frame.pack(anchor=tk.W)
        
        self.star_buttons = []
        for i in range(1, 6):
            star_btn = tk.Button(
                stars_frame,
                text="⭐",
                font=('TkDefaultFont', 20),
                bg=colors['frame_bg'],
                fg=colors['disabled_fg'],
                relief=tk.FLAT,
                command=lambda rating=i: self._set_rating(rating)
            )
            star_btn.pack(side=tk.LEFT, padx=3)
            self.star_buttons.append(star_btn)
        
        self._update_star_display()
        
        # Specific aspects
        aspects_frame = self._create_section("Rate Specific Aspects")
        
        self.aspect_ratings = {}
        aspects = [
            ("ease_of_use", "Ease of use"),
            ("learning_effectiveness", "Learning effectiveness"),
            ("image_quality", "Image quality"),
            ("ai_descriptions", "AI description quality"),
            ("vocabulary_extraction", "Vocabulary extraction"),
            ("export_features", "Export features")
        ]
        
        for aspect_key, aspect_name in aspects:
            aspect_frame = tk.Frame(aspects_frame, bg=colors['frame_bg'])
            aspect_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(
                aspect_frame,
                text=aspect_name + ":",
                font=('TkDefaultFont', 10),
                bg=colors['frame_bg'],
                fg=colors['fg'],
                width=20,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            rating_var = tk.IntVar(value=3)
            self.aspect_ratings[aspect_key] = rating_var
            
            for i in range(1, 6):
                radio = tk.Radiobutton(
                    aspect_frame,
                    text=str(i),
                    variable=rating_var,
                    value=i,
                    font=('TkDefaultFont', 9),
                    bg=colors['frame_bg'],
                    fg=colors['fg'],
                    selectcolor=colors['entry_bg']
                )
                radio.pack(side=tk.LEFT)
        
        # Usage patterns
        usage_frame = self._create_section("Usage Patterns")
        
        tk.Label(
            usage_frame,
            text="How often do you use the app?",
            font=('TkDefaultFont', 10),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(anchor=tk.W)
        
        self.usage_frequency = tk.StringVar(value="weekly")
        frequencies = [
            ("daily", "Daily"),
            ("weekly", "A few times a week"),
            ("monthly", "A few times a month"),
            ("rarely", "Rarely")
        ]
        
        for value, text in frequencies:
            radio = tk.Radiobutton(
                usage_frame,
                text=text,
                variable=self.usage_frequency,
                value=value,
                font=('TkDefaultFont', 10),
                bg=colors['frame_bg'],
                fg=colors['fg'],
                selectcolor=colors['entry_bg']
            )
            radio.pack(anchor=tk.W, pady=2)
        
        # Learning goals
        goals_frame = self._create_section("Learning Progress")
        
        tk.Label(
            goals_frame,
            text="Has the app helped you achieve your Spanish learning goals?",
            font=('TkDefaultFont', 10),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(anchor=tk.W)
        
        self.learning_progress = tk.StringVar(value="somewhat")
        progress_options = [
            ("very_much", "Very much - I've learned a lot"),
            ("somewhat", "Somewhat - I've made some progress"),
            ("a_little", "A little - Minor improvement"),
            ("not_really", "Not really - No significant progress")
        ]
        
        for value, text in progress_options:
            radio = tk.Radiobutton(
                goals_frame,
                text=text,
                variable=self.learning_progress,
                value=value,
                font=('TkDefaultFont', 10),
                bg=colors['frame_bg'],
                fg=colors['fg'],
                selectcolor=colors['entry_bg']
            )
            radio.pack(anchor=tk.W, pady=2)
        
        # Recommendations
        rec_frame = self._create_section("Recommendation")
        
        tk.Label(
            rec_frame,
            text="Would you recommend this app to other Spanish learners?",
            font=('TkDefaultFont', 10),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(anchor=tk.W)
        
        self.recommendation = tk.StringVar(value="yes")
        rec_options = [
            ("definitely", "Definitely"),
            ("probably", "Probably"),
            ("maybe", "Maybe"),
            ("probably_not", "Probably not"),
            ("definitely_not", "Definitely not")
        ]
        
        for value, text in rec_options:
            radio = tk.Radiobutton(
                rec_frame,
                text=text,
                variable=self.recommendation,
                value=value,
                font=('TkDefaultFont', 10),
                bg=colors['frame_bg'],
                fg=colors['fg'],
                selectcolor=colors['entry_bg']
            )
            radio.pack(anchor=tk.W, pady=2)
        
        # Additional comments
        self._create_comments_section("Additional Comments (Optional)")
        
        # Action buttons
        self._create_action_buttons("Submit Survey")
    
    def _create_header(self, title: str, subtitle: str):
        """Create form header"""
        colors = self.theme_manager.get_colors()
        
        header_frame = tk.Frame(self.scrollable_frame, bg=colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = tk.Label(
            header_frame,
            text=title,
            font=('TkDefaultFont', 16, 'bold'),
            bg=colors['bg'],
            fg=colors['info']
        )
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text=subtitle,
            font=('TkDefaultFont', 10),
            bg=colors['bg'],
            fg=colors['disabled_fg']
        )
        subtitle_label.pack(pady=(5, 0))
    
    def _create_section(self, title: str) -> tk.Frame:
        """Create a form section"""
        colors = self.theme_manager.get_colors()
        
        section_frame = tk.LabelFrame(
            self.scrollable_frame,
            text=title,
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg'],
            padx=15,
            pady=10
        )
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        return section_frame
    
    def _create_comments_section(self, title: str = "Additional Comments"):
        """Create comments section"""
        colors = self.theme_manager.get_colors()
        
        comments_frame = self._create_section(title)
        
        tk.Label(
            comments_frame,
            text="Share any additional thoughts or suggestions:",
            font=('TkDefaultFont', 10),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(anchor=tk.W)
        
        self.comments_text = tk.Text(
            comments_frame,
            height=5,
            font=('TkDefaultFont', 10),
            bg=colors['text_bg'],
            fg=colors['text_fg'],
            wrap=tk.WORD
        )
        self.comments_text.pack(fill=tk.X, pady=(5, 0))
    
    def _create_contact_section(self):
        """Create contact information section"""
        colors = self.theme_manager.get_colors()
        
        contact_frame = self._create_section("Contact Information (Optional)")
        
        tk.Label(
            contact_frame,
            text="If you'd like us to follow up, please provide your email:",
            font=('TkDefaultFont', 10),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(anchor=tk.W)
        
        self.email_entry = tk.Entry(
            contact_frame,
            font=('TkDefaultFont', 10),
            bg=colors['entry_bg'],
            fg=colors['entry_fg'],
            width=40
        )
        self.email_entry.pack(anchor=tk.W, pady=(5, 0))
        
        privacy_label = tk.Label(
            contact_frame,
            text="We'll only use this to respond to your feedback. Your email won't be shared.",
            font=('TkDefaultFont', 9, 'italic'),
            bg=colors['frame_bg'],
            fg=colors['disabled_fg']
        )
        privacy_label.pack(anchor=tk.W, pady=(5, 0))
    
    def _create_system_info_section(self):
        """Create system information section"""
        colors = self.theme_manager.get_colors()
        
        system_frame = self._create_section("System Information")
        
        try:
            import platform
            import sys
            
            # Get system info
            system_info = f\"\"\"Operating System: {platform.system()} {platform.release()}
Python Version: {sys.version.split()[0]}
App Version: 2.0.0\"\"\"  # Would get from actual version
            
            info_text = tk.Text(
                system_frame,
                height=4,
                font=('TkDefaultFont', 9),
                bg=colors['text_bg'],
                fg=colors['text_fg'],
                state=tk.DISABLED
            )
            info_text.pack(fill=tk.X)
            
            info_text.config(state=tk.NORMAL)
            info_text.insert(tk.END, system_info)
            info_text.config(state=tk.DISABLED)
            
        except Exception:
            tk.Label(
                system_frame,
                text="System information not available",
                font=('TkDefaultFont', 9),
                bg=colors['frame_bg'],
                fg=colors['disabled_fg']
            ).pack()
    
    def _create_action_buttons(self, submit_text: str = "Submit Feedback"):
        """Create action buttons"""
        colors = self.theme_manager.get_colors()
        
        button_frame = tk.Frame(self.scrollable_frame, bg=colors['bg'])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            font=('TkDefaultFont', 10),
            bg=colors['button_bg'],
            fg=colors['button_fg'],
            relief=tk.FLAT,
            command=self._cancel_feedback,
            padx=20
        )
        cancel_btn.pack(side=tk.LEFT)
        
        # Submit button
        submit_btn = tk.Button(
            button_frame,
            text=submit_text,
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['success'],
            fg=colors['select_fg'],
            relief=tk.FLAT,
            command=self._submit_feedback,
            padx=20
        )
        submit_btn.pack(side=tk.RIGHT)
    
    def _set_rating(self, rating: int):
        """Set star rating"""
        self.rating.set(rating)
        self._update_star_display()
    
    def _update_star_display(self):
        """Update star button display"""
        colors = self.theme_manager.get_colors()
        
        for i, btn in enumerate(self.star_buttons, 1):
            if i <= self.rating.get():
                btn.config(fg=colors['warning'])  # Gold color for selected stars
            else:
                btn.config(fg=colors['disabled_fg'])
    
    def _on_feedback_type_change(self):
        """Handle feedback type change"""
        # Clear the form and recreate it
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self._create_feedback_form()
    
    def _submit_feedback(self):
        """Submit the feedback"""
        feedback_data = self._collect_feedback_data()
        
        if not self._validate_feedback(feedback_data):
            return
        
        # Save feedback locally
        self._save_feedback(feedback_data)
        
        # Show confirmation
        messagebox.showinfo(
            "Feedback Submitted",
            "Thank you for your feedback! We appreciate you taking the time to help us improve.",
            parent=self.feedback_window
        )
        
        # Track feedback submission
        if self.on_feedback_submit:
            self.on_feedback_submit(feedback_data['type'])
        
        # Close window
        self.feedback_window.destroy()
        self.feedback_window = None
    
    def _collect_feedback_data(self) -> Dict[str, Any]:
        """Collect all feedback data"""
        feedback_type = self.feedback_type.get()
        
        base_data = {
            'type': feedback_type,
            'timestamp': datetime.now().isoformat(),
            'rating': self.rating.get(),
            'comments': getattr(self, 'comments_text', None) and self.comments_text.get('1.0', tk.END).strip(),
            'email': getattr(self, 'email_entry', None) and self.email_entry.get().strip()
        }
        
        # Add type-specific data
        if feedback_type == "bug":
            base_data.update({
                'bug_description': getattr(self, 'bug_description', None) and self.bug_description.get('1.0', tk.END).strip(),
                'steps_to_reproduce': getattr(self, 'bug_steps', None) and self.bug_steps.get('1.0', tk.END).strip(),
                'expected_behavior': getattr(self, 'expected_behavior', None) and self.expected_behavior.get('1.0', tk.END).strip(),
                'actual_behavior': getattr(self, 'actual_behavior', None) and self.actual_behavior.get('1.0', tk.END).strip(),
                'severity': getattr(self, 'severity', None) and self.severity.get()
            })
        elif feedback_type == "feature":
            base_data.update({
                'feature_description': getattr(self, 'feature_description', None) and self.feature_description.get('1.0', tk.END).strip(),
                'use_case': getattr(self, 'feature_usecase', None) and self.feature_usecase.get('1.0', tk.END).strip(),
                'priority': getattr(self, 'priority', None) and self.priority.get(),
                'similar_features': getattr(self, 'similar_features', None) and self.similar_features.get('1.0', tk.END).strip()
            })
        elif feedback_type == "survey":
            aspect_ratings = {}
            if hasattr(self, 'aspect_ratings'):
                aspect_ratings = {key: var.get() for key, var in self.aspect_ratings.items()}
            
            base_data.update({
                'aspect_ratings': aspect_ratings,
                'usage_frequency': getattr(self, 'usage_frequency', None) and self.usage_frequency.get(),
                'learning_progress': getattr(self, 'learning_progress', None) and self.learning_progress.get(),
                'recommendation': getattr(self, 'recommendation', None) and self.recommendation.get()
            })
        
        return base_data
    
    def _validate_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """Validate feedback data"""
        feedback_type = feedback_data['type']
        
        if feedback_type == "bug":
            if not feedback_data.get('bug_description'):
                messagebox.showerror("Missing Information", "Please describe the problem.", parent=self.feedback_window)
                return False
        elif feedback_type == "feature":
            if not feedback_data.get('feature_description'):
                messagebox.showerror("Missing Information", "Please describe the feature you'd like.", parent=self.feedback_window)
                return False
        
        # Validate email format if provided
        email = feedback_data.get('email', '').strip()
        if email and '@' not in email:
            messagebox.showerror("Invalid Email", "Please enter a valid email address.", parent=self.feedback_window)
            return False
        
        return True
    
    def _save_feedback(self, feedback_data: Dict[str, Any]):
        """Save feedback to local file"""
        try:
            # Load existing feedback
            if self.feedback_file.exists():
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    existing_feedback = json.load(f)
            else:
                existing_feedback = []
            
            # Add new feedback
            existing_feedback.append(feedback_data)
            
            # Save back to file
            self.feedback_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(existing_feedback, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving feedback: {e}")
    
    def _cancel_feedback(self):
        """Cancel feedback submission"""
        self.feedback_window.destroy()
        self.feedback_window = None
    
    def _bind_mousewheel(self):
        """Enable mouse wheel scrolling"""
        def _on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.feedback_window.bind("<MouseWheel>", _on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get feedback statistics"""
        try:
            if not self.feedback_file.exists():
                return {'total_feedback': 0}
            
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                feedback_list = json.load(f)
            
            # Analyze feedback
            stats = {
                'total_feedback': len(feedback_list),
                'by_type': {},
                'average_rating': 0,
                'recent_feedback': 0
            }
            
            # Count by type and calculate average rating
            ratings = []
            recent_count = 0
            cutoff_date = datetime.now().replace(day=1)  # This month
            
            for feedback in feedback_list:
                fb_type = feedback.get('type', 'unknown')
                stats['by_type'][fb_type] = stats['by_type'].get(fb_type, 0) + 1
                
                if 'rating' in feedback:
                    ratings.append(feedback['rating'])
                
                # Count recent feedback
                try:
                    fb_date = datetime.fromisoformat(feedback['timestamp'])
                    if fb_date >= cutoff_date:
                        recent_count += 1
                except:
                    pass
            
            if ratings:
                stats['average_rating'] = sum(ratings) / len(ratings)
            
            stats['recent_feedback'] = recent_count
            
            return stats
            
        except Exception:
            return {'total_feedback': 0}
    
    def hide(self):
        """Hide the feedback window"""
        if self.feedback_window:
            self.feedback_window.destroy()
            self.feedback_window = None