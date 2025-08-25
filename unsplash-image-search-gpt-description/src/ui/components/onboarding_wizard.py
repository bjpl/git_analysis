"""
Modern onboarding wizard with progressive screens and smooth transitions.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path

from ..styles import StyleManager, Easing


@dataclass
class OnboardingStep:
    """Individual step in the onboarding process."""
    title: str
    description: str
    content_widget: Callable[[tk.Widget, StyleManager], tk.Widget]
    validation: Optional[Callable[[], bool]] = None
    skip_enabled: bool = True


class WelcomeStep(tk.Frame):
    """Welcome step content."""
    
    def __init__(self, parent: tk.Widget, style_manager: StyleManager):
        super().__init__(parent)
        self.style_manager = style_manager
        self._create_content()
    
    def _create_content(self):
        """Create welcome content."""
        # Large welcome icon
        icon_label = tk.Label(
            self, text="🎉",
            font=('Segoe UI', 48),
            bg=self.style_manager.theme.colors.background,
            fg=self.style_manager.theme.colors.primary
        )
        icon_label.pack(pady=(20, 10))
        
        # Welcome message
        welcome_text = """Welcome to the Unsplash Image Search & GPT Description Tool!
        
This application helps you discover images and build your Spanish vocabulary through AI-powered descriptions."""
        
        message_label = tk.Label(
            self,
            text=welcome_text,
            font=('Segoe UI', 12),
            bg=self.style_manager.theme.colors.background,
            fg=self.style_manager.theme.colors.on_background,
            wraplength=400,
            justify='center'
        )
        message_label.pack(pady=10)
        
        # Features list
        features_frame = tk.Frame(self, bg=self.style_manager.theme.colors.background)
        features_frame.pack(pady=20)
        
        features = [
            "🔍 Search beautiful images from Unsplash",
            "🤖 AI-generated Spanish descriptions",
            "📚 Build vocabulary with translations",
            "📊 Track learning progress",
            "🌙 Light and dark themes"
        ]
        
        for feature in features:
            feature_label = tk.Label(
                features_frame,
                text=feature,
                font=('Segoe UI', 10),
                bg=self.style_manager.theme.colors.background,
                fg=self.style_manager.theme.colors.on_background,
                anchor='w'
            )
            feature_label.pack(anchor='w', pady=2)


class ApiSetupStep(tk.Frame):
    """API keys setup step."""
    
    def __init__(self, parent: tk.Widget, style_manager: StyleManager):
        super().__init__(parent)
        self.style_manager = style_manager
        self.api_keys = {}
        self._create_content()
    
    def _create_content(self):
        """Create API setup content."""
        # Icon
        icon_label = tk.Label(
            self, text="🔑",
            font=('Segoe UI', 36),
            bg=self.style_manager.theme.colors.background,
            fg=self.style_manager.theme.colors.primary
        )
        icon_label.pack(pady=(10, 20))
        
        # Description
        desc_text = """To get started, you'll need API keys from Unsplash and OpenAI.
