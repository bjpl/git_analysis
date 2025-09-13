#!/usr/bin/env python3
"""
Enhanced Curriculum CLI with Thoughtful Claude Integration
This version includes comprehensive UI improvements and seamless Claude assistance
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from curriculum_cli_enhanced import *
from enhanced_learning_system import CLIClaudeIntegration, ComprehensiveLearningEnhancer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.columns import Columns
from rich import box
from rich.align import Align
from rich.text import Text

console = Console()

class EnhancedCurriculumCLI(CurriculumCLI):
    """
    Enhanced CLI with thoughtful Claude integration
    Extends the base CLI with comprehensive learning features
    """
    
    def __init__(self):
        super().__init__()
        self.claude_integration = CLIClaudeIntegration()
        self.learning_enhancer = ComprehensiveLearningEnhancer()
        self.session_insights = []
        self.questions_asked = []
        
    def display_welcome_enhanced(self):
        """Enhanced welcome screen with Claude integration info"""
        console.clear()
        
        # Create a beautiful welcome layout
        welcome_text = Text()
        welcome_text.append("🎓 ", style="bold yellow")
        welcome_text.append("ALGORITHMIC THINKING", style="bold cyan")
        welcome_text.append(" & ", style="bold white")
        welcome_text.append("DATA STRUCTURES", style="bold green")
        welcome_text.append(" 🎓\n", style="bold yellow")
        welcome_text.append("Enhanced with ", style="dim")
        welcome_text.append("Claude AI Learning Companion", style="bold magenta")
        
        # Create info panels
        features_panel = Panel(
            "[bold cyan]Features:[/bold cyan]\n"
            "• Comprehensive curriculum with 50+ lessons\n"
            "• Interactive comprehension checks\n"
            "• [bold yellow]AI-powered Q&A with Claude[/bold yellow]\n"
            "• Smart question suggestions\n"
            "• Structured note-taking\n"
            "• Progress tracking & analytics\n"
            "• Practice problems\n"
            "• Personalized recommendations",
            title="[bold]What's Included[/bold]",
            border_style="cyan",
            box=box.ROUNDED
        )
        
        claude_panel = Panel(
            "[bold magenta]Claude Integration:[/bold magenta]\n"
            "• Ask questions about any lesson\n"
            "• Get detailed explanations\n"
            "• Debug your implementations\n"
            "• Explore real-world applications\n"
            "• Understand complexity analysis\n"
            "• Compare different approaches\n\n"
            "[dim]Keep Claude Code open alongside[/dim]\n"
            "[dim]for the best learning experience![/dim]",
            title="[bold]AI Learning Assistant[/bold]",
            border_style="magenta",
            box=box.ROUNDED
        )
        
        # Display welcome screen
        console.print("\n")
        console.print(Align.center(welcome_text))
        console.print("\n")
        
        # Display panels side by side
        console.print(Columns([features_panel, claude_panel], equal=True, expand=True))
        
        # Show quick stats if user exists
        if hasattr(self, 'current_user') and self.current_user:
            stats = self.get_quick_stats()
            if stats:
                stats_text = (
                    f"[bold green]Welcome back, {self.current_user.username}![/bold green]\n"
                    f"Progress: {stats['completed']}/{stats['total']} lessons "
                    f"({stats['percentage']:.1f}%)"
                )
                console.print("\n")
                console.print(Panel(stats_text, border_style="green", box=box.DOUBLE))
        
        console.print("\n[dim]Press Enter to continue...[/dim]")
        input()
    
    def get_quick_stats(self):
        """Get quick statistics for the user"""
        try:
            all_lessons = self.get_all_lessons()
            progress = self.db.get_user_progress(self.current_user.id)
            completed = sum(1 for lid in progress if progress[lid].get('completed'))
            
            return {
                'completed': completed,
                'total': len(all_lessons),
                'percentage': (completed / len(all_lessons) * 100) if all_lessons else 0
            }
        except:
            return None
    
    def display_lesson_enhanced(self, lesson):
        """Enhanced lesson display with Claude integration"""
        console.clear()
        
        # Header with lesson info
        self._display_lesson_header(lesson)
        
        # Main content in organized sections
        self._display_lesson_content(lesson)
        
        # Code examples with syntax highlighting
        if lesson.get('code'):
            self._display_code_section(lesson)
        
        # Claude assistance section
        self._display_claude_assistance(lesson)
        
        # Interactive learning menu
        console.print("\n[bold cyan]Ready to explore this lesson?[/bold cyan]")
        input("Press Enter to continue...")
        
        # Run interactive learning session
        user_notes = self.interactive_learning_enhanced(lesson)
        
        # Comprehension check
        score = self.run_comprehension_enhanced(lesson)
        
        # Save everything
        self._save_enhanced_progress(lesson, user_notes, score)
        
        return score >= 60
    
    def _display_lesson_header(self, lesson):
        """Display lesson header with metadata"""
        # Title bar
        title_text = Text()
        title_text.append("📚 ", style="bold")
        title_text.append(lesson['title'], style="bold cyan")
        
        console.rule(title_text, style="cyan")
        
        # Metadata table
        metadata = Table(show_header=False, box=None, padding=(0, 2))
        metadata.add_column(style="bold")
        metadata.add_column()
        
        if lesson.get('difficulty'):
            diff_color = {
                'beginner': 'green',
                'intermediate': 'yellow', 
                'advanced': 'red'
            }.get(lesson['difficulty'], 'white')
            metadata.add_row("Difficulty:", f"[{diff_color}]{lesson['difficulty'].title()}[/{diff_color}]")
        
        if lesson.get('time'):
            metadata.add_row("Time:", f"{lesson['time']} minutes")
        
        if lesson.get('module'):
            metadata.add_row("Module:", lesson['module'])
        
        console.print(metadata)
        console.print()
    
    def _display_lesson_content(self, lesson):
        """Display main lesson content"""
        # Learning objectives
        if lesson.get('learning_objectives'):
            objectives_text = "\n".join(f"• {obj}" for obj in lesson['learning_objectives'])
            console.print(Panel(
                objectives_text,
                title="[bold]🎯 Learning Objectives[/bold]",
                border_style="green",
                box=box.ROUNDED
            ))
            console.print()
        
        # Main content
        content = lesson.get('content', 'No content available')
        console.print(Panel(
            Markdown(content),
            title="[bold]📖 Lesson Content[/bold]",
            border_style="cyan",
            box=box.ROUNDED
        ))
    
    def _display_code_section(self, lesson):
        """Display code examples with syntax highlighting"""
        console.print("\n[bold]💻 Code Implementation:[/bold]\n")
        syntax = Syntax(
            lesson['code'],
            "python",
            theme="monokai",
            line_numbers=True,
            word_wrap=True
        )
        console.print(Panel(syntax, border_style="blue", box=box.ROUNDED))
    
    def _display_claude_assistance(self, lesson):
        """Display Claude assistance section with smart questions"""
        console.print("\n")
        console.rule("[bold magenta]🤖 Claude AI Assistance[/bold magenta]", style="magenta")
        
        # Generate smart questions
        questions = self.learning_enhancer.analyze_lesson_for_questions(lesson)
        
        # Create question categories display
        question_table = Table(
            title="[bold]Suggested Questions to Explore[/bold]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta"
        )
        question_table.add_column("Category", style="cyan", width=20)
        question_table.add_column("Questions", style="white")
        
        # Add top questions from each category
        for category, q_list in list(questions.items())[:4]:
            if q_list:
                questions_text = "\n".join(f"• {q}" for q in q_list[:2])
                question_table.add_row(
                    category.replace('_', ' ').title(),
                    questions_text
                )
        
        console.print(question_table)
        
        # Practice problems
        problems = self.learning_enhancer.create_practice_problems(lesson)
        if problems:
            console.print("\n[bold]🎯 Practice Problems:[/bold]")
            for i, problem in enumerate(problems[:3], 1):
                console.print(Panel(
                    f"[bold]{problem['description']}[/bold]\n\n"
                    f"[dim]Hint: {problem['hint']}[/dim]",
                    title=f"Problem {i}",
                    border_style="yellow",
                    box=box.MINIMAL
                ))
        
        console.print("\n[dim]💡 Tip: Copy any question above and ask Claude for a detailed explanation![/dim]")
    
    def interactive_learning_enhanced(self, lesson):
        """Enhanced interactive learning menu with better UI"""
        all_notes = []
        
        while True:
            console.print("\n")
            console.rule("[bold cyan]Interactive Learning Menu[/bold cyan]", style="cyan")
            
            # Create menu options
            menu = Table(show_header=False, box=None, padding=(0, 2))
            menu.add_column(style="bold yellow", width=3)
            menu.add_column(style="white")
            
            menu.add_row("1.", "📝 Take notes about this lesson")
            menu.add_row("2.", "❓ Ask a question (prepare for Claude)")
            menu.add_row("3.", "🔍 View suggested questions")
            menu.add_row("4.", "📚 Review my notes")
            menu.add_row("5.", "💡 Get practice problems")
            menu.add_row("6.", "🎯 See my learning patterns")
            menu.add_row("7.", "✅ Continue to comprehension check")
            
            console.print(menu)
            
            choice = Prompt.ask(
                "\n[bold]Your choice[/bold]",
                choices=["1", "2", "3", "4", "5", "6", "7"],
                default="7"
            )
            
            if choice == "1":
                note = self._take_note_enhanced(lesson)
                if note:
                    all_notes.append(note)
                    console.print("[green]✓ Note saved![/green]")
            
            elif choice == "2":
                question_context = self._prepare_question_enhanced(lesson)
                if question_context:
                    all_notes.append(f"Question prepared: {question_context['question']}")
                    self.questions_asked.append(question_context)
            
            elif choice == "3":
                self._show_suggested_questions(lesson)
            
            elif choice == "4":
                self._review_notes_enhanced(all_notes)
            
            elif choice == "5":
                self._show_practice_problems(lesson)
            
            elif choice == "6":
                self._show_learning_patterns()
            
            elif choice == "7":
                break
        
        return "\n---\n".join(all_notes) if all_notes else ""
    
    def _take_note_enhanced(self, lesson):
        """Enhanced note-taking with structure"""
        console.print("\n[bold]📝 Add a Note[/bold]")
        console.print("[dim]What insight or question would you like to save?[/dim]\n")
        
        note_type = Prompt.ask(
            "Note type",
            choices=["insight", "question", "todo", "concept", "other"],
            default="insight"
        )
        
        note_content = Prompt.ask("[bold]Your note[/bold]")
        
        if note_content:
            timestamp = datetime.now().strftime("%H:%M")
            formatted_note = f"[{timestamp}] [{note_type.upper()}] {note_content}"
            
            # Add emoji based on type
            emoji_map = {
                "insight": "💡",
                "question": "❓",
                "todo": "📌",
                "concept": "🔑",
                "other": "📝"
            }
            
            return f"{emoji_map.get(note_type, '📝')} {formatted_note}"
        
        return None
    
    def _prepare_question_enhanced(self, lesson):
        """Prepare a question for Claude with full context"""
        console.print("\n[bold]❓ Prepare a Question for Claude[/bold]")
        console.print("[dim]I'll help you format your question with context[/dim]\n")
        
        # Show question categories
        console.print("[bold]Question type:[/bold]")
        categories = [
            "conceptual - Understanding why/how it works",
            "implementation - Coding and debugging help",
            "complexity - Time/space analysis",
            "application - Real-world usage",
            "comparison - Vs other approaches"
        ]
        
        for i, cat in enumerate(categories, 1):
            console.print(f"  {i}. {cat}")
        
        cat_choice = Prompt.ask("Choose category", choices=["1","2","3","4","5"], default="1")
        category = categories[int(cat_choice)-1].split(" - ")[0]
        
        # Get the question
        question = Prompt.ask("\n[bold]Your question[/bold]")
        
        if question:
            # Format for Claude
            context = self.claude_integration.format_question_for_claude(lesson, question)
            
            # Show formatted context
            console.print("\n[bold green]✓ Question prepared with context![/bold green]")
            console.print(Panel(
                context[:500] + "..." if len(context) > 500 else context,
                title="[bold]Formatted for Claude[/bold]",
                border_style="green"
            ))
            
            # Track learning pattern
            self.learning_enhancer.track_learning_pattern(
                lesson['id'],
                category,
                30  # Estimated time
            )
            
            # Save to clipboard if possible
            try:
                import pyperclip
                pyperclip.copy(context)
                console.print("\n[green]✓ Copied to clipboard! Paste this to Claude.[/green]")
            except:
                console.print("\n[yellow]Copy the above text to ask Claude[/yellow]")
            
            return {
                'question': question,
                'category': category,
                'context': context,
                'lesson_id': lesson['id']
            }
        
        return None
    
    def _show_suggested_questions(self, lesson):
        """Show detailed suggested questions"""
        console.clear()
        console.rule("[bold magenta]🔍 Suggested Questions[/bold magenta]", style="magenta")
        
        questions = self.learning_enhancer.analyze_lesson_for_questions(lesson)
        
        for category, q_list in questions.items():
            if q_list:
                console.print(f"\n[bold cyan]{category.replace('_', ' ').upper()}:[/bold cyan]")
                for i, q in enumerate(q_list, 1):
                    console.print(f"  {i}. {q}")
        
        console.print("\n[dim]Copy any question and ask Claude for a detailed explanation![/dim]")
        input("\nPress Enter to return...")
    
    def _review_notes_enhanced(self, notes):
        """Review notes with better formatting"""
        if not notes:
            console.print("[yellow]No notes yet for this session[/yellow]")
            return
        
        console.clear()
        console.rule("[bold]📚 Your Notes[/bold]", style="cyan")
        
        for note in notes:
            console.print(Panel(note, box=box.MINIMAL, border_style="dim"))
        
        input("\nPress Enter to return...")
    
    def _show_practice_problems(self, lesson):
        """Show practice problems in detail"""
        console.clear()
        console.rule("[bold yellow]🎯 Practice Problems[/bold yellow]", style="yellow")
        
        problems = self.learning_enhancer.create_practice_problems(lesson)
        
        for i, problem in enumerate(problems, 1):
            console.print(Panel(
                f"[bold]Challenge:[/bold] {problem['description']}\n\n"
                f"[bold]Hint:[/bold] {problem['hint']}\n\n"
                f"[bold]Validation:[/bold] {problem['validation']}",
                title=f"Problem {i}",
                border_style="yellow",
                box=box.ROUNDED
            ))
            console.print()
        
        input("Press Enter to return...")
    
    def _show_learning_patterns(self):
        """Show personalized learning insights"""
        console.clear()
        console.rule("[bold]🎯 Your Learning Patterns[/bold]", style="green")
        
        recommendations = self.learning_enhancer.get_personalized_recommendations()
        
        if recommendations:
            console.print("\n[bold]Insights about your learning:[/bold]\n")
            for rec in recommendations:
                console.print(f"  • {rec}")
        
        # Show session insights if any
        if self.session_insights:
            console.print("\n[bold]This session:[/bold]\n")
            for insight in self.session_insights[-5:]:  # Last 5 insights
                console.print(f"  • {insight}")
        
        # Show questions asked
        if self.questions_asked:
            console.print(f"\n[bold]Questions explored: {len(self.questions_asked)}[/bold]")
            console.print("[dim]Keep asking questions - curiosity drives learning![/dim]")
        
        input("\nPress Enter to return...")
    
    def run_comprehension_enhanced(self, lesson):
        """Enhanced comprehension check with better feedback"""
        questions = lesson.get('comprehension_questions', [])
        if not questions:
            console.print("[yellow]No comprehension questions for this lesson[/yellow]")
            return 100
        
        console.clear()
        console.rule("[bold green]📊 Comprehension Check[/bold green]", style="green")
        
        correct = 0
        total = len(questions)
        
        for i, q in enumerate(questions, 1):
            console.print(f"\n[bold]Question {i} of {total}:[/bold]")
            console.print(Panel(q['question'], border_style="cyan"))
            
            # Display options
            for j, option in enumerate(q['options']):
                console.print(f"  {j + 1}. {option}")
            
            # Get answer with retries
            max_attempts = 2
            for attempt in range(max_attempts):
                try:
                    answer = IntPrompt.ask(
                        "\n[bold]Your answer[/bold]",
                        choices=[str(i) for i in range(1, len(q['options']) + 1)]
                    )
                    answer = int(answer) - 1
                    
                    if answer == q['correct']:
                        console.print("[bold green]✓ Correct![/bold green]")
                        correct += 1
                        if q.get('explanation'):
                            console.print(f"[dim]{q['explanation']}[/dim]")
                    else:
                        console.print("[bold red]✗ Not quite right[/bold red]")
                        if attempt < max_attempts - 1:
                            console.print("[yellow]Try once more...[/yellow]")
                        else:
                            console.print(f"[dim]Correct answer: {q['options'][q['correct']]}[/dim]")
                            if q.get('explanation'):
                                console.print(f"[dim]{q['explanation']}[/dim]")
                            
                            # Suggest asking Claude
                            console.print("\n[magenta]💡 Consider asking Claude to explain this concept![/magenta]")
                    
                    break
                    
                except:
                    if attempt < max_attempts - 1:
                        console.print("[red]Invalid input. Please try again.[/red]")
                    else:
                        console.print("[red]Skipping question due to input error[/red]")
        
        score = (correct / total) * 100
        
        # Display results with feedback
        console.print("\n")
        console.rule("[bold]Results[/bold]", style="cyan")
        
        result_panel = Panel(
            f"[bold]Score: {score:.1f}%[/bold]\n"
            f"Correct: {correct}/{total}\n\n"
            f"{self._get_score_feedback(score)}",
            border_style="green" if score >= 60 else "yellow",
            box=box.DOUBLE
        )
        console.print(result_panel)
        
        input("\nPress Enter to continue...")
        return score
    
    def _get_score_feedback(self, score):
        """Get personalized feedback based on score"""
        if score >= 90:
            return "[green]Excellent! You've mastered this concept! 🌟[/green]"
        elif score >= 75:
            return "[green]Great job! You have a solid understanding! 💪[/green]"
        elif score >= 60:
            return "[yellow]Good progress! Review the areas you missed. 📚[/yellow]"
        else:
            return "[yellow]Keep practicing! Consider asking Claude about the concepts that were challenging. 🤔[/yellow]"
    
    def _save_enhanced_progress(self, lesson, notes, score):
        """Save progress with all enhancements"""
        # Add session insights
        if score >= 60:
            self.session_insights.append(f"Completed {lesson['title']} with {score:.0f}% comprehension")
        
        # Save to database
        self.db.save_progress(
            self.current_user.id,
            lesson['id'],
            completed=True,
            time_spent=int(time.time() - self.session_start) if hasattr(self, 'session_start') else 0,
            quiz_score=score,
            notes=notes
        )
        
        console.print("\n[green]✓ Progress saved successfully![/green]")
        
        if notes:
            console.print("[green]✓ Your notes and questions have been saved![/green]")
    
    def show_progress_enhanced(self):
        """Enhanced progress display with insights"""
        console.clear()
        console.rule("[bold cyan]📊 Learning Progress[/bold cyan]", style="cyan")
        
        # Get progress data
        all_lessons = self.get_all_lessons()
        progress = self.db.get_user_progress(self.current_user.id)
        
        # Calculate stats
        completed = []
        in_progress = []
        not_started = []
        
        for lesson in all_lessons:
            if lesson['id'] in progress:
                if progress[lesson['id']].get('completed'):
                    completed.append(lesson)
                else:
                    in_progress.append(lesson)
            else:
                not_started.append(lesson)
        
        # Display overview
        overview = Table(title="[bold]Overall Progress[/bold]", box=box.ROUNDED)
        overview.add_column("Status", style="bold")
        overview.add_column("Count", justify="center")
        overview.add_column("Percentage", justify="right")
        
        total = len(all_lessons)
        overview.add_row(
            "[green]Completed[/green]",
            str(len(completed)),
            f"{len(completed)/total*100:.1f}%"
        )
        overview.add_row(
            "[yellow]In Progress[/yellow]",
            str(len(in_progress)),
            f"{len(in_progress)/total*100:.1f}%"
        )
        overview.add_row(
            "[dim]Not Started[/dim]",
            str(len(not_started)),
            f"{len(not_started)/total*100:.1f}%"
        )
        
        console.print(overview)
        
        # Show completed lessons with scores
        if completed:
            console.print("\n[bold green]✅ Completed Lessons:[/bold green]")
            for lesson in completed[:10]:  # Show last 10
                score = progress[lesson['id']].get('quiz_score', 0)
                console.print(f"  • {lesson['title']}: {score:.0f}%")
        
        # Show recommendations
        console.print("\n[bold]📚 Recommended Next Steps:[/bold]")
        if in_progress:
            console.print(f"  • Continue with: {in_progress[0]['title']}")
        elif not_started:
            console.print(f"  • Start: {not_started[0]['title']}")
        else:
            console.print("  • Review completed lessons or explore advanced topics!")
        
        # Show insights
        insights = self.learning_enhancer.get_personalized_recommendations()
        if insights:
            console.print("\n[bold]💡 Learning Insights:[/bold]")
            for insight in insights:
                console.print(f"  • {insight}")
        
        input("\nPress Enter to return...")
    
    def run(self):
        """Main run method with enhanced UI"""
        self.display_welcome_enhanced()
        super().run()  # Run the base CLI with enhancements

def main():
    """Run the enhanced CLI"""
    console.print("[bold cyan]Initializing Enhanced Learning System...[/bold cyan]")
    cli = EnhancedCurriculumCLI()
    cli.run()

if __name__ == "__main__":
    main()