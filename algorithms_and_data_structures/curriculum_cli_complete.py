#!/usr/bin/env python3
"""
Complete Curriculum CLI with Full Content and Progress-Based Learning
A comprehensive learning platform with continuous progression tracking.
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
# COMPLETE CURRICULUM DATA
# ==============================================================================

FULL_CURRICULUM = {
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
- Improves logical thinking""",
                        "code": """def find_maximum(numbers):
    \"\"\"Simple algorithm to find maximum\"\"\"
    if not numbers:
        return None
    
    max_num = numbers[0]
    for num in numbers[1:]:
        if num > max_num:
            max_num = num
    return max_num"""
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

## Common Complexities:
- **O(1)**: Constant time
- **O(log n)**: Logarithmic time
- **O(n)**: Linear time
- **O(n log n)**: Linearithmic time
- **O(n²)**: Quadratic time
- **O(2^n)**: Exponential time

## Space Complexity
Measures memory usage growth with input size.""",
                        "code": """# Examples of different time complexities

# O(1) - Constant time
def get_first(arr):
    return arr[0] if arr else None

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
    return False"""
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
- Time: O(n)
- Space: O(1)

## When to use:
- Small datasets
- Unsorted data
- Simple implementation needed""",
                        "code": """def linear_search(arr, target):
    \"\"\"Linear search implementation\"\"\"
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

# Example usage
numbers = [4, 2, 7, 1, 9, 5]
index = linear_search(numbers, 7)
print(f"Found at index: {index}")  # Output: 2"""
                    },
                    {
                        "id": "search_002",
                        "title": "Binary Search",
                        "difficulty": "beginner",
                        "time": 45,
                        "content": """# Binary Search

Efficient search algorithm for sorted arrays using divide and conquer.

## How it works:
1. Compare target with middle element
2. If equal, return index
3. If less, search left half
4. If greater, search right half
5. Repeat until found or exhausted

## Complexity:
- Time: O(log n)
- Space: O(1) iterative, O(log n) recursive

## Requirements:
- Array must be sorted
- Random access to elements""",
                        "code": """def binary_search(arr, target):
    \"\"\"Binary search - iterative approach\"\"\"
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

def binary_search_recursive(arr, target, left=0, right=None):
    \"\"\"Binary search - recursive approach\"\"\"
    if right is None:
        right = len(arr) - 1
    
    if left > right:
        return -1
    
    mid = (left + right) // 2
    
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, right)
    else:
        return binary_search_recursive(arr, target, left, mid - 1)"""
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
3. Repeat until no swaps needed

## Complexity:
- Time: O(n²) average/worst, O(n) best
- Space: O(1)

## Characteristics:
- Stable sort
- In-place sorting
- Adaptive (performs better on nearly sorted data)""",
                        "code": """def bubble_sort(arr):
    \"\"\"Optimized bubble sort with early termination\"\"\"
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
    
    return arr"""
                    },
                    {
                        "id": "sort_002",
                        "title": "Quick Sort",
                        "difficulty": "intermediate",
                        "time": 60,
                        "content": """# Quick Sort

Efficient divide-and-conquer sorting algorithm.

## How it works:
1. Choose a pivot element
2. Partition array around pivot
3. Recursively sort left and right subarrays

## Complexity:
- Time: O(n log n) average, O(n²) worst
- Space: O(log n) for recursion

## Characteristics:
- In-place sorting
- Not stable
- Generally fastest in practice""",
                        "code": """def quicksort(arr, low=0, high=None):
    \"\"\"Quick sort implementation\"\"\"
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
    \"\"\"Partition helper function\"\"\"
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1"""
                    },
                    {
                        "id": "sort_003",
                        "title": "Merge Sort",
                        "difficulty": "intermediate", 
                        "time": 60,
                        "content": """# Merge Sort

Stable divide-and-conquer sorting algorithm.

## How it works:
1. Divide array into two halves
2. Recursively sort both halves
3. Merge sorted halves

## Complexity:
- Time: O(n log n) all cases
- Space: O(n) for merging

## Characteristics:
- Stable sort
- Predictable performance
- Good for linked lists""",
                        "code": """def merge_sort(arr):
    \"\"\"Merge sort implementation\"\"\"
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
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result"""
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

A problem-solving technique where a function calls itself.

## Key Components:
1. **Base Case**: Condition to stop recursion
2. **Recursive Case**: Problem broken into smaller subproblems

## When to Use:
- Problem has recursive structure
- Can be broken into similar subproblems
- Tree/graph traversal
- Divide and conquer algorithms

## Common Pitfalls:
- Stack overflow
- Redundant calculations
- Missing base case""",
                        "code": """# Classic recursion examples

def factorial(n):
    \"\"\"Calculate factorial recursively\"\"\"
    if n <= 1:  # Base case
        return 1
    return n * factorial(n - 1)  # Recursive case

def fibonacci(n):
    \"\"\"Fibonacci sequence (inefficient)\"\"\"
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def fibonacci_memo(n, memo={}):
    \"\"\"Fibonacci with memoization\"\"\"
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    
    memo[n] = fibonacci_memo(n-1, memo) + fibonacci_memo(n-2, memo)
    return memo[n]"""
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

Arrays are the most fundamental data structure, storing elements in contiguous memory.

## Characteristics:
- **Fixed size** (in most languages)
- **Index-based access**: O(1)
- **Cache-friendly**: Elements stored sequentially
- **Memory efficient**: No overhead for pointers

## Operations:
- Access: O(1)
- Search: O(n)
- Insert: O(n)
- Delete: O(n)

## When to Use:
- Need fast access by index
- Size is known and fixed
- Cache performance matters""",
                        "code": """# Array operations in Python

# Python lists are dynamic arrays
arr = [1, 2, 3, 4, 5]

# Access - O(1)
first = arr[0]
last = arr[-1]

# Insert - O(n) average
arr.insert(2, 10)  # Insert 10 at index 2

# Delete - O(n) average  
arr.pop(3)  # Remove element at index 3

# Search - O(n)
index = arr.index(10) if 10 in arr else -1

# Common array algorithms
def rotate_array(arr, k):
    \"\"\"Rotate array k positions to the right\"\"\"
    k = k % len(arr)
    arr[:] = arr[-k:] + arr[:-k]
    return arr"""
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

Linear data structure where elements are stored in nodes, each pointing to the next.

## Advantages:
- Dynamic size
- Efficient insertion/deletion at any position
- Memory efficient for sparse data

## Disadvantages:
- No random access
- Extra memory for pointers
- Not cache-friendly
- Reverse traversal not possible

## Operations:
- Insert at head: O(1)
- Insert at tail: O(n) without tail pointer
- Delete: O(n)
- Search: O(n)""",
                        "code": """class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
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
    
    def delete(self, data):
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
        
        self.head = prev"""
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

Hierarchical data structure where each node has at most two children.

## Types:
- **Full Binary Tree**: Every node has 0 or 2 children
- **Complete Binary Tree**: All levels filled except possibly last
- **Perfect Binary Tree**: All internal nodes have 2 children
- **Binary Search Tree**: Left < Node < Right

## Traversals:
- **Inorder**: Left → Root → Right (BST gives sorted order)
- **Preorder**: Root → Left → Right
- **Postorder**: Left → Right → Root
- **Level Order**: Level by level (BFS)

## Applications:
- Expression trees
- Decision trees
- File systems
- Priority queues (heaps)""",
                        "code": """class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class BinaryTree:
    def __init__(self):
        self.root = None
    
    def inorder(self, node):
        \"\"\"Inorder traversal - Left, Root, Right\"\"\"
        if not node:
            return []
        
        result = []
        result.extend(self.inorder(node.left))
        result.append(node.val)
        result.extend(self.inorder(node.right))
        return result
    
    def preorder(self, node):
        \"\"\"Preorder traversal - Root, Left, Right\"\"\"
        if not node:
            return []
        
        result = [node.val]
        result.extend(self.preorder(node.left))
        result.extend(self.preorder(node.right))
        return result
    
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
        
        return result"""
                    },
                    {
                        "id": "ds_tree_002",
                        "title": "Binary Search Trees",
                        "difficulty": "intermediate",
                        "time": 60,
                        "content": """# Binary Search Trees (BST)

A binary tree where left subtree < node < right subtree.

## Properties:
- Inorder traversal gives sorted sequence
- Search, insert, delete: O(log n) average, O(n) worst
- No duplicates (typically)

## Operations:
- **Search**: Compare and go left/right
- **Insert**: Find correct position and add
- **Delete**: Three cases (leaf, one child, two children)

## Balance:
- Unbalanced BST degrades to O(n)
- Self-balancing: AVL, Red-Black trees""",
                        "code": """class BSTNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None
    
    def insert(self, val):
        \"\"\"Insert value into BST\"\"\"
        if not self.root:
            self.root = BSTNode(val)
        else:
            self._insert_helper(self.root, val)
    
    def _insert_helper(self, node, val):
        if val < node.val:
            if node.left:
                self._insert_helper(node.left, val)
            else:
                node.left = BSTNode(val)
        else:
            if node.right:
                self._insert_helper(node.right, val)
            else:
                node.right = BSTNode(val)
    
    def search(self, val):
        \"\"\"Search for value in BST\"\"\"
        return self._search_helper(self.root, val)
    
    def _search_helper(self, node, val):
        if not node:
            return False
        
        if val == node.val:
            return True
        elif val < node.val:
            return self._search_helper(node.left, val)
        else:
            return self._search_helper(node.right, val)
    
    def find_min(self, node):
        \"\"\"Find minimum value in subtree\"\"\"
        while node.left:
            node = node.left
        return node.val"""
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

Graphs consist of vertices (nodes) and edges (connections).

## Types:
- **Directed vs Undirected**
- **Weighted vs Unweighted**
- **Cyclic vs Acyclic**
- **Connected vs Disconnected**

## Representations:
1. **Adjacency Matrix**: 2D array
   - Space: O(V²)
   - Edge check: O(1)
   - All neighbors: O(V)

2. **Adjacency List**: Array of lists
   - Space: O(V + E)
   - Edge check: O(degree)
   - All neighbors: O(degree)

## When to Use:
- Matrix: Dense graphs, edge lookups
- List: Sparse graphs, traversals""",
                        "code": """# Graph representations

class GraphMatrix:
    \"\"\"Graph using adjacency matrix\"\"\"
    def __init__(self, vertices):
        self.V = vertices
        self.graph = [[0] * vertices for _ in range(vertices)]
    
    def add_edge(self, u, v, weight=1):
        self.graph[u][v] = weight
        self.graph[v][u] = weight  # For undirected
    
    def has_edge(self, u, v):
        return self.graph[u][v] != 0

class GraphList:
    \"\"\"Graph using adjacency list\"\"\"
    def __init__(self):
        self.graph = {}
    
    def add_vertex(self, v):
        if v not in self.graph:
            self.graph[v] = []
    
    def add_edge(self, u, v):
        if u not in self.graph:
            self.graph[u] = []
        if v not in self.graph:
            self.graph[v] = []
        
        self.graph[u].append(v)
        self.graph[v].append(u)  # For undirected
    
    def get_neighbors(self, v):
        return self.graph.get(v, [])"""
                    },
                    {
                        "id": "ds_graph_002",
                        "title": "Graph Traversals",
                        "difficulty": "intermediate",
                        "time": 75,
                        "content": """# Graph Traversals

Two fundamental ways to explore graphs.

## Depth-First Search (DFS):
- Uses stack (or recursion)
- Goes deep before wide
- Applications: Path finding, cycle detection, topological sort
- Time: O(V + E)
- Space: O(V)

## Breadth-First Search (BFS):
- Uses queue
- Explores level by level
- Applications: Shortest path (unweighted), connected components
- Time: O(V + E)
- Space: O(V)""",
                        "code": """from collections import deque

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
    \"\"\"DFS using stack\"\"\"
    visited = set()
    stack = [start]
    
    while stack:
        vertex = stack.pop()
        
        if vertex not in visited:
            visited.add(vertex)
            print(vertex, end=' ')
            
            # Add unvisited neighbors
            for neighbor in graph[vertex]:
                if neighbor not in visited:
                    stack.append(neighbor)
    
    return visited

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
    
    return visited"""
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

Method for solving complex problems by breaking them into simpler subproblems.

## Key Principles:
1. **Overlapping Subproblems**: Same subproblems solved multiple times
2. **Optimal Substructure**: Optimal solution contains optimal subsolutions

## Approaches:
1. **Top-Down (Memoization)**: Recursive with caching
2. **Bottom-Up (Tabulation)**: Iterative with table

## Steps:
1. Identify if DP applicable
2. Define state and recurrence
3. Implement with memoization or tabulation
4. Optimize space if possible

## Classic Problems:
- Fibonacci, Coin Change
- Longest Common Subsequence
- 0/1 Knapsack
- Edit Distance""",
                        "code": """# DP Examples

def fib_memo(n, memo={}):
    \"\"\"Fibonacci with memoization - O(n) time, O(n) space\"\"\"
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    
    memo[n] = fib_memo(n-1, memo) + fib_memo(n-2, memo)
    return memo[n]

def fib_tabulation(n):
    \"\"\"Fibonacci with tabulation - O(n) time, O(n) space\"\"\"
    if n <= 1:
        return n
    
    dp = [0] * (n + 1)
    dp[1] = 1
    
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    
    return dp[n]

def coin_change(coins, amount):
    \"\"\"Minimum coins needed to make amount\"\"\"
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    
    return dp[amount] if dp[amount] != float('inf') else -1

def longest_common_subsequence(text1, text2):
    \"\"\"Find LCS of two strings\"\"\"
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    return dp[m][n]"""
                    }
                ]
            }
        ]
    }
}

# ==============================================================================
# DATABASE AND MODELS
# ==============================================================================

@dataclass
class Lesson:
    id: str
    title: str
    content: str
    code: str
    difficulty: str
    time: int  # minutes
    module: str = ""
    course: str = ""
    order: int = 0

@dataclass
class UserProgress:
    user_id: str
    lesson_id: str
    status: str  # "not_started", "in_progress", "completed"
    score: float = 0.0
    time_spent: int = 0
    completed_at: Optional[str] = None
    last_accessed: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class User:
    id: str
    username: str
    current_lesson_id: Optional[str] = None
    total_lessons_completed: int = 0
    total_time_spent: int = 0
    current_streak: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())

class DatabaseManager:
    def __init__(self, db_path="curriculum_complete.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        self.load_full_curriculum()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lessons (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT,
                code TEXT,
                difficulty TEXT,
                time INTEGER,
                module TEXT,
                course TEXT,
                lesson_order INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                current_lesson_id TEXT,
                total_lessons_completed INTEGER DEFAULT 0,
                total_time_spent INTEGER DEFAULT 0,
                current_streak INTEGER DEFAULT 0,
                created_at TEXT,
                last_activity TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                user_id TEXT,
                lesson_id TEXT,
                status TEXT DEFAULT 'not_started',
                score REAL DEFAULT 0.0,
                time_spent INTEGER DEFAULT 0,
                completed_at TEXT,
                last_accessed TEXT,
                PRIMARY KEY (user_id, lesson_id)
            )
        ''')
        
        self.conn.commit()
    
    def load_full_curriculum(self):
        """Load all curriculum content"""
        cursor = self.conn.cursor()
        
        # Check if already loaded
        cursor.execute("SELECT COUNT(*) FROM lessons")
        if cursor.fetchone()[0] > 5:  # Already has more than the demo lessons
            return
        
        # Clear existing demo lessons
        cursor.execute("DELETE FROM lessons")
        
        lesson_order = 0
        
        for course_key, course_data in FULL_CURRICULUM.items():
            course_title = course_data["title"]
            
            for module in course_data["modules"]:
                module_title = module["title"]
                
                for lesson_data in module["lessons"]:
                    lesson_order += 1
                    cursor.execute('''
                        INSERT OR REPLACE INTO lessons 
                        (id, title, content, code, difficulty, time, module, course, lesson_order)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        lesson_data["id"],
                        lesson_data["title"],
                        lesson_data["content"],
                        lesson_data.get("code", ""),
                        lesson_data["difficulty"],
                        lesson_data["time"],
                        module_title,
                        course_title,
                        lesson_order
                    ))
        
        self.conn.commit()
    
    def get_user(self, username: str) -> Optional[User]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row:
            return User(
                id=row['id'],
                username=row['username'],
                current_lesson_id=row['current_lesson_id'],
                total_lessons_completed=row['total_lessons_completed'],
                total_time_spent=row['total_time_spent'],
                current_streak=row['current_streak'],
                created_at=row['created_at'],
                last_activity=row['last_activity']
            )
        return None
    
    def create_user(self, username: str) -> User:
        user_id = hashlib.md5(username.encode()).hexdigest()
        user = User(id=user_id, username=username)
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO users (id, username, current_lesson_id, total_lessons_completed,
                             total_time_spent, current_streak, created_at, last_activity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user.id, user.username, user.current_lesson_id, user.total_lessons_completed,
              user.total_time_spent, user.current_streak, user.created_at, user.last_activity))
        self.conn.commit()
        
        return user
    
    def update_user(self, user: User):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE users SET current_lesson_id = ?, total_lessons_completed = ?,
                           total_time_spent = ?, current_streak = ?, last_activity = ?
            WHERE id = ?
        ''', (user.current_lesson_id, user.total_lessons_completed,
              user.total_time_spent, user.current_streak, user.last_activity, user.id))
        self.conn.commit()
    
    def get_all_lessons(self) -> List[Lesson]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM lessons ORDER BY lesson_order')
        lessons = []
        for row in cursor.fetchall():
            lessons.append(Lesson(
                id=row['id'],
                title=row['title'],
                content=row['content'],
                code=row['code'],
                difficulty=row['difficulty'],
                time=row['time'],
                module=row['module'],
                course=row['course'],
                order=row['lesson_order']
            ))
        return lessons
    
    def get_lesson(self, lesson_id: str) -> Optional[Lesson]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM lessons WHERE id = ?', (lesson_id,))
        row = cursor.fetchone()
        if row:
            return Lesson(
                id=row['id'],
                title=row['title'],
                content=row['content'],
                code=row['code'],
                difficulty=row['difficulty'],
                time=row['time'],
                module=row['module'],
                course=row['course'],
                order=row['lesson_order']
            )
        return None
    
    def get_next_lesson(self, current_lesson_id: str) -> Optional[Lesson]:
        """Get the next lesson in sequence"""
        cursor = self.conn.cursor()
        
        # Get current lesson order
        cursor.execute('SELECT lesson_order FROM lessons WHERE id = ?', (current_lesson_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        current_order = row['lesson_order']
        
        # Get next lesson
        cursor.execute('''
            SELECT * FROM lessons 
            WHERE lesson_order > ? 
            ORDER BY lesson_order 
            LIMIT 1
        ''', (current_order,))
        
        row = cursor.fetchone()
        if row:
            return Lesson(
                id=row['id'],
                title=row['title'],
                content=row['content'],
                code=row['code'],
                difficulty=row['difficulty'],
                time=row['time'],
                module=row['module'],
                course=row['course'],
                order=row['lesson_order']
            )
        return None
    
    def get_user_progress(self, user_id: str) -> List[UserProgress]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM progress WHERE user_id = ?', (user_id,))
        progress_list = []
        for row in cursor.fetchall():
            progress_list.append(UserProgress(
                user_id=row['user_id'],
                lesson_id=row['lesson_id'],
                status=row['status'],
                score=row['score'],
                time_spent=row['time_spent'],
                completed_at=row['completed_at'],
                last_accessed=row['last_accessed']
            ))
        return progress_list
    
    def update_progress(self, progress: UserProgress):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO progress 
            (user_id, lesson_id, status, score, time_spent, completed_at, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (progress.user_id, progress.lesson_id, progress.status, progress.score,
              progress.time_spent, progress.completed_at, progress.last_accessed))
        self.conn.commit()
    
    def get_first_incomplete_lesson(self, user_id: str) -> Optional[Lesson]:
        """Get the first lesson that isn't completed"""
        cursor = self.conn.cursor()
        
        # Get all lessons in order
        cursor.execute('''
            SELECT l.* FROM lessons l
            LEFT JOIN progress p ON l.id = p.lesson_id AND p.user_id = ?
            WHERE p.status IS NULL OR p.status != 'completed'
            ORDER BY l.lesson_order
            LIMIT 1
        ''', (user_id,))
        
        row = cursor.fetchone()
        if row:
            return Lesson(
                id=row['id'],
                title=row['title'],
                content=row['content'],
                code=row['code'],
                difficulty=row['difficulty'],
                time=row['time'],
                module=row['module'],
                course=row['course'],
                order=row['lesson_order']
            )
        return None

# ==============================================================================
# LEARNING ENGINE
# ==============================================================================

class ContinuousLearningCLI:
    def __init__(self):
        self.db = DatabaseManager()
        self.current_user = None
        self.current_lesson = None
        self.session_start = None
    
    def login_or_register(self, username: str) -> User:
        """Login or create user"""
        user = self.db.get_user(username)
        
        if user:
            console.print(f"\n[bold green]Welcome back, {username}![/bold green]")
            
            # Update streak
            last_activity = datetime.fromisoformat(user.last_activity)
            today = datetime.now()
            days_diff = (today.date() - last_activity.date()).days
            
            if days_diff == 1:
                user.current_streak += 1
                console.print(f"[yellow]🔥 Streak extended to {user.current_streak} days![/yellow]")
            elif days_diff > 1:
                user.current_streak = 1
                console.print(f"[dim]Streak reset. Starting fresh![/dim]")
            
            user.last_activity = today.isoformat()
            self.db.update_user(user)
        else:
            user = self.db.create_user(username)
            console.print(f"\n[bold green]Welcome to the Learning Platform, {username}![/bold green]")
            console.print("[cyan]Your learning journey begins now![/cyan]")
        
        self.current_user = user
        return user
    
    def continue_learning(self):
        """Continue from where user left off"""
        if not self.current_user:
            return
        
        # Get the next incomplete lesson
        next_lesson = self.db.get_first_incomplete_lesson(self.current_user.id)
        
        if not next_lesson:
            console.print("[green]🎉 Congratulations! You've completed all lessons![/green]")
            self.show_progress()
            return
        
        # Check if user has a current lesson saved
        if self.current_user.current_lesson_id:
            current = self.db.get_lesson(self.current_user.current_lesson_id)
            if current and current.id != next_lesson.id:
                console.print(f"\n[yellow]You were working on: {current.title}[/yellow]")
                if Confirm.ask("Would you like to continue with that lesson?"):
                    next_lesson = current
        
        console.print(f"\n[bold cyan]📚 Continuing with: {next_lesson.title}[/bold cyan]")
        console.print(f"[dim]Course: {next_lesson.course} > {next_lesson.module}[/dim]")
        
        self.start_lesson(next_lesson)
    
    def start_from_beginning(self):
        """Start from the first lesson"""
        lessons = self.db.get_all_lessons()
        if not lessons:
            console.print("[red]No lessons available![/red]")
            return
        
        first_lesson = lessons[0]
        console.print(f"\n[bold cyan]📚 Starting from the beginning![/bold cyan]")
        self.start_lesson(first_lesson)
    
    def start_lesson(self, lesson: Lesson):
        """Display and track lesson"""
        self.current_lesson = lesson
        self.session_start = time.time()
        
        # Update user's current lesson
        self.current_user.current_lesson_id = lesson.id
        self.db.update_user(self.current_user)
        
        # Update or create progress
        progress = UserProgress(
            user_id=self.current_user.id,
            lesson_id=lesson.id,
            status="in_progress"
        )
        self.db.update_progress(progress)
        
        # Display lesson
        console.print("\n" + "="*80)
        console.print(Panel(
            f"[bold cyan]{lesson.title}[/bold cyan]\n\n"
            f"[yellow]⏱️  Estimated time: {lesson.time} minutes[/yellow]\n"
            f"[green]📈 Difficulty: {lesson.difficulty}[/green]\n"
            f"[blue]📚 {lesson.course} > {lesson.module}[/blue]",
            title="📖 Lesson",
            border_style="cyan"
        ))
        
        # Display content
        console.print("\n")
        md = Markdown(lesson.content)
        console.print(md)
        
        # Display code if available
        if lesson.code:
            console.print("\n[bold cyan]💻 Code Example:[/bold cyan]\n")
            syntax = Syntax(lesson.code, "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, border_style="blue"))
        
        # Mark as completed
        if Confirm.ask("\n✅ Mark this lesson as completed?"):
            self.complete_lesson()
    
    def complete_lesson(self):
        """Mark current lesson as completed"""
        if not self.current_lesson or not self.current_user:
            return
        
        # Calculate time spent
        time_spent = int((time.time() - self.session_start) / 60) if self.session_start else 0
        
        # Update progress
        progress = UserProgress(
            user_id=self.current_user.id,
            lesson_id=self.current_lesson.id,
            status="completed",
            score=100.0,
            time_spent=time_spent,
            completed_at=datetime.now().isoformat()
        )
        self.db.update_progress(progress)
        
        # Update user stats
        self.current_user.total_lessons_completed += 1
        self.current_user.total_time_spent += time_spent
        self.db.update_user(self.current_user)
        
        console.print(f"\n[green]✅ Lesson completed! Time spent: {time_spent} minutes[/green]")
        
        # Get next lesson
        next_lesson = self.db.get_next_lesson(self.current_lesson.id)
        if next_lesson:
            console.print(f"\n[cyan]Next lesson: {next_lesson.title}[/cyan]")
            if Confirm.ask("Continue to next lesson?"):
                self.start_lesson(next_lesson)
        else:
            console.print("\n[bold green]🎉 You've completed all available lessons![/bold green]")
    
    def show_progress(self):
        """Display detailed progress"""
        if not self.current_user:
            return
        
        lessons = self.db.get_all_lessons()
        progress_list = self.db.get_user_progress(self.current_user.id)
        progress_map = {p.lesson_id: p for p in progress_list}
        
        # Group by course
        courses = {}
        for lesson in lessons:
            if lesson.course not in courses:
                courses[lesson.course] = []
            courses[lesson.course].append(lesson)
        
        # Calculate overall progress
        total_lessons = len(lessons)
        completed_lessons = sum(1 for p in progress_list if p.status == "completed")
        overall_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        # Display overall stats
        console.print(Panel(
            f"[bold]Overall Progress[/bold]\n\n"
            f"📚 Lessons Completed: {completed_lessons}/{total_lessons} ({overall_progress:.1f}%)\n"
            f"⏱️  Total Study Time: {self.current_user.total_time_spent} minutes\n"
            f"🔥 Current Streak: {self.current_user.current_streak} days\n"
            f"📅 Member Since: {self.current_user.created_at[:10]}",
            title=f"📊 Progress for {self.current_user.username}",
            border_style="green"
        ))
        
        # Display progress by course
        for course_name, course_lessons in courses.items():
            table = Table(title=f"\n{course_name}", box=box.ROUNDED)
            table.add_column("Lesson", style="cyan", width=40)
            table.add_column("Module", style="blue", width=25)
            table.add_column("Status", justify="center", width=12)
            table.add_column("Time", justify="center", width=10)
            
            for lesson in course_lessons:
                progress = progress_map.get(lesson.id)
                
                if progress:
                    status_icon = {
                        "completed": "[green]✅[/green]",
                        "in_progress": "[yellow]🔄[/yellow]",
                        "not_started": "[dim]⭕[/dim]"
                    }.get(progress.status, "[dim]⭕[/dim]")
                    
                    time_str = f"{progress.time_spent}m" if progress.time_spent > 0 else "-"
                else:
                    status_icon = "[dim]⭕[/dim]"
                    time_str = "-"
                
                table.add_row(
                    lesson.title,
                    lesson.module,
                    status_icon,
                    time_str
                )
            
            console.print(table)
        
        # Show progress bar
        console.print(f"\n[bold]Overall Completion:[/bold]")
        progress_bar = ProgressBar(total=total_lessons, completed=completed_lessons)
        console.print(f"[green]{'█' * int(overall_progress / 5)}{'░' * (20 - int(overall_progress / 5))}[/green] {overall_progress:.1f}%")
    
    def list_all_lessons(self):
        """Display all available lessons in a tree structure"""
        lessons = self.db.get_all_lessons()
        
        tree = Tree("📚 [bold]Complete Curriculum[/bold]")
        
        # Group by course and module
        courses = {}
        for lesson in lessons:
            if lesson.course not in courses:
                courses[lesson.course] = {}
            if lesson.module not in courses[lesson.course]:
                courses[lesson.course][lesson.module] = []
            courses[lesson.course][lesson.module].append(lesson)
        
        # Build tree
        for course_name, modules in courses.items():
            course_branch = tree.add(f"📘 [bold blue]{course_name}[/bold blue]")
            
            for module_name, module_lessons in modules.items():
                module_branch = course_branch.add(f"📂 [cyan]{module_name}[/cyan]")
                
                for lesson in module_lessons:
                    difficulty_color = {
                        "beginner": "green",
                        "intermediate": "yellow",
                        "advanced": "red"
                    }.get(lesson.difficulty, "white")
                    
                    module_branch.add(
                        f"📄 {lesson.title} "
                        f"[{difficulty_color}]({lesson.difficulty})[/{difficulty_color}] "
                        f"[dim]{lesson.time}m[/dim]"
                    )
        
        console.print(tree)
        
        # Show statistics
        total_time = sum(l.time for l in lessons)
        console.print(f"\n[bold]Total Content:[/bold] {len(lessons)} lessons, ~{total_time//60} hours")
    
    def interactive_menu(self):
        """Main interactive menu"""
        while True:
            console.print("\n" + "="*80)
            console.print(Panel(
                "[bold cyan]Learning Mode Options[/bold cyan]\n\n"
                "[1] 🚀 Continue Learning (from where you left off)\n"
                "[2] 📖 Start from Beginning\n"
                "[3] 📚 Browse All Lessons\n"
                "[4] 📊 View Progress\n"
                "[5] 🔍 Search Lessons\n"
                "[6] ❌ Exit",
                title="📚 Main Menu",
                border_style="blue"
            ))
            
            choice = Prompt.ask("\nYour choice", choices=["1", "2", "3", "4", "5", "6"])
            
            if choice == "1":
                self.continue_learning()
            elif choice == "2":
                self.start_from_beginning()
            elif choice == "3":
                self.list_all_lessons()
            elif choice == "4":
                self.show_progress()
            elif choice == "5":
                query = Prompt.ask("Search for")
                self.search_lessons(query)
            elif choice == "6":
                console.print("\n[yellow]Keep learning! See you soon! 👋[/yellow]")
                break
    
    def search_lessons(self, query: str):
        """Search for lessons"""
        lessons = self.db.get_all_lessons()
        query_lower = query.lower()
        
        results = []
        for lesson in lessons:
            if (query_lower in lesson.title.lower() or
                query_lower in lesson.content.lower() or
                query_lower in lesson.module.lower() or
                query_lower in lesson.course.lower()):
                results.append(lesson)
        
        if results:
            console.print(f"\n[green]Found {len(results)} results:[/green]\n")
            for i, lesson in enumerate(results, 1):
                console.print(f"{i}. {lesson.title} ({lesson.course} > {lesson.module})")
            
            if Confirm.ask("\nWould you like to start one of these lessons?"):
                choice = IntPrompt.ask("Enter lesson number", default=1)
                if 1 <= choice <= len(results):
                    self.start_lesson(results[choice-1])
        else:
            console.print(f"[yellow]No results found for: {query}[/yellow]")

# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

@click.command()
@click.option('--username', '-u', help='Username for quick login')
@click.option('--continue', 'continue_learning', is_flag=True, help='Continue from last lesson')
@click.option('--list', 'list_lessons', is_flag=True, help='List all lessons')
@click.option('--progress', is_flag=True, help='Show progress')
def main(username, continue_learning, list_lessons, progress):
    """
    Complete Curriculum Learning Platform
    Learn algorithms and data structures with continuous progress tracking!
    """
    try:
        app = ContinuousLearningCLI()
        
        # Header
        console.print("\n" + "="*80)
        console.print(Panel(
            "[bold cyan]🎓 ALGORITHMS & DATA STRUCTURES LEARNING PLATFORM 🎓[/bold cyan]\n\n"
            "[yellow]Complete curriculum with continuous progress tracking[/yellow]",
            border_style="bright_blue"
        ))
        
        # Login
        if not username:
            username = Prompt.ask("\nPlease enter your username")
        
        app.login_or_register(username)
        
        # Handle command line options
        if list_lessons:
            app.list_all_lessons()
        elif progress:
            app.show_progress()
        elif continue_learning:
            app.continue_learning()
        else:
            # Show quick options
            console.print("\n[bold]Quick Start Options:[/bold]")
            console.print("• Press [cyan]Enter[/cyan] to continue from where you left off")
            console.print("• Type [cyan]'menu'[/cyan] for all options")
            console.print("• Type [cyan]'list'[/cyan] to see all lessons")
            
            choice = Prompt.ask("\nYour choice", default="continue")
            
            if choice.lower() == "continue" or choice == "":
                app.continue_learning()
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