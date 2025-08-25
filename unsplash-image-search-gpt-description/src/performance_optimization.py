"""
Comprehensive Performance Optimization System for Image Collection

This module provides advanced performance optimization features including:
- Memory usage analysis and optimization
- Resource disposal management
- Chunked image collection processing
- UI responsiveness improvements
- Progress feedback with cancellation support
"""

import gc
import time
import threading
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict, deque
import queue
import weakref
import psutil
from PIL import Image, ImageTk
import requests
from io import BytesIO
import logging

# Import existing performance modules
from src.utils.performance.memory_manager import MemoryManager
from src.utils.performance.task_queue import TaskQueue, TaskPriority
from src.utils.performance.performance_monitor import PerformanceMonitor
from src.utils.performance.image_optimizer import ImageOptimizer


@dataclass
class PerformanceMetrics:
    """Performance metrics for image collection operations."""
    memory_usage_mb: float
    cpu_usage_percent: float
    images_processed: int
    cache_hit_ratio: float
    average_load_time: float
    ui_responsiveness: float
    active_threads: int
    pending_tasks: int


class ResourceManager:
    """
    Advanced resource management system with automatic cleanup.
    """
    
    def __init__(self):
        self.active_resources: Dict[str, Any] = {}
        self.cleanup_callbacks: Dict[str, Callable] = {}
        self.resource_locks: Dict[str, threading.Lock] = defaultdict(threading.Lock)
        self._cleanup_thread: Optional[threading.Thread] = None
        self._cleanup_running = False
        self._cleanup_interval = 30.0  # 30 seconds
        
    def register_resource(self, resource_id: str, resource: Any, cleanup_callback: Callable):
        """Register a resource for automatic cleanup."""
        with self.resource_locks[resource_id]:
            self.active_resources[resource_id] = resource
            self.cleanup_callbacks[resource_id] = cleanup_callback
            
    def release_resource(self, resource_id: str) -> bool:
        """Manually release a specific resource."""
        with self.resource_locks[resource_id]:
            if resource_id in self.active_resources:
                try:
                    cleanup_callback = self.cleanup_callbacks.get(resource_id)
                    if cleanup_callback:
                        cleanup_callback()
                except Exception as e:
                    logging.error(f"Error in cleanup callback for {resource_id}: {e}")
                finally:
                    del self.active_resources[resource_id]
                    del self.cleanup_callbacks[resource_id]
                    return True
            return False
            
    def start_auto_cleanup(self):
        """Start automatic resource cleanup thread."""
        if not self._cleanup_running:
            self._cleanup_running = True
            self._cleanup_thread = threading.Thread(
                target=self._cleanup_loop,
                daemon=True,
                name="ResourceCleanup"
            )
            self._cleanup_thread.start()
            
    def stop_auto_cleanup(self):
        """Stop automatic resource cleanup."""
        self._cleanup_running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5.0)
            
    def _cleanup_loop(self):
        """Automatic cleanup loop."""
        while self._cleanup_running:
            try:
                self._perform_cleanup()
                time.sleep(self._cleanup_interval)
            except Exception as e:
                logging.error(f"Error in resource cleanup: {e}")
                
    def _perform_cleanup(self):
        """Perform resource cleanup based on memory pressure."""
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # If memory usage is high, perform aggressive cleanup
        if current_memory > 800:  # 800MB threshold
            self._aggressive_cleanup()
        elif current_memory > 500:  # 500MB threshold
            self._gentle_cleanup()
            
    def _gentle_cleanup(self):
        """Gentle resource cleanup."""
        # Release oldest resources first
        to_remove = []
        for resource_id in list(self.active_resources.keys())[:5]:  # Clean up 5 oldest
            to_remove.append(resource_id)
            
        for resource_id in to_remove:
            self.release_resource(resource_id)
            
        # Force garbage collection
        gc.collect()
        
    def _aggressive_cleanup(self):
        """Aggressive resource cleanup for high memory usage."""
        # Release half of all resources
        resource_ids = list(self.active_resources.keys())
        to_remove = resource_ids[:len(resource_ids)//2]
        
        for resource_id in to_remove:
            self.release_resource(resource_id)
            
        # Multiple garbage collection passes
        for _ in range(3):
            gc.collect()
            
    def get_resource_count(self) -> int:
        """Get count of active resources."""
        return len(self.active_resources)


class ChunkedImageCollector:
    """
    Chunked image collection system to prevent memory overload.
    """
    
    def __init__(self, memory_manager: MemoryManager, chunk_size: int = 10):
        self.memory_manager = memory_manager
        self.chunk_size = chunk_size
        self.collected_chunks: List[List[Dict]] = []
        self.current_chunk: List[Dict] = []
        self.processing_queue = queue.Queue()
        self.chunk_callbacks: List[Callable] = []
        self._processing = False
        self._process_thread: Optional[threading.Thread] = None
        
    def add_image_data(self, image_data: Dict):
        """Add image data to current chunk."""
        self.current_chunk.append(image_data)
        
        if len(self.current_chunk) >= self.chunk_size:
            self._finalize_chunk()
            
    def _finalize_chunk(self):
        """Finalize current chunk and start a new one."""
        if self.current_chunk:
            chunk = self.current_chunk.copy()
            self.collected_chunks.append(chunk)
            self.processing_queue.put(chunk)
            self.current_chunk.clear()
            
            # Notify callbacks
            for callback in self.chunk_callbacks:
                try:
                    callback(chunk, len(self.collected_chunks))
                except Exception as e:
                    logging.error(f"Error in chunk callback: {e}")
                    
    def start_processing(self):
        """Start background chunk processing."""
        if not self._processing:
            self._processing = True
            self._process_thread = threading.Thread(
                target=self._process_chunks,
                daemon=True,
                name="ChunkProcessor"
            )
            self._process_thread.start()
            
    def stop_processing(self):
        """Stop chunk processing."""
        self._processing = False
        if self._process_thread:
            self._process_thread.join(timeout=5.0)
            
    def _process_chunks(self):
        """Process chunks in background."""
        while self._processing:
            try:
                chunk = self.processing_queue.get(timeout=1.0)
                self._process_chunk(chunk)
                self.processing_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Error processing chunk: {e}")
                
    def _process_chunk(self, chunk: List[Dict]):
        """Process a single chunk of images."""
        # Implement chunk-specific processing here
        # For example: optimize images, generate thumbnails, etc.
        
        # Clean up memory after processing
        self.memory_manager.perform_cleanup()
        
    def add_chunk_callback(self, callback: Callable):
        """Add callback for chunk completion."""
        self.chunk_callbacks.append(callback)
        
    def finalize_collection(self):
        """Finalize the current collection."""
        if self.current_chunk:
            self._finalize_chunk()
            
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        return {
            'total_chunks': len(self.collected_chunks),
            'current_chunk_size': len(self.current_chunk),
            'pending_processing': self.processing_queue.qsize(),
            'total_images': sum(len(chunk) for chunk in self.collected_chunks) + len(self.current_chunk)
        }


class UIResponsivenessOptimizer:
    """
    Optimizes UI responsiveness during heavy operations.
    """
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.update_queue = queue.Queue()
        self.progress_callbacks: Dict[str, Callable] = {}
        self._ui_thread: Optional[threading.Thread] = None
        self._ui_running = False
        self.debounce_delays: Dict[str, float] = defaultdict(lambda: 0.1)
        self.last_updates: Dict[str, float] = defaultdict(float)
        
    def start_ui_optimization(self):
        """Start UI optimization thread."""
        if not self._ui_running:
            self._ui_running = True
            self._ui_thread = threading.Thread(
                target=self._ui_update_loop,
                daemon=True,
                name="UIOptimizer"
            )
            self._ui_thread.start()
            
    def stop_ui_optimization(self):
        """Stop UI optimization."""
        self._ui_running = False
        if self._ui_thread:
            self._ui_thread.join(timeout=5.0)
            
    def schedule_ui_update(self, update_id: str, update_func: Callable, args: tuple = (), 
                          debounce: bool = True):
        """Schedule a UI update with optional debouncing."""
        current_time = time.time()
        
        if debounce:
            # Check if we should debounce this update
            last_update = self.last_updates[update_id]
            debounce_delay = self.debounce_delays[update_id]
            
            if current_time - last_update < debounce_delay:
                return  # Skip this update due to debouncing
                
        self.last_updates[update_id] = current_time
        self.update_queue.put((update_id, update_func, args))
        
    def _ui_update_loop(self):
        """UI update processing loop."""
        while self._ui_running:
            try:
                update_id, update_func, args = self.update_queue.get(timeout=0.1)
                
                # Execute update on main thread
                self.root.after_idle(lambda: self._execute_ui_update(update_func, args))
                
                self.update_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Error in UI update loop: {e}")
                
    def _execute_ui_update(self, update_func: Callable, args: tuple):
        """Execute UI update safely."""
        try:
            update_func(*args)
        except Exception as e:
            logging.error(f"Error executing UI update: {e}")
            
    def register_progress_callback(self, operation_id: str, callback: Callable):
        """Register progress callback for an operation."""
        self.progress_callbacks[operation_id] = callback
        
    def update_progress(self, operation_id: str, progress: float, message: str = ""):
        """Update progress for an operation."""
        callback = self.progress_callbacks.get(operation_id)
        if callback:
            self.schedule_ui_update(
                f"progress_{operation_id}",
                callback,
                (progress, message),
                debounce=True
            )
            
    def set_debounce_delay(self, update_id: str, delay: float):
        """Set debounce delay for a specific update type."""
        self.debounce_delays[update_id] = delay


class ProgressFeedbackSystem:
    """
    Advanced progress feedback system with cancellation support.
    """
    
    def __init__(self, parent_widget: tk.Widget):
        self.parent = parent_widget
        self.active_operations: Dict[str, Dict[str, Any]] = {}
        self.progress_widgets: Dict[str, Dict[str, tk.Widget]] = {}
        self.cancellation_callbacks: Dict[str, Callable] = {}
        
    def create_progress_widget(self, operation_id: str, title: str, 
                              can_cancel: bool = True) -> Dict[str, tk.Widget]:
        """Create progress widgets for an operation."""
        frame = ttk.Frame(self.parent)
        frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Title label
        title_label = ttk.Label(frame, text=title, font=('TkDefaultFont', 9))
        title_label.pack(anchor=tk.W)
        
        # Progress bar
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            frame, 
            mode='determinate',
            variable=progress_var,
            maximum=100
        )
        progress_bar.pack(fill=tk.X, pady=(2, 5))
        
        # Status and controls frame
        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill=tk.X)
        
        # Status label
        status_label = ttk.Label(
            controls_frame, 
            text="Starting...", 
            font=('TkDefaultFont', 8)
        )
        status_label.pack(side=tk.LEFT)
        
        widgets = {
            'frame': frame,
            'title_label': title_label,
            'progress_bar': progress_bar,
            'progress_var': progress_var,
            'status_label': status_label,
            'controls_frame': controls_frame
        }
        
        # Cancel button
        if can_cancel:
            cancel_button = ttk.Button(
                controls_frame,
                text="Cancel",
                command=lambda: self.cancel_operation(operation_id),
                style='Danger.TButton'
            )
            cancel_button.pack(side=tk.RIGHT)
            widgets['cancel_button'] = cancel_button
            
        self.progress_widgets[operation_id] = widgets
        self.active_operations[operation_id] = {
            'title': title,
            'progress': 0.0,
            'status': 'Starting...',
            'can_cancel': can_cancel,
            'cancelled': False
        }
        
        return widgets
        
    def update_progress(self, operation_id: str, progress: float, status: str = ""):
        """Update progress for an operation."""
        if operation_id not in self.active_operations:
            return
            
        # Update operation data
        operation = self.active_operations[operation_id]
        operation['progress'] = max(0.0, min(100.0, progress))
        if status:
            operation['status'] = status
            
        # Update UI widgets
        widgets = self.progress_widgets.get(operation_id)
        if widgets:
            widgets['progress_var'].set(operation['progress'])
            widgets['status_label'].configure(text=operation['status'])
            
        # Auto-remove completed operations
        if progress >= 100.0:
            self.parent.after(2000, lambda: self.remove_operation(operation_id))
            
    def cancel_operation(self, operation_id: str):
        """Cancel an operation."""
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            operation['cancelled'] = True
            operation['status'] = "Cancelled"
            
            # Update UI
            widgets = self.progress_widgets.get(operation_id)
            if widgets:
                widgets['status_label'].configure(text="Cancelled")
                widgets['progress_bar'].configure(mode='indeterminate')
                widgets['progress_bar'].start()
                if 'cancel_button' in widgets:
                    widgets['cancel_button'].configure(state=tk.DISABLED)
                    
            # Call cancellation callback
            callback = self.cancellation_callbacks.get(operation_id)
            if callback:
                try:
                    callback()
                except Exception as e:
                    logging.error(f"Error in cancellation callback: {e}")
                    
            # Remove after delay
            self.parent.after(1000, lambda: self.remove_operation(operation_id))
            
    def remove_operation(self, operation_id: str):
        """Remove an operation and its widgets."""
        if operation_id in self.progress_widgets:
            widgets = self.progress_widgets[operation_id]
            widgets['frame'].destroy()
            del self.progress_widgets[operation_id]
            
        if operation_id in self.active_operations:
            del self.active_operations[operation_id]
            
        if operation_id in self.cancellation_callbacks:
            del self.cancellation_callbacks[operation_id]
            
    def register_cancellation_callback(self, operation_id: str, callback: Callable):
        """Register callback for operation cancellation."""
        self.cancellation_callbacks[operation_id] = callback
        
    def is_cancelled(self, operation_id: str) -> bool:
        """Check if an operation is cancelled."""
        operation = self.active_operations.get(operation_id)
        return operation.get('cancelled', False) if operation else False
        
    def get_active_operations(self) -> List[str]:
        """Get list of active operation IDs."""
        return list(self.active_operations.keys())


