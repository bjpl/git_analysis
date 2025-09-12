#!/usr/bin/env python3
"""
Complete Standalone Curriculum CLI - Fully Functional Implementation
A beautiful and robust CLI for learning algorithms and data structures.
"""

import json
import os
import sys
import time
import random
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import re

# Rich imports for beautiful terminal UI
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.layout import Layout
    from rich.align import Align
    from rich.columns import Columns
    from rich import box
    from rich.text import Text
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Installing required package 'rich' for beautiful terminal output...")
    os.system(f"{sys.executable} -m pip install rich")
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.layout import Layout
    from rich.align import Align
    from rich.columns import Columns
    from rich import box
    from rich.text import Text
    from rich.markdown import Markdown

# Click for CLI commands
try:
    import click
except ImportError:
    print("Installing required package 'click' for CLI commands...")
    os.system(f"{sys.executable} -m pip install click")
    import click

# Initialize console
console = Console()

# ==============================================================================
# DATA MODELS
# ==============================================================================

class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ContentType(Enum):
    LESSON = "lesson"
    EXERCISE = "exercise"
    QUIZ = "quiz"
    PROJECT = "project"
    ARTICLE = "article"

@dataclass
class User:
    """User profile for tracking progress"""
    id: str
    username: str
    email: str = ""
    skill_level: str = "beginner"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    preferences: Dict[str, Any] = field(default_factory=dict)
    achievements: List[str] = field(default_factory=list)
    current_streak: int = 0
    total_study_time: int = 0  # in minutes
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Lesson:
    """Individual lesson content"""
    id: str
    title: str
    description: str
    content: str
    code_examples: List[Dict[str, str]]
    difficulty: str
    estimated_time: int  # in minutes
    prerequisites: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    exercises: List[Dict[str, Any]] = field(default_factory=list)
    quiz_questions: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

@dataclass
class Progress:
    """User progress tracking"""
    user_id: str
    lesson_id: str
    status: str  # "not_started", "in_progress", "completed"
    score: float = 0.0
    time_spent: int = 0  # in minutes
    attempts: int = 0
    completed_at: Optional[str] = None
    notes: str = ""

@dataclass
class Course:
    """Course structure"""
    id: str
    title: str
    description: str
    modules: List[Dict[str, Any]]
    difficulty: str
    estimated_hours: int
    prerequisites: List[str] = field(default_factory=list)
    learning_outcomes: List[str] = field(default_factory=list)
    instructor: str = "AI Tutor"
    tags: List[str] = field(default_factory=list)

# ==============================================================================
# DATABASE MANAGER
# ==============================================================================

