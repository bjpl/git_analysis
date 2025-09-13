#!/usr/bin/env python3
"""
Test Script for Unified CLI Formatter
Demonstrates all formatting capabilities with beautiful output
"""

import sys
import os
from pathlib import Path
import time
import asyncio

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Force color output
os.environ["FORCE_COLOR"] = "1"
os.environ["COLORTERM"] = "truecolor"

def test_formatting():
    """Test all formatting capabilities"""
    from src.cli_formatter import CLIFormatter, BoxStyle
    
    formatter = CLIFormatter()
    
    # Test 1: Beautiful Headers
    print("\n" + "="*70)
    print("TEST 1: BEAUTIFUL HEADERS")
    print("="*70)
    
    formatter.display_header(
        "🚀 Algorithm Learning Platform",
        "Master Data Structures & Algorithms",
        BoxStyle.HEADER
    )
    
    time.sleep(1)
    
    # Test 2: Content Panels
    print("\n" + "="*70)
    print("TEST 2: CONTENT PANELS")
    print("="*70)
    
    content = """Welcome to the Algorithm Learning Platform!
    
This platform offers:
• Interactive lessons on algorithms
• Hands-on coding exercises
• Visual algorithm demonstrations
• Progress tracking and achievements"""
    
    formatter.display_panel(
        content,
        title="📚 About This Platform",
        style=BoxStyle.CONTENT
    )
    
    time.sleep(1)
    
    # Test 3: Beautiful Tables
    print("\n" + "="*70)
    print("TEST 3: BEAUTIFUL TABLES")
    print("="*70)
    
    columns = [
        {'name': 'Algorithm', 'style': 'cyan', 'width': 20},
        {'name': 'Time Complexity', 'style': 'yellow', 'width': 15},
        {'name': 'Space Complexity', 'style': 'magenta', 'width': 15},
        {'name': 'Use Case', 'style': 'white', 'width': 30}
    ]
    
    rows = [
        ['Quick Sort', 'O(n log n)', 'O(log n)', 'General purpose sorting'],
        ['Merge Sort', 'O(n log n)', 'O(n)', 'Stable sorting, external sorting'],
        ['Binary Search', 'O(log n)', 'O(1)', 'Searching sorted arrays'],
        ['BFS', 'O(V + E)', 'O(V)', 'Shortest path, level traversal'],
        ['DFS', 'O(V + E)', 'O(V)', 'Path finding, topological sort']
    ]
    
    formatter.display_table(
        "Algorithm Complexity Overview",
        columns,
        rows,
        BoxStyle.CONTENT
    )
    
    time.sleep(1)
    
    # Test 4: Code Display
    print("\n" + "="*70)
    print("TEST 4: SYNTAX-HIGHLIGHTED CODE")
    print("="*70)
    
    code_example = """def quicksort(arr):
    '''Implementation of QuickSort algorithm'''
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

# Example usage
numbers = [3, 6, 8, 10, 1, 2, 1]
sorted_numbers = quicksort(numbers)
print(f"Sorted: {sorted_numbers}")"""
    
    formatter.display_code(
        code_example,
        title="QuickSort Implementation",
        language="python"
    )
    
    time.sleep(1)
    
    # Test 5: Tree Structure
    print("\n" + "="*70)
    print("TEST 5: TREE STRUCTURE")
    print("="*70)
    
    curriculum_tree = {
        "Fundamentals": {
            "Big O Notation": "Understanding time complexity",
            "Arrays": "Basic data structure",
            "Linked Lists": "Dynamic data structure"
        },
        "Sorting Algorithms": {
            "Bubble Sort": "O(n²) - Simple comparison",
            "Quick Sort": "O(n log n) - Divide & conquer",
            "Merge Sort": "O(n log n) - Stable sorting"
        },
        "Advanced Topics": {
            "Dynamic Programming": "Optimization technique",
            "Graph Algorithms": "Network problems",
            "Machine Learning": "AI applications"
        }
    }
    
    formatter.display_tree(
        "Curriculum Structure",
        curriculum_tree
    )
    
    time.sleep(1)
    
    # Test 6: Progress Bar
    print("\n" + "="*70)
    print("TEST 6: PROGRESS INDICATORS")
    print("="*70)
    
    if formatter.console:
        with formatter.display_progress("Processing algorithms", 100) as progress:
            task = progress.add_task("Processing algorithms", total=100)
            for i in range(100):
                progress.update(task, advance=1)
                time.sleep(0.01)
    
    # Test 7: Status Messages
    print("\n" + "="*70)
    print("TEST 7: STATUS MESSAGES")
    print("="*70)
    
    formatter.success("✨ Successfully loaded curriculum data!")
    time.sleep(0.5)
    formatter.info("ℹ️ 15 lessons available in current module")
    time.sleep(0.5)
    formatter.warning("⚠️ Some features require cloud integration")
    time.sleep(0.5)
    formatter.error("❌ Failed to connect to cloud services (running in offline mode)")
    
    # Test 8: Gradient Text
    print("\n" + "="*70)
    print("TEST 8: GRADIENT TEXT EFFECTS")
    print("="*70)
    
    if formatter.console:
        gradient_text = formatter.create_gradient_text(
            "Welcome to the Beautiful CLI Experience!"
        )
        formatter.console.print(gradient_text)
    
    # Test 9: Multiple Box Styles
    print("\n" + "="*70)
    print("TEST 9: DIFFERENT BOX STYLES")
    print("="*70)
    
    formatter.display_panel(
        "This uses DOUBLE_EDGE box style for headers",
        title="Header Style",
        style=BoxStyle.HEADER
    )
    
    time.sleep(0.5)
    
    formatter.display_panel(
        "This uses ROUNDED box style for content",
        title="Content Style",
        style=BoxStyle.CONTENT
    )
    
    time.sleep(0.5)
    
    formatter.display_panel(
        "This uses HEAVY_HEAD box style for emphasis",
        title="Emphasis Style",
        style=BoxStyle.EMPHASIS
    )
    
    # Test 10: Complex Layout
    print("\n" + "="*70)
    print("TEST 10: COMPLEX LAYOUT COMPOSITION")
    print("="*70)
    
    formatter.display_header(
        "🎯 Algorithm Mastery Dashboard",
        "Your Learning Progress",
        BoxStyle.HEADER
    )
    
    stats_columns = [
        {'name': 'Metric', 'style': 'cyan'},
        {'name': 'Value', 'style': 'yellow'},
        {'name': 'Status', 'style': 'green'}
    ]
    
    stats_rows = [
        ['Lessons Completed', '12/20', '🟢 On Track'],
        ['Practice Problems', '45', '⭐ Excellent'],
        ['Quiz Score', '92%', '🏆 Outstanding'],
        ['Time Invested', '15.5 hours', '📈 Consistent']
    ]
    
    formatter.display_table(
        "Learning Statistics",
        stats_columns,
        stats_rows,
        BoxStyle.CONTENT
    )
    
    print("\n" + "="*70)
    print("✅ ALL FORMATTING TESTS COMPLETED SUCCESSFULLY!")
    print("="*70)


