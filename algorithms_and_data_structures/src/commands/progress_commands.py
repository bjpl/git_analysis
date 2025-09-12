#!/usr/bin/env python3
"""
Progress Commands - Student progress tracking and analytics

This module provides:
- Track student progress through curricula and content
- View detailed progress reports and analytics
- Set and manage learning goals and milestones
- Generate progress visualizations and charts
- Export progress data for external analysis
- Manage progress notifications and alerts
"""

import json
import asyncio
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta

from .base import BaseCommand, CommandResult, CommandMetadata, CommandCategory
from ..ui.formatter import TerminalFormatter
from ..models.progress import Progress
from ..core.exceptions import CLIError


class ProgressListCommand(BaseCommand):
    """List student progress records with filtering"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="progress-list",
            description="List student progress records",
            category=CommandCategory.CURRICULUM,
            aliases=["progress-ls", "list-progress"],
            examples=[
                "progress-list",
                "progress-list --student 123",
                "progress-list --curriculum 456 --status completed",
                "progress-list --date-from 2024-01-01 --format json",
                "progress-list --content-type lesson --difficulty beginner"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="List student progress records"
        )
        
        # Filtering options
        parser.add_argument(
            '--student',
            type=int,
            help='Filter by student ID'
        )
        parser.add_argument(
            '--curriculum',
            type=int,
            help='Filter by curriculum ID'
        )
        parser.add_argument(
            '--content',
            type=int,
            help='Filter by content ID'
        )
        parser.add_argument(
            '--status',
            choices=['not_started', 'in_progress', 'completed', 'failed'],
            help='Filter by progress status'
        )
        parser.add_argument(
            '--content-type',
            choices=['lesson', 'exercise', 'assessment', 'quiz'],
            help='Filter by content type'
        )
        parser.add_argument(
            '--difficulty',
            choices=['beginner', 'intermediate', 'advanced', 'expert'],
            help='Filter by difficulty level'
        )
        
        # Date filtering
        parser.add_argument(
            '--date-from',
            help='Filter from date (YYYY-MM-DD)'
        )
        parser.add_argument(
            '--date-to',
            help='Filter to date (YYYY-MM-DD)'
        )
        parser.add_argument(
            '--last-days',
            type=int,
            help='Filter last N days'
        )
        
        # Score filtering
        parser.add_argument(
            '--min-score',
            type=float,
            help='Minimum completion score'
        )
        parser.add_argument(
            '--max-score',
            type=float,
            help='Maximum completion score'
        )
        
        # Sorting options
        parser.add_argument(
            '--sort',
            choices=['student', 'content', 'status', 'score', 'started', 'completed'],
            default='started',
            help='Sort field'
        )
        parser.add_argument(
            '--order',
            choices=['asc', 'desc'],
            default='desc',
            help='Sort order'
        )
        
        # Output options
        parser.add_argument(
            '--format',
            choices=['table', 'json', 'summary', 'chart'],
            default='table',
            help='Output format'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Maximum number of results'
        )
        parser.add_argument(
            '--include-details',
            action='store_true',
            help='Include detailed progress information'
        )
        
        return parser
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        try:
            parsed_args = self.parse_args(args)
            
            # Get progress records
            progress_records = await self._get_progress_records(context, parsed_args)
            
            if not progress_records:
                return CommandResult(
                    success=True,
                    message="No progress records found matching the criteria"
                )
            
            # Format output
            if parsed_args.format == 'json':
                output = json.dumps(progress_records, indent=2, default=str)
                print(output)
            elif parsed_args.format == 'summary':
                self._show_summary(context.formatter, progress_records)
            elif parsed_args.format == 'chart':
                self._show_chart(context.formatter, progress_records)
            else:
                self._show_table(context.formatter, progress_records, parsed_args.include_details)
            
            return CommandResult(
                success=True,
                message=f"Found {len(progress_records)} progress record(s)",
                data={'progress_records': progress_records}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to list progress: {e}",
                error=e
            )
    
    async def _get_progress_records(self, context, args) -> List[Dict[str, Any]]:
        """Get progress records with filtering and sorting"""
        # Mock data - replace with actual database query
        mock_progress = [
            {
                'id': 1,
                'student_id': 101,
                'student_name': 'Alice Johnson',
                'curriculum_id': 1,
                'curriculum_name': 'Python Fundamentals',
                'content_id': 1,
                'content_title': 'Introduction to Python',
                'content_type': 'lesson',
                'difficulty': 'beginner',
                'status': 'completed',
                'score': 95.5,
                'started_at': '2024-01-15T09:30:00',
                'completed_at': '2024-01-15T10:15:00',
                'time_spent': 2700,  # seconds
                'attempts': 1,
                'progress_percentage': 100.0
            },
            {
                'id': 2,
                'student_id': 101,
                'student_name': 'Alice Johnson',
                'curriculum_id': 1,
                'curriculum_name': 'Python Fundamentals',
                'content_id': 2,
                'content_title': 'Python Variables Exercise',
                'content_type': 'exercise',
                'difficulty': 'beginner',
                'status': 'in_progress',
                'score': None,
                'started_at': '2024-01-15T10:20:00',
                'completed_at': None,
                'time_spent': 1200,
                'attempts': 0,
                'progress_percentage': 60.0
            },
            {
                'id': 3,
                'student_id': 102,
                'student_name': 'Bob Smith',
                'curriculum_id': 1,
                'curriculum_name': 'Python Fundamentals',
                'content_id': 1,
                'content_title': 'Introduction to Python',
                'content_type': 'lesson',
                'difficulty': 'beginner',
                'status': 'completed',
                'score': 87.3,
                'started_at': '2024-01-16T14:00:00',
                'completed_at': '2024-01-16T15:10:00',
                'time_spent': 4200,
                'attempts': 2,
                'progress_percentage': 100.0
            }
        ]
        
        # Apply filters
        filtered_progress = mock_progress
        
        if args.student:
            filtered_progress = [p for p in filtered_progress if p['student_id'] == args.student]
        
        if args.curriculum:
            filtered_progress = [p for p in filtered_progress if p['curriculum_id'] == args.curriculum]
        
        if args.content:
            filtered_progress = [p for p in filtered_progress if p['content_id'] == args.content]
        
        if args.status:
            filtered_progress = [p for p in filtered_progress if p['status'] == args.status]
        
        if args.content_type:
            filtered_progress = [p for p in filtered_progress if p['content_type'] == args.content_type]
        
        if args.difficulty:
            filtered_progress = [p for p in filtered_progress if p['difficulty'] == args.difficulty]
        
        if args.min_score is not None:
            filtered_progress = [p for p in filtered_progress if p.get('score') and p['score'] >= args.min_score]
        
        if args.max_score is not None:
            filtered_progress = [p for p in filtered_progress if p.get('score') and p['score'] <= args.max_score]
        
        # Date filtering
        if args.date_from or args.date_to or args.last_days:
            if args.last_days:
                date_from = datetime.now() - timedelta(days=args.last_days)
            else:
                date_from = datetime.fromisoformat(args.date_from) if args.date_from else None
            
            date_to = datetime.fromisoformat(args.date_to) if args.date_to else datetime.now()
            
            filtered_progress = [
                p for p in filtered_progress 
                if (not date_from or datetime.fromisoformat(p['started_at']) >= date_from) and
                   datetime.fromisoformat(p['started_at']) <= date_to
            ]
        
        # Apply sorting
        sort_key = {
            'student': lambda x: x['student_name'],
            'content': lambda x: x['content_title'],
            'status': lambda x: x['status'],
            'score': lambda x: x.get('score', 0),
            'started': lambda x: x['started_at'],
            'completed': lambda x: x.get('completed_at', '')
        }.get(args.sort, lambda x: x['started_at'])
        
        reverse = args.order == 'desc'
        filtered_progress.sort(key=sort_key, reverse=reverse)
        
        # Apply limit
        if args.limit:
            filtered_progress = filtered_progress[:args.limit]
        
        return filtered_progress
    
    def _show_table(self, formatter: TerminalFormatter, progress_records: List[Dict[str, Any]], include_details: bool):
        """Show progress records in table format"""
        if include_details:
            headers = ['Student', 'Content', 'Status', 'Score', 'Time', 'Progress', 'Completed']
        else:
            headers = ['Student', 'Content', 'Status', 'Score', 'Progress']
        
        table_data = []
        for record in progress_records:
            time_spent_str = f"{record['time_spent'] // 60}m" if record['time_spent'] else "-"
            
            if include_details:
                table_data.append({
                    'Student': record['student_name'],
                    'Content': record['content_title'][:25] + '...' if len(record['content_title']) > 25 else record['content_title'],
                    'Status': record['status'].upper().replace('_', ' '),
                    'Score': f"{record['score']:.1f}%" if record['score'] else "-",
                    'Time': time_spent_str,
                    'Progress': f"{record['progress_percentage']:.0f}%",
                    'Completed': record['completed_at'][:10] if record['completed_at'] else "-"
                })
            else:
                table_data.append({
                    'Student': record['student_name'],
                    'Content': record['content_title'][:30] + '...' if len(record['content_title']) > 30 else record['content_title'],
                    'Status': record['status'].upper().replace('_', ' '),
                    'Score': f"{record['score']:.1f}%" if record['score'] else "-",
                    'Progress': f"{record['progress_percentage']:.0f}%"
                })
        
        formatter.table(table_data, headers)
    
    def _show_summary(self, formatter: TerminalFormatter, progress_records: List[Dict[str, Any]]):
        """Show progress summary with statistics"""
        total_records = len(progress_records)
        completed = len([p for p in progress_records if p['status'] == 'completed'])
        in_progress = len([p for p in progress_records if p['status'] == 'in_progress'])
        not_started = len([p for p in progress_records if p['status'] == 'not_started'])
        
        # Overall statistics
        formatter.header("Progress Summary", level=2)
        stats = {
            'Total Records': total_records,
            'Completed': f"{completed} ({completed/total_records*100:.1f}%)",
            'In Progress': f"{in_progress} ({in_progress/total_records*100:.1f}%)",
            'Not Started': f"{not_started} ({not_started/total_records*100:.1f}%)"
        }
        formatter.key_value_pairs(stats)
        
        # Score statistics for completed items
        completed_records = [p for p in progress_records if p['status'] == 'completed' and p.get('score')]
        if completed_records:
            scores = [p['score'] for p in completed_records]
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)
            
            formatter.header("Score Statistics", level=2)
            score_stats = {
                'Average Score': f"{avg_score:.1f}%",
                'Minimum Score': f"{min_score:.1f}%",
                'Maximum Score': f"{max_score:.1f}%",
                'Records with Scores': len(completed_records)
            }
            formatter.key_value_pairs(score_stats)
    
    def _show_chart(self, formatter: TerminalFormatter, progress_records: List[Dict[str, Any]]):
        """Show progress as ASCII chart"""
        # Status distribution chart
        status_counts = {}
        for record in progress_records:
            status = record['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        formatter.header("Progress Distribution", level=2)
        max_count = max(status_counts.values()) if status_counts else 1
        
        for status, count in status_counts.items():
            bar_length = int((count / max_count) * 30)
            bar = "█" * bar_length
            percentage = (count / len(progress_records)) * 100
            formatter.info(f"{status.upper().replace('_', ' '):12} {bar} {count} ({percentage:.1f}%)")
        
        # Score distribution for completed items
        completed_scores = [p['score'] for p in progress_records if p['status'] == 'completed' and p.get('score')]
        if completed_scores:
            formatter.header("Score Distribution (Completed)", level=2)
            
            # Create score ranges
            ranges = [(0, 60), (60, 70), (70, 80), (80, 90), (90, 100)]
            range_counts = {f"{r[0]}-{r[1]}%": 0 for r in ranges}
            
            for score in completed_scores:
                for r in ranges:
                    if r[0] <= score <= r[1]:
                        range_counts[f"{r[0]}-{r[1]}%"] += 1
                        break
            
            max_range_count = max(range_counts.values()) if range_counts else 1
            for range_name, count in range_counts.items():
                if count > 0:
                    bar_length = int((count / max_range_count) * 20)
                    bar = "█" * bar_length
                    formatter.info(f"{range_name:8} {bar} {count}")


class ProgressShowCommand(BaseCommand):
    """Show detailed progress information for a student or content"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="progress-show",
            description="Show detailed progress information",
            category=CommandCategory.CURRICULUM,
            aliases=["progress-info", "show-progress"],
            examples=[
                "progress-show --student 123",
                "progress-show --student 123 --curriculum 456",
                "progress-show --content 789",
                "progress-show --student 123 --format json"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="Show detailed progress information"
        )
        
        # Target selection
        parser.add_argument(
            '--student',
            type=int,
            help='Student ID to show progress for'
        )
        parser.add_argument(
            '--curriculum',
            type=int,
            help='Curriculum ID (with --student)'
        )
        parser.add_argument(
            '--content',
            type=int,
            help='Show progress for specific content'
        )
        
        # Display options
        parser.add_argument(
            '--format',
            choices=['detailed', 'json', 'summary'],
            default='detailed',
            help='Output format'
        )
        parser.add_argument(
            '--include-timeline',
            action='store_true',
            help='Include progress timeline'
        )
        parser.add_argument(
            '--include-analytics',
            action='store_true',
            help='Include learning analytics'
        )
        
        return parser
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        try:
            parsed_args = self.parse_args(args)
            
            if not any([parsed_args.student, parsed_args.content]):
                return CommandResult(
                    success=False,
                    message="Please specify --student or --content"
                )
            
            # Get progress data
            if parsed_args.student:
                progress_data = await self._get_student_progress(
                    context, parsed_args.student, parsed_args.curriculum
                )
                title = f"Progress for Student {parsed_args.student}"
            else:
                progress_data = await self._get_content_progress(
                    context, parsed_args.content
                )
                title = f"Progress for Content {parsed_args.content}"
            
            if not progress_data:
                return CommandResult(
                    success=False,
                    message="No progress data found"
                )
            
            # Display progress
            if parsed_args.format == 'json':
                output = json.dumps(progress_data, indent=2, default=str)
                print(output)
            elif parsed_args.format == 'summary':
                self._show_summary_view(context.formatter, progress_data, title)
            else:
                self._show_detailed_view(context.formatter, progress_data, title, parsed_args)
            
            return CommandResult(
                success=True,
                data={'progress_data': progress_data}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to show progress: {e}",
                error=e
            )
    
    async def _get_student_progress(self, context, student_id: int, curriculum_id: Optional[int] = None) -> Dict[str, Any]:
        """Get comprehensive student progress data"""
        # Mock implementation
        return {
            'student_id': student_id,
            'student_name': 'Alice Johnson',
            'email': 'alice.johnson@example.com',
            'enrolled_date': '2024-01-10',
            'curricula': [
                {
                    'curriculum_id': 1,
                    'curriculum_name': 'Python Fundamentals',
                    'enrollment_date': '2024-01-10',
                    'status': 'active',
                    'overall_progress': 75.0,
                    'completed_modules': 2,
                    'total_modules': 4,
                    'completed_content': 8,
                    'total_content': 15,
                    'average_score': 91.2,
                    'time_spent': 18000,  # seconds
                    'last_activity': '2024-01-16T15:30:00',
                    'modules': [
                        {
                            'module_id': 1,
                            'module_name': 'Getting Started',
                            'status': 'completed',
                            'progress': 100.0,
                            'score': 95.5,
                            'completed_at': '2024-01-15T16:20:00',
                            'content_items': [
                                {
                                    'content_id': 1,
                                    'title': 'Introduction to Python',
                                    'type': 'lesson',
                                    'status': 'completed',
                                    'score': 95.5,
                                    'time_spent': 2700
                                },
                                {
                                    'content_id': 2,
                                    'title': 'Python Variables Exercise',
                                    'type': 'exercise',
                                    'status': 'completed',
                                    'score': 88.0,
                                    'time_spent': 1800
                                }
                            ]
                        },
                        {
                            'module_id': 2,
                            'module_name': 'Data Types',
                            'status': 'in_progress',
                            'progress': 60.0,
                            'score': None,
                            'completed_at': None,
                            'content_items': [
                                {
                                    'content_id': 3,
                                    'title': 'Python Data Types',
                                    'type': 'lesson',
                                    'status': 'completed',
                                    'score': 92.0,
                                    'time_spent': 3200
                                },
                                {
                                    'content_id': 4,
                                    'title': 'Working with Strings',
                                    'type': 'exercise',
                                    'status': 'in_progress',
                                    'score': None,
                                    'time_spent': 1200
                                }
                            ]
                        }
                    ]
                }
            ],
            'learning_streaks': {
                'current_streak': 7,
                'longest_streak': 12,
                'weekly_goal': 5,
                'weekly_progress': 4
            },
            'achievements': [
                {'name': 'First Steps', 'earned_at': '2024-01-10T10:00:00'},
                {'name': 'Quick Learner', 'earned_at': '2024-01-15T16:20:00'}
            ]
        }
    
    async def _get_content_progress(self, context, content_id: int) -> Dict[str, Any]:
        """Get progress data for specific content across all students"""
        # Mock implementation
        return {
            'content_id': content_id,
            'content_title': 'Introduction to Python',
            'content_type': 'lesson',
            'curriculum_name': 'Python Fundamentals',
            'module_name': 'Getting Started',
            'total_enrolled': 245,
            'started': 230,
            'completed': 210,
            'completion_rate': 91.3,
            'average_score': 89.7,
            'average_time': 3200,
            'difficulty_rating': 4.2,
            'student_progress': [
                {
                    'student_id': 101,
                    'student_name': 'Alice Johnson',
                    'status': 'completed',
                    'score': 95.5,
                    'time_spent': 2700,
                    'completed_at': '2024-01-15T10:15:00'
                },
                {
                    'student_id': 102,
                    'student_name': 'Bob Smith',
                    'status': 'completed',
                    'score': 87.3,
                    'time_spent': 4200,
                    'completed_at': '2024-01-16T15:10:00'
                }
            ]
        }
    
    def _show_detailed_view(self, formatter: TerminalFormatter, progress_data: Dict[str, Any], title: str, args):
        """Show detailed progress view"""
        formatter.header(title, level=1)
        
        if 'student_name' in progress_data:
            self._show_student_detailed(formatter, progress_data, args)
        else:
            self._show_content_detailed(formatter, progress_data, args)
    
    def _show_student_detailed(self, formatter: TerminalFormatter, data: Dict[str, Any], args):
        """Show detailed student progress"""
        # Student info
        formatter.header("Student Information", level=2)
        student_info = {
            'Name': data['student_name'],
            'Email': data.get('email', 'Not provided'),
            'Enrolled': data['enrolled_date'],
            'Active Curricula': len(data['curricula'])
        }
        formatter.key_value_pairs(student_info)
        
        # Learning streaks
        if 'learning_streaks' in data:
            formatter.header("Learning Activity", level=2)
            streaks = data['learning_streaks']
            streak_info = {
                'Current Streak': f"{streaks['current_streak']} days",
                'Longest Streak': f"{streaks['longest_streak']} days",
                'Weekly Goal': f"{streaks['weekly_progress']}/{streaks['weekly_goal']} days"
            }
            formatter.key_value_pairs(streak_info)
        
        # Curricula progress
        for curriculum in data['curricula']:
            formatter.header(f"Curriculum: {curriculum['curriculum_name']}", level=2)
            
            # Overall curriculum stats
            overall_stats = {
                'Overall Progress': f"{curriculum['overall_progress']:.1f}%",
                'Modules Completed': f"{curriculum['completed_modules']}/{curriculum['total_modules']}",
                'Content Completed': f"{curriculum['completed_content']}/{curriculum['total_content']}",
                'Average Score': f"{curriculum['average_score']:.1f}%" if curriculum['average_score'] else "N/A",
                'Time Spent': f"{curriculum['time_spent'] // 3600}h {(curriculum['time_spent'] % 3600) // 60}m",
                'Last Activity': curriculum['last_activity'][:16]
            }
            formatter.key_value_pairs(overall_stats, indent=1)
            
            # Modules progress
            if args.include_timeline:
                formatter.header("Modules Progress", level=3)
                for module in curriculum['modules']:
                    status_icon = "✅" if module['status'] == 'completed' else "🔄" if module['status'] == 'in_progress' else "⏳"
                    
                    formatter.info(f"  {status_icon} {module['module_name']} - {module['progress']:.0f}%")
                    
                    if module.get('content_items'):
                        for content in module['content_items']:
                            content_icon = {
                                'lesson': '📚',
                                'exercise': '💪',
                                'quiz': '❓',
                                'assessment': '📊'
                            }.get(content['type'], '📄')
                            
                            score_text = f" ({content['score']:.1f}%)" if content.get('score') else ""
                            time_text = f" - {content['time_spent']//60}m" if content.get('time_spent') else ""
                            
                            formatter.info(f"    {content_icon} {content['title']}{score_text}{time_text}")
        
        # Achievements
        if 'achievements' in data and data['achievements']:
            formatter.header("Achievements", level=2)
            for achievement in data['achievements']:
                formatter.info(f"🏆 {achievement['name']} - {achievement['earned_at'][:10]}")
    
    def _show_content_detailed(self, formatter: TerminalFormatter, data: Dict[str, Any], args):
        """Show detailed content progress across students"""
        # Content info
        formatter.header("Content Information", level=2)
        content_info = {
            'Title': data['content_title'],
            'Type': data['content_type'].title(),
            'Curriculum': data['curriculum_name'],
            'Module': data['module_name']
        }
        formatter.key_value_pairs(content_info)
        
        # Progress statistics
        formatter.header("Progress Statistics", level=2)
        stats = {
            'Total Enrolled': data['total_enrolled'],
            'Started': f"{data['started']} ({data['started']/data['total_enrolled']*100:.1f}%)",
            'Completed': f"{data['completed']} ({data['completion_rate']:.1f}%)",
            'Average Score': f"{data['average_score']:.1f}%",
            'Average Time': f"{data['average_time']//60} minutes",
            'Difficulty Rating': f"{data['difficulty_rating']:.1f}/5.0"
        }
        formatter.key_value_pairs(stats)
        
        # Student progress table
        if args.include_analytics and data.get('student_progress'):
            formatter.header("Top Student Performance", level=2)
            
            # Sort by score descending
            top_students = sorted(
                [s for s in data['student_progress'] if s.get('score')],
                key=lambda x: x['score'],
                reverse=True
            )[:10]  # Top 10
            
            table_data = []
            for student in top_students:
                table_data.append({
                    'Student': student['student_name'],
                    'Status': student['status'].upper(),
                    'Score': f"{student['score']:.1f}%" if student.get('score') else "-",
                    'Time': f"{student['time_spent']//60}m" if student.get('time_spent') else "-",
                    'Completed': student['completed_at'][:10] if student.get('completed_at') else "-"
                })
            
            formatter.table(table_data)
    
    def _show_summary_view(self, formatter: TerminalFormatter, progress_data: Dict[str, Any], title: str):
        """Show summary progress view"""
        formatter.header(title, level=2)
        
        if 'student_name' in progress_data:
            # Student summary
            total_progress = sum(c['overall_progress'] for c in progress_data['curricula']) / len(progress_data['curricula'])
            total_content_completed = sum(c['completed_content'] for c in progress_data['curricula'])
            total_content = sum(c['total_content'] for c in progress_data['curricula'])
            
            summary = {
                'Student': progress_data['student_name'],
                'Overall Progress': f"{total_progress:.1f}%",
                'Content Completed': f"{total_content_completed}/{total_content}",
                'Active Curricula': len(progress_data['curricula']),
                'Current Streak': f"{progress_data.get('learning_streaks', {}).get('current_streak', 0)} days"
            }
        else:
            # Content summary
            summary = {
                'Content': progress_data['content_title'],
                'Completion Rate': f"{progress_data['completion_rate']:.1f}%",
                'Average Score': f"{progress_data['average_score']:.1f}%",
                'Students Enrolled': progress_data['total_enrolled'],
                'Students Completed': progress_data['completed']
            }
        
        formatter.key_value_pairs(summary)


