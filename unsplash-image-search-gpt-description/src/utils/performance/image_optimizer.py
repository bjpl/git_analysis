"""
Image loading and optimization utilities.
"""

import threading
import time
import weakref
from typing import Dict, Optional, Callable, Tuple, Any
from PIL import Image, ImageTk
import requests
from io import BytesIO
import tkinter as tk
from .memory_manager import MemoryManager
from .task_queue import TaskQueue, TaskPriority, create_image_download_task


class ProgressiveImageLoader:
    """
    Progressive image loading with multiple quality levels.
    """
    
    def __init__(self, memory_manager: MemoryManager, task_queue: TaskQueue):
        self.memory_manager = memory_manager
        self.task_queue = task_queue
        self.loading_tasks: Dict[str, str] = {}  # url -> task_id
        
    def load_progressive(
        self,
        base_url: str,
        callback: Callable[[Image.Image, str], None],
        error_callback: Optional[Callable[[Exception], None]] = None,
        sizes: Tuple[str, ...] = ('thumb', 'small', 'regular')
    ):
        """
        Load image progressively from thumbnail to full size.
        
        Args:
            base_url: Unsplash image URL template
            callback: Called with (image, quality_level) for each loaded size
            error_callback: Called on error
            sizes: Quality levels to load in order
        """
        def load_next_size(size_index=0):
            if size_index >= len(sizes):
                return
                
            size = sizes[size_index]
            # Replace URL size parameter
            url = base_url.replace('regular', size)
            cache_key = f"{url}_{size}"
            
            # Check cache first
            cached_data = self.memory_manager.get_image_from_cache(cache_key)
            if cached_data:
                try:
                    image = Image.open(BytesIO(cached_data))
                    callback(image, size)
                    # Continue to next size
                    load_next_size(size_index + 1)
                    return
                except Exception as e:
                    if error_callback:
                        error_callback(e)
                    return
            
            # Download image
            def on_success(data: bytes):
                try:
                    # Cache the data
                    self.memory_manager.put_image_in_cache(cache_key, data)
                    # Create image
                    image = Image.open(BytesIO(data))
                    callback(image, size)
                    # Continue to next size
                    load_next_size(size_index + 1)
                except Exception as e:
                    if error_callback:
                        error_callback(e)
                        
            def on_error(e: Exception):
                if error_callback:
                    error_callback(e)
                    
            # Submit download task
            task_function = create_image_download_task(url, on_success, on_error)
            task_id = self.task_queue.submit_task(
                f"Progressive load {size}",
                task_function,
                priority=TaskPriority.HIGH if size_index == 0 else TaskPriority.NORMAL,
                callback=on_success,
                error_callback=on_error
            )
            
            self.loading_tasks[cache_key] = task_id
            
        # Start loading from first size
        load_next_size()


