"""
Startup optimization utilities for faster application launch.
"""

import threading
import time
import importlib
import sys
from typing import Dict, List, Callable, Optional, Any
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import json


class LazyImporter:
    """
    Lazy module importer that defers expensive imports until needed.
    """
    
    def __init__(self):
        self.modules: Dict[str, Any] = {}
        self.import_times: Dict[str, float] = {}
        self.deferred_imports: Dict[str, Callable] = {}
        
    def defer_import(self, module_name: str, import_func: Callable):
        """
        Defer import of a module until it's actually needed.
        
        Args:
            module_name: Name of the module
            import_func: Function that performs the import
        """
        self.deferred_imports[module_name] = import_func
        
    def get_module(self, module_name: str):
        """Get module, importing it if needed."""
        if module_name not in self.modules:
            if module_name in self.deferred_imports:
                start_time = time.time()
                self.modules[module_name] = self.deferred_imports[module_name]()
                import_time = time.time() - start_time
                self.import_times[module_name] = import_time
                print(f"Lazy imported {module_name} in {import_time:.3f}s")
            else:
                raise ImportError(f"Module {module_name} not registered for lazy import")
                
        return self.modules[module_name]
        
    def preload_modules(self, module_names: List[str]):
        """Preload specified modules in background."""
        def preload():
            for module_name in module_names:
                try:
                    self.get_module(module_name)
                except Exception as e:
                    print(f"Failed to preload {module_name}: {e}")
                    
        threading.Thread(target=preload, daemon=True).start()
        
    def get_import_stats(self) -> Dict[str, float]:
        """Get import time statistics."""
        return self.import_times.copy()


class SplashScreen:
    """
    Splash screen with progress reporting during startup.
    """
    
    def __init__(self, title: str = "Loading...", size: tuple = (400, 300)):
        self.title = title
        self.size = size
        self.window: Optional[tk.Toplevel] = None
        self.progress_var: Optional[tk.DoubleVar] = None
        self.status_var: Optional[tk.StringVar] = None
        self.progress_bar: Optional[ttk.Progressbar] = None
        self.status_label: Optional[tk.Label] = None
        self._is_visible = False
        
    def show(self):
        """Show the splash screen."""
        if self._is_visible:
            return
            
        # Create splash window
        self.window = tk.Toplevel()
        self.window.title(self.title)
        self.window.geometry(f"{self.size[0]}x{self.size[1]}")
        self.window.resizable(False, False)
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.size[0] // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.size[1] // 2)
        self.window.geometry(f"+{x}+{y}")
        
        # Remove window decorations for splash screen effect
        self.window.overrideredirect(True)
        
        # Create main frame
        main_frame = tk.Frame(
            self.window, 
            bg='white',
            relief=tk.RAISED,
            borderwidth=2
        )
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text=self.title,
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#333333'
        )
        title_label.pack(pady=20)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=300
        )
        self.progress_bar.pack(pady=20)
        
        # Status label
        self.status_var = tk.StringVar(value="Initializing...")\n        self.status_label = tk.Label(
            main_frame,
            textvariable=self.status_var,
            bg='white',
            fg='#666666',
            font=('Arial', 10)
        )
        self.status_label.pack(pady=10)
        
        # Version/Copyright info
        info_label = tk.Label(
            main_frame,
            text="© 2024 Unsplash Image Search Tool",
            bg='white',
            fg='#999999',
            font=('Arial', 8)
        )
        info_label.pack(side=tk.BOTTOM, pady=10)
        
        self._is_visible = True
        self.window.update()
        
    def update_progress(self, progress: float, status: str = ""):
        """Update progress and status."""
        if not self._is_visible or not self.window:
            return
            
        try:
            if self.progress_var:
                self.progress_var.set(progress)
            if self.status_var and status:
                self.status_var.set(status)
            self.window.update()
        except tk.TclError:
            # Window may have been destroyed
            pass
            
    def hide(self):
        """Hide the splash screen."""
        if self.window:
            self.window.destroy()
            self.window = None
        self._is_visible = False


