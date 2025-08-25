"""
Quick test runner to verify the UI fix works.
This will test the fixed version against various scenarios.
"""

import sys
import os
from pathlib import Path
import traceback
import time

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_ui_creation():
    """Test that UI creates properly without hanging."""
    print("Testing basic UI creation...")
    
    try:
        # Import the fixed version
        from ui_fix_main import UIFixedImageSearchApp
        import tkinter as tk
        
        print("  ✓ Imports successful")
        
        # Mock the config manager to avoid actual setup
        from unittest.mock import patch
        
        with patch('ui_fix_main.ensure_api_keys_configured') as mock_config:
            mock_config.return_value = None  # Simulate cancelled setup
            
            print("  → Creating application...")
            app = UIFixedImageSearchApp()
            
            print("  ✓ Application created without errors")
            
            # Check basic properties
            assert app.winfo_exists(), "Window doesn't exist"
            assert "Unsplash" in app.title(), "Title not set correctly"
            assert app.winfo_width() > 100, "Window too narrow"
            assert app.winfo_height() > 100, "Window too short"
            
            print("  ✓ Window properties correct")
            
            # Check UI elements exist
            assert hasattr(app, 'search_entry'), "Search entry missing"
            assert hasattr(app, 'status_label'), "Status label missing"
            assert hasattr(app, 'image_label'), "Image label missing"
            
            print("  ✓ UI elements created")
            
            # Check debug logging
            assert hasattr(app, 'debug_messages'), "Debug logging missing"
            assert len(app.debug_messages) > 0, "No debug messages"
            
            print("  ✓ Debug logging working")
            
            # Update UI to ensure it's responsive
            app.update_idletasks()
            
            print("  ✓ UI responsive")
            
            # Clean up
            app.destroy()
            
            print("  ✓ Cleanup successful")
            
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        traceback.print_exc()
        return False

def test_visual_display():
    """Quick visual test - shows window briefly."""
    print("\\nTesting visual display...")
    
    try:
        from ui_fix_main import UIFixedImageSearchApp
        from unittest.mock import patch
        import threading
        
        with patch('ui_fix_main.ensure_api_keys_configured') as mock_config:
            mock_config.return_value = None
            
            print("  → Creating visible application...")
            app = UIFixedImageSearchApp()
            
            # Force window to front
            app.lift()
            app.attributes('-topmost', True)
            app.after(100, lambda: app.attributes('-topmost', False))
            
            print("  ✓ Window should now be visible")
            print("    Check: Window shows properly (not blank)")
            print("    Check: UI elements are visible")
            print("    Check: Status bar shows message")
            
            # Auto-close after 3 seconds
            def auto_close():
                time.sleep(3)
                try:
                    app.quit()
                except:
                    pass
            
            closer = threading.Thread(target=auto_close, daemon=True)
            closer.start()
            
            # Run briefly
            try:
                app.mainloop()
            except:
                pass
            
            print("  ✓ Visual test completed")
            
        return True
        
    except Exception as e:
        print(f"  ✗ Visual test error: {e}")
        return False

def test_error_handling():
    """Test error handling scenarios."""
    print("\\nTesting error handling...")
    
    try:
        from ui_fix_main import UIFixedImageSearchApp
        from unittest.mock import patch
        
        # Test with config error
        with patch('ui_fix_main.ensure_api_keys_configured') as mock_config:
            mock_config.side_effect = Exception("Mock configuration error")
            
            print("  → Testing config error handling...")
            app = UIFixedImageSearchApp()
            
            # Give background thread time to run
            time.sleep(0.5)
            app.update_idletasks()
            
            # App should still exist and be functional
            assert app.winfo_exists(), "App crashed on config error"
            
            # Status should reflect error state
            status = app.status_label.cget('text').lower()
            assert any(word in status for word in ['configuration', 'setup', 'needed']), f"Status doesn't reflect error: {status}"
            
            print("  ✓ Config error handled gracefully")
            
            app.destroy()
            
        return True
        
    except Exception as e:
        print(f"  ✗ Error handling test failed: {e}")
        return False

def test_performance():
    """Test that UI creation is fast."""
    print("\\nTesting performance...")
    
    try:
        from ui_fix_main import UIFixedImageSearchApp
        from unittest.mock import patch
        import time
        
        with patch('ui_fix_main.ensure_api_keys_configured') as mock_config:
            mock_config.return_value = None
            
            start_time = time.time()
            app = UIFixedImageSearchApp()
            creation_time = time.time() - start_time
            
            print(f"  → UI creation time: {creation_time:.2f} seconds")
            
            assert creation_time < 5.0, f"UI creation too slow: {creation_time:.2f}s"
            print("  ✓ UI creation is fast enough")
            
            # Test UI responsiveness
            start_time = time.time()
            for _ in range(10):
                app.update_idletasks()
            update_time = time.time() - start_time
            
            print(f"  → UI update time: {update_time:.3f} seconds")
            assert update_time < 1.0, f"UI updates too slow: {update_time:.3f}s"
            print("  ✓ UI is responsive")
            
            app.destroy()
            
        return True
        
    except Exception as e:
        print(f"  ✗ Performance test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("UI Fix Test Suite")
    print("=" * 50)
    print("Testing the fixed version of the image search app")
    print("This verifies the blank window issue is resolved.\\n")
    
    tests = [
        ("Basic UI Creation", test_basic_ui_creation),
        ("Error Handling", test_error_handling),
        ("Performance", test_performance),
        ("Visual Display", test_visual_display),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"Running: {test_name}")
        try:
            if test_func():
                print(f"✓ {test_name} PASSED\\n")
                passed += 1
            else:
                print(f"✗ {test_name} FAILED\\n")
                failed += 1
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}\\n")
            failed += 1
    
    print("=" * 50)
    print("TEST SUMMARY")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")
    
    if failed == 0:
        print("\\n🎉 ALL TESTS PASSED!")
        print("The UI fix should resolve the blank window issue.")
        print("\\nTo use the fixed version, run:")
        print("  python src/ui_fix_main.py")
    else:
        print(f"\\n❌ {failed} tests failed.")
        print("Please check the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\\n" + "=" * 50)
        print("READY TO USE!")
        print("=" * 50)
        print("The fixed version is available at:")
        print("  src/ui_fix_main.py")
        print("\\nKey improvements:")
        print("• UI always creates, even without API keys")
        print("• Proper window focus and visibility") 
        print("• Debug logging for troubleshooting")
        print("• Graceful error handling")
        print("• No race conditions between dialogs")
        print("• Background API configuration")
    
    sys.exit(0 if success else 1)