"""
Performance monitoring dashboard component for the UI.
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from typing import Dict, List, Optional, Any
import time
from collections import deque
import threading
from ...utils.performance import PerformanceMonitor, MemoryManager, TaskQueue


class PerformanceWidget(tk.Frame):
    """Base widget for performance display components."""
    
    def __init__(self, parent, title: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        self.title = title
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the basic UI structure."""
        if self.title:
            title_label = tk.Label(
                self, 
                text=self.title,
                font=('TkDefaultFont', 10, 'bold')
            )
            title_label.pack(anchor='w', padx=5, pady=(5, 0))


class MetricsDisplayWidget(PerformanceWidget):
    """Widget to display current performance metrics."""
    
    def __init__(self, parent, performance_monitor: PerformanceMonitor, **kwargs):
        self.performance_monitor = performance_monitor
        self.metric_vars: Dict[str, tk.StringVar] = {}
        super().__init__(parent, title="Performance Metrics", **kwargs)
        
    def _setup_ui(self):
        """Setup metrics display UI."""
        super()._setup_ui()
        
        # Create metrics frame
        metrics_frame = tk.Frame(self, relief=tk.SUNKEN, borderwidth=1)
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Memory usage
        self.metric_vars['memory'] = tk.StringVar(value="Memory: -- MB")
        memory_label = tk.Label(metrics_frame, textvariable=self.metric_vars['memory'])
        memory_label.pack(anchor='w', padx=5, pady=2)
        
        # CPU usage
        self.metric_vars['cpu'] = tk.StringVar(value="CPU: --%")
        cpu_label = tk.Label(metrics_frame, textvariable=self.metric_vars['cpu'])
        cpu_label.pack(anchor='w', padx=5, pady=2)
        
        # FPS
        self.metric_vars['fps'] = tk.StringVar(value="FPS: --")
        fps_label = tk.Label(metrics_frame, textvariable=self.metric_vars['fps'])
        fps_label.pack(anchor='w', padx=5, pady=2)
        
        # Active threads
        self.metric_vars['threads'] = tk.StringVar(value="Threads: --")
        threads_label = tk.Label(metrics_frame, textvariable=self.metric_vars['threads'])
        threads_label.pack(anchor='w', padx=5, pady=2)
        
        # Start updating
        self._update_metrics()
        
    def _update_metrics(self):
        """Update displayed metrics."""
        try:
            current_metrics = self.performance_monitor.get_current_metrics()
            if current_metrics:
                self.metric_vars['memory'].set(f"Memory: {current_metrics.memory_usage_mb:.1f} MB")
                self.metric_vars['cpu'].set(f"CPU: {current_metrics.cpu_usage_percent:.1f}%")
                self.metric_vars['fps'].set(f"FPS: {current_metrics.fps:.1f}")
                self.metric_vars['threads'].set(f"Threads: {current_metrics.active_threads}")
                
        except Exception as e:
            print(f"Error updating metrics: {e}")
            
        # Schedule next update
        self.after(1000, self._update_metrics)