Don't worry - we'll guide you through getting them!"""
        
        desc_label = tk.Label(
            self,
            text=desc_text,
            font=('Segoe UI', 11),
            bg=self.style_manager.theme.colors.background,
            fg=self.style_manager.theme.colors.on_background,
            wraplength=400,
            justify='center'
        )
        desc_label.pack(pady=(0, 30))
        
        # API key inputs
        self._create_api_input(
            "Unsplash API Key",
            "unsplash_key",
            "Get your free key from unsplash.com/developers",
            "https://unsplash.com/developers"
        )
        
        self._create_api_input(
            "OpenAI API Key", 
            "openai_key",
            "Get your key from platform.openai.com",
            "https://platform.openai.com"
        )
    
    def _create_api_input(self, title: str, key: str, description: str, help_url: str):
        """Create API key input section."""
        section_frame = self.style_manager.create_frame(self, variant='card')
        section_frame.pack(fill='x', pady=5, padx=20)
        
        # Title
        title_label = self.style_manager.create_label(
            section_frame, title, heading=4
        )
        title_label.pack(anchor='w', padx=15, pady=(15, 5))
        
        # Input frame
        input_frame = tk.Frame(section_frame)
        input_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        # Entry
        self.api_keys[key + '_var'] = tk.StringVar()
        entry = self.style_manager.create_entry(
            input_frame, 
            textvariable=self.api_keys[key + '_var'],
            show="*"
        )
        entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # Help button
        help_btn = self.style_manager.create_button(
            input_frame, "Get Key", variant='text'
        )
        help_btn.configure(
            command=lambda: self._open_help_url(help_url)
        )
        help_btn.pack(side='right')
        
        # Description
        desc_label = tk.Label(
            section_frame,
            text=description,
            font=('Segoe UI', 9),
            bg=self.style_manager.theme.colors.surface,
            fg=self.style_manager.theme.colors.outline,
            wraplength=350
        )
        desc_label.pack(anchor='w', padx=15, pady=(0, 15))
    
    def _open_help_url(self, url: str):
        """Open help URL in browser."""
        import webbrowser
        webbrowser.open(url)
    
    def get_api_keys(self) -> Dict[str, str]:
        """Get entered API keys."""
        return {
            'unsplash': self.api_keys['unsplash_key_var'].get().strip(),
            'openai': self.api_keys['openai_key_var'].get().strip()
        }
    
    def validate(self) -> bool:
        """Validate API key inputs."""
        keys = self.get_api_keys()
        return len(keys['unsplash']) > 10 and len(keys['openai']) > 20


class PreferencesStep(tk.Frame):
    """User preferences setup step."""
    
    def __init__(self, parent: tk.Widget, style_manager: StyleManager):
        super().__init__(parent)
        self.style_manager = style_manager
        self.preferences = {}
        self._create_content()
    
    def _create_content(self):
        """Create preferences content."""
        # Icon
        icon_label = tk.Label(
            self, text="⚙️",
            font=('Segoe UI', 36),
            bg=self.style_manager.theme.colors.background,
            fg=self.style_manager.theme.colors.primary
        )
        icon_label.pack(pady=(10, 20))
        
        # Description
        desc_label = tk.Label(
            self,
            text="Customize your experience with these preferences:",
            font=('Segoe UI', 11),
            bg=self.style_manager.theme.colors.background,
            fg=self.style_manager.theme.colors.on_background
        )
        desc_label.pack(pady=(0, 20))
        
        # Preferences container
        prefs_container = tk.Frame(self, bg=self.style_manager.theme.colors.background)
        prefs_container.pack(fill='both', expand=True, padx=40)
        
        # Theme preference
        self._create_preference(
            prefs_container,
            "Theme",
            "theme",
            ["Light", "Dark", "System"],
            "Light",
            "Choose your preferred color scheme"
        )
        
        # Language preference
        self._create_preference(
            prefs_container,
            "Language",
            "language", 
            ["English", "Spanish"],
            "English",
            "Interface language"
        )
        
        # Daily goal
        self._create_preference(
            prefs_container,
            "Daily Vocabulary Goal",
            "daily_goal",
            ["5 words", "10 words", "15 words", "20 words"],
            "10 words",
            "How many new words to learn per day"
        )
        
        # Auto-save
        self._create_toggle_preference(
            prefs_container,
            "Auto-save Vocabulary",
            "auto_save",
            True,
            "Automatically save words as you learn them"
        )
        
        # Animations
        self._create_toggle_preference(
            prefs_container,
            "Enable Animations",
            "animations",
            True,
            "Smooth transitions and visual effects"
        )
    
    def _create_preference(self, parent: tk.Widget, title: str, key: str,
                          options: List[str], default: str, description: str):
        """Create dropdown preference."""
        pref_frame = tk.Frame(parent, bg=self.style_manager.theme.colors.background)
        pref_frame.pack(fill='x', pady=8)
        
        # Title
        title_label = tk.Label(
            pref_frame,
            text=title,
            font=('Segoe UI', 10, 'bold'),
            bg=self.style_manager.theme.colors.background,
            fg=self.style_manager.theme.colors.on_background,
            anchor='w'
        )
        title_label.pack(anchor='w')
        
        # Option frame
        option_frame = tk.Frame(pref_frame, bg=self.style_manager.theme.colors.background)
        option_frame.pack(fill='x', pady=(5, 0))
        
        # Combobox
        var = tk.StringVar(value=default)
        self.preferences[key] = var
        
        combobox = ttk.Combobox(
            option_frame,
            textvariable=var,
            values=options,
            state='readonly',
            width=15
        )
        combobox.pack(side='left')
        
        # Description
        if description:
            desc_label = tk.Label(
                option_frame,
                text=description,
                font=('Segoe UI', 9),
                bg=self.style_manager.theme.colors.background,
                fg=self.style_manager.theme.colors.outline
            )
            desc_label.pack(side='left', padx=(10, 0))
    
    def _create_toggle_preference(self, parent: tk.Widget, title: str, key: str,
                                 default: bool, description: str):
        """Create toggle preference."""
        pref_frame = tk.Frame(parent, bg=self.style_manager.theme.colors.background)
        pref_frame.pack(fill='x', pady=8)
        
        # Variable
        var = tk.BooleanVar(value=default)
        self.preferences[key] = var
        
        # Checkbox
        checkbox = tk.Checkbutton(
            pref_frame,
            text=title,
            variable=var,
            font=('Segoe UI', 10, 'bold'),
            bg=self.style_manager.theme.colors.background,
            fg=self.style_manager.theme.colors.on_background,
            activebackground=self.style_manager.theme.colors.surface_variant,
            selectcolor=self.style_manager.theme.colors.surface
        )
        checkbox.pack(anchor='w')
        
        # Description
        if description:
            desc_label = tk.Label(
                pref_frame,
                text=description,
                font=('Segoe UI', 9),
                bg=self.style_manager.theme.colors.background,
                fg=self.style_manager.theme.colors.outline,
                wraplength=350
            )
            desc_label.pack(anchor='w', padx=(25, 0), pady=(2, 0))
    
    def get_preferences(self) -> Dict[str, Any]:
        """Get selected preferences."""
        prefs = {}
        for key, var in self.preferences.items():
            prefs[key] = var.get()
        return prefs


class CompletionStep(tk.Frame):
    """Onboarding completion step."""
    
    def __init__(self, parent: tk.Widget, style_manager: StyleManager):
        super().__init__(parent)
        self.style_manager = style_manager
        self._create_content()
    
    def _create_content(self):
        """Create completion content."""
        # Success icon
        icon_label = tk.Label(
            self, text="✅",
            font=('Segoe UI', 48),
            bg=self.style_manager.theme.colors.background,
            fg=self.style_manager.theme.colors.success
        )
        icon_label.pack(pady=(20, 10))
        
        # Completion message
        message_text = """Perfect! You're all set up and ready to start learning.
        
