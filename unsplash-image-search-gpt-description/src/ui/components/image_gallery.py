"""
Modern image gallery component with grid/list toggle, lazy loading, and smooth transitions.
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from typing import List, Dict, Callable, Optional, Any, Tuple
from enum import Enum
import threading
from io import BytesIO
import math

from ..styles import StyleManager, Easing


class GalleryView(Enum):
    """Gallery view types."""
    GRID = "grid"
    LIST = "list"
    MASONRY = "masonry"


class ImageItem:
    """Represents an image item in the gallery."""
    
    def __init__(self, image_id: str, url: str, thumbnail_url: str = None,
                 title: str = "", description: str = "", metadata: Dict = None):
        self.image_id = image_id
        self.url = url
        self.thumbnail_url = thumbnail_url or url
        self.title = title
        self.description = description
        self.metadata = metadata or {}
        
        # Loading state
        self.thumbnail_loaded = False
        self.full_image_loaded = False
        self.thumbnail_image: Optional[ImageTk.PhotoImage] = None
        self.full_image: Optional[ImageTk.PhotoImage] = None
        self.loading = False


class ImageTile(tk.Frame):
    """Individual image tile in the gallery."""
    
    def __init__(self, parent: tk.Widget, item: ImageItem, 
                 style_manager: StyleManager, view_mode: GalleryView,
                 on_click: Callable[[ImageItem], None] = None,
                 on_hover: Callable[[ImageItem, bool], None] = None):
        super().__init__(parent)
        
        self.item = item
        self.style_manager = style_manager
        self.view_mode = view_mode
        self.on_click = on_click
        self.on_hover = on_hover
        
        self.is_hovered = False
        self.is_selected = False
        
        self._create_widgets()
        self._setup_bindings()
        
        # Register with style manager
        classes = ['frame', 'image-tile', f'view-{view_mode.value}']
        self.style_manager.register_widget(self, classes=classes)
    
    def _create_widgets(self):
        """Create tile widgets based on view mode."""
        if self.view_mode == GalleryView.GRID:
            self._create_grid_layout()
        elif self.view_mode == GalleryView.LIST:
            self._create_list_layout()
        else:  # MASONRY
            self._create_masonry_layout()
    
    def _create_grid_layout(self):
        """Create grid view layout."""
        # Main container
        self.configure(
            relief='flat',
            borderwidth=1,
            bg=self.style_manager.theme.colors.surface
        )
        
        # Image container with aspect ratio preservation
        self.image_frame = tk.Frame(
            self, 
            width=200, 
            height=150,
            bg=self.style_manager.theme.colors.surface_variant
        )
        self.image_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.image_frame.pack_propagate(False)
        
        # Image label (placeholder initially)
        self.image_label = tk.Label(
            self.image_frame,
            text="🖼",
            font=('Segoe UI', 24),
            bg=self.style_manager.theme.colors.surface_variant,
            fg=self.style_manager.theme.colors.outline
        )
        self.image_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Loading indicator
        self.loading_label = tk.Label(
            self.image_frame,
            text="⟳",
            font=('Segoe UI', 16),
            bg=self.style_manager.theme.colors.surface_variant,
            fg=self.style_manager.theme.colors.primary
        )
        
        # Title overlay (appears on hover)
        self.title_overlay = tk.Frame(
            self.image_frame,
            bg=self.style_manager.theme.colors.inverse_surface + '90',  # Semi-transparent
            height=40
        )
        
        self.title_label = tk.Label(
            self.title_overlay,
            text=self.item.title or "Untitled",
            font=('Segoe UI', 10, 'bold'),
            bg=self.style_manager.theme.colors.inverse_surface + '90',
            fg=self.style_manager.theme.colors.inverse_on_surface,
            wraplength=180
        )
        self.title_label.pack(expand=True, pady=5)
        
        # Initially hide overlay
        self.title_overlay.place_forget()
    
    def _create_list_layout(self):
        """Create list view layout."""
        self.configure(
            relief='flat',
            borderwidth=1,
            bg=self.style_manager.theme.colors.surface,
            height=80
        )
        self.pack_propagate(False)
        
        # Thumbnail (small, left side)
        self.thumbnail_frame = tk.Frame(
            self, 
            width=60, 
            height=60,
            bg=self.style_manager.theme.colors.surface_variant
        )
        self.thumbnail_frame.pack(side='left', padx=10, pady=10)
        self.thumbnail_frame.pack_propagate(False)
        
        self.image_label = tk.Label(
            self.thumbnail_frame,
            text="🖼",
            font=('Segoe UI', 16),
            bg=self.style_manager.theme.colors.surface_variant,
            fg=self.style_manager.theme.colors.outline
        )
        self.image_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Content (right side)
        content_frame = tk.Frame(
            self,
            bg=self.style_manager.theme.colors.surface
        )
        content_frame.pack(side='left', fill='both', expand=True, padx=(0, 10), pady=10)
        
        # Title
        self.title_label = tk.Label(
            content_frame,
            text=self.item.title or "Untitled",
            font=('Segoe UI', 12, 'bold'),
            bg=self.style_manager.theme.colors.surface,
            fg=self.style_manager.theme.colors.on_surface,
            anchor='w'
        )
        self.title_label.pack(anchor='w', fill='x')
        
        # Description
        if self.item.description:
            desc_text = self.item.description[:100] + "..." if len(self.item.description) > 100 else self.item.description
            self.desc_label = tk.Label(
                content_frame,
                text=desc_text,
                font=('Segoe UI', 10),
                bg=self.style_manager.theme.colors.surface,
                fg=self.style_manager.theme.colors.outline,
                anchor='w',
                wraplength=300,
                justify='left'
            )
            self.desc_label.pack(anchor='w', fill='x', pady=(2, 0))
        
        # Metadata
        if self.item.metadata:
            metadata_text = " • ".join([f"{k}: {v}" for k, v in list(self.item.metadata.items())[:3]])
            self.metadata_label = tk.Label(
                content_frame,
                text=metadata_text,
                font=('Segoe UI', 9),
                bg=self.style_manager.theme.colors.surface,
                fg=self.style_manager.theme.colors.outline,
                anchor='w'
            )
            self.metadata_label.pack(anchor='w', fill='x', pady=(2, 0))
    
    def _create_masonry_layout(self):
        """Create masonry view layout (variable height)."""
        # Similar to grid but with dynamic height based on image aspect ratio
        self._create_grid_layout()
        
        # Adjust height based on content
        if self.item.metadata and 'aspect_ratio' in self.item.metadata:
            aspect_ratio = self.item.metadata['aspect_ratio']
            new_height = int(200 / aspect_ratio) if aspect_ratio > 0 else 150
            self.image_frame.configure(height=new_height)
    
    def _setup_bindings(self):
        """Setup event bindings."""
        # Bind to all relevant widgets for consistent interaction
        widgets_to_bind = [self, self.image_frame, self.image_label]
        if hasattr(self, 'title_label'):
            widgets_to_bind.append(self.title_label)
        
        for widget in widgets_to_bind:
            widget.bind('<Button-1>', self._on_click)
            widget.bind('<Enter>', self._on_enter)
            widget.bind('<Leave>', self._on_leave)
    
    def _on_click(self, event):
        """Handle click event."""
        if self.on_click:
            self.on_click(self.item)
    
    def _on_enter(self, event):
        """Handle mouse enter."""
        if not self.is_hovered:
            self.is_hovered = True
            self._update_hover_state()
            
            if self.on_hover:
                self.on_hover(self.item, True)
    
    def _on_leave(self, event):
        """Handle mouse leave."""
        if self.is_hovered:
            self.is_hovered = False
            self._update_hover_state()
            
            if self.on_hover:
                self.on_hover(self.item, False)
    
    def _update_hover_state(self):
        """Update visual state based on hover."""
        if self.view_mode == GalleryView.GRID:
            if self.is_hovered:
                # Show title overlay
                self.title_overlay.place(x=0, y=0, relwidth=1, height=40)
                
                # Animate scale up
                self.style_manager.animate_widget(
                    self, 'pulse', scale=1.02, duration=0.2
                )
                
                # Update border
                self.configure(
                    borderwidth=2,
                    highlightbackground=self.style_manager.theme.colors.primary,
                    highlightthickness=2
                )
            else:
                # Hide title overlay
                self.title_overlay.place_forget()
                
                # Reset border
                self.configure(
                    borderwidth=1,
                    highlightthickness=0
                )
        
        elif self.view_mode == GalleryView.LIST:
            if self.is_hovered:
                self.configure(bg=self.style_manager.theme.colors.surface_variant)
                # Update all child backgrounds
                self._update_child_backgrounds(self.style_manager.theme.colors.surface_variant)
            else:
                self.configure(bg=self.style_manager.theme.colors.surface)
                self._update_child_backgrounds(self.style_manager.theme.colors.surface)
    
    def _update_child_backgrounds(self, color: str):
        """Update background color of child widgets."""
        for child in self.winfo_children():
            try:
                if child.winfo_class() in ['Frame', 'Label']:
                    child.configure(bg=color)
            except:
                pass
    
    def load_thumbnail(self, image_data: bytes = None, image_url: str = None):
        """Load thumbnail image."""
        if self.item.loading:
            return
        
        self.item.loading = True
        
        # Show loading indicator
        if hasattr(self, 'loading_label'):
            self.loading_label.place(relx=0.5, rely=0.5, anchor='center')
            # Animate loading indicator
            self._animate_loading()
        
        # Load in background thread
        threading.Thread(
            target=self._load_thumbnail_worker,
            args=(image_data, image_url or self.item.thumbnail_url),
            daemon=True
        ).start()
    
    def _load_thumbnail_worker(self, image_data: bytes = None, url: str = None):
        """Worker thread for loading thumbnail."""
        try:
            if image_data:
                image = Image.open(BytesIO(image_data))
            else:
                # In a real implementation, you'd fetch from URL
                # For now, we'll create a placeholder
                image = self._create_placeholder_image()
            
            # Resize for thumbnail
            if self.view_mode == GalleryView.GRID:
                target_size = (190, 140)
            elif self.view_mode == GalleryView.LIST:
                target_size = (50, 50)
            else:  # Masonry
                aspect_ratio = image.width / image.height
                target_size = (190, int(190 / aspect_ratio))
            
            image.thumbnail(target_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Update UI in main thread
            self.after(0, self._update_thumbnail, photo)
            
        except Exception as e:
            print(f"Error loading thumbnail: {e}")
            self.after(0, self._thumbnail_error)
    
    def _create_placeholder_image(self) -> Image.Image:
        """Create placeholder image."""
        img = Image.new('RGB', (200, 150), color=self.style_manager.theme.colors.surface_variant)
        return img
    
    def _update_thumbnail(self, photo: ImageTk.PhotoImage):
        """Update thumbnail in main thread."""
        self.item.thumbnail_image = photo
        self.item.thumbnail_loaded = True
        self.item.loading = False
        
        # Hide loading indicator
        if hasattr(self, 'loading_label'):
            self.loading_label.place_forget()
        
        # Update image label
        self.image_label.configure(image=photo, text="")
        self.image_label.image = photo  # Keep reference
        
        # Animate fade in
        self.style_manager.animate_widget(
            self.image_label, 'fade_in', duration=0.3
        )
    
    def _thumbnail_error(self):
        """Handle thumbnail loading error."""
        self.item.loading = False
        
        # Hide loading indicator
        if hasattr(self, 'loading_label'):
            self.loading_label.place_forget()
        
        # Show error icon
        self.image_label.configure(
            text="❌",
            font=('Segoe UI', 20),
            fg=self.style_manager.theme.colors.error
        )
    
    def _animate_loading(self):
        """Animate loading indicator."""
        if hasattr(self, 'loading_label') and self.item.loading:
            # Simple rotation animation
            current_text = self.loading_label.cget('text')
            rotation_chars = ['⟳', '⟲', '⟳', '⟲']
            next_char = rotation_chars[(rotation_chars.index(current_text) + 1) % len(rotation_chars)]
            self.loading_label.configure(text=next_char)
            
            # Schedule next frame
            self.after(200, self._animate_loading)
    
    def set_selected(self, selected: bool):
        """Set selection state."""
        self.is_selected = selected
        
        if selected:
            self.configure(
                borderwidth=3,
                highlightbackground=self.style_manager.theme.colors.primary,
                highlightcolor=self.style_manager.theme.colors.primary,
                highlightthickness=3
            )
        else:
            self.configure(
                borderwidth=1,
                highlightthickness=0
            )
    
    def get_item(self) -> ImageItem:
        """Get the image item."""
        return self.item


class VirtualizedScrollFrame(tk.Frame):
    """Virtualized scrollable frame for large image collections."""
    
    def __init__(self, parent: tk.Widget, style_manager: StyleManager):
        super().__init__(parent)
        
        self.style_manager = style_manager
        self.items: List[ImageItem] = []
        self.visible_tiles: Dict[int, ImageTile] = {}
        self.view_mode = GalleryView.GRID
        
        # Viewport settings
        self.viewport_start = 0
        self.viewport_end = 0
        self.tile_height = 200  # Approximate tile height
        self.tiles_per_row = 4
        self.buffer_tiles = 5  # Extra tiles to render outside viewport
        
        self._create_widgets()
        self._setup_bindings()
    
    def _create_widgets(self):
        """Create scrollable container."""
        # Canvas for scrolling
        self.canvas = tk.Canvas(
            self,
            highlightthickness=0,
            bg=self.style_manager.theme.colors.background
        )
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        
        self.canvas.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # Container frame
        self.container = tk.Frame(self.canvas, bg=self.style_manager.theme.colors.background)
        self.canvas_window = self.canvas.create_window(0, 0, anchor="nw", window=self.container)
        
        # Layout
        self.canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
    
    def _setup_bindings(self):
        """Setup scrolling and resize bindings."""
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)
        self.bind_all('<Prior>', lambda e: self.canvas.yview_scroll(-1, "pages"))
        self.bind_all('<Next>', lambda e: self.canvas.yview_scroll(1, "pages"))
    
    def _on_canvas_configure(self, event):
        """Handle canvas resize."""
        # Update container width
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        # Recalculate tiles per row
        if self.view_mode == GalleryView.GRID:
            tile_width = 220  # Including padding
            self.tiles_per_row = max(1, canvas_width // tile_width)
        elif self.view_mode == GalleryView.LIST:
            self.tiles_per_row = 1
        
        # Update virtualization
        self._update_viewport()
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self._update_viewport()
    
    def set_items(self, items: List[ImageItem]):
        """Set gallery items."""
        self.items = items
        self._calculate_layout()
        self._update_viewport()
    
    def _calculate_layout(self):
        """Calculate layout dimensions."""
        if not self.items:
            return
        
        if self.view_mode == GalleryView.GRID:
            rows = math.ceil(len(self.items) / self.tiles_per_row)
            total_height = rows * self.tile_height
        elif self.view_mode == GalleryView.LIST:
            total_height = len(self.items) * 80  # List item height
        else:  # Masonry
            # More complex calculation needed for masonry
            total_height = len(self.items) * 180  # Approximate
        
        # Update scroll region
        self.canvas.configure(scrollregion=(0, 0, 0, total_height))
    
    def _update_viewport(self):
        """Update visible tiles based on viewport."""
        if not self.items:
            return
        
        # Get visible region
        canvas_height = self.canvas.winfo_height()
        scroll_top = self.canvas.canvasy(0)
        scroll_bottom = scroll_top + canvas_height
        
        # Calculate visible tile range
        if self.view_mode == GalleryView.GRID:
            start_row = max(0, int(scroll_top / self.tile_height) - self.buffer_tiles)
            end_row = min(
                math.ceil(len(self.items) / self.tiles_per_row),
                int(scroll_bottom / self.tile_height) + self.buffer_tiles
            )
            
            start_index = start_row * self.tiles_per_row
            end_index = min(len(self.items), (end_row + 1) * self.tiles_per_row)
            
        else:  # List view
            item_height = 80
            start_index = max(0, int(scroll_top / item_height) - self.buffer_tiles)
            end_index = min(len(self.items), int(scroll_bottom / item_height) + self.buffer_tiles)
        
        # Update visible tiles
        self._render_tiles(start_index, end_index)
    
    def _render_tiles(self, start_index: int, end_index: int):
        """Render tiles in the specified range."""
        # Remove tiles outside range
        to_remove = []
        for index, tile in self.visible_tiles.items():
            if index < start_index or index >= end_index:
                tile.destroy()
                to_remove.append(index)
        
        for index in to_remove:
            del self.visible_tiles[index]
        
        # Add new tiles
        for i in range(start_index, end_index):
            if i not in self.visible_tiles and i < len(self.items):
                item = self.items[i]
                tile = ImageTile(
                    self.container, item, self.style_manager, 
                    self.view_mode, self._on_tile_click, self._on_tile_hover
                )
                
                self._position_tile(tile, i)
                self.visible_tiles[i] = tile
                
                # Load thumbnail
                tile.load_thumbnail()
    
    def _position_tile(self, tile: ImageTile, index: int):
        """Position tile in the container."""
        if self.view_mode == GalleryView.GRID:
            row = index // self.tiles_per_row
            col = index % self.tiles_per_row
            
            x = col * 220
            y = row * self.tile_height
            
            tile.place(x=x, y=y, width=210, height=self.tile_height - 10)
            
        elif self.view_mode == GalleryView.LIST:
            y = index * 80
            tile.place(x=0, y=y, relwidth=1, height=80)
    
    def _on_tile_click(self, item: ImageItem):
        """Handle tile click."""
        # Implement tile selection/interaction
        print(f"Clicked on {item.title}")
    
    def _on_tile_hover(self, item: ImageItem, is_hovering: bool):
        """Handle tile hover."""
        if is_hovering:
            print(f"Hovering over {item.title}")
    
    def set_view_mode(self, view_mode: GalleryView):
        """Change view mode."""
        self.view_mode = view_mode
        
        # Clear existing tiles
        for tile in self.visible_tiles.values():
            tile.destroy()
        self.visible_tiles.clear()
        
        # Recalculate layout
        self._calculate_layout()
        self._update_viewport()


class ImageGallery(tk.Frame):
    """Main image gallery component with view controls."""
    
    def __init__(self, parent: tk.Widget, style_manager: StyleManager,
                 on_image_select: Callable[[ImageItem], None] = None,
                 on_view_change: Callable[[GalleryView], None] = None):
        super().__init__(parent)
        
        self.style_manager = style_manager
        self.on_image_select = on_image_select
        self.on_view_change = on_view_change
        
        self.current_view = GalleryView.GRID
        self.items: List[ImageItem] = []
        self.selected_item: Optional[ImageItem] = None
        
        self._create_widgets()
        
        # Register with style manager
        self.style_manager.register_widget(self, classes=['frame', 'image-gallery'])
    
    def _create_widgets(self):
        """Create gallery widgets."""
        # Header with view controls
        header = tk.Frame(self, height=50)
        header.pack(fill='x', padx=10, pady=5)
        header.pack_propagate(False)
        
        # Title
        title_label = self.style_manager.create_label(
            header, "Image Gallery", heading=2
        )
        title_label.pack(side='left', pady=10)
        
        # View controls
        view_controls = tk.Frame(header)
        view_controls.pack(side='right', pady=10)
        
        # View mode buttons
        self.grid_btn = self.style_manager.create_button(
            view_controls, "⊞", variant='text'
        )
        self.grid_btn.configure(command=lambda: self._set_view_mode(GalleryView.GRID))
        self.grid_btn.pack(side='left', padx=2)
        
        self.list_btn = self.style_manager.create_button(
            view_controls, "≡", variant='text'
        )
        self.list_btn.configure(command=lambda: self._set_view_mode(GalleryView.LIST))
        self.list_btn.pack(side='left', padx=2)
        
        # Results count
        self.count_label = self.style_manager.create_label(
            view_controls, "0 images"
        )
        self.count_label.pack(side='right', padx=(20, 0))
        
        # Separator
        separator = ttk.Separator(self, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=5)
        
        # Gallery container
        self.gallery_container = VirtualizedScrollFrame(self, self.style_manager)
        self.gallery_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Update initial view button state
        self._update_view_buttons()
    
    def _set_view_mode(self, view_mode: GalleryView):
        """Set gallery view mode."""
        if self.current_view != view_mode:
            self.current_view = view_mode
            self.gallery_container.set_view_mode(view_mode)
            self._update_view_buttons()
            
            if self.on_view_change:
                self.on_view_change(view_mode)
            
            # Animate view transition
            self.style_manager.animate_widget(
                self.gallery_container, 'fade_in', duration=0.3
            )
    
    def _update_view_buttons(self):
        """Update view button states."""
        # Reset all buttons
        for btn in [self.grid_btn, self.list_btn]:
            self.style_manager.remove_class(btn, 'active')
        
        # Highlight active button
        if self.current_view == GalleryView.GRID:
            self.style_manager.add_class(self.grid_btn, 'active')
        elif self.current_view == GalleryView.LIST:
            self.style_manager.add_class(self.list_btn, 'active')
    
    def set_images(self, items: List[ImageItem]):
        """Set gallery images."""
        self.items = items
        self.gallery_container.set_items(items)
        
        # Update count
        count_text = f"{len(items)} {'image' if len(items) == 1 else 'images'}"
        self.count_label.configure(text=count_text)
        
        # Clear selection
        self.selected_item = None
    
    def add_images(self, items: List[ImageItem]):
        """Add images to gallery (for pagination)."""
        self.items.extend(items)
        self.gallery_container.set_items(self.items)
        
        # Update count
        count_text = f"{len(self.items)} {'image' if len(self.items) == 1 else 'images'}"
        self.count_label.configure(text=count_text)
    
    def clear_images(self):
        """Clear all images."""
        self.items.clear()
        self.gallery_container.set_items([])
        self.count_label.configure(text="0 images")
        self.selected_item = None
    
    def get_selected_item(self) -> Optional[ImageItem]:
        """Get currently selected item."""
        return self.selected_item
    
    def set_loading(self, loading: bool):
        """Set loading state."""
        if loading:
            # Show loading overlay
            loading_overlay = tk.Label(
                self,
                text="Loading images...",
                font=('Segoe UI', 14),
                bg=self.style_manager.theme.colors.background + '80',  # Semi-transparent
                fg=self.style_manager.theme.colors.on_background
            )
            loading_overlay.place(relx=0.5, rely=0.5, anchor='center')
            self.loading_overlay = loading_overlay
        else:
            # Hide loading overlay
            if hasattr(self, 'loading_overlay'):
                self.loading_overlay.destroy()
                del self.loading_overlay