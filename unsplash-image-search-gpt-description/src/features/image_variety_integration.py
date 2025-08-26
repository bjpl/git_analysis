"""
Integration module for adding image variety features to the main application.
Provides enhanced search capabilities with session-aware image rotation.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO
import threading
import random
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .enhanced_session_tracker import EnhancedSessionTracker, get_image_search_parameters


class ImageVarietyManager:
    """Manages image variety and search enhancement for the main application."""
    
    def __init__(self, main_app, data_dir: Path = None):
        self.main_app = main_app
        self.data_dir = data_dir or Path('./data/sessions')
        self.session_tracker = EnhancedSessionTracker(self.data_dir)
        
        # Add new UI elements
        self._enhance_ui()
        
        # Replace original search methods
        self._wrap_search_methods()
    
    def _enhance_ui(self):
        """Add new UI controls for image variety features."""
        # Create a new frame for variety controls
        variety_frame = ttk.Frame(self.main_app.main_frame)
        variety_frame.pack(fill='x', padx=5, pady=2)
        
        # Shuffle button
        self.shuffle_button = ttk.Button(
            variety_frame, 
            text="🔀 Shuffle Images", 
            command=self._shuffle_images,
            state="disabled"
        )
        self.shuffle_button.pack(side='left', padx=2)
        
        # New search button (forces fresh search)
        self.new_search_button = ttk.Button(
            variety_frame,
            text="🆕 Fresh Search",
            command=self._fresh_search,
            state="disabled"
        )
        self.new_search_button.pack(side='left', padx=2)
        
        # Query stats label
        self.stats_label = ttk.Label(
            variety_frame,
            text="",
            font=('Arial', 8)
        )
        self.stats_label.pack(side='right', padx=5)
        
        # Add to main app's button list for enable/disable control
        if hasattr(self.main_app, 'control_buttons'):
            self.main_app.control_buttons.extend([self.shuffle_button, self.new_search_button])
        
    def _wrap_search_methods(self):
        """Wrap the original search methods to add variety features."""
        # Store original methods
        self.original_search_images = self.main_app.search_images
        self.original_thread_search_images = self.main_app.thread_search_images
        self.original_get_next_image = self.main_app.get_next_image
        
        # Replace with enhanced versions
        self.main_app.search_images = self._enhanced_search_images
        self.main_app.thread_search_images = self._enhanced_thread_search_images
        self.main_app.get_next_image = self._enhanced_get_next_image
    
    def _enhanced_search_images(self):
        """Enhanced image search with variety management."""
        query = self.main_app.search_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter a search term.")
            return
        
        # Update query stats
        self._update_query_stats(query)
        
        # Enable variety buttons
        self.shuffle_button.config(state="normal")
        self.new_search_button.config(state="normal")
        
        # Call original search
        self.original_search_images()
    
    def _enhanced_thread_search_images(self, query):
        """Enhanced background image search with variety parameters."""
        try:
            # Get variety-enhanced search parameters
            search_params = get_image_search_parameters(self.session_tracker, query, shuffle=False)
            
            headers = {"Authorization": f"Client-ID {self.main_app.UNSPLASH_ACCESS_KEY}"}
            
            # Build URL with variety parameters
            url = (f"https://api.unsplash.com/search/photos?"
                   f"query={query}&"
                   f"page={search_params['page']}&"
                   f"per_page={search_params['per_page']}&"
                   f"order_by={search_params['order_by']}&"
                   f"orientation={search_params['orientation']}&"
                   f"content_filter={search_params['content_filter']}")
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results", [])
            
            # Apply offset to skip already seen images
            offset = search_params.get('query_offset', 0)
            if offset > 0 and len(results) > offset:
                results = results[offset:] + results[:offset]
            
            # Filter out recently seen images
            filtered_results = []
            for result in results:
                image_id = result.get('id')
                if not self.session_tracker.has_seen_image(query, image_id):
                    filtered_results.append(result)
                if len(filtered_results) >= 10:  # Limit to reasonable number
                    break
            
            # If no new images, use original results
            if not filtered_results:
                filtered_results = results[:5]  # Take first 5 as fallback
            
            self.main_app.current_results = filtered_results
            
            if not self.main_app.current_results:
                self.main_app.after(0, lambda: messagebox.showinfo("No Results", f"No images found for '{query}'."))
                return
            
            # Get first image
            result = self._enhanced_get_next_image()
            if result:
                photo, pil_img, image_data = result
                
                # Record the image as shown
                image_id = image_data.get('id')
                image_url = image_data.get('urls', {}).get('regular')
                if image_id and image_url:
                    self.session_tracker.record_image_shown(
                        query, image_id, image_url, search_params['page']
                    )
                
                self.main_app.after(0, lambda: self.main_app.display_image(photo, pil_img))
                
        except Exception as e:
            self.main_app.after(0, lambda: messagebox.showerror("Search Error", f"Failed to search images: {e}"))
        finally:
            self.main_app.after(0, self.main_app.hide_progress)
            self.main_app.after(0, self.main_app.enable_buttons)
    
    def _enhanced_get_next_image(self):
        """Get next image with session tracking."""
        if not self.main_app.current_results or self.main_app.current_index >= len(self.main_app.current_results):
            return None
            
        candidate = self.main_app.current_results[self.main_app.current_index]
        self.main_app.current_index += 1
        
        try:
            img_url = candidate["urls"]["regular"]
            img_response = requests.get(img_url, timeout=15)
            img_response.raise_for_status()
            
            image = Image.open(BytesIO(img_response.content))
            photo = ImageTk.PhotoImage(image)
            
            self.main_app.current_image_url = img_url
            self.main_app.used_image_urls.add(img_url)
            
            return photo, image, candidate
            
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    
    def _shuffle_images(self):
        """Shuffle images for current query."""
        query = self.main_app.search_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter a search term first.")
            return
        
        self.main_app.show_progress("Shuffling images...")
        self.main_app.disable_buttons()
        
        threading.Thread(
            target=self._thread_shuffle_images,
            args=(query,),
            daemon=True,
            name="ShuffleImages"
        ).start()
    
    def _thread_shuffle_images(self, query):
        """Background thread for shuffling images."""
        try:
            # Get shuffled search parameters
            search_params = get_image_search_parameters(self.session_tracker, query, shuffle=True)
            
            headers = {"Authorization": f"Client-ID {self.main_app.UNSPLASH_ACCESS_KEY}"}
            
            # Add randomization to order_by for more variety
            order_options = ['relevant', 'latest', 'popular']
            search_params['order_by'] = random.choice(order_options)
            
            url = (f"https://api.unsplash.com/search/photos?"
                   f"query={query}&"
                   f"page={search_params['page']}&"
                   f"per_page={search_params['per_page']}&"
                   f"order_by={search_params['order_by']}")
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results", [])
            
            # Shuffle the results
            random.shuffle(results)
            
            # Apply offset
            offset = search_params.get('query_offset', 0)
            if offset > 0 and len(results) > offset:
                results = results[offset:] + results[:offset]
            
            self.main_app.current_results = results
            self.main_app.current_index = 0
            
            if not results:
                self.main_app.after(0, lambda: messagebox.showinfo("No Results", f"No shuffled images found for '{query}'."))
                return
            
            # Get first shuffled image
            result = self._enhanced_get_next_image()
            if result:
                photo, pil_img, image_data = result
                
                # Record the shuffled image
                image_id = image_data.get('id')
                image_url = image_data.get('urls', {}).get('regular')
                if image_id and image_url:
                    self.session_tracker.record_image_shown(
                        query, image_id, image_url, search_params['page']
                    )
                
                self.main_app.after(0, lambda: self.main_app.display_image(photo, pil_img))
                self.main_app.after(0, lambda: self._update_query_stats(query))
                
        except Exception as e:
            self.main_app.after(0, lambda: messagebox.showerror("Shuffle Error", f"Failed to shuffle images: {e}"))
        finally:
            self.main_app.after(0, self.main_app.hide_progress)
            self.main_app.after(0, self.main_app.enable_buttons)
    
    def _fresh_search(self):
        """Perform a completely fresh search ignoring history."""
        query = self.main_app.search_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter a search term first.")
            return
        
        # Reset query history
        self.session_tracker.reset_query_history(query)
        
        # Perform new search
        self.main_app.show_progress("Starting fresh search...")
        self.main_app.disable_buttons()
        
        threading.Thread(
            target=self._enhanced_thread_search_images,
            args=(query,),
            daemon=True,
            name="FreshSearch"
        ).start()
    
    def _update_query_stats(self, query):
        """Update the query statistics display."""
        try:
            stats = self.session_tracker.get_query_stats(query)
            stats_text = f"Page {stats['current_page']} | {stats['images_shown']} seen"
            self.stats_label.config(text=stats_text)
        except Exception as e:
            print(f"Error updating query stats: {e}")
            self.stats_label.config(text="")
    
    def get_session_summary(self) -> Dict:
        """Get current session summary for display."""
        return self.session_tracker.get_session_stats()
    
    def save_session(self):
        """Save current session data."""
        self.session_tracker.save_session()
    
    def reset_session(self):
        """Reset the current session."""
        self.session_tracker.reset_session()
    
    def export_search_history(self, output_file: Optional[Path] = None) -> Path:
        """Export search history for analysis."""
        if output_file is None:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.data_dir / f"search_history_export_{timestamp}.json"
        
        try:
            import json
            history_data = self.session_tracker.current_session.search_variety_manager.to_dict()
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
            return output_file
        except Exception as e:
            print(f"Error exporting search history: {e}")
            return None


def integrate_image_variety(main_app, data_dir: Path = None) -> ImageVarietyManager:
    """
    Integrate image variety features into an existing main application.
    
    Args:
        main_app: The main application instance
        data_dir: Directory for storing session data
    
    Returns:
        ImageVarietyManager: The integrated variety manager
    """
    return ImageVarietyManager(main_app, data_dir)


# Utility functions for easy integration
def add_variety_to_search_results(results: List[Dict], query: str, 
                                 session_tracker: EnhancedSessionTracker) -> List[Dict]:
    """Filter search results to add variety based on session history."""
    if not results:
        return results
    
    filtered_results = []
    for result in results:
        image_id = result.get('id')
        if image_id and not session_tracker.has_seen_image(query, image_id):
            filtered_results.append(result)
    
    # If no new images, return a subset of original results
    if not filtered_results:
        return results[:5]
    
    return filtered_results


def create_search_url_with_variety(base_url: str, query: str, 
                                  session_tracker: EnhancedSessionTracker,
                                  shuffle: bool = False) -> str:
    """Create a search URL with variety parameters."""
    search_params = get_image_search_parameters(session_tracker, query, shuffle)
    
    # Add variety parameters to base URL
    if '?' in base_url:
        separator = '&'
    else:
        separator = '?'
    
    variety_params = (f"page={search_params['page']}&"
                     f"per_page={search_params['per_page']}&"
                     f"order_by={search_params['order_by']}")
    
    return f"{base_url}{separator}{variety_params}"