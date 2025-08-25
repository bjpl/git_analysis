"""
Contextual hints system that provides on-demand help and guidance
Shows relevant tips based on user actions and application state
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, List, Callable
import time
from dataclasses import dataclass
from enum import Enum


class HintTrigger(Enum):
    """Different triggers for showing hints"""
    APP_START = "app_start"
    FIRST_SEARCH = "first_search"
    IMAGE_LOADED = "image_loaded"
    DESCRIPTION_GENERATED = "description_generated"
    VOCABULARY_EXTRACTED = "vocabulary_extracted"
    FIRST_WORD_ADDED = "first_word_added"
    EXPORT_AVAILABLE = "export_available"
    IDLE_TIME = "idle_time"
    ERROR_OCCURRED = "error_occurred"
    FEATURE_DISCOVERY = "feature_discovery"


@dataclass
class Hint:
    """A contextual hint definition"""
    id: str
    trigger: HintTrigger
    title: str
    content: str
    action_text: str = "Got it"
    action_callback: Optional[Callable] = None
    show_once: bool = True
    delay_seconds: float = 0
    position: str = "auto"  # "top", "bottom", "left", "right", "center", "auto"
    icon: str = "💡"
    priority: int = 1  # Higher priority hints show first


class HintTracker:
    """Tracks which hints have been shown to avoid repetition"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.shown_hints = set()
        self.dismissed_hints = set()
        self._load_hint_history()
    
    def _load_hint_history(self):
        """Load hint history from configuration"""
        try:
            data_dir = self.config_manager.get_paths()['data_dir']
            hint_file = data_dir / "hint_history.txt"
            
            if hint_file.exists():
                with open(hint_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('shown:'):
                            self.shown_hints.add(line[6:])
                        elif line.startswith('dismissed:'):
                            self.dismissed_hints.add(line[10:])
        except:
            pass  # Ignore errors, start fresh
    
    def _save_hint_history(self):
        """Save hint history to configuration"""
        try:
            data_dir = self.config_manager.get_paths()['data_dir']
            data_dir.mkdir(parents=True, exist_ok=True)
            hint_file = data_dir / "hint_history.txt"
            
            with open(hint_file, 'w', encoding='utf-8') as f:
                for hint_id in self.shown_hints:
                    f.write(f"shown:{hint_id}\\n")
                for hint_id in self.dismissed_hints:
                    f.write(f"dismissed:{hint_id}\\n")
        except:
            pass  # Ignore save errors
    
    def mark_shown(self, hint_id: str):
        """Mark a hint as shown"""
        self.shown_hints.add(hint_id)
        self._save_hint_history()
    
    def mark_dismissed(self, hint_id: str):
        """Mark a hint as dismissed by user"""
        self.dismissed_hints.add(hint_id)
        self._save_hint_history()
    
    def should_show(self, hint: Hint) -> bool:
        """Check if a hint should be shown"""
        if hint.show_once and hint.id in self.shown_hints:
            return False
        if hint.id in self.dismissed_hints:
            return False
        return True
    
    def reset_history(self):
        """Reset all hint history (for testing)"""
        self.shown_hints.clear()
        self.dismissed_hints.clear()
        self._save_hint_history()


class HintPopup:
    """Individual hint popup window"""
    
    def __init__(self, parent: tk.Widget, hint: Hint, theme_manager, 
                 on_dismiss: Callable[[str], None] = None):
        self.parent = parent
        self.hint = hint
        self.theme_manager = theme_manager
        self.on_dismiss = on_dismiss
        self.popup_window = None
        self.auto_hide_timer = None
    
    def show(self, target_widget: Optional[tk.Widget] = None):
        """Show the hint popup"""
        if self.popup_window:
            return
        
        colors = self.theme_manager.get_colors()
        
        # Create popup window
        self.popup_window = tk.Toplevel(self.parent)
        self.popup_window.wm_overrideredirect(True)  # Remove window decorations
        self.popup_window.configure(bg=colors['tooltip_bg'])
        self.popup_window.attributes('-topmost', True)
        
        # Create content frame
        content_frame = tk.Frame(
            self.popup_window,
            bg=colors['tooltip_bg'],
            relief=tk.RAISED,
            borderwidth=2
        )
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with icon and close button
        header_frame = tk.Frame(content_frame, bg=colors['info'])
        header_frame.pack(fill=tk.X)
        
        # Icon and title
        title_frame = tk.Frame(header_frame, bg=colors['info'])
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        icon_label = tk.Label(
            title_frame,
            text=self.hint.icon,
            font=('TkDefaultFont', 16),
            bg=colors['info'],
            fg=colors['select_fg']
        )
        icon_label.pack(side=tk.LEFT, padx=(10, 5), pady=5)
        
        title_label = tk.Label(
            title_frame,
            text=self.hint.title,
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['info'],
            fg=colors['select_fg']
        )
        title_label.pack(side=tk.LEFT, pady=5)
        
        # Close button
        close_button = tk.Button(
            header_frame,
            text="✕",
            font=('TkDefaultFont', 12, 'bold'),
            bg=colors['info'],
            fg=colors['select_fg'],
            relief=tk.FLAT,
            command=self.hide,
            width=3
        )
        close_button.pack(side=tk.RIGHT, padx=5, pady=2)
        
        # Content
        content_label = tk.Label(
            content_frame,
            text=self.hint.content,
            font=('TkDefaultFont', 10),
            bg=colors['tooltip_bg'],
            fg=colors['tooltip_fg'],
            wraplength=300,
            justify=tk.LEFT,
            padx=15,
            pady=10
        )
        content_label.pack(fill=tk.X)
        
        # Action buttons
        if self.hint.action_text or self.hint.action_callback:
            button_frame = tk.Frame(content_frame, bg=colors['tooltip_bg'])
            button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
            
            # Dismiss button
            dismiss_button = tk.Button(
                button_frame,
                text="Don't show again",
                font=('TkDefaultFont', 9),
                bg=colors['button_bg'],
                fg=colors['disabled_fg'],
                relief=tk.FLAT,
                command=self._dismiss_hint,
                padx=15
            )
            dismiss_button.pack(side=tk.LEFT)
            
            # Action button
            if self.hint.action_text:
                action_button = tk.Button(
                    button_frame,
                    text=self.hint.action_text,
                    font=('TkDefaultFont', 9, 'bold'),
                    bg=colors['select_bg'],
                    fg=colors['select_fg'],
                    relief=tk.FLAT,
                    command=self._handle_action,
                    padx=15
                )
                action_button.pack(side=tk.RIGHT)
        
        # Position the popup
        self._position_popup(target_widget)
        
        # Auto-hide after 30 seconds if no interaction
        self.auto_hide_timer = self.popup_window.after(30000, self.hide)
        
        # Bind escape key to close
        self.popup_window.bind('<Escape>', lambda e: self.hide())
        self.popup_window.focus_set()
    
    def _position_popup(self, target_widget: Optional[tk.Widget]):
        """Position the popup relative to target widget or screen"""
        self.popup_window.update_idletasks()
        popup_width = self.popup_window.winfo_width()
        popup_height = self.popup_window.winfo_height()
        
        if target_widget and target_widget.winfo_exists():
            # Position relative to target widget
            widget_x = target_widget.winfo_rootx()
            widget_y = target_widget.winfo_rooty()
            widget_width = target_widget.winfo_width()
            widget_height = target_widget.winfo_height()
            
            if self.hint.position == "auto":
                # Choose best position
                screen_width = self.popup_window.winfo_screenwidth()
                screen_height = self.popup_window.winfo_screenheight()
                
                # Try positioning to the right first
                if widget_x + widget_width + popup_width + 20 < screen_width:
                    x = widget_x + widget_width + 10
                    y = widget_y
                # Try below
                elif widget_y + widget_height + popup_height + 20 < screen_height:
                    x = widget_x
                    y = widget_y + widget_height + 10
                # Try above
                elif widget_y - popup_height - 10 > 0:
                    x = widget_x
                    y = widget_y - popup_height - 10
                # Default to right of widget
                else:
                    x = max(10, widget_x + widget_width + 10)
                    y = max(10, widget_y)
            else:
                # Use specified position
                margin = 10
                if self.hint.position == "right":
                    x = widget_x + widget_width + margin
                    y = widget_y
                elif self.hint.position == "left":
                    x = widget_x - popup_width - margin
                    y = widget_y
                elif self.hint.position == "bottom":
                    x = widget_x
                    y = widget_y + widget_height + margin
                elif self.hint.position == "top":
                    x = widget_x
                    y = widget_y - popup_height - margin
                else:
                    x = widget_x
                    y = widget_y
        else:
            # Center on screen
            screen_width = self.popup_window.winfo_screenwidth()
            screen_height = self.popup_window.winfo_screenheight()
            x = (screen_width - popup_width) // 2
            y = (screen_height - popup_height) // 2
        
        # Ensure popup stays on screen
        screen_width = self.popup_window.winfo_screenwidth()
        screen_height = self.popup_window.winfo_screenheight()
        
        x = max(10, min(x, screen_width - popup_width - 10))
        y = max(10, min(y, screen_height - popup_height - 10))
        
        self.popup_window.geometry(f"+{x}+{y}")
    
    def _handle_action(self):
        """Handle action button click"""
        if self.hint.action_callback:
            self.hint.action_callback()
        self.hide()
    
    def _dismiss_hint(self):
        """Dismiss hint permanently"""
        if self.on_dismiss:
            self.on_dismiss(self.hint.id)
        self.hide()
    
    def hide(self):
        """Hide the popup"""
        if self.auto_hide_timer:
            self.popup_window.after_cancel(self.auto_hide_timer)
            self.auto_hide_timer = None
        
        if self.popup_window:
            self.popup_window.destroy()
            self.popup_window = None


class ContextualHints:
    """
    Main contextual hints system that manages all hints and their triggers
    """
    
    def __init__(self, parent: tk.Tk, theme_manager, onboarding_manager):
        self.parent = parent
        self.theme_manager = theme_manager
        self.onboarding_manager = onboarding_manager
        self.config_manager = onboarding_manager.config_manager
        
        self.tracker = HintTracker(self.config_manager)
        self.active_popups = []
        self.is_active = False
        
        # App state tracking
        self.app_state = {
            'searches_performed': 0,
            'descriptions_generated': 0,
            'words_added': 0,
            'last_activity_time': time.time(),
            'errors_encountered': 0
        }
        
        # Define all hints
        self.hints = self._create_hint_definitions()
        
        # Set up idle monitoring
        self.idle_check_timer = None
    
    def _create_hint_definitions(self) -> List[Hint]:
        """Create all hint definitions"""
        return [
            # Welcome hints
            Hint(
                id="welcome_first_search",
                trigger=HintTrigger.APP_START,
                title="Ready to Start Learning?",
                content="Try searching for a topic that interests you! Popular searches include 'comida' (food), 'naturaleza' (nature), or 'ciudad' (city).",
                action_text="Start Searching",
                delay_seconds=2,
                priority=1
            ),
            
            # Search hints
            Hint(
                id="search_tips",
                trigger=HintTrigger.FIRST_SEARCH,
                title="Search Tips",
                content="Try searching in Spanish for better results! Examples: 'mercado', 'playa', 'montaña'. You can also search in English if you prefer.",
                action_text="Got it",
                position="bottom",
                priority=2
            ),
            
            # Image interaction hints
            Hint(
                id="image_zoom_tip",
                trigger=HintTrigger.IMAGE_LOADED,
                title="Explore the Image",
                content="You can zoom in/out with the controls below the image or use Ctrl+Mouse Wheel. This helps you notice details for better descriptions.",
                action_text="Thanks",
                position="right",
                delay_seconds=3,
                priority=2
            ),
            
            # Description hints
            Hint(
                id="add_notes_tip",
                trigger=HintTrigger.IMAGE_LOADED,
                title="Add Your Observations",
                content="Before generating a description, try adding your own notes about what you see. This gives the AI more context for better vocabulary.",
                action_text="I'll try that",
                position="left",
                delay_seconds=8,
                priority=1
            ),
            
            Hint(
                id="description_generated_tip",
                trigger=HintTrigger.DESCRIPTION_GENERATED,
                title="Rich Spanish Content",
                content="The AI description includes natural Spanish with varied vocabulary. Read it carefully - it's designed to be educational content for learners.",
                action_text="Understood",
                position="left",
                delay_seconds=2,
                priority=2
            ),
            
            # Vocabulary hints
            Hint(
                id="vocabulary_extraction_tip",
                trigger=HintTrigger.VOCABULARY_EXTRACTED,
                title="Click Words to Learn",
                content="The blue words below are automatically extracted vocabulary. Click any word to add it to your learning list with English translation.",
                action_text="Let me try",
                position="top",
                delay_seconds=1,
                priority=1,
                icon="📚"
            ),
            
            Hint(
                id="first_word_added_tip",
                trigger=HintTrigger.FIRST_WORD_ADDED,
                title="Great Start!",
                content="You've added your first word! Keep clicking words that interest you. Your vocabulary list appears on the right and can be exported for studying.",
                action_text="Keep going",
                position="right",
                priority=1,
                icon="🎉"
            ),
            
            # Export hints
            Hint(
                id="export_reminder",
                trigger=HintTrigger.EXPORT_AVAILABLE,
                title="Don't Forget to Export",
                content="You've collected several vocabulary words! Remember to export them to Anki, CSV, or text format for studying later.",
                action_text="Show me how",
                action_callback=lambda: self._show_export_help(),
                position="top",
                delay_seconds=5,
                priority=2,
                icon="📤"
            ),
            
            # Productivity hints
            Hint(
                id="keyboard_shortcuts",
                trigger=HintTrigger.IDLE_TIME,
                title="Keyboard Shortcuts",
                content="Speed up your workflow! Use Ctrl+N for new search, Ctrl+G to generate descriptions, and F1 for help.",
                action_text="Show all shortcuts",
                action_callback=lambda: self._show_shortcuts_help(),
                position="center",
                priority=1,
                icon="⌨️"
            ),
            
            # Feature discovery
            Hint(
                id="theme_toggle",
                trigger=HintTrigger.FEATURE_DISCOVERY,
                title="Customize Your Experience",
                content="Try the dark/light theme toggle in the toolbar, or use Ctrl+T. You can also adjust zoom and other settings.",
                action_text="Nice!",
                position="bottom",
                delay_seconds=10,
                priority=3
            ),
            
            # Error recovery hints
            Hint(
                id="api_error_help",
                trigger=HintTrigger.ERROR_OCCURRED,
                title="Having Trouble?",
                content="If you're seeing API errors, check your internet connection and API key settings. You can reconfigure them in the settings menu.",
                action_text="Check Settings",
                action_callback=lambda: self._show_settings_help(),
                position="center",
                priority=1,
                icon="⚠️"
            ),
            
            # Learning encouragement
            Hint(
                id="learning_progress",
                trigger=HintTrigger.FEATURE_DISCOVERY,
                title="You're Making Progress!",
                content="The more images you explore, the more vocabulary you'll discover. Try different topics to expand your Spanish knowledge.",
                action_text="Keep learning",
                position="center",
                delay_seconds=15,
                priority=3,
                icon="📈"
            )
        ]
    
    def activate(self):
        """Activate the contextual hints system"""
        self.is_active = True
        self._start_idle_monitoring()
        
        # Show initial welcome hint
        self._trigger_hint(HintTrigger.APP_START)
    
    def deactivate(self):
        """Deactivate the contextual hints system"""
        self.is_active = False
        self._stop_idle_monitoring()
        
        # Hide all active popups
        for popup in self.active_popups[:]:
            popup.hide()
    
    def trigger_hint(self, trigger: HintTrigger, context: Dict[str, Any] = None):
        """Trigger hints based on app events"""
        if not self.is_active:
            return
        
        self._update_app_state(trigger, context)
        self._trigger_hint(trigger, context)
    
    def _trigger_hint(self, trigger: HintTrigger, context: Dict[str, Any] = None):
        """Internal method to trigger hints"""
        matching_hints = [h for h in self.hints if h.trigger == trigger]
        
        # Sort by priority (higher first)
        matching_hints.sort(key=lambda h: h.priority, reverse=True)
        
        for hint in matching_hints:
            if self.tracker.should_show(hint):
                # Show hint after delay
                if hint.delay_seconds > 0:
                    self.parent.after(
                        int(hint.delay_seconds * 1000),
                        lambda h=hint: self._show_hint(h, context)
                    )
                else:
                    self._show_hint(hint, context)
                
                # Only show one hint per trigger usually
                break
    
    def _show_hint(self, hint: Hint, context: Dict[str, Any] = None):
        """Show a specific hint"""
        if not self.is_active:
            return
        
        # Find target widget if context provides one
        target_widget = None
        if context and 'target_widget' in context:
            target_widget = context['target_widget']
        
        # Create and show popup
        popup = HintPopup(
            self.parent,
            hint,
            self.theme_manager,
            on_dismiss=self.tracker.mark_dismissed
        )
        
        popup.show(target_widget)
        self.active_popups.append(popup)
        
        # Mark as shown
        self.tracker.mark_shown(hint.id)
        
        # Clean up popup reference when it's closed
        def cleanup():
            if popup in self.active_popups:
                self.active_popups.remove(popup)
        
        # Monitor popup for cleanup
        def check_popup():
            if not popup.popup_window or not popup.popup_window.winfo_exists():
                cleanup()
            else:
                self.parent.after(1000, check_popup)
        
        check_popup()
    
    def _update_app_state(self, trigger: HintTrigger, context: Dict[str, Any] = None):
        """Update app state based on events"""
        self.app_state['last_activity_time'] = time.time()
        
        if trigger == HintTrigger.FIRST_SEARCH:
            self.app_state['searches_performed'] += 1
        elif trigger == HintTrigger.DESCRIPTION_GENERATED:
            self.app_state['descriptions_generated'] += 1
        elif trigger == HintTrigger.FIRST_WORD_ADDED:
            self.app_state['words_added'] += 1
        elif trigger == HintTrigger.ERROR_OCCURRED:
            self.app_state['errors_encountered'] += 1
            
        # Check for export reminder
        if (self.app_state['words_added'] >= 5 and 
            self.app_state['words_added'] % 5 == 0):
            self._trigger_hint(HintTrigger.EXPORT_AVAILABLE)
    
    def _start_idle_monitoring(self):
        """Start monitoring for idle time to show productivity hints"""
        def check_idle():
            if not self.is_active:
                return
            
            idle_time = time.time() - self.app_state['last_activity_time']
            
            # Show idle hint after 60 seconds of inactivity
            if idle_time > 60:
                self._trigger_hint(HintTrigger.IDLE_TIME)
                # Reset activity time to avoid repeated hints
                self.app_state['last_activity_time'] = time.time()
            
            # Check again in 30 seconds
            self.idle_check_timer = self.parent.after(30000, check_idle)
        
        check_idle()
    
    def _stop_idle_monitoring(self):
        """Stop idle monitoring"""
        if self.idle_check_timer:
            self.parent.after_cancel(self.idle_check_timer)
            self.idle_check_timer = None
    
    def _show_export_help(self):
        """Show export help"""
        # This would integrate with the main help system
        print("Showing export help...")  # Placeholder
    
    def _show_shortcuts_help(self):
        """Show keyboard shortcuts help"""
        # This would show the main help dialog
        print("Showing shortcuts help...")  # Placeholder
    
    def _show_settings_help(self):
        """Show settings help"""
        print("Showing settings help...")  # Placeholder
    
    def reset_hints(self):
        """Reset all hint history (for testing)"""
        self.tracker.reset_history()
    
    def add_custom_hint(self, hint: Hint):
        """Add a custom hint"""
        self.hints.append(hint)
    
    def remove_hint(self, hint_id: str):
        """Remove a hint by ID"""
        self.hints = [h for h in self.hints if h.id != hint_id]
    
    def get_hint_statistics(self) -> Dict[str, Any]:
        """Get statistics about hint usage"""
        return {
            'total_hints': len(self.hints),
            'hints_shown': len(self.tracker.shown_hints),
            'hints_dismissed': len(self.tracker.dismissed_hints),
            'app_state': self.app_state.copy(),
            'active_popups': len(self.active_popups)
        }