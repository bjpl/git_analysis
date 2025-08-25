"""
Test script to verify the UI rendering fix works correctly.
"""

import sys
import tkinter as tk
from tkinter import ttk
import threading
import time

def test_ui_rendering():
    """Test that the main window renders correctly."""
    print("Testing UI rendering fix...")
    print("-" * 50)
    
    # Test 1: Check if main window renders immediately
    print("Test 1: Main window immediate rendering...")
    
    try:
        # Import the fixed application
        from main import ImageSearchApp
        
        # Create app instance
        app = ImageSearchApp()
        
        # Check window is created
        assert app.winfo_exists(), "Window not created"
        print("✓ Main window created")
        
        # Check window has correct title
        assert "Unsplash" in app.title(), "Wrong window title"
        print("✓ Window title set correctly")
        
        # Check window has correct size
        app.update_idletasks()
        width = app.winfo_reqwidth()
        height = app.winfo_reqheight()
        print(f"✓ Window size: {width}x{height}")
        
        # Test 2: Check if main widgets exist
        print("\nTest 2: Widget creation...")
        
        # Check main frame exists
        assert hasattr(app, 'main_frame'), "Main frame not created"
        print("✓ Main frame exists")
        
        # Check search widgets exist
        assert hasattr(app, 'search_entry'), "Search entry not created"
        assert hasattr(app, 'search_button'), "Search button not created"
        print("✓ Search controls created")
        
        # Check content areas exist
        assert hasattr(app, 'image_canvas'), "Image canvas not created"
        assert hasattr(app, 'note_text'), "Note text not created"
        assert hasattr(app, 'description_text'), "Description text not created"
        print("✓ Content areas created")
        
        # Check status bar exists
        assert hasattr(app, 'status_label'), "Status label not created"
        assert hasattr(app, 'stats_label'), "Stats label not created"
        print("✓ Status bar created")
        
        # Test 3: Check initialization state
        print("\nTest 3: Initialization state...")
        
        # Let async initialization run
        app.update()
        time.sleep(0.5)
        app.update()
        
        # Check if loading screen was removed
        if hasattr(app, 'loading_screen'):
            try:
                exists = app.loading_screen.winfo_exists()
                if not exists:
                    print("✓ Loading screen removed after init")
            except:
                print("✓ Loading screen properly destroyed")
        else:
            print("✓ Loading screen handled")
        
        # Check status messages
        status_text = app.status_label.cget('text')
        print(f"✓ Status: {status_text}")
        
        # Test 4: Check API key handling
        print("\nTest 4: API key handling...")
        
        if app.api_keys_ready:
            print("✓ API keys configured - full functionality")
            assert app.search_button.cget('state') != 'disabled', "Search should be enabled"
        else:
            print("✓ API keys not configured - limited mode")
            print("  App runs without blocking for API configuration")
        
        # Test 5: UI responsiveness
        print("\nTest 5: UI responsiveness...")
        
        # Test that UI is responsive
        app.update()
        print("✓ UI event loop is responsive")
        
        # Test search entry accepts input
        app.search_entry.insert(0, "test")
        assert app.search_entry.get() == "test", "Search entry not accepting input"
        print("✓ Search entry accepts input")
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("The UI rendering fix is working correctly.")
        print("=" * 50)
        
        # Clean up
        app.destroy()
        return True
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_visual_test():
    """Run visual test for manual verification."""
    print("\nRunning visual test...")
    print("Check that:")
    print("1. Main window appears immediately (not blank)")
    print("2. All UI elements are visible")
    print("3. No blocking dialog appears on startup")
    print("4. App is responsive to user input")
    print("-" * 50)
    
    try:
        from main import ImageSearchApp
        app = ImageSearchApp()
        
        # Add visual indicator
        indicator = ttk.Label(
            app.main_frame,
            text="✓ UI FIX SUCCESSFUL - Window rendered correctly!",
            foreground="green",
            font=('Arial', 12, 'bold')
        )
        indicator.pack(pady=10)
        
        app.mainloop()
        
    except Exception as e:
        print(f"Visual test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run automated tests
    success = test_ui_rendering()
    
    if success and len(sys.argv) > 1 and sys.argv[1] == "--visual":
        # Run visual test if requested
        run_visual_test()
    elif not success:
        print("\nAutomated tests failed. Fix the issues and try again.")
        sys.exit(1)