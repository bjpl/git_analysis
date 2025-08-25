"""
Interactive tour system with contextual hints and progressive disclosure
Guides users through the main features of the application
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, List, Dict, Any, Tuple
import time
from dataclasses import dataclass
from enum import Enum


class TourStep(Enum):
    """Different types of tour steps"""
    HIGHLIGHT = "highlight"
    TOOLTIP = "tooltip"
    MODAL = "modal"
    OVERLAY = "overlay"


@dataclass
class TourPoint:
    """Defines a single point in the tour"""
    id: str
    title: str
    content: str
    target_widget: str  # Widget identifier or path
    step_type: TourStep = TourStep.HIGHLIGHT
    position: str = "auto"  # "top", "bottom", "left", "right", "auto"
    action_text: str = "Next"
    is_interactive: bool = False
    wait_for_action: bool = False
    prerequisites: List[str] = None
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []


class TourHighlight:
    """Creates highlighted overlays and tooltips for tour steps"""
    
    def __init__(self, parent: tk.Widget, theme_manager):
        self.parent = parent
        self.theme_manager = theme_manager
        self.overlay = None
        self.tooltip = None
        self.highlight_frame = None
    
    def highlight_widget(self, widget: tk.Widget, tour_point: TourPoint):
        """Create a highlight overlay for a widget"""
        if not widget:
            return
        
        colors = self.theme_manager.get_colors()
        
        # Get widget position and size
        widget.update_idletasks()
        x = widget.winfo_rootx() - self.parent.winfo_rootx()
        y = widget.winfo_rooty() - self.parent.winfo_rooty()
        width = widget.winfo_width()
        height = widget.winfo_height()
        
        # Create overlay that covers entire parent
        if self.overlay:
            self.overlay.destroy()
        
        self.overlay = tk.Frame(
            self.parent,
            bg='black'
        )
        self.overlay.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Make overlay semi-transparent effect by using stipple
        self.overlay.configure(bg=colors['bg'])
        self.overlay.bind("<Button-1>", lambda e: None)  # Capture clicks
        
        # Create highlight frame around target widget
        if self.highlight_frame:
            self.highlight_frame.destroy()
        
        padding = 8
        self.highlight_frame = tk.Frame(
            self.overlay,
            bg=colors['select_bg'],
            relief=tk.RAISED,
            borderwidth=3
        )
        self.highlight_frame.place(
            x=x-padding, 
            y=y-padding,
            width=width + 2*padding,
            height=height + 2*padding
        )
        
        # Create inner frame to "cut out" the widget area
        inner_frame = tk.Frame(
            self.highlight_frame,
            bg=colors['bg']
        )
        inner_frame.place(x=3, y=3, width=width + 2*padding - 6, height=height + 2*padding - 6)
        
        # Create tooltip
        self._create_tooltip(tour_point, x, y, width, height)
        
        # Bring target widget to front
        widget.lift()
        
        # Pulse effect
        self._start_pulse_effect()
    
    def _create_tooltip(self, tour_point: TourPoint, x: int, y: int, width: int, height: int):
        """Create tooltip for the tour point"""
        colors = self.theme_manager.get_colors()
        
        if self.tooltip:
            self.tooltip.destroy()
        
        # Calculate tooltip position
        tooltip_x, tooltip_y = self._calculate_tooltip_position(
            x, y, width, height, tour_point.position
        )
        
        # Create tooltip frame
        self.tooltip = tk.Frame(
            self.overlay,
            bg=colors['tooltip_bg'],
            relief=tk.RAISED,
            borderwidth=1
        )
        self.tooltip.place(x=tooltip_x, y=tooltip_y)
        
        # Header with title
        header_frame = tk.Frame(self.tooltip, bg=colors['select_bg'])
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame,
            text=tour_point.title,
            font=('TkDefaultFont', 10, 'bold'),
            bg=colors['select_bg'],
            fg=colors['select_fg'],
            padx=15,
            pady=8
        )
        title_label.pack()
        
        # Content area
        content_frame = tk.Frame(self.tooltip, bg=colors['tooltip_bg'], padx=15, pady=10)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        content_label = tk.Label(
            content_frame,
            text=tour_point.content,
            font=('TkDefaultFont', 9),
            bg=colors['tooltip_bg'],
            fg=colors['tooltip_fg'],
            justify=tk.LEFT,
            wraplength=250
        )
        content_label.pack(anchor=tk.W)
        
        # Add pointer arrow
        self._add_tooltip_arrow(tour_point.position)
    
    def _calculate_tooltip_position(self, x: int, y: int, width: int, height: int, 
                                   position: str) -> Tuple[int, int]:
        """Calculate optimal tooltip position"""
        tooltip_width = 300
        tooltip_height = 120
        margin = 15
        
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        if position == "auto":
            # Auto-calculate best position
            if y > tooltip_height + margin:
                position = "top"
            elif y + height + tooltip_height + margin < parent_height:
                position = "bottom"
            elif x > tooltip_width + margin:
                position = "left"
            else:
                position = "right"
        
        if position == "top":
            tooltip_x = max(0, min(x + width//2 - tooltip_width//2, parent_width - tooltip_width))
            tooltip_y = max(0, y - tooltip_height - margin)
        elif position == "bottom":
            tooltip_x = max(0, min(x + width//2 - tooltip_width//2, parent_width - tooltip_width))
            tooltip_y = min(y + height + margin, parent_height - tooltip_height)
        elif position == "left":
            tooltip_x = max(0, x - tooltip_width - margin)
            tooltip_y = max(0, min(y + height//2 - tooltip_height//2, parent_height - tooltip_height))
        else:  # right
            tooltip_x = min(x + width + margin, parent_width - tooltip_width)
            tooltip_y = max(0, min(y + height//2 - tooltip_height//2, parent_height - tooltip_height))
        
        return tooltip_x, tooltip_y
    
    def _add_tooltip_arrow(self, position: str):
        """Add arrow pointing to target widget"""
        # Simple arrow using Unicode characters
        colors = self.theme_manager.get_colors()
        
        if position in ["top", "auto"]:
            arrow_text = "▼"
        elif position == "bottom":
            arrow_text = "▲"
        elif position == "left":
            arrow_text = "►"
        else:
            arrow_text = "◄"
        
        arrow_label = tk.Label(
            self.tooltip,
            text=arrow_text,
            font=('TkDefaultFont', 12),
            bg=colors['tooltip_bg'],
            fg=colors['select_bg']
        )
        
        if position == "top":
            arrow_label.pack(side=tk.BOTTOM)
        elif position == "bottom":
            arrow_label.pack(side=tk.TOP)
    
    def _start_pulse_effect(self):
        """Create subtle pulse effect for highlight"""
        if not self.highlight_frame:
            return
        
        def pulse(alpha=1.0, direction=-1):
            if not self.highlight_frame:
                return
            
            colors = self.theme_manager.get_colors()
            
            # Cycle between normal and brighter colors
            if alpha <= 0.3:
                direction = 1
            elif alpha >= 1.0:
                direction = -1
            
            alpha += direction * 0.05
            
            # Schedule next pulse
            self.parent.after(100, lambda: pulse(alpha, direction))
        
        pulse()
    
    def clear_highlight(self):
        """Remove all highlight elements"""
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
        if self.highlight_frame:
            self.highlight_frame.destroy()
            self.highlight_frame = None


class TourSystem:
    """
    Main tour system that guides users through the application
    """
    
    def __init__(self, parent: tk.Tk, theme_manager, 
                 on_completion: Callable = None, on_skip: Callable = None):
        self.parent = parent
        self.theme_manager = theme_manager
        self.on_completion = on_completion
        self.on_skip = on_skip
        
        self.current_step = 0
        self.is_active = False
        self.highlight_system = TourHighlight(parent, theme_manager)
        
        # Control panel
        self.control_panel = None
        
        # Tour points - defined in order
        self.tour_points = self._create_tour_points()
    
    def _create_tour_points(self) -> List[TourPoint]:
        """Define all tour points"""
        return [
            TourPoint(
                id="welcome",
                title="Welcome to Your Learning Journey!",
                content="This tour will show you how to search for images, generate AI descriptions, and build your Spanish vocabulary. Let's start!",
                target_widget="search_entry",
                step_type=TourStep.HIGHLIGHT,
                position="bottom"
            ),
            TourPoint(
                id="search_area",
                title="Search for Images",
                content="Enter any topic you want to explore in Spanish. Try 'comida', 'naturaleza', or 'ciudad'. Press Enter or click 'Buscar Imagen' to search.",
                target_widget="search_entry",
                step_type=TourStep.HIGHLIGHT,
                position="bottom",
                is_interactive=True
            ),
            TourPoint(
                id="image_display",
                title="Image Preview Area",
                content="Your searched images appear here. You can zoom in/out and scroll to explore details. The zoom controls are at the bottom.",
                target_widget="image_canvas",
                step_type=TourStep.HIGHLIGHT,
                position="right"
            ),
            TourPoint(
                id="notes_area",
                title="Add Your Notes",
                content="Write your own observations or questions about the image here. This helps provide context to the AI for better descriptions.",
                target_widget="note_text",
                step_type=TourStep.HIGHLIGHT,
                position="left"
            ),
            TourPoint(
                id="generate_description",
                title="Generate AI Description",
                content="Click this button to get a detailed Spanish description of your image. The AI analyzes what it sees and creates rich, educational content.",
                target_widget="generate_desc_button",
                step_type=TourStep.HIGHLIGHT,
                position="top"
            ),
            TourPoint(
                id="description_area",
                title="AI-Generated Description",
                content="The AI description appears here in natural Spanish. Pay attention to vocabulary, grammar structures, and cultural context.",
                target_widget="description_text",
                step_type=TourStep.HIGHLIGHT,
                position="left"
            ),
            TourPoint(
                id="extracted_phrases",
                title="Click Words to Learn",
                content="The AI automatically extracts useful vocabulary from the description. Click any blue word or phrase to add it to your learning list!",
                target_widget="extracted_frame",
                step_type=TourStep.HIGHLIGHT,
                position="top"
            ),
            TourPoint(
                id="vocabulary_list",
                title="Your Vocabulary Collection",
                content="Words you select appear here with English translations. This becomes your personal vocabulary list for studying.",
                target_widget="target_listbox",
                step_type=TourStep.HIGHLIGHT,
                position="top"
            ),
            TourPoint(
                id="export_options",
                title="Export Your Learning",
                content="Export your vocabulary to Anki, text files, or CSV for further study. Perfect for spaced repetition learning!",
                target_widget="export_button",
                step_type=TourStep.HIGHLIGHT,
                position="bottom"
            ),
            TourPoint(
                id="theme_toggle",
                title="Customize Your Experience",
                content="Switch between light and dark themes for comfortable viewing. Use Ctrl+T as a keyboard shortcut!",
                target_widget="theme_button",
                step_type=TourStep.HIGHLIGHT,
                position="bottom"
            ),
            TourPoint(
                id="completion",
                title="Tour Complete!",
                content="You're ready to start learning! Remember: you can always access help through F1 or the help menu. Enjoy building your Spanish vocabulary!",
                target_widget="search_entry",
                step_type=TourStep.MODAL
            )
        ]
    
    def start_tour(self):
        """Start the interactive tour"""
        if self.is_active:
            return
        
        self.is_active = True
        self.current_step = 0
        self._create_control_panel()
        self._show_current_step()
    
    def stop_tour(self):
        """Stop the tour and clean up"""
        self.is_active = False
        self.highlight_system.clear_highlight()
        
        if self.control_panel:
            self.control_panel.destroy()
            self.control_panel = None
    
    def _create_control_panel(self):
        """Create the tour control panel"""
        colors = self.theme_manager.get_colors()
        
        # Position at bottom of screen
        self.control_panel = tk.Frame(
            self.parent,
            bg=colors['frame_bg'],
            relief=tk.RAISED,
            borderwidth=1
        )
        self.control_panel.place(relx=0.5, rely=0.95, anchor=tk.S)
        
        # Progress indicator
        progress_text = f"Step {self.current_step + 1} of {len(self.tour_points)}"
        self.progress_label = tk.Label(
            self.control_panel,
            text=progress_text,
            font=('TkDefaultFont', 9),
            bg=colors['frame_bg'],
            fg=colors['fg'],
            padx=15,
            pady=5
        )
        self.progress_label.pack(side=tk.LEFT)
        
        # Control buttons
        button_frame = tk.Frame(self.control_panel, bg=colors['frame_bg'])
        button_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Skip button
        self.skip_button = tk.Button(
            button_frame,
            text="Skip Tour",
            command=self._skip_tour,
            font=('TkDefaultFont', 9),
            bg=colors['button_bg'],
            fg=colors['disabled_fg'],
            relief=tk.FLAT,
            padx=15
        )
        self.skip_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Previous button
        self.prev_button = tk.Button(
            button_frame,
            text="← Previous",
            command=self._previous_step,
            font=('TkDefaultFont', 9),
            bg=colors['button_bg'],
            fg=colors['button_fg'],
            relief=tk.FLAT,
            padx=15
        )
        self.prev_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Next button
        self.next_button = tk.Button(
            button_frame,
            text="Next →",
            command=self._next_step,
            font=('TkDefaultFont', 9, 'bold'),
            bg=colors['select_bg'],
            fg=colors['select_fg'],
            relief=tk.FLAT,
            padx=15
        )
        self.next_button.pack(side=tk.LEFT)
        
        self._update_control_panel()
    
    def _show_current_step(self):
        """Show the current tour step"""
        if not self.is_active or self.current_step >= len(self.tour_points):
            self._complete_tour()
            return
        
        tour_point = self.tour_points[self.current_step]
        
        # Find target widget
        target_widget = self._find_widget(tour_point.target_widget)
        
        if target_widget:
            if tour_point.step_type == TourStep.MODAL:
                self._show_modal_step(tour_point)
            else:
                self.highlight_system.highlight_widget(target_widget, tour_point)
        else:
            # Widget not found, skip to next step
            print(f"Warning: Widget '{tour_point.target_widget}' not found, skipping step")
            self._next_step()
        
        self._update_control_panel()
    
    def _show_modal_step(self, tour_point: TourPoint):
        """Show a modal dialog for special steps"""
        from ..theme_manager import ThemedMessageBox
        
        # Clear any existing highlights
        self.highlight_system.clear_highlight()
        
        # Show modal
        ThemedMessageBox.show_info(
            self.parent,
            tour_point.title,
            tour_point.content,
            self.theme_manager
        )
    
    def _find_widget(self, widget_path: str) -> Optional[tk.Widget]:
        """Find a widget by its attribute path"""
        try:
            # This assumes the main app has attributes matching widget_path
            # You might need to adjust this based on your app structure
            parts = widget_path.split('.')
            widget = self.parent
            
            for part in parts:
                widget = getattr(widget, part, None)
                if widget is None:
                    return None
            
            return widget
        except:
            return None
    
    def _next_step(self):
        """Go to next tour step"""
        self.current_step += 1
        self._show_current_step()
    
    def _previous_step(self):
        """Go to previous tour step"""
        if self.current_step > 0:
            self.current_step -= 1
            self._show_current_step()
    
    def _skip_tour(self):
        """Skip the entire tour"""
        self.stop_tour()
        if self.on_skip:
            self.on_skip()
    
    def _complete_tour(self):
        """Complete the tour"""
        self.stop_tour()
        if self.on_completion:
            self.on_completion()
    
    def _update_control_panel(self):
        """Update the control panel state"""
        if not self.control_panel:
            return
        
        # Update progress
        progress_text = f"Step {self.current_step + 1} of {len(self.tour_points)}"
        self.progress_label.config(text=progress_text)
        
        # Update button states
        self.prev_button.config(
            state=tk.NORMAL if self.current_step > 0 else tk.DISABLED
        )
        
        # Update next button text for last step
        if self.current_step == len(self.tour_points) - 1:
            self.next_button.config(text="Finish! ✓")
        else:
            self.next_button.config(text="Next →")
    
    def set_widget_finder(self, finder_func: Callable[[str], Optional[tk.Widget]]):
        """Set a custom widget finder function"""
        self._find_widget = finder_func
    
    def add_tour_point(self, tour_point: TourPoint):
        """Add a custom tour point"""
        self.tour_points.append(tour_point)
    
    def remove_tour_point(self, point_id: str):
        """Remove a tour point by ID"""
        self.tour_points = [tp for tp in self.tour_points if tp.id != point_id]
    
    def is_tour_active(self) -> bool:
        """Check if tour is currently active"""
        return self.is_active