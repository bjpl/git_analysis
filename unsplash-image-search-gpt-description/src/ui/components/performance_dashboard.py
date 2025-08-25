"""
Performance Dashboard Widget for real-time performance monitoring.
"""

import tkinter as tk
from tkinter import ttk
import time
import threading
from typing import Dict, Any, Optional, Callable
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class PerformanceGraph:
    """Real-time performance graph widget."""
    
    def __init__(self, parent: tk.Widget, title: str, max_points: int = 60):
        self.parent = parent
        self.title = title
        self.max_points = max_points
        self.data_points = deque(maxlen=max_points)
        self.time_points = deque(maxlen=max_points)
        
        # Create matplotlib figure
        self.figure, self.ax = plt.subplots(figsize=(6, 3))
        self.figure.patch.set_facecolor('#f0f0f0')
        self.ax.set_title(title, fontsize=10)
        self.ax.set_ylabel('Value')
        self.ax.grid(True, alpha=0.3)
        
        # Initialize empty line
        self.line, = self.ax.plot([], [], 'b-', linewidth=2)
        self.ax.set_xlim(0, max_points)
        self.ax.set_ylim(0, 100)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def add_data_point(self, value: float):
        """Add a new data point to the graph."""
        current_time = time.time()
        self.data_points.append(value)
        self.time_points.append(current_time)
        
        # Update the line data
        if len(self.data_points) > 1:
            # Use relative time for x-axis
            relative_times = [t - self.time_points[0] for t in self.time_points]
            self.line.set_data(relative_times, list(self.data_points))
            
            # Update axis limits
            if self.data_points:
                self.ax.set_ylim(0, max(100, max(self.data_points) * 1.1))
            if relative_times:
                self.ax.set_xlim(0, max(60, relative_times[-1]))
                
        # Redraw the canvas
        self.canvas.draw_idle()
        
    def set_y_limit(self, max_y: float):
        """Set the maximum Y axis limit."""
        self.ax.set_ylim(0, max_y)
        self.canvas.draw_idle()
        
    def clear(self):
        """Clear all data points."""
        self.data_points.clear()
        self.time_points.clear()
        self.line.set_data([], [])
        self.canvas.draw_idle()


class MetricsDisplay:
    """Display for key performance metrics."""
    
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.metrics_frame = ttk.LabelFrame(parent, text="Performance Metrics", padding="10")
        self.metrics_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.metrics_vars = {}
        self.metrics_labels = {}
        
        # Create metric displays
        self._create_metric_display("Memory Usage", "memory_mb", "MB")
        self._create_metric_display("CPU Usage", "cpu_percent", "%")
        self._create_metric_display("Cache Hit Ratio", "cache_hit_ratio", "%")
        self._create_metric_display("Images Processed", "images_processed", "")
        self._create_metric_display("Pending Tasks", "pending_tasks", "")
        self._create_metric_display("Active Threads", "active_threads", "")
        
    def _create_metric_display(self, label: str, key: str, unit: str):
        """Create a metric display row."""
        row_frame = ttk.Frame(self.metrics_frame)
        row_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(row_frame, text=f"{label}:", width=15).pack(side=tk.LEFT)
        
        var = tk.StringVar(value="0")
        self.metrics_vars[key] = var
        
        value_label = ttk.Label(row_frame, textvariable=var, font=('TkDefaultFont', 9, 'bold'))
        value_label.pack(side=tk.LEFT, padx=(5, 2))
        
        if unit:
            ttk.Label(row_frame, text=unit).pack(side=tk.LEFT)
            
        self.metrics_labels[key] = value_label
        
    def update_metric(self, key: str, value: Any, format_str: str = "{:.1f}"):
        """Update a specific metric."""
        if key in self.metrics_vars:
            if isinstance(value, (int, float)):
                formatted_value = format_str.format(value)
            else:
                formatted_value = str(value)
            self.metrics_vars[key].set(formatted_value)
            
            # Color coding for critical values
            if key == "memory_mb" and value > 800:
                self.metrics_labels[key].configure(foreground='red')
            elif key == "cpu_percent" and value > 80:
                self.metrics_labels[key].configure(foreground='red')
            else:
                self.metrics_labels[key].configure(foreground='black')


