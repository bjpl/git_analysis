#!/usr/bin/env python3
"""
Flow Nexus Algorithm Teacher - Beautiful Formatted Output
Provides rich, colorful, and properly formatted algorithm explanations
"""

import sys
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import json

# Rich terminal formatting
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.columns import Columns
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.layout import Layout
    from rich.tree import Tree
    from rich import box
    from rich.style import Style
    from rich.padding import Padding
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: Rich library not available. Install with: pip install rich")

# Fallback to colorama if rich not available
try:
    from colorama import init, Fore, Back, Style as ColoramaStyle
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

@dataclass
class ComplexityInfo:
    """Complexity information for algorithms"""
    time_best: str
    time_average: str
    time_worst: str
    space: str
    description: str

class AlgorithmTeacher:
    """Beautiful algorithm teaching system with Flow Nexus integration"""
    
    def __init__(self):
        """Initialize the teacher with rich console"""
        self.console = Console() if RICH_AVAILABLE else None
        self.complexity_examples = {
            "O(1)": ComplexityInfo(
                time_best="O(1)",
                time_average="O(1)", 
                time_worst="O(1)",
                space="O(1)",
                description="Constant time - The Holy Grail of algorithms! 🏆"
            ),
            "O(log n)": ComplexityInfo(
                time_best="O(1)",
                time_average="O(log n)",
                time_worst="O(log n)",
                space="O(1)",
                description="Logarithmic time - Divide and conquer mastery! ⚔️"
            ),
            "O(n)": ComplexityInfo(
                time_best="O(1)",
                time_average="O(n)",
                time_worst="O(n)",
                space="O(1)",
                description="Linear time - Simple and effective! 📈"
            ),
            "O(n log n)": ComplexityInfo(
                time_best="O(n log n)",
                time_average="O(n log n)",
                time_worst="O(n log n)",
                space="O(log n)",
                description="Linearithmic - The sweet spot for sorting! 🎯"
            ),
            "O(n²)": ComplexityInfo(
                time_best="O(n)",
                time_average="O(n²)",
                time_worst="O(n²)",
                space="O(1)",
                description="Quadratic - Works for small datasets! 📊"
            ),
            "O(2ⁿ)": ComplexityInfo(
                time_best="O(2ⁿ)",
                time_average="O(2ⁿ)",
                time_worst="O(2ⁿ)",
                space="O(n)",
                description="Exponential - The combinatorial explosion! 💥"
            )
        }
    
    def display_header(self, title: str, subtitle: str = ""):
        """Display a beautiful header"""
        if RICH_AVAILABLE and self.console:
            # Create gradient-like header
            header_text = Text(title, style="bold magenta")
            if subtitle:
                subtitle_text = Text(subtitle, style="italic cyan")
                content = Columns([header_text, subtitle_text])
            else:
                content = header_text
            
            panel = Panel(
                content,
                box=box.DOUBLE_EDGE,
                border_style="bright_blue",
                padding=(1, 2)
            )
            self.console.print(panel)
        elif COLORAMA_AVAILABLE:
            print(f"\n{Fore.MAGENTA}{ColoramaStyle.BRIGHT}{'='*60}")
            print(f"{Fore.CYAN}{ColoramaStyle.BRIGHT}{title.center(60)}")
            if subtitle:
                print(f"{Fore.YELLOW}{subtitle.center(60)}")
            print(f"{Fore.MAGENTA}{ColoramaStyle.BRIGHT}{'='*60}{ColoramaStyle.RESET_ALL}\n")
        else:
            print(f"\n{'='*60}")
            print(title.center(60))
            if subtitle:
                print(subtitle.center(60))
            print(f"{'='*60}\n")
    
    def display_complexity_analysis(self, algorithm: str, complexity: ComplexityInfo):
        """Display beautiful complexity analysis"""
        if RICH_AVAILABLE and self.console:
            # Create a beautiful table
            table = Table(
                title=f"🎯 {algorithm} Complexity Analysis",
                box=box.ROUNDED,
                border_style="bright_green",
                header_style="bold magenta",
                title_style="bold cyan"
            )
            
            table.add_column("Metric", style="cyan", width=20)
            table.add_column("Complexity", style="yellow", width=15)
            table.add_column("Description", style="white", width=40)
            
            table.add_row("⚡ Time (Best)", complexity.time_best, "Best case scenario")
            table.add_row("📊 Time (Average)", complexity.time_average, "Expected performance")
            table.add_row("🔥 Time (Worst)", complexity.time_worst, "Worst case scenario")
            table.add_row("💾 Space", complexity.space, "Memory usage")
            
            self.console.print(table)
            
            # Add description panel
            desc_panel = Panel(
                Text(complexity.description, style="bold yellow"),
                title="💡 Key Insight",
                border_style="yellow",
                padding=(1, 2)
            )
            self.console.print(desc_panel)
            
        elif COLORAMA_AVAILABLE:
            print(f"\n{Fore.GREEN}📊 {algorithm} Complexity Analysis{ColoramaStyle.RESET_ALL}")
            print(f"{Fore.CYAN}{'─'*50}")
            print(f"{Fore.YELLOW}⚡ Time (Best):    {complexity.time_best}")
            print(f"{Fore.YELLOW}📊 Time (Average): {complexity.time_average}")
            print(f"{Fore.RED}🔥 Time (Worst):   {complexity.time_worst}")
            print(f"{Fore.BLUE}💾 Space:          {complexity.space}")
            print(f"{Fore.CYAN}{'─'*50}")
            print(f"{Fore.MAGENTA}💡 {complexity.description}{ColoramaStyle.RESET_ALL}\n")
        else:
            print(f"\n{algorithm} Complexity Analysis")
            print("-" * 50)
            print(f"Time (Best):    {complexity.time_best}")
            print(f"Time (Average): {complexity.time_average}")
            print(f"Time (Worst):   {complexity.time_worst}")
            print(f"Space:          {complexity.space}")
            print("-" * 50)
            print(f"{complexity.description}\n")
    
    def display_code_example(self, title: str, code: str, language: str = "python"):
        """Display beautiful syntax-highlighted code"""
        if RICH_AVAILABLE and self.console:
            # Create syntax-highlighted code
            syntax = Syntax(
                code,
                language,
                theme="monokai",
                line_numbers=True,
                background_color="default"
            )
            
            # Wrap in a panel
            code_panel = Panel(
                syntax,
                title=f"💻 {title}",
                border_style="bright_blue",
                padding=(1, 2),
                box=box.ROUNDED
            )
            
            self.console.print(code_panel)
            
        elif COLORAMA_AVAILABLE:
            print(f"\n{Fore.BLUE}💻 {title}{ColoramaStyle.RESET_ALL}")
            print(f"{Fore.CYAN}{'─'*60}")
            # Simple line numbering with colors
            lines = code.split('\n')
            for i, line in enumerate(lines, 1):
                print(f"{Fore.GREEN}{i:3}{Fore.WHITE} {line}")
            print(f"{Fore.CYAN}{'─'*60}{ColoramaStyle.RESET_ALL}\n")
        else:
            print(f"\n{title}")
            print("-" * 60)
            print(code)
            print("-" * 60 + "\n")
    
    def display_visual_comparison(self, algorithms: List[Dict[str, Any]]):
        """Display visual comparison of algorithms"""
        if RICH_AVAILABLE and self.console:
            # Create comparison table
            table = Table(
                title="🔬 Algorithm Comparison",
                box=box.HEAVY_HEAD,
                border_style="bright_cyan",
                header_style="bold on blue"
            )
            
            table.add_column("Algorithm", style="bold yellow", width=20)
            table.add_column("Time Complexity", style="green", width=15)
            table.add_column("Space Complexity", style="blue", width=15)
            table.add_column("Best For", style="magenta", width=30)
            
            for algo in algorithms:
                table.add_row(
                    algo["name"],
                    algo["time"],
                    algo["space"],
                    algo["best_for"]
                )
            
            self.console.print(table)
            
        elif COLORAMA_AVAILABLE:
            print(f"\n{Fore.CYAN}🔬 Algorithm Comparison{ColoramaStyle.RESET_ALL}")
            print(f"{Fore.BLUE}{'='*80}")
            print(f"{Fore.YELLOW}{'Algorithm':<20} {'Time':<15} {'Space':<15} {'Best For':<30}")
            print(f"{Fore.BLUE}{'-'*80}")
            for algo in algorithms:
                print(f"{Fore.GREEN}{algo['name']:<20} "
                      f"{Fore.CYAN}{algo['time']:<15} "
                      f"{Fore.MAGENTA}{algo['space']:<15} "
                      f"{Fore.WHITE}{algo['best_for']:<30}")
            print(f"{Fore.BLUE}{'='*80}{ColoramaStyle.RESET_ALL}\n")
        else:
            print("\nAlgorithm Comparison")
            print("=" * 80)
            print(f"{'Algorithm':<20} {'Time':<15} {'Space':<15} {'Best For':<30}")
            print("-" * 80)
            for algo in algorithms:
                print(f"{algo['name']:<20} {algo['time']:<15} {algo['space']:<15} {algo['best_for']:<30}")
            print("=" * 80 + "\n")
    
    def teach_big_o_notation(self):
        """Teach Big O notation with beautiful formatting"""
        self.display_header(
            "🚀 Big O Notation Masterclass",
            "Understanding Algorithm Complexity"
        )
        
        # Introduction
        if RICH_AVAILABLE and self.console:
            intro = Panel(
                Markdown("""
# What is Big O Notation?

Big O notation is a mathematical notation that describes the **limiting behavior** 
of a function when the argument tends towards a particular value or infinity.

In computer science, we use it to classify algorithms according to how their 
**run time** or **space requirements** grow as the input size grows.

## Key Concepts:
- **O(1)** - Constant time: Holy grail! ⚡
- **O(log n)** - Logarithmic: Divide and conquer! 🎯
- **O(n)** - Linear: Simple iteration! 📈
- **O(n log n)** - Linearithmic: Efficient sorting! 🎪
- **O(n²)** - Quadratic: Nested loops! 📊
- **O(2ⁿ)** - Exponential: Combinatorial explosion! 💥
                """),
                title="📚 Conceptual Foundation",
                border_style="bright_blue",
                padding=(1, 2)
            )
            self.console.print(intro)
        else:
            print("\n📚 What is Big O Notation?\n")
            print("Big O notation describes how algorithms scale with input size.")
            print("\nKey Complexities:")
            print("  O(1) - Constant time")
            print("  O(log n) - Logarithmic")
            print("  O(n) - Linear")
            print("  O(n log n) - Linearithmic")
            print("  O(n²) - Quadratic")
            print("  O(2ⁿ) - Exponential\n")
        
        # Show examples for each complexity
        for complexity_type in ["O(n²)", "O(2ⁿ)"]:
            if complexity_type in self.complexity_examples:
                self.display_complexity_analysis(
                    complexity_type,
                    self.complexity_examples[complexity_type]
                )
        
        # Code examples
        bubble_sort_code = """def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr"""
        
        self.display_code_example(
            "Bubble Sort - O(n²) Example",
            bubble_sort_code,
            "python"
        )
        
        fibonacci_code = """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)"""
        
        self.display_code_example(
            "Naive Fibonacci - O(2ⁿ) Example",
            fibonacci_code,
            "python"
        )
        
        # Comparison table
        algorithms = [
            {"name": "Array Access", "time": "O(1)", "space": "O(1)", "best_for": "Direct index access"},
            {"name": "Binary Search", "time": "O(log n)", "space": "O(1)", "best_for": "Sorted arrays"},
            {"name": "Linear Search", "time": "O(n)", "space": "O(1)", "best_for": "Unsorted arrays"},
            {"name": "Merge Sort", "time": "O(n log n)", "space": "O(n)", "best_for": "Large datasets"},
            {"name": "Bubble Sort", "time": "O(n²)", "space": "O(1)", "best_for": "Small or nearly sorted"},
            {"name": "Traveling Salesman", "time": "O(n!)", "space": "O(n)", "best_for": "Small graphs only"}
        ]
        
        self.display_visual_comparison(algorithms)
        
        # Final insight
        if RICH_AVAILABLE and self.console:
            insight = Panel(
                Text.from_markup(
                    "[bold yellow]🎯 Key Takeaway:[/bold yellow]\n\n"
                    "[white]Understanding Big O helps you:[/white]\n"
                    "• [green]Choose the right algorithm for your use case[/green]\n"
                    "• [cyan]Predict performance at scale[/cyan]\n"
                    "• [magenta]Optimize bottlenecks effectively[/magenta]\n"
                    "• [blue]Pass technical interviews with confidence![/blue]",
                    justify="left"
                ),
                box=box.DOUBLE,
                border_style="bright_yellow",
                padding=(1, 2)
            )
            self.console.print(insight)
        else:
            print("\n🎯 Key Takeaway:")
            print("Understanding Big O helps you:")
            print("  • Choose the right algorithm")
            print("  • Predict performance at scale")
            print("  • Optimize bottlenecks")
            print("  • Ace technical interviews!\n")

def main():
    """Main entry point for the Flow Nexus teacher"""
    teacher = AlgorithmTeacher()
    
    # Check if running in Flow Nexus environment
    if os.environ.get("FLOW_NEXUS_SANDBOX"):
        print("🚀 Running in Flow Nexus Sandbox Environment")
    
    # Teach Big O with beautiful formatting
    teacher.teach_big_o_notation()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())