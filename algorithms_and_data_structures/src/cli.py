#!/usr/bin/env python3
"""
Fixed Curriculum CLI - Clean single-format lesson display
Resolves dual-format display issues and provides clean, readable output
"""

import json
import os
import sys
import time
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# Import Rich for beautiful terminal UI
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich import box
    from rich.text import Text
except ImportError:
    print("Installing required package 'rich' for beautiful terminal output...")
    os.system(f"{sys.executable} -m pip install rich")
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich import box
    from rich.text import Text

# Import our clean display module
from .ui.clean_lesson_display import CleanLessonDisplay

console = Console()

# Sample lesson data for testing
SAMPLE_LESSONS = {
    "big_o_notation": {
        "id": "algo_big_o",
        "title": "Big O Notation",
        "difficulty": "beginner",
        "time": 15,
        "module": "Foundations",
        "content": """# Understanding Big O Notation: The Language of Algorithm Efficiency

You know how when you're looking for a book in your home library, the time it takes depends on how organized it is? That's exactly what Big O notation helps us understand about algorithms - how their performance changes as we scale up the problem size.

## Why This Matters

Imagine you're building an app that starts with 100 users, then grows to 1 million. Big O notation tells you whether your app will still work smoothly or grind to a halt. It's the difference between Instagram loading instantly with billions of photos versus taking minutes to show your feed.

## The Core Concept

Big O notation describes the **worst-case scenario** for how long an algorithm takes relative to the input size. Think of it like this: if you're planning a road trip, you'd want to know the worst traffic conditions you might face, not just the best-case Sunday morning drive.

## Common Time Complexities (From Best to Worst)

### O(1) - Constant Time: The Holy Grail
Like looking up a word in a dictionary when you know the exact page number. Whether the dictionary has 100 or 100,000 pages, if you know the page number, it takes the same time.

**Real-world example**: Accessing an array element by index

### O(log n) - Logarithmic Time: The Power of Divide and Conquer
Like finding a word in a dictionary by repeatedly opening to the middle and deciding which half to search. Each decision eliminates half of the remaining pages.

**Real-world example**: Binary search in a sorted phonebook

### O(n) - Linear Time: The Sequential Scanner
Like reading every page of a book to find a specific quote. If the book is twice as long, it takes twice as long.

**Real-world example**: Finding the maximum value in an unsorted list

### O(n log n) - Linearithmic Time: The Efficient Sorter
Like organizing a deck of cards using merge sort - divide the deck, sort smaller piles, then merge them back together.

**Real-world example**: Efficient sorting algorithms like merge sort

### O(n²) - Quadratic Time: The Nested Loop Trap
Like comparing every person in a room with every other person for a group photo arrangement. With 10 people, that's 100 comparisons; with 100 people, that's 10,000 comparisons!

**Real-world example**: Bubble sort or finding all pairs

### O(2ⁿ) - Exponential Time: The Combinatorial Explosion
Like trying every possible combination of pizza toppings. Each new topping doubles the number of possible pizzas.

**Real-world example**: Naive recursive Fibonacci

## Space Complexity: The Memory Dimension

Big O also describes memory usage. Sometimes we trade space for speed:
- **O(1) space**: Uses same variables regardless of input size
- **O(n) space**: Creates new data proportional to input size

## Practical Rules of Thumb

1. **Drop Constants**: O(2n) becomes O(n) - at scale, the multiplier doesn't change the growth pattern
2. **Drop Lower Terms**: O(n² + n) becomes O(n²) - the highest power dominates
3. **Different Variables**: O(a + b) not O(n) when dealing with two different inputs

## Real-World Impact

Here's what these complexities mean for actual running time with 1 million items:
- O(1): 1 operation - instant
- O(log n): ~20 operations - instant
- O(n): 1 million operations - ~1 second
- O(n log n): 20 million operations - ~20 seconds
- O(n²): 1 trillion operations - ~11 days!

## The Key Insight

Big O isn't about precise timing - it's about understanding how algorithms scale. An O(n²) algorithm might be faster than O(n) for small inputs, but will always lose as data grows. Choose your algorithms based on your expected data size!

## Practice Exercises

1. What's the time complexity of searching for a name in an unsorted list?
2. If an algorithm takes 1 second for 1000 items and 4 seconds for 2000 items, what's likely its complexity?
3. Why might you choose an O(n²) algorithm over an O(n log n) algorithm?

Remember: The best algorithm depends on your specific use case. A simple O(n²) sort might be perfect for sorting 10 items, while you'd need O(n log n) for a million items.""",
        "code": """# Examples of different time complexities

# O(1) - Constant time
def get_first_element(arr):
    return arr[0] if arr else None

# O(log n) - Logarithmic time  
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

# O(n) - Linear time
def find_max(arr):
    if not arr:
        return None
    max_val = arr[0]
    for val in arr:  # Must check every element
        if val > max_val:
            max_val = val
    return max_val

# O(n log n) - Linearithmic time
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])  # Divide
    right = merge_sort(arr[mid:])  # Divide
    return merge(left, right)  # Conquer

# O(n²) - Quadratic time
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - 1 - i):  # Nested loop = n²
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

# O(2ⁿ) - Exponential time
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)  # Branches exponentially

# Space complexity examples
# O(1) space - uses same variables regardless of input
def sum_array(arr):
    total = 0
    for num in arr:
        total += num
    return total

# O(n) space - creates new array proportional to input
def double_array(arr):
    return [x * 2 for x in arr]""",
        "practice_problems": [
            {
                "title": "Identify the Complexity",
                "description": "What is the time complexity of this function?",
                "example": "def mystery(n):\n    for i in range(n):\n        for j in range(n):\n            print(i, j)"
            },
            {
                "title": "Optimize the Algorithm",
                "description": "How would you improve this O(n²) duplicate finder to O(n)?",
                "example": "def has_duplicates(arr):\n    for i in range(len(arr)):\n        for j in range(i+1, len(arr)):\n            if arr[i] == arr[j]:\n                return True\n    return False"
            }
        ]
    }
}


