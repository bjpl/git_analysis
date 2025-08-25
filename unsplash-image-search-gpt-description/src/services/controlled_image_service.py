"""
Controlled Image Service - Prevents infinite image collection
Implements the architecture design for safe image loading with user controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import OrderedDict
import requests
from PIL import Image, ImageTk
from io import BytesIO
import threading
import json
import logging
import uuid
from concurrent.futures import Future, TimeoutError as FutureTimeoutError


@dataclass
class ImageCollectionLimits:
    """Configuration for image collection limits."""
    max_images_per_session: int = 50
    max_pages_per_session: int = 10
    warn_threshold: int = 30
    batch_size: int = 5
    confirmation_interval: int = 20  # Confirm every N images


class SearchSession:
    """Manages the state of a search session with limits."""
    
    def __init__(self, query: str, limits: ImageCollectionLimits):
        self.query = query
        self.limits = limits
        self.images_loaded = 0
        self.pages_fetched = 0
        self.current_page = 1
        self.current_index = 0
        self.current_results = []
        self.is_stopped = False
        self.created_at = datetime.now()
        self.status = "active"
        self.used_image_urls = set()
        
    def can_load_more_images(self) -> bool:
        """Check if more images can be loaded within limits."""
        return (not self.is_stopped and 
                self.images_loaded < self.limits.max_images_per_session and
                self.pages_fetched < self.limits.max_pages_per_session)
    
    def should_warn_user(self) -> bool:
        """Check if user should be warned about approaching limits."""
        return self.images_loaded >= self.limits.warn_threshold
    
    def requires_confirmation(self) -> bool:
        """Check if user confirmation is required."""
        return (self.images_loaded > 0 and 
                self.images_loaded % self.limits.confirmation_interval == 0)
    
    def get_progress_text(self) -> str:
        """Get human-readable progress text."""
        percentage = (self.images_loaded / self.limits.max_images_per_session) * 100
        return f"{self.images_loaded}/{self.limits.max_images_per_session} images ({percentage:.0f}%)"
    
    def get_remaining_images(self) -> int:
        """Get number of images remaining in session."""
        return max(0, self.limits.max_images_per_session - self.images_loaded)


class RateLimitManager:
    """Manages API rate limiting to prevent quota exhaustion."""
    
    def __init__(self, max_calls_per_hour: int = 45):
        self.max_calls_per_hour = max_calls_per_hour
        self.api_calls_count = 0
        self.last_reset = datetime.now()
        
    def can_make_api_call(self) -> bool:
        """Check if an API call can be made within rate limits."""
        self.reset_if_needed()
        return self.api_calls_count < self.max_calls_per_hour
    
    def record_api_call(self):
        """Record an API call for rate limiting."""
        self.api_calls_count += 1
        
    def get_time_until_reset(self) -> int:
        """Get minutes until rate limit resets."""
        next_reset = self.last_reset + timedelta(hours=1)
        return max(0, int((next_reset - datetime.now()).total_seconds() / 60))
    
    def reset_if_needed(self):
        """Reset rate limit counter if hour has passed."""
        if datetime.now() - self.last_reset >= timedelta(hours=1):
            self.api_calls_count = 0
            self.last_reset = datetime.now()
    
    def get_calls_remaining(self) -> int:
        """Get number of API calls remaining."""
        self.reset_if_needed()
        return max(0, self.max_calls_per_hour - self.api_calls_count)


class IntelligentImageCache:
    """Memory-aware image cache with automatic cleanup."""
    
    def __init__(self, max_size_mb: int = 100):
        self.cache = OrderedDict()
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.current_size = 0
        
    def add_image(self, url: str, image_data: bytes):
        """Add image to cache with size management."""
        image_size = len(image_data)
        
        # Remove old images if needed
        while (self.current_size + image_size > self.max_size_bytes and self.cache):
            oldest_url = next(iter(self.cache))
            removed_data = self.cache.pop(oldest_url)
            self.current_size -= len(removed_data)
        
        self.cache[url] = image_data
        self.current_size += image_size
        
        # Move to end (most recently used)
        self.cache.move_to_end(url)
    
    def get_image(self, url: str) -> Optional[bytes]:
        """Get image from cache if available."""
        if url in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(url)
            return self.cache[url]
        return None
    
    def clear(self):
        """Clear all cached images."""
        self.cache.clear()
        self.current_size = 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cached_images": len(self.cache),
            "size_mb": round(self.current_size / (1024 * 1024), 2),
            "max_size_mb": self.max_size_bytes / (1024 * 1024)
        }


class LoadMoreConfirmationDialog:
    """Dialog for confirming continued image loading."""
    
    def __init__(self, parent, session: SearchSession):
        self.session = session
        self.result = False
        self.dialog = None
        self.create_dialog(parent)
        
    def create_dialog(self, parent):
        """Create the confirmation dialog."""
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Continue Loading Images?")
        self.dialog.geometry("450x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 225
        y = (self.dialog.winfo_screenheight() // 2) - 150
        self.dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Continue Loading Images?",
            font=('TkDefaultFont', 12, 'bold')
        )
        title_label.pack(pady=(0, 15))
        
        # Progress info
        progress_text = f"""
