"""
Optimized Image Collection System Integration

This module integrates advanced performance optimizations into the image collection workflow.
"""

import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional, Callable, Any
import logging
from pathlib import Path
import json

from .performance_optimization import PerformanceOptimizer, ProgressFeedbackSystem
from .ui.components.performance_dashboard import PerformanceDashboard
from .utils.performance.task_queue import TaskPriority
from .services.unsplash_service import UnsplashService


class OptimizedImageCollector:
    """
    High-performance image collection system with comprehensive optimizations.
    """
    
    def __init__(self, main_app, unsplash_service: UnsplashService):
        self.main_app = main_app
        self.unsplash_service = unsplash_service
        
        # Initialize performance optimizer
        self.performance_optimizer = PerformanceOptimizer(
            main_app.root if hasattr(main_app, 'root') else main_app,
            str(main_app.DATA_DIR)
        )
        
        # Collection state
        self.collection_active = False
        self.collection_paused = False
        self.collection_cancelled = False
        self.collected_images = []
        self.collection_stats = {
            'total_requested': 0,
            'successfully_collected': 0,
            'failed_collections': 0,
            'cache_hits': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Configuration
        self.batch_size = 5  # Process images in batches
        self.max_concurrent_downloads = 3
        self.memory_threshold_mb = 400
        self.chunk_size = 10
        
        # Progress tracking
        self.progress_system: Optional[ProgressFeedbackSystem] = None
        self.current_operation_id: Optional[str] = None
        
        # Performance dashboard
        self.dashboard: Optional[PerformanceDashboard] = None
        
        # Callbacks
        self.progress_callbacks: List[Callable] = []
        self.completion_callbacks: List[Callable] = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def initialize_optimization(self):
        """Initialize the optimization system."""
        try:
            self.performance_optimizer.start_optimization()
            self.logger.info("Performance optimization system started")
        except Exception as e:
            self.logger.error(f"Failed to start performance optimization: {e}")
            
    def shutdown_optimization(self):
        """Shutdown the optimization system."""
        try:
            self.performance_optimizer.stop_optimization()
            self.logger.info("Performance optimization system stopped")
        except Exception as e:
            self.logger.error(f"Error stopping performance optimization: {e}")
            
    def show_performance_dashboard(self):
        """Show the performance monitoring dashboard."""
        if not self.dashboard:
            parent = self.main_app.root if hasattr(self.main_app, 'root') else self.main_app
            self.dashboard = PerformanceDashboard(parent, self.performance_optimizer)
        self.dashboard.show_dashboard()
        
    def setup_progress_feedback(self, parent_widget: tk.Widget):
        """Setup progress feedback system."""
        self.progress_system = ProgressFeedbackSystem(parent_widget)
        
    def collect_images_optimized(self, query: str, max_images: int = 30,
                               progress_callback: Optional[Callable] = None) -> List[Dict]:
        """
        Collect images with comprehensive performance optimizations.
        
        Args:
            query: Search query for images
            max_images: Maximum number of images to collect
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of collected image data
        """
        if self.collection_active:
            raise RuntimeError("Collection already in progress")
            
        self.collection_active = True
        self.collection_cancelled = False
        self.collection_paused = False
        self.collected_images.clear()
        
        # Initialize collection stats
        self.collection_stats = {
            'total_requested': max_images,
            'successfully_collected': 0,
            'failed_collections': 0,
            'cache_hits': 0,
            'start_time': time.time(),
            'end_time': None
        }
        
        # Setup progress tracking
        if self.progress_system:
            self.current_operation_id = f"collection_{int(time.time())}"
            progress_widgets = self.progress_system.create_progress_widget(
                self.current_operation_id,
                f"Collecting images for '{query}'",
                can_cancel=True
            )
            
            # Register cancellation callback
            self.progress_system.register_cancellation_callback(
                self.current_operation_id,
                self.cancel_collection
            )
        
        try:
            # Collect images using chunked processing
            self.logger.info(f"Starting optimized collection of {max_images} images for '{query}'")
            
            collected_images = self._collect_images_chunked(
                query, max_images, progress_callback
            )
            
            self.collection_stats['end_time'] = time.time()
            self.collection_stats['successfully_collected'] = len(collected_images)
            
            # Update progress to completion
            if self.progress_system and self.current_operation_id:
                self.progress_system.update_progress(
                    self.current_operation_id,
                    100.0,
                    f"Completed: {len(collected_images)} images collected"
                )
            
            # Notify completion callbacks
            for callback in self.completion_callbacks:
                try:
                    callback(collected_images, self.collection_stats)
                except Exception as e:
                    self.logger.error(f"Error in completion callback: {e}")
                    
            self.logger.info(f"Collection completed: {len(collected_images)} images")
            return collected_images
            
        except Exception as e:
            self.logger.error(f"Error during image collection: {e}")
            self.collection_stats['end_time'] = time.time()
            
            if self.progress_system and self.current_operation_id:
                self.progress_system.update_progress(
                    self.current_operation_id,
                    0.0,
                    f"Error: {str(e)}"
                )
                
            raise
        finally:
            self.collection_active = False
            
    def _collect_images_chunked(self, query: str, max_images: int,
                               progress_callback: Optional[Callable]) -> List[Dict]:
        """Collect images using chunked processing for better performance."""
        collected_images = []
        total_pages = (max_images + 9) // 10  # 10 images per page
        
        for page in range(1, total_pages + 1):
            if self.collection_cancelled:
                self.logger.info("Collection cancelled by user")
                break
                
            # Handle pause
            while self.collection_paused and not self.collection_cancelled:
                time.sleep(0.1)
                
            if self.collection_cancelled:
                break
                
            # Calculate images needed for this page
            images_needed = min(10, max_images - len(collected_images))
            if images_needed <= 0:
                break
                
            # Update progress
            progress_percent = (len(collected_images) / max_images) * 100
            status_message = f"Searching page {page}/{total_pages} ({len(collected_images)}/{max_images} images)"
            
            if progress_callback:
                progress_callback(progress_percent, status_message)
                
            if self.progress_system and self.current_operation_id:
                self.progress_system.update_progress(
                    self.current_operation_id,
                    progress_percent,
                    status_message
                )
            
            try:
                # Search for images on this page
                search_result = self.unsplash_service.search_photos(
                    query=query,
                    page=page,
                    per_page=images_needed
                )
                
                if 'results' in search_result and search_result['results']:
                    page_images = search_result['results']
                    
                    # Process images in batches for better memory management
                    batch_images = self._process_image_batch(page_images, query)
                    collected_images.extend(batch_images)
                    
                    # Check memory usage and perform cleanup if needed
                    current_memory = self.performance_optimizer.memory_manager.get_memory_usage_mb()
                    if current_memory > self.memory_threshold_mb:
                        self.logger.info(f"Memory threshold reached ({current_memory:.1f}MB), performing cleanup")
                        self.performance_optimizer.memory_manager.perform_cleanup()
                        
                else:
                    self.logger.warning(f"No results found for page {page}")
                    break
                    
            except Exception as e:
                self.logger.error(f"Error collecting page {page}: {e}")
                self.collection_stats['failed_collections'] += 1
                
                # Don't break on single page failure, try next page
                continue
                
            # Brief pause between pages to prevent rate limiting
            time.sleep(0.5)
            
        return collected_images
        
    def _process_image_batch(self, images: List[Dict], query: str) -> List[Dict]:
        """Process a batch of images with optimization."""
        processed_images = []
        
        for image_data in images:
            if self.collection_cancelled:
                break
                
            try:
                # Check if image is already processed (cache check)
                image_url = image_data.get('urls', {}).get('regular', '')
                canonical_url = self.unsplash_service.canonicalize_url(image_url)
                
                # Skip if already collected
                if canonical_url in self.main_app.used_image_urls:
                    continue
                    
                # Enhance image data with additional metadata
                enhanced_data = self._enhance_image_data(image_data, query)
                processed_images.append(enhanced_data)
                
                # Add to used URLs
                self.main_app.used_image_urls.add(canonical_url)
                
            except Exception as e:
                self.logger.error(f"Error processing image: {e}")
                self.collection_stats['failed_collections'] += 1
                continue
                
        return processed_images
        
    def _enhance_image_data(self, image_data: Dict, query: str) -> Dict:
        """Enhance image data with additional metadata."""
        enhanced_data = image_data.copy()
        enhanced_data.update({
            'collection_query': query,
            'collection_timestamp': time.time(),
            'collection_id': self.current_operation_id,
            'processed': True
        })
        
        return enhanced_data
        
    def pause_collection(self):
        """Pause the current collection."""
        if self.collection_active and not self.collection_paused:
            self.collection_paused = True
            self.logger.info("Collection paused")
            
            if self.progress_system and self.current_operation_id:
                self.progress_system.update_progress(
                    self.current_operation_id,
                    self.progress_system.active_operations[self.current_operation_id]['progress'],
                    "Paused"
                )
                
    def resume_collection(self):
        """Resume the paused collection."""
        if self.collection_active and self.collection_paused:
            self.collection_paused = False
            self.logger.info("Collection resumed")
            
    def cancel_collection(self):
        """Cancel the current collection."""
        if self.collection_active:
            self.collection_cancelled = True
            self.collection_active = False
            self.logger.info("Collection cancelled")
            
    def get_collection_status(self) -> Dict[str, Any]:
        """Get current collection status and statistics."""
        return {
            'active': self.collection_active,
            'paused': self.collection_paused,
            'cancelled': self.collection_cancelled,
            'stats': self.collection_stats.copy(),
            'collected_count': len(self.collected_images),
            'memory_usage_mb': self.performance_optimizer.memory_manager.get_memory_usage_mb(),
            'performance_metrics': self.performance_optimizer.get_performance_metrics()
        }
        
    def add_progress_callback(self, callback: Callable):
        """Add progress update callback."""
        self.progress_callbacks.append(callback)
        
    def add_completion_callback(self, callback: Callable):
        """Add collection completion callback."""
        self.completion_callbacks.append(callback)
        
    def configure_collection(self, **kwargs):
        """Configure collection parameters."""
        if 'batch_size' in kwargs:
            self.batch_size = kwargs['batch_size']
        if 'max_concurrent_downloads' in kwargs:
            self.max_concurrent_downloads = kwargs['max_concurrent_downloads']
        if 'memory_threshold_mb' in kwargs:
            self.memory_threshold_mb = kwargs['memory_threshold_mb']
        if 'chunk_size' in kwargs:
            self.chunk_size = kwargs['chunk_size']
            
        self.logger.info(f"Collection configured: {kwargs}")
        
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization report."""
        base_report = self.performance_optimizer.get_optimization_report()
        
        # Add collection-specific metrics
        base_report['collection_metrics'] = {
            'collection_stats': self.collection_stats,
            'configuration': {
                'batch_size': self.batch_size,
                'max_concurrent_downloads': self.max_concurrent_downloads,
                'memory_threshold_mb': self.memory_threshold_mb,
                'chunk_size': self.chunk_size
            }
        }
        
        return base_report
        
    def export_collection_report(self, file_path: str):
        """Export collection performance report."""
        report = self.get_optimization_report()
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            self.logger.info(f"Collection report exported to {file_path}")
        except Exception as e:
            self.logger.error(f"Error exporting report: {e}")
            raise


class OptimizedImageCollectionWidget:
    """
    UI widget for optimized image collection with performance monitoring.
    """
    
    def __init__(self, parent: tk.Widget, main_app):
        self.parent = parent
        self.main_app = main_app
        self.collector: Optional[OptimizedImageCollector] = None
        
        self._create_widget()
        
    def _create_widget(self):
        """Create the collection widget."""
        # Main frame
        self.main_frame = ttk.LabelFrame(self.parent, text="Optimized Image Collection", padding="10")
        self.main_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Controls frame
        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Collection settings
        settings_frame = ttk.Frame(controls_frame)
        settings_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(settings_frame, text="Max Images:").pack(side=tk.LEFT)
        self.max_images_var = tk.StringVar(value="30")
        ttk.Entry(settings_frame, textvariable=self.max_images_var, width=10).pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(settings_frame, text="Memory Limit (MB):").pack(side=tk.LEFT)
        self.memory_limit_var = tk.StringVar(value="400")
        ttk.Entry(settings_frame, textvariable=self.memory_limit_var, width=10).pack(side=tk.LEFT, padx=(5, 10))
        
        # Action buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill=tk.X)
        
        self.start_button = ttk.Button(
            button_frame,
            text="Start Optimized Collection",
            command=self._start_collection
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.pause_button = ttk.Button(
            button_frame,
            text="Pause",
            command=self._pause_collection,
            state=tk.DISABLED
        )
        self.pause_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._cancel_collection,
            state=tk.DISABLED
        )
        self.cancel_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.dashboard_button = ttk.Button(
            button_frame,
            text="Performance Dashboard",
            command=self._show_dashboard
        )
        self.dashboard_button.pack(side=tk.RIGHT)
        
        # Progress frame (will be populated by progress system)
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress_frame.pack(fill=tk.X, pady=(10, 0))
        
    def initialize_collector(self, unsplash_service: UnsplashService):
        """Initialize the optimized collector."""
        self.collector = OptimizedImageCollector(self.main_app, unsplash_service)
        self.collector.initialize_optimization()
        self.collector.setup_progress_feedback(self.progress_frame)
        
        # Add callbacks
        self.collector.add_completion_callback(self._on_collection_complete)
        
    def _start_collection(self):
        """Start optimized image collection."""
        if not self.collector:
            messagebox.showerror("Error", "Collector not initialized")
            return
            
        query = self.main_app.search_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter a search query")
            return
            
        try:
            max_images = int(self.max_images_var.get())
            memory_limit = float(self.memory_limit_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric values")
            return
            
        # Configure collector
        self.collector.configure_collection(
            memory_threshold_mb=memory_limit
        )
        
        # Update UI state
        self.start_button.configure(state=tk.DISABLED)
        self.pause_button.configure(state=tk.NORMAL)
        self.cancel_button.configure(state=tk.NORMAL)
        
        # Start collection in background thread
        threading.Thread(
            target=self._run_collection,
            args=(query, max_images),
            daemon=True,
            name="OptimizedCollection"
        ).start()
        
    def _run_collection(self, query: str, max_images: int):
        """Run the optimized collection in background."""
        try:
            collected_images = self.collector.collect_images_optimized(
                query, max_images, self._update_progress
            )
            
            # Update main app with collected images
            self.main_app.after(0, lambda: self._update_main_app(collected_images))
            
        except Exception as e:
            self.main_app.after(0, lambda: self._handle_collection_error(str(e)))
            
    def _update_progress(self, progress: float, message: str):
        """Update progress in main thread."""
        # This will be handled by the progress system
        pass
        
    def _pause_collection(self):
        """Pause the collection."""
        if self.collector:
            if self.collector.collection_paused:
                self.collector.resume_collection()
                self.pause_button.configure(text="Pause")
            else:
                self.collector.pause_collection()
                self.pause_button.configure(text="Resume")
                
    def _cancel_collection(self):
        """Cancel the collection."""
        if self.collector:
            self.collector.cancel_collection()
            
    def _show_dashboard(self):
        """Show performance dashboard."""
        if self.collector:
            self.collector.show_performance_dashboard()
            
    def _on_collection_complete(self, images: List[Dict], stats: Dict):
        """Handle collection completion."""
        def update_ui():
            self.start_button.configure(state=tk.NORMAL)
            self.pause_button.configure(state=tk.DISABLED, text="Pause")
            self.cancel_button.configure(state=tk.DISABLED)
            
            # Show completion message
            messagebox.showinfo(
                "Collection Complete",
                f"Successfully collected {len(images)} images\n"
                f"Time taken: {stats.get('end_time', 0) - stats.get('start_time', 0):.1f} seconds"
            )
            
        self.main_app.after(0, update_ui)
        
    def _update_main_app(self, images: List[Dict]):
        """Update main application with collected images."""
        # This would integrate with the main app's image handling
        # Implementation depends on main app structure
        pass
        
    def _handle_collection_error(self, error_message: str):
        """Handle collection errors."""
        self.start_button.configure(state=tk.NORMAL)
        self.pause_button.configure(state=tk.DISABLED, text="Pause")
        self.cancel_button.configure(state=tk.DISABLED)
        
        messagebox.showerror("Collection Error", f"Error during collection:\n{error_message}")
        
    def cleanup(self):
        """Cleanup resources."""
        if self.collector:
            self.collector.shutdown_optimization()