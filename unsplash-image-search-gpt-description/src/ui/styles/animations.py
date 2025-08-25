"""
Animation system for smooth micro-interactions and transitions.
Provides easing functions, transition management, and animation utilities.
"""

import tkinter as tk
import math
from typing import Callable, Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
import time


class Easing(Enum):
    """Easing functions for animations."""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    EASE_IN_CUBIC = "ease_in_cubic"
    EASE_OUT_CUBIC = "ease_out_cubic"
    EASE_IN_OUT_CUBIC = "ease_in_out_cubic"
    EASE_IN_QUART = "ease_in_quart"
    EASE_OUT_QUART = "ease_out_quart"
    EASE_IN_OUT_QUART = "ease_in_out_quart"
    BOUNCE_OUT = "bounce_out"
    ELASTIC_OUT = "elastic_out"


@dataclass
class AnimationState:
    """State tracking for active animation."""
    start_time: float
    duration: float
    start_value: Union[int, float, tuple]
    end_value: Union[int, float, tuple]
    easing: Easing
    callback: Callable
    update_callback: Optional[Callable] = None
    complete_callback: Optional[Callable] = None
    after_id: Optional[str] = None
    paused: bool = False
    pause_time: float = 0


class EasingFunctions:
    """Collection of easing function implementations."""
    
    @staticmethod
    def linear(t: float) -> float:
        """Linear interpolation."""
        return t
    
    @staticmethod  
    def ease_in(t: float) -> float:
        """Quadratic ease in."""
        return t * t
    
    @staticmethod
    def ease_out(t: float) -> float:
        """Quadratic ease out."""
        return 1 - (1 - t) * (1 - t)
    
    @staticmethod
    def ease_in_out(t: float) -> float:
        """Quadratic ease in/out."""
        if t < 0.5:
            return 2 * t * t
        return 1 - pow(-2 * t + 2, 2) / 2
    
    @staticmethod
    def ease_in_cubic(t: float) -> float:
        """Cubic ease in."""
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Cubic ease out."""
        return 1 - pow(1 - t, 3)
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Cubic ease in/out."""
        if t < 0.5:
            return 4 * t * t * t
        return 1 - pow(-2 * t + 2, 3) / 2
    
    @staticmethod
    def ease_in_quart(t: float) -> float:
        """Quartic ease in."""
        return t * t * t * t
    
    @staticmethod
    def ease_out_quart(t: float) -> float:
        """Quartic ease out."""
        return 1 - pow(1 - t, 4)
    
    @staticmethod
    def ease_in_out_quart(t: float) -> float:
        """Quartic ease in/out."""
        if t < 0.5:
            return 8 * t * t * t * t
        return 1 - pow(-2 * t + 2, 4) / 2
    
    @staticmethod
    def bounce_out(t: float) -> float:
        """Bounce ease out."""
        n1 = 7.5625
        d1 = 2.75
        
        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375
    
    @staticmethod
    def elastic_out(t: float) -> float:
        """Elastic ease out."""
        if t == 0:
            return 0
        if t == 1:
            return 1
        
        c4 = (2 * math.pi) / 3
        return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


