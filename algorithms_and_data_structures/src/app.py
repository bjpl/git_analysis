"""
Adaptive Learning System - Main Application Class
Coordinates all components and manages the application lifecycle.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import sqlite3

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich import print as rprint

from models.user_profile import UserProfile, UserSession, UserProgress
from models.content_models import Topic, Problem, Concept
from models.analytics_models import PerformanceMetrics, LearningAnalytics
from services.curriculum_service import CurriculumService
from services.content_service import ContentService
from services.analytics_service import AnalyticsService
from services.recommendation_engine import RecommendationEngine
from services.adaptive_learning_engine import AdaptiveLearningEngine
from data.database_manager import DatabaseManager
from utils.logging_config import get_logger
from utils.config_manager import ConfigManager


class AdaptiveLearningApp:
    """
    Main application class that coordinates all components and manages
    the application lifecycle.
    """
    
    def __init__(self, config_path: Optional[str] = None, 
                 profile_name: Optional[str] = None, 
                 debug_mode: bool = False):
        """
        Initialize the Adaptive Learning Application.
        
        Args:
            config_path: Path to configuration file
            profile_name: Name of user profile to load
            debug_mode: Enable debug mode
        """
        self.console = Console()
        self.logger = get_logger(__name__)
        self.debug_mode = debug_mode
        
        # Load configuration
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # Initialize database
        self.db_manager = DatabaseManager(
            db_path=self.config.get('database_path', 'data/adaptive_learning.db')
        )
        
        # Initialize services
        self._initialize_services()
        
        # Load or create user profile
        self.user_profile = self._load_user_profile(profile_name)
        
        # Current session tracking
        self.current_session: Optional[UserSession] = None
        
        self.logger.info("Adaptive Learning Application initialized")
    
    def _initialize_services(self):
        """Initialize all application services."""
        try:
            # Core services
            self.curriculum_service = CurriculumService(
                db_manager=self.db_manager,
                config=self.config
            )
            
            self.content_service = ContentService(
                db_manager=self.db_manager,
                config=self.config
            )
            
            self.analytics_service = AnalyticsService(
                db_manager=self.db_manager
            )
            
            # AI/ML services
            self.recommendation_engine = RecommendationEngine(
                db_manager=self.db_manager,
                content_service=self.content_service,
                analytics_service=self.analytics_service
            )
            
            self.adaptive_engine = AdaptiveLearningEngine(
                curriculum_service=self.curriculum_service,
                content_service=self.content_service,
                analytics_service=self.analytics_service,
                recommendation_engine=self.recommendation_engine
            )
            
            self.logger.info("All services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize services: {str(e)}")
            raise
    
    def _load_user_profile(self, profile_name: Optional[str]) -> UserProfile:
        """Load or create user profile."""
        try:
            if profile_name:
                # Try to load existing profile
                profile = self.db_manager.get_user_profile(profile_name)
                if profile:
                    self.logger.info(f"Loaded user profile: {profile_name}")
                    return profile
            
            # Create new profile or load default
            profile_name = profile_name or "default"
            profile = UserProfile(
                name=profile_name,
                created_at=datetime.now(),
                preferences=self.config.get('default_user_preferences', {}),
                learning_goals=[]
            )
            
            # Save new profile
            self.db_manager.save_user_profile(profile)
            self.logger.info(f"Created new user profile: {profile_name}")
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Failed to load user profile: {str(e)}")
            raise
    
    def start_learning_session(self, topic: Optional[str] = None, 
                             difficulty: Optional[str] = None,
                             time_limit: Optional[int] = None) -> None:
        """Start an adaptive learning session."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Initializing learning session...", total=None)
                
                # Create session
                self.current_session = UserSession(
                    user_profile_id=self.user_profile.id,
                    session_type='learning',
                    topic=topic,
                    difficulty=difficulty,
                    time_limit=timedelta(minutes=time_limit) if time_limit else None,
                    started_at=datetime.now()
                )
                
                progress.update(task, description="Loading content...")
                
                # Get personalized content
                if topic:
                    content = self.content_service.get_topic_content(topic, difficulty)
                else:
                    # Get recommended content
                    recommendations = self.recommendation_engine.get_learning_recommendations(
                        self.user_profile
                    )
                    content = recommendations[0] if recommendations else None
                
                if not content:
                    self.console.print("[red]No content available for the specified criteria[/red]")
                    return
                
                progress.update(task, description="Starting adaptive learning...")
                
                # Start adaptive learning session
                self.adaptive_engine.start_session(
                    user_profile=self.user_profile,
                    session=self.current_session,
                    content=content
                )
            
            self.console.print("[green]Learning session started successfully![/green]")
            
        except Exception as e:
            self.logger.error(f"Failed to start learning session: {str(e)}")
            self.console.print(f"[red]Error starting learning session: {str(e)}[/red]")
    
    def start_practice_session(self, topic: Optional[str] = None,
                             problem_count: int = 5,
                             difficulty: Optional[str] = None) -> None:
        """Start a practice session with problems."""
        try:
            self.console.print(f"[cyan]Starting practice session...[/cyan]")
            
            # Get practice problems
            problems = self.content_service.get_practice_problems(
                topic=topic,
                difficulty=difficulty,
                count=problem_count,
                user_profile=self.user_profile
            )
            
            if not problems:
                self.console.print("[red]No practice problems found for the specified criteria[/red]")
                return
            
            # Create session
            self.current_session = UserSession(
                user_profile_id=self.user_profile.id,
                session_type='practice',
                topic=topic,
                difficulty=difficulty,
                started_at=datetime.now()
            )
            
            # Display problems in an interactive format
            self._run_practice_problems(problems)
            
        except Exception as e:
            self.logger.error(f"Failed to start practice session: {str(e)}")
            self.console.print(f"[red]Error starting practice session: {str(e)}[/red]")
    
    def start_quiz_session(self, topic: Optional[str] = None,
                          question_count: int = 10) -> None:
        """Start a quiz session."""
        try:
            self.console.print(f"[cyan]Starting quiz session...[/cyan]")
            
            # Get quiz questions
            questions = self.content_service.generate_quiz_questions(
                topic=topic,
                count=question_count,
                user_profile=self.user_profile
            )
            
            if not questions:
                self.console.print("[red]No quiz questions available[/red]")
                return
            
            # Create session
            self.current_session = UserSession(
                user_profile_id=self.user_profile.id,
                session_type='quiz',
                topic=topic,
                started_at=datetime.now()
            )
            
            # Run quiz
            self._run_quiz(questions)
            
        except Exception as e:
            self.logger.error(f"Failed to start quiz session: {str(e)}")
            self.console.print(f"[red]Error starting quiz session: {str(e)}[/red]")
    
    def show_progress_dashboard(self) -> None:
        """Display user progress dashboard."""
        try:
            progress_data = self.analytics_service.get_user_progress(self.user_profile)
            
            # Create dashboard layout
            layout = Layout()
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="body"),
                Layout(name="footer", size=3)
            )
            
            # Header
            layout["header"].update(
                Panel(
                    f"[bold cyan]Progress Dashboard - {self.user_profile.name}[/bold cyan]",
                    style="bright_blue"
                )
            )
            
            # Body with progress information
            body_layout = Layout()
            body_layout.split_row(
                Layout(name="stats"),
                Layout(name="topics")
            )
            
            # Statistics
            stats_table = self._create_stats_table(progress_data)
            body_layout["stats"].update(Panel(stats_table, title="Statistics"))
            
            # Topics progress
            topics_table = self._create_topics_progress_table(progress_data)
            body_layout["topics"].update(Panel(topics_table, title="Topics Progress"))
            
            layout["body"].update(body_layout)
            
            # Footer
            layout["footer"].update(
                Panel(
                    "[dim]Use 'analytics' command for detailed analysis[/dim]",
                    style="dim"
                )
            )
            
            self.console.print(layout)
            
        except Exception as e:
            self.logger.error(f"Failed to show progress dashboard: {str(e)}")
            self.console.print(f"[red]Error loading progress dashboard: {str(e)}[/red]")
    
    def show_recommendations(self) -> None:
        """Display personalized recommendations."""
        try:
            recommendations = self.recommendation_engine.get_comprehensive_recommendations(
                self.user_profile
            )
            
            if not recommendations:
                self.console.print("[yellow]No recommendations available at this time[/yellow]")
                return
            
            # Display recommendations in categories
            self._display_recommendations(recommendations)
            
        except Exception as e:
            self.logger.error(f"Failed to show recommendations: {str(e)}")
            self.console.print(f"[red]Error generating recommendations: {str(e)}[/red]")
    
    def show_analytics(self, detailed: bool = False) -> None:
        """Display performance analytics."""
        try:
            analytics = self.analytics_service.get_comprehensive_analytics(
                self.user_profile,
                detailed=detailed
            )
            
            self._display_analytics(analytics, detailed)
            
        except Exception as e:
            self.logger.error(f"Failed to show analytics: {str(e)}")
            self.console.print(f"[red]Error loading analytics: {str(e)}[/red]")
    
    def list_topics(self) -> None:
        """List all available topics with progress information."""
        try:
            topics = self.curriculum_service.get_all_topics()
            progress_data = self.analytics_service.get_user_progress(self.user_profile)
            
            # Create topics table
            table = Table(title="Available Topics")
            table.add_column("Topic", style="cyan")
            table.add_column("Difficulty", style="yellow")
            table.add_column("Progress", style="green")
            table.add_column("Problems", justify="right")
            table.add_column("Concepts", justify="right")
            table.add_column("Status")
            
            for topic in topics:
                # Get progress for this topic
                topic_progress = progress_data.get('topics', {}).get(topic.name, {})
                progress_pct = topic_progress.get('completion_percentage', 0)
                
                # Status indicator
                if progress_pct == 0:
                    status = "[red]Not Started[/red]"
                elif progress_pct < 50:
                    status = "[yellow]In Progress[/yellow]"
                elif progress_pct < 100:
                    status = "[blue]Advanced[/blue]"
                else:
                    status = "[green]Completed[/green]"
                
                table.add_row(
                    topic.name,
                    topic.difficulty,
                    f"{progress_pct:.1f}%",
                    str(len(topic.problems)),
                    str(len(topic.concepts)),
                    status
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.logger.error(f"Failed to list topics: {str(e)}")
            self.console.print(f"[red]Error loading topics: {str(e)}[/red]")
    
    def search_content(self, query: str, search_type: str = 'all') -> None:
        """Search for content based on query."""
        try:
            results = self.content_service.search_content(
                query=query,
                search_type=search_type,
                user_profile=self.user_profile
            )
            
            if not results:
                self.console.print(f"[yellow]No results found for: {query}[/yellow]")
                return
            
            self._display_search_results(results, query)
            
        except Exception as e:
            self.logger.error(f"Failed to search content: {str(e)}")
            self.console.print(f"[red]Error performing search: {str(e)}[/red]")
    
    def config_menu(self) -> None:
        """Display and handle configuration menu."""
        try:
            self.console.print("[cyan]Configuration Menu[/cyan]")
            # Implementation for configuration management
            # This would include settings like difficulty preferences, 
            # learning goals, notification settings, etc.
            
            self.console.print("[dim]Configuration menu functionality will be implemented here[/dim]")
            
        except Exception as e:
            self.logger.error(f"Failed to open config menu: {str(e)}")
            self.console.print(f"[red]Error accessing configuration: {str(e)}[/red]")
    
    def _run_practice_problems(self, problems: List[Problem]) -> None:
        """Run through practice problems interactively."""
        # Implementation for interactive problem solving
        self.console.print(f"[green]Starting practice with {len(problems)} problems[/green]")
        
        for i, problem in enumerate(problems, 1):
            self.console.print(f"\n[bold]Problem {i}/{len(problems)}:[/bold]")
            self.console.print(f"[cyan]{problem.title}[/cyan]")
            self.console.print(f"{problem.description}")
            
            # This would include interactive problem solving logic
            self.console.print("[dim]Interactive problem solving will be implemented here[/dim]")
    
    def _run_quiz(self, questions: List[Dict[str, Any]]) -> None:
        """Run quiz questions interactively."""
        self.console.print(f"[green]Starting quiz with {len(questions)} questions[/green]")
        
        # Implementation for interactive quiz
        for i, question in enumerate(questions, 1):
            self.console.print(f"\n[bold]Question {i}/{len(questions)}:[/bold]")
            self.console.print(f"[cyan]{question['question']}[/cyan]")
            
            # This would include interactive quiz logic
            self.console.print("[dim]Interactive quiz functionality will be implemented here[/dim]")
    
    def _create_stats_table(self, progress_data: Dict[str, Any]) -> Table:
        """Create statistics table."""
        table = Table(show_header=False)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        stats = progress_data.get('overall_stats', {})
        table.add_row("Total Study Time", f"{stats.get('total_time', 0)} hours")
        table.add_row("Problems Solved", str(stats.get('problems_solved', 0)))
        table.add_row("Concepts Mastered", str(stats.get('concepts_mastered', 0)))
        table.add_row("Current Streak", f"{stats.get('current_streak', 0)} days")
        table.add_row("Average Score", f"{stats.get('average_score', 0):.1f}%")
        
        return table
    
    def _create_topics_progress_table(self, progress_data: Dict[str, Any]) -> Table:
        """Create topics progress table."""
        table = Table()
        table.add_column("Topic", style="cyan")
        table.add_column("Progress", style="green")
        table.add_column("Score", style="yellow")
        
        topics_data = progress_data.get('topics', {})
        for topic_name, topic_data in topics_data.items():
            progress = f"{topic_data.get('completion_percentage', 0):.1f}%"
            score = f"{topic_data.get('average_score', 0):.1f}%"
            table.add_row(topic_name, progress, score)
        
        return table
    
    def _display_recommendations(self, recommendations: Dict[str, List]) -> None:
        """Display recommendations in organized format."""
        for category, items in recommendations.items():
            if items:
                self.console.print(f"\n[bold cyan]{category.title()}:[/bold cyan]")
                for item in items:
                    self.console.print(f"  • {item}")
    
    def _display_analytics(self, analytics: Dict[str, Any], detailed: bool) -> None:
        """Display analytics information."""
        self.console.print("[bold cyan]Performance Analytics[/bold cyan]")
        
        if detailed:
            # Show detailed analytics
            self.console.print("[dim]Detailed analytics display will be implemented here[/dim]")
        else:
            # Show summary analytics
            self.console.print("[dim]Summary analytics display will be implemented here[/dim]")
    
    def _display_search_results(self, results: Dict[str, List], query: str) -> None:
        """Display search results."""
        self.console.print(f"[green]Search results for: {query}[/green]")
        
        for result_type, items in results.items():
            if items:
                self.console.print(f"\n[bold]{result_type.title()}:[/bold]")
                for item in items:
                    self.console.print(f"  • {item}")
    
    def cleanup(self) -> None:
        """Cleanup resources and save state."""
        try:
            # Save current session if active
            if self.current_session:
                self.current_session.ended_at = datetime.now()
                self.db_manager.save_session(self.current_session)
            
            # Save user profile
            self.db_manager.save_user_profile(self.user_profile)
            
            # Close database connection
            self.db_manager.close()
            
            self.logger.info("Application cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()