class DatabaseManager:
    """Handles all database operations"""
    
    def __init__(self, db_path: str = "curriculum.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        
    def create_tables(self):
        """Create all necessary tables"""
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                skill_level TEXT DEFAULT 'beginner',
                created_at TEXT,
                preferences TEXT,
                achievements TEXT,
                current_streak INTEGER DEFAULT 0,
                total_study_time INTEGER DEFAULT 0,
                last_activity TEXT
            )
        ''')
        
        # Lessons table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lessons (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                content TEXT,
                code_examples TEXT,
                difficulty TEXT,
                estimated_time INTEGER,
                prerequisites TEXT,
                learning_objectives TEXT,
                exercises TEXT,
                quiz_questions TEXT,
                tags TEXT
            )
        ''')
        
        # Progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                user_id TEXT,
                lesson_id TEXT,
                status TEXT DEFAULT 'not_started',
                score REAL DEFAULT 0.0,
                time_spent INTEGER DEFAULT 0,
                attempts INTEGER DEFAULT 0,
                completed_at TEXT,
                notes TEXT,
                PRIMARY KEY (user_id, lesson_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (lesson_id) REFERENCES lessons(id)
            )
        ''')
        
        # Courses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                modules TEXT,
                difficulty TEXT,
                estimated_hours INTEGER,
                prerequisites TEXT,
                learning_outcomes TEXT,
                instructor TEXT DEFAULT 'AI Tutor',
                tags TEXT
            )
        ''')
        
        self.conn.commit()
    
    def save_user(self, user: User) -> bool:
        """Save or update user"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (id, username, email, skill_level, created_at, preferences, 
                 achievements, current_streak, total_study_time, last_activity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.id, user.username, user.email, user.skill_level,
                user.created_at, json.dumps(user.preferences),
                json.dumps(user.achievements), user.current_streak,
                user.total_study_time, user.last_activity
            ))
            self.conn.commit()
            return True
        except Exception as e:
            console.print(f"[red]Error saving user: {e}[/red]")
            return False
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row:
            return User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                skill_level=row['skill_level'],
                created_at=row['created_at'],
                preferences=json.loads(row['preferences'] or '{}'),
                achievements=json.loads(row['achievements'] or '[]'),
                current_streak=row['current_streak'],
                total_study_time=row['total_study_time'],
                last_activity=row['last_activity']
            )
        return None
    
    def save_lesson(self, lesson: Lesson) -> bool:
        """Save or update lesson"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO lessons 
                (id, title, description, content, code_examples, difficulty,
                 estimated_time, prerequisites, learning_objectives, 
                 exercises, quiz_questions, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                lesson.id, lesson.title, lesson.description, lesson.content,
                json.dumps(lesson.code_examples), lesson.difficulty,
                lesson.estimated_time, json.dumps(lesson.prerequisites),
                json.dumps(lesson.learning_objectives), json.dumps(lesson.exercises),
                json.dumps(lesson.quiz_questions), json.dumps(lesson.tags)
            ))
            self.conn.commit()
            return True
        except Exception as e:
            console.print(f"[red]Error saving lesson: {e}[/red]")
            return False
    
    def get_lesson(self, lesson_id: str) -> Optional[Lesson]:
        """Get lesson by ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM lessons WHERE id = ?', (lesson_id,))
        row = cursor.fetchone()
        if row:
            return Lesson(
                id=row['id'],
                title=row['title'],
                description=row['description'],
                content=row['content'],
                code_examples=json.loads(row['code_examples'] or '[]'),
                difficulty=row['difficulty'],
                estimated_time=row['estimated_time'],
                prerequisites=json.loads(row['prerequisites'] or '[]'),
                learning_objectives=json.loads(row['learning_objectives'] or '[]'),
                exercises=json.loads(row['exercises'] or '[]'),
                quiz_questions=json.loads(row['quiz_questions'] or '[]'),
                tags=json.loads(row['tags'] or '[]')
            )
        return None
    
    def get_all_lessons(self) -> List[Lesson]:
        """Get all lessons"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM lessons')
        lessons = []
        for row in cursor.fetchall():
            lessons.append(Lesson(
                id=row['id'],
                title=row['title'],
                description=row['description'],
                content=row['content'],
                code_examples=json.loads(row['code_examples'] or '[]'),
                difficulty=row['difficulty'],
                estimated_time=row['estimated_time'],
                prerequisites=json.loads(row['prerequisites'] or '[]'),
                learning_objectives=json.loads(row['learning_objectives'] or '[]'),
                exercises=json.loads(row['exercises'] or '[]'),
                quiz_questions=json.loads(row['quiz_questions'] or '[]'),
                tags=json.loads(row['tags'] or '[]')
            ))
        return lessons
    
    def save_progress(self, progress: Progress) -> bool:
        """Save or update progress"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO progress 
                (user_id, lesson_id, status, score, time_spent, 
                 attempts, completed_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                progress.user_id, progress.lesson_id, progress.status,
                progress.score, progress.time_spent, progress.attempts,
                progress.completed_at, progress.notes
            ))
            self.conn.commit()
            return True
        except Exception as e:
            console.print(f"[red]Error saving progress: {e}[/red]")
            return False
    
    def get_user_progress(self, user_id: str) -> List[Progress]:
        """Get all progress for a user"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM progress WHERE user_id = ?', (user_id,))
        progress_list = []
        for row in cursor.fetchall():
            progress_list.append(Progress(
                user_id=row['user_id'],
                lesson_id=row['lesson_id'],
                status=row['status'],
                score=row['score'],
                time_spent=row['time_spent'],
                attempts=row['attempts'],
                completed_at=row['completed_at'],
                notes=row['notes']
            ))
        return progress_list
    
    def close(self):
        """Close database connection"""
        self.conn.close()

# ==============================================================================
# CONTENT MANAGER
# ==============================================================================

class ContentManager:
    """Manages curriculum content and lessons"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.current_user = None
        self.load_default_content()
    
    def load_default_content(self):
        """Load default curriculum content"""
        # Check if content already exists
        lessons = self.db.get_all_lessons()
        if len(lessons) > 0:
            return  # Content already loaded
        
        # Create default lessons
        default_lessons = [
            Lesson(
                id="arrays_intro",
                title="Introduction to Arrays",
                description="Learn the fundamentals of arrays and their operations",
                content="""
# Arrays: The Foundation of Data Structures

Arrays are one of the most fundamental data structures in computer science.
They provide a way to store multiple elements of the same type in contiguous memory.

## Key Concepts:
- **Fixed Size**: Arrays have a predetermined size
- **Index-Based Access**: Elements accessed via indices (0 to n-1)
- **Contiguous Memory**: Elements stored sequentially in memory
- **O(1) Access Time**: Direct access to any element

## Common Operations:
1. **Access**: O(1) - Direct index access
2. **Search**: O(n) - Linear search, O(log n) if sorted (binary search)
3. **Insertion**: O(n) - May require shifting elements
4. **Deletion**: O(n) - May require shifting elements
                """,
                code_examples=[
                    {
                        "language": "python",
                        "code": """# Creating and using arrays in Python
# Python uses lists as dynamic arrays

# Initialize an array
arr = [1, 2, 3, 4, 5]

# Access element (O(1))
first = arr[0]  # 1
last = arr[-1]  # 5

# Update element (O(1))
arr[2] = 10  # [1, 2, 10, 4, 5]

# Insert element (O(n))
arr.insert(2, 7)  # [1, 2, 7, 10, 4, 5]

