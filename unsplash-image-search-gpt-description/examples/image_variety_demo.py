"""
Demonstration of the image variety features.
Shows how to integrate session tracking and image rotation with the main application.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / 'src'))

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime

# Import the variety management features
from features.enhanced_session_tracker import EnhancedSessionTracker, get_image_search_parameters
from features.image_variety_integration import ImageVarietyManager


class MockMainApp:
    """Mock main application to demonstrate variety features."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Image Variety Demo")
        self.root.geometry("800x600")
        
        # Mock attributes that the variety manager expects
        self.current_results = []
        self.current_index = 0
        self.current_image_url = ""
        self.used_image_urls = set()
        self.current_query = ""
        self.UNSPLASH_ACCESS_KEY = "demo_key"  # Mock key for demo
        self.control_buttons = []
        
        # Setup UI
        self._setup_ui()
        
        # Initialize variety manager
        self.variety_manager = None
        self._initialize_variety_manager()
    
    def _setup_ui(self):
        """Setup the demo UI."""
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Search frame
        search_frame = ttk.Frame(self.main_frame)
        search_frame.pack(fill='x', pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side='left', padx=(0, 5))
        
        self.search_button = ttk.Button(search_frame, text="Search Images", command=self.search_images)
        self.search_button.pack(side='left', padx=5)
        
        self.control_buttons.append(self.search_button)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=5)
        
        # Image display area (mock)
        self.image_frame = ttk.LabelFrame(self.main_frame, text="Image Display")
        self.image_frame.pack(fill='both', expand=True, pady=5)
        
        self.image_label = ttk.Label(self.image_frame, text="No image loaded", anchor='center')
        self.image_label.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Results frame
        self.results_frame = ttk.LabelFrame(self.main_frame, text="Session Statistics")
        self.results_frame.pack(fill='x', pady=5)
        
        self.results_text = tk.Text(self.results_frame, height=8, wrap='word')
        self.results_text.pack(fill='x', padx=5, pady=5)
        
        # Control buttons frame will be added by variety manager
        
        # Demo data display
        self._setup_demo_display()
    
    def _setup_demo_display(self):
        """Setup demo-specific display elements."""
        demo_frame = ttk.LabelFrame(self.main_frame, text="Demo Controls")
        demo_frame.pack(fill='x', pady=5)
        
        # Demo buttons
        ttk.Button(demo_frame, text="Simulate Search", command=self._demo_search).pack(side='left', padx=2)
        ttk.Button(demo_frame, text="Show Statistics", command=self._show_statistics).pack(side='left', padx=2)
        ttk.Button(demo_frame, text="Export History", command=self._export_history).pack(side='left', padx=2)
        ttk.Button(demo_frame, text="Reset Session", command=self._reset_session).pack(side='left', padx=2)
    
    def _initialize_variety_manager(self):
        """Initialize the image variety manager."""
        try:
            data_dir = project_root / 'data' / 'demo_sessions'
            data_dir.mkdir(parents=True, exist_ok=True)
            
            self.variety_manager = ImageVarietyManager(self, data_dir)
            
            self._log_message("Image variety manager initialized successfully!")
            self._log_message(f"Data directory: {data_dir}")
            
        except Exception as e:
            self._log_message(f"Error initializing variety manager: {e}")
    
    def search_images(self):
        """Mock search images function."""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter a search term.")
            return
        
        self.current_query = query
        self._log_message(f"Starting search for: '{query}'")
        
        # Show progress
        self.show_progress(f"Searching for '{query}'...")
        self.disable_buttons()
        
        # Simulate search in background
        threading.Thread(
            target=self.thread_search_images,
            args=(query,),
            daemon=True,
            name="MockSearch"
        ).start()
    
    def thread_search_images(self, query):
        """Mock background search function."""
        try:
            # Simulate API delay
            time.sleep(1)
            
            # Get variety parameters
            if self.variety_manager:
                search_params = get_image_search_parameters(
                    self.variety_manager.session_tracker, query
                )
                self.after(0, lambda: self._log_message(f"Search parameters: {search_params}"))
            
            # Simulate finding results
            mock_results = self._generate_mock_results(query, 10)
            self.current_results = mock_results
            self.current_index = 0
            
            # Simulate getting first image
            if self.current_results:
                result = self.get_next_image()
                if result:
                    self.after(0, lambda: self.display_image(None, None, result[2]))
                    
                    # Record in variety manager
                    if self.variety_manager:
                        image_data = result[2]
                        self.variety_manager.session_tracker.record_image_shown(
                            query, image_data['id'], image_data['url'], 1
                        )
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Search Error", f"Mock search failed: {e}"))
        finally:
            self.after(0, self.hide_progress)
            self.after(0, self.enable_buttons)
    
    def get_next_image(self):
        """Mock get next image function."""
        if not self.current_results or self.current_index >= len(self.current_results):
            return None
        
        candidate = self.current_results[self.current_index]
        self.current_index += 1
        
        self.current_image_url = candidate['url']
        self.used_image_urls.add(candidate['url'])
        
        return None, None, candidate  # Mock: no actual PIL image
    
    def display_image(self, photo, pil_image, image_data=None):
        """Mock display image function."""
        if image_data:
            display_text = f"Image: {image_data['id']}\\nURL: {image_data['url']}\\nDescription: {image_data.get('description', 'N/A')}"
            self.image_label.config(text=display_text)
            
            self._log_message(f"Displaying image: {image_data['id']}")
            
            # Track in variety manager
            if self.variety_manager:
                query = self.search_entry.get().strip()
                stats = self.variety_manager.session_tracker.get_query_stats(query)
                self._log_message(f"Query stats: {stats}")
    
    def show_progress(self, message):
        """Show progress indicator."""
        self.progress.start()
        self._log_message(f"Progress: {message}")
    
    def hide_progress(self):
        """Hide progress indicator."""
        self.progress.stop()
    
    def disable_buttons(self):
        """Disable control buttons."""
        for button in self.control_buttons:
            button.config(state='disabled')
    
    def enable_buttons(self):
        """Enable control buttons."""
        for button in self.control_buttons:
            button.config(state='normal')
    
    def after(self, delay, func):
        """Schedule function call."""
        self.root.after(delay, func)
    
    def _generate_mock_results(self, query, count):
        """Generate mock search results."""
        import hashlib
        results = []
        
        for i in range(count):
            # Generate consistent but varied mock data
            seed = hashlib.md5(f"{query}_{i}_{int(time.time())}".encode()).hexdigest()[:8]
            result = {
                'id': f"img_{seed}",
                'url': f"https://example.com/image_{seed}.jpg",
                'description': f"Mock image for '{query}' (#{i+1})",
                'author': f"Artist_{seed[:4]}",
                'tags': [query.lower(), f"tag_{seed[:3]}"]
            }
            results.append(result)
        
        return results
    
    def _demo_search(self):
        """Perform a demo search with variety."""
        demo_queries = ["sunset", "mountain", "ocean", "forest", "city"]
        import random
        query = random.choice(demo_queries)
        
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, query)
        self.search_images()
    
    def _show_statistics(self):
        """Show current session statistics."""
        if not self.variety_manager:
            self._log_message("Variety manager not available")
            return
        
        try:
            stats = self.variety_manager.get_session_summary()
            overall_stats = self.variety_manager.session_tracker.get_overall_stats()
            
            stats_text = f"""
=== Current Session ===
Date: {stats.get('session_date', 'N/A')}
Time: {stats.get('session_time', 'N/A')}
Images Viewed: {stats.get('images_viewed', 0)}
Unique Searches: {stats.get('unique_searches', 0)}
Quiz Attempts: {stats.get('total_attempts', 0)}
Accuracy: {stats.get('accuracy_percentage', 0)}%

=== Overall Statistics (30 days) ===
Total Sessions: {overall_stats.get('total_sessions', 0)}
Total Images Viewed: {overall_stats.get('total_images_viewed', 0)}
Total Searches: {overall_stats.get('total_unique_searches', 0)}
Overall Accuracy: {overall_stats.get('overall_accuracy', 0)}%
"""
            
            self._log_message(stats_text)
            
        except Exception as e:
            self._log_message(f"Error getting statistics: {e}")
    
    def _export_history(self):
        """Export search history."""
        if not self.variety_manager:
            self._log_message("Variety manager not available")
            return
        
        try:
            export_file = self.variety_manager.export_search_history()
            if export_file:
                self._log_message(f"Search history exported to: {export_file}")
            else:
                self._log_message("Failed to export search history")
                
        except Exception as e:
            self._log_message(f"Error exporting history: {e}")
    
    def _reset_session(self):
        """Reset the current session."""
        if not self.variety_manager:
            self._log_message("Variety manager not available")
            return
        
        try:
            self.variety_manager.reset_session()
            self._log_message("Session reset successfully")
            self.results_text.delete(1.0, tk.END)
            
        except Exception as e:
            self._log_message(f"Error resetting session: {e}")
    
    def _log_message(self, message):
        """Log a message to the results area."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\\n"
        
        self.results_text.insert(tk.END, log_entry)
        self.results_text.see(tk.END)
        print(f"Demo Log: {message}")
    
    def run(self):
        """Run the demo application."""
        self._log_message("Image Variety Demo Started")
        self._log_message("Try searching for different terms and use the variety buttons!")
        self.root.mainloop()


def main():
    """Run the image variety demo."""
    print("Starting Image Variety Demo...")
    
    try:
        app = MockMainApp()
        app.run()
    except KeyboardInterrupt:
        print("\\nDemo interrupted by user")
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()