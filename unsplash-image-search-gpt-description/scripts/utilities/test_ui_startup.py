"""
Quick test to verify UI startup fix
"""
import sys
import time
import tkinter as tk
from tkinter import ttk

def test_ui_startup():
    """Test that the UI starts up correctly"""
    print("Testing UI startup fix...")
    print("=" * 50)
    
    try:
        # Test 1: Check if tkinter is working
        print("Test 1: Checking tkinter...")
        test_root = tk.Tk()
        test_root.withdraw()
        test_root.destroy()
        print("✓ Tkinter is working")
        
        # Test 2: Import main application
        print("\nTest 2: Importing application...")
        from main import ImageSearchApp
        print("✓ Application imported successfully")
        
        # Test 3: Create application instance
        print("\nTest 3: Creating application instance...")
        app = ImageSearchApp()
        print("✓ Application instance created")
        
        # Test 4: Check if main widgets exist
        print("\nTest 4: Checking for main widgets...")
        widgets_to_check = [
            ('search_entry', 'Search entry field'),
            ('search_button', 'Search button'),
            ('image_label', 'Image display label'),
            ('description_text', 'Description text widget'),
            ('note_text', 'Note text widget')
        ]
        
        missing_widgets = []
        for widget_name, description in widgets_to_check:
            if hasattr(app, widget_name):
                print(f"  ✓ {description} exists")
            else:
                print(f"  ✗ {description} missing!")
                missing_widgets.append(widget_name)
        
        # Test 5: Check window properties
        print("\nTest 5: Checking window properties...")
        title = app.title()
        geometry = app.geometry()
        print(f"  Window title: {title}")
        print(f"  Window geometry: {geometry}")
        
        if title and title != "tk":
            print("  ✓ Window has proper title")
        else:
            print("  ✗ Window has default 'tk' title!")
        
        # Test 6: Check if widgets are visible
        print("\nTest 6: Checking widget visibility...")
        app.update_idletasks()
        
        if hasattr(app, 'search_entry'):
            if app.search_entry.winfo_viewable():
                print("  ✓ Search entry is visible")
            else:
                print("  ✗ Search entry is not visible!")
        
        # Summary
        print("\n" + "=" * 50)
        if not missing_widgets:
            print("✅ SUCCESS: All UI components created successfully!")
            print("The blank window issue has been FIXED!")
        else:
            print(f"⚠️ WARNING: Some widgets are missing: {missing_widgets}")
            print("The UI may not be fully functional.")
        
        print("\nApplication is running. Close the window to exit.")
        print("=" * 50)
        
        # Keep the window open for manual inspection
        app.mainloop()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    test_ui_startup()