# Delete element (O(n))
arr.pop(3)  # [1, 2, 7, 4, 5]

# Search element (O(n))
index = arr.index(7) if 7 in arr else -1"""
                    }
                ],
                difficulty="beginner",
                estimated_time=30,
                prerequisites=[],
                learning_objectives=[
                    "Understand array structure and memory layout",
                    "Master basic array operations",
                    "Analyze time complexity of operations",
                    "Implement array manipulation algorithms"
                ],
                exercises=[
                    {
                        "title": "Find Maximum Element",
                        "description": "Write a function to find the maximum element in an array",
                        "difficulty": "easy",
                        "solution": "def find_max(arr):\n    return max(arr) if arr else None"
                    },
                    {
                        "title": "Reverse Array",
                        "description": "Reverse an array in-place",
                        "difficulty": "easy",
                        "solution": "def reverse_array(arr):\n    arr.reverse()\n    return arr"
                    }
                ],
                quiz_questions=[
                    {
                        "question": "What is the time complexity of accessing an element in an array?",
                        "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"],
                        "correct": 0,
                        "explanation": "Arrays provide constant-time access to elements using their index."
                    }
                ],
                tags=["arrays", "fundamentals", "data-structures"]
            ),
            Lesson(
                id="sorting_bubble",
                title="Bubble Sort Algorithm",
                description="Understanding the bubble sort algorithm and its implementation",
                content="""
# Bubble Sort: The Simple Sorting Algorithm

Bubble Sort is one of the simplest sorting algorithms. It repeatedly steps through
the list, compares adjacent elements and swaps them if they're in the wrong order.

## How It Works:
1. Compare adjacent elements
2. Swap if they're in wrong order
3. Repeat until no swaps needed

## Characteristics:
- **Time Complexity**: O(n²) average and worst case, O(n) best case
- **Space Complexity**: O(1) - sorts in place
- **Stable**: Yes - maintains relative order of equal elements
- **Adaptive**: Yes - performs better on partially sorted data
                """,
                code_examples=[
                    {
                        "language": "python",
                        "code": """def bubble_sort(arr):
    \"\"\"
    Bubble Sort implementation with optimization
    \"\"\"
    n = len(arr)
    
    for i in range(n):
        # Flag to optimize for already sorted arrays
        swapped = False
        
        # Last i elements are already in place
        for j in range(0, n - i - 1):
            # Swap if current element > next element
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        
        # If no swaps occurred, array is sorted
        if not swapped:
            break
    
    return arr

# Example usage
numbers = [64, 34, 25, 12, 22, 11, 90]
sorted_nums = bubble_sort(numbers.copy())
print(f"Original: {numbers}")
print(f"Sorted: {sorted_nums}")"""
                    }
                ],
                difficulty="beginner",
                estimated_time=45,
                prerequisites=["arrays_intro"],
                learning_objectives=[
                    "Understand bubble sort algorithm",
                    "Implement bubble sort from scratch",
                    "Analyze time and space complexity",
                    "Identify optimization opportunities"
                ],
                exercises=[
                    {
                        "title": "Sort Strings",
                        "description": "Modify bubble sort to sort an array of strings",
                        "difficulty": "easy"
                    },
                    {
                        "title": "Count Swaps",
                        "description": "Modify bubble sort to return the number of swaps performed",
                        "difficulty": "medium"
                    }
                ],
                quiz_questions=[
                    {
                        "question": "What is the worst-case time complexity of Bubble Sort?",
                        "options": ["O(n)", "O(n log n)", "O(n²)", "O(2^n)"],
                        "correct": 2,
                        "explanation": "Bubble Sort has O(n²) worst-case complexity when the array is reverse sorted."
                    }
                ],
                tags=["sorting", "algorithms", "bubble-sort"]
            ),
            Lesson(
                id="linked_lists_intro",
                title="Introduction to Linked Lists",
                description="Learn about linked lists and their advantages over arrays",
                content="""
# Linked Lists: Dynamic Data Structures

A linked list is a linear data structure where elements are stored in nodes,
and each node points to the next node in the sequence.

## Structure:
- **Node**: Contains data and reference to next node
- **Head**: Reference to the first node
- **Tail**: Reference to the last node (optional)

## Advantages over Arrays:
- Dynamic size
- Efficient insertion/deletion at any position
- Memory efficient for sparse data

## Disadvantages:
- No random access (must traverse from head)
- Extra memory for storing pointers
- Not cache friendly
                """,
                code_examples=[
                    {
                        "language": "python",
                        "code": """class Node:
    \"\"\"Node class for linked list\"\"\"
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    \"\"\"Singly linked list implementation\"\"\"
    def __init__(self):
        self.head = None
    
    def append(self, data):
        \"\"\"Add element at the end\"\"\"
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
    
    def prepend(self, data):
        \"\"\"Add element at the beginning\"\"\"
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
    
    def display(self):
        \"\"\"Print all elements\"\"\"
        elements = []
        current = self.head
        while current:
            elements.append(str(current.data))
            current = current.next
        return " -> ".join(elements)