class ProgressTrackCommand(BaseCommand):
    """Track or update student progress manually"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="progress-track",
            description="Track or update student progress",
            category=CommandCategory.CURRICULUM,
            aliases=["progress-update", "track-progress"],
            examples=[
                "progress-track --student 123 --content 456 --status completed --score 95",
                "progress-track --student 123 --content 456 --time-spent 1800",
                "progress-track --bulk-file progress_updates.json"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="Track or update student progress"
        )
        
        # Individual tracking
        parser.add_argument(
            '--student',
            type=int,
            help='Student ID'
        )
        parser.add_argument(
            '--content',
            type=int,
            help='Content ID'
        )
        parser.add_argument(
            '--status',
            choices=['not_started', 'in_progress', 'completed', 'failed'],
            help='Progress status'
        )
        parser.add_argument(
            '--score',
            type=float,
            help='Completion score (0-100)'
        )
        parser.add_argument(
            '--time-spent',
            type=int,
            help='Time spent in seconds'
        )
        parser.add_argument(
            '--notes',
            help='Additional notes'
        )
        
        # Bulk operations
        parser.add_argument(
            '--bulk-file',
            help='JSON file with bulk progress updates'
        )
        
        # Options
        parser.add_argument(
            '--notify',
            action='store_true',
            help='Send notification to student'
        )
        
        return parser
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        try:
            parsed_args = self.parse_args(args)
            
            if parsed_args.bulk_file:
                return await self._handle_bulk_update(context, parsed_args)
            else:
                return await self._handle_single_update(context, parsed_args)
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to track progress: {e}",
                error=e
            )
    
    async def _handle_single_update(self, context, args) -> CommandResult:
        """Handle single progress update"""
        if not args.student or not args.content:
            return CommandResult(
                success=False,
                message="Both --student and --content are required for individual tracking"
            )
        
        # Prepare update data
        update_data = {
            'student_id': args.student,
            'content_id': args.content,
            'updated_at': datetime.now().isoformat()
        }
        
        if args.status:
            update_data['status'] = args.status
        if args.score is not None:
            update_data['score'] = args.score
        if args.time_spent is not None:
            update_data['time_spent'] = args.time_spent
        if args.notes:
            update_data['notes'] = args.notes
        
        # Validate update
        validation_errors = self._validate_update(update_data)
        if validation_errors:
            return CommandResult(
                success=False,
                message="Validation errors:\n" + "\n".join(validation_errors)
            )
        
        # Show preview
        if not args.force:
            context.formatter.header("Progress Update Preview", level=2)
            context.formatter.key_value_pairs(update_data)
            
            if not self.confirm_action("Apply this progress update?", default=True):
                return CommandResult(
                    success=False,
                    message="Update cancelled"
                )
        
        # Apply update
        progress_id = await self._update_progress(context, update_data)
        
        # Send notification if requested
        if args.notify:
            await self._send_notification(context, args.student, update_data)
        
        context.formatter.success(
            f"Progress updated for student {args.student} on content {args.content}"
        )
        
        return CommandResult(
            success=True,
            message="Progress updated successfully",
            data={'progress_id': progress_id, 'update': update_data}
        )
    
    async def _handle_bulk_update(self, context, args) -> CommandResult:
        """Handle bulk progress updates from file"""
        file_path = Path(args.bulk_file)
        if not file_path.exists():
            return CommandResult(
                success=False,
                message=f"File not found: {args.bulk_file}"
            )
        
        try:
            with open(file_path, 'r') as f:
                bulk_updates = json.load(f)
        except json.JSONDecodeError as e:
            return CommandResult(
                success=False,
                message=f"Invalid JSON in file: {e}"
            )
        
        if not isinstance(bulk_updates, list):
            return CommandResult(
                success=False,
                message="Bulk file must contain a list of progress updates"
            )
        
        # Validate all updates
        validation_errors = []
        for i, update in enumerate(bulk_updates):
            errors = self._validate_update(update)
            if errors:
                validation_errors.extend([f"Update {i+1}: {error}" for error in errors])
        
        if validation_errors:
            return CommandResult(
                success=False,
                message="Validation errors:\n" + "\n".join(validation_errors)
            )
        
        # Show preview
        context.formatter.header(f"Bulk Update Preview ({len(bulk_updates)} updates)", level=2)
        
        # Show summary
        students = set(u.get('student_id') for u in bulk_updates if u.get('student_id'))
        content_items = set(u.get('content_id') for u in bulk_updates if u.get('content_id'))
        
        summary = {
            'Total Updates': len(bulk_updates),
            'Students Affected': len(students),
            'Content Items': len(content_items)
        }
        context.formatter.key_value_pairs(summary)
        
        if not args.force:
            if not self.confirm_action("Apply all progress updates?", default=True):
                return CommandResult(
                    success=False,
                    message="Bulk update cancelled"
                )
        
        # Apply updates
        successful_updates = 0
        failed_updates = []
        
        with context.formatter.progress_bar(len(bulk_updates), "Updating progress") as pbar:
            for i, update in enumerate(bulk_updates):
                try:
                    await self._update_progress(context, update)
                    successful_updates += 1
                except Exception as e:
                    failed_updates.append((i + 1, str(e)))
                
                pbar.update()
        
        # Show results
        if failed_updates:
            context.formatter.warning(f"{len(failed_updates)} updates failed:")
            for update_num, error in failed_updates[:5]:  # Show first 5 errors
                context.formatter.error(f"Update {update_num}: {error}")
            
            if len(failed_updates) > 5:
                context.formatter.info(f"... and {len(failed_updates) - 5} more errors")
        
        context.formatter.success(
            f"Bulk update completed: {successful_updates}/{len(bulk_updates)} successful"
        )
        
        return CommandResult(
            success=len(failed_updates) == 0,
            message=f"Bulk update completed with {successful_updates} successful and {len(failed_updates)} failed updates",
            data={
                'successful_updates': successful_updates,
                'failed_updates': len(failed_updates),
                'errors': failed_updates
            }
        )
    
    def _validate_update(self, update_data: Dict[str, Any]) -> List[str]:
        """Validate progress update data"""
        errors = []
        
        if not update_data.get('student_id'):
            errors.append("Student ID is required")
        
        if not update_data.get('content_id'):
            errors.append("Content ID is required")
        
        if 'score' in update_data:
            score = update_data['score']
            if not isinstance(score, (int, float)) or score < 0 or score > 100:
                errors.append("Score must be a number between 0 and 100")
        
        if 'time_spent' in update_data:
            time_spent = update_data['time_spent']
            if not isinstance(time_spent, int) or time_spent < 0:
                errors.append("Time spent must be a non-negative integer (seconds)")
        
        if 'status' in update_data:
            status = update_data['status']
            if status not in ['not_started', 'in_progress', 'completed', 'failed']:
                errors.append("Invalid status value")
        
        return errors
    
    async def _update_progress(self, context, update_data: Dict[str, Any]) -> int:
        """Update progress in database"""
        # Mock implementation - replace with actual database update
        progress_id = hash(f"{update_data['student_id']}_{update_data['content_id']}_{datetime.now()}") % 10000
        
        # In real implementation:
        # progress = await Progress.get_or_create(
        #     student_id=update_data['student_id'],
        #     content_id=update_data['content_id']
        # )
        # progress.update(**update_data)
        # await progress.save()
        
        return progress_id
    
    async def _send_notification(self, context, student_id: int, update_data: Dict[str, Any]):
        """Send notification to student about progress update"""
        # Mock implementation - replace with actual notification system
        context.formatter.info(f"Notification sent to student {student_id}")


class ProgressAnalyticsCommand(BaseCommand):
    """Generate progress analytics and reports"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="progress-analytics",
            description="Generate progress analytics and reports",
            category=CommandCategory.CURRICULUM,
            aliases=["progress-report", "analytics"],
            examples=[
                "progress-analytics --type overview",
                "progress-analytics --type curriculum --curriculum 123",
                "progress-analytics --type student-performance --export csv",
                "progress-analytics --type engagement --date-range 30"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="Generate progress analytics and reports"
        )
        
        # Report type
        parser.add_argument(
            '--type',
            choices=['overview', 'curriculum', 'student-performance', 'engagement', 'completion-rates'],
            default='overview',
            help='Type of analytics report'
        )
        
        # Filters
        parser.add_argument(
            '--curriculum',
            type=int,
            help='Curriculum ID for curriculum-specific reports'
        )
        parser.add_argument(
            '--date-range',
            type=int,
            help='Number of days to include in analysis'
        )
        parser.add_argument(
            '--student-group',
            help='Filter by student group or cohort'
        )
        
        # Output options
        parser.add_argument(
            '--format',
            choices=['report', 'json', 'chart'],
            default='report',
            help='Output format'
        )
        parser.add_argument(
            '--export',
            choices=['csv', 'json', 'pdf'],
            help='Export format for the report'
        )
        parser.add_argument(
            '--output-file',
            help='Output file path for export'
        )
        
        return parser
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        try:
            parsed_args = self.parse_args(args)
            
            # Generate analytics based on type
            if parsed_args.type == 'overview':
                analytics_data = await self._generate_overview_analytics(context, parsed_args)
            elif parsed_args.type == 'curriculum':
                analytics_data = await self._generate_curriculum_analytics(context, parsed_args)
            elif parsed_args.type == 'student-performance':
                analytics_data = await self._generate_performance_analytics(context, parsed_args)
            elif parsed_args.type == 'engagement':
                analytics_data = await self._generate_engagement_analytics(context, parsed_args)
            elif parsed_args.type == 'completion-rates':
                analytics_data = await self._generate_completion_analytics(context, parsed_args)
            
            # Display analytics
            if parsed_args.format == 'json':
                output = json.dumps(analytics_data, indent=2, default=str)
                print(output)
            elif parsed_args.format == 'chart':
                self._show_analytics_charts(context.formatter, analytics_data, parsed_args.type)
            else:
                self._show_analytics_report(context.formatter, analytics_data, parsed_args.type)
            
            # Export if requested
            if parsed_args.export:
                export_path = await self._export_analytics(
                    context, analytics_data, parsed_args.export, 
                    parsed_args.output_file, parsed_args.type
                )
                context.formatter.success(f"Analytics exported to: {export_path}")
            
            return CommandResult(
                success=True,
                message=f"{parsed_args.type.title()} analytics generated successfully",
                data={'analytics': analytics_data}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to generate analytics: {e}",
                error=e
            )
    
    async def _generate_overview_analytics(self, context, args) -> Dict[str, Any]:
        """Generate overview analytics"""
        # Mock implementation
        return {
            'report_type': 'overview',
            'generated_at': datetime.now().isoformat(),
            'date_range_days': args.date_range or 30,
            'total_students': 1250,
            'active_students': 890,
            'total_curricula': 15,
            'total_content_items': 420,
            'overall_completion_rate': 73.5,
            'average_engagement_score': 8.2,
            'top_performing_curricula': [
                {'name': 'Python Fundamentals', 'completion_rate': 89.2, 'avg_score': 91.5},
                {'name': 'Web Development', 'completion_rate': 76.8, 'avg_score': 87.3},
                {'name': 'Data Science', 'completion_rate': 65.4, 'avg_score': 85.7}
            ],
            'student_activity_trend': {
                'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                'active_students': [780, 820, 865, 890],
                'completions': [145, 167, 189, 203]
            }
        }
    
    async def _generate_curriculum_analytics(self, context, args) -> Dict[str, Any]:
        """Generate curriculum-specific analytics"""
        # Mock implementation
        curriculum_id = args.curriculum or 1
        
        return {
            'report_type': 'curriculum',
            'curriculum_id': curriculum_id,
            'curriculum_name': 'Python Fundamentals',
            'generated_at': datetime.now().isoformat(),
            'enrollment_stats': {
                'total_enrolled': 245,
                'active_students': 189,
                'completed_students': 156,
                'completion_rate': 63.7
            },
            'module_performance': [
                {
                    'module_name': 'Getting Started',
                    'completion_rate': 92.7,
                    'avg_score': 88.5,
                    'avg_time_hours': 2.3,
                    'difficulty_rating': 3.8
                },
                {
                    'module_name': 'Data Types',
                    'completion_rate': 78.4,
                    'avg_score': 85.2,
                    'avg_time_hours': 3.1,
                    'difficulty_rating': 4.2
                }
            ],
            'content_analytics': {
                'most_challenging': [
                    {'title': 'Advanced Functions', 'completion_rate': 45.2, 'avg_attempts': 2.8},
                    {'title': 'Object-Oriented Programming', 'completion_rate': 52.1, 'avg_attempts': 2.3}
                ],
                'highest_rated': [
                    {'title': 'Introduction to Python', 'rating': 4.8, 'completion_rate': 96.3},
                    {'title': 'Basic Syntax', 'rating': 4.6, 'completion_rate': 89.7}
                ]
            },
            'time_analysis': {
                'avg_completion_time_days': 14.2,
                'fastest_completion_days': 3,
                'slowest_completion_days': 45,
                'peak_activity_hours': [14, 15, 16, 20, 21]  # 2-4 PM and 8-9 PM
            }
        }
    
    async def _generate_performance_analytics(self, context, args) -> Dict[str, Any]:
        """Generate student performance analytics"""
        # Mock implementation
        return {
            'report_type': 'student_performance',
            'generated_at': datetime.now().isoformat(),
            'score_distribution': {
                '0-60': 8,
                '60-70': 23,
                '70-80': 67,
                '80-90': 134,
                '90-100': 98
            },
            'performance_metrics': {
                'average_score': 82.4,
                'median_score': 84.5,
                'top_10_percent_threshold': 94.2,
                'bottom_10_percent_threshold': 62.8
            },
            'improvement_trends': {
                'students_improving': 201,
                'students_declining': 45,
                'students_stable': 84,
                'avg_improvement_rate': 12.3
            },
            'high_performers': [
                {'student_name': 'Alice Johnson', 'avg_score': 96.8, 'completion_rate': 100},
                {'student_name': 'Charlie Brown', 'avg_score': 94.2, 'completion_rate': 98},
                {'student_name': 'Diana Prince', 'avg_score': 93.7, 'completion_rate': 96}
            ],
            'at_risk_students': [
                {'student_name': 'Student A', 'avg_score': 58.2, 'completion_rate': 23, 'last_activity': '2024-01-10'},
                {'student_name': 'Student B', 'avg_score': 62.5, 'completion_rate': 34, 'last_activity': '2024-01-12'}
            ]
        }
    
    async def _generate_engagement_analytics(self, context, args) -> Dict[str, Any]:
        """Generate engagement analytics"""
        # Mock implementation
        return {
            'report_type': 'engagement',
            'generated_at': datetime.now().isoformat(),
            'date_range_days': args.date_range or 30,
            'engagement_metrics': {
                'daily_active_users': 156,
                'avg_session_duration_minutes': 42.3,
                'avg_sessions_per_user': 4.2,
                'bounce_rate': 12.4
            },
            'activity_patterns': {
                'peak_hours': [14, 15, 16, 20, 21],
                'peak_days': ['Tuesday', 'Wednesday', 'Thursday'],
                'weekend_activity_rate': 23.5
            },
            'engagement_by_content_type': {
                'lesson': {'avg_time_minutes': 28.5, 'completion_rate': 78.3},
                'exercise': {'avg_time_minutes': 35.2, 'completion_rate': 68.7},
                'quiz': {'avg_time_minutes': 12.8, 'completion_rate': 84.1},
                'assessment': {'avg_time_minutes': 45.6, 'completion_rate': 72.9}
            },
            'retention_metrics': {
                'day_1_retention': 89.2,
                'day_7_retention': 67.8,
                'day_30_retention': 45.3,
                'avg_days_to_completion': 18.7
            }
        }
    
    async def _generate_completion_analytics(self, context, args) -> Dict[str, Any]:
        """Generate completion rate analytics"""
        # Mock implementation
        return {
            'report_type': 'completion_rates',
            'generated_at': datetime.now().isoformat(),
            'overall_completion_rate': 73.5,
            'completion_by_curriculum': [
                {'name': 'Python Fundamentals', 'rate': 89.2, 'enrolled': 245, 'completed': 219},
                {'name': 'Web Development', 'rate': 76.8, 'enrolled': 189, 'completed': 145},
                {'name': 'Data Science', 'rate': 65.4, 'enrolled': 156, 'completed': 102}
            ],
            'completion_by_difficulty': {
                'beginner': 84.7,
                'intermediate': 72.3,
                'advanced': 58.9,
                'expert': 41.2
            },
            'time_to_completion': {
                'avg_days': 21.4,
                'median_days': 18,
                'percentiles': {
                    '25th': 12,
                    '50th': 18,
                    '75th': 28,
                    '90th': 42
                }
            },
            'drop_off_analysis': {
                'common_exit_points': [
                    {'content': 'Advanced Functions', 'exit_rate': 23.4},
                    {'content': 'Object-Oriented Programming', 'exit_rate': 18.7},
                    {'content': 'Error Handling', 'exit_rate': 15.2}
                ],
                'early_dropout_rate': 8.9,
                'mid_course_dropout_rate': 12.4
            }
        }
    
    def _show_analytics_report(self, formatter: TerminalFormatter, data: Dict[str, Any], report_type: str):
        """Show analytics report in formatted text"""
        formatter.header(f"{report_type.replace('_', ' ').title()} Analytics Report", level=1)
        formatter.info(f"Generated: {data['generated_at'][:16]}")
        
        if report_type == 'overview':
            self._show_overview_report(formatter, data)
        elif report_type == 'curriculum':
            self._show_curriculum_report(formatter, data)
        elif report_type == 'student_performance':
            self._show_performance_report(formatter, data)
        elif report_type == 'engagement':
            self._show_engagement_report(formatter, data)
        elif report_type == 'completion_rates':
            self._show_completion_report(formatter, data)
    
    def _show_overview_report(self, formatter: TerminalFormatter, data: Dict[str, Any]):
        """Show overview analytics report"""
        # Key metrics
        formatter.header("Key Metrics", level=2)
        metrics = {
            'Total Students': data['total_students'],
            'Active Students': f"{data['active_students']} ({data['active_students']/data['total_students']*100:.1f}%)",
            'Total Curricula': data['total_curricula'],
            'Content Items': data['total_content_items'],
            'Overall Completion Rate': f"{data['overall_completion_rate']:.1f}%",
            'Engagement Score': f"{data['average_engagement_score']:.1f}/10.0"
        }
        formatter.key_value_pairs(metrics)
        
        # Top performing curricula
        formatter.header("Top Performing Curricula", level=2)
        top_curricula_data = []
        for curriculum in data['top_performing_curricula']:
            top_curricula_data.append({
                'Curriculum': curriculum['name'],
                'Completion Rate': f"{curriculum['completion_rate']:.1f}%",
                'Average Score': f"{curriculum['avg_score']:.1f}%"
            })
        formatter.table(top_curricula_data)
    
    def _show_curriculum_report(self, formatter: TerminalFormatter, data: Dict[str, Any]):
        """Show curriculum analytics report"""
        formatter.info(f"Curriculum: {data['curriculum_name']} (ID: {data['curriculum_id']})")
        
        # Enrollment stats
        formatter.header("Enrollment Statistics", level=2)
        enrollment = data['enrollment_stats']
        formatter.key_value_pairs({
            'Total Enrolled': enrollment['total_enrolled'],
            'Active Students': enrollment['active_students'],
            'Completed Students': enrollment['completed_students'],
            'Completion Rate': f"{enrollment['completion_rate']:.1f}%"
        })
        
        # Module performance
        formatter.header("Module Performance", level=2)
        module_data = []
        for module in data['module_performance']:
            module_data.append({
                'Module': module['module_name'],
                'Completion': f"{module['completion_rate']:.1f}%",
                'Avg Score': f"{module['avg_score']:.1f}%",
                'Avg Time': f"{module['avg_time_hours']:.1f}h",
                'Difficulty': f"{module['difficulty_rating']:.1f}/5"
            })
        formatter.table(module_data)
    
    def _show_performance_report(self, formatter: TerminalFormatter, data: Dict[str, Any]):
        """Show performance analytics report"""
        # Performance metrics
        formatter.header("Performance Metrics", level=2)
        metrics = data['performance_metrics']
        formatter.key_value_pairs({
            'Average Score': f"{metrics['average_score']:.1f}%",
            'Median Score': f"{metrics['median_score']:.1f}%",
            'Top 10% Threshold': f"{metrics['top_10_percent_threshold']:.1f}%",
            'Bottom 10% Threshold': f"{metrics['bottom_10_percent_threshold']:.1f}%"
        })
        
        # Score distribution
        formatter.header("Score Distribution", level=2)
        for range_name, count in data['score_distribution'].items():
            percentage = (count / sum(data['score_distribution'].values())) * 100
            bar_length = int((count / max(data['score_distribution'].values())) * 30)
            bar = "█" * bar_length
            formatter.info(f"{range_name:8} {bar} {count} ({percentage:.1f}%)")
        
        # High performers
        if data.get('high_performers'):
            formatter.header("High Performers", level=2)
            performer_data = []
            for student in data['high_performers']:
                performer_data.append({
                    'Student': student['student_name'],
                    'Avg Score': f"{student['avg_score']:.1f}%",
                    'Completion Rate': f"{student['completion_rate']:.0f}%"
                })
            formatter.table(performer_data)
    
    def _show_engagement_report(self, formatter: TerminalFormatter, data: Dict[str, Any]):
        """Show engagement analytics report"""
        # Engagement metrics
        formatter.header("Engagement Metrics", level=2)
        metrics = data['engagement_metrics']
        formatter.key_value_pairs({
            'Daily Active Users': metrics['daily_active_users'],
            'Avg Session Duration': f"{metrics['avg_session_duration_minutes']:.1f} minutes",
            'Avg Sessions per User': f"{metrics['avg_sessions_per_user']:.1f}",
            'Bounce Rate': f"{metrics['bounce_rate']:.1f}%"
        })
        
        # Activity patterns
        formatter.header("Activity Patterns", level=2)
        patterns = data['activity_patterns']
        formatter.info(f"Peak Hours: {', '.join(map(str, patterns['peak_hours']))}")
        formatter.info(f"Peak Days: {', '.join(patterns['peak_days'])}")
        formatter.info(f"Weekend Activity: {patterns['weekend_activity_rate']:.1f}%")
        
        # Retention metrics
        formatter.header("Retention Metrics", level=2)
        retention = data['retention_metrics']
        formatter.key_value_pairs({
            'Day 1 Retention': f"{retention['day_1_retention']:.1f}%",
            'Day 7 Retention': f"{retention['day_7_retention']:.1f}%",
            'Day 30 Retention': f"{retention['day_30_retention']:.1f}%",
            'Avg Days to Completion': f"{retention['avg_days_to_completion']:.1f}"
        })
    
    def _show_completion_report(self, formatter: TerminalFormatter, data: Dict[str, Any]):
        """Show completion analytics report"""
        formatter.info(f"Overall Completion Rate: {data['overall_completion_rate']:.1f}%")
        
        # Completion by curriculum
        formatter.header("Completion by Curriculum", level=2)
        curriculum_data = []
        for curriculum in data['completion_by_curriculum']:
            curriculum_data.append({
                'Curriculum': curriculum['name'],
                'Rate': f"{curriculum['rate']:.1f}%",
                'Enrolled': curriculum['enrolled'],
                'Completed': curriculum['completed']
            })
        formatter.table(curriculum_data)
        
        # Time to completion
        formatter.header("Time to Completion", level=2)
        time_stats = data['time_to_completion']
        formatter.key_value_pairs({
            'Average': f"{time_stats['avg_days']:.1f} days",
            'Median': f"{time_stats['median_days']} days",
            '25th Percentile': f"{time_stats['percentiles']['25th']} days",
            '75th Percentile': f"{time_stats['percentiles']['75th']} days",
            '90th Percentile': f"{time_stats['percentiles']['90th']} days"
        })
    
    def _show_analytics_charts(self, formatter: TerminalFormatter, data: Dict[str, Any], report_type: str):
        """Show analytics as ASCII charts"""
        formatter.header(f"{report_type.replace('_', ' ').title()} Charts", level=1)
        
        # Show relevant charts based on report type
        if report_type == 'overview' and 'student_activity_trend' in data:
            trend = data['student_activity_trend']
            formatter.header("Active Students Trend", level=2)
            
            max_value = max(trend['active_students'])
            for i, (label, value) in enumerate(zip(trend['labels'], trend['active_students'])):
                bar_length = int((value / max_value) * 40)
                bar = "█" * bar_length
                formatter.info(f"{label:8} {bar} {value}")
        
        elif report_type == 'student_performance' and 'score_distribution' in data:
            formatter.header("Score Distribution", level=2)
            
            max_count = max(data['score_distribution'].values())
            for range_name, count in data['score_distribution'].items():
                bar_length = int((count / max_count) * 30)
                bar = "█" * bar_length
                percentage = (count / sum(data['score_distribution'].values())) * 100
                formatter.info(f"{range_name:8} {bar} {count} ({percentage:.1f}%)")
    
    async def _export_analytics(self, context, data: Dict[str, Any], export_format: str, 
                               output_file: Optional[str], report_type: str) -> str:
        """Export analytics to file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{report_type}_analytics_{timestamp}.{export_format}"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if export_format == 'json':
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        elif export_format == 'csv':
            # Convert data to CSV format (simplified)
            import csv
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Report Type', 'Generated At'])
                writer.writerow([data['report_type'], data['generated_at']])
                # Add more specific CSV formatting based on report type
        elif export_format == 'pdf':
            # Mock PDF export - would use a PDF library in real implementation
            with open(output_path.with_suffix('.txt'), 'w') as f:
                f.write(f"Analytics Report: {report_type}\n")
                f.write(f"Generated: {data['generated_at']}\n\n")
                f.write(json.dumps(data, indent=2, default=str))
        
        return str(output_path)
