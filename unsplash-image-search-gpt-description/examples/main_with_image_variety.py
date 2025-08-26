"""
Example of integrating image variety features into the existing main.py application.
This demonstrates the minimal changes needed to add session-aware image rotation.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from PIL import Image, ImageTk
from io import BytesIO
import threading
import os
import sys
import json
import re
import csv
import time
from pathlib import Path
from datetime import datetime
import traceback

# Add src to path for importing our variety features
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / 'src'))

# Import config manager with error handling (same as original)
try:
    from config_manager import ConfigManager
except ImportError as e:
    print(f"Warning: Could not import config_manager: {e}")
    # Create minimal ConfigManager for fallback
    class ConfigManager:
        def __init__(self):
            self.config_dir = Path('.')
            self.data_dir = Path('./data')
            self.data_dir.mkdir(exist_ok=True)
        def get_api_keys(self):
            return {'unsplash': '', 'openai': '', 'gpt_model': 'gpt-4o-mini'}
        def get_paths(self):
            return {
                'data_dir': self.data_dir,
                'log_file': self.data_dir / 'session_log.json',
                'vocabulary_file': self.data_dir / 'vocabulary.csv'
            }
        def validate_api_keys(self):
            return False

# NEW: Import image variety features
from features.image_variety_integration import integrate_image_variety


class UnsplashGPTApp(tk.Tk):
    """Enhanced UnsplashGPT Application with Image Variety Features."""
    
    def __init__(self):
        super().__init__()
        
        # Basic app setup (same as original)
        self.title("UnsplashGPT - Enhanced with Image Variety")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Initialize config manager
        self.config_manager = ConfigManager()
        
        # Initialize main variables (same as original)
        self.UNSPLASH_ACCESS_KEY = ""
        self.OPENAI_API_KEY = ""
        self.GPT_MODEL = "gpt-4o-mini"
        
        # Search state variables (same as original)
        self.current_query = ""
        self.current_page = 1
        self.current_results = []
        self.current_index = 0
        self.current_image_url = ""
        self.used_image_urls = set()
        self.current_pil_image = None
        
        # Control buttons list for enable/disable functionality
        self.control_buttons = []
        
        # Setup UI first
        self.setup_ui()
        
        # NEW: Initialize image variety system
        self.initialize_image_variety()
        
        # Load configuration after UI is ready
        self.after(100, self.load_configuration)
    
    def initialize_image_variety(self):
        """Initialize the image variety management system."""
        try:
            # Create data directory for session tracking
            variety_data_dir = Path('./data/image_sessions')
            variety_data_dir.mkdir(parents=True, exist_ok=True)
            
            # Integrate image variety features
            self.variety_manager = integrate_image_variety(
                main_app=self,
                data_dir=variety_data_dir
            )
            
            print("✅ Image variety system initialized successfully!")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize image variety system: {e}")
            self.variety_manager = None
    
    def setup_ui(self):
        """Setup the user interface (enhanced version of original)."""
        # Main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(
            self.main_frame, 
            text="🌅 UnsplashGPT - Enhanced with Image Variety", 
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Search frame
        search_frame = ttk.Frame(self.main_frame)
        search_frame.pack(fill='x', pady=5)
        
        ttk.Label(search_frame, text="Search Images:").pack(side='left', padx=(0, 5))
        
        self.search_entry = ttk.Entry(search_frame, width=30, font=('Arial', 11))
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.search_entry.bind('<Return>', lambda e: self.search_images())
        
        self.search_button = ttk.Button(search_frame, text="🔍 Search", command=self.search_images)
        self.search_button.pack(side='right')
        self.control_buttons.append(self.search_button)
        
        # Control buttons frame
        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.pack(fill='x', pady=5)
        
        self.another_button = ttk.Button(controls_frame, text="➡️ Another Image", command=self.another_image)
        self.another_button.pack(side='left', padx=(0, 5))
        self.another_button.config(state="disabled")
        self.control_buttons.append(self.another_button)
        
        # NOTE: Shuffle and Fresh Search buttons will be added automatically by variety_manager
        
        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=5)
        
        # Image display frame
        image_frame = ttk.LabelFrame(self.main_frame, text="Image Display")
        image_frame.pack(fill='both', expand=True, pady=5)
        
        self.image_label = ttk.Label(
            image_frame, 
            text="Search for images to get started!\\nTry: sunset, mountain, ocean, forest, city",
            anchor='center',
            font=('Arial', 12)
        )
        self.image_label.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Description frame
        desc_frame = ttk.LabelFrame(self.main_frame, text="GPT Description")
        desc_frame.pack(fill='x', pady=5)
        
        self.description_text = scrolledtext.ScrolledText(desc_frame, height=4, wrap='word')
        self.description_text.pack(fill='x', padx=5, pady=5)
        
        # Notes frame
        notes_frame = ttk.LabelFrame(self.main_frame, text="Your Notes")
        notes_frame.pack(fill='x', pady=5)
        
        self.note_text = scrolledtext.ScrolledText(notes_frame, height=3, wrap='word')
        self.note_text.pack(fill='x', padx=5, pady=5)
        
        # Status frame
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill='x', pady=2)
        
        self.status_label = ttk.Label(status_frame, text="Ready to search images", font=('Arial', 9))
        self.status_label.pack(side='left')
        
        # NEW: Session info will be added by variety manager on the right side
    
    def load_configuration(self):
        """Load API configuration (same as original logic)."""
        try:
            api_keys = self.config_manager.get_api_keys()
            self.UNSPLASH_ACCESS_KEY = api_keys.get('unsplash', '')
            self.OPENAI_API_KEY = api_keys.get('openai', '')
            self.GPT_MODEL = api_keys.get('gpt_model', 'gpt-4o-mini')
            
            if not self.UNSPLASH_ACCESS_KEY:
                self.show_api_setup_message()
            else:
                self.status_label.config(text="✅ Ready to search images")
                
        except Exception as e:
            print(f"Error loading configuration: {e}")
            self.show_api_setup_message()
    
    def show_api_setup_message(self):
        """Show message about API setup."""
        self.status_label.config(text="⚠️ API keys not configured")
        messagebox.showinfo(
            "API Setup Required",
            "Please configure your Unsplash API key to use image search.\\n\\n"
            "The application will work in demo mode for testing the variety features."
        )
    
    def search_images(self):
        """Search for images with variety enhancement."""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter a search term.")
            return
        
        if not self.UNSPLASH_ACCESS_KEY:
            # Demo mode - simulate search with variety features
            self.demo_search(query)
            return
        
        self.current_query = query
        self.current_index = 0
        self.show_progress(f"Searching for '{query}'...")
        self.disable_buttons()
        
        # NOTE: The variety_manager will automatically enhance this search
        # by wrapping thread_search_images with variety parameters
        
        threading.Thread(
            target=self.thread_search_images,
            args=(query,), 
            daemon=True,
            name="ImageSearch"
        ).start()
    
    def thread_search_images(self, query):
        """Search for images in background thread (enhanced by variety_manager)."""
        try:
            # NOTE: This method is automatically wrapped by variety_manager
            # to add variety parameters and filter previously seen images
            
            headers = {"Authorization": f"Client-ID {self.UNSPLASH_ACCESS_KEY}"}
            url = f"https://api.unsplash.com/search/photos?query={query}&page={self.current_page}&per_page=10"
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            self.current_results = data.get("results", [])
            
            if not self.current_results:
                self.after(0, lambda: messagebox.showinfo("No Results", f"No images found for '{query}'."))
                return
            
            # Get first image
            result = self.get_next_image()
            if result:
                photo, pil_img = result
                self.after(0, lambda: self.display_image(photo, pil_img))
                
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Search Error", f"Failed to search images: {e}"))
        finally:
            self.after(0, self.hide_progress)
            self.after(0, self.enable_buttons)
    
    def get_next_image(self):
        """Get next image from current results (enhanced by variety_manager)."""
        if not self.current_results or self.current_index >= len(self.current_results):
            return None
            
        candidate = self.current_results[self.current_index]
        self.current_index += 1
        
        try:
            img_url = candidate["urls"]["regular"]
            img_response = requests.get(img_url, timeout=15)
            img_response.raise_for_status()
            
            image = Image.open(BytesIO(img_response.content))
            photo = ImageTk.PhotoImage(image)
            
            self.current_image_url = img_url
            self.used_image_urls.add(img_url)
            
            return photo, image
            
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    
    def another_image(self):
        """Get another image from current search."""
        if not self.current_query:
            messagebox.showerror("Error", "Please search for images first.")
            return
            
        self.show_progress("Loading another image...")
        self.disable_buttons()
        
        threading.Thread(
            target=self.thread_get_next_image, 
            daemon=True,
            name="GetNextImage"
        ).start()
    
    def thread_get_next_image(self):
        """Get next image in background thread."""
        try:
            result = self.get_next_image()
            if result:
                photo, pil_img = result
                self.after(0, lambda: self.display_image(photo, pil_img))
            else:
                self.after(0, lambda: messagebox.showinfo("No More Images", "No more images available."))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to load image: {e}"))
        finally:
            self.after(0, self.hide_progress)
            self.after(0, self.enable_buttons)
    
    def display_image(self, photo, pil_image=None):
        """Display image in UI."""
        self.image_label.config(image=photo, text="")
        self.image_label.image = photo
        
        if pil_image:
            self.current_pil_image = pil_image
        
        # Clear previous content
        self.note_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.insert("1.0", "Image loaded! Use GPT features to get descriptions.")
        self.description_text.config(state=tk.DISABLED)
        
        # Enable the another image button
        self.another_button.config(state="normal")
        
        # Update status
        self.status_label.config(text=f"Displaying image for '{self.current_query}'")
    
    def demo_search(self, query):
        """Demo mode search to test variety features without API."""
        self.show_progress(f"Demo search for '{query}'...")
        self.disable_buttons()
        
        def demo_thread():
            try:
                # Simulate API delay
                time.sleep(1)
                
                # Generate mock image
                mock_image_text = f"🖼️ DEMO IMAGE\\n\\nQuery: {query}\\nTimestamp: {datetime.now().strftime('%H:%M:%S')}\\n\\nThis is a simulated image result.\\nThe variety system is tracking this search!"
                
                # Display mock result
                self.after(0, lambda: self.display_demo_result(query, mock_image_text))
                
                # NEW: Track in variety system
                if hasattr(self, 'variety_manager') and self.variety_manager:
                    mock_image_id = f"demo_{query}_{int(time.time())}"
                    mock_image_url = f"https://demo.example.com/{mock_image_id}.jpg"
                    self.variety_manager.session_tracker.record_image_shown(
                        query, mock_image_id, mock_image_url, 1
                    )
                    
                    # Show variety stats
                    stats = self.variety_manager.get_session_summary()
                    stats_text = f"Session: {stats.get('images_viewed', 0)} images, {stats.get('unique_searches', 0)} searches"
                    self.after(0, lambda: self.status_label.config(text=stats_text))
                
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Demo Error", f"Demo failed: {e}"))
            finally:
                self.after(0, self.hide_progress)
                self.after(0, self.enable_buttons)
        
        threading.Thread(target=demo_thread, daemon=True, name="DemoSearch").start()
    
    def display_demo_result(self, query, mock_text):
        """Display demo result."""
        self.current_query = query
        self.image_label.config(text=mock_text, image="")
        self.image_label.image = None
        
        # Enable another image button for demo
        self.another_button.config(state="normal")
        
        # Clear and set demo description
        self.note_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.insert("1.0", f"Demo mode: Showing simulated result for '{query}'. The image variety system is working behind the scenes!")
        self.description_text.config(state=tk.DISABLED)
    
    def show_progress(self, message="Working..."):
        """Show progress indicator."""
        self.progress.start()
        self.status_label.config(text=f"⏳ {message}")
    
    def hide_progress(self):
        """Hide progress indicator."""
        self.progress.stop()
    
    def disable_buttons(self):
        """Disable control buttons during operations."""
        for button in self.control_buttons:
            button.config(state='disabled')
    
    def enable_buttons(self):
        """Enable control buttons after operations."""
        for button in self.control_buttons:
            button.config(state='normal')
    
    def on_closing(self):
        """Handle application closing."""
        try:
            # NEW: Save session data before closing
            if hasattr(self, 'variety_manager') and self.variety_manager:
                self.variety_manager.save_session()
                print("Session data saved successfully")
                
        except Exception as e:
            print(f"Error saving session: {e}")
        finally:
            self.destroy()


def main():
    """Main application entry point."""
    print("🚀 Starting UnsplashGPT with Image Variety Features...")
    
    try:
        app = UnsplashGPTApp()
        
        # Handle window closing
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        print("✅ Application started successfully!")
        print("📝 Try searching for the same term multiple times to see variety in action!")
        print("🔀 Use the Shuffle and Fresh Search buttons for immediate variety!")
        
        app.mainloop()
        
    except KeyboardInterrupt:
        print("\\n❌ Application interrupted by user")
    except Exception as e:
        print(f"❌ Application error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()