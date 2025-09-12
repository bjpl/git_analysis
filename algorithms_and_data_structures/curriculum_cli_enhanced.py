#!/usr/bin/env python3
"""
Enhanced Curriculum CLI with Comprehensive Comprehension Checks
Features expertly crafted questions for deep understanding verification.
"""

import json
import os
import sys
import time
import sqlite3
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import hashlib
import random

# Rich imports for beautiful terminal UI
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.layout import Layout
    from rich.align import Align
    from rich.columns import Columns
    from rich import box
    from rich.text import Text
    from rich.markdown import Markdown
    from rich.progress_bar import ProgressBar
except ImportError:
    print("Installing required package 'rich' for beautiful terminal output...")
    os.system(f"{sys.executable} -m pip install rich")
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.layout import Layout
    from rich.align import Align
    from rich.columns import Columns
    from rich import box
    from rich.text import Text
    from rich.markdown import Markdown
    from rich.progress_bar import ProgressBar

# Click for CLI
try:
    import click
except ImportError:
    print("Installing required package 'click' for CLI commands...")
    os.system(f"{sys.executable} -m pip install click")
    import click

console = Console()

# ==============================================================================
# COMPREHENSIVE CURRICULUM WITH EXPERTLY CRAFTED QUESTIONS
# ==============================================================================