class LazyImageLoader:
    """
    Lazy image loader that only loads images when needed.
    """
    
    def __init__(self, memory_manager: MemoryManager, task_queue: TaskQueue):
        self.memory_manager = memory_manager
        self.task_queue = task_queue
        self.placeholder_image: Optional[ImageTk.PhotoImage] = None
        self.loading_image: Optional[ImageTk.PhotoImage] = None
        self.error_image: Optional[ImageTk.PhotoImage] = None
        
        # Weak references to active image widgets
        self.active_widgets: Dict[str, weakref.ref] = {}
        self.loading_tasks: Dict[str, str] = {}  # url -> task_id
        
        self._create_placeholder_images()
        
    def _create_placeholder_images(self):
        """Create placeholder images for different states."""
        try:
            # Create placeholder image
            placeholder = Image.new('RGB', (300, 200), color='#f0f0f0')
            self.placeholder_image = ImageTk.PhotoImage(placeholder)
            
            # Create loading image
            loading = Image.new('RGB', (300, 200), color='#e0e0e0')
            self.loading_image = ImageTk.PhotoImage(loading)
            
            # Create error image
            error = Image.new('RGB', (300, 200), color='#ffcccc')
            self.error_image = ImageTk.PhotoImage(error)
            
        except Exception as e:
            print(f"Error creating placeholder images: {e}")
            
    def load_image_lazy(
        self,
        url: str,
        widget: tk.Label,
        target_size: Optional[Tuple[int, int]] = None,
        zoom_factor: float = 1.0
    ):
        """
        Load image lazily into a widget.
        
        Args:
            url: Image URL to load
            widget: Tkinter Label widget to display image in
            target_size: Target image size (width, height)
            zoom_factor: Zoom factor to apply
        """
        # Generate cache key
        size_key = f"{target_size[0]}x{target_size[1]}" if target_size else "original"
        zoom_key = f"zoom_{zoom_factor:.2f}"
        cache_key = f"{url}_{size_key}_{zoom_key}"
        
        # Set placeholder immediately
        if self.placeholder_image:
            widget.configure(image=self.placeholder_image)
            widget.image = self.placeholder_image
            
        # Check processed image cache first
        cached_image = self.memory_manager.get_processed_image_from_cache(cache_key)
        if cached_image:
            try:
                photo = ImageTk.PhotoImage(cached_image)
                widget.configure(image=photo)
                widget.image = photo
                return
            except Exception as e:
                print(f"Error displaying cached image: {e}")
                
        # Check if already loading
        if url in self.loading_tasks:
            return
            
        # Show loading state
        if self.loading_image:
            widget.configure(image=self.loading_image)
            widget.image = self.loading_image
            
        # Store weak reference to widget
        self.active_widgets[cache_key] = weakref.ref(widget)
        
        # Define callbacks
        def on_success(image_data: bytes):
            try:
                # Remove from loading tasks
                if url in self.loading_tasks:
                    del self.loading_tasks[url]
                    
                # Process image
                image = Image.open(BytesIO(image_data))
                processed_image = self._process_image(image, target_size, zoom_factor)
                
                # Cache processed image
                self.memory_manager.put_processed_image_in_cache(cache_key, processed_image)
                
                # Update widget if it still exists
                widget_ref = self.active_widgets.get(cache_key)
                if widget_ref:
                    widget_instance = widget_ref()
                    if widget_instance:
                        photo = ImageTk.PhotoImage(processed_image)
                        widget_instance.configure(image=photo)
                        widget_instance.image = photo
                        
                # Clean up
                if cache_key in self.active_widgets:
                    del self.active_widgets[cache_key]
                    
            except Exception as e:
                print(f"Error processing loaded image: {e}")
                on_error(e)
                
        def on_error(error: Exception):
            # Remove from loading tasks
            if url in self.loading_tasks:
                del self.loading_tasks[url]
                
            # Show error image
            widget_ref = self.active_widgets.get(cache_key)
            if widget_ref:
                widget_instance = widget_ref()
                if widget_instance and self.error_image:
                    widget_instance.configure(image=self.error_image)
                    widget_instance.image = self.error_image
                    
            # Clean up
            if cache_key in self.active_widgets:
                del self.active_widgets[cache_key]
                
            print(f"Error loading image {url}: {error}")
            
        # Check raw image cache
        raw_data = self.memory_manager.get_image_from_cache(url)
        if raw_data:
            # Process cached data
            on_success(raw_data)
        else:
            # Download image
            task_function = create_image_download_task(url, on_success, on_error)
            task_id = self.task_queue.submit_task(
                f"Load image {url[-20:]}",
                task_function,
                priority=TaskPriority.NORMAL,
                callback=on_success,
                error_callback=on_error
            )
            
            self.loading_tasks[url] = task_id
            
    def _process_image(
        self,
        image: Image.Image,
        target_size: Optional[Tuple[int, int]],
        zoom_factor: float
    ) -> Image.Image:
        """Process image with resizing and zoom."""
        processed = image
        
        # Apply zoom first
        if zoom_factor != 1.0:
            original_size = processed.size
            new_size = (
                int(original_size[0] * zoom_factor),
                int(original_size[1] * zoom_factor)
            )
            processed = processed.resize(new_size, Image.Resampling.LANCZOS)
            
        # Apply target size if specified
        if target_size:
            processed = processed.resize(target_size, Image.Resampling.LANCZOS)
            
        return processed
        
    def cancel_loading(self, url: str):
        """Cancel loading for a specific URL."""
        if url in self.loading_tasks:
            task_id = self.loading_tasks[url]
            self.task_queue.cancel_task(task_id)
            del self.loading_tasks[url]
            
    def cancel_all_loading(self):
        """Cancel all active loading tasks."""
        for url in list(self.loading_tasks.keys()):
            self.cancel_loading(url)
            
    def cleanup_dead_widgets(self):
        """Clean up references to dead widgets."""
        dead_keys = []
        for key, widget_ref in self.active_widgets.items():
            if widget_ref() is None:
                dead_keys.append(key)
                
        for key in dead_keys:
            del self.active_widgets[key]


