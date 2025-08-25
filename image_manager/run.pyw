#!/usr/bin/env python
"""
Image Manager - Silent launcher (no console window)
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from image_manager import ImageOrganizer
    
    if __name__ == "__main__":
        app = ImageOrganizer()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
        
except Exception as e:
    import tkinter as tk
    from tkinter import messagebox
    
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Image Manager Error", f"Failed to start application:\n\n{str(e)}\n\nPlease check requirements are installed:\npip install -r requirements.txt")
    root.destroy()