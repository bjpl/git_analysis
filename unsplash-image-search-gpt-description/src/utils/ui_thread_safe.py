"""
UI Thread Safety Utilities

Provides decorators and mixins to ensure proper thread safety when updating
Tkinter UI components from background threads or async operations.
"""

import tkinter as tk
from tkinter import messagebox
import threading
import functools
import logging
from typing import Callable, Any, Optional


logger = logging.getLogger(__name__)


def is_main_thread() -> bool:
    """Check if current thread is the main thread."""
    return threading.current_thread() is threading.main_thread()


def ui_thread_safe(func: Callable) -> Callable:
    """
    Decorator to ensure function runs in UI thread.
    
    If called from a background thread, schedules the function to run
    in the UI thread using Tkinter's after() method.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if is_main_thread():
            # Already in UI thread, execute directly
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                logger.error(f"UI thread error in {func.__name__}: {e}")
                raise
        else:
            # Schedule in UI thread
            if hasattr(self, 'after'):
                try:
                    self.after(0, lambda: func(self, *args, **kwargs))
                except Exception as e:
                    logger.error(f"Failed to schedule UI update: {e}")
            else:
                logger.warning(f"Object {self} has no 'after' method for UI thread scheduling")
    
    return wrapper


def ui_safe_callback(widget: tk.Widget) -> Callable:
    """
    Create a thread-safe callback that uses the widget's after() method.
    
    Args:
        widget: Tkinter widget to use for scheduling
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if is_main_thread():
                return func(*args, **kwargs)
            else:
                widget.after(0, lambda: func(*args, **kwargs))
        
        return wrapper
    return decorator


class ThreadSafeUI:
    """
    Mixin class providing thread-safe UI update methods.
    
    Classes inheriting from this mixin get access to thread-safe versions
    of common UI operations.
    """
    
    @ui_thread_safe
    def update_status_safe(self, message: str) -> None:
        """Thread-safe status update."""
        if hasattr(self, 'status_label') and self.status_label:
            try:
                self.status_label.config(text=str(message))
                self.update_idletasks()
            except tk.TclError as e:
                logger.warning(f"Status update failed: {e}")
    
    @ui_thread_safe
    def show_error_safe(self, title: str, message: str) -> None:
        """Thread-safe error dialog."""
        try:
            messagebox.showerror(title, message, parent=self if hasattr(self, 'winfo_exists') else None)
        except Exception as e:
            logger.error(f"Error dialog failed: {e}")
    
    @ui_thread_safe
    def show_warning_safe(self, title: str, message: str) -> None:
        """Thread-safe warning dialog."""
        try:
            messagebox.showwarning(title, message, parent=self if hasattr(self, 'winfo_exists') else None)
        except Exception as e:
            logger.error(f"Warning dialog failed: {e}")
    
    @ui_thread_safe
    def show_info_safe(self, title: str, message: str) -> None:
        """Thread-safe info dialog."""
        try:
            messagebox.showinfo(title, message, parent=self if hasattr(self, 'winfo_exists') else None)
        except Exception as e:
            logger.error(f"Info dialog failed: {e}")
    
    @ui_thread_safe
    def update_progress_safe(self, value: int, message: str = "") -> None:
        """Thread-safe progress update."""
        try:
            if hasattr(self, 'progress_bar') and self.progress_bar:
                if hasattr(self.progress_bar, 'set'):
                    self.progress_bar.set(value)
                elif hasattr(self.progress_bar, 'configure'):
                    self.progress_bar.configure(value=value)
                    
            if message and hasattr(self, 'status_label') and self.status_label:
                self.status_label.config(text=str(message))
                
            self.update_idletasks()
        except tk.TclError as e:
            logger.warning(f"Progress update failed: {e}")
    
    @ui_thread_safe
    def show_progress_safe(self, message: str = "Loading...") -> None:
        """Thread-safe progress display."""
        try:
            if hasattr(self, 'progress_bar') and self.progress_bar:
                # Show progress bar
                if hasattr(self.progress_bar, 'grid'):
                    self.progress_bar.grid()
                elif hasattr(self.progress_bar, 'pack'):
                    self.progress_bar.pack()
                
                # Start indeterminate progress if supported
                if hasattr(self.progress_bar, 'start'):
                    self.progress_bar.start(10)
            
            self.update_status_safe(message)
        except Exception as e:
            logger.error(f"Show progress failed: {e}")
    
    @ui_thread_safe
    def hide_progress_safe(self) -> None:
        """Thread-safe progress hide."""
        try:
            if hasattr(self, 'progress_bar') and self.progress_bar:
                # Stop progress animation
                if hasattr(self.progress_bar, 'stop'):
                    self.progress_bar.stop()
                
                # Hide progress bar
                if hasattr(self.progress_bar, 'grid_remove'):
                    self.progress_bar.grid_remove()
                elif hasattr(self.progress_bar, 'pack_forget'):
                    self.progress_bar.pack_forget()
        except Exception as e:
            logger.error(f"Hide progress failed: {e}")
    
    @ui_thread_safe
    def disable_buttons_safe(self) -> None:
        """Thread-safe button disabling."""
        button_attrs = [
            'search_button', 'another_button', 'newsearch_button', 
            'generate_desc_button', 'export_button', 'theme_button'
        ]
        
        for attr in button_attrs:
            if hasattr(self, attr):
                button = getattr(self, attr)
                if button and hasattr(button, 'config'):
                    try:
                        button.config(state=tk.DISABLED)
                    except tk.TclError as e:
                        logger.warning(f"Failed to disable {attr}: {e}")
    
    @ui_thread_safe
    def enable_buttons_safe(self) -> None:
        """Thread-safe button enabling."""
        button_attrs = [
            'search_button', 'another_button', 'newsearch_button', 
            'generate_desc_button', 'export_button', 'theme_button'
        ]
        
        for attr in button_attrs:
            if hasattr(self, attr):
                button = getattr(self, attr)
                if button and hasattr(button, 'config'):
                    try:
                        button.config(state=tk.NORMAL)
                    except tk.TclError as e:
                        logger.warning(f"Failed to enable {attr}: {e}")
    
    @ui_thread_safe
    def update_text_widget_safe(self, widget, text: str, clear_first: bool = True) -> None:
        """Thread-safe text widget update."""
        if not widget:
            return
        
        try:
            # Enable editing if disabled
            original_state = str(widget.cget('state'))
            if original_state == tk.DISABLED:
                widget.config(state=tk.NORMAL)
            
            # Clear and insert text
            if clear_first:
                widget.delete("1.0", tk.END)
            widget.insert(tk.END, str(text))
            
            # Restore original state
            if original_state == tk.DISABLED:
                widget.config(state=tk.DISABLED)
                
            self.update_idletasks()
        except tk.TclError as e:
            logger.warning(f"Text widget update failed: {e}")
    
    @ui_thread_safe
    def clear_text_widget_safe(self, widget) -> None:
        """Thread-safe text widget clearing."""
        if not widget:
            return
        
        try:
            original_state = str(widget.cget('state'))
            if original_state == tk.DISABLED:
                widget.config(state=tk.NORMAL)
            
            widget.delete("1.0", tk.END)
            
            if original_state == tk.DISABLED:
                widget.config(state=tk.DISABLED)
                
        except tk.TclError as e:
            logger.warning(f"Text widget clear failed: {e}")
    
    @ui_thread_safe
    def update_listbox_safe(self, listbox, items: list, clear_first: bool = True) -> None:
        """Thread-safe listbox update."""
        if not listbox:
            return
        
        try:
            if clear_first:
                listbox.delete(0, tk.END)
            
            for item in items:
                listbox.insert(tk.END, str(item))
                
            self.update_idletasks()
        except tk.TclError as e:
            logger.warning(f"Listbox update failed: {e}")
    
    @ui_thread_safe
    def safe_after(self, delay: int, callback: Callable) -> None:
        """Thread-safe after() call."""
        if hasattr(self, 'after'):
            try:
                self.after(delay, callback)
            except Exception as e:
                logger.error(f"Safe after failed: {e}")


