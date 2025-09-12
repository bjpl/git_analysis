#!/usr/bin/env python3
"""
Honest Curriculum CLI - Removed misleading Q&A features
Focuses on what actually works: notes, progress tracking, and side-by-side Claude usage
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from curriculum_cli_enhanced import CurriculumCLI, console, Panel, Markdown, Syntax, Prompt, Confirm
from datetime import datetime

class HonestCurriculumCLI(CurriculumCLI):
    """
    Honest version of the CLI that removes misleading features
    and clearly indicates what requires Claude Code
    """
    
    def interactive_learning_menu(self, lesson):
        """
        Simplified interactive menu - removed fake Q&A feature
        """
        notes = []
        
        while True:
            console.print("\n" + "="*80)
            console.print("[bold cyan]Interactive Learning Menu[/bold cyan]")
            console.print("="*80)
            console.print()
            console.print("[bold]Choose an option:[/bold]")
            console.print("1. 📝 Add a note about this lesson")
            console.print("2. 💡 View suggested questions to ask Claude")
            console.print("3. 📚 Review lesson content again")
            console.print("4. 📋 View your notes")
            console.print("5. ✅ Continue to comprehension check")
            console.print()
            
            choice = Prompt.ask("[bold]Your choice[/bold]", 
                              choices=["1", "2", "3", "4", "5"], 
                              default="5")
            
            if choice == "1":
                # Add a note
                note = Prompt.ask("\n[bold]Enter your note[/bold]")
                if note:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    notes.append(f"[{timestamp}] {note}")
                    console.print("[green]✓ Note saved![/green]")
            
            elif choice == "2":
                # Show suggested questions for Claude
                self.show_claude_questions(lesson)
            
            elif choice == "3":
                # Review lesson
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
                # View notes
                if notes:
                    console.print("\n[bold]Your notes:[/bold]")
                    for note in notes:
                        console.print(f"  • {note}")
                else:
                    console.print("[yellow]No notes yet for this lesson[/yellow]")
                input("\nPress Enter to continue...")
            
            elif choice == "5":
                # Continue
                break
        
        return "\n".join(notes) if notes else None
    
    def show_claude_questions(self, lesson):
        """
        Show suggested questions to ask Claude (in Claude Code window)
        """
        console.print("\n" + "="*80)
        console.print("[bold magenta]🤖 Questions to Ask Claude[/bold magenta]")
        console.print("="*80)
        console.print()
        console.print("[yellow]Copy these questions to Claude Code for detailed answers:[/yellow]\n")
        
        title = lesson.get('title', 'this topic')
        
        # Conceptual questions
        console.print("[bold cyan]Conceptual Understanding:[/bold cyan]")
        console.print(f"  • Why does {title} work the way it does?")
        console.print(f"  • What problem does {title} solve that simpler approaches don't?")
        console.print(f"  • Can you explain {title} with a real-world analogy?")
        console.print()
        
        # Implementation questions
        console.print("[bold cyan]Implementation:[/bold cyan]")
        console.print(f"  • What are common mistakes when implementing {title}?")
        console.print(f"  • Can you show me {title} in JavaScript/Java/C++?")
        console.print(f"  • What edge cases should I consider for {title}?")
        console.print()
        
        # Analysis questions
        if 'complexity' in lesson.get('content', '').lower():
            console.print("[bold cyan]Complexity Analysis:[/bold cyan]")
            console.print(f"  • Why is the time complexity of {title} what it is?")
            console.print(f"  • Can you trace through an example showing the complexity?")
            console.print(f"  • What input would cause worst-case performance?")
            console.print()
        
        # Application questions
        console.print("[bold cyan]Real-World Applications:[/bold cyan]")
        console.print(f"  • Where is {title} used in production systems?")
        console.print(f"  • When would I choose {title} over alternatives?")
        console.print(f"  • What are modern variations of {title}?")
        console.print()
        
        console.print("[dim]💡 Tip: Keep Claude Code open beside your terminal for best results![/dim]")
        console.print("="*80)
        
        input("\nPress Enter to return to menu...")
    
    def display_welcome_honest(self):
        """
        Honest welcome message about capabilities
        """
        console.clear()
        console.print("\n" + "="*60)
        console.print("[bold cyan]🎓 ALGORITHMIC THINKING & DATA STRUCTURES[/bold cyan]")
        console.print("="*60)
        console.print()
        
        console.print("[bold]What This CLI Provides:[/bold]")
        console.print("  ✅ Complete curriculum with 50+ lessons")
        console.print("  ✅ Interactive comprehension checks")
        console.print("  ✅ Progress tracking in SQLite database")
        console.print("  ✅ Note-taking functionality")
        console.print("  ✅ Suggested questions for external Q&A")
        console.print()
        
        console.print("[bold]What This CLI Does NOT Do:[/bold]")
        console.print("  ❌ Answer questions (no API integration)")
        console.print("  ❌ Provide real-time AI assistance")
        console.print("  ❌ Generate dynamic explanations")
        console.print()
        
        console.print("[bold green]Recommended Usage:[/bold green]")
        console.print("  1. Run this CLI in your terminal")
        console.print("  2. Keep Claude Code open in another window")
        console.print("  3. Copy suggested questions to Claude for answers")
        console.print("  4. Save Claude's insights as notes in the CLI")
        console.print()
        
        console.print("[dim]This honest approach gives you the best learning experience[/dim]")
        console.print("[dim]without misleading features or false promises.[/dim]")
        console.print()
        
        input("Press Enter to continue...")
    
    def run(self):
        """Override run to show honest welcome"""
        self.display_welcome_honest()
        super().run()

def main():
    """Run the honest CLI"""
    cli = HonestCurriculumCLI()
    cli.run()

if __name__ == "__main__":
    main()