class MemoryCacheWidget(PerformanceWidget):
    """Widget to display memory and cache statistics."""
    
    def __init__(self, parent, memory_manager: MemoryManager, **kwargs):
        self.memory_manager = memory_manager
        self.cache_vars: Dict[str, tk.StringVar] = {}
        super().__init__(parent, title="Memory & Cache", **kwargs)
        
    def _setup_ui(self):
        """Setup cache display UI."""
        super()._setup_ui()
        
        # Create cache info frame
        cache_frame = tk.Frame(self, relief=tk.SUNKEN, borderwidth=1)
        cache_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Image cache stats
        self.cache_vars['image_cache'] = tk.StringVar(value="Image Cache: --")
        image_cache_label = tk.Label(cache_frame, textvariable=self.cache_vars['image_cache'])
        image_cache_label.pack(anchor='w', padx=5, pady=2)
        
        # Hit ratio
        self.cache_vars['hit_ratio'] = tk.StringVar(value="Hit Ratio: --%")
        hit_ratio_label = tk.Label(cache_frame, textvariable=self.cache_vars['hit_ratio'])
        hit_ratio_label.pack(anchor='w', padx=5, pady=2)
        
        # Memory usage
        self.cache_vars['cache_memory'] = tk.StringVar(value="Cache Memory: -- MB")
        memory_label = tk.Label(cache_frame, textvariable=self.cache_vars['cache_memory'])
        memory_label.pack(anchor='w', padx=5, pady=2)
        
        # Cleanup button
        cleanup_button = tk.Button(
            cache_frame,
            text="Clear Caches",
            command=self.memory_manager.clear_all_caches,
            width=15
        )
        cleanup_button.pack(anchor='w', padx=5, pady=5)
        
        # Start updating
        self._update_cache_stats()
        
    def _update_cache_stats(self):
        """Update cache statistics display."""
        try:
            stats = self.memory_manager.get_cache_stats()
            
            # Image cache info
            img_cache = stats.get('image_cache', {})
            size = img_cache.get('size', 0)
            max_size = img_cache.get('max_size', 0)
            self.cache_vars['image_cache'].set(f"Image Cache: {size}/{max_size} items")
            
            # Hit ratio
            hit_ratio = stats.get('hit_ratio', 0) * 100
            self.cache_vars['hit_ratio'].set(f"Hit Ratio: {hit_ratio:.1f}%")
            
            # Memory usage
            memory_mb = stats.get('memory_usage_mb', 0)
            self.cache_vars['cache_memory'].set(f"Cache Memory: {memory_mb:.1f} MB")
            
        except Exception as e:
            print(f"Error updating cache stats: {e}")
            
        # Schedule next update
        self.after(2000, self._update_cache_stats)


class TaskQueueWidget(PerformanceWidget):
    """Widget to display task queue status."""
    
    def __init__(self, parent, task_queue: TaskQueue, **kwargs):
        self.task_queue = task_queue
        self.queue_vars: Dict[str, tk.StringVar] = {}
        super().__init__(parent, title="Background Tasks", **kwargs)
        
    def _setup_ui(self):
        """Setup task queue display UI."""
        super()._setup_ui()
        
        # Create queue info frame
        queue_frame = tk.Frame(self, relief=tk.SUNKEN, borderwidth=1)
        queue_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pending tasks
        self.queue_vars['pending'] = tk.StringVar(value="Pending: --")
        pending_label = tk.Label(queue_frame, textvariable=self.queue_vars['pending'])
        pending_label.pack(anchor='w', padx=5, pady=2)
        
        # Active tasks
        self.queue_vars['active'] = tk.StringVar(value="Active: --")
        active_label = tk.Label(queue_frame, textvariable=self.queue_vars['active'])
        active_label.pack(anchor='w', padx=5, pady=2)
        
        # Completed tasks
        self.queue_vars['completed'] = tk.StringVar(value="Completed: --")
        completed_label = tk.Label(queue_frame, textvariable=self.queue_vars['completed'])
        completed_label.pack(anchor='w', padx=5, pady=2)
        
        # Average processing time
        self.queue_vars['avg_time'] = tk.StringVar(value="Avg Time: --s")
        avg_time_label = tk.Label(queue_frame, textvariable=self.queue_vars['avg_time'])
        avg_time_label.pack(anchor='w', padx=5, pady=2)
        
        # Active task list
        task_list_label = tk.Label(queue_frame, text="Active Tasks:", font=('TkDefaultFont', 9, 'bold'))
        task_list_label.pack(anchor='w', padx=5, pady=(5, 2))
        
        self.task_listbox = tk.Listbox(queue_frame, height=4, font=('TkDefaultFont', 8))
        self.task_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Start updating
        self._update_queue_stats()
        
    def _update_queue_stats(self):
        """Update task queue statistics."""
        try:
            stats = self.task_queue.get_queue_stats()
            
            self.queue_vars['pending'].set(f"Pending: {stats['pending_tasks']}")
            self.queue_vars['active'].set(f"Active: {stats['active_tasks']}")
            self.queue_vars['completed'].set(f"Completed: {stats['completed_tasks']}")
            self.queue_vars['avg_time'].set(f"Avg Time: {stats['avg_processing_time']:.2f}s")
            
            # Update active task list
            self.task_listbox.delete(0, tk.END)
            active_tasks = self.task_queue.get_active_tasks()
            for task in active_tasks[:10]:  # Show only first 10
                progress_text = f"({task.progress:.0%})" if task.progress > 0 else ""
                self.task_listbox.insert(tk.END, f"{task.name} {progress_text}")
                
        except Exception as e:
            print(f"Error updating queue stats: {e}")
            
        # Schedule next update
        self.after(1500, self._update_queue_stats)