class Transition:
    """Individual transition for animating a single property."""
    
    def __init__(self, widget: tk.Widget, property_name: str, 
                 start_value: Union[int, float, tuple], 
                 end_value: Union[int, float, tuple],
                 duration: float = 0.3, 
                 easing: Easing = Easing.EASE_OUT,
                 delay: float = 0,
                 update_callback: Optional[Callable] = None,
                 complete_callback: Optional[Callable] = None):
        
        self.widget = widget
        self.property_name = property_name
        self.start_value = start_value
        self.end_value = end_value  
        self.duration = duration
        self.easing = easing
        self.delay = delay
        self.update_callback = update_callback
        self.complete_callback = complete_callback
        
        self.animation_state: Optional[AnimationState] = None
        
    def start(self) -> str:
        """Start the transition animation."""
        if self.delay > 0:
            # Schedule delayed start
            return self.widget.after(
                int(self.delay * 1000), 
                self._start_animation
            )
        else:
            return self._start_animation()
    
    def _start_animation(self) -> str:
        """Internal method to start animation."""
        self.animation_state = AnimationState(
            start_time=time.time(),
            duration=self.duration,
            start_value=self.start_value,
            end_value=self.end_value,
            easing=self.easing,
            callback=self._animate_frame,
            update_callback=self.update_callback,
            complete_callback=self.complete_callback
        )
        
        return self._animate_frame()
    
    def _animate_frame(self) -> str:
        """Animate a single frame."""
        if not self.animation_state or self.animation_state.paused:
            return ""
            
        current_time = time.time()
        elapsed = current_time - self.animation_state.start_time
        progress = min(1.0, elapsed / self.animation_state.duration)
        
        # Apply easing function
        eased_progress = self._apply_easing(progress)
        
        # Calculate current value
        current_value = self._interpolate_value(
            self.animation_state.start_value,
            self.animation_state.end_value,
            eased_progress
        )
        
        # Update widget property
        self._update_widget_property(current_value)
        
        # Call update callback if provided
        if self.animation_state.update_callback:
            self.animation_state.update_callback(current_value, progress)
        
        # Check if animation is complete
        if progress >= 1.0:
            # Animation complete
            if self.animation_state.complete_callback:
                self.animation_state.complete_callback()
            self.animation_state = None
            return ""
        
        # Schedule next frame (approximately 60fps)
        self.animation_state.after_id = self.widget.after(16, self._animate_frame)
        return self.animation_state.after_id
    
    def _apply_easing(self, t: float) -> float:
        """Apply easing function to progress."""
        easing_map = {
            Easing.LINEAR: EasingFunctions.linear,
            Easing.EASE_IN: EasingFunctions.ease_in,
            Easing.EASE_OUT: EasingFunctions.ease_out,
            Easing.EASE_IN_OUT: EasingFunctions.ease_in_out,
            Easing.EASE_IN_CUBIC: EasingFunctions.ease_in_cubic,
            Easing.EASE_OUT_CUBIC: EasingFunctions.ease_out_cubic,
            Easing.EASE_IN_OUT_CUBIC: EasingFunctions.ease_in_out_cubic,
            Easing.EASE_IN_QUART: EasingFunctions.ease_in_quart,
            Easing.EASE_OUT_QUART: EasingFunctions.ease_out_quart,
            Easing.EASE_IN_OUT_QUART: EasingFunctions.ease_in_out_quart,
            Easing.BOUNCE_OUT: EasingFunctions.bounce_out,
            Easing.ELASTIC_OUT: EasingFunctions.elastic_out,
        }
        
        return easing_map.get(self.easing, EasingFunctions.ease_out)(t)
    
    def _interpolate_value(self, start: Union[int, float, tuple], 
                          end: Union[int, float, tuple], 
                          progress: float) -> Union[int, float, tuple]:
        """Interpolate between start and end values."""
        if isinstance(start, (int, float)) and isinstance(end, (int, float)):
            return start + (end - start) * progress
        
        elif isinstance(start, tuple) and isinstance(end, tuple):
            if len(start) != len(end):
                raise ValueError("Tuple values must have same length")
            
            return tuple(
                s + (e - s) * progress 
                for s, e in zip(start, end)
            )
        
        else:
            raise TypeError("Values must be numeric or tuples of numeric values")
    
    def _update_widget_property(self, value: Union[int, float, tuple]):
        """Update the widget property with new value."""
        try:
            if self.property_name == "alpha":
                # Special handling for alpha/transparency
                self._set_alpha(value)
            elif self.property_name == "position":
                # Special handling for position (x, y)
                if isinstance(value, tuple) and len(value) == 2:
                    self.widget.place(x=int(value[0]), y=int(value[1]))
            elif self.property_name == "size":
                # Special handling for size (width, height)
                if isinstance(value, tuple) and len(value) == 2:
                    self.widget.configure(width=int(value[0]), height=int(value[1]))
            else:
                # Standard property configuration
                config_dict = {self.property_name: value}
                self.widget.configure(**config_dict)
                
        except tk.TclError as e:
            # Handle cases where widget is destroyed or property invalid
            print(f"Animation error updating {self.property_name}: {e}")
            if self.animation_state:
                self.animation_state = None
    
    def _set_alpha(self, alpha: float):
        """Set widget transparency (limited Tkinter support)."""
        # Note: Tkinter has limited transparency support
        # This is a placeholder for alpha animations
        alpha_int = max(0, min(255, int(alpha * 255)))
        # In a real implementation, this might use platform-specific methods
        pass
    
    def pause(self):
        """Pause the animation."""
        if self.animation_state and not self.animation_state.paused:
            self.animation_state.paused = True
            self.animation_state.pause_time = time.time()
            if self.animation_state.after_id:
                self.widget.after_cancel(self.animation_state.after_id)
    
    def resume(self):
        """Resume the paused animation."""
        if self.animation_state and self.animation_state.paused:
            pause_duration = time.time() - self.animation_state.pause_time
            self.animation_state.start_time += pause_duration
            self.animation_state.paused = False
            self._animate_frame()
    
    def stop(self):
        """Stop the animation."""
        if self.animation_state:
            if self.animation_state.after_id:
                self.widget.after_cancel(self.animation_state.after_id)
            self.animation_state = None