Current Progress: {self.session.get_progress_text()}
Images loaded so far: {self.session.images_loaded}
Maximum allowed: {self.session.limits.max_images_per_session}
Remaining: {self.session.get_remaining_images()}

Query: "{self.session.query}"
        """.strip()
        
        info_label = ttk.Label(main_frame, text=progress_text, justify=tk.LEFT)
        info_label.pack(pady=(0, 15))
        
        # Warning if approaching limit
        if self.session.should_warn_user():
            warning_frame = ttk.Frame(main_frame)
            warning_frame.pack(fill=tk.X, pady=(0, 15))
            
            warning_label = ttk.Label(
                warning_frame,
                text="⚠️ Approaching maximum limit! Consider stopping soon.",
                foreground="orange",
                font=('TkDefaultFont', 9, 'italic')
            )
            warning_label.pack()
        
        # Additional info
        info_text = """
Loading more images will:
• Use additional API quota
• Take more time
• Use more memory

You can stop at any time and export your vocabulary.
        """.strip()
        
        ttk.Label(main_frame, text=info_text, justify=tk.LEFT, foreground="gray").pack(pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Continue button
        continue_btn = ttk.Button(
            button_frame,
            text=f"Continue Loading (Load {min(self.session.limits.batch_size, self.session.get_remaining_images())} more)",
            command=self.continue_loading
        )
        continue_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        stop_btn = ttk.Button(
            button_frame,
            text="Stop Here",
            command=self.stop_loading
        )
        stop_btn.pack(side=tk.LEFT)
        
        # Settings button
        settings_btn = ttk.Button(
            button_frame,
            text="⚙️ Adjust Limits",
            command=self.show_settings
        )
        settings_btn.pack(side=tk.RIGHT)
        
        # Bind escape key
        self.dialog.bind('<Escape>', lambda e: self.stop_loading())
        
        # Set focus to continue button
        continue_btn.focus_set()
    
    def continue_loading(self):
        """User chose to continue loading."""
        self.result = True
        self.dialog.destroy()
    
    def stop_loading(self):
        """User chose to stop loading."""
        self.result = False
        self.dialog.destroy()
    
    def show_settings(self):
        """Show settings dialog (placeholder)."""
        messagebox.showinfo(
            "Settings",
            "Limit settings can be adjusted in the main Settings menu.",
            parent=self.dialog
        )
    
    def show_modal(self) -> bool:
        """Show dialog and return result."""
        self.dialog.wait_window()
        return self.result


class ControlledImageService:
    """Service for controlled image loading with user consent and limits."""
    
    def __init__(self, unsplash_access_key: str, app_callback):
        self.unsplash_access_key = unsplash_access_key
        self.app_callback = app_callback
        
        # Initialize managers
        self.rate_limit_manager = RateLimitManager()
        self.image_cache = IntelligentImageCache()
        
        # Current session
        self.current_session: Optional[SearchSession] = None
        
        # Default limits
        self.default_limits = ImageCollectionLimits()
        
        # Cancellation support
        self._current_request_id: Optional[str] = None
        self._is_cancelled = False
        self._current_operation: Optional[str] = None
        self._progress_callback: Optional[Callable[[str], None]] = None
        
        # Logging
        self.logger = logging.getLogger(f"{__name__}.ControlledImageService")
        
        # Timeouts
        self.operation_timeout = 60  # Overall operation timeout
        self.single_request_timeout = 30  # Single request timeout
    
    def start_new_search(self, query: str, limits: Optional[ImageCollectionLimits] = None) -> bool:
        """Start a new search session with specified limits."""
        if limits is None:
            limits = self.default_limits
        
        self.current_session = SearchSession(query, limits)
        
        # Clear cache for new search
        self.image_cache.clear()
        
        return True
    
    def can_load_more_images(self) -> bool:
        """Check if more images can be loaded."""
        if not self.current_session:
            return False
        
        # Check session limits
        if not self.current_session.can_load_more_images():
            return False
        
        # Check rate limits
        if not self.rate_limit_manager.can_make_api_call():
            return False
        
        return True
    
    def get_next_image_controlled(self, progress_callback: Optional[Callable[[str], None]] = None) -> Optional[Tuple[ImageTk.PhotoImage, Image.Image, str]]:
        """
        Get next image with full control and limit checking.
        Returns (PhotoImage, PIL_Image, URL) or None if limit reached/stopped.
        """
        if not self.current_session:
            raise ValueError("No active search session")
        
        # Setup operation tracking
        self._current_request_id = str(uuid.uuid4())
        self._is_cancelled = False
        self._current_operation = "loading_image"
        self._progress_callback = progress_callback
        
        try:
            # Check if we can load more images
            if not self.can_load_more_images():
                return self.handle_limit_reached()
            
            # Check if user confirmation is required
            if self.current_session.requires_confirmation():
                if progress_callback:
                    progress_callback("Waiting for user confirmation...")
                if not self.get_user_confirmation():
                    self.current_session.is_stopped = True
                    return None
            
            # Proceed with loading
            if progress_callback:
                progress_callback("Loading next image...")
            return self.load_single_image_with_timeout()
            
        except CancellationError:
            self.logger.info("Image loading was cancelled by user")
            return None
        except Exception as e:
            self.handle_loading_error(e)
            return None
        finally:
            self._cleanup_operation()
    
    def load_single_image_with_timeout(self) -> Optional[Tuple[ImageTk.PhotoImage, Image.Image, str]]:
        """Load a single image with timeout and cancellation support."""
        start_time = time.time()
        
        while True:
            # Check timeout
            if time.time() - start_time > self.operation_timeout:
                raise TimeoutError(f"Image loading timeout after {self.operation_timeout}s")
            
            # Check cancellation
            if self._is_cancelled:
                raise CancellationError("Operation was cancelled")
            
            # Check if we need more results
            if self.current_session.current_index >= len(self.current_session.current_results):
                if self._progress_callback:
                    self._progress_callback("Fetching more search results...")
                if not self.fetch_next_page_with_timeout():
                    return None
            
            # Get next candidate
            candidate = self.current_session.current_results[self.current_session.current_index]
            self.current_session.current_index += 1
            
            candidate_url = candidate["urls"]["regular"]
            canonical_url = self.canonicalize_url(candidate_url)
            
            # Skip if already used
            if canonical_url in self.current_session.used_image_urls:
                continue
            
            # Try to load image
            try:
                if self._progress_callback:
                    self._progress_callback(f"Downloading image...")
                
                image_data = self.download_image_with_timeout(candidate_url)
                if image_data:
                    if self._progress_callback:
                        self._progress_callback("Processing image...")
                    
                    # Process image
                    pil_image = Image.open(BytesIO(image_data))
                    photo_image = ImageTk.PhotoImage(pil_image)
                    
                    # Record usage
                    self.current_session.used_image_urls.add(canonical_url)
                    self.current_session.images_loaded += 1
                    
                    # Cache image
                    self.image_cache.add_image(canonical_url, image_data)
                    
                    if self._progress_callback:
                        self._progress_callback("Image loaded successfully")
                    
                    return photo_image, pil_image, candidate_url
                    
            except CancellationError:
                raise
            except Exception as e:
                self.logger.warning(f"Error loading image {candidate_url}: {e}")
                continue
    
    def fetch_next_page_with_timeout(self) -> bool:
        """Fetch next page of search results with timeout and cancellation."""
        if not self.can_load_more_images():
            return False
        
        if self._is_cancelled:
            raise CancellationError("Operation was cancelled")
        
        try:
            headers = {"Authorization": f"Client-ID {self.unsplash_access_key}"}
            url = f"https://api.unsplash.com/search/photos?query={self.current_session.query}&page={self.current_session.current_page}&per_page=10"
            
            # Record API call
            self.rate_limit_manager.record_api_call()
            
            if self._progress_callback:
                self._progress_callback(f"Fetching page {self.current_session.current_page}...")
            
            response = requests.get(url, headers=headers, timeout=self.single_request_timeout)
            response.raise_for_status()
            
            data = response.json()
            new_results = data.get("results", [])
            
            if not new_results:
                return False
            
            self.current_session.current_results = new_results
            self.current_session.current_index = 0
            self.current_session.current_page += 1
            self.current_session.pages_fetched += 1
            
            self.logger.info(f"Fetched page {self.current_session.current_page - 1} with {len(new_results)} results")
            return True
            
        except Exception as e:
            self.logger.error(f"Error fetching page: {e}")
            return False
    
    def download_image_with_timeout(self, url: str) -> Optional[bytes]:
        """Download image with caching and timeout."""
        canonical_url = self.canonicalize_url(url)
        
        # Check cache first
        cached_data = self.image_cache.get_image(canonical_url)
        if cached_data:
            if self._progress_callback:
                self._progress_callback("Using cached image")
            return cached_data
        
        if self._is_cancelled:
            raise CancellationError("Operation was cancelled")
        
        # Download image
        try:
            response = requests.get(
                url, 
                timeout=self.single_request_timeout,
                stream=True
            )
            response.raise_for_status()
            
            # Download with progress tracking
            content_length = response.headers.get('content-length')
            if content_length and self._progress_callback:
                total_size = int(content_length)
                downloaded = 0
                chunks = []
                
                for chunk in response.iter_content(chunk_size=8192):
                    if self._is_cancelled:
                        raise CancellationError("Download was cancelled")
                    
                    chunks.append(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = int((downloaded / total_size) * 100)
                        self._progress_callback(f"Downloading... {progress}%")
                
                return b''.join(chunks)
            else:
                return response.content
                
        except CancellationError:
            raise
        except Exception as e:
            self.logger.error(f"Error downloading image: {e}")
            return None
    
    def get_user_confirmation(self) -> bool:
        """Get user confirmation to continue loading images."""
        if self.app_callback and hasattr(self.app_callback, 'get_parent_window'):
            parent = self.app_callback.get_parent_window()
        else:
            parent = None
        
        dialog = LoadMoreConfirmationDialog(parent, self.current_session)
        return dialog.show_modal()
    
    def handle_limit_reached(self) -> None:
        """Handle case where limits are reached."""
        if not self.current_session:
            return None
        
        if self.current_session.images_loaded >= self.current_session.limits.max_images_per_session:
            self.show_limit_reached_dialog("Maximum Images Reached", 
                f"You've reached the maximum of {self.current_session.limits.max_images_per_session} images per session.")
        elif not self.rate_limit_manager.can_make_api_call():
            time_until_reset = self.rate_limit_manager.get_time_until_reset()
            self.show_rate_limit_dialog(time_until_reset)
        
        return None
    
    def handle_loading_error(self, error: Exception):
        """Handle image loading errors gracefully."""
        error_msg = str(error)
        
        if "403" in error_msg:
            messagebox.showerror(
                "API Error", 
                "Unsplash API key may be invalid. Please check your configuration."
            )
        elif "rate" in error_msg.lower() or "429" in error_msg:
            time_until_reset = self.rate_limit_manager.get_time_until_reset()
            self.show_rate_limit_dialog(time_until_reset)
        else:
            messagebox.showerror("Loading Error", f"Error loading image: {error}")
    
    def show_limit_reached_dialog(self, title: str, message: str):
        """Show dialog when limits are reached."""
        full_message = f"{message}\n\n" + \
                      f"Session Statistics:\n" + \
                      f"• Images loaded: {self.current_session.images_loaded}\n" + \
                      f"• Pages fetched: {self.current_session.pages_fetched}\n" + \
                      f"• Search query: '{self.current_session.query}'\n\n" + \
                      "You can:\n" + \
                      "• Export your vocabulary\n" + \
                      "• Start a new search\n" + \
                      "• Adjust limits in settings"
        
        messagebox.showinfo(title, full_message)
    
    def show_rate_limit_dialog(self, time_until_reset: int):
        """Show dialog when rate limit is reached."""
        message = f"Rate limit reached!\n\n" + \
                 f"API calls made: {self.rate_limit_manager.api_calls_count}\n" + \
                 f"Time until reset: {time_until_reset} minutes\n\n" + \
                 "You can:\n" + \
                 "• Wait for the limit to reset\n" + \
                 "• Continue with already loaded images\n" + \
                 "• Export your current vocabulary"
        
        messagebox.showwarning("Rate Limit Reached", message)
    
    def stop_current_search(self):
        """Stop the current search session."""
        if self.current_session:
            self.current_session.is_stopped = True
            self.current_session.status = "stopped"
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics."""
        if not self.current_session:
            return {"status": "no_session"}
        
        cache_stats = self.image_cache.get_cache_stats()
        rate_stats = {
            "api_calls_made": self.rate_limit_manager.api_calls_count,
            "api_calls_remaining": self.rate_limit_manager.get_calls_remaining(),
            "time_until_reset": self.rate_limit_manager.get_time_until_reset()
        }
        
        return {
            "status": self.current_session.status,
            "query": self.current_session.query,
            "progress": self.current_session.get_progress_text(),
            "images_loaded": self.current_session.images_loaded,
            "pages_fetched": self.current_session.pages_fetched,
            "can_load_more": self.can_load_more_images(),
            "cache_stats": cache_stats,
            "rate_limit_stats": rate_stats
        }
    
    def cancel_current_operation(self) -> bool:
        """Cancel the current image loading operation."""
        if self._current_operation:
            self._is_cancelled = True
            self.logger.info(f"Cancelling operation: {self._current_operation}")
            return True
        return False
    
    def is_operation_active(self) -> bool:
        """Check if an operation is currently active."""
        return self._current_operation is not None and not self._is_cancelled
    
    def _cleanup_operation(self):
        """Clean up operation tracking."""
        self._current_request_id = None
        self._current_operation = None
        self._is_cancelled = False
        self._progress_callback = None
    
    @staticmethod
    def canonicalize_url(url: str) -> str:
        """Get canonical URL without query parameters."""
        return url.split('?')[0] if url else ""


class CancellationError(Exception):
    """Raised when an operation is cancelled."""
    pass


class TimeoutError(Exception):
    """Raised when an operation times out."""
    pass