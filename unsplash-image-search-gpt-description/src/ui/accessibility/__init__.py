"""
Accessibility module for Tkinter applications.
Provides comprehensive accessibility features including screen reader support,
keyboard navigation, high contrast themes, and WCAG 2.1 AA compliance.
"""

from .core import AccessibilityManager, AccessibilityWidget
from .screen_reader import ScreenReaderSupport
from .keyboard_nav import KeyboardNavigation
from .themes import HighContrastThemes, ColorBlindThemes
from .sound_cues import SoundManager
from .focus_manager import FocusManager

__all__ = [
    'AccessibilityManager',
    'AccessibilityWidget', 
    'ScreenReaderSupport',
    'KeyboardNavigation',
    'HighContrastThemes',
    'ColorBlindThemes',
    'SoundManager',
    'FocusManager'
]

# Version info
__version__ = '1.0.0'
__author__ = 'Accessibility Expert'
__description__ = 'Comprehensive accessibility features for Tkinter applications'