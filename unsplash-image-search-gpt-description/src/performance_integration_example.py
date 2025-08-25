"""
Example integration of performance optimization system with the main application.

This file demonstrates how to integrate all performance components into the
existing ImageSearchApp for optimal performance.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from pathlib import Path

# Performance imports
from src.utils.performance import (
    PerformanceMonitor,
    MemoryManager, 
    TaskQueue,
    ImageOptimizer,
    SearchDebouncer,
    StartupOptimizer,
    TaskPriority
)
from src.ui.components import PerformanceMonitorDashboard


class PerformanceOptimizedImageSearchApp(tk.Tk):
    """
    Performance-optimized version of the Image Search Application.
    
    Integrates all performance optimization components:
    - Performance monitoring
    - Memory management  
    - Background task processing
    - Image optimization
    - Input debouncing
    - Virtual scrolling for results
    """
    
    def __init__(self):
        # Initialize performance components FIRST
        self._init_performance_system()
        
        # Initialize Tkinter
        super().__init__()
        
        # App configuration
        self.title("Optimized Unsplash Image Search")
        self.geometry("1200x900")
        
        # App state
        self.current_search_results = []
        self.current_query = ""
        
        # Setup UI with performance optimizations
        self._setup_optimized_ui()
        
        # Start background systems
        self._start_performance_monitoring()
        
        # Setup performance dashboard (hidden by default)
        self._setup_performance_dashboard()
        
    def _init_performance_system(self):
        """Initialize all performance components."""
        
        # Core performance monitoring
        self.performance_monitor = PerformanceMonitor(
            log_file=Path("data/performance.log")
        )
        
        # Memory management with intelligent caching
        self.memory_manager = MemoryManager(
            image_cache_size=50,          # Cache up to 50 raw images
            image_cache_memory_mb=200.0   # Up to 200MB for image cache
        )
        
        # Background task processing
        self.task_queue = TaskQueue(max_workers=4)  # 4 worker threads
        
        # Image optimization system
        self.image_optimizer = ImageOptimizer(
            self.memory_manager,
            self.task_queue
        )
        self.image_optimizer.set_optimization_settings(
            max_size=(1200, 1200),  # Maximum display size
            preload_count=3         # Preload 3 images ahead
        )
        
        # Input debouncing
        self.search_debouncer = SearchDebouncer(
            delay=0.3,      # 300ms delay
            min_length=2    # Minimum 2 characters
        )
        
        # API call debouncing with rate limiting
        from src.utils.performance.debouncer import APICallDebouncer
        self.api_debouncer = APICallDebouncer(
            delay=1.0,          # 1 second delay
            calls_per_minute=45 # Under Unsplash's 50/hour limit
        )
        
    def _setup_optimized_ui(self):
        """Setup UI with performance optimizations applied."""
        
        # Main container
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search section with debounced input
        self._create_search_section(main_frame)
        
        # Performance toolbar
        self._create_performance_toolbar(main_frame)
        
        # Content area with optimized image display
        self._create_content_area(main_frame)
        
        # Status bar with performance metrics
        self._create_status_bar(main_frame)
        
    def _create_search_section(self, parent):
        """Create search section with debounced input."""
        search_frame = ttk.LabelFrame(parent, text="Search", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search input with debouncing
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            search_frame, 
            textvariable=self.search_var,
            font=('TkDefaultFont', 12),
            width=50
        )
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Bind debounced search
        self.search_var.trace_add(
            'write',
            lambda *args: self._on_search_input()
        )
        
        # Search button (immediate search)
        search_btn = ttk.Button(
            search_frame,
            text="Search Now",
            command=self._perform_immediate_search
        )
        search_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Loading indicator
        self.search_progress = ttk.Progressbar(
            search_frame,
            mode='indeterminate',
            length=200
        )
        self.search_progress.pack(side=tk.LEFT)
        
    def _create_performance_toolbar(self, parent):
        """Create toolbar with performance controls."""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Performance dashboard button
        perf_btn = ttk.Button(
            toolbar_frame,
            text="📊 Performance",
            command=self._show_performance_dashboard
        )
        perf_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Memory cleanup button
        cleanup_btn = ttk.Button(
            toolbar_frame,
            text="🧹 Clean Memory",
            command=self._perform_memory_cleanup
        )
        cleanup_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Cache stats label
        self.cache_stats_var = tk.StringVar(value="Cache: Loading...")
        cache_label = ttk.Label(toolbar_frame, textvariable=self.cache_stats_var)
        cache_label.pack(side=tk.RIGHT)
        
        # Update cache stats periodically
        self._update_cache_stats()
        
    def _create_content_area(self, parent):
        """Create content area with optimized image display."""
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Current image with zoom
        image_frame = ttk.LabelFrame(content_frame, text="Current Image", padding="10")
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Image display with lazy loading
        self.current_image_label = tk.Label(
            image_frame,
            text="No image loaded",
            bg="white",
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.current_image_label.pack(fill=tk.BOTH, expand=True)
        
        # Zoom controls
        zoom_frame = ttk.Frame(image_frame)
        zoom_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.zoom_var = tk.DoubleVar(value=1.0)
        zoom_scale = ttk.Scale(
            zoom_frame,
            from_=0.25,
            to=3.0,
            variable=self.zoom_var,
            orient=tk.HORIZONTAL,
            command=self._on_zoom_change
        )
        zoom_scale.pack(fill=tk.X)
        
        # Right panel - Search results with virtual scrolling
        results_frame = ttk.LabelFrame(content_frame, text="Search Results", padding="10")
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(5, 0))
        results_frame.configure(width=300)
        
        # Virtual scrolling container for results
        self._setup_virtual_results_list(results_frame)
        
    def _setup_virtual_results_list(self, parent):
        """Setup virtual scrolling for search results."""
        from src.utils.performance.virtual_scroll import VirtualScrollManager
        
        def create_result_item(result_data, parent_widget):
            """Create widget for a search result item."""
            item_frame = tk.Frame(
                parent_widget,
                relief=tk.RAISED,
                borderwidth=1,
                bg='white'
            )
            
            # Thumbnail placeholder
            thumb_label = tk.Label(
                item_frame,
                text="Loading...",
                width=20,
                height=3,
                bg='lightgray'
            )
            thumb_label.pack(padx=5, pady=5)
            
            # Load thumbnail lazily
            if 'urls' in result_data:
                self.image_optimizer.load_image_optimized(
                    result_data['urls']['thumb'],
                    thumb_label,
                    target_size=(150, 100)
                )
            
            # Click handler to load full image
            def on_click(event):
                self._load_full_image(result_data)
                
            item_frame.bind("<Button-1>", on_click)
            thumb_label.bind("<Button-1>", on_click)
            
            return item_frame
            
        # Create virtual scroll manager
        self.results_virtual_scroll = VirtualScrollManager(
            parent,
            item_height=120,  # Height of each result item
            buffer_size=3,    # Buffer 3 items above/below visible
            create_item_func=create_result_item
        )
        
    def _create_status_bar(self, parent):
        """Create status bar with performance metrics."""
        status_frame = ttk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Status message
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT, padx=5)
        
        # Performance metrics
        self.perf_metrics_var = tk.StringVar(value="")
        perf_label = ttk.Label(status_frame, textvariable=self.perf_metrics_var)
        perf_label.pack(side=tk.RIGHT, padx=5)
        
    def _start_performance_monitoring(self):
        """Start background performance monitoring."""
        
        # Start all monitoring systems
        self.performance_monitor.start_monitoring(interval=2.0)
        self.memory_manager.start_monitoring(interval=30.0)
        
        # Setup performance callback
        def on_performance_update(metrics):
            # Update status bar with current metrics
            perf_text = (f"Memory: {metrics.memory_usage_mb:.0f}MB | "
                        f"FPS: {metrics.fps:.1f} | "
                        f"Threads: {metrics.active_threads}")
            
            # Update UI in main thread
            self.after(0, lambda: self.perf_metrics_var.set(perf_text))
            
        self.performance_monitor.add_callback(on_performance_update)
        
    def _setup_performance_dashboard(self):
        """Setup the performance monitoring dashboard."""
        self.perf_dashboard = PerformanceMonitorDashboard(
            self,
            self.performance_monitor,
            self.memory_manager,
            self.task_queue
        )
        
        # Hide initially
        self.perf_dashboard.withdraw()
        
    def _on_search_input(self):
        """Handle debounced search input."""
        query = self.search_var.get().strip()
        
        if query:
            # Use debounced search
            self.search_debouncer.debounce_search(
                query,
                self._perform_background_search
            )
        else:
            # Clear results if empty
            self._clear_search_results()
            
    def _perform_immediate_search(self):
        """Perform immediate search (bypass debouncing)."""
        query = self.search_var.get().strip()
        if query:
            self._perform_background_search(query)
            
    def _perform_background_search(self, query):
        """Perform search in background with progress reporting."""
        
        # Update UI state
        self.status_var.set(f"Searching for '{query}'...")
        self.search_progress.start()
        self.current_query = query
        
        # Define search task
        def search_task():
            """Background search task."""
            try:
                # Simulate API call (replace with actual Unsplash API)
                time.sleep(1)  # Simulate network delay
                
                # Mock results
                results = [
                    {
                        'id': f'image_{i}',
                        'urls': {
                            'thumb': f'https://via.placeholder.com/150/{"ff0000" if i%2 else "0000ff"}',
                            'regular': f'https://via.placeholder.com/600/{"ff0000" if i%2 else "0000ff"}'
                        },
                        'description': f'Sample image {i} for {query}'
                    }
                    for i in range(20)  # Mock 20 results
                ]
                
                return results
                
            except Exception as e:
                print(f"Search error: {e}")
                return []
                
        # Define callbacks
        def on_search_success(results):
            """Handle successful search."""
            self.current_search_results = results
            
            # Update virtual scroll with new results
            self.results_virtual_scroll.set_items(results)
            
            # Update status
            self.status_var.set(f"Found {len(results)} images for '{query}'")
            self.search_progress.stop()
            
            # Load first image if available
            if results:
                self._load_full_image(results[0])
                
            # Preload some images for better performance
            if len(results) > 1:
                preload_urls = [r['urls']['thumb'] for r in results[1:4]]
                self.image_optimizer.preload_images(preload_urls)
                
        def on_search_error(error):
            """Handle search error."""
            self.status_var.set(f"Search failed: {error}")
            self.search_progress.stop()
            
        # Submit background task
        task_id = self.task_queue.submit_task(
            f"Search '{query}'",
            search_task,
            priority=TaskPriority.HIGH,
            callback=on_search_success,
            error_callback=on_search_error
        )
        
        # Record API call for monitoring
        self.performance_monitor.record_api_call('unsplash_search', 1000.0, True)
        
    def _load_full_image(self, image_data):
        """Load full resolution image with optimization."""
        if 'urls' not in image_data:
            return
            
        url = image_data['urls']['regular']
        
        # Update status
        self.status_var.set("Loading full image...")
        
        # Use optimized image loading with progressive enhancement
        self.image_optimizer.load_image_optimized(
            url,
            self.current_image_label,
            zoom_factor=self.zoom_var.get(),
            use_progressive=True
        )
        
    def _on_zoom_change(self, value):
        """Handle zoom level changes."""
        # Refresh current image with new zoom
        if hasattr(self, 'current_image_data'):
            self._load_full_image(self.current_image_data)
            
    def _clear_search_results(self):
        """Clear current search results."""
        self.current_search_results = []
        self.results_virtual_scroll.clear_items()
        self.status_var.set("Ready")
        
    def _show_performance_dashboard(self):
        """Show the performance monitoring dashboard."""
        self.perf_dashboard.show()
        
    def _perform_memory_cleanup(self):
        """Perform manual memory cleanup."""
        self.status_var.set("Cleaning memory...")
        
        def cleanup_task():
            """Background cleanup task."""
            self.memory_manager.perform_aggressive_cleanup()
            return "Cleanup complete"
            
        self.task_queue.submit_task(
            "Memory Cleanup",
            cleanup_task,
            callback=lambda result: self.status_var.set(result)
        )
        
    def _update_cache_stats(self):
        """Update cache statistics display."""
        try:
            stats = self.memory_manager.get_cache_stats()
            hit_ratio = stats.get('hit_ratio', 0) * 100
            memory_mb = stats.get('memory_usage_mb', 0)
            
            cache_text = f"Cache: {hit_ratio:.0f}% hit ratio, {memory_mb:.0f}MB"
            self.cache_stats_var.set(cache_text)
            
        except Exception as e:
            print(f"Error updating cache stats: {e}")
            
        # Schedule next update
        self.after(5000, self._update_cache_stats)
        
    def on_closing(self):
        """Handle application closing."""
        # Stop monitoring
        self.performance_monitor.stop_monitoring()
        self.memory_manager.stop_monitoring()
        
        # Shutdown task queue
        self.task_queue.shutdown()
        
        # Clean up resources
        self.image_optimizer.cleanup()
        
        # Close application
        self.destroy()


def create_optimized_startup():
    """Create optimized startup process for the application."""
    
    # Create startup optimizer
    optimizer = StartupOptimizer("Unsplash Image Search")
    
    # Register lazy imports for expensive modules
    optimizer.register_lazy_import(
        'PIL', 
        lambda: {'Image': __import__('PIL.Image', fromlist=['Image']).Image,
                'ImageTk': __import__('PIL.ImageTk', fromlist=['ImageTk']).ImageTk}
    )
    
    optimizer.register_lazy_import(
        'requests',
        lambda: __import__('requests')
    )
    
    optimizer.register_lazy_import(
        'matplotlib',
        lambda: __import__('matplotlib.pyplot')
    )
    
    # Add critical startup tasks
    optimizer.add_critical_task(
        "Initialize Performance System",
        lambda: print("✓ Performance system initialized"),
        weight=1.0
    )
    
    optimizer.add_critical_task(
        "Load Configuration",
        lambda: print("✓ Configuration loaded"),
        weight=1.0
    )
    
    # Add background tasks
    optimizer.add_background_task(
        "Warm Up Image Cache",
        lambda: print("✓ Image cache warmed up"),
        weight=1.0
    )
    
    optimizer.add_background_task(
        "Initialize API Connections",
        lambda: print("✓ API connections initialized"),
        weight=1.0
    )
    
    # Start optimized startup with splash screen
    app = optimizer.start_optimized_startup(
        show_splash=True,
        main_window_factory=PerformanceOptimizedImageSearchApp
    )
    
    return app, optimizer


def main():
    """Main entry point with performance optimization."""
    print("Starting optimized Unsplash Image Search application...")
    
    try:
        # Create app with optimized startup
        app, startup_optimizer = create_optimized_startup()
        
        if app:
            # Setup cleanup handler
            app.protocol("WM_DELETE_WINDOW", app.on_closing)
            
            # Start main loop
            print("✓ Application started successfully")
            app.mainloop()
            
            # Print performance stats after closing
            startup_stats = startup_optimizer.get_startup_stats()
            print(f"\nStartup Performance:")
            print(f"Total time: {startup_stats['total_startup_time']:.2f}s")
            print(f"Critical tasks: {startup_stats['critical_tasks_time']:.2f}s")
            print("Application closed successfully")
            
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()