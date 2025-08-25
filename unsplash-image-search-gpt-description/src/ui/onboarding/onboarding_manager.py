"""
Central manager for the onboarding experience
Orchestrates all onboarding components and tracks user progress
"""

import tkinter as tk
from tkinter import ttk
import json
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

from .welcome_screen import WelcomeScreen
from .tour_system import TourSystem
from .api_setup_wizard import APISetupWizard
from .sample_walkthrough import SampleWalkthrough
from .personalization import PersonalizationWizard
from .contextual_hints import ContextualHints


class OnboardingState(Enum):
    """Onboarding completion states"""
    NOT_STARTED = "not_started"
    WELCOME_COMPLETED = "welcome_completed" 
    TOUR_COMPLETED = "tour_completed"
    API_SETUP_COMPLETED = "api_setup_completed"
    SAMPLE_COMPLETED = "sample_completed"
    PERSONALIZATION_COMPLETED = "personalization_completed"
    FULLY_COMPLETED = "fully_completed"


@dataclass
class OnboardingProgress:
    """Tracks user's onboarding progress"""
    welcome_completed: bool = False
    tour_completed: bool = False
    api_setup_completed: bool = False
    sample_walkthrough_completed: bool = False
    personalization_completed: bool = False
    skip_onboarding: bool = False
    completion_date: Optional[str] = None
    user_preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.user_preferences is None:
            self.user_preferences = {}


