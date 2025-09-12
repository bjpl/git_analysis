#!/usr/bin/env python3
"""Demo of the Enhanced CLI with Comprehension Checks"""

from curriculum_cli_enhanced import FULL_CURRICULUM_WITH_QUESTIONS
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

def demo():
    """Show a demo of the enhanced CLI features"""
    
    console.print("\n" + "="*80)
    console.print("[bold cyan]ENHANCED CURRICULUM CLI DEMONSTRATION[/bold cyan]")
    console.print("="*80 + "\n")
    
    # Count total lessons
    total_lessons = 0
    total_questions = 0
    
    for course_key, course_data in FULL_CURRICULUM_WITH_QUESTIONS.items():
        if 'modules' in course_data:
            for module in course_data['modules']:
                for lesson in module.get('lessons', []):
                    total_lessons += 1
                    total_questions += len(lesson.get('comprehension_questions', []))
    
    # Show summary
    summary = Panel(
        f"""[bold]Curriculum Statistics:[/bold]
        
• Total Lessons: [green]{total_lessons}[/green]
• Total Comprehension Questions: [yellow]{total_questions}[/yellow]
• Average Questions per Lesson: [cyan]{total_questions/total_lessons:.1f}[/cyan]

[bold]Features:[/bold]
• 🎯 Expertly crafted comprehension questions
• 📊 Three difficulty levels (Understanding, Application, Analysis)
• 💡 Detailed explanations for every answer
• 📈 Progress tracking with SQLite database
• 🚀 Continuous learning mode
• 🎨 Beautiful terminal UI with Rich library""",
        title="[bold]Enhanced CLI Features[/bold]",
        border_style="green"
    )
    
    console.print(summary)
    
    # Show sample lesson
    console.print("\n[bold cyan]Sample Lesson with Comprehension Questions:[/bold cyan]\n")
    
    # Get first lesson as sample
    sample_lesson = None
    for course_key, course_data in FULL_CURRICULUM_WITH_QUESTIONS.items():
        if 'modules' in course_data:
            for module in course_data['modules']:
                for lesson in module.get('lessons', []):
                    sample_lesson = lesson
                    break
                if sample_lesson:
                    break
        if sample_lesson:
            break
    
    if sample_lesson:
        console.print(f"[yellow]Lesson:[/yellow] {sample_lesson['title']}")
        console.print(f"[yellow]Difficulty:[/yellow] {sample_lesson.get('difficulty', 'beginner')}")
        console.print(f"\n[yellow]Sample Comprehension Questions:[/yellow]\n")
        
        for i, q in enumerate(sample_lesson.get('comprehension_questions', [])[:2], 1):
            console.print(f"[bold]Question {i}:[/bold] {q['question']}")
            console.print("[dim]Options:[/dim]")
            for j, option in enumerate(q['options']):
                is_correct = j == q['correct']
                marker = "✓" if is_correct else " "
                console.print(f"  {marker} {j+1}. {option}")
            console.print(f"[dim]Explanation: {q['explanation'][:100]}...[/dim]")
            console.print(f"[dim]Difficulty: {q.get('difficulty', 'understanding').title()}[/dim]\n")
    
    # Show how to run
    console.print("\n" + "="*80)
    console.print("[bold green]How to Use:[/bold green]")
    console.print("="*80 + "\n")
    
    usage_table = Table(box=box.SIMPLE)
    usage_table.add_column("Command", style="cyan")
    usage_table.add_column("Description", style="white")
    
    usage_table.add_row(
        "python curriculum_cli_enhanced.py",
        "Start the interactive CLI"
    )
    usage_table.add_row(
        "Continue Learning",
        "Pick up where you left off"
    )
    usage_table.add_row(
        "Browse Lessons",
        "View all available lessons"
    )
    usage_table.add_row(
        "View Progress",
        "Check your learning statistics"
    )
    
    console.print(usage_table)
    
    console.print("\n[bold yellow]Key Features:[/bold yellow]")
    console.print("• Each lesson includes 2-3 comprehension questions")
    console.print("• Questions test understanding, application, and analysis")
    console.print("• Immediate feedback with explanations")
    console.print("• Progress tracking across sessions")
    console.print("• Beautiful terminal interface")
    
    console.print("\n[green]✅ The enhanced CLI is ready to use![/green]")
    console.print("[green]✅ All lessons have expertly crafted comprehension questions![/green]")
    console.print("[green]✅ Run 'python curriculum_cli_enhanced.py' to start learning![/green]\n")

if __name__ == "__main__":
    demo()