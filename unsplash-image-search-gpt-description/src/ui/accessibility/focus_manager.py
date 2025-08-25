"""
Focus management and keyboard navigation for accessibility.
Provides enhanced focus indicators and tab order management.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Optional, Callable, Any
import threading


class FocusManager:
    """
    Manages focus indicators and tab order for accessibility.
    Provides enhanced visual focus indicators and keyboard navigation.
    """
    
    def __init__(self, root_window: tk.Tk):
        self.root = root_window
        self.focused_widgets: Dict[tk.Widget, Dict[str, Any]] = {}
        self.tab_order: List[tk.Widget] = []
        self.focus_indicators: Dict[tk.Widget, tk.Widget] = {}
        self.focus_callbacks: List[Callable] = []
        
        # Focus indicator settings
        self.focus_ring_width = 3
        self.focus_ring_color = '#0078D4'
        self.focus_ring_offset = 2
        self.use_focus_rings = True
        
        # Setup global focus tracking
        self._setup_focus_tracking()
    
    def _setup_focus_tracking(self):
        """Setup global focus event tracking."""
        # Bind focus events to root to capture all focus changes
        self.root.bind_all('<FocusIn>', self._on_focus_in, add='+')
        self.root.bind_all('<FocusOut>', self._on_focus_out, add='+')
        
        # Keyboard navigation
        self.root.bind_all('<Tab>', self._on_tab, add='+')
        self.root.bind_all('<Shift-Tab>', self._on_shift_tab, add='+')
        
        # Arrow key navigation for certain contexts
        self.root.bind_all('<Up>', self._on_arrow_up, add='+')
        self.root.bind_all('<Down>', self._on_arrow_down, add='+')
        self.root.bind_all('<Left>', self._on_arrow_left, add='+')
        self.root.bind_all('<Right>', self._on_arrow_right, add='+')
        
        # Home/End for navigation
        self.root.bind_all('<Home>', self._on_home, add='+')
        self.root.bind_all('<End>', self._on_end, add='+')
    
    def add_widget(self, widget: tk.Widget, **options):
        """
        Add a widget to focus management.
        
        Args:
            widget: Widget to manage
            **options: Focus management options:
                - tab_index: Custom tab order index
                - focusable: Whether widget can receive focus
                - focus_ring: Whether to show focus ring
                - skip_tab: Skip this widget in tab navigation
                - aria_label: Accessible name for screen readers
                - role: Widget role for accessibility
        """
        self.focused_widgets[widget] = {
            'tab_index': options.get('tab_index'),
            'focusable': options.get('focusable', True),
            'focus_ring': options.get('focus_ring', True),
            'skip_tab': options.get('skip_tab', False),
            'aria_label': options.get('aria_label', ''),
            'role': options.get('role', ''),
            'original_config': {}
        }
        
        # Make widget focusable if not already
        if options.get('focusable', True):
            try:
                widget.configure(takefocus=1)
            except:
                pass
        
        # Store original configuration for restoration
        self._store_original_config(widget)
        
        # Add to tab order if not explicitly excluded
        if not options.get('skip_tab', False):
            self._add_to_tab_order(widget, options.get('tab_index'))
    
    def remove_widget(self, widget: tk.Widget):
        """Remove widget from focus management."""
        if widget in self.focused_widgets:
            # Remove focus ring if present
            self._remove_focus_ring(widget)
            
            # Remove from tab order
            if widget in self.tab_order:
                self.tab_order.remove(widget)
            
            # Restore original configuration
            self._restore_original_config(widget)
            
            # Remove from tracking
            del self.focused_widgets[widget]
    
    def set_tab_order(self, widgets: List[tk.Widget]):
        """Set explicit tab order for widgets."""
        self.tab_order = []
        for widget in widgets:
            if widget in self.focused_widgets and not self.focused_widgets[widget]['skip_tab']:
                self.tab_order.append(widget)
    
    def _add_to_tab_order(self, widget: tk.Widget, tab_index: Optional[int] = None):
        """Add widget to tab order at specified index."""
        if widget in self.tab_order:
            self.tab_order.remove(widget)
        
        if tab_index is not None:
            # Insert at specific index
            insert_pos = min(tab_index, len(self.tab_order))
            self.tab_order.insert(insert_pos, widget)
        else:
            # Add at end
            self.tab_order.append(widget)
    
    def _store_original_config(self, widget: tk.Widget):
        """Store original widget configuration for restoration."""
        try:
            original = {}
            # Store commonly modified properties
            for prop in ['relief', 'borderwidth', 'highlightthickness', 'highlightcolor']:
                try:
                    original[prop] = widget.cget(prop)
                except:
                    pass
            
            self.focused_widgets[widget]['original_config'] = original
        except:
            pass
    
    def _restore_original_config(self, widget: tk.Widget):
        """Restore original widget configuration."""
        try:
            if widget in self.focused_widgets:
                original = self.focused_widgets[widget]['original_config']
                for prop, value in original.items():
                    try:
                        widget.configure(**{prop: value})
                    except:
                        pass
        except:
            pass
    
    def _on_focus_in(self, event):
        """Handle focus in events."""
        widget = event.widget
        
        if widget in self.focused_widgets:
            # Add focus indicator
            self._show_focus_indicator(widget)
            
            # Announce to screen readers
            self._announce_focus_change(widget)
            
            # Notify callbacks
            for callback in self.focus_callbacks:
                try:
                    callback('focus_in', widget)
                except:
                    pass
    
    def _on_focus_out(self, event):
        """Handle focus out events."""
        widget = event.widget
        
        if widget in self.focused_widgets:
            # Remove focus indicator
            self._hide_focus_indicator(widget)
            
            # Notify callbacks
            for callback in self.focus_callbacks:
                try:
                    callback('focus_out', widget)
                except:
                    pass
    
    def _show_focus_indicator(self, widget: tk.Widget):
        """Show focus indicator for widget."""
        if not self.use_focus_rings:
            return
        
        widget_info = self.focused_widgets.get(widget, {})
        if not widget_info.get('focus_ring', True):
            return
        
        try:
            # Method 1: Try to use widget's built-in highlight
            widget.configure(
                highlightthickness=self.focus_ring_width,
                highlightcolor=self.focus_ring_color,
                highlightbackground=self.focus_ring_color
            )
        except:
            try:
                # Method 2: Try to modify border/relief
                widget.configure(
                    relief='solid',
                    borderwidth=self.focus_ring_width,
                    bd=self.focus_ring_width
                )
            except:
                # Method 3: Create overlay focus ring (more complex)
                self._create_focus_ring_overlay(widget)
    
    def _hide_focus_indicator(self, widget: tk.Widget):
        """Hide focus indicator for widget."""
        try:
            # Restore original highlight settings
            widget.configure(
                highlightthickness=0,
                highlightcolor='SystemButtonFace',
                highlightbackground='SystemButtonFace'
            )
        except:
            try:
                # Restore original border
                original_config = self.focused_widgets[widget]['original_config']
                widget.configure(
                    relief=original_config.get('relief', 'flat'),
                    borderwidth=original_config.get('borderwidth', 0)
                )
            except:
                pass
        
        # Remove focus ring overlay if present
        self._remove_focus_ring(widget)
    
    def _create_focus_ring_overlay(self, widget: tk.Widget):
        """Create a focus ring overlay for widgets that don't support highlighting."""
        try:
            parent = widget.winfo_parent()
            if not parent:
                return
            
            parent_widget = self.root.nametowidget(parent)
            
            # Get widget position and size
            x = widget.winfo_x()
            y = widget.winfo_y()
            width = widget.winfo_width()
            height = widget.winfo_height()
            
            # Create focus ring frame
            focus_ring = tk.Frame(
                parent_widget,
                bg=self.focus_ring_color,
                width=width + (self.focus_ring_offset * 2),
                height=height + (self.focus_ring_offset * 2)
            )
            
            # Position behind the widget
            focus_ring.place(
                x=x - self.focus_ring_offset,
                y=y - self.focus_ring_offset
            )
            
            # Lower it so widget appears on top
            focus_ring.lower(widget)
            
            # Store reference
            self.focus_indicators[widget] = focus_ring
            
        except Exception as e:
            print(f"Focus ring overlay creation failed: {e}")
    
    def _remove_focus_ring(self, widget: tk.Widget):
        """Remove focus ring overlay."""
        if widget in self.focus_indicators:
            try:
                self.focus_indicators[widget].destroy()
                del self.focus_indicators[widget]
            except:
                pass
    
    def _announce_focus_change(self, widget: tk.Widget):
        """Announce focus change to screen readers."""
        try:
            from .screen_reader import ScreenReaderSupport
            screen_reader = ScreenReaderSupport()
            
            widget_info = self.focused_widgets.get(widget, {})
            aria_label = widget_info.get('aria_label', '')
            role = widget_info.get('role', '')
            
            if aria_label:
                message = aria_label
            else:
                # Generate description from widget
                message = self._generate_widget_description(widget)
            
            if role:
                message = f"{role}, {message}"
            
            screen_reader.announce(message, priority='polite')
            
        except Exception as e:
            print(f"Focus announcement failed: {e}")
    
    def _generate_widget_description(self, widget: tk.Widget) -> str:
        """Generate accessible description for widget."""
        try:
            widget_class = widget.__class__.__name__
            description_parts = []
            
            # Widget type
            type_map = {
                'Button': 'button',
                'Entry': 'text input',
                'Text': 'text area',
                'Listbox': 'list',
                'Checkbutton': 'checkbox',
                'Radiobutton': 'radio button',
                'Scale': 'slider',
                'Combobox': 'combo box'
            }
            
            widget_type = type_map.get(widget_class, widget_class.lower())
            description_parts.append(widget_type)
            
            # Widget text/value
            for attr in ['text', 'textvariable']:
                try:
                    value = widget.cget(attr)
                    if value:
                        if hasattr(value, 'get'):
                            text = value.get()
                        else:
                            text = str(value)
                        if text.strip():
                            description_parts.append(text.strip())
                            break
                except:
                    pass
            
            # Widget state
            try:
                state = widget.cget('state')
                if state == 'disabled':
                    description_parts.append('disabled')
            except:
                pass
            
            return ', '.join(description_parts)
        except:
            return widget.__class__.__name__
    
    # Keyboard navigation event handlers
    def _on_tab(self, event):
        """Handle Tab key for forward navigation."""
        if not self.tab_order:
            return
        
        current = event.widget
        if current in self.tab_order:
            current_index = self.tab_order.index(current)
            next_index = (current_index + 1) % len(self.tab_order)
            next_widget = self.tab_order[next_index]
            
            # Focus next widget
            try:
                next_widget.focus_set()
                return 'break'  # Prevent default tab behavior
            except:
                pass
    
    def _on_shift_tab(self, event):
        """Handle Shift+Tab for backward navigation."""
        if not self.tab_order:
            return
        
        current = event.widget
        if current in self.tab_order:
            current_index = self.tab_order.index(current)
            prev_index = (current_index - 1) % len(self.tab_order)
            prev_widget = self.tab_order[prev_index]
            
            # Focus previous widget
            try:
                prev_widget.focus_set()
                return 'break'  # Prevent default behavior
            except:
                pass
    
    def _on_arrow_up(self, event):
        """Handle Up arrow key navigation."""
        return self._handle_arrow_navigation(event, 'up')
    
    def _on_arrow_down(self, event):
        """Handle Down arrow key navigation."""
        return self._handle_arrow_navigation(event, 'down')
    
    def _on_arrow_left(self, event):
        """Handle Left arrow key navigation."""
        return self._handle_arrow_navigation(event, 'left')
    
    def _on_arrow_right(self, event):
        """Handle Right arrow key navigation."""
        return self._handle_arrow_navigation(event, 'right')
    
    def _handle_arrow_navigation(self, event, direction: str):
        """Handle arrow key navigation within containers."""
        widget = event.widget
        
        # Only handle for specific widget types
        if isinstance(widget, (tk.Listbox, ttk.Treeview)):
            # Let these widgets handle their own arrow navigation
            return
        
        # For other widgets, implement custom arrow navigation
        if widget in self.tab_order and len(self.tab_order) > 1:
            current_index = self.tab_order.index(widget)
            
            if direction in ['up', 'left']:
                # Navigate backward
                next_index = (current_index - 1) % len(self.tab_order)
            else:  # down, right
                # Navigate forward
                next_index = (current_index + 1) % len(self.tab_order)
            
            next_widget = self.tab_order[next_index]
            try:
                next_widget.focus_set()
                return 'break'
            except:
                pass
    
    def _on_home(self, event):
        """Handle Home key - focus first widget."""
        if self.tab_order:
            try:
                self.tab_order[0].focus_set()
                return 'break'
            except:
                pass
    
    def _on_end(self, event):
        """Handle End key - focus last widget."""
        if self.tab_order:
            try:
                self.tab_order[-1].focus_set()
                return 'break'
            except:
                pass
    
    def focus_first(self):
        """Focus the first focusable widget."""
        if self.tab_order:
            try:
                self.tab_order[0].focus_set()
            except:
                pass
    
    def focus_last(self):
        """Focus the last focusable widget."""
        if self.tab_order:
            try:
                self.tab_order[-1].focus_set()
            except:
                pass
    
    def focus_next(self, current_widget: Optional[tk.Widget] = None):
        """Focus the next widget in tab order."""
        if not current_widget:
            current_widget = self.root.focus_get()
        
        if current_widget and current_widget in self.tab_order:
            current_index = self.tab_order.index(current_widget)
            next_index = (current_index + 1) % len(self.tab_order)
            try:
                self.tab_order[next_index].focus_set()
            except:
                pass
    
    def focus_previous(self, current_widget: Optional[tk.Widget] = None):
        """Focus the previous widget in tab order."""
        if not current_widget:
            current_widget = self.root.focus_get()
        
        if current_widget and current_widget in self.tab_order:
            current_index = self.tab_order.index(current_widget)
            prev_index = (current_index - 1) % len(self.tab_order)
            try:
                self.tab_order[prev_index].focus_set()
            except:
                pass
    
    def set_focus_ring_style(self, width: int = 3, color: str = '#0078D4', offset: int = 2):
        """Set focus ring visual style."""
        self.focus_ring_width = width
        self.focus_ring_color = color
        self.focus_ring_offset = offset
    
    def enable_focus_rings(self, enabled: bool = True):
        """Enable or disable visual focus rings."""
        self.use_focus_rings = enabled
    
    def add_focus_callback(self, callback: Callable[[str, tk.Widget], None]):
        """Add callback for focus events."""
        self.focus_callbacks.append(callback)
    
    def remove_focus_callback(self, callback: Callable):
        """Remove focus event callback."""
        if callback in self.focus_callbacks:
            self.focus_callbacks.remove(callback)
    
    def get_focus_order(self) -> List[str]:
        """Get current focus order as list of widget names."""
        return [str(widget) for widget in self.tab_order]
    
    def validate_tab_order(self) -> List[str]:
        """Validate current tab order and return issues."""
        issues = []
        
        # Check for destroyed widgets
        valid_widgets = []
        for widget in self.tab_order:
            try:
                widget.winfo_exists()
                valid_widgets.append(widget)
            except:
                issues.append(f"Widget {widget} no longer exists")
        
        self.tab_order = valid_widgets
        
        # Check for widgets that should be focusable but aren't in order
        for widget, info in self.focused_widgets.items():
            if info['focusable'] and not info['skip_tab'] and widget not in self.tab_order:
                issues.append(f"Focusable widget {widget} not in tab order")
        
        return issues