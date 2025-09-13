#!/usr/bin/env python3
"""
Test script to demonstrate the restored beautiful formatting for lessons
This shows how the Big O lesson should appear with proper frames and formatting
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ui.formatter import TerminalFormatter, Color
from src.ui.lesson_display import LessonDisplay


def main():
    """Demonstrate the beautiful formatting with the Big O lesson"""
    
    # Initialize formatter and display
    formatter = TerminalFormatter()
    display = LessonDisplay(formatter)
    
    # The Big O lesson content
    big_o_content = """## Understanding Big O Notation: The Language of Algorithm Efficiency

You know how when you're looking for a book in your home library, the time it takes depends on how organized it is? That's exactly what Big O notation helps us understand about algorithms - how their performance changes as we scale up the problem size.

### Why This Matters

Imagine you're building an app that starts with 100 users, then grows to 1 million. Big O notation tells you whether your app will still work smoothly or grind to a halt. It's the difference between Instagram loading instantly with billions of photos versus taking minutes to show your feed.

### The Core Concept

Big O notation describes the **worst-case scenario** for how long an algorithm takes relative to the input size. Think of it like this: if you're planning a road trip, you'd want to know the worst traffic conditions you might face, not just the best-case Sunday morning drive.

### Common Time Complexities (From Best to Worst)

#### O(1) - Constant Time: The Holy Grail
Like looking up a word in a dictionary when you know the exact page number. Whether the dictionary has 100 or 100,000 pages, if you know the page number, it takes the same time.

**Real-world example**: Accessing an array element by index
```python
def get_first_element(arr):
    return arr[0]  # Always takes same time, regardless of array size
```

#### O(log n) - Logarithmic Time: The Power of Divide and Conquer
Like finding a word in a dictionary by repeatedly opening to the middle and deciding which half to search. Each decision eliminates half of the remaining pages.

**Real-world example**: Binary search in a sorted phonebook
```python
def binary_search(sorted_arr, target):
    left, right = 0, len(sorted_arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if sorted_arr[mid] == target:
            return mid
        elif sorted_arr[mid] < target:
            left = mid + 1  # Eliminate left half
        else:
            right = mid - 1  # Eliminate right half
    return -1
```

#### O(n) - Linear Time: The Sequential Scanner
Like reading every page of a book to find a specific quote. If the book is twice as long, it takes twice as long.

**Real-world example**: Finding the maximum value in an unsorted list
```python
def find_max(arr):
    if not arr:
        return None
    max_val = arr[0]
    for val in arr:  # Must check every element
        if val > max_val:
            max_val = val
    return max_val
```

#### O(n log n) - Linearithmic Time: The Efficient Sorter
Like organizing a deck of cards using merge sort - divide the deck, sort smaller piles, then merge them back together.

**Real-world example**: Efficient sorting algorithms
```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])  # Divide
    right = merge_sort(arr[mid:])  # Divide
    return merge(left, right)  # Conquer
```

#### O(n²) - Quadratic Time: The Nested Loop Trap
Like comparing every person in a room with every other person for a group photo arrangement. With 10 people, that's 100 comparisons; with 100 people, that's 10,000 comparisons!

**Real-world example**: Bubble sort or finding all pairs
```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - 1 - i):  # Nested loop = n²
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
```

#### O(2ⁿ) - Exponential Time: The Combinatorial Explosion
Like trying every possible combination of pizza toppings. Each new topping doubles the number of possible pizzas.

**Real-world example**: Naive recursive Fibonacci
```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)  # Branches exponentially
```

### Space Complexity: The Memory Dimension

Big O also describes memory usage. Sometimes we trade space for speed:

```python
# O(1) space - uses same variables regardless of input
def sum_array(arr):
    total = 0
    for num in arr:
        total += num
    return total

# O(n) space - creates new array proportional to input
def double_array(arr):
    return [x * 2 for x in arr]
```

### Practical Rules of Thumb

1. **Drop Constants**: O(2n) becomes O(n) - at scale, the multiplier doesn't change the growth pattern
2. **Drop Lower Terms**: O(n² + n) becomes O(n²) - the highest power dominates
3. **Different Variables**: O(a + b) not O(n) when dealing with two different inputs

### Real-World Impact

Here's what these complexities mean for actual running time with 1 million items:
- O(1): 1 operation - instant
- O(log n): ~20 operations - instant
- O(n): 1 million operations - ~1 second
- O(n log n): 20 million operations - ~20 seconds
- O(n²): 1 trillion operations - ~11 days!

### The Key Insight

Big O isn't about precise timing - it's about understanding how algorithms scale. An O(n²) algorithm might be faster than O(n) for small inputs, but will always lose as data grows. Choose your algorithms based on your expected data size!

### Practice Exercises

1. What's the time complexity of searching for a name in an unsorted list?
2. If an algorithm takes 1 second for 1000 items and 4 seconds for 2000 items, what's likely its complexity?
3. Why might you choose an O(n²) algorithm over an O(n log n) algorithm?

Remember: The best algorithm depends on your specific use case. A simple O(n²) sort might be perfect for sorting 10 items, while you'd need O(n log n) for a million items."""

    # Clear screen for fresh display
    import os
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Display with beautiful formatting
    display.display_lesson(big_o_content, title="Big O Notation")
    
    print("\n" + formatter.rule(char="═"))
    print(formatter._colorize("\n✨ This is how your lesson should appear with beautiful formatting!", 
                             Color.BRIGHT_GREEN, Color.BOLD))
    print(formatter._colorize("The frame, colors, and structure make learning more engaging.\n", 
                             Color.BRIGHT_CYAN))


if __name__ == "__main__":
    main()