class ImageOptimizer:
    """
    Main image optimization system combining caching, lazy loading, and progressive loading.
    """
    
    def __init__(self, memory_manager: MemoryManager, task_queue: TaskQueue):
        self.memory_manager = memory_manager
        self.task_queue = task_queue
        self.lazy_loader = LazyImageLoader(memory_manager, task_queue)
        self.progressive_loader = ProgressiveImageLoader(memory_manager, task_queue)
        
        # Optimization settings
        self.max_image_size = (1200, 1200)  # Maximum display size
        self.jpeg_quality = 85
        self.preload_ahead = 2  # Number of images to preload ahead
        
        # Statistics
        self.stats = {
            'images_loaded': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'bytes_saved': 0,
            'load_times': []
        }
        
    def load_image_optimized(
        self,
        url: str,
        widget: tk.Label,
        target_size: Optional[Tuple[int, int]] = None,
        zoom_factor: float = 1.0,
        use_progressive: bool = False
    ):
        """
        Load image with optimal strategy.
        
        Args:
            url: Image URL
            widget: Target widget
            target_size: Desired image size
            zoom_factor: Zoom level
            use_progressive: Whether to use progressive loading
        """
        start_time = time.time()
        
        def on_load_complete():
            load_time = time.time() - start_time
            self.stats['load_times'].append(load_time)
            self.stats['images_loaded'] += 1
            
        if use_progressive:
            def progressive_callback(image: Image.Image, quality: str):
                try:
                    # Process and display image
                    processed = self._process_for_display(image, target_size, zoom_factor)
                    photo = ImageTk.PhotoImage(processed)
                    widget.configure(image=photo)
                    widget.image = photo
                    
                    if quality == 'regular':  # Final quality
                        on_load_complete()
                        
                except Exception as e:
                    print(f"Error in progressive callback: {e}")
                    
            self.progressive_loader.load_progressive(
                url,
                progressive_callback,
                error_callback=lambda e: print(f"Progressive load error: {e}")
            )
        else:
            self.lazy_loader.load_image_lazy(url, widget, target_size, zoom_factor)
            on_load_complete()
            
    def _process_for_display(
        self,
        image: Image.Image,
        target_size: Optional[Tuple[int, int]],
        zoom_factor: float
    ) -> Image.Image:
        """Process image for optimal display."""
        processed = image
        
        # Optimize size to prevent memory issues
        if processed.size[0] * processed.size[1] > 2000000:  # 2M pixels
            # Resize large images
            ratio = min(
                self.max_image_size[0] / processed.size[0],
                self.max_image_size[1] / processed.size[1]
            )
            if ratio < 1.0:
                new_size = (
                    int(processed.size[0] * ratio),
                    int(processed.size[1] * ratio)
                )
                processed = processed.resize(new_size, Image.Resampling.LANCZOS)
                
        # Apply zoom
        if zoom_factor != 1.0:
            original_size = processed.size
            new_size = (
                int(original_size[0] * zoom_factor),
                int(original_size[1] * zoom_factor)
            )
            processed = processed.resize(new_size, Image.Resampling.LANCZOS)
            
        # Apply target size
        if target_size:
            processed = processed.resize(target_size, Image.Resampling.LANCZOS)
            
        return processed
        
    def preload_images(self, urls: list, priority: TaskPriority = TaskPriority.LOW):
        """Preload images for better performance."""
        for url in urls[:self.preload_ahead]:
            # Only preload if not in cache
            if not self.memory_manager.get_image_from_cache(url):
                def preload_callback(data: bytes):
                    self.memory_manager.put_image_in_cache(url, data)
                    
                task_function = create_image_download_task(
                    url, preload_callback, lambda e: None
                )
                self.task_queue.submit_task(
                    f"Preload {url[-20:]}",
                    task_function,
                    priority=priority
                )
                
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics."""
        avg_load_time = (
            sum(self.stats['load_times']) / len(self.stats['load_times'])
            if self.stats['load_times'] else 0
        )
        
        return {
            'images_loaded': self.stats['images_loaded'],
            'average_load_time': avg_load_time,
            'cache_stats': self.memory_manager.get_cache_stats(),
            'active_loading_tasks': len(self.lazy_loader.loading_tasks)
        }
        
    def cleanup(self):
        """Clean up resources."""
        self.lazy_loader.cancel_all_loading()
        self.lazy_loader.cleanup_dead_widgets()
        
    def set_optimization_settings(
        self,
        max_size: Tuple[int, int] = (1200, 1200),
        jpeg_quality: int = 85,
        preload_count: int = 2
    ):
        """Update optimization settings."""
        self.max_image_size = max_size
        self.jpeg_quality = jpeg_quality
        self.preload_ahead = preload_count