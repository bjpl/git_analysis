#!/usr/bin/env python3
"""
Main entry point for the Adaptive Learning System CLI.
"""

import sys
import click
from pathlib import Path
from typing import Optional

# Add src to path if needed
sys.path.insert(0, str(Path(__file__).parent))

from app import AdaptiveLearningApp
from cli_engine import CLIEngine
from ui.formatter import TerminalFormatter
from config import Config

# Initialize formatter for beautiful output
formatter = TerminalFormatter()

@click.group(invoke_without_command=True)
@click.option('--interactive', '-i', is_flag=True, help='Start interactive mode')
@click.option('--version', '-v', is_flag=True, help='Show version')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def main(ctx, interactive: bool, version: bool, debug: bool):
    """
    Adaptive Learning System - Master algorithms and data structures!
    
    Use --interactive for an interactive learning experience.
    """
    if version:
        click.echo("Adaptive Learning System v1.0.0")
        return
    
    if interactive or ctx.invoked_subcommand is None:
        # Start interactive mode
        app = AdaptiveLearningApp()
        formatter.print_header("Welcome to Adaptive Learning System!")
        formatter.print_info("Starting interactive mode...")
        app.run_interactive()
    
    # Store debug flag for subcommands
    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug

@main.command()
@click.argument('topic')
@click.option('--difficulty', type=click.Choice(['beginner', 'intermediate', 'advanced']), 
              default='beginner', help='Difficulty level')
def learn(topic: str, difficulty: str):
    """Start learning a specific topic."""
    app = AdaptiveLearningApp()
    formatter.print_header(f"Learning: {topic}")
    formatter.print_info(f"Difficulty: {difficulty}")
    app.learn_topic(topic, difficulty)

@main.command()
@click.option('--topic', help='Specific topic to practice')
@click.option('--difficulty', type=click.Choice(['easy', 'medium', 'hard']), 
              default='medium', help='Problem difficulty')
@click.option('--count', default=5, help='Number of problems')
@click.option('--random', is_flag=True, help='Random problem selection')
def practice(topic: Optional[str], difficulty: str, count: int, random: bool):
    """Practice problems to reinforce learning."""
    app = AdaptiveLearningApp()
    formatter.print_header("Practice Mode")
    
    if topic:
        formatter.print_info(f"Topic: {topic}")
    formatter.print_info(f"Difficulty: {difficulty}")
    formatter.print_info(f"Problems: {count}")
    
    app.practice_problems(topic, difficulty, count, random)

@main.command()
@click.argument('topic', required=False)
@click.option('--questions', '-q', default=10, help='Number of questions')
@click.option('--time-limit', type=int, help='Time limit in minutes')
@click.option('--all', 'all_topics', is_flag=True, help='Quiz on all topics')
def quiz(topic: Optional[str], questions: int, time_limit: Optional[int], all_topics: bool):
    """Take a quiz to test your knowledge."""
    app = AdaptiveLearningApp()
    formatter.print_header("Quiz Mode")
    
    if all_topics:
        formatter.print_info("Testing all topics")
    elif topic:
        formatter.print_info(f"Topic: {topic}")
    
    formatter.print_info(f"Questions: {questions}")
    if time_limit:
        formatter.print_info(f"Time limit: {time_limit} minutes")
    
    app.start_quiz(topic if not all_topics else None, questions, time_limit)

@main.command()
@click.option('--detailed', is_flag=True, help='Show detailed progress')
@click.option('--export', type=click.Choice(['json', 'pdf', 'html']), 
              help='Export progress report')
@click.option('--topic', help='Show progress for specific topic')
def progress(detailed: bool, export: Optional[str], topic: Optional[str]):
    """View your learning progress and statistics."""
    app = AdaptiveLearningApp()
    formatter.print_header("Learning Progress")
    
    if topic:
        app.show_topic_progress(topic, detailed)
    else:
        app.show_overall_progress(detailed)
    
    if export:
        formatter.print_success(f"Progress exported to progress.{export}")
        app.export_progress(export)

@main.command()
@click.argument('query')
@click.option('--type', 'content_type', 
              type=click.Choice(['lesson', 'exercise', 'article', 'all']),
              default='all', help='Content type to search')
@click.option('--difficulty', help='Filter by difficulty')
def search(query: str, content_type: str, difficulty: Optional[str]):
    """Search for learning content."""
    app = AdaptiveLearningApp()
    formatter.print_header(f"Searching for: {query}")
    
    results = app.search_content(query, content_type, difficulty)
    if results:
        formatter.print_success(f"Found {len(results)} results")
        for result in results[:10]:  # Show top 10
            formatter.print_info(f"  • {result}")
    else:
        formatter.print_warning("No results found")

@main.command()
def quickstart():
    """Run the interactive quickstart wizard."""
    import sys
    import os
    
    # Try to run the quickstart script
    quickstart_path = Path(__file__).parent.parent / "scripts" / "quickstart.py"
    if quickstart_path.exists():
        os.system(f"{sys.executable} {quickstart_path}")
    else:
        formatter.print_error("Quickstart script not found")
        formatter.print_info("Running basic setup instead...")
        app = AdaptiveLearningApp()
        app.run_quickstart()

@main.command()
def demo():
    """Run the interactive demo."""
    import sys
    import os
    
    demo_path = Path(__file__).parent.parent / "demos" / "cli_demo.py"
    if demo_path.exists():
        os.system(f"{sys.executable} {demo_path}")
    else:
        formatter.print_error("Demo script not found")

@main.group()
def config():
    """Manage configuration settings."""
    pass

@config.command('show')
def config_show():
    """Show current configuration."""
    cfg = Config()
    formatter.print_header("Current Configuration")
    for key, value in cfg.to_dict().items():
        formatter.print_key_value(key, value)

@config.command('set')
@click.argument('key')
@click.argument('value')
def config_set(key: str, value: str):
    """Set a configuration value."""
    cfg = Config()
    cfg.set(key, value)
    formatter.print_success(f"Set {key} = {value}")

@config.command('reset')
@click.confirmation_option(prompt='Reset all settings to defaults?')
def config_reset():
    """Reset configuration to defaults."""
    cfg = Config()
    cfg.reset()
    formatter.print_success("Configuration reset to defaults")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        formatter.print_warning("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        formatter.print_error(f"Error: {e}")
        sys.exit(1)