class PerformanceAlerts:
    """Performance alert system."""
    
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.alerts_frame = ttk.LabelFrame(parent, text="Performance Alerts", padding="10")
        self.alerts_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.alert_text = tk.Text(
            self.alerts_frame, 
            height=4, 
            state=tk.DISABLED,
            font=('TkDefaultFont', 8)
        )
        self.alert_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for alerts
        scrollbar = ttk.Scrollbar(self.alerts_frame, orient="vertical", command=self.alert_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.alert_text.config(yscrollcommand=scrollbar.set)
        
        # Clear button
        clear_btn = ttk.Button(self.alerts_frame, text="Clear Alerts", command=self.clear_alerts)
        clear_btn.pack(pady=(5, 0))
        
    def add_alert(self, level: str, message: str):
        """Add a performance alert."""
        timestamp = time.strftime("%H:%M:%S")
        alert_text = f"[{timestamp}] {level.upper()}: {message}\n"
        
        self.alert_text.configure(state=tk.NORMAL)
        self.alert_text.insert(tk.END, alert_text)
        
        # Color coding
        if level.lower() == "critical":
            self.alert_text.tag_add("critical", f"end-{len(alert_text)}c", "end-1c")
            self.alert_text.tag_config("critical", foreground="red")
        elif level.lower() == "warning":
            self.alert_text.tag_add("warning", f"end-{len(alert_text)}c", "end-1c")
            self.alert_text.tag_config("warning", foreground="orange")
            
        self.alert_text.configure(state=tk.DISABLED)
        self.alert_text.see(tk.END)
        
    def clear_alerts(self):
        """Clear all alerts."""
        self.alert_text.configure(state=tk.NORMAL)
        self.alert_text.delete(1.0, tk.END)
        self.alert_text.configure(state=tk.DISABLED)


class OptimizationControls:
    """Controls for performance optimization."""
    
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.controls_frame = ttk.LabelFrame(parent, text="Optimization Controls", padding="10")
        self.controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.optimization_callbacks = {}
        
        # Cleanup buttons
        cleanup_frame = ttk.Frame(self.controls_frame)
        cleanup_frame.pack(fill=tk.X, pady=2)
        
        ttk.Button(
            cleanup_frame, 
            text="Clear Memory Cache", 
            command=self._clear_memory_cache
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            cleanup_frame, 
            text="Force Garbage Collection", 
            command=self._force_gc
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            cleanup_frame, 
            text="Optimize Resources", 
            command=self._optimize_resources
        ).pack(side=tk.LEFT)
        
        # Settings frame
        settings_frame = ttk.Frame(self.controls_frame)
        settings_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Memory threshold setting
        ttk.Label(settings_frame, text="Memory Limit (MB):").pack(side=tk.LEFT)
        self.memory_limit_var = tk.StringVar(value="800")
        memory_entry = ttk.Entry(settings_frame, textvariable=self.memory_limit_var, width=10)
        memory_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(
            settings_frame,
            text="Apply Settings",
            command=self._apply_settings
        ).pack(side=tk.LEFT)
        
    def register_callback(self, action: str, callback: Callable):
        """Register callback for optimization actions."""
        self.optimization_callbacks[action] = callback
        
    def _clear_memory_cache(self):
        """Clear memory cache."""
        callback = self.optimization_callbacks.get('clear_cache')
        if callback:
            callback()
            
    def _force_gc(self):
        """Force garbage collection."""
        callback = self.optimization_callbacks.get('force_gc')
        if callback:
            callback()
            
    def _optimize_resources(self):
        """Optimize resources."""
        callback = self.optimization_callbacks.get('optimize_resources')
        if callback:
            callback()
            
    def _apply_settings(self):
        """Apply optimization settings."""
        try:
            memory_limit = float(self.memory_limit_var.get())
            callback = self.optimization_callbacks.get('apply_settings')
            if callback:
                callback({'memory_limit': memory_limit})
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid memory limit value")


class PerformanceDashboard:
    """
    Complete performance monitoring dashboard.
    """
    
    def __init__(self, parent: tk.Widget, performance_optimizer):
        self.parent = parent
        self.optimizer = performance_optimizer
        self.dashboard_window = None
        self.monitoring_active = False
        self.update_thread = None
        
        # Performance thresholds
        self.memory_warning_threshold = 500.0
        self.memory_critical_threshold = 800.0
        self.cpu_warning_threshold = 80.0
        
    def show_dashboard(self):
        """Show the performance dashboard window."""
        if self.dashboard_window:
            self.dashboard_window.lift()
            return
            
        self.dashboard_window = tk.Toplevel(self.parent)
        self.dashboard_window.title("Performance Dashboard")
        self.dashboard_window.geometry("800x600")
        self.dashboard_window.protocol("WM_DELETE_WINDOW", self.hide_dashboard)
        
        # Create main container with scrolling
        canvas = tk.Canvas(self.dashboard_window)
        scrollbar = ttk.Scrollbar(self.dashboard_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Create dashboard components
        self.metrics_display = MetricsDisplay(scrollable_frame)
        self.performance_alerts = PerformanceAlerts(scrollable_frame)
        self.optimization_controls = OptimizationControls(scrollable_frame)
        
        # Create performance graphs
        graphs_frame = ttk.LabelFrame(scrollable_frame, text="Performance Graphs", padding="10")
        graphs_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Memory usage graph
        memory_frame = ttk.Frame(graphs_frame)
        memory_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.memory_graph = PerformanceGraph(memory_frame, "Memory Usage (MB)", max_points=120)
        
        # CPU usage graph
        cpu_frame = ttk.Frame(graphs_frame)
        cpu_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.cpu_graph = PerformanceGraph(cpu_frame, "CPU Usage (%)", max_points=120)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Register optimization callbacks
        self.optimization_controls.register_callback('clear_cache', self._clear_cache)
        self.optimization_controls.register_callback('force_gc', self._force_gc)
        self.optimization_controls.register_callback('optimize_resources', self._optimize_resources)
        self.optimization_controls.register_callback('apply_settings', self._apply_settings)
        
        # Start monitoring
        self.start_monitoring()
        
    def hide_dashboard(self):
        """Hide the performance dashboard."""
        self.stop_monitoring()
        if self.dashboard_window:
            self.dashboard_window.destroy()
            self.dashboard_window = None
            
    def start_monitoring(self):
        """Start performance monitoring updates."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.update_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True,
                name="DashboardUpdater"
            )
            self.update_thread.start()
            
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring_active = False
        if self.update_thread:
            self.update_thread.join(timeout=2.0)
            
    def _monitoring_loop(self):
        """Main monitoring update loop."""
        while self.monitoring_active:
            try:
                # Get current metrics
                metrics = self.optimizer.get_performance_metrics()
                if metrics:
                    # Update displays
                    self._update_displays(metrics)
                    
                    # Check for alerts
                    self._check_alerts(metrics)
                    
                time.sleep(2.0)  # Update every 2 seconds
            except Exception as e:
                print(f"Error in dashboard monitoring: {e}")
                
    def _update_displays(self, metrics):
        """Update all dashboard displays."""
        if not self.dashboard_window:
            return
            
        # Update metrics display
        self.metrics_display.update_metric("memory_mb", metrics.memory_usage_mb)
        self.metrics_display.update_metric("cpu_percent", metrics.cpu_usage_percent)
        self.metrics_display.update_metric("cache_hit_ratio", metrics.cache_hit_ratio * 100)
        self.metrics_display.update_metric("images_processed", metrics.images_processed, "{}")
        self.metrics_display.update_metric("pending_tasks", metrics.pending_tasks, "{}")
        self.metrics_display.update_metric("active_threads", metrics.active_threads, "{}")
        
        # Update graphs
        self.memory_graph.add_data_point(metrics.memory_usage_mb)
        self.cpu_graph.add_data_point(metrics.cpu_usage_percent)
        
    def _check_alerts(self, metrics):
        """Check metrics against thresholds and generate alerts."""
        # Memory alerts
        if metrics.memory_usage_mb > self.memory_critical_threshold:
            self.performance_alerts.add_alert(
                "critical", 
                f"Critical memory usage: {metrics.memory_usage_mb:.1f}MB"
            )
        elif metrics.memory_usage_mb > self.memory_warning_threshold:
            self.performance_alerts.add_alert(
                "warning", 
                f"High memory usage: {metrics.memory_usage_mb:.1f}MB"
            )
            
        # CPU alerts
        if metrics.cpu_usage_percent > self.cpu_warning_threshold:
            self.performance_alerts.add_alert(
                "warning",
                f"High CPU usage: {metrics.cpu_usage_percent:.1f}%"
            )
            
        # Task queue alerts
        if metrics.pending_tasks > 20:
            self.performance_alerts.add_alert(
                "info",
                f"Many pending tasks: {metrics.pending_tasks}"
            )
            
    def _clear_cache(self):
        """Clear memory cache."""
        self.optimizer.memory_manager.clear_all_caches()
        self.performance_alerts.add_alert("info", "Memory cache cleared")
        
    def _force_gc(self):
        """Force garbage collection."""
        import gc
        collected = gc.collect()
        self.performance_alerts.add_alert("info", f"Garbage collection: {collected} objects collected")
        
    def _optimize_resources(self):
        """Optimize system resources."""
        self.optimizer.memory_manager.perform_cleanup()
        self.optimizer.resource_manager._gentle_cleanup()
        self.performance_alerts.add_alert("info", "Resource optimization performed")
        
    def _apply_settings(self, settings: Dict[str, Any]):
        """Apply optimization settings."""
        memory_limit = settings.get('memory_limit')
        if memory_limit:
            self.memory_critical_threshold = memory_limit
            self.optimizer.memory_manager.set_memory_thresholds(
                memory_limit * 0.75,  # Warning at 75%
                memory_limit
            )
            self.performance_alerts.add_alert("info", f"Memory limit set to {memory_limit}MB")