class PerformanceGraphWidget(PerformanceWidget):
    """Widget with performance graphs using matplotlib."""
    
    def __init__(self, parent, performance_monitor: PerformanceMonitor, **kwargs):
        self.performance_monitor = performance_monitor
        self.fig = None
        self.axes = {}
        self.canvas = None
        self.animation = None
        
        # Data for plotting
        self.time_data = deque(maxlen=60)  # Last 60 seconds
        self.memory_data = deque(maxlen=60)
        self.cpu_data = deque(maxlen=60)
        self.fps_data = deque(maxlen=60)
        
        super().__init__(parent, title="Performance Graphs", **kwargs)
        
    def _setup_ui(self):
        """Setup graph display UI."""
        super()._setup_ui()
        
        try:
            # Create matplotlib figure
            self.fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(8, 6))
            self.fig.tight_layout(pad=2.0)
            
            # Configure axes
            self.axes['memory'] = ax1
            self.axes['cpu'] = ax2
            self.axes['fps'] = ax3
            self.axes['threads'] = ax4
            
            ax1.set_title('Memory Usage (MB)')
            ax1.set_ylabel('MB')
            
            ax2.set_title('CPU Usage (%)')
            ax2.set_ylabel('%')
            
            ax3.set_title('FPS')
            ax3.set_ylabel('FPS')
            
            ax4.set_title('Active Threads')
            ax4.set_ylabel('Count')
            
            # Create canvas
            self.canvas = FigureCanvasTkAgg(self.fig, self)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Start animation
            self.animation = animation.FuncAnimation(
                self.fig, 
                self._update_graphs, 
                interval=1000,
                blit=False
            )
            
        except ImportError:
            # Matplotlib not available, show message
            error_label = tk.Label(
                self,
                text="Matplotlib not available.\nGraphs disabled.",
                justify=tk.CENTER
            )
            error_label.pack(expand=True)
            
    def _update_graphs(self, frame):
        """Update performance graphs."""
        try:
            current_metrics = self.performance_monitor.get_current_metrics()
            if not current_metrics:
                return
                
            # Add new data point
            current_time = time.time()
            self.time_data.append(current_time)
            self.memory_data.append(current_metrics.memory_usage_mb)
            self.cpu_data.append(current_metrics.cpu_usage_percent)
            self.fps_data.append(current_metrics.fps)
            
            # Convert to relative time (last 60 seconds)
            if len(self.time_data) > 1:
                relative_times = [(t - self.time_data[0]) for t in self.time_data]
                
                # Clear and update each axis
                for ax in self.axes.values():
                    ax.clear()
                    
                # Memory graph
                ax1 = self.axes['memory']
                ax1.plot(relative_times, self.memory_data, 'b-', linewidth=2)
                ax1.set_title('Memory Usage (MB)')
                ax1.set_ylabel('MB')
                ax1.grid(True, alpha=0.3)
                
                # CPU graph
                ax2 = self.axes['cpu']
                ax2.plot(relative_times, self.cpu_data, 'r-', linewidth=2)
                ax2.set_title('CPU Usage (%)')
                ax2.set_ylabel('%')
                ax2.set_ylim(0, 100)
                ax2.grid(True, alpha=0.3)
                
                # FPS graph
                ax3 = self.axes['fps']
                ax3.plot(relative_times, self.fps_data, 'g-', linewidth=2)
                ax3.set_title('FPS')
                ax3.set_ylabel('FPS')
                ax3.grid(True, alpha=0.3)
                
                # Update canvas
                self.canvas.draw()
                
        except Exception as e:
            print(f"Error updating graphs: {e}")


