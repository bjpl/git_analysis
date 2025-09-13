#!/usr/bin/env python3
"""Test the unified formatter to ensure it works correctly"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ui.unified_formatter import (
    UnifiedFormatter, Formatter, TerminalFormatter,
    success, error, warning, info, header, 
    create_box, progress_bar, clear_screen
)

def test_unified_formatter():
    """Test all formatter functions"""
    print("\n" + "="*60)
    print("UNIFIED FORMATTER TEST")
    print("="*60 + "\n")
    
    # Test basic formatting
    print("1. Basic Color Formatting:")
    print("  ", success("✓ Success message"))
    print("  ", error("✗ Error message"))
    print("  ", warning("⚠ Warning message"))
    print("  ", info("ℹ Info message"))
    print()
    
    # Test headers
    print("2. Headers:")
    print(header("Default Header"))
    print()
    
    # Test box
    print("3. Box Formatting:")
    box_content = [
        "This is line 1",
        "This is line 2",
        "This is line 3"
    ]
    print(create_box(box_content, "Test Box"))
    print()
    
    # Test progress bar
    print("4. Progress Bars:")
    for i in [0, 25, 50, 75, 100]:
        print(f"  {i}%: {progress_bar(i, 100)}")
    print()
    
    # Test formatter instance
    print("5. Formatter Instance:")
    formatter = UnifiedFormatter()
    
    # Test table
    headers = ["Name", "Type", "Status"]
    rows = [
        ["Arrays", "Data Structure", "Complete"],
        ["QuickSort", "Algorithm", "In Progress"],
        ["Trees", "Data Structure", "Not Started"]
    ]
    print(formatter.create_table(headers, rows, show_index=True))
    print()
    
    # Test list formatting
    print("6. List Formatting:")
    items = ["First item", "Second item", "Third item"]
    print(formatter.format_list(items, style="bullet"))
    print()
    print(formatter.format_list(items, style="number"))
    print()
    
    # Test text wrapping
    print("7. Text Wrapping:")
    long_text = "This is a very long text that needs to be wrapped properly to fit within the terminal width. It should break at appropriate points and maintain proper indentation."
    print(formatter.wrap_text(long_text, width=50, indent=2))
    print()
    
    # Test backward compatibility
    print("8. Backward Compatibility:")
    old_formatter = Formatter()
    print("  Using Formatter class:", old_formatter.success("Works!"))
    
    terminal_formatter = TerminalFormatter()
    print("  Using TerminalFormatter:", terminal_formatter.success("Also works!"))
    print()
    
    # Test Windows compatibility
    print("9. Platform Info:")
    print(f"  Platform: {sys.platform}")
    print(f"  Colors enabled: {UnifiedFormatter.colors_enabled}")
    print(f"  Unicode enabled: {UnifiedFormatter.unicode_enabled}")
    print()
    
    # Test disabling colors
    print("10. Color Control:")
    UnifiedFormatter.disable_colors()
    print("  Colors disabled:", success("This should have no color"))
    UnifiedFormatter.enable_colors()
    print("  Colors enabled:", success("This should be green"))
    print()
    
    print("="*60)
    print(success("✓ All tests completed successfully!"))
    print("="*60)

if __name__ == "__main__":
    test_unified_formatter()