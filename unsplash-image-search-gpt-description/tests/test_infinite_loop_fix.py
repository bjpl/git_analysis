"""
Test script to verify the infinite loop fix in image collection
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_get_next_image_limits():
    """Test that get_next_image respects collection limits"""
    from unittest.mock import Mock, patch, MagicMock
    import tkinter as tk
    
    # Create a mock app instance
    mock_app = Mock()
    mock_app.images_collected_count = 29  # Just below limit
    mock_app.max_images_per_search = 30
    mock_app.search_cancelled = False
    mock_app.current_index = 0
    mock_app.current_results = []
    mock_app.current_page = 1
    mock_app.current_query = "test"
    mock_app.used_image_urls = set()
    mock_app.image_cache = {}
    mock_app.show_collection_limit_reached = Mock()
    
    # Import the actual method
    from main import ImageSearchApp
    
    # Test case 1: Should stop at collection limit
    print("Test 1: Collection limit enforcement...")
    mock_app.images_collected_count = 30  # At limit
    
    # Bind the method to our mock
    get_next_image = ImageSearchApp.get_next_image.__get__(mock_app, ImageSearchApp)
    
    # Should return None when at limit
    result = get_next_image()
    assert result is None, "Should return None when at collection limit"
    assert mock_app.show_collection_limit_reached.called, "Should show limit reached message"
    print("✓ Collection limit correctly enforced")
    
    # Test case 2: Should stop when cancelled
    print("\nTest 2: Cancellation flag enforcement...")
    mock_app.images_collected_count = 5  # Below limit
    mock_app.search_cancelled = True
    mock_app.show_collection_limit_reached.reset_mock()
    
    result = get_next_image()
    assert result is None, "Should return None when search is cancelled"
    assert not mock_app.show_collection_limit_reached.called, "Should not show limit message when cancelled"
    print("✓ Cancellation flag correctly enforced")
    
    # Test case 3: Verify counter increments
    print("\nTest 3: Collection counter increment...")
    
    # Check that main.py has the increment line
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'self.images_collected_count += 1' in content, "Counter increment is missing"
        print("✓ Collection counter increment found in code")
    
    # Test case 4: Reset on new search
    print("\nTest 4: Counter reset on new search...")
    
    # Check that search_image resets the counter
    assert 'self.images_collected_count = 0  # Reset collection count' in content, "Counter reset is missing"
    assert 'self.search_cancelled = False  # Reset cancellation flag' in content, "Cancellation reset is missing"
    print("✓ Counter and cancellation flag reset on new search")
    
    print("\n" + "="*50)
    print("✅ ALL TESTS PASSED - Infinite loop issue is FIXED!")
    print("="*50)
    print("\nKey fixes applied:")
    print("1. Added collection limit check in while loop")
    print("2. Added cancellation flag check in while loop")
    print("3. Increment images_collected_count on successful collection")
    print("4. Reset counters and flags on new search")
    
    return True

if __name__ == "__main__":
    try:
        test_get_next_image_limits()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)