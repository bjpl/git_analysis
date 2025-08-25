"""
Personalization wizard for customizing user experience
Collects preferences for learning goals, interface settings, and content preferences
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict, Any, List
import json


class PersonalizationWizard:
    """
    Collects user preferences to personalize their learning experience
    """
    
    def __init__(self, parent: tk.Tk, theme_manager,
                 on_completion: Callable[[Dict[str, Any]], None] = None,
                 on_skip: Callable = None):
        self.parent = parent
        self.theme_manager = theme_manager
        self.on_completion = on_completion
        self.on_skip = on_skip
        
        self.wizard_window = None
        self.current_page = 0
        self.total_pages = 4
        
        # Preference variables
        self.preferences = {}
        self._init_preference_variables()
        
        # Page definitions
        self.pages = [
            {
                'title': 'Learning Goals',
                'subtitle': 'What do you want to achieve?',
                'create_method': '_create_learning_goals_page'
            },
            {
                'title': 'Content Preferences', 
                'subtitle': 'What topics interest you?',
                'create_method': '_create_content_preferences_page'
            },
            {
                'title': 'Interface Settings',
                'subtitle': 'How do you like to learn?', 
                'create_method': '_create_interface_settings_page'
            },
            {
                'title': 'Summary',
                'subtitle': 'Review your preferences',
                'create_method': '_create_summary_page'
            }
        ]
    
    def _init_preference_variables(self):
        """Initialize all preference variables"""
        # Learning goals
        self.spanish_level = tk.StringVar(value="beginner")
        self.daily_goal = tk.StringVar(value="10")
        self.learning_style = tk.StringVar(value="visual")
        self.focus_areas = {
            'vocabulary': tk.BooleanVar(value=True),
            'grammar': tk.BooleanVar(value=False),
            'conversation': tk.BooleanVar(value=True),
            'reading': tk.BooleanVar(value=False),
            'listening': tk.BooleanVar(value=False)
        }
        
        # Content preferences
        self.preferred_topics = {
            'food': tk.BooleanVar(value=False),
            'travel': tk.BooleanVar(value=False),
            'nature': tk.BooleanVar(value=False),
            'city_life': tk.BooleanVar(value=False),
            'culture': tk.BooleanVar(value=False),
            'sports': tk.BooleanVar(value=False),
            'art': tk.BooleanVar(value=False),
            'technology': tk.BooleanVar(value=False),
            'family': tk.BooleanVar(value=False),
            'work': tk.BooleanVar(value=False)
        }
        self.difficulty_preference = tk.StringVar(value="mixed")
        self.description_length = tk.StringVar(value="medium")
        
        # Interface settings
        self.auto_extract = tk.BooleanVar(value=True)
        self.show_translations = tk.BooleanVar(value=True)
        self.export_format = tk.StringVar(value="anki")
        self.theme_preference = tk.StringVar(value="auto")
        self.font_size = tk.StringVar(value="normal")
        self.enable_sounds = tk.BooleanVar(value=False)
        self.show_hints = tk.BooleanVar(value=True)
    
    def show(self):
        """Display the personalization wizard"""
        if self.wizard_window:
            self.wizard_window.lift()
            return
        
        colors = self.theme_manager.get_colors()
        
        # Create wizard window
        self.wizard_window = tk.Toplevel(self.parent)
        self.wizard_window.title("Personalize Your Experience")
        self.wizard_window.geometry("650x550")
        self.wizard_window.configure(bg=colors['bg'])
        self.wizard_window.resizable(False, False)
        self.wizard_window.transient(self.parent)
        self.wizard_window.grab_set()
        
        # Center window
        self.wizard_window.update_idletasks()
        x = (self.wizard_window.winfo_screenwidth() // 2) - 325
        y = (self.wizard_window.winfo_screenheight() // 2) - 275
        self.wizard_window.geometry(f"+{x}+{y}")
        
        # Prevent closing with X button
        self.wizard_window.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        self._create_wizard_structure()
        self._show_page(0)
    
    def _create_wizard_structure(self):
        """Create the basic wizard structure"""
        colors = self.theme_manager.get_colors()
        
        # Header
        header_frame = tk.Frame(self.wizard_window, bg=colors['bg'])
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Icon and title
        icon_label = tk.Label(
            header_frame,
            text="⚙️",
            font=('TkDefaultFont', 24),
            bg=colors['bg'],
            fg=colors['info']
        )
        icon_label.pack()
        
        self.page_title_label = tk.Label(
            header_frame,
            text="Personalization",
            font=('TkDefaultFont', 16, 'bold'),
            bg=colors['bg'],
            fg=colors['fg']
        )
        self.page_title_label.pack(pady=(5, 0))
        
        self.page_subtitle_label = tk.Label(
            header_frame,
            text="Let's customize your experience",
            font=('TkDefaultFont', 10),
            bg=colors['bg'],
            fg=colors['disabled_fg']
        )
        self.page_subtitle_label.pack(pady=(2, 0))
        
        # Progress indicator
        progress_frame = tk.Frame(header_frame, bg=colors['bg'])
        progress_frame.pack(pady=(15, 0))
        
        self.progress_dots = []
        for i in range(self.total_pages):
            dot = tk.Label(
                progress_frame,
                text="●",
                font=('TkDefaultFont', 12),
                bg=colors['bg'],
                fg=colors['border']
            )
            dot.pack(side=tk.LEFT, padx=2)
            self.progress_dots.append(dot)
        
        # Content area
        self.content_frame = tk.Frame(self.wizard_window, bg=colors['bg'])
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Navigation
        nav_frame = tk.Frame(self.wizard_window, bg=colors['bg'])
        nav_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        # Skip button
        self.skip_button = tk.Button(
            nav_frame,
            text="Skip Personalization",
            command=self._skip_personalization,
            font=('TkDefaultFont', 10),
            bg=colors['button_bg'],
            fg=colors['disabled_fg'],
            relief=tk.FLAT,
            padx=20
        )
        self.skip_button.pack(side=tk.LEFT)
        
        # Right navigation
        right_nav = tk.Frame(nav_frame, bg=colors['bg'])
        right_nav.pack(side=tk.RIGHT)
        
        # Back button
        self.back_button = tk.Button(
            right_nav,
            text="← Back",
            command=self._previous_page,
            font=('TkDefaultFont', 10),
            bg=colors['button_bg'],
            fg=colors['button_fg'],
            relief=tk.FLAT,
            padx=20
        )
        self.back_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Next button
        self.next_button = tk.Button(
            right_nav,
            text="Next →",
            command=self._next_page,
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['select_bg'],
            fg=colors['select_fg'],
            relief=tk.FLAT,
            padx=20
        )
        self.next_button.pack(side=tk.LEFT)
    
    def _show_page(self, page_index: int):
        """Show a specific page"""
        if page_index < 0 or page_index >= self.total_pages:
            return
        
        self.current_page = page_index
        page = self.pages[page_index]
        colors = self.theme_manager.get_colors()
        
        # Update header
        self.page_title_label.config(text=page['title'])
        self.page_subtitle_label.config(text=page['subtitle'])
        
        # Update progress dots
        for i, dot in enumerate(self.progress_dots):
            if i == page_index:
                dot.config(fg=colors['select_bg'])
            elif i < page_index:
                dot.config(fg=colors['success'])
            else:
                dot.config(fg=colors['border'])
        
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Create page content
        create_method = getattr(self, page['create_method'])
        create_method()
        
        # Update navigation
        self.back_button.config(state=tk.NORMAL if page_index > 0 else tk.DISABLED)
        
        if page_index == self.total_pages - 1:
            self.next_button.config(text="Complete Setup ✓")
        else:
            self.next_button.config(text="Next →")
    
    def _create_learning_goals_page(self):
        """Create the learning goals page"""
        colors = self.theme_manager.get_colors()
        
        # Spanish level
        level_frame = tk.LabelFrame(
            self.content_frame,
            text="What's your Spanish level?",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg'],
            padx=15,
            pady=10
        )
        level_frame.pack(fill=tk.X, pady=(0, 15))
        
        levels = [
            ("beginner", "Beginner - Just starting out"),
            ("elementary", "Elementary - Know basic words"), 
            ("intermediate", "Intermediate - Can have simple conversations"),
            ("advanced", "Advanced - Fluent but want to improve")
        ]
        
        for value, text in levels:
            radio = tk.Radiobutton(
                level_frame,
                text=text,
                variable=self.spanish_level,
                value=value,
                font=('TkDefaultFont', 10),
                bg=colors['frame_bg'],
                fg=colors['fg'],
                selectcolor=colors['entry_bg']
            )
            radio.pack(anchor=tk.W, pady=2)
        
        # Daily goal
        goal_frame = tk.LabelFrame(
            self.content_frame,
            text="How many new words do you want to learn daily?",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg'],
            padx=15,
            pady=10
        )
        goal_frame.pack(fill=tk.X, pady=(0, 15))
        
        goal_options = [
            ("5", "5 words - Light learning"),
            ("10", "10 words - Steady progress"),
            ("20", "20 words - Intensive learning"),
            ("unlimited", "No limit - Learn as much as possible")
        ]
        
        for value, text in goal_options:
            radio = tk.Radiobutton(
                goal_frame,
                text=text,
                variable=self.daily_goal,
                value=value,
                font=('TkDefaultFont', 10),
                bg=colors['frame_bg'],
                fg=colors['fg'],
                selectcolor=colors['entry_bg']
            )
            radio.pack(anchor=tk.W, pady=2)
        
        # Learning style
        style_frame = tk.LabelFrame(
            self.content_frame,
            text="How do you learn best?",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg'],
            padx=15,
            pady=10
        )
        style_frame.pack(fill=tk.X, pady=(0, 15))
        
        styles = [
            ("visual", "Visual - Learning through images and context"),
            ("analytical", "Analytical - Focus on grammar and structure"),
            ("immersive", "Immersive - Learning through natural conversation"),
            ("mixed", "Mixed - Combination of all approaches")
        ]
        
        for value, text in styles:
            radio = tk.Radiobutton(
                style_frame,
                text=text,
                variable=self.learning_style,
                value=value,
                font=('TkDefaultFont', 10),
                bg=colors['frame_bg'],
                fg=colors['fg'],
                selectcolor=colors['entry_bg']
            )
            radio.pack(anchor=tk.W, pady=2)
        
        # Focus areas
        focus_frame = tk.LabelFrame(
            self.content_frame,
            text="What areas do you want to focus on?",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg'],
            padx=15,
            pady=10
        )
        focus_frame.pack(fill=tk.X)
        
        focus_areas = [
            ('vocabulary', 'Vocabulary - Learning new words'),
            ('grammar', 'Grammar - Understanding sentence structure'),
            ('conversation', 'Conversation - Speaking and listening'),
            ('reading', 'Reading - Understanding written text'),
            ('listening', 'Listening - Audio comprehension')
        ]
        
        for key, text in focus_areas:
            check = tk.Checkbutton(
                focus_frame,
                text=text,
                variable=self.focus_areas[key],
                font=('TkDefaultFont', 10),
                bg=colors['frame_bg'],
                fg=colors['fg'],
                selectcolor=colors['entry_bg']
            )
            check.pack(anchor=tk.W, pady=2)
    
    def _create_content_preferences_page(self):
        """Create the content preferences page"""
        colors = self.theme_manager.get_colors()
        
        # Preferred topics
        topics_frame = tk.LabelFrame(
            self.content_frame,
            text="What topics interest you most? (Select any that apply)",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg'],
            padx=15,
            pady=10
        )
        topics_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create topics in columns
        topics_container = tk.Frame(topics_frame, bg=colors['frame_bg'])
        topics_container.pack(fill=tk.X)
        
        left_col = tk.Frame(topics_container, bg=colors['frame_bg'])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_col = tk.Frame(topics_container, bg=colors['frame_bg'])
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        topic_labels = {
            'food': '🍽️ Food & Cooking',
            'travel': '✈️ Travel & Tourism', 
            'nature': '🌳 Nature & Environment',
            'city_life': '🏙️ City Life',
            'culture': '🎭 Culture & Traditions',
            'sports': '⚽ Sports & Recreation',
            'art': '🎨 Art & Creativity',
            'technology': '💻 Technology',
            'family': '👨‍👩‍👧‍👦 Family & Relationships',
            'work': '💼 Work & Business'
        }
        
        topics = list(topic_labels.items())
        for i, (key, text) in enumerate(topics):
            parent = left_col if i < len(topics) // 2 else right_col
            
            check = tk.Checkbutton(
                parent,
                text=text,
                variable=self.preferred_topics[key],
                font=('TkDefaultFont', 10),
                bg=colors['frame_bg'],
                fg=colors['fg'],
                selectcolor=colors['entry_bg']
            )
            check.pack(anchor=tk.W, pady=2)
        
        # Difficulty preference
        difficulty_frame = tk.LabelFrame(
            self.content_frame,
            text="What difficulty level do you prefer?",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg'],
            padx=15,
            pady=10
        )
        difficulty_frame.pack(fill=tk.X, pady=(0, 15))
        
        difficulties = [
            ("easy", "Easy - Simple vocabulary and short descriptions"),
            ("medium", "Medium - Moderate vocabulary with detailed descriptions"),
            ("challenging", "Challenging - Complex vocabulary and advanced concepts"),
            ("mixed", "Mixed - Variety of difficulty levels")
        ]
        
        for value, text in difficulties:
            radio = tk.Radiobutton(
                difficulty_frame,
                text=text,
                variable=self.difficulty_preference,
                value=value,
                font=('TkDefaultFont', 10),
                bg=colors['frame_bg'],
                fg=colors['fg'],
                selectcolor=colors['entry_bg']
            )
            radio.pack(anchor=tk.W, pady=2)
        
        # Description length
        length_frame = tk.LabelFrame(
            self.content_frame,
            text="How detailed should the AI descriptions be?",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg'],
            padx=15,
            pady=10
        )
        length_frame.pack(fill=tk.X)
        
        lengths = [
            ("short", "Short - Quick overviews (1-2 sentences)"),
            ("medium", "Medium - Detailed descriptions (1-2 paragraphs)"),
            ("long", "Long - Comprehensive analysis (multiple paragraphs)")
        ]
        
        for value, text in lengths:
            radio = tk.Radiobutton(
                length_frame,
                text=text,
                variable=self.description_length,
                value=value,
                font=('TkDefaultFont', 10),
                bg=colors['frame_bg'],
                fg=colors['fg'],
                selectcolor=colors['entry_bg']
            )
            radio.pack(anchor=tk.W, pady=2)
    
    def _create_interface_settings_page(self):
        """Create the interface settings page"""
        colors = self.theme_manager.get_colors()
        
        # Learning features
        features_frame = tk.LabelFrame(
            self.content_frame,
            text="Learning Features",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg'],
            padx=15,
            pady=10
        )
        features_frame.pack(fill=tk.X, pady=(0, 15))
        
        feature_options = [
            (self.auto_extract, "Automatically extract vocabulary from descriptions"),
            (self.show_translations, "Show English translations immediately"),
            (self.show_hints, "Show contextual hints and tips"),
            (self.enable_sounds, "Enable sound effects and notifications")
        ]
        
        for var, text in feature_options:
            check = tk.Checkbutton(
                features_frame,
                text=text,
                variable=var,
                font=('TkDefaultFont', 10),
                bg=colors['frame_bg'],
                fg=colors['fg'],
                selectcolor=colors['entry_bg']
            )
            check.pack(anchor=tk.W, pady=2)
        
        # Export format
        export_frame = tk.LabelFrame(
            self.content_frame,
            text="Preferred export format for vocabulary",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg'],
            padx=15,
            pady=10
        )
        export_frame.pack(fill=tk.X, pady=(0, 15))
        
        formats = [
            ("anki", "Anki - For spaced repetition learning"),
            ("csv", "CSV - For spreadsheet applications"),
            ("text", "Text - Simple text file format"),
            ("json", "JSON - Structured data format")
        ]
        
        for value, text in formats:
            radio = tk.Radiobutton(
                export_frame,
                text=text,
                variable=self.export_format,
                value=value,
                font=('TkDefaultFont', 10),
                bg=colors['frame_bg'],
                fg=colors['fg'],
                selectcolor=colors['entry_bg']
            )
            radio.pack(anchor=tk.W, pady=2)
        
        # Appearance settings
        appearance_frame = tk.LabelFrame(
            self.content_frame,
            text="Appearance",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['fg'],
            padx=15,
            pady=10
        )
        appearance_frame.pack(fill=tk.X)
        
        # Theme preference
        theme_subframe = tk.Frame(appearance_frame, bg=colors['frame_bg'])
        theme_subframe.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            theme_subframe,
            text="Theme:",
            font=('TkDefaultFont', 10),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(side=tk.LEFT)
        
        theme_combo = ttk.Combobox(
            theme_subframe,
            textvariable=self.theme_preference,
            values=["auto", "light", "dark"],
            state="readonly",
            width=15
        )
        theme_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Font size
        font_subframe = tk.Frame(appearance_frame, bg=colors['frame_bg'])
        font_subframe.pack(fill=tk.X)
        
        tk.Label(
            font_subframe,
            text="Font size:",
            font=('TkDefaultFont', 10),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(side=tk.LEFT)
        
        font_combo = ttk.Combobox(
            font_subframe,
            textvariable=self.font_size,
            values=["small", "normal", "large", "extra_large"],
            state="readonly",
            width=15
        )
        font_combo.pack(side=tk.LEFT, padx=(10, 0))
    
    def _create_summary_page(self):
        """Create the summary page"""
        colors = self.theme_manager.get_colors()
        
        # Summary title
        summary_label = tk.Label(
            self.content_frame,
            text="Here's your personalized configuration:",
            font=('TkDefaultFont', 11, 'bold'),
            bg=colors['bg'],
            fg=colors['fg']
        )
        summary_label.pack(pady=(0, 15))
        
        # Create scrollable summary
        canvas = tk.Canvas(
            self.content_frame,
            bg=colors['bg'],
            highlightthickness=0,
            height=300
        )
        scrollbar = ttk.Scrollbar(
            self.content_frame,
            orient="vertical",
            command=canvas.yview
        )
        scrollable_frame = tk.Frame(canvas, bg=colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Generate summary content
        self._generate_summary_content(scrollable_frame)
        
        # Note about changes
        note_label = tk.Label(
            self.content_frame,
            text="💡 You can change these settings anytime in the app preferences",
            font=('TkDefaultFont', 9, 'italic'),
            bg=colors['bg'],
            fg=colors['info'],
            wraplength=500
        )
        note_label.pack(pady=(15, 0))
    
    def _generate_summary_content(self, parent):
        """Generate the summary content"""
        colors = self.theme_manager.get_colors()
        
        # Learning Goals Summary
        goals_frame = tk.LabelFrame(
            parent,
            text="Learning Goals",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['info'],
            padx=15,
            pady=10
        )
        goals_frame.pack(fill=tk.X, pady=(0, 10))
        
        level_labels = {
            "beginner": "Beginner", "elementary": "Elementary",
            "intermediate": "Intermediate", "advanced": "Advanced"
        }
        
        goal_labels = {
            "5": "5 words", "10": "10 words", "20": "20 words", "unlimited": "No limit"
        }
        
        style_labels = {
            "visual": "Visual learning", "analytical": "Analytical approach",
            "immersive": "Immersive method", "mixed": "Mixed approaches"
        }
        
        goals_text = f"""Spanish Level: {level_labels.get(self.spanish_level.get(), "Not specified")}