class StartupTask:
    """Represents a startup task with progress reporting."""
    
    def __init__(self, name: str, task_func: Callable, weight: float = 1.0):
        self.name = name
        self.task_func = task_func
        self.weight = weight
        self.completed = False
        self.error: Optional[Exception] = None
        
    def execute(self) -> bool:
        """Execute the startup task."""
        try:
            self.task_func()
            self.completed = True
            return True
        except Exception as e:
            self.error = e
            return False


class StartupOptimizer:
    """
    Comprehensive startup optimization system.
    
    Features:
    - Lazy module importing
    - Background initialization
    - Splash screen with progress
    - Startup time profiling
    - Critical vs non-critical task separation
    """
    
    def __init__(self, app_name: str = "Application"):
        self.app_name = app_name
        self.lazy_importer = LazyImporter()
        self.splash_screen = SplashScreen(f"Loading {app_name}...")
        
        # Task lists
        self.critical_tasks: List[StartupTask] = []
        self.background_tasks: List[StartupTask] = []
        
        # Timing
        self.startup_start_time = 0.0
        self.critical_tasks_time = 0.0
        self.total_startup_time = 0.0
        
        # Progress tracking
        self.total_weight = 0.0
        self.completed_weight = 0.0
        
    def add_critical_task(self, name: str, task_func: Callable, weight: float = 1.0):
        """Add a critical startup task that must complete before showing UI."""
        task = StartupTask(name, task_func, weight)
        self.critical_tasks.append(task)
        self.total_weight += weight
        
    def add_background_task(self, name: str, task_func: Callable, weight: float = 1.0):
        """Add a background task that can run after UI is shown."""
        task = StartupTask(name, task_func, weight)
        self.background_tasks.append(task)
        
    def register_lazy_import(self, module_name: str, import_func: Callable):
        """Register a module for lazy importing."""
        self.lazy_importer.defer_import(module_name, import_func)
        
    def start_optimized_startup(
        self,
        show_splash: bool = True,
        main_window_factory: Optional[Callable] = None
    ):
        """
        Start optimized application startup process.
        
        Args:
            show_splash: Whether to show splash screen
            main_window_factory: Function to create main application window
        """
        self.startup_start_time = time.time()
        
        if show_splash:
            self.splash_screen.show()
            
        try:
            # Execute critical tasks
            self._execute_critical_tasks()
            
            # Create main window if factory provided
            main_window = None
            if main_window_factory:
                if show_splash:
                    self.splash_screen.update_progress(90, "Creating main window...")
                main_window = main_window_factory()
                
            # Hide splash screen
            if show_splash:
                self.splash_screen.update_progress(100, "Startup complete!")
                time.sleep(0.5)  # Brief pause to show completion
                self.splash_screen.hide()
                
            # Record critical tasks completion time
            self.critical_tasks_time = time.time() - self.startup_start_time
            
            # Start background tasks
            self._start_background_tasks()
            
            return main_window
            
        except Exception as e:
            if show_splash:
                self.splash_screen.hide()
            raise e
            
    def _execute_critical_tasks(self):
        """Execute all critical startup tasks."""
        for i, task in enumerate(self.critical_tasks):
            progress = (self.completed_weight / self.total_weight) * 80  # Up to 80%
            self.splash_screen.update_progress(progress, f"Loading {task.name}...")
            
            start_time = time.time()
            success = task.execute()
            execution_time = time.time() - start_time
            
            if success:
                self.completed_weight += task.weight
                print(f"✓ {task.name} completed in {execution_time:.3f}s")
            else:
                print(f"✗ {task.name} failed: {task.error}")
                # Decide whether to continue or abort based on task criticality
                # For now, we continue but log the error
                
    def _start_background_tasks(self):
        """Start background tasks in separate thread."""
        def run_background_tasks():
            print("Starting background initialization...")
            for task in self.background_tasks:
                start_time = time.time()
                success = task.execute()
                execution_time = time.time() - start_time
                
                if success:
                    print(f"✓ Background: {task.name} completed in {execution_time:.3f}s")
                else:
                    print(f"✗ Background: {task.name} failed: {task.error}")
                    
            self.total_startup_time = time.time() - self.startup_start_time
            print(f"Total startup time: {self.total_startup_time:.3f}s")
            print(f"Critical tasks time: {self.critical_tasks_time:.3f}s")
            print(f"Background tasks time: {self.total_startup_time - self.critical_tasks_time:.3f}s")
            
        threading.Thread(target=run_background_tasks, daemon=True).start()
        
    def get_lazy_module(self, module_name: str):
        """Get a lazily imported module."""
        return self.lazy_importer.get_module(module_name)
        
    def preload_modules(self, module_names: List[str]):
        """Preload specified modules in background."""
        self.lazy_importer.preload_modules(module_names)
        
    def get_startup_stats(self) -> Dict[str, Any]:
        """Get startup performance statistics."""
        return {
            'total_startup_time': self.total_startup_time,
            'critical_tasks_time': self.critical_tasks_time,
            'background_tasks_time': self.total_startup_time - self.critical_tasks_time,
            'critical_tasks_count': len(self.critical_tasks),
            'background_tasks_count': len(self.background_tasks),
            'failed_critical_tasks': [
                task.name for task in self.critical_tasks if task.error
            ],
            'failed_background_tasks': [
                task.name for task in self.background_tasks if task.error
            ],
            'import_times': self.lazy_importer.get_import_stats()
        }
        
    def save_startup_profile(self, file_path: Path):
        """Save startup performance profile for analysis."""
        stats = self.get_startup_stats()
        
        # Add detailed task information
        stats['critical_task_details'] = [
            {
                'name': task.name,
                'weight': task.weight,
                'completed': task.completed,
                'error': str(task.error) if task.error else None
            }
            for task in self.critical_tasks
        ]
        
        stats['background_task_details'] = [
            {
                'name': task.name,
                'weight': task.weight,
                'completed': task.completed,
                'error': str(task.error) if task.error else None
            }
            for task in self.background_tasks
        ]
        
        with open(file_path, 'w') as f:
            json.dump(stats, f, indent=2)
            

