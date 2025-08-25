"""
UI Styles package for modern Material Design-inspired theming.
Provides CSS-like styling system for Tkinter applications.
"""

from .material_theme import MaterialTheme, MaterialColors
from .style_manager import StyleManager, ComponentStyle
from .animations import AnimationManager, Transition, Easing

__all__ = [
    'MaterialTheme',
    'MaterialColors', 
    'StyleManager',
    'ComponentStyle',
    'AnimationManager',
    'Transition',
    'Easing'
]