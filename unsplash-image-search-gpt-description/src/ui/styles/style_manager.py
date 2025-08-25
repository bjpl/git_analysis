"""
CSS-like style manager for Tkinter widgets.
Provides centralized styling, theme management, and responsive design.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Union, List, Callable
from dataclasses import dataclass, field
from enum import Enum
import re

from .material_theme import MaterialTheme, MaterialVariant
from .animations import AnimationManager, Easing


class ComponentType(Enum):
    """UI component types for styling."""
    BUTTON = "button"
    ENTRY = "entry"
    LABEL = "label"
    FRAME = "frame"
    TEXT = "text"
    LISTBOX = "listbox"
    CANVAS = "canvas"
    PROGRESSBAR = "progressbar"
    SEPARATOR = "separator"
    SCROLLBAR = "scrollbar"
    COMBOBOX = "combobox"
    CHECKBUTTON = "checkbutton"
    RADIOBUTTON = "radiobutton"
    SCALE = "scale"
    SPINBOX = "spinbox"


@dataclass
class ComponentStyle:
    """CSS-like style definition for UI components."""
    
    # Layout
    width: Optional[int] = None
    height: Optional[int] = None
    padding: Optional[Union[int, tuple]] = None
    margin: Optional[Union[int, tuple]] = None
    
    # Colors
    background: Optional[str] = None
    foreground: Optional[str] = None
    border_color: Optional[str] = None
    active_background: Optional[str] = None
    active_foreground: Optional[str] = None
    select_background: Optional[str] = None
    select_foreground: Optional[str] = None
    
    # Border and shape
    border_width: Optional[int] = None
    border_radius: Optional[int] = None
    relief: Optional[str] = None
    
    # Typography
    font_family: Optional[str] = None
    font_size: Optional[int] = None
    font_weight: Optional[str] = None
    text_align: Optional[str] = None
    
    # States
    hover_background: Optional[str] = None
    hover_foreground: Optional[str] = None
    disabled_foreground: Optional[str] = None
    focus_outline: Optional[str] = None
    
    # Effects
    elevation: Optional[int] = None
    opacity: Optional[float] = None
    cursor: Optional[str] = None
    
    # Animation
    transition_duration: Optional[float] = None
    transition_easing: Optional[Easing] = None
    
    # Custom properties
    custom: Dict[str, Any] = field(default_factory=dict)


class StyleSelector:
    """CSS-like selector for targeting widgets."""
    
    def __init__(self, selector_string: str):
        self.raw_selector = selector_string
        self.parse_selector(selector_string)
    
    def parse_selector(self, selector: str):
        """Parse CSS-like selector string."""
        # Simple selector parsing - can be extended
        self.element = None
        self.classes = []
        self.id = None
        self.pseudo_classes = []
        
        # Parse element type
        parts = selector.split()
        for part in parts:
            if part.startswith('#'):
                self.id = part[1:]
            elif part.startswith('.'):
                self.classes.append(part[1:])
            elif ':' in part:
                element, pseudo = part.split(':', 1)
                if element:
                    self.element = element
                self.pseudo_classes.append(pseudo)
            else:
                self.element = part
    
    def matches_widget(self, widget: tk.Widget, widget_id: str = None, 
                      widget_classes: List[str] = None, 
                      pseudo_state: str = None) -> bool:
        """Check if selector matches widget."""
        # Match element type
        if self.element and self.element != widget.winfo_class().lower():
            return False
        
        # Match ID
        if self.id and self.id != widget_id:
            return False
        
        # Match classes
        widget_classes = widget_classes or []
        if self.classes:
            for class_name in self.classes:
                if class_name not in widget_classes:
                    return False
        
        # Match pseudo-classes
        if self.pseudo_classes:
            for pseudo in self.pseudo_classes:
                if pseudo != pseudo_state:
                    return False
        
        return True


class StyleSheet:
    """Collection of styles with CSS-like selectors."""
    
    def __init__(self):
        self.rules: List[tuple] = []  # (selector, style)
        
    def add_rule(self, selector: Union[str, StyleSelector], style: ComponentStyle):
        """Add style rule with selector."""
        if isinstance(selector, str):
            selector = StyleSelector(selector)
        self.rules.append((selector, style))
    
    def get_matching_styles(self, widget: tk.Widget, widget_id: str = None,
                           widget_classes: List[str] = None,
                           pseudo_state: str = None) -> List[ComponentStyle]:
        """Get all styles that match the widget."""
        matching_styles = []
        
        for selector, style in self.rules:
            if selector.matches_widget(widget, widget_id, widget_classes, pseudo_state):
                matching_styles.append(style)
        
        return matching_styles
    
    def merge_styles(self, styles: List[ComponentStyle]) -> ComponentStyle:
        """Merge multiple styles with later styles taking precedence."""
        if not styles:
            return ComponentStyle()
        
        merged = ComponentStyle()
        
        for style in styles:
            for field_name, field_value in style.__dict__.items():
                if field_value is not None:
                    if field_name == 'custom':
                        # Merge custom properties
                        merged.custom.update(field_value)
                    else:
                        setattr(merged, field_name, field_value)
        
        return merged


class ResponsiveBreakpoint:
    """Responsive design breakpoint."""
    
    def __init__(self, min_width: int = 0, max_width: int = float('inf')):
        self.min_width = min_width
        self.max_width = max_width
    
    def matches(self, window_width: int) -> bool:
        """Check if current window width matches breakpoint."""
        return self.min_width <= window_width <= self.max_width


class StyleManager:
    """Main style manager for the application."""
    
    def __init__(self, root: tk.Tk, theme: MaterialTheme = None):
        self.root = root
        self.theme = theme or MaterialTheme()
        self.animation_manager = AnimationManager(root)
        
        # Style storage
        self.stylesheet = StyleSheet()
        self.widget_registry: Dict[str, tk.Widget] = {}
        self.widget_classes: Dict[tk.Widget, List[str]] = {}
        self.widget_states: Dict[tk.Widget, str] = {}
        
        # Responsive design
        self.breakpoints: Dict[str, ResponsiveBreakpoint] = {}
        self.current_breakpoint: Optional[str] = None
        
        # Initialize default styles
        self._create_default_styles()
        
        # Setup window resize handling for responsive design
        self.root.bind('<Configure>', self._on_window_resize)
    
    def _create_default_styles(self):
        """Create default Material Design styles."""
        # Button styles
        self.stylesheet.add_rule(
            'button',
            ComponentStyle(
                background=self.theme.colors.surface_variant,
                foreground=self.theme.colors.on_surface,
                border_color=self.theme.colors.outline,
                border_width=1,
                border_radius=self.theme.radius.sm,
                padding=self.theme.spacing.md,
                font_family="Segoe UI",
                font_size=14,
                cursor="hand2",
                hover_background=self.theme.colors.primary,
                hover_foreground=self.theme.colors.on_primary,
                active_background=self.theme.colors.primary_variant,
                transition_duration=0.2,
                transition_easing=Easing.EASE_OUT
            )
        )
        
        # Primary button variant
        self.stylesheet.add_rule(
            'button.primary',
            ComponentStyle(
                background=self.theme.colors.primary,
                foreground=self.theme.colors.on_primary,
                elevation=2,
                hover_background=self.theme.colors.primary_variant
            )
        )
        
        # Secondary button variant  
        self.stylesheet.add_rule(
            'button.secondary',
            ComponentStyle(
                background=self.theme.colors.secondary,
                foreground=self.theme.colors.on_secondary,
                hover_background=self.theme.colors.secondary_variant
            )
        )
        
        # Text button variant
        self.stylesheet.add_rule(
            'button.text',
            ComponentStyle(
                background='transparent',
                border_width=0,
                hover_background=self.theme.colors.primary + '20'  # 20% opacity
            )
        )
        
        # Entry styles
        self.stylesheet.add_rule(
            'entry',
            ComponentStyle(
                background=self.theme.colors.surface,
                foreground=self.theme.colors.on_surface,
                border_color=self.theme.colors.outline,
                border_width=1,
                border_radius=self.theme.radius.xs,
                padding=self.theme.spacing.sm,
                font_family="Segoe UI",
                font_size=14,
                focus_outline=self.theme.colors.primary,
                select_background=self.theme.colors.primary,
                select_foreground=self.theme.colors.on_primary
            )
        )
        
        # Label styles
        self.stylesheet.add_rule(
            'label',
            ComponentStyle(
                background=self.theme.colors.background,
                foreground=self.theme.colors.on_background,
                font_family="Segoe UI",
                font_size=14
            )
        )
        
        # Heading styles
        for level in [1, 2, 3, 4, 5, 6]:
            size = max(12, 24 - level * 2)
            weight = "bold" if level <= 3 else "normal"
            self.stylesheet.add_rule(
                f'label.h{level}',
                ComponentStyle(
                    font_size=size,
                    font_weight=weight,
                    margin=(self.theme.spacing.md, 0)
                )
            )
        
        # Frame styles
        self.stylesheet.add_rule(
            'frame',
            ComponentStyle(
                background=self.theme.colors.background,
                border_color=self.theme.colors.outline_variant,
                border_width=0
            )
        )
        
        # Card frame style
        self.stylesheet.add_rule(
            'frame.card',
            ComponentStyle(
                background=self.theme.colors.surface,
                border_color=self.theme.colors.outline_variant,
                border_width=1,
                border_radius=self.theme.radius.md,
                padding=self.theme.spacing.lg,
                elevation=1
            )
        )
        
        # Text area styles
        self.stylesheet.add_rule(
            'text',
            ComponentStyle(
                background=self.theme.colors.surface,
                foreground=self.theme.colors.on_surface,
                border_color=self.theme.colors.outline,
                border_width=1,
                font_family="Segoe UI",
                font_size=14,
                select_background=self.theme.colors.primary,
                select_foreground=self.theme.colors.on_primary
            )
        )
        
        # Listbox styles
        self.stylesheet.add_rule(
            'listbox',
            ComponentStyle(
                background=self.theme.colors.surface,
                foreground=self.theme.colors.on_surface,
                border_color=self.theme.colors.outline,
                border_width=1,
                font_family="Segoe UI",
                font_size=14,
                select_background=self.theme.colors.primary,
                select_foreground=self.theme.colors.on_primary
            )
        )
    
    def set_theme(self, theme: MaterialTheme):
        """Update theme and refresh all styles."""
        self.theme = theme
        self.stylesheet = StyleSheet()
        self._create_default_styles()
        self._refresh_all_widgets()
    
    def add_breakpoint(self, name: str, min_width: int = 0, max_width: int = float('inf')):
        """Add responsive breakpoint."""
        self.breakpoints[name] = ResponsiveBreakpoint(min_width, max_width)
    
    def _on_window_resize(self, event):
        """Handle window resize for responsive design."""
        if event.widget != self.root:
            return
        
        window_width = event.width
        new_breakpoint = None
        
        for name, breakpoint in self.breakpoints.items():
            if breakpoint.matches(window_width):
                new_breakpoint = name
                break
        
        if new_breakpoint != self.current_breakpoint:
            self.current_breakpoint = new_breakpoint
            self._on_breakpoint_change(new_breakpoint)
    
    def _on_breakpoint_change(self, breakpoint_name: str):
        """Handle breakpoint change."""
        # Refresh responsive styles
        self._refresh_all_widgets()
    
    def register_widget(self, widget: tk.Widget, widget_id: str = None, 
                       classes: List[str] = None):
        """Register widget for styling."""
        if widget_id:
            self.widget_registry[widget_id] = widget
        
        if classes:
            self.widget_classes[widget] = classes
        
        # Apply initial styles
        self.apply_styles(widget, widget_id, classes)
    
    def add_class(self, widget: tk.Widget, class_name: str):
        """Add CSS class to widget."""
        if widget not in self.widget_classes:
            self.widget_classes[widget] = []
        
        if class_name not in self.widget_classes[widget]:
            self.widget_classes[widget].append(class_name)
            
            # Re-apply styles
            widget_id = self._get_widget_id(widget)
            self.apply_styles(widget, widget_id, self.widget_classes[widget])
    
    def remove_class(self, widget: tk.Widget, class_name: str):
        """Remove CSS class from widget."""
        if widget in self.widget_classes and class_name in self.widget_classes[widget]:
            self.widget_classes[widget].remove(class_name)
            
            # Re-apply styles
            widget_id = self._get_widget_id(widget)
            self.apply_styles(widget, widget_id, self.widget_classes[widget])
    
    def set_state(self, widget: tk.Widget, state: str):
        """Set pseudo-state for widget (hover, active, etc.)."""
        self.widget_states[widget] = state
        
        widget_id = self._get_widget_id(widget)
        classes = self.widget_classes.get(widget, [])
        self.apply_styles(widget, widget_id, classes, state)
    
    def clear_state(self, widget: tk.Widget):
        """Clear pseudo-state for widget."""
        if widget in self.widget_states:
            del self.widget_states[widget]
        
        widget_id = self._get_widget_id(widget)
        classes = self.widget_classes.get(widget, [])
        self.apply_styles(widget, widget_id, classes)
    
    def _get_widget_id(self, widget: tk.Widget) -> Optional[str]:
        """Get widget ID if registered."""
        for widget_id, registered_widget in self.widget_registry.items():
            if registered_widget == widget:
                return widget_id
        return None
    
    def apply_styles(self, widget: tk.Widget, widget_id: str = None,
                    classes: List[str] = None, pseudo_state: str = None):
        """Apply styles to widget based on current stylesheet."""
        # Get matching styles
        matching_styles = self.stylesheet.get_matching_styles(
            widget, widget_id, classes, pseudo_state
        )
        
        if not matching_styles:
            return
        
        # Merge styles
        final_style = self.stylesheet.merge_styles(matching_styles)
        
        # Apply style to widget
        self._apply_style_to_widget(widget, final_style)
    
    def _apply_style_to_widget(self, widget: tk.Widget, style: ComponentStyle):
        """Apply ComponentStyle to actual widget."""
        try:
            config_dict = {}
            
            # Basic properties
            if style.background:
                config_dict['bg'] = style.background
            if style.foreground:
                config_dict['fg'] = style.foreground
            if style.border_width is not None:
                config_dict['borderwidth'] = style.border_width
            if style.relief:
                config_dict['relief'] = style.relief
            if style.cursor:
                config_dict['cursor'] = style.cursor
            
            # Handle font
            if any([style.font_family, style.font_size, style.font_weight]):
                font_family = style.font_family or "TkDefaultFont"
                font_size = style.font_size or 10
                font_weight = style.font_weight or "normal"
                config_dict['font'] = (font_family, font_size, font_weight)
            
            # Special handling for different widget types
            widget_class = widget.winfo_class()
            
            if widget_class in ['Button', 'Label', 'Entry', 'Text', 'Listbox']:
                # Standard Tk widgets
                if style.active_background:
                    config_dict['activebackground'] = style.active_background
                if style.active_foreground:
                    config_dict['activeforeground'] = style.active_foreground
                if style.select_background:
                    config_dict['selectbackground'] = style.select_background
                if style.select_foreground:
                    config_dict['selectforeground'] = style.select_foreground
                if style.disabled_foreground:
                    config_dict['disabledforeground'] = style.disabled_foreground
            
            elif widget_class.startswith('T'):
                # TTK widgets - use different property names
                if style.background:
                    config_dict['background'] = style.background
                if style.foreground:
                    config_dict['foreground'] = style.foreground
            
            # Apply size constraints
            if style.width is not None:
                config_dict['width'] = style.width
            if style.height is not None:
                config_dict['height'] = style.height
            
            # Apply configuration
            if config_dict:
                widget.configure(**config_dict)
            
            # Handle padding and margin (requires layout manager cooperation)
            if style.padding is not None:
                self._apply_padding(widget, style.padding)
            
            # Setup hover effects
            if style.hover_background or style.hover_foreground:
                self._setup_hover_effects(widget, style)
            
            # Apply elevation effects
            if style.elevation is not None:
                self._apply_elevation(widget, style.elevation)
            
        except tk.TclError as e:
            print(f"Error applying style to {widget.winfo_class()}: {e}")
    
    def _apply_padding(self, widget: tk.Widget, padding: Union[int, tuple]):
        """Apply padding to widget (if supported by layout manager)."""
        # Note: Padding application depends on the layout manager
        # This is a placeholder for padding logic
        pass
    
    def _setup_hover_effects(self, widget: tk.Widget, style: ComponentStyle):
        """Setup hover enter/leave effects."""
        original_bg = widget.cget('bg') if hasattr(widget, 'cget') else None
        original_fg = widget.cget('fg') if hasattr(widget, 'cget') else None
        
        def on_enter(event=None):
            try:
                config = {}
                if style.hover_background:
                    config['bg'] = style.hover_background
                if style.hover_foreground:
                    config['fg'] = style.hover_foreground
                if config:
                    widget.configure(**config)
                    
                # Animate if transition specified
                if style.transition_duration:
                    # Use animation manager for smooth transitions
                    pass
                    
            except tk.TclError:
                pass
        
        def on_leave(event=None):
            try:
                config = {}
                if original_bg:
                    config['bg'] = original_bg
                if original_fg:
                    config['fg'] = original_fg
                if config:
                    widget.configure(**config)
            except tk.TclError:
                pass
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def _apply_elevation(self, widget: tk.Widget, level: int):
        """Apply elevation effect (shadow simulation for Tkinter)."""
        elevation_style = self.theme.get_elevation_style(level)
        
        # Since Tkinter doesn't support real shadows, we'll simulate with borders
        if level > 0:
            try:
                widget.configure(
                    relief='raised',
                    borderwidth=max(1, level),
                    highlightthickness=1,
                    highlightcolor=self.theme.colors.outline_variant
                )
            except tk.TclError:
                pass
    
    def _refresh_all_widgets(self):
        """Refresh styles for all registered widgets."""
        # Refresh registered widgets
        for widget_id, widget in self.widget_registry.items():
            try:
                classes = self.widget_classes.get(widget, [])
                pseudo_state = self.widget_states.get(widget)
                self.apply_styles(widget, widget_id, classes, pseudo_state)
            except tk.TclError:
                # Widget may have been destroyed
                continue
        
        # Refresh widgets with classes but no ID
        for widget, classes in list(self.widget_classes.items()):
            try:
                if widget not in self.widget_registry.values():
                    pseudo_state = self.widget_states.get(widget)
                    self.apply_styles(widget, None, classes, pseudo_state)
            except tk.TclError:
                # Widget may have been destroyed
                del self.widget_classes[widget]
    
    # Convenience methods for common operations
    def create_button(self, parent: tk.Widget, text: str = "", 
                     variant: str = "default", **kwargs) -> tk.Button:
        """Create styled button."""
        button = tk.Button(parent, text=text, **kwargs)
        
        classes = ["button"]
        if variant != "default":
            classes.append(variant)
        
        self.register_widget(button, classes=classes)
        return button
    
    def create_entry(self, parent: tk.Widget, **kwargs) -> tk.Entry:
        """Create styled entry."""
        entry = tk.Entry(parent, **kwargs)
        self.register_widget(entry, classes=["entry"])
        return entry
    
    def create_label(self, parent: tk.Widget, text: str = "", 
                    heading: int = None, **kwargs) -> tk.Label:
        """Create styled label."""
        label = tk.Label(parent, text=text, **kwargs)
        
        classes = ["label"]
        if heading:
            classes.append(f"h{heading}")
        
        self.register_widget(label, classes=classes)
        return label
    
    def create_frame(self, parent: tk.Widget, variant: str = "default", 
                    **kwargs) -> tk.Frame:
        """Create styled frame."""
        frame = tk.Frame(parent, **kwargs)
        
        classes = ["frame"]
        if variant != "default":
            classes.append(variant)
        
        self.register_widget(frame, classes=classes)
        return frame
    
    def create_card(self, parent: tk.Widget, **kwargs) -> tk.Frame:
        """Create Material Design card."""
        return self.create_frame(parent, variant="card", **kwargs)
    
    # Animation shortcuts
    def animate_widget(self, widget: tk.Widget, animation_type: str, **kwargs):
        """Animate widget with predefined animation."""
        animation_map = {
            'fade_in': self.animation_manager.fade_in,
            'fade_out': self.animation_manager.fade_out,
            'slide_in': self.animation_manager.slide_in,
            'slide_out': self.animation_manager.slide_out,
            'scale_in': self.animation_manager.scale_in,
            'bounce': self.animation_manager.bounce,
            'pulse': self.animation_manager.pulse
        }
        
        if animation_type in animation_map:
            return animation_map[animation_type](widget, **kwargs)
        
    def create_loading_indicator(self, parent: tk.Widget) -> tk.Label:
        """Create animated loading indicator."""
        indicator = tk.Label(parent, text="⟳", font=("Segoe UI", 16))
        self.register_widget(indicator, classes=["label"])
        
        # Start rotation animation
        self.animation_manager.create_loading_animation(indicator)
        
        return indicator