Daily Goal: {goal_labels.get(self.daily_goal.get(), "Not specified")}
Learning Style: {style_labels.get(self.learning_style.get(), "Not specified")}

Focus Areas:"""
        
        # Add selected focus areas
        selected_focus = [area.replace('_', ' ').title() for area, var in self.focus_areas.items() if var.get()]
        if selected_focus:
            goals_text += " " + ", ".join(selected_focus)
        else:
            goals_text += " None selected"
        
        tk.Label(
            goals_frame,
            text=goals_text,
            font=('TkDefaultFont', 9),
            bg=colors['frame_bg'],
            fg=colors['fg'],
            justify=tk.LEFT,
            anchor=tk.W
        ).pack(fill=tk.X)
        
        # Content Preferences Summary
        content_frame = tk.LabelFrame(
            parent,
            text="Content Preferences",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['info'],
            padx=15,
            pady=10
        )
        content_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Selected topics
        selected_topics = [topic.replace('_', ' ').title() for topic, var in self.preferred_topics.items() if var.get()]
        topics_text = "Preferred Topics: " + (", ".join(selected_topics) if selected_topics else "All topics")
        
        difficulty_labels = {
            "easy": "Easy", "medium": "Medium", "challenging": "Challenging", "mixed": "Mixed"
        }
        
        length_labels = {
            "short": "Short", "medium": "Medium", "long": "Long"
        }
        
        content_text = f"""{topics_text}

