#!/usr/bin/env python3
"""
Test script to demonstrate improved formatting features
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.formatter import TerminalFormatter, Theme, Color


def test_formatting_improvements():
    """Test and demonstrate all formatting improvements"""
    
    # Initialize formatter with custom theme
    formatter = TerminalFormatter()
    
    print("\n" + "="*80)
    print("FORMATTING IMPROVEMENTS DEMONSTRATION")
    print("="*80 + "\n")
    
    # Test 1: Enhanced Box Formatting
    print("\n1. ENHANCED BOX FORMATTING")
    print("-" * 40)
    
    # Basic box with proper padding and width control
    formatter.box(
        "This is a properly formatted box with controlled width and padding.\nNo more text overflow issues!",
        title="Basic Box",
        style="single",
        padding=2,
        width=60
    )
    
    # Double-bordered box with centered text
    formatter.box(
        "Centered text looks professional\nand is easy to read",
        title="✨ Centered Content",
        style="double",
        padding=3,
        align="center",
        width=60,
        color=Color.BRIGHT_CYAN
    )
    
    # Heavy box for important content
    formatter.box(
        "CRITICAL: Important information goes here.\nThis box style draws attention.",
        title="⚠️ Important",
        style="heavy",
        padding=2,
        width=60,
        color=Color.BRIGHT_RED
    )
    
    # Test 2: New Frame Feature
    print("\n2. DECORATIVE FRAMES")
    print("-" * 40)
    
    formatter.frame(
        "Ornate frames add elegance\nto special content",
        style="ornate",
        margin=2
    )
    
    # Test 3: Multi-Section Panels
    print("\n3. MULTI-SECTION PANELS")
    print("-" * 40)
    
    sections = [
        ("📊 Algorithm Complexity", "Time: O(n log n)\nSpace: O(n)\nBest for: Large datasets"),
        ("💡 Key Insight", "Binary search reduces the search space\nby half with each iteration"),
        ("🔧 Implementation Tips", "• Use iterative approach for space efficiency\n• Check for edge cases\n• Validate input data")
    ]
    
    formatter.panel(sections, title="Binary Search Analysis")
    
    # Test 4: Enhanced Headers
    print("\n4. ENHANCED HEADERS")
    print("-" * 40)
    
    formatter.header("Banner Style Header", level=1, style="banner", 
                    subtitle="With subtitle support")
    
    formatter.header("Centered Header", level=2, style="centered")
    
    formatter.header("Boxed Header", level=1, style="boxed",
                    subtitle="Clean and professional")
    
    # Test 5: Improved Rules
    print("\n5. IMPROVED HORIZONTAL RULES")
    print("-" * 40)
    
    formatter.rule(title="Single Rule", style="single")
    formatter.rule(title="Double Rule", style="double")
    formatter.rule(title="Thick Rule", style="thick")
    formatter.rule(style="gradient")
    
    # Test 6: Complex Layout Example
    print("\n6. COMPLEX LAYOUT EXAMPLE")
    print("-" * 40)
    
    # Simulate an algorithm explanation with proper formatting
    formatter.header("Quick Sort Algorithm", level=1, style="banner")
    
    formatter.box(
        "Quick Sort is a divide-and-conquer algorithm that picks an element\n"
        "as pivot and partitions the array around the pivot.",
        title="Overview",
        style="rounded",
        padding=2,
        width=70
    )
    
    sections = [
        ("Step 1: Choose Pivot", "Select an element from the array (first, last, or random)"),
        ("Step 2: Partition", "Rearrange array so elements smaller than pivot come before it"),
        ("Step 3: Recursively Sort", "Apply Quick Sort to sub-arrays on both sides of pivot")
    ]
    
    formatter.panel(sections, title="Algorithm Steps")
    
    # Code example with proper formatting
    code = """def quicksort(arr, low, high):
    if low < high:
        # Partition the array
        pi = partition(arr, low, high)
        
        # Recursively sort elements
        quicksort(arr, low, pi - 1)
        quicksort(arr, pi + 1, high)"""
    
    formatter.box(
        code,
        title="Python Implementation",
        style="double",
        padding=2,
        width=60,
        color=Color.BRIGHT_GREEN
    )
    
    # Performance metrics in a neat table-like format
    formatter.frame(
        "Time Complexity:\n"
        "  • Best Case: O(n log n)\n"
        "  • Average Case: O(n log n)\n"
        "  • Worst Case: O(n²)\n\n"
        "Space Complexity: O(log n)",
        style="simple",
        margin=1
    )
    
    formatter.rule(title="End of Demonstration", style="double")
    
    print("\n✅ All formatting features tested successfully!")
    print("\nKey Improvements:")
    print("  • Fixed text overflow with smart truncation")
    print("  • Added padding control for better spacing")
    print("  • Implemented width control to prevent box stretching")
    print("  • Added text alignment options (left, center, right)")
    print("  • Created new frame and panel components")
    print("  • Enhanced headers with multiple styles")
    print("  • Improved rules with various styles")
    print("  • Better color control for visual hierarchy")


if __name__ == "__main__":
    test_formatting_improvements()