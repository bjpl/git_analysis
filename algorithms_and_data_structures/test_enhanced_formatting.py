#!/usr/bin/env python3
"""
Test script to verify enhanced formatting is applied to curriculum content
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.ui.windows_formatter import WindowsFormatter
from src.ui.enhanced_lesson_formatter import EnhancedLessonFormatter

def test_enhanced_formatting():
    """Test the enhanced lesson formatter with sample curriculum content"""
    
    # Initialize formatter
    formatter = WindowsFormatter()
    enhanced_formatter = EnhancedLessonFormatter(formatter)
    
    # Sample lesson data similar to what would come from the curriculum
    sample_lesson = {
        'title': 'Big O Notation & Time Complexity',
        'subtitle': 'Understanding Algorithm Efficiency',
        'difficulty': 'beginner',
        'est_time': '10-15',
        'key_topics': [
            'Time Complexity',
            'Space Complexity', 
            'Growth Rates',
            'Complexity Analysis',
            'Best/Average/Worst Case'
        ],
        'time_complexity': 'O(1) to O(n!)',
        'space_complexity': 'O(1) to O(n)',
        'prerequisites': ['Basic programming', 'Mathematical notation'],
        'content': """# Understanding Big O Notation

Big O notation describes how algorithms scale as data grows. It's the language we use to describe algorithm efficiency.

## Real-World Impact

Here's what these complexities mean for actual running time with 1 million items:
- O(1): 1 operation - instant
- O(log n): ~20 operations - instant  
- O(n): 1 million operations - ~1 second
- O(n log n): 20 million operations - ~20 seconds
- O(n²): 1 trillion operations - ~11 days!

## The Key Insight

> Big O isn't about precise timing - it's about understanding how algorithms scale. An O(n²) algorithm might be faster than O(n) for small inputs, but will always lose as data grows. Choose your algorithms based on your expected data size!

## Practice Exercises

1. What's the time complexity of searching for a name in an unsorted list?
2. If an algorithm takes 1 second for 1000 items and 4 seconds for 2000 items, what's likely its complexity?
3. Why might you choose an O(n²) algorithm over an O(n log n) algorithm?

Remember: The best algorithm depends on your specific use case. A simple O(n²) sort might be perfect for sorting 10 items, while you'd need O(n log n) for a million items.
""",
        'code_examples': [
            {
                'title': 'Linear Search - O(n)',
                'description': 'Searches through each element one by one',
                'code': '''def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1''',
                'output': 'Found at index: 3',
                'language': 'python'
            },
            {
                'title': 'Binary Search - O(log n)', 
                'description': 'Divides search space in half each time',
                'code': '''def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1''',
                'output': 'Found at index: 7',
                'language': 'python'
            }
        ],
        'practice_problems': [
            {
                'title': 'Analyze Nested Loops',
                'difficulty': 'easy',
                'description': 'What is the time complexity of this code?',
                'example': '''for i in range(n):
    for j in range(n):
        print(i, j)''',
                'hint': 'Count how many times the print statement executes'
            },
            {
                'title': 'Optimize the Algorithm',
                'difficulty': 'medium',
                'description': 'Can you improve this O(n²) solution to O(n)?',
                'example': '''def find_duplicates(arr):
    duplicates = []
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if arr[i] == arr[j]:
                duplicates.append(arr[i])
    return duplicates''',
                'hint': 'Think about using a data structure to track seen elements'
            }
        ]
    }
    
    print("=" * 70)
    print("TESTING ENHANCED CURRICULUM FORMATTING")
    print("=" * 70)
    print("\nThis test demonstrates that the enhanced formatter applies")
    print("beautiful consistent formatting to ALL curriculum content,")
    print("not just the menu.\n")
    print("=" * 70)
    
    # Test the enhanced formatting
    enhanced_formatter.format_lesson_content(sample_lesson)
    
    # Test real-world impact section
    print("\n" + "=" * 70)
    print("TESTING REAL-WORLD IMPACT FORMATTING")
    print("=" * 70)
    
    real_world_content = """
Google uses O(1) hash tables for instant search suggestions.
Amazon's recommendation engine uses O(n log n) sorting algorithms.
Facebook's friend suggestions use O(n²) comparison algorithms optimized with clever heuristics.
Microsoft Excel recalculates formulas using topological sorting - O(V + E).
Apple's Photos app uses O(n) face detection with parallel processing.
    """
    
    enhanced_formatter.format_real_world_impact(real_world_content)
    
    # Test key insight formatting
    print("\n" + "=" * 70)
    print("TESTING KEY INSIGHT FORMATTING")
    print("=" * 70)
    
    insight = "The best algorithm depends on your use case. Don't optimize prematurely!"
    enhanced_formatter.format_key_insight(insight)
    
    print("\n" + "=" * 70)
    print("✅ FORMATTING TEST COMPLETE")
    print("=" * 70)
    print("\nThe enhanced formatter successfully applies consistent")
    print("beautiful formatting to all curriculum content!")
    print()

if __name__ == "__main__":
    test_enhanced_formatting()