class AsyncUIUpdater:
    """
    Helper class for coordinating UI updates from async operations.
    
    Provides methods to safely update UI from async callbacks.
    """
    
    def __init__(self, root_widget: tk.Widget):
        self.root = root_widget
        self._update_queue = []
        self._processing = False
    
    def schedule_update(self, callback: Callable, *args, **kwargs) -> None:
        """
        Schedule a UI update to run in the main thread.
        
        Args:
            callback: Function to call in UI thread
            *args: Arguments for callback
            **kwargs: Keyword arguments for callback
        """
        update_item = (callback, args, kwargs)
        self._update_queue.append(update_item)
        
        if not self._processing:
            self.root.after(0, self._process_queue)
    
    def _process_queue(self) -> None:
        """Process all queued UI updates."""
        self._processing = True
        
        try:
            while self._update_queue:
                callback, args, kwargs = self._update_queue.pop(0)
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"UI update error: {e}")
        finally:
            self._processing = False
    
    def clear_queue(self) -> None:
        """Clear all pending UI updates."""
        self._update_queue.clear()


def create_thread_safe_callback(widget: tk.Widget, func: Callable) -> Callable:
    """
    Create a thread-safe callback function.
    
    Args:
        widget: Widget to use for thread scheduling
        func: Function to make thread-safe
        
    Returns:
        Thread-safe wrapper function
    """
    def thread_safe_wrapper(*args, **kwargs):
        if is_main_thread():
            return func(*args, **kwargs)
        else:
            widget.after(0, lambda: func(*args, **kwargs))
    
    return thread_safe_wrapper


# Context manager for thread-safe UI operations
class UIThreadContext:
    """Context manager to ensure operations run in UI thread."""
    
    def __init__(self, widget: tk.Widget):
        self.widget = widget
        self.in_ui_thread = is_main_thread()
    
    def __enter__(self):
        if not self.in_ui_thread:
            # We're in a background thread, need to schedule in UI thread
            raise RuntimeError("Use schedule_in_ui_thread() for background thread operations")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def schedule_in_ui_thread(self, callback: Callable) -> None:
        """Schedule callback to run in UI thread."""
        self.widget.after(0, callback)