class PerformanceMonitorDashboard(tk.Toplevel):
    """
    Main performance monitoring dashboard window.
    """
    
    def __init__(
        self,
        parent,
        performance_monitor: PerformanceMonitor,
        memory_manager: MemoryManager,
        task_queue: TaskQueue,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.performance_monitor = performance_monitor
        self.memory_manager = memory_manager
        self.task_queue = task_queue
        
        self.title("Performance Monitor")
        self.geometry("900x700")
        self.resizable(True, True)
        
        # Don't destroy main app when closing this window
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the dashboard UI."""
        # Create main container with notebook for tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Real-time metrics tab
        realtime_frame = tk.Frame(notebook)
        notebook.add(realtime_frame, text="Real-time")
        
        # Left column - current metrics
        left_frame = tk.Frame(realtime_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        
        # Right column - graphs
        right_frame = tk.Frame(realtime_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Add widgets to left column
        metrics_widget = MetricsDisplayWidget(left_frame, self.performance_monitor)
        metrics_widget.pack(fill=tk.X, pady=(0, 10))
        
        cache_widget = MemoryCacheWidget(left_frame, self.memory_manager)
        cache_widget.pack(fill=tk.X, pady=(0, 10))
        
        queue_widget = TaskQueueWidget(left_frame, self.task_queue)
        queue_widget.pack(fill=tk.BOTH, expand=True)
        
        # Add graphs to right column
        try:
            graph_widget = PerformanceGraphWidget(right_frame, self.performance_monitor)
            graph_widget.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            print(f"Failed to create graphs: {e}")
            # Fallback to text display
            fallback_label = tk.Label(
                right_frame,
                text="Performance graphs unavailable.\nInstall matplotlib for visual graphs.",
                justify=tk.CENTER
            )
            fallback_label.pack(expand=True)
            
        # Statistics tab
        stats_frame = tk.Frame(notebook)
        notebook.add(stats_frame, text="Statistics")
        
        # Add statistics view
        self._setup_statistics_tab(stats_frame)
        
        # Controls tab
        controls_frame = tk.Frame(notebook)
        notebook.add(controls_frame, text="Controls")
        
        # Add control buttons
        self._setup_controls_tab(controls_frame)
        
    def _setup_statistics_tab(self, parent):
        """Setup the statistics tab."""
        # Create text widget with scrollbar for stats
        text_frame = tk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.stats_text = tk.Text(text_frame, wrap=tk.WORD, font=('Courier', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.stats_text.yview)
        
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.stats_text.config(yscrollcommand=scrollbar.set)
        
        # Refresh button
        refresh_button = tk.Button(
            parent,
            text="Refresh Statistics",
            command=self._refresh_statistics,
            width=20
        )
        refresh_button.pack(pady=5)
        
        # Initial load
        self._refresh_statistics()
        
    def _setup_controls_tab(self, parent):
        """Setup the controls tab."""
        controls_frame = tk.Frame(parent)
        controls_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Memory controls
        memory_label = tk.Label(controls_frame, text="Memory Management", font=('TkDefaultFont', 12, 'bold'))
        memory_label.pack(anchor='w', pady=(0, 10))
        
        clear_cache_button = tk.Button(
            controls_frame,
            text="Clear All Caches",
            command=self.memory_manager.clear_all_caches,
            width=20
        )
        clear_cache_button.pack(anchor='w', pady=2)
        
        force_gc_button = tk.Button(
            controls_frame,
            text="Force Garbage Collection",
            command=self.memory_manager.perform_cleanup,
            width=20
        )
        force_gc_button.pack(anchor='w', pady=2)
        
        # Performance controls
        perf_label = tk.Label(controls_frame, text="Performance", font=('TkDefaultFont', 12, 'bold'))
        perf_label.pack(anchor='w', pady=(20, 10))
        
        reset_stats_button = tk.Button(
            controls_frame,
            text="Reset Statistics",
            command=self.performance_monitor.reset_metrics,
            width=20
        )
        reset_stats_button.pack(anchor='w', pady=2)
        
        export_stats_button = tk.Button(
            controls_frame,
            text="Export Performance Data",
            command=self._export_performance_data,
            width=20
        )
        export_stats_button.pack(anchor='w', pady=2)
        
    def _refresh_statistics(self):
        """Refresh the statistics display."""
        try:
            # Get all statistics
            perf_stats = self.performance_monitor.get_api_stats()
            cache_stats = self.memory_manager.get_cache_stats()
            queue_stats = self.task_queue.get_queue_stats()
            
            # Format statistics text
            stats_text = "PERFORMANCE STATISTICS\n"
            stats_text += "=" * 50 + "\n\n"
            
            # API Statistics
            stats_text += "API CALL STATISTICS:\n"
            stats_text += "-" * 20 + "\n"
            for endpoint, stats in perf_stats.items():
                stats_text += f"{endpoint}:\n"
                stats_text += f"  Total Calls: {stats['total_calls']}\n"
                stats_text += f"  Avg Response: {stats['avg_response_time']:.2f}ms\n"
                stats_text += f"  Success Rate: {stats['success_rate']:.1%}\n\n"
                
            # Memory Statistics
            stats_text += "\nMEMORY STATISTICS:\n"
            stats_text += "-" * 20 + "\n"
            stats_text += f"Current Memory: {cache_stats['memory_usage_mb']:.1f} MB\n"
            stats_text += f"Peak Memory: {cache_stats['peak_memory_mb']:.1f} MB\n"
            stats_text += f"Cache Hit Ratio: {cache_stats['hit_ratio']:.1%}\n"
            stats_text += f"Cleanups Performed: {cache_stats['cleanups_performed']}\n\n"
            
            # Task Queue Statistics
            stats_text += "\nTASK QUEUE STATISTICS:\n"
            stats_text += "-" * 20 + "\n"
            stats_text += f"Pending Tasks: {queue_stats['pending_tasks']}\n"
            stats_text += f"Active Tasks: {queue_stats['active_tasks']}\n"
            stats_text += f"Completed Tasks: {queue_stats['completed_tasks']}\n"
            stats_text += f"Failed Tasks: {queue_stats['tasks_failed']}\n"
            stats_text += f"Average Processing Time: {queue_stats['avg_processing_time']:.2f}s\n"
            
            # Update text widget
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_text)
            
        except Exception as e:
            error_text = f"Error refreshing statistics: {e}\n"
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, error_text)
            
    def _export_performance_data(self):
        """Export performance data to file."""
        try:
            from tkinter.filedialog import asksaveasfilename
            from pathlib import Path
            import json
            
            filename = asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Export Performance Data"
            )
            
            if filename:
                file_path = Path(filename)
                self.performance_monitor.export_metrics(file_path)
                
                # Show success message
                success_label = tk.Label(
                    self,
                    text=f"Performance data exported to {file_path.name}",
                    fg="green"
                )
                success_label.pack(pady=5)
                self.after(3000, success_label.destroy)  # Remove after 3 seconds
                
        except Exception as e:
            print(f"Error exporting performance data: {e}")
            
    def show(self):
        """Show the performance monitor dashboard."""
        self.deiconify()
        self.lift()
        self.focus_set()
        
    def hide(self):
        """Hide the performance monitor dashboard."""
        self.withdraw()