# Example usage
ll = LinkedList()
ll.append(1)
ll.append(2)
ll.append(3)
ll.prepend(0)
print(ll.display())  # 0 -> 1 -> 2 -> 3"""
                    }
                ],
                difficulty="intermediate",
                estimated_time=60,
                prerequisites=["arrays_intro"],
                learning_objectives=[
                    "Understand linked list structure",
                    "Implement basic linked list operations",
                    "Compare linked lists with arrays",
                    "Analyze time complexity of operations"
                ],
                exercises=[
                    {
                        "title": "Find Middle",
                        "description": "Find the middle element of a linked list",
                        "difficulty": "medium"
                    },
                    {
                        "title": "Detect Cycle",
                        "description": "Detect if a linked list has a cycle",
                        "difficulty": "medium"
                    }
                ],
                quiz_questions=[
                    {
                        "question": "What is the time complexity of inserting at the head of a linked list?",
                        "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"],
                        "correct": 0,
                        "explanation": "Inserting at the head only requires updating the head pointer, which is O(1)."
                    }
                ],
                tags=["linked-lists", "data-structures", "pointers"]
            ),
            Lesson(
                id="binary_trees_intro",
                title="Binary Trees Fundamentals",
                description="Introduction to binary trees and tree traversal algorithms",
                content="""
# Binary Trees: Hierarchical Data Structures

A binary tree is a tree data structure where each node has at most two children,
referred to as left child and right child.

## Key Concepts:
- **Root**: Top node of the tree
- **Leaf**: Node with no children
- **Height**: Length of longest path from root to leaf
- **Depth**: Length of path from root to a node

## Types of Binary Trees:
1. **Full Binary Tree**: Every node has 0 or 2 children
2. **Complete Binary Tree**: All levels filled except possibly the last
3. **Perfect Binary Tree**: All internal nodes have 2 children, all leaves at same level
4. **Binary Search Tree (BST)**: Left subtree < node < right subtree

## Tree Traversals:
- **Inorder**: Left -> Root -> Right
- **Preorder**: Root -> Left -> Right
- **Postorder**: Left -> Right -> Root
- **Level Order**: Level by level (BFS)
                """,
                code_examples=[
                    {
                        "language": "python",
                        "code": """class TreeNode:
    \"\"\"Binary tree node\"\"\"
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class BinaryTree:
    \"\"\"Binary tree with traversal methods\"\"\"
    def __init__(self):
        self.root = None
    
    def inorder(self, node):
        \"\"\"Inorder traversal: Left -> Root -> Right\"\"\"
        result = []
        if node:
            result.extend(self.inorder(node.left))
            result.append(node.val)
            result.extend(self.inorder(node.right))
        return result
    
    def preorder(self, node):
        \"\"\"Preorder traversal: Root -> Left -> Right\"\"\"
        result = []
        if node:
            result.append(node.val)
            result.extend(self.preorder(node.left))
            result.extend(self.preorder(node.right))
        return result
    
    def postorder(self, node):
        \"\"\"Postorder traversal: Left -> Right -> Root\"\"\"
        result = []
        if node:
            result.extend(self.postorder(node.left))
            result.extend(self.postorder(node.right))
            result.append(node.val)
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
        
        return result

# Example: Create a binary tree
#       1
#      / \\
#     2   3
#    / \\
#   4   5

tree = BinaryTree()
tree.root = TreeNode(1)
tree.root.left = TreeNode(2)
tree.root.right = TreeNode(3)
tree.root.left.left = TreeNode(4)
tree.root.left.right = TreeNode(5)

print("Inorder:", tree.inorder(tree.root))    # [4, 2, 5, 1, 3]
print("Preorder:", tree.preorder(tree.root))  # [1, 2, 4, 5, 3]
print("Postorder:", tree.postorder(tree.root)) # [4, 5, 2, 3, 1]"""
                    }
                ],
                difficulty="intermediate",
                estimated_time=75,
                prerequisites=["linked_lists_intro"],
                learning_objectives=[
                    "Understand binary tree structure",
                    "Implement tree traversal algorithms",
                    "Recognize different types of binary trees",
                    "Solve tree-based problems"
                ],
                exercises=[
                    {
                        "title": "Tree Height",
                        "description": "Calculate the height of a binary tree",
                        "difficulty": "medium"
                    },
                    {
                        "title": "Is Balanced",
                        "description": "Check if a binary tree is balanced",
                        "difficulty": "medium"
                    }
                ],
                quiz_questions=[
                    {
                        "question": "Which traversal visits nodes as: Left, Root, Right?",
                        "options": ["Preorder", "Inorder", "Postorder", "Level Order"],
                        "correct": 1,
                        "explanation": "Inorder traversal visits left subtree, then root, then right subtree."
                    }
                ],
                tags=["trees", "binary-trees", "traversal", "data-structures"]
            ),
            Lesson(
                id="dynamic_programming_intro",
                title="Dynamic Programming Basics",
                description="Introduction to dynamic programming with classic problems",
                content="""
# Dynamic Programming: Optimization through Memorization

Dynamic Programming (DP) is a method for solving complex problems by breaking them
down into simpler subproblems and storing their solutions.

## Key Principles:
1. **Overlapping Subproblems**: Problem can be broken into subproblems which are reused
2. **Optimal Substructure**: Optimal solution contains optimal solutions to subproblems

## Approaches:
1. **Top-Down (Memoization)**: Recursive with caching
2. **Bottom-Up (Tabulation)**: Iterative with table

## Classic Problems:
- Fibonacci Sequence
- Coin Change
- Longest Common Subsequence
- 0/1 Knapsack
- Edit Distance
                """,
                code_examples=[
                    {
                        "language": "python",
                        "code": """# Example 1: Fibonacci with DP

def fib_recursive(n):
    \"\"\"Naive recursive approach - O(2^n)\"\"\"
    if n <= 1:
        return n
    return fib_recursive(n-1) + fib_recursive(n-2)

def fib_memoization(n, memo={}):
    \"\"\"Top-down DP with memoization - O(n)\"\"\"
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    
    memo[n] = fib_memoization(n-1, memo) + fib_memoization(n-2, memo)
    return memo[n]

def fib_tabulation(n):
    \"\"\"Bottom-up DP with tabulation - O(n)\"\"\"
    if n <= 1:
        return n
    
    dp = [0] * (n + 1)
    dp[1] = 1
    
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    
    return dp[n]

def fib_optimized(n):
    \"\"\"Space-optimized DP - O(1) space\"\"\"
    if n <= 1:
        return n
    
    prev2, prev1 = 0, 1
    
    for _ in range(2, n + 1):
        current = prev1 + prev2
        prev2 = prev1
        prev1 = current
    
    return prev1

# Example 2: Coin Change Problem

def coin_change(coins, amount):
    \"\"\"
    Find minimum number of coins to make amount
    Bottom-up DP approach
    \"\"\"
    # dp[i] = minimum coins needed for amount i
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    
    return dp[amount] if dp[amount] != float('inf') else -1

# Test the implementations
n = 10
print(f"Fibonacci({n}):")
print(f"  Memoization: {fib_memoization(n)}")
print(f"  Tabulation: {fib_tabulation(n)}")
print(f"  Optimized: {fib_optimized(n)}")

coins = [1, 2, 5]
amount = 11
print(f"\\nCoin Change (coins={coins}, amount={amount}):")
print(f"  Minimum coins: {coin_change(coins, amount)}")"""
                    }
                ],
                difficulty="advanced",
                estimated_time=90,
                prerequisites=["arrays_intro"],
                learning_objectives=[
                    "Understand dynamic programming principles",
                    "Identify DP problems",
                    "Implement memoization and tabulation",
                    "Optimize space complexity"
                ],
                exercises=[
                    {
                        "title": "Climbing Stairs",
                        "description": "Count ways to climb n stairs (1 or 2 steps at a time)",
                        "difficulty": "medium"
                    },
                    {
                        "title": "House Robber",
                        "description": "Maximum money that can be robbed from non-adjacent houses",
                        "difficulty": "medium"
                    }
                ],
                quiz_questions=[
                    {
                        "question": "What are the two main properties a problem must have for DP to be applicable?",
                        "options": [
                            "Sorting and Searching",
                            "Overlapping Subproblems and Optimal Substructure",
                            "Recursion and Iteration",
                            "Time and Space"
                        ],
                        "correct": 1,
                        "explanation": "DP requires overlapping subproblems (reusable solutions) and optimal substructure (optimal solution from optimal subproblem solutions)."
                    }
                ],
                tags=["dynamic-programming", "optimization", "algorithms", "advanced"]
            )
        ]
        
        # Save all default lessons
        for lesson in default_lessons:
            self.db.save_lesson(lesson)
        
        console.print("[green]✓[/green] Default curriculum content loaded successfully!")
    
    def get_lesson_by_topic(self, topic: str) -> Optional[Lesson]:
        """Get lesson by topic keyword"""
        lessons = self.db.get_all_lessons()
        topic_lower = topic.lower()
        
        for lesson in lessons:
            if (topic_lower in lesson.title.lower() or 
                topic_lower in lesson.description.lower() or
                any(topic_lower in tag for tag in lesson.tags)):
                return lesson
        
        return None
    
    def search_lessons(self, query: str) -> List[Lesson]:
        """Search lessons by query"""
        lessons = self.db.get_all_lessons()
        query_lower = query.lower()
        results = []
        
        for lesson in lessons:
            if (query_lower in lesson.title.lower() or
                query_lower in lesson.description.lower() or
                query_lower in lesson.content.lower() or
                any(query_lower in tag for tag in lesson.tags)):
                results.append(lesson)
        
        return results

