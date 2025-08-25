"""
Image viewer widget for displaying Unsplash images.
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO


class ImageViewer(ttk.LabelFrame):
    """Widget for displaying images with resizing capabilities."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="Vista Previa", padding="10", **kwargs)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        self.image_label = ttk.Label(self)
        self.image_label.grid(row=0, column=0, sticky="nsew")
        
        self.current_photo = None
        
    def display_image(self, image_data):
        """Display image from bytes data."""
        try:
            image = Image.open(BytesIO(image_data))
            image.thumbnail((600, 600))
            photo = ImageTk.PhotoImage(image)
            
            self.image_label.config(image=photo)
            self.image_label.image = photo  # Keep a reference
            self.current_photo = photo
            
            return photo
        except Exception as e:
            print(f"Error displaying image: {e}")
            return None
    
    def clear_image(self):
        """Clear the displayed image."""
        self.image_label.config(image="")
        self.image_label.image = None
        self.current_photo = None
    
    def display_image_from_pil(self, pil_image):
        """Display image from PIL Image object."""
        try:
            # Create a copy to avoid modifying the original
            image = pil_image.copy()
            image.thumbnail((600, 600))
            photo = ImageTk.PhotoImage(image)
            
            self.image_label.config(image=photo)
            self.image_label.image = photo  # Keep a reference
            self.current_photo = photo
            
            return photo
        except Exception as e:
            print(f"Error displaying PIL image: {e}")
            return None
    
    def has_image(self):
        """Check if an image is currently displayed."""
        return self.current_photo is not None