"""
Loading state components with smooth animations and Material Design styling.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
import math
import time

from ..styles import StyleManager, Easing


class LoadingSpinner(tk.Canvas):
    """Animated loading spinner widget."""
    
    def __init__(self, parent: tk.Widget, size: int = 40, 
                 style_manager: StyleManager = None):
        super().__init__(parent, width=size, height=size, highlightthickness=0)
        
        self.size = size
        self.style_manager = style_manager
        self.is_spinning = False
        self.rotation = 0
        self.after_id = None
        
        self._setup_colors()
        self._draw_spinner()
    
    def _setup_colors(self):
        """Setup spinner colors."""
        if self.style_manager:
            self.bg_color = self.style_manager.theme.colors.background
            self.spinner_color = self.style_manager.theme.colors.primary
            self.configure(bg=self.bg_color)
        else:
            self.bg_color = "#ffffff"
            self.spinner_color = "#2196f3"
    
    def _draw_spinner(self):
        """Draw spinner with current rotation."""
        self.delete("all")
        
        center = self.size // 2
        radius = (self.size - 10) // 2
        
        # Draw arc segments with varying opacity
        segments = 8
        for i in range(segments):
            start_angle = (360 / segments) * i + self.rotation
            extent = 360 / segments * 0.7  # Slight gap between segments
            
            # Calculate opacity based on position
            opacity = (i + 1) / segments
            alpha = int(opacity * 255)
            color = self._hex_with_alpha(self.spinner_color, alpha)
            
            self.create_arc(
                center - radius, center - radius,
                center + radius, center + radius,
                start=start_angle, extent=extent,
                outline=color, width=3, style="arc"
            )
    
    def _hex_with_alpha(self, hex_color: str, alpha: int) -> str:
        """Convert hex color with alpha to approximate color."""
        # Simple alpha blending with white background
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # Blend with white background based on alpha
        alpha_ratio = alpha / 255
        r = int(r * alpha_ratio + 255 * (1 - alpha_ratio))
        g = int(g * alpha_ratio + 255 * (1 - alpha_ratio))
        b = int(b * alpha_ratio + 255 * (1 - alpha_ratio))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def start_spinning(self):
        """Start spinner animation."""
        if not self.is_spinning:
            self.is_spinning = True
            self._animate()
    
    def stop_spinning(self):
        """Stop spinner animation."""
        self.is_spinning = False
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
    
    def _animate(self):
        """Animate spinner rotation."""
        if self.is_spinning:
            self.rotation = (self.rotation + 20) % 360
            self._draw_spinner()
            self.after_id = self.after(50, self._animate)  # ~20fps


class ProgressIndicator(tk.Frame):
    """Progress indicator with label and optional cancel button."""
    
    def __init__(self, parent: tk.Widget, style_manager: StyleManager = None,
                 show_cancel: bool = False, on_cancel: Callable = None,
                 timeout_seconds: int = 60):
        super().__init__(parent)
        
        self.style_manager = style_manager
        self.show_cancel = show_cancel
        self.on_cancel = on_cancel
        self.timeout_seconds = timeout_seconds
        self.current_progress = 0
        self.current_text = "Loading..."
        self.start_time = None
        self.timeout_after_id = None
        self.is_cancelled = False
        
        self._create_widgets()
        
        if self.style_manager:
            self.style_manager.register_widget(self, classes=['frame', 'progress-indicator'])
    
    def _create_widgets(self):
        """Create progress indicator widgets."""
        # Apply frame styling
        if self.style_manager:
            self.configure(
                bg=self.style_manager.theme.colors.surface,
                padx=20,
                pady=15
            )
        
        # Progress text
        self.text_label = tk.Label(
            self,
            text=self.current_text,
            font=('Segoe UI', 11),
            bg=self.configure()['bg'][-1],
            fg=self.style_manager.theme.colors.on_surface if self.style_manager else "#000000"
        )
        self.text_label.pack(anchor='w', pady=(0, 10))
        
        # Progress container
        progress_container = tk.Frame(self, bg=self.configure()['bg'][-1])
        progress_container.pack(fill='x')
        
        # Spinner
        self.spinner = LoadingSpinner(
            progress_container, size=20, style_manager=self.style_manager
        )
        self.spinner.pack(side='left', padx=(0, 10))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            progress_container,
            mode='indeterminate',
            length=200
        )
        self.progress_bar.pack(side='left', fill='x', expand=True)
        
        # Cancel button
        if self.show_cancel and self.on_cancel:
            self.cancel_button = tk.Button(
                progress_container,
                text="Cancel",
                font=('Segoe UI', 9),
                command=self.on_cancel,
                relief='flat',
                padx=15,
                pady=5
            )
            
            if self.style_manager:
                self.cancel_button.configure(
                    bg=self.style_manager.theme.colors.surface_variant,
                    fg=self.style_manager.theme.colors.on_surface,
                    activebackground=self.style_manager.theme.colors.outline_variant
                )
            
            self.cancel_button.pack(side='right', padx=(10, 0))
    
    def start_loading(self, text: str = "Loading...", timeout_callback: Callable = None):
        """Start loading animation with optional timeout."""
        self.current_text = text
        self.text_label.configure(text=text)
        self.spinner.start_spinning()
        self.progress_bar.start(10)
        self.start_time = time.time()
        self.is_cancelled = False
        
        # Setup timeout if specified
        if self.timeout_seconds > 0 and timeout_callback:
            self.timeout_after_id = self.after(
                self.timeout_seconds * 1000, 
                lambda: self._handle_timeout(timeout_callback)
            )
        
        # Start progress time tracking
        self._update_time_display()
    
    def stop_loading(self):
        """Stop loading animation and cleanup."""
        self.spinner.stop_spinning()
        self.progress_bar.stop()
        
        # Cancel timeout
        if self.timeout_after_id:
            self.after_cancel(self.timeout_after_id)
            self.timeout_after_id = None
        
        self.start_time = None
    
    def set_progress(self, progress: int, text: str = None):
        """Set determinate progress (0-100)."""
        self.progress_bar.configure(mode='determinate')
        self.progress_bar['value'] = progress
        
        if text:
            self.text_label.configure(text=text)
    
    def set_text(self, text: str):
        """Update progress text."""
        self.current_text = text
        
        # Add time elapsed if loading
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            display_text = f"{text} ({elapsed}s)"
        else:
            display_text = text
            
        self.text_label.configure(text=display_text)
    
    def _handle_timeout(self, timeout_callback: Callable):
        """Handle operation timeout."""
        self.set_text("Operation timed out")
        self.stop_loading()
        if timeout_callback:
            timeout_callback()
    
    def _update_time_display(self):
        """Update time display during loading."""
        if self.start_time and not self.is_cancelled:
            elapsed = int(time.time() - self.start_time)
            remaining = max(0, self.timeout_seconds - elapsed) if self.timeout_seconds > 0 else 0
            
            if self.timeout_seconds > 0 and remaining <= 10:
                # Show countdown in last 10 seconds
                display_text = f"{self.current_text} (timeout in {remaining}s)"
            else:
                display_text = f"{self.current_text} ({elapsed}s)"
            
            self.text_label.configure(text=display_text)
            
            # Schedule next update
            self.after(1000, self._update_time_display)
    
    def cancel(self):
        """Cancel the current operation."""
        self.is_cancelled = True
        if self.on_cancel:
            self.on_cancel()
        self.stop_loading()


class LoadingOverlay(tk.Toplevel):
    """Full-screen loading overlay with cancellation support."""
    
    def __init__(self, parent: tk.Widget, style_manager: StyleManager = None,
                 text: str = "Loading...", show_progress: bool = False,
                 show_cancel: bool = True, on_cancel: Callable = None):
        super().__init__(parent)
        
        self.style_manager = style_manager
        self.parent_widget = parent
        self.loading_text = text
        self.show_progress = show_progress
        self.show_cancel = show_cancel
        self.on_cancel = on_cancel
        self.start_time = None
        
        self._setup_overlay()
        self._create_widgets()
        self._position_overlay()
    
    def _setup_overlay(self):
        """Setup overlay window properties."""
        self.wm_overrideredirect(True)
        self.attributes('-topmost', True)
        
        # Semi-transparent background
        if self.style_manager:
            bg_color = self.style_manager.theme.colors.inverse_surface
        else:
            bg_color = "#000000"
        
        self.configure(bg=bg_color)
        self.attributes('-alpha', 0.8)  # Semi-transparent
    
    def _create_widgets(self):
        """Create overlay content."""
        # Main container
        container = tk.Frame(
            self,
            bg=self.configure()['bg'][-1],
            padx=40,
            pady=40
        )
        container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Large spinner
        self.spinner = LoadingSpinner(
            container, size=80, style_manager=self.style_manager
        )
        self.spinner.pack(pady=(0, 20))
        
        # Loading text
        text_color = self.style_manager.theme.colors.inverse_on_surface if self.style_manager else "#ffffff"
        
        self.text_label = tk.Label(
            container,
            text=self.loading_text,
            font=('Segoe UI', 16),
            bg=self.configure()['bg'][-1],
            fg=text_color
        )
        self.text_label.pack(pady=(0, 10))
        
        # Cancel button
        if self.show_cancel and self.on_cancel:
            self.cancel_button = tk.Button(
                container,
                text="Cancel",
                font=('Segoe UI', 12),
                command=self._handle_cancel,
                relief='flat',
                padx=20,
                pady=8,
                bg='#f44336' if not self.style_manager else self.style_manager.theme.colors.error,
                fg='white',
                activebackground='#d32f2f'
            )
            self.cancel_button.pack(pady=(20, 0))
        
        # Progress bar (optional)
        if self.show_progress:
            self.progress_bar = ttk.Progressbar(
                container,
                mode='indeterminate',
                length=300
            )
            self.progress_bar.pack()
    
    def _position_overlay(self):
        """Position overlay to cover parent window."""
        # Get parent window geometry
        parent_x = self.parent_widget.winfo_rootx()
        parent_y = self.parent_widget.winfo_rooty()
        parent_width = self.parent_widget.winfo_width()
        parent_height = self.parent_widget.winfo_height()
        
        # Set overlay geometry
        self.geometry(f"{parent_width}x{parent_height}+{parent_x}+{parent_y}")
    
    def show_loading(self):
        """Show loading overlay."""
        self.spinner.start_spinning()
        if hasattr(self, 'progress_bar'):
            self.progress_bar.start(10)
        
        self.start_time = time.time()
        
        # Start time update
        self._update_time_display()
        
        # Fade in animation
        self.attributes('-alpha', 0)
        self._fade_in()
    
    def hide_loading(self):
        """Hide loading overlay and cleanup."""
        self.spinner.stop_spinning()
        if hasattr(self, 'progress_bar'):
            self.progress_bar.stop()
        
        self.start_time = None
        
        # Fade out and destroy
        self._fade_out()
    
    def _fade_in(self, alpha: float = 0):
        """Fade in animation."""
        alpha += 0.1
        self.attributes('-alpha', alpha)
        
        if alpha < 0.8:
            self.after(30, lambda: self._fade_in(alpha))
    
    def _fade_out(self, alpha: float = 0.8):
        """Fade out animation."""
        alpha -= 0.1
        self.attributes('-alpha', alpha)
        
        if alpha > 0:
            self.after(30, lambda: self._fade_out(alpha))
        else:
            self.destroy()
    
    def set_text(self, text: str):
        """Update loading text with time elapsed."""
        self.loading_text = text
        
        # Add elapsed time if loading
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            display_text = f"{text}\n({elapsed}s elapsed)"
        else:
            display_text = text
            
        self.text_label.configure(text=display_text)
    
    def _handle_cancel(self):
        """Handle cancel button click."""
        if self.on_cancel:
            self.on_cancel()
        self.hide_loading()
    
    def _update_time_display(self):
        """Update time display during loading."""
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            display_text = f"{self.loading_text}\n({elapsed}s elapsed)"
            self.text_label.configure(text=display_text)
            
            # Schedule next update
            self.after(1000, self._update_time_display)
    
    def set_progress(self, progress: int):
        """Set progress value (0-100)."""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.configure(mode='determinate')
            self.progress_bar['value'] = progress


class PulsingDot(tk.Canvas):
    """Simple pulsing dot for subtle loading indication."""
    
    def __init__(self, parent: tk.Widget, size: int = 12,
                 style_manager: StyleManager = None):
        super().__init__(parent, width=size, height=size, highlightthickness=0)
        
        self.size = size
        self.style_manager = style_manager
        self.is_pulsing = False
        self.scale = 1.0
        self.direction = 1
        self.after_id = None
        
        self._setup_colors()
        self._draw_dot()
    
    def _setup_colors(self):
        """Setup dot colors."""
        if self.style_manager:
            self.bg_color = self.style_manager.theme.colors.background
            self.dot_color = self.style_manager.theme.colors.primary
            self.configure(bg=self.bg_color)
        else:
            self.bg_color = "#ffffff"
            self.dot_color = "#2196f3"
    
    def _draw_dot(self):
        """Draw pulsing dot."""
        self.delete("all")
        
        center = self.size // 2
        radius = int((self.size // 4) * self.scale)
        
        self.create_oval(
            center - radius, center - radius,
            center + radius, center + radius,
            fill=self.dot_color,
            outline=""
        )
    
    def start_pulsing(self):
        """Start pulsing animation."""
        if not self.is_pulsing:
            self.is_pulsing = True
            self._animate_pulse()
    
    def stop_pulsing(self):
        """Stop pulsing animation."""
        self.is_pulsing = False
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        
        # Reset to normal size
        self.scale = 1.0
        self._draw_dot()
    
    def _animate_pulse(self):
        """Animate pulsing effect."""
        if self.is_pulsing:
            # Oscillate scale between 0.5 and 1.5
            self.scale += self.direction * 0.1
            
            if self.scale >= 1.5:
                self.direction = -1
            elif self.scale <= 0.5:
                self.direction = 1
            
            self._draw_dot()
            self.after_id = self.after(80, self._animate_pulse)


class SkeletonLoader(tk.Frame):
    """Skeleton loading placeholder for content."""
    
    def __init__(self, parent: tk.Widget, style_manager: StyleManager = None,
                 lines: int = 3, width: int = 300):
        super().__init__(parent)
        
        self.style_manager = style_manager
        self.lines = lines
        self.skeleton_width = width
        self.is_animating = False
        self.skeleton_bars = []
        
        self._create_skeleton()
        
        if self.style_manager:
            self.style_manager.register_widget(self, classes=['frame', 'skeleton-loader'])
    
    def _create_skeleton(self):
        """Create skeleton loading bars."""
        if self.style_manager:
            bar_color = self.style_manager.theme.colors.surface_variant
            self.configure(bg=self.style_manager.theme.colors.background)
        else:
            bar_color = "#e0e0e0"
        
        for i in range(self.lines):
            # Vary bar widths slightly
            bar_width = self.skeleton_width - (i * 20 if i == self.lines - 1 else 0)
            
            bar = tk.Frame(
                self,
                bg=bar_color,
                height=12,
                width=bar_width
            )
            bar.pack(fill='x', pady=3)
            bar.pack_propagate(False)
            
            self.skeleton_bars.append(bar)
    
    def start_animation(self):
        """Start skeleton shimmer animation."""
        self.is_animating = True
        self._animate_shimmer()
    
    def stop_animation(self):
        """Stop skeleton animation."""
        self.is_animating = False
    
    def _animate_shimmer(self):
        """Animate shimmer effect on skeleton bars."""
        if not self.is_animating:
            return
        
        # Simple color pulse animation
        if self.style_manager:
            base_color = self.style_manager.theme.colors.surface_variant
            highlight_color = self.style_manager.theme.colors.outline_variant
        else:
            base_color = "#e0e0e0"
            highlight_color = "#f0f0f0"
        
        # Alternate colors
        for i, bar in enumerate(self.skeleton_bars):
            if (time.time() * 2 + i * 0.2) % 2 < 1:
                bar.configure(bg=highlight_color)
            else:
                bar.configure(bg=base_color)
        
        self.after(200, self._animate_shimmer)