Here's what you can do next:"""
        
        message_label = tk.Label(
            self,
            text=message_text,
            font=('Segoe UI', 12),
            bg=self.style_manager.theme.colors.background,
            fg=self.style_manager.theme.colors.on_background,
            wraplength=400,
            justify='center'
        )
        message_label.pack(pady=(0, 20))
        
        # Next steps
        steps_frame = tk.Frame(self, bg=self.style_manager.theme.colors.background)
        steps_frame.pack()
        
        next_steps = [
            "🔍 Start by searching for images that interest you",
            "🤖 Generate AI descriptions to learn new vocabulary", 
            "📚 Click on Spanish words to add them to your collection",
            "📊 Check your progress in the vocabulary dashboard",
            "⚙️ Customize settings anytime from the menu"
        ]
        
        for i, step in enumerate(next_steps, 1):
            step_label = tk.Label(
                steps_frame,
                text=step,
                font=('Segoe UI', 10),
                bg=self.style_manager.theme.colors.background,
                fg=self.style_manager.theme.colors.on_background,
                anchor='w'
            )
            step_label.pack(anchor='w', pady=3)
        
        # Motivational message
        motivation_text = "¡Buena suerte with your Spanish learning journey!"
        
        motivation_label = tk.Label(
            self,
            text=motivation_text,
            font=('Segoe UI', 11, 'italic'),
            bg=self.style_manager.theme.colors.background,
            fg=self.style_manager.theme.colors.primary
        )
        motivation_label.pack(pady=(30, 10))