class OnboardingManager:
    """
    Main orchestrator for the onboarding experience.
    Manages flow, state persistence, and component coordination.
    """
    
    def __init__(self, parent_window: tk.Tk, theme_manager, config_manager):
        self.parent = parent_window
        self.theme_manager = theme_manager
        self.config_manager = config_manager
        
        # State management
        self.progress = OnboardingProgress()
        self.progress_file = Path(config_manager.get_paths()['data_dir']) / "onboarding_progress.json"
        
        # Component initialization
        self.welcome_screen = None
        self.tour_system = None
        self.api_wizard = None
        self.sample_walkthrough = None
        self.personalization_wizard = None
        self.contextual_hints = None
        
        # Callbacks
        self.on_completion_callback: Optional[Callable] = None
        self.on_skip_callback: Optional[Callable] = None
        
        # Load existing progress
        self._load_progress()
        
    def _load_progress(self):
        """Load onboarding progress from disk"""
        try:
            if self.progress_file.exists():
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert dict back to dataclass
                    self.progress = OnboardingProgress(**data)
        except Exception as e:
            print(f"Error loading onboarding progress: {e}")
            self.progress = OnboardingProgress()
    
    def _save_progress(self):
        """Save onboarding progress to disk"""
        try:
            self.progress_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.progress), f, indent=2)
        except Exception as e:
            print(f"Error saving onboarding progress: {e}")
    
    def should_show_onboarding(self) -> bool:
        """Determine if onboarding should be shown"""
        if self.progress.skip_onboarding:
            return False
        
        # Check if any critical components are incomplete
        if not self.progress.api_setup_completed:
            # Always show if API setup isn't done
            return True
        
        if not self.progress.welcome_completed:
            return True
            
        return False
    
    def start_onboarding(self, completion_callback: Optional[Callable] = None, 
                        skip_callback: Optional[Callable] = None):
        """Start the onboarding process"""
        self.on_completion_callback = completion_callback
        self.on_skip_callback = skip_callback
        
        # Initialize contextual hints system (always available)
        if not self.contextual_hints:
            self.contextual_hints = ContextualHints(self.parent, self.theme_manager, self)
        
        if self.progress.skip_onboarding:
            self._handle_completion()
            return
        
        # Start with appropriate step based on progress
        if not self.progress.welcome_completed:
            self._show_welcome_screen()
        elif not self.progress.api_setup_completed:
            self._show_api_setup()
        elif not self.progress.tour_completed:
            self._show_tour()
        elif not self.progress.sample_walkthrough_completed:
            self._show_sample_walkthrough()
        elif not self.progress.personalization_completed:
            self._show_personalization()
        else:
            self._handle_completion()
    
    def _show_welcome_screen(self):
        """Show the welcome screen"""
        if not self.welcome_screen:
            self.welcome_screen = WelcomeScreen(
                self.parent, 
                self.theme_manager,
                on_continue=self._on_welcome_completed,
                on_skip=self._on_skip_onboarding
            )
        self.welcome_screen.show()
    
    def _on_welcome_completed(self):
        """Handle welcome screen completion"""
        self.progress.welcome_completed = True
        self._save_progress()
        
        if self.welcome_screen:
            self.welcome_screen.hide()
        
        # Continue to API setup
        self._show_api_setup()
    
    def _show_api_setup(self):
        """Show API setup wizard"""
        if not self.api_wizard:
            self.api_wizard = APISetupWizard(
                self.parent,
                self.theme_manager,
                self.config_manager,
                on_completion=self._on_api_setup_completed,
                on_skip=self._on_api_setup_skipped
            )
        self.api_wizard.show()
    
    def _on_api_setup_completed(self):
        """Handle API setup completion"""
        self.progress.api_setup_completed = True
        self._save_progress()
        
        if self.api_wizard:
            self.api_wizard.hide()
        
        # Continue to tour
        self._show_tour()
    
    def _on_api_setup_skipped(self):
        """Handle API setup being skipped"""
        # Still mark as completed but note it was skipped
        self.progress.api_setup_completed = True
        self._save_progress()
        
        if self.api_wizard:
            self.api_wizard.hide()
        
        # Continue to tour
        self._show_tour()
    
    def _show_tour(self):
        """Show interactive tour"""
        if not self.tour_system:
            self.tour_system = TourSystem(
                self.parent,
                self.theme_manager,
                on_completion=self._on_tour_completed,
                on_skip=self._on_tour_skipped
            )
        self.tour_system.start_tour()
    
    def _on_tour_completed(self):
        """Handle tour completion"""
        self.progress.tour_completed = True
        self._save_progress()
        
        # Continue to sample walkthrough
        self._show_sample_walkthrough()
    
    def _on_tour_skipped(self):
        """Handle tour being skipped"""
        self.progress.tour_completed = True
        self._save_progress()
        
        # Continue to sample walkthrough
        self._show_sample_walkthrough()
    
    def _show_sample_walkthrough(self):
        """Show sample image walkthrough"""
        if not self.sample_walkthrough:
            self.sample_walkthrough = SampleWalkthrough(
                self.parent,
                self.theme_manager,
                self.config_manager,
                on_completion=self._on_sample_completed,
                on_skip=self._on_sample_skipped
            )
        self.sample_walkthrough.start()
    
    def _on_sample_completed(self):
        """Handle sample walkthrough completion"""
        self.progress.sample_walkthrough_completed = True
        self._save_progress()
        
        # Continue to personalization
        self._show_personalization()
    
    def _on_sample_skipped(self):
        """Handle sample walkthrough being skipped"""
        self.progress.sample_walkthrough_completed = True
        self._save_progress()
        
        # Continue to personalization
        self._show_personalization()
    
    def _show_personalization(self):
        """Show personalization wizard"""
        if not self.personalization_wizard:
            self.personalization_wizard = PersonalizationWizard(
                self.parent,
                self.theme_manager,
                on_completion=self._on_personalization_completed,
                on_skip=self._on_personalization_skipped
            )
        self.personalization_wizard.show()
    
    def _on_personalization_completed(self, preferences: Dict[str, Any]):
        """Handle personalization completion"""
        self.progress.personalization_completed = True
        self.progress.user_preferences = preferences
        self._save_progress()
        
        if self.personalization_wizard:
            self.personalization_wizard.hide()
        
        # Complete onboarding
        self._handle_completion()
    
    def _on_personalization_skipped(self):
        """Handle personalization being skipped"""
        self.progress.personalization_completed = True
        self._save_progress()
        
        if self.personalization_wizard:
            self.personalization_wizard.hide()
        
        # Complete onboarding
        self._handle_completion()
    
    def _on_skip_onboarding(self):
        """Handle user choosing to skip entire onboarding"""
        self.progress.skip_onboarding = True
        self._save_progress()
        
        # Hide any open components
        self._cleanup_components()
        
        if self.on_skip_callback:
            self.on_skip_callback()
    
    def _handle_completion(self):
        """Handle onboarding completion"""
        import datetime
        self.progress.completion_date = datetime.datetime.now().isoformat()
        self._save_progress()
        
        # Cleanup components
        self._cleanup_components()
        
        # Activate contextual hints
        if self.contextual_hints:
            self.contextual_hints.activate()
        
        if self.on_completion_callback:
            self.on_completion_callback()
    
    def _cleanup_components(self):
        """Clean up all onboarding components"""
        if self.welcome_screen:
            self.welcome_screen.hide()
        if self.api_wizard:
            self.api_wizard.hide()
        if self.tour_system:
            self.tour_system.stop_tour()
        if self.sample_walkthrough:
            self.sample_walkthrough.stop()
        if self.personalization_wizard:
            self.personalization_wizard.hide()
    
    def reset_onboarding(self):
        """Reset onboarding progress (for testing/debugging)"""
        self.progress = OnboardingProgress()
        self._save_progress()
        self._cleanup_components()
        
        # Recreate components
        self.welcome_screen = None
        self.tour_system = None
        self.api_wizard = None
        self.sample_walkthrough = None
        self.personalization_wizard = None
    
    def get_contextual_hints(self) -> Optional[ContextualHints]:
        """Get the contextual hints system"""
        return self.contextual_hints
    
    def is_onboarding_complete(self) -> bool:
        """Check if onboarding is fully complete"""
        return (self.progress.skip_onboarding or 
                (self.progress.welcome_completed and 
                 self.progress.api_setup_completed and
                 self.progress.tour_completed and
                 self.progress.sample_walkthrough_completed and
                 self.progress.personalization_completed))
    
    def get_completion_percentage(self) -> float:
        """Get onboarding completion percentage"""
        if self.progress.skip_onboarding:
            return 100.0
        
        completed_steps = sum([
            self.progress.welcome_completed,
            self.progress.api_setup_completed,
            self.progress.tour_completed,
            self.progress.sample_walkthrough_completed,
            self.progress.personalization_completed
        ])
        
        return (completed_steps / 5) * 100.0
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences from onboarding"""
        return self.progress.user_preferences or {}