#!/usr/bin/env python3
"""
Interactive CLI Demo - Algorithms & Data Structures Learning Platform
Shows off the main features and capabilities of the CLI
"""

import sys
import time
import random
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.tree import Tree
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
from rich.columns import Columns
from rich import box

console = Console()

class CLIDemo:
    """Interactive demonstration of the CLI features"""
    
    def __init__(self):
        self.console = console
        self.demo_steps = [
            self.welcome_screen,
            self.show_curriculum_overview,
            self.demonstrate_learning_mode,
            self.show_practice_problems,
            self.demonstrate_progress_tracking,
            self.show_search_capabilities,
            self.demonstrate_quiz_mode,
            self.show_analytics,
            self.demonstrate_sparc_integration,
            self.closing_message
        ]
        
    def run(self):
        """Run the complete demo"""
        try:
            for step in self.demo_steps:
                step()
                if step != self.closing_message:
                    self.pause_for_effect()
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Demo interrupted. Thank you for watching![/yellow]")
            sys.exit(0)
    
    def pause_for_effect(self, duration: float = 2.0):
        """Pause between demo steps"""
        time.sleep(duration)
        self.console.print()
    
    def welcome_screen(self):
        """Display welcome screen with ASCII art"""
        ascii_art = """
    ╔═══════════════════════════════════════════════════════════╗
    ║   🎓 ALGORITHMS & DATA STRUCTURES LEARNING PLATFORM 🎓   ║
    ╚═══════════════════════════════════════════════════════════╝
        """
        
        self.console.print(Panel(
            Align.center(ascii_art, vertical="middle"),
            title="[bold cyan]Welcome to the Interactive Demo[/bold cyan]",
            border_style="bright_blue",
            box=box.DOUBLE
        ))
        
        features = [
            "✨ Beautiful Terminal UI with Rich Formatting",
            "📚 Comprehensive Curriculum Management",
            "🎯 Interactive Learning Modes",
            "💡 Smart Practice Problem Generation",
            "📊 Progress Tracking & Analytics",
            "🔍 Advanced Search Capabilities",
            "🧪 Test-Driven Development with SPARC",
            "🤖 AI-Powered Learning Assistance"
        ]
        
        self.console.print("\n[bold]Key Features:[/bold]")
        for feature in features:
            self.console.print(f"  {feature}")
            time.sleep(0.2)
    
    def show_curriculum_overview(self):
        """Demonstrate curriculum structure"""
        self.console.print("\n[bold cyan]📚 Curriculum Overview[/bold cyan]\n")
        
        # Create curriculum tree
        tree = Tree("🎓 [bold]Computer Science Fundamentals[/bold]")
        
        # Algorithms branch
        algorithms = tree.add("📘 Algorithms Fundamentals")
        algorithms.add("🔍 Searching Algorithms")
        algorithms.add("📊 Sorting Algorithms")
        algorithms.add("🔄 Recursion & Backtracking")
        algorithms.add("💰 Greedy Algorithms")
        algorithms.add("🧩 Dynamic Programming")
        
        # Data Structures branch
        ds = tree.add("📗 Data Structures")
        ds.add("📦 Arrays & Strings")
        ds.add("🔗 Linked Lists")
        ds.add("📚 Stacks & Queues")
        ds.add("🌳 Trees & Graphs")
        ds.add("🗂️ Hash Tables")
        ds.add("⚡ Advanced Structures")
        
        self.console.print(tree)
        
        # Show course statistics
        stats_table = Table(title="Course Statistics", box=box.ROUNDED)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Total Courses", "12")
        stats_table.add_row("Total Modules", "48")
        stats_table.add_row("Total Lessons", "156")
        stats_table.add_row("Practice Problems", "500+")
        stats_table.add_row("Estimated Time", "120 hours")
        
        self.console.print(stats_table)
    
    def demonstrate_learning_mode(self):
        """Show interactive learning mode"""
        self.console.print("\n[bold cyan]🎯 Interactive Learning Mode[/bold cyan]\n")
        
        # Simulate command execution
        self.console.print("[dim]$[/dim] adaptive-learning learn quicksort\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Loading lesson...", total=None)
            time.sleep(1)
            progress.update(task, description="Preparing interactive content...")
            time.sleep(1)
        
        # Show lesson content
        lesson_content = '''
[bold]Quick Sort Algorithm[/bold]

Quick Sort is a divide-and-conquer algorithm that picks an element as pivot
and partitions the array around it.

[yellow]Key Concepts:[/yellow]
• Pivot Selection
• Partitioning
• Recursive Sorting

[cyan]Time Complexity:[/cyan]
• Best: O(n log n)
• Average: O(n log n)  
• Worst: O(n²)
'''
        
        self.console.print(Panel(lesson_content, title="Lesson Content", border_style="green"))
        
        # Show code example
        code = '''def quicksort(arr, low, high):
    if low < high:
        pi = partition(arr, low, high)
        quicksort(arr, low, pi - 1)
        quicksort(arr, pi + 1, high)

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1'''
        
        syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
        self.console.print(Panel(syntax, title="Implementation", border_style="blue"))
    
    def show_practice_problems(self):
        """Demonstrate practice problem generation"""
        self.console.print("\n[bold cyan]💡 Practice Problems[/bold cyan]\n")
        
        problems = [
            {
                "title": "Two Sum",
                "difficulty": "Easy",
                "category": "Arrays",
                "time": "15 mins",
                "success_rate": "87%"
            },
            {
                "title": "Merge K Sorted Lists",
                "difficulty": "Hard",
                "category": "Linked Lists",
                "time": "45 mins",
                "success_rate": "42%"
            },
            {
                "title": "Binary Tree Level Order",
                "difficulty": "Medium",
                "category": "Trees",
                "time": "30 mins",
                "success_rate": "65%"
            }
        ]
        
        table = Table(title="Recommended Practice Problems", box=box.SIMPLE_HEAVY)
        table.add_column("Problem", style="cyan")
        table.add_column("Difficulty", justify="center")
        table.add_column("Category", style="magenta")
        table.add_column("Est. Time", justify="center")
        table.add_column("Success Rate", justify="center")
        
        for problem in problems:
            difficulty_color = {
                "Easy": "green",
                "Medium": "yellow",
                "Hard": "red"
            }[problem["difficulty"]]
            
            table.add_row(
                problem["title"],
                f"[{difficulty_color}]{problem['difficulty']}[/{difficulty_color}]",
                problem["category"],
                problem["time"],
                problem["success_rate"]
            )
        
        self.console.print(table)
        
        # Show problem solving interface
        self.console.print("\n[dim]$[/dim] adaptive-learning practice --problem \"Two Sum\"\n")
        
        problem_desc = """[bold]Problem: Two Sum[/bold]

Given an array of integers and a target sum, find two numbers 
that add up to the target.

[yellow]Example:[/yellow]
Input: nums = [2, 7, 11, 15], target = 9
Output: [0, 1] (because nums[0] + nums[1] = 9)

[cyan]Your solution:[/cyan]"""
        
        self.console.print(Panel(problem_desc, border_style="green"))
    
    def demonstrate_progress_tracking(self):
        """Show progress tracking features"""
        self.console.print("\n[bold cyan]📊 Progress Tracking[/bold cyan]\n")
        
        # Progress bars for different topics
        topics = [
            ("Arrays & Strings", 85),
            ("Linked Lists", 70),
            ("Trees & Graphs", 45),
            ("Dynamic Programming", 30),
            ("System Design", 15)
        ]
        
        for topic, progress in topics:
            bar = self.create_progress_bar(progress)
            self.console.print(f"{topic:.<25} {bar} {progress}%")
        
        # Show achievement badges
        self.console.print("\n[bold]🏆 Recent Achievements:[/bold]")
        achievements = [
            ("🥇", "Algorithm Master", "Completed all sorting algorithms"),
            ("🎯", "Problem Solver", "Solved 100 practice problems"),
            ("⚡", "Speed Demon", "Completed 10 problems under time limit"),
            ("🔥", "Hot Streak", "7-day learning streak")
        ]
        
        for icon, title, desc in achievements:
            self.console.print(f"  {icon} [bold]{title}[/bold] - {desc}")
    
    def show_search_capabilities(self):
        """Demonstrate search functionality"""
        self.console.print("\n[bold cyan]🔍 Advanced Search[/bold cyan]\n")
        
        self.console.print("[dim]$[/dim] adaptive-learning search \"binary search tree\"\n")
        
        # Show search results
        results = [
            ("Lesson", "Binary Search Trees Fundamentals", "trees/bst-basics", "95%"),
            ("Exercise", "Validate Binary Search Tree", "problems/validate-bst", "88%"),
            ("Article", "BST vs AVL Trees Comparison", "articles/bst-avl", "82%"),
            ("Video", "Implementing BST in Python", "videos/bst-python", "79%")
        ]
        
        table = Table(title="Search Results", box=box.MINIMAL)
        table.add_column("Type", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("Path", style="dim")
        table.add_column("Relevance", justify="center", style="green")
        
        for result in results:
            table.add_row(*result)
        
        self.console.print(table)
    
    def demonstrate_quiz_mode(self):
        """Show quiz functionality"""
        self.console.print("\n[bold cyan]🧪 Quiz Mode[/bold cyan]\n")
        
        quiz_question = """[bold]Question 1/5:[/bold] What is the time complexity of QuickSort in the average case?

[cyan]Options:[/cyan]
A) O(n)
B) O(n log n)
C) O(n²)
D) O(log n)

[yellow]Your answer:[/yellow] B

✅ [green]Correct![/green] QuickSort has an average time complexity of O(n log n).

[dim]Explanation: QuickSort divides the array into two parts around a pivot,
recursively sorting each part. On average, this creates a balanced partition
leading to O(n log n) complexity.[/dim]"""
        
        self.console.print(Panel(quiz_question, title="Quiz Question", border_style="blue"))
        
        # Show quiz progress
        self.console.print("\nQuiz Progress: [green]━━━━━[/green][dim]━━━━━━━━━━[/dim] 5/15")
        self.console.print("Current Score: [green]80%[/green] (4/5 correct)")
    
    def show_analytics(self):
        """Display learning analytics"""
        self.console.print("\n[bold cyan]📈 Learning Analytics[/bold cyan]\n")
        
        # Create analytics dashboard
        layout = Layout()
        layout.split_column(
            Layout(name="stats", size=7),
            Layout(name="chart", size=10)
        )
        
        # Statistics panel
        stats = """[bold]Weekly Statistics[/bold]
        
📚 Lessons Completed: 12
⏱️ Study Time: 8h 45m
🎯 Problems Solved: 47
📈 Accuracy Rate: 78%
🔥 Current Streak: 7 days"""
        
        layout["stats"].update(Panel(stats, border_style="green"))
        
        # Activity chart (ASCII)
        chart = """[bold]Daily Activity (Last 7 Days)[/bold]

Mon ████████████░░░░░░░░ 60%
Tue ████████████████░░░░ 80%
Wed ██████████░░░░░░░░░░ 50%
Thu ████████████████████ 100%
Fri ██████████████░░░░░░ 70%
Sat ████████░░░░░░░░░░░░ 40%
Sun ██████████████████░░ 90%"""
        
        layout["chart"].update(Panel(chart, border_style="blue"))
        
        self.console.print(layout)
    
    def demonstrate_sparc_integration(self):
        """Show SPARC methodology integration"""
        self.console.print("\n[bold cyan]🤖 SPARC Methodology Integration[/bold cyan]\n")
        
        sparc_phases = """[bold]SPARC Development Phases:[/bold]

1️⃣ [cyan]Specification[/cyan] - Define requirements and constraints
2️⃣ [yellow]Pseudocode[/yellow] - Design algorithm logic
3️⃣ [green]Architecture[/green] - Plan system structure
4️⃣ [magenta]Refinement[/magenta] - Implement with TDD
5️⃣ [blue]Completion[/blue] - Integrate and optimize"""
        
        self.console.print(Panel(sparc_phases, title="SPARC Workflow", border_style="cyan"))
        
        # Show Claude Flow integration
        self.console.print("\n[dim]$[/dim] npx claude-flow sparc tdd \"implement binary search\"\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            tasks = [
                "Initializing SPARC agents...",
                "Analyzing requirements...",
                "Generating test cases...",
                "Implementing solution...",
                "Running tests...",
                "Optimizing code..."
            ]
            
            for task_desc in tasks:
                task = progress.add_task(task_desc, total=None)
                time.sleep(0.5)
                progress.update(task, completed=True)
        
        self.console.print("[green]✓[/green] SPARC workflow completed successfully!")
    
    def closing_message(self):
        """Display closing message"""
        closing = """
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║         🎉 Demo Complete! Ready to Start Learning? 🎉      ║
    ║                                                            ║
    ║   Get started with:                                        ║
    ║   $ pip install -e .                                       ║
    ║   $ adaptive-learning --interactive                        ║
    ║                                                            ║
    ║   Or try:                                                  ║
    ║   $ adaptive-learning quickstart                           ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
        """
        
        self.console.print(Panel(
            Align.center(closing, vertical="middle"),
            title="[bold green]Thank You![/bold green]",
            border_style="bright_green",
            box=box.DOUBLE
        ))
        
        # Show links and resources
        resources = """
[bold]Resources:[/bold]
📖 Documentation: docs/USER_GUIDE.md
💻 GitHub: github.com/yourusername/algorithms-cli
🤝 Contributing: .github/CONTRIBUTING.md
📧 Support: support@example.com
        """
        
        self.console.print(resources)
    
    def create_progress_bar(self, percentage: int, width: int = 20) -> str:
        """Create a visual progress bar"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        
        if percentage >= 80:
            color = "green"
        elif percentage >= 50:
            color = "yellow"
        else:
            color = "red"
        
        return f"[{color}]{bar}[/{color}]"

def main():
    """Run the CLI demo"""
    demo = CLIDemo()
    
    try:
        console.print("\n[bold]Starting Interactive CLI Demo...[/bold]\n")
        console.print("[dim]Press Ctrl+C at any time to exit[/dim]\n")
        time.sleep(2)
        
        demo.run()
        
    except Exception as e:
        console.print(f"\n[red]Error during demo: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()