class CurriculumCLI:
    """Curriculum CLI with clean lesson display"""
    
    def __init__(self):
        self.console = console
        self.display = CleanLessonDisplay(console)
        self.current_user = None
        self.progress = {}
        
    def welcome(self):
        """Display welcome message"""
        self.console.clear()
        welcome_text = Text("Welcome to Algorithm Learning System", style="bold cyan")
        self.console.print(Panel.fit(
            welcome_text,
            border_style="bright_cyan",
            padding=(1, 2)
        ))
        self.console.print()
        
    def continue_learning(self):
        """Continue learning with clean display"""
        self.console.print("[cyan]Loading Big O Notation lesson...[/cyan]\n")
        
        # Simulate loading with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]Preparing lesson content...", total=None)
            time.sleep(1)
            progress.remove_task(task)
        
        # Get the lesson data
        lesson = SAMPLE_LESSONS["big_o_notation"]
        
        # Display the lesson using our clean display
        user_notes = self.display.display_lesson(lesson, show_notes_prompt=True)
        
        # Save notes if provided
        if user_notes:
            self.save_notes(lesson["id"], user_notes)
        
        # Ask about comprehension questions
        self.console.print()
        if Confirm.ask("[cyan]Would you like to test your understanding with some questions?[/cyan]"):
            self.run_comprehension_check(lesson)
        
        # Mark as complete
        self.mark_lesson_complete(lesson["id"])
        
        # Ask to continue
        self.console.print()
        if Confirm.ask("[cyan]Continue to next lesson?[/cyan]"):
            self.console.print("[yellow]Next lesson would load here...[/yellow]")
        else:
            self.console.print("[green]Great job! See you next time![/green]")
    
    def save_notes(self, lesson_id: str, notes: str):
        """Save user notes for a lesson"""
        # In a real implementation, this would save to database
        self.progress[f"{lesson_id}_notes"] = notes
        self.console.print(f"[green]✓ Notes saved for lesson {lesson_id}[/green]")
    
    def mark_lesson_complete(self, lesson_id: str):
        """Mark a lesson as complete"""
        # In a real implementation, this would update database
        self.progress[f"{lesson_id}_completed"] = True
        self.console.print(f"[green]✓ Lesson {lesson_id} marked as complete![/green]")
    
    def run_comprehension_check(self, lesson: Dict[str, Any]):
        """Run a simple comprehension check"""
        self.console.print("\n[bold]📊 Quick Comprehension Check[/bold]\n")
        
        questions = [
            {
                "question": "What does O(n²) mean for performance?",
                "options": [
                    "Linear growth",
                    "Quadratic growth - doubling input quadruples time",
                    "Constant time",
                    "Logarithmic growth"
                ],
                "correct": 1
            },
            {
                "question": "Which is generally better for large datasets?",
                "options": [
                    "O(n²)",
                    "O(n log n)",
                    "O(2ⁿ)",
                    "O(n!)"
                ],
                "correct": 1
            }
        ]
        
        score = 0
        for i, q in enumerate(questions, 1):
            self.console.print(f"[cyan]Question {i}:[/cyan] {q['question']}")
            for j, option in enumerate(q['options']):
                self.console.print(f"  {j+1}. {option}")
            
            answer = IntPrompt.ask("Your answer", choices=["1", "2", "3", "4"])
            if int(answer) - 1 == q['correct']:
                self.console.print("[green]✓ Correct![/green]")
                score += 1
            else:
                self.console.print(f"[red]✗ The correct answer was {q['correct']+1}[/red]")
            self.console.print()
        
        self.console.print(f"[bold]Score: {score}/{len(questions)}[/bold]")
        
        if score == len(questions):
            self.console.print("[green]Perfect! You've mastered this concept![/green]")
        elif score >= len(questions) * 0.6:
            self.console.print("[yellow]Good job! Review the parts you missed.[/yellow]")
        else:
            self.console.print("[red]Consider reviewing this lesson again.[/red]")
    
    def interactive_menu(self):
        """Show interactive menu"""
        while True:
            self.console.print("\n[bold]Main Menu[/bold]")
            self.console.print("1. Continue Learning")
            self.console.print("2. View Progress")
            self.console.print("3. Review Notes")
            self.console.print("4. Exit")
            
            choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4"])
            
            if choice == "1":
                self.continue_learning()
            elif choice == "2":
                self.show_progress()
            elif choice == "3":
                self.show_notes()
            elif choice == "4":
                self.console.print("[green]Goodbye! Keep learning![/green]")
                break
    
    def show_progress(self):
        """Show learning progress"""
        self.console.print("\n[bold]Your Progress[/bold]")
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Lesson", style="white")
        table.add_column("Status", style="green")
        table.add_column("Notes", style="yellow")
        
        # Show sample progress
        table.add_row(
            "Big O Notation",
            "✓ Complete" if self.progress.get("algo_big_o_completed") else "⏳ In Progress",
            "Yes" if self.progress.get("algo_big_o_notes") else "No"
        )
        table.add_row("Arrays", "Not Started", "No")
        table.add_row("Linked Lists", "Not Started", "No")
        
        self.console.print(table)
    
    def show_notes(self):
        """Show saved notes"""
        self.console.print("\n[bold]Your Notes[/bold]")
        
        notes_found = False
        for key, value in self.progress.items():
            if key.endswith("_notes"):
                lesson_id = key.replace("_notes", "")
                self.console.print(f"\n[cyan]Lesson: {lesson_id}[/cyan]")
                self.console.print(Panel(value, border_style="dim"))
                notes_found = True
        
        if not notes_found:
            self.console.print("[dim]No notes saved yet[/dim]")
    
    def run(self):
        """Run the CLI application"""
        self.welcome()
        
        # Show initial menu options
        self.console.print("\n[bold]What would you like to do?[/bold]")
        self.console.print("1. Continue Learning")
        self.console.print("2. View Progress")
        self.console.print("3. Review Notes")
        self.console.print("4. Exit")
        
        # Show initial menu choice
        choice = Prompt.ask(
            "\n[cyan]Select an option[/cyan]",
            choices=["1", "2", "3", "4"],
            default="1"
        )
        
        if choice == "1":
            self.continue_learning()
        elif choice == "2":
            self.show_progress()
        elif choice == "3":
            self.show_notes()
        elif choice == "4":
            self.console.print("[green]Goodbye! Keep learning![/green]")
            return
        
        # Show interactive menu after initial action
        self.interactive_menu()


def main():
    """Main entry point"""
    try:
        app = CurriculumCLI()
        app.welcome()
        
        # Simulate the user selecting option 2 (Continue Learning)
        app.continue_learning()
        
        # Then show the menu for further interaction
        app.interactive_menu()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Exiting...[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())


# Create alias for backward compatibility
AlgorithmLearningCLI = CurriculumCLI

if __name__ == "__main__":
    main()