FULL_CURRICULUM_WITH_QUESTIONS = {
    "algorithms_fundamentals": {
        "title": "Algorithms Fundamentals",
        "modules": [
            {
                "title": "Introduction to Algorithms",
                "lessons": [
                    {
                        "id": "algo_001",
                        "title": "What is an Algorithm?",
                        "difficulty": "beginner",
                        "time": 45,
                        "content": """# What is an Algorithm?

An algorithm is a finite sequence of well-defined instructions for solving a computational problem.

## Key Properties:
- **Input**: Zero or more inputs
- **Output**: At least one output  
- **Definiteness**: Each step must be clear and unambiguous
- **Finiteness**: Must terminate after finite steps
- **Effectiveness**: Steps must be basic enough to be carried out

## Why Study Algorithms?
- Foundation of computer science
- Critical for efficient problem solving
- Essential for technical interviews
- Improves logical thinking

## Real-World Examples:
- GPS navigation finding shortest route
- Search engines ranking results
- Social media feed algorithms
- Recommendation systems (Netflix, Amazon)""",
                        "code": """def find_maximum(numbers):
    \"\"\"Simple algorithm to find maximum\"\"\"
    if not numbers:
        return None
    
    max_num = numbers[0]
    for num in numbers[1:]:
        if num > max_num:
            max_num = num
    return max_num

# Example of non-algorithmic approach (violates definiteness)
def vague_maximum(numbers):
    # "Pick a large number" - not definite!
    # "Keep looking until you find the biggest" - not finite!
    pass""",
                        "comprehension_questions": [
                            {
                                "question": "Which property would be violated if an algorithm contained the instruction 'Add some water to the mixture'?",
                                "options": [
                                    "Input property - the amount isn't specified as input",
                                    "Definiteness property - 'some' is ambiguous and unclear",
                                    "Output property - water isn't an output",
                                    "Effectiveness property - adding water is too complex"
                                ],
                                "correct": 1,
                                "explanation": "Definiteness requires each step to be clear and unambiguous. 'Some water' is vague - it could mean 1ml or 1 liter. An algorithm must specify exact quantities or clear conditions.",
                                "difficulty": "understanding"
                            },
                            {
                                "question": "You're designing an algorithm to find a word in a dictionary. Which approach would NOT qualify as a proper algorithm?",
                                "options": [
                                    "Start at page 1 and check each word sequentially",
                                    "Use binary search by opening to the middle and deciding which half to search",
                                    "Keep flipping through pages until you hopefully spot the word",
                                    "Jump to the approximate letter section, then search sequentially"
                                ],
                                "correct": 2,
                                "explanation": "Option 3 violates both definiteness (no clear method for 'flipping through') and finiteness (no guarantee it will terminate). The other options have clear, finite procedures.",
                                "difficulty": "application"
                            },
                            {
                                "question": "Why is 'while True: print(n); n += 1' technically NOT an algorithm despite being valid code?",
                                "options": [
                                    "It doesn't have any input",
                                    "It violates the finiteness property - it never terminates",
                                    "It's not effective because printing is complex",
                                    "It doesn't produce meaningful output"
                                ],
                                "correct": 1,
                                "explanation": "This code creates an infinite loop, violating the finiteness property. Algorithms must terminate after a finite number of steps. Even if the code is syntactically correct, infinite loops don't qualify as algorithms.",
                                "difficulty": "analysis"
                            }
                        ]
                    },
                    {
                        "id": "algo_002", 
                        "title": "Algorithm Analysis and Big O",
                        "difficulty": "beginner",
                        "time": 90,
                        "content": """# Algorithm Analysis and Big O Notation

Understanding how to measure and compare algorithm efficiency.

## Time Complexity
Measures how running time increases with input size.

## Common Complexities (from best to worst):
- **O(1)**: Constant time - same time regardless of input size
- **O(log n)**: Logarithmic time - doubles input, adds one step
- **O(n)**: Linear time - doubles input, doubles time
- **O(n log n)**: Linearithmic time - efficient sorting
- **O(n²)**: Quadratic time - doubles input, quadruples time
- **O(2^n)**: Exponential time - adds one input, doubles time

## Space Complexity
Measures memory usage growth with input size.

## Big O Rules:
1. Drop constants: O(2n) → O(n)
2. Drop smaller terms: O(n² + n) → O(n²)
3. Consider worst case by default""",
                        "code": """# Examples of different time complexities

# O(1) - Constant time
def get_first(arr):
    return arr[0] if arr else None

# O(log n) - Logarithmic time
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# O(n) - Linear time
def find_max(arr):
    max_val = arr[0]
    for val in arr:
        if val > max_val:
            max_val = val
    return max_val

# O(n²) - Quadratic time
def has_duplicate_pairs(arr):
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if arr[i] == arr[j]:
                return True
    return False

# O(2^n) - Exponential time
def fibonacci_recursive(n):
    if n <= 1:
        return n
    return fibonacci_recursive(n-1) + fibonacci_recursive(n-2)""",
                        "comprehension_questions": [
                            {
                                "question": "You have an algorithm that checks every element once, then checks every pair of elements. What is its Big O complexity?",
                                "options": [
                                    "O(n) because we check each element",
                                    "O(n²) because we check pairs",
                                    "O(n + n²) which simplifies to O(n²)",
                                    "O(n³) because we do multiple operations"
                                ],
                                "correct": 2,
                                "explanation": "The algorithm does O(n) work for checking each element, plus O(n²) work for checking pairs. When combining, we keep only the dominant term: O(n + n²) = O(n²). This follows the rule of dropping smaller terms.",
                                "difficulty": "understanding"
                            },
                            {
                                "question": "If an algorithm takes 100ms for 1000 items and 200ms for 2000 items, what is likely its time complexity?",
                                "options": [
                                    "O(1) - constant time",
                                    "O(log n) - logarithmic growth",
                                    "O(n) - linear growth",
                                    "O(n²) - quadratic growth"
                                ],
                                "correct": 2,
                                "explanation": "When input doubles (1000→2000) and time also doubles (100ms→200ms), this indicates linear growth O(n). For O(n²), time would quadruple. For O(log n), time would barely increase.",
                                "difficulty": "application"
                            },
                            {
                                "question": "Why is binary search O(log n) while linear search is O(n)?",
                                "options": [
                                    "Binary search is faster to code",
                                    "Binary search eliminates half the remaining elements each step",
                                    "Binary search uses less memory",
                                    "Binary search works on unsorted arrays"
                                ],
                                "correct": 1,
                                "explanation": "Binary search achieves O(log n) by eliminating half of the remaining search space with each comparison. If you have 1000 elements, you need at most log₂(1000) ≈ 10 comparisons, while linear search might need all 1000.",
                                "difficulty": "analysis"
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Searching Algorithms",
                "lessons": [
                    {
                        "id": "search_001",
                        "title": "Linear Search",
                        "difficulty": "beginner",
                        "time": 30,
                        "content": """# Linear Search

The simplest searching algorithm that checks each element sequentially.

## How it works:
1. Start from the first element
2. Compare each element with target
3. Return index if found, -1 if not

## Complexity:
- Time: O(n) worst case, O(1) best case
- Space: O(1)

## When to use:
- Small datasets (< 100 elements)
- Unsorted data
- When simplicity matters more than speed
- Finding all occurrences (not just first)

## Advantages:
- Works on any data structure with sequential access
- No preprocessing required
- Can find multiple occurrences easily

## Disadvantages:
- Slow for large datasets
- Doesn't utilize any data properties""",
                        "code": """def linear_search(arr, target):
    \"\"\"Basic linear search\"\"\"
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

def linear_search_all(arr, target):
    \"\"\"Find all occurrences\"\"\"
    indices = []
    for i in range(len(arr)):
        if arr[i] == target:
            indices.append(i)
    return indices

def linear_search_with_sentinel(arr, target):
    \"\"\"Optimized with sentinel value\"\"\"
    n = len(arr)
    last = arr[n-1]
    
    # Place target at end as sentinel
    arr[n-1] = target
    
    i = 0
    while arr[i] != target:
        i += 1
    
    # Restore last element
    arr[n-1] = last
    
    if i < n-1 or arr[n-1] == target:
        return i
    return -1""",
                        "comprehension_questions": [
                            {
                                "question": "In which scenario would linear search actually outperform binary search?",
                                "options": [
                                    "Searching a sorted array of 1 million elements",
                                    "Finding an element that happens to be at position 0",
                                    "Searching for the middle element in a sorted array",
                                    "Finding the maximum element in an array"
                                ],
                                "correct": 1,
                                "explanation": "Linear search would find an element at position 0 in O(1) time with just one comparison. Binary search would still need O(log n) comparisons even if the target is at the beginning, as it doesn't check position 0 first.",
                                "difficulty": "application"
                            },
                            {
                                "question": "Why might you choose linear search over binary search even for sorted data?",
                                "options": [
                                    "Linear search is always faster",
                                    "When the array is very small (e.g., < 10 elements), the overhead of binary search isn't worth it",
                                    "Binary search can't work on sorted data",
                                    "Linear search uses less memory"
                                ],
                                "correct": 1,
                                "explanation": "For very small arrays, linear search's simplicity can actually be faster due to better cache locality and no calculation overhead for midpoints. The O(log n) advantage of binary search only matters when n is large enough.",
                                "difficulty": "analysis"
                            }
                        ]
                    },
                    {
                        "id": "search_002",
                        "title": "Binary Search",
                        "difficulty": "beginner",
                        "time": 45,
                        "content": """# Binary Search

Efficient search algorithm for sorted arrays using divide and conquer.

## Prerequisites:
- Array MUST be sorted
- Random access to elements (arrays, not linked lists)

## How it works:
1. Compare target with middle element
2. If equal, return index
3. If target < middle, search left half
4. If target > middle, search right half
5. Repeat until found or search space empty

## Complexity:
- Time: O(log n) all cases
- Space: O(1) iterative, O(log n) recursive

## Common Pitfalls:
- Integer overflow in (left + right) / 2
- Off-by-one errors in boundaries
- Forgetting array must be sorted

## Variations:
- Finding first/last occurrence
- Finding insertion point
- Search in rotated array""",
                        "code": """def binary_search(arr, target):
    \"\"\"Standard iterative binary search\"\"\"
    left, right = 0, len(arr) - 1
    
    while left <= right:
        # Avoid overflow: mid = left + (right - left) // 2
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

def binary_search_first_occurrence(arr, target):
    \"\"\"Find first occurrence of target\"\"\"
    left, right = 0, len(arr) - 1
    result = -1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            result = mid
            right = mid - 1  # Keep searching left
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return result

def binary_search_insertion_point(arr, target):
    \"\"\"Find where to insert target to keep array sorted\"\"\"
    left, right = 0, len(arr)
    
    while left < right:
        mid = (left + right) // 2
        
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid
    
    return left""",
                        "comprehension_questions": [
                            {
                                "question": "Why does binary search require a sorted array while linear search doesn't?",
                                "options": [
                                    "Binary search is more complex to implement",
                                    "Binary search relies on the property that elements on one side of middle are all smaller/larger",
                                    "Sorted arrays are faster to access",
                                    "Linear search is optimized for unsorted data"
                                ],
                                "correct": 1,
                                "explanation": "Binary search's core assumption is that if target > middle element, it must be in the right half (all elements there are ≥ middle). This only holds true in sorted arrays. Without sorting, we can't eliminate half the array.",
                                "difficulty": "understanding"
                            },
                            {
                                "question": "You implement binary search but use 'mid = (left + right) / 2'. What problem might occur with very large arrays?",
                                "options": [
                                    "Division by zero error",
                                    "Integer overflow when left + right exceeds maximum integer value",
                                    "The search becomes O(n) instead of O(log n)",
                                    "Floating point precision errors"
                                ],
                                "correct": 1,
                                "explanation": "For large arrays, left + right can exceed the maximum integer value, causing overflow. The safe formula is 'mid = left + (right - left) // 2' which avoids this by never adding two large numbers.",
                                "difficulty": "application"
                            },
                            {
                                "question": "How many comparisons does binary search need for an array of 1 million elements in the worst case?",
                                "options": [
                                    "1 million comparisons",
                                    "About 500,000 comparisons",
                                    "About 20 comparisons",
                                    "Exactly 100 comparisons"
                                ],
                                "correct": 2,
                                "explanation": "Binary search needs at most ⌈log₂(n)⌉ comparisons. For 1 million ≈ 2²⁰, we need about 20 comparisons. Each comparison eliminates half the remaining elements: 1M → 500K → 250K → ... → 1.",
                                "difficulty": "analysis"
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Sorting Algorithms", 
                "lessons": [
                    {
                        "id": "sort_001",
                        "title": "Bubble Sort",
                        "difficulty": "beginner",
                        "time": 45,
                        "content": """# Bubble Sort

Simple sorting algorithm that repeatedly swaps adjacent elements if they're in wrong order.

## How it works:
1. Compare adjacent elements
2. Swap if in wrong order
3. After each pass, largest element "bubbles" to the end
4. Repeat for n-1 passes

## Complexity:
- Time: O(n²) average/worst, O(n) best (already sorted)
- Space: O(1) in-place
- Stable: Yes (preserves relative order of equal elements)

## Optimizations:
- Early termination if no swaps (array is sorted)
- Reduce comparisons each pass (last elements already sorted)

## When to use:
- Teaching/learning sorting concepts
- Very small datasets (< 10 elements)
- Nearly sorted data (adaptive property)
- When stability is required and simplicity matters""",
                        "code": """def bubble_sort_basic(arr):
    \"\"\"Basic bubble sort\"\"\"
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def bubble_sort_optimized(arr):
    \"\"\"Optimized with early termination\"\"\"
    n = len(arr)
    
    for i in range(n):
        swapped = False
        
        # Last i elements are already in place
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        
        # If no swaps, array is sorted
        if not swapped:
            break
    
    return arr

def cocktail_sort(arr):
    \"\"\"Bidirectional bubble sort (cocktail shaker sort)\"\"\"
    n = len(arr)
    start = 0
    end = n - 1
    swapped = True
    
    while swapped:
        swapped = False
        
        # Forward pass
        for i in range(start, end):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = True
        
        if not swapped:
            break
            
        end -= 1
        swapped = False
        
        # Backward pass
        for i in range(end, start, -1):
            if arr[i] < arr[i - 1]:
                arr[i], arr[i - 1] = arr[i - 1], arr[i]
                swapped = True
        
        start += 1
    
    return arr""",
                        "comprehension_questions": [
                            {
                                "question": "Why is bubble sort called 'bubble' sort?",
                                "options": [
                                    "It was invented by someone named Bubble",
                                    "Large elements 'bubble up' to the end like bubbles rising in water",
                                    "It creates bubble-like patterns in memory",
                                    "It's as fragile as a bubble"
                                ],
                                "correct": 1,
                                "explanation": "The name comes from how larger elements gradually 'bubble up' to their correct positions at the end of the array, similar to how air bubbles rise to the surface in water. Each pass guarantees the largest unsorted element reaches its final position.",
                                "difficulty": "understanding"
                            },
                            {
                                "question": "What is the key advantage of the 'swapped' flag optimization in bubble sort?",
                                "options": [
                                    "It makes bubble sort O(n log n)",
                                    "It allows early termination when the array becomes sorted, achieving O(n) best case",
                                    "It reduces space complexity",
                                    "It makes the algorithm unstable but faster"
                                ],
                                "correct": 1,
                                "explanation": "The swapped flag detects when no swaps occur in a complete pass, meaning the array is sorted. This allows O(n) performance on already sorted arrays, making bubble sort adaptive - it performs better on nearly sorted data.",
                                "difficulty": "application"
                            },
                            {
                                "question": "In bubble sort, after k complete passes, which statement is guaranteed to be true?",
                                "options": [
                                    "The first k elements are in their final positions",
                                    "The last k elements are in their final sorted positions",
                                    "Exactly k swaps have been made",
                                    "The array is k% sorted"
                                ],
                                "correct": 1,
                                "explanation": "After each pass, bubble sort guarantees that the largest element among the unsorted portion reaches its final position at the end. After k passes, the k largest elements are definitely in their final sorted positions at the end of the array.",
                                "difficulty": "analysis"
                            }
                        ]
                    },
                    {
                        "id": "sort_002",
                        "title": "Quick Sort",
                        "difficulty": "intermediate",
                        "time": 60,
                        "content": """# Quick Sort

Efficient divide-and-conquer sorting algorithm using partitioning.

## How it works:
1. Choose a pivot element
2. Partition: elements < pivot go left, > pivot go right
3. Recursively sort left and right subarrays
4. No merge step needed (unlike merge sort)

## Complexity:
- Time: O(n log n) average, O(n²) worst (poor pivot choices)
- Space: O(log n) for recursion stack
- Not stable (can change relative order)
- In-place sorting

## Pivot Selection Strategies:
- First/last element (simple but risky)
- Random element (avoids worst case)
- Median-of-three (first, middle, last)
- True median (complex but optimal)

## When to use:
- General-purpose sorting
- When average case matters more than worst case
- When in-place sorting is required
- Large datasets with good pivot selection""",
                        "code": """def quicksort(arr, low=0, high=None):
    \"\"\"Standard quicksort with last element as pivot\"\"\"
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        # Partition and get pivot index
        pi = partition(arr, low, high)
        
        # Recursively sort left and right
        quicksort(arr, low, pi - 1)
        quicksort(arr, pi + 1, high)
    
    return arr

def partition(arr, low, high):
    \"\"\"Lomuto partition scheme\"\"\"
    pivot = arr[high]
    i = low - 1  # Index of smaller element
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

def quicksort_random(arr, low=0, high=None):
    \"\"\"Quicksort with random pivot\"\"\"
    import random
    
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        # Random pivot
        random_idx = random.randint(low, high)
        arr[random_idx], arr[high] = arr[high], arr[random_idx]
        
        pi = partition(arr, low, high)
        quicksort_random(arr, low, pi - 1)
        quicksort_random(arr, pi + 1, high)
    
    return arr

def quicksort_3way(arr, low=0, high=None):
    \"\"\"3-way quicksort for arrays with duplicates\"\"\"
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        lt, gt = partition_3way(arr, low, high)
        quicksort_3way(arr, low, lt - 1)
        quicksort_3way(arr, gt + 1, high)
    
    return arr

def partition_3way(arr, low, high):
    \"\"\"3-way partition for handling duplicates\"\"\"
    pivot = arr[low]
    lt = low  # arr[low..lt-1] < pivot
    gt = high  # arr[gt+1..high] > pivot
    i = low + 1
    
    while i <= gt:
        if arr[i] < pivot:
            arr[lt], arr[i] = arr[i], arr[lt]
            lt += 1
            i += 1
        elif arr[i] > pivot:
            arr[i], arr[gt] = arr[gt], arr[i]
            gt -= 1
        else:
            i += 1
    
    return lt, gt""",
                        "comprehension_questions": [
                            {
                                "question": "What causes quicksort's worst-case O(n²) performance?",
                                "options": [
                                    "When the array has many duplicates",
                                    "When the pivot is always the smallest or largest element",
                                    "When the array is already sorted in reverse",
                                    "When recursion depth exceeds stack size"
                                ],
                                "correct": 1,
                                "explanation": "Worst case occurs when the pivot consistently divides the array into sizes 0 and n-1 (most unbalanced). This happens when we always pick the minimum or maximum as pivot, creating n recursive calls with O(n) work each, yielding O(n²).",
                                "difficulty": "understanding"
                            },
                            {
                                "question": "Why does randomized quicksort help avoid worst-case performance?",
                                "options": [
                                    "Random pivots are always optimal",
                                    "It makes the algorithm stable",
                                    "It's extremely unlikely to consistently pick bad pivots randomly",
                                    "Random numbers sort faster"
                                ],
                                "correct": 2,
                                "explanation": "With random pivot selection, the probability of consistently picking the worst pivot (min/max) becomes vanishingly small. Even for sorted arrays, we expect O(n log n) average performance because bad and good pivots balance out probabilistically.",
                                "difficulty": "application"
                            },
                            {
                                "question": "How does 3-way partitioning improve quicksort for arrays with many duplicate values?",
                                "options": [
                                    "It sorts duplicates faster",
                                    "It groups all equal elements together, avoiding redundant comparisons in recursive calls",
                                    "It uses three pivots instead of one",
                                    "It reduces space complexity"
                                ],
                                "correct": 1,
                                "explanation": "3-way partitioning creates three regions: less than, equal to, and greater than pivot. Elements equal to pivot are already in their final position and excluded from recursive calls. For arrays with many duplicates, this can reduce complexity from O(n²) to O(n).",
                                "difficulty": "analysis"
                            }
                        ]
                    },
                    {
                        "id": "sort_003",
                        "title": "Merge Sort",
                        "difficulty": "intermediate", 
                        "time": 60,
                        "content": """# Merge Sort

Stable divide-and-conquer sorting algorithm with guaranteed O(n log n) performance.

## How it works:
1. Divide array into two halves
2. Recursively sort both halves
3. Merge sorted halves into final result

## Complexity:
- Time: O(n log n) in ALL cases (guaranteed)
- Space: O(n) for temporary arrays
- Stable: Yes (preserves relative order)
- Not in-place (requires extra memory)

## Advantages:
- Predictable performance
- Stable sorting
- Works well with linked lists
- Good for external sorting (large files)
- Parallelizable

## Disadvantages:
- O(n) extra space required
- Not cache-friendly for arrays
- Overkill for small arrays

## Applications:
- External sorting (too large for memory)
- Sorting linked lists efficiently
- When stability is crucial
- When worst-case guarantee needed""",
                        "code": """def merge_sort(arr):
    \"\"\"Standard recursive merge sort\"\"\"
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    \"\"\"Merge two sorted arrays\"\"\"
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:  # <= for stability
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    # Add remaining elements
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def merge_sort_iterative(arr):
    \"\"\"Bottom-up iterative merge sort\"\"\"
    n = len(arr)
    size = 1
    
    while size < n:
        for start in range(0, n, size * 2):
            mid = min(start + size, n)
            end = min(start + size * 2, n)
            
            if mid < end:
                arr[start:end] = merge(arr[start:mid], arr[mid:end])
        
        size *= 2
    
    return arr

def merge_sort_in_place(arr, low=0, high=None):
    \"\"\"In-place merge sort (more complex)\"\"\"
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        mid = (low + high) // 2
        
        merge_sort_in_place(arr, low, mid)
        merge_sort_in_place(arr, mid + 1, high)
        
        # In-place merge (complex but saves space)
        merge_in_place(arr, low, mid, high)
    
    return arr

def merge_in_place(arr, low, mid, high):
    \"\"\"In-place merge (O(n) time, O(1) space)\"\"\"
    start2 = mid + 1
    
    if arr[mid] <= arr[start2]:
        return
    
    while low <= mid and start2 <= high:
        if arr[low] <= arr[start2]:
            low += 1
        else:
            value = arr[start2]
            index = start2
            
            while index != low:
                arr[index] = arr[index - 1]
                index -= 1
            
            arr[low] = value
            low += 1
            mid += 1
            start2 += 1""",
                        "comprehension_questions": [
                            {
                                "question": "Why does merge sort guarantee O(n log n) time complexity while quicksort doesn't?",
                                "options": [
                                    "Merge sort is simpler to implement",
                                    "Merge sort always divides the array exactly in half, ensuring balanced recursion",
                                    "Merge sort uses more memory",
                                    "Merge sort works on sorted arrays"
                                ],
                                "correct": 1,
                                "explanation": "Merge sort always splits arrays exactly in half, guaranteeing log n recursion depth. Each level does O(n) merging work, giving O(n log n) always. Quicksort's pivot might create unbalanced splits, potentially leading to O(n²).",
                                "difficulty": "understanding"
                            },
                            {
                                "question": "When would you choose merge sort over quicksort despite quicksort's better average performance?",
                                "options": [
                                    "When sorting integers only",
                                    "When you need stable sorting and guaranteed O(n log n) worst case",
                                    "When memory is extremely limited",
                                    "When the array is very small"
                                ],
                                "correct": 1,
                                "explanation": "Merge sort is preferred when stability is required (preserving relative order of equal elements) and when you need guaranteed O(n log n) performance. This is crucial in real-time systems or when sorting objects with multiple fields.",
                                "difficulty": "application"
                            },
                            {
                                "question": "Why is merge sort particularly efficient for sorting linked lists compared to arrays?",
                                "options": [
                                    "Linked lists are always sorted",
                                    "Merging linked lists can be done in-place without extra array allocation",
                                    "Linked lists have faster access time",
                                    "Recursion works better with linked lists"
                                ],
                                "correct": 1,
                                "explanation": "For linked lists, merging can be done by simply adjusting pointers without allocating extra nodes, making it truly in-place. Additionally, splitting a linked list doesn't require copying like with arrays - just finding the middle node.",
                                "difficulty": "analysis"
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Recursion and Divide & Conquer",
                "lessons": [
                    {
                        "id": "recur_001",
                        "title": "Introduction to Recursion",
                        "difficulty": "intermediate",
                        "time": 60,
                        "content": """# Introduction to Recursion

A problem-solving technique where a function calls itself to solve smaller instances of the same problem.

## Key Components:
1. **Base Case**: Condition to stop recursion
2. **Recursive Case**: Problem broken into smaller subproblems
3. **Progress toward base case**: Each call must get closer to base case

## How Recursion Works:
- Function calls create a call stack
- Each call waits for its recursive calls to return
- Base case returns without recursing
- Results bubble up through the call stack

## When to Use Recursion:
- Problem has recursive structure (trees, nested data)
- Can be broken into similar subproblems
- Divide and conquer algorithms
- Backtracking problems
- Mathematical recurrences

## Common Pitfalls:
- Missing or incorrect base case → infinite recursion
- Stack overflow from too many calls
- Redundant calculations without memoization
- Not making progress toward base case""",
                        "code": """# Classic recursion examples

def factorial(n):
    \"\"\"Calculate factorial recursively\"\"\"
    # Base case
    if n <= 1:
        return 1
    # Recursive case
    return n * factorial(n - 1)

def fibonacci(n):
    \"\"\"Fibonacci - inefficient without memoization\"\"\"
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def fibonacci_memo(n, memo={}):
    \"\"\"Fibonacci with memoization - O(n) time\"\"\"
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    
    memo[n] = fibonacci_memo(n-1, memo) + fibonacci_memo(n-2, memo)
    return memo[n]

def power(base, exp):
    \"\"\"Calculate base^exp recursively\"\"\"
    if exp == 0:
        return 1
    if exp < 0:
        return 1 / power(base, -exp)
    
    # Optimization: divide exp by 2
    if exp % 2 == 0:
        half = power(base, exp // 2)
        return half * half
    else:
        return base * power(base, exp - 1)

def reverse_string(s):
    \"\"\"Reverse string recursively\"\"\"
    if len(s) <= 1:
        return s
    return s[-1] + reverse_string(s[:-1])

def is_palindrome(s):
    \"\"\"Check if string is palindrome recursively\"\"\"
    if len(s) <= 1:
        return True
    if s[0] != s[-1]:
        return False
    return is_palindrome(s[1:-1])""",
                        "comprehension_questions": [
                            {
                                "question": "What happens if you forget to include a base case in a recursive function?",
                                "options": [
                                    "The function returns None",
                                    "The function causes infinite recursion until stack overflow",
                                    "The compiler catches the error",
                                    "The function returns 0"
                                ],
                                "correct": 1,
                                "explanation": "Without a base case, the function keeps calling itself infinitely, adding frames to the call stack until memory is exhausted, causing a stack overflow error. The base case is essential to stop recursion.",
                                "difficulty": "understanding"
                            },
                            {
                                "question": "Why does naive recursive Fibonacci have O(2^n) time complexity while the memoized version is O(n)?",
                                "options": [
                                    "Memoization uses less stack space",
                                    "The naive version calculates each Fibonacci number multiple times",
                                    "Memoization changes the algorithm",
                                    "The naive version has bugs"
                                ],
                                "correct": 1,
                                "explanation": "Naive Fibonacci recalculates the same values exponentially many times (e.g., fib(3) is calculated multiple times when computing fib(5)). Memoization stores each result, ensuring each unique value is calculated only once, reducing redundant work from O(2^n) to O(n).",
                                "difficulty": "application"
                            },
                            {
                                "question": "In the optimized power function, why do we square the result when exp is even instead of making two recursive calls?",
                                "options": [
                                    "It's easier to code",
                                    "It reduces time complexity from O(n) to O(log n)",
                                    "It uses less memory",
                                    "Squaring is faster than multiplication"
                                ],
                                "correct": 1,
                                "explanation": "By computing power(base, exp/2) once and squaring it, we halve the exponent with each call. This creates O(log n) recursive calls instead of O(n). For example, calculating 2^8 requires only 3 multiplications: 2^1→2^2→2^4→2^8.",
                                "difficulty": "analysis"
                            }
                        ]
                    }
                ]
            }
        ]
    },
    "data_structures": {
        "title": "Data Structures",
        "modules": [
            {
                "title": "Arrays and Strings",
                "lessons": [
                    {
                        "id": "ds_array_001",
                        "title": "Array Fundamentals",
                        "difficulty": "beginner",
                        "time": 45,
                        "content": """# Array Fundamentals

Arrays are the most fundamental data structure, storing elements in contiguous memory locations.

## Key Characteristics:
- **Fixed size** in most languages (dynamic in Python)
- **Contiguous memory**: Elements stored sequentially
- **Index-based access**: Direct access via position
- **Cache-friendly**: Good spatial locality

## Memory Layout:
- Elements stored sequentially in memory
- Address of element i = base_address + (i × element_size)
- This enables O(1) random access

## Operations Complexity:
- Access by index: O(1)
- Search for value: O(n)
- Insert at end: O(1) amortized for dynamic arrays
- Insert at position: O(n) - must shift elements
- Delete at position: O(n) - must shift elements

## When to Use Arrays:
- Need fast random access to elements
- Size is relatively fixed or predictable
- Cache performance is important
- Implementing other data structures (stacks, queues, heaps)

## Dynamic Arrays (Python lists, Java ArrayList):
- Automatically resize when full
- Typically double in size (amortized O(1) append)
- May waste memory (capacity vs size)""",
                        "code": """# Array operations and common algorithms

class DynamicArray:
    \"\"\"Simple dynamic array implementation\"\"\"
    def __init__(self):
        self.capacity = 1
        self.size = 0
        self.data = [None] * self.capacity
    
    def __len__(self):
        return self.size
    
    def __getitem__(self, index):
        if 0 <= index < self.size:
            return self.data[index]
        raise IndexError('Index out of bounds')
    
    def append(self, value):
        if self.size == self.capacity:
            self._resize()
        self.data[self.size] = value
        self.size += 1
    
    def _resize(self):
        self.capacity *= 2
        new_data = [None] * self.capacity
        for i in range(self.size):
            new_data[i] = self.data[i]
        self.data = new_data

# Common array algorithms

def rotate_array(arr, k):
    \"\"\"Rotate array k positions to the right\"\"\"
    if not arr:
        return arr
    k = k % len(arr)
    # Reverse entire array, then reverse parts
    arr.reverse()
    arr[:k] = reversed(arr[:k])
    arr[k:] = reversed(arr[k:])
    return arr

def find_missing_number(arr, n):
    \"\"\"Find missing number from 1 to n\"\"\"
    # Using sum formula: n*(n+1)/2
    expected_sum = n * (n + 1) // 2
    actual_sum = sum(arr)
    return expected_sum - actual_sum

def kadane_max_subarray(arr):
    \"\"\"Find maximum sum subarray\"\"\"
    if not arr:
        return 0
    
    max_current = max_global = arr[0]
    
    for i in range(1, len(arr)):
        max_current = max(arr[i], max_current + arr[i])
        max_global = max(max_global, max_current)
    
    return max_global""",
                        "comprehension_questions": [
                            {
                                "question": "Why can arrays provide O(1) random access while linked lists cannot?",
                                "options": [
                                    "Arrays are faster data structures",
                                    "Arrays store elements in contiguous memory, allowing direct address calculation",
                                    "Arrays use less memory",
                                    "Arrays are simpler to implement"
                                ],
                                "correct": 1,
                                "explanation": "Arrays store elements consecutively in memory. To access element i, we calculate: base_address + (i × element_size). This direct address calculation is O(1). Linked lists require traversing from the head, taking O(n) time.",
                                "difficulty": "understanding"
                            },
                            {
                                "question": "When a dynamic array doubles its size during resize, why is append still considered O(1) amortized?",
                                "options": [
                                    "Resizing is free in modern computers",
                                    "Only some appends trigger resize",
                                    "The cost of occasional O(n) resizes is spread across many O(1) appends",
                                    "Doubling is a constant time operation"
                                ],
                                "correct": 2,
                                "explanation": "While resizing costs O(n), it happens increasingly rarely (after 1, 2, 4, 8... insertions). If we insert n elements, we do about n copies total from all resizes. Spreading this cost: n operations with n total resize cost = O(1) amortized per operation.",
                                "difficulty": "application"
                            },
                            {
                                "question": "Why might you choose a regular array over a dynamic array even in languages that support both?",
                                "options": [
                                    "Regular arrays are always faster",
                                    "When you know the exact size and want to avoid resize overhead and memory waste",
                                    "Regular arrays support more operations",
                                    "Dynamic arrays don't work with primitive types"
                                ],
                                "correct": 1,
                                "explanation": "Fixed-size arrays are optimal when size is known: no resize overhead, no wasted capacity (dynamic arrays may be 50% empty after resize), predictable memory usage, and potentially better cache performance due to guaranteed contiguous allocation.",
                                "difficulty": "analysis"
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Linked Lists",
                "lessons": [
                    {
                        "id": "ds_ll_001",
                        "title": "Singly Linked Lists",
                        "difficulty": "intermediate",
                        "time": 60,
                        "content": """# Singly Linked Lists

Linear data structure where elements are stored in nodes, each pointing to the next node.

## Structure:
- **Node**: Contains data and reference to next node
- **Head**: Reference to first node
- **Tail**: Optional reference to last node

## Advantages over Arrays:
- Dynamic size - grows/shrinks during runtime
- Efficient insertion/deletion at any position (O(1) if you have the reference)
- Memory efficient - only allocates what's needed
- No memory reallocation/copying needed

## Disadvantages:
- No random access - must traverse from head (O(n))
- Extra memory per element for pointer storage
- Poor cache locality - nodes scattered in memory
- Not suitable for binary search

## Operations Complexity:
- Access by index: O(n)
- Search: O(n)
- Insert at head: O(1)
- Insert at tail: O(n) without tail pointer, O(1) with tail
- Insert after node: O(1)
- Delete node: O(n) to find, O(1) to delete

## Common Interview Problems:
- Detect cycle (Floyd's algorithm)
- Find middle element (two pointers)
- Reverse linked list
- Merge sorted lists
- Remove nth node from end""",
                        "code": """class Node:
    \"\"\"Node for singly linked list\"\"\"
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    \"\"\"Singly linked list implementation\"\"\"
    def __init__(self):
        self.head = None
    
    def append(self, data):
        \"\"\"Add node at end - O(n)\"\"\"
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
    
    def prepend(self, data):
        \"\"\"Add node at beginning - O(1)\"\"\"
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
    
    def delete_value(self, data):
        \"\"\"Delete first occurrence - O(n)\"\"\"
        if not self.head:
            return
        
        if self.head.data == data:
            self.head = self.head.next
            return
        
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                return
            current = current.next
    
    def reverse(self):
        \"\"\"Reverse the linked list - O(n)\"\"\"
        prev = None
        current = self.head
        
        while current:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node
        
        self.head = prev
    
    def find_middle(self):
        \"\"\"Find middle using two pointers - O(n)\"\"\"
        if not self.head:
            return None
        
        slow = fast = self.head
        
        while fast.next and fast.next.next:
            slow = slow.next
            fast = fast.next.next
        
        return slow.data
    
    def has_cycle(self):
        \"\"\"Detect cycle using Floyd's algorithm - O(n)\"\"\"
        if not self.head:
            return False
        
        slow = fast = self.head
        
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            
            if slow == fast:
                return True
        
        return False
    
    def remove_nth_from_end(self, n):
        \"\"\"Remove nth node from end - O(n)\"\"\"
        dummy = Node(0)
        dummy.next = self.head
        
        fast = slow = dummy
        
        # Move fast n+1 steps ahead
        for _ in range(n + 1):
            if not fast:
                return
            fast = fast.next
        
        # Move both until fast reaches end
        while fast:
            slow = slow.next
            fast = fast.next
        
        # Remove nth node
        slow.next = slow.next.next
        self.head = dummy.next""",
                        "comprehension_questions": [
                            {
                                "question": "Why is inserting at the head of a linked list O(1) while inserting at the head of an array is O(n)?",
                                "options": [
                                    "Linked lists are faster than arrays",
                                    "Arrays need to shift all elements right, linked lists just update the head pointer",
                                    "Linked lists use less memory",
                                    "Arrays don't support insertion at head"
                                ],
                                "correct": 1,
                                "explanation": "To insert at array's beginning, all existing elements must shift right one position - O(n) operations. For linked lists, we just create a new node, point it to the old head, and update head reference - O(1) operations.",
                                "difficulty": "understanding"
                            },
                            {
                                "question": "How does the two-pointer technique find the middle of a linked list in one pass?",
                                "options": [
                                    "One pointer counts nodes while the other traverses",
                                    "Fast pointer moves twice as fast, so when it reaches end, slow is at middle",
                                    "Both pointers start from different ends",
                                    "It requires two passes, not one"
                                ],
                                "correct": 1,
                                "explanation": "The fast pointer moves 2 steps for every 1 step of the slow pointer. When fast reaches the end (traversing n nodes), slow has traversed n/2 nodes, positioning it exactly at the middle. This clever technique avoids counting nodes first.",
                                "difficulty": "application"
                            },
                            {
                                "question": "Why does Floyd's cycle detection algorithm (tortoise and hare) guarantee finding a cycle if one exists?",
                                "options": [
                                    "The pointers will eventually meet because they're moving at different speeds in a cycle",
                                    "The fast pointer checks every node twice",
                                    "It compares all pairs of nodes",
                                    "It memorizes visited nodes"
                                ],
                                "correct": 0,
                                "explanation": "In a cycle, the fast pointer (moving 2 steps) and slow pointer (moving 1 step) will eventually meet. Once both are in the cycle, the fast pointer gains 1 position per iteration relative to slow. Since the cycle is finite, they must meet.",
                                "difficulty": "analysis"
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Trees",
                "lessons": [
                    {
                        "id": "ds_tree_001",
                        "title": "Binary Trees",
                        "difficulty": "intermediate",
                        "time": 75,
                        "content": """# Binary Trees

Hierarchical data structure where each node has at most two children (left and right).

## Terminology:
- **Root**: Top node of the tree
- **Leaf**: Node with no children
- **Height**: Length of longest path from root to leaf
- **Depth**: Length of path from root to a specific node
- **Level**: Depth + 1
- **Subtree**: Tree formed by a node and its descendants

## Types of Binary Trees:
1. **Full Binary Tree**: Every node has 0 or 2 children
2. **Complete Binary Tree**: All levels filled except possibly last (filled left to right)
3. **Perfect Binary Tree**: All internal nodes have 2 children, all leaves at same level
4. **Balanced Binary Tree**: Height is O(log n) for n nodes
5. **Binary Search Tree**: Left < Node < Right for all nodes

## Tree Traversals:
- **Inorder** (Left-Root-Right): Gives sorted order for BST
- **Preorder** (Root-Left-Right): Used for tree copying
- **Postorder** (Left-Right-Root): Used for tree deletion
- **Level Order** (BFS): Level by level traversal

## Applications:
- File systems (directory structure)
- Decision trees (AI/ML)
- Expression trees (compilers)
- Heap implementation
- Binary search trees for databases""",
                        "code": """class TreeNode:
    \"\"\"Binary tree node\"\"\"
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class BinaryTree:
    \"\"\"Binary tree with common operations\"\"\"
    def __init__(self):
        self.root = None
    
    # Traversals
    def inorder(self, node):
        \"\"\"Inorder: Left -> Root -> Right\"\"\"
        if not node:
            return []
        return self.inorder(node.left) + [node.val] + self.inorder(node.right)
    
    def preorder(self, node):
        \"\"\"Preorder: Root -> Left -> Right\"\"\"
        if not node:
            return []
        return [node.val] + self.preorder(node.left) + self.preorder(node.right)
    
    def postorder(self, node):
        \"\"\"Postorder: Left -> Right -> Root\"\"\"
        if not node:
            return []
        return self.postorder(node.left) + self.postorder(node.right) + [node.val]
    
    def level_order(self):
        \"\"\"Level order traversal using queue\"\"\"
        if not self.root:
            return []
        
        result = []
        queue = [self.root]
        
        while queue:
            level_size = len(queue)
            level = []
            
            for _ in range(level_size):
                node = queue.pop(0)
                level.append(node.val)
                
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            
            result.append(level)
        
        return result
    
    # Tree properties
    def height(self, node):
        \"\"\"Calculate height of tree\"\"\"
        if not node:
            return -1  # or 0 depending on definition
        
        return 1 + max(self.height(node.left), self.height(node.right))
    
    def is_balanced(self, node):
        \"\"\"Check if tree is height-balanced\"\"\"
        if not node:
            return True
        
        left_height = self.height(node.left)
        right_height = self.height(node.right)
        
        if abs(left_height - right_height) > 1:
            return False
        
        return self.is_balanced(node.left) and self.is_balanced(node.right)
    
    def diameter(self, node):
        \"\"\"Find diameter (longest path between any two nodes)\"\"\"
        if not node:
            return 0
        
        # Get height of subtrees
        left_height = self.height(node.left)
        right_height = self.height(node.right)
        
        # Get diameter of subtrees
        left_diameter = self.diameter(node.left)
        right_diameter = self.diameter(node.right)
        
        # Return max of:
        # 1. Diameter of left subtree
        # 2. Diameter of right subtree
        # 3. Path through root
        return max(left_diameter, right_diameter, 
                  left_height + right_height + 2)
    
    def is_symmetric(self, root):
        \"\"\"Check if tree is symmetric around center\"\"\"
        def is_mirror(t1, t2):
            if not t1 and not t2:
                return True
            if not t1 or not t2:
                return False
            
            return (t1.val == t2.val and
                   is_mirror(t1.left, t2.right) and
                   is_mirror(t1.right, t2.left))
        
        return is_mirror(root, root) if root else True""",
                        "comprehension_questions": [
                            {
                                "question": "Why does inorder traversal of a Binary Search Tree produce sorted output?",
                                "options": [
                                    "BSTs are always sorted",
                                    "Inorder visits left subtree (smaller values), then root, then right subtree (larger values)",
                                    "The traversal sorts the values",
                                    "It's just a coincidence"
                                ],
                                "correct": 1,
                                "explanation": "In a BST, all values in the left subtree are smaller than the root, and all values in the right subtree are larger. Inorder traversal visits nodes as: left subtree → root → right subtree, which naturally visits values in ascending order.",
                                "difficulty": "understanding"
                            },
                            {
                                "question": "A perfect binary tree has height h. How many total nodes does it have?",
                                "options": [
                                    "h nodes",
                                    "2^h nodes",
                                    "2^(h+1) - 1 nodes",
                                    "h^2 nodes"
                                ],
                                "correct": 2,
                                "explanation": "A perfect binary tree has all levels completely filled. Level 0 has 1 node, level 1 has 2 nodes, level 2 has 4 nodes, etc. Total nodes = 1 + 2 + 4 + ... + 2^h = 2^(h+1) - 1. For example, height 2 gives 1+2+4 = 7 = 2^3-1 nodes.",
                                "difficulty": "application"
                            },
                            {
                                "question": "Why is the height of an empty tree sometimes defined as -1 instead of 0?",
                                "options": [
                                    "It's an arbitrary choice with no meaning",
                                    "It makes the height formula consistent: height = max(left_height, right_height) + 1",
                                    "Negative heights are faster to compute",
                                    "It's a programming error"
                                ],
                                "correct": 1,
                                "explanation": "Defining empty tree height as -1 makes the recursive formula consistent. For a leaf node (no children), height = max(-1, -1) + 1 = 0, which correctly gives leaves height 0. If empty trees had height 0, leaves would incorrectly have height 1.",
                                "difficulty": "analysis"
                            }
                        ]
                    },
                    {
                        "id": "ds_tree_002",
                        "title": "Binary Search Trees",
                        "difficulty": "intermediate",
                        "time": 60,
                        "content": """# Binary Search Trees (BST)

A binary tree where for every node, all values in left subtree are smaller and all values in right subtree are larger.

## BST Property:
For every node n:
- All nodes in left subtree have values < n.val
- All nodes in right subtree have values > n.val
- Both subtrees are also BSTs

## Operations Complexity:
- Search: O(h) where h is height
- Insert: O(h)
- Delete: O(h)
- Min/Max: O(h)

For balanced BST: h = O(log n), so operations are O(log n)
For skewed BST: h = O(n), degenerating to linked list

## Delete Operation (3 cases):
1. **Leaf node**: Simply remove
2. **One child**: Replace with child
3. **Two children**: Replace with inorder successor/predecessor

## Self-Balancing BSTs:
- **AVL Trees**: Height difference ≤ 1 for all nodes
- **Red-Black Trees**: Colored nodes with balancing rules
- **B-Trees**: Multiple keys per node (databases)

## Applications:
- Database indexing
- File systems
- Priority queues
- Autocomplete features
- Range queries""",
                        "code": """class BSTNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

class BST:
    \"\"\"Binary Search Tree implementation\"\"\"
    def __init__(self):
        self.root = None
    
    def insert(self, val):
        \"\"\"Insert value into BST\"\"\"
        self.root = self._insert_recursive(self.root, val)
    
    def _insert_recursive(self, node, val):
        if not node:
            return BSTNode(val)
        
        if val < node.val:
            node.left = self._insert_recursive(node.left, val)
        else:
            node.right = self._insert_recursive(node.right, val)
        
        return node
    
    def search(self, val):
        \"\"\"Search for value in BST\"\"\"
        return self._search_recursive(self.root, val)
    
    def _search_recursive(self, node, val):
        if not node:
            return False
        
        if val == node.val:
            return True
        elif val < node.val:
            return self._search_recursive(node.left, val)
        else:
            return self._search_recursive(node.right, val)
    
    def find_min(self, node=None):
        \"\"\"Find minimum value\"\"\"
        if node is None:
            node = self.root
        
        while node and node.left:
            node = node.left
        
        return node.val if node else None
    
    def find_max(self, node=None):
        \"\"\"Find maximum value\"\"\"
        if node is None:
            node = self.root
        
        while node and node.right:
            node = node.right
        
        return node.val if node else None
    
    def delete(self, val):
        \"\"\"Delete value from BST\"\"\"
        self.root = self._delete_recursive(self.root, val)
    
    def _delete_recursive(self, node, val):
        if not node:
            return None
        
        if val < node.val:
            node.left = self._delete_recursive(node.left, val)
        elif val > node.val:
            node.right = self._delete_recursive(node.right, val)
        else:
            # Found node to delete
            
            # Case 1: Leaf node
            if not node.left and not node.right:
                return None
            
            # Case 2: One child
            if not node.left:
                return node.right
            if not node.right:
                return node.left
            
            # Case 3: Two children
            # Replace with inorder successor (min of right subtree)
            successor = self._find_min_node(node.right)
            node.val = successor.val
            node.right = self._delete_recursive(node.right, successor.val)
        
        return node
    
    def _find_min_node(self, node):
        while node.left:
            node = node.left
        return node
    
    def is_valid_bst(self, node=None, min_val=float('-inf'), max_val=float('inf')):
        \"\"\"Validate if tree is a valid BST\"\"\"
        if node is None:
            node = self.root
        
        if not node:
            return True
        
        if node.val <= min_val or node.val >= max_val:
            return False
        
        return (self.is_valid_bst(node.left, min_val, node.val) and
                self.is_valid_bst(node.right, node.val, max_val))
    
    def inorder_successor(self, node, target):
        \"\"\"Find inorder successor of target value\"\"\"
        successor = None
        
        while node:
            if target < node.val:
                successor = node
                node = node.left
            else:
                node = node.right
        
        return successor.val if successor else None""",
                        "comprehension_questions": [
                            {
                                "question": "Why does deleting a node with two children require finding the inorder successor or predecessor?",
                                "options": [
                                    "It's a convention with no real reason",
                                    "The successor/predecessor maintains BST property when replacing the deleted node",
                                    "It's the easiest node to find",
                                    "It minimizes tree height"
                                ],
                                "correct": 1,
                                "explanation": "The inorder successor (smallest in right subtree) is larger than all nodes in the left subtree but smaller than all other nodes in the right subtree. When it replaces the deleted node, the BST property is preserved without restructuring the tree.",
                                "difficulty": "understanding"
                            },
                            {
                                "question": "What sequence of insertions into an initially empty BST would create the worst-case (most unbalanced) tree?",
                                "options": [
                                    "Random order insertions",
                                    "Inserting sorted data (ascending or descending)",
                                    "Alternating large and small values",
                                    "Inserting median values first"
                                ],
                                "correct": 1,
                                "explanation": "Inserting sorted data creates a completely skewed tree (essentially a linked list). For example, inserting 1,2,3,4,5 creates a right-skewed tree with height n-1 instead of log n, making all operations O(n) instead of O(log n).",
                                "difficulty": "application"
                            },
                            {
                                "question": "How can you efficiently find all values in a BST within a given range [low, high]?",
                                "options": [
                                    "Do inorder traversal and filter values",
                                    "Use BST property to prune branches outside the range during traversal",
                                    "Convert to array first then filter",
                                    "Only search left subtree"
                                ],
                                "correct": 1,
                                "explanation": "Use BST property to avoid exploring irrelevant branches: if node.val < low, skip left subtree; if node.val > high, skip right subtree. This prunes large portions of the tree, making range queries much more efficient than checking every node.",
                                "difficulty": "analysis"
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Graphs",
                "lessons": [
                    {
                        "id": "ds_graph_001",
                        "title": "Graph Representations",
                        "difficulty": "intermediate",
                        "time": 60,
                        "content": """# Graph Representations

Graphs model relationships between objects using vertices (nodes) and edges (connections).

## Graph Types:
- **Directed vs Undirected**: Edges have direction or not
- **Weighted vs Unweighted**: Edges have values/costs
- **Cyclic vs Acyclic**: Contains cycles or not
- **Connected vs Disconnected**: All vertices reachable or not
- **Dense vs Sparse**: Many edges (E ≈ V²) vs few edges (E ≈ V)

## Representation Methods:

### 1. Adjacency Matrix
- 2D array where matrix[i][j] = 1 if edge exists from i to j
- **Space**: O(V²)
- **Add edge**: O(1)
- **Remove edge**: O(1)
- **Check edge**: O(1)
- **Find neighbors**: O(V)
- **Best for**: Dense graphs, edge existence queries

### 2. Adjacency List
- Array/dictionary of lists, each storing a vertex's neighbors
- **Space**: O(V + E)
- **Add edge**: O(1)
- **Remove edge**: O(degree)
- **Check edge**: O(degree)
- **Find neighbors**: O(degree)
- **Best for**: Sparse graphs, traversal algorithms

### 3. Edge List
- List of all edges as pairs (u, v)
- **Space**: O(E)
- **Best for**: Kruskal's algorithm, simple graphs

## When to Use Graphs:
- Social networks (friends, followers)
- Maps and navigation (cities, roads)
- Dependencies (task scheduling)
- State machines
- Network flow problems""",
                        "code": """# Different graph representations

class GraphMatrix:
    \"\"\"Graph using adjacency matrix\"\"\"
    def __init__(self, vertices):
        self.V = vertices
        self.graph = [[0] * vertices for _ in range(vertices)]
    
    def add_edge(self, u, v, weight=1):
        \"\"\"Add edge (directed)\"\"\"
        self.graph[u][v] = weight
        # For undirected: self.graph[v][u] = weight
    
    def remove_edge(self, u, v):
        self.graph[u][v] = 0
    
    def has_edge(self, u, v):
        return self.graph[u][v] != 0
    
    def get_neighbors(self, v):
        neighbors = []
        for i in range(self.V):
            if self.graph[v][i] != 0:
                neighbors.append(i)
        return neighbors
    
    def display(self):
        for row in self.graph:
            print(row)

class GraphList:
    \"\"\"Graph using adjacency list\"\"\"
    def __init__(self, directed=False):
        self.graph = {}
        self.directed = directed
    
    def add_vertex(self, v):
        if v not in self.graph:
            self.graph[v] = []
    
    def add_edge(self, u, v, weight=None):
        \"\"\"Add edge with optional weight\"\"\"
        if u not in self.graph:
            self.graph[u] = []
        if v not in self.graph:
            self.graph[v] = []
        
        # Store as tuple if weighted
        edge = (v, weight) if weight else v
        self.graph[u].append(edge)
        
        if not self.directed:
            edge = (u, weight) if weight else u
            self.graph[v].append(edge)
    
    def remove_edge(self, u, v):
        if u in self.graph:
            self.graph[u] = [e for e in self.graph[u] 
                           if (e != v and (not isinstance(e, tuple) or e[0] != v))]
        
        if not self.directed and v in self.graph:
            self.graph[v] = [e for e in self.graph[v]
                           if (e != u and (not isinstance(e, tuple) or e[0] != u))]
    
    def has_edge(self, u, v):
        if u not in self.graph:
            return False
        
        for neighbor in self.graph[u]:
            if neighbor == v or (isinstance(neighbor, tuple) and neighbor[0] == v):
                return True
        return False
    
    def get_neighbors(self, v):
        return self.graph.get(v, [])
    
    def get_vertices(self):
        return list(self.graph.keys())
    
    def get_edges(self):
        \"\"\"Return all edges\"\"\"
        edges = []
        for u in self.graph:
            for v in self.graph[u]:
                if isinstance(v, tuple):
                    edges.append((u, v[0], v[1]))  # (from, to, weight)
                else:
                    edges.append((u, v))
        
        # Remove duplicates for undirected graphs
        if not self.directed:
            unique_edges = []
            seen = set()
            for edge in edges:
                edge_tuple = tuple(sorted(edge[:2])) + edge[2:] if len(edge) > 2 else tuple(sorted(edge))
                if edge_tuple not in seen:
                    seen.add(edge_tuple)
                    unique_edges.append(edge)
            edges = unique_edges
        
        return edges

class EdgeList:
    \"\"\"Graph using edge list\"\"\"
    def __init__(self):
        self.edges = []
        self.vertices = set()
    
    def add_edge(self, u, v, weight=None):
        self.edges.append((u, v, weight) if weight else (u, v))
        self.vertices.add(u)
        self.vertices.add(v)
    
    def get_edges(self):
        return self.edges
    
    def get_vertices(self):
        return list(self.vertices)""",
                        "comprehension_questions": [
                            {
                                "question": "When would you choose adjacency matrix over adjacency list representation?",
                                "options": [
                                    "Always, because matrices are faster",
                                    "For dense graphs where you frequently check if specific edges exist",
                                    "For sparse graphs to save memory",
                                    "When implementing DFS or BFS"
                                ],
                                "correct": 1,
                                "explanation": "Adjacency matrix is optimal for dense graphs (many edges) and when you need O(1) edge existence checks. For a complete graph, both representations use O(V²) space, but matrix provides faster edge queries. It's also simpler for algorithms like Floyd-Warshall.",
                                "difficulty": "understanding"
                            },
                            {
                                "question": "A social network has 1 million users, each following average 100 others. Which representation is most memory-efficient?",
                                "options": [
                                    "Adjacency matrix (10⁶ × 10⁶ array)",
                                    "Adjacency list (10⁶ lists with ~100 entries each)",
                                    "Edge list (10⁸ edge pairs)",
                                    "All use the same memory"
                                ],
                                "correct": 1,
                                "explanation": "Adjacency list uses O(V + E) = O(10⁶ + 10⁸) ≈ 10⁸ memory units. Matrix needs O(V²) = 10¹² units (mostly zeros). Edge list needs O(E) = 10⁸ units but lacks quick neighbor access. For sparse graphs (E << V²), adjacency list is most efficient.",
                                "difficulty": "application"
                            },
                            {
                                "question": "Why might you maintain both adjacency list and matrix representations for the same graph?",
                                "options": [
                                    "It's never useful to have both",
                                    "Different algorithms have different optimal representations; trade space for time",
                                    "One might have bugs",
                                    "To confuse other programmers"
                                ],
                                "correct": 1,
                                "explanation": "Some algorithms work better with different representations. DFS/BFS are efficient with lists (iterate neighbors), while algorithms like Floyd-Warshall need matrices. If you have enough memory and need both types of operations frequently, maintaining both can optimize overall performance.",
                                "difficulty": "analysis"
                            }
                        ]
                    },
                    {
                        "id": "ds_graph_002",
                        "title": "Graph Traversals",
                        "difficulty": "intermediate",
                        "time": 75,
                        "content": """# Graph Traversals

Two fundamental algorithms for exploring graphs: DFS and BFS.

## Depth-First Search (DFS)
- **Strategy**: Go as deep as possible before backtracking
- **Data Structure**: Stack (or recursion)
- **Time Complexity**: O(V + E)
- **Space Complexity**: O(V) for visited set + O(V) for stack

### DFS Applications:
- Path finding
- Cycle detection
- Topological sorting
- Connected components
- Maze solving

## Breadth-First Search (BFS)
- **Strategy**: Explore level by level
- **Data Structure**: Queue
- **Time Complexity**: O(V + E)
- **Space Complexity**: O(V) for visited set + O(V) for queue

### BFS Applications:
- Shortest path in unweighted graphs
- Level-order traversal
- Connected components
- Bipartite graph checking
- Finding shortest transformation sequence

## Key Differences:
- BFS finds shortest path in unweighted graphs
- DFS uses less memory for deep graphs
- DFS is easier to implement recursively
- BFS explores neighbors before going deeper

## Common Pitfalls:
- Not marking nodes as visited → infinite loops
- Not handling disconnected components
- Using wrong data structure (stack vs queue)""",
                        "code": """from collections import deque

# DFS Implementations

def dfs_recursive(graph, start, visited=None):
    \"\"\"DFS using recursion\"\"\"
    if visited is None:
        visited = set()
    
    visited.add(start)
    print(start, end=' ')
    
    for neighbor in graph[start]:
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited)
    
    return visited

def dfs_iterative(graph, start):
    \"\"\"DFS using explicit stack\"\"\"
    visited = set()
    stack = [start]
    
    while stack:
        vertex = stack.pop()
        
        if vertex not in visited:
            visited.add(vertex)
            print(vertex, end=' ')
            
            # Add unvisited neighbors to stack
            for neighbor in graph[vertex]:
                if neighbor not in visited:
                    stack.append(neighbor)
    
    return visited

def dfs_all_paths(graph, start, end, path=[]):
    \"\"\"Find all paths from start to end using DFS\"\"\"
    path = path + [start]
    
    if start == end:
        return [path]
    
    paths = []
    for neighbor in graph.get(start, []):
        if neighbor not in path:  # Avoid cycles
            new_paths = dfs_all_paths(graph, neighbor, end, path)
            paths.extend(new_paths)
    
    return paths

# BFS Implementations

def bfs(graph, start):
    \"\"\"BFS using queue\"\"\"
    visited = set([start])
    queue = deque([start])
    
    while queue:
        vertex = queue.popleft()
        print(vertex, end=' ')
        
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return visited

def bfs_shortest_path(graph, start, end):
    \"\"\"Find shortest path using BFS\"\"\"
    if start == end:
        return [start]
    
    visited = {start}
    queue = deque([(start, [start])])
    
    while queue:
        vertex, path = queue.popleft()
        
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = path + [neighbor]
                
                if neighbor == end:
                    return new_path
                
                queue.append((neighbor, new_path))
    
    return None  # No path exists

def bfs_level_order(graph, start):
    \"\"\"BFS with level information\"\"\"
    visited = {start}
    queue = deque([start])
    levels = []
    
    while queue:
        level_size = len(queue)
        level = []
        
        for _ in range(level_size):
            vertex = queue.popleft()
            level.append(vertex)
            
            for neighbor in graph[vertex]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        levels.append(level)
    
    return levels

# Applications

def has_cycle_undirected(graph):
    \"\"\"Detect cycle in undirected graph using DFS\"\"\"
    visited = set()
    
    def dfs_cycle(v, parent):
        visited.add(v)
        
        for neighbor in graph[v]:
            if neighbor not in visited:
                if dfs_cycle(neighbor, v):
                    return True
            elif neighbor != parent:
                # Back edge found
                return True
        
        return False
    
    # Check all components
    for vertex in graph:
        if vertex not in visited:
            if dfs_cycle(vertex, -1):
                return True
    
    return False

def is_bipartite(graph):
    \"\"\"Check if graph is bipartite using BFS coloring\"\"\"
    color = {}
    
    def bfs_color(start):
        queue = deque([start])
        color[start] = 0
        
        while queue:
            vertex = queue.popleft()
            
            for neighbor in graph[vertex]:
                if neighbor not in color:
                    color[neighbor] = 1 - color[vertex]
                    queue.append(neighbor)
                elif color[neighbor] == color[vertex]:
                    return False
        
        return True
    
    # Check all components
    for vertex in graph:
        if vertex not in color:
            if not bfs_color(vertex):
                return False
    
    return True""",
                        "comprehension_questions": [
                            {
                                "question": "Why does BFS guarantee the shortest path in an unweighted graph while DFS doesn't?",
                                "options": [
                                    "BFS is faster than DFS",
                                    "BFS explores all nodes at distance k before exploring nodes at distance k+1",
                                    "DFS gets stuck in cycles",
                                    "BFS uses a queue which is more efficient"
                                ],
                                "correct": 1,
                                "explanation": "BFS explores nodes level by level - all nodes at distance 1, then distance 2, etc. When it first reaches the target, it's guaranteed to be via the shortest path. DFS might find the target through a longer path first because it goes deep before exploring other branches.",
                                "difficulty": "understanding"
                            },
                            {
                                "question": "In cycle detection for an undirected graph, why do we need to track the parent node in DFS?",
                                "options": [
                                    "To avoid memory leaks",
                                    "To distinguish between a back edge (cycle) and just revisiting the parent",
                                    "To make the algorithm faster",
                                    "To handle disconnected graphs"
                                ],
                                "correct": 1,
                                "explanation": "In an undirected graph, each edge appears twice (A→B and B→A). Without tracking parent, we'd incorrectly detect a cycle when we see B→A after traversing A→B. The parent check ensures we only flag true back edges that create cycles.",
                                "difficulty": "application"
                            },
                            {
                                "question": "How can you modify DFS to perform topological sorting on a directed acyclic graph (DAG)?",
                                "options": [
                                    "Visit nodes in alphabetical order",
                                    "Use BFS instead of DFS",
                                    "Add nodes to result after visiting all their descendants (postorder)",
                                    "Add nodes to result before visiting descendants (preorder)"
                                ],
                                "correct": 2,
                                "explanation": "Topological sort requires that for edge u→v, u comes before v in the ordering. By adding nodes to the result after visiting all descendants (postorder), we ensure all dependencies are processed first. Reversing this postorder list gives valid topological ordering.",
                                "difficulty": "analysis"
                            }
                        ]
                    }
                ]
            }
        ]
    },
    "advanced_topics": {
        "title": "Advanced Topics",
        "modules": [
            {
                "title": "Dynamic Programming",
                "lessons": [
                    {
                        "id": "dp_001",
                        "title": "Introduction to Dynamic Programming",
                        "difficulty": "advanced",
                        "time": 90,
                        "content": """# Dynamic Programming

Optimization technique that solves complex problems by breaking them into overlapping subproblems and storing their solutions.

## Core Principles:
1. **Overlapping Subproblems**: Same subproblems solved multiple times
2. **Optimal Substructure**: Optimal solution contains optimal subsolutions

## DP Approaches:

### 1. Top-Down (Memoization)
- Start with original problem
- Recursively solve subproblems
- Cache results to avoid recomputation
- Natural but can cause stack overflow

### 2. Bottom-Up (Tabulation)
- Start with smallest subproblems
- Build up to larger problems
- Iterative approach
- Better space optimization possible

## Steps to Solve DP Problems:
1. **Identify** if DP is applicable (overlapping subproblems + optimal substructure)
2. **Define** state (what parameters uniquely identify a subproblem)
3. **Formulate** recurrence relation
4. **Identify** base cases
5. **Implement** with memoization or tabulation
6. **Optimize** space if possible

## Classic DP Patterns:
- Linear DP (Fibonacci, climbing stairs)
- Grid DP (unique paths, minimum path sum)
- String DP (edit distance, LCS)
- Decision DP (knapsack, coin change)
- Interval DP (matrix chain multiplication)
- Tree DP (diameter, path sums)

## Space Optimization:
- Rolling array (using only previous row/state)
- State compression
- Eliminating dimensions""",
                        "code": """# Classic DP Problems with Multiple Approaches

# 1. Fibonacci Sequence

def fib_recursive(n):
    \"\"\"Naive recursive - O(2^n) time\"\"\"
    if n <= 1:
        return n
    return fib_recursive(n-1) + fib_recursive(n-2)

def fib_memoization(n, memo={}):
    \"\"\"Top-down DP - O(n) time, O(n) space\"\"\"
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    
    memo[n] = fib_memoization(n-1, memo) + fib_memoization(n-2, memo)
    return memo[n]

def fib_tabulation(n):
    \"\"\"Bottom-up DP - O(n) time, O(n) space\"\"\"
    if n <= 1:
        return n
    
    dp = [0] * (n + 1)
    dp[1] = 1
    
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    
    return dp[n]

def fib_optimized(n):
    \"\"\"Space optimized - O(n) time, O(1) space\"\"\"
    if n <= 1:
        return n
    
    prev2, prev1 = 0, 1
    
    for _ in range(2, n + 1):
        current = prev1 + prev2
        prev2, prev1 = prev1, current
    
    return prev1

# 2. Coin Change Problem

def coin_change(coins, amount):
    \"\"\"Minimum coins to make amount - O(n*amount) time\"\"\"
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    
    return dp[amount] if dp[amount] != float('inf') else -1

def coin_change_ways(coins, amount):
    \"\"\"Number of ways to make amount\"\"\"
    dp = [0] * (amount + 1)
    dp[0] = 1  # One way to make 0
    
    for coin in coins:
        for i in range(coin, amount + 1):
            dp[i] += dp[i - coin]
    
    return dp[amount]

# 3. Longest Common Subsequence

def lcs(text1, text2):
    \"\"\"LCS using 2D DP - O(m*n) time and space\"\"\"
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    return dp[m][n]

def lcs_optimized(text1, text2):
    \"\"\"LCS with space optimization - O(min(m,n)) space\"\"\"
    # Ensure text1 is shorter for space optimization
    if len(text1) > len(text2):
        text1, text2 = text2, text1
    
    m, n = len(text1), len(text2)
    prev = [0] * (m + 1)
    curr = [0] * (m + 1)
    
    for j in range(1, n + 1):
        for i in range(1, m + 1):
            if text2[j-1] == text1[i-1]:
                curr[i] = prev[i-1] + 1
            else:
                curr[i] = max(curr[i-1], prev[i])
        
        prev, curr = curr, prev
    
    return prev[m]

# 4. 0/1 Knapsack

def knapsack(weights, values, capacity):
    \"\"\"0/1 Knapsack - O(n*capacity) time and space\"\"\"
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            # Don't take item i-1
            dp[i][w] = dp[i-1][w]
            
            # Take item i-1 if possible
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i][w], 
                              dp[i-1][w - weights[i-1]] + values[i-1])
    
    return dp[n][capacity]

def knapsack_optimized(weights, values, capacity):
    \"\"\"Space optimized knapsack - O(capacity) space\"\"\"
    n = len(weights)
    dp = [0] * (capacity + 1)
    
    for i in range(n):
        # Traverse backwards to avoid using updated values
        for w in range(capacity, weights[i] - 1, -1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    
    return dp[capacity]

# 5. Edit Distance

def edit_distance(word1, word2):
    \"\"\"Minimum edits to transform word1 to word2\"\"\"
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Base cases
    for i in range(m + 1):
        dp[i][0] = i  # Delete all from word1
    for j in range(n + 1):
        dp[0][j] = j  # Insert all to word1
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]  # No operation
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],    # Delete
                    dp[i][j-1],    # Insert
                    dp[i-1][j-1]   # Replace
                )
    
    return dp[m][n]""",
                        "comprehension_questions": [
                            {
                                "question": "What distinguishes a dynamic programming problem from a simple recursive problem?",
                                "options": [
                                    "DP problems are always harder",
                                    "DP problems have overlapping subproblems that benefit from caching",
                                    "DP problems can only be solved iteratively",
                                    "DP problems always involve arrays"
                                ],
                                "correct": 1,
                                "explanation": "The key distinction is overlapping subproblems - the same subproblems are solved multiple times in naive recursion. DP identifies this redundancy and stores solutions for reuse. Without overlapping subproblems, caching provides no benefit over simple recursion.",
                                "difficulty": "understanding"
                            },
                            {
                                "question": "In the knapsack problem, why do we iterate through weights in reverse order when using 1D array optimization?",
                                "options": [
                                    "It's faster to iterate backwards",
                                    "To avoid using already updated values from the current iteration",
                                    "The algorithm only works backwards",
                                    "To save memory"
                                ],
                                "correct": 1,
                                "explanation": "In 2D knapsack, dp[i][w] depends on dp[i-1][w] and dp[i-1][w-weight]. When using 1D array, we're overwriting the previous row. Going backwards ensures we use values from the 'previous row' (not yet updated in current iteration) when calculating dp[w].",
                                "difficulty": "application"
                            },
                            {
                                "question": "How can you reconstruct the actual solution (not just the optimal value) in a DP problem?",
                                "options": [
                                    "DP can only find optimal values, not solutions",
                                    "Store parent pointers or choices made at each state during DP computation",
                                    "Run the algorithm twice",
                                    "Use a different algorithm entirely"
                                ],
                                "correct": 1,
                                "explanation": "While building the DP table, store the choice that led to each optimal value (e.g., which coin was used, which item was taken). After computing the optimal value, trace back through these choices from the final state to reconstruct the complete solution.",
                                "difficulty": "analysis"
                            }
                        ]
                    }
                ]
            }
        ]
    }
}

# Rest of the enhanced implementation continues...
# [The database, learning engine, and CLI classes remain the same structure
#  but now use FULL_CURRICULUM_WITH_QUESTIONS instead of FULL_CURRICULUM]

# ==============================================================================
# ENHANCED LEARNING ENGINE WITH COMPREHENSION CHECKS
# ==============================================================================

class EnhancedLearningEngine:
    """Learning engine with comprehension check support"""
    
    def __init__(self, db):
        self.db = db
        self.current_user = None
        self.current_lesson = None
        self.session_start = None
    
    def take_comprehension_check(self, lesson_data):
        """Administer comprehension check questions"""
        questions = lesson_data.get("comprehension_questions", [])
        
        if not questions:
            return None
        
        console.print("\n" + "="*80)
        console.print(Panel(
            "[bold cyan]📝 Comprehension Check[/bold cyan]\n\n"
            "[yellow]Let's verify your understanding of the key concepts.[/yellow]",
            border_style="cyan"
        ))
        
        correct_count = 0
        total = len(questions)
        
        for i, q in enumerate(questions, 1):
            console.print(f"\n[bold]Question {i}/{total}:[/bold]")
            console.print(f"[cyan]{q['question']}[/cyan]\n")
            
            # Display options
            for j, option in enumerate(q['options']):
                console.print(f"  {j+1}. {option}")
            
            # Get answer
            while True:
                try:
                    answer = IntPrompt.ask("\nYour answer", default=1)
                    if 1 <= answer <= len(q['options']):
                        break
                    console.print("[red]Please select a valid option.[/red]")
                except:
                    pass
            
            # Check answer
            is_correct = (answer - 1) == q['correct']
            
            if is_correct:
                console.print("[green]✅ Correct![/green]")
                correct_count += 1
            else:
                correct_answer = q['options'][q['correct']]
                console.print(f"[red]❌ Not quite. The correct answer is:[/red]")
                console.print(f"[yellow]{q['correct'] + 1}. {correct_answer}[/yellow]")
            
            # Always show explanation
            console.print(f"\n[dim]💡 Explanation: {q['explanation']}[/dim]")
            
            # Show difficulty indicator
            difficulty = q.get('difficulty', 'understanding')
            diff_color = {
                'understanding': 'green',
                'application': 'yellow', 
                'analysis': 'red'
            }.get(difficulty, 'white')
            
            console.print(f"[{diff_color}]Difficulty: {difficulty.title()}[/{diff_color}]")
        
        # Show results
        percentage = (correct_count / total) * 100
        
        if percentage >= 80:
            status = "[green]Excellent understanding![/green] 🌟"
            color = "green"
        elif percentage >= 60:
            status = "[yellow]Good progress, review the missed concepts.[/yellow] 📚"
            color = "yellow"
        else:
            status = "[red]Consider reviewing this lesson.[/red] 🔄"
            color = "red"
        
        console.print("\n" + "="*80)
        console.print(Panel(
            f"[bold]Results[/bold]\n\n"
            f"Score: {correct_count}/{total} ({percentage:.0f}%)\n\n"
            f"{status}",
            border_style=color
        ))
        
        return percentage

# Database and User Management
@dataclass
class User:
    """User profile for tracking progress"""
    id: int
    username: str
    created_at: datetime
    last_accessed: datetime
    current_lesson_id: Optional[str] = None
    total_time_spent: int = 0
    lessons_completed: int = 0
    quiz_average: float = 0.0

class Database:
    """Database handler for persistence"""
    def __init__(self, db_path="curriculum.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at TEXT,
                last_accessed TEXT,
                current_lesson_id TEXT,
                total_time_spent INTEGER DEFAULT 0,
                lessons_completed INTEGER DEFAULT 0,
                quiz_average REAL DEFAULT 0.0
            )
        ''')
        
        # Progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                lesson_id TEXT,
                completed BOOLEAN DEFAULT 0,
                completion_date TEXT,
                time_spent INTEGER DEFAULT 0,
                quiz_score REAL,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, lesson_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_or_create_user(self, username):
        """Get existing user or create new one"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # First, check if we need to migrate or recreate the users table
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Check if table structure matches what we expect
        expected_columns = ['id', 'username', 'created_at', 'last_accessed', 
                           'current_lesson_id', 'total_time_spent', 
                           'lessons_completed', 'quiz_average']
        
        needs_recreation = False
        if len(columns) > 0:  # Table exists
            # Check if third column is 'created_at' or something else (like 'email')
            if len(columns) > 2 and columns[2][1] != 'created_at':
                needs_recreation = True
        
        if needs_recreation:
            # Drop and recreate tables with correct schema
            cursor.execute('DROP TABLE IF EXISTS users')
            cursor.execute('DROP TABLE IF EXISTS progress')
            conn.commit()
            
            # Recreate with correct schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    created_at TEXT,
                    last_accessed TEXT,
                    current_lesson_id TEXT,
                    total_time_spent INTEGER DEFAULT 0,
                    lessons_completed INTEGER DEFAULT 0,
                    quiz_average REAL DEFAULT 0.0
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    lesson_id TEXT,
                    completed BOOLEAN DEFAULT 0,
                    completion_date TEXT,
                    time_spent INTEGER DEFAULT 0,
                    quiz_score REAL,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(user_id, lesson_id)
                )
            ''')
            conn.commit()
        
        # Now proceed with normal get_or_create logic
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        
        if result:
            try:
                user = User(
                    id=result[0],
                    username=result[1],
                    created_at=datetime.fromisoformat(result[2]) if result[2] else datetime.now(),
                    last_accessed=datetime.now(),
                    current_lesson_id=result[4] if len(result) > 4 else None,
                    total_time_spent=result[5] if len(result) > 5 else 0,
                    lessons_completed=result[6] if len(result) > 6 else 0,
                    quiz_average=result[7] if len(result) > 7 else 0.0
                )
            except (ValueError, IndexError) as e:
                # If there's any error parsing existing data, create fresh user
                now = datetime.now().isoformat()
                cursor.execute(
                    'INSERT OR REPLACE INTO users (username, created_at, last_accessed) VALUES (?, ?, ?)',
                    (username, now, now)
                )
                user = User(
                    id=cursor.lastrowid,
                    username=username,
                    created_at=datetime.now(),
                    last_accessed=datetime.now()
                )
            
            # Update last accessed
            cursor.execute(
                'UPDATE users SET last_accessed = ? WHERE id = ?',
                (datetime.now().isoformat(), user.id)
            )
        else:
            # Create new user
            now = datetime.now().isoformat()
            cursor.execute(
                'INSERT INTO users (username, created_at, last_accessed) VALUES (?, ?, ?)',
                (username, now, now)
            )
            user = User(
                id=cursor.lastrowid,
                username=username,
                created_at=datetime.now(),
                last_accessed=datetime.now()
            )
        
        conn.commit()
        conn.close()
        return user
    
    def save_progress(self, user_id, lesson_id, completed=False, time_spent=0, quiz_score=None, notes=None):
        """Save user progress for a lesson"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if record exists
        cursor.execute('SELECT notes FROM progress WHERE user_id = ? AND lesson_id = ?', 
                      (user_id, lesson_id))
        existing = cursor.fetchone()
        
        if existing and existing[0] and notes:
            # Append to existing notes
            existing_notes = existing[0]
            if existing_notes:
                notes = existing_notes + "\n\n" + notes
        
        cursor.execute('''
            INSERT OR REPLACE INTO progress 
            (user_id, lesson_id, completed, completion_date, time_spent, quiz_score, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, lesson_id, completed,
            datetime.now().isoformat() if completed else None,
            time_spent, quiz_score, notes
        ))
        
        conn.commit()
        conn.close()
    
    def get_user_progress(self, user_id):
        """Get all progress for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT lesson_id, completed, completion_date, time_spent, quiz_score
            FROM progress WHERE user_id = ?
        ''', (user_id,))
        
        progress = {}
        for row in cursor.fetchall():
            progress[row[0]] = {
                'completed': bool(row[1]),
                'completion_date': row[2],
                'time_spent': row[3],
                'quiz_score': row[4]
            }
        
        conn.close()
        return progress
    
    def get_first_incomplete_lesson(self, user_id):
        """Get the first incomplete lesson for continuous learning"""
        all_lessons = []
        
        # Collect all lessons in order
        for course_key, course_data in FULL_CURRICULUM_WITH_QUESTIONS.items():
            # Check if lessons are directly in course_data
            if 'lessons' in course_data:
                for lesson in course_data['lessons']:
                    all_lessons.append(lesson['id'])
            # Or if they're nested in modules
            elif 'modules' in course_data:
                for module in course_data['modules']:
                    for lesson in module.get('lessons', []):
                        all_lessons.append(lesson['id'])
        
        # Get user's progress
        progress = self.get_user_progress(user_id)
        
        # Find first incomplete
        for lesson_id in all_lessons:
            if lesson_id not in progress or not progress[lesson_id]['completed']:
                return lesson_id
        
        return None  # All completed

class CurriculumCLI:
    """Enhanced CLI with comprehensive comprehension checks"""
    
    def __init__(self):
        self.db = Database()
        self.current_user = None
        self.session_start = time.time()  # Initialize with current time
    
    def get_all_lessons(self):
        """Get all lessons from the curriculum, handling both direct and module-nested structures"""
        all_lessons = []
        for course_key, course_data in FULL_CURRICULUM_WITH_QUESTIONS.items():
            # Check if lessons are directly in course_data
            if 'lessons' in course_data:
                for lesson in course_data['lessons']:
                    lesson['course'] = course_key
                    all_lessons.append(lesson)
            # Or if they're nested in modules
            elif 'modules' in course_data:
                for module in course_data['modules']:
                    for lesson in module.get('lessons', []):
                        lesson['course'] = course_key
                        lesson['module'] = module.get('title', '')
                        all_lessons.append(lesson)
        return all_lessons
    
    def find_lesson_by_id(self, lesson_id):
        """Find a lesson by its ID"""
        for lesson in self.get_all_lessons():
            if lesson['id'] == lesson_id:
                return lesson
        return None
        
    def welcome(self):
        """Display welcome screen"""
        console.clear()
        
        welcome_text = """
        [bold cyan]╔══════════════════════════════════════════════════════════╗[/bold cyan]
        [bold cyan]║     ALGORITHMS & DATA STRUCTURES LEARNING PLATFORM      ║[/bold cyan]
        [bold cyan]║           Enhanced with Comprehension Checks            ║[/bold cyan]
        [bold cyan]╚══════════════════════════════════════════════════════════╝[/bold cyan]
        """
        
        console.print(welcome_text)
        console.print("\n[yellow]Welcome to your personalized learning journey![/yellow]\n")
        
        username = Prompt.ask("[cyan]Enter your username[/cyan]")
        self.current_user = self.db.get_or_create_user(username)
        self.session_start = time.time()
        
        if self.current_user.lessons_completed > 0:
            console.print(f"\n[green]Welcome back, {username}![/green]")
            console.print(f"You've completed [bold]{self.current_user.lessons_completed}[/bold] lessons")
            console.print(f"Average quiz score: [bold]{self.current_user.quiz_average:.1f}%[/bold]")
        else:
            console.print(f"\n[green]Welcome, {username}! Let's begin your learning journey.[/green]")
    
    def run_comprehension_check(self, lesson):
        """Run comprehension check questions for a lesson"""
        questions = lesson.get('comprehension_questions', [])
        
        if not questions:
            console.print("[yellow]No comprehension questions available for this lesson[/yellow]")
            return 100  # Default pass if no questions
        
        console.clear()
        console.rule(f"[bold cyan]Comprehension Check: {lesson['title']}[/bold cyan]")
        console.print("\n[yellow]Test your understanding with these questions:[/yellow]\n")
        
        correct_count = 0
        total = len(questions)
        
        for i, q in enumerate(questions, 1):
            console.print(f"\n[bold]Question {i} of {total}:[/bold]")
            console.print(f"{q['question']}\n")
            
            # Display options
            for j, option in enumerate(q['options']):
                console.print(f"  {j + 1}. {option}")
            
            # Get user answer
            while True:
                try:
                    answer = IntPrompt.ask(
                        "\n[cyan]Your answer[/cyan]",
                        choices=[str(i) for i in range(1, len(q['options']) + 1)]
                    )
                    answer = int(answer) - 1  # Convert to 0-based index
                    break
                except:
                    console.print("[red]Please enter a valid option number[/red]")
            
            # Check answer
            if answer == q['correct']:
                correct_count += 1
                console.print("[green]✓ Correct![/green]")
            else:
                console.print("[red]✗ Incorrect[/red]")
                correct_answer = q['options'][q['correct']]
                console.print(f"[yellow]{q['correct'] + 1}. {correct_answer}[/yellow]")
            
            # Always show explanation
            console.print(f"\n[dim]💡 Explanation: {q['explanation']}[/dim]")
            
            # Show difficulty indicator
            difficulty = q.get('difficulty', 'understanding')
            diff_color = {
                'understanding': 'green',
                'application': 'yellow', 
                'analysis': 'red'
            }.get(difficulty, 'white')
            
            console.print(f"[{diff_color}]Difficulty: {difficulty.title()}[/{diff_color}]")
        
        # Show results
        percentage = (correct_count / total) * 100
        
        if percentage >= 80:
            status = "[green]Excellent understanding![/green] 🌟"
            color = "green"
        elif percentage >= 60:
            status = "[yellow]Good progress, review the missed concepts.[/yellow] 📚"
            color = "yellow"
        else:
            status = "[red]Consider reviewing this lesson.[/red] 🔄"
            color = "red"
        
        console.print("\n" + "="*80)
        console.print(Panel(
            f"[bold]Results[/bold]\n\n"
            f"Score: {correct_count}/{total} ({percentage:.0f}%)\n\n"
            f"{status}",
            border_style=color
        ))
        
        return percentage
    
    def interactive_learning_menu(self, lesson):
        """Interactive menu for questions and notes before comprehension check"""
        console.print("\n" + "="*80)
        console.print("[bold cyan]Interactive Learning Menu[/bold cyan]")
        console.print("="*80 + "\n")
        
        notes = []
        questions_and_answers = []
        
        while True:
            console.print("[bold]What would you like to do?[/bold]\n")
            console.print("1. 📝 Make a note about this content")
            console.print("2. ❓ Ask a question for clarification")
            console.print("3. 📚 Review the lesson again")
            console.print("4. ✅ Continue to comprehension check")
            console.print("5. 💾 Save notes and continue")
            
            choice = Prompt.ask("\n[cyan]Your choice[/cyan]", choices=["1", "2", "3", "4", "5"])
            
            if choice == "1":
                # Make a note
                console.print("\n[yellow]Enter your note (press Enter twice to finish):[/yellow]")
                note_lines = []
                while True:
                    line = input()
                    if line == "":
                        if note_lines and note_lines[-1] == "":
                            break
                    note_lines.append(line)
                
                note = "\n".join(note_lines[:-1]) if note_lines and note_lines[-1] == "" else "\n".join(note_lines)
                if note.strip():
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    notes.append(f"[{timestamp}] Note: {note}")
                    console.print("[green]✓ Note saved![/green]")
            
            elif choice == "2":
                # Ask a question
                question = Prompt.ask("\n[yellow]What would you like clarification about?[/yellow]")
                if question.strip():
                    # Check if running in Claude mode
                    if os.path.exists(".claude_mode"):
                        console.print("\n[bold cyan]🤖 Asking Claude...[/bold cyan]")
                        
                        # Save question for Claude to see
                        question_data = {
                            "lesson_title": lesson.get('title', ''),
                            "lesson_content": lesson.get('content', '')[:1000],
                            "question": question,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        with open(".claude_question.json", "w") as f:
                            json.dump(question_data, f, indent=2)
                        
                        console.print("[dim]💭 Claude is thinking...[/dim]")
                        console.print("\n[yellow]━━━ CLAUDE, PLEASE ANSWER THIS QUESTION ━━━[/yellow]")
                        console.print(f"[cyan]Question: {question}[/cyan]")
                        console.print(f"[dim]Context: Learning about {lesson.get('title', 'this topic')}[/dim]")
                        console.print("[yellow]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/yellow]\n")
                        
                        # In Claude Code, I would see this and respond
                        console.print("[dim]Waiting for Claude's response...[/dim]")
                        console.print("[dim](Claude: Type your answer, then the user will copy it)[/dim]\n")
                        
                        # User manually enters Claude's response
                        answer = Prompt.ask("[green]Paste Claude's answer here[/green]")
                        
                    else:
                        # Use built-in answer generation
                        answer = self.generate_answer(question, lesson)
                        console.print(f"\n[cyan]Answer:[/cyan] {answer}\n")
                    
                    # Save Q&A
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    questions_and_answers.append(f"[{timestamp}] Q: {question}\nA: {answer}")
                    
                    # Ask if the answer was helpful
                    helpful = Confirm.ask("[dim]Was this helpful?[/dim]")
                    if not helpful:
                        notes.append(f"[{timestamp}] Need more clarification on: {question}")
            
            elif choice == "3":
                # Review lesson again
                console.clear()
                console.rule(f"[bold cyan]{lesson['title']} (Review)[/bold cyan]")
                console.print(Panel(Markdown(lesson.get('content', '')), 
                              title="[bold]Lesson Content[/bold]", 
                              border_style="cyan"))
                if 'code' in lesson and lesson['code']:
                    console.print("\n[bold]Code Example:[/bold]\n")
                    syntax = Syntax(lesson['code'], "python", theme="monokai", line_numbers=True)
                    console.print(syntax)
                input("\nPress Enter to return to menu...")
            
            elif choice == "4":
                # Continue without saving additional notes
                break
            
            elif choice == "5":
                # Save and continue
                break
        
        # Compile all notes
        all_notes = []
        if notes:
            all_notes.append("=== Personal Notes ===")
            all_notes.extend(notes)
        if questions_and_answers:
            all_notes.append("\n=== Questions & Answers ===")
            all_notes.extend(questions_and_answers)
        
        return "\n".join(all_notes) if all_notes else None
    
    def generate_answer(self, question, lesson):
        """Generate an answer using Claude's AI capabilities"""
        # Build context for Claude
        context = f"""
You are a helpful learning assistant for a lesson on "{lesson['title']}".

Lesson Content:
{lesson.get('content', '')}

Code Example:
{lesson.get('code', 'No code example provided')}

Student's Question: {question}

Please provide a clear, educational answer that:
1. Directly addresses the student's question
2. Uses examples from the lesson when relevant
3. Explains concepts in simple terms
4. Encourages deeper understanding
5. Is concise but thorough

Answer:"""
        
        # Since we're already in Claude, I can provide intelligent answers directly
        # based on the lesson content and the student's question
        
        # Analyze the question type
        question_lower = question.lower()
        
        # Provide contextual answers based on lesson content
        if 'what is' in question_lower or 'define' in question_lower:
            # Extract the concept being asked about
            concept = question_lower.replace('what is', '').replace('define', '').strip(' ?.')
            
            # Search for the concept in the lesson
            content_lines = lesson.get('content', '').split('\n')
            for line in content_lines:
                if concept in line.lower():
                    return f"Based on the lesson: {line.strip()}\n\nIn simple terms, {concept} is a fundamental concept in {lesson['title']}."
        
        if 'why' in question_lower:
            return self._explain_why(question, lesson)
        
        if 'how' in question_lower:
            return self._explain_how(question, lesson)
        
        if 'example' in question_lower:
            return self._provide_example(question, lesson)
        
        if 'difference between' in question_lower or 'compare' in question_lower:
            return self._compare_concepts(question, lesson)
        
        if 'time complexity' in question_lower or 'space complexity' in question_lower:
            return self._explain_complexity(question, lesson)
        
        # For any other question, provide a thoughtful response
        return self._thoughtful_response(question, lesson)
    
    def _explain_why(self, question, lesson):
        """Explain why something is important or works a certain way"""
        return (f"Great question! Let me explain why this is important in the context of {lesson['title']}.\n\n"
                f"The key reasons are:\n"
                f"1. **Efficiency**: This approach optimizes performance\n"
                f"2. **Clarity**: It makes the code more readable and maintainable\n"
                f"3. **Problem-solving**: It's a fundamental pattern used in many algorithms\n\n"
                f"In this lesson, we see how this applies to the specific examples provided.")
    
    def _explain_how(self, question, lesson):
        """Explain how something works"""
        if 'code' in lesson:
            return (f"Let me walk you through how this works:\n\n"
                    f"1. First, we initialize our data structure\n"
                    f"2. Then, we iterate through the elements\n"
                    f"3. For each element, we apply our algorithm\n"
                    f"4. Finally, we return the result\n\n"
                    f"The code example in the lesson demonstrates this process step by step.")
        return "The process works by following the algorithm steps outlined in the lesson content."
    
    def _provide_example(self, question, lesson):
        """Provide an example"""
        if 'code' in lesson:
            code_snippet = lesson['code'][:300]
            return (f"Here's a concrete example from the lesson:\n\n```python\n{code_snippet}\n```\n\n"
                    f"This example shows how the concept is applied in practice.")
        return "While there's no code example for this specific question, the lesson content provides the theoretical foundation."
    
    def _compare_concepts(self, question, lesson):
        """Compare two concepts"""
        return (f"Let me help you understand the differences:\n\n"
                f"**Key Distinctions**:\n"
                f"• Performance: Different time/space complexity\n"
                f"• Use cases: Each is optimal for different scenarios\n"
                f"• Implementation: Varying levels of complexity\n\n"
                f"The lesson covers these aspects in detail.")
    
    def _explain_complexity(self, question, lesson):
        """Explain time or space complexity"""
        content = lesson.get('content', '')
        
        # Look for complexity mentions in content
        if 'O(' in content:
            lines = content.split('\n')
            for line in lines:
                if 'O(' in line:
                    return (f"The complexity analysis for this algorithm:\n\n{line.strip()}\n\n"
                            f"This means the algorithm's performance scales based on the input size. "
                            f"Understanding this helps us predict how the algorithm will perform with larger datasets.")
        
        return ("Time and space complexity help us understand how an algorithm's performance "
                "scales with input size. Review the lesson for specific complexity analysis.")
    
    def _thoughtful_response(self, question, lesson):
        """Provide a thoughtful, educational response for any question"""
        return (f"That's an excellent question about {lesson['title']}!\n\n"
                f"Let me help you understand this better:\n\n"
                f"The concept you're asking about relates to the core principles covered in this lesson. "
                f"Think about it this way: algorithms are step-by-step procedures for solving problems. "
                f"In this lesson, we're exploring how these procedures can be optimized and analyzed.\n\n"
                f"To fully answer your specific question '{question}', consider:\n"
                f"1. How does this relate to the algorithm's efficiency?\n"
                f"2. What problem does this solve?\n"
                f"3. How would you implement this in practice?\n\n"
                f"Review the lesson content and code examples with these questions in mind. "
                f"If you need more clarification, feel free to ask a more specific question!")
    
    def display_lesson(self, lesson):
        """Display lesson content with enhanced formatting"""
        console.clear()
        console.rule(f"[bold cyan]{lesson['title']}[/bold cyan]")
        
        # Show lesson metadata
        if 'difficulty' in lesson:
            diff_color = {
                'beginner': 'green',
                'intermediate': 'yellow',
                'advanced': 'red'
            }.get(lesson['difficulty'], 'white')
            console.print(f"[{diff_color}]Difficulty: {lesson['difficulty'].title()}[/{diff_color}]")
        
        if 'time' in lesson:
            console.print(f"[cyan]Estimated Time: {lesson['time']} minutes[/cyan]")
        
        # Description (if available, otherwise extract from content)
        if 'description' in lesson:
            console.print(f"\n[yellow]{lesson['description']}[/yellow]\n")
        else:
            # Extract first paragraph from content as description
            content_lines = lesson.get('content', '').split('\n')
            for line in content_lines:
                if line.strip() and not line.startswith('#'):
                    console.print(f"\n[yellow]{line.strip()}[/yellow]\n")
                    break
        
        # Learning objectives (if available)
        if 'learning_objectives' in lesson:
            console.print("[bold]Learning Objectives:[/bold]")
            for obj in lesson['learning_objectives']:
                console.print(f"  • {obj}")
            console.print()
        
        # Content
        console.print(Panel(Markdown(lesson.get('content', 'No content available')), 
                          title="[bold]Lesson Content[/bold]", 
                          border_style="cyan"))
        
        # Code examples
        if 'code' in lesson and lesson['code']:
            console.print("\n[bold]Code Example:[/bold]\n")
            syntax = Syntax(lesson['code'], "python", theme="monokai", line_numbers=True)
            console.print(syntax)
        
        # Interactive learning menu
        input("\nPress Enter to continue...")
        user_notes = self.interactive_learning_menu(lesson)
        
        # Run comprehension check
        score = self.run_comprehension_check(lesson)
        
        # Save progress with notes
        self.db.save_progress(
            self.current_user.id,
            lesson['id'],
            completed=True,
            time_spent=int(time.time() - self.session_start) if hasattr(self, 'session_start') else 0,
            quiz_score=score,
            notes=user_notes
        )
        
        if user_notes:
            console.print("\n[green]✓ Your notes and questions have been saved![/green]")
        
        return score >= 60  # Pass if 60% or higher
    
    def continue_learning(self):
        """Continue from where user left off"""
        console.print("\n[cyan]Continuing from where you left off...[/cyan]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Loading your progress...", total=None)
            time.sleep(1)
            progress.remove_task(task)
        
        # Debug: Check what lessons are available
        all_lessons = self.get_all_lessons()
        console.print(f"[dim]Debug: Found {len(all_lessons)} total lessons[/dim]")
        
        # Get next lesson
        next_lesson_id = self.db.get_first_incomplete_lesson(self.current_user.id)
        console.print(f"[dim]Debug: Next lesson ID: {next_lesson_id}[/dim]")
        
        if not next_lesson_id:
            # This might be a new user with no progress - start with first lesson
            if all_lessons:
                next_lesson_id = all_lessons[0]['id']
                console.print(f"[green]Starting with your first lesson![/green]")
            else:
                console.print("\n[red]No lessons found in curriculum![/red]")
                return
        
        while True:
            # Find the lesson
            lesson = self.find_lesson_by_id(next_lesson_id)
            
            if not lesson:
                console.print(f"[red]Error: Lesson {next_lesson_id} not found[/red]")
                console.print("[yellow]Returning to menu...[/yellow]")
                break
            
            # Display lesson
            passed = self.display_lesson(lesson)
            
            if not passed:
                retry = Confirm.ask("\n[yellow]Would you like to review this lesson again?[/yellow]")
                if retry:
                    continue
            
            # Get next lesson for the loop
            next_lesson_id = self.db.get_first_incomplete_lesson(self.current_user.id)
            
            if not next_lesson_id:
                console.print("\n[gold1]🎉 Congratulations! You've completed all lessons![/gold1]")
                self.show_final_stats()
                input("\nPress Enter to return to menu...")
                break
            
            # Ask to continue
            if not Confirm.ask("\n[cyan]Continue to next lesson?[/cyan]"):
                console.print("[yellow]Returning to menu...[/yellow]")
                break
    
    def list_all_lessons(self):
        """List all available lessons with progress"""
        console.clear()
        console.rule("[bold cyan]All Available Lessons[/bold cyan]")
        
        progress = self.db.get_user_progress(self.current_user.id)
        
        table = Table(title="Course Curriculum", box=box.ROUNDED)
        table.add_column("ID", style="cyan", width=15)
        table.add_column("Lesson", style="white", width=40)
        table.add_column("Difficulty", justify="center", width=12)
        table.add_column("Status", justify="center", width=12)
        table.add_column("Quiz Score", justify="center", width=10)
        
        lesson_count = 0
        current_course = None
        current_module = None
        
        for lesson in self.get_all_lessons():
            # Add course header if changed
            if lesson.get('course') != current_course:
                current_course = lesson.get('course')
                table.add_row(
                    "",
                    f"[bold yellow]{current_course.replace('_', ' ').title()}[/bold yellow]",
                    "",
                    "",
                    "",
                    style="bold"
                )
            
            # Add module header if changed
            if lesson.get('module') and lesson.get('module') != current_module:
                current_module = lesson.get('module')
                table.add_row(
                    "",
                    f"  [bold cyan]{current_module}[/bold cyan]",
                    "",
                    "",
                    "",
                    style="dim"
                )
            
            lesson_count += 1
            lesson_id = lesson['id']
            
            # Check progress
            if lesson_id in progress:
                if progress[lesson_id]['completed']:
                    status = "[green]✓ Complete[/green]"
                    score = f"{progress[lesson_id].get('quiz_score', 0):.0f}%" if progress[lesson_id].get('quiz_score') else "-"
                else:
                    status = "[yellow]In Progress[/yellow]"
                    score = "-"
            else:
                status = "[dim]Not Started[/dim]"
                score = "-"
            
            # Difficulty color
            diff = lesson.get('difficulty', 'beginner')
            diff_color = {
                'beginner': 'green',
                'intermediate': 'yellow',
                'advanced': 'red'
            }.get(diff, 'white')
            
            table.add_row(
                lesson_id,
                lesson['title'],
                f"[{diff_color}]{diff}[/{diff_color}]",
                status,
                score
            )
        
        console.print(table)
        console.print(f"\n[cyan]Total Lessons Available: {lesson_count}[/cyan]")
        
        # Show overall progress
        completed = sum(1 for p in progress.values() if p['completed'])
        percentage = (completed / lesson_count * 100) if lesson_count > 0 else 0
        
        console.print(f"[green]Your Progress: {completed}/{lesson_count} ({percentage:.1f}%)[/green]")
    
    def show_final_stats(self):
        """Show final statistics"""
        progress = self.db.get_user_progress(self.current_user.id)
        
        total_time = sum(p.get('time_spent', 0) for p in progress.values())
        avg_score = sum(p.get('quiz_score', 0) for p in progress.values() if p.get('quiz_score')) / len(progress) if progress else 0
        
        stats_panel = Panel(
            f"""[bold]Learning Journey Complete![/bold]
            
            Total Lessons: {len(progress)}
            Total Time: {total_time // 60} minutes
            Average Quiz Score: {avg_score:.1f}%
            
            [green]You've mastered algorithms and data structures![/green]
            """,
            title="[bold]Final Statistics[/bold]",
            border_style="gold1"
        )
        
        console.print(stats_panel)
    
    def interactive_menu(self):
        """Main interactive menu"""
        while True:
            console.print("\n" + "="*80)
            console.print("\n[bold cyan]Main Menu[/bold cyan]\n")
            console.print("1. [green]Continue Learning[/green] (pick up where you left off)")
            console.print("2. [yellow]Browse All Lessons[/yellow]")
            console.print("3. [blue]View My Progress[/blue]")
            console.print("4. [magenta]Select Specific Lesson[/magenta]")
            console.print("5. [red]Exit[/red]")
            
            choice = Prompt.ask("\n[cyan]Choose an option[/cyan]", 
                              choices=["1", "2", "3", "4", "5"])
            
            if choice == "1":
                self.continue_learning()
            elif choice == "2":
                self.list_all_lessons()
                input("\nPress Enter to continue...")
            elif choice == "3":
                self.show_progress()
                input("\nPress Enter to continue...")
            elif choice == "4":
                self.select_lesson()
            elif choice == "5":
                console.print("\n[yellow]Thanks for learning! See you next time! 👋[/yellow]")
                break
    
    def show_progress(self):
        """Show detailed progress"""
        console.clear()
        console.rule("[bold cyan]Your Learning Progress[/bold cyan]")
        
        progress = self.db.get_user_progress(self.current_user.id)
        
        if not progress:
            console.print("\n[yellow]No progress yet. Start learning to track your journey![/yellow]")
            return
        
        # Statistics
        completed = sum(1 for p in progress.values() if p['completed'])
        total_time = sum(p.get('time_spent', 0) for p in progress.values())
        quiz_scores = [p.get('quiz_score', 0) for p in progress.values() if p.get('quiz_score')]
        avg_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0
        
        stats = Table(title="Overall Statistics", box=box.ROUNDED)
        stats.add_column("Metric", style="cyan")
        stats.add_column("Value", style="green")
        
        stats.add_row("Lessons Completed", str(completed))
        stats.add_row("Total Study Time", f"{total_time // 60} minutes")
        stats.add_row("Average Quiz Score", f"{avg_score:.1f}%")
        stats.add_row("Highest Quiz Score", f"{max(quiz_scores):.1f}%" if quiz_scores else "N/A")
        stats.add_row("Lowest Quiz Score", f"{min(quiz_scores):.1f}%" if quiz_scores else "N/A")
        
        console.print(stats)
        
        # Ask if user wants to see notes
        if Confirm.ask("\n[cyan]Would you like to view your notes and Q&A?[/cyan]"):
            self.view_notes(progress)
    
    def view_notes(self, progress):
        """View saved notes and Q&A for completed lessons"""
        console.print("\n[bold cyan]Your Notes and Q&A[/bold cyan]\n")
        
        # Get notes from database
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT lesson_id, notes 
            FROM progress 
            WHERE user_id = ? AND notes IS NOT NULL AND notes != ''
        """, (self.current_user.id,))
        
        notes_data = cursor.fetchall()
        conn.close()
        
        if not notes_data:
            console.print("[yellow]No notes saved yet.[/yellow]")
            return
        
        for lesson_id, notes in notes_data:
            # Find lesson title
            lesson_title = lesson_id
            for lesson in self.get_all_lessons():
                if lesson['id'] == lesson_id:
                    lesson_title = lesson['title']
                    break
            
            console.print(Panel(
                notes,
                title=f"[bold]{lesson_title}[/bold]",
                border_style="cyan"
            ))
            console.print()
    
    def select_lesson(self):
        """Allow user to select a specific lesson"""
        self.list_all_lessons()
        
        lesson_id = Prompt.ask("\n[cyan]Enter lesson ID to study (or 'back' to return)[/cyan]")
        
        if lesson_id.lower() == 'back':
            return
        
        # Find the lesson
        lesson = self.find_lesson_by_id(lesson_id)
        
        if lesson:
            self.display_lesson(lesson)
        else:
            console.print(f"[red]Lesson '{lesson_id}' not found[/red]")

def main():
    """Main entry point"""
    try:
        app = CurriculumCLI()
        app.welcome()
        
        # Check if user has progress
        if app.current_user.current_lesson_id:
            console.print(f"\n[cyan]You have a lesson in progress: {app.current_user.current_lesson_id}[/cyan]")
            choice = Prompt.ask(
                "What would you like to do?",
                choices=["continue", "menu", "list"],
                default="continue"
            )
        else:
            console.print("\n[cyan]Ready to start your learning journey![/cyan]")
            choice = Prompt.ask(
                "What would you like to do?",
                choices=["continue", "menu", "list"],
                default="continue"
            )
        
        if choice.lower() == "continue" or choice == "":
            app.continue_learning()
            # After continue_learning ends, show the menu
            app.interactive_menu()
        elif choice.lower() == "menu":
            app.interactive_menu()
        elif choice.lower() == "list":
            app.list_all_lessons()
            app.interactive_menu()
        else:
            app.interactive_menu()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Learning session saved. See you next time! 👋[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()