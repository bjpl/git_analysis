"""
Example integration of controlled image loading system.
Shows how to integrate the new controlled image service with the existing app.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from services.controlled_image_service import (
    ControlledImageService, 
    ImageCollectionLimits, 
    SearchSession
)
from ui.widgets.controlled_search_panel import ControlledSearchPanel
from ui.theme_manager import ThemeManager
from config_manager import ConfigManager


class ControlledImageSearchDemo:
    """Demo application showing controlled image search integration."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Controlled Image Search Demo")
        self.root.geometry("900x700")
        
        # Initialize configuration and services
        self.config_manager = ConfigManager()
        self.theme_manager = ThemeManager(self.config_manager)
        
        # Get API keys
        api_keys = self.config_manager.get_api_keys()
        if not api_keys['unsplash']:
            messagebox.showerror("Missing API Key", "Unsplash API key is required for this demo.")
            self.root.destroy()
            return
        
        # Initialize controlled image service
        self.image_service = ControlledImageService(
            api_keys['unsplash'],
            app_callback=self
        )
        
        # Current state
        self.current_session = None
        self.loaded_images = []
        
        self.create_widgets()
        self.setup_callbacks()
        
    def create_widgets(self):
        """Create the demo UI."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Controlled Image Search Demo",
            font=('TkDefaultFont', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Create controlled search panel
        self.search_panel = ControlledSearchPanel(main_frame, self.theme_manager)
        
        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left: Image display
        image_frame = ttk.LabelFrame(content_frame, text="Current Image", padding="10")
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.image_label = tk.Label(image_frame, text="No image loaded", bg='lightgray')
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Right: Session info and controls
        info_frame = ttk.LabelFrame(content_frame, text="Session Information", padding="10")
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        info_frame.configure(width=300)
        info_frame.pack_propagate(False)
        
        # Session stats
        self.session_info = tk.Text(info_frame, height=15, width=35, wrap=tk.WORD, state=tk.DISABLED)
        self.session_info.pack(fill=tk.BOTH, expand=True)
        
        # Update stats periodically
        self.update_session_info()
        self.root.after(2000, self.periodic_update)
    
    def setup_callbacks(self):
        """Setup callbacks for the search panel."""
        self.search_panel.set_callbacks(
            on_search=self.handle_search,
            on_load_more=self.handle_load_more,
            on_stop=self.handle_stop,
            get_stats=self.get_session_stats
        )
    
    def handle_search(self, query: str, limits: ImageCollectionLimits):
        """Handle new search request."""
        print(f"Starting search for: {query}")
        
        # Start new search session
        success = self.image_service.start_new_search(query, limits)
        if success:
            self.current_session = self.image_service.current_session
            self.search_panel.update_session(self.current_session)
            self.loaded_images.clear()
            
            # Load first image automatically
            self.load_next_image()
    
    def handle_load_more(self):
        """Handle load more request."""
        print("Loading more images...")
        
        # Load next batch
        batch_size = self.current_session.limits.batch_size if self.current_session else 5
        loaded_count = 0
        
        for i in range(batch_size):
            if self.load_next_image():
                loaded_count += 1
            else:
                break
        
        print(f"Loaded {loaded_count} images")
        
        # Update UI
        self.search_panel.update_session(self.current_session)
    
    def handle_stop(self):
        """Handle stop request."""
        print("Stopping search session")
        self.image_service.stop_current_search()
        self.search_panel.update_session(self.current_session)
    
    def load_next_image(self) -> bool:
        """Load the next image and display it."""
        try:
            result = self.image_service.get_next_image_controlled()
            if result:
                photo_image, pil_image, url = result
                
                # Display image
                self.image_label.configure(image=photo_image, text="")
                self.image_label.image = photo_image  # Keep reference
                
                # Store image info
                self.loaded_images.append({
                    'url': url,
                    'timestamp': datetime.now(),
                    'size': pil_image.size
                })
                
                print(f"Loaded image: {url[:50]}...")
                return True
            else:
                print("No more images available")
                return False
                
        except Exception as e:
            print(f"Error loading image: {e}")
            messagebox.showerror("Loading Error", f"Error loading image: {e}")
            return False
    
    def get_session_stats(self):
        """Get current session statistics."""
        return self.image_service.get_session_stats()
    
    def update_session_info(self):
        """Update the session information display."""
        self.session_info.configure(state=tk.NORMAL)
        self.session_info.delete("1.0", tk.END)
        
        if self.current_session:
            # Session details
            info_text = f"""SESSION DETAILS:
Query: {self.current_session.query}
Status: {self.current_session.status.upper()}
Created: {self.current_session.created_at.strftime('%H:%M:%S')}

PROGRESS:
Images loaded: {self.current_session.images_loaded}
Maximum allowed: {self.current_session.limits.max_images_per_session}
Pages fetched: {self.current_session.pages_fetched}
Can load more: {'Yes' if self.current_session.can_load_more_images() else 'No'}

LIMITS:
Max images: {self.current_session.limits.max_images_per_session}
Max pages: {self.current_session.limits.max_pages_per_session}
Batch size: {self.current_session.limits.batch_size}
Warning threshold: {self.current_session.limits.warn_threshold}
Confirmation interval: {self.current_session.limits.confirmation_interval}

"""
            
            # Add service stats
            stats = self.get_session_stats()
            if stats and stats.get('status') != 'no_session':
                rate_stats = stats.get('rate_limit_stats', {})
                cache_stats = stats.get('cache_stats', {})
                
                info_text += f"""API USAGE:
Calls made: {rate_stats.get('api_calls_made', 0)}
Calls remaining: {rate_stats.get('api_calls_remaining', 0)}
Reset in: {rate_stats.get('time_until_reset', 0)} min

CACHE:
Cached images: {cache_stats.get('cached_images', 0)}
Cache size: {cache_stats.get('size_mb', 0):.1f} MB
Max size: {cache_stats.get('max_size_mb', 0)} MB

"""
            
            # Add loaded images info
            if self.loaded_images:
                info_text += f"LOADED IMAGES ({len(self.loaded_images)}):\\n"
                for i, img_info in enumerate(self.loaded_images[-5:], 1):  # Show last 5
                    url_short = img_info['url'][:30] + "..." if len(img_info['url']) > 30 else img_info['url']
                    size_str = f"{img_info['size'][0]}x{img_info['size'][1]}"
                    time_str = img_info['timestamp'].strftime('%H:%M:%S')
                    info_text += f"  {i}. [{time_str}] {size_str} - {url_short}\\n"
        else:
            info_text = "No active search session\\n\\nClick 'Search' to start a new session."
        
        self.session_info.insert(tk.END, info_text)
        self.session_info.configure(state=tk.DISABLED)
    
    def periodic_update(self):
        """Periodic update of session information."""
        self.update_session_info()
        self.root.after(2000, self.periodic_update)  # Update every 2 seconds
    
    def get_parent_window(self):
        """Return parent window for dialogs."""
        return self.root
    
    def run(self):
        """Run the demo application."""
        self.root.mainloop()


def main():
    """Main entry point for the demo."""
    demo = ControlledImageSearchDemo()
    demo.run()


if __name__ == "__main__":
    # Add necessary imports for the demo
    from datetime import datetime
    main()