Difficulty Level: {difficulty_labels.get(self.difficulty_preference.get(), "Not specified")}
Description Length: {length_labels.get(self.description_length.get(), "Not specified")}"""
        
        tk.Label(
            content_frame,
            text=content_text,
            font=('TkDefaultFont', 9),
            bg=colors['frame_bg'],
            fg=colors['fg'],
            justify=tk.LEFT,
            anchor=tk.W,
            wraplength=450
        ).pack(fill=tk.X)
        
        # Interface Settings Summary
        interface_frame = tk.LabelFrame(
            parent,
            text="Interface Settings",
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['frame_bg'],
            fg=colors['info'],
            padx=15,
            pady=10
        )
        interface_frame.pack(fill=tk.X)
        
        # Feature settings
        features_enabled = []
        feature_names = {
            'auto_extract': 'Auto-extract vocabulary',
            'show_translations': 'Show translations',
            'show_hints': 'Show hints',
            'enable_sounds': 'Enable sounds'
        }
        
        for key, name in feature_names.items():
            if getattr(self, key).get():
                features_enabled.append(name)
        
        features_text = "Enabled Features: " + (", ".join(features_enabled) if features_enabled else "None")
        
        interface_text = f"""{features_text}

Export Format: {self.export_format.get().upper()}
Theme: {self.theme_preference.get().title()}
Font Size: {self.font_size.get().replace('_', ' ').title()}"""
        
        tk.Label(
            interface_frame,
            text=interface_text,
            font=('TkDefaultFont', 9),
            bg=colors['frame_bg'],
            fg=colors['fg'],
            justify=tk.LEFT,
            anchor=tk.W
        ).pack(fill=tk.X)
    
    def _collect_preferences(self) -> Dict[str, Any]:
        """Collect all preferences into a dictionary"""
        preferences = {
            'learning_goals': {
                'spanish_level': self.spanish_level.get(),
                'daily_goal': self.daily_goal.get(),
                'learning_style': self.learning_style.get(),
                'focus_areas': {area: var.get() for area, var in self.focus_areas.items()}
            },
            'content_preferences': {
                'preferred_topics': {topic: var.get() for topic, var in self.preferred_topics.items()},
                'difficulty_preference': self.difficulty_preference.get(),
                'description_length': self.description_length.get()
            },
            'interface_settings': {
                'auto_extract': self.auto_extract.get(),
                'show_translations': self.show_translations.get(),
                'export_format': self.export_format.get(),
                'theme_preference': self.theme_preference.get(),
                'font_size': self.font_size.get(),
                'enable_sounds': self.enable_sounds.get(),
                'show_hints': self.show_hints.get()
            },
            'setup_date': tk.datetime.datetime.now().isoformat() if hasattr(tk, 'datetime') else None
        }
        
        return preferences
    
    def _next_page(self):
        """Go to next page or complete"""
        if self.current_page < self.total_pages - 1:
            self._show_page(self.current_page + 1)
        else:
            # Complete personalization
            preferences = self._collect_preferences()
            if self.on_completion:
                self.on_completion(preferences)
    
    def _previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self._show_page(self.current_page - 1)
    
    def _skip_personalization(self):
        """Skip personalization"""
        from ..theme_manager import ThemedMessageBox
        
        result = ThemedMessageBox.ask_yes_no(
            self.wizard_window,
            "Skip Personalization",
            "Are you sure you want to skip personalization?\\n\\n" +
            "We can customize the app to better match your learning style.",
            self.theme_manager
        )
        
        if result and self.on_skip:
            self.on_skip()
    
    def _on_window_close(self):
        """Handle window close"""
        self._skip_personalization()
    
    def hide(self):
        """Hide the wizard"""
        if self.wizard_window:
            self.wizard_window.destroy()
            self.wizard_window = None