def test_fallback_modes():
    """Test fallback modes when Rich is not available"""
    print("\n\n" + "="*70)
    print("TESTING FALLBACK MODES")
    print("="*70)
    
    # Temporarily disable Rich to test fallbacks
    import sys
    original_modules = sys.modules.copy()
    
    # Remove Rich from modules
    for module in list(sys.modules.keys()):
        if 'rich' in module:
            del sys.modules[module]
    
    # Reimport formatter without Rich
    from src.cli_formatter import CLIFormatter
    
    fallback_formatter = CLIFormatter()
    
    print("\nTesting Colorama Fallback:")
    fallback_formatter.display_header(
        "Fallback Mode Test",
        "Using Colorama for colors"
    )
    
    fallback_formatter.success("This uses colorama for green text")
    fallback_formatter.error("This uses colorama for red text")
    fallback_formatter.warning("This uses colorama for yellow text")
    fallback_formatter.info("This uses colorama for cyan text")
    
    # Restore original modules
    sys.modules.update(original_modules)


if __name__ == "__main__":
    print("\n" + "🚀"*35)
    print(" UNIFIED CLI FORMATTER TEST SUITE ".center(70, "="))
    print("🚀"*35)
    
    try:
        # Run main tests
        test_formatting()
        
        # Optionally test fallback modes
        # test_fallback_modes()
        
        print("\n" + "🎉"*35)
        print(" ALL TESTS PASSED! ".center(70, "="))
        print("🎉"*35)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)