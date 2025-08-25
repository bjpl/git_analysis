"""
Virtual scrolling implementation for large lists.
"""

import tkinter as tk
from tkinter import ttk
import math
from typing import List, Callable, Optional, Any, Tuple
from dataclasses import dataclass


@dataclass
class VirtualItem:
    """Represents an item in the virtual scroll list."""
    index: int
    data: Any
    height: int = 50  # Default item height
    widget: Optional[tk.Widget] = None


class VirtualScrollManager:
    """
    Virtual scrolling manager for efficiently displaying large lists.
    
    Only renders visible items plus a buffer, dramatically reducing
    memory usage and improving performance for large datasets.
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        item_height: int = 50,
        buffer_size: int = 5,
        create_item_func: Optional[Callable[[Any, tk.Widget], tk.Widget]] = None
    ):
        """
        Initialize virtual scroll manager.
        
        Args:
            parent: Parent widget to contain the scrollable area
            item_height: Height of each item in pixels
            buffer_size: Number of extra items to render above/below visible area
            create_item_func: Function to create widget for item data
        """
        self.parent = parent
        self.item_height = item_height
        self.buffer_size = buffer_size
        self.create_item_func = create_item_func or self._default_create_item
        
        # Data
        self.items: List[Any] = []
        self.virtual_items: List[VirtualItem] = []
        self.visible_widgets: List[tk.Widget] = []
        
        # Scroll state
        self.scroll_top = 0
        self.visible_start = 0
        self.visible_end = 0
        self.container_height = 0
        
        # UI components
        self.canvas: Optional[tk.Canvas] = None
        self.scrollbar: Optional[ttk.Scrollbar] = None
        self.content_frame: Optional[tk.Frame] = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the scrollable UI components."""
        # Create canvas for scrolling
        self.canvas = tk.Canvas(self.parent, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create scrollbar
        self.scrollbar = ttk.Scrollbar(
            self.parent, 
            orient="vertical", 
            command=self._on_scrollbar
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Create content frame
        self.content_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(
            0, 0, anchor="nw", window=self.content_frame
        )
        
        # Bind events
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)  # Linux
        self.canvas.bind("<Button-5>", self._on_mousewheel)  # Linux
        
        # Make canvas focusable for keyboard events
        self.canvas.bind("<Key>", self._on_key)
        self.canvas.focus_set()
        
    def set_items(self, items: List[Any]):
        """Set the list of items to display."""
        self.items = items
        self.virtual_items = [
            VirtualItem(i, item, self.item_height)
            for i, item in enumerate(items)
        ]
        self._update_scroll_region()
        self._render_visible_items()
        
    def add_item(self, item: Any):
        """Add a single item to the list."""
        self.items.append(item)
        virtual_item = VirtualItem(len(self.virtual_items), item, self.item_height)
        self.virtual_items.append(virtual_item)
        self._update_scroll_region()
        self._render_visible_items()
        
    def remove_item(self, index: int):
        """Remove item at specified index."""
        if 0 <= index < len(self.items):
            del self.items[index]
            del self.virtual_items[index]
            
            # Update indices
            for i in range(index, len(self.virtual_items)):
                self.virtual_items[i].index = i
                
            self._update_scroll_region()
            self._render_visible_items()
            
    def clear_items(self):
        """Clear all items."""
        self.items.clear()
        self.virtual_items.clear()
        self._clear_widgets()
        self._update_scroll_region()
        
    def _update_scroll_region(self):
        """Update the scroll region based on total content height."""
        total_height = len(self.virtual_items) * self.item_height
        self.canvas.configure(scrollregion=(0, 0, 0, total_height))
        
    def _render_visible_items(self):
        """Render only the currently visible items."""
        if not self.virtual_items:
            return
            
        # Calculate visible range
        canvas_height = self.canvas.winfo_height()
        if canvas_height <= 1:  # Canvas not initialized yet
            self.parent.after(100, self._render_visible_items)
            return
            
        self.container_height = canvas_height
        
        # Calculate which items should be visible
        scroll_top = self.canvas.canvasy(0)
        scroll_bottom = scroll_top + canvas_height
        
        start_index = max(0, int(scroll_top // self.item_height) - self.buffer_size)
        end_index = min(
            len(self.virtual_items),
            int(scroll_bottom // self.item_height) + self.buffer_size + 1
        )
        
        # Only re-render if visible range changed significantly
        if (abs(start_index - self.visible_start) > self.buffer_size or 
            abs(end_index - self.visible_end) > self.buffer_size):
            
            self.visible_start = start_index
            self.visible_end = end_index
            
            # Clear existing widgets
            self._clear_widgets()
            
            # Create widgets for visible items
            for i in range(start_index, end_index):
                if i < len(self.virtual_items):
                    self._create_item_widget(i)
                    
    def _create_item_widget(self, index: int):
        """Create widget for item at specified index."""
        virtual_item = self.virtual_items[index]
        
        if virtual_item.widget:
            # Widget already exists, just make sure it's positioned correctly
            y_pos = index * self.item_height
            virtual_item.widget.place(y=y_pos)
        else:
            # Create new widget
            widget = self.create_item_func(virtual_item.data, self.content_frame)
            virtual_item.widget = widget
            self.visible_widgets.append(widget)
            
            # Position the widget
            y_pos = index * self.item_height
            widget.place(x=0, y=y_pos, relwidth=1, height=self.item_height)
            
    def _clear_widgets(self):
        """Clear all visible widgets."""
        for widget in self.visible_widgets:
            widget.destroy()
        self.visible_widgets.clear()
        
        # Clear widget references in virtual items
        for virtual_item in self.virtual_items:
            virtual_item.widget = None
            
    def _default_create_item(self, data: Any, parent: tk.Widget) -> tk.Widget:
        """Default item creation function."""
        frame = tk.Frame(parent, relief=tk.RAISED, borderwidth=1)
        label = tk.Label(frame, text=str(data), anchor="w")
        label.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        return frame
        
    def _on_canvas_configure(self, event):
        """Handle canvas resize."""
        # Update content frame width
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        # Re-render visible items if container size changed
        if abs(event.height - self.container_height) > 10:
            self._render_visible_items()
            
    def _on_scrollbar(self, *args):
        """Handle scrollbar events."""
        self.canvas.yview(*args)
        self._render_visible_items()
        
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if event.delta:
            # Windows
            delta = -1 * (event.delta / 120)
        else:
            # Linux
            delta = -1 if event.num == 4 else 1
            
        self.canvas.yview_scroll(int(delta), "units")
        self._render_visible_items()
        
    def _on_key(self, event):
        """Handle keyboard navigation."""
        if event.keysym == "Up":
            self.canvas.yview_scroll(-1, "units")
            self._render_visible_items()
        elif event.keysym == "Down":
            self.canvas.yview_scroll(1, "units")
            self._render_visible_items()
        elif event.keysym == "Page_Up":
            self.canvas.yview_scroll(-10, "units")
            self._render_visible_items()
        elif event.keysym == "Page_Down":
            self.canvas.yview_scroll(10, "units")
            self._render_visible_items()
        elif event.keysym == "Home":
            self.canvas.yview_moveto(0)
            self._render_visible_items()
        elif event.keysym == "End":
            self.canvas.yview_moveto(1)
            self._render_visible_items()
            
    def scroll_to_item(self, index: int):
        """Scroll to make the specified item visible."""
        if 0 <= index < len(self.virtual_items):
            total_height = len(self.virtual_items) * self.item_height
            item_y = index * self.item_height
            
            if total_height > 0:
                fraction = item_y / total_height
                self.canvas.yview_moveto(fraction)
                self._render_visible_items()
                
    def get_visible_range(self) -> Tuple[int, int]:
        """Get the range of currently visible items."""
        return (self.visible_start, self.visible_end)
        
    def get_stats(self) -> dict:
        """Get virtual scrolling statistics."""
        return {
            'total_items': len(self.virtual_items),
            'visible_items': len(self.visible_widgets),
            'visible_range': (self.visible_start, self.visible_end),
            'memory_efficiency': (
                len(self.visible_widgets) / max(1, len(self.virtual_items)) * 100
            ),
            'item_height': self.item_height,
            'buffer_size': self.buffer_size
        }
        
    def set_item_height(self, height: int):
        """Update item height and re-render."""
        self.item_height = height
        for virtual_item in self.virtual_items:
            virtual_item.height = height
        self._update_scroll_region()
        self._render_visible_items()
        
    def refresh(self):
        """Force refresh of visible items."""
        self._render_visible_items()


# Utility function to create a virtual scroll widget
def create_virtual_listbox(
    parent: tk.Widget,
    items: List[Any],
    item_height: int = 30,
    create_item_func: Optional[Callable] = None
) -> VirtualScrollManager:
    """
    Create a virtual scrolling listbox.
    
    Args:
        parent: Parent widget
        items: List of items to display
        item_height: Height of each item
        create_item_func: Function to create item widgets
        
    Returns:
        VirtualScrollManager instance
    """
    # Create frame for the virtual scroll widget
    scroll_frame = tk.Frame(parent)
    
    # Create virtual scroll manager
    virtual_scroll = VirtualScrollManager(
        scroll_frame,
        item_height,
        create_item_func=create_item_func
    )
    
    # Set initial items
    virtual_scroll.set_items(items)
    
    return virtual_scroll, scroll_frame