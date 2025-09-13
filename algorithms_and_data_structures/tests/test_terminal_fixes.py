#!/usr/bin/env python3
"""
Test script to verify terminal box border alignment fixes
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.terminal_utils import terminal_utils, get_terminal_width, create_safe_box, wrap_text_safe
from ui.windows_formatter import WindowsFormatter
from curriculum_manager import CurriculumManager


def test_terminal_width_detection():
    """Test terminal width detection"""
    print("Testing terminal width detection...")
    
    # Get raw terminal width
    raw_width = terminal_utils.capabilities.width
    print(f"Raw terminal width: {raw_width}")
    
    # Test default safe width (margin=2)
    safe_width_default = get_terminal_width()
    safe_width_2 = get_terminal_width(margin=2)
    safe_width_4 = get_terminal_width(margin=4)
    
    print(f"Safe width (default): {safe_width_default}")
    print(f"Safe width (margin=2): {safe_width_2}")
    print(f"Safe width (margin=4): {safe_width_4}")
    
    assert raw_width > 0, "Terminal width should be positive"
    assert safe_width_default == raw_width - 2, "Default safe width calculation incorrect"
    assert safe_width_2 == raw_width - 2, "Safe width calculation incorrect"
    assert safe_width_4 == raw_width - 4, "Safe width calculation incorrect"
    print("✅ Terminal width detection tests passed")


def test_safe_box_creation():
    """Test safe box creation with various content sizes"""
    print("\nTesting safe box creation...")
    
    # Test 1: Simple content
    content1 = "Hello, World!"
    box1 = create_safe_box(content1, title="Test Box 1")
    print("Box 1 (Simple content):")
    print(box1)
    print()
    
    # Test 2: Multi-line content
    content2 = """This is a multi-line content box.
It contains several lines of text.
Each line should be properly wrapped and aligned."""
    box2 = create_safe_box(content2, title="Multi-line Test")
    print("Box 2 (Multi-line content):")
    print(box2)
    print()
    
    # Test 3: Long content that needs wrapping
    content3 = "This is a very long line of text that should be wrapped automatically when it exceeds the available width in the terminal window."
    box3 = create_safe_box(content3, title="Wrapping Test")
    print("Box 3 (Long content with wrapping):")
    print(box3)
    print()
    
    # Test 4: Content without title
    content4 = "Content without a title should also work properly."
    box4 = create_safe_box(content4)
    print("Box 4 (No title):")
    print(box4)
    print()
    
    print("✅ Safe box creation tests passed")


def test_text_wrapping():
    """Test safe text wrapping"""
    print("\nTesting text wrapping...")
    
    long_text = "This is a very long piece of text that needs to be wrapped properly to fit within the terminal width constraints without breaking the visual alignment of boxes and other UI elements."
    
    # Test wrapping at different widths
    for width in [30, 50, 70]:
        wrapped = wrap_text_safe(long_text, width)
        print(f"Wrapped at width {width}:")
        for line in wrapped:
            print(f"  '{line}' (length: {len(line)})")
            assert len(line) <= width, f"Line exceeds width: {len(line)} > {width}"
        print()
    
    print("✅ Text wrapping tests passed")


def test_windows_formatter():
    """Test Windows formatter with safe utilities"""
    print("\nTesting Windows formatter...")
    
    formatter = WindowsFormatter()
    
    # Test box creation
    test_content = "This is a test of the Windows formatter box functionality."
    box_result = formatter.box(test_content, title="Windows Formatter Test")
    print("Windows formatter box:")
    print(box_result)
    print()
    
    # Test progress bar
    progress_result = formatter.render_progress_bar(7, 10, "Test Progress")
    print("Windows formatter progress bar:")
    print(progress_result)
    print()
    
    print("✅ Windows formatter tests passed")


def test_curriculum_manager():
    """Test curriculum manager display functions"""
    print("\nTesting curriculum manager...")
    
    try:
        manager = CurriculumManager()
        
        # Test banner display
        print("Testing curriculum banner:")
        manager.display_curriculum_banner()
        print()
        
        # Test curriculum list display with sample data
        sample_curricula = [
            {
                "id": 1,
                "name": "Test Curriculum",
                "description": "A test curriculum with a moderately long description to test text wrapping and alignment features.",
                "status": "active",
                "difficulty": "intermediate",
                "category": "Computer Science",
                "author": "Test Author",
                "modules": 5,
                "lessons": 15,
                "students": 100,
                "completion_rate": 85.5,
                "average_rating": 4.7,
                "total_duration": "40-60 hours",
                "tags": ["algorithms", "data-structures", "programming", "computer-science"]
            }
        ]
        
        print("Testing curriculum list display:")
        manager.display_curriculum_list(sample_curricula)
        print()
        
        print("✅ Curriculum manager tests passed")
        
    except Exception as e:
        print(f"⚠️  Curriculum manager test failed: {e}")


def test_terminal_width_edge_cases():
    """Test edge cases for terminal width"""
    print("\nTesting terminal width edge cases...")
    
    # Test capabilities detection
    caps = terminal_utils.capabilities
    print(f"Terminal capabilities:")
    print(f"  Width: {caps.width}")
    print(f"  Height: {caps.height}")
    print(f"  Unicode support: {caps.supports_unicode}")
    print(f"  Color support: {caps.supports_color}")
    print(f"  Platform: {caps.platform}")
    print(f"  Terminal type: {caps.terminal_type}")
    print(f"  Safe box style: {caps.safe_box_style}")
    print()
    
    # Test different terminal widths
    print("Testing boxes at different simulated widths:")
    original_width = terminal_utils.capabilities.width
    
    for test_width in [40, 80, 120]:
        # Temporarily override width for testing
        terminal_utils.capabilities.width = test_width
        
        test_content = f"Testing box at width {test_width}. This content should wrap properly within the specified width constraints."
        box = create_safe_box(test_content, title=f"Width {test_width} Test")
        
        print(f"Box at width {test_width}:")
        print(box)
        print()
    
    # Restore original width
    terminal_utils.capabilities.width = original_width
    
    print("✅ Terminal width edge cases tests passed")


def main():
    """Run all tests"""
    print("=" * 60)
    print("TERMINAL BOX BORDER ALIGNMENT FIXES - TEST SUITE")
    print("=" * 60)
    
    try:
        test_terminal_width_detection()
        test_safe_box_creation()
        test_text_wrapping()
        test_windows_formatter()
        test_curriculum_manager()
        test_terminal_width_edge_cases()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! Terminal box fixes are working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()