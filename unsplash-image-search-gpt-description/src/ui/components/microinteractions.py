"""
Micro-interaction components with smooth animations and Material Design feedback.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Any
import math
import time

from ..styles import StyleManager, Easing


class HoverButton(tk.Button):
    """Button with smooth hover animations and Material Design ripple effect."""
    
    def __init__(self, parent: tk.Widget, text: str = "", 
                 style_manager: StyleManager = None,
                 on_click: Callable = None,
                 variant: str = 'default',
                 **kwargs):
        super().__init__(parent, text=text, **kwargs)
        
        self.style_manager = style_manager
        self.on_click = on_click
        self.variant = variant
        
        # State tracking
        self.is_hovered = False
        self.is_pressed = False
        self.original_bg = None
        self.hover_bg = None
        self.press_bg = None
        
        # Animation state
        self.hover_animation_id = None
        self.press_animation_id = None
        
        self._setup_colors()
        self._setup_bindings()
        
        if self.style_manager:
            classes = ['button', 'hover-button']
            if variant != 'default':
                classes.append(variant)
            self.style_manager.register_widget(self, classes=classes)
    
    def _setup_colors(self):
        """Setup button colors based on variant and theme."""
        if not self.style_manager:
            return
        
        theme = self.style_manager.theme
        
        if self.variant == 'primary':
            self.original_bg = theme.colors.primary
            self.hover_bg = theme.colors.primary_variant
            self.press_bg = self._darken_color(theme.colors.primary_variant, 0.1)
            text_color = theme.colors.on_primary
        elif self.variant == 'secondary':
            self.original_bg = theme.colors.secondary
            self.hover_bg = theme.colors.secondary_variant  
            self.press_bg = self._darken_color(theme.colors.secondary_variant, 0.1)
            text_color = theme.colors.on_secondary
        else:  # default
            self.original_bg = theme.colors.surface_variant
            self.hover_bg = theme.colors.outline_variant
            self.press_bg = theme.colors.outline
            text_color = theme.colors.on_surface
        
        # Apply initial styling
        self.configure(
            bg=self.original_bg,
            fg=text_color,
            activebackground=self.press_bg,
            relief='flat',
            borderwidth=0,
            font=('Segoe UI', 10),
            cursor='hand2',
            padx=16,
            pady=8
        )
    
    def _darken_color(self, hex_color: str, factor: float) -> str:
        """Darken a hex color by given factor."""
        # Simple darkening - multiply RGB values by (1-factor)
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))  
        b = int(b * (1 - factor))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _setup_bindings(self):
        """Setup event bindings for interactions."""
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
        
        # Command binding
        if self.on_click:
            self.configure(command=self.on_click)
    
    def _on_enter(self, event):
        """Handle mouse enter."""
        if not self.is_hovered:
            self.is_hovered = True
            self._animate_hover_in()
    
    def _on_leave(self, event):
        """Handle mouse leave.""" 
        if self.is_hovered:
            self.is_hovered = False
            self._animate_hover_out()
    
    def _on_press(self, event):
        """Handle button press."""
        self.is_pressed = True
        self._animate_press()
        
        # Create ripple effect
        self._create_ripple_effect(event.x, event.y)
    
    def _on_release(self, event):
        """Handle button release."""
        self.is_pressed = False
        self._animate_release()
    
    def _animate_hover_in(self):
        """Animate hover enter effect."""
        if self.style_manager:
            self.style_manager.animation_manager.animate_property(
                self, 'bg', self.original_bg, self.hover_bg,
                duration=0.2, easing=Easing.EASE_OUT
            )
            
            # Subtle scale effect
            self.style_manager.animate_widget(
                self, 'pulse', scale=1.02, duration=0.2
            )
    
    def _animate_hover_out(self):
        """Animate hover leave effect."""
        if self.style_manager:
            self.style_manager.animation_manager.animate_property(
                self, 'bg', self.hover_bg, self.original_bg,
                duration=0.3, easing=Easing.EASE_OUT
            )
    
    def _animate_press(self):
        """Animate button press."""
        if self.style_manager:
            # Quick scale down
            self.style_manager.animate_widget(
                self, 'pulse', scale=0.98, duration=0.1
            )
    
    def _animate_release(self):
        """Animate button release.""" 
        if self.style_manager:
            # Scale back to normal
            self.style_manager.animate_widget(
                self, 'pulse', scale=1.02 if self.is_hovered else 1.0, duration=0.2
            )
    
    def _create_ripple_effect(self, x: int, y: int):
        """Create ripple effect at click position."""
        # Create ripple overlay
        ripple = tk.Label(
            self,
            bg=self.style_manager.theme.colors.surface if self.style_manager else "#ffffff",
            width=2,
            height=1
        )
        ripple.place(x=x-10, y=y-5, width=20, height=10)
        
        # Animate ripple expansion and fade
        if self.style_manager:
            self.style_manager.animate_widget(
                ripple, 'scale_in', duration=0.3,
                complete_callback=lambda: ripple.destroy()
            )


class AnimatedButton(tk.Frame):
    """Button with advanced animations and state management."""
    
    def __init__(self, parent: tk.Widget, text: str = "",
                 style_manager: StyleManager = None,
                 on_click: Callable = None,
                 icon: str = "",
                 loading: bool = False,
                 **kwargs):
        super().__init__(parent, **kwargs)
        
        self.style_manager = style_manager
        self.on_click = on_click
        self.text = text
        self.icon = icon
        self.loading = loading
        
        self._create_button()
        
        if self.style_manager:
            self.style_manager.register_widget(self, classes=['frame', 'animated-button'])
    
    def _create_button(self):
        """Create button components."""
        if self.style_manager:
            self.configure(bg=self.style_manager.theme.colors.primary)
        
        # Main button area
        self.button_area = tk.Frame(
            self,
            cursor='hand2',
            padx=16,
            pady=10
        )
        self.button_area.pack(fill='both', expand=True)
        
        if self.style_manager:
            self.button_area.configure(bg=self.style_manager.theme.colors.primary)
        
        # Content frame for icon and text
        content_frame = tk.Frame(self.button_area)
        content_frame.pack()
        
        if self.style_manager:
            content_frame.configure(bg=self.style_manager.theme.colors.primary)
        
        # Icon label (if provided)
        if self.icon:
            self.icon_label = tk.Label(
                content_frame,
                text=self.icon,
                font=('Segoe UI', 14),
                bg=self.style_manager.theme.colors.primary if self.style_manager else None,
                fg=self.style_manager.theme.colors.on_primary if self.style_manager else None
            )
            self.icon_label.pack(side='left', padx=(0, 8) if self.text else 0)
        
        # Text label
        if self.text:
            self.text_label = tk.Label(
                content_frame,
                text=self.text,
                font=('Segoe UI', 10, 'bold'),
                bg=self.style_manager.theme.colors.primary if self.style_manager else None,
                fg=self.style_manager.theme.colors.on_primary if self.style_manager else None
            )
            self.text_label.pack(side='left')
        
        # Loading spinner (hidden by default)
        self.loading_frame = tk.Frame(content_frame)
        if self.style_manager:
            self.loading_frame.configure(bg=self.style_manager.theme.colors.primary)
        
        if self.loading:
            self.show_loading()
        
        # Bind events
        self._setup_bindings()
    
    def _setup_bindings(self):
        """Setup interaction bindings."""
        widgets_to_bind = [self, self.button_area, self.loading_frame]
        
        if hasattr(self, 'icon_label'):
            widgets_to_bind.append(self.icon_label)
        if hasattr(self, 'text_label'):
            widgets_to_bind.append(self.text_label)
        
        for widget in widgets_to_bind:
            widget.bind('<Button-1>', self._on_click)
            widget.bind('<Enter>', self._on_enter)
            widget.bind('<Leave>', self._on_leave)
    
    def _on_click(self, event):
        """Handle button click."""
        if self.loading:
            return  # Ignore clicks while loading
        
        # Animate click
        if self.style_manager:
            self.style_manager.animate_widget(
                self, 'pulse', scale=0.95, duration=0.1,
                complete_callback=lambda: self.style_manager.animate_widget(
                    self, 'pulse', scale=1.0, duration=0.1
                )
            )
        
        # Call callback
        if self.on_click:
            self.on_click()
    
    def _on_enter(self, event):
        """Handle hover enter."""
        if self.loading:
            return
        
        if self.style_manager:
            # Subtle lift effect
            self.style_manager.animate_widget(
                self, 'pulse', scale=1.02, duration=0.2
            )
    
    def _on_leave(self, event):
        """Handle hover leave."""
        if self.loading:
            return
        
        if self.style_manager:
            self.style_manager.animate_widget(
                self, 'pulse', scale=1.0, duration=0.2
            )
    
    def show_loading(self):
        """Show loading state."""
        self.loading = True
        
        # Hide normal content
        if hasattr(self, 'icon_label'):
            self.icon_label.pack_forget()
        if hasattr(self, 'text_label'):
            self.text_label.pack_forget()
        
        # Show loading content
        self.loading_frame.pack()
        
        # Create spinner
        from .loading_states import LoadingSpinner
        self.spinner = LoadingSpinner(
            self.loading_frame, size=20, style_manager=self.style_manager
        )
        self.spinner.pack(side='left', padx=(0, 8))
        self.spinner.start_spinning()
        
        # Loading text
        loading_text = tk.Label(
            self.loading_frame,
            text="Loading...",
            font=('Segoe UI', 10),
            bg=self.style_manager.theme.colors.primary if self.style_manager else None,
            fg=self.style_manager.theme.colors.on_primary if self.style_manager else None
        )
        loading_text.pack(side='left')
    
    def hide_loading(self):
        """Hide loading state."""
        self.loading = False
        
        # Stop and remove spinner
        if hasattr(self, 'spinner'):
            self.spinner.stop_spinning()
            self.spinner.destroy()
        
        # Hide loading content
        self.loading_frame.pack_forget()
        
        # Show normal content
        if hasattr(self, 'icon_label'):
            self.icon_label.pack(side='left', padx=(0, 8) if self.text else 0)
        if hasattr(self, 'text_label'):
            self.text_label.pack(side='left')
    
    def set_text(self, text: str):
        """Update button text."""
        self.text = text
        if hasattr(self, 'text_label'):
            self.text_label.configure(text=text)
    
    def set_icon(self, icon: str):
        """Update button icon."""
        self.icon = icon
        if hasattr(self, 'icon_label'):
            self.icon_label.configure(text=icon)


class FloatingActionButton(tk.Frame):
    """Material Design floating action button with shadow and animations."""
    
    def __init__(self, parent: tk.Widget, icon: str = "+",
                 style_manager: StyleManager = None,
                 on_click: Callable = None,
                 size: int = 56,
                 **kwargs):
        super().__init__(parent, **kwargs)
        
        self.style_manager = style_manager
        self.on_click = on_click
        self.icon = icon
        self.size = size
        
        # State
        self.is_hovered = False
        self.is_extended = False
        self.extended_text = ""
        
        self._create_fab()
        
        if self.style_manager:
            self.style_manager.register_widget(self, classes=['frame', 'fab'])
    
    def _create_fab(self):
        """Create FAB components."""
        # Configure frame
        self.configure(
            width=self.size,
            height=self.size,
            bg=self.style_manager.theme.colors.secondary if self.style_manager else "#03dac6",
            relief='raised',
            borderwidth=0,
            cursor='hand2'
        )
        self.pack_propagate(False)
        
        # Create shadow effect with multiple frames
        self._create_shadow_effect()
        
        # Icon label
        self.icon_label = tk.Label(
            self,
            text=self.icon,
            font=('Segoe UI', 20),
            bg=self.style_manager.theme.colors.secondary if self.style_manager else "#03dac6",
            fg=self.style_manager.theme.colors.on_secondary if self.style_manager else "#000000"
        )
        self.icon_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Extended text label (hidden by default)
        self.text_label = tk.Label(
            self,
            text="",
            font=('Segoe UI', 10, 'bold'),
            bg=self.style_manager.theme.colors.secondary if self.style_manager else "#03dac6",
            fg=self.style_manager.theme.colors.on_secondary if self.style_manager else "#000000"
        )
        
        self._setup_bindings()
    
    def _create_shadow_effect(self):
        """Create layered shadow effect."""
        # Create shadow layers behind FAB
        shadow_colors = ["#00000020", "#00000015", "#00000010"]
        shadow_offsets = [(2, 2), (4, 4), (6, 6)]
        
        for i, (color, (x_offset, y_offset)) in enumerate(zip(shadow_colors, shadow_offsets)):
            shadow = tk.Frame(
                self.master,
                width=self.size + i * 2,
                height=self.size + i * 2,
                bg=color,
                relief='flat'
            )
            shadow.place(
                x=self.winfo_x() + x_offset,
                y=self.winfo_y() + y_offset
            )
            shadow.lower(self)  # Place behind FAB
    
    def _setup_bindings(self):
        """Setup interaction bindings."""
        widgets_to_bind = [self, self.icon_label, self.text_label]
        
        for widget in widgets_to_bind:
            widget.bind('<Button-1>', self._on_click)
            widget.bind('<Enter>', self._on_enter)
            widget.bind('<Leave>', self._on_leave)
    
    def _on_click(self, event):
        """Handle FAB click."""
        if self.style_manager:
            # Animated press effect
            self.style_manager.animate_widget(
                self, 'pulse', scale=0.9, duration=0.1,
                complete_callback=lambda: self.style_manager.animate_widget(
                    self, 'pulse', scale=1.1 if self.is_hovered else 1.0, duration=0.2
                )
            )
        
        if self.on_click:
            self.on_click()
    
    def _on_enter(self, event):
        """Handle hover enter."""
        self.is_hovered = True
        
        if self.style_manager:
            # Scale up slightly
            self.style_manager.animate_widget(
                self, 'pulse', scale=1.1, duration=0.2
            )
        
        # Show extended state if configured
        if self.extended_text and not self.is_extended:
            self.extend(self.extended_text)
    
    def _on_leave(self, event):
        """Handle hover leave."""
        self.is_hovered = False
        
        if self.style_manager:
            # Scale back to normal
            self.style_manager.animate_widget(
                self, 'pulse', scale=1.0, duration=0.2
            )
        
        # Hide extended state
        if self.is_extended:
            self.contract()
    
    def extend(self, text: str):
        """Extend FAB with text."""
        if self.is_extended:
            return
        
        self.is_extended = True
        original_width = self.size
        
        # Calculate new width based on text
        self.text_label.configure(text=text)
        self.update_idletasks()
        text_width = self.text_label.winfo_reqwidth()
        new_width = original_width + text_width + 20
        
        # Animate width expansion
        if self.style_manager:
            self.style_manager.animation_manager.animate_property(
                self, 'width', original_width, new_width,
                duration=0.3, easing=Easing.EASE_OUT_CUBIC
            )
        
        # Show text with delay
        self.after(150, self._show_extended_text)
    
    def contract(self):
        """Contract FAB to icon only."""
        if not self.is_extended:
            return
        
        self.is_extended = False
        
        # Hide text first
        self.text_label.place_forget()
        
        # Animate width contraction
        if self.style_manager:
            self.style_manager.animation_manager.animate_property(
                self, 'width', self.winfo_width(), self.size,
                duration=0.2, easing=Easing.EASE_IN_CUBIC
            )
    
    def _show_extended_text(self):
        """Show extended text with fade in."""
        # Position text to the right of icon
        self.text_label.place(x=self.size, rely=0.5, anchor='w')
        
        if self.style_manager:
            self.style_manager.animate_widget(
                self.text_label, 'fade_in', duration=0.2
            )
    
    def set_extended_text(self, text: str):
        """Set text for extended state."""
        self.extended_text = text
    
    def set_icon(self, icon: str):
        """Update FAB icon."""
        self.icon = icon
        self.icon_label.configure(text=icon)


class PulsingIndicator(tk.Label):
    """Simple pulsing indicator for drawing attention."""
    
    def __init__(self, parent: tk.Widget, text: str = "●",
                 style_manager: StyleManager = None,
                 pulse_color: str = None,
                 **kwargs):
        super().__init__(parent, text=text, **kwargs)
        
        self.style_manager = style_manager
        self.pulse_color = pulse_color or (style_manager.theme.colors.error if style_manager else "#f44336")
        self.original_color = self.cget('fg')
        
        self.is_pulsing = False
        self.pulse_direction = 1  # 1 for brightening, -1 for dimming
        self.pulse_alpha = 1.0
        
        self._setup_styling()
    
    def _setup_styling(self):
        """Setup initial styling."""
        if self.style_manager:
            self.configure(
                bg=self.style_manager.theme.colors.background,
                fg=self.pulse_color,
                font=('Segoe UI', 12)
            )
    
    def start_pulsing(self):
        """Start pulsing animation."""
        if not self.is_pulsing:
            self.is_pulsing = True
            self._animate_pulse()
    
    def stop_pulsing(self):
        """Stop pulsing animation."""
        self.is_pulsing = False
        self.configure(fg=self.pulse_color)
    
    def _animate_pulse(self):
        """Animate pulsing effect."""
        if not self.is_pulsing:
            return
        
        # Update alpha
        self.pulse_alpha += self.pulse_direction * 0.1
        
        # Reverse direction at bounds
        if self.pulse_alpha >= 1.0:
            self.pulse_alpha = 1.0
            self.pulse_direction = -1
        elif self.pulse_alpha <= 0.3:
            self.pulse_alpha = 0.3
            self.pulse_direction = 1
        
        # Apply alpha to color (simplified)
        alpha_color = self._apply_alpha(self.pulse_color, self.pulse_alpha)
        self.configure(fg=alpha_color)
        
        # Schedule next frame
        self.after(50, self._animate_pulse)
    
    def _apply_alpha(self, hex_color: str, alpha: float) -> str:
        """Apply alpha to hex color (simplified blend with background)."""
        # Simple alpha blending - mix with white background
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        
        # Blend with white based on alpha
        r = int(r * alpha + 255 * (1 - alpha))
        g = int(g * alpha + 255 * (1 - alpha))
        b = int(b * alpha + 255 * (1 - alpha))
        
        return f"#{r:02x}{g:02x}{b:02x}"


class TooltipButton(tk.Button):
    """Button with enhanced tooltip on hover."""
    
    def __init__(self, parent: tk.Widget, text: str = "",
                 tooltip_text: str = "",
                 style_manager: StyleManager = None,
                 **kwargs):
        super().__init__(parent, text=text, **kwargs)
        
        self.style_manager = style_manager
        self.tooltip_text = tooltip_text
        self.tooltip_window = None
        
        self._setup_tooltip()
        
        if self.style_manager:
            self.style_manager.register_widget(self, classes=['button', 'tooltip-button'])
    
    def _setup_tooltip(self):
        """Setup tooltip bindings."""
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Motion>', self._on_motion)
    
    def _on_enter(self, event):
        """Show tooltip on enter."""
        self.after(500, self._show_tooltip)  # Delay tooltip
    
    def _on_leave(self, event):
        """Hide tooltip on leave."""
        self._hide_tooltip()
    
    def _on_motion(self, event):
        """Update tooltip position on motion."""
        if self.tooltip_window:
            self._position_tooltip(event)
    
    def _show_tooltip(self):
        """Show tooltip window."""
        if self.tooltip_window or not self.tooltip_text:
            return
        
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self)
        self.tooltip_window.wm_overrideredirect(True)
        
        if self.style_manager:
            bg_color = self.style_manager.theme.colors.inverse_surface
            fg_color = self.style_manager.theme.colors.inverse_on_surface
        else:
            bg_color = "#333333"
            fg_color = "#ffffff"
        
        self.tooltip_window.configure(bg=bg_color)
        
        # Create tooltip label
        tooltip_label = tk.Label(
            self.tooltip_window,
            text=self.tooltip_text,
            bg=bg_color,
            fg=fg_color,
            font=('Segoe UI', 9),
            padx=8,
            pady=4,
            relief='solid',
            borderwidth=1
        )
        tooltip_label.pack()
        
        # Position tooltip
        self._position_tooltip()
        
        # Animate in
        if self.style_manager:
            self.tooltip_window.attributes('-alpha', 0)
            self._fade_tooltip_in()
    
    def _position_tooltip(self, event=None):
        """Position tooltip near cursor."""
        if not self.tooltip_window:
            return
        
        x = self.winfo_rootx() + 20
        y = self.winfo_rooty() + self.winfo_height() + 5
        
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
    
    def _hide_tooltip(self):
        """Hide tooltip window."""
        if self.tooltip_window:
            if self.style_manager:
                self._fade_tooltip_out()
            else:
                self.tooltip_window.destroy()
                self.tooltip_window = None
    
    def _fade_tooltip_in(self, alpha=0.0):
        """Fade tooltip in."""
        alpha += 0.1
        self.tooltip_window.attributes('-alpha', alpha)
        
        if alpha < 0.9:
            self.after(20, lambda: self._fade_tooltip_in(alpha))
    
    def _fade_tooltip_out(self, alpha=0.9):
        """Fade tooltip out."""
        alpha -= 0.1
        
        if alpha > 0:
            self.tooltip_window.attributes('-alpha', alpha)
            self.after(20, lambda: self._fade_tooltip_out(alpha))
        else:
            self.tooltip_window.destroy()
            self.tooltip_window = None