class PerformanceOptimizer:
    """
    Main performance optimization coordinator.
    """
    
    def __init__(self, root: tk.Tk, data_dir: str):
        self.root = root
        self.data_dir = data_dir
        
        # Initialize components
        self.memory_manager = MemoryManager()
        self.task_queue = TaskQueue(max_workers=4)
        self.performance_monitor = PerformanceMonitor()
        self.image_optimizer = ImageOptimizer(self.memory_manager, self.task_queue)
        self.resource_manager = ResourceManager()
        self.chunked_collector = ChunkedImageCollector(self.memory_manager)
        self.ui_optimizer = UIResponsivenessOptimizer(root)
        
        # Performance thresholds
        self.memory_warning_threshold = 400.0  # MB
        self.memory_critical_threshold = 800.0  # MB
        self.performance_callbacks: List[Callable] = []
        
        # Statistics
        self.stats = {
            'total_images_processed': 0,
            'memory_cleanups_performed': 0,
            'ui_optimizations_applied': 0,
            'chunks_processed': 0
        }
        
    def start_optimization(self):
        """Start all optimization systems."""
        self.memory_manager.start_monitoring(interval=15.0)
        self.performance_monitor.start_monitoring(interval=5.0)
        self.resource_manager.start_auto_cleanup()
        self.chunked_collector.start_processing()
        self.ui_optimizer.start_ui_optimization()
        
        # Register performance callback
        self.performance_monitor.add_callback(self._performance_callback)
        
    def stop_optimization(self):
        """Stop all optimization systems."""
        self.memory_manager.stop_monitoring()
        self.performance_monitor.stop_monitoring()
        self.resource_manager.stop_auto_cleanup()
        self.chunked_collector.stop_processing()
        self.ui_optimizer.stop_ui_optimization()
        
        # Cleanup
        self.task_queue.shutdown()
        
    def _performance_callback(self, metrics):
        """Handle performance metrics updates."""
        # Check for memory pressure
        if metrics.memory_usage_mb > self.memory_critical_threshold:
            self._handle_critical_memory()
        elif metrics.memory_usage_mb > self.memory_warning_threshold:
            self._handle_memory_warning()
            
        # Update UI with performance info
        self.ui_optimizer.schedule_ui_update(
            "performance_update",
            self._update_performance_display,
            (metrics,)
        )
        
        # Notify callbacks
        for callback in self.performance_callbacks:
            try:
                callback(metrics)
            except Exception as e:
                logging.error(f"Error in performance callback: {e}")
                
    def _handle_memory_warning(self):
        """Handle memory warning threshold."""
        self.memory_manager.perform_cleanup()
        self.image_optimizer.lazy_loader.cleanup_dead_widgets()
        self.stats['memory_cleanups_performed'] += 1
        
    def _handle_critical_memory(self):
        """Handle critical memory threshold."""
        self.memory_manager.perform_aggressive_cleanup()
        self.resource_manager._aggressive_cleanup()
        self.stats['memory_cleanups_performed'] += 1
        
    def _update_performance_display(self, metrics):
        """Update performance display in UI."""
        # This would update performance indicators in the UI
        # Implementation depends on specific UI components
        pass
        
    def optimize_image_collection(self, images: List[Dict], 
                                 progress_callback: Optional[Callable] = None) -> List[Dict]:
        """Optimize image collection processing."""
        optimized_images = []
        total_images = len(images)
        
        # Process images in chunks
        for i, image_data in enumerate(images):
            if progress_callback:
                progress = (i / total_images) * 100
                progress_callback(progress, f"Processing image {i+1}/{total_images}")
                
            # Add to chunked collector
            self.chunked_collector.add_image_data(image_data)
            
            # Optimize image if needed
            if 'url' in image_data:
                self._optimize_single_image(image_data)
                
            optimized_images.append(image_data)
            self.stats['total_images_processed'] += 1
            
            # Check for memory pressure periodically
            if i % 10 == 0:
                current_memory = self.memory_manager.get_memory_usage_mb()
                if current_memory > self.memory_warning_threshold:
                    self._handle_memory_warning()
                    
        # Finalize collection
        self.chunked_collector.finalize_collection()
        
        if progress_callback:
            progress_callback(100.0, "Collection optimization complete")
            
        return optimized_images
        
    def _optimize_single_image(self, image_data: Dict):
        """Optimize a single image."""
        # Implement single image optimization
        # This could include resizing, format conversion, etc.
        pass
        
    def create_progress_feedback(self, parent: tk.Widget) -> ProgressFeedbackSystem:
        """Create progress feedback system."""
        return ProgressFeedbackSystem(parent)
        
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization report."""
        memory_stats = self.memory_manager.get_cache_stats()
        queue_stats = self.task_queue.get_queue_stats()
        collection_stats = self.chunked_collector.get_collection_stats()
        optimization_stats = self.image_optimizer.get_optimization_stats()
        
        return {
            'memory_optimization': {
                'current_usage_mb': memory_stats['memory_usage_mb'],
                'peak_usage_mb': memory_stats['peak_memory_mb'],
                'cache_hit_ratio': memory_stats['hit_ratio'],
                'cleanups_performed': self.stats['memory_cleanups_performed']
            },
            'task_processing': {
                'pending_tasks': queue_stats['pending_tasks'],
                'completed_tasks': queue_stats['completed_tasks'],
                'failed_tasks': queue_stats['tasks_failed'],
                'average_processing_time': queue_stats['avg_processing_time']
            },
            'collection_processing': {
                'total_chunks': collection_stats['total_chunks'],
                'total_images': collection_stats['total_images'],
                'pending_processing': collection_stats['pending_processing']
            },
            'image_optimization': {
                'images_loaded': optimization_stats['images_loaded'],
                'average_load_time': optimization_stats['average_load_time'],
                'active_loading_tasks': optimization_stats['active_loading_tasks']
            },
            'system_resources': {
                'active_resources': self.resource_manager.get_resource_count(),
                'active_threads': threading.active_count()
            },
            'overall_stats': self.stats.copy()
        }
        
    def add_performance_callback(self, callback: Callable):
        """Add performance monitoring callback."""
        self.performance_callbacks.append(callback)
        
    def get_performance_metrics(self) -> Optional[PerformanceMetrics]:
        """Get current performance metrics."""
        monitor_metrics = self.performance_monitor.get_current_metrics()
        if not monitor_metrics:
            return None
            
        memory_stats = self.memory_manager.get_cache_stats()
        optimization_stats = self.image_optimizer.get_optimization_stats()
        
        return PerformanceMetrics(
            memory_usage_mb=monitor_metrics.memory_usage_mb,
            cpu_usage_percent=monitor_metrics.cpu_usage_percent,
            images_processed=self.stats['total_images_processed'],
            cache_hit_ratio=memory_stats['hit_ratio'],
            average_load_time=optimization_stats.get('average_load_time', 0),
            ui_responsiveness=monitor_metrics.fps,
            active_threads=monitor_metrics.active_threads,
            pending_tasks=self.task_queue.get_queue_stats()['pending_tasks']
        )