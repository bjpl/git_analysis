#!/usr/bin/env python3
"""
Test script to display formatted output with Windows-compatible characters
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ui.windows_formatter import WindowsFormatter

def test_display():
    """Test the Windows formatter with sample content"""
    formatter = WindowsFormatter()
    
    # Clear screen
    formatter.clear_screen()
    
    # Display main header
    print(formatter.header(
        "ALGORITHMS & DATA STRUCTURES",
        "Learning Platform - Beautiful Terminal Interface",
        level=1
    ))
    
    print()
    
    # Display features
    print(formatter.header("Key Features", level=2))
    print(formatter.list_items([
        "Clean, readable output without broken boxes",
        "Windows-optimized ASCII characters",
        "Beautiful color schemes that work",
        "Progressive learning curriculum",
        "Interactive practice problems"
    ], style="arrow"))
    
    print()
    
    # Display progress
    print(formatter.header("Your Progress", level=2))
    print(formatter.progress_bar(7, 10, "Overall Learning"))
    
    print()
    
    # Display sample code
    code = """def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1"""
    
    print(formatter.code_block(code, "python", "Binary Search Implementation"))
    
    print()
    
    # Display algorithm comparison table
    print(formatter.header("Algorithm Comparison", level=2))
    headers = ["Algorithm", "Time Complexity", "Space", "Use Case"]
    rows = [
        ["Binary Search", "O(log n)", "O(1)", "Sorted arrays"],
        ["Linear Search", "O(n)", "O(1)", "Any array"],
        ["Quick Sort", "O(n log n)", "O(log n)", "General sorting"],
        ["Merge Sort", "O(n log n)", "O(n)", "Stable sorting"]
    ]
    print(formatter.table(headers, rows))
    
    print()
    
    # Display a nice box with info
    info_content = """Welcome to your learning journey!
    
This platform provides a comprehensive curriculum
for mastering algorithms and data structures.

Start with foundational concepts and progress
through increasingly complex topics at your own pace."""
    
    print(formatter.box(
        info_content,
        title="Getting Started",
        style="simple"
    ))
    
    print()
    print(formatter.divider("End of Demo"))
    print()
    print(formatter.success("Display test completed successfully!"))
    print(formatter.info("All formatting elements are now Windows-compatible"))
    print()

if __name__ == "__main__":
    test_display()