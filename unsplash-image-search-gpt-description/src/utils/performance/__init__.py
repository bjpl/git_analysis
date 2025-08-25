"""
Performance utilities for desktop application optimization.

This package provides:
- Performance monitoring
- Memory management
- Background task processing
- Image loading optimizations
- Request queuing and cancellation
"""

from .performance_monitor import PerformanceMonitor
from .memory_manager import MemoryManager
from .task_queue import TaskQueue, BackgroundTask
from .image_optimizer import ImageOptimizer, LazyImageLoader
from .debouncer import Debouncer
from .virtual_scroll import VirtualScrollManager
from .startup_optimizer import StartupOptimizer

__all__ = [
    'PerformanceMonitor',
    'MemoryManager', 
    'TaskQueue',
    'BackgroundTask',
    'ImageOptimizer',
    'LazyImageLoader',
    'Debouncer',
    'VirtualScrollManager',
    'StartupOptimizer'
]