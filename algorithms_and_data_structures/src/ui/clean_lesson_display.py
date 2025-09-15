#!/usr/bin/env python3
"""
Clean Lesson Display Module - Fixed single-format display for lessons
Ensures content is displayed only once in a clean, readable format
"""

import textwrap
import re
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.table import Table
from rich import box
from rich.text import Text
from rich.prompt import Prompt, Confirm


class CleanLessonDisplay:
    """Display lessons cleanly without duplication or formatting issues"""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize with a Rich console"""
        self.console = console or Console()
        self.width = self.console.width
        
    def display_lesson(self, lesson: Dict[str, Any], show_notes_prompt: bool = True) -> Optional[str]:
        """
        Display a lesson with clean, single-format output
        
        Args:
            lesson: Lesson dictionary containing content, code, etc.
            show_notes_prompt: Whether to show the notes prompt
            
        Returns:
            User notes if prompted, None otherwise
        """
        # Clear screen for clean display
        self.console.clear()
        
        # Display title in a beautiful panel
        title = lesson.get('title', 'Lesson')
        self.console.print(Panel.fit(
            f"[bold cyan]{title}[/bold cyan]",
            border_style="bright_cyan",
            padding=(1, 2)
        ))
        
        # Display metadata in a clean format
        self._display_metadata(lesson)
        
        # Display main content using Rich Markdown
        content = lesson.get('content', 'No content available')
        self._display_content(content)
        
        # Display code examples if present
        if 'code' in lesson and lesson['code']:
            self._display_code_examples(lesson['code'])
        
        # Display practice problems if present
        if 'practice_problems' in lesson:
            self._display_practice_problems(lesson['practice_problems'])
        
        # Handle note-taking if requested
        if show_notes_prompt:
            return self._handle_notes()
        
        return None
    
    def _display_metadata(self, lesson: Dict[str, Any]) -> None:
        """Display lesson metadata in a clean table format"""
        metadata_items = []
        
        # Difficulty with color coding
        if 'difficulty' in lesson:
            diff = lesson['difficulty']
            diff_colors = {
                'beginner': 'green',
                'intermediate': 'yellow',
                'advanced': 'red'
            }
            color = diff_colors.get(diff, 'white')
            metadata_items.append(
                f"[{color}]● Difficulty: {diff.title()}[/{color}]"
            )
        
        # Estimated time
        if 'time' in lesson:
            metadata_items.append(
                f"[cyan]⏱ Time: {lesson['time']} minutes[/cyan]"
            )
        
        # Prerequisites
        if 'prerequisites' in lesson:
            prereqs = ", ".join(lesson['prerequisites'])
            metadata_items.append(
                f"[yellow]📚 Prerequisites: {prereqs}[/yellow]"
            )
        
        # Display metadata in columns
        if metadata_items:
            self.console.print("  ".join(metadata_items))
            self.console.print()
    
    def _display_content(self, content: str) -> None:
        """Display the main lesson content using Rich Markdown"""
        # Remove any duplicate formatting or ASCII art boxes
        # Clean up the content to ensure single format
        cleaned_content = self._clean_content(content)
        
        # Display using Rich Markdown for proper formatting
        self.console.print(Panel(
            Markdown(cleaned_content),
            title="[bold]📖 Lesson Content[/bold]",
            border_style="cyan",
            padding=(1, 2)
        ))
        self.console.print()
    
    def _clean_content(self, content: str) -> str:
        """Clean content to remove duplicate formatting"""
        # Remove ASCII art boxes and borders
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip pure ASCII art border lines
            if re.match(r'^[+\-=│├└┌┐┘┤┬┴┼─]+$', line.strip()):
                continue
            # Skip lines that are just borders with spaces
            if re.match(r'^[│|]\s*[│|]?$', line.strip()):
                continue
            # Remove leading border characters
            line = re.sub(r'^[│|]\s*', '', line)
            line = re.sub(r'\s*[│|]$', '', line)
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _display_code_examples(self, code: str) -> None:
        """Display code examples with syntax highlighting"""
        self.console.print("[bold]💻 Code Examples:[/bold]")
        self.console.print()
        
        # Use Rich Syntax for proper code highlighting
        syntax = Syntax(
            code,
            "python",
            theme="monokai",
            line_numbers=True,
            word_wrap=False
        )
        
        self.console.print(Panel(
            syntax,
            border_style="bright_blue",
            padding=(1, 1)
        ))
        self.console.print()
    
    def _display_practice_problems(self, problems: list) -> None:
        """Display practice problems in a clean format"""
        self.console.print("[bold]🎯 Practice Problems:[/bold]")
        self.console.print()
        
        for i, problem in enumerate(problems, 1):
            # Problem title
            title = problem.get('title', f'Problem {i}')
            self.console.print(f"[cyan]{i}. {title}[/cyan]")
            
            # Problem description
            if 'description' in problem:
                self.console.print(f"   {problem['description']}")
            
            # Example
            if 'example' in problem:
                self.console.print(f"   [dim]Example: {problem['example']}[/dim]")
            
            self.console.print()
    
    def _handle_notes(self) -> Optional[str]:
        """Handle note-taking interaction"""
        self.console.print("[bold yellow]📝 Taking Notes[/bold yellow]")
        self.console.print("[dim]Enter your notes below (press Enter twice to finish):[/dim]")
        self.console.print()
        
        notes_lines = []
        empty_lines = 0
        
        while True:
            try:
                line = input()
                if line == "":
                    empty_lines += 1
                    if empty_lines >= 2:
                        break
                    notes_lines.append(line)
                else:
                    empty_lines = 0
                    notes_lines.append(line)
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Note-taking cancelled[/yellow]")
                return None
        
        notes = '\n'.join(notes_lines).strip()
        
        if notes:
            self.console.print("\n[green]✓ Notes saved successfully![/green]")
            return notes
        else:
            self.console.print("\n[dim]No notes entered[/dim]")
            return None


def display_lesson_clean(lesson_data: Dict[str, Any]) -> Optional[str]:
    """
    Convenience function to display a lesson cleanly
    
    Args:
        lesson_data: Dictionary containing lesson information
        
    Returns:
        User notes if any, None otherwise
    """
    display = CleanLessonDisplay()
    return display.display_lesson(lesson_data)