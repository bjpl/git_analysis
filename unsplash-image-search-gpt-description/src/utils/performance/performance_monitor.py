"""
Performance monitoring utilities for tracking application performance.
"""

import time
import threading
import psutil
import tkinter as tk
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
from pathlib import Path


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    timestamp: float
    memory_usage_mb: float
    cpu_usage_percent: float
    fps: float = 0.0
    api_calls: int = 0
    response_time_ms: float = 0.0
    active_threads: int = 0
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


class FPSCounter:
    """Tracks frames per second for UI performance monitoring."""
    
    def __init__(self, window_size: int = 60):
        self.window_size = window_size
        self.frame_times = deque(maxlen=window_size)
        self.last_time = time.time()
        
    def tick(self) -> float:
        """Record a frame and return current FPS."""
        current_time = time.time()
        self.frame_times.append(current_time - self.last_time)
        self.last_time = current_time
        
        if len(self.frame_times) < 2:
            return 0.0
            
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0


class APICallTracker:
    """Tracks API call metrics."""
    
    def __init__(self):
        self.calls = defaultdict(int)
        self.response_times = defaultdict(list)
        self.errors = defaultdict(int)
        self._lock = threading.Lock()
        
    def record_call(self, endpoint: str, response_time_ms: float, success: bool = True):
        """Record an API call."""
        with self._lock:
            self.calls[endpoint] += 1
            self.response_times[endpoint].append(response_time_ms)
            if not success:
                self.errors[endpoint] += 1
                
    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get API call statistics."""
        with self._lock:
            stats = {}
            for endpoint in self.calls:
                times = self.response_times[endpoint]
                stats[endpoint] = {
                    'total_calls': self.calls[endpoint],
                    'avg_response_time': sum(times) / len(times) if times else 0,
                    'min_response_time': min(times) if times else 0,
                    'max_response_time': max(times) if times else 0,
                    'error_count': self.errors[endpoint],
                    'success_rate': ((self.calls[endpoint] - self.errors[endpoint]) / 
                                   self.calls[endpoint]) if self.calls[endpoint] > 0 else 0
                }
            return stats
            
    def reset(self):
        """Reset all statistics."""
        with self._lock:
            self.calls.clear()
            self.response_times.clear()
            self.errors.clear()


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system.
    
    Tracks:
    - Memory usage
    - CPU usage
    - FPS (UI responsiveness)
    - API call metrics
    - Custom application metrics
    """
    
    def __init__(self, log_file: Optional[Path] = None):
        self.log_file = log_file
        self.fps_counter = FPSCounter()
        self.api_tracker = APICallTracker()
        self.metrics_history: List[PerformanceMetrics] = []
        self.custom_metrics: Dict[str, Any] = {}
        
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable[[PerformanceMetrics], None]] = []
        self._lock = threading.Lock()
        
        # Get process for memory/CPU tracking
        self.process = psutil.Process()
        
    def start_monitoring(self, interval: float = 1.0):
        """Start background performance monitoring."""
        if self._monitoring:
            return
            
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop background monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
            
    def _monitor_loop(self, interval: float):
        """Background monitoring loop."""
        while self._monitoring:
            try:
                metrics = self._collect_metrics()
                with self._lock:
                    self.metrics_history.append(metrics)
                    # Keep only last 1000 entries
                    if len(self.metrics_history) > 1000:
                        self.metrics_history.pop(0)
                
                # Notify callbacks
                for callback in self._callbacks:
                    try:
                        callback(metrics)
                    except Exception as e:
                        print(f"Error in performance callback: {e}")
                        
                # Log to file if specified
                if self.log_file:
                    self._log_metrics(metrics)
                    
            except Exception as e:
                print(f"Error in performance monitoring: {e}")
                
            time.sleep(interval)
            
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics."""
        try:
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            cpu_percent = self.process.cpu_percent()
            
            active_threads = threading.active_count()
            
            return PerformanceMetrics(
                timestamp=time.time(),
                memory_usage_mb=memory_mb,
                cpu_usage_percent=cpu_percent,
                fps=self.fps_counter.tick(),
                active_threads=active_threads,
                custom_metrics=self.custom_metrics.copy()
            )
        except Exception as e:
            print(f"Error collecting metrics: {e}")
            return PerformanceMetrics(
                timestamp=time.time(),
                memory_usage_mb=0,
                cpu_usage_percent=0
            )
            
    def _log_metrics(self, metrics: PerformanceMetrics):
        """Log metrics to file."""
        try:
            log_entry = {
                'timestamp': metrics.timestamp,
                'memory_mb': metrics.memory_usage_mb,
                'cpu_percent': metrics.cpu_usage_percent,
                'fps': metrics.fps,
                'threads': metrics.active_threads,
                'custom': metrics.custom_metrics
            }
            
            # Append to log file
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            print(f"Error logging metrics: {e}")
            
    def record_api_call(self, endpoint: str, response_time_ms: float, success: bool = True):
        """Record an API call for tracking."""
        self.api_tracker.record_call(endpoint, response_time_ms, success)
        
    def set_custom_metric(self, name: str, value: Any):
        """Set a custom application metric."""
        with self._lock:
            self.custom_metrics[name] = value
            
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get the most recent performance metrics."""
        with self._lock:
            return self.metrics_history[-1] if self.metrics_history else None
            
    def get_metrics_history(self, duration_seconds: Optional[float] = None) -> List[PerformanceMetrics]:
        """Get metrics history, optionally filtered by time duration."""
        with self._lock:
            if duration_seconds is None:
                return self.metrics_history.copy()
                
            cutoff_time = time.time() - duration_seconds
            return [m for m in self.metrics_history if m.timestamp >= cutoff_time]
            
    def get_api_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get API call statistics."""
        return self.api_tracker.get_stats()
        
    def add_callback(self, callback: Callable[[PerformanceMetrics], None]):
        """Add a callback to be called when new metrics are collected."""
        self._callbacks.append(callback)
        
    def remove_callback(self, callback: Callable[[PerformanceMetrics], None]):
        """Remove a metrics callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
            
    def get_average_metrics(self, duration_seconds: float = 60.0) -> Optional[PerformanceMetrics]:
        """Get averaged metrics over a time period."""
        recent_metrics = self.get_metrics_history(duration_seconds)
        if not recent_metrics:
            return None
            
        avg_memory = sum(m.memory_usage_mb for m in recent_metrics) / len(recent_metrics)
        avg_cpu = sum(m.cpu_usage_percent for m in recent_metrics) / len(recent_metrics)
        avg_fps = sum(m.fps for m in recent_metrics) / len(recent_metrics)
        avg_threads = sum(m.active_threads for m in recent_metrics) / len(recent_metrics)
        
        return PerformanceMetrics(
            timestamp=time.time(),
            memory_usage_mb=avg_memory,
            cpu_usage_percent=avg_cpu,
            fps=avg_fps,
            active_threads=avg_threads
        )
        
    def reset_metrics(self):
        """Reset all collected metrics."""
        with self._lock:
            self.metrics_history.clear()
            self.custom_metrics.clear()
        self.api_tracker.reset()
        
    def export_metrics(self, file_path: Path, format: str = 'json'):
        """Export metrics to file."""
        with self._lock:
            data = {
                'metrics_history': [
                    {
                        'timestamp': m.timestamp,
                        'memory_mb': m.memory_usage_mb,
                        'cpu_percent': m.cpu_usage_percent,
                        'fps': m.fps,
                        'threads': m.active_threads,
                        'custom': m.custom_metrics
                    }
                    for m in self.metrics_history
                ],
                'api_stats': self.get_api_stats()
            }
            
        if format == 'json':
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")