class OnboardingWizard(tk.Toplevel):
    """Main onboarding wizard window."""
    
    def __init__(self, parent: tk.Widget, style_manager: StyleManager,
                 on_complete: Callable[[Dict[str, Any]], None] = None):
        super().__init__(parent)
        
        self.style_manager = style_manager
        self.on_complete = on_complete
        self.parent_widget = parent
        
        # State
        self.current_step = 0
        self.wizard_data: Dict[str, Any] = {}
        self.steps: List[OnboardingStep] = []
        
        self._setup_window()
        self._create_steps()
        self._create_ui()
        self._show_step(0)
    
    def _setup_window(self):
        """Setup wizard window properties."""
        self.title("Welcome to Unsplash Image Search")
        self.geometry("600x500")
        self.resizable(False, False)
        self.transient(self.parent_widget)
        self.grab_set()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 300
        y = (self.winfo_screenheight() // 2) - 250
        self.geometry(f"+{x}+{y}")
        
        # Apply theme
        self.configure(bg=self.style_manager.theme.colors.background)
        
        # Prevent closing without completion
        self.protocol("WM_DELETE_WINDOW", self._on_close_attempt)
    
    def _create_steps(self):
        """Define onboarding steps."""
        self.steps = [
            OnboardingStep(
                "Welcome",
                "Let's get you started with your Spanish learning journey!",
                WelcomeStep,
                skip_enabled=True
            ),
            OnboardingStep(
                "API Setup", 
                "Configure your API keys to access images and AI descriptions",
                ApiSetupStep,
                validation=lambda: self.current_step_widget.validate(),
                skip_enabled=False
            ),
            OnboardingStep(
                "Preferences",
                "Customize your learning experience",
                PreferencesStep,
                skip_enabled=True
            ),
            OnboardingStep(
                "All Set!",
                "You're ready to start learning Spanish with images",
                CompletionStep,
                skip_enabled=False
            )
        ]
    
    def _create_ui(self):
        """Create wizard UI."""
        # Header with progress
        self._create_header()
        
        # Content area
        self.content_frame = tk.Frame(
            self,
            bg=self.style_manager.theme.colors.background
        )
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Footer with navigation buttons
        self._create_footer()
    
    def _create_header(self):
        """Create wizard header with progress indicator."""
        header_frame = tk.Frame(
            self,
            bg=self.style_manager.theme.colors.surface,
            height=80
        )
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Progress indicator
        progress_frame = tk.Frame(
            header_frame,
            bg=self.style_manager.theme.colors.surface
        )
        progress_frame.pack(fill='x', padx=30, pady=15)
        
        self.progress_dots = []
        dots_frame = tk.Frame(progress_frame, bg=self.style_manager.theme.colors.surface)
        dots_frame.pack()
        
        for i in range(len(self.steps)):
            dot = tk.Label(
                dots_frame,
                text="●",
                font=('Segoe UI', 16),
                bg=self.style_manager.theme.colors.surface,
                fg=self.style_manager.theme.colors.outline_variant
            )
            dot.pack(side='left', padx=8)
            self.progress_dots.append(dot)
        
        # Step title and description
        title_frame = tk.Frame(header_frame, bg=self.style_manager.theme.colors.surface)
        title_frame.pack(fill='x', padx=30, pady=(0, 15))
        
        self.step_title = tk.Label(
            title_frame,
            text="Welcome",
            font=('Segoe UI', 16, 'bold'),
            bg=self.style_manager.theme.colors.surface,
            fg=self.style_manager.theme.colors.on_surface
        )
        self.step_title.pack(anchor='w')
        
        self.step_description = tk.Label(
            title_frame,
            text="Let's get started!",
            font=('Segoe UI', 10),
            bg=self.style_manager.theme.colors.surface,
            fg=self.style_manager.theme.colors.outline,
            wraplength=400
        )
        self.step_description.pack(anchor='w', pady=(2, 0))
    
    def _create_footer(self):
        """Create wizard footer with navigation."""
        footer_frame = tk.Frame(
            self,
            bg=self.style_manager.theme.colors.surface,
            height=60
        )
        footer_frame.pack(fill='x', side='bottom')
        footer_frame.pack_propagate(False)
        
        button_frame = tk.Frame(footer_frame, bg=self.style_manager.theme.colors.surface)
        button_frame.pack(fill='x', padx=20, pady=10)
        
        # Back button
        self.back_btn = self.style_manager.create_button(
            button_frame, "Back", variant='text'
        )
        self.back_btn.configure(command=self._go_back, state='disabled')
        self.back_btn.pack(side='left')
        
        # Skip button
        self.skip_btn = self.style_manager.create_button(
            button_frame, "Skip", variant='text'
        )
        self.skip_btn.configure(command=self._skip_step)
        self.skip_btn.pack(side='left', padx=(10, 0))
        
        # Next/Finish button
        self.next_btn = self.style_manager.create_button(
            button_frame, "Next", variant='primary'
        )
        self.next_btn.configure(command=self._go_next)
        self.next_btn.pack(side='right')
    
    def _show_step(self, step_index: int):
        """Show specific step."""
        if not (0 <= step_index < len(self.steps)):
            return
        
        self.current_step = step_index
        step = self.steps[step_index]
        
        # Update header
        self.step_title.configure(text=step.title)
        self.step_description.configure(text=step.description)
        
        # Update progress dots
        for i, dot in enumerate(self.progress_dots):
            if i < step_index:
                dot.configure(fg=self.style_manager.theme.colors.success)
            elif i == step_index:
                dot.configure(fg=self.style_manager.theme.colors.primary)
            else:
                dot.configure(fg=self.style_manager.theme.colors.outline_variant)
        
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Create step content
        self.current_step_widget = step.content_widget(
            self.content_frame, self.style_manager
        )
        self.current_step_widget.pack(fill='both', expand=True)
        
        # Animate content in
        self.style_manager.animate_widget(
            self.current_step_widget, 'fade_in', duration=0.3
        )
        
        # Update buttons
        self.back_btn.configure(state='normal' if step_index > 0 else 'disabled')
        
        if step.skip_enabled:
            self.skip_btn.pack(side='left', padx=(10, 0))
        else:
            self.skip_btn.pack_forget()
        
        if step_index == len(self.steps) - 1:
            self.next_btn.configure(text="Finish")
        else:
            self.next_btn.configure(text="Next")
    
    def _go_back(self):
        """Go to previous step."""
        if self.current_step > 0:
            self._show_step(self.current_step - 1)
    
    def _skip_step(self):
        """Skip current step."""
        step = self.steps[self.current_step]
        if step.skip_enabled:
            self._go_next()
    
    def _go_next(self):
        """Go to next step or finish."""
        step = self.steps[self.current_step]
        
        # Validate current step
        if step.validation and not step.validation():
            self._show_validation_error()
            return
        
        # Collect data from current step
        self._collect_step_data()
        
        # Move to next step or finish
        if self.current_step < len(self.steps) - 1:
            self._show_step(self.current_step + 1)
        else:
            self._complete_wizard()
    
    def _collect_step_data(self):
        """Collect data from current step."""
        step_name = self.steps[self.current_step].title.lower().replace(' ', '_')
        
        if hasattr(self.current_step_widget, 'get_api_keys'):
            self.wizard_data.update(self.current_step_widget.get_api_keys())
        
        if hasattr(self.current_step_widget, 'get_preferences'):
            self.wizard_data['preferences'] = self.current_step_widget.get_preferences()
    
    def _show_validation_error(self):
        """Show validation error."""
        error_label = tk.Label(
            self.content_frame,
            text="Please fill in all required fields before continuing.",
            font=('Segoe UI', 10),
            bg=self.style_manager.theme.colors.background,
            fg=self.style_manager.theme.colors.error
        )
        error_label.pack(side='bottom', pady=10)
        
        # Remove error after 3 seconds
        self.after(3000, error_label.destroy)
        
        # Animate error
        self.style_manager.animate_widget(
            error_label, 'bounce', distance=5, duration=0.4
        )
    
    def _complete_wizard(self):
        """Complete onboarding wizard."""
        if self.on_complete:
            self.on_complete(self.wizard_data)
        
        # Show success animation
        self.style_manager.animate_widget(
            self.next_btn, 'pulse', scale=1.1, duration=0.3,
            complete_callback=self.destroy
        )
    
    def _on_close_attempt(self):
        """Handle close attempt."""
        if self.current_step == len(self.steps) - 1:
            # Allow closing on completion step
            self._complete_wizard()
        else:
            # Show confirmation dialog
            from tkinter import messagebox
            result = messagebox.askyesno(
                "Exit Setup",
                "Are you sure you want to exit? You'll need to complete setup later to use the application.",
                parent=self
            )
            if result:
                self.destroy()