# Utility functions for common startup optimizations

def create_lazy_pil_import():
    """Create lazy import function for PIL (expensive import)."""
    def import_pil():
        from PIL import Image, ImageTk
        return {'Image': Image, 'ImageTk': ImageTk}
    return import_pil


def create_lazy_requests_import():
    """Create lazy import function for requests."""
    def import_requests():
        import requests
        return requests
    return import_requests


def create_lazy_openai_import():
    """Create lazy import function for OpenAI."""
    def import_openai():
        from openai import OpenAI
        return OpenAI
    return import_openai


def optimize_tkinter_startup():
    """Optimize Tkinter startup by deferring expensive operations."""
    # Defer ttk style configuration
    def defer_ttk_styles():
        # This would contain expensive ttk style setup
        pass
        
    # Defer font loading
    def defer_font_loading():
        # This would contain font loading operations
        pass
        
    return [defer_ttk_styles, defer_font_loading]


# Example usage for the image search application
def create_image_search_startup_optimizer():
    """Create startup optimizer specifically for the image search application."""
    optimizer = StartupOptimizer("Unsplash Image Search")
    
    # Register lazy imports
    optimizer.register_lazy_import('PIL', create_lazy_pil_import())
    optimizer.register_lazy_import('requests', create_lazy_requests_import())
    optimizer.register_lazy_import('openai', create_lazy_openai_import())
    
    # Add critical tasks
    optimizer.add_critical_task(
        "Load Configuration",
        lambda: print("Loading configuration..."),
        weight=1.0
    )
    
    optimizer.add_critical_task(
        "Initialize Theme Manager",
        lambda: print("Initializing theme manager..."),
        weight=1.0
    )
    
    optimizer.add_critical_task(
        "Setup Performance Monitoring",
        lambda: print("Setting up performance monitoring..."),
        weight=0.5
    )
    
    # Add background tasks
    optimizer.add_background_task(
        "Load Vocabulary Cache",
        lambda: print("Loading vocabulary cache..."),
        weight=1.0
    )
    
    optimizer.add_background_task(
        "Preload Common Images",
        lambda: print("Preloading common images..."),
        weight=1.0
    )
    
    optimizer.add_background_task(
        "Initialize API Services",
        lambda: print("Initializing API services..."),
        weight=1.0
    )
    
    return optimizer