# ==============================================================================
# LEARNING ENGINE
# ==============================================================================

class LearningEngine:
    """Core learning functionality"""
    
    def __init__(self, db: DatabaseManager, content_manager: ContentManager):
        self.db = db
        self.content_manager = content_manager
        self.current_user = None
        self.current_lesson = None
        self.session_start = None
    
    def login_or_register(self, username: str) -> User:
        """Login existing user or create new one"""
        user = self.db.get_user(username)
        
        if user:
            console.print(f"[green]Welcome back, {username}![/green]")
            # Update streak
            last_activity = datetime.fromisoformat(user.last_activity)
            today = datetime.now()
            if (today - last_activity).days == 1:
                user.current_streak += 1
                console.print(f"[yellow]🔥 Streak: {user.current_streak} days![/yellow]")
            elif (today - last_activity).days > 1:
                user.current_streak = 1
            user.last_activity = today.isoformat()
        else:
            # Create new user
            user = User(
                id=hashlib.md5(username.encode()).hexdigest(),
                username=username,
                email=f"{username}@example.com"
            )
            console.print(f"[green]Welcome to the Learning Platform, {username}![/green]")
            console.print("[cyan]A new profile has been created for you.[/cyan]")
        
        self.db.save_user(user)
        self.current_user = user
        return user
    
    def start_lesson(self, lesson: Lesson):
        """Start a lesson"""
        self.current_lesson = lesson
        self.session_start = time.time()
        
        # Create or update progress
        progress = Progress(
            user_id=self.current_user.id,
            lesson_id=lesson.id,
            status="in_progress",
            attempts=1
        )
        self.db.save_progress(progress)
        
        # Display lesson content
        console.print(Panel(
            f"[bold cyan]{lesson.title}[/bold cyan]\n\n"
            f"[yellow]Estimated time: {lesson.estimated_time} minutes[/yellow]\n"
            f"[green]Difficulty: {lesson.difficulty}[/green]",
            title="📚 Lesson",
            border_style="cyan"
        ))
        
        console.print("\n[bold]Description:[/bold]")
        console.print(lesson.description)
        
        console.print("\n[bold]Learning Objectives:[/bold]")
        for obj in lesson.learning_objectives:
            console.print(f"  • {obj}")
        
        if lesson.prerequisites:
            console.print("\n[bold]Prerequisites:[/bold]")
            for prereq in lesson.prerequisites:
                console.print(f"  • {prereq}")
        
        console.print("\n" + "="*60 + "\n")
        
        # Display content as markdown
        md = Markdown(lesson.content)
        console.print(md)
        
        # Display code examples
        if lesson.code_examples:
            console.print("\n[bold cyan]Code Examples:[/bold cyan]\n")
            for example in lesson.code_examples:
                syntax = Syntax(
                    example['code'],
                    example.get('language', 'python'),
                    theme="monokai",
                    line_numbers=True
                )
                console.print(Panel(syntax, border_style="blue"))
        
        return True
    
    def practice_exercises(self, lesson: Lesson):
        """Practice exercises for a lesson"""
        if not lesson.exercises:
            console.print("[yellow]No exercises available for this lesson.[/yellow]")
            return
        
        console.print("\n[bold cyan]Practice Exercises:[/bold cyan]\n")
        
        for i, exercise in enumerate(lesson.exercises, 1):
            console.print(Panel(
                f"[bold]Exercise {i}: {exercise['title']}[/bold]\n\n"
                f"{exercise['description']}\n\n"
                f"Difficulty: {exercise.get('difficulty', 'medium')}",
                border_style="green"
            ))
            
            if Confirm.ask("Would you like to see the solution?"):
                if 'solution' in exercise:
                    syntax = Syntax(
                        exercise['solution'],
                        "python",
                        theme="monokai",
                        line_numbers=True
                    )
                    console.print(Panel(syntax, title="Solution", border_style="blue"))
            
            if i < len(lesson.exercises):
                if not Confirm.ask("\nContinue to next exercise?"):
                    break
    
    def take_quiz(self, lesson: Lesson) -> float:
        """Take a quiz for the lesson"""
        if not lesson.quiz_questions:
            console.print("[yellow]No quiz available for this lesson.[/yellow]")
            return 0.0
        
        console.print("\n[bold cyan]Quiz Time! 🎯[/bold cyan]\n")
        correct = 0
        total = len(lesson.quiz_questions)
        
        for i, question in enumerate(lesson.quiz_questions, 1):
            console.print(Panel(
                f"[bold]Question {i}/{total}:[/bold]\n\n"
                f"{question['question']}",
                border_style="blue"
            ))
            
            # Display options
            for j, option in enumerate(question['options']):
                console.print(f"  {j+1}. {option}")
            
            # Get answer
            while True:
                try:
                    answer = IntPrompt.ask("\nYour answer (enter number)", default=1)
                    if 1 <= answer <= len(question['options']):
                        break
                    console.print("[red]Please enter a valid option number.[/red]")
                except:
                    console.print("[red]Please enter a number.[/red]")
            
            # Check answer
            if answer - 1 == question['correct']:
                console.print("[green]✓ Correct![/green]")
                correct += 1
            else:
                console.print(f"[red]✗ Incorrect. The correct answer is: {question['options'][question['correct']]}[/red]")
            
            if 'explanation' in question:
                console.print(f"[dim]Explanation: {question['explanation']}[/dim]")
            
            console.print()
        
        score = (correct / total) * 100
        console.print(Panel(
            f"[bold]Quiz Complete![/bold]\n\n"
            f"Score: {correct}/{total} ({score:.1f}%)",
            border_style="green" if score >= 70 else "yellow"
        ))
        
        # Update progress
        if self.current_user and self.current_lesson:
            progress = Progress(
                user_id=self.current_user.id,
                lesson_id=self.current_lesson.id,
                status="completed" if score >= 70 else "in_progress",
                score=score,
                time_spent=int((time.time() - self.session_start) / 60) if self.session_start else 0,
                completed_at=datetime.now().isoformat() if score >= 70 else None
            )
            self.db.save_progress(progress)
        
        return score
    
    def show_progress(self):
        """Display user progress"""
        if not self.current_user:
            console.print("[red]Please login first.[/red]")
            return
        
        progress_list = self.db.get_user_progress(self.current_user.id)
        lessons = self.db.get_all_lessons()
        
        # Create progress table
        table = Table(title=f"Learning Progress for {self.current_user.username}", box=box.ROUNDED)
        table.add_column("Lesson", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Score", justify="center")
        table.add_column("Time Spent", justify="center")
        table.add_column("Attempts", justify="center")
        
        # Create a map of progress by lesson_id
        progress_map = {p.lesson_id: p for p in progress_list}
        
        completed_count = 0
        total_score = 0.0
        total_time = 0
        
        for lesson in lessons:
            progress = progress_map.get(lesson.id)
            
            if progress:
                status_color = {
                    "completed": "green",
                    "in_progress": "yellow",
                    "not_started": "dim"
                }.get(progress.status, "white")
                
                status_icon = {
                    "completed": "✓",
                    "in_progress": "○",
                    "not_started": "·"
                }.get(progress.status, "·")
                
                table.add_row(
                    lesson.title,
                    f"[{status_color}]{status_icon} {progress.status}[/{status_color}]",
                    f"{progress.score:.1f}%" if progress.score > 0 else "-",
                    f"{progress.time_spent} min" if progress.time_spent > 0 else "-",
                    str(progress.attempts)
                )
                
                if progress.status == "completed":
                    completed_count += 1
                    total_score += progress.score
                total_time += progress.time_spent
            else:
                table.add_row(
                    lesson.title,
                    "[dim]· not_started[/dim]",
                    "-",
                    "-",
                    "0"
                )
        
        console.print(table)
        
        # Summary statistics
        total_lessons = len(lessons)
        completion_rate = (completed_count / total_lessons * 100) if total_lessons > 0 else 0
        avg_score = (total_score / completed_count) if completed_count > 0 else 0
        
        summary = Panel(
            f"[bold]Summary Statistics[/bold]\n\n"
            f"📚 Lessons Completed: {completed_count}/{total_lessons} ({completion_rate:.1f}%)\n"
            f"🎯 Average Score: {avg_score:.1f}%\n"
            f"⏱️  Total Study Time: {total_time} minutes\n"
            f"🔥 Current Streak: {self.current_user.current_streak} days\n"
            f"🏆 Achievements: {len(self.current_user.achievements)}",
            border_style="green"
        )
        console.print(summary)

# ==============================================================================
# CLI APPLICATION
# ==============================================================================

class CurriculumCLI:
    """Main CLI application"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.content_manager = ContentManager(self.db)
        self.learning_engine = LearningEngine(self.db, self.content_manager)
        self.running = True
    
    def display_menu(self):
        """Display main menu"""
        menu = """
[bold cyan]📚 Curriculum Learning Platform[/bold cyan]
[dim]────────────────────────────────[/dim]

[bold]Available Commands:[/bold]
  1. [cyan]learn[/cyan] <topic>     - Start learning a topic
  2. [cyan]practice[/cyan] <topic>  - Practice exercises
  3. [cyan]quiz[/cyan] <topic>      - Take a quiz
  4. [cyan]progress[/cyan]          - View your progress
  5. [cyan]search[/cyan] <query>    - Search for content
  6. [cyan]list[/cyan]              - List all lessons
  7. [cyan]demo[/cyan]              - Run interactive demo
  8. [cyan]help[/cyan]              - Show this menu
  9. [cyan]exit[/cyan]              - Exit the program

[dim]Type a command to get started![/dim]
        """
        console.print(Panel(menu, border_style="blue"))
    
    def list_lessons(self):
        """List all available lessons"""
        lessons = self.db.get_all_lessons()
        
        # Create tree structure
        tree = Tree("📚 [bold]Available Lessons[/bold]")
        
        # Group by difficulty
        beginner = tree.add("🌱 [green]Beginner[/green]")
        intermediate = tree.add("🌿 [yellow]Intermediate[/yellow]")
        advanced = tree.add("🌳 [red]Advanced[/red]")
        
        for lesson in lessons:
            node_text = f"{lesson.title} [dim]({lesson.estimated_time} min)[/dim]"
            if lesson.difficulty == "beginner":
                beginner.add(node_text)
            elif lesson.difficulty == "intermediate":
                intermediate.add(node_text)
            else:
                advanced.add(node_text)
        
        console.print(tree)
    
    def interactive_mode(self):
        """Run in interactive mode"""
        console.print("[bold cyan]Welcome to the Curriculum Learning Platform![/bold cyan]")
        console.print("[yellow]Interactive mode - Type 'help' for commands[/yellow]\n")
        
        # Get username
        username = Prompt.ask("Please enter your username")
        self.learning_engine.login_or_register(username)
        
        self.display_menu()
        
        while self.running:
            try:
                command = Prompt.ask("\n[bold]>[/bold]").strip().lower()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0]
                args = parts[1:] if len(parts) > 1 else []
                
                if cmd == "exit" or cmd == "quit":
                    self.running = False
                    console.print("[yellow]Goodbye! Keep learning! 👋[/yellow]")
                
                elif cmd == "help":
                    self.display_menu()
                
                elif cmd == "list":
                    self.list_lessons()
                
                elif cmd == "progress":
                    self.learning_engine.show_progress()
                
                elif cmd == "demo":
                    self.run_demo()
                
                elif cmd == "learn":
                    if not args:
                        topic = Prompt.ask("What topic would you like to learn?")
                    else:
                        topic = " ".join(args)
                    
                    lesson = self.content_manager.get_lesson_by_topic(topic)
                    if lesson:
                        self.learning_engine.start_lesson(lesson)
                        
                        if Confirm.ask("\nWould you like to practice exercises?"):
                            self.learning_engine.practice_exercises(lesson)
                        
                        if Confirm.ask("\nReady to take the quiz?"):
                            self.learning_engine.take_quiz(lesson)
                    else:
                        console.print(f"[red]No lesson found for topic: {topic}[/red]")
                        console.print("[yellow]Try 'list' to see available lessons.[/yellow]")
                
                elif cmd == "practice":
                    if not args:
                        topic = Prompt.ask("What topic would you like to practice?")
                    else:
                        topic = " ".join(args)
                    
                    lesson = self.content_manager.get_lesson_by_topic(topic)
                    if lesson:
                        self.learning_engine.practice_exercises(lesson)
                    else:
                        console.print(f"[red]No lesson found for topic: {topic}[/red]")
                
                elif cmd == "quiz":
                    if not args:
                        topic = Prompt.ask("What topic would you like to quiz on?")
                    else:
                        topic = " ".join(args)
                    
                    lesson = self.content_manager.get_lesson_by_topic(topic)
                    if lesson:
                        self.learning_engine.current_lesson = lesson
                        self.learning_engine.session_start = time.time()
                        self.learning_engine.take_quiz(lesson)
                    else:
                        console.print(f"[red]No lesson found for topic: {topic}[/red]")
                
                elif cmd == "search":
                    if not args:
                        query = Prompt.ask("Enter search query")
                    else:
                        query = " ".join(args)
                    
                    results = self.content_manager.search_lessons(query)
                    if results:
                        console.print(f"\n[green]Found {len(results)} results:[/green]")
                        for lesson in results:
                            console.print(f"  • {lesson.title} - {lesson.description}")
                    else:
                        console.print(f"[yellow]No results found for: {query}[/yellow]")
                
                else:
                    console.print(f"[red]Unknown command: {cmd}[/red]")
                    console.print("[yellow]Type 'help' for available commands.[/yellow]")
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit.[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    
    def run_demo(self):
        """Run interactive demo"""
        console.print("\n[bold cyan]🎬 Starting Interactive Demo[/bold cyan]\n")
        
        # Demo user login
        console.print("[dim]Demo: Logging in as 'demo_user'...[/dim]")
        time.sleep(1)
        demo_user = self.learning_engine.login_or_register("demo_user")
        
        # Show available lessons
        console.print("\n[dim]Demo: Showing available lessons...[/dim]")
        time.sleep(1)
        self.list_lessons()
        
        # Start a lesson
        console.print("\n[dim]Demo: Starting 'Arrays' lesson...[/dim]")
        time.sleep(2)
        lesson = self.content_manager.get_lesson_by_topic("arrays")
        if lesson:
            self.learning_engine.start_lesson(lesson)
        
        # Show progress
        console.print("\n[dim]Demo: Displaying progress...[/dim]")
        time.sleep(1)
        self.learning_engine.show_progress()
        
        console.print("\n[bold green]✓ Demo Complete![/bold green]")
        console.print("[yellow]You can now try these commands yourself![/yellow]")
    
    def cleanup(self):
        """Clean up resources"""
        self.db.close()

# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

@click.command()
@click.option('--demo', is_flag=True, help='Run interactive demo')
@click.option('--username', help='Username for quick login')
def main(demo, username):
    """
    Curriculum Learning Platform - Master algorithms and data structures!
    """
    try:
        app = CurriculumCLI()
        
        if demo:
            app.run_demo()
        else:
            if username:
                app.learning_engine.login_or_register(username)
            app.interactive_mode()
        
        app.cleanup()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye! Keep learning! 👋[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()