class AnimationManager:
    """Manages multiple animations and provides high-level animation utilities."""
    
    def __init__(self, root_widget: tk.Widget):
        self.root = root_widget
        self.active_animations: Dict[str, List[Transition]] = {}
        self.animation_id_counter = 0
        
    def _get_next_id(self) -> str:
        """Get next unique animation ID."""
        self.animation_id_counter += 1
        return f"anim_{self.animation_id_counter}"
    
    def fade_in(self, widget: tk.Widget, duration: float = 0.3, 
                easing: Easing = Easing.EASE_OUT,
                complete_callback: Optional[Callable] = None) -> str:
        """Fade in animation (opacity 0 to 1)."""
        return self._create_alpha_animation(
            widget, 0, 1, duration, easing, complete_callback
        )
    
    def fade_out(self, widget: tk.Widget, duration: float = 0.3,
                 easing: Easing = Easing.EASE_OUT,
                 complete_callback: Optional[Callable] = None) -> str:
        """Fade out animation (opacity 1 to 0)."""
        return self._create_alpha_animation(
            widget, 1, 0, duration, easing, complete_callback
        )
    
    def slide_in(self, widget: tk.Widget, direction: str = "left",
                 distance: int = 100, duration: float = 0.4,
                 easing: Easing = Easing.EASE_OUT_CUBIC,
                 complete_callback: Optional[Callable] = None) -> str:
        """Slide in animation from specified direction."""
        current_x = widget.winfo_x()
        current_y = widget.winfo_y()
        
        direction_map = {
            "left": (-distance, 0),
            "right": (distance, 0),
            "up": (0, -distance),
            "down": (0, distance)
        }
        
        offset_x, offset_y = direction_map.get(direction, (0, 0))
        start_pos = (current_x + offset_x, current_y + offset_y)
        end_pos = (current_x, current_y)
        
        # Set initial position
        widget.place(x=start_pos[0], y=start_pos[1])
        
        return self.animate_property(
            widget, "position", start_pos, end_pos, 
            duration, easing, complete_callback=complete_callback
        )
    
    def slide_out(self, widget: tk.Widget, direction: str = "right",
                  distance: int = 100, duration: float = 0.4,
                  easing: Easing = Easing.EASE_IN_CUBIC,
                  complete_callback: Optional[Callable] = None) -> str:
        """Slide out animation in specified direction."""
        current_x = widget.winfo_x()
        current_y = widget.winfo_y()
        
        direction_map = {
            "left": (-distance, 0),
            "right": (distance, 0),
            "up": (0, -distance),
            "down": (0, distance)
        }
        
        offset_x, offset_y = direction_map.get(direction, (0, 0))
        start_pos = (current_x, current_y)
        end_pos = (current_x + offset_x, current_y + offset_y)
        
        return self.animate_property(
            widget, "position", start_pos, end_pos,
            duration, easing, complete_callback=complete_callback
        )
    
    def scale_in(self, widget: tk.Widget, duration: float = 0.3,
                 easing: Easing = Easing.EASE_OUT_CUBIC,
                 complete_callback: Optional[Callable] = None) -> str:
        """Scale in animation (size 0 to normal)."""
        original_width = widget.winfo_reqwidth()
        original_height = widget.winfo_reqheight()
        
        widget.configure(width=1, height=1)
        
        return self.animate_property(
            widget, "size", (1, 1), (original_width, original_height),
            duration, easing, complete_callback=complete_callback
        )
    
    def bounce(self, widget: tk.Widget, distance: int = 10,
               duration: float = 0.6, complete_callback: Optional[Callable] = None) -> str:
        """Bounce animation."""
        current_y = widget.winfo_y()
        start_pos = (widget.winfo_x(), current_y)
        bounce_pos = (widget.winfo_x(), current_y - distance)
        
        def bounce_back():
            self.animate_property(
                widget, "position", bounce_pos, start_pos,
                duration / 2, Easing.BOUNCE_OUT, complete_callback=complete_callback
            )
        
        return self.animate_property(
            widget, "position", start_pos, bounce_pos,
            duration / 2, Easing.EASE_OUT, complete_callback=bounce_back
        )
    
    def pulse(self, widget: tk.Widget, scale: float = 1.1,
              duration: float = 0.4, complete_callback: Optional[Callable] = None) -> str:
        """Pulse animation (scale up and down)."""
        original_width = widget.winfo_reqwidth()
        original_height = widget.winfo_reqheight()
        
        pulse_width = int(original_width * scale)
        pulse_height = int(original_height * scale)
        
        def scale_back():
            self.animate_property(
                widget, "size", (pulse_width, pulse_height), (original_width, original_height),
                duration / 2, Easing.EASE_OUT, complete_callback=complete_callback
            )
        
        return self.animate_property(
            widget, "size", (original_width, original_height), (pulse_width, pulse_height),
            duration / 2, Easing.EASE_OUT, complete_callback=scale_back
        )
    
    def animate_property(self, widget: tk.Widget, property_name: str,
                        start_value: Union[int, float, tuple],
                        end_value: Union[int, float, tuple],
                        duration: float = 0.3,
                        easing: Easing = Easing.EASE_OUT,
                        delay: float = 0,
                        update_callback: Optional[Callable] = None,
                        complete_callback: Optional[Callable] = None) -> str:
        """Animate any widget property."""
        animation_id = self._get_next_id()
        
        transition = Transition(
            widget, property_name, start_value, end_value,
            duration, easing, delay, update_callback, complete_callback
        )
        
        # Store reference to animation
        if animation_id not in self.active_animations:
            self.active_animations[animation_id] = []
        self.active_animations[animation_id].append(transition)
        
        # Start animation
        transition.start()
        
        return animation_id
    
    def _create_alpha_animation(self, widget: tk.Widget, start_alpha: float,
                               end_alpha: float, duration: float,
                               easing: Easing, complete_callback: Optional[Callable]) -> str:
        """Create alpha animation (placeholder for transparency effects)."""
        # Since Tkinter has limited transparency support, we'll simulate 
        # with other visual effects like scaling or color changes
        return self.animate_property(
            widget, "alpha", start_alpha, end_alpha, 
            duration, easing, complete_callback=complete_callback
        )
    
    def stop_animation(self, animation_id: str):
        """Stop specific animation by ID."""
        if animation_id in self.active_animations:
            for transition in self.active_animations[animation_id]:
                transition.stop()
            del self.active_animations[animation_id]
    
    def stop_all_animations(self):
        """Stop all active animations."""
        for animation_id in list(self.active_animations.keys()):
            self.stop_animation(animation_id)
    
    def pause_animation(self, animation_id: str):
        """Pause specific animation by ID."""
        if animation_id in self.active_animations:
            for transition in self.active_animations[animation_id]:
                transition.pause()
    
    def resume_animation(self, animation_id: str):
        """Resume specific animation by ID."""
        if animation_id in self.active_animations:
            for transition in self.active_animations[animation_id]:
                transition.resume()
    
    def create_loading_animation(self, widget: tk.Widget) -> str:
        """Create a loading/spinner animation."""
        # Implement a rotation or pulsing effect for loading states
        def pulse_callback():
            self.pulse(widget, 1.1, 1.0, pulse_callback)
        
        return self.pulse(widget, 1.05, 1.0, pulse_callback)
    
    def create_hover_effect(self, widget: tk.Widget, 
                           hover_scale: float = 1.02,
                           hover_duration: float = 0.2) -> tuple:
        """Create hover enter/leave effects."""
        original_width = widget.winfo_reqwidth()
        original_height = widget.winfo_reqheight()
        
        def on_enter(event=None):
            hover_width = int(original_width * hover_scale)
            hover_height = int(original_height * hover_scale)
            self.animate_property(
                widget, "size", (original_width, original_height),
                (hover_width, hover_height), hover_duration, Easing.EASE_OUT
            )
        
        def on_leave(event=None):
            hover_width = int(original_width * hover_scale)
            hover_height = int(original_height * hover_scale)
            self.animate_property(
                widget, "size", (hover_width, hover_height),
                (original_width, original_height), hover_duration, Easing.EASE_OUT
            )
        
        return on_enter, on_leave